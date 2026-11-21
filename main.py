#!/usr/bin/env python3
"""Passport of the Republic of Ostravane — invented passport spread.

Renders one 1024x724 PNG to /output/entry.png (or ./entry.png when run
locally). No network. All text is drawn programmatically so dates, stamps
and issue details agree exactly; the portrait is a bundled asset.
"""
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"

W, H = 1024, 724
PAPER = (244, 236, 218)
PAPER_DARK = (232, 222, 198)
INK = (28, 32, 48)
INK_SOFT = (58, 62, 78)
RULE = (120, 110, 88)
BLUE = (28, 64, 128)
VIOLET = (96, 48, 128)
RED = (168, 32, 32)
TEAL = (18, 90, 92)


def font(name, size):
    return ImageFont.truetype(str(ASSETS / name), size)


# ---------------------------------------------------------------- MRZ
def _mrz_val(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - 55  # A=10 .. Z=35


def _mrz_check(s):
    total = 0
    for i, ch in enumerate(s):
        total += _mrz_val(ch) * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<OSTHALVORSDATTER<<MAREN<SOLVEIG"
    line1 = (line1 + "<" * 44)[:44]
    doc = "OS4471902"
    dob = "880314"      # 14 MAR 1988
    exp = "350602"      # 02 JUN 2035
    opt = "<" * 15
    body = doc + _mrz_check(doc) + "OST" + dob + _mrz_check(dob) + "F" + exp + _mrz_check(exp) + opt
    line2 = body + _mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


# ---------------------------------------------------------------- helpers
def text(d, xy, s, f, fill=INK, anchor="la", spacing=0):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, spacing=spacing)


def letterspaced(d, xy, s, f, fill, spacing_px):
    """Draw text with extra tracking, left anchored at xy."""
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + spacing_px
    return x


