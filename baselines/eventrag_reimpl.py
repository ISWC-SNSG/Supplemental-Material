"""EventRAG-style benchmark-local adapter.

This file is an independent protocol-level adaptation for the event-logic
benchmark used in the paper. It is not the official implementation of the
corresponding cited system and is not intended to reproduce all components,
hyperparameters, prompts, or engineering details of the original work. It
preserves the central retrieval or graph-reasoning bias needed for controlled
comparison under the shared benchmark input/output protocol.
"""

from __future__ import annotations

from typing import Any

from tsrisk.graph_reasoning import enumerate_candidate_paths, select_local_subgraph
from .common import PrivateResources, make_prediction, retrieve_seed_events


def _event_centric_score(graph, path, query_record):
    years = set(query_record.get('years') or [])
    score = 0.0
    for event_id in path['event_ids']:
        node = graph.nodes[event_id]
        if str(node.get('is_key_event')).lower() in ('true','1'):
            score += 1.0
        if years and any(str(y) in str(node.get('event_date') or '') for y in years):
            score += 0.3
    score -= 0.15 * max(0, len(path['event_ids']) - 2)
    return score


def predict(resources: PrivateResources, query_record: dict, top_k_events: int = 12, max_hops: int = 2, max_path_len: int = 5) -> dict[str, Any]:
    seeds = retrieve_seed_events(resources, query_record, top_k=top_k_events)
    seed_ids = [s['event_id'] for s in seeds]
    subgraph, kept_nodes = select_local_subgraph(resources.graph, seed_ids, max_hops=max_hops, min_relation_confidence=0.45, case_id=query_record.get('case_id'))
    candidates = enumerate_candidate_paths(subgraph, max_path_len=max_path_len, top_k_seed=min(12, len(kept_nodes)), seed_event_ids=seed_ids, include_singletons=True)
    scored = sorted(candidates, key=lambda p: (_event_centric_score(subgraph, p, query_record), -len(p['event_ids'])), reverse=True)
    best = scored[0]['event_ids'] if scored else (seed_ids[:1] if seed_ids else [])
    return make_prediction(resources, query_record, best)
