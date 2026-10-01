"""gentle_monster: synopsis -> layout PDF -> (on request) blueprint + MP4. Runs without an LLM or Discord.

What this holds -- the failures that actually happened while building it:
  1. The hand-drawn circulation of the four first spaces walked through objects in four places
     (a closed wire gate, two candle sculptures, a basin rim). Nobody saw it until a camera walked it.
     So every layout is measured: the path keeps >= 0.3 m from every solid item. RED/GREEN below.
  2. A model told "rule X failed" learns to satisfy the checker. The retry prompt must carry facts
     about the layout (item id and coordinates), not rule names.
  3. Default = synopsis + layout PDF only; blueprint and MP4 only on request.
Browser parts (layout PDF, stills) are skipped with '건너뜀' when Chromium cannot start.
Run: python3 tests/test_gentle_monster.py
"""
from __future__ import annotations

import ast  # noqa: F401
import copy
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

뿌리 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(뿌리))
임시 = tempfile.mkdtemp(prefix="gmtest-")
os.environ["GENTLE_MONSTER_OUT"] = 임시          # outputs outside the repository

from gentle_monster import discord_cmd, paths, pipeline, spec, synopsis  # noqa: E402

FAIL = []


def ok(cond, what):
    print(("  ok  " if cond else "  FAIL ") + what)
    if not cond:
        FAIL.append(what)


print("== bundled examples pass the check (GREEN) ==")
EX = spec.examples()
ok(set(EX) == {"gm", "tb", "ac", "ae"}, "four bundled spaces: gm tb ac ae")
for k, j in EX.items():
    bad = spec.check(j)
    ok(not bad, f"{k}: no problems" + ("" if not bad else f" -- {bad[:2]}"))
    d, where, _ = spec.clearance(j["layout"])
    ok(d >= spec.CLEAR, f"{k}: circulation keeps {d:.2f} m from {where} (>= {spec.CLEAR})")

print("\n== the checker catches what went wrong before (RED) ==")
tb = copy.deepcopy(EX["tb"])
c2 = next(i for i in tb["layout"]["items"] if i["id"] == "candle2")
cx, cy = (c2["x0"] + c2["x1"]) / 2, (c2["y0"] + c2["y1"]) / 2
tb["layout"]["flows"][0]["pts"].insert(4, [cx, cy])                  # walk straight through a candle
bad = spec.check(tb)
ok(any("candle2" in b and "inside" in b for b in bad), "a path through candle2 is reported with the item id")
ok(any("x %.1f" % c2["x0"] in b for b in bad), "... and with its coordinates (a fact, not a rule name)")

gm = copy.deepcopy(EX["gm"])
wl = next(i for i in gm["layout"]["items"] if i["id"] == "wire_l")
wl["x1"] = 12.8                                                       # close the passage in the wire gate
gm["layout"]["items"] = [i for i in gm["layout"]["items"] if i["id"] != "wire_r"]
ok(any("wire_l" in b for b in spec.check(gm)), "a closed wire gate on the path is reported")

ae = copy.deepcopy(EX["ae"])
ae["layout"]["flows"][0]["pts"][2] = [5.2, 4.9]                     # graze the round basin
ok(any("basin" in b for b in spec.check(ae)), "a path over the basin rim is reported (round footprint)")

x = copy.deepcopy(EX["ac"])
door = next(i for i in x["layout"]["items"] if i["type"] == "door")
door["y0"], door["y1"] = 5, 5.2
ok(any("street edge" in b for b in spec.check(x)), "a door off the street edge is reported")
x = copy.deepcopy(EX["ac"])
x["stops"][0]["at"] = [16.5, 1.0]
ok(any("off the circulation" in b for b in spec.check(x)), "a stop off the path is reported")
x = copy.deepcopy(EX["ac"])
x["title"] = "모놀리스"
ok(any("Korean" in b for b in spec.check(x)), "Korean text on an English page is reported")
x = copy.deepcopy(EX["ac"])
m = next(i for i in x["layout"]["items"] if i["id"] == "mono_a")
m2 = dict(m, id="mono_z", x0=m["x0"] + .2, x1=m["x1"] + .2)
x["layout"]["items"].append(m2)
ok(any("overlap" in b and "mono_z" in b for b in spec.check(x)), "overlapping solid items are reported")

print("\n== synopsis: model writes, code judges ==")
prompts = []
good = json.dumps(EX["ae"])


def fake(p, answers=[json.dumps(tb), "not json at all", good]):
    prompts.append(p)
    return answers[len(prompts) - 1]


