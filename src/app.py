import os
import sys
import time
import threading
import customtkinter as ctk
from PIL import Image

from src.core.clicker import Clicker
from src.core.recorder import Recorder, Recording
from src.core.player import Player
from src.utils.config import load_config, save_config
from src.utils.hotkeys import HotkeyManager
from src.utils.session_log import add_session
from src.utils.i18n import set_lang
from src.utils import error_log
from src.ui import theme as T
from src.ui.main_window import MainWindow
from src.ui.close_dialog import CloseDialog


APP_VERSION = "1.0.0"
_BUILD_TAG = "Gz-2026"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Install error logging early
        error_log.install(APP_VERSION)

        self._config = load_config()
        self._tray_icon = None
        self._session_start: float | None = None

        # Load saved language before building UI
        saved_lang = self._config.get("language", "es")
        set_lang(saved_lang)

        # Apply saved theme
        saved_theme = self._config.get("theme", "dark")
        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme("blue")

        self.title("AutoClic")
        self.geometry("580x750")
        self.minsize(400, 500)
        self.configure(fg_color=T.bg())

        # Splash screen
        from src.ui.splash import SplashScreen
        self._splash = SplashScreen(self, version=APP_VERSION)
        self.withdraw()  # Hide main window during splash

        # Window icon
        self._icon_path = self._resolve_asset("assets", "icon.png")
        if self._icon_path:
            self.iconbitmap(default=self._resolve_asset("assets", "icon.ico") or "")
            self._icon_image = Image.open(self._icon_path)

        # Core
        self._clicker = Clicker()
        self._recorder = Recorder()
        self._player = Player()

        # Hotkeys
        self._hotkey_mgr = HotkeyManager()

        # UI
        self._main_window = MainWindow(
            self, self._clicker, self._recorder, self._player,
            on_hotkeys_changed=self._rebind_hotkeys,
            on_topmost_changed=self._set_topmost,
        )
        self._main_window.pack(fill="both", expand=True)

        self._rebind_hotkeys(self._config)
        self._hotkey_mgr.start()

        # Restore saved state
        self._restore_state()

        # Apply saved always-on-top
        if self._config.get("always_on_top", False):
            self.attributes("-topmost", True)

        # Monitor session for logging
        self._monitor_session()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Setup tray
        self._setup_tray()

        # Close splash and show main window after 1.5s
        self.after(1500, self._close_splash)

        # Check for updates in background
        from src.utils.updater import check_for_update
        check_for_update(APP_VERSION, self._on_update_available)

    def _close_splash(self):
        if hasattr(self, "_splash") and self._splash:
            self._splash.destroy()
            self._splash = None
        self.deiconify()

    def _on_update_available(self, new_version: str, download_url: str):
        """Called from updater thread when new version is found."""
        self.after(0, lambda: self._main_window.tab_settings.show_update(new_version, download_url))

    @staticmethod
    def _resolve_asset(*parts) -> str | None:
        """Resolve asset path for both dev and PyInstaller bundled mode."""
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base, *parts)
        return path if os.path.exists(path) else None

    def _rebind_hotkeys(self, config: dict):
        self._hotkey_mgr.clear()
        hk_ac = config.get("hotkey_autoclick", "F6")
        hk_rec = config.get("hotkey_record", "F7")
        hk_play = config.get("hotkey_play", "F8")
        hk_cp = config.get("hotkey_cycle_profile", "")
        hk_cm = config.get("hotkey_cycle_macro", "")

        if hk_ac:
            self._hotkey_mgr.bind(hk_ac, self._toggle_autoclick)
        if hk_rec:
            self._hotkey_mgr.bind(hk_rec, self._toggle_record)
        if hk_play:
            self._hotkey_mgr.bind(hk_play, self._toggle_play)
        if hk_cp:
            self._hotkey_mgr.bind(hk_cp, self._cycle_profile)
        if hk_cm:
            self._hotkey_mgr.bind(hk_cm, self._cycle_macro)

    def _toggle_autoclick(self):
        self.after(0, self._main_window.tab_autoclick.toggle)

    def _toggle_record(self):
        self.after(0, self._main_window.tab_recorder.toggle_record)

    def _toggle_play(self):
        self.after(0, self._main_window.tab_recorder.toggle_play)

    def _cycle_profile(self):
        self.after(0, self._do_cycle_profile)

    def _do_cycle_profile(self):
        from src.utils.profiles import list_profiles, load_profile
        profiles = list_profiles()
        if not profiles:
            return
        tab = self._main_window.tab_autoclick
        current = tab._profile_var.get()
        try:
            idx = profiles.index(current)
            next_idx = (idx + 1) % len(profiles)
        except ValueError:
            next_idx = 0
        next_name = profiles[next_idx]
        data = load_profile(next_name)
        if data is None:
            return

        behavior = load_config().get("cycle_profile_behavior", "stop_load")
        if behavior == "stop_load":
            if self._clicker.is_running:
                tab.toggle()
            tab._set_state(data)
            tab._profile_var.set(next_name)
        elif behavior == "load_start":
            was_running = self._clicker.is_running
            if was_running:
                self._clicker.stop()
            tab._set_state(data)
            tab._profile_var.set(next_name)
            tab.toggle()
        elif behavior == "select":
            tab._set_state(data)
            tab._profile_var.set(next_name)

    def _cycle_macro(self):
        self.after(0, self._do_cycle_macro)

    def _do_cycle_macro(self):
        from src.utils.macros import list_macros, load_macro
        macros = list_macros()
        if not macros:
            return
        tab = self._main_window.tab_recorder
        current = tab._macro_var.get()
        try:
            idx = macros.index(current)
            next_idx = (idx + 1) % len(macros)
        except ValueError:
            next_idx = 0
        next_name = macros[next_idx]
        data = load_macro(next_name)
        if data is None:
            return

        behavior = load_config().get("cycle_macro_behavior", "stop_load")
        if behavior == "stop_load":
            if self._player.is_playing:
                self._player.stop()
            tab._macro_var.set(next_name)
            self._recorder.recording = Recording.from_list(data)
        elif behavior == "load_start":
            if self._player.is_playing:
                self._player.stop()
            tab._macro_var.set(next_name)
            self._recorder.recording = Recording.from_list(data)
            tab.toggle_play()
        elif behavior == "select":
            tab._macro_var.set(next_name)
            self._recorder.recording = Recording.from_list(data)

    def _set_topmost(self, value: bool):
        self.attributes("-topmost", value)

    # ── Session monitoring ──
    def _monitor_session(self):
        if self._clicker.is_running:
            if self._session_start is None:
                self._session_start = time.time()
        else:
            if self._session_start is not None:
                duration = time.time() - self._session_start
                add_session(self._clicker.click_count, duration, "autoclick")
                self._session_start = None
        self.after(500, self._monitor_session)

    # ── System tray ──
    def _setup_tray(self):
        try:
            import pystray
            self._pystray = pystray
        except ImportError:
            self._pystray = None
            return

    def _minimize_to_tray(self):
        if not self._pystray:
            self.iconify()
            return

        self.withdraw()

        if hasattr(self, "_icon_image"):
            img = self._icon_image.copy()
            img.thumbnail((64, 64))
        else:
            img = Image.new("RGB", (64, 64), T.BG_DARK)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([8, 8, 56, 56], radius=10, fill=T.NEON_GREEN)
            draw.text((18, 14), "AC", fill=T.BG_DARK)

        from src.utils.i18n import t
        menu = self._pystray.Menu(
            self._pystray.MenuItem(t("tray_show"), self._restore_from_tray, default=True),
            self._pystray.MenuItem(t("tray_quit"), self._quit_from_tray),
        )

        self._tray_icon = self._pystray.Icon("AutoClic", img, "AutoClic", menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _restore_from_tray(self, icon=None, item=None):
        if self._tray_icon:
            self._tray_icon.stop()
            self._tray_icon = None
        self.after(0, self.deiconify)

    def _quit_from_tray(self, icon=None, item=None):
        if self._tray_icon:
            self._tray_icon.stop()
            self._tray_icon = None
        self.after(0, self._do_quit)

    # ── State persistence ──
    def _restore_state(self):
        saved = self._config.get("autoclick_state", {})
        if saved:
            self._main_window.tab_autoclick._set_state(saved)

        last_rec = self._config.get("last_recording", [])
        if last_rec:
            self._recorder._recording = Recording.from_list(last_rec)
            self._main_window.tab_recorder._refresh_events()

    def _save_state(self):
        fresh_config = load_config()
        fresh_config["autoclick_state"] = self._main_window.tab_autoclick._get_state()
        fresh_config["last_recording"] = self._recorder.recording.to_list()
        save_config(fresh_config)

    # ── Close handling ──
    def _on_close(self):
        close_action = self._config.get("close_action", "ask")

        if close_action == "ask":
            CloseDialog(self, self._handle_close_choice)
        elif close_action == "tray":
            self._minimize_to_tray()
        else:
            self._do_quit()

    def _handle_close_choice(self, action: str, remember: bool):
        if remember:
            self._config["close_action"] = action
            save_config(self._config)

        if action == "tray":
            self._minimize_to_tray()
        else:
            self._do_quit()

    def _do_quit(self):
        self._save_state()

        if self._session_start is not None:
            duration = time.time() - self._session_start
            add_session(self._clicker.click_count, duration, "autoclick")

        self._clicker.stop()
        self._recorder.stop()
        self._player.stop()
        self._hotkey_mgr.stop()

        if self._tray_icon:
            self._tray_icon.stop()

        self.destroy()
