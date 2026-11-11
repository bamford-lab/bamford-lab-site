#!/usr/bin/env python3
"""Build the Bamford Lab logo masters, with the lettering set in real type.

THIS IS THE MASTER LOGO BUILD. It replaced `vectorise-logo.py`, which traced the whole
source raster including the letters; traced letters are a bezier approximation of a
rasterised edge and carry a visible wobble when zoomed.

    python3 brand/build-logo-typeset.py

The shipped logo (`brand/vectorise-logo.py`) traces the whole source raster, letters
included. Traced letters are a bezier approximation of a rasterised edge, so their stems
and diagonals carry a slight wobble that shows when you zoom a long way in. This script
instead:

  * sets "BAMFORD", "LAB" and the tagline in a real typeface, taking the glyph outlines
    straight from the font, so the lettering is geometrically exact at any size;
  * keeps the two ICONS traced, because they are drawn artwork with no typographic
    equivalent: the virus particle (which stands in for the "O" of BAMFORD) and the
    membrane-plus-receptor above "LAB". They separate cleanly because both sit outside
    the letter bodies.

Typeface is Archivo, chosen by rendering candidates at the logo's own cap height and
comparing: it matches the original's width, weight and grotesque character closely,
where Montserrat was too geometric and Libre Franklin too narrow.

Writes the three masters that everything else derives from:
  src/assets/logo-full.svg        crimson + amber, for light backgrounds
  src/assets/logo-full-dark.svg   cream + lifted amber, for dark backgrounds
  src/assets/favicon-virus.svg    the virus alone, for the favicon and the nav mark
plus brand/logo-redesign/typeset-test.png as a visual check.

After running this, regenerate everything downstream:
  python3 brand/build-logo-pack.py
  rsvg-convert ... (favicon PNGs, see the project notes)
  python3 brand/build-slide-backgrounds.py && build-title-slide.py && build-pptx-template.py
"""

import pathlib
import sys

import numpy as np
import potrace
from PIL import Image
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from skimage import filters

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "brand" / "logo-source.png"
OUT = ROOT / "brand" / "logo-redesign"
# Archivo, vendored into the repo so the build is reproducible without a network.
# SIL Open Font License, see brand/fonts/Archivo-OFL.txt. Chosen by rendering candidates
# at the logo's own cap height: it matches the original's width, weight and grotesque
# character, where Montserrat was too geometric and Libre Franklin too narrow.
FONT = ROOT / "brand" / "fonts" / "Archivo.ttf"

CRIMSON, AMBER = "#b41f35", "#e08a3c"
WEIGHT = 700

# Geometry measured off the original artwork, in source pixels.
CAP = 125                 # cap height of BAMFORD / LAB
BASE_1 = 450              # baseline of BAMFORD
BASE_2 = 0                # baseline of LAB, filled in below
X_LEFT = 27               # left edge of the B
WORD_RIGHT = 976          # right edge of the D
VIRUS_CX, VIRUS_CY = 635.5, 382.5
TAG_CAP = 63
TAG_LEFT, TAG_RIGHT = 25, 1381
# The tagline is CENTRED with a modest fixed letterspacing, not stretched to the full
# width of the wordmark. Stretching it forced huge gaps between letters once the
# lettering became real type, because Archivo sets wider than the traced original.
TAG_TRACK_EM = 0.09
UP = 4                    # upsample before tracing the icons
# The virus is wider than the "O" it replaces, so it cannot simply inherit that glyph's
# advance or its spikes crowd the F and the R. Give it its own slot: its true width plus
# breathing room either side. The word then grows, and everything to its right shifts.
VIRUS_PAD = 2
LAB_GAP = 60              # the original gap between the D of BAMFORD and the L of LAB
# The source art has four small arcs under the receptor. They read as cartoon motion lines; the
# generous reading is signal transduction. Set False to drop them.
SHOW_ARCS = False


