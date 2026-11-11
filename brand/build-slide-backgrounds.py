#!/usr/bin/env python3
"""Build 16:9 PowerPoint slide backgrounds for the Bamford Lab / EVOLVE-AI deck.

Run from the repository root:   python3 brand/build-slide-backgrounds.py

Outputs into brand/slide-backgrounds/ at 3840x2160 (16:9):
  cover-plain.png        red gradient + logo strip, clear space for the title
  cover-constellation.png  the same, with the lab's particle motif very faintly behind
  content.png            white body with a red gradient title banner across the top

Colour: #a6192e, sampled from James's existing slides (QUB brand red). The gradient
runs from a lifted crimson at top-left to a deeper maroon at bottom-right, with a soft
radial glow, so it reads as depth rather than as a flat fill.

Logo sourcing, in descending order of quality:
  Bamford Lab   - rendered from SVG, so it is vector-sharp at any size.
  NILAB emblem  - from the 12095px master in ~/NILAB, effectively lossless here.
  QUB + IGFS    - src/assets/igfs-logo.png (794x130). Used near native size.
  SoBS / NILAB wordmarks - RE-TYPESET in Lato rather than upscaled from a screenshot.
    Both are plain text, so setting them live is sharper than any amount of upscaling.
    See the note at the bottom of this file about replacing these with official vectors.
"""

import math
import pathlib
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

Image.MAX_IMAGE_PIXELS = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "brand" / "slide-backgrounds"
TMP = OUT / "_assets"
NILAB_DIR = pathlib.Path.home() / "NILAB"
LOGO_DIR = pathlib.Path.home() / "Pictures" / "Logos"

W, H = 3840, 2160
# 3840/288 = 13.333in and 2160/288 = 7.5in, which is EXACTLY a 16:9 PowerPoint slide.
# Stamping the DPI means "Insert > Picture" drops the image in at precisely full-slide
# size instead of PowerPoint guessing and scaling it to something arbitrary.
DPI = (288, 288)

BRAND_RED = (166, 25, 46)      # #a6192e, sampled from the existing slides
GRAD_LIGHT = (186, 42, 64)
GRAD_DARK = (118, 14, 33)
GLOW = (205, 56, 78)
AMBER = (233, 162, 74)

LATO = "/usr/share/fonts/truetype/lato/Lato-%s.ttf"
# The lab logo's bounding box includes the membrane, which sticks up well above the
# lettering. Centring that box drops the wordmark below the other logos in the strip, so
# lift it by this fraction of its height to align the LETTERING with them, not the box.
BAM_OPTICAL_LIFT = 0.186
# The NILAB roundel is a circle among wordmarks, so it needs to be proportionally taller
# than the text marks to carry equal weight. Expressed as a multiple of the strip height
# so the two strip builds stay consistent and it scales with everything else.
NILAB_RATIO = 1.45
# NOTE on centring: the strip is centred on its bounding box, and measures symmetric
# (margins within 4px of each other, gaps 239/109/121/239). Its ink MASS sits right of
# centre because IGFS and the roundel are dense while the lab wordmark is airy. Shifting
# the strip left to compensate was tried and reverted: it makes the geometric margins
# visibly unequal AND misaligns the strip with the rule beneath it, which is centred
# independently. Leave it centred geometrically.


def font(weight, size):
    return ImageFont.truetype(LATO % weight, size)


# ----------------------------------------------------------------- background
def gradient_panel(w, h, light=GRAD_LIGHT, dark=GRAD_DARK, glow=GLOW):
    """Diagonal gradient with a soft radial glow. Built small and upscaled, which
    is both much faster than per-pixel work and gives a smoother ramp."""
    sw, sh = 160, max(1, int(160 * h / w))
    base = Image.new("RGB", (sw, sh))
    px = base.load()
    for y in range(sh):
        for x in range(sw):
            t = (x / max(sw - 1, 1) * 0.65) + (y / max(sh - 1, 1) * 0.35)
            px[x, y] = tuple(int(light[i] + (dark[i] - light[i]) * t) for i in range(3))

    halo = Image.new("L", (sw, sh), 0)
    hp = halo.load()
    cx, cy, r = sw * 0.72, sh * 0.18, sw * 0.62
    for y in range(sh):
        for x in range(sw):
            d = math.hypot(x - cx, y - cy) / r
            hp[x, y] = int(max(0.0, 1.0 - d) ** 2 * 150)
    base = Image.composite(Image.new("RGB", (sw, sh), glow), base, halo)
    return base.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))


