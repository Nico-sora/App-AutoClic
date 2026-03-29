import json
import os
from datetime import datetime
from src.utils.config import _get_data_dir

LOG_PATH = os.path.join(_get_data_dir(), "session_log.json")


def _load_log() -> list[dict]:
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_log(entries: list[dict]) -> None:
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def add_session(click_count: int, duration_sec: float, mode: str = "autoclick") -> None:
    entries = _load_log()
    entries.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "clicks": click_count,
        "duration_sec": round(duration_sec, 1),
    })
    # Mantener solo las últimas 200 entradas
    if len(entries) > 200:
        entries = entries[-200:]
    _save_log(entries)


def get_sessions() -> list[dict]:
    return _load_log()


def clear_sessions() -> None:
    _save_log([])
