#!/usr/bin/env python3
"""Build the local YouTube archive, homepage cards, sitemap and robots.txt."""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "youtube-videos.json"
GUIDE_DIR = ROOT / "guide"
MANIFEST = GUIDE_DIR / ".generated-video-pages.json"
BASE_URL = "https://www.manganogregorio.it"
HOME_START, HOME_END = "<!-- GUIDES_HOME_START -->", "<!-- GUIDES_HOME_END -->"
MONTHS = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def truncate(value: str, limit: int = 140) -> str:
    value = clean_text(value)
    return value if len(value) <= limit else value[:limit - 1].rsplit(" ", 1)[0] + "…"


def date_label(value: str) -> str:
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return f"{date.day} {MONTHS[date.month - 1]} {date.year}"
    except ValueError:
        return "Data non disponibile"


def thumbnail(video: dict) -> str:
    thumbs = video.get("thumbnails", {})
    for size in ("maxres", "standard", "high", "medium", "default"):
        if thumbs.get(size, {}).get("url"):
            return thumbs[size]["url"]
    return f"https://i.ytimg.com/vi/{quote(video['videoId'])}/hqdefault.jpg"


def mobile_thumbnail(video: dict) -> str:
    """Use YouTube's broadly available 480px thumbnail on small screens."""
    return f"https://i.ytimg.com/vi/{quote(video['videoId'])}/hqdefault.jpg"


def font_links() -> str:
    return '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap">'''


def profile_image(root: str, size: int) -> str:
    return f'<img src="{root}assets/branding/gregorio-profilo-small.webp" width="{size}" height="{size}" alt="Gregorio Mangano" decoding="async">'


def page_header(title: str, description: str, canonical_path: str, image: str, schema: dict) -> str:
    root = "../"
    schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" type="image/png" href="{root}assets/logo.png">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(truncate(description))}">
