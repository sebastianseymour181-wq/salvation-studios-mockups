#!/usr/bin/env python3
"""Import Salvation Studios gallery images from the June 2026 Box list."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "photos" / "gallery-2026-06-25"
MANIFEST = OUT_DIR / "gallery-manifest.json"


ITEMS = [
    ("1vkzqb9xor2tblr6i2mrybsqi4ssu1lu", "Sports. writing in the control room 2024"),
    ("mjkf5wa74jp7rke5kac0z023i0e5bx7l", "TELECOM wrapping up their debut single 2024"),
    ("y2zlsjtm9qlkk0vnmxxrrmdfzdkuzb6h", ""),
    ("ir9rrv9rno9ogft9zmoj0xx1ukmlsng7", ""),
    ("5prjv8sgdseu94an062366dtxdyr354p", "Cameron Nesbitt producing"),
    ("n2uu88w6k08hxswxtdcxv5lm38y5tzlo", "Azodi K Pop Writing camp 2024"),
    ("erw7p2ayao8stvd0cfjyy2bqydcibqid", "Jon McClure in the studio with Reverend And The Makers 2024"),
    ("xcdemfl3eh7qqojw4d3l4mzdvcyvl6sk", "Jack Maynard and Josh Wantie in the studio 2023"),
    ("ji2968bmyen1vv5ln1bosk7d6blvqia9", "David Gilmour with his 1950s Fender Esquire"),
    ("xbllwdu8151za7ljvz1aee5epz3xhn36", "Dimitri Tikovoi with working with Reverend and The Makers 2024"),
    ("vblel1zxlcz3dypaohp3ckeejqq97w7t", "World Orchestra"),
    ("bs56zb4unmp6ee8uilyegy2m8m5yodn3", "Reverend and the Makers wrapping up a strings session 2024"),
    ("iq6kt886sta861zr6qx6djssouy3c8i9", "SNAYX live video session 2024"),
    ("vri0dw8x13gxrudmegc7ag0uzf8pn86b", ""),
    ("s7y4uqzf7gz9ovh4vwqvv2ortig3m3jr", "NOISY in the control room 2024"),
    ("fpq4cdbj8r7nwfwckzkmqrv933aaa4oo", "LYRA laying down some vocals 2023"),
    ("4r2rar85xplelq3j8on1zyjssui83ql4", "Matt Glasbey in with David Gilmour 2024"),
    ("ymgwmohh6i5md1h576t8nh281hxbd3h9", "James Marriot in the studio 2023"),
    ("o1rq5njy1ycml56y7jeln234p6yf0wgo", "Dominic Ferris playing our beautiful C3 2024"),
    ("hi1037br5rkppvs5rnpkl73fbonqe49n", "Joe Montague on the drums 2024"),
    ("t1g9v23hy6hr5pohtehq5qm3yfviyatf", "Dizzee Rascal making a big track in the studio 2024"),
    ("qcu4a60u3d336waaqw2froxzpis2h9tw", "Dan Carey & Alexis Smith in the studio tracking WetLeg 2024"),
    ("ydhu1agj0g95xb83mq4scatwtm1get38", "Theo Verney with Youth Sector 2024"),
    ("jdrlqiob9pni0idohdd26m4a2d2mkbix", ""),
    ("w41kjxw3x5gnjthq9wxoq5zj8cvkupb8", ""),
    ("w5war4ihjq0y713dccewz2ber1cwwpbt", "Beautiful string quartet 2024"),
    ("44ej5xmcsyh3jwjwni7p2vhmposijhcf", ""),
    ("d48eajg37viqbgl1qlqxy5bzsl1z7v3g", "Phill Brown working the Neve 2025"),
    ("hakvli8o6z2j5j6fysngvfyg1k96rhng", ""),
    ("ow7k8q7se4jn6kqqr49gu57bwttgso2m", "Jesse Wood in with CANDAR and Sean Genocky 2024"),
    ("a8eskaw92a3n406e1gmn17d5jihqy5e3", ""),
    ("xxvkpln2epy1jzpauwn8sb47qba32jhw", "RCS Writing Camp 2023"),
    ("rwguof61jujmuljlgwlgtqfit3gx1rl8", "Sean Genocky with his WEM Copicat 2024"),
    ("gc2g31bfjak3f4pjrbaliht05fva9k6u", "Nick Brine and Rusty wrapping up a session 2025"),
    ("s4ubs3lrunfpzh9z78ked3pagdwj7yqe", ""),
    ("dg1l8i0du0kfrjruujmoagpw63x5277s", "XXX micing our 2048 Reverb-Trem"),
    ("a7mcvki8ka8jjcma3pnnjhir0kzqy68i", "Lewis Thompson in the studio 2024"),
    ("hiwegmysrfty80a0a7xn5f9cb6t1fgqh", ""),
    ("vv6mwj1gz1wfzgq19kocpfxmdzc7ry0l", "akdk making some serious noise in the live room 2023"),
    ("qsla7iq2kpxwd5ozfb849riuahgvki4d", "City Dog chilling with Lemmy 2023"),
    ("ywnqptf2z2x8ak4kl30v1y425qc6gkn9", "Sam from Comforts playing our ES-335 Gibson 2023"),
    ("rpki68g2252v0ugmdrjj4lyu1nrb6bjc", "Oliver Alberici with Adrian Hall in 2023"),
    ("3ay4gyh7ge9zmlsqr5wv8y1ljzj1g86g", "Rich Costey and Rusty wrapping up a session 2024"),
    ("173kwu91vnujh04hr3qcsvi6y3bk5snf", "Adrian Hall working the Neve 2023"),
    ("ofyhh1bfy6fynwzarfys207hvdgocujv", "Phill Cook with Sam Tompkins 2024"),
    ("29ot63ocphzw1n52yc86cs877jkhx5bb", "Pete Hutchings with Beach Riot 2023"),
    ("frxkik2qypxrds8kodckh03ymgbrkrk4", "Joseph Rodgers mixing masterclass 2024"),
    ("9711v81qt8k4q9ywiqvxybffzyskso2y", "Sie Medway-Smith mixing masterclass 2024"),
    ("fay04h6yblj9vs95ci0k58t2v8ytziad", "MYTHS live session 2024"),
    ("4p08l7en03c832tf1nj1sg4i4wcmr1cw", "Adrian Hall mixing masterclass 2024"),
    ("rn6owkeo93eugvyg6m9ekk7r0dl20sbi", "James Maltby Script runthrough 2024"),
    ("w4vo5ic7kdtsxya1z8npqz8plor4lo8m", "GOETIA tracking with Phill Brown 2024"),
    ("3mv94yx9uppalgfx1h6hwnhpb2r6b415", "Wet Leg in the studio tracking their album “moisturizer” 2024"),
    ("uapvaymub7wiu4spwe4yt24l4lywjb53", "Fright Years with Theo Verney 2024"),
    ("zvgip22edtdfzxp0g2bsizs2tncgefzj", "Phill Brown getting a crazy drum sound 2025"),
    ("nfau9wicqxcxv3t7qi0wcdg9rddj0oc4", "Drum tuning masterclass with Al Moody 2024"),
    ("3qq2s1hw3dxszicqgpgnyckqkecz4p6w", "Finn Genockey jazz session 2025"),
    ("imd5gynr5bj47t3e9d8o16fcdw9ems1d", "Writing Camp"),
    ("03a6kg7pw0ei8nmf7gu86rc2huya5vu5", "Frankcastre tracking 2024"),
    ("b04udubqq30dnw36b9d7szntxj3wakn3", "Lewis Thompson Writing Camp 2024"),
    ("37ew4nr8v7hez146h8qia6e8xaazkaor", "Fondoo with Sean Genocky 2023"),
    ("vhdnoqvt60w2ya2wjylz7jbwe9d3d6b0", "Ben Poole Live Video Session 2023"),
    ("25qdwnfvwfsxz6sl5lyu7gvs8ufvfyp4", "Cassyette Live Video Session 2024"),
    ("nfxqdjy8w1ayj87hcgn4o2gryy403sy6", "ArrDee laying down some guitar 2024"),
    ("rnocynjnkyadd8avszlt9uks6ulpuc3a", ""),
    ("kkrcbxepx3dvb8wo9hjnoyj36rq5e56q", "Adam Greenspan tracking PIGLET 2023"),
    ("5e6dulurltxeuy2vb79wxqbz9jddgw4o", "Danny Adderson Album recording 2024"),
    ("u45c8qhyavay0pa8m9fcf1ria9b478pd", "Black Limes 2024"),
    ("fmgsau773dt1g3184e1zkfr9sw1rgwqg", "Cats In Space album recording with Ian Caple 2024"),
    ("8c3zach6ju4smtlfp2fswkrkjkw1nxei", "CANDAR recording 2024"),
    ("6u2hk9uwuf2hyl65taidxyko9y3wdzln", "ArrDee in the studio 2025"),
    ("h89o4akcenky6wd3z0wd8y7o1mxh0wsu", "Lyra tracking vocals 2026"),
    ("e2aw7sl0wokf0v5y5zsln1a02os8vv11", "Hot Wax with Theo Verney 2025"),
    ("u5y4irt39cw1qhkh3qyaoc9wipr5cohn", "Theo Verney on the Neve with Hot Wax 2025"),
    ("cbeavd60c36flcsmpwtw6sg6mjh04vns", "Theo Verney tuning drums 2025"),
    ("hy8jt4mmgou85ns1cdvjukilrusaet9t", "Skindred Album Session 2025"),
    ("gbl60g4kxmjms3m6r1zvc5s30zdd1efp", "Skindred recording their album “You Got This” 2025"),
    ("e7l6g5c3uszaiprg6dpjetkaktkm2yxw", "Benji with his Hennessy 2025"),
    ("q5npah2vjmdhqsbmhy57fifwx6lf1g0v", "Benji tracking vocals for Skindred 2025"),
    ("5z7mjqng8ctef6vpefir3j4h2of4lvi9", "Skindred’s crazy drum rig 2025"),
    ("ar2yjt8n1l11hqeb3o5pxw6ltdw5e2pm", "Wargasm writing session with Charlie Russell and Kieron Pepper 2025"),
    ("ym5lyclsv5l50rwj2iskrako208ku2pg", "Kieron Pepper in the studio with Wargasm 2025"),
    ("uu3iedqhksl9jtyq6mv2axok63nlu58a", "Saint Agnus live video session with BlueJuice 2025"),
    ("pyyv1s6v9nabrwbxb8t9v6wf25hq59tc", "Saint Agnes Live Video session 2025"),
    ("0rgx3rbjqtsdzwmjzl4qad13sp0bvfbh", "Blue Juice Visuals capturing a Saint Agnus session 2025"),
    ("1s4smaxx7ayzsm4pzzvqq3zwxio2fa09", "Ollie from SNAYX tracking vocals 2025"),
    ("0fykthejrvmotsuwm0vl9dwqphahd4an", "Charlie from SNAYX in the vocal booth 2025"),
    ("bnz2vct0gr0tiwlzngmndcsdjpxuj81n", "Charlie Russell on the Neve 2025"),
    ("corusuli96io8er5tudxiviulb3nt8w0", ""),
    ("xdzn8oh0sgwy1fg13i5rc3tctjeft81j", "Badger and Example in the studio 2025"),
    ("idjsgobs9bqulfdytsth2mb1vb69m9pw", "Badger and Example in the studio 2025"),
    ("grdztlo3l97l8p6p6lzl46rn9vs9bjqv", "Lovejoy drum tracking 2025"),
    ("mlzt7o2v0kjlt7iud4vlexgzdt64igif", "ArrDee in the studio 2025"),
]


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
    slug = slugify(caption, f"gallery-{idx:02d}-{box_id[:8]}")
    out_path = OUT_DIR / f"{idx:02d}-{slug}.webp"
    source_url = f"https://xviimusicgroup.box.com/s/{box_id}"
    static_url = f"https://xviimusicgroup.box.com/shared/static/{box_id}.jpg"

    if not out_path.exists():
        with tempfile.TemporaryDirectory(prefix="salvation-gallery-") as tmp:
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
        "source_url": source_url,
        "src": "/" + str(out_path.relative_to(ROOT)),
        "caption": caption,
        "alt": caption or "Salvation Studios gallery photograph",
        "width": width,
        "height": height,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    unique: list[tuple[int, str, str]] = []
    for box_id, caption in ITEMS:
        if box_id in seen:
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
                print(f"ok {idx:02d} {box_id} {caption[:60]}")
            except Exception as exc:  # noqa: BLE001
                failures.append((idx, box_id, str(exc)))
                print(f"fail {idx:02d} {box_id}: {exc}")

    results.sort(key=lambda item: int(item["index"]))
    MANIFEST.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if failures:
        (OUT_DIR / "gallery-failures.json").write_text(
            json.dumps(failures, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"failures: {len(failures)}")
    print(f"imported: {len(results)}")
    print(f"manifest: {MANIFEST.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
