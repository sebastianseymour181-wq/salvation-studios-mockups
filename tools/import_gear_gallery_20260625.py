#!/usr/bin/env python3
"""Import and mix Salvation Studios gear images into the gallery page."""

from __future__ import annotations

import html
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "photos" / "gallery-2026-06-25"
GEAR_MANIFEST = OUT_DIR / "gear-manifest.json"
GALLERY_MANIFEST = OUT_DIR / "gallery-manifest.json"
GALLERY_HTML = ROOT / "gallery.html"
HOME_HTML = ROOT / "index.html"


GEAR_ITEMS = [
    ("li6s9ehwqrea4i31hphmoxknmceltiwh", "Hammond B3 organ"),
    ("nf2yldc5921ief7jq8ll6bn53oxohgp7", "1963 Fender Jazzmaster and Mesa Boogie Mark V"),
    ("z44t52mvivl729eojxqo7zowapamvhg0", "C&C Custom Kit and Ludwig 402 snare"),
    ("7ahsy6zav5bcgdjm567cxx9lzp7l7ky6", "Ampeg GU-12"),
    ("xzfd1mc1lf3oqwkxnbkr79nh74vke1o3", "From front to back: Flea 47, Soundeluxe U95, Neumann 47 Fet, Neumann-Gefell CMV 563, Austrian Audio OC818, AKG C414, Coles 4038, Soyuz Bomblet, Sony C800G, Neumann M150, Neumann U87"),
    ("c1kc4hgi1ia7tl9c4qxodbqn42quadbi", "C&C Custom Kit"),
    ("ohtfvwhubllzyxbqrzsn2gc83n9hfq0q", "One of our Neumann M150s"),
    ("2y8g30mig024ewhgv2kdj0mxbfsmt0ky", "Epiphone Jack Casady and our Ampeg B-15-N with Portaflex cab"),
    ("sqamvxilfzxaeas2xt264611yrr1uhn4", "Fender Rhodes Mark 1"),
    ("yrv6wulixpbl611hll33bolfbxws52u4", ""),
    ("cnm58s0ymdja7a8fjbufjwmzwgy9q3tv", ""),
    ("m5wo69eeftiea3rsrl9v3h44plp7g7f9", "Tama Starclassic Maple Kit"),
    ("vdupk9jo6fqjyvo2qun8jrtdv70kuwar", "Sonor Benny Greb, Craviotto, Ludwig 402, Dunnett Steel"),
    ("j5f5lq3ahp8jw9ko540kpmu6umlb5m80", "Hammond The Sounder"),
    ("ljdbs5z2sivtlq3x573fbv59i3qe6tdv", "WEM Watkins Starfinder Twin 15 Cabs"),
    ("nnsjjd5h4dg5rdr5eh35knfdce0nthjr", "1964 Fender Bassman"),
    ("bfwyni23nq054awsunqpjdg16b8aiffy", "1960s Fender Pro Reverb"),
    ("zy83heyw6ntm0ibm6h0txuwkplnvtzgb", "AKG C414"),
    ("tvbxflet8318rxajfy3hul9gd31s1vsu", "1983 Gibson ES-335 and 1965 Vox AC30"),
    ("rcl9s72xanewtzecf8o5v6rdo8ij6whd", "Austrian Audio OC818"),
    ("kdskyg37h4tvzgeavyro6q136tv6ydjd", "1973 Sound City B120 with Matching Cabinet"),
    ("stiqv39yjpkg2n8oam5lio2p3q95it7q", "Sound Deluxe U95"),
    ("hwzazkvt6wsdi3sboagxiqly5o81wjmn", "One of our Coles 4038"),
    ("zjjn6pphqs6x7dts4qqud5iwatnxsesm", "1971 Marshall JMP 50"),
    ("b37yfbcfozgmqkiuf5ww2tky07u4rduh", "Roland Space Echo RE-201"),
    ("m87f4vl74ck466lpcg0ownajk3eydv6w", "Neumann U47 Fet"),
    ("hhk5k2e98240qgso5icv7cc9mxwhi3ca", "Overdrive Special by Norbury (Exact point to point replica of the Dumble Amp)"),
    ("5ay3569eudf7faouyo2c41cd88xjaf9f", "Soyuz Bomblet"),
    ("7qjbnkioc0opa0ys2qhihwahxiufqcqh", "Neumann Geffel CMV 563"),
    ("1568ss0ozgx1qnocfw8a7t98uvrfqti9", "Neumann U87"),
    ("fz57x4su78o2lnu7wyf3lpyuaqbs4qjp", "Hiwatt DR103 with matching cabinet"),
    ("10cpvwjr9dlxr4jzkvfchy9g6z2zvw4c", "Sony C800"),
    ("4cswkw3hplucpnm41jfa7rwcnmvi2gm1", "Flea 47 Vintage"),
    ("j9sn7rgdwj22jsxf9c8cumybq56zclo5", "Orange OR120"),
    ("e6mdsghr6j8c7n1upur78fjviid7ir95", "Wurlitzer EP200A"),
    ("ajw7k4tzgclc2c157n64x5thhisoazvc", "1970s Ludwig Cortex kit"),
    ("wsmfkpujdsik1ww8og2fzsptrudhuuq4", "1965 Fender Telecaster and our 1972 Ampeg GU-12"),
]


