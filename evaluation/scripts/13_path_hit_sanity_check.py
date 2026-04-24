#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import networkx as nx
import pandas as pd

from tsrisk.graph_reasoning import (
    build_graph,
    enumerate_candidate_paths,
    parse_query_heuristic,
    score_path,
    select_local_subgraph,
)
from tsrisk.metrics import list_hit, path_exact_match, path_overlap_f1
from tsrisk.retrieval import BM25EventRetriever
from tsrisk.utils import dump_json, ensure_dir, get_output_root, read_jsonl, read_yaml


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return '_No rows._'
    try:
        return df.to_markdown(index=False)
    except ImportError:
        cols = [str(c) for c in df.columns]
        lines = [
            '| ' + ' | '.join(cols) + ' |',
            '| ' + ' | '.join(['---'] * len(cols)) + ' |',
        ]
        for _, row in df.iterrows():
            vals = []
            for col in df.columns:
                text = '' if pd.isna(row[col]) else str(row[col])
                text = text.replace('\n', ' ').replace('|', '\\|')
                vals.append(text)
            lines.append('| ' + ' | '.join(vals) + ' |')
        return '\n'.join(lines)


def parse_path_sequence(seq: str | None) -> list[str]:
    if not isinstance(seq, str) or not seq.strip() or seq.strip() == '-':
        return []
    return [x.strip() for x in seq.split('->') if x.strip()]


def legacy_select_local_subgraph(
    g: nx.DiGraph,
    seed_event_ids: list[str],
    max_hops: int = 3,
    min_relation_confidence: float = 0.5,
) -> tuple[nx.DiGraph, list[str]]:
    keep = {node for node in seed_event_ids if node in g}
    frontier = set(keep)
    for _ in range(max_hops):
        nxt = set()
        for node in frontier:
            for src, dst, data in list(g.out_edges(node, data=True)) + list(g.in_edges(node, data=True)):
                conf = float(data.get('relation_confidence') or 0.0)
                if conf < min_relation_confidence:
                    continue
                nxt.add(src)
                nxt.add(dst)
        keep |= nxt
        frontier = nxt - keep
        if not frontier:
            break
    sub = g.subgraph(keep).copy()
    return sub, list(sub.nodes())


def legacy_enumerate_candidate_paths(
    g: nx.DiGraph,
    max_path_len: int = 5,
    top_k_seed: int = 10,
    seed_event_ids: list[str] | None = None,
) -> list[dict]:
    seed_event_ids = list(seed_event_ids or [])
    anchors: list[str] = []
    seen_nodes = set()
    for node in list(seed_event_ids) + list(g.nodes()):
        if node not in g or node in seen_nodes:
            continue
        seen_nodes.add(node)
        anchors.append(node)
    anchors = anchors[:top_k_seed]

    paths: list[dict] = []
    seen_paths = set()
    for source in anchors:
        for target in anchors:
            if source == target:
                continue
            try:
                for event_ids in nx.all_simple_paths(g, source=source, target=target, cutoff=max_path_len):
                    if len(event_ids) < 2:
                        continue
                    key = tuple(event_ids)
                    if key in seen_paths:
                        continue
                    seen_paths.add(key)
                    relation_ids = [
                        g.edges[event_ids[i], event_ids[i + 1]].get('relation_id')
                        for i in range(len(event_ids) - 1)
                    ]
                    paths.append(
                        {
                            'event_ids': event_ids,
                            'relation_ids': relation_ids,
                            'path_type': 'chain',
                        }
                    )
            except nx.NetworkXNoPath:
                continue
    return paths


def legacy_score_path(g: nx.DiGraph, path: dict, target_risk: str | None = None) -> float:
    event_ids = path['event_ids']
    path_len = len(event_ids)
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

    critical_coverage = 0.0
    for event_id in event_ids:
        node = g.nodes[event_id]
        if str(node.get('is_key_event')).lower() in ('true', '1'):
            critical_coverage += 1.0
        if str(node.get('is_turning_point')).lower() in ('true', '1'):
            critical_coverage += 1.0
        if target_risk and node.get('risk_dimension') == target_risk:
            critical_coverage += 0.5
    critical_coverage /= max(1, path_len)

    return causal + escalation + temporal + critical_coverage + 0.8 * path_len


