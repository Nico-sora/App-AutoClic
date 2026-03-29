import threading
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KbController

from src.core.recorder import Recording

# 47 7a 2d 32 30 32 36
BUTTON_MAP = {
    "left": Button.left,
    "middle": Button.middle,
    "right": Button.right,
}


class Player:
    def __init__(self):
        self._mouse = MouseController()
        self._kb = KbController()
        self._thread: threading.Thread | None = None
        self._running = threading.Event()

    @property
    def is_playing(self) -> bool:
        return self._running.is_set()

    def play(self, recording: Recording, *, repeat: int = 1, speed: float = 1.0,
             interval_ms: int = 0) -> None:
        if self._running.is_set():
            return
        self._running.set()
        self._thread = threading.Thread(
            target=self._loop, args=(recording, repeat, speed, interval_ms), daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()

    def _loop(self, recording: Recording, repeat: int, speed: float, interval_ms: int):
        count = 0
        infinite = repeat <= 0
        interval_sec = interval_ms / 1000.0

        while self._running.is_set() and (infinite or count < repeat):
            # Esperar intervalo entre ejecuciones (no en la primera)
            if count > 0 and interval_sec > 0:
                self._sleep(interval_sec)
                if not self._running.is_set():
                    return

            for event in recording.events:
                if not self._running.is_set():
                    return

                delay = event.delay / speed if speed > 0 else event.delay
                self._sleep(delay)

                if not self._running.is_set():
                    return

                if event.event_type == "click":
                    self._mouse.position = (event.x, event.y)
                    btn = BUTTON_MAP.get(event.button, Button.left)
                    self._mouse.click(btn)

                elif event.event_type == "move":
                    self._mouse.position = (event.x, event.y)

                elif event.event_type == "key_press":
                    self._press_key(event.key)

                elif event.event_type == "key_release":
                    self._release_key(event.key)

            count += 1

        self._running.clear()

    def _sleep(self, seconds: float) -> None:
        remaining = seconds
        while remaining > 0 and self._running.is_set():
            sleep_time = min(remaining, 0.05)
            time.sleep(sleep_time)
            remaining -= sleep_time

    def _press_key(self, key_str: str) -> None:
        k = self._resolve_key(key_str)
        if k:
            self._kb.press(k)

    def _release_key(self, key_str: str) -> None:
        k = self._resolve_key(key_str)
        if k:
            self._kb.release(k)

    @staticmethod
    def _resolve_key(key_str: str):
        if len(key_str) == 1:
            return key_str
        return getattr(Key, key_str, None)
