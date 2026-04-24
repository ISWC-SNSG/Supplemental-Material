"""RoG-style benchmark-local adapter.

This file is an independent protocol-level adaptation for the event-logic
benchmark used in the paper. It is not the official implementation of the
corresponding cited system and is not intended to reproduce all components,
hyperparameters, prompts, or engineering details of the original work. It
preserves the central retrieval or graph-reasoning bias needed for controlled
comparison under the shared benchmark input/output protocol.
"""

from __future__ import annotations

from typing import Any

from .common import PrivateResources, answer_from_path, build_private_resources, make_prediction, retrieve_seed_events, shortest_path_if_any


def predict(resources: PrivateResources, query_record: dict, top_k_events: int = 10, max_path_len: int = 5) -> dict[str, Any]:
    seeds = retrieve_seed_events(resources, query_record, top_k=top_k_events)
    seed_ids = [s['event_id'] for s in seeds]
    best_path = []
    best_score = -1.0
    # relation paths as reasoning plans
    for i, src in enumerate(seed_ids):
        for dst in seed_ids[i+1:]:
            path = shortest_path_if_any(resources.graph, src, dst, cutoff=max_path_len)
            if len(path) >= 2:
                score = 1.0 / len(path)
                if score > best_score:
                    best_score = score
                    best_path = path
    if not best_path and seed_ids:
        best_path = [seed_ids[0]]
    return make_prediction(resources, query_record, best_path)
