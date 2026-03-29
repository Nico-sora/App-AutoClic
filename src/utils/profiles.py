import json
import os
import re
from src.utils.config import _get_data_dir, _write_private

PROFILES_DIR = os.path.join(_get_data_dir(), "profiles")

_SAFE_NAME_RE = re.compile(r'^[\w\-. ]+$')


def _sanitize_name(name: str) -> str:
    """Sanitize profile name to prevent path traversal."""
    name = os.path.basename(name)
    name = name.replace("..", "").strip()
    if not name or not _SAFE_NAME_RE.match(name):
        raise ValueError(f"Invalid profile name: {name!r}")
    return name


def _ensure_dir():
    os.makedirs(PROFILES_DIR, exist_ok=True)


def save_profile(name: str, data: dict) -> None:
    name = _sanitize_name(name)
    _ensure_dir()
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    _write_private(path, json.dumps(data, indent=2, ensure_ascii=False))


def load_profile(name: str) -> dict | None:
    name = _sanitize_name(name)
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def list_profiles() -> list[str]:
    _ensure_dir()
    names = []
    for f in os.listdir(PROFILES_DIR):
        if f.endswith(".json"):
            names.append(f[:-5])
    return sorted(names)


def delete_profile(name: str) -> None:
    name = _sanitize_name(name)
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
