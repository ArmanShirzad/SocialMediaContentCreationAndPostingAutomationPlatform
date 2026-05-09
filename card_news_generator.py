"""Card news image generator for Instagram (1080x1350, 4:5 ratio)."""

import json
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Colors matching DESIGN.md
BG_DARK = (26, 26, 46)       # #1a1a2e
BG_GRADIENT = (22, 33, 62)   # #16213e
ACCENT = (212, 165, 116)     # #D4A574
WHITE = (255, 255, 255)
TEXT_GRAY = (170, 170, 170)
TEXT_DIM = (140, 140, 140)
CARD_BG = (250, 250, 250)

WIDTH = 1080
HEIGHT = 1350
HERO_HEIGHT = int(HEIGHT * 0.55)

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"


def load_font(size, index=0):
    """Load AppleSDGothicNeo at given size. index: 0=Regular, 3=Semibold, 5=Bold, 8=Heavy."""
    try:
        return ImageFont.truetype(FONT_PATH, size, index=index)
    except Exception:
        return ImageFont.truetype(FONT_PATH, size, index=0)


def draw_gradient(draw, y_start, y_end, color_top, color_bottom):
    """Draw a vertical linear gradient."""
    for y in range(y_start, y_end):
        ratio = (y - y_start) / max(1, y_end - y_start)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def wrap_text(text, font, max_width, draw):
    """Word-wrap text to fit within max_width pixels."""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        chars = list(paragraph)
        current = ""
        for ch in chars:
            test = current + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width:
                if current:
                    lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)
    return lines


def generate(title, summary, output_path, source="ContentFlow", date_str=None):
    """Generate a card news image."""
    import datetime
    if not date_str:
        date_str = datetime.date.today().strftime("%Y.%m.%d")

    img = Image.new("RGB", (WIDTH, HEIGHT), CARD_BG)
    draw = ImageDraw.Draw(img)

    # Hero gradient background
    draw_gradient(draw, 0, HERO_HEIGHT, BG_DARK, BG_GRADIENT)

    # Category label
    font_category = load_font(28, index=5)
    draw.text((72, HERO_HEIGHT - 280), "TECH NEWS", font=font_category, fill=ACCENT)

    # Title
    font_title = load_font(52, index=8)
    title_lines = wrap_text(title, font_title, WIDTH - 144, draw)
    title_y = HERO_HEIGHT - 230
    for line in title_lines[:4]:
        draw.text((72, title_y), line, font=font_title, fill=WHITE)
        title_y += 68

    # Accent divider line
    divider_y = HERO_HEIGHT + 40
    draw.rectangle([(72, divider_y), (72 + 60, divider_y + 4)], fill=ACCENT)

    # Summary
    font_summary = load_font(34, index=0)
    summary_lines = wrap_text(summary, font_summary, WIDTH - 144, draw)
    summary_y = divider_y + 36
    for line in summary_lines[:8]:
        draw.text((72, summary_y), line, font=font_summary, fill=(85, 85, 85))
        summary_y += 52

    # Footer
    font_footer = load_font(26, index=3)
    footer_y = HEIGHT - 80
    draw.text((72, footer_y), source, font=font_footer, fill=TEXT_DIM)

    font_date = load_font(24, index=0)
    date_bbox = draw.textbbox((0, 0), date_str, font=font_date)
    date_w = date_bbox[2] - date_bbox[0]
    draw.text((WIDTH - 72 - date_w, footer_y + 2), date_str, font=font_date, fill=TEXT_DIM)

    # Subtle border
    draw.rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], outline=(220, 220, 220), width=1)

    img.save(output_path, "PNG", quality=95)
    return output_path


if __name__ == "__main__":
    data = json.loads(sys.argv[1])
    result = generate(
        title=data["title"],
        summary=data["summary"],
        output_path=data["output_path"],
        source=data.get("source", "ContentFlow"),
        date_str=data.get("date"),
    )
    print(json.dumps({"success": True, "path": result}))
