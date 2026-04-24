from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from rank_bm25 import BM25Okapi

from .metrics import extract_years, keyword_tokens, normalize_text


@dataclass
class EventRecord:
    event_id: str
    case_id: str | None
    event_title: str | None
    event_summary: str | None
    actor: str | None
    target_entity: str | None
    policy_action_type: str | None
    risk_dimension: str | None
    event_date: str | None
    is_key_event: bool | None = None
    is_turning_point: bool | None = None

    @property
    def text(self) -> str:
        parts = [
            self.event_title or '',
            self.event_summary or '',
            self.actor or '',
            self.target_entity or '',
            self.policy_action_type or '',
            self.risk_dimension or '',
        ]
        return ' '.join([p for p in parts if p]).strip()


class BM25EventRetriever:
    def __init__(self, events: List[Dict[str, Any]]):
        self.events = [EventRecord(**{k: v for k, v in e.items() if k in EventRecord.__annotations__}) for e in events]
        self.event_by_id = {ev.event_id: ev for ev in self.events}
        self.corpus = [keyword_tokens(ev.text) for ev in self.events]
        self.bm25 = BM25Okapi(self.corpus)
        self.index_by_case: dict[str, list[int]] = {}
        for idx, ev in enumerate(self.events):
            if ev.case_id:
                self.index_by_case.setdefault(ev.case_id, []).append(idx)

    def _candidate_indices(self, query_record: dict[str, Any] | None = None) -> list[int]:
        if not query_record:
            return list(range(len(self.events)))
        case_id = query_record.get('case_id')
        if case_id and case_id in self.index_by_case:
            return list(self.index_by_case[case_id])
        return list(range(len(self.events)))

    def _structural_score(self, ev: EventRecord, query: str, query_record: dict[str, Any] | None = None) -> float:
        if not query_record:
            return 0.0
        score = 0.0
        case_id = query_record.get('case_id')
        if case_id and ev.case_id == case_id:
            score += 3.0

        query_text_norm = normalize_text(query)
        target_actor = normalize_text(query_record.get('target_actor') or '')
        event_actor = normalize_text(ev.actor or '')
        event_target = normalize_text(ev.target_entity or '')
        event_title = normalize_text(ev.event_title or '')

        if target_actor:
            if target_actor in event_actor or target_actor in event_target or target_actor in event_title:
                score += 2.5
            else:
                actor_terms = [t for t in target_actor.split() if len(t) >= 3]
                overlap = sum(1 for term in actor_terms if term in event_actor or term in event_target or term in event_title)
                score += min(2.0, 0.7 * overlap)

        direct_terms = [t for t in keyword_tokens(query_text_norm) if len(t) >= 4]
        entity_overlap = sum(1 for term in direct_terms if term in event_actor or term in event_target or term in event_title)
        score += min(2.0, 0.25 * entity_overlap)

        query_risk = query_record.get('target_risk_dimension') or query_record.get('risk_dimension')
        if query_risk and ev.risk_dimension == query_risk:
            score += 1.0

        query_years = set(extract_years((query_record.get('time_scope') or '') + ' ' + query))
        event_years = set(extract_years(ev.event_date or ''))
        if query_years and event_years:
            if query_years & event_years:
                score += 0.75
            else:
                score -= 0.2

        if str(ev.is_key_event).lower() in ('true', '1'):
            score += 0.2
        if str(ev.is_turning_point).lower() in ('true', '1'):
            score += 0.35
        return score

    @staticmethod
    def _normalize_scores(values: list[float]) -> list[float]:
        if not values:
            return []
        lo = min(values)
        hi = max(values)
        if hi == lo:
            return [0.0 for _ in values]
        return [(v - lo) / (hi - lo) for v in values]

    def search(
        self,
        query: str,
        top_k: int = 10,
        query_record: dict[str, Any] | None = None,
        candidate_event_ids: Iterable[str] | None = None,
    ) -> List[Dict[str, Any]]:
        q_tokens = keyword_tokens(query)
        scores = list(self.bm25.get_scores(q_tokens))
        candidate_indices = self._candidate_indices(query_record)
        if candidate_event_ids is not None:
            allowed = set(candidate_event_ids)
            candidate_indices = [idx for idx in candidate_indices if self.events[idx].event_id in allowed]
        semantic_values = [scores[idx] for idx in candidate_indices]
        semantic_norm = self._normalize_scores(semantic_values)
        ranked = []
        for pos, idx in enumerate(candidate_indices):
            ev = self.events[idx]
            structure = self._structural_score(ev, query, query_record=query_record)
            combined = semantic_norm[pos] + structure
            ranked.append((combined, semantic_norm[pos], structure, ev))
        ranked.sort(key=lambda item: (item[0], item[2], item[3].event_date or ''), reverse=True)
        out = []
        for combined, semantic, structure, ev in ranked[:top_k]:
            rec = ev.__dict__.copy()
            rec['retrieval_score'] = float(combined)
            rec['semantic_score'] = float(semantic)
            rec['structural_score'] = float(structure)
            out.append(rec)
        return out
