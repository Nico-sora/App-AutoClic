import json
import customtkinter as ctk
from tkinter import filedialog
from src.core.recorder import Recorder, Recording
from src.core.player import Player
from src.ui import theme as T
from src.ui.tooltip import Tooltip
from src.utils.i18n import t, on_lang_change
from src.utils.config import load_config
from src.utils.macros import save_macro, load_macro, list_macros, delete_macro


class TabRecorder(ctk.CTkFrame):
    def __init__(self, master, recorder: Recorder, player: Player, **kwargs):
        super().__init__(master, fg_color=T.BG_DARK, **kwargs)
        self._recorder = recorder
        self._player = player
        self._sec_labels = {}
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

    def _hk_rec(self):
        return load_config().get("hotkey_record", "F7")

    def _hk_play(self):
        return load_config().get("hotkey_play", "F8")

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=T.BG_DARK)
        scroll.pack(fill="both", expand=True)

        # ── Grabación ──
        sec = self._section(scroll, "sec_recording", "⏺")
        body = ctk.CTkFrame(sec, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")

        self._rec_btn = ctk.CTkButton(
            row, text=t("btn_record", hk=self._hk_rec()), width=180,
            fg_color=T.NEON_RED, hover_color=T.NEON_RED + "CC",
            text_color=T.BG_DARK, font=T.FONT_SECTION,
            corner_radius=T.CORNER_RADIUS_SM, command=self.toggle_record,
        )
        self._rec_btn.pack(side="left", padx=(0, 12))
        self._rec_status = ctk.CTkLabel(row, text=t("rec_stopped"), font=T.FONT_BODY, text_color=T.TEXT_MUTED)
        self._rec_status.pack(side="left")

        # ── Eventos ──
        sec_list = self._section(scroll, "sec_events", "📋")
        self._textbox = ctk.CTkTextbox(
            sec_list, height=150, state="disabled",
            fg_color=T.BG_INPUT, text_color=T.NEON_GREEN,
            font=T.FONT_MONO, corner_radius=T.CORNER_RADIUS_SM,
            border_width=1, border_color=T.BORDER_DIM,
        )
        self._textbox.pack(fill="both", expand=True, padx=14, pady=(4, 6))

        row_btns = ctk.CTkFrame(sec_list, fg_color="transparent")
        row_btns.pack(fill="x", padx=14, pady=(0, 10))
        btn_s = {"fg_color": T.BG_INPUT, "hover_color": T.BG_CARD_HOVER,
                 "border_width": 1, "border_color": T.BORDER_DIM,
                 "text_color": T.TEXT_SECONDARY, "font": T.FONT_SMALL}

        self._btn_clear = ctk.CTkButton(row_btns, text=t("btn_clear"), width=80, command=self._clear_events, **btn_s)
        self._btn_clear.pack(side="left", padx=(0, 4))
        self._btn_del_event = ctk.CTkButton(
            row_btns, text=t("btn_delete_event"), width=110, command=self._delete_selected_event,
            **{**btn_s, "border_color": T.NEON_RED, "text_color": T.NEON_RED})
        self._btn_del_event.pack(side="left", padx=4)
        self._btn_save_f = ctk.CTkButton(row_btns, text=t("btn_save_file"), width=80, command=self._save_recording,
                       **{**btn_s, "border_color": T.NEON_GREEN, "text_color": T.NEON_GREEN})
        self._btn_save_f.pack(side="left", padx=4)
        self._btn_load_f = ctk.CTkButton(row_btns, text=t("btn_load_file"), width=80, command=self._load_recording,
                       **{**btn_s, "border_color": T.NEON_CYAN, "text_color": T.NEON_CYAN})
        self._btn_load_f.pack(side="left", padx=4)

        self._event_count_label = ctk.CTkLabel(row_btns, text=t("events_count", n=0), font=T.FONT_MONO, text_color=T.TEXT_MUTED)
        self._event_count_label.pack(side="right")

        # ── Macros guardadas ──
        sec_macros = self._section(scroll, "sec_macros", "📁")
        body_m = ctk.CTkFrame(sec_macros, fg_color="transparent")
        body_m.pack(fill="x", padx=14, pady=(4, 10))

        row_m = ctk.CTkFrame(body_m, fg_color="transparent")
        row_m.pack(fill="x", pady=2)

        self._macro_var = ctk.StringVar(value="")
        self._macro_menu = ctk.CTkOptionMenu(
            row_m, variable=self._macro_var, values=list_macros() or [t("empty")],
            width=160, **T.option_menu_style(),
        )
        self._macro_menu.pack(side="left", padx=(0, 8))

        self._btn_load_macro = ctk.CTkButton(row_m, text=t("btn_load"), width=70, fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                       border_width=1, border_color=T.NEON_CYAN, text_color=T.NEON_CYAN,
                       font=T.FONT_SMALL, command=self._load_macro)
        self._btn_load_macro.pack(side="left", padx=2)
        self._btn_save_macro = ctk.CTkButton(row_m, text=t("btn_save"), width=70, fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                       border_width=1, border_color=T.NEON_GREEN, text_color=T.NEON_GREEN,
                       font=T.FONT_SMALL, command=self._save_macro)
        self._btn_save_macro.pack(side="left", padx=2)
        self._btn_del_macro = ctk.CTkButton(row_m, text=t("btn_delete"), width=70, fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
                       border_width=1, border_color=T.NEON_RED, text_color=T.NEON_RED,
                       font=T.FONT_SMALL, command=self._delete_macro)
        self._btn_del_macro.pack(side="left", padx=2)

        row_m2 = ctk.CTkFrame(body_m, fg_color="transparent")
        row_m2.pack(fill="x", pady=(4, 0))
        self._lbl_macro_name = ctk.CTkLabel(row_m2, text=t("name"), font=T.FONT_SMALL, text_color=T.TEXT_MUTED)
        self._lbl_macro_name.pack(side="left", padx=(0, 6))
        self._macro_name_entry = ctk.CTkEntry(row_m2, width=180, placeholder_text=t("macro_name_placeholder"), **T.input_style())
        self._macro_name_entry.pack(side="left")

        # ── Reproducción ──
        sec_play = self._section(scroll, "sec_playback", "▶")
        body = ctk.CTkFrame(sec_play, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 6))

        row_opts = ctk.CTkFrame(body, fg_color="transparent")
        row_opts.pack(fill="x", pady=2)

        self._lbl_repeat = ctk.CTkLabel(row_opts, text=t("label_repeat"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_repeat.pack(side="left", padx=(0, 6))
        self._repeat_var = ctk.StringVar(value="1")
        self._repeat_entry = ctk.CTkEntry(row_opts, width=55, textvariable=self._repeat_var, justify="center", **T.input_style())
        self._repeat_entry.pack(side="left", padx=(0, 6))
        self._lbl_times = ctk.CTkLabel(row_opts, text=t("label_times"), font=T.FONT_SMALL, text_color=T.TEXT_MUTED)
        self._lbl_times.pack(side="left", padx=(0, 20))

        self._lbl_speed = ctk.CTkLabel(row_opts, text=t("label_speed"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_speed.pack(side="left", padx=(0, 6))
        self._speed_var = ctk.StringVar(value="1x")
        self._speed_menu = ctk.CTkOptionMenu(row_opts, variable=self._speed_var,
                          values=["0.25x", "0.5x", "1x", "2x", "4x"], width=85,
                          **T.option_menu_style())
        self._speed_menu.pack(side="left")

        row_interval = ctk.CTkFrame(body, fg_color="transparent")
        row_interval.pack(fill="x", pady=(6, 2))
        self._lbl_wait = ctk.CTkLabel(row_interval, text=t("label_wait_between"), font=T.FONT_BODY, text_color=T.TEXT_SECONDARY)
        self._lbl_wait.pack(side="left", padx=(0, 8))
        self._int_h = ctk.StringVar(value="0")
        self._int_m = ctk.StringVar(value="0")
        self._int_s = ctk.StringVar(value="0")
        for label, var in [("H", self._int_h), ("M", self._int_m), ("S", self._int_s)]:
            ctk.CTkLabel(row_interval, text=label, font=T.FONT_MONO, text_color=T.TEXT_MUTED).pack(side="left", padx=(6, 2))
            ctk.CTkEntry(row_interval, width=50, textvariable=var, justify="center", **T.input_style()).pack(side="left", padx=(0, 2))

        self._play_btn = ctk.CTkButton(
            sec_play, text=t("btn_play", hk=self._hk_play()), height=44,
            **T.neon_btn_style(T.NEON_CYAN), command=self.toggle_play,
        )
        self._play_btn.pack(fill="x", padx=14, pady=(6, 12))

        # ── Tooltips ──
        Tooltip(self._repeat_entry, t("tip_repeat"))
        Tooltip(self._speed_menu, t("tip_speed"))

    def _refresh_lang(self):
        for key, (lbl, icon) in self._sec_labels.items():
            lbl.configure(text=f"{icon}  {t(key)}" if icon else t(key))
        if not self._recorder.is_recording:
            self._rec_btn.configure(text=t("btn_record", hk=self._hk_rec()))
            self._rec_status.configure(text=t("rec_stopped"))
        else:
            self._rec_btn.configure(text=t("btn_stop_record", hk=self._hk_rec()))
            self._rec_status.configure(text=t("rec_recording"))
        self._btn_clear.configure(text=t("btn_clear"))
        self._btn_del_event.configure(text=t("btn_delete_event"))
        self._btn_save_f.configure(text=t("btn_save_file"))
        self._btn_load_f.configure(text=t("btn_load_file"))
        n = len(self._recorder.recording.events)
        self._event_count_label.configure(text=t("events_count", n=n))
        # Macros
        self._btn_load_macro.configure(text=t("btn_load"))
        self._btn_save_macro.configure(text=t("btn_save"))
        self._btn_del_macro.configure(text=t("btn_delete"))
        self._lbl_macro_name.configure(text=t("name"))
        # Playback
        self._lbl_repeat.configure(text=t("label_repeat"))
        self._lbl_times.configure(text=t("label_times"))
        self._lbl_speed.configure(text=t("label_speed"))
        self._lbl_wait.configure(text=t("label_wait_between"))
        if not self._player.is_playing:
            self._play_btn.configure(text=t("btn_play", hk=self._hk_play()))
        else:
            self._play_btn.configure(text=t("btn_stop_play", hk=self._hk_play()))

    def toggle_record(self):
        if self._recorder.is_recording:
            self._recorder.stop()
            self._rec_btn.configure(text=t("btn_record", hk=self._hk_rec()), fg_color=T.NEON_RED, text_color=T.BG_DARK)
            self._rec_status.configure(text=t("rec_stopped"), text_color=T.TEXT_MUTED)
            self._refresh_events()
        else:
            self._recorder.start()
            self._rec_btn.configure(text=t("btn_stop_record", hk=self._hk_rec()), fg_color=T.BG_INPUT, text_color=T.NEON_RED)
            self._rec_status.configure(text=t("rec_recording"), text_color=T.NEON_RED)

    def toggle_play(self):
        if self._player.is_playing:
            self._player.stop()
            self._play_btn.configure(text=t("btn_play", hk=self._hk_play()), **T.neon_btn_style(T.NEON_CYAN))
        else:
            recording = self._recorder.recording
            if not recording.events:
                return
            try:
                repeat = int(self._repeat_var.get() or 1)
            except (ValueError, TypeError):
                repeat = 1
            speed_str = self._speed_var.get().replace("x", "")
            try:
                speed = float(speed_str) if speed_str else 1.0
            except (ValueError, TypeError):
                speed = 1.0
            try:
                h = int(self._int_h.get() or 0)
                m = int(self._int_m.get() or 0)
                s = int(self._int_s.get() or 0)
            except (ValueError, TypeError):
                h, m, s = 0, 0, 0
            interval_ms = (h * 3600 + m * 60 + s) * 1000
            self._player.play(recording, repeat=repeat, speed=speed, interval_ms=interval_ms)
            self._play_btn.configure(text=t("btn_stop_play", hk=self._hk_play()), **T.neon_btn_style(T.NEON_RED))
            self._poll_playing()

    def _poll_playing(self):
        if self._player.is_playing:
            self.after(300, self._poll_playing)
        else:
            self._play_btn.configure(text=t("btn_play", hk=self._hk_play()), **T.neon_btn_style(T.NEON_CYAN))

    def _refresh_events(self):
        events = self._recorder.recording.events
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        for i, ev in enumerate(events, 1):
            delay_str = f"[+{ev.delay:.3f}s] " if ev.delay > 0 else ""
            self._textbox.insert("end", f"  {i:>4}  {delay_str}{ev.description()}\n")
        self._textbox.configure(state="disabled")
        self._event_count_label.configure(text=t("events_count", n=len(events)))

    def _clear_events(self):
        self._recorder._recording.events.clear()
        self._refresh_events()

    def _delete_selected_event(self):
        """Delete the last recorded event."""
        events = self._recorder.recording.events
        if not events:
            return
        events.pop()
        self._refresh_events()

    def _save_recording(self):
        recording = self._recorder.recording
        if not recording.events:
            return
        path = filedialog.asksaveasfilename(title=t("dlg_save_rec"), defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(recording.to_list(), f, indent=2, ensure_ascii=False)

    def _load_recording(self):
        path = filedialog.askopenfilename(title=t("dlg_load_rec"), filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._recorder._recording = Recording.from_list(data)
            self._refresh_events()
        except Exception:
            pass

    # ── Macros ──
    def _save_macro(self):
        name = self._macro_name_entry.get().strip()
        if not name:
            return
        recording = self._recorder.recording
        if not recording.events:
            return
        save_macro(name, recording.to_list())
        self._refresh_macros()

    def _load_macro(self):
        name = self._macro_var.get()
        if not name or name == t("empty"):
            return
        data = load_macro(name)
        if data:
            self._recorder._recording = Recording.from_list(data)
            self._refresh_events()

    def _delete_macro(self):
        name = self._macro_var.get()
        if not name or name == t("empty"):
            return
        from src.ui.confirm_dialog import ConfirmDialog
        ConfirmDialog(
            self.winfo_toplevel(),
            title=t("confirm_delete_title"),
            message=t("confirm_delete_macro_msg", name=name),
            on_result=lambda confirmed: self._do_delete_macro(name) if confirmed else None,
        )

    def _do_delete_macro(self, name: str):
        delete_macro(name)
        self._refresh_macros()

    def _refresh_macros(self):
        names = list_macros()
        self._macro_menu.configure(values=names or [t("empty")])
        self._macro_var.set(names[0] if names else t("empty"))
