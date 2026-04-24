from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from tsrisk.graph_reasoning import (
    build_graph,
    enumerate_candidate_paths,
    parse_query_heuristic,
    score_path,
    select_local_subgraph,
)
from tsrisk.metrics import keyword_tokens, normalize_uncertainty_label
from tsrisk.retrieval import BM25EventRetriever


@dataclass
class PrivateResources:
    graph: Any
    retriever: BM25EventRetriever
    events: list[dict]
    relations: list[dict]


def build_private_resources(events: list[dict], relations: list[dict]) -> PrivateResources:
    graph = build_graph(events, relations)
    retriever = BM25EventRetriever(events)
    return PrivateResources(graph=graph, retriever=retriever, events=events, relations=relations)


def retrieve_seed_events(resources: PrivateResources, query_record: dict, top_k: int = 10) -> list[dict]:
    query_text = query_record.get('query_text', '')
    return resources.retriever.search(query_text, top_k=top_k, query_record=query_record)


def answer_from_path(resources: PrivateResources, query_record: dict, path_event_ids: list[str]) -> tuple[str, str]:
    titles = []
    for event_id in path_event_ids:
        node = resources.graph.nodes[event_id]
        title = (node.get('event_title') or node.get('event_summary') or event_id).strip()
        titles.append(title)
    if not titles:
        return '', ''
    query_type = (query_record.get('query_type') or '').strip()
    if query_type == 'counterfactual_risk':
        answer = 'The available event chain suggests the conclusion remains partially supported after excluding the queried event.'
    elif query_type == 'policy_escalation_reasoning':
        answer = 'The selected support chain indicates a progressive tightening of restrictions across the linked events.'
    elif query_type == 'cause_tracing':
        answer = 'The selected support chain identifies the most relevant upstream events for the queried effect.'
    else:
        answer = 'The selected support chain captures the most relevant events for the queried risk.'
    rationale = ' -> '.join(titles)
    return answer, rationale


def uncertainty_from_path(resources: PrivateResources, query_record: dict, path_event_ids: list[str]) -> str:
    query_type = (query_record.get('query_type') or '').strip()
    if not path_event_ids:
        return 'insufficient-evidence'
    if query_type == 'counterfactual_risk' and len(path_event_ids) > 0:
        return 'partially-supported'
    if len(path_event_ids) == 1:
        return 'partially-supported'
    return 'fully-supported'


def make_prediction(resources: PrivateResources, query_record: dict, path_event_ids: list[str]) -> dict[str, Any]:
    answer, rationale = answer_from_path(resources, query_record, path_event_ids)
    relation_ids = []
    for i in range(max(0, len(path_event_ids)-1)):
        if resources.graph.has_edge(path_event_ids[i], path_event_ids[i+1]):
            relation_ids.append(resources.graph.edges[path_event_ids[i], path_event_ids[i+1]].get('relation_id'))
    return {
        'query_id': query_record.get('query_id'),
        'answer': answer,
        'rationale': rationale,
        'uncertainty_label': normalize_uncertainty_label(uncertainty_from_path(resources, query_record, path_event_ids)),
        'selected_path_event_ids': path_event_ids,
        'selected_path_relation_ids': relation_ids,
        'notes': 'benchmark-local deterministic adapter',
    }


def shortest_path_if_any(graph, source: str, target: str, cutoff: int = 5) -> list[str]:
    try:
        import networkx as nx
        for path in nx.all_simple_paths(graph, source=source, target=target, cutoff=cutoff):
            return list(path)
    except Exception:
        pass
    return []
