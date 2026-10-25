import base64
import os
import re
from io import BytesIO

import numpy as np
from PIL import Image

BORDERS_DIR = "borders"
DEFAULT_BORDER = os.path.join(BORDERS_DIR, "default.png")
LOGO = os.path.join(BORDERS_DIR, "logo.png")

def safe_name(name):
    # Remove characters that are not allowed in file names on Windows and Linux
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip()

def border_path(player_name):
    return os.path.join(BORDERS_DIR, f"{safe_name(player_name).lower()}.png")

def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

def rgb_to_hex(color):
    return "#{:02x}{:02x}{:02x}".format(*color)

def make_border(left_color, right_color):
    # Every border is split in two halves, the left one and the right one, each with a single color.
    # Recolor default.png keeping its shape and transparency
    border = np.array(Image.open(DEFAULT_BORDER).convert("RGBA"))
    half = border.shape[1] // 2
    border[:, :half, :3] = hex_to_rgb(left_color)
    border[:, half:, :3] = hex_to_rgb(right_color)
    return Image.fromarray(border)

def save_border(player_name, left_color, right_color):
    path = border_path(player_name)
    make_border(left_color, right_color).save(path)
    return path

def get_border(player_name):
    path = border_path(player_name)
    if not os.path.exists(path):
        path = DEFAULT_BORDER
    return Image.open(path).convert("RGBA")

def dominant_color(pixels):
    opaque = pixels[pixels[:, 3] > 200][:, :3]
    if len(opaque) == 0:
        return "#ffffff"
    colors, counts = np.unique(opaque, axis=0, return_counts=True)
    return rgb_to_hex(colors[counts.argmax()])

def get_border_colors(player_name):
    border = np.array(get_border(player_name))
    half = border.shape[1] // 2
    return {
        "left": dominant_color(border[:, :half].reshape(-1, 4)),
        "right": dominant_color(border[:, half:].reshape(-1, 4)),
        "custom": os.path.exists(border_path(player_name)),
    }

def border_preview(left_color, right_color):
    # Small preview of the border and logo on a dark background, returned as a data URL for the WebUI
    preview = Image.new("RGBA", (1920, 1080), (37, 37, 37, 255))
    preview.alpha_composite(make_border(left_color, right_color))
    if os.path.exists(LOGO):
        preview.alpha_composite(Image.open(LOGO).convert("RGBA"))
    buffer = BytesIO()
    preview.convert("RGB").resize((480, 270), Image.LANCZOS).save(buffer, "PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
