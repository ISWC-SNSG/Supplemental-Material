#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tsrisk.utils import read_yaml, read_jsonl, write_jsonl, output_path
from tsrisk.prompts import load_prompt, make_plain_llm_user_prompt, make_standard_rag_user_prompt, make_ours_user_prompt
from tsrisk.retrieval import BM25EventRetriever
from tsrisk.graph_reasoning import build_graph, parse_query_heuristic, select_local_subgraph, enumerate_candidate_paths, score_path
from openai_runner import responses_create_json


def make_public_user_prompt(query: dict, method: str) -> str:
    meta = query.get('meta') or {}
    lines = [f"Question: {query['query_text']}"]
    ref_qa = meta.get('reference_qa_list')
    if ref_qa:
        lines.append(f"Reference QA hints: {ref_qa}")
    chunks = meta.get('golden_chunks') or []
    if chunks:
        lines.append("Reference evidence:")
        for i, chunk in enumerate(chunks[:8], start=1):
            lines.append(f"[{i}] {chunk}")
    if method == 'ours':
        lines.append("Use structured temporal reasoning over the supplied evidence only.")
    else:
        lines.append("Use the supplied evidence only.")
    lines.append("Return JSON only.")
    return '\n'.join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--method', choices=['plain_llm', 'standard_rag', 'ours'], required=True)
    ap.add_argument('--split', default='dev')
    ap.add_argument('--limit', type=int, default=3)
    args = ap.parse_args()
    cfg = read_yaml(args.config)
    public_task_file = Path(cfg.get('task_file') or (Path(cfg['processed_dir']) / 'task_queries.jsonl'))

    if cfg['dataset'] == 'private':
        queries = [q for q in read_jsonl(cfg['query_file']) if q.get('split') == args.split][:args.limit]
        events = list(read_jsonl(cfg['event_file']))
        relations = list(read_jsonl(cfg['relation_file']))
    else:
        queries = [q for q in read_jsonl(public_task_file) if q.get('split', 'test') == args.split][:args.limit]
        events = []
        relations = []
    retriever = BM25EventRetriever(events) if events else None
    graph = build_graph(events, relations) if events and relations else None

    system_prompt = load_prompt(Path('prompts') / f'system_{args.method}.txt')
    outputs = []
    for q in queries:
        if args.method == 'plain_llm':
            user_prompt = make_plain_llm_user_prompt(q)
        elif args.method == 'standard_rag':
            if retriever is not None:
                top_events = retriever.search(q['query_text'], top_k=cfg['methods'][args.method]['top_k_events'], query_record=q)
                user_prompt = make_standard_rag_user_prompt(q, top_events)
            else:
                user_prompt = make_public_user_prompt(q, args.method)
        else:
            if retriever is not None and graph is not None:
                parsed = parse_query_heuristic(q)
                seeds = retriever.search(q['query_text'], top_k=cfg['methods'][args.method]['top_k_events'], query_record=q)
                seed_ids = [x['event_id'] for x in seeds]
                subgraph, kept = select_local_subgraph(
                    graph,
                    seed_ids,
                    max_hops=cfg['methods'][args.method]['max_hops'],
                    min_relation_confidence=cfg['methods'][args.method]['min_relation_confidence'],
                    case_id=parsed.get('case_id'),
                )
                cand_paths = enumerate_candidate_paths(
                    subgraph,
                    max_path_len=cfg['methods'][args.method]['max_path_len'],
                    seed_event_ids=seed_ids,
                    include_singletons=True,
                )
                for p in cand_paths:
                    p['score'] = score_path(subgraph, p, parsed['risk_dimension'], query_info=parsed)
                cand_paths = sorted(cand_paths, key=lambda x: (x['score'], -len(x['event_ids'])), reverse=True)[:cfg['methods'][args.method]['top_k_paths']]
                sub_events = [dict(subgraph.nodes[n]) for n in subgraph.nodes()]
                user_prompt = make_ours_user_prompt(q, sub_events, cand_paths)
            else:
                user_prompt = make_public_user_prompt(q, args.method)
        pred = responses_create_json(system_prompt, user_prompt)
        pred['query_id'] = q['query_id']
        pred['method'] = args.method
        outputs.append(pred)
    outpath = output_path('predictions') / f"{cfg['name']}_{args.split}_{args.method}_online.jsonl"
    write_jsonl(outputs, outpath)
    print('Wrote', outpath)


if __name__ == '__main__':
    main()
