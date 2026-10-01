"""worldplan 앱 화면 (gentle_monster/apps/worldplan) -- 엔진 심판의 V 로 잰다(apps/check 의 worldtrip 과 같은 판정 함수).

  1. 정적: 경로가 전부 상대 경로다 · 외부 주소를 부르지 않는다 · 엔진 주소를 바꿀 수 있다 · 토큰이 엔진과 같다 · JS 문법
  2. GREEN: 고정 응답(tests/fixtures/worldplan, 진짜 엔진이 낸 것)으로 계획 ACCEPT · REJECT · 물어보기가 V 를 다 지킨다
  3. RED: 한 가지씩 깨뜨린 화면이 **바로 그 검사**를 실패한다
브라우저가 없으면 2·3 은 '건너뜀'.
Run: python3 tests/test_worldplan_app.py
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
APP = 뿌리 / "gentle_monster" / "apps" / "worldplan"
FIX = 뿌리 / "tests" / "fixtures" / "worldplan"
FAIL = []


def ok(cond, what):
    print(("  ok  " if cond else "  FAIL ") + what)
    if not cond:
        FAIL.append(what)


print("== static ==")
html = (APP / "index.html").read_text(encoding="utf-8")
js = (APP / "app.js").read_text(encoding="utf-8")
css = (APP / "app.css").read_text(encoding="utf-8") + (APP / "tokens.css").read_text(encoding="utf-8")
ok(not re.search(r'(href|src)="/', html), "index.html 의 경로가 전부 상대 경로다(어디에 붙여도 돈다)")
loads = (re.findall(r'(?:href|src)="(https?://[^"]+)"', html) + re.findall(r"url\([\"']?(https?://[^)\"']+)", css)
         + re.findall(r"fetch\([\"'`](https?://[^\"'`]+)", js))
ok(not loads, f"외부 주소를 부르지 않는다 {loads[:3]}")
ok("fetch(API + path" in js and 'name="worldplan-api"' in html, "엔진 주소를 바꿀 수 있다(meta · ?api=)")
ok(not re.search(r"font-size:\s*(\d|1[01])(\.\d+)?px", css), "CSS 에 12px 아래 글자가 없다")
from gentle_monster.apps import worldplan_tokens  # noqa: E402
from gentle_monster.engine import tokens as T     # noqa: E402
want = T.css_vars(worldplan_tokens.tokens())
ok(want in (APP / "tokens.css").read_text(encoding="utf-8"), "tokens.css 가 엔진이 지금 짓는 토큰과 같다(손으로 고치지 않았다)")
for f in ("sample", "plan", "plan_reject", "assistant"):
    ok((FIX / f"{f}.json").is_file(), f"고정 응답 {f}.json")
ok(json.loads((FIX / "plan.json").read_text())["verdict"] == "ACCEPT"
   and json.loads((FIX / "plan_reject.json").read_text())["verdict"] == "REJECT", "고정 응답이 ACCEPT 와 REJECT 를 둘 다 담는다")
if shutil.which("node"):
    r = subprocess.run(["node", "--check", str(APP / "app.js")], capture_output=True, text=True)
    ok(r.returncode == 0, f"node --check app.js {r.stderr.strip()[:120]}")
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
    g = check.measure_worldplan()
    for k, v in g["V"].items():
        ok(v, f"V {k}")
    print("   ", {k: g["facts"][k] for k in ("min-contrast", "min-font-375", "text-items", "bytes")})

    print("== RED: 한 가지씩 깨뜨리면 그 검사가 실패한다 ==")
    breaks = {
        "offline": ("index.html", '<link rel="stylesheet" href="app.css">',
                    '<link rel="stylesheet" href="app.css"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo">'),
        "contrast-rendered": ("app.css", ".hint{color:var(--sub);", ".hint{color:#d6d6d0;"),
        "headings": ("index.html", '<h2 id="ask-h">', '<h1>x</h1><h2 id="ask-h">'),
        "js-errors": ("app.js", "function drawClock() {", "function drawClock() {\n    undefinedThing.go();"),
        # 폰에서 표를 카드로 펴는 규칙을 빼면 계획 표가 화면 밖으로 나간다 -- 실제로 이 검사가 처음 잡은 결함이다
        "overflow-375": ("app.css", "@media (max-width:599px){", "@media (max-width:1px){"),
        "rendered": ("app.js", 'render(await call("/api/plan", { request: req }), req);', "await call(\"/api/plan\", { request: req });"),
    }
    for want, (f, a, b) in breaks.items():
        d = Path(tempfile.mkdtemp(prefix="wpred-")) / "app"
        shutil.copytree(APP, d)
        src = (d / f).read_text(encoding="utf-8")
        if a not in src:
            ok(False, f"RED {want}: 깨뜨릴 자리 {a!r} 가 {f} 에 없다")
            continue
        (d / f).write_text(src.replace(a, b, 1), encoding="utf-8")
        try:
            r = check.measure_worldplan(app=d)
            failed = [k for k, v in r["V"].items() if not v]
        except Exception as e:  # noqa: BLE001
            failed = [f"(측정 불가: {type(e).__name__})"]
        ok(want in failed, f"RED {want}: 실패한 검사 {failed}")

print()
print("FAIL" if FAIL else "OK", len(FAIL))
sys.exit(1 if FAIL else 0)
