# Result Alignment Note

The files in this directory are aligned to the manuscript tables used in the anonymous submission.

## Canonical source files

- `private_main_results_final.csv`
- `private_ablation_final.csv`
- `maven_ere_90doc_final_summary.csv`
- `chronoqa_90_final_summary_overall.csv`

## Verification scope

The private-benchmark main and ablation results are aligned with the 36-query held-out private test split documented in:

- `data/techrisk_eventlogic_bench/splits/split_summary.json`
- `data/techrisk_eventlogic_bench/splits/test_query_manifest.csv`
- `artifacts/paper_results/private_test_split_summary.md`

These files are intended as paper-aligned verification artifacts. They support inspection of the reported table values and benchmark split definitions, but they are not a full model-backed reproduction of every inference run.
