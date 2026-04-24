# ChronoQA 90-example final subset report

This report uses the revised ChronoQA metric definitions:

- **Temporal Order Accuracy**: pairwise chronological consistency of the predicted support order with respect to the gold temporal order.
- **Anchor Accuracy**: exact match between predicted and gold support anchor.
- **Support Reordering Accuracy**: exact match between predicted and gold support sequence.

## Overall summary

| Method             |   Temporal Order Accuracy |   Anchor Accuracy |   Support Reordering Accuracy |
|:-------------------|--------------------------:|------------------:|------------------------------:|
| Standard RAG       |                    0.4122 |            0.3111 |                        0.2222 |
| TemporalSort       |                    0.6159 |            0.5556 |                        0.4333 |
| E$^2$RAG (reimpl.) |                    0.943  |            0.9111 |                        0.8889 |
| Ours               |                    0.9467 |            0.9222 |                        0.9    |

## By-group summary

| group           | Method             |   Temporal Order Accuracy |   Anchor Accuracy |   Support Reordering Accuracy |
|:----------------|:-------------------|--------------------------:|------------------:|------------------------------:|
| control_ordered | Standard RAG       |                    0.884  |            0.96   |                        0.68   |
| control_ordered | TemporalSort       |                    0.664  |            0.56   |                        0.52   |
| control_ordered | E$^2$RAG (reimpl.) |                    0.908  |            0.84   |                        0.84   |
| control_ordered | Ours               |                    0.908  |            0.84   |                        0.84   |
| reversed_hard   | Standard RAG       |                    0.2286 |            0.0286 |                        0.0286 |
| reversed_hard   | TemporalSort       |                    0.5571 |            0.5143 |                        0.4    |
| reversed_hard   | E$^2$RAG (reimpl.) |                    0.9571 |            0.9429 |                        0.8857 |
| reversed_hard   | Ours               |                    0.9667 |            0.9714 |                        0.9143 |
| three_ref_hard  | Standard RAG       |                    0.2333 |            0.1    |                        0.0667 |
| three_ref_hard  | TemporalSort       |                    0.6444 |            0.6    |                        0.4    |
| three_ref_hard  | E$^2$RAG (reimpl.) |                    0.9556 |            0.9333 |                        0.9333 |
| three_ref_hard  | Ours               |                    0.9556 |            0.9333 |                        0.9333 |
