NEON_GREEN = "#00FF88"
NEON_CYAN = "#00D4FF"
NEON_RED = "#FF3366"
NEON_YELLOW = "#FFE156"
NEON_PURPLE = "#B44AFF"

BG_DARK = "#0D0D0D"
BG_CARD = "#1A1A1A"
BG_CARD_HOVER = "#222222"
BG_INPUT = "#141414"
BORDER_DIM = "#2A2A2A"
BORDER_GLOW = "#00FF8844"

TEXT_PRIMARY = "#E8E8E8"
TEXT_SECONDARY = "#888888"
TEXT_MUTED = "#555555"

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SECTION = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 11)
FONT_MONO = ("Consolas", 11)
FONT_BTN_BIG = ("Segoe UI", 14, "bold")

CORNER_RADIUS = 12
CORNER_RADIUS_SM = 8
BORDER_WIDTH = 1

def card_style():
    return {
        "fg_color": BG_CARD,
        "corner_radius": CORNER_RADIUS,
        "border_width": BORDER_WIDTH,
        "border_color": BORDER_DIM,
    }

def input_style():
    return {
        "fg_color": BG_INPUT,
        "border_color": BORDER_DIM,
        "text_color": TEXT_PRIMARY,
        "corner_radius": CORNER_RADIUS_SM,
    }

def neon_btn_style(color=NEON_GREEN):
    hover = color + "CC" if len(color) == 7 else color
    return {
        "fg_color": color,
        "hover_color": hover,
        "text_color": BG_DARK,
        "corner_radius": CORNER_RADIUS_SM,
        "font": FONT_BTN_BIG,
    }

def danger_btn_style():
    return neon_btn_style(NEON_RED)

def option_menu_style():
    return {
        "fg_color": BG_INPUT,
        "button_color": BORDER_DIM,
        "button_hover_color": "#3A3A3A",
        "dropdown_fg_color": BG_CARD,
        "dropdown_hover_color": BG_CARD_HOVER,
        "text_color": TEXT_PRIMARY,
        "corner_radius": CORNER_RADIUS_SM,
    }

def radio_style(color=NEON_CYAN):
    return {
        "fg_color": color,
        "border_color": BORDER_DIM,
        "hover_color": color + "88" if len(color) == 7 else color,
        "text_color": TEXT_PRIMARY,
        "font": FONT_BODY,
    }
