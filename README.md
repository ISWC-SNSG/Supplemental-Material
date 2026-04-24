# Anonymous Verification Package

This repository provides an anonymous verification package for a manuscript under peer review. It is organized to support inspection of the released benchmark files, fixed public-subset manifests, metric definitions, paper-aligned result artifacts, and evaluation utilities used in the submission. It is **not** intended to be a full open-source engineering release or an official reproduction of third-party baseline systems.

## Repository Contents
- `data/techrisk_eventlogic_bench/`: released processed benchmark files for `TechRisk-EventLogic-Bench`
- `data/public_eval_subsets/`: fixed public-evaluation subset manifests used in the submission
- `src/`: reference implementation components for the proposed method and shared scoring utilities
- `baselines/`: benchmark-local baseline adapters used to document the controlled comparison protocol
- `configs/` and `prompts/`: experiment configurations and prompt templates
- `evaluation/scripts/`: evaluation utilities and paper-table materialization scripts
- `optional_online_runner/`: optional model-backed online/batch runner utilities; not required for table verification
- `artifacts/paper_results/`: canonical source files aligned with the reported paper tables
- `docs/`: dataset notes, metric protocols, subset notes, anonymity note, reproducibility scope, and supplemental-material text templates

## Benchmark Roles in the Submission
- `TechRisk-EventLogic-Bench` is the **main target-domain benchmark** used for the private-benchmark main results and ablation analysis.
- `MAVEN-ERE Causal-Temporal 90-Document Evaluation Subset` is used **only** for controlled component-level validation of local support-structure construction and causal-temporal path selection.
- `ChronoQA Temporal-Balanced 90-Example Final Evaluation Subset` is used **only** as a fixed diagnostic subset for validation of the temporal-sensitive component of path selection. The reported ChronoQA results use the metric protocol documented in `docs/chronoqa_metric_protocol.md`; the private-benchmark metrics are defined in `docs/private_metric_protocol.md`.

## Verification Entry Points
### Private benchmark scoring and table utilities
- Private benchmark scoring: `evaluation/scripts/09_score_private.py`
- Table utility: `evaluation/scripts/11_make_tables.py`
- Private benchmark baseline-adapter runner: `evaluation/scripts/16_run_private_reimpl_baselines.py`

### Public subset artifacts
- MAVEN-ERE reported-summary materialization: `evaluation/scripts/17_write_maven_ere_reported_summary.py`
- ChronoQA metric recomputation from per-example predictions: `evaluation/scripts/18_evaluate_chronoqa_90_final.py`

### Optional model-backed runners
Model-backed online and batch execution utilities are provided in `optional_online_runner/` as reference workflow scripts. They are optional and are not needed to inspect or recompute the released table artifacts where per-example predictions are available.

## Baseline Adapter Scope
The files in `baselines/` are independent benchmark-local adapters. They are not official implementations of RoG, KG^2RAG, EventRAG, or E^2RAG and are not intended to reproduce all components, hyperparameters, prompts, or engineering details of the original systems. They preserve the central retrieval or graph-reasoning bias of the corresponding methods under the shared event-logic input/output protocol used in the paper. See `baseline_adapter_notes.md` for details.

## Canonical Result Files
The following files in `artifacts/paper_results/` are the canonical source files aligned with the four main tables reported in the paper:
- `private_main_results_final.csv`: main results on the private benchmark
- `private_ablation_final.csv`: ablation study on the private benchmark
- `maven_ere_90doc_final_summary.csv`: reported summary on the MAVEN-ERE 90-document subset
- `chronoqa_90_final_summary_overall.csv`: reported results on the balanced ChronoQA 90-example final subset

Additional files in the same directory provide markdown renderings, per-group breakdowns, per-task analyses, subset summaries, or reported-summary artifacts for documentation and supplementary inspection. When per-example predictions are available, evaluation scripts recompute the corresponding summaries from those files. When only paper-aligned summaries are provided, the repository labels them as reported-summary artifacts rather than full inference reproductions.

## Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Reproduction and Verification Notes
- Use `reproduction.md` for the paper-aligned verification workflow.
- Use `baseline_adapter_notes.md` for the benchmark-local baseline-adapter scope.
- Use `docs/private_metric_protocol.md` and `docs/chronoqa_metric_protocol.md` for metric definitions.
- Use `docs/REPRODUCIBILITY_SCOPE.md` for what this anonymous package does and does not aim to reproduce.
- Full raw mirrors of the original public datasets and official third-party baseline code are **not** redistributed in this repository.

## Anonymous Review Note
This repository is prepared for anonymous peer review only. Persistent public release endpoints, final author metadata, and final licensing statements can be attached after the review stage.
