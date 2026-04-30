# Dataset Overview

## Main benchmark

`TechRisk-EventLogic-Bench` is the main target-domain benchmark released in this repository. It contains processed technology-security event-logic benchmark files used for the main experiments, including case records, source records, events, relations, queries, paths, and benchmark statistics.

The benchmark is intended as a compact, expert-verified, verification-oriented diagnostic resource for support-path-oriented technology-security risk analysis. It supports inspection of answer quality, support-path faithfulness, provenance-grounded rationale quality, and support-sensitive uncertainty matching under the released benchmark protocol.

The released benchmark contains 97 annotated query-support instances: 40 train, 21 dev, and 36 held-out private test queries. The held-out test split is used for the reported private main and ablation results. Non-test instances are used for benchmark construction, protocol verification, and adapter-format checking; they are not used to select test-specific thresholds or report held-out evaluation results.

## Public evaluation subsets

This repository also includes two fixed public-benchmark subset manifests used for controlled component-level validation:

- `MAVEN-ERE Causal-Temporal 90-Document Evaluation Subset`
- `ChronoQA Temporal-Balanced 90-Example Final Evaluation Subset`

These public subsets are not treated as co-equal replacements for the main benchmark. They are fixed balanced diagnostic subsets used to make the reported component-level evaluations transparent.

Full raw mirrors of the original public datasets are not redistributed.
