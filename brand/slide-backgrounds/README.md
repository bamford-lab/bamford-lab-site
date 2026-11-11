# Slide backgrounds

16:9 PowerPoint backgrounds at **3840 x 2160**. A PowerPoint 16:9 slide is 13.33 x 7.5 inches,
so that works out at about **288 DPI**: sharp on any projector, and sharp in print if a slide
ever ends up in a poster or a report.

There are **two sets**. The `-lab` files carry no funder marks, so anyone in the group can use
them whatever their funding. The `-nilab` files are for NILAB-funded work.

| File | Use |
|---|---|
| `cover-lab.png` | Title slide, generic. Red gradient, Bamford Lab + QUB/IGFS + School of Biological Sciences across the top. |
| `cover-lab-constellation.png` | The same, with the lab's particle motif (molecules, antibodies, virus particles) very faintly behind. Ties the deck to the website. |
| `content-lab.png` | Every other slide, generic. Red gradient title banner, white body, Bamford Lab + QUB on the right. |
| `content-lab-transparent.png` | **Best for adding by hand.** Same banner, but everything below it is transparent, so it never hides your content and needs no Send to Back. |
| `cover-nilab.png` | Title slide with the NILAB roundel added. |
| `cover-nilab-constellation.png` | As above, with the particle motif. |
| `content-nilab.png` | Content slide with the QUB and NILAB lockup on the right. |
| `content-nilab-transparent.png` | **Best for adding by hand.** As above with a transparent body. |

## A finished title slide

`title-slide.svg` and `title-slide.png` are a complete opening slide, not just a background:
logos, title, name, supervisory team and affiliation all laid out.

**Use the PNG** if the wording is right as it stands. **Use the SVG** when a talk needs a
different title: the title, name and footer are real, editable text, so you can open it in
Inkscape, Illustrator, or any text editor and change the words.

Or regenerate it, which handles the line breaks and spacing for you:

```bash
python3 brand/build-title-slide.py --title "Where do protein language models go blind?"
python3 brand/build-title-slide.py --title "..." --name "Someone Else" --no-nilab
python3 brand/build-title-slide.py --plain          # without the constellation texture
python3 brand/build-title-slide.py --title "..." --out belfast-2026   # a separate file
```

On the title slides the logos sit in two centred rows at the top, the lab's own mark then
Queen's with IGFS and the School of Biological Sciences, with the text centred beneath them
and the NILAB roundel on its own at the foot of the slide. The cover
backgrounds still carry them as a single horizontal row, since a tall stack would eat the
space you need for your own title.

The title shrinks a step at a time until it fits four lines, and the whole block (logos, title,
name, footer) is measured and then centred vertically, so it stays balanced whether the title
runs to one line or four.

**If you hand-edit the SVG:** SVG has no automatic text wrapping, so each title line is its own
`<tspan>`. Change the words freely, but mind the line breaks yourself, or just regenerate.

## Easiest: just open the template

Three templates, all with the backgrounds already applied. Open one and start typing.

| File | Title slide |
|---|---|
| `bamford-lab-NILAB.pptx` | EVOLVE-AI |
| `bamford-lab-NILAB-plm.pptx` | Predicting where PLMs are evolutionarily blind |
| `bamford-lab.pptx` | generic cover, no funder marks, for anyone in the group |

**For a new talk**, make its title slide and then rebuild the templates:

```bash
python3 brand/build-title-slide.py --title "Your talk title" --out title-slide-foo
# add ("True, "bamford-lab-NILAB-foo.pptx", "title-slide-foo") to the decks list in
# brand/build-pptx-template.py, then:
python3 brand/build-pptx-template.py
```
 **Home > New Slide > Title and Content** gives you another content slide with
the banner already on it, title placeholder positioned and styled white.

Use these and you can ignore everything below.

## Or apply a background by hand

**Use Format Background, not Insert Picture.** This is the usual trip-up: *Insert → Picture*
drops the file in as a floating object sitting on top of the slide, which is why it can appear
small and in the middle. You want it to BE the background.

PowerPoint: **Design → Format Background → Picture or texture fill → Insert → From a File**.
LibreOffice Impress: **Slide → Slide Properties → Background → Image**.

To apply it to every slide at once, do it on the Slide Master (**View → Slide Master**) rather
than slide by slide.

### PowerPoint in the browser

Use the copies in **`for-powerpoint-web/`**. They are the same images at **1280 x 720**.

