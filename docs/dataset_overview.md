# Dataset Overview

## Main benchmark

`TechRisk-EventLogic-Bench` is the main target-domain benchmark released in this repository. It contains processed technology-security event-logic benchmark files used for the main experiments, including case records, source records, events, relations, queries, paths, split manifests, and benchmark statistics.

The released benchmark contains 97 annotated diagnostic queries over 10 technology-security cases. The private-benchmark main and ablation results are reported on a stratified held-out test split of 36 expert-verified queries. The remaining 61 non-test instances are used for benchmark construction, protocol verification, and adapter-format checking; they are not used to select test-specific thresholds or report held-out evaluation results.

The 36-query held-out test split is exposed in two ways: through the `split` field in `data/techrisk_eventlogic_bench/queries.jsonl` and `queries.csv`, and through explicit manifests under `data/techrisk_eventlogic_bench/splits/`. The split update preserves all original query texts, gold answers, gold rationales, gold support paths, and gold uncertainty labels.

The benchmark is intended as a compact, expert-guided, verification-oriented diagnostic resource for support-path-oriented technology-security risk analysis. It supports inspection of answer quality, support-path faithfulness, provenance-grounded rationale quality, structure-aware utility, and support-sensitive uncertainty matching under the released benchmark protocol.

## Public evaluation subsets

This repository also includes two fixed public-benchmark subset manifests used for controlled component-level validation:

- `MAVEN-ERE Causal-Temporal 90-Document Evaluation Subset`
- `ChronoQA Temporal-Balanced 90-Example Final Evaluation Subset`

These public subsets are not treated as co-equal replacements for the main benchmark. They are fixed balanced diagnostic subsets used to make the reported component-level evaluations transparent.

Full raw mirrors of the original public datasets are not redistributed.
