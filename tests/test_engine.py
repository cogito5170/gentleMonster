"""gentle_monster frontend engine: tokens -> page -> browser judge -> se_new policy.

What this holds:
  1. The judge is shown to FAIL on pages that are broken in known ways (RED) and to pass the engine's
     own pages (GREEN). A judge that only ever says green has not been shown to measure anything.
  2. The policy: invariants before the objective, regressions refused, ties refused, content changes
     refused, default REJECT. Each branch is pinned with a fake measurement.
  3. The judge's resolution: J is compared at 0.01 -- the first run ACCEPTed a 0.003 air gain that was
     smaller than the change caused by the screenshot downscale alone.
Browser parts are skipped with '건너뜀' when Chromium cannot start.
Run: python3 tests/test_engine.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

뿌리 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(뿌리))
임시 = tempfile.mkdtemp(prefix="gmengine-")
os.environ["GENTLE_MONSTER_OUT"] = 임시

from gentle_monster import discord_cmd, intent, paths, spec  # noqa: E402
from gentle_monster import engine  # noqa: E402
from gentle_monster.engine import color as C, compose, judge, policy, tokens as T  # noqa: E402

FAIL = []


def ok(cond, what):
    print(("  ok  " if cond else "  FAIL ") + what)
    if not cond:
        FAIL.append(what)


EX = spec.examples()

print("== colour math ==")
ok(C.contrast("#000000", "#ffffff") == 21.0, "black on white is 21:1")
ok(C.contrast("#777777", "#777777") == 1.0, "a colour on itself is 1:1")
for fg, bg in (("#d7301f", "#0b0d0e"), ("#9aa3a8", "#fbfbfb"), ("#888888", "#999999")):
    ok(C.contrast(C.ensure(fg, bg, 4.5), bg) >= 4.5, f"ensure({fg} on {bg}) reaches 4.5:1")
ok(C.ensure("#000000", "#ffffff", 4.5) == "#000000", "ensure leaves a passing colour untouched")

print("\n== tokens ==")
for k, job in EX.items():
    g = T.genome0(job)
    t = T.tokens(job, g)
    ok(T.valid(g), f"{k}: genome0 is in range")
    ok(not judge.static(t)["fail"], f"{k}: token contrast pairs pass ({judge.static(t)['pairs']})")
    ok(T.tokens(job, g) == t, f"{k}: tokens are deterministic")
d = T.dtcg(T.tokens(EX["gm"], T.genome0(EX["gm"])))
ok(d["color"]["$type"] == "color" and all("$value" in v for k, v in d["color"].items() if not k.startswith("$")), "DTCG export: every colour has $value")
ok(T.theme(EX["gm"]) == "dark" and T.theme(EX["tb"]) == "light", "room.light sets the theme (dark_gallery -> dark)")

print("\n== operators stay inside the genome ==")
g = T.genome0(EX["gm"])
for name, f in policy.OPERATORS.items():
    ok(T.valid(f(g)), f"{name} keeps the genome valid")
edge = dict(g, ratio=T.GENES["ratio"][-1])
ok(policy.OPERATORS["scale-up"](edge) == edge, "a step past the end of a gene is a no-op, not a wrap")

print("\n== compose: offline, English, content does not depend on the genome ==")
strip = lambda h: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<footer.*?</footer>|<style>.*?</style>|<script>.*?</script>", "", h, flags=re.S))).strip()
for k, job in EX.items():
    h = compose.page(job, T.tokens(job, T.genome0(job)))
    ok(not re.search(r"(?:src|href)=\"https?:", h) and "@import" not in h, f"{k}: no network reference in the page")
    ok(not re.search("[가-힣]", h), f"{k}: no Korean text on the page")
texts = {" ".join(sorted(strip(compose.page(EX["tb"], T.tokens(EX["tb"], f(T.genome0(EX["tb"]))))).split()))
         for f in policy.OPERATORS.values()}                  # sorted: the sequence operator reorders sections
ok(len(texts) == 1, "every operator changes how the room is told, not what is told (same visible text)")

print("\n== policy (se_new): invariants first, regressions and ties refused, default REJECT ==")
V = {k: True for k in ("overflow-375", "contrast-rendered", "offline")}
J = {"drama": .9, "air": .7, "measure": .9}
base = {"V": V, "J": J, "score": .8333, "content": "c1"}
up = {"V": V, "J": dict(J, air=.75), "score": .85, "content": "c1"}
ok(policy.decide(base, up)["decision"] == "ACCEPT", "V holds, nothing fell, J rose -> ACCEPT")
r = policy.decide(base, dict(up, V=dict(V, offline=False)))
ok(r["decision"] == "REJECT" and r["dJ"] is None, "an invariant fails -> REJECT, and ΔJ is not even computed")
r = policy.decide(base, {"V": V, "J": dict(J, air=.95, measure=.88), "score": .91, "content": "c1"})
ok(r["decision"] == "REJECT" and "regression" in r["why"][0], "J mean rose but one component fell -> REJECT (regression)")
ok(policy.decide(base, dict(base))["decision"] == "REJECT", "a tie is not an improvement -> REJECT")
ok(policy.decide(base, dict(up, content="c2"))["decision"] == "REJECT", "different visible content -> REJECT (it measured something else)")
ok(policy.decide(base, up, same_page=True)["decision"] == "REJECT", "same HTML -> REJECT (nothing changed)")
ok(policy.decide(None, up)["decision"] == "REJECT", "a missing measurement -> REJECT")
w0 = policy.weights([])
ok(set(w0.values()) == {1.0}, "π0 is uniform -- fair before clever")
w = policy.weights([{"op": "air-down", "decision": "ACCEPT"}] * 40
                   + [{"op": o, "decision": "REJECT"} for o in policy.OPERATORS if o != "air-down"] * 40)
ok(w["air-down"] == policy.CEIL and w["motion"] == policy.FLOOR, "π is clamped: no operator takes over, none is dropped")

print("\n== build with a fake judge: ledger, determinism, ships what was measured ==")


def fake(p, t):
    g = t["genome"]
    air = round(1 - abs(g["air"] - .8), 2)                 # this fake prefers air 0.8
    return {"V": {"x": True}, "J": {"air": air, "k": .5}, "score": round((air + .5) / 2, 4), "content": "same", "facts": {}}


r1 = engine.build(EX["ae"], Path(임시) / "f1", rounds=6, log=lambda s: None, measure=fake)
r2 = engine.build(EX["ae"], Path(임시) / "f2", rounds=6, log=lambda s: None, measure=fake)
rows = policy.read(r1["ledger"])
ok(len(rows) == 7 and rows[0]["decision"] == "BASE", "the ledger holds the base and every round, rejections included")
ok(r1["genome"]["air"] == .8 and r1["accepted"] >= 1, "the loop climbs to what the judge prefers (air 0.8)")
ok(r1["genome"] == r2["genome"] or r1["accepted"] == r2["accepted"], "same job -> same walk (seeded, not random)")
ok(json.loads(Path(r1["tokens"]).read_text())["$extensions"]["gentle_monster"]["genome"] == r1["genome"], "tokens.json carries the shipped genome")

print("\n== !젠몬 reads a web-page request ==")
it = intent.parse("방금 거 웹 사이트로", jobs=["a", "b"])
ok(it["action"] == "site" and it["job"] == "b", "'방금 거 웹 사이트로' -> site on the newest job")
it = intent.parse("비 오는 밤의 문턱을 주제로 한 성수 플래그십, 웹페이지까지", jobs=[])
ok(it["action"] == "make" and "site" in it["steps"], "a brief + '웹페이지까지' -> make with the site step")
seen = []
(Path(임시) / "j1").mkdir(exist_ok=True)
(Path(임시) / "j1" / "job.json").write_text(json.dumps(EX["gm"]), encoding="utf-8")
discord_cmd.run("!젠몬 j1 사이트로 만들어줘", runner=lambda argv, log, fw: seen.append(argv) or "started")
ok(seen and seen[0][-2:] == ["site", "j1"], "!젠몬 launches `site <job>`")

print("\n== browser judge: RED on broken pages, GREEN on the engine's pages ==")
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        paths.launch(p, gl=False).close()
    browser = True
except Exception as ex:                                    # noqa: BLE001
    browser = False
    print(f"  건너뜀 -- no browser here ({type(ex).__name__})")
if browser:
    job = EX["gm"]
    t = T.tokens(job, T.genome0(job))
    good = Path(임시) / "good.html"
    good.write_text(compose.page(job, t), encoding="utf-8")
    m = judge.measure(good, t)
    ok(all(m["V"].values()), f"GREEN: the engine's page holds every invariant ({[k for k, v in m['V'].items() if not v]})")
    ok(abs(m["facts"]["min-contrast"] - min(judge.static(t)["pairs"][k] for k in ("ink/bg", "sub/bg", "accent-text/bg"))) < .05,
       "two routes agree: lowest rendered contrast = lowest token pair")
    ok(all(0 <= x <= 1 for x in m["J"].values()) and all(round(x, 2) == x for x in m["J"].values()), "J components are in 0..1 at 0.01")
    src = good.read_text(encoding="utf-8")
    breaks = {
        "contrast-rendered": src.replace("</style>", ".why p{color:" + t["color"]["bg"] + "!important}</style>"),
        "overflow-375": src.replace("</style>", ".cue{width:900px;white-space:nowrap}</style>"),
        "offline": src.replace("</head>", '<link rel="stylesheet" href="https://fonts.example.com/x.css"></head>'),
        "reduced-motion": src.replace("</style>", "@keyframes z{to{opacity:.5}}.kicker{animation:z 9s infinite}</style>"),
        "names": src.replace('aria-label="generated texture', 'data-x="generated texture'),
        "headings": src.replace('<h2 id="h-syn"', '<h4 id="h-syn"').replace("Synopsis</h2>", "Synopsis</h4>"),
        "js-errors": src.replace("</body>", "<script>null.x</script></body>"),
    }
    for check, html in breaks.items():
        bp = Path(임시) / f"red_{check}.html"
        bp.write_text(html, encoding="utf-8")
        mb = judge.measure(bp, t)
        failed = [k for k, v in mb["V"].items() if not v]
        ok(failed == [check], f"RED: a page broken for `{check}` fails exactly that check (failed: {failed})")
    out = engine.build(EX["tb"], Path(임시) / "tb_site", rounds=2, log=lambda s: None)
    ok(out["ships"] and Path(out["html"]).is_file(), "the real loop ships a page that holds every invariant")
    ok(len(policy.read(out["ledger"])) == 3, "and its ledger has the base + 2 rounds")

shutil.rmtree(임시, ignore_errors=True)
print(f"\n{'실패 ' + str(len(FAIL)) if FAIL else '전부 통과'}")
sys.exit(1 if FAIL else 0)
