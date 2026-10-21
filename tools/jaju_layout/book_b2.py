"""JAJU 포트폴리오 — 수정안 B2: B안의 톤 + C안의 건축 · 패션 레이아웃, 압축.

  python3 tools/jaju_layout/book_b2.py   ->  docs/jaju_rounding_vmd/layout/plan_b2.pdf

사용자 결정(2026-10-21): 전체 톤은 B안(검정 · 산세리프 · 작은 표기), 건축은 C안의 여는 면 · 9 · 10쪽 레이아웃, 압축적으로.
  표지 · 01      B안 그대로 (tools/p1_layout/cover_options.py)
  02–04         장 1 · 관찰하다 (ch1_photo.py)
  05–07         장 2 · 담다 — C안 8(여는 면) · 9(콜라주) · 10(방 안의 진열)
  08–10         장 3 · 채우다 — 여는 면(C안 틀) · 네 장소 네 착장 · 착장 분해
  11 · 12 · 뒤  제안 · 자주 · 뒤표지 — C안 레이아웃을 B 톤으로
C안의 목차 · 도해 사이 면 · 별도 프롤로그는 뺐다(압축). 그룹별 PDF 를 pdfunite 로 잇는다.
이미지는 모두 화면용 사본(긴 변 2200 px)으로 넣어 10 MB 아래로 맞춘다.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, os.path.join(REPO, 'tools/p1_layout'))

import ch1_photo as c1  # noqa: E402
import ch2_arch as c2  # noqa: E402
import cover_options as co  # noqa: E402
import plan_c as pc  # noqa: E402

OUT, TMP = c1.OUT, c1.TMP
t, photo, dash, ring, lab, e = pc.t, pc.photo, pc.dash, pc.ring, pc.lab, pc.e

# ── C안 지면을 B 톤으로 ──────────────────────────────────────────────────────────────────
NUM = {9: 6, 10: 7, 15: 11, 16: 12}   # C안 함수가 부르는 쪽 번호 → 이 책의 쪽 번호
LABEL = {'02 CONTAIN': '02 — CONTAIN', '03 FILL': '03 — FILL'}


def chrome(n, word):
    """B안 · 장 1 과 같은 표기: 왼쪽 위 책 이름, 오른쪽 위 쪽 번호, 왼쪽 아래 장."""
    return (t(10, 7, 80, 4, 'FROM THE INSIDE', 'tiny') + t(207, 7, 80, 4, f'{n:02d}', 'tiny r')
            + t(10, 201, 120, 4, LABEL.get(word, word), 'tiny'))


pc.chrome = lambda n, word: chrome(NUM.get(n, n), word)
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
.ttl{font-family:Inst,sans-serif;font-weight:700;font-size:64pt;line-height:64pt;letter-spacing:-.02em;color:#fff}
.num{font-family:Inst,sans-serif;font-weight:700;font-size:11pt;color:#C8322B}
.ttk{font-size:9pt}.big{color:#fff}
.dg .fillg{fill:#3a3a3a}
.inkbg{background:#0B0B0B}.cvt{font-family:Inst,sans-serif;font-weight:700;font-size:40pt;line-height:46pt}
.pal{display:flex;gap:1.2mm}.pal div{position:static;flex:1}.pal i{display:block;height:7mm}.pal span{display:block;font-size:5.8pt;color:#8a8a8a;margin-top:1mm;font-style:normal}
"""


# ── 장의 여는 면 — 장 1 의 2쪽(01 Observe)과 같은 틀 ──────────────────────────────────────
#   장 2 는 앞서 만든 ch2_arch.page5 를 그대로, 장 3 은 같은 틀로 새로.
def fill_open():
    def m(to, s):
        return c1.corners(178, 148)

    return ''.join([
        c1.head(8, '03 — FILL'),
        c1.t(18, 54, 80, 30, '03', 'chno'),
        c1.t(18, 92, 90, 12, 'Fill', 'chtitle'),
        c1.t(18, 105, 90, 8, '채우다', 'chko'),
        c1.t(18, 124, 86, 30, '<p>웃음이 머문 곳에는 늘 조합이 있었다.</p><p>나는 자주 입는 옷으로 빈 자리를 채운다.</p>', 'body'),
        c1.t(18, 141, 86, 20, '<p>Where a smile stayed, there was always a combination.</p><p>I fill the empty place with clothes I wear often.</p>', 'bodyen'),
        c2.diagram(18, 158, 80, 30, [('Read', '읽다'), ('Choose', '고르다'), ('Fill', '채우다')]),
        c1.photo('FA-02', 109, 31, 178, 148, focus=(0.45, 0.47), marks=m),
        c1.t(109, 182, 178, 5, '<b>FA-02</b>&nbsp;&nbsp;유리 안에서 밖을 본다 · 흰 셔츠 · 네이비 팬츠', 'cap'),
    ])


# ── 09 · 네 장소, 네 착장 (Galatasaray 의 색 변주 타일) ───────────────────────────────────
FOUR = [('FA-01', (0.55, 0.62), 'Riverside, night', '강변 · 밤', '올리브 롱 파카 · 검정 셔츠 · 흰 티'),
        ('FA-04', (0.53, 0.55), 'Shop front, evening', '가게 앞 · 저녁', '검정 롱코트 · 네이비 팬츠 · 회색 스니커즈'),
        ('FA-05', (0.72, 0.6), 'Park, afternoon', '놀이공원 · 오후', '베이지 재킷 · 회색 팬츠'),
        ('FA-03', (0.6, 0.5), 'Seaside rocks', '바닷가 바위', '회색 니트 · 연청 데님')]


