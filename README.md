# Team CSU-CHINA 2026 Wiki — BRIDGE

**BRIDGE: BCAN-Responsive Injury-Directed Gating in Engineered T cells** — a
SynNotch-based neural repair platform. Engineered T cells cross the blood-brain
barrier, sense the injury marker BCAN, and release the repair factor BDNF
exactly where neurons were lost.

This repository contains all coding assets that generate the team's wiki
(HTML, CSS, JavaScript, Python). It follows the official iGEM
frozen-flask wiki template.

Images, photos, icons and fonts **MUST** be stored on `static.igem.wiki` using
[the uploads tool](https://teams.igem.org/go/deliverables/wiki/uploads), and
videos **must** be embedded from [iGEM Video Universe](https://video.igem.org).
**Everything the wiki loads must be served from iGEM infrastructure** — no
external or third-party CDNs.

Images are served from `static.igem.wiki`; the self-hosted development webfonts
remain in `static/fonts/`. No Google Fonts or third-party CDN links are used.

For up-to-date requirements, resources, help and guidance, visit
[teams.igem.org/go/deliverables/wiki](https://teams.igem.org/go/deliverables/wiki).

## Getting started

You should probably only edit the files inside folders `static`, `wiki` and
`wiki > pages`.

1. Open the Web IDE
2. Make the changes on the files you wish:
    * For the menu, change the file [menu.html](wiki/menu.html)
    * For the layout, change the file [layout.html](wiki/layout.html)
    * For the footer, change the file [footer.html](wiki/footer.html)
    * For the pages, change the corresponding file in the folder
      [pages](wiki/pages)
3. Review the changes you made
4. Once you are done, save the changes by **committing** them to the *main
   branch* of the repository
5. An automated script will build, test and deploy your wiki, which should
   take less than 30 seconds.

## About this wiki

### Files

The static assets are in the `static` directory. The layout and templates are
in the `wiki` directory, and the pages live in the `wiki > pages` directory.
Unless you are an experienced and/or adventurous human, you probably shouldn't
change other files.

    |__ static/               -> static assets (CSS and JavaScript files only)
        |__ fonts.css         -> @font-face rules for the self-hosted fonts
        |__ fonts/            -> woff2 files (dev copy; move to static.igem.wiki)
        |__ mechanism-meshes/ -> OBJ meshes loaded by mechanism-demo.html
    |__ wiki/                 -> Main directory for the pages and layouts
        |__ footer.html       -> Footer that will appear in all the pages
        |__ layout.html       -> Main layout of your wiki. All the pages will follow its structure
        |__ menu.html         -> Menu that will appear in all the pages
        |__ pages/            -> Directory for all the pages
            |__ home.html     -> Landing page (hero + 3D brain point-cloud)
            |__ *.html        -> Content pages of the wiki
    |__ .gitignore            -> Tells GitLab which files/directories should not be uploaded to the repository
    |__ .gitlab-ci.yml        -> Automated flow for building, testing and deploying your website.
    |__ LICENSE               -> License CC-by-4.0, all wikis are required to have this license - DO NOT MODIFY
    |__ README.md             -> File containing the text you are reading right now
    |__ app.py                -> Python code managing your wiki
    |__ dependencies.txt      -> Software dependencies from the Python code

### Page map

The menu groups the pages following iGEM conventions:

* **Project**: description, design, engineering, results, parts, contribution, implementation
* **Wet Lab**: experiments, notebook, measurement, alternative-platform, safety
* **Dry Lab**: model, software
* **Engagement**: human-practices, education, entrepreneurship, inclusivity, sustainability
* **Team**: team (top level)

Every content page extends `wiki/layout.html` and fills these blocks:

* `{% block title %}` — the full `<title>` string
* `{% block signal %}` — `broken` on problem pages (coral, gap in the middle),
  `connected` on solution pages (uninterrupted teal → cyan)
* `{% block page_content %}` — hero, article body + sticky outline, next-page cards
* `{% block head %}` / `{% block scripts %}` — optional per-page styles and scripts
  (used by `home.html` and `mechanism-demo.html`)

The active menu state is computed automatically from `request.path` in
`wiki/menu.html` — no per-page editing needed.

### Technologies

* [GitLab Pages](https://docs.gitlab.com/ee/user/project/pages/)
* [Python](https://www.python.org): Programming language
* [Flask](https://palletsprojects.com/projects/flask): Python framework
* [Frozen-Flask](https://pypi.org/project/Frozen-Flask): Library that builds the wiki to be deployed as a static website
* Vanilla CSS/JS design system (`static/tokens.css`, `static/layout.css`, `static/bridge.js`)

### Building locally (advanced users)

#### Important

Ensure you are using Python `>=3.8` (Python 3.12 recommended) to avoid
compatibility issues. You can check your Python version by running
`python3 --version` in your terminal.

#### Install

```bash
git clone https://gitlab.igem.org/2026/csu-china.git
cd csu-china
python3 -m venv venv
. venv/bin/activate # on Linux, MacOS; or
. venv\Scripts\activate # on Windows
pip install -r dependencies.txt
```

#### Execute

```bash
python app.py
```

Then open http://127.0.0.1:8080 — the home page is `/`, content pages are
`/<page>` (e.g. `/description`).

#### Build the static site (what CI does)

```bash
flask --app app.py freeze
```

The frozen site is written to `public/` and can be previewed with any static
file server, e.g. `python -m http.server -d public 8321`.
