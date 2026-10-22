"""JAJU 포트폴리오 — B18: B17 을 판형 315 × 195 mm 로 옮기고, 사용자가 InDesign 에서 고친 4쪽(/01 Observe.)의 값을 모든 쪽에 맞춘 판.

  python3 tools/jaju_layout/plan_b18.py   ->  docs/jaju_rounding_vmd/layout/plan_b18.pdf (18쪽)

사용자: "4쪽 외곽의 사각 표시, 선 두께, 십자가의 위치 변경, 텍스트 위치 변경 등 변경된 사항을 반영하여 다음 페이지들을 수정하라."
사용자 파일(PORTFOLIO.indd 의 IDML, 4쪽)에서 읽은 값 — docs/jaju_rounding_vmd/layout_315x195.md:
  기준선   위 11.58 · 아래 180.5mm, 14 → 301mm, 두께 0.9pt(0.3175mm)
  십자     가운데 157.5mm(양 끝 14 · 301 은 파트 표지가 아닌 쪽), 팔 1.8mm, 0.2mm
  모서리   크림 0.85pt(0.3mm) — 바깥 모서리 (13.57, 11.57) · (301.42, 11.57) · (13.57, 180.42) · (301.42, 180.42), 팔 6.85mm
           어두운 밑선 0.9mm 는 (14, 12) · (301, 12) · (14, 180) · (301, 180), 팔 6mm
  바닥 줄  7pt, 위 184.35mm, 왼쪽 14 · 가운데 107.5–207.5 · 오른쪽 261–301
  파트 표지 /번호 Lora Italic 20pt → 제목 210 타임라인 Bold 100pt(번호보다 13.09mm 아래) → 한국어 Pretendard Bold 15pt(+33.83) → 영어 Lora Italic 9pt(+43.32),
           한국어 · 영어는 제목보다 4.27mm 안쪽. 4쪽 한국어 문장은 사용자가 고친 '일상 속, 스쳐 지나가는 사람들을 관찰하다.'
옮기는 방법: 쪽 안의 틀은 가로 315/297 · 세로 195/210 배로 자리 · 크기를 옮기고(글자 크기는 그대로), 사진은 새 틀에 맞춰 다시 자른다.
쪽 전체를 덮는 선 그림(SVG)은 같은 비율로 늘인다. 격자 · 모서리 · 바닥 줄 · 파트 표지는 위 값으로 새로 그린다.
"""
import os
import re
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b17 as b17  # noqa: E402

b16, b15, b10 = b17.b16, b17.b15, b17.b10
b7, b4, pe = b10.b7, b10.b4, b10.pe
pc = pe.pc
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT

W, H = 315.0, 195.0
SX, SY = W / 297, H / 210
TOP, BOT, L, R, CX = 11.58, 180.5, 14.0, 301.0, 157.5
RULE_W, CROSS_W = 0.3175, 0.2
FOLIO_Y = 184.35


def MAP(x, y, w, h):
    return (None if x is None else x * SX, None if y is None else y * SY,
            None if w is None else w * SX, None if h is None else h * SY)


# ── 자리 옮기기: div · photo · crop 의 코드만 바꿔 끼운다 (다른 모듈이 이미 들고 있는 이름까지 한꺼번에) ──────
STATE = [0]  # >0 이면 옮기지 않는다 (photo · crop 안의 div, 새로 그리는 것)


def _div_wrap(x, y, w, h, inner='', cls='', style=''):
    if _STATE[0] == 0:
        x, y, w, h = _MAP(x, y, w, h)
        inner = inner.replace("viewBox='0 0 297 210'", "viewBox='0 0 297 210' preserveAspectRatio='none'")
    return _div_orig(x, y, w, h, inner, cls, style)


def _photo_wrap(pid, x, y, w, h, focus=(0.5, 0.5), zoom=1.0, marks=None, grey=False):
    if _STATE[0] == 0:
        x, y, w, h = _MAP(x, y, w, h)
    _STATE[0] += 1
    try:
        return _photo_orig(pid, x, y, w, h, focus, zoom, marks, grey)
    finally:
        _STATE[0] -= 1


