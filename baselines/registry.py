from __future__ import annotations

from typing import Callable

from . import rog_reimpl, kg2rag_reimpl, eventrag_reimpl, e2rag_reimpl

_PRIVATE_METHODS = {
    'rog_reimpl': rog_reimpl.predict,
    'kg2rag_reimpl': kg2rag_reimpl.predict,
    'eventrag_reimpl': eventrag_reimpl.predict,
    'e2rag_reimpl': e2rag_reimpl.predict,
}


def get_private_method(name: str) -> Callable:
    if name not in _PRIVATE_METHODS:
        raise KeyError(f'Unknown baseline method: {name}')
    return _PRIVATE_METHODS[name]


def list_private_methods() -> list[str]:
    return sorted(_PRIVATE_METHODS)
