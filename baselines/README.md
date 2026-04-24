# Benchmark-Local Baseline Adapters

This directory contains independent benchmark-local baseline adapters used to document the controlled comparison protocol in the paper.

## Included adapters
- `RoG (reimpl.)`
- `KG^2RAG (reimpl.)`
- `EventRAG (reimpl.)`
- `E^2RAG (reimpl.)`
- `TemporalSort` (ChronoQA only)

## Scope
These adapters are **not** official implementations of the cited systems and are not intended to reproduce every component, hyperparameter, prompt, or engineering detail of the original papers. They are independent protocol-level adaptations that preserve the central retrieval or graph-reasoning bias of each method while aligning all methods with the same event-logic input/output format used by this benchmark.

The paper uses the suffix `(reimpl.)` to indicate that these are benchmark-local adaptations rather than official releases from the original authors.
