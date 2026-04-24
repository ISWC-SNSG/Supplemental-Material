from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, Iterator

import orjson
import yaml


def read_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_output_root(default: str = 'outputs') -> Path:
    root = os.getenv('TSRISK_OUTPUT_ROOT', default)
    return ensure_dir(root)


def output_path(*parts: str) -> Path:
    root = get_output_root()
    p = root
    for part in parts:
        p = p / part
    return p


def write_jsonl(items: Iterable[dict[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        for item in items:
            f.write(orjson.dumps(item))
            f.write(b'\n')


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path, 'rb') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield orjson.loads(line)


def dump_json(obj: Any, path: str | Path, indent: int = 2) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
