# ChronoQA Metric Protocol (Final 90-Example Release)

This repository uses the following ChronoQA metric definitions for the fixed 90-example final diagnostic subset.

## Temporal Order Accuracy
Temporal Order Accuracy is defined as the **pairwise chronological consistency** of the predicted support order with respect to the gold temporal order.
For each example, all ordered event pairs implied by `gold_order` are compared against the relative positions of the same items in `pred_order`.

## Anchor Accuracy
Anchor Accuracy is defined as the **exact match** between `pred_anchor` and `gold_anchor`.

## Support Reordering Accuracy
Support Reordering Accuracy is defined as the **exact match** between `pred_order` and `gold_order`.

## Motivation
These definitions deliberately separate three different capabilities:
- selecting the correct temporal anchor,
- preserving pairwise chronological consistency,
- recovering the exact support sequence.
