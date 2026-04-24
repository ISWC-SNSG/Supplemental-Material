#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from tsrisk.uncertainty import append_calibration_note, calibrate_uncertainty_label
from tsrisk.utils import ensure_dir, read_jsonl, read_yaml, write_jsonl


def parse_predictions(pred_path: Path) -> list[dict]:
    records = list(read_jsonl(pred_path))
    out = []
    for rec in records:
        if 'response' not in rec:
            out.append(rec)
            continue
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
    return out


def default_output_path(predictions: Path) -> Path:
    return predictions.with_name(f'{predictions.stem}_uncertainty_calibrated.jsonl')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--predictions', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--output', default=None)
    ap.add_argument('--report', default=None)
    args = ap.parse_args()

    cfg = read_yaml(args.config)
    query_file = cfg.get('query_file')
    if not query_file:
        raise SystemExit('This calibrator currently expects a config with query_file (private benchmark).')

    queries = {q['query_id']: q for q in read_jsonl(query_file)}
    predictions_path = Path(args.predictions)
    preds = parse_predictions(predictions_path)

    calibrated = []
    report_rows = []
    for pred in preds:
        qid = pred.get('query_id') or pred.get('custom_id')
        if pred.get('parse_failed'):
            calibrated.append(pred)
            report_rows.append(
                {
                    'query_id': qid,
                    'query_type': queries.get(qid, {}).get('query_type', ''),
                    'old_uncertainty_label': pred.get('uncertainty_label', ''),
                    'new_uncertainty_label': pred.get('uncertainty_label', ''),
                    'changed': 0,
                    'reason': 'parse_failed',
                }
            )
            continue
        query = queries.get(qid)
        if not query:
            calibrated.append(pred)
            continue
        old_label = pred.get('uncertainty_label', '')
        new_label, reason = calibrate_uncertainty_label(
            query_type=query.get('query_type'),
            predicted_label=old_label,
            selected_path_event_ids=pred.get('selected_path_event_ids', []) or [],
            notes=pred.get('notes', ''),
            rationale=pred.get('rationale', ''),
            answer=pred.get('answer', ''),
        )
        updated = dict(pred)
        updated['uncertainty_label'] = new_label
        updated['notes'] = append_calibration_note(pred.get('notes', ''), reason, old_label, new_label)
        calibrated.append(updated)
        report_rows.append(
            {
                'query_id': qid,
                'query_type': query.get('query_type', ''),
                'old_uncertainty_label': old_label,
                'new_uncertainty_label': new_label,
                'changed': 1 if old_label != new_label else 0,
                'reason': reason,
            }
        )

    output_path = Path(args.output) if args.output else default_output_path(predictions_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(calibrated, output_path)

    report_path = Path(args.report) if args.report else output_path.with_name(f'{output_path.stem}_report.csv')
    ensure_dir(report_path.parent)
    pd.DataFrame(report_rows).to_csv(report_path, index=False)
    print(f'Wrote calibrated predictions to {output_path}')
    print(f'Wrote calibration report to {report_path}')


if __name__ == '__main__':
    main()
