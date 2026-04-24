"""KG^2RAG-style benchmark-local adapter.

This file is an independent protocol-level adaptation for the event-logic
benchmark used in the paper. It is not the official implementation of the
corresponding cited system and is not intended to reproduce all components,
hyperparameters, prompts, or engineering details of the original work. It
preserves the central retrieval or graph-reasoning bias needed for controlled
comparison under the shared benchmark input/output protocol.
"""

from __future__ import annotations

from typing import Any

from tsrisk.graph_reasoning import enumerate_candidate_paths, score_path, select_local_subgraph
from .common import PrivateResources, make_prediction, retrieve_seed_events


def predict(resources: PrivateResources, query_record: dict, top_k_events: int = 10, max_hops: int = 2, max_path_len: int = 5) -> dict[str, Any]:
    seeds = retrieve_seed_events(resources, query_record, top_k=top_k_events)
    seed_ids = [s['event_id'] for s in seeds]
    # graph-guided expansion and organization
    subgraph, kept_nodes = select_local_subgraph(resources.graph, seed_ids, max_hops=max_hops, min_relation_confidence=0.5, case_id=query_record.get('case_id'))
    candidates = enumerate_candidate_paths(subgraph, max_path_len=max_path_len, top_k_seed=min(10, len(kept_nodes)), seed_event_ids=seed_ids, include_singletons=True)
    scored = sorted(candidates, key=lambda p: (score_path(subgraph, p, query_info=query_record), -len(p['event_ids'])) , reverse=True)
    best = scored[0]['event_ids'] if scored else (seed_ids[:1] if seed_ids else [])
    return make_prediction(resources, query_record, best)
