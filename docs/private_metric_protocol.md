# Private Benchmark Metric Protocol

This document defines the private-benchmark metrics used in the submitted paper. The private benchmark is designed for full-pipeline technology-security risk analysis, where each prediction contains an answer, a selected support path, a rationale, and an uncertainty label.

## Answer quality

- **Answer Char-F1** measures character-level similarity between the predicted answer and the gold answer after text normalization.
- **Strict Macro Token-F1** measures stricter token-level overlap between the predicted answer and the gold answer.

These lexical metrics are reported directly and are not replaced by the structure-aware utility metrics below.

## Path quality

Let the predicted support path for instance `i` be `P_i` and the gold support path be `G_i`.

- **Top1 Path Hit** (`H_i`) is `1` if the predicted support path contains at least one event from the gold support chain, and `0` otherwise.
- **Path Overlap F1** (`O_i`) is the set-level F1 between the predicted and gold support-event sets after order-preserving deduplication.
- **Path Exact Match** (`E_i`) is `1` if the predicted support path exactly matches the gold path after order-preserving deduplication, and `0` otherwise.

## Structure-aware utility

The composite structure-aware metrics are computed **at the instance level** and then averaged across evaluation instances. They should not be recomputed from rounded table-level aggregates.

Let `A_i` denote Answer Char-F1, `H_i` denote Top1 Path Hit, `O_i` denote Path Overlap F1, and `E_i` denote Path Exact Match for instance `i`.

The **Grounded Answer Score** is defined as:

```text
G_i = A_i * O_i
```

It rewards answers that are textually close to the gold answer and grounded in the correct support region.

The **Structure-First Score** is defined as:

```text
F_i = 0.4 * O_i + 0.2 * E_i + 0.2 * H_i + 0.2 * A_i
```

It places greater weight on support-path faithfulness while still retaining an answer-quality term. These metrics are intended as complementary measures of support-grounded reasoning quality, not as replacements for lexical answer metrics.

## Uncertainty quality

- **Uncertainty Match** is the exact match between the normalized predicted uncertainty label and the gold uncertainty label.

The main paper reports Uncertainty Match because the current benchmark is primarily designed for support-path-oriented evaluation. More detailed uncertainty calibration metrics are treated as future work in the paper's scope discussion.
