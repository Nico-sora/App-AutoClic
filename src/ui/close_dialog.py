import customtkinter as ctk
from src.ui import theme as T
from src.utils.i18n import t


class CloseDialog(ctk.CTkToplevel):
    """Custom dialog shown when user clicks X: close or minimize to tray."""

    def __init__(self, master, on_choice: callable):
        super().__init__(master)
        self._on_choice = on_choice
        self.title("AutoClic")
        self.geometry("340x220")
        self.resizable(False, False)
        self.configure(fg_color=T.BG_DARK)
        self.transient(master)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        px = master.winfo_x() + (master.winfo_width() - 340) // 2
        py = master.winfo_y() + (master.winfo_height() - 220) // 2
        self.geometry(f"+{px}+{py}")

        # Title
        ctk.CTkLabel(
            self, text=t("close_dialog_title"),
            font=T.FONT_SECTION, text_color=T.TEXT_PRIMARY,
        ).pack(pady=(24, 16))

        # Close button
        ctk.CTkButton(
            self, text=t("close_btn_quit"), height=38, width=260,
            fg_color=T.NEON_RED, hover_color=T.NEON_RED + "CC",
            text_color=T.BG_DARK, font=T.FONT_BODY,
            corner_radius=T.CORNER_RADIUS_SM,
            command=lambda: self._choose("close"),
        ).pack(pady=(0, 8))

        # Tray button
        ctk.CTkButton(
            self, text=t("close_btn_tray"), height=38, width=260,
            fg_color=T.NEON_CYAN, hover_color=T.NEON_CYAN + "CC",
            text_color=T.BG_DARK, font=T.FONT_BODY,
            corner_radius=T.CORNER_RADIUS_SM,
            command=lambda: self._choose("tray"),
        ).pack(pady=(0, 12))

        # Remember checkbox
        self._remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text=t("close_chk_remember"), variable=self._remember_var,
            fg_color=T.NEON_PURPLE, hover_color=T.NEON_PURPLE + "88",
            border_color=T.BORDER_DIM, text_color=T.TEXT_SECONDARY,
            font=T.FONT_SMALL,
        ).pack()

        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _choose(self, action: str):
        remember = self._remember_var.get()
        self.grab_release()
        self.destroy()
        self._on_choice(action, remember)

    def _cancel(self):
        self.grab_release()
        self.destroy()
