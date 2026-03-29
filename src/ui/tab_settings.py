import json
import webbrowser
import customtkinter as ctk
from tkinter import filedialog
from src.utils.config import load_config, save_config, _get_data_dir
from src.utils.session_log import get_sessions, clear_sessions
from src.utils.i18n import t, set_lang, get_lang, on_lang_change, STRINGS
from src.utils.profiles import list_profiles, load_profile
from src.ui import theme as T
from src.ui.tooltip import Tooltip

LANG_MAP = {
    "Español": "es", "English": "en", "Português": "pt", "Français": "fr",
    "Deutsch": "de", "Italiano": "it", "Русский": "ru", "中文": "zh",
    "日本語": "ja", "한국어": "ko", "Polski": "pl", "Türkçe": "tr",
    "Nederlands": "nl", "العربية": "ar",
}
LANG_MAP_REV = {v: k for k, v in LANG_MAP.items()}

# Internal theme keys (what CTk/config uses) <-> i18n keys
THEME_I18N = [
    ("dark", "theme_dark"),
    ("light", "theme_light"),
    ("system", "theme_system"),
]

# Change this URL when you have your privacy policy published
PRIVACY_URL = "https://example.com/privacy"


class TabSettings(ctk.CTkFrame):
    def __init__(self, master, on_hotkeys_changed: callable = None,
                 on_topmost_changed: callable = None, **kwargs):
        super().__init__(master, fg_color=T.BG_DARK, **kwargs)
        self._on_hotkeys_changed = on_hotkeys_changed
        self._on_topmost_changed = on_topmost_changed
        self._config = load_config()
        self._sec_labels = {}
        self._tooltips = []
        self._build_ui()
        on_lang_change(self._refresh_lang)

    def _section(self, parent, title_key, icon=""):
        frame = ctk.CTkFrame(parent, **T.card_style())
        frame.pack(fill="x", padx=8, pady=4)
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10, 2))
        lbl = ctk.CTkLabel(header, text=f"{icon}  {t(title_key)}", font=T.FONT_SECTION, text_color=T.NEON_CYAN)
        lbl.pack(anchor="w")
        self._sec_labels[title_key] = (lbl, icon)
        return frame

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=T.BG_DARK)
        scroll.pack(fill="both", expand=True)
        self._scroll = scroll

        # ── Apariencia ──
        sec = self._section(scroll, "sec_appearance", "🎨")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=4)
        self._lbl_theme = ctk.CTkLabel(row, text=t("label_theme"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_theme.pack(side="left", padx=(0, 10))
        saved_theme = self._config.get("theme", "dark")
        theme_display = next((t(ik) for tk, ik in THEME_I18N if tk == saved_theme), t("theme_dark"))
        self._theme_var = ctk.StringVar(value=theme_display)
        self._theme_menu = ctk.CTkOptionMenu(
            row, variable=self._theme_var,
            values=[t(ik) for _, ik in THEME_I18N],
            command=self._change_theme, width=130, **T.option_menu_style())
        self._theme_menu.pack(side="left")

        row2 = ctk.CTkFrame(body, fg_color="transparent")
        row2.pack(fill="x", pady=4)
        self._topmost_var = ctk.BooleanVar(value=self._config.get("always_on_top", False))
        self._chk_top = ctk.CTkCheckBox(
            row2, text=t("chk_always_on_top"), variable=self._topmost_var, command=self._toggle_topmost,
            fg_color=T.NEON_CYAN, hover_color=T.NEON_CYAN + "88",
            border_color=T.BORDER_DIM, text_color=T.TEXT_PRIMARY, font=T.FONT_BODY,
        )
        self._chk_top.pack(anchor="w")

        # Countdown
        row_cd = ctk.CTkFrame(body, fg_color="transparent")
        row_cd.pack(fill="x", pady=4)
        self._lbl_countdown = ctk.CTkLabel(row_cd, text=t("label_countdown"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_countdown.pack(side="left", padx=(0, 8))
        self._countdown_var = ctk.StringVar(value=str(self._config.get("countdown_seconds", 3)))
        self._countdown_entry = ctk.CTkEntry(row_cd, width=55, textvariable=self._countdown_var, justify="center", **T.input_style())
        self._countdown_entry.pack(side="left", padx=(0, 6))
        self._lbl_cd_sec = ctk.CTkLabel(row_cd, text=t("label_countdown_sec"), font=T.FONT_SMALL, text_color=T.TEXT_MUTED)
        self._lbl_cd_sec.pack(side="left")
        self._tooltips.append(Tooltip(self._countdown_entry, t("tip_countdown")))

        # Notify on finish
        row_notify = ctk.CTkFrame(body, fg_color="transparent")
        row_notify.pack(fill="x", pady=4)
        self._notify_var = ctk.BooleanVar(value=self._config.get("notify_on_finish", True))
        self._chk_notify = ctk.CTkCheckBox(
            row_notify, text=t("chk_notify_finish"), variable=self._notify_var,
            fg_color=T.NEON_CYAN, hover_color=T.NEON_CYAN + "88",
            border_color=T.BORDER_DIM, text_color=T.TEXT_PRIMARY, font=T.FONT_BODY,
        )
        self._chk_notify.pack(anchor="w")

        # Close action
        row_close = ctk.CTkFrame(body, fg_color="transparent")
        row_close.pack(fill="x", pady=4)
        self._lbl_close_action = ctk.CTkLabel(row_close, text=t("label_close_action"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_close_action.pack(side="left", padx=(0, 8))
        close_map = {"ask": "close_ask", "close": "close_quit", "tray": "close_tray"}
        saved_close = self._config.get("close_action", "ask")
        self._close_action_var = ctk.StringVar(value=t(close_map.get(saved_close, "close_ask")))
        self._close_menu = ctk.CTkOptionMenu(
            row_close, variable=self._close_action_var,
            values=[t("close_ask"), t("close_quit"), t("close_tray")],
            width=130, **T.option_menu_style(),
        )
        self._close_menu.pack(side="left")

        # ── Hotkeys ──
        sec = self._section(scroll, "sec_hotkeys", "⌨")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        self._hk_vars = {}
        self._hk_labels = {}
        self._hk_displays = {}
        self._hk_capture_btns = {}
        hotkeys_info = [
            ("hotkey_autoclick", "hk_autoclick", T.NEON_GREEN),
            ("hotkey_record", "hk_record", T.NEON_RED),
            ("hotkey_play", "hk_play", T.NEON_CYAN),
        ]

        for key, label_key, color in hotkeys_info:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=4)
            lbl = ctk.CTkLabel(row, text=f"  {t(label_key)}:", width=140, anchor="w",
                         font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
            lbl.pack(side="left")
            self._hk_labels[label_key] = lbl

            var = ctk.StringVar(value=self._config.get(key, ""))
            self._hk_vars[key] = var

            display = ctk.CTkLabel(
                row, text=var.get() or "—", width=120,
                font=T.FONT_MONO, text_color=color,
                fg_color=T.BG_INPUT, corner_radius=T.CORNER_RADIUS_SM,
            )
            display.pack(side="left", padx=(0, 8))
            self._hk_displays[key] = display

            cap_btn = ctk.CTkButton(
                row, text=t("hk_capture"), width=110,
                fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                border_width=1, border_color=color, text_color=color,
                font=T.FONT_SMALL,
                command=lambda k=key, c=color: self._capture_hotkey(k, c),
            )
            cap_btn.pack(side="left")
            self._hk_capture_btns[key] = cap_btn

        # ── Hotkey reference ──
        sec_ref = self._section(scroll, "sec_hotkey_ref", "⚡")
        self._hk_ref_body = ctk.CTkFrame(sec_ref, fg_color="transparent")
        self._hk_ref_body.pack(fill="x", padx=14, pady=(4, 10))
        self._hk_ref_labels = []
        self._build_hotkey_ref()

        # ── Idioma ──
        sec = self._section(scroll, "sec_language", "🌐")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=4)
        self._lbl_lang = ctk.CTkLabel(row, text=t("label_language"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_lang.pack(side="left", padx=(0, 10))
        current_lang_name = LANG_MAP_REV.get(get_lang(), "Español")
        self._lang_var = ctk.StringVar(value=current_lang_name)
        ctk.CTkOptionMenu(row, variable=self._lang_var,
                          values=["Español", "English", "Português", "Français",
                                  "Deutsch", "Italiano", "Русский", "中文",
                                  "日本語", "한국어", "Polski", "Türkçe",
                                  "Nederlands", "العربية"],
                          width=130, command=self._change_language, **T.option_menu_style()).pack(side="left")

        # ── Export / Import ──
        row_ei = ctk.CTkFrame(scroll, fg_color="transparent")
        row_ei.pack(fill="x", padx=8, pady=(8, 2))
        btn_s = {"height": 36, "font": T.FONT_SMALL, "corner_radius": T.CORNER_RADIUS_SM}
        self._btn_export = ctk.CTkButton(
            row_ei, text=t("btn_export_config"), width=200,
            fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
            border_width=1, border_color=T.NEON_CYAN, text_color=T.NEON_CYAN,
            command=self._export_config, **btn_s,
        )
        self._btn_export.pack(side="left", padx=(0, 6))
        self._btn_import = ctk.CTkButton(
            row_ei, text=t("btn_import_config"), width=200,
            fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
            border_width=1, border_color=T.NEON_YELLOW, text_color=T.NEON_YELLOW,
            command=self._import_config, **btn_s,
        )
        self._btn_import.pack(side="left")

        # ── Guardar config ──
        self._save_btn = ctk.CTkButton(
            scroll, text=t("btn_save_config"), height=44,
            **T.neon_btn_style(T.NEON_PURPLE), command=self._save,
        )
        self._save_btn.pack(fill="x", padx=8, pady=(8, 4))

        self._status_label = ctk.CTkLabel(scroll, text="", font=T.FONT_BODY, text_color=T.NEON_GREEN)
        self._status_label.pack(pady=(0, 4))

        # ── Acerca de ──
        sec = self._section(scroll, "sec_about", "ℹ")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        from src.app import APP_VERSION
        self._lbl_version = ctk.CTkLabel(body, text=t("about_version", v=APP_VERSION), font=T.FONT_BODY, text_color=T.TEXT_PRIMARY)
        self._lbl_version.pack(anchor="w", pady=2)
        self._lbl_publisher = ctk.CTkLabel(body, text=t("about_publisher"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_publisher.pack(anchor="w", pady=2)

        self._lbl_privacy = ctk.CTkLabel(
            body, text=t("about_privacy"), font=T.FONT_BODY,
            text_color=T.NEON_CYAN, cursor="hand2",
        )
        self._lbl_privacy.pack(anchor="w", pady=2)
        self._lbl_privacy.bind("<Button-1>", lambda e: webbrowser.open(PRIVACY_URL))

        # Update available label (hidden by default)
        self._lbl_update = ctk.CTkLabel(body, text="", font=T.FONT_BODY, text_color=T.NEON_YELLOW)
        self._lbl_update.pack(anchor="w", pady=2)
        self._update_url = ""

        # ── Historial ──
        sec = self._section(scroll, "sec_history", "📊")
        self._history_textbox = ctk.CTkTextbox(
            sec, height=140, state="disabled",
            fg_color=T.BG_INPUT, text_color=T.TEXT_PRIMARY,
            font=T.FONT_MONO, corner_radius=T.CORNER_RADIUS_SM,
            border_width=1, border_color=T.BORDER_DIM,
        )
        self._history_textbox.pack(fill="both", expand=True, padx=14, pady=(4, 6))

        row_hist = ctk.CTkFrame(sec, fg_color="transparent")
        row_hist.pack(fill="x", padx=14, pady=(0, 10))
        self._btn_refresh = ctk.CTkButton(row_hist, text=t("btn_refresh"), width=90,
                       fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                       border_width=1, border_color=T.NEON_CYAN, text_color=T.NEON_CYAN,
                       font=T.FONT_SMALL, command=self._refresh_history)
        self._btn_refresh.pack(side="left", padx=(0, 6))
        self._btn_clear_hist = ctk.CTkButton(row_hist, text=t("btn_clear_history"), width=120,
                       fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                       border_width=1, border_color=T.NEON_RED, text_color=T.NEON_RED,
                       font=T.FONT_SMALL, command=self._clear_history)
        self._btn_clear_hist.pack(side="left")

        self._refresh_history()

    # ── Hotkey reference ──
    def _build_hotkey_ref(self):
        for w in self._hk_ref_labels:
            w.destroy()
        self._hk_ref_labels.clear()

        ref_info = [
            ("hk_autoclick", "hotkey_autoclick", T.NEON_GREEN),
            ("hk_record", "hotkey_record", T.NEON_RED),
            ("hk_play", "hotkey_play", T.NEON_CYAN),
        ]
        for label_key, config_key, color in ref_info:
            hk_val = self._hk_vars.get(config_key, ctk.StringVar(value=self._config.get(config_key, ""))).get() or "—"
            row = ctk.CTkFrame(self._hk_ref_body, fg_color="transparent")
            row.pack(fill="x", pady=1)
            lbl = ctk.CTkLabel(row, text=f"  {t(label_key)}:  {hk_val}", font=T.FONT_MONO, text_color=color)
            lbl.pack(anchor="w")
            self._hk_ref_labels.append(row)

    # ── Update notification ──
    def show_update(self, new_version: str, download_url: str):
        self._update_url = download_url
        self._lbl_update.configure(
            text=t("update_available", v=new_version),
            cursor="hand2",
        )
        self._lbl_update.bind("<Button-1>", lambda e: webbrowser.open(download_url))

    def _refresh_lang(self):
        for key, (lbl, icon) in self._sec_labels.items():
            lbl.configure(text=f"{icon}  {t(key)}" if icon else t(key))
        self._lbl_theme.configure(text=t("label_theme"))
        # Re-map theme dropdown to new language
        old_internal = self._theme_display_to_internal(self._theme_var.get())
        new_values = [t(ik) for _, ik in THEME_I18N]
        self._theme_menu.configure(values=new_values)
        new_display = next((t(ik) for tk, ik in THEME_I18N if tk == old_internal), new_values[0])
        self._theme_var.set(new_display)
        self._chk_top.configure(text=t("chk_always_on_top"))
        self._lbl_countdown.configure(text=t("label_countdown"))
        self._lbl_cd_sec.configure(text=t("label_countdown_sec"))
        self._chk_notify.configure(text=t("chk_notify_finish"))
        self._lbl_close_action.configure(text=t("label_close_action"))
        # Re-map close action dropdown
        old_close_internal = self._close_display_to_internal(self._close_action_var.get())
        close_i18n = [("ask", "close_ask"), ("close", "close_quit"), ("tray", "close_tray")]
        new_close_vals = [t(ik) for _, ik in close_i18n]
        self._close_menu.configure(values=new_close_vals)
        new_close_display = next((t(ik) for tk, ik in close_i18n if tk == old_close_internal), new_close_vals[0])
        self._close_action_var.set(new_close_display)
        for label_key, lbl in self._hk_labels.items():
            lbl.configure(text=f"  {t(label_key)}:")
        for key, btn in self._hk_capture_btns.items():
            btn.configure(text=t("hk_capture"))
        self._build_hotkey_ref()
        self._lbl_lang.configure(text=t("label_language"))
        self._btn_export.configure(text=t("btn_export_config"))
        self._btn_import.configure(text=t("btn_import_config"))
        self._save_btn.configure(text=t("btn_save_config"))
        # About
        from src.app import APP_VERSION
        self._lbl_version.configure(text=t("about_version", v=APP_VERSION))
        self._lbl_publisher.configure(text=t("about_publisher"))
        self._lbl_privacy.configure(text=t("about_privacy"))
        if self._update_url:
            # Re-translate update label
            ver = self._lbl_update.cget("text").split("v")[-1] if self._lbl_update.cget("text") else ""
            if ver:
                self._lbl_update.configure(text=t("update_available", v=ver))
        self._btn_refresh.configure(text=t("btn_refresh"))
        self._btn_clear_hist.configure(text=t("btn_clear_history"))
        # Tooltips
        if self._tooltips:
            self._tooltips[0].text = t("tip_countdown")
        self._refresh_history()

    def _theme_display_to_internal(self, display_value: str) -> str:
        """Convert translated theme name to internal CTk value."""
        for internal, i18n_key in THEME_I18N:
            for lang in STRINGS[i18n_key]:
                if STRINGS[i18n_key][lang] == display_value:
                    return internal
        return "dark"

    def _change_theme(self, value):
        ctk.set_appearance_mode(self._theme_display_to_internal(value))

    def _change_language(self, value):
        lang_code = LANG_MAP.get(value, "es")
        set_lang(lang_code)
        self._config["language"] = lang_code
        save_config(self._config)

    def _toggle_topmost(self):
        if self._on_topmost_changed:
            self._on_topmost_changed(self._topmost_var.get())

    def _capture_hotkey(self, config_key: str, color: str):
        from pynput import keyboard as kb
        from src.utils.hotkeys import _MOD_NAMES, key_to_name, format_hotkey

        display = self._hk_displays[config_key]
        cap_btn = self._hk_capture_btns[config_key]
        cap_btn.configure(text=t("hk_waiting"), state="disabled", border_color=T.NEON_YELLOW)
        display.configure(text="...", text_color=T.NEON_YELLOW)

        pressed_mods = set()
        capturing = True

        def on_press(key):
            nonlocal capturing
            if not capturing:
                return False
            mod = _MOD_NAMES.get(key)
            if mod:
                pressed_mods.add(mod)
                # Show modifiers in real-time
                partial = "+".join(sorted(pressed_mods)) + "+..."
                self.after(0, lambda: display.configure(text=partial))
                return  # Keep listening for the main key

            # Non-modifier key pressed → finalize
            capturing = False
            main_key = key_to_name(key)
            mods_frozen = frozenset(pressed_mods)
            hotkey_str = format_hotkey(mods_frozen, main_key)

            self.after(0, lambda: self._hk_vars[config_key].set(hotkey_str))
            self.after(0, lambda: display.configure(text=hotkey_str, text_color=color))
            self.after(0, lambda: cap_btn.configure(
                text=t("hk_capture"), state="normal", border_color=color))
            self.after(0, self._build_hotkey_ref)
            return False

        def on_release(key):
            mod = _MOD_NAMES.get(key)
            if mod:
                pressed_mods.discard(mod)

        listener = kb.Listener(on_press=on_press, on_release=on_release)
        listener.daemon = True
        listener.start()

    def _close_display_to_internal(self, display_value: str) -> str:
        close_i18n = [("ask", "close_ask"), ("close", "close_quit"), ("tray", "close_tray")]
        for internal, i18n_key in close_i18n:
            for lang in STRINGS[i18n_key]:
                if STRINGS[i18n_key][lang] == display_value:
                    return internal
        return "ask"

    # ── Export / Import ──
    def _export_config(self):
        import os
        path = filedialog.asksaveasfilename(
            title=t("btn_export_config"), defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not path:
            return

        export_data = {"config": dict(self._config), "profiles": {}}
        for name in list_profiles():
            data = load_profile(name)
            if data:
                export_data["profiles"][name] = data

        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        self._status_label.configure(text=t("export_ok"))
        self.after(2500, lambda: self._status_label.configure(text=""))

    def _import_config(self):
        import os
        from src.utils.profiles import save_profile

        path = filedialog.askopenfilename(
            title=t("btn_import_config"), filetypes=[("JSON", "*.json")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        # Import config
        if "config" in data and isinstance(data["config"], dict):
            save_config(data["config"])

        # Import profiles
        if "profiles" in data and isinstance(data["profiles"], dict):
            for name, profile_data in data["profiles"].items():
                save_profile(name, profile_data)

        self._status_label.configure(text=t("import_ok"))
        self.after(3000, lambda: self._status_label.configure(text=""))

    def _save(self):
        self._config["theme"] = self._theme_display_to_internal(self._theme_var.get())
        for key, var in self._hk_vars.items():
            self._config[key] = var.get().strip()
        self._config["language"] = LANG_MAP.get(self._lang_var.get(), "es")
        self._config["always_on_top"] = self._topmost_var.get()
        self._config["notify_on_finish"] = self._notify_var.get()
        # Clamp countdown to 0-10
        try:
            cd = max(0, min(10, int(self._countdown_var.get())))
        except ValueError:
            cd = 3
        self._config["countdown_seconds"] = cd
        self._countdown_var.set(str(cd))
        self._config["close_action"] = self._close_display_to_internal(self._close_action_var.get())
        save_config(self._config)
        self._status_label.configure(text=t("config_saved"))
        if self._on_hotkeys_changed:
            self._on_hotkeys_changed(self._config)
        self.after(2500, lambda: self._status_label.configure(text=""))

    def _refresh_history(self):
        sessions = get_sessions()
        self._history_textbox.configure(state="normal")
        self._history_textbox.delete("1.0", "end")
        if not sessions:
            self._history_textbox.insert("end", t("no_sessions") + "\n")
        else:
            self._history_textbox.insert("end", t("hist_header") + "\n")
            self._history_textbox.insert("end", "  " + "─" * 55 + "\n")
            for s in reversed(sessions[-50:]):
                dur = s.get("duration_sec", 0)
                m, sec = divmod(int(dur), 60)
                h, m = divmod(m, 60)
                dur_str = f"{h}h{m:02d}m{sec:02d}s" if h else f"{m}m{sec:02d}s"
                self._history_textbox.insert(
                    "end", f"  {s['timestamp']}  {s['mode']:<12} {s['clicks']:>6}    {dur_str}\n")
        self._history_textbox.configure(state="disabled")

    def _clear_history(self):
        clear_sessions()
        self._refresh_history()
