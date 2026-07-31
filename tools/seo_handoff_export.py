#!/usr/bin/env python3
"""Export a portable Salvation Studios SEO/copy handoff pack.

This is designed for the coworker/Seb frontend pivot: keep the current static
site as a source of SEO, copy and schema truth, then generate a compact route
manifest that can be ported into another frontend without rereading every page.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from html.parser import HTMLParser
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HOST = "https://www.salvationstudios.co.uk"
INDEXABLE = {
    "index.html",
    "recording-studio-brighton.html",
    "equipment.html",
    "gallery.html",
    "testimonials.html",
    "spaces.html",
    "services.html",
    "rooms/main-studio.html",
    "rooms/live-room.html",
    "rooms/control-room.html",
    "rooms/writing-rooms.html",
    "rooms/the-bunker.html",
    "services/recording.html",
    "services/mixing.html",
    "services/mastering.html",
    "services/live-videos.html",
    "services/signature-sessions.html",
    "services/grassroots.html",
    "services/accommodation-hospitality.html",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self._capture_heading: str | None = None
        self._heading_depth = 0
        self._heading_chunks: list[str] = []
        self.headings: dict[str, list[str]] = {"h1": [], "h2": [], "h3": []}
        self.meta: dict[str, str] = {}
        self.canonical = ""
        self.og_image = ""
        self.links: list[str] = []
        self.jsonld_raw: list[str] = []
        self._in_jsonld = False
        self._jsonld_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        elif tag in self.headings:
            self._capture_heading = tag
            self._heading_depth = 1
            self._heading_chunks = []
        elif self._capture_heading:
            self._heading_depth += 1
        elif tag == "meta":
            key = attrs_d.get("name") or attrs_d.get("property")
            if key:
                self.meta[key] = attrs_d.get("content", "")
                if key == "og:image":
                    self.og_image = attrs_d.get("content", "")
        elif tag == "link" and attrs_d.get("rel") == "canonical":
            self.canonical = attrs_d.get("href", "")
        elif tag == "a" and attrs_d.get("href"):
            self.links.append(attrs_d["href"])
        elif tag == "script" and attrs_d.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_chunks = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif self._capture_heading:
            self._heading_depth -= 1
            if self._heading_depth <= 0:
                heading = " ".join(" ".join(self._heading_chunks).split())
                if heading:
                    self.headings[self._capture_heading].append(heading)
                self._capture_heading = None
                self._heading_chunks = []
                self._heading_depth = 0
        elif tag == "script" and self._in_jsonld:
            raw = "".join(self._jsonld_chunks).strip()
            if raw:
                self.jsonld_raw.append(raw)
            self._in_jsonld = False
            self._jsonld_chunks = []

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title += text
        if self._capture_heading:
            self._heading_chunks.append(text)
        if self._in_jsonld:
            self._jsonld_chunks.append(data)


def route_for_file(rel: str) -> str:
    if rel == "index.html":
        return "/"
    if rel.endswith(".html"):
        rel = rel[:-5]
    return "/" + rel + "/"


def load_sitemap(root: Path) -> set[str]:
    sitemap = root / "sitemap.xml"
    if not sitemap.exists():
        return set()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(sitemap)
    urls = set()
    for loc in tree.findall(".//sm:loc", ns):
        if loc.text:
            urls.add(urlparse(loc.text).path or "/")
    return urls


def schema_types(raw_items: list[str]) -> list[str]:
    found: list[str] = []
    for raw in raw_items:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            found.append("INVALID_JSON_LD")
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            t = node.get("@type")
            if isinstance(t, list):
                found.extend(str(x) for x in t)
            elif t:
                found.append(str(t))
    return sorted(dict.fromkeys(found))


def internal_links(links: list[str]) -> list[str]:
    clean = []
    for href in links:
        if href.startswith(("mailto:", "tel:", "#", "javascript:", "data:")):
            continue
        parsed = urlparse(href)
        if parsed.netloc and parsed.netloc not in {"www.salvationstudios.co.uk", "salvationstudios.co.uk"}:
            continue
        path = parsed.path or "/"
        if not path.startswith("/"):
            path = "/" + path
        clean.append(path)
    return sorted(dict.fromkeys(clean))


@dataclass
class PageRecord:
    file: str
    route: str
    title: str
    meta_description: str
    canonical: str
    h1: list[str]
    h2: list[str]
    h3: list[str]
    og_image: str
    schema_types: list[str]
    internal_links: list[str]
    checks: list[str]


def analyse_page(path: Path, sitemap_routes: set[str]) -> PageRecord:
    rel = path.relative_to(ROOT).as_posix()
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    route = route_for_file(rel)
    expected_canonical = PUBLIC_HOST + route
    checks: list[str] = []
    desc = parser.meta.get("description", "")
    if not parser.title:
        checks.append("missing title")
    if len(desc) < 80:
        checks.append("meta description short/missing")
    if len(desc) > 165:
        checks.append("meta description long")
    if parser.canonical != expected_canonical:
        checks.append(f"canonical mismatch: expected {expected_canonical}")
    if len(parser.headings["h1"]) != 1:
        checks.append(f"expected exactly 1 H1, found {len(parser.headings['h1'])}")
    if route not in sitemap_routes:
        checks.append("route missing from sitemap")
    types = schema_types(parser.jsonld_raw)
    if "WebPage" not in types:
        checks.append("schema missing WebPage")
    return PageRecord(
        file=rel,
        route=route,
        title=parser.title,
        meta_description=desc,
        canonical=parser.canonical,
        h1=parser.headings["h1"],
        h2=parser.headings["h2"][:12],
        h3=parser.headings["h3"][:16],
        og_image=parser.og_image,
        schema_types=types,
        internal_links=internal_links(parser.links),
        checks=checks,
    )


def markdown_report(records: list[PageRecord], generated_at: str) -> str:
    failing = [r for r in records if r.checks]
    lines: list[str] = []
    lines.append("# Salvation Studios — Seb/coworker SEO handoff manifest")
    lines.append("")
    lines.append(f"Generated: {generated_at}")
    lines.append(f"Source repo: `{ROOT}`")
    lines.append(f"Public host assumption: `{PUBLIC_HOST}`")
    lines.append("")
    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"- Indexable pages exported: {len(records)}")
    lines.append(f"- Pages with export-time checks to review: {len(failing)}")
    lines.append("- Use this as the route-by-route copy/SEO/schema source when porting Hermes/SouthernLoop work into Seb's canonical frontend.")
    lines.append("- Do not invent missing client facts; preserve explicit source-backed wording, especially contact details, location, equipment and room claims.")
    lines.append("")
    if failing:
        lines.append("## Checks to review before port")
        lines.append("")
        for r in failing:
            lines.append(f"- `{r.route}` — " + "; ".join(r.checks))
        lines.append("")
    else:
        lines.append("## Checks")
        lines.append("")
        lines.append("All exported pages passed the lightweight handoff checks: title present, 80–165 char description, canonical route, one H1, sitemap inclusion and WebPage schema.")
        lines.append("")
    lines.append("## Port order")
    lines.append("")
    lines.append("1. Home `/` — brand proposition, primary internal links, global LocalBusiness/WebSite schema.")
    lines.append("2. `/recording-studio-brighton/` — main commercial SEO landing page for the #1 Google goal.")
    lines.append("3. `/#home-enquiry` — structured enquiry section and GBP/contact details.")
    lines.append("4. Room pages: main studio, live room, control room, writing rooms and the Bunker.")
    lines.append("5. Service pages: recording, mixing, mastering, live videos, signature sessions, giveaways/offers, accommodation/hospitality.")
    lines.append("6. Equipment, gallery, testimonials and spaces pages.")
    lines.append("")
    lines.append("## Route manifest")
    lines.append("")
    for r in sorted(records, key=lambda x: (x.route != "/", x.route)):
        lines.append(f"### {r.route}")
        lines.append("")
        lines.append(f"- Source file: `{r.file}`")
        lines.append(f"- Title: {r.title}")
        lines.append(f"- Meta description: {r.meta_description}")
        lines.append(f"- Canonical: {r.canonical}")
        if r.h1:
            lines.append(f"- H1: {r.h1[0]}")
        if r.og_image:
            lines.append(f"- OG image: `{r.og_image}`")
        lines.append("- Schema types: " + (", ".join(r.schema_types) if r.schema_types else "none detected"))
        if r.h2:
            lines.append("- Main H2s:")
            for h in r.h2[:8]:
                lines.append(f"  - {h}")
        key_links = [x for x in r.internal_links if x != r.route][:12]
        if key_links:
            lines.append("- Internal links to preserve:")
            for link in key_links:
                lines.append(f"  - `{link}`")
        if r.checks:
            lines.append("- Review flags: " + "; ".join(r.checks))
        lines.append("")
    lines.append("## Seb handoff implementation checklist")
    lines.append("")
    lines.append("- Copy each page's `<title>`, meta description, canonical, OG/Twitter fields and JSON-LD into the canonical frontend route metadata layer.")
    lines.append("- Preserve clean URLs with trailing slash canonical targets and update `sitemap.xml` / `robots.txt` after porting.")
    lines.append("- Keep old Squarespace redirects mapped to the nearest equivalent route; do not remove redirect coverage just because the visual frontend changes.")
    lines.append("- Keep contact CTAs consistent: `info@salvationstudios.co.uk`, `+44 333 444 5508`, GBP link, and structured enquiry fields.")
    lines.append("- Re-run Seb frontend's build plus a crawl/hygiene check after metadata is ported.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--generated-at", default="unspecified")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    sitemap_routes = load_sitemap(ROOT)
    records = []
    for rel in sorted(INDEXABLE):
        path = ROOT / rel
        if path.exists():
            records.append(analyse_page(path, sitemap_routes))
    data = {
        "generated_at": args.generated_at,
        "source_repo": str(ROOT),
        "public_host": PUBLIC_HOST,
        "page_count": len(records),
        "pages_with_review_flags": sum(1 for r in records if r.checks),
        "pages": [asdict(r) for r in records],
    }
    (args.out_dir / "seo-handoff-manifest.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.out_dir / "seo-handoff-manifest.md").write_text(markdown_report(records, args.generated_at), encoding="utf-8")
    print(f"exported {len(records)} pages to {args.out_dir}")
    if data["pages_with_review_flags"]:
        print(f"review flags: {data['pages_with_review_flags']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
