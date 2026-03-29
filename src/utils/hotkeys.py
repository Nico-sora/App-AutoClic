from pynput import keyboard

# ── Modifier keys ──
_MODIFIERS = {
    keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
    keyboard.Key.alt_l, keyboard.Key.alt_r,
    keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
}

_MOD_NAMES = {
    keyboard.Key.ctrl_l: "Ctrl", keyboard.Key.ctrl_r: "Ctrl",
    keyboard.Key.alt_l: "Alt", keyboard.Key.alt_r: "Alt",
    keyboard.Key.shift: "Shift", keyboard.Key.shift_l: "Shift", keyboard.Key.shift_r: "Shift",
}

# ── Key name → pynput Key ──
_KEY_MAP = {}
for _i in range(1, 25):
    _k = getattr(keyboard.Key, f"f{_i}", None)
    if _k:
        _KEY_MAP[f"F{_i}"] = _k

_SPECIAL_MAP = {
    "Space": keyboard.Key.space, "Enter": keyboard.Key.enter,
    "Tab": keyboard.Key.tab, "Esc": keyboard.Key.esc,
    "Backspace": keyboard.Key.backspace, "Delete": keyboard.Key.delete,
    "Insert": keyboard.Key.insert, "Home": keyboard.Key.home,
    "End": keyboard.Key.end, "PageUp": keyboard.Key.page_up,
    "PageDown": keyboard.Key.page_down,
    "Up": keyboard.Key.up, "Down": keyboard.Key.down,
    "Left": keyboard.Key.left, "Right": keyboard.Key.right,
    "PrintScreen": keyboard.Key.print_screen, "Pause": keyboard.Key.pause,
    "NumLock": keyboard.Key.num_lock, "CapsLock": keyboard.Key.caps_lock,
    "ScrollLock": keyboard.Key.scroll_lock,
}
_KEY_MAP.update(_SPECIAL_MAP)


def parse_hotkey(text: str) -> tuple[frozenset[str], str]:
    """Parse 'Ctrl+Shift+I' into (frozenset({'Ctrl','Shift'}), 'I')."""
    parts = [p.strip() for p in text.split("+")]
    mods = frozenset(p for p in parts[:-1] if p in ("Ctrl", "Alt", "Shift"))
    key = parts[-1] if parts else ""
    return mods, key


def format_hotkey(mods: frozenset[str], key: str) -> str:
    """Format (frozenset({'Ctrl'}), 'I') into 'Ctrl+I'."""
    order = [m for m in ("Ctrl", "Alt", "Shift") if m in mods]
    return "+".join(order + [key])


def key_to_name(key) -> str:
    """Convert a pynput key event to a display name."""
    # Check special / function keys
    for name, mapped in _KEY_MAP.items():
        if key == mapped:
            return name
    # Character keys
    if hasattr(key, "char") and key.char:
        return key.char.upper()
    if hasattr(key, "name") and key.name:
        return key.name.capitalize()
    return str(key)


class HotkeyManager:
    def __init__(self):
        self._listener: keyboard.Listener | None = None
        self._bindings: list[tuple[frozenset[str], str, callable]] = []
        self._pressed_mods: set[str] = set()

    def bind(self, hotkey_str: str, callback: callable) -> None:
        mods, key = parse_hotkey(hotkey_str)
        self._bindings.append((mods, key.upper(), callback))

    def clear(self) -> None:
        self._bindings.clear()
        self._pressed_mods.clear()

    def _on_press(self, key) -> None:
        # Track modifiers
        mod_name = _MOD_NAMES.get(key)
        if mod_name:
            self._pressed_mods.add(mod_name)
            return

        # Get key name
        current_key = key_to_name(key).upper()
        current_mods = frozenset(self._pressed_mods)

        for req_mods, req_key, cb in self._bindings:
            if req_key == current_key and req_mods == current_mods:
                cb()

    def _on_release(self, key) -> None:
        mod_name = _MOD_NAMES.get(key)
        if mod_name:
            self._pressed_mods.discard(mod_name)

    def start(self) -> None:
        if self._listener is not None:
            return
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
