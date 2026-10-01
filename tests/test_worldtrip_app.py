"""worldtrip 앱 화면 (gentle_monster/apps/worldtrip) -- 엔진 심판의 V 로 잰다.

  1. 정적: 경로가 전부 상대 경로다(어디에 올려도 돈다) · 외부 주소를 부르지 않는다 · 엔진 주소를 바꿀 수 있다 ·
     JS 문법(node 가 있으면)
  2. GREEN: 고정 응답(tests/fixtures/worldtrip, 진짜 엔진이 낸 것)으로 계획 ACCEPT · REJECT · 탐색 화면이 V 를 다 지킨다
  3. RED: 한 가지씩 깨뜨린 화면이 **바로 그 검사**를 실패한다 -- 안 그러면 위의 GREEN 은 아무것도 안 잰 것이다
브라우저가 없으면 2·3 은 '건너뜀'.
Run: python3 tests/test_worldtrip_app.py
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

뿌리 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(뿌리))
APP = 뿌리 / "gentle_monster" / "apps" / "worldtrip"
FIX = 뿌리 / "tests" / "fixtures" / "worldtrip"
FAIL = []


def ok(cond, what):
    print(("  ok  " if cond else "  FAIL ") + what)
    if not cond:
        FAIL.append(what)


print("== static ==")
html = (APP / "index.html").read_text(encoding="utf-8")
js = (APP / "app.js").read_text(encoding="utf-8")
css = (APP / "app.css").read_text(encoding="utf-8")
ok(not re.search(r'(href|src)="/', html), "index.html 의 경로가 전부 상대 경로다")
# 실제로 부르는 자리만 본다: html 속성 · css url() · js 문자열. 주석 속 예시 주소는 부르는 것이 아니다
Q = "[\"'`]"
loads = (re.findall(r'(?:href|src)="(https?://[^"]+)"', html)
         + re.findall(r"url\(" + Q + r"?(https?://[^)\"']+)", css)
         + [u for u in re.findall(Q + r"(https?://[^\"'`]*)", js)
            if u not in ("http://www.w3.org/2000/svg", "https://엔진주소 (비우면 같은 출처)")])
ok(not loads, f"외부 주소를 부르지 않는다(글꼴·CDN 없음) {loads[:3]}")
ok("fetch(API + path" in js and 'name="worldtrip-api"' in html, "엔진 주소를 바꿀 수 있다(meta · ?api= · 저장값)")
ok(not re.search(r"font-size:\s*(\d|1[01])(\.\d+)?px", css), "CSS 에 12px 아래 글자가 없다")
for f in ("plan", "plan_reject", "explore", "city", "ledger", "status"):
    ok((FIX / f"{f}.json").is_file(), f"고정 응답 {f}.json")
ok(json.loads((FIX / "plan.json").read_text())["verdict"] == "ACCEPT" and json.loads((FIX / "plan_reject.json").read_text())["verdict"] == "REJECT",
   "고정 응답이 ACCEPT 와 REJECT 를 둘 다 담는다")
if shutil.which("node"):
    for f in ("app.js", "sw.js"):
        r = subprocess.run(["node", "--check", str(APP / f)], capture_output=True, text=True)
        ok(r.returncode == 0, f"node --check {f} {r.stderr.strip()[:120]}")
else:
    print("  건너뜀 node 가 없다")


def browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        from gentle_monster import paths
        with sync_playwright() as p:
            paths.launch(p, gl=False).close()
        return True
    except Exception as e:  # noqa: BLE001
        print(f"  건너뜀 브라우저를 못 띄웠다: {type(e).__name__}")
        return False


if browser_ok():
    from gentle_monster.apps import check

    print("== GREEN: 고정 응답으로 세 상태 x 두 폭 ==")
    g = check.measure()
    for k, v in g["V"].items():
        ok(v, f"V {k}")
    print("   ", {k: g["facts"][k] for k in ("min-contrast", "min-font-375", "text-items", "bytes")})

    print("== RED: 한 가지씩 깨뜨리면 그 검사가 실패한다 ==")
    breaks = {
        "offline": ("index.html", '<link rel="stylesheet" href="app.css">',
                    '<link rel="stylesheet" href="app.css"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo">'),
        "min-font-375": ("app.css", ".small{font-size:13px}", ".small{font-size:9px}"),
        "contrast-rendered": ("app.css", "--sub:#66665f;", "--sub:#c4c4bd;"),
        "headings": ("index.html", '<h2 id="ex-h"', '<h1 id="ex-h2">x</h1><h2 id="ex-h"'),
        "js-errors": ("app.js", "function buildBrief() {", "function buildBrief() {\n    undefinedThing.go();"),
        "overflow-375": ("app.css", ".cover{display:grid;", ".cover{min-width:900px;display:grid;"),
    }
    for want, (f, a, b) in breaks.items():
        d = Path(tempfile.mkdtemp(prefix="wtred-")) / "app"
        shutil.copytree(APP, d)
        src = (d / f).read_text(encoding="utf-8")
        if a not in src:
            ok(False, f"RED {want}: 깨뜨릴 자리 {a!r} 가 {f} 에 없다")
            continue
        (d / f).write_text(src.replace(a, b, 1), encoding="utf-8")
        try:
            r = check.measure(app=d)
            failed = [k for k, v in r["V"].items() if not v]
        except Exception as e:  # noqa: BLE001 -- 화면이 아예 안 그려져도 '실패' 로 잡혀야 한다
            failed = [f"(측정 불가: {type(e).__name__})"]
        ok(want in failed, f"RED {want}: 실패한 검사 {failed}")

print()
print("FAIL" if FAIL else "OK", len(FAIL))
sys.exit(1 if FAIL else 0)
