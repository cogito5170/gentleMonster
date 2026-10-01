"""앱 화면 검사 -- gentle_monster 엔진의 심판(engine/judge.py)을 **떠 있는 앱**에 건다.

엔진의 심판은 한 장짜리 정적 페이지(file://)를 잰다. 앱은 엔진 API 를 불러 화면을 짓는 동적 페이지라,
여기서는 같은 측정 코드(judge._JS_TEXT · judge._JS_DOC)를 **결과가 다 그려진 뒤의 화면**에 건다.
보는 상태는 셋이다: 계획 결과(ACCEPT) · 거절 결과(REJECT) · 탐색(트리 + 도시 안내). 폭은 375 · 1440.

    V -- 하나라도 안 서면 내보내지 않는다(모르는 것은 통과가 아니다)
        overflow-375 / overflow-1440   가로 스크롤 0 · 화면 밖으로 나간 글 상자 0
        contrast-rendered              보이는 글마다 계산된 색을 배경까지 합성해 >= 4.5 (큰 글 3)
        min-font-375                   폰에서 12px 아래 글 없음
        offline                        앱 출처(와 엔진) 밖으로 나가는 요청 0 -- 글꼴·CDN·추적기
        js-errors                      페이지 오류 0
        names                          그림·svg[role=img] 마다 접근 가능한 이름
        headings                       lang · h1 하나 · 제목 단계 건너뛰기 없음
        reduced-motion                 reduce 에서 도는 애니메이션 0
        weight                         앱 파일 합 <= 1.5 MB

엔진 없이 돌릴 때는 tests/fixtures/worldtrip/ 의 응답(진짜 엔진이 낸 것을 적어 둔 것)을 /api 에 끼운다.
떠 있는 엔진을 재려면 --url http://127.0.0.1:8766/ 을 준다.

    python3 -m gentle_monster.apps.check                 # 고정 응답으로
    python3 -m gentle_monster.apps.check --url URL        # 떠 있는 worldtrip 앱으로

이 검사가 **못** 보는 것: engine/judge 와 같다(그림 위 글의 대비, 가상 요소 ::after 가 가리는 정도).
그리고 표시하는 **값이 맞는지**는 보지 않는다 -- 그것은 worldtrip 엔진의 심판(T0–T7) 몫이다.
"""
from __future__ import annotations

import argparse
import functools
import json
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from gentle_monster import paths
from gentle_monster.engine.judge import _JS_DOC, _JS_TEXT

APP = Path(__file__).resolve().parent / "worldtrip"
FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "worldtrip"
MAX_BYTES = 1_500_000


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def _serve_static(root: Path):
    h = functools.partial(_Quiet, directory=str(root))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def _fixture_route(fx: Path, state: dict):
    def handle(route):
        u = urlparse(route.request.url).path
        name = {"/api/explore": "explore", "/api/city": "city", "/api/ledger": "ledger", "/api/status": "status"}.get(u)
        if u == "/api/plan":
            name = state.get("plan", "plan")
        if not name:
            return route.fulfill(status=404, body="{}", content_type="application/json")
        route.fulfill(status=200, body=(fx / f"{name}.json").read_text(encoding="utf-8"), content_type="application/json")
    return handle