ALT_OVERRIDES = {
    "yrv6wulixpbl611hll33bolfbxws52u4": "White drum kit detail at Salvation Studios",
    "cnm58s0ymdja7a8fjbufjwmzwgy9q3tv": "White drum kit set up at Salvation Studios",
}


def slugify(value: str, fallback: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:72].strip("-") or fallback


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def dimensions(path: Path) -> tuple[int, int]:
    out = run(["magick", "identify", "-format", "%w %h", str(path)]).stdout
    width, height = out.strip().split()
    return int(width), int(height)


def import_item(item: tuple[int, str, str]) -> dict[str, object]:
    idx, box_id, caption = item
    slug = slugify(caption, f"gear-{idx:02d}-{box_id[:8]}")
    out_path = OUT_DIR / f"gear-{idx:02d}-{slug}.webp"
    static_url = f"https://xviimusicgroup.box.com/shared/static/{box_id}.jpg"

    if not out_path.exists():
        with tempfile.TemporaryDirectory(prefix="salvation-gear-") as tmp:
            raw = Path(tmp) / f"{box_id}.jpg"
            run([
                "curl",
                "-L",
                "--fail",
                "--retry",
                "2",
                "--connect-timeout",
                "20",
                "--max-time",
                "180",
                "-A",
                "Mozilla/5.0",
                "-o",
                str(raw),
                static_url,
            ])
            run([
                "magick",
                str(raw),
                "-auto-orient",
                "-resize",
                "1800x1800>",
                "-strip",
                "-quality",
                "78",
                str(out_path),
            ])

    width, height = dimensions(out_path)
    return {
        "index": idx,
        "box_id": box_id,
        "source_url": f"https://xviimusicgroup.box.com/s/{box_id}",
        "src": "/" + str(out_path.relative_to(ROOT)),
        "caption": caption,
        "alt": caption or ALT_OVERRIDES[box_id],
        "width": width,
        "height": height,
        "type": "gear",
    }


def figure_class(item: dict[str, object], position: int) -> str:
    width = int(item["width"])
    height = int(item["height"])
    ratio = width / height
    classes = ["gp"]
    if ratio > 1.28:
        classes.append("wide")
    elif ratio < 0.78:
        classes.append("tall")
    if position % 13 == 0 and ratio > 0.9:
        classes.append("xlarge")
    return " ".join(classes)


def render_figure(item: dict[str, object], position: int) -> str:
    caption = str(item.get("caption") or "")
    alt = str(item.get("alt") or "Salvation Studios gallery photograph")
    class_name = figure_class(item, position)
    lines = [
        f'    <figure class="{class_name}">',
        f'      <img src="{html.escape(str(item["src"]), quote=True)}" alt="{html.escape(alt, quote=True)}" width="{item["width"]}" height="{item["height"]}" decoding="async" loading="lazy">',
    ]
    if caption:
        caption_class = ' class="caption-long"' if len(caption) > 90 else ""
        lines.append(f"      <figcaption{caption_class}>{html.escape(caption)}</figcaption>")
    lines.append("    </figure>")
    return "\n".join(lines)


