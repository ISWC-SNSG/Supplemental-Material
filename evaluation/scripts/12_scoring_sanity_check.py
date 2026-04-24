#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from tsrisk.utils import ensure_dir, get_output_root


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


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


def truncate(text: str, limit: int = 120) -> str:
    text = (text or '').strip().replace('\n', ' ')
    if len(text) <= limit:
        return text
    return text[: limit - 3] + '...'


def method_from_private_stem(stem: str) -> str:
    prefix = 'private_benchmark_test_'
    suffix = '_summary'
    name = stem
    if name.startswith(prefix):
        name = name[len(prefix) :]
    if name.endswith(suffix):
        name = name[: -len(suffix)]
    return name


def build_private_rows(baseline_reports: Path, repaired_reports: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    examples: list[dict] = []
    for summary_path in sorted(repaired_reports.glob('private_benchmark_test_*_summary.json')):
        method = method_from_private_stem(summary_path.stem)
        repaired = load_json(summary_path)
        baseline = load_json(baseline_reports / summary_path.name)
        per_query_path = repaired_reports / f'private_benchmark_test_{method}_per_query.csv'
        per_query = pd.read_csv(per_query_path) if per_query_path.exists() else pd.DataFrame()

        if not per_query.empty:
            relaxed = per_query[per_query['answer_char_f1'] >= 0.5]
            strong_relaxed = per_query[(per_query['strict_em'] == 0) & (per_query['answer_char_f1'] >= 0.7)]
            for _, row in strong_relaxed.sort_values(['answer_char_f1', 'answer_contains'], ascending=False).head(3).iterrows():
                examples.append(
                    {
                        'method': method,
                        'query_id': row['query_id'],
                        'char_f1': round(float(row['answer_char_f1']), 3),
                        'contains': int(row['answer_contains']),
                        'pred_answer': truncate(str(row['pred_answer'])),
                        'gold_answer': truncate(str(row['gold_answer'])),
                    }
                )
        else:
            relaxed = pd.DataFrame()
            strong_relaxed = pd.DataFrame()

        rows.append(
            {
                'method': method,
                'n': int(repaired.get('n', 0)),
                'baseline_reported_accuracy_em': round(float(baseline.get('accuracy_em', 0.0)), 4),
                'baseline_reported_macro_f1': round(float(baseline.get('macro_f1', 0.0)), 4),
                'strict_accuracy_em': round(float(repaired.get('strict_accuracy_em', 0.0)), 4),
                'strict_macro_token_f1': round(float(repaired.get('strict_macro_token_f1', 0.0)), 4),
                'answer_norm_em': round(float(repaired.get('answer_norm_em', 0.0)), 4),
                'answer_char_f1': round(float(repaired.get('answer_char_f1', 0.0)), 4),
                'answer_contains': round(float(repaired.get('answer_contains', 0.0)), 4),
                'queries_char_f1_ge_0_5': int(len(relaxed)),
                'strict_zero_but_char_f1_ge_0_7': int(len(strong_relaxed)),
            }
        )
    return pd.DataFrame(rows).sort_values('method'), pd.DataFrame(examples)


def build_public_rows(baseline_reports: Path, repaired_reports: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for summary_path in sorted(repaired_reports.glob('chronoqa_*_summary.json')):
        repaired = load_json(summary_path)
        baseline = load_json(baseline_reports / summary_path.name)
        rows.append(
            {
                'file': summary_path.name,
                'n': int(repaired.get('n', 0)),
                'baseline_reported_accuracy_em': round(float(baseline.get('accuracy_em', 0.0)), 4),
                'baseline_reported_macro_f1': round(float(baseline.get('macro_f1', 0.0)), 4),
                'strict_accuracy_em': round(float(repaired.get('strict_accuracy_em', 0.0)), 4),
                'strict_macro_token_f1': round(float(repaired.get('strict_macro_token_f1', 0.0)), 4),
                'answer_norm_em': round(float(repaired.get('answer_norm_em', 0.0)), 4),
                'answer_char_f1': round(float(repaired.get('answer_char_f1', 0.0)), 4),
                'answer_contains': round(float(repaired.get('answer_contains', 0.0)), 4),
            }
        )
    return pd.DataFrame(rows).sort_values('file')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline-reports-dir', default='outputs/reports')
    ap.add_argument('--repaired-reports-dir', default=None)
    args = ap.parse_args()

    baseline_reports = Path(args.baseline_reports_dir)
    repaired_reports = Path(args.repaired_reports_dir) if args.repaired_reports_dir else get_output_root() / 'reports'
    repaired_reports = ensure_dir(repaired_reports)

    private_df, example_df = build_private_rows(baseline_reports, repaired_reports)
    public_df = build_public_rows(baseline_reports, repaired_reports)

    if private_df.empty:
        raise SystemExit(f'No repaired private summaries found in {repaired_reports}')

    private_df.to_csv(repaired_reports / 'scoring_sanity_private.csv', index=False)
    if not example_df.empty:
        example_df.to_csv(repaired_reports / 'scoring_sanity_private_examples.csv', index=False)
    if not public_df.empty:
        public_df.to_csv(repaired_reports / 'scoring_sanity_public.csv', index=False)

    notes = [
        '# Scoring Sanity Check',
        '',
        '## Private Benchmark',
        '',
        'This compares the original report files under `outputs/reports/` against the repaired relaxed-metric summaries in the active output root.',
        '',
        df_to_markdown(private_df),
        '',
    ]

    if not example_df.empty:
        notes.extend(
            [
                'Queries below still have `strict_em = 0`, but the repaired scorer now gives high overlap credit for paraphrastic answers.',
                '',
                df_to_markdown(example_df),
                '',
            ]
        )

    if not public_df.empty:
        notes.extend(
            [
                '## Public Benchmark Note',
                '',
                'ChronoQA is still hard under normalized EM, but it no longer collapses to all-zero answer quality once Chinese-safe char overlap and containment are added.',
                '',
                df_to_markdown(public_df),
                '',
            ]
        )

    report_path = repaired_reports / 'scoring_sanity_check.md'
    report_path.write_text('\n'.join(notes), encoding='utf-8')
    print(f'Wrote {report_path}')


if __name__ == '__main__':
    main()
