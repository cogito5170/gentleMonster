"""JAJU 포트폴리오 9쪽 Front, or back? — 스케이트 진 'STREET CULTURE' 펼침면 꼴로 다시 짠 판 (315 × 195).

  python3 tools/jaju_layout/p09_back_zine.py   ->  docs/jaju_rounding_vmd/layout/p09_back_zine.pdf

사용자: "해당 페이지(사용자 InDesign 의 Front, or back? 쪽)를 두번째 이미지(STREET CULTURE)화 하여라. 레이아웃, 배치, 폰트 등을
참고하여 재가공하라. 인디자인과 포토샵으로 보내라."
사례에서 가져온 것:
  · 왼쪽 쪽: 흑백 사진을 살구색 종이에 먹 한 색으로 찍은 꼴(밝은 곳 = 종이색, 세로 결) — 쪽 끝까지 → 앞모습 FA-04
  · 펼침면을 둘로 나눈 아주 큰 좁은 대문자: 왼쪽 먹색 'STREET' | 오른쪽 종이색 'CULTURE' → 'FRONT,' | 'OR BACK?' (쪽 제목)
  · 왼쪽 사진 위 빨간 상자(접는 선까지) — 제목 '1990s' + 고정폭 본문 → '(A) FRONT' + 착장 분해 네 줄(사진의 점에서 지시선)
  · 오른쪽 쪽: 빨간 바탕, 큰 낱말에 걸친 사진(사례의 뛰어오르는 사람 자리) → 뒷모습 FA-03,
    큰 낱말 아래 본문 → 큰 인용 + 영어, 아래쪽 흑백 사진 둘 + 오른쪽 단 글 → 니트의 결 · 어깨의 품 두 조각 + 끝 줄
    (오려 낸 사람 사진은 오려 내기가 새 그림이라 네모 사진으로)
글: 사용자 쪽 그대로 — 제목 · 라벨 넷 · 큰 인용 · 영어 · 끝 줄. 바닥 줄은 새 구성(파트 2 Match, 9쪽).
좁은 굵은 글꼴이 없어 Instrument Sans Bold 장평 62%. 사진의 먹 한 색 · 세로 결은 파일에 구워 넣는다(InDesign · 포토샵도 같게).
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import part2_match as p2  # noqa: E402

d, W, H = p2.d, p2.W, p2.H
OUT, TMP, PRINT, FONTS, CROPS, FA = p2.OUT, p2.TMP, p2.PRINT, p2.FONTS, p2.CROPS, p2.FA
PAPER, RED, INK = '#E9A48D', '#E2382B', '#151311'
CX, L, FOLIO_Y = 157.5, 14.0, 184.35

QUOTE = ['매장 안의 손님은', '마네킹의 등을 먼저 본다.']
EN = 'Inside the store, people meet the mannequin’s back first.'
END = ['그래서 나는 등을 먼저 입힌다 —', '니트의 결, 어깨에서 떨어지는 품.']
LABELS = [('HAIR', '짧고 단정하게', (610, 540)), ('COAT', '검정 오버핏 롱코트', (640, 930)),
          ('TROUSERS', '네이비 와이드 팬츠', (640, 1370)), ('SHOES', '회색 스니커즈', (600, 1455))]


def _rgb(hx):
    return np.array([int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)])


def mono(pid, x, y, w, h, cx, cy, span, bright=1.0, contrast=1.25):
    """흑백 사진을 종이에 먹 한 색으로: 회색 → 대비 · 밝기 → 종이색과 먹색 사이 + 세로 결(정해진 옅은 줄). 파일에 구워 넣는다.
    반환: (html, 원본 px → 쪽 mm 함수)."""
    im = Image.open(os.path.join(FA, pid + '.jpg')).convert('L')
    IW, IH = im.size
    sh = span * h / w
    if sh > IH:
        span, sh = IH * w / h, IH
    lft, tp = max(0, min(IW - span, cx - span / 2)), max(0, min(IH - sh, cy - sh / 2))
    c = im.crop((int(lft), int(tp), int(lft + span), int(tp + sh)))
    c.thumbnail((1600, 1600))
    v = np.asarray(c, dtype=np.float32) / 255
    v = np.clip(((v - .5) * contrast + .5) * bright, 0, 1)
    cols = np.arange(v.shape[1])
    streak = 1 - .10 * ((((cols * 2654435761) % 997) / 997) > .93) - .04 * ((((cols * 40503) % 89) / 89) > .8)
    v = v * streak[None, :]
    out = v[..., None] * _rgb(PAPER)[None, None, :] + (1 - v[..., None]) * _rgb(INK)[None, None, :]
    os.makedirs(CROPS, exist_ok=True)
    f = os.path.join(CROPS, f'back_{pid}_{cx}_{cy}_{span:.0f}_{w:.0f}x{h:.0f}_mono.jpg')
    Image.fromarray((np.clip(out, 0, 1) * 255).astype('uint8'), 'RGB').save(f, quality=88)
    k = w / span
    html = d(x, y, w, h, f"<img src='file://{f}' style='position:absolute;left:0;top:0;width:{w}mm;height:{h}mm'>", 'duo')
    return html, (lambda px, py: (x + (px - lft) * k, y + (py - tp) * k))


def folio():
    return (d(L, FOLIO_Y, 160, 4, '<p>FROM THE INSIDE&nbsp;&nbsp;—&nbsp;&nbsp;PART 2 MATCH</p>', 't ft pa')
            + d(107.5, FOLIO_Y, 100, 4, '<p>BREAKDOWN</p>', 't ft c')
            + d(261, FOLIO_Y, 40, 4, '<p>09</p>', 't ft r'))


def layers():
    """아래에서 위로 (이름, html, 보임) — PDF · InDesign 은 이어 붙이고, 포토샵은 층마다 굽는다."""
    front, f2mm = mono('FA-04', 0, 0, CX, H, 601, 750, 1202, bright=1.08)
    back, _ = mono('FA-03', 230, 42, 77, 70, 620, 700, 760, bright=1.1)
    knit, _ = mono('FA-03', 165, 104, 58, 74, 760, 820, 300, bright=1.1)
    shoulder, _ = mono('FA-03', 229, 134, 86, 47, 640, 480, 430, bright=1.1)
    BX, BY, BW, BH = 108, 72, CX - 108, 60          # 빨간 상자 (접는 선까지)
    rows, svg = '', ''
    for i, (en, ko, (px, py)) in enumerate(LABELS):
        ry = BY + 17 + i * 8.6
        rows += d(BX + 4.5, ry, BW - 7, 7, f"<p><span class='e'>{en}</span></p><p>{ko}</p>", 't lbz')
        ax, ay = f2mm(px, py)
        svg += (f"<circle cx='{ax:.2f}' cy='{ay:.2f}' r='.9' fill='{RED}'/>"
                f"<polyline points='{ax:.2f},{ay:.2f} {BX:.2f},{ry + 1.6:.2f} {BX + 3.4:.2f},{ry + 1.6:.2f}' class='ldz'/>")
    return [
        ('종이 · 빨간 쪽', f"<svg class='ov' viewBox='0 0 {W} {H}'><rect x='0' y='0' width='{CX}' height='{H}' fill='{PAPER}'/>"
                      f"<rect x='{CX}' y='0' width='{W - CX}' height='{H}' fill='{RED}'/></svg>", True),
        ('사진 (A) 앞 FA-04', front, True),
        ('FRONT,', d(7, 2, 160, 52, '<p>FRONT,</p>', 't big ink'), True),
        ('OR BACK?', d(CX + 5, 2, 160, 52, '<p>OR BACK?</p>', 't big pa'), True),
        ('사진 (B) 뒤 FA-03', back, True),
        ('사진 니트의 결', knit, True),
        ('사진 어깨의 품', shoulder, True),
        ('빨간 상자', f"<svg class='ov' viewBox='0 0 {W} {H}'><rect x='{BX}' y='{BY}' width='{BW}' height='{BH}' fill='{RED}'/></svg>", True),
        ('지시선', f"<svg class='ov' viewBox='0 0 {W} {H}'>{svg}</svg>", True),
        ('(A) FRONT · 라벨', d(BX + 4.5, BY + 3.5, BW - 7, 12, '<p>(A) FRONT</p>', 't hd') + rows
         + d(BX + 4.5, BY + BH - 5.6, BW - 7, 4, '<p>N°FA-04&nbsp;&nbsp;·&nbsp;&nbsp;BREAKDOWN</p>', 't cp'), True),
        ('큰 인용 · 영어', d(165, 47, 64, 20, ''.join(f'<p>{s}</p>' for s in QUOTE), 't qz')
         + d(165, 66, 60, 24, f'<p>{EN}</p>', 't mo wrap'), True),
        ('끝 줄', d(234, 119.5, 70, 14, ''.join(f'<p>{s}</p>' for s in END), 't kz'), True),
        ('캡션', d(230, 113, 72, 4, '<p>(B) BACK&nbsp;&nbsp;·&nbsp;&nbsp;N°FA-03</p>', 't cp')
         + d(165, 179.2, 58, 4, '<p>KNIT — 굵은 결</p>', 't cp')
         + d(229, 130.2, 72, 4, '<p>SHOULDER — 어깨에서 떨어지는 품</p>', 't cp'), True),
        ('바닥 줄', folio(), True),
    ]


def page():
    return ''.join(h for _, h, _ in layers())


KO = p2.KO
CSS = p2.CSS + f"""
.duo{{overflow:hidden}}
.big{{font-family:Inst,sans-serif;font-weight:700;font-size:135pt;line-height:128pt;letter-spacing:-.01em;transform:scaleX(.62);transform-origin:0 0}}
.big.ink{{color:{INK}}}.big.pa{{color:{PAPER}}}
.hd{{font-family:Inst,sans-serif;font-weight:400;font-size:24pt;line-height:26pt;color:{INK};transform:scaleX(.74);transform-origin:0 0}}
.lbz{{font-family:{KO};font-size:7.4pt;line-height:9.6pt;color:{INK}}}.lbz .e{{font-family:Mono,monospace;font-size:6.6pt;letter-spacing:.06em}}
.ov .ldz{{fill:none;stroke:{INK};stroke-width:.22}}
.qz{{font-family:{KO};font-size:13pt;line-height:18.5pt;color:{INK};-webkit-text-stroke:.3pt {INK}}}
.mo{{font-family:Mono,monospace;font-size:7.4pt;line-height:11pt;color:{INK};text-align:justify}}
.kz{{font-family:{KO};font-size:8.4pt;line-height:13pt;color:{INK}}}
.cp{{font-family:Mono,monospace;font-size:5.8pt;letter-spacing:.04em;color:{INK};white-space:nowrap}}.cp.pa{{color:{PAPER}}}
.ft.pa{{color:{INK}}}.ft.pp{{color:{PAPER}}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'p09_back_zine.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p09 Front or back zine</title><style>{CSS}</style></head>"
                f"<body><div class='sheet' style='background:{PAPER}'>{page()}</div></body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p09_back_zine.pdf'), os.path.join(TMP, 'p09b')], check=True)


if __name__ == '__main__':
    main()
