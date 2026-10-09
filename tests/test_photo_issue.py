"""photo_issue: a magazine around the user's own photographs.

Holds:
  1. The user's words are used verbatim -- check_texts() passes on the real spec and FAILS when one word changes.
  2. Built with stand-in photos (the real ones are personal and stay out of git, in photos/): every photo appears,
     the PDF has one page per HTML page, nothing overflows at print size.
  3. Print resolution is measured, not assumed: large stand-ins PASS, 468 px stand-ins (the size of the
     screenshot crops) FAIL -- that check is what told us the originals are needed for print.
  4. A photo missing from disk FAILS.
Run: python3 tests/test_photo_issue.py
"""
from __future__ import annotations

import copy
import re
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

뿌리 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(뿌리))
임시 = tempfile.mkdtemp(prefix="gmphoto-")
os.environ["GENTLE_MONSTER_OUT"] = 임시

from PIL import Image, ImageDraw  # noqa: E402

from gentle_monster.magazine import pdf as PDF, photo_issue as PI  # noqa: E402

FAIL = []
SPEC = 뿌리 / "editorial" / "issues" / "spa_00_stops.json"


def ok(cond, what):
    print(("  ok  " if cond else "  FAIL ") + what)
    if not cond:
        FAIL.append(what)


def status(checks, name):
    return next((c["status"] for c in checks if c["check"].startswith(name)), None)


