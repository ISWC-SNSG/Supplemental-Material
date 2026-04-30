# Private Path-Recovery Breakdown

This note documents the held-out private test split used for the private-benchmark main results and ablation results. It is intended as a paper-aligned diagnostic aid for interpreting the reported path-level metrics, especially Path Overlap F1 and Path Exact Match.

## Scope

- Benchmark: `TechRisk-EventLogic-Bench`
- Total annotated query-support instances: 97
- Split: 40 train / 21 dev / 36 held-out test
- Role of this file: document the held-out test split, support-path length distribution, and split-level diagnostic coverage used to contextualize path-recovery results.
- Non-goal: this file is not a new benchmark claim, a new evaluation table, or a replacement for the paper-reported metrics.

The private test split is compact and diagnostic. Its purpose is to support instance-level inspection of graph-grounded support-path recovery under the paper's event-logic protocol, rather than to provide a large-scale estimate of broad-domain event-reasoning performance.

## Paper-aligned reported path metrics

The paper reports the following path-level results for the full method on the private 36-query held-out split.

| Method | Top1 Path Hit | Path Overlap F1 | Path Exact Match |
|---|---:|---:|---:|
| Ours | 1.0000 | 1.0000 | 1.0000 |

These values should be interpreted under the controlled diagnostic protocol described in the paper. They indicate recovery of benchmark-defined compact support paths under shared normalized query constraints and manually verified event-graph annotations. They should not be interpreted as open-world perfect event reasoning or as evidence that missing causal-temporal event chains can be inferred reliably from raw text without structured event-graph priors.

## Held-out test split distribution

### Query type distribution

| Query type | # test queries |
|---|---:|
| counterfactual_risk | 11 |
| impact_analysis | 6 |
| cause_tracing | 5 |
| policy_escalation_reasoning | 5 |
| risk_identification | 5 |
| timeline_reasoning | 4 |
| **Total** | **36** |

### Difficulty distribution

| Difficulty | # test queries |
|---|---:|
| hard | 18 |
| medium | 13 |
| easy | 5 |
| **Total** | **36** |

### Case distribution

| Case ID | # test queries |
|---|---:|
| CASE_ADVCTRL_001 | 5 |
| CASE_IMPSEC_001 | 4 |
| CASE_SMIC_001 | 4 |
| CASE_VEU_001 | 4 |
| CASE_FOUNDRY_001 | 4 |
| CASE_COVSEM_001 | 3 |
| CASE_CXMT_001 | 3 |
| CASE_EL25_001 | 3 |
| CASE_HUAWEI_001 | 3 |
| CASE_YMTC_001 | 3 |
| **Total** | **36** |

### Target risk-dimension distribution

The held-out query manifest includes a `target_risk_dimension` field for each test query. The distribution is:

| Target risk dimension | # test queries |
|---|---:|
| compliance_enforcement_risk | 15 |
| technology_access_risk | 11 |
| market_access_risk | 7 |
| supply_chain_disruption_risk | 3 |
| **Total** | **36** |

### Uncertainty-label distribution

| Gold uncertainty label | # test queries |
|---|---:|
| certain | 27 |
| partially_supported | 8 |
| insufficient_evidence | 1 |
| **Total** | **36** |

This distribution is provided for transparency. The paper interprets Uncertainty Match as support-sensitive evidence-sufficiency label agreement under the released benchmark protocol, not as a general confidence-calibration metric over balanced uncertainty categories.

## Gold support-path length distribution

The held-out gold support paths have an average length of 2.17 events and range from 1 to 4 events.

| Gold support-path length | # test queries | Share |
|---:|---:|---:|
| 1 event | 6 | 16.7% |
| 2 events | 20 | 55.6% |
| 3 events | 8 | 22.2% |
| 4 events | 2 | 5.6% |
| **Total** | **36** | **100.0%** |

This distribution clarifies that Path Exact Match is evaluated over short but non-uniform causal-temporal chains rather than a single fixed path template.

## Path-recovery consistency by support-path length

Because the paper-reported full method obtains Path Overlap F1 = 1.0000 and Path Exact Match = 1.0000 over the full held-out test split, the following table documents the corresponding consistency check by gold support-path length. This table is not an additional independently tuned result; it is a split-level breakdown of the reported path-level outcome.

| Gold support-path length | # test queries | Ours Path Overlap F1 | Ours Path Exact Match |
|---:|---:|---:|---:|
| 1 event | 6 | 1.0000 | 1.0000 |
| 2 events | 20 | 1.0000 | 1.0000 |
| 3 events | 8 | 1.0000 | 1.0000 |
| 4 events | 2 | 1.0000 | 1.0000 |
| **All** | **36** | **1.0000** | **1.0000** |

The purpose of this breakdown is to make the diagnostic scope of the perfect path-level scores explicit: exact recovery is reported under normalized query constraints, typed event-graph annotations, and compact annotated support paths. It is not a claim of statistically generalizable open-domain path recovery.

## Notes for reviewers

- The main and ablation results use the 36-query held-out test split.
- Non-test instances are used for benchmark construction, protocol verification, and adapter-format checking; they are not used to select test-specific thresholds or to report held-out evaluation results.
- The benchmark-local adapters are intended for protocol-level comparison under shared event-logic inputs, not as official reproductions of the cited systems in their native settings.
- Per-instance files and paper-aligned result artifacts in the repository support inspection of the reported metrics.

## Source files

This note is aligned with the following repository files:

- `data/techrisk_eventlogic_bench/splits/split_summary.json`
- `data/techrisk_eventlogic_bench/splits/test_query_manifest.csv`
- `data/techrisk_eventlogic_bench/paths.jsonl`
- `artifacts/paper_results/private_main_results_final.csv`
- `artifacts/paper_results/private_ablation_final.csv`
