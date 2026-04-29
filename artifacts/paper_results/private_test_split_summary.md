# Private Test Split Summary

The private benchmark main and ablation results are reported on the held-out test split of `TechRisk-EventLogic-Bench`.

| Item | Count |
|---|---:|
| Total benchmark queries | 97 |
| Train queries | 40 |
| Dev queries | 21 |
| Held-out test queries | 36 |

## Held-out test uncertainty distribution

| Gold uncertainty label | Count |
|---|---:|
| certain | 27 |
| partially_supported | 8 |
| insufficient_evidence | 1 |

## Held-out test query-type distribution

| Query type | Count |
|---|---:|
| counterfactual_risk | 11 |
| impact_analysis | 6 |
| policy_escalation_reasoning | 5 |
| risk_identification | 5 |
| cause_tracing | 5 |
| timeline_reasoning | 4 |

The 36-query split is exposed through `data/techrisk_eventlogic_bench/queries.jsonl`, `data/techrisk_eventlogic_bench/queries.csv`, and the explicit manifests under `data/techrisk_eventlogic_bench/splits/`. Each test query requires answer generation, causal-temporal support-path selection, grounded rationale construction, structure-aware scoring, and support-sensitive uncertainty matching.
