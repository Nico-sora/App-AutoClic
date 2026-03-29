import json
import os
import sys

DEFAULT_CONFIG = {
    "hotkey_autoclick": "F6",
    "hotkey_record": "F7",
    "hotkey_play": "F8",
    "theme": "dark",
    "language": "es",
    "countdown_seconds": 3,
    "always_on_top": False,
    "close_action": "ask",
    "notify_on_finish": True,
    "autoclick_state": {},
    "last_recording": [],
}


def _get_data_dir() -> str:
    """Return writable directory for user data (config, profiles, logs)."""
    if getattr(sys, "frozen", False):
        # Running as .exe → use %APPDATA%/AutoClic Gz (always writable)
        data_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AutoClic Gz")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    # Running in dev → two levels up from src/utils/config.py
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


CONFIG_PATH = os.path.join(_get_data_dir(), "config.json")


def load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = {**DEFAULT_CONFIG, **data}
        return merged
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
