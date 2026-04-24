#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import json
import pandas as pd

from tsrisk.report import save_table


def method_from_file(name: str) -> str:
    stem = name.replace('_summary.json', '')
    prefix_map = {
        'private_benchmark_test_': '',
        'chronoqa_sampled_test_': 'sampled_',
        'chronoqa_test_': '',
        'maven_ere_': '',
    }
    for prefix, replacement in prefix_map.items():
        if stem.startswith(prefix):
            stem = replacement + stem[len(prefix) :]
            break
    if stem.endswith('_online'):
        stem = stem[: -len('_online')]
    return stem


def select_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    keep = [col for col in columns if col in df.columns]
    return df[keep].copy()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--reports-dir', required=True)
    args = ap.parse_args()
    reports = Path(args.reports_dir)
    rows = []
    for p in reports.glob('*_summary.json'):
        data = json.loads(p.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            continue
        rows.append({'file': p.name, **data})
    if not rows:
        raise SystemExit('No *_summary.json files found.')
    df = pd.DataFrame(rows).sort_values('file')
    private_df = df[df['file'].str.startswith('private_benchmark_')].copy()
    public_df = df[df['file'].str.startswith('chronoqa_') | df['file'].str.startswith('maven_ere_')].copy()
    if not private_df.empty:
        private_df['method'] = private_df['file'].map(method_from_file)
        private_table = select_columns(
            private_df,
            [
                'method',
                'n',
                'answer_char_f1',
                'answer_norm_em',
                'answer_contains',
                'strict_macro_token_f1',
                'top1_path_hit',
                'path_overlap_f1',
                'path_exact_match',
                'grounded_answer_score',
                'structure_first_score',
                'uncertainty_match',
                'uncertainty_macro_f1',
                'parse_failed_rate',
            ],
        ).sort_values('method')
        save_table(private_table, reports / 'main_results_private.csv', reports / 'table_1_main_results.md')
    if not public_df.empty:
        public_df['method'] = public_df['file'].map(method_from_file)
        public_table = select_columns(
            public_df,
            [
                'method',
                'n',
                'answer_char_f1',
                'answer_norm_em',
                'answer_contains',
                'strict_macro_token_f1',
                'note',
            ],
        ).sort_values('method')
        save_table(public_table, reports / 'main_results_public.csv', reports / 'table_2_public_generalization.md')
    if private_df.empty and public_df.empty:
        save_table(df, reports / 'main_results_private.csv', reports / 'table_1_main_results.md')
    print('Wrote tables to', reports)


if __name__ == '__main__':
    main()