def stand_ins(folder: Path, w: int, h: int, n: int = 15):
    folder.mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        im = Image.new("RGB", (w, h), (20 * i % 255, 90 + 9 * i, 200 - 11 * i))
        d = ImageDraw.Draw(im)
        for k in range(0, w, max(8, w // 40)):
            d.line((k, 0, w - k, h), fill=(255 - 15 * i % 255, 40 * (i % 5), 120), width=max(1, w // 400))
        im.save(folder / f"{i:02d}.png")


def spec_with(folder: Path) -> Path:
    s = json.loads(SPEC.read_text(encoding="utf-8"))
    s["photo_dir"] = str(folder)
    p = Path(임시) / f"spec-{folder.name}.json"
    p.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
    return p


print("[texts]")
spec = PI.load(SPEC)
ok(PI.check_texts(spec) == [], "every user text in the spec is verbatim in docs/portfolio")
bad = copy.deepcopy(spec)
bad["intro"]["ko"][0] = bad["intro"]["ko"][0].replace("장면", "풍경")
ok(any("intro" in b for b in PI.check_texts(bad)), "RED: one changed word in the intro is caught")
bad = copy.deepcopy(spec)
bad["manifesto"]["lines"][1] = "and spaces shape us back."
ok(any("manifesto" in b for b in PI.check_texts(bad)), "RED: a manifesto line that drifted from the philosophy is caught")
bad = copy.deepcopy(spec)
bad["back"]["en"] = bad["back"]["en"].replace("stops", "pauses")
ok(any("back" in b for b in PI.check_texts(bad)), "RED: the back-cover sentence changed is caught")
ok(len(spec["photos"]) == 15 and spec["cover"]["photo"] == spec["lens"]["chosen"], "cover photo = the lens page's choice")

print("[light]")
ok(PI.light({"mono": False, "dark": 0.8, "brightness": 0.1, "warmth": 0, "saturation": 0.3}) == "밤", "a dark frame reads as 밤")
ok(PI.light({"mono": True, "dark": 0.1, "brightness": 0.5, "warmth": 0, "saturation": 0.0}) == "흑백", "a grey frame reads as 흑백")
ok(PI.light({"mono": False, "dark": 0.1, "brightness": 0.5, "warmth": 0.12, "saturation": 0.3}) == "해 질 녘", "a warm frame reads as 해 질 녘")

print("[stencil]")
try:
    from PIL import ImageFont
    import numpy as np
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 1000)
    svg = PI.masthead_svg("SPA")

    def rows(ch, x0, x1):
        im = Image.new("L", (800, 1000), 0); ImageDraw.Draw(im).text((0, 0), ch, font=font, fill=255)
        a = np.asarray(im) > 128
        ys = [y for y in range(200, 950) if a[y, x0:x1].any()]
        runs = []
        for y in ys:
            if runs and y == runs[-1][1] + 1:
                runs[-1][1] = y
            else:
                runs.append([y, y])
        return runs
    cuts = [tuple(map(int, m)) for m in re.findall(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)" fill="#000"', svg)]
    covers = lambda run, c: c[1] <= run[0] and c[1] + c[3] >= run[1]
    s_runs, p_runs = rows("S", 316, 350), rows("P", 215, 240)
    ok(covers(s_runs[0], cuts[0]) and covers(s_runs[-1], cuts[1]), f"S: cuts break the top and bottom curves {s_runs[0]} {s_runs[-1]}")
    pc = cuts[2]
    ok(all(covers(r, (0, pc[1], 0, pc[3])) for r in p_runs), f"P: the bowl is lifted off the stem at every join {p_runs}")
except (OSError, ImportError) as ex:
    print(f"  건너뜀  stencil ({ex})")

print("[techniques · mood]")
ok(len(PI.TECHNIQUES) >= PI.MIN_TECHNIQUES, f"{len(PI.TECHNIQUES)} techniques registered, each with a source")
ok(all(src for _, src in PI.TECHNIQUES.values()), "every technique names where it came from")
ok(set(spec["mood_reference"]["tokens"].values()) <= {PI.PAPER, PI.INK, PI.MUTE_RAW, PI.LINE, PI.ACCENT_RAW, PI.GREY},
   "the page tokens are the VISUAL INDEX tokens")
svg = PI.image_in_type("STOP", "x.jpg")
ok("<pattern" in svg and "background-clip" not in svg, "image-in-type is an SVG pattern fill (background-clip left PDF seams)")
bc = PI.barcode_svg("SPA-00")
ok(bc.count("<rect") == 8 * 5, "the barcode encodes exactly '*SPA-00*' (8 characters × 5 bars) -- no ISSN, no price")

print("[typography rules]")
ok(PI.KO_SPACING.search("SKP-S 의 주제") and PI.KO_SPACING.search("‘Sunshine’ 도 숨을") and not PI.KO_SPACING.search("SKP-S의 주제"),
   "RED/GREEN: a space before a Korean particle after a Latin word is caught; none is not")
ok(abs(PI.X(11, "r") + PI.COL - (100 - PI.OUTER)) < 0.01 and abs(PI.X(11, "l") + PI.COL - (100 - PI.INNER)) < 0.01 and PI.X(0, "l") < PI.X(0, "r"),
   "mirrored grid: 12 columns fill each page; the binding side is wider")

if not PDF.available():
    print("  건너뜀  build (Chromium not found)")
else:
    print("[build: large stand-ins]")
    big = Path(임시) / "big"
    stand_ins(big, 4000, 2205)   # a full-height page of a 16:9 photo needs ~1,800 px of height at 150 dpi
    r = PI.build(spec_with(big), name="big")
    ok(r["pdf_result"] and r["pdf_result"]["pages"] == r["pages"] == 26, f"26 pages in HTML and PDF ({r['pdf_result'] and r['pdf_result']['pages']})")
    ok(status(r["checks"], "every photo appears") == "PASS", "every photo appears at least once")
    ok(status(r["checks"], "text overflow") == "PASS", "nothing overflows at print size")
    pres_ = next(c for c in r["checks"] if c["check"].startswith("print resolution"))
    ok(pres_["status"] == "PASS", f"GREEN: 4000 px photos print sharp (2400 px did not: the night spread crops to full height) -- {pres_['detail'][:120]}")
    ok(status(r["checks"], "user texts are verbatim") == "PASS", "texts verbatim in the build")
    ok(status(r["checks"], "phone width") in ("PASS", "NOT_CHECKED"), f"phone width: {status(r['checks'], 'phone width')}")
    ok(r["verdict"] in ("PASS", "WARNING"), f"verdict {r['verdict']} (WARNING: the lens cites snippets)")
    html = Path(r["html"]).read_text(encoding="utf-8")
    ok("독립 콘셉트 매거진" in html and "Gemini" not in html, "independence line on the back; no model named in the page")

    for name in ("blocks sit on the mirrored 12-column grid", "no faux-bold Korean", "smallest text at print size", "no text block overlaps another (print",
                 "no text block overlaps another (375", "story sections appear", "the night stop comes after",
                 "contents page numbers", "no space between a Latin word", "text contrast", "VISUAL INDEX tokens are the page's tokens",
                 "photos at the catalogue's saturate(.78)", "every registered technique is on a page", "at least 20 techniques", "even page count"):     # 'catalogue red agrees' is about the real cover photo, not stand-ins
        ok(status(r["checks"], name) == "PASS", f"GREEN: {name}")

    print("[RED: break the layout on purpose]")
    red = Path(r["dir"]).parent / "red"
    shutil.copytree(Path(r["dir"]), red)
    h = (red / "index.html").read_text(encoding="utf-8")
    h = h.replace('data-technique="white_space" style="', 'data-technique="white_space" style="margin-top:-24cqw;', 1)   # 'In this issue' onto the standfirst
    h = h.replace('<p class="ko" lang="ko" style="font-size:', '<p class="ko" lang="ko" style="font-weight:700;font-size:', 1)   # Korean set bold
    h = h.replace('data-technique="text_columns" style="', 'data-technique="text_columns" style="margin-left:1.3cqw;', 1)
    (red / "index.html").write_text(h, encoding="utf-8")
    m = PDF.measure(red / "index.html", 869, 1134, "qa-print")
    pg = {p["i"]: p for p in m["pages"]}
    ok(any(p.get("clash") for p in m["pages"]), "RED: a title pushed onto the text is reported as an overlap")
    ok(any(p.get("faux") for p in m["pages"]), "RED: Korean set bold is reported as faux bold")
    ok(any(abs(c_["x"] - PI.X(c_["col"], c_["mirror"] or "r")) > 0.3 for p in m["pages"] for c_ in p.get("cols", [])), "RED: a block nudged 1.3 cqw off its column is reported")

    print("[build: screenshot-size stand-ins]")
    small = Path(임시) / "small"
    stand_ins(small, 468, 258)
    r = PI.build(spec_with(small), name="small", pdf=False)
    ok(status(r["checks"], "print resolution") == "FAIL", "RED: 468 px photos fail the print-resolution check")

    print("[build: a photo missing]")
    (small / "07.png").unlink()
    r = PI.build(spec_with(small), name="missing", pdf=False)
    ok(status(r["checks"], "every photo in the spec is on disk") == "FAIL", "RED: a missing photo fails")

shutil.rmtree(임시, ignore_errors=True)
print(f"\n{'FAILED ' + str(len(FAIL)) if FAIL else 'ALL OK'}")
sys.exit(1 if FAIL else 0)
