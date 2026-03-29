"""Simple update checker for AutoClic."""

import ssl
import threading
import urllib.request
import json
from urllib.parse import urlparse

# Change this URL when you publish your app.
# It should return JSON: {"version": "1.2.0", "url": "https://..."}
UPDATE_CHECK_URL = "https://api.github.com/repos/Nico-sora/App-AutoClic/releases/latest"

ALLOWED_DOWNLOAD_HOSTS = {"github.com", "objects.githubusercontent.com"}


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
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # Support both GitHub releases API and simple JSON
            new_version = data.get("tag_name", data.get("version", "")).lstrip("v")
            download_url = data.get("html_url", data.get("url", ""))

            if new_version and _is_newer(new_version, current_version):
                if not _is_trusted_url(download_url):
                    return
                callback(new_version, download_url)
        except Exception:
            pass  # Silently fail — update check is optional

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()


def _is_trusted_url(url: str) -> bool:
    """Only allow download URLs from trusted GitHub domains."""
    try:
        parsed = urlparse(url)
        return parsed.scheme == "https" and parsed.hostname in ALLOWED_DOWNLOAD_HOSTS
    except Exception:
        return False


def _is_newer(new: str, current: str) -> bool:
    """Compare semantic version strings."""
    try:
        new_parts = [int(x) for x in new.split(".")]
        cur_parts = [int(x) for x in current.split(".")]
        return new_parts > cur_parts
    except (ValueError, AttributeError):
        return False