def off_case_fraction(subgraph: nx.DiGraph, case_id: str | None) -> float:
    if not case_id or subgraph.number_of_nodes() == 0:
        return 0.0
    off_case = sum(1 for node in subgraph.nodes() if subgraph.nodes[node].get('case_id') != case_id)
    return off_case / subgraph.number_of_nodes()


def summarize(rows: list[dict], label: str) -> dict:
    df = pd.DataFrame(rows)
    prefix = f'{label}_'
    return {
        'heuristic': label,
        'top1_path_hit': float(df[f'{prefix}top1_path_hit'].mean()) if len(df) else 0.0,
        'path_overlap_f1': float(df[f'{prefix}path_overlap_f1'].mean()) if len(df) else 0.0,
        'path_exact_match': float(df[f'{prefix}path_exact_match'].mean()) if len(df) else 0.0,
        'avg_predicted_path_len': float(df[f'{prefix}path_len'].mean()) if len(df) else 0.0,
        'avg_subgraph_nodes': float(df[f'{prefix}subgraph_nodes'].mean()) if len(df) else 0.0,
        'avg_subgraph_case_count': float(df[f'{prefix}subgraph_case_count'].mean()) if len(df) else 0.0,
        'avg_off_case_fraction': float(df[f'{prefix}off_case_fraction'].mean()) if len(df) else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='configs/private_benchmark.yaml')
    ap.add_argument('--split', default='test')
    ap.add_argument('--method', default='ours')
    ap.add_argument('--reports-dir', default=None)
    args = ap.parse_args()

    cfg = read_yaml(args.config)
    reports_dir = Path(args.reports_dir) if args.reports_dir else get_output_root() / 'reports'
    reports_dir = ensure_dir(reports_dir)

    events = list(read_jsonl(cfg['event_file']))
    relations = list(read_jsonl(cfg['relation_file']))
    queries = [q for q in read_jsonl(cfg['query_file']) if q.get('split') == args.split]
    paths = {p['query_id']: p for p in read_jsonl(cfg['path_file'])}

    graph = build_graph(events, relations)
    retriever = BM25EventRetriever(events)
    method_cfg = cfg['methods'][args.method]

    rows: list[dict] = []
    for query in queries:
        gold_path = parse_path_sequence(paths[query['query_id']].get('path_event_sequence'))

        legacy_seeds = retriever.search(query['query_text'], top_k=method_cfg['top_k_events'])
        legacy_seed_ids = [rec['event_id'] for rec in legacy_seeds]
        legacy_query = parse_query_heuristic(query['query_text'])
        legacy_subgraph, _ = legacy_select_local_subgraph(
            graph,
            legacy_seed_ids,
            max_hops=method_cfg.get('max_hops', 3),
            min_relation_confidence=method_cfg.get('min_relation_confidence', 0.5),
        )
        legacy_paths = legacy_enumerate_candidate_paths(
            legacy_subgraph,
            max_path_len=method_cfg.get('max_path_len', 5),
            top_k_seed=10,
            seed_event_ids=legacy_seed_ids,
        )
        for path in legacy_paths:
            path['score'] = legacy_score_path(legacy_subgraph, path, target_risk=legacy_query.get('risk_dimension'))
        legacy_paths = sorted(legacy_paths, key=lambda item: item['score'], reverse=True)
        legacy_top = legacy_paths[0]['event_ids'] if legacy_paths else []

        repaired_query = parse_query_heuristic(query)
        repaired_seeds = retriever.search(query['query_text'], top_k=method_cfg['top_k_events'], query_record=query)
        repaired_seed_ids = [rec['event_id'] for rec in repaired_seeds]
        repaired_subgraph, _ = select_local_subgraph(
            graph,
            repaired_seed_ids,
            max_hops=method_cfg.get('max_hops', 3),
            min_relation_confidence=method_cfg.get('min_relation_confidence', 0.5),
            case_id=repaired_query.get('case_id'),
        )
        repaired_paths = enumerate_candidate_paths(
            repaired_subgraph,
            max_path_len=method_cfg.get('max_path_len', 5),
            seed_event_ids=repaired_seed_ids,
            include_singletons=True,
        )
        for path in repaired_paths:
            path['score'] = score_path(
                repaired_subgraph,
                path,
                target_risk=repaired_query.get('risk_dimension'),
                query_info=repaired_query,
            )
        repaired_paths = sorted(repaired_paths, key=lambda item: (item['score'], -len(item['event_ids'])), reverse=True)
        repaired_top = repaired_paths[0]['event_ids'] if repaired_paths else []

        rows.append(
            {
                'query_id': query['query_id'],
                'query_type': query.get('query_type', ''),
                'case_id': query.get('case_id', ''),
                'gold_path_event_ids': '->'.join(gold_path),
                'legacy_top_path_event_ids': '->'.join(legacy_top),
                'legacy_top1_path_hit': list_hit(legacy_top, gold_path) if gold_path else 0.0,
                'legacy_path_overlap_f1': path_overlap_f1(legacy_top, gold_path) if gold_path else 0.0,
                'legacy_path_exact_match': path_exact_match(legacy_top, gold_path) if gold_path else 0.0,
                'legacy_path_len': len(legacy_top),
                'legacy_subgraph_nodes': legacy_subgraph.number_of_nodes(),
                'legacy_subgraph_case_count': len({legacy_subgraph.nodes[node].get('case_id') for node in legacy_subgraph.nodes()}),
                'legacy_off_case_fraction': off_case_fraction(legacy_subgraph, query.get('case_id')),
                'repaired_top_path_event_ids': '->'.join(repaired_top),
                'repaired_top1_path_hit': list_hit(repaired_top, gold_path) if gold_path else 0.0,
                'repaired_path_overlap_f1': path_overlap_f1(repaired_top, gold_path) if gold_path else 0.0,
                'repaired_path_exact_match': path_exact_match(repaired_top, gold_path) if gold_path else 0.0,
                'repaired_path_len': len(repaired_top),
                'repaired_subgraph_nodes': repaired_subgraph.number_of_nodes(),
                'repaired_subgraph_case_count': len({repaired_subgraph.nodes[node].get('case_id') for node in repaired_subgraph.nodes()}),
                'repaired_off_case_fraction': off_case_fraction(repaired_subgraph, query.get('case_id')),
            }
        )

    df = pd.DataFrame(rows).sort_values('query_id')
    summary_df = pd.DataFrame([summarize(rows, 'legacy'), summarize(rows, 'repaired')])
    improvement_df = df[
        (df['legacy_top1_path_hit'] == 0.0) & (df['repaired_top1_path_hit'] == 1.0)
    ][
        [
            'query_id',
            'query_type',
            'gold_path_event_ids',
            'legacy_top_path_event_ids',
            'repaired_top_path_event_ids',
            'legacy_subgraph_case_count',
            'repaired_subgraph_case_count',
        ]
    ]

    stem = f'private_{args.split}_path_hit_sanity'
    df.to_csv(reports_dir / f'{stem}_per_query.csv', index=False)
    summary_df.to_csv(reports_dir / f'{stem}_summary.csv', index=False)
    if not improvement_df.empty:
        improvement_df.to_csv(reports_dir / f'{stem}_improved_cases.csv', index=False)

    dump_json(summary_df.to_dict(orient='records'), reports_dir / f'{stem}_summary.json')

    notes = [
        '# Path-Hit Sanity Check',
        '',
        'The legacy baseline reproduces the pre-repair structure: global BM25 retrieval, no case gating, buggy expansion, no singleton paths, and a length-biased additive path scorer.',
        '',
        df_to_markdown(summary_df),
        '',
    ]
    if not improvement_df.empty:
        notes.extend(
            [
                'Queries below were misses under the legacy heuristic but become hits after the repair.',
                '',
                df_to_markdown(improvement_df.head(10)),
                '',
            ]
        )

    report_path = reports_dir / f'{stem}.md'
    report_path.write_text('\n'.join(notes), encoding='utf-8')
    print(f'Wrote {report_path}')


if __name__ == '__main__':
    main()
