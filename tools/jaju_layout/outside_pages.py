"""JAJU 포트폴리오 맨 끝 두 쪽(부록 A-1 · A-2) — 학교 밖: 카페 · 창고 / 봉사 (315 × 195). 파트 3(Contain) 흐름을 잇는다.

사용자(10-26): "조금 더 밝은 그레이 톤으로 제작하라." "추가 첨부의 느낌을 주고자 한다." → 밝은 회색 종이 + 먹색 글, APPENDIX 꼬리표 · A-1 · A-2.

  python3 tools/jaju_layout/outside_pages.py   ->  docs/jaju_rounding_vmd/layout/outside_pages.pdf (2쪽)

사용자: "(PORTFOLIO 4.indd) 맨 마지막 카페와 봉사에 대한 페이지를 디자인하라. 기존의 포트폴리오 흐름과 이어지도록 제작한다.
포트폴리오 사례를 참고하여 임의 판단 하에 제작한다."
흐름: Contain(건축학부에서 배운 것은 공간을 보는 법 · 매장마다 다른 공간을 읽어야 한다) → 학부 · 인턴 모형(틀을 그리고, 그 안을 들여다봤다)
      → **학교 밖 1: 같은 공간을 다시 쓰다(카페 홀 · 매장 창고)** → **학교 밖 2: 누군가의 방을 새로(해비타트 봉사)** → 끝.
꼴: 사용자가 InDesign 에서 만든 'From the city to the room.' 쪽 그대로 — 어두운 바탕 · 크림 글, 가는 산세리프 영어 제목 두 줄,
    한국어 리드 두 줄, 사진마다 영어 한 낱말 + 한국어 설명 + 출처 한 줄, 위아래 기준선 · 십자 · 바닥 줄.
사례: 6 Desjobert(쪽당 제목 + 2–4줄) · 1 ETÉREO(굵은 첫 낱말 캡션, 앞의 말을 뒤에서 회수) · 2 Galatasaray(같은 메시지 반복 — '공간을 읽는다').
글: 카페 · 창고는 사용자 원문(쪽 화면) 그대로의 사실을 '-다' 꼴로. 봉사는 InDesign 파일에서 읽힌 낱말
    (해비타트 · 다녀왔습니다 · 도배 · 페인트 · 주거 · 새단장 · 낡고 · 환경으로 · 예산을 배분하여 · 직접 뛰며 · 삶의 · 개선시켜주는 · 잊지 · 경험으로)로
    다시 짠 초안 — 원문 확인 필요. 봉사 사진은 InDesign 파일 밖 링크라 받지 못해 사진 자리만 둔다.
사진: CF-01 · ST-01–04 는 사용자가 보낸 쪽 화면에서 잘라 낸 것(해상도 낮음) — InDesign 에서 원본(IMG_78xx 등)으로 다시 연결.
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import part2_match as p2  # noqa: E402

d, W, H = p2.d, p2.W, p2.H
OUT, TMP, PRINT, FONTS, CROPS = p2.OUT, p2.TMP, p2.PRINT, p2.FONTS, p2.CROPS
SRC = os.path.join(p2.REPO, 'docs/jaju_rounding_vmd/assets/outside')
BG, CR, MUTE = '#D7D6D3', '#1B1B1A', '#6E6A64'   # 부록: 밝은 회색 종이 + 먹색 (사용자 원래 카페 쪽 #C3C3C3 보다 한 톤 밝게)
BODY, SUBK = '#34322F', '#4A4743'
L, R, CX, FOLIO_Y = 14.0, 301.0, 157.5, 184.35

HALL = ('카페 아르바이트를 하며, 공간이 가진 잠재력에 비해 테이블 배치가 아쉽다고 느꼈다. 홀의 규모와 창문, 테이블 간격을 바탕으로 '
        '테이블을 다시 놓고, 식물로 손님끼리 시선이 마주치는 곳을 가려 공간을 나누었다.')
STORE = ('매장 지하 창고는 수납이 정돈되어 있지 않았다. 선반을 그리드로 나눠 품목별로 수납을 분리하고, 모든 물품을 다시 정돈해 '
         '재고 관리와 업무 효율을 높였다.')
HABITAT = ('해비타트 봉사에 다녀왔다. 도배와 페인트로 낡은 주거 공간을 새로 단장해, 사는 사람에게 조금 더 나은 환경으로 바꾸었다. '
           '정해진 예산을 나눠 쓰며 현장을 직접 뛰었고, 공간을 바꾸는 일이 누군가의 삶을 바꾼다는 것을 잊지 못할 경험으로 배웠다.')


def place(name, x, y, w, h, fx=.5, fy=.5):
    """사진을 틀 비율로 잘라(가운데 fx, fy) 넣는다."""
    im = Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB')
    IW, IH = im.size
    if IW / IH > w / h:
        cw, ch = IH * w / h, IH
    else:
        cw, ch = IW, IW * h / w
    l, t = max(0, min(IW - cw, fx * IW - cw / 2)), max(0, min(IH - ch, fy * IH - ch / 2))
    os.makedirs(CROPS, exist_ok=True)
    f = os.path.join(CROPS, f'out_{name}_{w:.0f}x{h:.0f}.jpg')
    im.crop((int(l), int(t), int(l + cw), int(t + ch))).save(f, quality=92)
    return d(x, y, w, h, f"<img src='file://{f}' style='position:absolute;left:0;top:0;width:{w}mm;height:{h}mm'>", 'ph')


def slot(x, y, w, h, label):
    """받지 못한 사진의 자리 — 점선 틀 + 이름(InDesign 에서 사진을 넣는다)."""
    return (f"<svg class='ov' viewBox='0 0 {W} {H}'><rect x='{x}' y='{y}' width='{w}' height='{h}' class='slot'/></svg>"
            + d(x + 2.4, y + 2.2, w - 4.8, 4, f'<p>{label}</p>', 't cap3'))


def cap(x, y, w, word, ko, src):
    return (d(x, y, w, 7, f'<p>{word}</p>', 't cw')
            + d(x, y + 7.4, w, 4, f'<p>{ko}</p>', 't ck')
            + d(x, y + 11.3, w, 4, f'<p>{src}</p>', 't cs'))


def frame(name, no):
    """부록 표시: 오른쪽 위 'APPENDIX · A-n' 꼬리표, 바닥 줄 'FROM THE INSIDE — APPENDIX' · 쪽 이름 · A-n."""
    return (p2.rules(CR, .35)
            + d(R - 39.6, 14.1, 15.4, 4.4, '', 'tagbox')                 # 먹색 상자 — 글과 따로(InDesign 에서도 남게)
            + d(R - 38.4, 14.75, 14, 4, '<p>APPENDIX</p>', 't tag w')
            + d(R - 30, 14.75, 30, 4, f'<p>{no}&nbsp;&nbsp;·&nbsp;&nbsp;학교 밖</p>', 't tag')
            + d(L, FOLIO_Y, 160, 4, '<p>FROM THE INSIDE&nbsp;&nbsp;—&nbsp;&nbsp;APPENDIX</p>', 't ft')
            + d(107.5, FOLIO_Y, 100, 4, f'<p>{name}</p>', 't ft c')
            + d(261, FOLIO_Y, 40, 4, f'<p>{no}</p>', 't ft r'))


def page_space():
    """학교 밖 1 — 같은 공간을 다시 쓰다 (카페 홀 · 매장 창고)."""
    gx, gy, c1, c2, gap, rh = 163, 22, 88, 46, 4, 66
    o = [d(L, 16, 140, 30, '<p>Same space,</p><p>used again.</p>', 't ttl5'),
         d(L, 43, 140, 12, '<p>학교 밖에서도 먼저 공간을 읽었다.</p><p>새로 사지 않고, 있던 것의 자리를 다시 정했다.</p>', 't lead'),
         place('CF-01', L, 62, 58, 80, .5, .5),
         cap(L, 145, 58, 'Hall', '카페 홀 — 테이블 재배치 · 식물로 나눈 시선', 'CAFÉ, PART-TIME'),
         d(80, 62, 70, 5, '<p>(1) HALL</p>', 't no'),
         d(80, 68, 70, 34, f'<p>{HALL}</p>', 't body wrap'),
         d(80, 104, 70, 5, '<p>(2) STORAGE</p>', 't no'),
         d(80, 110, 70, 28, f'<p>{STORE}</p>', 't body wrap'),
         d(80, 145, 70, 14, '<p>같은 공간도 무엇을 어디에 두느냐에 따라 쓰임이 달라진다.</p>', 't end wrap'),
         place('ST-01', gx, gy, c1, rh), place('ST-02', gx + c1 + gap, gy, c2, rh),
         place('ST-03', gx, gy + rh + gap, c1, rh), place('ST-04', gx + c1 + gap, gy + rh + gap, c2, rh),
         cap(gx, gy + 2 * rh + gap + 3, 90, 'Storage', '매장 지하 창고 — 그리드로 나눈 품목별 수납', 'STORE BASEMENT, PART-TIME'),
         d(R - 60, gy + 2 * rh + gap + 3, 60, 14, '<p>01 – 04</p><p>선반 · 품목별 칸</p>', 't cs r'),
         frame('SAME SPACE', 'A-1')]
    return ''.join(o)


def page_habitat():
    """학교 밖 2 — 누군가의 방을 새로 (해비타트 봉사). 사진은 자리만."""
    o = [d(L, 16, 140, 30, '<p>A room,</p><p>made new.</p>', 't ttl5'),
         d(L, 43, 140, 12, '<p>공간을 고치는 일은, 그 안에 사는 사람의 하루를 바꾼다.</p>'
                           '<p>해비타트 봉사에서, 그것을 직접 겪었다.</p>', 't lead'),
         d(L, 62, 66, 44, f'<p>{HABITAT}</p>', 't body wrap'),
         slot(L, 110, 66, 44, '사진 — 도배 · 페인트 작업'),
         cap(L, 157, 66, 'Habitat', '해비타트 봉사 — 낡은 주거 공간 새단장', 'VOLUNTEER'),
         slot(86, 62, 64, 92, '사진 — 고친 뒤의 방'),
         slot(163, 22, 138, 100, '사진 — 현장 / 함께한 사람들'),
         d(163, 128, 138, 12, '<p>JAJU 가 채우는 것도,</p><p>누군가의 하루가 머무는 공간이다.</p>', 't close'),
         d(163, 144, 138, 10, "<p>What JAJU fills, too, is a space where someone's day is lived.</p>", 't en'),
         d(163, 156, 138, 10, '<p>보고 → 맞추고 → 공간을 읽고 → 채운다</p>', 't cs'),
         frame('A ROOM, MADE NEW', 'A-2')]
    return ''.join(o)


PAGES = [page_space, page_habitat]

KO = p2.KO
CSS = p2.CSS + f"""
@font-face{{font-family:Lora;font-style:italic;src:url('file://{FONTS}/Lora-Italic.ttf')}}
.ph{{overflow:hidden}}
.ov .slot{{fill:none;stroke:{CR};stroke-opacity:.45;stroke-width:.25;stroke-dasharray:1.4 1}}
.ttl5{{font-family:Inst,sans-serif;font-weight:400;font-size:33pt;line-height:34pt;letter-spacing:-.01em;color:{CR}}}
.lead{{font-family:{KO};font-size:9.6pt;line-height:15pt;color:{CR};word-break:keep-all}}
.no{{font-family:Mono,monospace;font-size:6.6pt;letter-spacing:.08em;color:{MUTE}}}
.body{{font-family:{KO};font-size:7.8pt;line-height:12.6pt;color:{BODY};word-break:keep-all}}.body p{{white-space:normal}}
.end{{font-family:{KO};font-size:8.6pt;line-height:13pt;color:{CR};word-break:keep-all;-webkit-text-stroke:.15pt {CR}}}.end p{{white-space:normal}}
.cw{{font-family:Inst,sans-serif;font-weight:400;font-size:14pt;line-height:16pt;color:{CR}}}
.ck{{font-family:{KO};font-size:6.8pt;line-height:9pt;color:{SUBK}}}
.cs{{font-family:Inst,sans-serif;font-size:6.2pt;line-height:8.4pt;letter-spacing:.04em;color:{MUTE}}}.cs.r{{text-align:right}}
.cap3{{font-family:{KO};font-size:6.4pt;color:{MUTE}}}
.close{{font-family:{KO};font-size:15pt;line-height:21pt;color:{CR};-webkit-text-stroke:.25pt {CR}}}
.en{{font-family:Lora,serif;font-style:italic;font-size:8pt;line-height:11pt;color:{MUTE}}}
.ft{{color:{MUTE}}}.ft.r{{text-align:right}}
.tag{{font-family:Mono,monospace;font-size:6.4pt;letter-spacing:.08em;color:{CR};text-align:right;white-space:nowrap}}
.tagbox{{background:{CR}}}.tag.w{{color:{BG};text-align:left}}
"""


def html_doc():
    sheets = ''.join(f"<div class='sheet' style='background:{BG}'>{fn()}</div>" for fn in PAGES)
    return (f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU outside pages</title><style>{CSS}</style></head>"
            f"<body>{sheets}</body></html>")


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'outside_pages.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(html_doc())
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'outside_pages.pdf'), os.path.join(TMP, 'outp')], check=True)


if __name__ == '__main__':
    main()
