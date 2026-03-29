import time
import threading
from dataclasses import dataclass, field
from pynput import mouse, keyboard


@dataclass
class RecordedEvent:
    event_type: str  # "click", "move", "key_press", "key_release"
    timestamp: float = 0.0
    x: int = 0
    y: int = 0
    button: str = ""
    key: str = ""
    delay: float = 0.0  # delay desde el evento anterior

    def description(self) -> str:
        from src.utils.i18n import t
        if self.event_type == "click":
            return t("ev_click", btn=self.button, x=self.x, y=self.y)
        elif self.event_type == "move":
            return t("ev_move", x=self.x, y=self.y)
        elif self.event_type == "key_press":
            return t("ev_key_press", key=self.key)
        elif self.event_type == "key_release":
            return t("ev_key_release", key=self.key)
        return self.event_type


@dataclass
class Recording:
    events: list[RecordedEvent] = field(default_factory=list)

    def to_list(self) -> list[dict]:
        return [
            {
                "event_type": e.event_type,
                "x": e.x,
                "y": e.y,
                "button": e.button,
                "key": e.key,
                "delay": e.delay,
            }
            for e in self.events
        ]

    @classmethod
    def from_list(cls, data: list[dict]) -> "Recording":
        events = []
        for d in data:
            events.append(RecordedEvent(**d))
        return cls(events=events)


class Recorder:
    def __init__(self):
        self._recording = Recording()
        self._mouse_listener: mouse.Listener | None = None
        self._kb_listener: keyboard.Listener | None = None
        self._running = threading.Event()
        self._last_time: float = 0
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._running.is_set()

    @property
    def recording(self) -> Recording:
        return self._recording

    def start(self) -> None:
        if self._running.is_set():
            return
        self._recording = Recording()
        self._last_time = time.perf_counter()
        self._running.set()

        self._mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_move=self._on_move,
        )
        self._kb_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._mouse_listener.daemon = True
        self._kb_listener.daemon = True
        self._mouse_listener.start()
        self._kb_listener.start()

    def stop(self) -> None:
        self._running.clear()
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._kb_listener:
            self._kb_listener.stop()
            self._kb_listener = None

    def _calc_delay(self) -> float:
        now = time.perf_counter()
        delay = now - self._last_time
        self._last_time = now
        return delay

    def _on_click(self, x, y, button, pressed):
        if not self._running.is_set() or not pressed:
            return
        with self._lock:
            delay = self._calc_delay()
            btn_name = button.name if hasattr(button, "name") else str(button)
            self._recording.events.append(
                RecordedEvent(
                    event_type="click", x=int(x), y=int(y),
                    button=btn_name, delay=delay,
                )
            )

    def _on_move(self, x, y):
        if not self._running.is_set():
            return
        with self._lock:
            # Reducir eventos de movimiento: solo guardar cada 50ms mínimo
            now = time.perf_counter()
            if now - self._last_time < 0.05:
                return
            delay = self._calc_delay()
            self._recording.events.append(
                RecordedEvent(event_type="move", x=int(x), y=int(y), delay=delay)
            )

    def _on_key_press(self, key):
        if not self._running.is_set():
            return
        with self._lock:
            delay = self._calc_delay()
            key_str = self._key_to_str(key)
            self._recording.events.append(
                RecordedEvent(event_type="key_press", key=key_str, delay=delay)
            )

    def _on_key_release(self, key):
        if not self._running.is_set():
            return
        with self._lock:
            delay = self._calc_delay()
            key_str = self._key_to_str(key)
            self._recording.events.append(
                RecordedEvent(event_type="key_release", key=key_str, delay=delay)
            )

    @staticmethod
    def _key_to_str(key) -> str:
        if hasattr(key, "char") and key.char:
            return key.char
        if hasattr(key, "name"):
            return key.name
        return str(key)
