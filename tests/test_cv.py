"""cv: a one-page CV in the SPA design (editorial/cv/test_cv.json).

Holds:
  1. Nothing is invented: every printed sentence is in its source document -- one changed word FAILS -- and
     every null field is printed as a red [blank] and counted; filling one lowers the count.
  2. Built with large stand-ins, in each of the three layouts (rows · split · creative): one A4 PDF page, nothing overflows, no block overlaps, fonts load,
     every block on the 12-column grid, print resolution PASSES.
  3. Broken on purpose, the page is caught: a block slid onto its neighbour is an overlap, a block nudged
     off its column is off the grid, 468 px photos (the screenshot crops) FAIL print resolution.
Run: python3 tests/test_cv.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

뿌리 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(뿌리))
임시 = tempfile.mkdtemp(prefix="gmcv-")
os.environ["GENTLE_MONSTER_OUT"] = 임시

from PIL import Image, ImageDraw  # noqa: E402

from gentle_monster.magazine import cv as CV, pdf as PDF  # noqa: E402

SPEC = 뿌리 / "editorial/cv/test_cv.json"
FAIL = []


def ok(cond, msg):
    print(("  ok  " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def status(checks, name):
    return next((c["status"] for c in checks if c["check"].startswith(name)), None)


def stand_ins(folder: Path, w: int, h: int):
    folder.mkdir(parents=True, exist_ok=True)
    for i in range(1, 16):
        im = Image.new("RGB", (w, h), (20 * i % 255, 90 + 9 * i, 200 - 11 * i))
        d = ImageDraw.Draw(im)
        for k in range(0, w, max(8, w // 40)):
            d.line((k, 0, w - k, h), fill=(255 - 15 * i % 255, 40 * (i % 5), 120), width=max(1, w // 400))
        im.save(folder / f"{i:02d}.png")


def spec_with(folder: Path, **change) -> Path:
    s = json.loads(SPEC.read_text(encoding="utf-8"))
    s["photo_dir"] = str(folder)
    for k, v in change.items():
        s[k] = v
    p = Path(임시) / f"spec-{folder.name}-{len(change)}.json"
    p.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
    return p


spec = json.loads(SPEC.read_text(encoding="utf-8"))
print("[texts · blanks]")
ok(CV.check_texts(spec) == [], "GREEN: printed sentences are in their sources")
bad = json.loads(json.dumps(spec))
bad["profile"]["ko"] = bad["profile"]["ko"].replace("멈추는", "머무는")
ok(CV.check_texts(bad) != [], "RED: one changed word in the profile FAILS")
bad = json.loads(json.dumps(spec))
bad["projects"][1]["title"] = "Invented Project"
ok(any("fact_source" in b for b in CV.check_texts(bad)), "RED: a project with no source document FAILS")
n0 = len(CV.blanks(spec))
filled = json.loads(json.dumps(spec))
filled["languages"][0]["level"] = "native"
ok(n0 > 0 and len(CV.blanks(filled)) == n0 - 1, f"filling a blank lowers the count ({n0} -> {n0 - 1})")

if not PDF.available():
    print("  -- Chromium not found: build checks skipped")
else:
    big = Path(임시) / "big"
    stand_ins(big, 4000, 2205)
    for lay in ("split", "creative", "rows"):                  # rows last: the RED copy below is made from it
        print(f"[build: large stand-ins · {lay}]")
        r = CV.build(spec_with(big), name="big", layout=lay)
        for name in ("printed sentences", "every photo in the spec", "nothing runs past", "no text block overlaps", "smallest text",
                     "Korean set only", "vendored Korean fonts", "blocks sit on the 12-column grid", "images load", "print resolution",
                     "PDF is one A4 page"):
            ok(status(r["checks"], name) == "PASS", f"GREEN {lay}: {name}")
        weak = [c["detail"] for c in r["checks"] if c["check"].startswith("text contrast") and c["status"] != "PASS"]
        ok(not weak, f"GREEN {lay}: every text/ground pair >= 4.5:1 " + "; ".join(weak))
        ok(status(r["checks"], "fields left for the applicant") == "WARNING", f"{lay}: blanks are reported, not hidden (WARNING)")

    print("[RED: break the page on purpose]")
    red = Path(r["dir"]).parent / "red"
    shutil.copytree(Path(r["dir"]), red)
    h = (red / "index.html").read_text(encoding="utf-8")
    i = h.index(">Profile<")
    j = h.rindex('style="left:', 0, i) + len('style="')
    h = h[:j] + "margin-left:-30cqw;" + h[j:]                  # the profile slid onto the portrait and the name
    (red / "index.html").write_text(h, encoding="utf-8")
    m = PDF.measure(red / "index.html", 794, 1123, "qa-print")
    p = m["pages"][0]
    ok(bool(p["clash"]), "RED: a block slid onto its neighbour is reported as an overlap")
    ok(any(abs(c["x"] - CV.X(c["col"]) / CV.W_MM * 100) > 0.3 for c in p["cols"]), "RED: the same block is off its column")

    print("[build: screenshot-size stand-ins]")
    small = Path(임시) / "small"
    stand_ins(small, 468, 258)
    r = CV.build(spec_with(small), name="small", pdf=False)
    ok(status(r["checks"], "print resolution") == "FAIL", "RED: 468 px photos FAIL print resolution")

shutil.rmtree(임시, ignore_errors=True)
print(f"\n{'FAILED ' + str(len(FAIL)) if FAIL else 'ALL OK'}")
sys.exit(1 if FAIL else 0)
