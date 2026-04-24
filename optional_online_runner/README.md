# Optional Online / Batch Runner

This directory contains optional utilities for running model-backed generation or batch-style inference in an external environment. These utilities are **not required** for verifying the released paper tables. They are provided as reference workflow scripts only.

The anonymous review package focuses on released benchmark files, fixed subset manifests, metric definitions, paper-aligned result artifacts, and evaluation utilities. Users who wish to rerun model-backed inference should configure their own backend credentials outside this repository. No credentials, private service configuration, or vendor-specific runtime state are included.

Because these scripts depend on an external model service or local runner, their outputs may vary with backend versions and runtime settings. The canonical paper-aligned source files are stored in `artifacts/paper_results/`.