PowerPoint for the web **ignores the DPI stamped in a PNG** and works to the universal 96 DPI
assumption, which is why the 3840px versions come in at the wrong size however they are added.
At 96 DPI, 1280 x 720 is exactly 13.33 x 7.5 inches, so these drop straight in at full slide
size with nothing to resize.

The web version also has **no Format Background picture fill**, so inserting a picture is the
only route. Use the **`-transparent`** content files: they paint the banner and leave the rest
clear, so they never cover your content.

If one still lands at the wrong size, select it and use **Picture > Size** to set width
**13.33"** and height **7.5"**, then **Position** 0 and 0. That always works.

Better still for the web: upload **`bamford-lab-NILAB.pptx`** to OneDrive and open it there.
The backgrounds are already on the slide layout, so there is nothing to insert at all.

### Adding one by hand (desktop apps)

All the files are stamped at **288 DPI**, which makes 3840 x 2160 work out as exactly
13.33 x 7.5 inches, the size of a 16:9 slide. So *Insert > Picture* now drops any of them in
at precisely full slide size with no resizing. (Before that was stamped, the software had to
guess the physical size and got it wrong, which is why an inserted image came out small and
floating in the middle.)

For content slides added by hand, use the **`-transparent`** versions. The plain ones have a
solid white body, so as a picture they sit on top of everything and hide it until you Send to
Back. The transparent ones only paint the banner, so your content shows straight through and
there is nothing else to do.

**If you already inserted an older copy**, regenerating the file does not change the picture
already sitting in your deck. Delete it and insert the current file.

Keep **Tile picture as texture** switched OFF, or it will repeat rather than fill.

## Where to put your text

- **Cover:** there is a faint hairline about a quarter of the way down. Start the title block
  just under it. Everything below is deliberately empty.
- **Content:** the banner is the top **430px** of a 2160px slide, so in PowerPoint terms the
  title sits in roughly the top fifth. Keep the title left-aligned and clear of the logos on
  the right. The thin amber line marks the bottom of the banner: keep body content below it.

## Type

The title slide is set in **Lato** by default. Two alternatives are a flag away:

```bash
python3 brand/build-title-slide.py --font plex    # IBM Plex Sans, the website's interface face
python3 brand/build-title-slide.py --font serif   # Newsreader, the website's heading face
```

`serif` was tried and rejected: a serif title looks out of place against the logo strip.
`plex` is the one to reach for if Lato ever feels too generic, since it is more distinctive
while still being a sans, and it matches the website.

Plex and Newsreader live at `~/.local/share/fonts/bamford/`. The **PNG** has the type baked
in and looks right anywhere. The **SVG** references fonts by name, so on a machine without
them it falls back to Helvetica or Georgia. Copy those files across, or just use the PNG.

## Colour

The red is **#a6192e**, sampled from the slides you were already using (it is the Queen's
brand red). The gradient runs from a lifted crimson at top left to a deeper maroon at bottom
right, with a soft glow, so it reads as depth rather than a flat fill. Accent amber is
**#e9a24a**, the same amber as the virus core in the lab logo.

## A note on logo quality

**Vector-quality, no upscaling:**

- **Bamford Lab** - rendered from its own SVG.
- **Queen's University Belfast** - rasterised from the official EPS in
  `~/Pictures/Logos/QUB New logo set_Black`. The white EPS renders white-on-white and cannot be
  keyed, so the script renders the *black* EPS and inverts it into an alpha mask instead. The
  QUB+IGFS lockup is **rebuilt**: vector QUB, then the IGFS half cropped out of the old raster,
  because enlarging the logo strip made the all-raster lockup go soft.
- **NILAB roundel** - from the 12,095px master in `~/NILAB`.

**Re-typeset, not upscaled:** the **School of Biological Sciences** and **NILAB** wordmarks. The
only copies available were a 135px PNG and a 514px screenshot, and upscaling cannot recover
detail that was never captured, so both are set fresh as live text in Lato. That is sharp at any
size and very close to the originals, but Lato is **not guaranteed to be the official typeface**.

To finish the job, drop the **vector (EPS/SVG/PDF)** IGFS and School of Biological Sciences logos
into `~/Pictures/Logos/` and point `qub_igfs()` and `sobs_wordmark()` in
`brand/build-slide-backgrounds.py` at them. The QUB EPS is already wired up and shows the pattern.

## Rebuilding

```bash
python3 brand/build-slide-backgrounds.py     # from the repository root
```
