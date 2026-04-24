from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Tuple

import networkx as nx

from .metrics import extract_years, keyword_tokens, normalize_text, path_overlap_f1


def build_graph(events: List[dict], relations: List[dict]) -> nx.DiGraph:
    g = nx.DiGraph()
    for e in events:
        g.add_node(e['event_id'], **e)
    for r in relations:
        head = r['head_event_id']
        tail = r['tail_event_id']
        if head in g and tail in g:
            g.add_edge(head, tail, **r)
    return g


def _infer_risk_dimension(query: str) -> str:
    q = query.lower()
    if 'supply' in q or 'procurement' in q:
        return 'supply_chain_disruption_risk'
    if 'market' in q:
        return 'market_access_risk'
    if 'compliance' in q or 'enforcement' in q or 'entity list' in q:
        return 'compliance_enforcement_risk'
    return 'technology_access_risk'


def _infer_query_type(query: str) -> str:
    q = query.lower()
    if 'why' in q or 'cause' in q:
        return 'cause_tracing'
    if 'how did' in q or 'tighten' in q or 'escalat' in q:
        return 'policy_escalation_reasoning'
    if 'timeline' in q or 'between' in q or 'evolve' in q:
        return 'timeline_reasoning'
    if 'if ' in q or 'would' in q:
        return 'counterfactual_risk'
    if 'impact' in q or 'downstream' in q:
        return 'impact_analysis'
    return 'risk_identification'


def parse_query_heuristic(query: str | dict) -> dict:
    if isinstance(query, dict):
        query_text = query.get('query_text', '')
        return {
            'query_text': query_text,
            'risk_dimension': query.get('target_risk_dimension') or _infer_risk_dimension(query_text),
            'query_type': query.get('query_type') or _infer_query_type(query_text),
            'case_id': query.get('case_id'),
            'target_actor': query.get('target_actor'),
            'time_scope': query.get('time_scope'),
            'years': extract_years((query.get('time_scope') or '') + ' ' + query_text),
            'query_terms': keyword_tokens(query_text),
        }
    query_text = query
    return {
        'query_text': query_text,
        'risk_dimension': _infer_risk_dimension(query_text),
        'query_type': _infer_query_type(query_text),
        'case_id': None,
        'target_actor': None,
        'time_scope': None,
        'years': extract_years(query_text),
        'query_terms': keyword_tokens(query_text),
    }


def _event_matches_case(g: nx.DiGraph, node_id: str, case_id: str | None) -> bool:
    if not case_id:
        return True
    return g.nodes[node_id].get('case_id') == case_id


def select_local_subgraph(
    g: nx.DiGraph,
    seed_event_ids: List[str],
    max_hops: int = 2,
    min_relation_confidence: float = 0.6,
    case_id: str | None = None,
) -> Tuple[nx.DiGraph, List[str]]:
    seed_ids = [node for node in seed_event_ids if node in g and _event_matches_case(g, node, case_id)]
    keep = set(seed_ids)
    frontier = list(seed_ids)
    for _ in range(max_hops):
        next_frontier: list[str] = []
        for node in frontier:
            for src, dst, data in list(g.out_edges(node, data=True)) + list(g.in_edges(node, data=True)):
                conf = float(data.get('relation_confidence') or 0.0)
                if conf < min_relation_confidence:
                    continue
                neighbor = dst if src == node else src
                if not _event_matches_case(g, neighbor, case_id):
                    continue
                if neighbor not in keep:
                    keep.add(neighbor)
                    next_frontier.append(neighbor)
        frontier = next_frontier
        if not frontier:
            break
    sub = g.subgraph(keep).copy()
    for node in list(sub.nodes()):
        if node in seed_ids:
            continue
        if sub.degree(node) == 0:
            sub.remove_node(node)
    return sub, list(sub.nodes())


def _candidate_anchor_nodes(g: nx.DiGraph, seed_event_ids: Sequence[str], top_k_seed: int = 10) -> list[str]:
    ordered = []
    seen = set()
    for node in list(seed_event_ids) + list(g.nodes()):
        if node not in g or node in seen:
            continue
        seen.add(node)
        ordered.append(node)
    return ordered[:top_k_seed]


def enumerate_candidate_paths(
    g: nx.DiGraph,
    max_path_len: int = 5,
    top_k_seed: int = 10,
    seed_event_ids: Sequence[str] | None = None,
    include_singletons: bool = True,
) -> List[dict]:
    seed_event_ids = list(seed_event_ids or [])
    anchors = _candidate_anchor_nodes(g, seed_event_ids, top_k_seed=top_k_seed)
    paths: list[dict[str, Any]] = []
    seen = set()

    if include_singletons:
        for node in anchors:
            key = (node,)
            if key in seen:
                continue
            seen.add(key)
            paths.append({'event_ids': [node], 'relation_ids': [], 'path_type': 'singleton'})

    for s in anchors:
        for t in anchors:
            if s == t:
                continue
            try:
                for path in nx.all_simple_paths(g, source=s, target=t, cutoff=max_path_len):
                    if len(path) < 2:
                        continue
                    key = tuple(path)
                    if key in seen:
                        continue
                    seen.add(key)
                    rels = []
                    for i in range(len(path) - 1):
                        rels.append(g.edges[path[i], path[i + 1]].get('relation_id'))
                    paths.append({'event_ids': path, 'relation_ids': rels, 'path_type': 'chain'})
            except nx.NetworkXNoPath:
                continue
    return paths


