# Private Benchmark Metric Protocol

This document defines the private-benchmark metrics used in the submitted paper. The private benchmark is designed for full-pipeline technology-security risk analysis, where each prediction contains an answer, a selected support path, a rationale, and an uncertainty label. The private benchmark is a compact, support-path-oriented diagnostic benchmark.

The private main and ablation tables are computed on the 36-query held-out private test split defined by the query-level `split` field and the explicit split manifests under `data/techrisk_eventlogic_bench/splits/`. Metrics are computed at the instance level and then averaged over the 36 held-out test instances.

The metrics below are intended to support inspection of answer quality, support-path faithfulness, structure-aware utility, and support-sensitive uncertainty matching under the released benchmark protocol. They should not be interpreted as broad calibration metrics or as large-scale estimates of open-domain event-reasoning performance.

## Answer quality

- **Answer Char-F1** measures character-level similarity between the predicted answer and the gold answer after text normalization.
- **Strict Macro Token-F1** measures stricter token-level overlap between the predicted answer and the gold answer.

These lexical metrics are reported directly and are not replaced by the structure-aware utility metrics below.

## Path quality

Let the predicted support path for instance `i` be `P_i` and the gold support path be `G_i`.

- **Top1 Path Hit** (`H_i`) is `1` if the predicted support path contains at least one event from the gold support chain, and `0` otherwise.
- **Path Overlap F1** (`O_i`) is the set-level F1 between the predicted and gold support-event sets after order-preserving deduplication.
- **Path Exact Match** (`E_i`) is `1` if the predicted support path exactly matches the gold path after order-preserving deduplication, and `0` otherwise.

Path metrics evaluate the selected support path predicted by each method. The path editor used by the proposed method does not access gold support paths, gold rationales, or gold answers during inference.

## Structure-aware utility

The composite structure-aware metrics are computed **at the instance level** and then averaged across evaluation instances. They should not be recomputed from rounded table-level aggregates.

Let `Q_i` denote the instance-level answer-quality score used for composite scoring. In the released paper-aligned private-benchmark results, `Q_i` is computed from Answer Char-F1 after the same text normalization used by the private benchmark scorer.

Let `H_i`, `O_i`, and `E_i` denote Top1 Path Hit, Path Overlap F1, and Path Exact Match for instance `i`.

The **Grounded Answer Score** is defined as:

```text
G_i = Q_i * O_i
```

It rewards answers that are textually close to the gold answer and grounded in the correct support region.

The **Structure-First Score** is defined as:

```text
F_i = 0.4 * O_i + 0.2 * E_i + 0.2 * H_i + 0.2 * Q_i
```

It places greater weight on support-path faithfulness while still retaining an answer-quality term.

These metrics are intended as complementary measures of support-grounded reasoning quality, not as replacements for lexical answer metrics.

## Uncertainty quality

- **Uncertainty Match** is the exact match between the normalized predicted uncertainty label and the gold uncertainty label.

The main paper reports Uncertainty Match because the current benchmark is primarily designed for support-path-oriented evaluation. The revised 36-query held-out test split includes `certain`, `partially_supported`, and `insufficient_evidence` instances, but the split remains compact and should not be used to support broad calibration claims over balanced uncertainty categories. Uncertainty Match should therefore be interpreted as support-sensitive label matching under the released benchmark protocol, while broader uncertainty calibration is treated as future work in the paper's scope discussion.

## Reporting notes

- The private main and ablation tables are computed on the 36-query held-out private test split.
- The non-test instances are used for benchmark construction, protocol verification, and adapter-format checking; they are not used to select test-specific thresholds or to report held-out evaluation results.
- The scoring weights, relation-confidence threshold, path-length budget, path-editing rules, and uncertainty-decision rules are fixed globally for each method configuration rather than adjusted per instance or selected on the held-out test split.
