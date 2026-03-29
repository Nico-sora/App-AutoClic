"""Simple update checker for AutoClic."""

import threading
import urllib.request
import json

# Change this URL when you publish your app.
# It should return JSON: {"version": "1.2.0", "url": "https://..."}
UPDATE_CHECK_URL = "https://api.github.com/repos/YOUR_USER/AutoClic/releases/latest"


def check_for_update(current_version: str, callback: callable):
    """Check for updates in a background thread.

    callback(new_version, download_url) is called on the main thread if
    an update is available. If no update or error, callback is not called.
    """

    def _check():
        try:
            req = urllib.request.Request(
                UPDATE_CHECK_URL,
                headers={"User-Agent": "AutoClic-UpdateChecker"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # Support both GitHub releases API and simple JSON
            new_version = data.get("tag_name", data.get("version", "")).lstrip("v")
            download_url = data.get("html_url", data.get("url", ""))

            if new_version and _is_newer(new_version, current_version):
                callback(new_version, download_url)
        except Exception:
            pass  # Silently fail — update check is optional

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()


def _is_newer(new: str, current: str) -> bool:
    """Compare semantic version strings."""
    try:
        new_parts = [int(x) for x in new.split(".")]
        cur_parts = [int(x) for x in current.split(".")]
        return new_parts > cur_parts
    except (ValueError, AttributeError):
        return False
