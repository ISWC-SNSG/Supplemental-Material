from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

from .utils import write_jsonl, dump_json

CORE_SHEETS = ['cases', 'sources', 'events', 'relations', 'queries', 'paths']


def _load_sheet(xlsx_path: str | Path, sheet_name: str) -> pd.DataFrame:
    raw = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None)
    header = raw.iloc[1].tolist()
    df = raw.iloc[4:].copy()
    df.columns = header
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    # Drop fully unnamed columns if any
    keep_cols = [c for c in df.columns if isinstance(c, str) and c.strip()]
    df = df[keep_cols]
    return df


def normalize_private_workbook(xlsx_path: str | Path, output_dir: str | Path) -> Dict[str, int]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stats = {}
    for sheet in CORE_SHEETS:
        df = _load_sheet(xlsx_path, sheet)
        # Convert NaNs to None
        records = df.where(pd.notna(df), None).to_dict(orient='records')
        write_jsonl(records, output_dir / f'{sheet}.jsonl')
        df.to_csv(output_dir / f'{sheet}.csv', index=False)
        stats[sheet] = len(records)
    dump_json(stats, output_dir / 'benchmark_stats.json')
    return stats
