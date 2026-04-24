#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tsrisk.utils import read_yaml, read_jsonl, write_jsonl, ensure_dir


def build_private(cfg: dict) -> None:
    outdir = ensure_dir(cfg['processed_dir'])
    queries = list(read_jsonl(cfg['query_file']))
    write_jsonl(queries, outdir / 'task_queries.jsonl')
    print('Wrote', len(queries), 'private task queries')


def build_chronoqa(cfg: dict) -> None:
    external = Path(cfg['external_dir']) / 'chronoqa.json'
    if not external.exists():
        raise SystemExit(f'ChronoQA file not found: {external}. Download it first or inspect download_notes.md.')
    outdir = ensure_dir(cfg['processed_dir'])
    import json
    items = json.loads(external.read_text(encoding='utf-8'))
    tasks = []
    for i, item in enumerate(items):
        tasks.append({
            'query_id': item.get('id', f'chronoqa_{i}'),
            'query_text': item['question'],
            'gold_answer': item.get('answer', ''),
            'split': item.get('split', 'test'),
            'meta': item,
        })
    write_jsonl(tasks, outdir / 'task_queries.jsonl')
    print('Wrote', len(tasks), 'ChronoQA tasks')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    args = ap.parse_args()
    cfg = read_yaml(args.config)
    if cfg['dataset'] == 'private':
        build_private(cfg)
    elif cfg['dataset'] == 'chronoqa':
        build_chronoqa(cfg)
    else:
        raise ValueError(cfg['dataset'])


if __name__ == '__main__':
    main()
