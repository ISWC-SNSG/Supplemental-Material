from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def load_prompt(path: str | Path) -> str:
    return Path(path).read_text(encoding='utf-8')


def make_plain_llm_user_prompt(query: dict) -> str:
    return f"Question: {query['query_text']}\nReturn JSON only."


def make_standard_rag_user_prompt(query: dict, events: List[dict]) -> str:
    lines = [f"Question: {query['query_text']}", "Retrieved event evidence:"]
    for ev in events:
        lines.append(f"- {ev.get('event_id')}: {ev.get('event_title')} | {ev.get('event_summary')}")
    lines.append("Return JSON only.")
    return '\n'.join(lines)


def make_ours_user_prompt(query: dict, subgraph_events: List[dict], candidate_paths: List[dict]) -> str:
    lines = [f"Question: {query['query_text']}"]
    lines.append("Local subgraph events:")
    for ev in subgraph_events:
        lines.append(
            f"- {ev.get('event_id')}: {ev.get('event_title')} | actor={ev.get('actor')} | "
            f"target={ev.get('target_entity')} | risk={ev.get('risk_dimension')} | summary={ev.get('event_summary')}"
        )
    lines.append("Candidate supporting paths:")
    for i, p in enumerate(candidate_paths[:5], start=1):
        lines.append(f"Path {i}: event_ids={p.get('event_ids')} relation_ids={p.get('relation_ids')} score={p.get('score')}")
    lines.append("Use only the supplied graph/path evidence. Return JSON only.")
    return '\n'.join(lines)
