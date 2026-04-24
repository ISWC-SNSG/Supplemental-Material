from __future__ import annotations

from pathlib import Path
import pandas as pd


def _to_markdown_fallback(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    lines = [
        '| ' + ' | '.join(cols) + ' |',
        '| ' + ' | '.join(['---'] * len(cols)) + ' |',
    ]
    for _, row in df.iterrows():
        vals = []
        for col in df.columns:
            val = row[col]
            text = '' if pd.isna(val) else str(val)
            text = text.replace('\n', ' ').replace('|', '\\|')
            vals.append(text)
        lines.append('| ' + ' | '.join(vals) + ' |')
    return '\n'.join(lines)


def save_table(df: pd.DataFrame, out_csv: str | Path, out_md: str | Path) -> None:
    out_csv = Path(out_csv); out_md = Path(out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    try:
        markdown = df.to_markdown(index=False)
    except ImportError:
        markdown = _to_markdown_fallback(df)
    out_md.write_text(markdown, encoding='utf-8')
