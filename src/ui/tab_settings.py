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

THEME_I18N = [
    ("dark", "theme_dark"),
    ("light", "theme_light"),
    ("system", "theme_system"),
]

PRIVACY_URL = "https://github.com/Nico-sora/App-AutoClic/blob/master/PRIVACY.md"


class TabSettings(ctk.CTkFrame):
    def __init__(self, master, on_hotkeys_changed: callable = None,
                 on_topmost_changed: callable = None, **kwargs):
        super().__init__(master, fg_color=T.bg(), **kwargs)
        self._on_hotkeys_changed = on_hotkeys_changed
        self._on_topmost_changed = on_topmost_changed
        self._config = load_config()
        self._sec_labels = {}
        self._sec_frames = {}
        self._tooltips = []
        self._build_ui()
        on_lang_change(self._refresh_lang)

    def _section(self, parent, title_key, icon=""):
        frame = ctk.CTkFrame(parent, **T.card_style())
        frame.pack(fill="x", padx=8, pady=4)
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10, 2))
        lbl = ctk.CTkLabel(header, text=f"{icon}  {t(title_key)}", font=T.FONT_SECTION, text_color=T.text_primary())
        lbl.pack(anchor="w")
        self._sec_labels[title_key] = (lbl, icon)
        self._sec_frames[title_key] = frame
        return frame

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=T.bg())
        scroll.pack(fill="both", expand=True)
        self._scroll = scroll

        # ── Apariencia ──
        sec = self._section(scroll, "sec_appearance", "\U0001F3A8")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=4)
        self._lbl_theme = ctk.CTkLabel(row, text=t("label_theme"), font=T.FONT_BODY, text_color=T.text_secondary())
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
            fg_color=T.neon_cyan(), hover_color=T.neon_cyan() + "88",
            border_color=T.border_dim(), text_color=T.text_primary(), font=T.FONT_BODY,
        )
        self._chk_top.pack(anchor="w")

        # Countdown
        row_cd = ctk.CTkFrame(body, fg_color="transparent")
        row_cd.pack(fill="x", pady=4)
        self._lbl_countdown = ctk.CTkLabel(row_cd, text=t("label_countdown"), font=T.FONT_BODY, text_color=T.text_secondary())
        self._lbl_countdown.pack(side="left", padx=(0, 8))
        self._countdown_var = ctk.StringVar(value=str(self._config.get("countdown_seconds", 3)))
        self._countdown_entry = ctk.CTkEntry(row_cd, width=55, textvariable=self._countdown_var, justify="center", **T.input_style())
        self._countdown_entry.pack(side="left", padx=(0, 6))
        self._lbl_cd_sec = ctk.CTkLabel(row_cd, text=t("label_countdown_sec"), font=T.FONT_SMALL, text_color=T.text_muted())
        self._lbl_cd_sec.pack(side="left")
        self._tooltips.append(Tooltip(self._countdown_entry, t("tip_countdown")))

        # Notify on finish
        row_notify = ctk.CTkFrame(body, fg_color="transparent")
        row_notify.pack(fill="x", pady=4)
        self._notify_var = ctk.BooleanVar(value=self._config.get("notify_on_finish", True))
        self._chk_notify = ctk.CTkCheckBox(
            row_notify, text=t("chk_notify_finish"), variable=self._notify_var,
            fg_color=T.neon_cyan(), hover_color=T.neon_cyan() + "88",
            border_color=T.border_dim(), text_color=T.text_primary(), font=T.FONT_BODY,
        )
        self._chk_notify.pack(anchor="w")

        # Close action
        row_close = ctk.CTkFrame(body, fg_color="transparent")
        row_close.pack(fill="x", pady=4)
        self._lbl_close_action = ctk.CTkLabel(row_close, text=t("label_close_action"), font=T.FONT_BODY, text_color=T.text_secondary())
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
        sec = self._section(scroll, "sec_hotkeys", "\u2328")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        self._hk_vars = {}
        self._hk_labels = {}
        self._hk_displays = {}
        self._hk_capture_btns = {}
        # Store color function names for dynamic theme refresh
        self._hk_color_fns = {
            "hotkey_autoclick": T.neon_green,
            "hotkey_record": T.neon_red,
            "hotkey_play": T.neon_cyan,
            "hotkey_cycle_profile": T.neon_yellow,
            "hotkey_cycle_macro": T.neon_purple,
        }
        hotkeys_info = [
            ("hotkey_autoclick", "hk_autoclick", T.neon_green()),
            ("hotkey_record", "hk_record", T.neon_red()),
            ("hotkey_play", "hk_play", T.neon_cyan()),
            ("hotkey_cycle_profile", "hk_cycle_profile", T.neon_yellow()),
            ("hotkey_cycle_macro", "hk_cycle_macro", T.neon_purple()),
        ]

        for key, label_key, color in hotkeys_info:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=4)
            lbl = ctk.CTkLabel(row, text=f"  {t(label_key)}:", width=140, anchor="w",
                         font=T.FONT_BODY, text_color=T.text_secondary())
            lbl.pack(side="left")
            self._hk_labels[label_key] = lbl

            var = ctk.StringVar(value=self._config.get(key, ""))
            self._hk_vars[key] = var

            display = ctk.CTkLabel(
                row, text=var.get() or "\u2014", width=120,
                font=T.FONT_MONO, text_color=color,
                fg_color=T.bg_input(), corner_radius=T.CORNER_RADIUS_SM,
            )
            display.pack(side="left", padx=(0, 8))
            self._hk_displays[key] = display

            cap_btn = ctk.CTkButton(
                row, text=t("hk_capture"), width=110,
                fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
                border_width=1, border_color=color, text_color=color,
                font=T.FONT_SMALL,
                command=lambda k=key, c=color: self._capture_hotkey(k, c),
            )
            cap_btn.pack(side="left")
            self._hk_capture_btns[key] = cap_btn

        # ── Comportamiento de ciclo ──
        self._cycle_behavior_vars = {}
        cycle_behavior_items = [
            ("cycle_profile_behavior", "hk_cycle_profile"),
            ("cycle_macro_behavior", "hk_cycle_macro"),
        ]
        for cfg_key, label_key in cycle_behavior_items:
            row_b = ctk.CTkFrame(body, fg_color="transparent")
            row_b.pack(fill="x", pady=2)
            lbl_b = ctk.CTkLabel(
                row_b, text=f"  {t(label_key)} — {t('label_cycle_behavior')}",
                width=200, anchor="w", font=T.FONT_SMALL, text_color=T.text_muted(),
            )
            lbl_b.pack(side="left")
            saved_beh = self._config.get(cfg_key, "stop_load")
            beh_map = {
                "stop_load": t("cycle_behavior_stop_load"),
                "load_start": t("cycle_behavior_load_start"),
                "select": t("cycle_behavior_select"),
            }
            beh_var = ctk.StringVar(value=beh_map.get(saved_beh, t("cycle_behavior_stop_load")))
            self._cycle_behavior_vars[cfg_key] = beh_var
            beh_menu = ctk.CTkOptionMenu(
                row_b, variable=beh_var,
                values=[t("cycle_behavior_stop_load"), t("cycle_behavior_load_start"), t("cycle_behavior_select")],
                width=160, command=lambda val, k=cfg_key: self._save_cycle_behavior(k, val),
                **T.option_menu_style(),
            )
            beh_menu.pack(side="left", padx=(0, 8))

        # ── Idioma ──
        sec = self._section(scroll, "sec_language", "\U0001F310")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=4)
        self._lbl_lang = ctk.CTkLabel(row, text=t("label_language"), font=T.FONT_BODY, text_color=T.text_secondary())
        self._lbl_lang.pack(side="left", padx=(0, 10))
        current_lang_name = LANG_MAP_REV.get(get_lang(), "Español")
        self._lang_var = ctk.StringVar(value=current_lang_name)
        self._lang_menu = ctk.CTkOptionMenu(row, variable=self._lang_var,
                          values=["Español", "English", "Português", "Français",
                                  "Deutsch", "Italiano", "Русский", "中文",
                                  "日本語", "한국어", "Polski", "Türkçe",
                                  "Nederlands", "العربية"],
                          width=130, command=self._change_language, **T.option_menu_style())
        self._lang_menu.pack(side="left")

        # ── Export / Import ──
        sec_ei = self._section(scroll, "sec_export_import", "\U0001F4E6")
        body_ei = ctk.CTkFrame(sec_ei, fg_color="transparent")
        body_ei.pack(fill="x", padx=14, pady=(4, 10))
        row_ei = ctk.CTkFrame(body_ei, fg_color="transparent")
        row_ei.pack(fill="x")
        btn_s = {"height": 36, "font": T.FONT_SMALL, "corner_radius": T.CORNER_RADIUS_SM}
        self._btn_export = ctk.CTkButton(
            row_ei, text=t("btn_export_config"), width=200,
            fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
            border_width=1, border_color=T.neon_cyan(), text_color=T.neon_cyan(),
            command=self._export_config, **btn_s,
        )
        self._btn_export.pack(side="left", padx=(0, 6))
        self._btn_import = ctk.CTkButton(
            row_ei, text=t("btn_import_config"), width=200,
            fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
            border_width=1, border_color=T.neon_yellow(), text_color=T.neon_yellow(),
            command=self._import_config, **btn_s,
        )
        self._btn_import.pack(side="left")

        # ── Guardar config ──
        self._save_btn = ctk.CTkButton(
            scroll, text=t("btn_save_config"), height=44,
            **T.neon_btn_style(T.neon_purple()), command=self._save,
        )
        self._save_btn.pack(fill="x", padx=8, pady=(8, 4))

        self._status_label = ctk.CTkLabel(scroll, text="", font=T.FONT_BODY, text_color=T.neon_green())
        self._status_label.pack(pady=(0, 4))

        # ── Historial ──
        sec = self._section(scroll, "sec_history", "\U0001F4CA")
        self._history_textbox = ctk.CTkTextbox(
            sec, height=140, state="disabled",
            fg_color=T.bg_input(), text_color=T.text_primary(),
            font=T.FONT_MONO, corner_radius=T.CORNER_RADIUS_SM,
            border_width=1, border_color=T.border_dim(),
        )
        self._history_textbox.pack(fill="both", expand=True, padx=14, pady=(4, 6))

        row_hist = ctk.CTkFrame(sec, fg_color="transparent")
        row_hist.pack(fill="x", padx=14, pady=(0, 10))
        self._btn_refresh = ctk.CTkButton(row_hist, text=t("btn_refresh"), width=90,
                       fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
                       border_width=1, border_color=T.neon_cyan(), text_color=T.neon_cyan(),
                       font=T.FONT_SMALL, command=self._refresh_history)
        self._btn_refresh.pack(side="left", padx=(0, 6))
        self._btn_clear_hist = ctk.CTkButton(row_hist, text=t("btn_clear_history"), width=120,
                       fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
                       border_width=1, border_color=T.neon_red(), text_color=T.neon_red(),
                       font=T.FONT_SMALL, command=self._clear_history)
        self._btn_clear_hist.pack(side="left")

        # ── Acerca de ──
        sec = self._section(scroll, "sec_about", "\u2139")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        from src.app import APP_VERSION
        self._lbl_version = ctk.CTkLabel(body, text=t("about_version", v=APP_VERSION), font=T.FONT_BODY, text_color=T.text_primary())
        self._lbl_version.pack(anchor="w", pady=2)
        self._lbl_publisher = ctk.CTkLabel(body, text=t("about_publisher"), font=T.FONT_BODY, text_color=T.text_secondary())
        self._lbl_publisher.pack(anchor="w", pady=2)

        self._lbl_privacy = ctk.CTkLabel(
            body, text=t("about_privacy"), font=T.FONT_BODY,
            text_color=T.neon_cyan(), cursor="hand2",
        )
        self._lbl_privacy.pack(anchor="w", pady=2)
        self._lbl_privacy.bind("<Button-1>", lambda e: webbrowser.open(PRIVACY_URL))

        self._lbl_update = ctk.CTkLabel(body, text="", font=T.FONT_BODY, text_color=T.neon_yellow())
        self._lbl_update.pack(anchor="w", pady=2)
        self._update_url = ""

        self._refresh_history()

    # ── Update notification ──
    def show_update(self, new_version: str, download_url: str):
        self._update_url = download_url
        self._lbl_update.configure(
            text=t("update_available", v=new_version),
            cursor="hand2",
        )
        self._lbl_update.bind("<Button-1>", lambda e: webbrowser.open(download_url))

    def refresh_theme(self):
        """Re-apply theme colors."""
        self.configure(fg_color=T.bg())
        self._scroll.configure(fg_color=T.bg())
        for title_key, frame in self._sec_frames.items():
            frame.configure(**T.card_style())
        for title_key, (lbl, icon) in self._sec_labels.items():
            lbl.configure(text_color=T.text_primary())
        self._lbl_theme.configure(text_color=T.text_secondary())
        self._theme_menu.configure(**T.option_menu_style())
        self._chk_top.configure(fg_color=T.neon_cyan(), border_color=T.border_dim(), text_color=T.text_primary())
        self._lbl_countdown.configure(text_color=T.text_secondary())
        self._countdown_entry.configure(**T.input_style())
        self._lbl_cd_sec.configure(text_color=T.text_muted())
        self._chk_notify.configure(fg_color=T.neon_cyan(), border_color=T.border_dim(), text_color=T.text_primary())
        self._lbl_close_action.configure(text_color=T.text_secondary())
        self._close_menu.configure(**T.option_menu_style())
        for lbl in self._hk_labels.values():
            lbl.configure(text_color=T.text_secondary())
        for key, display in self._hk_displays.items():
            color_fn = self._hk_color_fns.get(key, T.neon_cyan)
            display.configure(fg_color=T.bg_input(), text_color=color_fn())
        for key, btn in self._hk_capture_btns.items():
            color_fn = self._hk_color_fns.get(key, T.neon_cyan)
            btn.configure(fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
                         border_color=color_fn(), text_color=color_fn())
        self._lbl_lang.configure(text_color=T.text_secondary())
        self._lang_menu.configure(**T.option_menu_style())
        self._btn_export.configure(fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
                                   border_color=T.neon_cyan(), text_color=T.neon_cyan())
        self._btn_import.configure(fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
                                   border_color=T.neon_yellow(), text_color=T.neon_yellow())
        self._save_btn.configure(**T.neon_btn_style(T.neon_purple()))
        self._status_label.configure(text_color=T.neon_green())
        self._history_textbox.configure(fg_color=T.bg_input(), text_color=T.text_primary(), border_color=T.border_dim())
        self._btn_refresh.configure(fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
                                    border_color=T.neon_cyan(), text_color=T.neon_cyan())
        self._btn_clear_hist.configure(fg_color=T.bg_input(), hover_color=T.bg_card_hover(),
                                       border_color=T.neon_red(), text_color=T.neon_red())
        self._lbl_version.configure(text_color=T.text_primary())
        self._lbl_publisher.configure(text_color=T.text_secondary())
        self._lbl_privacy.configure(text_color=T.neon_cyan())
        self._lbl_update.configure(text_color=T.neon_yellow())

    def _refresh_lang(self):
        for key, (lbl, icon) in self._sec_labels.items():
            lbl.configure(text=f"{icon}  {t(key)}" if icon else t(key))
        self._lbl_theme.configure(text=t("label_theme"))
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
        self._lbl_lang.configure(text=t("label_language"))
        self._btn_export.configure(text=t("btn_export_config"))
        self._btn_import.configure(text=t("btn_import_config"))
        self._save_btn.configure(text=t("btn_save_config"))
        from src.app import APP_VERSION
        self._lbl_version.configure(text=t("about_version", v=APP_VERSION))
        self._lbl_publisher.configure(text=t("about_publisher"))
        self._lbl_privacy.configure(text=t("about_privacy"))
        if self._update_url:
            ver = self._lbl_update.cget("text").split("v")[-1] if self._lbl_update.cget("text") else ""
            if ver:
                self._lbl_update.configure(text=t("update_available", v=ver))
        self._btn_refresh.configure(text=t("btn_refresh"))
        self._btn_clear_hist.configure(text=t("btn_clear_history"))
        if self._tooltips:
            self._tooltips[0].text = t("tip_countdown")
        self._refresh_history()

    def _theme_display_to_internal(self, display_value: str) -> str:
        for internal, i18n_key in THEME_I18N:
            for lang in STRINGS[i18n_key]:
                if STRINGS[i18n_key][lang] == display_value:
                    return internal
        return "dark"

    def _change_theme(self, value):
        internal = self._theme_display_to_internal(value)
        ctk.set_appearance_mode(internal)
        # Trigger theme refresh on the main window
        self.after(50, self._trigger_theme_refresh)

    def _trigger_theme_refresh(self):
        top = self.winfo_toplevel()
        top.configure(fg_color=T.bg())
        if hasattr(top, "_main_window"):
            top._main_window.refresh_theme()

    def _change_language(self, value):
        lang_code = LANG_MAP.get(value, "es")
        set_lang(lang_code)
        self._config["language"] = lang_code
        save_config(self._config)

    def _toggle_topmost(self):
        if self._on_topmost_changed:
            self._on_topmost_changed(self._topmost_var.get())

    def _save_cycle_behavior(self, cfg_key: str, display_val: str) -> None:
        rev = {
            t("cycle_behavior_stop_load"): "stop_load",
            t("cycle_behavior_load_start"): "load_start",
            t("cycle_behavior_select"): "select",
        }
        internal = rev.get(display_val, "stop_load")
        self._config = load_config()
        self._config[cfg_key] = internal
        save_config(self._config)
        if self._on_hotkeys_changed:
            self._on_hotkeys_changed(self._config)

    def _capture_hotkey(self, config_key: str, color: str):
        from pynput import keyboard as kb
        from src.utils.hotkeys import _MOD_NAMES, key_to_name, format_hotkey

        display = self._hk_displays[config_key]
        cap_btn = self._hk_capture_btns[config_key]
        cap_btn.configure(text=t("hk_waiting"), state="disabled", border_color=T.neon_yellow())
        display.configure(text="...", text_color=T.neon_yellow())

        pressed_mods = set()
        capturing = True

        def on_press(key):
            nonlocal capturing
            if not capturing:
                return False
            mod = _MOD_NAMES.get(key)
            if mod:
                pressed_mods.add(mod)
                partial = "+".join(sorted(pressed_mods)) + "+..."
                self.after(0, lambda: display.configure(text=partial))
                return
            capturing = False
            main_key = key_to_name(key)
            mods_frozen = frozenset(pressed_mods)
            hotkey_str = format_hotkey(mods_frozen, main_key)
            self.after(0, lambda: self._hk_vars[config_key].set(hotkey_str))
            self.after(0, lambda: display.configure(text=hotkey_str, text_color=color))
            self.after(0, lambda: cap_btn.configure(
                text=t("hk_capture"), state="normal", border_color=color))
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
        from src.utils.profiles import save_profile
        from src.utils.config import DEFAULT_CONFIG

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

        if "config" in data and isinstance(data["config"], dict):
            allowed_keys = set(DEFAULT_CONFIG.keys())
            filtered = {k: v for k, v in data["config"].items() if k in allowed_keys}
            save_config(filtered)

        if "profiles" in data and isinstance(data["profiles"], dict):
            for name, profile_data in data["profiles"].items():
                if not isinstance(profile_data, dict):
                    continue
                try:
                    save_profile(name, profile_data)
                except ValueError:
                    continue

        self._status_label.configure(text=t("import_ok"))
        self.after(3000, lambda: self._status_label.configure(text=""))

    def _save(self):
        self._config["theme"] = self._theme_display_to_internal(self._theme_var.get())
        for key, var in self._hk_vars.items():
            self._config[key] = var.get().strip()
        self._config["language"] = LANG_MAP.get(self._lang_var.get(), "es")
        self._config["always_on_top"] = self._topmost_var.get()
        self._config["notify_on_finish"] = self._notify_var.get()
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
            self._history_textbox.insert("end", "  " + "\u2500" * 55 + "\n")
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
