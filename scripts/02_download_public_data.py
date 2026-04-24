#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
import requests


def _log_note(msg: str) -> None:
    notes = Path('outputs/reports/download_notes.md')
    notes.parent.mkdir(parents=True, exist_ok=True)
    with notes.open('a', encoding='utf-8') as f:
        f.write(f'\n- {msg}\n')


def download_chronoqa(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    url = 'https://raw.githubusercontent.com/czy1999/ChronoQA/main/chronoqa.json'
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        (outdir / 'chronoqa.json').write_bytes(r.content)
        print('Downloaded ChronoQA to', outdir / 'chronoqa.json')
    except Exception as e:
        _log_note(f'ChronoQA download failed from {url}: {e}')
        print('ChronoQA download failed:', e)


def download_maven(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    repo_dir = outdir / 'maven-ere-repo'
    try:
        if not repo_dir.exists():
            subprocess.run(['git', 'clone', 'https://github.com/THU-KEG/MAVEN-ERE.git', str(repo_dir)], check=True)
        data_dir = repo_dir / 'data'
        if data_dir.exists():
            script = data_dir / 'download_maven.sh'
            if script.exists():
                subprocess.run(['bash', str(script)], cwd=str(data_dir), check=False)
        print('Prepared MAVEN-ERE repo at', repo_dir)
    except Exception as e:
        _log_note(f'MAVEN-ERE download/clone failed: {e}')
        print('MAVEN-ERE preparation failed:', e)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', choices=['chronoqa', 'maven_ere'], required=True)
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()
    outdir = Path(args.output_dir) / args.dataset
    if args.dataset == 'chronoqa':
        download_chronoqa(outdir)
    else:
        download_maven(outdir)


if __name__ == '__main__':
    main()
