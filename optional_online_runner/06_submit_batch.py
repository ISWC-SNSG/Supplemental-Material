#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from openai_runner import get_backend, submit_local_batch

load_dotenv()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--request-file', required=True)
    args = ap.parse_args()
    if get_backend() == 'codex_cli':
        batch_id = submit_local_batch(args.request_file)
        print('input_file_id=', Path(args.request_file).resolve())
        print('batch_id=', batch_id)
        return
    client = OpenAI()
    req = Path(args.request_file)
    uploaded = client.files.create(file=req.open('rb'), purpose='batch')
    batch = client.batches.create(input_file_id=uploaded.id, endpoint='/v1/responses', completion_window='24h')
    print('input_file_id=', uploaded.id)
    print('batch_id=', batch.id)


if __name__ == '__main__':
    main()
