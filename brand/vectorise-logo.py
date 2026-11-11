#!/usr/bin/env python3
"""
Regenerate the Bamford Lab logo SVGs from the raster source (brand/logo-source.jpeg).

The source is the original integrated wordmark: the virus particle is the
"o" in "Bamford", and a cytokine receptor binding its ligand forms the "L" of "Lab",
tagline "ANTIVIRAL IMMUNITY". (The "L" was an antibody until Oct 2026; it was replaced
because the lab works on innate immunity, not antibodies.)
It is crimson + amber on white.

This does a clean TWO-COLOUR trace with smooth Bezier curves via potracer
(pure-Python potrace). Outputs:
  - src/assets/logo-full.svg        crimson #b41f35 + amber #e08a3c   (light backgrounds)
  - src/assets/logo-full-dark.svg   white #f4ecec  + amber #e9a24a   (dark backgrounds: hero, footer)
  - src/assets/favicon-virus.svg    the virus mark only (nav + favicon)

Requires: pip install potracer pillow scikit-image numpy
After running, regenerate the PNG favicons + OG image (see README / commands below).

GOTCHA: potracer traces the FALSE region as the shape, so masks are inverted (~mask)
before tracing. Do not remove the ~ or the logo comes out filled/inverted.
"""
import numpy as np, potrace
from PIL import Image
from skimage import measure, morphology, filters

# Prefer the LOSSLESS source. Editing a JPEG and re-saving it compounds compression
# artefacts along every colour boundary, and the tracer faithfully follows that wobble,
# which is what once made the perfectly-drawn amber discs come out visibly hand-drawn.
SRC = 'brand/logo-source.png' if __import__('os').path.exists('brand/logo-source.png') else 'brand/logo-source.jpeg'
im0 = Image.open(SRC).convert('RGB'); arr0 = np.asarray(im0).astype(int)
R, G, B = arr0[..., 0], arr0[..., 1], arr0[..., 2]
colored = (R - G) > 20                       # any logo pixel (letters/icons) vs white bg
ys, xs = np.where(colored); pad = 16
y0, y1 = max(ys.min()-pad, 0), min(ys.max()+pad, arr0.shape[0])
x0, x1 = max(xs.min()-pad, 0), min(xs.max()+pad, arr0.shape[1])
crop = im0.crop((x0, y0, x1, y1))
UP = 4
crop = crop.resize((crop.width*UP, crop.height*UP), Image.LANCZOS)   # upsample for smoother boundaries
a = np.asarray(crop).astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
red_ish = (R - G) > 20
amber   = red_ish & (G > 105) & ((G - B) > 35) & (B < 140)         # amber: high G, low B
crimson = red_ish & ~amber                                        # everything else red = crimson
crimson = morphology.remove_small_objects(crimson, 160)
amber   = morphology.remove_small_objects(amber, 90)
crimson = morphology.remove_small_holes(crimson, 100)

# Smooth the binary masks before tracing. Each letter in the source carries a darker
# outline, so the colour threshold cuts through a soft ramp and lands at a slightly
# different place along it from pixel to pixel. Tracing that raw gives visibly wobbly
# stems and diagonals. Blurring the mask and re-thresholding at 0.5 averages that out.
def _smooth(mask, sigma=2.4):
    return filters.gaussian(mask.astype(float), sigma=sigma) > 0.5
crimson = _smooth(crimson)
amber   = _smooth(amber)
H, W = crimson.shape

def to_d(mask, ox=0, oy=0):
    bmp = potrace.Bitmap(np.ascontiguousarray(~mask))             # ~mask: potracer traces False region
    path = bmp.trace(turdsize=3, alphamax=1.0, opticurve=True, opttolerance=0.2)
    out = []
    for cur in path.curves:
        sp = cur.start_point; s = f"M{sp.x+ox:.2f} {sp.y+oy:.2f}"
        for seg in cur.segments:
            e = seg.end_point
            if seg.is_corner:
                c = seg.c; s += f"L{c.x+ox:.2f} {c.y+oy:.2f}L{e.x+ox:.2f} {e.y+oy:.2f}"
            else:
                c1, c2 = seg.c1, seg.c2
                s += f"C{c1.x+ox:.2f} {c1.y+oy:.2f} {c2.x+ox:.2f} {c2.y+oy:.2f} {e.x+ox:.2f} {e.y+oy:.2f}"
        s += "Z"; out.append(s)
    return "".join(out)

