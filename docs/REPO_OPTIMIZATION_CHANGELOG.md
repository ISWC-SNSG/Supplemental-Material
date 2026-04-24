# Anonymous Repository Optimization Changelog

This changelog documents the repository-scope optimization performed for anonymous review.

## Strategy
The repository is scoped as an anonymous verification package rather than a full open-source engineering release. It provides benchmark files, fixed subset manifests, metric definitions, paper-aligned result artifacts, evaluation utilities, and benchmark-local baseline adapters. It does not redistribute official third-party baseline code or full raw public dataset mirrors.

## File-level changes

### Repository positioning
- `README.md`: rewritten to describe the repository as an anonymous verification package.
- `reproduction.md`: rewritten as a paper-aligned verification guide rather than a full engineering reproduction guide.
- `repo_inventory.md`: updated to reflect the revised structure and scope.
- `docs/REPRODUCIBILITY_SCOPE.md`: added to define what is in scope and out of scope.

### Baseline adapter scope
- `baselines/README.md`: renamed the concept from reimplementations to benchmark-local baseline adapters.
- `baseline_adapter_notes.md`: added as the main baseline adapter scope note; the previous `reimplementation_notes.md` was removed.
- `baselines/rog_reimpl.py`, `baselines/kg2rag_reimpl.py`, `baselines/eventrag_reimpl.py`, `baselines/e2rag_reimpl.py`: added file-level docstrings explaining that these are independent protocol-level adapters, not official implementations.
- `prompts/system_*_reimpl.txt`: added scope notes indicating that prompts represent protocol-level adapters rather than official baseline implementations.

### Public subset and result verification
- `evaluation/scripts/17_evaluate_maven_ere_90doc.py`: renamed to `evaluation/scripts/17_write_maven_ere_reported_summary.py` and relabeled as a reported-summary materialization utility.
- `evaluation/scripts/18_evaluate_chronoqa_90_final.py`: retained as the ChronoQA metric recomputation utility from per-example predictions.
- `artifacts/paper_results/RESULT_ALIGNMENT_NOTE.md`: updated to distinguish recomputable per-example artifacts from reported-summary artifacts.
- `docs/public_subset_notes.md`: updated to clarify the role of MAVEN-ERE and ChronoQA as fixed diagnostic subsets.
- `docs/dataset_overview.md`: updated to clarify released benchmark and public-subset scope.

### Optional model-backed runner isolation
- Online and batch runner scripts were moved from `scripts/` to `optional_online_runner/`.
- `optional_online_runner/README.md`: added to clarify that these scripts are optional and not required for table verification.
- `src/tsrisk/openai_runner.py`: moved to `optional_online_runner/openai_runner.py` so core package files do not expose optional backend-specific runner code.
- `.env.example`: rewritten as optional model-backed inference settings.

### Supplemental material text
- `docs/SUPPLEMENTAL_MATERIAL_STATEMENT.md`: rewritten to describe released benchmark files, fixed manifests, paper-aligned artifacts, evaluation utilities, reference baseline adapters, and non-redistribution of official third-party code or full public raw dataset mirrors.

### Makefile
- `Makefile`: updated to point to the revised verification utilities and optional online runner commands.

## Verification checks
- Maven-ERE summary materialization script runs successfully.
- ChronoQA summary recomputation from `chronoqa_90_final_per_task.csv` runs successfully.
- Legacy terms such as `reimplementation_notes.md`, `full reproduction`, and the old MAVEN script name are removed from repository documentation.
