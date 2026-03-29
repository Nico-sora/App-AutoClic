import webbrowser
import customtkinter as ctk
from src.ui import theme as T
from src.utils.i18n import t, on_lang_change

# ── PLACEHOLDER: Replace these with your real links ──
PAYPAL_URL = "https://www.paypal.com/donate/?hosted_button_id=3VEC3FMJGQKEC"
GITHUB_SPONSORS_URL = "https://github.com/sponsors/Nico-sora"


class TabDonate(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=T.BG_DARK, **kwargs)
        self._build_ui()
        on_lang_change(self._refresh_lang)

    def _build_ui(self):
        # Center container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.45, anchor="center")

        # Heart icon
        ctk.CTkLabel(
            container, text="\u2764", font=("Segoe UI Emoji", 48),
            text_color=T.NEON_RED,
        ).pack(pady=(0, 8))

        # Title
        self._title = ctk.CTkLabel(
            container, text=t("donate_title"),
            font=("Segoe UI", 20, "bold"), text_color=T.TEXT_PRIMARY,
        )
        self._title.pack(pady=(0, 12))

        # Description
        self._desc = ctk.CTkLabel(
            container, text=t("donate_desc"),
            font=T.FONT_BODY, text_color=T.TEXT_SECONDARY,
            justify="center",
        )
        self._desc.pack(pady=(0, 24))

        # PayPal button
        self._btn_paypal = ctk.CTkButton(
            container, text=t("donate_paypal"), height=44, width=280,
            fg_color="#0070BA", hover_color="#005A9E",
            text_color="#FFFFFF", font=("Segoe UI", 15, "bold"),
            corner_radius=T.CORNER_RADIUS_SM,
            command=lambda: webbrowser.open(PAYPAL_URL),
        )
        self._btn_paypal.pack(pady=(0, 12))

        # GitHub Sponsors button
        self._btn_github = ctk.CTkButton(
            container, text=t("donate_github"), height=44, width=280,
            fg_color="#24292F", hover_color="#1B1F23",
            text_color="#FFFFFF", font=("Segoe UI", 15, "bold"),
            corner_radius=T.CORNER_RADIUS_SM,
            command=lambda: webbrowser.open(GITHUB_SPONSORS_URL),
        )
        self._btn_github.pack(pady=(0, 20))

        # Thanks message
        self._thanks = ctk.CTkLabel(
            container, text=t("donate_thanks"),
            font=T.FONT_SMALL, text_color=T.TEXT_MUTED,
        )
        self._thanks.pack()

    def _refresh_lang(self):
        self._title.configure(text=t("donate_title"))
        self._desc.configure(text=t("donate_desc"))
        self._btn_paypal.configure(text=t("donate_paypal"))
        self._btn_github.configure(text=t("donate_github"))
        self._thanks.configure(text=t("donate_thanks"))
