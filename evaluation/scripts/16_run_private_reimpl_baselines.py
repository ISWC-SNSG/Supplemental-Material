#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SRC_ROOT = REPO_ROOT / 'src'
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
from pathlib import Path

from baselines.common import build_private_resources
from baselines.registry import get_private_method, list_private_methods
from tsrisk.utils import ensure_dir, read_jsonl, read_yaml, write_jsonl


def main() -> None:
    ap = argparse.ArgumentParser(description='Run benchmark-local baseline adapters on the private benchmark.')
    ap.add_argument('--config', default='configs/private_reimpl_baselines.yaml')
    ap.add_argument('--method', choices=list_private_methods(), required=True)
    ap.add_argument('--split', default='test')
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    cfg = read_yaml(args.config)
    queries = [q for q in read_jsonl(cfg['query_file']) if q.get('split') == args.split]
    events = list(read_jsonl(cfg['event_file']))
    relations = list(read_jsonl(cfg['relation_file']))
    resources = build_private_resources(events, relations)
    method = get_private_method(args.method)
    params = cfg.get('methods', {}).get(args.method, {})

    preds = []
    for q in queries:
        pred = method(resources, q, **params)
        preds.append(pred)
    write_jsonl(preds, args.output)
    print(f'Wrote {len(preds)} predictions to {args.output}')


if __name__ == '__main__':
    main()