def _crop_wrap(pid, x, y, w, h, cx, cy, span, marks=None):
    if _STATE[0] == 0:
        x, y, w, h = _MAP(x, y, w, h)
    _STATE[0] += 1
    try:
        return _crop_orig(pid, x, y, w, h, cx, cy, span, marks)
    finally:
        _STATE[0] -= 1


def swap(fn, wrapper, orig_name):
    g = fn.__globals__
    g[orig_name] = types.FunctionType(fn.__code__, g, fn.__name__ + '_orig', fn.__defaults__)
    g['_MAP'], g['_STATE'] = MAP, STATE
    fn.__code__ = wrapper.__code__


swap(pc.div, _div_wrap, '_div_orig')
swap(pc.photo, _photo_wrap, '_photo_orig')
swap(b7._crop, _crop_wrap, '_crop_orig')
b7.grid = lambda light, vf=False: ''  # 격자는 아래에서 새로 그린다


def _move(html, x, y0, y1):  # plan_b10.move — 옮긴 좌표로 찾는다
    a, b = f"left:{x * SX}mm;top:{y0 * SY}mm;", f"left:{x * SX}mm;top:{y1 * SY}mm;"
    assert a in html, a
    return html.replace(a, b, 1)


b10.move = _move


def raw_div(x, y, w, h, inner='', cls='', style=''):
    return pc._div_orig(x, y, w, h, inner, cls, style)


def raw_t(x, y, w, h, inner, cls, style=''):
    return raw_div(x, y, w, h, inner, 't ' + cls, style)


# ── 격자 · 모서리 ──────────────────────────────────────────────────────────────────────
def grid(light, vf):
    a_rule, a_cross = (.4, .85) if light else (.16, .55)
    ln = lambda x1, y1, x2, y2, wd, col, a: (f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' "
                                              f"style='stroke:{col};stroke-opacity:{a};stroke-width:{wd}'/>")
    cream, under = '#EFE7DA', '#15120F'
    g = ln(L, TOP, R, TOP, RULE_W, cream, a_rule) + ln(L, BOT, R, BOT, RULE_W, cream, a_rule)
    xs = (CX,) if vf else (L, CX, R)
    for x in xs:
        for y in (TOP, BOT):
            g += ln(x - 1.8, y, x + 1.8, y, CROSS_W, cream, a_cross) + ln(x, y - 1.8, x, y + 1.8, CROSS_W, cream, a_cross)
    if vf:
        pl = lambda pts, wd, col, a: (f"<polyline points='{' '.join(f'{p[0]},{p[1]}' for p in pts)}' "
                                      f"style='fill:none;stroke:{col};stroke-opacity:{a};stroke-width:{wd}'/>")
        for (ux, uy, dx, dy), (cx_, cy_) in zip([(14, 12, 1, 1), (301, 12, -1, 1), (14, 180, 1, -1), (301, 180, -1, -1)],
                                               [(13.57, 11.57), (301.42, 11.57), (13.57, 180.42), (301.42, 180.42)]):
            g += pl([(ux + dx * 6, uy), (ux, uy), (ux, uy + dy * 6)], .9, under, .35)
            g += pl([(cx_ + dx * 6.85, cy_), (cx_, cy_), (cx_, cy_ + dy * 6.85)], .3, cream, .9)
    return raw_div(0, 0, W, H, f"<svg class='ov' viewBox='0 0 {W} {H}'>{g}</svg>", '')


FOOT = re.compile(r"class='t (ft[^']*)' style='left:[^;]*mm;top:[^;]*mm;width:[^;]*mm;")


def fix_folios(html):
    def sub(m):
        c = m.group(1)
        x, w = (261, 40) if ' r' in c else (107.5, 100) if ' c' in c else (L, 160)
        return f"class='t {c}' style='left:{x}mm;top:{FOLIO_Y}mm;width:{w}mm;"
    return FOOT.sub(sub, html)


