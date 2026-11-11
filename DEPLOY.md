# Deploying the Bamford Lab website

Stack: **Eleventy** (static site generator) + **Sveltia CMS** (browser-based editing) + **Cloudflare Pages** (free hosting) + a **custom domain**. This guide takes you from the local project to a live site with a `/admin` login that Connor and the students can use.

Work top to bottom. Steps 1 to 3 get the site online; steps 4 to 5 add the editor.

---

## 0. Run it locally first

```bash
cd bamford-lab-site
npm install
npm run dev        # live preview at http://localhost:8080
npm run build      # one-off build into _site/
```

Content lives in plain files you can edit by hand any time:
- `src/people/*.md`   one file per lab member
- `src/news/*.md`     one file per news item
- `src/_data/site.json`  email, address, social links
- Research / About / Publications / Find us text: `src/index.njk`

---

## 1. Buy the domain

Recommended registrar: **Cloudflare Registrar** (at-cost, no markup, and it lives in the same account you will host on). Namecheap or Gandi also fine.

Suggested name: **bamfordlab.org**. Buy it, then continue.

---

## 2. Put the code on GitHub

Create a new repository (for example `bamford-lab`) under your account or a lab org, then from this folder:

```bash
git init
git add -A
git commit -m "Bamford Lab website"
git branch -M main
git remote add origin https://github.com/YOUR-USER/bamford-lab.git
git push -u origin main
```

Note the `owner/repo` (e.g. `jsmccabe1/bamford-lab`); you need it in step 5.

---

## 3. Host on Cloudflare Pages

1. Sign in at <https://dash.cloudflare.com> and go to **Workers & Pages > Create > Pages > Connect to Git**.
2. Pick the repository you just pushed.
3. Build settings:
   - **Framework preset:** None (or Eleventy if offered)
   - **Build command:** `npm run build`
   - **Build output directory:** `_site`
4. **Save and Deploy.** In about a minute you get a live URL like `bamford-lab.pages.dev`.

Every `git push` to `main` now rebuilds and redeploys automatically.

### Point your domain at it
In the Pages project: **Custom domains > Set up a custom domain**, enter `bamfordlab.org` (and `www.bamfordlab.org`). If the domain is on Cloudflare, DNS is added for you and HTTPS is automatic. Done: the site is live and "proper".

Then set your live address in `src/_data/site.json` so social-media link previews work:

```json
"url": "https://bamfordlab.org",
```

Commit and push.

---

## 4. Create the GitHub OAuth app (for CMS login)

The CMS saves edits by committing to your repo, so it needs permission to log in as a GitHub user.

1. GitHub > **Settings > Developer settings > OAuth Apps > New OAuth App**.
2. Fill in:
   - **Application name:** Bamford Lab CMS
   - **Homepage URL:** `https://bamfordlab.org`
   - **Authorization callback URL:** `https://auth.bamfordlab.org/callback`  (the worker you make in step 5)
3. Register, then copy the **Client ID** and generate a **Client secret**. Keep them safe for the next step.

---

## 5. CMS login

**Sole technical admin (the current setup): nothing to deploy.** `src/admin/config.yml`
has no `base_url`, so <https://bamfordlab.org/admin/> shows a **Sign In with Token**
button. Create a GitHub personal access token (fine-grained: repository
`bamford-lab/bamford-lab-site`, **Contents: Read and write**; or a classic token with
the `repo` scope), paste it in, and you are editing. The token is kept in that
browser's local storage, so each browser needs it once.

Only do the OAuth-app-and-worker dance below if NON-TECHNICAL lab members need to log
in without handling tokens themselves.

<details>
<summary>Optional: auth worker for non-technical editors</summary>

## 5b. Deploy the auth worker and finish the CMS

Sveltia CMS needs a tiny auth handler. Use the ready-made one:

1. Clone and deploy the worker (needs the free `wrangler` CLI, `npm i -g wrangler`):
   ```bash
   git clone https://github.com/sveltia/sveltia-cms-auth.git
   cd sveltia-cms-auth
   wrangler deploy
   ```
2. In the Cloudflare dashboard, open that Worker > **Settings > Variables** and add (as encrypted secrets):
   - `GITHUB_CLIENT_ID` = the Client ID from step 4
   - `GITHUB_CLIENT_SECRET` = the Client secret from step 4
   - `ALLOWED_DOMAINS` = `bamfordlab.org`
3. Give the Worker a tidy route: add a custom domain/route `auth.bamfordlab.org` to it (Worker > Settings > Domains & Routes). This must match the callback URL from step 4.
4. Edit **`src/admin/config.yml`** (the two lines marked `<-- EDIT`):
   ```yaml
   backend:
     name: github
     repo: YOUR-USER/bamford-lab        # your repo
     branch: main
     base_url: https://auth.bamfordlab.org   # your worker domain
   ```
5. Commit and push. Now visit **`https://bamfordlab.org/admin/`**, click **Login with GitHub**, and you are in.

Anyone you add as a **collaborator on the GitHub repo** can then log in and edit.

</details>

---

## Editing workflow (share this with the lab)

1. Go to `https://bamfordlab.org/admin/` and log in with GitHub.
2. **People:** add yourself or edit your card (name, role, photo, project, funder, bio, "outside the lab"). Set a photo by dragging an image in.
3. **News:** click **New News item**, write a title, date, tag and a sentence or two.
4. Hit **Publish**. The site rebuilds and updates in about a minute.

No code, no HTML. Every change is saved as a normal file in the repo, so nothing is ever locked in.

---

## Alternative host

Netlify works the same way (build command `npm run build`, publish directory `_site`) if you ever prefer it. The CMS and content do not change.
