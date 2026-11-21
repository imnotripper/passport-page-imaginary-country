#!/usr/bin/env python3
"""Build the passport spread image for the Republic of Velmora.

Draws an open two-page passport spread (data page + visas page) at
1024x640 with PIL, compositing a generated ID portrait. All dates,
stamps and the MRZ are internally consistent:

  holder      MARA ILEANA SELVANE, born 12 MAR 1994, Port Alver
  passport    VM 0418827, issued 14 JUN 2021, expires 14 JUN 2031
  stamps      Dravostan Sep 2022, Kessar May 2023, Tarn Isles Nov 2024
              (all after the 2021 issue date, in chronological order)
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.abspath(__file__))
PORTRAIT = "/tmp/portrait.png"
OUT = os.path.join(REPO, "entry.png")

W, H = 1024, 640
INK = (38, 38, 42)
GREY = (110, 108, 100)
PAPER = (246, 240, 222)
PAPER2 = (243, 236, 214)

FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF_B = font(f"{FD}/DejaVuSerif-Bold.ttf", 26)
SERIF = font(f"{FD}/DejaVuSerif.ttf", 15)
SANS = font(f"{FL}/LiberationSans-Regular.ttf", 14)
SANS_B = font(f"{FL}/LiberationSans-Bold.ttf", 15)
SANS_S = font(f"{FL}/LiberationSans-Regular.ttf", 11)
SANS_XS = font(f"{FL}/LiberationSans-Regular.ttf", 9)
MONO = font(f"{FD}/DejaVuSansMono.ttf", 15)
MONO_B = font(f"{FD}/DejaVuSansMono-Bold.ttf", 13)
STAMP_B = font(f"{FL}/LiberationSans-Bold.ttf", 17)
STAMP = font(f"{FL}/LiberationSans-Regular.ttf", 12)
STAMP_S = font(f"{FL}/LiberationSans-Regular.ttf", 10)


# ---------------------------------------------------------------- MRZ
def mrz_check(s):
    weights = (7, 3, 1)
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[c] = 10 + i
    vals["<"] = 0
    return str(sum(vals[ch] * weights[i % 3] for i, ch in enumerate(s)) % 10)


def mrz_lines():
    name = "SELVANE<<MARA<ILEANA"
    line1 = ("P<VEL" + name).ljust(44, "<")
    doc = "VM0418827"
    dob = "940312"
    exp = "310614"
    pers = "<" * 14
    line2 = (
        doc + mrz_check(doc)
        + "VEL"
        + dob + mrz_check(dob)
        + "F"
        + exp + mrz_check(exp)
        + pers + mrz_check(pers)
    )
    assert len(line2) == 43
    composite = doc + mrz_check(doc) + dob + mrz_check(dob) + exp + mrz_check(exp) + pers + mrz_check(pers)
    line2 = line2 + mrz_check(composite)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- helpers
def center(draw, cx, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def stamp_layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def paste_stamp(base, layer, angle, xy):
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(rot, xy)


def draw_stamp(base, box, angle, color, lines, title_size=17):
    """lines: list of (text, font, bold?) drawn centred in a rounded rect."""
    x, y, w, h = box
    layer = stamp_layer((w + 40, h + 40))
    d = ImageDraw.Draw(layer)
    a = 200  # ink alpha
    col = color + (a,)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=8,
                        outline=col, width=3)
    d.rounded_rectangle([26, 26, 14 + w, 14 + h], radius=5,
                        outline=col, width=1)
    cy = 20
    for text, fnt in lines:
        tw = d.textlength(text, font=fnt)
        d.text((20 + (w - tw) / 2, cy + 4), text, font=fnt, fill=col)
        cy += fnt.size + 5
    paste_stamp(base, layer, angle, (x - 20, y - 20))


# ---------------------------------------------------------------- build
def build():
    random.seed(42)
    img = Image.new("RGB", (W, H), (52, 48, 44))
    # table shading
    d = ImageDraw.Draw(img)
    for i in range(H):
        shade = 52 + int(6 * math.sin(i / 90.0))
        d.line([(0, i), (W, i)], fill=(shade, shade - 3, shade - 6))

    # pages
    pages = []
    for px in (16, 512):
        page = Image.new("RGB", (484, 608), PAPER)
        pd = ImageDraw.Draw(page)
        # faint paper noise
        for _ in range(900):
            x, y = random.randint(0, 483), random.randint(0, 607)
            v = random.randint(228, 250)
            pd.point((x, y), fill=(v, v - 4, v - 14))
        # soft shadow edge
        pd.rectangle([0, 0, 483, 607], outline=(190, 180, 158), width=1)
        pages.append(page)
    img.paste(pages[0], (16, 16))
    img.paste(pages[1], (512, 16))
    # gutter shadow
    gd = ImageDraw.Draw(img, "RGBA")
    gd.rectangle([500, 16, 512, 624], fill=(0, 0, 0, 60))
    gd.rectangle([512, 16, 524, 624], fill=(0, 0, 0, 40))

    left = ImageDraw.Draw(img)
    right = ImageDraw.Draw(img)
    LX, RX = 16, 512  # page origins

    # ================================================= LEFT PAGE: data page
    # watermark
    wm = Image.new("RGBA", (484, 608), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.text((40, 300), "VELMORA", font=font(f"{FD}/DejaVuSerif-Bold.ttf", 54),
            fill=(120, 100, 60, 12))
    img.paste(wm.rotate(-24, resample=Image.BICUBIC, center=(242, 304)),
              (LX, 16), wm.rotate(-24, resample=Image.BICUBIC, center=(242, 304)))

    # emblem: circle, waves, star
    cx, cy = LX + 242, 16 + 52
    left.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=(122, 96, 32), width=2)
    left.ellipse([cx - 19, cy - 19, cx + 19, cy + 19], outline=(122, 96, 32), width=1)
    for k, yy in enumerate((cy - 2, cy + 5, cy + 12)):
        pts = [(cx - 15 + t, yy + 2.5 * math.sin(t / 4.0)) for t in range(31)]
        left.line(pts, fill=(122, 96, 32), width=2)
    # star (5-point, alternating outer/inner radius)
    sx, sy = cx, cy - 13
    star = []
    for i in range(10):
        rr = 5 if i % 2 == 0 else 2.2
        ang = math.radians(-90 + 36 * i)
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    left.polygon(star, fill=(122, 96, 32))

    center(left, LX + 242, 16 + 84, "REPUBLIC OF VELMORA", SERIF_B)
    center(left, LX + 242, 16 + 116, "REPUBLIKA VELMORA  ·  PASSPORT",
           font(f"{FL}/LiberationSans-Regular.ttf", 12), fill=GREY)
    left.line([LX + 28, 16 + 142, LX + 456, 16 + 142], fill=(122, 96, 32), width=2)
    left.line([LX + 28, 16 + 146, LX + 456, 16 + 146], fill=(122, 96, 32), width=1)

    # ---- portrait
    por = Image.open(PORTRAIT).convert("RGB")
    # crop to 3:4 head-and-shoulders
    pw, ph = por.size
    por = por.crop((int(pw * 0.18), int(ph * 0.06), int(pw * 0.82), int(ph * 0.86)))
    por = por.resize((152, 203), Image.LANCZOS)
    img.paste(por, (LX + 304, 16 + 168))
    left.rectangle([LX + 304, 16 + 168, LX + 456, 16 + 371],
                   outline=(90, 84, 70), width=2)

    # ---- data fields (label / value pairs)
    fields = [
        ("SURNAME / PREZIME", "SELVANE"),
        ("GIVEN NAMES / IMENA", "MARA ILEANA"),
        ("NATIONALITY / DRŽAVLJANSTVO", "VELMORAN"),
        ("DATE OF BIRTH / ROĐENA", "12 MAR 1994"),
        ("PLACE OF BIRTH / MJESTO ROĐENJA", "PORT ALVER"),
        ("SEX / SPOL", "F"),
        ("DATE OF ISSUE / IZDANO", "14 JUN 2021"),
        ("DATE OF EXPIRY / VRIJEDI DO", "14 JUN 2031"),
        ("AUTHORITY / TIJELO", "MINISTRY OF THE INTERIOR"),
        ("PASSPORT No. / BROJ", "VM 0418827"),
    ]
    y = 16 + 168
    for label, value in fields:
        left.text((LX + 28, y), label, font=SANS_XS, fill=GREY)
        left.text((LX + 28, y + 11), value, font=SANS_B, fill=INK)
        y += 30
    # signature (under the portrait, clear of the data fields)
    left.line([LX + 304, 16 + 396, LX + 456, 16 + 396], fill=INK, width=1)
    left.text((LX + 304, 16 + 400), "HOLDER'S SIGNATURE / POTPIS",
              font=SANS_XS, fill=GREY)
    sig = ImageFont.truetype(f"{FD}/DejaVuSerif.ttf", 19)
    left.text((LX + 312, 16 + 374), "Mara Selvane", font=sig, fill=(40, 40, 90))

    # ---- MRZ
    l1, l2 = mrz_lines()
    left.rectangle([LX + 28, 16 + 508, LX + 456, 16 + 556], fill=(238, 231, 210))
    left.text((LX + 30, 16 + 514), l1, font=MONO, fill=INK)
    left.text((LX + 30, 16 + 534), l2, font=MONO, fill=INK)

    # ================================================= RIGHT PAGE: visas
    center(right, RX + 242, 16 + 30, "VISAS", SERIF_B)
    center(right, RX + 242, 16 + 62, "VIZE  ·  PAGE 3", SANS_S, fill=GREY)
    right.line([RX + 28, 16 + 84, RX + 456, 16 + 84], fill=(122, 96, 32), width=2)

    base = img.convert("RGBA")

    # one complete entry+exit pair per neighbour, in chronological order
    st_b = font(f"{FL}/LiberationSans-Bold.ttf", 14)
    st_d = font(f"{FL}/LiberationSans-Bold.ttf", 13)
    st_m = font(f"{FL}/LiberationSans-Regular.ttf", 10)
    st_s = font(f"{FL}/LiberationSans-Regular.ttf", 9)
    rows = [
        (16 + 108, (31, 58, 138), "DRAVOSTAN", "03 SEP 2022", "11 SEP 2022",
         "KOROVGRAD", "1187", "1204"),
        (16 + 196, (91, 42, 134), "KESSAR", "22 MAY 2023", "30 MAY 2023",
         "VELKA GATE", "0441", "0458"),
        (16 + 284, (16, 96, 84), "ISLES OF TARN", "08 NOV 2024", "15 NOV 2024",
         "TARN QUAY · FERRY", "0923", "0936"),
    ]
    for y, color, country, d_in, d_out, post, n_in, n_out in rows:
        draw_stamp(base, (RX + 40, y, 200, 78), -5, color, [
            (country, st_b),
            ("— ENTRY —", st_m),
            (d_in, st_d),
            (f"{post} · No. {n_in}", st_s),
        ])
        draw_stamp(base, (RX + 244, y, 200, 78), 4, color, [
            (country, st_b),
            ("— EXIT —", st_m),
            (d_out, st_d),
            (f"{post} · No. {n_out}", st_s),
        ])

    # visa-condition stamp: the telling paperwork detail
    draw_stamp(base, (RX + 40, 16 + 388, 404, 80), -2, (168, 32, 32), [
        ("ENTRY VALID FOR COASTAL DISTRICTS ONLY", STAMP_B),
        ("TRAVEL TO THE INTERIOR REQUIRES", STAMP),
        ("A MINISTRY PERMIT  ·  PORT ALVER", STAMP),
    ])
    # ferry tax fee stamp
    draw_stamp(base, (RX + 120, 16 + 492, 244, 52), 3, (168, 32, 32), [
        ("FERRY TAX  12 VEL  ·  PAID", STAMP_B),
        ("08 NOV 2024", STAMP),
    ])
    # small note under stamps (drawn on the composited layer)
    bd = ImageDraw.Draw(base)
    bd.text((RX + 40, 16 + 566),
            "Three journeys, all by land and ferry; no air entries recorded.",
            font=SANS_S, fill=GREY + (255,))

    out = base.convert("RGB")
    out.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, out.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
