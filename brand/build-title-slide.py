#!/usr/bin/env python3
"""Build a finished 16:9 title slide for a Bamford Lab talk, as SVG and PNG.

    python3 brand/build-title-slide.py                      # James's default EVOLVE-AI slide
    python3 brand/build-title-slide.py --title "My talk title" --name "Someone Else"
    python3 brand/build-title-slide.py --no-nilab           # generic, no funder marks
    python3 brand/build-title-slide.py --plain              # no constellation texture

The SVG keeps the title, name and footer as **real, editable text**, so for a one-off talk
you can open it in Inkscape, Illustrator or even a text editor and change the wording
without regenerating anything. The logo strip is embedded as a high-resolution image,
composited from the best available source for each mark (see build-slide-backgrounds.py).

Why the title is split into explicit lines: SVG has no automatic text wrapping, so each
line is its own <tspan>. The script wraps for you by measuring the real font. If you edit
the title by hand afterwards, mind the line breaks yourself.
"""

import argparse
import base64
import io
import pathlib
import sys

from PIL import Image, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from importlib import import_module

bg = import_module("build-slide-backgrounds".replace("-", "_")) if False else None
# the backgrounds module has a hyphenated name, so load it by path
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "slidebg", pathlib.Path(__file__).resolve().parent / "build-slide-backgrounds.py")
SB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SB)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "brand" / "slide-backgrounds"

W, H = 3840, 2160
MARGIN = 300
AMBER = "#e9a24a"
LATO = "/usr/share/fonts/truetype/lato/Lato-%s.ttf"
# The slides use the same faces as the website: Newsreader for headings, IBM Plex Sans
# for supporting text. Installed under ~/.local/share/fonts/bamford/.
FONT_DIR = pathlib.Path.home() / ".local/share/fonts/bamford"
SERIF = FONT_DIR / "Newsreader.ttf"
SANS = FONT_DIR / "IBMPlexSans.ttf"
SERIF_STACK = "Newsreader, Georgia, 'Times New Roman', serif"
SANS_STACK = "'IBM Plex Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"

DEFAULTS = dict(
    title=("EVOLVE-AI: evolutionary-informed deep learning for deciphering and modifying "
           "cell-cell communication during infection, inflammation and cancer"),
    name="James McCabe",
    supervisors="Supervisory team: Connor Bamford, Barry Devereux, Kyle Matchett",
    affiliation=("Queen's University Belfast  |  Northern Ireland Landscape Partnership "
                 "in AI for Bioscience (NILAB)"),
)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


FACES = {
    # key: (measuring font path, SVG font stack, title weight)
    "lato":  (LATO % "Bold", "Lato, 'Helvetica Neue', Helvetica, Arial, sans-serif", 700),
    "plex":  (str(SANS), SANS_STACK, 600),
    "serif": (str(SERIF), SERIF_STACK, 600),
}


def cap_height(face, size):
    """Actual cap height for a face at a given size. font-size includes ascender and
    descender room, so using it as the baseline offset overshoots by a third."""
    path, _stack, weight = FACES[face]
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([weight, 72] if face == "serif" else [100, weight])
    except Exception:
        pass
    b = f.getbbox("H")
    return b[3] - b[1]


def descender(face, size, text):
    """How far the text's ink falls BELOW its baseline. Needed because a title ending
    in a descender ('evolutionarily blind') reaches lower than one that does not, so
    measuring the gap to the rule from the baseline makes it uneven."""
    path, _stack, weight = FACES[face]
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([weight, 72] if face == "serif" else [100, weight])
    except Exception:
        pass
    return max(0, f.getbbox(text, anchor="ls")[3])


