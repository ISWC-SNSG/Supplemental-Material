#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from tsrisk.metrics import char_f1, contains_match, exact_match, normalized_exact_match, token_f1
from tsrisk.utils import dump_json, ensure_dir, get_output_root, read_jsonl, read_yaml


def parse_predictions(pred_path: Path) -> list[dict]:
    records = list(read_jsonl(pred_path))
    out = []
    for rec in records:
        if 'response' in rec:
            body = rec.get('response', {}).get('body', {})
            text = body.get('output_text')
            if text is None:
                out.append({'query_id': rec.get('custom_id'), 'parse_failed': True, 'raw_body': body})
                continue
            try:
                obj = json.loads(text)
                obj['query_id'] = rec.get('custom_id')
                out.append(obj)
            except Exception:
                out.append({'query_id': rec.get('custom_id'), 'parse_failed': True, 'raw_text': text})
        else:
            out.append(rec)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', choices=['chronoqa', 'maven_ere'], required=True)
    ap.add_argument('--predictions', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--reports-dir', default=None)
    args = ap.parse_args()
    cfg = read_yaml(args.config)
    public_task_file = Path(cfg.get('task_file') or (Path(cfg['processed_dir']) / 'task_queries.jsonl'))

    outdir = ensure_dir(args.reports_dir) if args.reports_dir else ensure_dir(get_output_root() / 'reports')
    stem = Path(args.predictions).stem

    if args.dataset == 'chronoqa':
        tasks = {q['query_id']: q for q in read_jsonl(public_task_file)}
        preds = parse_predictions(Path(args.predictions))
        rows = []
        for p in preds:
            qid = p.get('query_id') or p.get('custom_id')
            if qid not in tasks:
                continue
            q = tasks[qid]
            pred_answer = p.get('answer', '')
            gold_answer = q.get('gold_answer', '')
            rows.append({
                'query_id': qid,
                'strict_em': exact_match(pred_answer, gold_answer),
                'strict_token_f1': token_f1(pred_answer, gold_answer),
                'answer_norm_em': normalized_exact_match(pred_answer, gold_answer),
                'answer_char_f1': char_f1(pred_answer, gold_answer),
                'answer_contains': contains_match(pred_answer, gold_answer),
                'pred_answer': pred_answer,
                'gold_answer': gold_answer,
            })
        df = pd.DataFrame(rows)
        summary = {
            'n': int(len(df)),
            'accuracy_em': float(df['answer_norm_em'].mean()) if len(df) else 0.0,
            'macro_f1': float(df['answer_char_f1'].mean()) if len(df) else 0.0,
            'strict_accuracy_em': float(df['strict_em'].mean()) if len(df) else 0.0,
            'strict_macro_token_f1': float(df['strict_token_f1'].mean()) if len(df) else 0.0,
            'answer_norm_em': float(df['answer_norm_em'].mean()) if len(df) else 0.0,
            'answer_char_f1': float(df['answer_char_f1'].mean()) if len(df) else 0.0,
            'answer_contains': float(df['answer_contains'].mean()) if len(df) else 0.0,
        }
        if len(df):
            df.to_csv(outdir / f'{stem}_per_item.csv', index=False)
        dump_json(summary, outdir / f'{stem}_summary.json')
        print(summary)
        return

    summary = {
        'note': 'MAVEN-ERE scorer placeholder: dataset download and sampling preparation should be handled separately before relation/path evaluation.'
    }
    dump_json(summary, outdir / f'{stem}_summary.json')
    print(summary)


if __name__ == '__main__':
    main()
