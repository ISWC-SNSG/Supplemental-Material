# TechRisk-EventLogic-Bench Split Manifests

This directory exposes the query-level split used by the private benchmark protocol.

The processed benchmark contains 97 annotated diagnostic queries. The revised split is:

| Split | Queries | Role |
|---|---:|---|
| train | 40 | benchmark construction, protocol verification, and adapter-format checking |
| dev | 21 | development/protocol checking without test-specific threshold selection |
| test | 36 | held-out diagnostic evaluation for the private-benchmark main and ablation results |

The file `test_query_manifest.csv` lists the 36 held-out test queries with their case, query type, difficulty level, uncertainty label, target risk dimension, and gold support-path identifier. The split update preserves all original query texts, gold answers, gold rationales, gold support paths, and gold uncertainty labels; only the split assignments are revised.