def _actor_alignment(node: dict, query_info: dict[str, Any]) -> float:
    target_actor = normalize_text(query_info.get('target_actor') or '')
    if not target_actor:
        return 0.0
    event_actor = normalize_text(node.get('actor') or '')
    event_target = normalize_text(node.get('target_entity') or '')
    event_title = normalize_text(node.get('event_title') or '')
    if target_actor in event_actor or target_actor in event_target or target_actor in event_title:
        return 1.0
    return 0.0


def _term_alignment(node: dict, query_info: dict[str, Any]) -> float:
    terms = [t for t in query_info.get('query_terms', []) if len(t) >= 4]
    if not terms:
        return 0.0
    haystack = normalize_text(' '.join([
        node.get('event_title') or '',
        node.get('event_summary') or '',
        node.get('actor') or '',
        node.get('target_entity') or '',
    ]))
    hits = sum(1 for term in terms if term in haystack)
    return min(1.0, 0.2 * hits)


def score_path(g: nx.DiGraph, path: dict, target_risk: str | None = None, query_info: dict | None = None) -> float:
    query_info = parse_query_heuristic(query_info or {})
    target_risk = target_risk or query_info.get('risk_dimension')
    query_type = query_info.get('query_type', 'risk_identification')
    event_ids = path['event_ids']
    path_len = len(event_ids)
    edge_len = max(0, path_len - 1)

    causal = 0.0
    escalation = 0.0
    temporal = 0.0
    for i in range(len(event_ids) - 1):
        data = g.edges[event_ids[i], event_ids[i + 1]]
        rel_type = data.get('relation_type')
        conf = float(data.get('relation_confidence') or 0.0)
        if rel_type in ('direct_causality', 'conditional_trigger'):
            causal += conf
        if rel_type in ('policy_escalation', 'impact_propagation'):
            escalation += conf
        if rel_type == 'temporal_precedence':
            temporal += conf
    if edge_len > 0:
        causal /= edge_len
        escalation /= edge_len
        temporal /= edge_len

    node_scores = []
    for ev_id in event_ids:
        node = g.nodes[ev_id]
        node_score = 0.0
        if str(node.get('is_key_event')).lower() in ('true', '1'):
            node_score += 1.0
        if str(node.get('is_turning_point')).lower() in ('true', '1'):
            node_score += 1.2
        if target_risk and node.get('risk_dimension') == target_risk:
            node_score += 0.8
        node_score += _actor_alignment(node, query_info)
        node_score += _term_alignment(node, query_info)
        query_years = set(query_info.get('years') or [])
        event_years = set(extract_years(node.get('event_date') or ''))
        if query_years and event_years and query_years & event_years:
            node_score += 0.25
        node_scores.append(node_score)
    critical_coverage = sum(node_scores) / path_len if path_len else 0.0

    query_type_bonus = 0.0
    length_weight = {
        'risk_identification': 1.4,
        'impact_analysis': 1.2,
        'cause_tracing': 0.9,
        'timeline_reasoning': 0.45,
        'policy_escalation_reasoning': 0.95,
        'counterfactual_risk': 0.6,
    }.get(query_type, 0.8)

    if query_type == 'risk_identification':
        query_type_bonus += 2.0 if path_len == 1 else (0.8 if path_len == 2 else -0.4 * (path_len - 2))
    elif query_type == 'impact_analysis':
        query_type_bonus += 1.0 if path_len == 1 else (0.5 if path_len == 2 else -0.3 * max(0, path_len - 2))
    elif query_type == 'cause_tracing':
        causal *= 1.5
        query_type_bonus += 0.7 if path_len <= 3 else -0.2 * max(0, path_len - 3)
    elif query_type == 'timeline_reasoning':
        temporal *= 1.4
        query_type_bonus += 0.3 if path_len >= 2 else -0.2
    elif query_type == 'policy_escalation_reasoning':
        escalation *= 1.6
        query_type_bonus += 0.9 if path_len == 2 else (0.5 if path_len == 3 else -0.35 * max(0, path_len - 3))
    elif query_type == 'counterfactual_risk':
        query_type_bonus += 0.3 if path_len <= 3 else 0.0

    compact_bonus = 1.2 / max(1, path_len)
    length_penalty = length_weight * edge_len
    same_case_bonus = 0.4 if len({g.nodes[ev].get('case_id') for ev in event_ids}) == 1 else 0.0

    return (
        1.8 * causal
        + 1.8 * escalation
        + 1.2 * temporal
        + 1.5 * critical_coverage
        + compact_bonus
        + query_type_bonus
        + same_case_bonus
        - length_penalty
    )


def path_disagreement(paths: Sequence[dict]) -> float:
    if len(paths) < 2:
        return 0.0
    overlaps = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            overlaps.append(path_overlap_f1(paths[i].get('event_ids', []), paths[j].get('event_ids', [])))
    if not overlaps:
        return 0.0
    return 1.0 - (sum(overlaps) / len(overlaps))
