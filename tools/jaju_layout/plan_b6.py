"""JAJU 포트폴리오 — B6: B4 의 흐름(쪽 순서)은 그대로, 사례 6 에서 배운 레이아웃 · 텍스트 · 배치만 들인 판.

  python3 tools/jaju_layout/plan_b6.py   ->  docs/jaju_rounding_vmd/layout/plan_b6.pdf

사용자: "기존 B4 의 흐름 순서는 지켜라. 주어진 틀 안에서 레이아웃, 텍스트, 배치 등의 피드백을 진행한 후 수정."
쪽 순서는 B4 와 같다: 표지 · 01 Prologue · 02 Observe · 03 grid · 04 detail · 05 Reading · 06 Contain · 07 City · 08 Room ·
09 Fill · 10 Four · 11 Items · 12 Breakdown · 13 Proposal · 14 Often · 15 About · 뒤표지.
쪽별 피드백과 바꾼 것: docs/jaju_rounding_vmd/plan_b6.md
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b5 as b5  # noqa: E402

b4, b3, pe = b5.b4, b5.b3, b5.pe
pc, t, div, photo, e, af, frame = pe.pc, pe.t, pe.div, pe.photo, pe.e, pe.af, pe.frame
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
NAME = pe.NAME


# ── 01 · Prologue — 유령 글자 + 마침표 제목 + 본문을 한 덩어리로 ─────────────────────────────
def p_prologue():
    body = ''.join(f'<p>{e(l)}</p>' for l in pc.LEAD_KO[:-1])
    return ''.join([
        t(10, 12, 280, 40, 'Prologue', 'ghost'),
        t(14, 32, 120, 14, 'Prologue.', 'h1'),
        t(14, 62, 140, 60, '<p>밖에서 보면</p><p>상품이 보이고,</p><p>안에서 보면</p><p>사람이 보인다.</p>', 'pullbig'),
        div(14, 142, 5, 5, '', 'dotor'),
        t(162, 62, 122, 80, body, 'kb'),
        t(162, 126, 122, 10, f'<p>{e(pc.LEAD_KO[-1])}</p>', 'kbb'),
        t(162, 146, 112, 40, f'<p>{e(pc.LEAD_EN)}</p>', 'enb'),
    ])


# ── 05 · Reading a window — 목록을 줄인다 (제목 + 2–4줄 원칙) ────────────────────────────────
def p_reading():
    html = b3.p_reading()
    for a, b in [('지나가는 사람의 눈높이', '눈높이'), ('눈높이 바로 아래, 가장 진한 색의 병', '가장 진한 색의 병'),
                 ('같은 잔을 줄 세워 리듬을 만든다', '같은 잔의 줄'), ('초록 하나로 공간에 숨을', '초록 하나'),
                 ('위에서 떨어지는 작은 빛', '위에서 떨어지는 빛'), ('사진 메뉴 — 멀리서 먼저 보이는 칸', '멀리서 먼저 보이는 칸'),
                 ('세트 메뉴 — 멈춘 뒤에 읽는 칸', '멈춘 뒤에 읽는 칸'), ('손에 닿는 높이의 큰 사진', '손에 닿는 높이'),
                 ('창 안의 사람 — 진열의 마지막 한 점', '창 안의 사람'),
                 ('<p>다른 가게의 진열창 앞에서도</p><p>나는 같은 것을 읽는다.</p><p>어디에 눈이 먼저 가고, 무엇이 손에 닿는지.</p>',
                  '<p>남의 진열창 앞에서도 같은 것을 읽는다.</p><p>눈이 먼저 가는 곳, 손이 닿는 곳.</p>')]:
        html = html.replace(a, b)
    return html


# ── 15 · About — 사례 6 의 Hello · Resume 처럼 ───────────────────────────────────────────
def p_about():
    rows = [('MAJOR', '건축학과 · 학교 · 학년 ____'), ('APPLYING', 'JAJU 라운딩 VMD'),
            ('EXPERIENCE', '판매 · 진열 · 매장 경험 ____'), ('ROUNDING', '출장 · 장기 근무 가능 여부 ____'),
            ('IN THIS BOOK', '사진 17 · 건축 작업 10 · 착장 5 — 모두 직접 찍고 만든 것'),
            ('IMAGE CREDIT', '표지 이미지 ____ (직접 촬영 / 출처)')]
    tbl = ''.join(f"<div class='ab'><b>{a}</b><span>{b}</span></div>" for a, b in rows)
    return ''.join([
        t(10, 12, 200, 40, 'About', 'ghost'),
        t(14, 32, 120, 14, 'About.', 'h1'),
        t(14, 52, 140, 8, f"I’m {NAME}.", 'imname'),
        t(14, 64, 132, 30, '<p>사람이 멈추는 자리를 보고,</p><p>그 자리에 맞는 조합을 세우는 사람.</p>', 'kb'),
        t(14, 90, 132, 90, tbl, 'abt'),
        photo('FA-05', 176, 22, 109, 166, focus=(0.74, 0.62), zoom=1.5),
        t(176, 190, 109, 5, 'FA-05 — 놀이공원 기념품 노점 앞', 'data'),
    ])


PAGES = [(lambda: b3.p_cover(), ''), (p_prologue, ''), (b5.p_observe, 'g1'), (pe.p_grid, 'g1'), (b4.p_detail, 'g1'),
         (p_reading, 'g1'), (b5.p_contain, ''), (pe.p_collage, ''), (b5.p_room, ''), (b5.p_fill, ''), (b4.p_four, ''),
         (b4.p_items, ''), (pe.p_breakdown, ''), (b4.p_proposal, ''), (pe.p_often, ''), (p_about, ''), (b5.p_back, '')]
PARTS = {2: 'PART 1 OBSERVE', 3: 'PART 1 OBSERVE', 4: 'PART 1 OBSERVE', 5: 'PART 1 OBSERVE', 6: 'PART 2 CONTAIN', 7: 'PART 2 CONTAIN',
         8: 'PART 2 CONTAIN', 9: 'PART 3 FILL', 10: 'PART 3 FILL', 11: 'PART 3 FILL', 12: 'PART 3 FILL'}
H2 = re.compile(r"(class='t h2'[^>]*>)([^<]*?[A-Za-z])(</div>)")


def page(i, p, g):
    html = b4.render(p, g)
    html = H2.sub(lambda m: m.group(1) + m.group(2) + '.' + m.group(3), html)  # 제목은 마침표로 끝난다 (사례 6)
    if 0 < i < len(PAGES) - 1:
        if not b5.FOOT_NUM.search(html):
            html += (pe.foot_light if p is b5.p_room else b4.RAW)(i, PARTS.get(i, ''))
        html = b5.FOOT_NUM.sub(lambda m: f'{m.group(1)}{i:02d}{m.group(2)}', html)
    return html


def main():
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet {g}'>{page(i, p, g)}</div>" for i, (p, g) in enumerate(PAGES))
    h = os.path.join(TMP, 'plan_b6.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B6</title><style>{b5.CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b6.pdf'), os.path.join(TMP, 'plan_b6')], check=True)


if __name__ == '__main__':
    main()
