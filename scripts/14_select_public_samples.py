#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import quantiles

from tsrisk.utils import dump_json, ensure_dir, get_output_root, read_jsonl, write_jsonl


def proportional_allocation(group_sizes: dict[tuple, int], total: int) -> dict[tuple, int]:
    active = {key: size for key, size in group_sizes.items() if size > 0}
    if not active:
        return {}
    if total <= len(active):
        ranked = sorted(active.items(), key=lambda item: item[1], reverse=True)
        return {key: 1 if idx < total else 0 for idx, (key, _) in enumerate(ranked)}

    base = {key: 1 for key in active}
    remaining = total - len(active)
    total_size = sum(active.values())
    fractions = {}
    for key, size in active.items():
        exact = remaining * (size / total_size)
        take = min(size - 1, math.floor(exact))
        base[key] += take
        fractions[key] = exact - take
    assigned = sum(base.values())
    leftovers = total - assigned
    ranked_keys = sorted(active, key=lambda key: (fractions[key], active[key]), reverse=True)
    for key in ranked_keys:
        if leftovers <= 0:
            break
        if base[key] >= active[key]:
            continue
        base[key] += 1
        leftovers -= 1
    return base


def select_chronoqa_samples(seed: int, sampled_dir: Path, sampling_dir: Path) -> None:
    source_path = Path('data/processed/public/chronoqa/task_queries.jsonl')
    records = list(read_jsonl(source_path))
    rng = random.Random(seed)

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        meta = record.get('meta') or {}
        temporal_type = meta.get('temporal_type') or 'unknown'
        doc_setting = meta.get('reference_document_count') or 'unknown'
        grouped[(temporal_type, doc_setting)].append(record)

    allocations = proportional_allocation({key: len(items) for key, items in grouped.items()}, total=200)
    sampled: list[dict] = []
    sampled_ids: list[str] = []
    for key in sorted(grouped):
        items = list(grouped[key])
        rng.shuffle(items)
        take = allocations.get(key, 0)
        chosen = items[:take]
        sampled.extend(chosen)
        sampled_ids.extend(item['query_id'] for item in chosen)

    out_path = sampled_dir / 'chronoqa_200.jsonl'
    write_jsonl(sampled, out_path)

    temporal_counts = Counter((item.get('meta') or {}).get('temporal_type') or 'unknown' for item in sampled)
    doc_counts = Counter((item.get('meta') or {}).get('reference_document_count') or 'unknown' for item in sampled)
    strata_counts = Counter(
        (
            (item.get('meta') or {}).get('temporal_type') or 'unknown',
            (item.get('meta') or {}).get('reference_document_count') or 'unknown',
        )
        for item in sampled
    )

    manifest = {
        'dataset': 'chronoqa',
        'original_size': len(records),
        'sampled_size': len(sampled),
        'seed': seed,
        'sampling_logic': 'Proportional stratified sampling over temporal_type x reference_document_count from task_queries.jsonl.',
        'metadata_limitations': [
            'No explicit difficulty field was found in task_queries.jsonl, so difficulty balancing was not applied.',
        ],
        'selected_ids': sampled_ids,
        'counts_by_temporal_type': dict(sorted(temporal_counts.items())),
        'counts_by_reference_document_count': dict(sorted(doc_counts.items())),
        'counts_by_strata': {f'{k1}__{k2}': v for (k1, k2), v in sorted(strata_counts.items())},
        'output_file': str(out_path),
    }
    dump_json(manifest, sampling_dir / 'chronoqa_200_manifest.json')


def maven_doc_stats(record: dict, source_split: str) -> dict:
    events = record.get('events') or []
    temporal_relations = record.get('temporal_relations') or {}
    causal_relations = record.get('causal_relations') or {}
    subevent_relations = record.get('subevent_relations') or []

    event_cluster_count = len(events)
    event_mention_count = sum(len(event.get('mention') or []) for event in events)
    temporal_rel_count = sum(len(items) for items in temporal_relations.values())
    causal_rel_count = sum(len(items) for items in causal_relations.values())
    subevent_rel_count = len(subevent_relations)
    coref_link_count = sum(max(0, len(event.get('mention') or []) - 1) for event in events)
    total_structure_links = temporal_rel_count + causal_rel_count + subevent_rel_count + coref_link_count
    density = total_structure_links / max(1, event_cluster_count)

    return {
        'id': record['id'],
        'source_split': source_split,
        'title': record.get('title', ''),
        'event_cluster_count': event_cluster_count,
        'event_mention_count': event_mention_count,
        'temporal_rel_count': temporal_rel_count,
        'causal_rel_count': causal_rel_count,
        'subevent_rel_count': subevent_rel_count,
        'coref_link_count': coref_link_count,
        'total_structure_links': total_structure_links,
        'density': density,
        'eligible': causal_rel_count > 0 or subevent_rel_count > 0 or temporal_rel_count >= 2 or coref_link_count > 0,
    }


def assign_density_buckets(stats: list[dict]) -> None:
    densities = [item['density'] for item in stats]
    if len(densities) < 3:
        for item in stats:
            item['density_bucket'] = 'medium'
        return
    q1, q2 = quantiles(densities, n=3, method='inclusive')
    for item in stats:
        if item['density'] <= q1:
            item['density_bucket'] = 'low'
        elif item['density'] <= q2:
            item['density_bucket'] = 'medium'
        else:
            item['density_bucket'] = 'high'


