# Result Alignment Note

The files in this directory are aligned to the manuscript tables used in the anonymous submission. The canonical source files for the four main reported tables are:

- `private_main_results_final.csv`
- `private_ablation_final.csv` (with `private_ablation_filled.csv` kept as a backward-compatible copy)
- `maven_ere_90doc_final_summary.csv`
- `chronoqa_90_final_summary_overall.csv` 
## Verification scope
The CSV files in this directory are canonical source files for verifying the reported table values. Private-benchmark metric definitions, including the instance-level Grounded Answer Score and Structure-First Score, are documented in `docs/private_metric_protocol.md`. When per-example prediction files are available, the evaluation scripts recompute the corresponding summaries from those files. For artifacts that are provided only as paper-aligned summaries, the repository labels them as reported-summary artifacts rather than full inference reproductions.

- ChronoQA results can be recomputed from `chronoqa_90_final_per_task.csv` using `evaluation/scripts/18_evaluate_chronoqa_90_final.py`.
- MAVEN-ERE results are released as a fixed subset manifest plus paper-aligned reported-summary artifacts; `evaluation/scripts/17_write_maven_ere_reported_summary.py` materializes the reported summary and subset mode counts for inspection.

All values, method names, and decimal formatting in the canonical files match the manuscript tables.
