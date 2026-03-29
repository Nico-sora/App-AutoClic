import customtkinter as ctk
from pynput.mouse import Controller as MouseController

from src.core.clicker import Clicker
from src.core.recorder import Recorder
from src.core.player import Player
from src.ui import theme as T
from src.utils.i18n import t, on_lang_change
from src.ui.tab_autoclick import TabAutoClick
from src.ui.tab_recorder import TabRecorder
from src.ui.tab_settings import TabSettings
from src.ui.tab_donate import TabDonate
from src.ui.tab_contact import TabContact


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, clicker: Clicker, recorder: Recorder, player: Player,
                 on_hotkeys_changed: callable = None,
                 on_topmost_changed: callable = None, **kwargs):
        super().__init__(master, fg_color=T.BG_DARK, **kwargs)

        self._clicker = clicker
        self._player = player
        self._recorder = recorder
        self._mouse = MouseController()

        # ── Header neon ──
        header = ctk.CTkFrame(self, fg_color=T.BG_DARK, height=56)
        header.pack(fill="x", padx=16, pady=(12, 0))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="AUTO", font=("Segoe UI", 26, "bold"),
                      text_color=T.NEON_GREEN).pack(side="left")
        ctk.CTkLabel(header, text="CLIC", font=("Segoe UI", 26, "bold"),
                      text_color=T.NEON_CYAN).pack(side="left", padx=(2, 0))
        self._subtitle = ctk.CTkLabel(header, text=t("app_subtitle"),
                      font=T.FONT_SMALL, text_color=T.TEXT_MUTED)
        self._subtitle.pack(side="left", padx=(12, 0), pady=(6, 0))

        ctk.CTkFrame(self, height=2, fg_color=T.NEON_GREEN, corner_radius=0).pack(fill="x", padx=16, pady=(4, 0))
        ctk.CTkFrame(self, height=1, fg_color=T.BORDER_DIM, corner_radius=0).pack(fill="x", padx=16)

        # ── Tabs ──
        self._tabview = ctk.CTkTabview(
            self, fg_color=T.BG_DARK,
            segmented_button_fg_color=T.BG_CARD,
            segmented_button_selected_color=T.NEON_GREEN,
            segmented_button_selected_hover_color=T.NEON_GREEN + "CC",
            segmented_button_unselected_color=T.BG_CARD,
            segmented_button_unselected_hover_color=T.BG_CARD_HOVER,
            text_color=T.BG_DARK,
            corner_radius=T.CORNER_RADIUS,
        )
        self._tabview.pack(fill="both", expand=True, padx=12, pady=(6, 4))

        # Tab names used as internal keys (never change)
        self._tab_keys = ["  Auto Clic  ", "  Grabador  ", "  Configuración  ", "  Donar  ", "  Contacto  "]
        self._tab_i18n = ["tab_autoclick", "tab_recorder", "tab_settings", "tab_donate", "tab_contact"]

        tab1 = self._tabview.add(self._tab_keys[0])
        tab2 = self._tabview.add(self._tab_keys[1])
        tab3 = self._tabview.add(self._tab_keys[2])
        tab4 = self._tabview.add(self._tab_keys[3])
        tab5 = self._tabview.add(self._tab_keys[4])

        tab1.configure(fg_color=T.BG_DARK)
        tab2.configure(fg_color=T.BG_DARK)
        tab3.configure(fg_color=T.BG_DARK)
        tab4.configure(fg_color=T.BG_DARK)
        tab5.configure(fg_color=T.BG_DARK)

        self.tab_autoclick = TabAutoClick(tab1, clicker)
        self.tab_autoclick.pack(fill="both", expand=True)

        self.tab_recorder = TabRecorder(tab2, recorder, player)
        self.tab_recorder.pack(fill="both", expand=True)

        self.tab_settings = TabSettings(tab3, on_hotkeys_changed=on_hotkeys_changed,
                                         on_topmost_changed=on_topmost_changed)
        self.tab_settings.pack(fill="both", expand=True)

        self.tab_donate = TabDonate(tab4)
        self.tab_donate.pack(fill="both", expand=True)

        self.tab_contact = TabContact(tab5)
        self.tab_contact.pack(fill="both", expand=True)

        # ── Status bar ──
        self._statusbar = ctk.CTkFrame(self, fg_color=T.BG_CARD, height=30, corner_radius=0)
        self._statusbar.pack(fill="x", side="bottom")
        self._statusbar.pack_propagate(False)

        self._status_dot = ctk.CTkLabel(self._statusbar, text="●", font=("", 12),
                                         text_color=T.TEXT_MUTED, width=20)
        self._status_dot.pack(side="left", padx=(12, 2))

        self._status_label = ctk.CTkLabel(self._statusbar, text=t("inactive"),
                                           font=T.FONT_SMALL, text_color=T.TEXT_SECONDARY)
        self._status_label.pack(side="left")

        self._click_count_label = ctk.CTkLabel(self._statusbar, text=f"{t('clicks')}: 0",
                                                font=T.FONT_MONO, text_color=T.TEXT_MUTED)
        self._click_count_label.pack(side="left", padx=(20, 0))

        self._pos_label = ctk.CTkLabel(self._statusbar, text="X: 0  Y: 0",
                                        font=T.FONT_MONO, text_color=T.TEXT_MUTED)
        self._pos_label.pack(side="right", padx=(0, 12))

        on_lang_change(self._refresh_lang)
        self._update_statusbar()

    def _refresh_lang(self):
        self._subtitle.configure(text=t("app_subtitle"))
        # Update tab button texts via internal segmented button
        try:
            buttons = self._tabview._segmented_button._buttons_dict
            for tab_key, i18n_key in zip(self._tab_keys, self._tab_i18n):
                if tab_key in buttons:
                    buttons[tab_key].configure(text=t(i18n_key))
        except AttributeError:
            pass

    def _update_statusbar(self):
        if self._clicker.is_running:
            self._status_dot.configure(text_color=T.NEON_GREEN)
            self._status_label.configure(text=t("active"), text_color=T.NEON_GREEN)
            self._click_count_label.configure(
                text=f"{t('clicks')}: {self._clicker.click_count}", text_color=T.NEON_YELLOW)
        elif self._player.is_playing:
            self._status_dot.configure(text_color=T.NEON_CYAN)
            self._status_label.configure(text=t("playing"), text_color=T.NEON_CYAN)
            self._click_count_label.configure(text="", text_color=T.TEXT_MUTED)
        elif self._recorder.is_recording:
            self._status_dot.configure(text_color=T.NEON_RED)
            self._status_label.configure(text=t("recording_status"), text_color=T.NEON_RED)
            self._click_count_label.configure(text="", text_color=T.TEXT_MUTED)
        else:
            self._status_dot.configure(text_color=T.TEXT_MUTED)
            self._status_label.configure(text=t("inactive"), text_color=T.TEXT_SECONDARY)
            self._click_count_label.configure(
                text=f"{t('clicks')}: {self._clicker.click_count}", text_color=T.TEXT_MUTED)

        try:
            pos = self._mouse.position
            self._pos_label.configure(text=f"X: {int(pos[0])}  Y: {int(pos[1])}")
        except Exception:
            pass

        self.after(100, self._update_statusbar)
