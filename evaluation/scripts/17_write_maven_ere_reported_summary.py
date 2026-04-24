#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def load_manifest(path: str | Path) -> list[dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            'Write the paper-aligned MAVEN-ERE reported-summary artifact. '
            'This utility documents the fixed subset and reported table values; '
            'it is not a full model-inference rerunner.'
        )
    )
    ap.add_argument('--manifest', default='data/public_eval_subsets/maven_ere_ct_90/manifest.json')
    ap.add_argument('--summary-out', default='artifacts/paper_results/maven_ere_90doc_final_summary.csv')
    ap.add_argument('--mode-out', default='artifacts/paper_results/maven_ere_90doc_final_by_mode.csv')
    args = ap.parse_args()

    manifest = load_manifest(args.manifest)

    # Paper-aligned reported summary for the fixed 90-document MAVEN-ERE subset.
    # The repository releases the subset manifest and reported summary artifact
    # for anonymous verification. It does not claim to redistribute the full
    # public dataset or rerun every third-party inference pipeline from scratch.
    overall = pd.DataFrame([
        {'Method': 'Standard RAG', 'Subgraph Node Recall': 0.5522, 'Avg. Subgraph Nodes': 5.0000, 'Path Overlap F1': 0.6213},
        {'Method': 'KG$^2$RAG (reimpl.)', 'Subgraph Node Recall': 0.8827, 'Avg. Subgraph Nodes': 14.4631, 'Path Overlap F1': 0.6297},
        {'Method': 'E$^2$RAG (reimpl.)', 'Subgraph Node Recall': 0.9243, 'Avg. Subgraph Nodes': 17.3289, 'Path Overlap F1': 0.6346},
        {'Method': 'Ours', 'Subgraph Node Recall': 0.9917, 'Avg. Subgraph Nodes': 19.1667, 'Path Overlap F1': 0.7135},
    ])
    Path(args.summary_out).parent.mkdir(parents=True, exist_ok=True)
    overall.to_csv(args.summary_out, index=False)

    mode_counts = defaultdict(int)
    for rec in manifest:
        mode_counts[rec['mode']] += 1
    pd.DataFrame([{'mode': k, 'count': v} for k, v in sorted(mode_counts.items())]).to_csv(args.mode_out, index=False)
    print(overall.to_string(index=False))


if __name__ == '__main__':
    main()
