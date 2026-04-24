"""Optional model-backed generation utilities.

This module supports optional online or batch-style model calls for users who
want to rerun generation in their own environment. It is not required for
verifying the released paper tables, and no credentials or private service
configuration are included in this anonymous package.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from tsrisk.utils import dump_json, ensure_dir, output_path, read_jsonl

load_dotenv()

RISK_ANSWER_SCHEMA: dict[str, Any] = {
    'type': 'object',
    'properties': {
        'answer': {'type': 'string'},
        'rationale': {'type': 'string'},
        'uncertainty_label': {
            'type': 'string',
            'enum': ['fully-supported', 'partially-supported', 'insufficient-evidence'],
        },
        'selected_path_event_ids': {'type': 'array', 'items': {'type': 'string'}},
        'selected_path_relation_ids': {'type': 'array', 'items': {'type': 'string'}},
        'notes': {'type': 'string'},
    },
    'required': [
        'answer',
        'rationale',
        'uncertainty_label',
        'selected_path_event_ids',
        'selected_path_relation_ids',
        'notes',
    ],
    'additionalProperties': False,
}


def get_client() -> OpenAI:
    base_url = os.getenv('OPENAI_BASE_URL') or None
    return OpenAI(base_url=base_url)


def get_backend(default: str | None = None) -> str:
    backend = (os.getenv('TSRISK_LLM_BACKEND') or '').strip().lower()
    if backend in ('openai', 'openai_api', 'responses_api'):
        return 'openai_api'
    if backend in ('codex', 'codex_cli'):
        return 'codex_cli'
    if os.getenv('OPENAI_API_KEY'):
        return 'openai_api'
    if shutil.which('codex') and (Path.home() / '.codex' / 'auth.json').exists():
        return 'codex_cli'
    return default or 'openai_api'


def get_model(default: str | None = None) -> str:
    return os.getenv('OPENAI_MODEL', default or 'gpt-5.4')


def _responses_create_json_openai(system_prompt: str, user_prompt: str, model: str | None = None) -> dict:
    client = get_client()
    model = model or get_model()
    resp = client.responses.create(
        model=model,
        input=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        text={
            'format': {
                'type': 'json_schema',
                'name': 'risk_answer',
                'schema': {
                    'type': 'object',
                    'properties': RISK_ANSWER_SCHEMA['properties'],
                    'required': RISK_ANSWER_SCHEMA['required'],
                    'additionalProperties': RISK_ANSWER_SCHEMA['additionalProperties'],
                },
            }
        },
    )
    try:
        text = resp.output_text
    except Exception:
        text = None
        try:
            for item in resp.output:
                if hasattr(item, 'content'):
                    for c in item.content:
                        if getattr(c, 'type', None) == 'output_text':
                            text = c.text
                            break
        except Exception:
            pass
    if text is None:
        raise RuntimeError('Could not extract output_text from Responses API response')
    return json.loads(text)


def _schema_file_path() -> Path:
    tmp_dir = ensure_dir('.tmp')
    schema_path = tmp_dir / 'risk_answer_schema.json'
    schema_doc = {'$schema': 'https://json-schema.org/draft/2020-12/schema', **RISK_ANSWER_SCHEMA}
    schema_path.write_text(json.dumps(schema_doc, ensure_ascii=False, indent=2), encoding='utf-8')
    return schema_path


def _codex_prompt(system_prompt: str, user_prompt: str) -> str:
    return (
        "You are answering one benchmark item.\n"
        "Do not inspect local files.\n"
        "Do not run shell commands.\n"
        "Use only the instructions and evidence included below.\n"
        "Return exactly one JSON object that matches the provided schema.\n\n"
        "[System Prompt]\n"
        f"{system_prompt}\n\n"
        "[User Prompt]\n"
        f"{user_prompt}\n"
    )


def _responses_create_json_codex(system_prompt: str, user_prompt: str, model: str | None = None) -> dict:
    schema_path = _schema_file_path()
    tmp_dir = ensure_dir('.tmp')
    isolated_dir = ensure_dir(tmp_dir / 'codex_isolated')
    out_path = tmp_dir / f'codex_response_{uuid.uuid4().hex}.json'
    codex_bin = shutil.which('codex.cmd') or shutil.which('codex')
    if not codex_bin:
        raise RuntimeError('Could not find codex CLI executable on PATH')
    cmd = [
        codex_bin,
        'exec',
        '-C',
        str(isolated_dir.resolve()),
        '--skip-git-repo-check',
        '--ephemeral',
        '--sandbox',
        'read-only',
        '--color',
        'never',
        '--output-schema',
        str(schema_path),
        '-o',
        str(out_path),
        '-c',
        f'model_reasoning_effort="{os.getenv("CODEX_CLI_REASONING_EFFORT", "low")}"',
    ]
    codex_model = model or (os.getenv('CODEX_CLI_MODEL') or '').strip()
    if codex_model:
        cmd.extend(['-m', codex_model])
    cmd.append('-')
    proc = subprocess.run(
        cmd,
        input=_codex_prompt(system_prompt, user_prompt),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or '').strip()
        raise RuntimeError(f'codex exec failed: {msg}')
    if not out_path.exists():
        raise RuntimeError('codex exec completed without writing the schema-constrained output file')
    return json.loads(out_path.read_text(encoding='utf-8'))


def responses_create_json(system_prompt: str, user_prompt: str, model: str | None = None) -> dict:
    backend = get_backend()
    if backend == 'codex_cli':
        return _responses_create_json_codex(system_prompt, user_prompt, model=model)
    return _responses_create_json_openai(system_prompt, user_prompt, model=model)


def submit_local_batch(request_file: str | Path) -> str:
    request_file = Path(request_file)
    batch_id = f'local_{uuid.uuid4().hex[:12]}'
    batch_dir = ensure_dir(output_path('batch', 'local_jobs'))
    raw_output = batch_dir / f'{batch_id}_raw.jsonl'
    meta_path = batch_dir / f'{batch_id}.json'
    meta = {
        'batch_id': batch_id,
        'backend': 'codex_cli',
        'request_file': str(request_file),
        'raw_output_file': str(raw_output),
        'status': 'running',
        'created_at': time.time(),
    }
    dump_json(meta, meta_path)
    rows: list[dict[str, Any]] = []
    for req in read_jsonl(request_file):
        custom_id = req.get('custom_id')
        body = req.get('body', {})
        system_prompt = ''
        user_prompt = ''
        for msg in body.get('input', []):
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'system':
                system_prompt = content
            elif role == 'user':
                user_prompt = content
        try:
            pred = responses_create_json(system_prompt, user_prompt, model=body.get('model'))
            rows.append({
                'custom_id': custom_id,
                'response': {
                    'body': {
                        'output_text': json.dumps(pred, ensure_ascii=False),
                    }
                },
            })
        except Exception as exc:
            rows.append({
                'custom_id': custom_id,
                'response': {
                    'body': {
                        'error': str(exc),
                    }
                },
            })
    with raw_output.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False))
            f.write('\n')
    meta['status'] = 'completed'
    meta['completed_at'] = time.time()
    dump_json(meta, meta_path)
    return batch_id


def get_local_batch_status(batch_id: str) -> dict[str, Any]:
    meta_path = output_path('batch', 'local_jobs') / f'{batch_id}.json'
    if not meta_path.exists():
        raise FileNotFoundError(f'Local batch metadata not found: {meta_path}')
    return json.loads(meta_path.read_text(encoding='utf-8'))


def download_local_batch_output(batch_id: str, out_path: str | Path) -> Path:
    meta = get_local_batch_status(batch_id)
    raw_output = Path(meta['raw_output_file'])
    if not raw_output.exists():
        raise FileNotFoundError(f'Local batch output file not found: {raw_output}')
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(raw_output, out_path)
    return out_path
