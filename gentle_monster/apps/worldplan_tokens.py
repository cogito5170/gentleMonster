"""worldplan 화면의 디자인 토큰을 짓는다 -- apps/worldplan/tokens.css · tokens.json.

worldplan 을 이 엔진의 job 하나로 적는다(브랜드 · 팔레트 · 강조색 하나 · 조명 · 재료). engine.tokens 가 색(WCAG 대비까지
밀어 올린) · 유동 타입 스케일 · 8 px 간격 · 움직임을 계산한다. 화면은 지은 두 파일만 읽는다 -- 실행에 이 엔진이 필요 없다.

    python3 -m gentle_monster.apps.worldplan_tokens
"""
from __future__ import annotations

import json
from pathlib import Path

from gentle_monster.engine import tokens as T

APP = Path(__file__).resolve().parent / "worldplan"

# 밤의 남색(다른 시간대의 밤) · 종이 · 강조색 하나(지금 이 순간)
JOB = {
    "brand": "worldplan",
    "title": "World Schedule Planner",
    "room": {"light": "white_gallery"},
    "palette": [{"hex": "#0E1A2B"}, {"hex": "#F4F1EA"}, {"hex": "#3D5A80"}, {"hex": "#98A6B5"}],
    "accent": "#D9480F",
    "materials": [{"preset": "paper"}, {"preset": "concrete"}, {"preset": "steel"}, {"preset": "glass"}],
}
# 시간표를 다루는 도구라 움직임은 없다(still) -- 표는 읽혀야 하고, 움직이면 안 된다
GENOME = {"ratio": 1.25, "air": 1.0, "cols": 12, "tension": 0, "mast": "solid", "voice": "grotesk",
          "motion": "still", "order": "intent-first"}


def tokens() -> dict:
    return T.tokens(JOB, GENOME)


def build(out: Path = APP) -> dict:
    t = tokens()
    css = ("/* gentleMonster frontend engine 이 지은 토큰 -- 손으로 고치지 말고 "
           "`python3 -m gentle_monster.apps.worldplan_tokens` 로 다시 짓는다 */\n" + T.css_vars(t) + "\n")
    (out / "tokens.css").write_text(css, encoding="utf-8")
    (out / "tokens.json").write_text(json.dumps(T.dtcg(t), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return t


if __name__ == "__main__":
    print(json.dumps(build()["color"], ensure_ascii=False))
