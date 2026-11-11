# Bamford Lab website

The website for the Bamford Lab (antiviral immunity, Queen's University Belfast). Built with [Eleventy](https://www.11ty.dev/), edited through [Sveltia CMS](https://github.com/sveltia/sveltia-cms), hosted on Cloudflare Pages.

## Quick start

```bash
./preview.sh     # starts the server and opens the site. Use this.
```

Or by hand:

```bash
npm install
npm run dev      # http://localhost:8080
npm run build    # builds into _site/
```

> **Never open `_site/index.html` directly.** Asset paths are absolute (`/assets/...`), so a
> `file://` URL cannot resolve the stylesheet or images and the page renders unstyled and
> broken. It is not a fault in the site: the pages must be *served*. Always view the site at
> **http://localhost:8080**, via `./preview.sh` or `npm run dev`. There is also a
> double-clickable **"Bamford Lab site (preview)"** launcher on the Desktop.

## Where content lives

| What | File(s) |
|------|---------|
| Lab members | `src/people/*.md` (one per person) |
| News items | `src/news/*.md` (one per post) |
| Contact, socials, address | `src/_data/site.json` |
| Research / About / Publications / Find us copy | `src/index.njk` |
| Logo and images | `src/assets/` |
| Global layout (nav, footer) | `src/_includes/base.njk` |
| Styles | `src/assets/styles.css` |
| CMS setup | `src/admin/config.yml` |

### Adding a person by hand
Create `src/people/4-name.md`:

```markdown
---
name: Full Name
role: PhD Researcher
order: 4
initials: FN
photo: "/assets/uploads/name.jpg"   # or leave "" to show initials
projectLabel: Project
projectTitle: "Their project title."
funders: "Funded by X. Collaborators: Y."
outside: "what they do outside the lab."
draft: false
---
Around 100 words of bio here.
```

### Adding news by hand
Create `src/news/2026-10-31-title.md`:

```markdown
---
title: Headline
date: 2026-10-31
tag: Grant
---
A sentence or two.
```

Or just use the `/admin/` editor once deployed (see **DEPLOY.md**).

## Deploying

See **DEPLOY.md** for the full walkthrough: domain, GitHub, Cloudflare Pages, and the CMS login.
