import json
import os
import stat
import sys

_WATERMARK = bytes([0x47, 0x7A, 0x2D, 0x32, 0x30, 0x32, 0x36])  # Gz-2026

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
    "hotkey_cycle_profile": "",
    "hotkey_cycle_macro": "",
    "cycle_profile_behavior": "stop_load",
    "cycle_macro_behavior": "stop_load",
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


def _write_private(path: str, content: str) -> None:
    """Write file with owner-only permissions (0o600)."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        os.close(fd)
        raise


def save_config(config: dict) -> None:
    _write_private(CONFIG_PATH, json.dumps(config, indent=2, ensure_ascii=False))
