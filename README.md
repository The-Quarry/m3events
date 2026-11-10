# M3 Events website

Live at https://m3events.gg (GitHub Pages, served from the repo root).

## How the site is built

All page content lives in one file: `src/site.html`. Edit that file, then run:

    python3 build.py

This writes one real page per URL (`/`, `/donkey-drop-out/`, `/gu36/`, `/getting-here/`, `/volunteer/`, `/about/`, `/terms/`), plus `assets/site.css`, `assets/site.js`, `sitemap.xml`, `robots.txt` and `404.html`. Commit the generated files together with the change to `src/site.html`. Do not edit the generated files directly, as the next build overwrites them.

Page titles, descriptions, social preview images and structured data are set in the `PAGES` and `JSONLD` blocks at the top of `build.py`.

## Adding a page

1. Add a `<div id="page-NAME" class="page">...</div>` section to `src/site.html`.
2. Add an entry for it in `PAGES` in `build.py` (path, title, description, image).
3. Link to it with a normal `<a href="/path/">`.
4. Run `python3 build.py`.
