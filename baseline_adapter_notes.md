# Benchmark-Local Baseline Adapter Notes

## Naming convention in the paper

The manuscript refers to the stronger baselines as:

- `RoG (reimpl.)`
- `KG^2RAG (reimpl.)`
- `EventRAG (reimpl.)`
- `E^2RAG (reimpl.)`

## Interpretation of `(reimpl.)`

The cited systems were not originally designed for the private technology-security benchmark or for the exact event-logic input/output protocol used in this repository.

The released files therefore provide benchmark-local adapters: independent protocol-level adaptations used to instantiate the central retrieval or graph-reasoning bias of each baseline under a shared evaluation protocol. These adapters are not official implementations and should not be read as complete reproductions of the original systems. Official third-party code, model weights, prompts, and full engineering pipelines are not redistributed.

Accordingly, the comparison should be interpreted as a protocol-level comparison under shared event-logic inputs, rather than as a complete ranking of the original systems in their native settings.

## Adapter principles

1. Preserve the central retrieval or graph-reasoning bias of the source method.
2. Align all methods with the same event-logic input format and scoring protocol.
3. Use the same output schema for answer, rationale, support path, and uncertainty label whenever applicable.
4. Avoid method-specific access to gold support paths, gold rationales, gold answers, or evaluation labels during inference.
5. Avoid benchmark-specific prompt tuning that would make one baseline incomparable to the others.
6. Report the released files as benchmark-local adapters rather than official reproductions.

## Adapter-specific notes

### RoG (reimpl.)

Instantiates a path-as-plan preference over retrieved event candidates, favoring concise relation paths as reasoning plans.

### KG^2RAG (reimpl.)

Instantiates seed retrieval followed by graph-guided neighborhood expansion and organized local evidence selection.

### EventRAG (reimpl.)

Instantiates event-centric retrieval and path selection with lightweight temporal preference over event-focused candidates.

### E^2RAG (reimpl.)

Instantiates entity-event dual-bias path ranking by jointly modeling event progression and entity anchoring.
