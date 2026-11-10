#!/usr/bin/env python3
"""Build the M3 Events site from src/site.html.

src/site.html holds every page in one file (this is the file to edit).
Running this script writes one real HTML file per page, plus shared CSS/JS,
sitemap.xml, robots.txt and 404.html, all in the repo root ready for GitHub Pages.

    python3 build.py

Commit the generated files together with the source change.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "site.html"
BASE = "https://m3events.gg"

# id in source -> output config
PAGES = {
    "home": {
        "path": "/",
        "title": "M3 Events | Guernsey Trail Running Events",
        "description": "Trail running events in Guernsey: the GU36 round-island ultra and the Donkey Drop Out backyard ultra. Small island, serious trails, founded by runners for runners.",
        "image": "/images/cliffs.jpg",
        "nav": "nav-home",
    },
    "ddo": {
        "path": "/donkey-drop-out/",
        "title": "Donkey Drop Out Backyard Ultra, Guernsey | M3 Events",
        "description": "Donkey Drop Out is Guernsey's only backyard ultra: one loop of about 4 miles every hour until only one runner remains. August 2027.",
        "image": "/images/ddo-hero.jpg",
        "nav": "nav-home",
        "maps": True,
    },
    "gu36": {
        "path": "/gu36/",
        "title": "GU36 Round Island Ultra, Guernsey | M3 Events",
        "description": "GU36 is a fully marked 36 mile (58km) ultra around the entire island of Guernsey on 16 May 2027, starting and finishing in St Peter Port.",
        "image": "/images/gu36-hero.jpg",
        "nav": "nav-home",
        "maps": True,
    },
    "getting-here": {
        "path": "/getting-here/",
        "title": "Getting to Guernsey for a Race | M3 Events",
        "description": "How to get to Guernsey for an M3 Events race: flights, ferries and places to stay on the island.",
        "image": "/images/cliffs.jpg",
        "nav": "nav-gh",
    },
    "volunteers": {
        "path": "/volunteer/",
        "title": "Volunteer at a Guernsey Trail Race | M3 Events",
        "description": "Volunteer at an M3 Events race in Guernsey. Every volunteer gets a free coffee, and helpers for a full event earn free race entry.",
        "image": "/images/cliffs.jpg",
        "nav": "nav-vol",
    },
    "about": {
        "path": "/about/",
        "title": "About M3 Events | Guernsey Trail Running",
        "description": "M3 Events was founded by three Guernsey runners who wanted to share the island's cliffs, valleys and coastal paths with the wider running community.",
        "image": "/images/cliffs.jpg",
        "nav": "nav-about",
    },
    "tc": {
        "path": "/terms/",
        "title": "Terms and Conditions | M3 Events",
        "description": "Terms and conditions for entering M3 Events races in Guernsey.",
        "image": "/images/cliffs.jpg",
        "nav": None,
    },
}

ORG = {
    "@type": "Organization",
    "name": "M3 Events",
    "url": BASE + "/",
    "logo": BASE + "/images/logo-wave-green.svg",
    "sameAs": ["https://www.facebook.com/m3running"],
}

JSONLD = {
    "home": [
        {"@context": "https://schema.org", **ORG},
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "M3 Events",
            "url": BASE + "/",
        },
    ],
    "gu36": [
        {
            "@context": "https://schema.org",
            "@type": "SportsEvent",
            "name": "GU36",
            "description": PAGES["gu36"]["description"],
            "startDate": "2027-05-16",
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "location": {
                "@type": "Place",
                "name": "St Peter Port, Guernsey",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "St Peter Port",
                    "addressCountry": "GG",
                },
            },
            "image": [BASE + "/images/gu36-hero.jpg"],
            "url": BASE + "/gu36/",
            "organizer": {"@type": "Organization", "name": "M3 Events", "url": BASE + "/"},
        }
    ],
}

PAGE_START = re.compile(r'<div id="page-([\w-]+)" class="page">')


def short_hash(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def split_source(src):
    style = re.search(r"<style>(.*?)</style>", src, re.S).group(1).strip("\n")
    nav = re.search(r'<nav class="nav">.*?</nav>', src, re.S).group(0)
    script_start = src.rindex("<script>")
    script = src[script_start + len("<script>"): src.rindex("</script>")].strip("\n")

    starts = [(m.group(1), m.start()) for m in PAGE_START.finditer(src)]
    pages = {}
    for i, (pid, pos) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else script_start
        chunk = src[pos:end].rstrip()
        # drop the section banner comment that precedes the next page
        chunk = re.sub(r"\s*<!--[^>]*-->\s*$", "", chunk)
        pages[pid] = chunk
    missing = set(PAGES) - set(pages)
    assert not missing, f"pages missing from source: {missing}"
    return style, nav, pages, script


def head(cfg, css_href, js_needs_leaflet, jsonld, noindex=False):
    url = BASE + cfg["path"]
    title = cfg["title"]
    desc = cfg["description"]
    img = BASE + cfg["image"]
    parts = [
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>{title}</title>",
        f'<meta name="description" content="{desc}">',
    ]
    if noindex:
        parts.append('<meta name="robots" content="noindex">')
    else:
        parts.append(f'<link rel="canonical" href="{url}">')
        parts += [
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="M3 Events">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{desc}">',
            f'<meta property="og:url" content="{url}">',
            f'<meta property="og:image" content="{img}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{title}">',
            f'<meta name="twitter:description" content="{desc}">',
            f'<meta name="twitter:image" content="{img}">',
        ]
    parts.append('<link rel="icon" href="/images/logo-wave-green.svg" type="image/svg+xml">')
    if js_needs_leaflet:
        parts += [
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">',
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>',
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-gpx/1.7.0/gpx.min.js"></script>',
        ]
    parts += [
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Barlow:ital,wght@0,300;0,400;0,600;1,300&display=swap" rel="stylesheet">',
        f'<link rel="stylesheet" href="{css_href}">',
    ]
    for block in jsonld:
        parts.append('<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False) + "</script>")
    return "\n".join(parts)


def render(cfg, pid, nav, chunk, css_href, js_href, noindex=False, activate=True):
    if activate:
        chunk = chunk.replace('class="page"', 'class="page active"', 1)
    page_nav = nav
    if cfg.get("nav"):
        page_nav = nav.replace(f'id="{cfg["nav"]}"', f'id="{cfg["nav"]}" class="active"', 1)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en-GB">\n<head>\n'
        + head(cfg, css_href, cfg.get("maps", False), JSONLD.get(pid, []), noindex)
        + "\n</head>\n<body>\n\n"
        + page_nav
        + "\n\n"
        + chunk
        + f'\n\n<script src="{js_href}"></script>\n</body>\n</html>\n'
    )


def write(path, text):
    path = ROOT / path.lstrip("/")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    src = SRC.read_text(encoding="utf-8")
    style, nav, pages, script = split_source(src)

    write("assets/site.css", style + "\n")
    write("assets/site.js", script + "\n")
    css_href = f"/assets/site.css?v={short_hash(style)}"
    js_href = f"/assets/site.js?v={short_hash(script)}"

    for pid, cfg in PAGES.items():
        out = cfg["path"].lstrip("/") + "index.html"
        write(out, render(cfg, pid, nav, pages[pid], css_href, js_href))

    not_found = (
        '<div id="page-404" class="page">\n'
        '  <div class="ev-hero" style="background:#0e1228;border-bottom:4px solid var(--m3-green)">\n'
        '    <div class="ev-eyebrow" style="color:var(--m3-green)">M3 Events · Guernsey</div>\n'
        '    <h1 class="ev-title">Page not<br><span style="color:var(--m3-green)">found.</span></h1>\n'
        '    <p class="ev-subtitle">That page has moved or never existed. Head back and find your next race.</p>\n'
        '    <a class="btn btn-coral" href="/">View all events</a>\n'
        "  </div>\n</div>"
    )
    nf_cfg = {
        "path": "/404.html",
        "title": "Page not found | M3 Events",
        "description": "Page not found.",
        "image": "/images/cliffs.jpg",
        "nav": None,
    }
    nf_chunk = not_found.replace('class="page"', 'class="page active"', 1)
    write("404.html", render(nf_cfg, "404", nav, nf_chunk, css_href, js_href, noindex=True, activate=False))

    urls = "\n".join(f"  <url><loc>{BASE}{c['path']}</loc></url>" for c in PAGES.values())
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n",
    )
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /src/\n\nSitemap: {BASE}/sitemap.xml\n")
    print("Built", len(PAGES), "pages + 404, sitemap, robots, assets")


if __name__ == "__main__":
    main()