# ── 파트 표지 (사용자 4쪽의 값) ──────────────────────────────────────────────────────
def opener(pid, focus, num, word, ko, en, X, T, foot, dark=False):
    cls = 'pt dk' if dark else 'pt'
    STATE[0] += 1
    try:
        img = pc.photo(pid, 0, 0, W, H, focus=focus)
    finally:
        STATE[0] -= 1
    return ''.join([
        img, '' if dark else "<div class='shadeL'></div>",
        raw_t(X + 1.5, T - 13.09 - .7, 200, 8, num, cls + ' on-num'),
        raw_t(X, T, 290, 30, word, cls + ' on-word'),
        raw_t(X + 4.27, T + 33.83 - .5, 230, 8, ko, cls + ' on-ko'),
        raw_t(X + 4.27, T + 43.32 - .35, 230, 6, en, cls + ' on-en'),
        foot,
    ]).replace("class='t pt on-word'", "data-font='210 타임라인|Bold' class='t pt on-word'").replace(
        "class='t pt dk on-word'", "data-font='210 타임라인|Bold' class='t pt dk on-word'")


def p_observe():
    return opener('PH-13', (0.5, 0.4), '/01', 'Observe.', '일상 속, 스쳐 지나가는 사람들을 관찰하다.',
                  'Outside the shop, in everyday moments, I keep watching people.', 12.5, 124.25,
                  pe.foot_light(2, 'PART 1 OBSERVE'))


def p_fill():
    return opener('FA-02', (0.55, 0.32), '/03', 'Fill.', '웃음이 머문 곳에는 늘 조합이 있었다.',
                  'Where a smile stayed, there was always a combination.', 185.0, 37.1,
                  b4.RAW(9, 'PART 3 FILL'), dark=True)


OPENERS = {2: p_observe, 9: p_fill}
LIGHT, VF, NOGRID = {2, 8, 9}, {2, 6, 9}, {8}


def sheets():
    out, n = [], len(b15.PAGES)
    for i, (p, g) in enumerate(b15.PAGES):
        if i in OPENERS:
            html, g = b10.page(i, OPENERS[i], g)
        else:
            html, g = b10.page(i, p, g)
        html = b17.renumber(html)
        html = html.replace('left:10mm;top:24mm;width:280mm;height:100mm', 'left:{:.3f}mm;top:{:.3f}mm;width:{:.3f}mm;height:{:.3f}mm'.format(*MAP(10, 24, 280, 100)))
        if 0 < i < n - 1:
            html = fix_folios(html)
            if i not in NOGRID:
                html += grid(i in LIGHT, i in VF)
        out.append(f"<div class='sheet {g}'>{html}</div>")
    out.insert(1, f"<div class='sheet'>{b16.p_opening()}</div>")
    return out


CSS = b17.b13.CSS + f"""
@page{{size:{W}mm {H}mm;margin:0}}.sheet{{width:{W}mm;height:{H}mm}}
.shadeL{{width:{W}mm;height:{H}mm}}
.ft{{font-size:7pt}}
.on-num{{font-family:Lora,serif;font-style:italic;font-size:20pt;line-height:24pt;white-space:nowrap}}
.on-word{{font-family:Young,serif;font-weight:700;font-size:100pt;line-height:100pt;white-space:nowrap;-webkit-text-stroke:1.2pt currentColor}}
.on-ko{{font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:15pt;line-height:18pt;white-space:nowrap}}
.on-en{{font-family:Lora,serif;font-style:italic;font-size:9pt;line-height:11pt;white-space:nowrap}}
"""


def html_doc():
    return (f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU plan B18</title><style>{CSS}</style></head>"
            f"<body>{''.join(sheets())}</body></html>")


def main():
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'plan_b18.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(html_doc())
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'plan_b18.pdf'), os.path.join(TMP, 'plan_b18')], check=True)


if __name__ == '__main__':
    main()
