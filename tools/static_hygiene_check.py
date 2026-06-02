#!/usr/bin/env python3
"""Static deployment hygiene checks for the Salvation Studios static site."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HOST = "https://www.salvationstudios.co.uk"
EXCLUDED_DIRS = {".git", ".superpowers", "node_modules"}
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
EXPECTED_TEL = "tel:+443334445508"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def html_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.html")
        if not any(part in EXCLUDED_DIRS for part in p.parts)
    )


def clean_url_for(relative: str) -> str:
    if relative == "index.html":
        return f"{PUBLIC_HOST}/"
    return f"{PUBLIC_HOST}/{relative[:-5]}/"


def sitemap_locs() -> set[str]:
    xml_path = ROOT / "sitemap.xml"
    tree = ET.parse(xml_path)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {node.text.strip() for node in tree.findall(".//sm:loc", ns) if node.text}


def load_redirects() -> list[dict]:
    return json.loads((ROOT / "vercel.json").read_text()).get("redirects", [])


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> int:
    failures: list[str] = []
    files = {rel(p): p for p in html_files()}

    unknown = set(files) - INDEXABLE_HTML - NOINDEX_HTML
    if unknown:
        failures.append(f"unclassified html files: {sorted(unknown)}")

    for relative, path in files.items():
        text = path.read_text(errors="ignore")
        if re.search(r"href=[\"']#[\"']", text):
            failures.append(f"placeholder href remains in {relative}")
        tel_links = re.findall(r"href=[\"'](tel:[^\"']+)[\"']", text)
        for tel in tel_links:
            if "*" in tel or not re.fullmatch(r"tel:\+?[0-9]+", tel):
                failures.append(f"invalid or masked tel link remains in {relative}: {tel}")
            elif tel != EXPECTED_TEL:
                failures.append(f"unexpected tel link in {relative}: {tel}")
        if relative in NOINDEX_HTML and not re.search(r"<meta\s+name=[\"']robots[\"']\s+content=[\"']noindex,\s*nofollow[\"']", text, re.I):
            failures.append(f"noindex meta missing from non-production page {relative}")

    locs = sitemap_locs()
    expected_locs = {clean_url_for(page) for page in INDEXABLE_HTML}
    if locs != expected_locs:
        failures.append(f"sitemap mismatch missing={sorted(expected_locs-locs)} extra={sorted(locs-expected_locs)}")

    redirect_sources = {r.get("source") for r in load_redirects()}
    required_redirects = {
        "/salvation-studios", "/salvation-studios.html", "/concept-index", "/concept-index.html",
        "/vocal-booth", "/isolation-booth-1", "/isolation-booth-2", "/amp-booth",
        "/dry-hire", "/lighting", "/catering",
        "/microphones", "/outboard", "/drums", "/guitars", "/amps", "/basses",
    }
    for source in sorted(required_redirects):
        if source not in redirect_sources:
            failures.append(f"missing redirect for {source}")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: {len(files)} html files audited; {len(locs)} sitemap routes aligned; deployment hygiene clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
