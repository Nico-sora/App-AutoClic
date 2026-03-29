import webbrowser
from urllib.parse import quote
import customtkinter as ctk
from src.ui import theme as T
from src.utils.i18n import t, on_lang_change

CONTACT_EMAIL = "nico.delpuerto.2000@gmail.com"

SUBJECT_KEYS = [
    "contact_subject_bug",
    "contact_subject_suggestion",
    "contact_subject_question",
    "contact_subject_security",
]


class TabContact(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=T.BG_DARK, **kwargs)
        self._build_ui()
        on_lang_change(self._refresh_lang)

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.45, anchor="center")

        # Mail icon
        ctk.CTkLabel(
            container, text="\u2709", font=("Segoe UI Emoji", 44),
            text_color=T.NEON_CYAN,
        ).pack(pady=(0, 6))

        # Title
        self._title = ctk.CTkLabel(
            container, text=t("contact_title"),
            font=("Segoe UI", 20, "bold"), text_color=T.TEXT_PRIMARY,
        )
        self._title.pack(pady=(0, 16))

        # Subject dropdown
        self._subject_label = ctk.CTkLabel(
            container, text=t("contact_subject"),
            font=T.FONT_SECTION, text_color=T.TEXT_SECONDARY, anchor="w",
        )
        self._subject_label.pack(fill="x", padx=4, pady=(0, 4))

        self._subject_values = [t(k) for k in SUBJECT_KEYS]
        self._subject_var = ctk.StringVar(value=self._subject_values[0])
        self._subject_menu = ctk.CTkOptionMenu(
            container, variable=self._subject_var,
            values=self._subject_values, width=320,
            **T.option_menu_style(),
        )
        self._subject_menu.pack(pady=(0, 12))

        # Email input
        self._email_label = ctk.CTkLabel(
            container, text=t("contact_email"),
            font=T.FONT_SECTION, text_color=T.TEXT_SECONDARY, anchor="w",
        )
        self._email_label.pack(fill="x", padx=4, pady=(0, 4))

        self._email_entry = ctk.CTkEntry(
            container, width=320, height=36,
            placeholder_text="usuario@ejemplo.com",
            **T.input_style(),
        )
        self._email_entry.pack(pady=(0, 12))

        # Message textbox
        self._msg_label = ctk.CTkLabel(
            container, text=t("contact_message"),
            font=T.FONT_SECTION, text_color=T.TEXT_SECONDARY, anchor="w",
        )
        self._msg_label.pack(fill="x", padx=4, pady=(0, 4))

        self._textbox = ctk.CTkTextbox(
            container, width=320, height=110,
            fg_color=T.BG_INPUT, border_color=T.BORDER_DIM,
            text_color=T.TEXT_PRIMARY, corner_radius=T.CORNER_RADIUS_SM,
            font=T.FONT_BODY, border_width=T.BORDER_WIDTH,
        )
        self._textbox.pack(pady=(0, 2))
        self._textbox.bind("<KeyRelease>", self._update_counter)

        # Character counter
        self._counter = ctk.CTkLabel(
            container, text="0 / 400",
            font=T.FONT_SMALL, text_color=T.TEXT_MUTED, anchor="e",
        )
        self._counter.pack(fill="x", padx=8, pady=(0, 12))

        # Send button
        self._btn_send = ctk.CTkButton(
            container, text=t("contact_send"), height=44, width=320,
            **T.neon_btn_style(T.NEON_GREEN),
            command=self._send,
        )
        self._btn_send.pack(pady=(0, 6))

        # Validation message (hidden by default)
        self._validation = ctk.CTkLabel(
            container, text="", font=T.FONT_SMALL,
            text_color=T.NEON_RED, height=20,
        )
        self._validation.pack()

    def _update_counter(self, _event=None):
        text = self._textbox.get("1.0", "end-1c")
        count = len(text)
        if count > 400:
            self._textbox.delete("1.0", "end")
            self._textbox.insert("1.0", text[:400])
            count = 400
        color = T.NEON_RED if count >= 380 else T.NEON_YELLOW if count >= 320 else T.TEXT_MUTED
        self._counter.configure(text=f"{count} / 400", text_color=color)

    def _show_validation(self, msg_key):
        self._validation.configure(text=t(msg_key))
        self.after(3000, lambda: self._validation.configure(text=""))

    def _send(self):
        email = self._email_entry.get().strip()
        message = self._textbox.get("1.0", "end-1c").strip()

        if not email:
            self._show_validation("contact_error_email")
            return
        if not message:
            self._show_validation("contact_error_message")
            return

        subject_text = self._subject_var.get()
        subject = f"[AutoClic] {subject_text}"
        body = f"{message}\n\n---\n{t('contact_from')}: {email}"

        mailto = f"mailto:{CONTACT_EMAIL}?subject={quote(subject)}&body={quote(body)}"
        webbrowser.open(mailto)

    def _refresh_lang(self):
        self._title.configure(text=t("contact_title"))
        self._subject_label.configure(text=t("contact_subject"))
        self._email_label.configure(text=t("contact_email"))
        self._msg_label.configure(text=t("contact_message"))
        self._btn_send.configure(text=t("contact_send"))

        old_idx = 0
        old_val = self._subject_var.get()
        for i, k in enumerate(SUBJECT_KEYS):
            if old_val == self._subject_values[i] if i < len(self._subject_values) else False:
                old_idx = i
                break

        self._subject_values = [t(k) for k in SUBJECT_KEYS]
        self._subject_menu.configure(values=self._subject_values)
        self._subject_var.set(self._subject_values[old_idx])
