import threading
import time
import random
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KbController


_ORIGIN = "Gz-2026"

BUTTON_MAP = {
    "left": Button.left,
    "middle": Button.middle,
    "right": Button.right,
    "x1": Button.x1,
    "x2": Button.x2,
}


class Clicker:
    def __init__(self):
        self._mouse = MouseController()
        self._kb = KbController()
        self._thread: threading.Thread | None = None
        self._running = threading.Event()
        self.click_count = 0

    @property
    def is_running(self) -> bool:
        return self._running.is_set()

    def start(
        self,
        *,
        button: str = "left",
        custom_key: str | None = None,
        interval_ms: int = 100,
        duration_ms: int = 0,
        fixed_pos: tuple[int, int] | None = None,
        click_type: str = "simple",
        random_zone: tuple[int, int, int, int] | None = None,
        random_interval_ms: int = 0,
    ) -> None:
        if self._running.is_set():
            return
        self.click_count = 0
        self._running.set()
        self._thread = threading.Thread(
            target=self._loop,
            args=(button, custom_key, interval_ms, duration_ms, fixed_pos,
                  click_type, random_zone, random_interval_ms),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()

    def _loop(self, button, custom_key, interval_ms, duration_ms, fixed_pos,
              click_type, random_zone, random_interval_ms):
        interval = interval_ms / 1000.0
        start_time = time.perf_counter()
        click_count_map = {"single": 1, "double": 2, "triple": 3}
        n_clicks = click_count_map.get(click_type, 1)

        while self._running.is_set():
            if duration_ms > 0:
                elapsed = (time.perf_counter() - start_time) * 1000
                if elapsed >= duration_ms:
                    break

            # Posición
            if random_zone:
                x1, y1, x2, y2 = random_zone
                rx = random.randint(min(x1, x2), max(x1, x2))
                ry = random.randint(min(y1, y2), max(y1, y2))
                self._mouse.position = (rx, ry)
            elif fixed_pos:
                self._mouse.position = fixed_pos

            # Acción
            if custom_key:
                self._press_key(custom_key)
                self.click_count += 1
            else:
                btn = BUTTON_MAP.get(button, Button.left)
                self._mouse.click(btn, n_clicks)
                self.click_count += 1

            # Intervalo con variación aleatoria
            if random_interval_ms > 0:
                variation = random.randint(-random_interval_ms, random_interval_ms) / 1000.0
                actual_interval = max(0.01, interval + variation)
            else:
                actual_interval = interval

            remaining = actual_interval
            while remaining > 0 and self._running.is_set():
                sleep_time = min(remaining, 0.05)
                time.sleep(sleep_time)
                remaining -= sleep_time

        self._running.clear()

    def _press_key(self, key_str: str) -> None:
        if len(key_str) == 1:
            self._kb.press(key_str)
            self._kb.release(key_str)
        else:
            try:
                k = getattr(Key, key_str.lower(), None)
                if k:
                    self._kb.press(k)
                    self._kb.release(k)
            except Exception:
                pass
