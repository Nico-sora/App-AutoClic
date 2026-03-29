import customtkinter as ctk
from src.ui import theme as T
from src.utils.i18n import t


class ConfirmDialog(ctk.CTkToplevel):
    """Reusable confirmation dialog. Calls on_result(True) or on_result(False)."""

    def __init__(self, master, title: str, message: str, on_result: callable,
                 confirm_text: str | None = None, cancel_text: str | None = None):
        super().__init__(master)
        self._on_result = on_result
        self.title(title)
        self.geometry("380x180")
        self.resizable(False, False)
        self.configure(fg_color=T.BG_DARK)
        self.transient(master)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        px = master.winfo_x() + (master.winfo_width() - 380) // 2
        py = master.winfo_y() + (master.winfo_height() - 180) // 2
        self.geometry(f"+{px}+{py}")

        ctk.CTkLabel(
            self, text=message, font=T.FONT_BODY,
            text_color=T.TEXT_PRIMARY, wraplength=340,
        ).pack(pady=(24, 20))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 16))

        ctk.CTkButton(
            btn_frame, text=confirm_text or t("confirm_yes"), width=140, height=36,
            fg_color=T.NEON_RED, hover_color=T.NEON_RED + "CC",
            text_color=T.BG_DARK, font=T.FONT_BODY,
            corner_radius=T.CORNER_RADIUS_SM,
            command=lambda: self._choose(True),
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            btn_frame, text=cancel_text or t("confirm_cancel"), width=140, height=36,
            fg_color=T.BG_INPUT, hover_color=T.BG_CARD_HOVER,
            border_width=1, border_color=T.BORDER_DIM,
            text_color=T.TEXT_SECONDARY, font=T.FONT_BODY,
            corner_radius=T.CORNER_RADIUS_SM,
            command=lambda: self._choose(False),
        ).pack(side="left")

        self.protocol("WM_DELETE_WINDOW", lambda: self._choose(False))

    def _choose(self, confirmed: bool):
        self.grab_release()
        self.destroy()
        self._on_result(confirmed)
