# Bamford Lab logo pack

Reusable logo files for slides, posters, papers, email signatures and merchandise.
Open `_preview.png` to see every version at a glance (the chequerboard means a transparent background).

## Which file do I want?

| Where you are putting it | Use |
|---|---|
| A white slide or a white poster | `bamford-lab-logo-colour` (transparent, so the slide shows through) |
| A white slide, and you want a defined logo block | `bamford-lab-logo-on-white` |
| A light but not-white background (cream, pale grey, a photo) | `bamford-lab-logo-maroon` or `bamford-lab-logo-colour` |
| A dark slide, a dark poster, a photo | `bamford-lab-logo-white` |
| You want the lab's dark red as a solid panel | `bamford-lab-logo-on-maroon` |
| A near-black panel, matching the website hero | `bamford-lab-logo-on-plum` |
| Printing in one colour, or a journal that wants greyscale | `bamford-lab-logo-black` |
| A small space: avatar, favicon, social profile, slide corner | any `bamford-lab-mark-*` (the virus on its own) |

## SVG or PNG?

**Use the SVG whenever the software will take one.** It is vector, so it stays perfectly
sharp at any size, from a business card to a conference banner. PowerPoint, Keynote,
Google Slides, Word, Illustrator, Inkscape and Figma all accept SVG.

Use a PNG only if something refuses SVG. Two sizes are supplied:

- `@2400w` for print, posters and anything large
- `@800w` for slides, documents and email

The virus mark alone comes at `@1200w` and `@512w`, and is square.

**Never scale a PNG up.** If it looks soft, go back to the SVG.

## Colour reference

| Name | Hex | Used for |
|---|---|---|
| Crimson | `#b41f35` | the primary brand red |
| Maroon | `#8f1728` | the deeper red, for solid panels and one-colour work |
| Amber | `#e08a3c` | the virus core and the antibody highlights |
| Amber (light) | `#e9a24a` | the amber on dark backgrounds, lifted for contrast |
| Plum-black | `#180a0e` | the near-black from the website hero and footer |
| Cream | `#f4ecec` | the off-white used for the logo on dark backgrounds |

## Please do not

- Stretch or squash it. Hold shift while resizing, or set width and height together.
- Recolour it into something outside the palette above.
- Rebuild the wordmark by typing "Bamford Lab" in a font. The virus is the "o" and the
  antibody is built into the "L", so it will not match.
- Put the colour version on a dark background, or the white version on a light one.
- Crowd it. Leave clear space around the logo of at least the height of the virus mark.

## Regenerating this pack

These files are generated, not hand-drawn. The two masters live in `src/assets/`
(`logo-full.svg` and `favicon-virus.svg`), and both trace back to `brand/logo-source.jpeg`
via `brand/vectorise-logo.py`. To rebuild the pack after a change to the masters, run
`brand/build-logo-pack.py` from the repository root.
