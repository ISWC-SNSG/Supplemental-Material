#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from openai_runner import download_local_batch_output, get_backend
from tsrisk.utils import output_path

load_dotenv()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch-id', required=True)
    args = ap.parse_args()
    if get_backend() == 'codex_cli' or args.batch_id.startswith('local_'):
        out = output_path('predictions') / f'batch_{args.batch_id}.jsonl'
        download_local_batch_output(args.batch_id, out)
        print('Wrote', out)
        return
    client = OpenAI()
    b = client.batches.retrieve(args.batch_id)
    if not getattr(b, 'output_file_id', None):
        raise SystemExit('Batch has no output_file_id yet.')
    content = client.files.content(b.output_file_id)
    out = output_path('predictions') / f'batch_{args.batch_id}.jsonl'
    out.parent.mkdir(parents=True, exist_ok=True)
    data = content.read()
    out.write_bytes(data)
    print('Wrote', out)


if __name__ == '__main__':
    main()