def constellation(w, h, n=90, seed=7):
    """The lab's particle motif: molecules, cytokine receptors and virus particles, linked.
    Deliberately faint. It should register as texture, never as content."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = [(rng.uniform(0, w), rng.uniform(0, h)) for _ in range(n)]

    link = w * 0.11
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i + 1:]:
            dist = math.hypot(x1 - x2, y1 - y2)
            if dist < link:
                a = int((1 - dist / link) * 46)
                d.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, a), width=2)

    for i, (x, y) in enumerate(pts):
        kind = i % 9
        if kind == 0:                                    # virus
            r = rng.uniform(13, 20)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 70), width=3)
            d.ellipse([x - r * .45, y - r * .45, x + r * .45, y + r * .45],
                      fill=AMBER + (62,))
            for k in range(8):
                a = k * math.pi / 4
                d.line([(x + math.cos(a) * r, y + math.sin(a) * r),
                        (x + math.cos(a) * (r + 9), y + math.sin(a) * (r + 9))],
                       fill=(255, 255, 255, 62), width=3)
        elif kind == 1:                                  # cytokine receptor + ligand
            # Mirrors the "L" of the logo: a stalk opening into a cupped binding pocket
            # with a molecule in it. Replaced an antibody, which was the wrong immunology.
            s = rng.uniform(13, 19)
            d.line([(x, y + s * 1.7), (x, y + s * 0.1)], fill=(255, 255, 255, 68), width=3)
            d.arc([x - s * .72, y - s * .72, x + s * .72, y + s * .72], 0, 180,
                  fill=(255, 255, 255, 68), width=3)
            r = s * 0.46
            d.ellipse([x - r, y - s * .18 - r, x + r, y - s * .18 + r], fill=AMBER + (70,))
        else:                                            # molecule
            r = rng.uniform(3, 6)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 80))
    return layer


# ---------------------------------------------------------------- logo assets
def svg(path, width):
    TMP.mkdir(parents=True, exist_ok=True)
    out = TMP / (pathlib.Path(path).stem + f"_{width}.png")
    subprocess.run(["rsvg-convert", "-w", str(width), str(path), "-o", str(out)], check=True)
    return Image.open(out).convert("RGBA")


def fit(im, height):
    return im.resize((max(1, round(im.width * height / im.height)), height), Image.LANCZOS)


def text_block(lines, align_left=True):
    """Render a stack of (text, weight, size, tracking) as a transparent image."""
    pad = 8
    widths, heights, rendered = [], [], []
    for txt, weight, size, track in lines:
        f = font(weight, size)
        w = sum(f.getlength(c) + track for c in txt)
        img = Image.new("RGBA", (int(w) + pad * 2, int(size * 1.5)), (0, 0, 0, 0))
        dd = ImageDraw.Draw(img)
        x = pad
        for c in txt:
            dd.text((x, 0), c, font=f, fill=(255, 255, 255, 255))
            x += f.getlength(c) + track
        rendered.append(img)
        widths.append(img.width)
        heights.append(int(size * 1.26))
    out = Image.new("RGBA", (max(widths), sum(heights)), (0, 0, 0, 0))
    y = 0
    for img, h in zip(rendered, heights):
        out.paste(img, (0 if align_left else (out.width - img.width) // 2, y), img)
        y += h
    return out.crop(out.getbbox())


def sobs_wordmark():
    return text_block([("SCHOOL OF", "Light", 60, 1.5),
                       ("BIOLOGICAL", "Bold", 60, 0.5),
                       ("SCIENCES", "Bold", 60, 0.5)])


def nilab_wordmark():
    return text_block([("NORTHERN IRELAND", "Bold", 62, 1.0),
                       ("LANDSCAPE PARTNERSHIP IN AI", "Bold", 62, 1.0),
                       ("FOR BIOSCIENCE", "Light", 62, 1.0)])


def nilab_emblem(height):
    for name in ("NILAB_Logo-modified.png", "NILAB_Logo.png"):
        p = NILAB_DIR / name
        if p.exists():
            return fit(Image.open(p).convert("RGBA"), height)
    return None


def qub_igfs(height, gap=None):
    """QUB + IGFS lockup, rebuilt so the QUB half comes from the vector EPS.

    The only IGFS artwork available is the 794px web raster, which goes soft once the
    logo strip is scaled up. Half the fix is free: crop the IGFS portion out of that
    raster (it starts after the divider at x~355) and pair it with the vector QUB.

    `gap` is exposed because a caller that places this lockup next to a FURTHER divider
    has to space that one identically. Leaving it to each builder's own constant is what
    made the IGFS-to-School gap read as nearly double the QUB-to-IGFS one on the title
    slide. Pass the same value you use between the row's other parts.
    """
    raster = Image.open(ROOT / "src/assets/igfs-logo.png").convert("RGBA")
    igfs = raster.crop((355, 0, raster.width, raster.height))
    igfs = igfs.crop(igfs.getbbox())

    qub = qub_only(height)
    igfs = fit(igfs, int(height * 0.82))
    div = rule(int(height * 0.95), 3, 130)

    if gap is None:
        gap = int(height * 0.34)
    w = qub.width + gap + 3 + gap + igfs.width
    out = Image.new("RGBA", (w, height), (0, 0, 0, 0))
    cy = height // 2
    x = 0
    out.alpha_composite(qub, (x, cy - qub.height // 2)); x += qub.width + gap
    out.alpha_composite(div, (x, cy - div.height // 2)); x += 3 + gap
    out.alpha_composite(igfs, (x, cy - igfs.height // 2))
    return out


def qub_only(height):
    """The official QUB landscape logo, rasterised from the EPS so it is vector-quality.

    The white EPS renders white-on-white and so cannot be keyed, but the BLACK EPS
    rasterises cleanly and its inverse is exactly the alpha channel we want. So we
    render the black one, invert it to an alpha mask, and fill with white.
    """
    eps = LOGO_DIR / "QUB New logo set_Black" / "Queen\u2019s Black Logo - Landscape.eps"
    if eps.exists():
        im = Image.open(eps)
        im.load(scale=10)
        mask = ImageOps.invert(im.convert("L"))
        out = Image.new("RGBA", mask.size, (255, 255, 255, 255))
        out.putalpha(mask)
        out = out.crop(out.getbbox())
        return fit(out, height)
    # fallback: the low-resolution web raster
    return fit(Image.open(ROOT / "src/assets/qub-logo.png").convert("RGBA"), height)


def rule(h, thickness=3, alpha=120):
    r = Image.new("RGBA", (thickness, h), (255, 255, 255, alpha))
    return r


# --------------------------------------------------------------------- slides
def build_cover(with_constellation, nilab=True):
    bg = gradient_panel(W, H).convert("RGBA")
    if with_constellation:
        bg.alpha_composite(constellation(W, H))

    strip_h = 200
    bam = fit(svg(ROOT / "brand/logo-pack/bamford-lab-logo-white.svg", 1800), int(strip_h * 1.25))
    qi = qub_igfs(strip_h - 44)
    sobs = fit(sobs_wordmark(), strip_h - 58)

    parts = [bam, qi, sobs]
    if nilab:
        parts.append(nilab_emblem(int(strip_h * NILAB_RATIO)))
    gap = 118
    dividers = {0, 2} if len(parts) > 3 else {0}
    total = (sum(p.width for p in parts) + gap * (len(parts) - 1)
             + len(dividers) * (gap + 3))
    x = (W - total) // 2
    cy = 340
    for i, p in enumerate(parts):
        lift = int(p.height * BAM_OPTICAL_LIFT) if i == 0 else 0
        bg.alpha_composite(p, (int(x), int(cy - p.height / 2 - lift)))
        x += p.width + gap
        if i in dividers:
            r = rule(strip_h - 40)
            bg.alpha_composite(r, (int(x), int(cy - r.height / 2)))
            x += 3 + gap

    # a faint rule marking where the title block can start
    d = ImageDraw.Draw(bg)
    d.line([(300, 640), (W - 300, 640)], fill=(255, 255, 255, 48), width=3)
    return bg.convert("RGB")


def build_content(nilab=True, transparent=False):
    """The content slide furniture.

    transparent=True leaves the body fully transparent instead of white. That version is
    for dropping onto a slide as a PICTURE: it still inserts at exact full-slide size, but
    because everything below the banner is transparent it does not hide whatever is already
    on the slide, so there is no need to send it to the back.
    """
    band = 430
    if transparent:
        page = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    else:
        page = Image.new("RGB", (W, H), (255, 255, 255))
    banner = gradient_panel(W, band).convert("RGBA")
    # the same particle motif as the covers, so the deck reads as one set. Generated at
    # the banner's own size so it is naturally clipped to it, with its own seed so it
    # does not repeat the cover's arrangement, and a lower count to suit the shallow band.
    banner.alpha_composite(constellation(W, band, n=34, seed=19))
    page.paste(banner.convert("RGB"), (0, 0))

    if nilab:
        # QUB crest + the NILAB wordmark, rebuilt rather than upscaled from the screenshot
        crest = qub_only(int(band * 0.46))
        word = fit(nilab_wordmark(), int(band * 0.34))
    else:
        # Generic lab version: the lab mark alongside the QUB and IGFS lockup, so it
        # suits any member whatever their funder.
        crest = fit(svg(ROOT / "brand/logo-pack/bamford-lab-logo-white.svg", 1400),
                    int(band * 0.42))
        word = qub_only(int(band * 0.30))
    r = rule(int(band * 0.42), 3, 150)

    pad = 150
    total = crest.width + 54 + 3 + 54 + word.width
    x = W - pad - total
    cy = band // 2
    layer = Image.new("RGBA", page.size, (0, 0, 0, 0))
    layer.alpha_composite(crest, (int(x), int(cy - crest.height / 2)))
    x += crest.width + 54
    layer.alpha_composite(r, (int(x), int(cy - r.height / 2)))
    x += 3 + 54
    layer.alpha_composite(word, (int(x), int(cy - word.height / 2)))
    page = Image.alpha_composite(page.convert("RGBA"), layer)
    if not transparent:
        page = page.convert("RGB")

    # thin amber keyline under the banner, echoing the logo's virus core
    d = ImageDraw.Draw(page)
    d.rectangle([0, band, W, band + 7], fill=AMBER + ((255,) if transparent else ()))
    return page


def main():
    if not (ROOT / "src/assets/igfs-logo.png").exists():
        print("Run from the repository root.", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    # Generic lab set: no funder marks, so anyone in the group can use them.
    build_cover(False, nilab=False).save(OUT / "cover-lab.png", dpi=DPI)
    build_cover(True, nilab=False).save(OUT / "cover-lab-constellation.png", dpi=DPI)
    build_content(nilab=False).save(OUT / "content-lab.png", dpi=DPI)
    build_content(nilab=False, transparent=True).save(
        OUT / "content-lab-transparent.png", dpi=DPI)
    # NILAB set: for James and anyone else NILAB-funded.
    build_cover(False, nilab=True).save(OUT / "cover-nilab.png", dpi=DPI)
    build_cover(True, nilab=True).save(OUT / "cover-nilab-constellation.png", dpi=DPI)
    build_content(nilab=True).save(OUT / "content-nilab.png", dpi=DPI)
    build_content(nilab=True, transparent=True).save(
        OUT / "content-nilab-transparent.png", dpi=DPI)
    print(f"Wrote 8 backgrounds at {W}x{H} to {OUT.relative_to(ROOT)}/")
    return 0


# NOTE ON LOGO QUALITY
# The School of Biological Sciences and NILAB wordmarks here are re-typeset in Lato,
# because the only copies available were a 135px PNG and a 514px screenshot and no
# amount of upscaling recovers detail that was never captured. Lato is close but it
# is NOT guaranteed to be the official typeface. To make these exactly correct, get
# the vector (SVG/EPS/PDF) versions of the QUB, IGFS, School of Biological Sciences
# and NILAB logos from the QUB brand portal, drop them in, and switch the functions
# above to render from those instead.

if __name__ == "__main__":
    raise SystemExit(main())
