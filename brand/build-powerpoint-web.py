#!/usr/bin/env python3
"""Mirror the slide artwork into the sizes PowerPoint for the WEB actually honours.

    python3 brand/build-powerpoint-web.py        # run LAST, after the other two builds

The masters in brand/slide-backgrounds/ are 3840x2160 stamped at 288 DPI, so desktop
PowerPoint places them at exactly 13.33x7.5in. PowerPoint in the browser ignores PNG DPI,
works to a flat 96, and has no Format Background picture fill, so a 3840px file dragged
onto a slide always lands at the wrong size. 1280x720 at 96 DPI is the same 13.33x7.5in
and drops in correctly.

This used to be done by hand, which meant the copies silently went stale whenever a master
was rebuilt. Running it is now the last step of the slide build.
"""

import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
BG = ROOT / "brand" / "slide-backgrounds"
WEB = BG / "for-powerpoint-web"

SIZE = (1280, 720)      # 13.333 x 7.5in at 96 DPI
DPI = (96, 96)


def main() -> int:
    masters = sorted(p for p in BG.glob("*.png"))
    if not masters:
        print("No masters found. Run build-slide-backgrounds.py first.", file=sys.stderr)
        return 1

    WEB.mkdir(parents=True, exist_ok=True)
    for src in masters:
        im = Image.open(src)
        # Keep the alpha channel only where there is genuine transparency: the -transparent
        # content slides are meant to be dropped over an existing background.
        im = im.convert("RGBA" if im.mode == "RGBA" and im.getextrema()[3][0] < 255 else "RGB")
        im.resize(SIZE, Image.LANCZOS).save(WEB / src.name, dpi=DPI)

    print(f"Mirrored {len(masters)} slides to {WEB.relative_to(ROOT)}/ at "
          f"{SIZE[0]}x{SIZE[1]} @ {DPI[0]} DPI")
    print("Drag these onto a slide in PowerPoint for the web; use the 3840px masters on desktop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
