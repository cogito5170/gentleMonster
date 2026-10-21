"""JAJU 포트폴리오 — B3: B2(기존 안)를 부족한 점 분석(b2_gap_analysis.md)대로 고친 판.

  python3 tools/jaju_layout/plan_b3.py   ->  docs/jaju_rounding_vmd/layout/plan_b3.pdf

B2 의 톤(어두운 바탕 · 사진 띠 표지)은 지키고, 분석의 고칠 순서 1–7 을 반영한다.
지면 부품은 plan_e.py 의 것을 빌리고 색만 바꾼다:
  1 리듬      파트 여는 쪽 = 사진 전면 + 큰 세리프(Observe · Fill), Contain 은 글자가 사진을 담는다
  2 위계      제목 Young Serif 18–32pt · 본문 10pt · 메타 Plex Mono 6pt · 영문은 읽히는 이탤릭
  3 색        따뜻한 검정(#15120F) · 따뜻한 회색 · 강조 오렌지(#D9773A, JAJU 쪽)
  4 캡션      N° · 때 · 사진에서 잰 색 — 메타 하나로 통일
  5 VMD 증거  새 쪽 'Reading a window' — 가진 사진 속 남의 진열창 · 메뉴판을 VMD 의 눈으로 읽는다(표시만, 지어내지 않음)
              제안 쪽은 가는 선 + 실제 사진의 결
  6 끝        Often = 사진 위 · 번호 · 아래 산문. 뒤표지 = 표지 사진을 좌우로 뒤집어 유리의 글자가 바로 읽힌다(밖에 나왔다)
  7 반복      01 Prologue 에서 표지 사진 재사용을 뺐다 — 글만의 쪽
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_e as pe  # noqa: E402

pc, t, div, photo, e = pe.pc, pe.t, pe.div, pe.photo, pe.e
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
BG, FG, GR, OR, CREAM = '#15120F', '#EFE7DA', '#9A8F82', '#D9773A', pe.CREAM

# ── 쪽 번호: 새 쪽(05)이 들어가 그 뒤로 하나씩 민다 ─────────────────────────────────────
_foot = pe.foot


def foot(n, part=''):
    return _foot(n + 1 if n >= 5 else n, part)


pe.foot = foot


# ── 표지 (B2 의 틀: 사진 띠 + 아래 어두운 띠, 글자 위계만 고침) ───────────────────────────
def p_cover(flip=False):
    img = photo('COVER', 0, 0, 297, 142, focus=(0.5, 0.39))
    if flip:
        img = img.replace("<img ", "<img class='flip' ", 1)
    if not flip:
        words = [t(14, 152, 200, 24, 'From the Inside', 'cvt2'),
                 t(14, 172, 200, 8, '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.', 'cvk'),
                 t(14, 181, 200, 6, 'From the street you see the products. From inside, you see the people.', 'cve')]
        name = [t(203, 190, 80, 5, pe.NAME, 'mast r'), t(183, 196, 100, 5, 'VISUAL MERCHANDISER PORTFOLIO&nbsp;&nbsp;2026', 'mast r dim')]
    else:
        words = [t(14, 152, 200, 24, 'Outside', 'cvt2'),
                 t(14, 172, 220, 8, '이제 당신은 밖에 있다. 유리의 글자가 바로 읽힌다.', 'cvk'),
                 t(14, 181, 200, 6, 'Now you are outside. The name on the glass reads the right way round.', 'cve')]
        name = [t(203, 184, 80, 5, pe.NAME, 'mast r'), t(183, 190, 100, 5, 'VISUAL MERCHANDISER', 'mast r dim'),
                t(183, 196, 100, 5, '연락처 ____', 'mast r dim')]
    return ''.join([div(0, 0, 297, 210, '', 'bg'), img,
                    t(14, 8, 120, 5, 'FROM THE INSIDE', 'mast'), t(163, 8, 120, 5, 'JAJU 라운딩 VMD', 'mast r'),
                    *words, *name])


# ── 01 · Prologue — 글만의 쪽 (표지 사진을 다시 쓰지 않는다) ───────────────────────────────
def p_prologue():
    body = ''.join(f'<p>{e(l)}</p>' for l in pc.LEAD_KO[:-1])
    return ''.join([
        t(14, 22, 80, 6, 'PROLOGUE', 'pn2'),
        t(14, 40, 140, 60, '<p>밖에서 보면</p><p>상품이 보이고,</p><p>안에서 보면</p><p>사람이 보인다.</p>', 'pullbig'),
        div(14, 120, 6, 6, '', 'dotor'),
        t(162, 40, 122, 80, body, 'kb'),
        t(162, 104, 122, 10, f'<p>{e(pc.LEAD_KO[-1])}</p>', 'kbb'),
        t(162, 124, 112, 50, f'<p>{e(pc.LEAD_EN)}</p>', 'enb'),
        pe.foot(1),
    ])


# ── 05 · Reading a window — 라운딩 VMD 의 눈 (새 쪽) ─────────────────────────────────────
def p_reading():
    af, frame = pe.af, pe.frame

    def shop(to, s):
        ey = to(0, 620)[1]
        bx, by = to(815, 700)
        cx, cy = to(925, 705)
        gx, gy = to(790, 560)
        lx, ly = to(905, 410)
        return (f"<line x1='0' y1='{ey:.1f}' x2='66' y2='{ey:.1f}' class='afl'/><text x='1.5' y='{ey - 1.2:.1f}' class='afs'>a) EYE LEVEL</text>"
                + af(bx, by, 3.2, 'b)') + af(cx, cy, 3.2, 'c)') + af(gx, gy, 2.8, 'd)', 'left') + af(lx, ly, 2.6, 'e)'))

    def truck(to, s):
        return (frame(*to(808, 200), 210 * s, 350 * s, 'f) TOP') + frame(*to(1215, 140), 280 * s, 490 * s, 'g) SIDE')
                + frame(*to(567, 560), 400 * s, 280 * s, 'h) LOW') + af(*to(683, 318), 3.2, 'i)'))

    keys = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in [
        ('a)', 'Eye level', '지나가는 사람의 눈높이'), ('b)', 'Hero', '눈높이 바로 아래, 가장 진한 색의 병'),
        ('c)', 'Repeat', '같은 잔을 줄 세워 리듬을 만든다'), ('d)', 'Green', '초록 하나로 공간에 숨을'),
        ('e)', 'Light', '위에서 떨어지는 작은 빛')])
    keys2 = ''.join(f"<div class='k'><b>{a}</b> {b}<span>{c}</span></div>" for a, b, c in [
        ('f)', 'Top', '사진 메뉴 — 멀리서 먼저 보이는 칸'), ('g)', 'Side', '세트 메뉴 — 멈춘 뒤에 읽는 칸'),
        ('h)', 'Low', '손에 닿는 높이의 큰 사진'), ('i)', 'Inside', '창 안의 사람 — 진열의 마지막 한 점')])
    return ''.join([
        t(14, 22, 84, 10, 'Reading a window', 'h2'),
        t(14, 36, 84, 30, '<p>다른 가게의 진열창 앞에서도</p><p>나는 같은 것을 읽는다.</p><p>어디에 눈이 먼저 가고, 무엇이 손에 닿는지.</p>', 'kb'),
        t(14, 70, 84, 80, keys, 'keys'),
        t(14, 176, 84, 12, '<p>N°FA-04&nbsp;&nbsp;EVENING&nbsp;&nbsp;생활용품 가게 진열창</p><p>N°PH-06&nbsp;&nbsp;DUSK&nbsp;&nbsp;푸드 트럭 메뉴판</p>', 'data'),
        photo('FA-04', 104, 22, 66, 166, focus=(888 / 1202, 610 / 1500), zoom=2.6, marks=shop),
        photo('PH-06', 176, 22, 109, 72, focus=(0.6, 0.45), marks=truck),
        t(176, 102, 109, 70, keys2, 'keys'),
        t(176, 170, 109, 18, '<p>라운딩 VMD 는 매장을 돌며 같은 질문을 한다 — 눈높이에 무엇이 있는가, 멈춘 뒤에 무엇을 읽는가.</p>', 'note2'),
        _foot(5, 'PART 1 OBSERVE'),
    ])


CSS = (pe.CSS
       .replace(pe.PAPER, BG).replace(pe.INK, FG).replace(pe.MUTE, GR).replace(pe.ACC, OR)
       .replace('#d9d0c2', '#221d18').replace('#cbbfae', '#3a332c').replace('#e4d9c8', '#d8cdbd'))
CSS += f"""
.bg{{background:{BG}}}
.flip{{transform:scaleX(-1)}}
.cvt2{{font-family:Young,serif;font-size:34pt;line-height:36pt;color:{CREAM};white-space:nowrap}}
.mast.dim{{color:{GR}}}
.pt.dk{{color:#1E1914}}
.pullbig{{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:30pt;line-height:40pt;color:{FG}}}
.dotor{{background:{OR};border-radius:50%}}
.note2{{font-family:'WenQuanYi Zen Hei',sans-serif;font-size:7.6pt;line-height:12pt;color:{GR};border-top:.2mm solid #3a332c;padding-top:2.2mm}}.note2 p{{white-space:normal}}
"""

PAGES = [lambda: p_cover(), p_prologue, pe.p_observe, pe.p_grid, pe.p_detail, p_reading, pe.p_contain, pe.p_collage,
         pe.p_room, pe.p_fill, pe.p_four, pe.p_breakdown, pe.p_proposal, pe.p_often, lambda: p_cover(flip=True)]


def main():
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet'>{p()}</div>" for p in PAGES)
    h = os.path.join(TMP, 'plan_b3.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B3</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b3.pdf'), os.path.join(TMP, 'plan_b3')], check=True)


if __name__ == '__main__':
    main()
