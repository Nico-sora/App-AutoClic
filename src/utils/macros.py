"""Named macro storage for recorder tab."""

import json
import os
from src.utils.config import _get_data_dir

MACROS_DIR = os.path.join(_get_data_dir(), "macros")


def _ensure_dir():
    os.makedirs(MACROS_DIR, exist_ok=True)


def save_macro(name: str, data: list) -> None:
    _ensure_dir()
    path = os.path.join(MACROS_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_macro(name: str) -> list | None:
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
    path = os.path.join(MACROS_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