# ----------------------------------------------------------------- icon tracing
def trace(mask, scale, ox=0.0, oy=0.0):
    """Trace a boolean mask to SVG path data, in source-pixel coordinates."""
    bmp = potrace.Bitmap(np.ascontiguousarray(~mask))       # potracer traces the FALSE region
    path = bmp.trace(turdsize=3, alphamax=1.0, opticurve=True, opttolerance=0.2)
    out = []
    for cur in path.curves:
        p = cur.start_point
        s = f"M{p.x / scale + ox:.2f} {p.y / scale + oy:.2f}"
        for seg in cur.segments:
            e = seg.end_point
            if seg.is_corner:
                c = seg.c
                s += (f"L{c.x / scale + ox:.2f} {c.y / scale + oy:.2f}"
                      f"L{e.x / scale + ox:.2f} {e.y / scale + oy:.2f}")
            else:
                c1, c2 = seg.c1, seg.c2
                s += (f"C{c1.x / scale + ox:.2f} {c1.y / scale + oy:.2f} "
                      f"{c2.x / scale + ox:.2f} {c2.y / scale + oy:.2f} "
                      f"{e.x / scale + ox:.2f} {e.y / scale + oy:.2f}")
        s += "Z"
        out.append(s)
    return "".join(out)


def icon_paths():
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    red = (R - G) > 20
    amber = red & (G > 105) & ((G - B) > 35) & (B < 140)
    crimson = red & ~amber
    H, W = crimson.shape
    yy, xx = np.mgrid[0:H, 0:W]

    regions = {
        "virus": (np.hypot(yy - VIRUS_CY, xx - VIRUS_CX) < 86)
                 & (np.hypot(yy - VIRUS_CY, xx - VIRUS_CX) > 30),
        "receptor": (xx > 1000) & (xx < 1400) & (yy < 336),
    }
    paths = {}
    for name, reg in regions.items():
        m = crimson & reg
        if name == "receptor":
            # Keep only the membrane and the receptor itself. This drops two things:
            # the four small arcs (separate components, area < 500), and the tops of the
            # L, A and B which poke into this region and would otherwise be drawn twice,
            # once as artwork and once as type.
            from skimage import measure as _m
            keep = np.zeros_like(m)
            lab = _m.label(m)
            for prop in _m.regionprops(lab):
                is_arc = prop.area < 500
                is_letter_top = prop.bbox[0] >= 320
                if is_letter_top:
                    continue
                if is_arc and not SHOW_ARCS:
                    continue
                if is_arc and prop.bbox[0] < 320:
                    continue        # tiny speckles high up are JPEG noise
                keep[lab == prop.label] = True
            if SHOW_ARCS:
                for prop in _m.regionprops(lab):
                    if 150 < prop.area < 500 and prop.bbox[0] >= 285:
                        keep[lab == prop.label] = True
            m = keep
        big = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                         .resize((W * UP, H * UP), Image.LANCZOS)) > 127
        big = filters.gaussian(big.astype(float), sigma=2.4) > 0.5
        paths[name] = trace(big, UP)
    # the amber discs are true circles, emitted as <circle> not traced
    return paths


# ------------------------------------------------------------------- typesetting
class Typesetter:
    def __init__(self, path, weight):
        self.font = TTFont(str(path))
        if "fvar" in self.font:
            from fontTools.varLib.mutator import instantiateVariableFont
            axes = {a.axisTag: a.defaultValue for a in self.font["fvar"].axes}
            axes["wght"] = weight
            self.font = instantiateVariableFont(self.font, axes, inplace=False)
        self.gs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upem = self.font["head"].unitsPerEm
        ymax = self.font["glyf"]["H"].yMax if "glyf" in self.font else self.upem * 0.72
        self.cap_units = ymax

    def glyph(self, ch):
        return self.gs[self.cmap[ord(ch)]]

    def advance(self, ch, size):
        return self.glyph(ch).width * size / self.upem

    def size_for_cap(self, cap_px):
        return cap_px * self.upem / self.cap_units

    def path(self, ch, size, x, baseline):
        """SVG path data for one glyph, scaled and placed. SVG y grows downward."""
        pen = SVGPathPen(self.gs)
        self.glyph(ch).draw(pen)
        d = pen.getCommands()
        if not d:
            return ""
        k = size / self.upem
        return (f'<g transform="translate({x:.2f},{baseline:.2f}) scale({k:.5f},{-k:.5f})">'
                f'<path d="{d}"/></g>')

    def run(self, text, size, x, baseline, tracking=0.0, skip=None):
        """Lay out a string; returns (svg, positions) with positions per character."""
        out, pos = [], []
        for ch in text:
            pos.append((ch, x, self.advance(ch, size)))
            if ch != " " and ch != skip:
                out.append(self.path(ch, size, x, baseline))
            x += self.advance(ch, size) + tracking
        return "".join(out), pos, x - tracking

    def width(self, text, size, tracking=0.0):
        return sum(self.advance(c, size) for c in text) + tracking * (len(text) - 1)