def measure(url: "str | None" = None, fixtures: Path = FIXTURES, app: Path = APP) -> dict:
    """앱 하나를 잰다. url 이 없으면 정적 파일 + 고정 응답."""
    from playwright.sync_api import sync_playwright
    srv = None
    if url is None:
        srv, url = _serve_static(app)
    origin = "{0.scheme}://{0.netloc}".format(urlparse(url))
    ext, errs, raw = [], [], {}
    try:
        with sync_playwright() as p:
            b = paths.launch(p, gl=False)
            for w in (375, 1440):
                for state in ("plan", "plan_reject", "explore"):
                    ctx = b.new_context(viewport={"width": w, "height": 900}, reduced_motion="reduce")
                    ctx.route(lambda u: not u.startswith(origin), lambda r: (ext.append(r.request.url), r.abort()))
                    pg = ctx.new_page()
                    if srv is not None:
                        pg.route("**/api/**", _fixture_route(fixtures, {"plan": "plan" if state != "plan_reject" else "plan_reject"}))
                    pg.on("pageerror", lambda e_: errs.append(str(e_)))
                    try:
                        if state == "explore":
                            pg.goto(url + "#explore", wait_until="load")
                            pg.wait_for_selector(".cityrow", timeout=15000)
                            pg.locator(".cityrow").first.click()
                            pg.wait_for_selector("#guide .cityname", timeout=15000)
                        else:
                            pg.goto(url + "#plan", wait_until="load")
                            pg.wait_for_selector("#must .chip", timeout=15000)
                            pg.click(".go")
                            pg.wait_for_selector(".stamp", timeout=60000)
                    except Exception as e:  # noqa: BLE001 -- 안 그려진 화면도 재서 '안 그려졌다' 로 낸다(예외로 끝내지 않는다)
                        errs.append(f"{w}-{state}: 화면이 다 그려지지 않았다 ({type(e).__name__})")
                    pg.wait_for_timeout(150)
                    raw[f"{w}-{state}"] = {"doc": pg.evaluate(_JS_DOC), "text": pg.evaluate(_JS_TEXT),
                                           "verdict": pg.evaluate("() => (document.querySelector('.stamp')||{}).textContent || ''")}
                    ctx.close()
            b.close()
    finally:
        if srv is not None:
            srv.shutdown()
            srv.server_close()
    v, facts = {}, {"states": {}}
    for k, r in raw.items():
        facts["states"][k] = {"verdict": r["verdict"], "overflow": r["doc"]["overflow"], "cut": r["text"]["cut"][:3]}
    items = [x for r in raw.values() for x in r["text"]["items"]]
    low = sorted((x for x in items if x["ratio"] < x["need"]), key=lambda x: x["ratio"])
    unm = [x for r in raw.values() for x in r["text"]["unmeasured"]]
    v["overflow-375"] = all(r["doc"]["overflow"] <= 1 and not r["text"]["cut"] for k, r in raw.items() if k.startswith("375"))
    v["overflow-1440"] = all(r["doc"]["overflow"] <= 1 and not r["text"]["cut"] for k, r in raw.items() if k.startswith("1440"))
    v["contrast-rendered"] = bool(items) and not low and not unm
    sizes375 = [float(s) for k, r in raw.items() if k.startswith("375") for s in r["text"]["sizes"]]
    v["min-font-375"] = bool(sizes375) and min(sizes375) >= 12
    v["offline"] = not ext
    v["js-errors"] = not errs
    v["names"] = all(r["doc"]["unnamed"] == 0 for r in raw.values())
    v["headings"] = all(r["doc"]["lang"] != "" and r["doc"]["h1"] == 1 and r["doc"]["skip"] == 0 for r in raw.values())
    v["reduced-motion"] = all(r["doc"]["running"] == 0 for r in raw.values())
    size = sum(f.stat().st_size for f in app.iterdir() if f.is_file())
    v["weight"] = size <= MAX_BYTES
    # 사소한 설명 죽이기: 결과 화면이 실제로 그려졌나(빈 화면은 넘칠 것도 대비가 낮을 것도 없다)
    drawn = {k: r["verdict"] for k, r in raw.items() if not k.endswith("explore")}
    v["rendered"] = all(x.strip().lower() in ("accept", "reject") for x in drawn.values()) and len(items) > 50
    facts.update({"min-contrast": min((x["ratio"] for x in items), default=None), "low-contrast": low[:6], "unmeasured": unm[:6],
                  "external": ext[:6], "errors": [e[:200] for e in errs[:3]], "min-font-375": min(sizes375, default=None),
                  "text-items": len(items), "bytes": size, "fixtures": str(fixtures) if srv is not None else None, "url": url})
    return {"V": v, "ships": all(v.values()), "facts": facts}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gentle_monster.apps.check", description="worldtrip 앱 화면을 엔진 심판의 V 로 잰다")
    ap.add_argument("--url", help="떠 있는 앱 주소 (없으면 정적 파일 + 고정 응답)")
    a = ap.parse_args(argv)
    r = measure(a.url)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r["ships"] else 1


if __name__ == "__main__":
    sys.exit(main())