def rule(d, x0, y, x1, color=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def draw_emblem(d, cx, cy, s, color=INK):
    """Lighthouse over waves inside a double ring — Ostravane's arms."""
    r = s // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], outline=color, width=1)
    # tower
    tw = s * 0.10
    d.polygon([(cx - tw, cy + r * 0.55), (cx - tw * 0.7, cy - r * 0.45),
               (cx + tw * 0.7, cy - r * 0.45), (cx + tw, cy + r * 0.55)], fill=color)
    d.rectangle([cx - tw * 0.9, cy - r * 0.62, cx + tw * 0.9, cy - r * 0.45], fill=color)
    # waves
    for k, wy in enumerate((0.28, 0.48)):
        y = cy + r * wy
        pts = []
        for i in range(21):
            xx = cx - r * 0.72 + i * (r * 1.44 / 20)
            yy = y + (4 if i % 2 == 0 else -4)
            pts.append((xx, yy))
        d.line(pts, fill=color, width=2)


def stamp(img, cx, cy, lines, color, angle, w=208, h=76, fsize=15):
    """A rotated rectangular border-control stamp on its own layer."""
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    sd.rounded_rectangle([6, 6, w + 34, h + 34], radius=8,
                         outline=color + (235,), width=2)
    sd.rounded_rectangle([10, 10, w + 30, h + 30], radius=6,
                         outline=color + (235,), width=1)
    f = font("sans-bold.ttf", fsize)
    fs = font("sans.ttf", fsize - 2)
    y = 14
    for i, ln in enumerate(lines):
        ff = f if i == 0 else fs
        tw = sd.textlength(ln, font=ff)
        sd.text(((w + 40 - tw) / 2, y), ln, font=ff, fill=color + (235,))
        y += fsize + 3
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    img.paste(layer, (int(cx - (w + 40) / 2), int(cy - (h + 40) / 2)), layer)


def paper_base():
    rng = random.Random(20250602)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    # faint mottling
    for _ in range(900):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        a = rng.randint(4, 12)
        d.ellipse([x, y, x + 3, y + 3], fill=(190, 175, 140, a))
    # vignette
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], fill=0)
    vd.ellipse([-120, -120, W + 120, H + 120], fill=60)
    vig = vig.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new("RGB", (W, H), (168, 150, 112))
    img = Image.composite(dark, img, vig.point(lambda v: v // 4))
    return img


def build():
    img = paper_base()
    d = ImageDraw.Draw(img, "RGBA")

    # outer double border + centre fold
    d.rectangle([14, 14, W - 15, H - 15], outline=RULE, width=2)
    d.rectangle([20, 20, W - 21, H - 21], outline=RULE, width=1)
    d.line([(W // 2, 22), (W // 2, H - 22)], fill=(150, 138, 108), width=1)
    d.line([(W // 2 + 2, 22), (W // 2 + 2, H - 22)], fill=(255, 250, 235, 90), width=1)

    # ============================== LEFT PAGE: data page =================
    x0, x1 = 34, W // 2 - 14
    # header
    draw_emblem(d, 78, 66, 56)
    letterspaced(d, (116, 44), "REPUBLIC OF OSTRAVANE",
                 font("serif-bold.ttf", 21), INK, 2)
    text(d, (116, 72), "LÝÐVELDIÐ OSTRAVANE  ·  PASSPORT  ·  VEGABRÉF",
         font("sans.ttf", 11), INK_SOFT)
    rule(d, x0, 100, x1, RULE, 2)
    rule(d, x0, 103, x1, RULE, 1)

    # portrait
    px, py, pw, ph = 44, 118, 186, 248
    portrait = Image.open(ASSETS / "portrait.png").convert("RGB")
    portrait = portrait.resize((pw, ph), Image.LANCZOS)
    img.paste(portrait, (px, py))
    d.rectangle([px, py, px + pw, py + ph], outline=INK, width=2)
    d.rectangle([px + 4, py + 4, px + pw - 4, py + ph - 4], outline=(255, 255, 255, 120), width=1)
    # ghost image / security mark
    d.ellipse([px + pw - 34, py + ph - 34, px + pw - 6, py + ph - 6],
              outline=(255, 255, 255, 160), width=2)
    text(d, (px + pw - 20, py + ph - 27), "OS", font("sans-bold.ttf", 11),
         fill=(255, 255, 255, 200), anchor="mm")
    # signature under portrait
    text(d, (px + pw // 2, py + ph + 12), "Maren Halvorsdatter",
         font("serif-italic.ttf", 21), INK, anchor="ma")
    rule(d, px, py + ph + 38, px + pw, RULE, 1)
    text(d, (px + pw // 2, py + ph + 42), "HOLDER'S SIGNATURE",
         font("sans.ttf", 9), INK_SOFT, anchor="ma")

    # data fields
    fx = 252
    fields = [
        ("SURNAME", "HALVORSDATTER"),
        ("GIVEN NAMES", "MAREN SOLVEIG"),
        ("NATIONALITY", "OSTRAVANESE"),
        ("DATE OF BIRTH", "14 MAR 1988"),
        ("PLACE OF BIRTH", "GULLHAVEN"),
        ("SEX", "F"),
        ("HEIGHT", "172 cm"),
        ("DATE OF ISSUE", "02 JUN 2025"),
        ("DATE OF EXPIRY", "02 JUN 2035"),
        ("AUTHORITY", "GULLHAVEN PASSPORT OFFICE"),
        ("DOCUMENT No.", "OS 4471 902"),
    ]
    y = 116
    for label, value in fields:
        text(d, (fx, y), label, font("sans.ttf", 9), INK_SOFT)
        text(d, (fx, y + 12), value, font("sans-bold.ttf", 15), INK)
        y += 33

    # Observations box fills the lower data page and ties the story together
    ob0, ob1 = y + 6, 606
    d.rectangle([fx, ob0, x1, ob1], outline=RULE, width=1)
    text(d, (fx + 10, ob0 + 8), "OBSERVATIONS", font("sans-bold.ttf", 11), INK)
    text(d, (fx + 10, ob0 + 28), "This passport is also the holder's Seaman's",
         font("sans.ttf", 12), INK)
    text(d, (fx + 10, ob0 + 46), "Book (see endorsement overleaf). Finger-",
         font("sans.ttf", 12), INK)
    text(d, (fx + 10, ob0 + 64), "prints held on file at Gullhaven.",
         font("sans.ttf", 12), INK)
    text(d, (fx + 10, ob0 + 86), "Valid for all countries.",
         font("sans.ttf", 12), INK)

    # MRZ
    mrz1, mrz2 = mrz_lines()
    my = H - 96
    rule(d, x0, my - 12, x1, RULE, 1)
    text(d, (x0, my), mrz1, font("mono.ttf", 15), INK)
    text(d, (x0, my + 20), mrz2, font("mono.ttf", 15), INK)
    text(d, (x0, my + 44), "P<OST  ·  Machine-readable zone — holder is a seafarer; see endorsement overleaf",
         font("sans.ttf", 9), INK_SOFT)

    # ============================== RIGHT PAGE: visas & stamps ============
    x0, x1 = W // 2 + 14, W - 34
    letterspaced(d, (x0, 44), "VISAS AND ENDORSEMENTS",
                 font("serif-bold.ttf", 19), INK, 2)
    text(d, (x0, 70), "VEGABRÉF — STAMPS OF NEIGHBOURING STATES",
         font("sans.ttf", 11), INK_SOFT)
    rule(d, x0, 100, x1, RULE, 2)
    rule(d, x0, 103, x1, RULE, 1)

    # One coherent voyage: issued 02 JUN 2025 in Gullhaven; every stamp
    # after that date, departures and arrivals alternating in order.
    stamps = [
        # (cx, cy, lines, colour, angle)
        (x0 + 112, 158, ["DEPARTURE", "GULLHAVEN — OSTRAVANE", "18 JUN 2025"], BLUE, -4),
        (x0 + 344, 158, ["ARRIVAL", "TÓRSHAVN — FAROE IS.", "19 JUN 2025"], VIOLET, 3),
        (x0 + 112, 252, ["DEPARTURE", "TÓRSHAVN — FAROE IS.", "02 JUL 2025"], BLUE, 3),
        (x0 + 344, 252, ["ARRIVAL", "BERGEN — NORWAY", "04 JUL 2025"], VIOLET, -3),
        (x0 + 112, 346, ["DEPARTURE", "BERGEN — NORWAY", "21 JUL 2025"], BLUE, -2),
        (x0 + 344, 346, ["ARRIVAL", "GULLHAVEN — OSTRAVANE", "22 JUL 2025"], RED, 4),
    ]
    for cx, cy, lines, color, angle in stamps:
        stamp(img, cx, cy, lines, color, angle)

    # Crew visa line under the stamps
    text(d, ((x0 + x1) // 2, 396), "CREW VISA — MV SKERRY LIGHT · TÓRSHAVN–BERGEN · ONE VOYAGE",
         font("sans-bold.ttf", 11), TEAL, anchor="ma")
    rule(d, x0, 420, x1, RULE, 1)

    # Seafarer's endorsement — the telling paperwork detail
    ey0, ey1 = 436, H - 92
    d.rectangle([x0, ey0, x1, ey1], outline=INK, width=2)
    d.rectangle([x0 + 4, ey0 + 4, x1 - 4, ey1 - 4], outline=RULE, width=1)
    text(d, (x0 + 16, ey0 + 12), "SEAFARER'S ENDORSEMENT",
         font("sans-bold.ttf", 15), INK)
    text(d, (x0 + 16, ey0 + 36),
         "Holder is rated Able Seaman. This passport serves as",
         font("sans.ttf", 13), INK)
    text(d, (x0 + 16, ey0 + 56),
         "Seaman's Book No. SB-4471, and is valid for signing on",
         font("sans.ttf", 13), INK)
    text(d, (x0 + 16, ey0 + 76),
         "any Ostravane-registered vessel without further visa.",
         font("sans.ttf", 13), INK)
    text(d, (x0 + 16, ey0 + 100),
         "Gildir sem sjómaður — valid as a seaman.",
         font("serif-italic.ttf", 12), INK_SOFT)
    # Light Dues fee stamp, bottom-right inside the box
    stamp(img, x1 - 110, ey1 - 48, ["LIGHT DUES PAID", "12 KR · GULLHAVEN", "02 JUN 2025"],
          RED, -6, w=170, h=52, fsize=12)
    text(d, (x0 + 16, ey1 - 22),
         "Harbour dues collected at every light.",
         font("sans.ttf", 10), INK_SOFT)

    # footer
    text(d, ((x0 + x1) // 2, H - 78),
         "This passport is the property of the Republic of Ostravane.",
         font("sans.ttf", 9), INK_SOFT, anchor="ma")
    text(d, ((x0 + x1) // 2, H - 62),
         "If found, return to any Ostravane harbour office or consulate.",
         font("sans.ttf", 9), INK_SOFT, anchor="ma")
    return img


def main():
    img = build()
    out = Path(os.environ.get("OUTPUT_PATH", "/output/entry.png"))
    if not out.parent.exists():
        out = Path("entry.png")
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {img.size[0]}x{img.size[1]} {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
