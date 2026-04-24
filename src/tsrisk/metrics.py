from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Iterable, List, Sequence

_DASH_RE = re.compile(r'[\u2010-\u2015\u2212\u2043\uFE58\uFE63\uFF0D]+')
_SPACE_RE = re.compile(r'\s+')
_NUM_UNIT_RE = re.compile(r'(?<=\d)\s+(?=[a-zA-Z%])')
_ALNUM_SPLIT_RE = re.compile(r'(?<=[a-zA-Z])\s+(?=\d)|(?<=\d)\s+(?=[a-zA-Z])')
_TOKEN_RE = re.compile(r'[\u4e00-\u9fff]|[a-z0-9]+', re.IGNORECASE)
_YEAR_RE = re.compile(r'(19|20)\d{2}')

_CHINESE_PUNCT = (
    '，。、；：？！【】（）《》〈〉「」『』“”‘’…—～·、￥'
    '﹏﹑﹔﹕﹖﹗﹘﹙﹚﹛﹜﹝﹞｡｢｣､'
)
_EXTRA_QUOTES = "\"'`“”‘’«»‹›"
_PUNCT_TO_SPACE = {ord(ch): ' ' for ch in _CHINESE_PUNCT + _EXTRA_QUOTES}
for ch in '[](){}<>:;,./!?@#$%^&*_+=|\\-':
    _PUNCT_TO_SPACE[ord(ch)] = ' '

_DEFAULT_LABELS = ['fully-supported', 'partially-supported', 'insufficient-evidence']


def strict_normalize_text(s: str) -> str:
    s = (s or '').lower().strip()
    s = _SPACE_RE.sub(' ', s)
    return s


def normalize_text(s: str) -> str:
    s = unicodedata.normalize('NFKC', s or '')
    s = _DASH_RE.sub('-', s)
    s = s.translate(_PUNCT_TO_SPACE)
    s = s.lower()
    s = _NUM_UNIT_RE.sub('', s)
    s = _ALNUM_SPLIT_RE.sub('', s)
    s = _SPACE_RE.sub(' ', s).strip()
    return s


def compact_normalize_text(s: str) -> str:
    return normalize_text(s).replace(' ', '')


def normalize_uncertainty_label(label: str | None) -> str:
    norm = normalize_text(label or '').replace(' ', '-').replace('_', '-')
    mapping = {
        'certain': 'fully-supported',
        'fully-supported': 'fully-supported',
        'partially-supported': 'partially-supported',
        'partiallysupported': 'partially-supported',
        'insufficient-evidence': 'insufficient-evidence',
        'insufficientevidence': 'insufficient-evidence',
    }
    return mapping.get(norm, norm)


def exact_match(pred: str, gold: str) -> float:
    return 1.0 if strict_normalize_text(pred) == strict_normalize_text(gold) else 0.0


def normalized_exact_match(pred: str, gold: str) -> float:
    return 1.0 if compact_normalize_text(pred) == compact_normalize_text(gold) else 0.0


def token_f1(pred: str, gold: str) -> float:
    p = strict_normalize_text(pred).split()
    g = strict_normalize_text(gold).split()
    if not p or not g:
        return 0.0
    common = Counter(p) & Counter(g)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(p)
    recall = num_same / len(g)
    return 2 * precision * recall / (precision + recall)


def _char_tokens(s: str) -> list[str]:
    return list(compact_normalize_text(s))


def char_f1(pred: str, gold: str) -> float:
    p = _char_tokens(pred)
    g = _char_tokens(gold)
    if not p or not g:
        return 0.0
    common = Counter(p) & Counter(g)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(p)
    recall = num_same / len(g)
    return 2 * precision * recall / (precision + recall)


def contains_match(pred: str, gold: str) -> float:
    p = compact_normalize_text(pred)
    g = compact_normalize_text(gold)
    if not p or not g:
        return 0.0
    return 1.0 if p in g or g in p else 0.0


def relaxed_answer_score(pred: str, gold: str) -> float:
    return max(normalized_exact_match(pred, gold), contains_match(pred, gold), char_f1(pred, gold))


def list_hit(pred_ids: List[str], gold_ids: List[str]) -> float:
    return 1.0 if set(pred_ids) & set(gold_ids) else 0.0


def _dedupe_preserve_order(ids: Sequence[str]) -> list[str]:
    seen = set()
    out = []
    for item in ids:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def path_exact_match(pred_ids: Sequence[str], gold_ids: Sequence[str]) -> float:
    return 1.0 if list(_dedupe_preserve_order(pred_ids)) == list(_dedupe_preserve_order(gold_ids)) else 0.0


def path_overlap_f1(pred_ids: Sequence[str], gold_ids: Sequence[str]) -> float:
    p = _dedupe_preserve_order(pred_ids)
    g = _dedupe_preserve_order(gold_ids)
    if not p or not g:
        return 0.0
    pset = set(p)
    gset = set(g)
    common = len(pset & gset)
    if common == 0:
        return 0.0
    precision = common / len(pset)
    recall = common / len(gset)
    return 2 * precision * recall / (precision + recall)


def label_confusion_matrix(preds: Sequence[str], golds: Sequence[str], labels: Sequence[str] | None = None) -> dict[str, dict[str, int]]:
    labels = [normalize_uncertainty_label(x) for x in (labels or _DEFAULT_LABELS)]
    matrix = {gold: {pred: 0 for pred in labels} for gold in labels}
    for pred, gold in zip(preds, golds):
        pred_norm = normalize_uncertainty_label(pred)
        gold_norm = normalize_uncertainty_label(gold)
        if gold_norm not in matrix:
            matrix[gold_norm] = {lab: 0 for lab in labels}
        if pred_norm not in matrix[gold_norm]:
            for row in matrix.values():
                row.setdefault(pred_norm, 0)
        matrix[gold_norm][pred_norm] += 1
    return matrix


def label_macro_f1(preds: Sequence[str], golds: Sequence[str], labels: Sequence[str] | None = None) -> float:
    labels = [normalize_uncertainty_label(x) for x in (labels or _DEFAULT_LABELS)]
    pred_norm = [normalize_uncertainty_label(x) for x in preds]
    gold_norm = [normalize_uncertainty_label(x) for x in golds]
    if not gold_norm:
        return 0.0
    f1s = []
    for label in labels:
        tp = sum(1 for p, g in zip(pred_norm, gold_norm) if p == label and g == label)
        fp = sum(1 for p, g in zip(pred_norm, gold_norm) if p == label and g != label)
        fn = sum(1 for p, g in zip(pred_norm, gold_norm) if p != label and g == label)
        if tp == 0 and fp == 0 and fn == 0:
            f1s.append(0.0)
            continue
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * precision * recall / (precision + recall) if (precision + recall) else 0.0)
    return sum(f1s) / len(f1s) if f1s else 0.0


def extract_years(text: str | None) -> list[int]:
    years = []
    for match in _YEAR_RE.finditer(text or ''):
        years.append(int(match.group(0)))
    return years


def keyword_tokens(text: str | None) -> list[str]:
    return _TOKEN_RE.findall(normalize_text(text or ''))
