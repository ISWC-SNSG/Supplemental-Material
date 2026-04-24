#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SRC_ROOT = REPO_ROOT / 'src'
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pandas as pd

METHOD_ORDER = [
    'Standard RAG',
    'TemporalSort',
    'E$^2$RAG (reimpl.)',
    'Ours',
]
GROUP_ORDER = ['control_ordered', 'reversed_hard', 'three_ref_hard']


def parse_order(value: str) -> list[int]:
    return list(ast.literal_eval(value)) if isinstance(value, str) else list(value)


def pairwise_temporal_accuracy(gold_order: str, pred_order: str) -> float:
    gold = parse_order(gold_order)
    pred = parse_order(pred_order)
    pos = {item: idx for idx, item in enumerate(pred)}
    total = 0
    correct = 0
    for i in range(len(gold)):
        for j in range(i + 1, len(gold)):
            a, b = gold[i], gold[j]
            if a in pos and b in pos:
                total += 1
                if pos[a] < pos[b]:
                    correct += 1
    return correct / total if total else 1.0


def anchor_accuracy(gold_anchor: int, pred_anchor: int) -> float:
    return float(gold_anchor == pred_anchor)


def support_reordering_accuracy(gold_order: str, pred_order: str) -> float:
    return float(parse_order(gold_order) == parse_order(pred_order))


def main() -> None:
    ap = argparse.ArgumentParser(description='Evaluate the final 90-example ChronoQA subset using revised ChronoQA metrics.')
    ap.add_argument('--manifest', default='data/public_eval_subsets/chronoqa_temporal_balanced_90_final/manifest.json')
    ap.add_argument('--per-task', default='artifacts/paper_results/chronoqa_90_final_per_task.csv')
    ap.add_argument('--summary-out', default='artifacts/paper_results/chronoqa_90_final_summary_overall.csv')
    ap.add_argument('--group-out', default='artifacts/paper_results/chronoqa_90_final_summary_by_group.csv')
    ap.add_argument('--report-out', default='artifacts/paper_results/chronoqa_90_final_report.md')
    args = ap.parse_args()

    df = pd.read_csv(args.per_task)
    df['temporal_order_accuracy'] = df.apply(lambda r: pairwise_temporal_accuracy(r['gold_order'], r['pred_order']), axis=1)
    df['anchor_accuracy'] = df.apply(lambda r: anchor_accuracy(r['gold_anchor'], r['pred_anchor']), axis=1)
    df['support_reordering_accuracy'] = df.apply(lambda r: support_reordering_accuracy(r['gold_order'], r['pred_order']), axis=1)
    df.to_csv(args.per_task, index=False, float_format='%.4f')

    overall = (df.groupby('method')[['temporal_order_accuracy', 'anchor_accuracy', 'support_reordering_accuracy']]
                 .mean().reset_index())
    overall.columns = ['Method', 'Temporal Order Accuracy', 'Anchor Accuracy', 'Support Reordering Accuracy']
    overall['Method'] = pd.Categorical(overall['Method'], categories=METHOD_ORDER, ordered=True)
    overall = overall.sort_values('Method')
    overall.to_csv(args.summary_out, index=False, float_format='%.4f')

    by_group = (df.groupby(['group', 'method'])[['temporal_order_accuracy', 'anchor_accuracy', 'support_reordering_accuracy']]
                  .mean().reset_index())
    by_group.columns = ['group', 'Method', 'Temporal Order Accuracy', 'Anchor Accuracy', 'Support Reordering Accuracy']
    by_group['group'] = pd.Categorical(by_group['group'], categories=GROUP_ORDER, ordered=True)
    by_group['Method'] = pd.Categorical(by_group['Method'], categories=METHOD_ORDER, ordered=True)
    by_group = by_group.sort_values(['group', 'Method'])
    by_group.to_csv(args.group_out, index=False, float_format='%.4f')

    with open(args.report_out, 'w', encoding='utf-8') as f:
        f.write('# ChronoQA 90-example final subset report\n\n')
        f.write('This report uses the revised ChronoQA metric definitions:\n\n')
        f.write('- **Temporal Order Accuracy**: pairwise chronological consistency of the predicted support order with respect to the gold temporal order.\n')
        f.write('- **Anchor Accuracy**: exact match between predicted and gold support anchor.\n')
        f.write('- **Support Reordering Accuracy**: exact match between predicted and gold support sequence.\n\n')
        f.write('## Overall summary\n\n')
        f.write(overall.round(4).to_markdown(index=False))
        f.write('\n\n## By-group summary\n\n')
        f.write(by_group.round(4).to_markdown(index=False))
        f.write('\n')

    print(overall)


if __name__ == '__main__':
    main()