def mixed_items(gallery: list[dict[str, object]], gear: list[dict[str, object]]) -> list[dict[str, object]]:
    return gallery + gear


def update_gallery_html(items: list[dict[str, object]]) -> None:
    text = GALLERY_HTML.read_text(encoding="utf-8")
    start = text.index('  <div class="gallery-grid" aria-label=')
    end = text.index("  </div>\n</section>", start)
    figures = "\n".join(render_figure(item, pos) for pos, item in enumerate(items, start=1))
    replacement = '  <div class="gallery-grid" aria-label="Salvation Studios session and gear gallery">\n' + figures + "\n"
    GALLERY_HTML.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


HOME_CLASSES = [
    "gp tall reveal",
    "gp tall reveal reveal-d1",
    "gp reveal reveal-d2",
    "gp reveal reveal-d3",
    "gp tall reveal",
    "gp reveal reveal-d1",
    "gp reveal reveal-d2",
    "gp reveal reveal-d3",
    "gp reveal",
    "gp reveal reveal-d1",
    "gp wide reveal reveal-d2",
    "gp reveal reveal-d3",
    "gp reveal",
    "gp reveal reveal-d1",
    "gp wide reveal reveal-d2",
    "gp reveal reveal-d3",
    "gp wide reveal",
    "gp reveal reveal-d1",
    "gp wide reveal reveal-d2",
]


def render_home_figure(item: dict[str, object], class_name: str) -> str:
    caption = str(item["caption"])
    caption_class = ' class="caption-long"' if len(caption) > 90 else ""
    return "\n".join([
        f'    <figure class="{class_name}">',
        f'      <img src="{html.escape(str(item["src"]), quote=True)}" alt="{html.escape(str(item["alt"]), quote=True)}" width="{item["width"]}" height="{item["height"]}" decoding="async" loading="lazy">',
        f"      <figcaption{caption_class}>{html.escape(caption)}</figcaption>",
        "    </figure>",
    ])


def update_home_html(items: list[dict[str, object]]) -> None:
    text = HOME_HTML.read_text(encoding="utf-8")
    start = text.index('  <div class="gallery-mosaic">')
    end = text.index("  </div>\n</section>", start)
    figures = "\n".join(render_home_figure(item, class_name) for item, class_name in zip(items, HOME_CLASSES))
    replacement = '  <div class="gallery-mosaic">\n' + figures + "\n"
    HOME_HTML.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    skipped_duplicates: list[dict[str, str]] = []
    unique: list[tuple[int, str, str]] = []
    for box_id, caption in GEAR_ITEMS:
        if box_id in seen:
            skipped_duplicates.append({"box_id": box_id, "caption": caption})
            continue
        seen.add(box_id)
        unique.append((len(unique) + 1, box_id, caption))

    results: list[dict[str, object]] = []
    failures: list[tuple[int, str, str]] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        future_map = {pool.submit(import_item, item): item for item in unique}
        for future in as_completed(future_map):
            idx, box_id, caption = future_map[future]
            try:
                result = future.result()
                results.append(result)
                print(f"ok gear {idx:02d} {box_id} {caption[:72]}")
            except Exception as exc:  # noqa: BLE001
                failures.append((idx, box_id, str(exc)))
                print(f"fail gear {idx:02d} {box_id}: {exc}")

    results.sort(key=lambda item: int(item["index"]))
    manifest = {
        "items": results,
        "skipped_duplicates": skipped_duplicates,
    }
    GEAR_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if failures:
        (OUT_DIR / "gear-failures.json").write_text(
            json.dumps(failures, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"failures: {len(failures)}")
        return 1

    gallery = json.loads(GALLERY_MANIFEST.read_text(encoding="utf-8"))
    update_gallery_html(mixed_items(gallery, results))
    update_home_html(gallery[:10] + results[:9])
    print(f"gear imported: {len(results)}")
    print(f"skipped duplicate links: {len(skipped_duplicates)}")
    print(f"manifest: {GEAR_MANIFEST.relative_to(ROOT)}")
    print(f"updated: {GALLERY_HTML.relative_to(ROOT)}")
    print(f"updated: {HOME_HTML.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
