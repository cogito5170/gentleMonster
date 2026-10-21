"""JAJU 포트폴리오 — 수정안 B2: B안의 톤 + C안의 건축 레이아웃(9 · 10쪽), 압축.

  python3 tools/jaju_layout/book_b2.py   ->  docs/jaju_rounding_vmd/layout/plan_b2.pdf

사용자 결정(2026-10-21): 전체 톤은 B안(검정 · 산세리프 · 작은 표기), 건축은 C안 9 · 10쪽의 레이아웃을 가져온다, 압축적으로.
  표지 · 01       B안 그대로 (tools/p1_layout/cover_options.py)
  02–04          장 1 · 관찰하다 (ch1_photo.py)
  05–06          장 2 · 담다 — 두 쪽으로 압축. C안 9쪽(콜라주)에 장 제목과 격자 골조를 넣어 여는 면을 겸하고, 10쪽(방 안의 진열)을 잇는다
  07–09          장 3 · 채우다 — 여는 면은 장 1 과 같은 틀, 2×2 · 착장 분해는 C안 레이아웃 (패션 사진 받기 전: 빈 칸)
  10 · 11 · 뒤   제안 · 자주 · 뒤표지 — C안 레이아웃을 B 톤으로
C안의 도해 사이 면 · 목차 · 별도 프롤로그는 뺐다(압축). 각 쪽은 그룹별 PDF 로 뽑아 pdfunite 로 잇는다.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, os.path.join(REPO, 'tools/p1_layout'))

import ch1_photo as c1  # noqa: E402
import cover_options as co  # noqa: E402
import plan_c as pc  # noqa: E402

OUT, TMP = c1.OUT, c1.TMP
t, photo, dash, ring, lab = pc.t, pc.photo, pc.dash, pc.ring, pc.lab

# ── C안 지면을 B 톤으로 ──────────────────────────────────────────────────────────────────
NUM = {9: 5, 10: 6, 13: 8, 14: 9, 15: 10, 16: 11}
LABEL = {'02 CONTAIN': '02 — CONTAIN', '03 FILL': '03 — FILL', 'PROPOSAL': 'PROPOSAL', 'OFTEN': 'OFTEN'}


def b_chrome(n, word):
    """B안 · 장 1 과 같은 표기: 왼쪽 위 책 이름, 오른쪽 위 쪽 번호, 왼쪽 아래 장."""
    return (t(10, 7, 80, 4, 'FROM THE INSIDE', 'tiny') + t(207, 7, 80, 4, f'{NUM.get(n, n):02d}', 'tiny r')
            + t(10, 201, 120, 4, LABEL.get(word, word), 'tiny'))


pc.chrome = b_chrome
pc.gutter = lambda: ''

DARK = (pc.CSS
        .replace(pc.PAPER, '#0B0B0B').replace(pc.INK, '#EDEDED').replace(pc.MID, '#8A8A8A')
        .replace('#d3cdc4', '#2a2a2a').replace('#cfc8bc', '#333333').replace('#d8d2c8', '#151515')
        .replace('#e2ddd5', '#161616').replace('#b8b0a4', '#4a4a4a').replace('#8d867b', '#8a8a8a').replace('#a8a196', '#555555'))
DARK += """
.tiny{font-size:6pt;line-height:8pt;letter-spacing:.06em;color:#8a8a8a;white-space:nowrap}
.body{color:#CFCFCF}.h{color:#fff}
.cc .ct{font-family:Inst,sans-serif;font-style:normal;font-weight:700;font-size:8.5pt;color:#fff}
.sec{font-family:Inst,sans-serif;font-weight:700;font-size:22pt;line-height:26pt;color:#fff}
.chno{font-family:Inst,sans-serif;font-size:40pt;line-height:40pt;font-weight:700;color:#fff;letter-spacing:-.02em}
.ttk{font-size:9pt}.big{color:#fff}
.dg .fillg{fill:#3a3a3a}
.inkbg{background:#0B0B0B}.cvt{font-family:Inst,sans-serif;font-weight:700;font-size:40pt;line-height:46pt}
"""


# ── 05 · 담다 (C안 9쪽 + 장 제목 + 격자 골조) ──────────────────────────────────────────
def contain_1():
    def red(to, s):
        cx, cy = to(1525, 715)
        return ring(cx, cy, 3.6)

    def yard(to, s):
        x0, y0 = to(380, 140)
        return dash(x0, y0, 330 * s, 400 * s) + lab(x0 + 1.2, y0 + 3.6, 'Courtyard')

    def frame(to, s):
        fx, fy = to(1020, 560)
        vx, vy = to(790, 300)
        return (dash(fx, fy, 330 * s, 230 * s) + lab(fx + 1, fy - 1.4, 'Fill')
                + dash(vx, vy, 190 * s, 150 * s) + lab(vx + 1, vy - 1.4, 'Void'))

    def capt(x, y, w, ttl, txt, pid):
        return t(x, y, w, 12, f"<i class='ct'>{ttl}</i><span>{txt}</span><span class='pid'>{pid}</span>", 'cc')

    return ''.join([
        b_chrome(5, '02 CONTAIN'),
        t(12, 20, 40, 16, '02', 'chno'),
        t(40, 22, 100, 12, 'Contain', 'sec'),
        t(40, 33, 100, 6, '담다 — 건축', 'ttk'),
        t(12, 44, 128, 20, '<p>멈춘 자리에는 늘 틀이 있었다. 도시에서 마당으로, 마당에서 집으로 —</p><p>틀을 좁혀 갈수록 그 안의 하루가 보인다.</p>', 'body'),
        photo('AR-09', 12, 64, 128.5, 56, marks=red), capt(12, 122, 128.5, 'City', '도시의 광장 — 렌더', 'AR-09'),
        photo('AR-06', 12, 140, 60, 45, focus=(0.5, 0.45), marks=yard), capt(76, 168, 64, 'Courtyard', '건물 사이를 비운 마당', 'AR-06'),
        photo('AR-05', 156.5, 22, 128.5, 54, focus=(0.45, 0.5)), capt(156.5, 78, 128.5, 'Path', '두 매스를 잇는 회랑과 길', 'AR-05'),
        photo('AR-10', 156.5, 98, 60, 60), capt(156.5, 160, 60, 'House', '골목 언덕의 집', 'AR-10'),
        photo('AR-03', 222, 98, 63, 60, focus=(0.55, 0.45), marks=frame), capt(222, 160, 63, 'Frame', '칸을 비우고 채운 격자 골조', 'AR-03'),
        t(156.5, 182, 128.5, 6, '모형 · 렌더 — 건축학과 작업. 프로젝트 이름 · 학년 ____', 'cap'),
    ])


# ── 07 · 채우다 여는 면 (장 1 의 2쪽과 같은 틀) ─────────────────────────────────────────
def fill_open():
    return ''.join([
        c1.head(7, '03 — FILL'),
        c1.t(18, 54, 80, 30, '03', 'chno'),
        c1.t(18, 92, 90, 12, 'Fill', 'chtitle'),
        c1.t(18, 105, 90, 8, '채우다', 'chko'),
        c1.t(18, 124, 86, 30, '<p>웃음이 머문 곳에는 늘 조합이 있었다.</p><p>나는 자주 입는 옷으로 빈 자리를 채운다.</p>', 'body'),
        c1.t(18, 141, 86, 20, '<p>Where a smile stayed, there was always a combination.</p><p>I fill the empty place with clothes I wear often.</p>', 'bodyen'),
        c1.photo('FA-01', 109, 31, 178, 148),
        c1.t(109, 182, 178, 5, '<b>FA-01</b>&nbsp;&nbsp;착장 · ____', 'cap'),
    ])


def render(name, pages, css):
    body = ''.join(f"<div class='sheet'>{p}</div>" for p in pages)
    h = os.path.join(TMP, f'b2_{name}.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>")
    pdf = os.path.join(TMP, f'b2_{name}.pdf')
    subprocess.run(['node', c1.PRINT, h, pdf, os.path.join(TMP, f'b2_{name}')], check=True)
    return pdf


def main():
    os.makedirs(TMP, exist_ok=True)
    parts = [render('cover', [co.b_cover(), co.b_page1()], co.CSS)]
    c1.main()
    parts.append(os.path.join(OUT, 'ch1_photo.pdf'))
    parts.append(render('contain', [contain_1(), pc.c2_detail()], DARK))
    c1.PHOTO = os.path.join(REPO, 'docs/jaju_rounding_vmd/assets/fashion')
    c1.DESC['FA-01'] = '착장 전신 한 장 — 가장 나다운 조합'
    parts.append(render('fill_open', [fill_open()], c1.CSS))
    parts.append(render('rest', [pc.c3_combos(), pc.c3_breakdown(), pc.p_proposal(), pc.p_often(), pc.p_back()], DARK))
    out = os.path.join(OUT, 'plan_b2.pdf')
    subprocess.run(['pdfunite', *parts, out], check=True)
    print('wrote', out)


if __name__ == '__main__':
    main()
