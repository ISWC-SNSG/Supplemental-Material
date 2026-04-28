# Reproducibility Scope

This anonymous package is designed as a paper-aligned verification package. It supports inspection of the benchmark files, fixed subset manifests, metric definitions, reported result artifacts, and evaluation utilities used in the submission.

## In scope
- Inspecting the released processed private benchmark files.
- Inspecting fixed public-subset manifests for MAVEN-ERE and ChronoQA.
- Verifying canonical table source files in `artifacts/paper_results/`.
- Recomputing ChronoQA summary metrics from the released per-example prediction file.
- Running benchmark-local baseline adapters under the shared event-logic input/output protocol.
- Inspecting metric definitions, prompt templates, and configuration files.

## Out of scope
- Official reproduction of third-party systems such as RoG, KG^2RAG, EventRAG, or E^2RAG.
- Redistribution of official third-party baseline code or full public raw dataset mirrors.
- End-to-end rerunning of model-backed online inference without external backend credentials.
- Claiming that the baseline adapters reproduce every hyperparameter, component, prompt, or engineering detail of the original systems.
- Treating the compact private benchmark as a large-scale estimate of broad-domain event-reasoning performance.

## Rationale
The repository is intentionally scoped to anonymous review. It exposes the materials needed to inspect the paper's benchmark protocol and reported results while avoiding redistribution of third-party code or raw public datasets.