def fit_tracking(ts, text, size, target):
    """Letter-spacing that makes `text` span exactly `target` pixels."""
    natural = ts.width(text, size, 0.0)
    return (target - natural) / max(len(text) - 1, 1)


def main():
    if not FONT.exists():
        print(f"Archivo not found at {FONT}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    icons = icon_paths()
    ts = Typesetter(FONT, WEIGHT)

    size = ts.size_for_cap(CAP)

    # Lay BAMFORD out by hand so the virus gets a slot of its own.
    virus_w = 721 - 550                       # measured spike-to-spike width
    slot = virus_w + 2 * VIRUS_PAD
    track = fit_tracking(ts, "BAMFORD", size, WORD_RIGHT - X_LEFT)
    parts, x = [], X_LEFT
    virus_slot_cx = None
    for ch in "BAMFORD":
        if ch == "O":
            virus_slot_cx = x + slot / 2
            x += slot + track
            continue
        parts.append(ts.path(ch, size, x, BASE_1))
        x += ts.advance(ch, size) + track
    word = "".join(parts)
    word_right = x - track
    shift = word_right - WORD_RIGHT           # how much the word grew
    vdx = virus_slot_cx - VIRUS_CX            # move the virus art to its slot centre

    # LAB at its natural spacing, simply placed LAB_GAP after the D. Forcing it to a
    # fixed width needed negative tracking, which ran the L's foot into the A's leg.
    lab_x = word_right + LAB_GAP
    lab, _, lab_right = ts.run("LAB", size, lab_x, BASE_1, 0.0)
    shift = lab_right - 1378                  # how much wider the whole lockup now is

    # the rule spans the full lockup; the tagline is centred under it
    tag_right = lab_right
    tsize = ts.size_for_cap(TAG_CAP)
    tag_track = tsize * TAG_TRACK_EM
    tag_w = ts.width("ANTIVIRAL IMMUNITY", tsize, tag_track)
    tag_x = TAG_LEFT + ((tag_right - TAG_LEFT) - tag_w) / 2      # centred under the rule
    tag, _, _ = ts.run("ANTIVIRAL IMMUNITY", tsize, tag_x, 602, tag_track)

    def document(crimson, amber, body, vb):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
                f'role="img" aria-label="Bamford Lab, Antiviral Immunity">'
                f'<g fill="{crimson}">{body}</g>'
                f'{amber}</svg>')

    word_body = (f'{word}{lab}{tag}'
                 f'<rect x="{TAG_LEFT}" y="500" width="{tag_right - TAG_LEFT:.0f}" height="7" rx="3"/>'
                 f'<g transform="translate({vdx:.2f},0)">'
                 f'<path fill-rule="evenodd" d="{icons["virus"]}"/></g>'
                 f'<g transform="translate({shift:.2f},0)">'
                 f'<path fill-rule="evenodd" d="{icons["receptor"]}"/></g>')

    def discs(col):
        return (f'<circle fill="{col}" cx="{VIRUS_CX + vdx:.2f}" cy="{VIRUS_CY}" r="22"/>'
                f'<circle fill="{col}" cx="{1192.5 + shift:.2f}" cy="181.5" r="22"/>')

    # Measure the real content bounds by rendering once, so the viewBox is tight and the
    # logo carries no dead space (which would misalign it in the nav, footer and slides).
    import subprocess, tempfile
    probe = document(CRIMSON, discs(AMBER), word_body, f"0 0 {int(1408 + shift)} 768")
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as fh:
        fh.write(probe); probe_path = fh.name
    png = probe_path + ".png"
    PW = 2000
    subprocess.run(["rsvg-convert", "-w", str(PW), probe_path, "-o", png], check=True)
    arr = np.asarray(Image.open(png).convert("RGBA"))
    ys, xs = np.where(arr[..., 3] > 30)
    k = (1408 + shift) / PW
    pad = 10
    x0, y0 = xs.min() * k - pad, ys.min() * k - pad
    x1, y1 = xs.max() * k + pad, ys.max() * k + pad
    vb_full = f"{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}"

    (ROOT / "src/assets/logo-full.svg").write_text(
        document(CRIMSON, discs(AMBER), word_body, vb_full))

    # --- wordmark only: no tagline, no rule. For small places like the site nav, where
    # the tagline would render a few pixels tall and be illegible anyway. ---
    mark_body = (f'{word}{lab}'
                 f'<g transform="translate({vdx:.2f},0)">'
                 f'<path fill-rule="evenodd" d="{icons["virus"]}"/></g>'
                 f'<g transform="translate({shift:.2f},0)">'
                 f'<path fill-rule="evenodd" d="{icons["receptor"]}"/></g>')
    probe_m = document(CRIMSON, discs(AMBER), mark_body, f"0 0 {int(1408 + shift)} 768")
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as fh:
        fh.write(probe_m); mp = fh.name
    subprocess.run(["rsvg-convert", "-w", str(PW), mp, "-o", mp + ".png"], check=True)
    ma = np.asarray(Image.open(mp + ".png").convert("RGBA"))
    mys, mxs = np.where(ma[..., 3] > 30)
    mx0, my0 = mxs.min() * k - pad, mys.min() * k - pad
    mx1, my1 = mxs.max() * k + pad, mys.max() * k + pad
    vb_mark_only = f"{mx0:.1f} {my0:.1f} {mx1 - mx0:.1f} {my1 - my0:.1f}"
    (ROOT / "src/assets/logo-wordmark.svg").write_text(
        document(CRIMSON, discs(AMBER), mark_body, vb_mark_only))
    (ROOT / "src/assets/logo-wordmark-dark.svg").write_text(
        document("#f4ecec", discs("#e9a24a"), mark_body, vb_mark_only))

    # --- nav pair: the wordmark WITHOUT the virus, and the virus ALONE, sharing one
    # viewBox so they stack perfectly as two <img>s. Split so the virus can spin on
    # hover without the SVG being inlined (it is ~96KB, too big for every page).
    # Brand crimson, matching the rest of the site (11 Nov 2026). This was previously
    # the deeper #8f1728 for contrast (8.6:1 against the nav band, against 6.3:1), but
    # James found it read as noticeably darker than every other red on the page. 6.3:1
    # still clears WCAG AA comfortably for lettering this size.
    NAV_RED = "#b41f35"
    novirus_body = (f'{word}{lab}'
                    f'<g transform="translate({shift:.2f},0)">'
                    f'<path fill-rule="evenodd" d="{icons["receptor"]}"/></g>')
    novirus_discs = f'<circle fill="{AMBER}" cx="{1192.5 + shift:.2f}" cy="181.5" r="22"/>'
    (ROOT / "src/assets/logo-wordmark-nav.svg").write_text(
        document(NAV_RED, novirus_discs, novirus_body, vb_mark_only))

    virus_only = (f'<g transform="translate({vdx:.2f},0)">'
                  f'<path fill-rule="evenodd" d="{icons["virus"]}"/></g>')
    (ROOT / "src/assets/logo-wordmark-nav-virus.svg").write_text(
        document(NAV_RED,
                 f'<circle fill="{AMBER}" cx="{VIRUS_CX + vdx:.2f}" cy="{VIRUS_CY}" r="22"/>',
                 virus_only, vb_mark_only))

    _x0, _y0, _w, _h = (float(v) for v in vb_mark_only.split())
    print(f"  nav virus centre: {100*(VIRUS_CX + vdx - _x0)/_w:.2f}% across, "
          f"{100*(VIRUS_CY - _y0)/_h:.2f}% down  <- CSS transform-origin")
    (ROOT / "src/assets/logo-full-dark.svg").write_text(
        document("#f4ecec", discs("#e9a24a"), word_body, vb_full))

    # --- favicon: the virus alone, square and centred ---
    vcx = VIRUS_CX + vdx
    vbody = f'<g transform="translate({vdx:.2f},0)"><path fill-rule="evenodd" d="{icons["virus"]}"/></g>'
    half = 92
    vb_mark = f"{vcx - half:.1f} {VIRUS_CY - half:.1f} {half * 2} {half * 2}"
    (ROOT / "src/assets/favicon-virus.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_mark}" '
        f'role="img" aria-label="Bamford Lab">'
        f'<g fill="{CRIMSON}">{vbody}</g>'
        f'<circle fill="{AMBER}" cx="{vcx:.2f}" cy="{VIRUS_CY}" r="22"/></svg>')

    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsvg-convert", "-w", "2816", str(ROOT / "src/assets/logo-full.svg"),
                    "-o", str(OUT / "typeset-test.png")], check=True)
    print("wrote logo-full.svg, logo-full-dark.svg, favicon-virus.svg")
    print(f"  virus slot {slot:.0f}px (art {virus_w}px + {VIRUS_PAD}px each side)")
    print(f"  tagline {tag_w:.0f}px wide, centred under a {tag_right - TAG_LEFT:.0f}px rule")
    print(f"  viewBox {vb_full}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
