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
TEST_HOST = "salvation-studios-mockups-three.vercel.app"
EXCLUDED_DIRS = {".git", ".superpowers", ".vercel", "__pycache__", "node_modules"}
EXPECTED_TEL = "tel:+443334445508"
EXPECTED_EMAIL = "info@salvationstudios.co.uk"

INDEXABLE_HTML = {
    "index.html",
    "about.html",
    "our-engineers.html",
    "privacy.html",
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

NOINDEX_HTML = {
    "concept-index.html",
    "concept-1-bunker.html",
    "concept-2-bloom.html",
    "concept-3-signal.html",
    "concept-4-void.html",
    "salvation-studios.html",
    "rooms/vocal-booth.html",
    "rooms/iso-booths.html",
    "live-video-sessions.html",
}

AD_NOINDEX_HTML = {
    "enquire.html",
}

OLD_SITE_ROUTES = {
    "/amp-booth", "/amps", "/basses", "/book-online", "/catering",
    "/chillout-zone-kitchen-1", "/chillout-zone-kitchen-2", "/competition-1",
    "/contact", "/contactus", "/control-room", "/control-room-as-a-writing-room",
    "/copy-of-enquiries-ad-landing-page", "/copy-of-signature-sessions-nick-brine",
    "/drums", "/dry-hire", "/enquiries", "/ep-giveaway", "/equipment", "/giveaways-offers",
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
    "/services/giveaways-offers", "/studio-tour", "/subterranean-room", "/test-landing-page-video",
    "/video-showreel-email-1", "/video-showreel-email-2", "/vocal-booth",
    "/what-the-clients-say", "/white-rooms", "/writing-rooms",
}

# New public routes should not be redirected to themselves.
NEW_PUBLIC_ROUTES = {
    "/", "/about", "/our-engineers", "/privacy", "/recording-studio-brighton", "/equipment", "/gallery", "/testimonials", "/spaces", "/services",
    "/rooms/main-studio", "/rooms/live-room", "/rooms/control-room", "/rooms/writing-rooms", "/rooms/the-bunker",
    "/services/recording", "/services/mixing",
    "/services/mastering", "/services/live-videos", "/services/signature-sessions", "/services/grassroots", "/services/accommodation-hospitality",
}

ASSET_EXTENSIONS = {
    ".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".svg", ".ico",
    ".xml", ".txt", ".json", ".woff", ".woff2", ".mp4", ".webm",
}

EXPECTED_SEARCH_URLS = {
    "About Salvation Studios": "/about/",
    "Our Engineers": "/our-engineers/",
    "Accommodation": "/services/accommodation-hospitality/",
    "Catering": "/services/accommodation-hospitality/",
    "Hospitality": "/services/accommodation-hospitality/",
    "Dry Hire": "/services/recording/",
    "Lighting": "/services/live-videos/",
    "Vocal Booth": "/rooms/live-room/#isolation",
    "Iso Booths": "/rooms/live-room/#isolation",
    "Isolation Booths": "/rooms/live-room/#isolation",
    "Main Studio": "/rooms/main-studio/",
    "Grassroots": "/services/grassroots/",
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
    return candidate if candidate in INDEXABLE_HTML or candidate in NOINDEX_HTML or candidate in AD_NOINDEX_HTML else None


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
        self.title_parts: list[str] = []
        self.meta: list[dict[str, str]] = []
        self.h1_count = 0
        self._in_title = False
        self._in_json_ld = False
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): v or "" for k, v in attrs}
        if "id" in attr_map:
            self.ids.add(attr_map["id"])
        if tag.lower() == "h1":
            self.h1_count += 1
        if tag.lower() == "meta":
            self.meta.append(attr_map)
        for name in ("href", "src"):
            if name in attr_map:
                self.attrs.append((tag.lower(), name, attr_map[name]))
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "script" and attr_map.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
        if tag.lower() == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._buf).strip())
            self._in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_json_ld:
            self._buf.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    def meta_content(self, *, name: str | None = None, prop: str | None = None) -> str:
        for item in self.meta:
            if name and item.get("name", "").lower() == name.lower():
                return item.get("content", "").strip()
            if prop and item.get("property", "").lower() == prop.lower():
                return item.get("content", "").strip()
        return ""


def parse_html(path: Path) -> LinkParser:
    parser = LinkParser()
    parser.feed(path.read_text(errors="ignore"))
    return parser