<link rel="canonical" href="{BASE_URL}{canonical_path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(truncate(description))}">
<meta property="og:url" content="{BASE_URL}{canonical_path}">
<meta property="og:image" content="{html.escape(image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(truncate(description))}">
<meta name="twitter:image" content="{html.escape(image)}">
<script type="application/ld+json">{schema_json}</script>
{font_links()}
<link rel="stylesheet" href="{root}style.css?rev=9">
<link rel="stylesheet" href="guide.css">
</head>
<body class="guide-page">
<header class="site-header"><a class="brand" href="{root}index.html">{profile_image(root, 36)}<span>Gregorio<em>Mangano</em></span></a><nav class="main-nav" aria-label="Navigazione principale"><a href="{root}index.html#chi-sono">Chi sono</a><a href="{root}index.html#servizi">Servizi</a><span class="projects-menu"><a href="{root}index.html#progetti">Progetti</a><details class="projects-dropdown"><summary aria-label="Apri elenco progetti"></summary><div><a href="{root}mg-avviatore.html">M.G Avviatore</a><a href="{root}mg-windows-toolbox.html">M.G Windows Toolbox</a><a href="{root}mg-linux-toolbox.html">M.G Linux Toolbox</a></div></details></span><a href="{root}guide/">Guide</a><a href="{root}index.html#contatti">Contatti</a><a class="nav-donation" href="{root}donazioni.html">♡ Donazioni</a></nav><a class="button button-dark header-cta" href="{root}index.html#contatti">Parliamone ↗</a><button class="menu-toggle" type="button" aria-label="Apri menu" aria-expanded="false" aria-controls="mobile-menu">☰</button><nav id="mobile-menu" class="mobile-menu" aria-label="Menu mobile" hidden><a href="{root}index.html#chi-sono">Chi sono</a><a href="{root}index.html#servizi">Servizi</a><details><summary>Progetti</summary><a href="{root}index.html#progetti">Tutti i progetti</a><a href="{root}mg-avviatore.html">M.G Avviatore</a><a href="{root}mg-windows-toolbox.html">M.G Windows Toolbox</a><a href="{root}mg-linux-toolbox.html">M.G Linux Toolbox</a></details><a href="{root}guide/">Guide</a><a href="{root}index.html#contatti">Contatti</a><a class="nav-donation" href="{root}donazioni.html">♡ Donazioni</a><a class="button button-dark" href="{root}index.html#contatti">Parliamone ↗</a></nav></header>'''


def page_footer() -> str:
    root = "../"
    return f'''<footer class="site-footer rich-footer"><div class="wrap footer-grid"><div class="footer-brand"><a class="brand" href="{root}index.html">{profile_image(root, 42)}<span>Gregorio<em>Mangano</em></span></a><p>Tecnologia spiegata con parole chiare.</p></div><nav><b>Esplora</b><a href="{root}index.html#chi-sono">Chi sono</a><a href="{root}guide/">Guide</a><a href="{root}index.html#contatti">Contatti</a></nav><nav><b>Progetti</b><a href="{root}mg-avviatore.html">M.G Avviatore</a><a href="{root}mg-windows-toolbox.html">M.G Windows Toolbox</a><a href="{root}mg-linux-toolbox.html">M.G Linux Toolbox</a></nav><nav><b>Seguimi</b><a href="https://www.youtube.com/@GregorioMangano" target="_blank" rel="noopener noreferrer">YouTube</a><a href="https://github.com/gregoriomangano" target="_blank" rel="noopener noreferrer">GitHub</a><a href="{root}donazioni.html">♥ Donazioni</a></nav></div><div class="wrap footer-bottom">© 2026 MANGANO GREGORIO</div></footer><script src="{root}site.js"></script></body></html>'''


def card(video: dict) -> str:
    description = card_description(video.get("description") or video["title"])
    return f'''<article class="guide-card" data-guide-card data-category="{html.escape(video.get('category', 'Altro'))}"><a href="{html.escape(video['url'])}" target="_blank" rel="noopener noreferrer" aria-label="Guarda su YouTube: {html.escape(video['title'])}"><picture><source media="(max-width: 620px)" srcset="{html.escape(mobile_thumbnail(video))}"><img src="{html.escape(thumbnail(video))}" width="1280" height="720" alt="Thumbnail del video {html.escape(video['title'])}" loading="lazy" decoding="async"></picture><div class="guide-card-body"><p class="guide-card-meta">{html.escape(video.get('category', 'Altro'))} · {html.escape(date_label(video.get('publishedAt', '')))}</p><h2>{html.escape(video['title'])}</h2><p>{html.escape(truncate(description, 190))}</p><span>Guarda il video ↗</span></div></a></article>'''


def card_description(value: str) -> str:
    """Keep YouTube text, removing only obvious clutter before showing an excerpt."""
    lines = []
    for raw_line in value.splitlines():
        line = clean_text(raw_line)
        if not line or re.fullmatch(r"https?://\S+", line):
            continue
        if re.match(r"^(iscriviti|seguimi|supporta il canale|link utili|sito ufficiale)\b", line, re.I):
            continue
        lines.append(line)
    text = clean_text(" ".join(lines))
    text = re.sub(r"(?:[🌐👉]\s*)?(?:sito ufficiale:\s*)?https?://\S+", "", text, flags=re.I)
    text = clean_text(text)
    text = re.sub(r"(?:[\U0001F300-\U0001FAFF]\s*){2,}", "", text)
    return text or clean_text(value)


def archive_page(videos: list[dict]) -> str:
    path = "/guide/"
    title = "Guide Windows, Linux e IA | Gregorio Mangano"
    description = "Guide, prove e video pratici su Windows, Linux, intelligenza artificiale, software e strumenti utili spiegati da Gregorio Mangano."
    schema = {"@context": "https://schema.org", "@graph": [{"@type": "WebPage", "name": "Guide, prove e tutorial su Windows, Linux e Intelligenza Artificiale", "url": BASE_URL + path, "isPartOf": {"@type": "WebSite", "name": "Gregorio Mangano", "url": BASE_URL + "/"}}, {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"}, {"@type": "ListItem", "position": 2, "name": "Guide", "item": BASE_URL + path}]}]}
    cards = "".join(card(video) for video in videos)
    empty = "<p class=\"guide-empty\">L'archivio apparirà qui dopo il primo aggiornamento dai video pubblici del canale.</p>" if not videos else ""
    filters = "".join(f"<button type=\"button\" data-guide-filter=\"{category}\">{category}</button>" for category in ("Tutte", "Windows", "Linux", "Intelligenza artificiale", "Altro"))
    return page_header(title, description, path, "https://www.manganogregorio.it/assets/youtube-banner.jpg", schema) + f'''<main><section class="guide-wrap guide-hero"><p class="guide-kicker">Archivio del canale</p><h1>Guide, prove e tutorial<span class="guide-h1-topics"> su Windows, Linux e Intelligenza Artificiale</span></h1><p>Video, prove e guide pratiche su Windows, Linux, intelligenza artificiale, software e strumenti che utilizzo davvero.</p></section><section class="guide-wrap guide-archive"><div class="guide-toolbar" aria-label="Filtra i video">{filters}</div>{empty}<div class="guide-grid">{cards}</div><button class="guide-more" type="button" hidden>Carica altri video</button></section></main>''' + page_footer().replace("</body>", "<script src=\"guide.js\"></script></body>")


def home_section(videos: list[dict]) -> str:
    cards = "".join(card(video) for video in videos[:3])
    empty = "<p class=\"home-guides-empty\">Le ultime guide del canale compariranno qui dopo il primo aggiornamento automatico.</p>" if not videos else ""
    return f'''{HOME_START}<section class="home-guides wrap" aria-labelledby="ultimi-video"><div class="home-guides-heading"><p class="home-kicker">Dal canale YouTube</p><h2 id="ultimi-video">Ultimi video</h2><p>Guide e prove appena pubblicate, raccolte qui senza doverle cercare una per una.</p></div>{empty}<div class="home-guide-grid">{cards}</div><a class="button button-dark" href="guide/">Tutte le guide ↗</a></section>{HOME_END}'''


def write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def replace_home_section(section: str) -> bool:
    index = ROOT / "index.html"
    content = index.read_text(encoding="utf-8")
    if HOME_START not in content or HOME_END not in content:
        raise RuntimeError("Mancano i marcatori della sezione Guide nella homepage.")
    start, rest = content.split(HOME_START, 1)
    _, end = rest.split(HOME_END, 1)
    return write_if_changed(index, start + section + end)


def previous_lastmod(path: str) -> str | None:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        return None
    match = re.search(rf"<loc>{re.escape(BASE_URL + path)}</loc>(?:<lastmod>([^<]+)</lastmod>)?", sitemap.read_text(encoding="utf-8"))
    return match.group(1) if match and match.group(1) else None


def write_sitemap(guide_changed: bool, home_changed: bool) -> None:
    today = datetime.now(timezone.utc).date().isoformat()
    guide_lastmod = today if guide_changed else previous_lastmod("/guide/")
    home_lastmod = today if home_changed else previous_lastmod("/")
    paths = ["/", "/mg-avviatore.html", "/mg-windows-toolbox.html", "/mg-linux-toolbox.html", "/donazioni.html", "/guide/"]
    items = []
    for path in paths:
        lastmod = home_lastmod if path == "/" else guide_lastmod if path == "/guide/" else None
        suffix = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        items.append(f"  <url><loc>{xml_escape(BASE_URL + path)}</loc>{suffix}</url>")
    items_xml = "\n".join(items)
    write_if_changed(ROOT / "sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items_xml}\n</urlset>\n')
    write_if_changed(ROOT / "robots.txt", "User-agent: *\nAllow: /\n\nSitemap: https://www.manganogregorio.it/sitemap.xml\n")


def remove_generated_video_pages() -> int:
    previous = set(json.loads(MANIFEST.read_text(encoding="utf-8"))) if MANIFEST.exists() else set()
    removed = 0
    for slug in previous:
        target = GUIDE_DIR / slug
        if target.is_dir():
            shutil.rmtree(target)
            removed += 1
    if MANIFEST.exists():
        MANIFEST.unlink()
    return removed


def validate(videos: list[dict]) -> None:
    content = (GUIDE_DIR / "index.html").read_text(encoding="utf-8")
    if content.count("<h1") != 1:
        raise RuntimeError("Gerarchia H1 non valida in guide/index.html")
    if re.search(r'<article class="guide-card"[^>]*><a href="(?!https://www\.youtube\.com/watch\?v=)', content):
        raise RuntimeError("Le card Guide non devono puntare a pagine interne.")
    if "localhost" in (ROOT / "sitemap.xml").read_text(encoding="utf-8"):
        raise RuntimeError("La sitemap non deve contenere localhost.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="genera e verifica l'output")
    parser.parse_args()
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    videos = data.get("videos", [])
    videos.sort(key=lambda video: video.get("publishedAt", ""), reverse=True)
    GUIDE_DIR.mkdir(exist_ok=True)
    removed = remove_generated_video_pages()
    guide_changed = write_if_changed(GUIDE_DIR / "index.html", archive_page(videos))
    home_changed = replace_home_section(home_section(videos))
    write_sitemap(guide_changed, home_changed)
    validate(videos)
    print(f"Generato l'archivio Guide con {len(videos)} video; rimosse {removed} pagine video automatiche.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
