#!/usr/bin/env python3
"""Build the reusable Bamford Lab logo pack from the two master SVGs.

Run from the repository root:   python3 brand/build-logo-pack.py

Reads  src/assets/logo-full.svg  and  src/assets/favicon-virus.svg,
writes recoloured SVGs plus rendered PNGs into brand/logo-pack/.

Each master is a clean two-path SVG (one crimson path, one amber path), so
recolouring is a plain string substitution. Solid-background versions get a
background rect plus even padding, otherwise the artwork sits tight against
the edge and looks cramped on a slide.

Requires rsvg-convert (librsvg) for the PNGs, and Pillow for the preview sheet.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "assets"
OUT = ROOT / "brand" / "logo-pack"

# Master colours, as they appear in the source SVGs
CRIMSON, AMBER = "#b41f35", "#e08a3c"
# Palette
MAROON, PLUM, WHITE, CREAM, AMBER_LIGHT, INK = (
    "#8f1728", "#180a0e", "#ffffff", "#f4ecec", "#e9a24a", "#1c1114",
)


def recolour(svg: str, crimson_to: str, amber_to: str) -> str:
    return svg.replace(CRIMSON, crimson_to).replace(AMBER, amber_to)


def with_background(svg: str, colour: str, pad_frac: float = 0.10) -> str:
    """Add a full-bleed background and even padding.

    The viewBox is NOT assumed to start at 0 0: the masters are emitted with a tight
    viewBox around the artwork, so minx/miny are non-zero.
    """
    m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg)
    x0, y0, w, h = (float(m.group(i)) for i in (1, 2, 3, 4))
    pad = h * pad_frac
    body = svg[svg.index(">", svg.index("<svg")) + 1: svg.rindex("</svg>")]
    vb = f"{x0 - pad:.1f} {y0 - pad:.1f} {w + 2 * pad:.1f} {h + 2 * pad:.1f}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" '
        f'aria-label="Bamford Lab, Antiviral Immunity">'
        f'<rect x="{x0 - pad:.1f}" y="{y0 - pad:.1f}" width="{w + 2 * pad:.1f}" '
        f'height="{h + 2 * pad:.1f}" fill="{colour}"/>{body}</svg>'
    )


def build_preview():
    """Contact sheet of every variant, on a chequerboard so transparency is visible.
    Built here rather than by hand so it cannot go stale when the logo changes."""
    from PIL import Image, ImageDraw, ImageFont
    files = (sorted(OUT.glob("bamford-lab-logo-*@800w.png"))
             + sorted(OUT.glob("bamford-lab-mark-*@512w.png")))
    if not files:
        return
    cols, cw, ch, pad, lbl = 4, 460, 300, 18, 26

    def chequer(size, sq=12):
        im = Image.new("RGB", size, (234, 234, 234))
        d = ImageDraw.Draw(im)
        for y in range(0, size[1], sq):
            for x in range(0, size[0], sq):
                if (x // sq + y // sq) % 2:
                    d.rectangle([x, y, x + sq, y + sq], fill=(214, 214, 214))
        return im

    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cw + pad) + pad,
                              rows * (ch + lbl + pad) + pad + 34), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 14)
        title = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Bold.ttf", 18)
    except OSError:
        font = title = ImageFont.load_default()
    d.text((pad, 10), "Bamford Lab logo pack  (chequerboard = transparent background)",
           fill=(20, 20, 20), font=title)
    for i, f in enumerate(files):
        r, c = divmod(i, cols)
        x, y = pad + c * (cw + pad), 34 + pad + r * (ch + lbl + pad)
        cell = chequer((cw, ch))
        logo = Image.open(f).convert("RGBA")
        logo.thumbnail((cw - 28, ch - 28), Image.LANCZOS)
        cell.paste(logo, ((cw - logo.width) // 2, (ch - logo.height) // 2), logo)
        sheet.paste(cell, (x, y))
        d.text((x, y + ch + 5), f.name.split("@")[0].replace("bamford-lab-", ""),
               fill=(40, 40, 40), font=font)
    sheet.save(OUT / "_preview.png")


def main() -> int:
    if not (SRC / "logo-full.svg").exists():
        print("Run this from the repository root.", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    full = (SRC / "logo-full.svg").read_text()
    mark = (SRC / "favicon-virus.svg").read_text()

    variants = {
        # transparent background
        "bamford-lab-logo-colour":       recolour(full, CRIMSON, AMBER),
        "bamford-lab-logo-maroon":       recolour(full, MAROON, MAROON),
        "bamford-lab-logo-maroon-amber": recolour(full, MAROON, AMBER),
        "bamford-lab-logo-white":        recolour(full, WHITE, AMBER_LIGHT),
        "bamford-lab-logo-black":        recolour(full, INK, INK),
        # solid background
        "bamford-lab-logo-on-white":     with_background(recolour(full, CRIMSON, AMBER), WHITE),
        "bamford-lab-logo-on-maroon":    with_background(recolour(full, CREAM, AMBER_LIGHT), MAROON),
        "bamford-lab-logo-on-plum":      with_background(recolour(full, CREAM, AMBER_LIGHT), PLUM),
        # the virus mark alone
        "bamford-lab-mark-colour":       recolour(mark, CRIMSON, AMBER),
        "bamford-lab-mark-maroon":       recolour(mark, MAROON, MAROON),
        "bamford-lab-mark-white":        recolour(mark, WHITE, AMBER_LIGHT),
        "bamford-lab-mark-on-white":     with_background(recolour(mark, CRIMSON, AMBER), WHITE, 0.12),
    }

    for name, svg in variants.items():
        (OUT / f"{name}.svg").write_text(svg)

    for name in variants:
        widths = (1200, 512) if "mark" in name else (2400, 800)
        for w in widths:
            subprocess.run(
                ["rsvg-convert", "-w", str(w), str(OUT / f"{name}.svg"),
                 "-o", str(OUT / f"{name}@{w}w.png")],
                check=True,
            )

    build_preview()
    print(f"Wrote {len(variants)} SVGs and {len(variants) * 2} PNGs to {OUT.relative_to(ROOT)}/")
    print("Preview sheet _preview.png rebuilt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
