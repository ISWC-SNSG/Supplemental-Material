#!/usr/bin/env python3
from __future__ import annotations

import argparse, json
from pathlib import Path

from tsrisk.utils import read_jsonl, write_jsonl


def extract_text_from_body(body: dict):
    if 'output_text' in body and body['output_text']:
        return body['output_text']
    try:
        for item in body.get('output', []):
            for c in item.get('content', []):
                if c.get('type') == 'output_text':
                    return c.get('text')
    except Exception:
        pass
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    rows = []
    for rec in read_jsonl(args.input):
        custom_id = rec.get('custom_id')
        body = rec.get('response', {}).get('body', {})
        text = extract_text_from_body(body)
        if text is None:
            rows.append({'query_id': custom_id, 'parse_failed': True, 'raw_body': body})
            continue
        try:
            obj = json.loads(text)
            obj['query_id'] = custom_id
            rows.append(obj)
        except Exception:
            rows.append({'query_id': custom_id, 'parse_failed': True, 'raw_text': text})
    write_jsonl(rows, args.output)
    print('Wrote normalized predictions to', args.output)


if __name__ == '__main__':
    main()
