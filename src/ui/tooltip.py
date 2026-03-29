import customtkinter as ctk
from src.ui import theme as T


class Tooltip:
    """Simple hover tooltip for any CTk widget."""

    def __init__(self, widget: ctk.CTkBaseClass, text: str, delay: int = 400):
        self._widget = widget
        self._text = text
        self._delay = delay
        self._tip_window: ctk.CTkToplevel | None = None
        self._after_id: str | None = None

        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        if self._tip_window:
            try:
                self._label.configure(text=value)
            except Exception:
                pass

    def _on_enter(self, event=None):
        self._after_id = self._widget.after(self._delay, self._show)

    def _on_leave(self, event=None):
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self):
        if self._tip_window or not self._text:
            return
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4

        self._tip_window = tw = ctk.CTkToplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        tw.configure(fg_color=T.BG_CARD)

        self._label = ctk.CTkLabel(
            tw, text=self._text,
            font=T.FONT_SMALL, text_color=T.TEXT_PRIMARY,
            fg_color=T.BG_CARD, corner_radius=6,
            padx=10, pady=6,
        )
        self._label.pack()

    def _hide(self):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None
