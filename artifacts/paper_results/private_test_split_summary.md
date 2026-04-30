# Private Test Split Summary

The private main and ablation results are reported on the 36-query held-out private test split.

## Split counts

| Item | Count |
|---|---:|
| Total benchmark queries | 97 |
| Train queries | 40 |
| Dev queries | 21 |
| Held-out test queries | 36 |

## Test uncertainty distribution

| Label | Count |
|---|---:|
| certain | 27 |
| partially_supported | 8 |
| insufficient_evidence | 1 |

## Test query-type distribution

| Query type | Count |
|---|---:|
| cause_tracing | 5 |
| counterfactual_risk | 11 |
| impact_analysis | 6 |
| policy_escalation_reasoning | 5 |
| risk_identification | 5 |
| timeline_reasoning | 4 |

## Test difficulty distribution

| Difficulty | Count |
|---|---:|
| easy | 5 |
| medium | 13 |
| hard | 18 |

## Test case distribution

| Case ID | Count |
|---|---:|
| CASE_ADVCTRL_001 | 5 |
| CASE_COVSEM_001 | 3 |
| CASE_CXMT_001 | 3 |
| CASE_EL25_001 | 3 |
| CASE_FOUNDRY_001 | 4 |
| CASE_HUAWEI_001 | 3 |
| CASE_IMPSEC_001 | 4 |
| CASE_SMIC_001 | 4 |
| CASE_VEU_001 | 4 |
| CASE_YMTC_001 | 3 |

## Scope note

The revised split changes only split assignments. It preserves the original gold answers, support paths, rationales, and uncertainty labels. Non-test instances are used for benchmark construction, protocol verification, and adapter-format checking, not for selecting test-specific thresholds.
