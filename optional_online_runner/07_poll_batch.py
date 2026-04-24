#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time

from dotenv import load_dotenv
from openai import OpenAI

from openai_runner import get_backend, get_local_batch_status

load_dotenv()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch-id', required=True)
    ap.add_argument('--interval', type=int, default=30)
    args = ap.parse_args()
    if get_backend() == 'codex_cli' or args.batch_id.startswith('local_'):
        status = get_local_batch_status(args.batch_id)
        print(
            'status=', status.get('status'),
            'completed=', status.get('completed_at'),
            'output_file_id=', status.get('raw_output_file'),
        )
        return
    client = OpenAI()
    while True:
        b = client.batches.retrieve(args.batch_id)
        print('status=', b.status, 'completed=', getattr(b, 'completed_at', None), 'output_file_id=', getattr(b, 'output_file_id', None))
        if b.status in ('completed', 'failed', 'cancelled', 'expired'):
            break
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