r = synopsis.generate("an apothecary with a water ritual", ask=fake, rounds=3)
ok(r["job"] is not None and r["rounds"] == 3, "a bad draft and a non-JSON reply are retried; the third (valid) is kept")
ok("candle2" in prompts[1] and "must change" in prompts[1], "the retry carries the facts about the failed layout")
ok("CLEAR" not in prompts[1] and "spec.check" not in prompts[1], "the retry does not name the checker's rules")
ok("not a parseable JSON" in prompts[2], "a non-JSON reply is told so")
r = synopsis.generate("x", ask=lambda p: json.dumps(tb), rounds=2)
ok(r["job"] is None and r["problems"], "a layout that never passes is not handed on (job None + problems)")
p0 = synopsis.prompt("brief", "")
ok("Return ONLY a JSON object" in p0 and "0.3 m" in p0, "the prompt states the output form and the clearance in metres")
ok(all(s in p0 for s in spec.SHAPES) and all(m in p0 for m in spec.MATERIALS), "the prompt lists every shape and material the scene can build")

print("\n== pipeline: default is synopsis + layout only ==")
pipeline.synopsis("t_ex", example="gm", log=lambda s: None)
ok((Path(임시) / "t_ex" / "job.json").is_file() and (Path(임시) / "t_ex" / "synopsis.md").is_file(), "job.json + synopsis.md written outside the repo")
st = pipeline.status("t_ex")
ok(st["synopsis"] and not st["blueprint"] and not st["video"], "no blueprint or video unless asked")
try:
    pipeline.load_job("does_not_exist")
    ok(False, "missing job raises")
except FileNotFoundError:
    ok(True, "a missing job raises FileNotFoundError with a hint")
ok(paths.job_dir("../../etc").resolve().parent == Path(임시).resolve(), "job names cannot walk out of the output folder")
for esc in ("../../etc/passwd", "/etc/passwd", "inbox/discord_attachments/../../x.png"):
    try:
        paths.resolve_photo(esc)
        ok(False, f"photo path {esc} blocked")
    except ValueError:
        ok(True, f"photo path {esc} blocked")

print("\n== !젠몬 command ==")
calls = []
fake_run = lambda argv, log, what: (calls.append(argv), "시작 (가짜)")[1]
ok(discord_cmd.run("hello", fake_run) is None and discord_cmd.run("!젠몬예제", fake_run) is None, "unknown text returns None")
ok("레이아웃 PDF" in discord_cmd.run("!젠몬", fake_run), "bare !젠몬 is help")
out = discord_cmd.run("!젠몬 비 오는 밤의 문턱을 주제로 한 플래그십", fake_run)
ok(calls and calls[-1][3] == "make" and "--full" not in calls[-1], "a brief launches make without --full (default steps only)")
discord_cmd.run("!젠몬 전부 비 오는 밤의 문턱을 주제로 한 플래그십", fake_run)
ok("--full" in calls[-1], "'전부' asks for blueprint + MP4")
ok("없다" in discord_cmd.run("!젠몬 영상 nope", fake_run), "video for an unknown job is refused before launching")
src = (뿌리 / "gentle_monster" / "discord_cmd.py").read_text(encoding="utf-8")
top = [n for n in ast.parse(src).body if isinstance(n, (ast.Import, ast.ImportFrom))]
ok(all(getattr(n, "module", "") in ("__future__", "sys", "time", "pathlib") or all(a.name in ("sys", "time") for a in getattr(n, "names", [])) for n in top),
   "discord_cmd imports only light modules at top level (G012)")

print("\n== !젠몬 natural language (intent.parse) ==")
from gentle_monster import intent  # noqa: E402
J = ["ex_gm_0930", "gm_0930101010"]
for 말, n, 기대 in (
        ("!젠몬", 0, ("help", "")), ("!젠몬 목록", 0, ("list", "")), ("!젠몬 예제 tb", 0, ("example", "")),
        ("!젠몬 탬버린즈 예제로 무드보드", 0, ("example", "")), ("!젠몬 이솝 예제로 해줘", 0, ("example", "")),
        ("!젠몬 비 오는 밤의 문턱을 주제로 한 성수 플래그십", 0, ("make", "")),
        ("!젠몬 방금 거 영상도 뽑아줘", 0, ("video", "gm_0930101010")),
        ("!젠몬 청사진 ex_gm_0930", 0, ("blueprint", "ex_gm_0930")),
        ("!젠몬 이 레퍼런스처럼 무드보드 다시 만들어줘", 2, ("layout", "gm_0930101010")),
        ("!젠몬 아까 그거 사진 넣어서 다시", 4, ("layout", "gm_0930101010")),
        ("!젠몬 영상 nope_job", 0, ("missing_job", "nope_job")),
        ("!젠몬 ㅎㅇ", 0, ("unclear", ""))):
    r = intent.parse(말, J, n_images=n)
    ok((r["action"], r["job"]) == 기대, f"{말!r} (+{n} images) -> {기대}  [got {r['action']}, {r['job']!r}]")
