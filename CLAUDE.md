# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Guardrails (from the iGEM template — keep)

- Read **[README.md](README.md)** first — it covers the stack, where to edit,
  build/serve commands, and the iGEM asset rules (images via the uploads tool,
  videos from iGEM servers, no external CDNs).
- Don't change `LICENSE` or the footer's license notice + GitLab repository link
  (both required on every page for judging).
- `.gitlab-ci.yml` works as-is; change it only if you know what you're doing —
  any build/deploy issues that result are the team's responsibility.

## What this is

BRIDGE team wiki for iGEM 2026 — "BCAN-Responsive Injury-Directed Gating in Engineered T cells" (SynNotch-based neural repair). Built on the official iGEM frozen-flask wiki template: Flask + Frozen-Flask, no frontend framework, deployed to GitLab Pages on gitlab.igem.org by CI.

## Commands

- Create env & install: `python -m venv venv` → `venv\Scripts\activate` → `pip install -r dependencies.txt`
- Dev server: `python app.py` → http://127.0.0.1:8080 (`/` home, `/<page>` content pages); or double-click `preview.bat`
- Build the static site exactly like CI: `flask --app app.py freeze` → `public/`
- Verify the frozen build: `python -m http.server -d public 8321`, then curl pages + `static/*` for HTTP 200 and crawl for dead links
- Rebuild hero brain mesh after changing the source model: `python tools/merge_nodes.py models/高精度脑模型.obj static/brain-mesh.js 0.06` (optional flags: `shell`, `patch`)
- Extract source text from the project deck: parse `content/BRIDGE.pptx` with python-pptx

## Site architecture (iGEM template layout)

    |__ static/               -> static assets (CSS and JavaScript only)
        |__ tokens.css        -> the 16-color palette as CSS vars + fonts + reset
        |__ layout.css        -> nav/dropdowns, footer, cards, content-page scaffolding
        |__ bridge.js         -> scroll signal line, cursor glow, reveal, scroll-spy, counters
        |__ brain-mesh.js     -> const BRAIN_MESH = {verts, tris, hidden} (home hero only)
        |__ fonts.css + fonts/-> self-hosted woff2 (dev copy of fonts; see asset rules below)
        |__ mechanism-meshes/ -> OBJ meshes fetched by mechanism-demo.html
    |__ wiki/
        |__ layout.html       -> base template: head, signal-line, cursor-glow, menu/footer includes, bridge.js
        |__ menu.html         -> grouped dropdown nav; active state auto-computed from request.path
        |__ footer.html       -> footer incl. REQUIRED CC-by-4.0 license + gitlab.igem.org repo link
        |__ pages/            -> one Jinja template per page (22 pages)
    |__ app.py / dependencies.txt / .gitlab-ci.yml / LICENSE -> iGEM template infrastructure (LICENSE: do not modify)

22 pages in `wiki/pages/`: `home.html` (hero with 3D brain point-cloud) + `mechanism-demo.html` + 20 content pages in the iGEM-standard grouping:

- **Project**: description, design, engineering, results, parts, contribution, implementation
- **Wet Lab**: experiments, notebook, measurement, alternative-platform, safety
- **Dry Lab**: model, software
- **Engagement**: human-practices, education, entrepreneurship, inclusivity, sustainability
- **Team**: team

URLs are route-based (`/description`, not `/description.html`). **Never write `.html` links** — internal links must use `{{ url_for('pages', page='...') }}` (or `url_for('home')`); static assets use `{{ url_for('static', filename='...') }}`. Frozen-Flask makes them relative at build time.

Every content page extends `wiki/layout.html` and sets these blocks:

- `{% block title %}` — full `<title>` string (format: `Page — BRIDGE · iGEM 2026`)
- `{% block signal %}` — the site signature scroll line: `broken` (coral with a mid gap) on problem pages, `connected` (uninterrupted teal→cyan) on solution pages. Set deliberately per page. Home leaves it empty (default gradient).
- `{% block page_content %}` — `.page-hero` (hero-tag + h1 with `.grad` span + lede) → `.article-wrap` (`.article-body` with h2/h3 ids + sticky `.outline` aside whose links match those ids) → `.next-pages` (3 cross-page cards)
- `{% block head %}` / `{% block scripts %}` — only for pages with bespoke styles/scripts (home, mechanism-demo)

## Asset rules (iGEM, enforced at judging)

Everything the wiki loads must come from iGEM infrastructure — **no external CDNs**. Google Fonts were already replaced by self-hosted woff2 in `static/fonts/` (latin subsets of Space Grotesk + Noto Sans SC). Images/fonts currently in `static/img` + `static/fonts` are dev copies: before final submission upload them via the iGEM uploads tool and switch URLs to `static.igem.wiki`.

## Content sources

- `content/` (gitignored) — authoritative project material (BRIDGE.pptx is the master deck; 项目介绍.md, mechanism PNGs). Page copy comes from here, not invented. Mechanism figures live in `static/img/` with English filenames.
- `references/` (gitignored) — reference wikis incl. `csu-china-main` (the team's pristine copy of the iGEM template; layout/menu/footer patterns).
- Real numbers only: 4 core plasmids (a-BCAN-SynNotch, 5×UAS-Luc/GFP/BDNF), 5 experiment stages, 10+ HP events, 300+ participants, 80+ Kindle members.

## Hero brain-mesh pipeline

`models/高精度脑模型.obj` (20MB) → `tools/merge_nodes.py` (voxel-merge, shell filter, gap patch, buried-point marking) → `static/brain-mesh.js` (`const BRAIN_MESH = {verts, tris, hidden}`) → rendered by the inline canvas script in `wiki/pages/home.html` only.

## Conventions

- New content page: copy an existing one from `wiki/pages/` (e.g. `description.html`), change title/signal/hero/outline/next-cards — do not add page-specific CSS if `static/` already covers it.
- Never link `href="#"` — every menu and card link must resolve to a real route (verified: zero dead links site-wide).
- Menu active state is automatic (`request.path` in `menu.html`) — no per-page editing.
- Color semantics are load-bearing (`static/tokens.css`): `--signal-coral` ONLY for injury/alarm, `--research-amber` ONLY for repair/outcomes; navy/teal/cyan carry the main narrative.
- All scroll animation must respect the existing `prefers-reduced-motion` fallback in `static/layout.css`.
