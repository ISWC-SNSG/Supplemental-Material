#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from tsrisk.metrics import (
    char_f1,
    contains_match,
    exact_match,
    label_confusion_matrix,
    label_macro_f1,
    list_hit,
    normalize_uncertainty_label,
    normalized_exact_match,
    path_exact_match,
    path_overlap_f1,
    token_f1,
)
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


def parse_path_sequence(seq: str | None) -> list[str]:
    if not isinstance(seq, str) or not seq.strip() or seq.strip() == '-':
        return []
    return [x.strip() for x in seq.split('->') if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--predictions', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--reports-dir', default=None)
    args = ap.parse_args()

    cfg = read_yaml(args.config)
    queries = {q['query_id']: q for q in read_jsonl(cfg['query_file'])}
    paths = {p['query_id']: p for p in read_jsonl(cfg['path_file'])}
    preds = parse_predictions(Path(args.predictions))

    rows = []
    pred_labels = []
    gold_labels = []
    for p in preds:
        qid = p.get('query_id') or p.get('custom_id')
        if qid not in queries:
            continue
        q = queries[qid]
        gold_path = paths.get(qid, {})
        pred_answer = p.get('answer', '')
        gold_answer = q.get('gold_answer', '')
        pred_unc = p.get('uncertainty_label', '')
        gold_unc = q.get('gold_uncertainty_label', '')
        pred_events = p.get('selected_path_event_ids', []) or []
        gold_events = parse_path_sequence(gold_path.get('path_event_sequence'))
        row = {
            'query_id': qid,
            'case_id': q.get('case_id', ''),
            'query_type': q.get('query_type', ''),
            'strict_em': exact_match(pred_answer, gold_answer),
            'strict_token_f1': token_f1(pred_answer, gold_answer),
            'answer_norm_em': normalized_exact_match(pred_answer, gold_answer),
            'answer_char_f1': char_f1(pred_answer, gold_answer),
            'answer_contains': contains_match(pred_answer, gold_answer),
            'top1_path_hit': list_hit(pred_events, gold_events) if gold_events else 0.0,
            'path_overlap_f1': path_overlap_f1(pred_events, gold_events) if gold_events else 0.0,
            'path_exact_match': path_exact_match(pred_events, gold_events) if gold_events else 0.0,
            'uncertainty_match': 1.0 if normalize_uncertainty_label(pred_unc) == normalize_uncertainty_label(gold_unc) else 0.0,
            'parse_failed': 1.0 if p.get('parse_failed') else 0.0,
            'pred_answer': pred_answer,
            'gold_answer': gold_answer,
            'pred_uncertainty_label': pred_unc,
            'gold_uncertainty_label': gold_unc,
            'pred_path_event_ids': '->'.join(pred_events),
            'gold_path_event_ids': '->'.join(gold_events),
        }
        rows.append(row)
        pred_labels.append(pred_unc)
        gold_labels.append(gold_unc)

    df = pd.DataFrame(rows)
    outdir = ensure_dir(args.reports_dir) if args.reports_dir else ensure_dir(get_output_root() / 'reports')
    stem = Path(args.predictions).stem

    confusion = label_confusion_matrix(pred_labels, gold_labels)
    confusion_df = pd.DataFrame(confusion).T.fillna(0).astype(int)
    if len(df):
        # Composite structure-aware metrics are computed at the instance level
        # and then averaged in the summary. They should not be recomputed from
        # rounded table-level aggregates.
        df['grounded_answer_score'] = df['answer_char_f1'] * df['path_overlap_f1']
        df['structure_first_score'] = (
            0.4 * df['path_overlap_f1']
            + 0.2 * df['path_exact_match']
            + 0.2 * df['top1_path_hit']
            + 0.2 * df['answer_char_f1']
        )
    else:
        df['grounded_answer_score'] = pd.Series(dtype=float)
        df['structure_first_score'] = pd.Series(dtype=float)

    summary = {
        'n': int(len(df)),
        'accuracy_em': float(df['answer_norm_em'].mean()) if len(df) else 0.0,
        'macro_f1': float(df['answer_char_f1'].mean()) if len(df) else 0.0,
        'strict_accuracy_em': float(df['strict_em'].mean()) if len(df) else 0.0,
        'strict_macro_token_f1': float(df['strict_token_f1'].mean()) if len(df) else 0.0,
        'answer_norm_em': float(df['answer_norm_em'].mean()) if len(df) else 0.0,
        'answer_char_f1': float(df['answer_char_f1'].mean()) if len(df) else 0.0,
        'answer_contains': float(df['answer_contains'].mean()) if len(df) else 0.0,
        'top1_path_hit': float(df['top1_path_hit'].mean()) if len(df) else 0.0,
        'path_overlap_f1': float(df['path_overlap_f1'].mean()) if len(df) else 0.0,
        'path_exact_match': float(df['path_exact_match'].mean()) if len(df) else 0.0,
        'grounded_answer_score': float(df['grounded_answer_score'].mean()) if len(df) else 0.0,
        'structure_first_score': float(df['structure_first_score'].mean()) if len(df) else 0.0,
        'uncertainty_match': float(df['uncertainty_match'].mean()) if len(df) else 0.0,
        'uncertainty_macro_f1': float(label_macro_f1(pred_labels, gold_labels)) if gold_labels else 0.0,
        'parse_failed_rate': float(df['parse_failed'].mean()) if len(df) else 0.0,
    }

    df.to_csv(outdir / f'{stem}_per_query.csv', index=False)
    confusion_df.to_csv(outdir / f'{stem}_uncertainty_confusion.csv')
    dump_json(confusion, outdir / f'{stem}_uncertainty_confusion.json')
    dump_json(summary, outdir / f'{stem}_summary.json')
    print(summary)


if __name__ == '__main__':
    main()