def select_maven_samples(seed: int, sampled_dir: Path, sampling_dir: Path) -> None:
    source_files = {
        'train': Path(r'C:\Users\jianggan\Desktop\workspace\MAVEN_ERE\MAVEN_ERE\train.jsonl'),
        'valid': Path(r'C:\Users\jianggan\Desktop\workspace\MAVEN_ERE\MAVEN_ERE\valid.jsonl'),
    }
    records: list[dict] = []
    stats: list[dict] = []
    record_by_id: dict[str, dict] = {}
    for split, path in source_files.items():
        for record in read_jsonl(path):
            copied = dict(record)
            copied['source_split'] = split
            records.append(copied)
            record_by_id[copied['id']] = copied
            stats.append(maven_doc_stats(record, split))

    eligible = [item for item in stats if item['eligible']]
    assign_density_buckets(eligible)

    by_bucket: dict[str, list[dict]] = defaultdict(list)
    for item in eligible:
        by_bucket[item['density_bucket']].append(item)

    rng = random.Random(seed)
    target_by_bucket = {'low': 30, 'medium': 40, 'high': 20}
    sampled_stats: list[dict] = []
    for bucket in ('low', 'medium', 'high'):
        items = list(by_bucket.get(bucket, []))
        items.sort(
            key=lambda item: (
                item['causal_rel_count'] > 0 or item['subevent_rel_count'] > 0,
                item['total_structure_links'],
                item['event_cluster_count'],
            ),
            reverse=True,
        )
        rng.shuffle(items)
        sampled_stats.extend(items[: min(target_by_bucket[bucket], len(items))])

    if len(sampled_stats) < 90:
        selected_ids = {item['id'] for item in sampled_stats}
        remainder = [item for item in eligible if item['id'] not in selected_ids]
        remainder.sort(
            key=lambda item: (
                item['causal_rel_count'] > 0 or item['subevent_rel_count'] > 0,
                item['total_structure_links'],
                item['event_cluster_count'],
            ),
            reverse=True,
        )
        for item in remainder:
            if len(sampled_stats) >= 90:
                break
            sampled_stats.append(item)

    sampled_stats = sampled_stats[:90]
    sampled_records = []
    for item in sampled_stats:
        record = dict(record_by_id[item['id']])
        record['_sample_meta'] = {
            'density_bucket': item['density_bucket'],
            'doc_stats': {
                'event_cluster_count': item['event_cluster_count'],
                'event_mention_count': item['event_mention_count'],
                'temporal_rel_count': item['temporal_rel_count'],
                'causal_rel_count': item['causal_rel_count'],
                'subevent_rel_count': item['subevent_rel_count'],
                'coref_link_count': item['coref_link_count'],
            },
        }
        sampled_records.append(record)

    sampled_records = sorted(sampled_records, key=lambda item: item['id'])
    out_path = sampled_dir / 'maven_ere_docs_90.jsonl'
    write_jsonl(sampled_records, out_path)

    bucket_counts = Counter(item['density_bucket'] for item in sampled_stats)
    split_counts = Counter(item['source_split'] for item in sampled_stats)
    relation_presence = {
        'with_causal': sum(1 for item in sampled_stats if item['causal_rel_count'] > 0),
        'with_subevent': sum(1 for item in sampled_stats if item['subevent_rel_count'] > 0),
        'with_temporal_chain': sum(1 for item in sampled_stats if item['temporal_rel_count'] >= 2),
        'with_coref_links': sum(1 for item in sampled_stats if item['coref_link_count'] > 0),
    }
    manifest = {
        'dataset': 'maven_ere',
        'original_size_train_valid': len(records),
        'eligible_size_train_valid': len(eligible),
        'sampled_size': len(sampled_records),
        'seed': seed,
        'sampling_logic': 'Document-level sampling over train+valid only, stratified by relation-density bucket with preference for docs containing causal, subevent, temporal-chain, or coreference structure.',
        'metadata_limitations': [
            'The public test split does not expose relation labels, so the sampling pool used train+valid only.',
            'Coreference links were approximated from repeated mentions inside the same event cluster because no separate coreference field is exposed.',
        ],
        'counts_by_density_bucket': dict(sorted(bucket_counts.items())),
        'counts_by_source_split': dict(sorted(split_counts.items())),
        'relation_presence_summary': relation_presence,
        'selected_ids': [item['id'] for item in sampled_stats],
        'output_file': str(out_path),
    }
    dump_json(manifest, sampling_dir / 'maven_ere_docs_90_manifest.json')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=2026)
    args = ap.parse_args()

    sampled_dir = ensure_dir('data/sampled')
    output_root = get_output_root()
    sampling_dir = ensure_dir(output_root / 'sampling')
    logs_dir = ensure_dir(output_root / 'logs')

    select_chronoqa_samples(args.seed, sampled_dir, sampling_dir)
    select_maven_samples(args.seed, sampled_dir, sampling_dir)

    log_path = logs_dir / 'data_selection.log'
    log_path.write_text(
        (
            f'seed={args.seed}\n'
            'chronoqa_sample=data/sampled/chronoqa_200.jsonl\n'
            'chronoqa_manifest={}\n'
            'maven_sample=data/sampled/maven_ere_docs_90.jsonl\n'
            'maven_manifest={}\n'
        ).format(
            sampling_dir / 'chronoqa_200_manifest.json',
            sampling_dir / 'maven_ere_docs_90_manifest.json',
        ),
        encoding='utf-8',
    )
    print('Wrote sampled public dataset manifests to', sampling_dir)


if __name__ == '__main__':
    main()
