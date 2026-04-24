from __future__ import annotations

from typing import Iterable, Sequence

from .metrics import normalize_text, normalize_uncertainty_label

DEFAULT_LABEL = 'partially-supported'

_INSUFFICIENT_CUES = [
    'insufficient evidence',
    'missing evidence',
    'no evidence',
    'no supporting evidence',
    'not enough evidence',
    'no selected path',
    'no supplied relation',
]

_INDIRECT_CUES = [
    'counterfactual',
    'inferred',
    'inferential',
    'indirect',
    'not explicit',
    'not directly',
    'not fully',
    'partly supported',
    'partially supported',
    'would likely',
    'would still',
    'does not quantify',
    'does not provide the full facts',
    'broader context',
    'somewhat inferential',
    'not explicitly proven',
    'not explicitly stated',
    'not a direct relation',
    'no candidate supporting path',
    'not listed candidate path',
]

_DIRECT_CUES = [
    'direct evidence supports',
    'direct path evidence supports',
    'evidence supports',
    'clearly supports',
    'explicitly supports',
    'directly grounded',
    'direct path evidence',
]


def _normalize_query_type(query_type: str | None) -> str:
    return normalize_text(query_type or '').replace(' ', '_').replace('-', '_')


def _normalize_cues(cues: Iterable[str]) -> list[str]:
    return [normalize_text(cue) for cue in cues]


_INSUFFICIENT_CUES_NORM = _normalize_cues(_INSUFFICIENT_CUES)
_INDIRECT_CUES_NORM = _normalize_cues(_INDIRECT_CUES)
_DIRECT_CUES_NORM = _normalize_cues(_DIRECT_CUES)


def _contains_any(text: str, cues: Sequence[str]) -> bool:
    return any(cue and cue in text for cue in cues)


def calibrate_uncertainty_label(
    *,
    query_type: str | None,
    predicted_label: str | None,
    selected_path_event_ids: Sequence[str] | None,
    notes: str | None = None,
    rationale: str | None = None,
    answer: str | None = None,
) -> tuple[str, str]:
    pred = normalize_uncertainty_label(predicted_label or '')
    query_type_norm = _normalize_query_type(query_type)
    path_ids = [x for x in (selected_path_event_ids or []) if x]
    path_count = len(path_ids)
    evidence_text = normalize_text(' '.join([notes or '', rationale or '', answer or '']))

    has_insufficient = _contains_any(evidence_text, _INSUFFICIENT_CUES_NORM)
    has_indirect = _contains_any(evidence_text, _INDIRECT_CUES_NORM)
    has_direct = _contains_any(evidence_text, _DIRECT_CUES_NORM)

    if path_count == 0:
        if has_direct:
            return 'partially-supported', 'No selected path was returned, so full support is downgraded to partial support.'
        return 'insufficient-evidence', 'No selected path was returned for this answer.'

    if query_type_norm == 'counterfactual_risk':
        if has_insufficient or has_indirect:
            return 'partially-supported', 'Counterfactual answer relies on inferred or indirect support cues.'
        if has_direct:
            return 'fully-supported', 'Counterfactual answer has direct support cues and at least one selected path.'
        if pred == 'fully-supported':
            return 'partially-supported', 'Counterfactual answers default to partial support unless direct support cues are present.'
        if pred in ('partially-supported', 'insufficient-evidence'):
            return pred, 'Original counterfactual uncertainty label retained.'
        return DEFAULT_LABEL, 'Counterfactual answer defaulted to partial support.'

    if has_insufficient:
        return 'partially-supported', 'Notes/rationale mention missing or non-direct support despite having a selected path.'

    if pred == 'insufficient-evidence':
        if has_direct:
            return 'partially-supported', 'A selected path exists and direct support cues are present, so the original label was overly cautious.'
        return 'partially-supported', 'A selected path exists, so the answer is at least partially supported.'

    if has_indirect:
        return 'partially-supported', 'Notes/rationale contain inferential or weak-support cues.'

    if pred == 'partially-supported' and has_direct:
        return 'fully-supported', 'Direct support cues with a selected path upgrade partial support to full support.'

    if pred == 'fully-supported':
        return pred, 'Original fully-supported label retained.'
    if pred == 'partially-supported':
        return pred, 'Original partially-supported label retained.'
    return 'fully-supported', 'Selected path exists and no weak-support cues were found.'


def append_calibration_note(notes: str | None, reason: str, old_label: str | None, new_label: str) -> str:
    base = (notes or '').strip()
    message = f'uncertainty_calibration: {normalize_uncertainty_label(old_label or "") or "unknown"} -> {new_label}; {reason}'
    if not base:
        return message
    if message in base:
        return base
    return f'{base} | {message}'