def search_index_entries() -> list[tuple[str, str]]:
    search_file = ROOT / "search.js"
    if not search_file.exists():
        return []
    text = search_file.read_text(errors="ignore")
    return [
        (match.group(1), match.group(4))
        for match in re.finditer(
            r"\[\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*\]",
            text,
        )
    ]


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

    unknown = set(files) - INDEXABLE_HTML - NOINDEX_HTML - AD_NOINDEX_HTML
    if unknown:
        failures.append(f"unclassified html files: {sorted(unknown)}")

    config = load_config()
    redirects = config.get("redirects", [])
    redirect_sources = {r.get("source") for r in redirects}
    redirect_destinations = {r.get("source"): r.get("destination") for r in redirects}
    for old_route in ("/giveaways-offers", "/services/giveaways-offers"):
        if redirect_destinations.get(old_route) != "/services/grassroots":
            failures.append(f"Grassroots legacy redirect mismatch for {old_route}")

    headers = config.get("headers", [])
    header_sources = {h.get("source") for h in headers}
    test_host_rules = [
        rule for rule in headers
        if rule.get("source") == "/(.*)"
        and {"type": "host", "value": TEST_HOST} in rule.get("has", [])
        and {"key": "X-Robots-Tag", "value": "noindex, nofollow"} in rule.get("headers", [])
    ]
    if len(test_host_rules) != 1:
        failures.append("test hostname must have exactly one host-scoped noindex, nofollow header")
    elif any(headers.index(test_host_rules[0]) < headers.index(rule) for rule in headers if rule.get("source") in {"/enquire", "/enquire/"}):
        failures.append("test-host noindex header must override advertising-route follow policy")
    if not {"/enquire", "/enquire/"}.issubset(header_sources):
        failures.append("advertising enquiry route is missing its noindex response header")
    if not {"/live-video-sessions", "/live-video-sessions/"}.issubset(header_sources):
        failures.append("live video campaign route is missing its noindex response header")
    rewrites = {rule.get("source"): rule.get("destination") for rule in config.get("rewrites", [])}
    if rewrites.get("/enquire/") != "/enquire.html":
        failures.append("advertising enquiry clean route rewrite is missing")
    if rewrites.get("/live-video-sessions/") != "/live-video-sessions.html":
        failures.append("live video campaign clean route rewrite is missing")
    if rewrites.get("/our-engineers/") != "/our-engineers.html":
        failures.append("Our Engineers clean route rewrite is missing")
    if "/docs/:path*" not in header_sources:
        failures.append("docs directory is publicly deployable without noindex header")
    expected_concept_header_sources = {
        "/concept-index",
        "/concept-index/",
        "/concept-index.html",
        "/concept-1-bunker",
        "/concept-1-bunker/",
        "/concept-2-bloom",
        "/concept-2-bloom/",
        "/concept-3-signal",
        "/concept-3-signal/",
        "/concept-4-void",
        "/concept-4-void/",
    }
    if not expected_concept_header_sources.issubset(header_sources):
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
        if route in NEW_PUBLIC_ROUTES:
            continue
        if route not in redirect_sources:
            failures.append(f"missing old-site redirect for {route}")

    for relative, path in files.items():
        text = path.read_text(errors="ignore")
        parser = parse_html(path)

        if relative != "live-video-sessions.html" and any(
            attr == "href" and urlparse(value).path.rstrip("/") == "/live-video-sessions"
            for _, attr, value in parser.attrs
        ):
            failures.append(f"unlisted live video campaign is linked from {relative}")

        if re.search(r"href=[\"']#[\"']", text):
            failures.append(f"placeholder href remains in {relative}")
        if ".superpowers" in text:
            failures.append(f"hidden .superpowers artifact referenced in {relative}")
        if re.search(r"\b(Book a Session|Book A Session|Book Your Session|Book Now|Reserve Now)\b", text):
            failures.append(f"booking-language overpromise remains in {relative}")
        if re.search(r"direct backend|approved destination|transparent and reviewable", text, re.I):
            failures.append(f"internal implementation copy remains in {relative}")
        if re.search(r"tel:[^\"']*\*", text):
            failures.append(f"masked tel link/text remains in {relative}")

        canonical = re.search(r"<link\s+rel=[\"']canonical[\"']\s+href=[\"']([^\"']+)[\"']", text, re.I)
        if relative in INDEXABLE_HTML:
            expected = clean_url_for(relative)
            if not canonical or canonical.group(1) != expected:
                failures.append(f"canonical mismatch in {relative}: expected {expected}")
            title = parser.title
            description = parser.meta_content(name="description")
            og_title = parser.meta_content(prop="og:title")
            og_description = parser.meta_content(prop="og:description")
            if not (25 <= len(title) <= 70):
                failures.append(f"SEO title length out of range in {relative}: {len(title)} chars")
            if not (80 <= len(description) <= 170):
                failures.append(f"SEO description length out of range in {relative}: {len(description)} chars")
            if parser.h1_count != 1:
                failures.append(f"expected exactly one h1 in {relative}, found {parser.h1_count}")
            if not og_title or not og_description:
                failures.append(f"missing Open Graph title/description in {relative}")
            desktop_nav = re.search(r'<ul class="nav-links">(.*?)</ul>', text, re.S)
            if not desktop_nav or 'href="/our-engineers/"' not in desktop_nav.group(1):
                failures.append(f"Our Engineers top navigation is missing from {relative}")
        if relative == "services/grassroots.html":
            for term in ("affordable", "unsigned", "emerging", "independent"):
                if term not in text.lower():
                    failures.append(f"Grassroots page is missing required message: {term}")
            if re.search(r"don't have any active offers|don’t have any active offers", text, re.I):
                failures.append("Grassroots page still contains inactive-offers copy")
            if re.search(r"£\s*\d", text):
                failures.append("Grassroots page publishes an unapproved price")
            if len(re.findall(r'class=["\']grassroots-audience-item["\']', text)) != 2:
                failures.append("Grassroots page must list exactly Unsigned and Emerging")
            if re.search(r"<h3>\s*Independent\s*</h3>", text, re.I):
                failures.append("Grassroots page still lists Independent as an audience category")
        if relative in NOINDEX_HTML and not re.search(r"<meta\s+name=[\"']robots[\"']\s+content=[\"']noindex,\s*nofollow[\"']", text, re.I):
            failures.append(f"noindex meta missing from non-production page {relative}")
        if relative in AD_NOINDEX_HTML and not re.search(r"<meta\s+name=[\"']robots[\"']\s+content=[\"']noindex,\s*follow[\"']", text, re.I):
            failures.append(f"noindex, follow meta missing from advertising page {relative}")

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

    homepage = (ROOT / "index.html").read_text(errors="ignore")
    advert_page = (ROOT / "enquire.html").read_text(errors="ignore")
    campaign_page = (ROOT / "live-video-sessions.html").read_text(errors="ignore")
    if "10 hours of studio time" in campaign_page:
        failures.append("live video campaign still promises 10 hours of studio time")
    if "Tell us about your session with no obligation" not in campaign_page:
        failures.append("live video campaign call to action is missing")
    if "Create live videos that look as good as they sound." not in campaign_page:
        failures.append("live video campaign tagline is missing")
    for relative, text in (("index.html", homepage), ("enquire.html", advert_page), ("live-video-sessions.html", campaign_page)):
        if text.count('src="/enquiry.js?') != 1:
            failures.append(f"shared enquiry handler must load exactly once in {relative}")
        if text.count('class="enquiry-form"') != 1:
            failures.append(f"expected exactly one enquiry form in {relative}")
        if text.count('name="form_started_at"') != 1:
            failures.append(f"expected exactly one enquiry timing field in {relative}")

    responsive_assets = {
        "photos/optimized/hero/main-studio-640.avif",
        "photos/optimized/hero/main-studio-960.avif",
        "photos/optimized/hero/main-studio-1440.avif",
        "photos/optimized/hero/main-studio-1920.avif",
        "photos/optimized/brand/logo-160.webp",
        "photos/optimized/brand/logo-320.webp",
        "photos/optimized/brand/salvation-script-360.webp",
        "photos/optimized/brand/salvation-script-705.webp",
    }
    for asset in sorted(responsive_assets):
        if not (ROOT / asset).is_file():
            failures.append(f"missing responsive homepage asset: {asset}")
        if f"/{asset}" not in homepage:
            failures.append(f"responsive homepage asset is not referenced: {asset}")
    if homepage.count('fetchpriority="high"') != 1:
        failures.append("homepage must have exactly one high-priority image")
    if not re.search(r'src="/photos/optimized/studio-sfpb\.webp"[^>]*loading="lazy"', homepage):
        failures.append("below-fold Main Studio image must be lazy-loaded")

    for name, value in search_index_entries():
        expected = EXPECTED_SEARCH_URLS.get(name)
        if expected and value != expected:
            failures.append(f"unexpected search index URL for {name}: {value} expected {expected}")
        parsed = urlparse(value)
        if re.search(r"\.html($|[#?])", value):
            failures.append(f"non-clean search index URL: {value}")
        if not value.startswith("/"):
            failures.append(f"non-root-relative search index URL: {value}")
            continue
        if parsed.path.rstrip("/") == "/live-video-sessions":
            failures.append("unlisted live video campaign appears in site search")
        suffix = Path(parsed.path).suffix.lower()
        if suffix in ASSET_EXTENSIONS:
            if not asset_exists(parsed.path):
                failures.append(f"missing search index asset: {value}")
            continue
        target = route_to_file(parsed.path.rstrip("/") + "/")
        if target is None and parsed.path != "/":
            failures.append(f"search index route does not resolve: {value}")
            continue
        if parsed.fragment and target:
            target_parser = parse_html(ROOT / target)
            if parsed.fragment not in target_parser.ids:
                failures.append(f"search index anchor does not resolve: {value}")

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
