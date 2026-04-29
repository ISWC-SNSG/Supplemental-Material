# Release Inventory

## Primary release components

- `data/techrisk_eventlogic_bench/`: processed files for `TechRisk-EventLogic-Bench`.
- `data/techrisk_eventlogic_bench/splits/`: train/dev/test query-id manifests, split summary, and 36-query held-out test manifest.
- `data/public_eval_subsets/maven_ere_ct_90/`
- `data/public_eval_subsets/chronoqa_temporal_balanced_90_final/`
- `src/`
- `baselines/`
- `configs/`
- `prompts/`
- `evaluation/scripts/`
- `optional_online_runner/`
- `artifacts/paper_results/`
- `docs/`
- `docs/private_metric_protocol.md`: private-benchmark metric definitions, including structure-aware utility scores and the 36-query held-out test split scope.
- `docs/chronoqa_metric_protocol.md`: revised ChronoQA metric definitions.
- `README.md`
- `reproduction.md`
- `baseline_adapter_notes.md`

## Notes

- The repository includes processed release files for the main benchmark.
- The released private benchmark contains 97 annotated diagnostic queries, with 40 train, 21 dev, and 36 held-out test queries.
- The public-benchmark resources are released as fixed diagnostic subset manifests rather than full raw dataset mirrors.
- Stable paper-aligned result artifacts are included in `artifacts/paper_results/`.
- The baseline files are benchmark-local adapters, not official implementations of the cited systems.
- Optional model-backed online/batch scripts are isolated in `optional_online_runner/` and are not required for table verification.
