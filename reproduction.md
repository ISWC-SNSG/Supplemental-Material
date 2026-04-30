# Paper-Aligned Verification Guide

This document describes the verification workflow for the anonymous review package. The package supports inspection of released benchmark files, fixed public-subset manifests, metric definitions, and paper-aligned result artifacts. It is not a full engineering reproduction of all model-backed inference runs or official third-party baseline systems.

## 1. Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## 2. Main benchmark files

The processed release files of `TechRisk-EventLogic-Bench` are included in:

```text
data/techrisk_eventlogic_bench/
```

To regenerate derived task files from the included processed benchmark, use:

```bash
python scripts/03_build_tasks.py --config configs/private_benchmark.yaml
```

## 3. Private benchmark scoring and table utilities

Metric definitions for the private benchmark, including the instance-level Grounded Answer Score and Structure-First Score, are documented in `docs/private_metric_protocol.md`.

If per-example prediction files are available, score them with:

```bash
python evaluation/scripts/09_score_private.py --predictions <predictions.jsonl>
python evaluation/scripts/11_make_tables.py --reports-dir <reports_dir>
```

The repository also includes canonical paper-aligned result files in `artifacts/paper_results/` for verifying the reported table values.

## 4. Benchmark-local baseline adapters

The private benchmark adapters can be run with:

```bash
python evaluation/scripts/16_run_private_reimpl_baselines.py --config configs/private_reimpl_baselines.yaml --method rog_reimpl --split test --output outputs/private_rog_reimpl_test.jsonl
python evaluation/scripts/16_run_private_reimpl_baselines.py --config configs/private_reimpl_baselines.yaml --method kg2rag_reimpl --split test --output outputs/private_kg2rag_reimpl_test.jsonl
python evaluation/scripts/16_run_private_reimpl_baselines.py --config configs/private_reimpl_baselines.yaml --method eventrag_reimpl --split test --output outputs/private_eventrag_reimpl_test.jsonl
python evaluation/scripts/16_run_private_reimpl_baselines.py --config configs/private_reimpl_baselines.yaml --method e2rag_reimpl --split test --output outputs/private_e2rag_reimpl_test.jsonl
```

These are benchmark-local adapters, not official implementations of the cited systems. See `baseline_adapter_notes.md`.

## 5. Public-benchmark subset artifacts

### MAVEN-ERE Causal-Temporal 90-Document Evaluation Subset

```bash
python evaluation/scripts/17_write_maven_ere_reported_summary.py --manifest data/public_eval_subsets/maven_ere_ct_90/manifest.json
```

This materializes the paper-aligned reported summary and the subset mode counts. It is a reported-summary verification utility, not a full model-inference rerunner.

### ChronoQA Temporal-Balanced 90-Example Final Evaluation Subset

```bash
python evaluation/scripts/18_evaluate_chronoqa_90_final.py --manifest data/public_eval_subsets/chronoqa_temporal_balanced_90_final/manifest.json
```

This recomputes the revised ChronoQA metrics from the released per-example prediction file when available.

## 6. Optional model-backed runners

Optional online and batch runner utilities are located in `optional_online_runner/`. These scripts require external model/backend configuration and are not needed to verify the released paper tables. No credentials or private service configuration are included.

## 7. Stable reported artifacts

Canonical paper-aligned source files:

- `artifacts/paper_results/private_main_results_final.csv`
- `artifacts/paper_results/private_ablation_final.csv`
- `artifacts/paper_results/maven_ere_90doc_final_summary.csv`
- `artifacts/paper_results/chronoqa_90_final_summary_overall.csv`

## 8. Raw public data note

The repository does not redistribute full raw mirrors of MAVEN-ERE or ChronoQA. Please see `data/raw/public/README.md` for instructions if you want to obtain the original public datasets from their official sources.

## 8. Raw public data note

The repository does not redistribute full raw mirrors of MAVEN-ERE or ChronoQA. Please see `data/raw/public/README.md` for instructions if you want to obtain the original public datasets from their official sources.

