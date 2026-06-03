#!/usr/bin/env python3
"""Static deployment hygiene checks for the Salvation Studios static site.

The site is deployed with Vercel cleanUrls=true, so this script audits the
production canonical route graph rather than just checking local file paths.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HOST = "https://www.salvationstudios.co.uk"
EXCLUDED_DIRS = {".git", ".superpowers", "node_modules"}
EXPECTED_TEL = "tel:+443334445508"
EXPECTED_EMAIL = "info@salvationstudios.co.uk"

INDEXABLE_HTML = {
    "index.html",
    "recording-studio-brighton.html",
    "equipment.html",
    "gallery.html",
    "testimonials.html",
    "contact.html",
    "rooms/live-room.html",
    "rooms/control-room.html",
    "rooms/writing-rooms.html",
    "rooms/the-bunker.html",
    "rooms/vocal-booth.html",
    "rooms/iso-booths.html",
    "services/recording.html",
    "services/mixing.html",
    "services/dry-hire.html",
    "services/lighting.html",
    "services/catering.html",
}

NOINDEX_HTML = {
    "concept-index.html",
    "concept-1-bunker.html",
    "concept-2-bloom.html",
    "concept-3-signal.html",
    "concept-4-void.html",
    "salvation-studios.html",
}

OLD_SITE_ROUTES = {
    "/about", "/amp-booth", "/amps", "/basses", "/book-online", "/catering",
    "/chillout-zone-kitchen-1", "/chillout-zone-kitchen-2", "/competition-1",
    "/contactus", "/control-room", "/control-room-as-a-writing-room",
    "/copy-of-enquiries-ad-landing-page", "/copy-of-signature-sessions-nick-brine",
    "/drums", "/dry-hire", "/enquiries", "/ep-giveaway", "/equipment",
    "/general-5-2", "/general-5-6", "/general-clean", "/guitars", "/home",
    "/isolation-booth-1", "/isolation-booth-2", "/jobs",
    "/join-our-roster-of-session-musicians", "/lighting", "/live-room",
    "/live-room-as-a-writing-room", "/live-video-giveaway", "/live-videos-2025",
    "/live-videos-ad", "/live-videos-reel", "/meet-the-team", "/mezzanine-room",
    "/microphones", "/outboard", "/phill-brown-competition",
    "/producers-engineers-mixing", "/recording-studio", "/salvation-art",
    "/salvation-black-friday-sale", "/salvation-studios", "/salvation-studios.html",
    "/signature-sessions-gavin-monaghan", "/signature-sessions-matt-glasbey",
    "/signature-sessions-nick-brine", "/signature-sessions-phill-brown",
    "/single-giveaway-2025", "/single-giveaway-2026", "/single-giveaway-2026-tiktok",
    "/studio-tour", "/subterranean-room", "/test-landing-page-video",
    "/video-showreel-email-1", "/video-showreel-email-2", "/vocal-booth",
    "/what-the-clients-say", "/white-rooms", "/writing-rooms",
}

# New public routes should not be redirected to themselves.
NEW_PUBLIC_ROUTES = {
    "/", "/recording-studio-brighton", "/equipment", "/gallery", "/testimonials", "/contact",
    "/rooms/live-room", "/rooms/control-room", "/rooms/writing-rooms", "/rooms/the-bunker", "/rooms/vocal-booth",
    "/rooms/iso-booths", "/services/recording", "/services/mixing", "/services/dry-hire",
    "/services/lighting", "/services/catering",
}

ASSET_EXTENSIONS = {
    ".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".svg", ".ico",
    ".xml", ".txt", ".json", ".woff", ".woff2", ".mp4", ".webm",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def clean_path_for(relative: str) -> str:
    if relative == "index.html":
        return "/"
    return f"/{relative[:-5]}/"


def clean_url_for(relative: str) -> str:
    return f"{PUBLIC_HOST}{clean_path_for(relative)}"


def route_to_file(path: str) -> str | None:
    clean = path.split("?", 1)[0].split("#", 1)[0]
    if clean == "/":
        return "index.html"
    if clean.endswith("/"):
        clean = clean[:-1]
    candidate = f"{clean.lstrip('/')}.html"
    return candidate if candidate in INDEXABLE_HTML or candidate in NOINDEX_HTML else None


def html_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.html")
        if not any(part in EXCLUDED_DIRS for part in p.parts)
    )


def sitemap_locs() -> set[str]:
    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {node.text.strip() for node in tree.findall(".//sm:loc", ns) if node.text}


def load_config() -> dict:
    return json.loads((ROOT / "vercel.json").read_text())


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.attrs: list[tuple[str, str, str]] = []
        self.ids: set[str] = set()
        self.json_ld: list[str] = []
        self._in_json_ld = False
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): v or "" for k, v in attrs}
        if "id" in attr_map:
            self.ids.add(attr_map["id"])
        for name in ("href", "src"):
            if name in attr_map:
                self.attrs.append((tag.lower(), name, attr_map[name]))
        if tag.lower() == "script" and attr_map.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._buf).strip())
            self._in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._buf.append(data)


def parse_html(path: Path) -> LinkParser:
    parser = LinkParser()
    parser.feed(path.read_text(errors="ignore"))
    return parser


def is_external(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.netloc != "www.salvationstudios.co.uk"


def local_path_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme in {"mailto", "tel", "data", "javascript"}:
        return None
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc != "www.salvationstudios.co.uk":
            return None
        return parsed.path or "/"
    return parsed.path or "/"


def asset_exists(path: str) -> bool:
    return (ROOT / path.lstrip("/")).exists()


def main() -> int:
    failures: list[str] = []
    files = {rel(p): p for p in html_files()}

    unknown = set(files) - INDEXABLE_HTML - NOINDEX_HTML
    if unknown:
        failures.append(f"unclassified html files: {sorted(unknown)}")

    config = load_config()
    redirects = config.get("redirects", [])
    redirect_sources = {r.get("source") for r in redirects}

    header_sources = {h.get("source") for h in config.get("headers", [])}
    if "/docs/:path*" not in header_sources:
        failures.append("docs directory is publicly deployable without noindex header")
    if "/concept-:path*" not in header_sources:
        failures.append("concept pages missing noindex header")

    for r in redirects:
        source = r.get("source")
        dest = r.get("destination")
        if source in NEW_PUBLIC_ROUTES and dest == source:
            failures.append(f"self-redirect on public route {source}")
        if isinstance(dest, str) and dest.startswith("/") and not dest.startswith("/$"):
            if route_to_file(dest.rstrip("/") + "/") is None and dest != "/":
                failures.append(f"redirect destination has no public file: {source} -> {dest}")

    for route in sorted(OLD_SITE_ROUTES):
        if route in NEW_PUBLIC_ROUTES or route == "/contact":
            continue
        if route not in redirect_sources:
            failures.append(f"missing old-site redirect for {route}")

    for relative, path in files.items():
        text = path.read_text(errors="ignore")
        parser = parse_html(path)

        if re.search(r"href=[\"']#[\"']", text):
            failures.append(f"placeholder href remains in {relative}")
        if ".superpowers" in text:
            failures.append(f"hidden .superpowers artifact referenced in {relative}")
        if re.search(r"\b(Book a Session|Reserve Now)\b", text):
            failures.append(f"booking-language overpromise remains in {relative}")
        if re.search(r"tel:[^\"']*\*", text):
            failures.append(f"masked tel link/text remains in {relative}")

        canonical = re.search(r"<link\s+rel=[\"']canonical[\"']\s+href=[\"']([^\"']+)[\"']", text, re.I)
        if relative in INDEXABLE_HTML:
            expected = clean_url_for(relative)
            if not canonical or canonical.group(1) != expected:
                failures.append(f"canonical mismatch in {relative}: expected {expected}")
        if relative in NOINDEX_HTML and not re.search(r"<meta\s+name=[\"']robots[\"']\s+content=[\"']noindex,\s*nofollow[\"']", text, re.I):
            failures.append(f"noindex meta missing from non-production page {relative}")

        for tag, attr, value in parser.attrs:
            if not value:
                continue
            if attr == "href" and value.startswith("tel:"):
                if value != EXPECTED_TEL:
                    failures.append(f"unexpected tel link in {relative}: {value}")
                continue
            if attr == "href" and value.startswith("mailto:"):
                if EXPECTED_EMAIL not in value:
                    failures.append(f"unexpected mailto in {relative}: {value}")
                continue
            if is_external(value):
                continue
            if value.startswith("#"):
                fragment = value[1:]
                if fragment and fragment not in parser.ids:
                    failures.append(f"missing same-page anchor target from {relative}: {value}")
                continue
            local = local_path_from_url(value)
            if local is None:
                continue
            parsed = urlparse(value)
            if value.startswith(('./', '../')) or re.search(r"(^|/)index\.html($|[#?])", value) or re.search(r"\.html($|[#?])", value):
                failures.append(f"non-clean internal {attr} in {relative}: {value}")
            if not value.startswith(("/", "http://", "https://", "#")):
                failures.append(f"non-root-relative local {attr} in {relative}: {value}")
            suffix = Path(parsed.path).suffix.lower()
            if suffix in ASSET_EXTENSIONS:
                if not asset_exists(parsed.path):
                    failures.append(f"missing asset from {relative}: {value}")
            elif attr == "href" and local.startswith("/"):
                target = route_to_file(local.rstrip("/") + "/")
                if target is None and local != "/":
                    failures.append(f"internal route does not resolve from {relative}: {value}")
                if parsed.fragment and target:
                    target_parser = parser if target == relative else parse_html(ROOT / target)
                    if parsed.fragment not in target_parser.ids:
                        failures.append(f"missing anchor target from {relative}: {value}")

        for raw in parser.json_ld:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                failures.append(f"invalid JSON-LD in {relative}: {exc}")
                continue
            graph = data.get("@graph", []) if isinstance(data, dict) else []
            nodes = graph if isinstance(graph, list) else [data]
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                if "AggregateRating" in json.dumps(node) or "aggregateRating" in node:
                    failures.append(f"unverified AggregateRating in {relative}")
                if "openingHours" in json.dumps(node):
                    failures.append(f"unverified opening hours in {relative}")
                if node.get("telephone") and node.get("telephone") != "+44 333 444 5508":
                    failures.append(f"unexpected schema telephone in {relative}: {node.get('telephone')}")

    locs = sitemap_locs()
    expected_locs = {clean_url_for(page) for page in INDEXABLE_HTML}
    if locs != expected_locs:
        failures.append(f"sitemap mismatch missing={sorted(expected_locs-locs)} extra={sorted(locs-expected_locs)}")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(
        f"PASS: {len(files)} html files audited; {len(locs)} sitemap routes aligned; "
        f"{len(OLD_SITE_ROUTES)} old routes accounted; clean URL crawl/schema/contact hygiene clean"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
