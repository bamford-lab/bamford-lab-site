#!/usr/bin/env python3
"""Build ready-to-use PowerPoint templates with the backgrounds already applied.

    python3 brand/build-pptx-template.py

Writes into brand/slide-backgrounds/:
    bamford-lab-NILAB.pptx    title slide + content layout, with the NILAB marks
    bamford-lab.pptx          the same without funder marks, for anyone in the group

Why this exists: setting a picture as a slide *background* is a different menu from
inserting a picture, and inserting one leaves it floating on top of the slide at whatever
size PowerPoint feels like. This sidesteps the whole problem. Open the .pptx, start typing.

The background is placed on the slide LAYOUT and pushed to the back of the z-order, so
every new slide made from that layout inherits it automatically and your content always
sits on top of it.
"""

import pathlib
import sys

from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from lxml import etree

ROOT = pathlib.Path(__file__).resolve().parent.parent
BG = ROOT / "brand" / "slide-backgrounds"

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)   # 16:9


BG_XML = (
    '<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    '<p:bgPr><a:blipFill rotWithShape="1"><a:blip r:embed="{rid}"/>'
    '<a:stretch><a:fillRect/></a:stretch></a:blipFill><a:effectLst/></p:bgPr></p:bg>'
)


def set_background(container, image):
    """Set a real picture BACKGROUND on a slide or layout.

    This writes the same <p:bg><p:bgPr><a:blipFill> that PowerPoint's
    "Format Background > Picture fill" produces, rather than inserting a floating
    picture. Put on a layout, every slide using that layout inherits it.
    """
    image_part, rid = container.part.get_or_add_image_part(str(image))
    cSld = container._element.find(qn("p:cSld"))
    for old in cSld.findall(qn("p:bg")):
        cSld.remove(old)
    cSld.insert(0, etree.fromstring(BG_XML.format(rid=rid)))


def build(nilab: bool, out_name: str, title_stem: str = "title-slide"):
    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H

    suffix = "nilab" if nilab else "lab"
    title_png = BG / f"{title_stem}.png"
    content_png = BG / f"content-{suffix}.png"
    cover_png = BG / f"cover-{suffix}-constellation.png"

    blank = prs.slide_layouts[6]            # Blank
    title_and_content = prs.slide_layouts[1]

    # --- put the background on the LAYOUT so new slides inherit it ---
    set_background(title_and_content, content_png)

    # Pull the layout's placeholders clear of the red banner and size them sensibly.
    for ph in title_and_content.placeholders:
        if ph.placeholder_format.idx == 0:          # title, sits on the red banner
            ph.left, ph.top = Inches(0.55), Inches(0.30)
            ph.width, ph.height = Inches(8.4), Inches(0.90)
            # Set it on the paragraph (defRPr), not on runs: a layout placeholder holds
            # prompt text rather than real runs, so run-level formatting would not stick.
            para = ph.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.LEFT
            para.font.size, para.font.bold = Pt(30), True
            para.font.name = "Lato"
            para.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        else:                                        # body
            ph.left, ph.top = Inches(0.55), Inches(1.85)
            ph.width, ph.height = Inches(12.2), Inches(5.1)

    # --- slide 1: the finished title slide, as a full-bleed image ---
    s1 = prs.slides.add_slide(blank)
    set_background(s1, title_png if (nilab and title_png.exists()) else cover_png)

    # --- slide 2: an example content slide so the layout is obvious ---
    s2 = prs.slides.add_slide(title_and_content)
    t = s2.shapes.title
    t.text = "Your slide title here"
    # Formatting has to be restated on the run: typing into a placeholder creates a run,
    # and a run does not pick up the layout's paragraph-level defaults in every renderer.
    para = t.text_frame.paragraphs[0]
    para.alignment = PP_ALIGN.LEFT
    for r in para.runs:
        r.font.size, r.font.bold = Pt(30), True
        r.font.name = "Lato"
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    out = BG / out_name
    prs.save(str(out))
    return out


def main():
    if not (BG / "content-nilab.png").exists():
        print("Run brand/build-slide-backgrounds.py first.", file=sys.stderr)
        return 1

    # One template per title slide, so each talk opens ready to go. Add a line here (and
    # generate the matching title slide with build-title-slide.py --out) for a new talk.
    decks = [
        (True,  "bamford-lab-NILAB.pptx",     "title-slide"),
        (True,  "bamford-lab-NILAB-plm.pptx", "title-slide-plm"),
        (True,  "bamford-lab-NILAB-druggable.pptx", "title-slide-druggable"),
        (False, "bamford-lab.pptx",           "title-slide"),
    ]
    made = []
    for nilab, name, stem in decks:
        if nilab and not (BG / f"{stem}.png").exists():
            print(f"  skipping {name}: {stem}.png not found", file=sys.stderr)
            continue
        made.append(build(nilab, name, stem).name)
    print("Wrote " + ", ".join(made))
    print("Open one and start typing. New slides: Home > New Slide > Title and Content.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
