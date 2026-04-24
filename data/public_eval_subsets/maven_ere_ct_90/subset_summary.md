# MAVEN-ERE 90-document subset summary

This package contains the preserved 90-document MAVEN-ERE subset used as the final paper subset reference.

## Preserved source artifact
The exact preserved artifact recovered from the prior chat/package is `original_selected_ids_manifest.json`, which contains:
- dataset: maven_ere
- sampled_size: 90
- seed: 2026
- train/valid composition: {'train': 70, 'valid': 20}
- density buckets: {'high': 20, 'low': 30, 'medium': 40}
- relation presence summary: {'with_causal': 85, 'with_subevent': 45, 'with_temporal_chain': 90, 'with_coref_links': 56}

## Final exported manifest
The file `maven_ere_90doc_final_manifest.json` contains 90 records with the required fields:
- `doc_id`
- `title`
- `mode`
- `events`
- `temp`
- `causal`
- `sub`
- `src`
- `dst`
- `gold_path`
- `gold_rels`
- `score`
- plus preserved extra field: `split`

## Three-way distribution
- causal-heavy: 30
- temporal-heavy: 30
- mixed-structure: 30

## Selection principle used for the 90-doc paper subset
The exact 90 document IDs are extracted from the preserved prior manifest and are **not re-sampled**.
Within this fixed 90-document set, the exported per-record fields are aligned to the three paper modes:
- causal-heavy documents emphasize causal/precondition structure,
- temporal-heavy documents emphasize temporal-chain structure,
- mixed-structure documents preserve both temporal and causal/subevent structure.

## Provenance note
The preserved prior artifact stores the exact 90 selected document IDs and sampling metadata.
The richer per-record JSON exported here is built over those exact selected IDs using the original MAVEN-ERE documents, while preserving the fixed 30/30/30 mode split required by the final paper setup.
