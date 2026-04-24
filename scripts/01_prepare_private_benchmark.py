#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tsrisk.io_private import normalize_private_workbook


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()

    stats = normalize_private_workbook(args.input, args.output_dir)
    print('Prepared private benchmark:', stats)


if __name__ == '__main__':
    main()