def four_places():
    o = [chrome(9, '03 FILL'),
         t(12, 22, 128, 8, 'Four places, four outfits', 'h'),
         t(12, 34, 124, 30, '<p>나는 그날 갈 장소에 옷의 톤을 맞춘다.</p><p>장소가 틀이라면, 옷은 그 틀을 채우는 조합이다.</p>', 'body'),
         t(12, 52, 124, 10, 'I match the tone of my clothes to the place I am going.', 'en')]
    for i, (pid, f, en, ko, items) in enumerate(FOUR):
        r, c = divmod(i, 2)
        x, y = 156.5 + c * 66, 22 + r * 86
        o.append(photo(pid, x, y, 62.5, 76, focus=f))
        o.append(t(x, y + 77.5, 62.5, 8, f"<p><b>0{i + 1}</b>&nbsp;{en}<span class='pid'>{pid}</span></p><p>{ko} — {items}</p>", 'gc'))
    pal = ''.join(f"<div><i style='background:{c}'></i><span>{w}</span></div>" for c, w in
                  [('#1c1c1a', '검정'), ('#4f4a2c', '올리브'), ('#cbbfae', '베이지'), ('#8f8b84', '회색')])
    o += [t(12, 140, 128, 6, 'Palette', 'h'),
          div(12, 150, 90, 14, pal, 'pal'),
          t(12, 170, 124, 12, '<p>네 장소의 색이 달라도 옷의 색은 네 가지 안에 있다.</p>', 'cap2')]
    return ''.join(o)


def div(x, y, w, h, inner, cls):
    return pc.div(x, y, w, h, inner, cls)


# ── 10 · 착장 분해 (Skate zine 의 아이템 라벨) ─────────────────────────────────────────
def breakdown():
    x0, y0, w, h = 40, 22, 56, 172
    W, H = 1202, 1500
    s = max(w / W, h / H)
    ox = min(0, max(w - W * s, w / 2 - 0.53 * W * s))
    pts = [('Hair', '짧고 단정하게', 610, 540), ('Coat', '검정 오버핏 롱코트', 640, 930),
           ('Trousers', '네이비 와이드 팬츠', 640, 1370), ('Shoes', '회색 스니커즈', 600, 1455)]
    svg = ''
    for i, (en, ko, px, py) in enumerate(pts):
        cx, cy = x0 + ox + px * s, y0 + py * s
        ly = [60, 100, 150, 182][i]
        svg += f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='1' class='dotr'/>"
        svg += f"<polyline points='{cx:.2f},{cy:.2f} 104,{ly} 112,{ly}' class='gl2' fill='none'/>"
        svg += f"<text x='114' y='{ly + 1}' class='lb2'><tspan font-weight='700'>{en}</tspan>  {ko}</text>"
    return ''.join([
        chrome(10, '03 FILL'),
        t(12, 22, 26, 40, '<p><b>Breakdown</b></p><p>착장 한 벌을</p><p>아이템으로</p>', 'side'),
        photo('FA-04', x0, y0, w, h, focus=(0.53, 0.5)),
        pc.div(0, 0, 297, 210, f"<svg class='ov' viewBox='0 0 297 210'>{svg}</svg>", ''),
        t(12, 176, 26, 20, '<p>FA-04</p><p>가게 앞 · 저녁</p>', 'cap2'),
        photo('FA-03', 168, 22, 60, 76, focus=(0.6, 0.5)),
        t(168, 100, 60, 10, '<p>뒤에서 — 매장 안의 손님은</p><p>마네킹의 등을 먼저 본다</p>', 'cap2'),
        t(234, 22, 52, 60, '<p><b>Back</b></p><p>니트의 결,</p><p>어깨에서 떨어지는 품.</p><p>등에도 조합이 있다.</p>', 'side'),
        t(168, 130, 117, 30, '<p>무엇을 고르고 무엇을 뺐는지가 조합을 만든다.</p><p>진열도 착장도 — 한 칸을 채우는 일이다.</p>', 'body'),
        t(168, 160, 117, 10, 'What is chosen, and what is left out, makes the combination.', 'en'),
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
    c1.SRC = pc.screen  # 모든 쪽을 화면용 사본으로
    c1.has = pc.has
    c1.size = lambda pid: pc.Image.open(pc.path(pid)).size
    opener_css = c1.CSS + c2.EXTRA_CSS
    parts = [render('cover', [co.b_cover(), co.b_page1()], co.CSS)]
    c1.main()
    parts.append(os.path.join(OUT, 'ch1_photo.pdf'))
    parts.append(render('contain_open', [c2.page5()], opener_css))
    parts.append(render('contain', [pc.c2_collage(), pc.c2_detail()], DARK))
    parts.append(render('fill_open', [fill_open()], opener_css))
    parts.append(render('rest', [four_places(), breakdown(), pc.p_proposal(), pc.p_often(), pc.p_back()], DARK))
    out = os.path.join(OUT, 'plan_b2.pdf')
    subprocess.run(['pdfunite', *parts, out], check=True)
    print('wrote', out)


if __name__ == '__main__':
    main()
