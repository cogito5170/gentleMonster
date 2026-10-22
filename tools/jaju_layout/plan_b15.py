"""JAJU 포트폴리오 — B15: B14 그대로, 03 Where people stop 의 왼쪽 단만 2-2 세션 시안(p03_options 안 A)의 배치로.

  python3 tools/jaju_layout/plan_b15.py   ->  docs/jaju_rounding_vmd/layout/plan_b15.pdf

사용자: "4페이지의 좌측 레이아웃을 해당 이미지와 같이 수정한다." (안 A 시안 캡처)
시안의 배치: 제목 한 줄 19pt(y 22) → 국문 본문(y 36) → 영문 이탤릭(y 70) → 아래 고정폭 글 덩어리(y 148).
글은 확정 문구(2-2 3안) 그대로 — 시안의 본문은 확정 전 문구라 쓰지 않는다. 맺음은 영문 아래, 고정폭 덩어리 위에.
오른쪽 사진 · 캡션은 B14 그대로.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b14 as b14  # noqa: E402

b13, b10 = b14.b13, b14.b10
pe = b10.pe
t, photo = pe.t, pe.photo
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT


def p_grid():
    gx, gy, cw, ch, gap = 100, 22, 89.5, 46.5, 4
    o = [t(14, 22, 84, 10, 'Where people stop.', 'h2'),
         t(14, 36, 84, 30, '<p>멈춘 사람은 대개 짧은 질문 하나를 하고 있다.</p><p>조금 더 있을까? 뭐 먹지?</p><p>어느 게 맛있어 보이지?</p>', 'kb'),
         t(14, 70, 80, 16, 'People who stop are usually asking one short question. Stay a little longer? What should I eat? Which one looks good?', 'enb wrap'),
         t(14, 102, 84, 20, '<p>나도 가게 앞에서 질문 하나를 한다.</p><p>어떻게 놓으면 지나가던 사람이 걸음을 멈출까.</p>', 'kb'),
         t(14, 118, 80, 14, 'In front of a shop, I ask one too: how should I place things so that people passing by will stop?', 'enb wrap'),
         t(14, 148, 80, 40, '<p>17 FRAMES / 06 SHOWN</p><p>SEA → STREET → SHOP</p><p>&nbsp;</p>'
                            '<p>SIX PLACES, SIX QUESTIONS —</p><p>MY GUESS.</p>', 'letter')]
    for i, (pid, place, en, q, box) in enumerate(b13.A):
        r, c = divmod(i, 2)
        x, y = gx + c * (cw + gap), gy + r * (ch + 10)
        hx = pe.accent(pid)
        o.append(photo(pid, x, y, cw, ch, marks=b13.dashed(pid, box, en)))
        o.append(t(x, y + ch + 1.8, cw, 6, f"<p><span class='n3'>N°{i + 1:02d}</span><b>{place}–</b> {q}"
                                           f"<span class='sw3' style='background:{hx}'></span><span class='hx3'>{hx}</span></p>", 'cap'))
    return ''.join(o)


PAGES = [(p_grid if p is b13.p_grid else p, g) for p, g in b14.PAGES]


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for i, (p, g) in enumerate(PAGES):
        html, g = b10.page(i, p, g)
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'plan_b15.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B15</title><style>{b13.CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b15.pdf'), os.path.join(TMP, 'plan_b15')], check=True)


if __name__ == '__main__':
    main()