def wrap(text, face, size, max_width):
    """Greedy wrap, measured with the real font so the SVG lines actually fit."""
    path, _stack, weight = FACES[face]
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([weight, 72] if face == "serif" else [100, weight])
    except Exception:
        pass
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def logo_strip(nilab=True, height=150):
    """The TOP logo block: two centred rows, stacked.

        1. the lab's own mark
        2. Queen's, IGFS and the School of Biological Sciences

    NILAB is NOT here: it is placed on its own beneath the text, so the funder sits at
    the foot of the slide rather than in the institutional block.
    """
    bam = SB.fit(SB.svg(ROOT / "brand/logo-pack/bamford-lab-logo-white.svg", 1800),
                 int(height * 1.30))
    sobs = SB.fit(SB.sobs_wordmark(), int(height * 0.66))

    # Row 2 holds THREE marks separated by TWO dividers, but one of those dividers lives
    # inside the QUB+IGFS lockup. Both must be given the same breathing room or the row
    # reads as unevenly spaced, so the gap is set once here and passed down.
    gap = int(height * 0.34)
    qi = SB.qub_igfs(int(height * 0.80), gap=gap)
    div = SB.rule(int(height * 0.80), 3, 130)
    r2_w = qi.width + gap + 3 + gap + sobs.width
    r2_h = max(qi.height, sobs.height, div.height)
    row2 = Image.new("RGBA", (r2_w, r2_h), (0, 0, 0, 0))
    x = 0
    for part in (qi, div, sobs):
        row2.alpha_composite(part, (x, (r2_h - part.height) // 2))
        x += part.width + (gap if part is not div else gap)
    row2 = row2.crop(row2.getbbox())

    rows = [bam, row2]
    v_gap = int(height * 0.40)
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows) + v_gap * (len(rows) - 1)
    block = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    y = 0
    for r in rows:
        block.alpha_composite(r, ((W - r.width) // 2, y))
        y += r.height + v_gap
    return block.crop(block.getbbox())


def data_uri(im):
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def build_svg(title, name, supervisors, affiliation, nilab=True, constellation=True,
              face="lato"):
    strip = logo_strip(nilab)
    # The top logo block is a two-row stack, sized by width. Keep this modest: a stack
    # scaled like the old single row (2900) grows tall enough to push the title off.
    strip_w = 1520
    strip_h = int(strip.height * strip_w / strip.width)
    strip_uri = data_uri(strip)

    nilab_img = SB.nilab_emblem(430) if nilab else None
    nilab_uri = data_uri(nilab_img) if nilab_img is not None else None

    texture = ""
    if constellation:
        tex = SB.constellation(W, H)
        texture = (f'<image x="0" y="0" width="{W}" height="{H}" '
                   f'xlink:href="{data_uri(tex)}" />')

    # Shrink the title a step at a time until it fits four lines, so a long title
    # stays readable and a short one does not look lost.
    title_stack = FACES[face][1]
    title_weight = FACES[face][2]
    for t_size in (124, 116, 108, 100, 92):
        t_lead = int(t_size * 1.28)
        tlines = wrap(title, face, t_size, W - MARGIN * 2 - 200)
        if len(tlines) <= 4:
            break

    # Lay the whole slide out relative to the top of the logo strip, then shift the
    # lot so it sits VERTICALLY CENTRED. Anchoring to the top and bottom edges instead
    # leaves a dead band between the logos and the title whenever the title is short.
    RULE_H = 6
    # The three parts are positioned INDEPENDENTLY, not centred as one block:
    #   * the TEXT is centred on the true middle of the slide, because it is the thing
    #     the eye should land on first;
    #   * the LOGO block is anchored near the top edge, so it reads second;
    #   * the NILAB roundel is anchored near the bottom edge, well clear of the text.
    LOGO_TOP = 108            # distance from the slide top to the logo block
    NILAB_BOTTOM = 133        # distance from the slide bottom to the roundel
    # True centring left only 50px between the logo strip and the title, so the top of
    # the slide read as one condensed block. The text is pushed below the centre and the
    # roundel moves down with it by the same amount, which keeps their spacing intact.
    TEXT_DROP = 72
    MIN_LOGO_GAP = 90         # the title may never crowd the strip, however long it runs
    NILAB_CLEAR = 31          # breathing room between the affiliation line and the roundel
    NILAB_MIN_BOTTOM = 90     # the roundel may never run off the bottom edge

    t_cap = cap_height(face, t_size)
    RULE_GAP = 72
    NAME_SIZE = 92

    # lay the text out relative to its own top, then centre that on the slide
    t_first_r = t_cap
    t_last_r = t_first_r + (len(tlines) - 1) * t_lead
    rule_y_r = t_last_r + descender(face, t_size, tlines[-1]) + RULE_GAP
    name_y_r = rule_y_r + RULE_H + RULE_GAP + cap_height(face, NAME_SIZE)
    sup_y_r = name_y_r + 100
    aff_y_r = sup_y_r + 84
    text_h = aff_y_r + descender(face, 48, affiliation)

    logo_y = LOGO_TOP
    text_top = max((H - text_h) // 2 + TEXT_DROP, logo_y + strip_h + MIN_LOGO_GAP)
    t_first = text_top + t_first_r
    rule_y = text_top + rule_y_r
    name_y = text_top + name_y_r
    sup_y = text_top + sup_y_r
    aff_y = text_top + aff_y_r

    nilab_h = nilab_img.height if nilab_img is not None else 0
    nilab_y = H - NILAB_BOTTOM - nilab_h
    if nilab_img is not None:
        # A title long enough to be clamped off the logo strip pushes the text into the
        # roundel's space. Let the roundel give way, shrinking only if it would otherwise
        # fall off the bottom edge, so an overlong title degrades rather than breaks.
        if nilab_y < text_top + text_h + NILAB_CLEAR:
            nilab_y = text_top + text_h + NILAB_CLEAR
            overflow = (nilab_y + nilab_h) - (H - NILAB_MIN_BOTTOM)
            if overflow > 0:
                nilab_img = SB.nilab_emblem(nilab_h - overflow)
                nilab_uri = data_uri(nilab_img)
                nilab_h = nilab_img.height

    # The rule spans the full text measure, so it is evenly inset on both sides.
    rule_w = W - MARGIN * 2

    # Everything is centred on the slide axis to match the logo strip above it.
    CX = W // 2
    title_tspans = "".join(
        f'<tspan x="{CX}" y="{t_first + i * t_lead}">{esc(l)}</tspan>'
        for i, l in enumerate(tlines))

    nilab_tag = ""
    if nilab_img is not None:
        nw, nh = nilab_img.width, nilab_img.height
        nilab_tag = (f'<image x="{(W - nw) // 2}" y="{nilab_y}" width="{nw}" height="{nh}" '
                     f'xlink:href="{nilab_uri}" />')

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="#ba2a40"/>
      <stop offset="55%"  stop-color="#a6192e"/>
      <stop offset="100%" stop-color="#760e21"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.72" cy="0.16" r="0.68">
      <stop offset="0%"   stop-color="#cd384e" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#cd384e" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>
  {texture}

  <!-- Logos. Embedded as high-resolution images; edit the text below, not these. -->
  <image x="{(W - strip_w) // 2}" y="{logo_y}" width="{strip_w}" height="{strip_h}"
         xlink:href="{strip_uri}" />
  {nilab_tag}

  <!-- ===== EDIT FROM HERE ===== -->
  <g fill="#ffffff">
    <text font-family="{title_stack}" font-size="{t_size}" font-weight="{title_weight}"
          letter-spacing="-1" text-anchor="middle">{title_tspans}</text>

    <rect x="{MARGIN}" y="{rule_y}" width="{rule_w}" height="{RULE_H}" fill="{AMBER}"/>

    <text x="{CX}" y="{name_y}" font-family="{title_stack}" text-anchor="middle"
          font-size="92" font-weight="{title_weight}">{esc(name)}</text>
    <text x="{CX}" y="{sup_y}" font-family="{title_stack}" font-size="52" text-anchor="middle"
          font-weight="400" fill="#ffffff" fill-opacity="0.84">{esc(supervisors)}</text>
    <text x="{CX}" y="{aff_y}" font-family="{title_stack}" font-size="48" text-anchor="middle"
          font-weight="400" fill="#ffffff" fill-opacity="0.70">{esc(affiliation)}</text>
  </g>
</svg>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default=DEFAULTS["title"])
    ap.add_argument("--name", default=DEFAULTS["name"])
    ap.add_argument("--supervisors", default=DEFAULTS["supervisors"])
    ap.add_argument("--affiliation", default=DEFAULTS["affiliation"])
    ap.add_argument("--no-nilab", action="store_true")
    ap.add_argument("--plain", action="store_true", help="no constellation texture")
    ap.add_argument("--font", default="lato", choices=["lato", "plex", "serif"],
                    help="lato (default), plex (IBM Plex Sans), serif (Newsreader)")
    ap.add_argument("--out", default="title-slide")
    a = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    svg = build_svg(a.title, a.name, a.supervisors, a.affiliation,
                    nilab=not a.no_nilab, constellation=not a.plain, face=a.font)
    svg_path = OUT / f"{a.out}.svg"
    svg_path.write_text(svg)

    import subprocess
    png_path = OUT / f"{a.out}.png"
    subprocess.run(["rsvg-convert", "-w", str(W), str(svg_path), "-o", str(png_path)], check=True)
    # rsvg-convert writes no DPI, so stamp 288 on afterwards: at that density the image is
    # exactly 13.333 x 7.5in, i.e. a 16:9 slide, so PowerPoint inserts it at full size.
    stamped = Image.open(png_path)
    stamped.save(png_path, dpi=(288, 288))
    print(f"Wrote {svg_path.name} (editable text) and {png_path.name} ({W}x{H})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
