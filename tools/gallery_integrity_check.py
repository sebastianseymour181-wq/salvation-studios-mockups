#!/usr/bin/env python3
"""Verify Salvation's approved homepage and full-gallery manifests."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHOTO_DIR = ROOT / "photos" / "gallery-2026-06-25"


class FigureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.figures: list[dict[str, object]] = []
        self.current: dict[str, object] | None = None
        self.in_caption = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "figure":
            self.current = {"class": values.get("class", ""), "caption": ""}
        elif tag == "img" and self.current is not None:
            self.current.update(values)
        elif tag == "figcaption" and self.current is not None:
            self.in_caption = True

    def handle_data(self, data: str) -> None:
        if self.in_caption and self.current is not None:
            self.current["caption"] = str(self.current["caption"]) + data

    def handle_endtag(self, tag: str) -> None:
        if tag == "figcaption":
            self.in_caption = False
        elif tag == "figure" and self.current is not None:
            self.current["caption"] = str(self.current["caption"]).strip()
            self.figures.append(self.current)
            self.current = None


def load_items(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["items"] if isinstance(data, dict) else data


def parse_figures(path: Path, marker: str) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    start = text.index(marker)
    end = text.index("  </div>\n</section>", start)
    parser = FigureParser()
    parser.feed(text[start:end])
    return parser.figures


def check_figures(actual: list[dict[str, object]], expected: list[dict[str, object]], label: str) -> None:
    assert len(actual) == len(expected), f"{label}: expected {len(expected)} figures, found {len(actual)}"
    for position, (figure, item) in enumerate(zip(actual, expected), start=1):
        prefix = f"{label} position {position}"
        assert figure.get("src") == item["src"], f"{prefix}: wrong image order"
        assert figure.get("alt") == item["alt"], f"{prefix}: alt mismatch"
        assert figure.get("width") == str(item["width"]), f"{prefix}: width mismatch"
        assert figure.get("height") == str(item["height"]), f"{prefix}: height mismatch"
        assert figure.get("caption") == item["caption"], f"{prefix}: caption mismatch"
        assert (ROOT / str(item["src"]).lstrip("/")).is_file(), f"{prefix}: local image missing"


def main() -> int:
    sessions = load_items(PHOTO_DIR / "gallery-manifest.json")
    gear = load_items(PHOTO_DIR / "gear-manifest.json")
    assert len(sessions) == 95 and len({item["box_id"] for item in sessions}) == 95
    assert len(gear) == 37 and len({item["box_id"] for item in gear}) == 37
    assert all(item["alt"] and "gallery photograph" not in str(item["alt"]) for item in sessions + gear)
    assert all(not re.search(r"\b(?:19|20)\d{2}$", str(item["caption"])) for item in sessions + gear)

    home = parse_figures(ROOT / "index.html", '  <div class="gallery-mosaic">')
    gallery = parse_figures(ROOT / "gallery.html", '  <div class="gallery-grid" aria-label=')
    check_figures(home, sessions[:10] + gear[:9], "homepage")
    check_figures(gallery, sessions + gear, "gallery")
    print("PASS: homepage 19 images; gallery 95 sessions + 37 gear; order, captions, alt and files verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
