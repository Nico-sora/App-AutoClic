"""Named macro storage for recorder tab."""

import json
import os
import re
from src.utils.config import _get_data_dir, _write_private

MACROS_DIR = os.path.join(_get_data_dir(), "macros")

_SAFE_NAME_RE = re.compile(r'^[\w\-. ]+$')


def _sanitize_name(name: str) -> str:
    """Sanitize macro name to prevent path traversal."""
    name = os.path.basename(name)
    name = name.replace("..", "").strip()
    if not name or not _SAFE_NAME_RE.match(name):
        raise ValueError(f"Invalid macro name: {name!r}")
    return name


def _ensure_dir():
    os.makedirs(MACROS_DIR, exist_ok=True)


def save_macro(name: str, data: list) -> None:
    name = _sanitize_name(name)
    _ensure_dir()
    path = os.path.join(MACROS_DIR, f"{name}.json")
    _write_private(path, json.dumps(data, indent=2, ensure_ascii=False))


def load_macro(name: str) -> list | None:
    name = _sanitize_name(name)
    path = os.path.join(MACROS_DIR, f"{name}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def list_macros() -> list[str]:
    _ensure_dir()
    names = []
    for f in os.listdir(MACROS_DIR):
        if f.endswith(".json"):
            names.append(f[:-5])
    return sorted(names)


def delete_macro(name: str) -> None:
    name = _sanitize_name(name)
    path = os.path.join(MACROS_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