r = intent.parse("!젠몬 비 오는 밤의 성수 플래그십, 청사진이랑 영상까지 전부", J)
ok(r["action"] == "make" and r["steps"] == ["blueprint", "video"], "a brief with '전부' is make + blueprint + video")
ok(intent.parse("!젠몬 예제 tb", J)["example"] == "tb" and intent.parse("!젠몬 탬버린즈 예제", J)["example"] == "tb", "the example id comes from the id or the brand name")
ok(intent.parse("!젠몬 청사진 gm_0930101010", J)["example"] == "", "'gm' inside a job name is not read as the gm example")
ok(intent.parse("!젠몬 예제 gm으로", J)["example"] == "gm", "an example id followed by a Korean particle is still read")
ok(intent.parse("!젠몬 이솝 느낌으로 오래된 약국을 층층이 쌓은 한남동 매장", J)["brief"].startswith("이솝"), "the brief keeps the user's own words")

print("\n== !젠몬 passes attachments ==")
calls.clear()
discord_cmd.run("!젠몬 비 오는 밤의 문턱을 주제로 한 플래그십", fake_run,
                images=["inbox/discord_attachments/a.webp", "inbox/discord_attachments/b.PNG", "inbox/discord_attachments/c.pdf"])
imgs = [calls[-1][i + 1] for i, a in enumerate(calls[-1]) if a == "--image"]
ok(imgs == ["inbox/discord_attachments/a.webp", "inbox/discord_attachments/b.PNG"], "image attachments become --image (pdf left out)")
ok("--text" in calls[-1], "the user's words go along, so reference hints ('이 레이아웃처럼') reach photos.split")
calls.clear()
discord_cmd.run("!젠몬 비 오는 밤의 문턱을 주제로 한 플래그십", fake_run)
ok("--image" not in calls[-1], "no attachments -> no --image")

print("\n== photos: measured, not guessed ==")
from PIL import Image, ImageDraw  # noqa: E402
import random  # noqa: E402
from gentle_monster import photos as PH  # noqa: E402
그림 = Path(임시) / "_imgs"
그림.mkdir(parents=True, exist_ok=True)
rnd = random.Random(7)
for i, (base, dark) in enumerate(((200, False), (15, True), (150, False))):   # noisy "photographs"
    im = Image.new("RGB", (400, 300))
    im.putdata([tuple(max(0, min(255, base + rnd.randint(-40, 40) + (c * 20 if not dark else 0))) for c in range(3)) for _ in range(400 * 300)])
    im.save(그림 / f"p{i}.png")
bd = Image.new("RGB", (600, 400), "white")                                    # a board screenshot: flat paper + boxes
dr = ImageDraw.Draw(bd)
for x in range(4):
    dr.rectangle([30 + x * 140, 60, 140 + x * 140, 220], fill=(60 + x * 40, 60, 60))
dr.text((30, 20), "MAGAZINE", fill="black")
bd.save(그림 / "board.png")
sc = {f: PH.reference_score(그림 / f) for f in ("p0.png", "p1.png", "p2.png", "board.png")}
ok(max(sc[f] for f in ("p0.png", "p1.png", "p2.png")) < PH.REF_THRESHOLD <= sc["board.png"], f"flat-block share separates photos from a board ({sc})")
ph, rf = PH.split([str(그림 / f) for f in ("p0.png", "p1.png", "board.png")])
ok(rf == [str(그림 / "board.png")] and len(ph) == 2, "split: the board is the reference, the rest are photos")
shutil.copy(그림 / "p2.png", 그림 / "my_ref.png")
ok(PH.split([str(그림 / "my_ref.png")])[1], "a file named ref is a reference even if it looks like a photo")
m = PH.measure(그림 / "p1.png")
ok(m["dark"] > .5 and m["brightness"] < .3, "the dark photo measures dark")
rs = PH.reference_style(그림 / "board.png")
ok(rs["paper"] == "#ffffff" and not rs["dark_paper"], "reference paper colour is measured from the border")

