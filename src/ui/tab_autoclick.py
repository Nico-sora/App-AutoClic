import datetime
import customtkinter as ctk
from src.core.clicker import Clicker
from src.ui import theme as T
from src.ui.tooltip import Tooltip
from src.utils.i18n import t, on_lang_change, STRINGS
from src.utils.config import load_config
from src.utils.profiles import save_profile, load_profile, list_profiles, delete_profile


class TabAutoClick(ctk.CTkFrame):
    def __init__(self, master, clicker: Clicker, **kwargs):
        super().__init__(master, fg_color=T.BG_DARK, **kwargs)
        self._clicker = clicker
        self._picking_pos = False
        self._picking_zone_step = 0
        self._countdown_id = None
        self._widgets = {}
        self._build_ui()
        on_lang_change(self._refresh_lang)

    def _section(self, parent, title_key, icon=""):
        frame = ctk.CTkFrame(parent, **T.card_style())
        frame.pack(fill="x", padx=8, pady=4)
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10, 2))
        lbl = ctk.CTkLabel(header, text=f"{icon}  {t(title_key)}", font=T.FONT_SECTION, text_color=T.NEON_CYAN)
        lbl.pack(anchor="w")
        self._widgets[f"sec_{title_key}"] = (lbl, title_key, icon)
        return frame

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=T.BG_DARK)
        scroll.pack(fill="both", expand=True)
        self._scroll = scroll

        # ── Perfiles ──
        sec = self._section(scroll, "sec_profiles", "📁")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=2)

        self._profile_var = ctk.StringVar(value="")
        self._profile_menu = ctk.CTkOptionMenu(
            row, variable=self._profile_var, values=list_profiles() or [t("empty")],
            width=160, **T.option_menu_style(),
        )
        self._profile_menu.pack(side="left", padx=(0, 8))

        self._btn_load = ctk.CTkButton(row, text=t("btn_load"), width=70, fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                       border_width=1, border_color=T.NEON_CYAN, text_color=T.NEON_CYAN,
                       font=T.FONT_SMALL, command=self._load_profile)
        self._btn_load.pack(side="left", padx=2)
        self._btn_save_p = ctk.CTkButton(row, text=t("btn_save"), width=70, fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                       border_width=1, border_color=T.NEON_GREEN, text_color=T.NEON_GREEN,
                       font=T.FONT_SMALL, command=self._save_profile)
        self._btn_save_p.pack(side="left", padx=2)
        self._btn_del = ctk.CTkButton(row, text=t("btn_delete"), width=70, fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                       border_width=1, border_color=T.NEON_RED, text_color=T.NEON_RED,
                       font=T.FONT_SMALL, command=self._delete_profile)
        self._btn_del.pack(side="left", padx=2)

        row2 = ctk.CTkFrame(body, fg_color="transparent")
        row2.pack(fill="x", pady=(4, 0))
        self._lbl_name = ctk.CTkLabel(row2, text=t("name"), font=T.FONT_SMALL, text_color=T.TEXT_MUTED)
        self._lbl_name.pack(side="left", padx=(0, 6))
        self._profile_name_entry = ctk.CTkEntry(row2, width=180, placeholder_text=t("profile_name_placeholder"), **T.input_style())
        self._profile_name_entry.pack(side="left")

        # ── Tipo de acción ──
        sec = self._section(scroll, "sec_action_type", "🖱")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        self._action_var = ctk.StringVar(value="clic")
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=2)
        self._rb_mouse = ctk.CTkRadioButton(row, text=t("radio_mouse_click"), variable=self._action_var, value="clic",
                           command=self._toggle_action, **T.radio_style())
        self._rb_mouse.pack(side="left", padx=(0, 12))
        self._rb_key = ctk.CTkRadioButton(row, text=t("radio_key"), variable=self._action_var, value="tecla",
                           command=self._toggle_action, **T.radio_style())
        self._rb_key.pack(side="left", padx=(0, 12))
        self._rb_extra = ctk.CTkRadioButton(row, text=t("radio_extra_btn"), variable=self._action_var, value="extra",
                           command=self._toggle_action, **T.radio_style())
        self._rb_extra.pack(side="left")

        # Botón del mouse + tipo de clic
        self._frame_button = ctk.CTkFrame(body, fg_color="transparent")
        self._frame_button.pack(fill="x", pady=4)
        self._lbl_btn = ctk.CTkLabel(self._frame_button, text=t("label_button"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_btn.pack(side="left", padx=(0, 8))
        self._button_var = ctk.StringVar(value=t("btn_left"))
        self._btn_menu = ctk.CTkOptionMenu(self._frame_button, variable=self._button_var,
                          values=[t("btn_left"), t("btn_middle"), t("btn_right")], width=120, **T.option_menu_style())
        self._btn_menu.pack(side="left", padx=(0, 16))

        self._lbl_type = ctk.CTkLabel(self._frame_button, text=t("label_type"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_type.pack(side="left", padx=(0, 8))
        self._click_type_var = ctk.StringVar(value=t("click_single"))
        self._type_menu = ctk.CTkOptionMenu(self._frame_button, variable=self._click_type_var,
                          values=[t("click_single"), t("click_double"), t("click_triple")], width=100, **T.option_menu_style())
        self._type_menu.pack(side="left")

        # Tecla personalizada
        self._frame_key = ctk.CTkFrame(body, fg_color="transparent")
        self._captured_key = ctk.StringVar(value="")
        self._listening_key = False

        self._lbl_key = ctk.CTkLabel(self._frame_key, text=t("label_key"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_key.pack(side="left", padx=(0, 8))
        self._key_display = ctk.CTkLabel(
            self._frame_key, text=t("none_selected"), width=100,
            font=T.FONT_MONO, text_color=T.NEON_YELLOW,
            fg_color=T.BG_INPUT, corner_radius=T.CORNER_RADIUS_SM,
        )
        self._key_display.pack(side="left", padx=(0, 10))
        self._capture_btn = ctk.CTkButton(
            self._frame_key, text=t("btn_capture_key"), width=140,
            fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
            border_width=1, border_color=T.NEON_YELLOW,
            text_color=T.NEON_YELLOW, font=T.FONT_SMALL,
            command=self._start_key_capture,
        )
        self._capture_btn.pack(side="left")

        # Botones extra del mouse
        self._frame_extra = ctk.CTkFrame(body, fg_color="transparent")
        self._extra_btn_var = ctk.StringVar(value=t("btn_back_x1"))

        self._lbl_extra = ctk.CTkLabel(self._frame_extra, text=t("label_button"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_extra.pack(side="left", padx=(0, 8))
        self._extra_menu = ctk.CTkOptionMenu(self._frame_extra, variable=self._extra_btn_var,
                          values=[t("btn_back_x1"), t("btn_forward_x2")], width=160, **T.option_menu_style())
        self._extra_menu.pack(side="left", padx=(0, 12))

        self._captured_mouse_btn = ctk.StringVar(value="")
        self._mouse_btn_display = ctk.CTkLabel(
            self._frame_extra, text="", width=80,
            font=T.FONT_MONO, text_color=T.NEON_PURPLE,
            fg_color=T.BG_INPUT, corner_radius=T.CORNER_RADIUS_SM,
        )
        self._mouse_btn_display.pack(side="left", padx=(0, 8))
        self._capture_mouse_btn = ctk.CTkButton(
            self._frame_extra, text=t("btn_detect_btn"), width=130,
            fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
            border_width=1, border_color=T.NEON_PURPLE,
            text_color=T.NEON_PURPLE, font=T.FONT_SMALL,
            command=self._start_mouse_btn_capture,
        )
        self._capture_mouse_btn.pack(side="left")

        # ── Intervalo ──
        sec = self._section(scroll, "sec_interval", "⏱")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self._h_int = self._make_spinbox(row, "H")
        self._m_int = self._make_spinbox(row, "M")
        self._s_int = self._make_spinbox(row, "S")
        self._ms_int = self._make_spinbox(row, "ms", default=100)

        row_rand = ctk.CTkFrame(body, fg_color="transparent")
        row_rand.pack(fill="x", pady=(6, 0))
        self._lbl_rand = ctk.CTkLabel(row_rand, text=t("random_variation"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_rand.pack(side="left", padx=(0, 8))
        self._rand_ms = ctk.StringVar(value="0")
        self._rand_ms_entry = ctk.CTkEntry(row_rand, width=60, textvariable=self._rand_ms, justify="center", **T.input_style())
        self._rand_ms_entry.pack(side="left", padx=(0, 4))
        ctk.CTkLabel(row_rand, text="ms  (±)", font=T.FONT_SMALL, text_color=T.TEXT_MUTED).pack(side="left")

        # ── Duración ──
        sec = self._section(scroll, "sec_duration", "⏳")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        self._dur_var = ctk.StringVar(value="infinito")
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=2)
        self._rb_inf = ctk.CTkRadioButton(row, text=t("radio_infinite"), variable=self._dur_var, value="infinito",
                           command=self._toggle_duration, **T.radio_style(T.NEON_PURPLE))
        self._rb_inf.pack(side="left", padx=(0, 20))
        self._rb_time = ctk.CTkRadioButton(row, text=t("radio_by_time"), variable=self._dur_var, value="tiempo",
                           command=self._toggle_duration, **T.radio_style(T.NEON_PURPLE))
        self._rb_time.pack(side="left")

        self._frame_dur_time = ctk.CTkFrame(body, fg_color="transparent")
        self._frame_dur_time.pack(fill="x", pady=4)
        self._h_dur = self._make_spinbox(self._frame_dur_time, "H")
        self._m_dur = self._make_spinbox(self._frame_dur_time, "M")
        self._s_dur = self._make_spinbox(self._frame_dur_time, "S", default=10)
        self._toggle_duration()

        # ── Posición ──
        sec = self._section(scroll, "sec_position", "📍")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        self._pos_var = ctk.StringVar(value="cursor")
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=2)
        self._rb_cursor = ctk.CTkRadioButton(row, text=t("radio_follow_cursor"), variable=self._pos_var, value="cursor",
                           command=self._toggle_pos, **T.radio_style(T.NEON_YELLOW))
        self._rb_cursor.pack(side="left", padx=(0, 12))
        self._rb_fixed = ctk.CTkRadioButton(row, text=t("radio_fixed_pos"), variable=self._pos_var, value="fija",
                           command=self._toggle_pos, **T.radio_style(T.NEON_YELLOW))
        self._rb_fixed.pack(side="left", padx=(0, 12))
        self._rb_zone = ctk.CTkRadioButton(row, text=t("radio_random_zone"), variable=self._pos_var, value="zona",
                           command=self._toggle_pos, **T.radio_style(T.NEON_YELLOW))
        self._rb_zone.pack(side="left")

        # Posición fija
        self._frame_pos_fixed = ctk.CTkFrame(body, fg_color="transparent")
        self._frame_pos_fixed.pack(fill="x", pady=4)
        ctk.CTkLabel(self._frame_pos_fixed, text="X:", font=T.FONT_MONO, text_color=T.NEON_CYAN).pack(side="left")
        self._x_entry = ctk.CTkEntry(self._frame_pos_fixed, width=70, **T.input_style())
        self._x_entry.insert(0, "0")
        self._x_entry.pack(side="left", padx=(4, 12))
        ctk.CTkLabel(self._frame_pos_fixed, text="Y:", font=T.FONT_MONO, text_color=T.NEON_CYAN).pack(side="left")
        self._y_entry = ctk.CTkEntry(self._frame_pos_fixed, width=70, **T.input_style())
        self._y_entry.insert(0, "0")
        self._y_entry.pack(side="left", padx=(4, 12))
        self._pick_btn = ctk.CTkButton(
            self._frame_pos_fixed, text=t("btn_pick_pos"), width=110,
            fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
            border_width=1, border_color=T.NEON_YELLOW,
            text_color=T.NEON_YELLOW, font=T.FONT_SMALL,
            command=self._pick_position,
        )
        self._pick_btn.pack(side="left")

        # Zona aleatoria
        self._frame_zone = ctk.CTkFrame(body, fg_color="transparent")
        zone_row1 = ctk.CTkFrame(self._frame_zone, fg_color="transparent")
        zone_row1.pack(fill="x", pady=2)
        self._lbl_from = ctk.CTkLabel(zone_row1, text=t("zone_from"), font=T.FONT_MONO, text_color=T.NEON_CYAN)
        self._lbl_from.pack(side="left")
        self._zx1 = ctk.CTkEntry(zone_row1, width=65, **T.input_style())
        self._zx1.insert(0, "0")
        self._zx1.pack(side="left", padx=(4, 10))
        ctk.CTkLabel(zone_row1, text="Y1:", font=T.FONT_MONO, text_color=T.NEON_CYAN).pack(side="left")
        self._zy1 = ctk.CTkEntry(zone_row1, width=65, **T.input_style())
        self._zy1.insert(0, "0")
        self._zy1.pack(side="left", padx=(4, 10))

        zone_row2 = ctk.CTkFrame(self._frame_zone, fg_color="transparent")
        zone_row2.pack(fill="x", pady=2)
        self._lbl_to = ctk.CTkLabel(zone_row2, text=t("zone_to"), font=T.FONT_MONO, text_color=T.NEON_CYAN)
        self._lbl_to.pack(side="left")
        self._zx2 = ctk.CTkEntry(zone_row2, width=65, **T.input_style())
        self._zx2.insert(0, "500")
        self._zx2.pack(side="left", padx=(4, 10))
        ctk.CTkLabel(zone_row2, text="Y2:", font=T.FONT_MONO, text_color=T.NEON_CYAN).pack(side="left")
        self._zy2 = ctk.CTkEntry(zone_row2, width=65, **T.input_style())
        self._zy2.insert(0, "500")
        self._zy2.pack(side="left", padx=(4, 10))

        self._zone_pick_btn = ctk.CTkButton(
            self._frame_zone, text=t("btn_pick_zone"), width=180,
            fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
            border_width=1, border_color=T.NEON_YELLOW,
            text_color=T.NEON_YELLOW, font=T.FONT_SMALL,
            command=self._pick_zone,
        )
        self._zone_pick_btn.pack(anchor="w", pady=(4, 0))
        self._toggle_pos()

        # ── Botón principal ──
        self._start_btn = ctk.CTkButton(
            scroll, text=t("btn_start", hk=self._hk()), height=48,
            **T.neon_btn_style(T.NEON_GREEN), command=self.toggle,
        )
        self._start_btn.pack(fill="x", padx=8, pady=(8, 4))

        # ── Scheduler ──
        sec = self._section(scroll, "sec_scheduler", "🕐")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))

        row_sched = ctk.CTkFrame(body, fg_color="transparent")
        row_sched.pack(fill="x", pady=2)
        self._sched_var = ctk.BooleanVar(value=False)
        self._chk_sched = ctk.CTkCheckBox(
            row_sched, text=t("chk_schedule"), variable=self._sched_var,
            command=self._toggle_scheduler,
            fg_color=T.NEON_PURPLE, hover_color=T.NEON_PURPLE + "88",
            border_color=T.BORDER_DIM, text_color=T.TEXT_PRIMARY, font=T.FONT_BODY,
        )
        self._chk_sched.pack(side="left", padx=(0, 8))

        self._sched_hour = ctk.StringVar(value="00")
        self._sched_min = ctk.StringVar(value="00")
        ctk.CTkEntry(row_sched, width=45, textvariable=self._sched_hour, justify="center", **T.input_style()).pack(side="left", padx=(0, 2))
        ctk.CTkLabel(row_sched, text=":", font=T.FONT_MONO, text_color=T.TEXT_MUTED).pack(side="left")
        ctk.CTkEntry(row_sched, width=45, textvariable=self._sched_min, justify="center", **T.input_style()).pack(side="left", padx=(2, 8))

        self._sched_status = ctk.CTkLabel(row_sched, text="", font=T.FONT_SMALL, text_color=T.NEON_PURPLE)
        self._sched_status.pack(side="left")
        self._sched_after_id = None

        # ── Tooltips ──
        Tooltip(self._rand_ms_entry, t("tip_random_variation"))
        Tooltip(self._zone_pick_btn, t("tip_random_zone"))

    def _make_spinbox(self, parent, label, default=0):
        ctk.CTkLabel(parent, text=label, font=T.FONT_MONO, text_color=T.TEXT_MUTED).pack(side="left", padx=(10, 3))
        var = ctk.StringVar(value=str(default))
        ctk.CTkEntry(parent, width=58, textvariable=var, justify="center", **T.input_style()).pack(side="left", padx=(0, 4))
        return var

    def _hk(self):
        return load_config().get("hotkey_autoclick", "F6")

    # ── Language refresh ──
    def _refresh_lang(self):
        for key, (lbl, title_key, icon) in self._widgets.items():
            lbl.configure(text=f"{icon}  {t(title_key)}" if icon else t(title_key))
        self._btn_load.configure(text=t("btn_load"))
        self._btn_save_p.configure(text=t("btn_save"))
        self._btn_del.configure(text=t("btn_delete"))
        self._lbl_name.configure(text=t("name"))
        self._rb_mouse.configure(text=t("radio_mouse_click"))
        self._rb_key.configure(text=t("radio_key"))
        self._rb_extra.configure(text=t("radio_extra_btn"))
        self._lbl_btn.configure(text=t("label_button"))
        self._lbl_type.configure(text=t("label_type"))
        self._lbl_key.configure(text=t("label_key"))
        self._lbl_extra.configure(text=t("label_button"))
        self._capture_btn.configure(text=t("btn_capture_key"))
        self._capture_mouse_btn.configure(text=t("btn_detect_btn"))
        self._lbl_rand.configure(text=t("random_variation"))
        self._rb_inf.configure(text=t("radio_infinite"))
        self._rb_time.configure(text=t("radio_by_time"))
        self._rb_cursor.configure(text=t("radio_follow_cursor"))
        self._rb_fixed.configure(text=t("radio_fixed_pos"))
        self._rb_zone.configure(text=t("radio_random_zone"))
        self._pick_btn.configure(text=t("btn_pick_pos"))
        self._zone_pick_btn.configure(text=t("btn_pick_zone"))
        self._lbl_from.configure(text=t("zone_from"))
        self._lbl_to.configure(text=t("zone_to"))
        if not self._clicker.is_running:
            self._start_btn.configure(text=t("btn_start", hk=self._hk()))
        else:
            self._start_btn.configure(text=t("btn_stop", hk=self._hk()))
        # Update dropdown values and re-map current selections
        old_btn = self._button_var.get()
        btn_keys = ["btn_left", "btn_middle", "btn_right"]
        new_btn_vals = [t(k) for k in btn_keys]
        self._btn_menu.configure(values=new_btn_vals)
        # Find which internal key matches old value and set new translated value
        _all_btn_translations = {STRINGS[k].get("es", ""): k for k in btn_keys}
        _all_btn_translations.update({STRINGS[k].get("en", ""): k for k in btn_keys})
        matched_key = _all_btn_translations.get(old_btn, "btn_left")
        self._button_var.set(t(matched_key))

        old_type = self._click_type_var.get()
        type_keys = ["click_single", "click_double", "click_triple"]
        new_type_vals = [t(k) for k in type_keys]
        self._type_menu.configure(values=new_type_vals)
        _all_type_translations = {STRINGS[k].get("es", ""): k for k in type_keys}
        _all_type_translations.update({STRINGS[k].get("en", ""): k for k in type_keys})
        matched_type = _all_type_translations.get(old_type, "click_single")
        self._click_type_var.set(t(matched_type))

        old_extra = self._extra_btn_var.get()
        extra_keys = ["btn_back_x1", "btn_forward_x2"]
        new_extra_vals = [t(k) for k in extra_keys]
        self._extra_menu.configure(values=new_extra_vals)
        _all_extra_translations = {STRINGS[k].get("es", ""): k for k in extra_keys}
        _all_extra_translations.update({STRINGS[k].get("en", ""): k for k in extra_keys})
        matched_extra = _all_extra_translations.get(old_extra, "btn_back_x1")
        self._extra_btn_var.set(t(matched_extra))

        if not self._captured_key.get():
            self._key_display.configure(text=t("none_selected"))
        # Scheduler
        self._chk_sched.configure(text=t("chk_schedule"))
        if self._sched_var.get():
            self._sched_status.configure(text=t("schedule_waiting"))

    # ── Toggles ──
    def _toggle_action(self):
        mode = self._action_var.get()
        self._frame_button.pack_forget()
        self._frame_key.pack_forget()
        self._frame_extra.pack_forget()
        if mode == "clic":
            self._frame_button.pack(fill="x", pady=4)
        elif mode == "tecla":
            self._frame_key.pack(fill="x", pady=4)
        elif mode == "extra":
            self._frame_extra.pack(fill="x", pady=4)

    def _toggle_duration(self):
        state = "disabled" if self._dur_var.get() == "infinito" else "normal"
        for child in self._frame_dur_time.winfo_children():
            try:
                child.configure(state=state)
            except Exception:
                pass

    def _toggle_pos(self):
        mode = self._pos_var.get()
        self._frame_pos_fixed.pack_forget()
        self._frame_zone.pack_forget()
        if mode == "fija":
            self._frame_pos_fixed.pack(fill="x", pady=4)
        elif mode == "zona":
            self._frame_zone.pack(fill="x", pady=4)

    # ── Key capture ──
    def _start_key_capture(self):
        from pynput import keyboard
        self._listening_key = True
        self._capture_btn.configure(text=t("btn_capture_key_waiting"), state="disabled", border_color=T.NEON_GREEN)
        self._key_display.configure(text="...", text_color=T.NEON_GREEN)

        def on_press(key):
            if not self._listening_key:
                return False
            self._listening_key = False
            if hasattr(key, "char") and key.char:
                key_str = key.char
            elif hasattr(key, "name"):
                key_str = key.name
            else:
                key_str = str(key)
            self._captured_key.set(key_str)
            self.after(0, lambda: self._key_display.configure(text=key_str.upper(), text_color=T.NEON_YELLOW))
            self.after(0, lambda: self._capture_btn.configure(text=t("btn_capture_key"), state="normal", border_color=T.NEON_YELLOW))
            return False

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    def _start_mouse_btn_capture(self):
        from pynput.mouse import Listener, Button
        self._capture_mouse_btn.configure(text=t("btn_detect_btn_waiting"), state="disabled", border_color=T.NEON_GREEN)
        self._mouse_btn_display.configure(text="...", text_color=T.NEON_GREEN)
        self._listening_mouse = True

        btn_names = {
            Button.left: t("btn_left"), Button.middle: t("btn_middle"),
            Button.right: t("btn_right"), Button.x1: t("btn_back_x1"),
            Button.x2: t("btn_forward_x2"),
        }

        def on_click(x, y, button, pressed):
            if not pressed or not self._listening_mouse:
                return
            self._listening_mouse = False
            name = btn_names.get(button, str(button))
            self._captured_mouse_btn.set(name)
            self._extra_btn_var.set(name)
            self.after(0, lambda: self._mouse_btn_display.configure(text=name.upper(), text_color=T.NEON_PURPLE))
            self.after(0, lambda: self._capture_mouse_btn.configure(
                text=t("btn_detect_btn"), state="normal", border_color=T.NEON_PURPLE))
            return False

        listener = Listener(on_click=on_click)
        listener.daemon = True
        listener.start()

    # ── Position pickers ──
    def _pick_position(self):
        from pynput.mouse import Listener
        self._pick_btn.configure(text=t("btn_pick_pos_waiting"), state="disabled")
        self._picking_pos = True

        def on_click(x, y, button, pressed):
            if pressed and self._picking_pos:
                self._picking_pos = False
                self._x_entry.delete(0, "end")
                self._x_entry.insert(0, str(int(x)))
                self._y_entry.delete(0, "end")
                self._y_entry.insert(0, str(int(y)))
                self._pick_btn.configure(text=t("btn_pick_pos"), state="normal")
                return False

        listener = Listener(on_click=on_click)
        listener.daemon = True
        listener.start()

    def _pick_zone(self):
        from pynput.mouse import Listener
        self._picking_zone_step = 1
        self._zone_pick_btn.configure(text=t("btn_pick_zone_1"), state="disabled")

        def on_click(x, y, button, pressed):
            if not pressed:
                return
            if self._picking_zone_step == 1:
                self._zx1.delete(0, "end")
                self._zx1.insert(0, str(int(x)))
                self._zy1.delete(0, "end")
                self._zy1.insert(0, str(int(y)))
                self._picking_zone_step = 2
                self.after(0, lambda: self._zone_pick_btn.configure(text=t("btn_pick_zone_2")))
            elif self._picking_zone_step == 2:
                self._zx2.delete(0, "end")
                self._zx2.insert(0, str(int(x)))
                self._zy2.delete(0, "end")
                self._zy2.insert(0, str(int(y)))
                self._picking_zone_step = 0
                self.after(0, lambda: self._zone_pick_btn.configure(text=t("btn_pick_zone"), state="normal"))
                return False

        listener = Listener(on_click=on_click)
        listener.daemon = True
        listener.start()

    # ── Helpers ──
    def _get_interval_ms(self) -> int:
        h = int(self._h_int.get() or 0)
        m = int(self._m_int.get() or 0)
        s = int(self._s_int.get() or 0)
        ms = int(self._ms_int.get() or 0)
        return (h * 3600 + m * 60 + s) * 1000 + ms

    def _get_duration_ms(self) -> int:
        if self._dur_var.get() == "infinito":
            return 0
        h = int(self._h_dur.get() or 0)
        m = int(self._m_dur.get() or 0)
        s = int(self._s_dur.get() or 0)
        return (h * 3600 + m * 60 + s) * 1000

    # ── Start / Stop ──
    def toggle(self):
        if self._clicker.is_running:
            self._clicker.stop()
            self._start_btn.configure(text=t("btn_start", hk=self._hk()), **T.neon_btn_style(T.NEON_GREEN))
            if self._countdown_id:
                self.after_cancel(self._countdown_id)
                self._countdown_id = None
        else:
            countdown = load_config().get("countdown_seconds", 3)
            if countdown <= 0:
                self._do_start()
            else:
                self._start_countdown(countdown)

    def _start_countdown(self, n):
        if n <= 0:
            self._do_start()
            return
        self._start_btn.configure(
            text=t("countdown", n=n),
            fg_color=T.NEON_YELLOW, hover_color=T.NEON_YELLOW, text_color=T.BG_DARK,
        )
        self._countdown_id = self.after(1000, lambda: self._start_countdown(n - 1))

    def _do_start(self):
        self._countdown_id = None
        interval_ms = self._get_interval_ms()
        if interval_ms <= 0:
            interval_ms = 100
        duration_ms = self._get_duration_ms()
        random_interval_ms = int(self._rand_ms.get() or 0)

        # Reverse maps: translated display text → internal key
        btn_rev = {
            t("btn_left"): "left", t("btn_middle"): "middle", t("btn_right"): "right",
            t("btn_back_x1"): "x1", t("btn_forward_x2"): "x2",
        }
        type_rev = {
            t("click_single"): "single", t("click_double"): "double", t("click_triple"): "triple",
        }

        custom_key = None
        button = btn_rev.get(self._button_var.get(), "left")
        click_type = type_rev.get(self._click_type_var.get(), "single")
        action = self._action_var.get()
        if action == "tecla":
            custom_key = self._captured_key.get().strip() or None
            button = "left"
        elif action == "extra":
            button = btn_rev.get(self._extra_btn_var.get(), "x1")

        fixed_pos = None
        random_zone = None
        mode = self._pos_var.get()
        if mode == "fija":
            try:
                fixed_pos = (int(self._x_entry.get()), int(self._y_entry.get()))
            except ValueError:
                pass
        elif mode == "zona":
            try:
                random_zone = (int(self._zx1.get()), int(self._zy1.get()),
                               int(self._zx2.get()), int(self._zy2.get()))
            except ValueError:
                pass

        self._clicker.start(
            button=button, custom_key=custom_key, interval_ms=interval_ms,
            duration_ms=duration_ms, fixed_pos=fixed_pos, click_type=click_type,
            random_zone=random_zone, random_interval_ms=random_interval_ms,
        )
        self._start_btn.configure(text=t("btn_stop", hk=self._hk()), **T.neon_btn_style(T.NEON_RED))
        if duration_ms > 0:
            self.after(duration_ms + 200, self._check_stopped)

    def _check_stopped(self):
        if not self._clicker.is_running:
            self._start_btn.configure(text=t("btn_start", hk=self._hk()), **T.neon_btn_style(T.NEON_GREEN))
            # Sound notification when auto-click by duration finishes
            try:
                config = load_config()
                if config.get("notify_on_finish", True):
                    import winsound
                    winsound.MessageBeep()
            except Exception:
                pass

    # ── Profiles ──
    def _get_state(self) -> dict:
        return {
            "action": self._action_var.get(), "button": self._button_var.get(),
            "click_type": self._click_type_var.get(), "captured_key": self._captured_key.get(),
            "h_int": self._h_int.get(), "m_int": self._m_int.get(),
            "s_int": self._s_int.get(), "ms_int": self._ms_int.get(),
            "rand_ms": self._rand_ms.get(), "dur": self._dur_var.get(),
            "h_dur": self._h_dur.get(), "m_dur": self._m_dur.get(), "s_dur": self._s_dur.get(),
            "pos": self._pos_var.get(), "x": self._x_entry.get(), "y": self._y_entry.get(),
            "zx1": self._zx1.get(), "zy1": self._zy1.get(),
            "zx2": self._zx2.get(), "zy2": self._zy2.get(),
            "extra_btn": self._extra_btn_var.get(),
        }

    def _set_state(self, d: dict):
        for var, key in [(self._action_var, "action"), (self._button_var, "button"),
                         (self._click_type_var, "click_type"), (self._captured_key, "captured_key"),
                         (self._h_int, "h_int"), (self._m_int, "m_int"),
                         (self._s_int, "s_int"), (self._ms_int, "ms_int"),
                         (self._rand_ms, "rand_ms"), (self._dur_var, "dur"),
                         (self._h_dur, "h_dur"), (self._m_dur, "m_dur"),
                         (self._s_dur, "s_dur"), (self._pos_var, "pos"),
                         (self._extra_btn_var, "extra_btn")]:
            if key in d:
                var.set(d[key])
        for entry, key in [(self._x_entry, "x"), (self._y_entry, "y"),
                           (self._zx1, "zx1"), (self._zy1, "zy1"),
                           (self._zx2, "zx2"), (self._zy2, "zy2")]:
            if key in d:
                entry.delete(0, "end")
                entry.insert(0, d[key])
        if self._captured_key.get():
            self._key_display.configure(text=self._captured_key.get().upper())
        self._toggle_action()
        self._toggle_duration()
        self._toggle_pos()

    def _save_profile(self):
        name = self._profile_name_entry.get().strip()
        if not name:
            return
        save_profile(name, self._get_state())
        self._refresh_profiles()

    def _load_profile(self):
        name = self._profile_var.get()
        if not name or name == t("empty"):
            return
        data = load_profile(name)
        if data:
            self._set_state(data)

    def _delete_profile(self):
        name = self._profile_var.get()
        if not name or name == t("empty"):
            return
        from src.ui.confirm_dialog import ConfirmDialog
        ConfirmDialog(
            self.winfo_toplevel(),
            title=t("confirm_delete_title"),
            message=t("confirm_delete_msg", name=name),
            on_result=lambda confirmed: self._do_delete_profile(name) if confirmed else None,
        )

    def _do_delete_profile(self, name: str):
        delete_profile(name)
        self._refresh_profiles()

    def _refresh_profiles(self):
        names = list_profiles()
        self._profile_menu.configure(values=names or [t("empty")])
        self._profile_var.set(names[0] if names else t("empty"))

    # ── Scheduler ──
    def _toggle_scheduler(self):
        if self._sched_var.get():
            self._sched_status.configure(text=t("schedule_waiting"))
            self._sched_check()
        else:
            self._sched_status.configure(text="")
            if self._sched_after_id:
                self.after_cancel(self._sched_after_id)
                self._sched_after_id = None

    def _sched_check(self):
        if not self._sched_var.get():
            return
        now = datetime.datetime.now()
        try:
            target_h = int(self._sched_hour.get())
            target_m = int(self._sched_min.get())
        except ValueError:
            self._sched_after_id = self.after(1000, self._sched_check)
            return

        if now.hour == target_h and now.minute == target_m and not self._clicker.is_running:
            self._sched_var.set(False)
            self._sched_status.configure(text="")
            self.toggle()
        else:
            self._sched_after_id = self.after(1000, self._sched_check)