cd = to_d(crimson)

# The amber elements (the virus core, and the ligand bound to the receptor) are true
# circles, so emit them as <circle> rather than tracing them. A traced circle is a
# bezier approximation of a rasterised edge and always carries a slight wobble that is
# obvious when anyone zooms in. Anything amber that is NOT near-circular still gets traced.
amber_circles, amber_rest = [], np.zeros_like(amber)
for _p in measure.regionprops(measure.label(amber)):
    if _p.area >= 200 and _p.solidity > 0.93 and _p.eccentricity < 0.30:
        _cy, _cx = _p.centroid
        _r = ((_p.bbox[2]-_p.bbox[0]) + (_p.bbox[3]-_p.bbox[1])) / 4.0
        amber_circles.append((_cx, _cy, _r))
    else:
        amber_rest[measure.label(amber) == _p.label] = True
ad = to_d(amber_rest) if amber_rest.any() else ''
def write(fn, cf, af):
    open(fn, 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="Bamford Lab, Antiviral Immunity">'
        f'<path fill="{cf}" fill-rule="evenodd" d="{cd}"/>'
        + (f'<path fill="{af}" fill-rule="evenodd" d="{ad}"/>' if ad else '')
        + ''.join(f'<circle fill="{af}" cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/>'
                  for cx, cy, r in amber_circles)
        + '</svg>')
write('src/assets/logo-full.svg',      '#b41f35', '#e08a3c')
write('src/assets/logo-full-dark.svg', '#f4ecec', '#e9a24a')

# --- virus favicon: find the round amber core, crop around it, keep only central components ---
# Identify the virus core by what SURROUNDS it, which is the only stable signal.
# There are two round amber blobs (the virus core, and the ligand bound to the receptor)
# and they are near-identical in size and roundness, so neither "roundest" nor "highest"
# works: both have picked the ligand at some point and produced a receptor favicon.
# The virus core is enclosed by its capsid and spikes, so an annulus around it is almost
# entirely crimson (~0.94), while a ligand sits in an open cup (~0.22). Pick the blob with
# the most crimson around it.
yy, xx = np.mgrid[0:H, 0:W]
lbl = measure.label(amber); best = None; best_ring = -1.0
for p in measure.regionprops(lbl):
    if p.area < 200: continue
    pcy, pcx = p.centroid; pr = (p.area / np.pi) ** 0.5
    dist = np.hypot(yy - pcy, xx - pcx)
    ring = (dist > pr * 1.9) & (dist < pr * 3.0)
    enclosed = crimson[ring].mean() if ring.any() else 0.0
    if enclosed > best_ring: best_ring, best = enclosed, p
cy, cx = best.centroid; r = (best.area/np.pi)**0.5; half = int(r * 4.4)   # scales with the core, so it stays correct at any UP factor
xa, xb = max(int(cx-half), 0), min(int(cx+half), W); ya, yb = max(int(cy-half), 0), min(int(cy+half), H)
vc = crimson[ya:yb, xa:xb].copy(); va = amber[ya:yb, xa:xb].copy()
vh, vw = vc.shape; ccx, ccy = cx-xa, cy-ya; side = max(vw, vh)
def keep_central(mask, cyc, cxc, rad):
    out = np.zeros_like(mask); L = measure.label(mask)
    for p in measure.regionprops(L):
        if ((p.centroid[0]-cyc)**2 + (p.centroid[1]-cxc)**2)**0.5 < rad: out[L == p.label] = True
    return out
vc = keep_central(vc, ccy, ccx, side*0.46); va = keep_central(va, ccy, ccx, side*0.46)
ox, oy = (side-vw)//2, (side-vh)//2
open('src/assets/favicon-virus.svg', 'w').write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side} {side}" width="{side}" height="{side}" '
    f'role="img" aria-label="Bamford Lab">'
    f'<path fill="#b41f35" fill-rule="evenodd" d="{to_d(vc, ox, oy)}"/>'
    f'<path fill="#e08a3c" fill-rule="evenodd" d="{to_d(va, ox, oy)}"/></svg>')
print("regenerated logo-full.svg, logo-full-dark.svg, favicon-virus.svg")