print("\n== moodboard: pool order (no browser) ==")
from gentle_monster import moodboard as MB  # noqa: E402
pool = MB.Pool([str(그림 / f) for f in ("p0.png", "p1.png", "p2.png")])
sp = MB._spreads(EX["gm"], MB.style([], use_llm=False), pool, [("#000000", "")], [("a", "", "concrete")] * 4, None)
hero, bl, back = pool.used[1], pool.used[0], pool.used[2]
ok(bl["path"].endswith("p1.png"), "the darkest photo is kept for the full bleed even though the pool is ranked by strength")
ok(len({hero["path"], bl["path"], back["path"]}) == 3, "cover, bleed and back cover are three different photos")
more = pool.take()
ok("p1.png" in sp["bleed"] and "p1.png" not in sp["cover"], "the spreads put the dark photo on the bleed, not the cover")
ok(more.get("detail") and not more.get("texture"), "when photos run out an image comes back as a detail crop, not a flat texture")
ok(MB.Pool([]).take().get("texture"), "a texture only when there is no image at all")
ok(MB._short("Graphite and red wax under every step.") == "Graphite and red wax under", "captions are cut at a word boundary")
ok(set(MB.style([str(그림 / "board.png")], use_llm=False)["sequence"]) <= set(MB.CATALOG), "a measured reference keeps a valid spread sequence")
bad = MB._llm_read(str(그림 / "board.png"), ask_vision=lambda p, r: '{"sequence": ["hero", "grid"]}')
ok(bad is None, "a vision answer naming spreads outside the catalogue is thrown away")
good_v = MB._llm_read(str(그림 / "board.png"), ask_vision=lambda p, r: '{"sequence": ["cover", "bleed", "board", "sequence"], "masthead": "solid"}')
ok(good_v and good_v["sequence"][:2] == ["cover", "bleed"], "a valid vision answer sets the spread order")

print("\n== standalone ==")
ok("out/" in (뿌리 / ".gitignore").read_text(encoding="utf-8"), "outputs (out/) are never committed")
req = (뿌리 / "requirements.txt").read_text(encoding="utf-8")
ok(all(k in req for k in ("playwright", "pillow", "numpy", "matplotlib", "imageio-ffmpeg")), "requirements list every runtime dependency")
import importlib  # noqa: E402
for 모듈 in ("gentle_monster.llm", "gentle_monster.render", "render3d.plan", "render3d.layout"):
    try:
        importlib.import_module(모듈)
        ok(True, f"{모듈} imports without the SE repository")
    except Exception as e:                                # noqa: BLE001
        ok(False, f"{모듈} imports without the SE repository ({type(e).__name__}: {e})")
from gentle_monster import llm  # noqa: E402
_k = os.environ.pop("GEMINI_API_KEY", None), os.environ.pop("GOOGLE_API_KEY", None)
try:
    llm.ask("x")
    ok(False, "no key -> RuntimeError")
except RuntimeError:
    ok(True, "no Gemini key -> the call says so (no other model is substituted)")
for n, v in zip(("GEMINI_API_KEY", "GOOGLE_API_KEY"), _k):
    if v:
        os.environ[n] = v

print("\n== browser parts (layout PDF, stills) ==")
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        paths.launch(p).close()
    browser = True
except Exception as e:                                    # noqa: BLE001
    browser = False
    print(f"  건너뜀 -- no browser here ({type(e).__name__})")
if browser:
    r = pipeline.layout("t_ex", use_llm=False, log=lambda s: None)
    pdf = Path(r["pdf"])
    ok(pdf.is_file() and pdf.read_bytes()[:4] == b"%PDF", "layout.pdf is a PDF")
    ok(pdf.read_bytes().count(b"/Type /Page") - pdf.read_bytes().count(b"/Type /Pages") == 1, "the layout is exactly one page")
    import re
    html = (Path(임시) / "t_ex" / "layout.html").read_text(encoding="utf-8")
    ok(not re.search("[가-힣]", html), "the layout page has no Korean text")
    ok("moodboard" in r and Path(r["moodboard"]).read_bytes()[:4] == b"%PDF", "the default step also makes the moodboard PDF")
    mb = Path(r["moodboard"]).read_bytes()
    ok(mb.count(b"/Type /Page") - mb.count(b"/Type /Pages") == 8, "the moodboard is eight spreads")
    ok(len(list((Path(임시) / "t_ex").glob("render_*.png"))) == len(pipeline.MOOD_VIEWS), "with fewer than 3 photos the room's renders fill the board")
    ok(not re.search("[가-힣]", (Path(임시) / "t_ex" / "moodboard.html").read_text(encoding="utf-8")), "the moodboard has no Korean text")
    r2 = pipeline.layout("t_ex", images=[str(그림 / f) for f in ("p0.png", "p1.png", "p2.png", "board.png")], use_llm=False, log=lambda s: None)
    ok(len(list((Path(임시) / "t_ex" / "photos").iterdir())) == 3 and len(list((Path(임시) / "t_ex" / "refs").iterdir())) == 1,
       "photos and the reference are kept in the job folder (split by measurement)")
    ok(r2["moodboard_info"]["style"]["measured"] and r2["moodboard_info"]["generated_fills"] == 0, "3 photos + a reference: the reference is measured, no generated fills")
    from gentle_monster import render
    rs = render.stills(spec.examples()["tb"], paths.job_dir("t_still"), views=("cut",), w=480, h=300)
    ok(Path(rs["cut"]).stat().st_size > 5000, "the photoreal scene renders a cutaway still without errors")

shutil.rmtree(임시, ignore_errors=True)
print(f"\n{'실패 ' + str(len(FAIL)) if FAIL else '전부 통과'}")
sys.exit(1 if FAIL else 0)
