import customtkinter as ctk
from src.ui import theme as T


class SplashScreen(ctk.CTkToplevel):
    """Splash screen shown during app startup."""

    def __init__(self, master, version: str = "1.0.0"):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(fg_color=T.BG_DARK)
        self.attributes("-topmost", True)

        width, height = 380, 200
        sx = self.winfo_screenwidth() // 2 - width // 2
        sy = self.winfo_screenheight() // 2 - height // 2
        self.geometry(f"{width}x{height}+{sx}+{sy}")

        # Border frame
        border = ctk.CTkFrame(self, fg_color=T.BG_DARK, border_width=2, border_color=T.NEON_GREEN, corner_radius=12)
        border.pack(fill="both", expand=True, padx=2, pady=2)

        # Title
        title_frame = ctk.CTkFrame(border, fg_color="transparent")
        title_frame.pack(pady=(30, 8))
        ctk.CTkLabel(title_frame, text="AUTO", font=("Segoe UI", 32, "bold"),
                     text_color=T.NEON_GREEN).pack(side="left")
        ctk.CTkLabel(title_frame, text="CLIC", font=("Segoe UI", 32, "bold"),
                     text_color=T.NEON_CYAN).pack(side="left", padx=(2, 0))

        # Version
        ctk.CTkLabel(border, text=f"v{version}", font=T.FONT_SMALL,
                     text_color=T.TEXT_MUTED).pack(pady=(0, 16))

        # Progress bar
        self._progress = ctk.CTkProgressBar(
            border, width=280, height=6,
            fg_color=T.BG_INPUT, progress_color=T.NEON_GREEN,
            corner_radius=3,
        )
        self._progress.pack(pady=(0, 20))
        self._progress.set(0)

        self._step = 0
        self._animate()

    def _animate(self):
        self._step += 1
        progress = min(self._step / 15, 1.0)
        self._progress.set(progress)
        if progress < 1.0:
            self.after(100, self._animate)
