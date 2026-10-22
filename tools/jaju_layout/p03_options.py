"""JAJU 포트폴리오 — 03 쪽 세 가지 안 (B8 의 02 Observe 문장 다음).

  python3 tools/jaju_layout/p03_options.py   ->  docs/jaju_rounding_vmd/layout/p03_options.pdf (3쪽: A · B · C)

02: "가게 밖, 스쳐 지나가는 일상에서도 나는 사람들을 눈여겨본다." 에 이어지는 03 쪽.
  A  Where people stop. — 사람이 멈춘 자리 여섯 곳, 사람마다 점선 틀 (바다 → 거리 → 가게)
  B  What they look at. — 등 뒤에서 본 세 사람 + 그 사람이 보는 것 (메뉴판 · 네온 간판 · 불판)
  C  From far to near.  — 멀리(무리) → 가까이(한 사람) → 바로 뒤(그 사람이 보는 것), 줄마다 사진이 커진다
좌표는 원본 사진의 비율(0–1). 시간대(DUSK · DAY)는 확인된 촬영 정보가 아니라 뺐다. HEX 는 사진(B 는 잘라 낸 칸)에서 잰 값.
"""
import colorsys
import os
import subprocess

from PIL import Image

import plan_b8_observe as b8

b7 = b8.b7
pe, t, OUT, TMP, PRINT = b7.pe, b7.t, b7.OUT, b7.TMP, b7.PRINT
photo, accent, pc = pe.photo, pe.accent, pe.pc


def size(pid):
    return Image.open(pc.path(pid)).size


def sw(hx):
    return f"<span class='sw' style='background:{hx}'></span><span class='hx'>{hx}</span>"


def region(pid, w, h, focus, zoom):
    """photo(pid, ·, ·, w, h, focus, zoom) 가 보여 주는 원본 영역(px) — photo() 와 같은 계산."""
    W, H = size(pid)
    s = max(w / W, h / H) * zoom
    iw, ih = W * s, H * s
    ox = min(0, max(w - iw, w / 2 - focus[0] * iw))
    oy = min(0, max(h - ih, h / 2 - focus[1] * ih))
    return -ox / s, -oy / s, w / s, h / s


def accent_in(pid, box):
    """잘라 낸 칸 안에서 가장 채도 높은 부분의 평균 색."""
    x, y, w, h = box
    im = Image.open(pc.path(pid)).convert('RGB').crop((int(x), int(y), int(x + w), int(y + h)))
    im.thumbnail((200, 200))
    px = list(im.get_flattened_data()) if hasattr(im, 'get_flattened_data') else list(im.getdata())
    key = lambda p: (lambda hsv: hsv[1] * hsv[2])(colorsys.rgb_to_hsv(*(c / 255 for c in p)))
    top = sorted(px, key=key, reverse=True)[:max(8, len(px) // 40)]
    r, g, b = (sum(p[i] for p in top) // len(top) for i in range(3))
    return f'#{r:02X}{g:02X}{b:02X}'


def marks_for(pid, boxes):
    W, H = size(pid)

    def m(to, s):
        o = ''
        for fx, fy, fw, fh, label in boxes:
            x0, y0 = to(fx * W, fy * H)
            r = f"x='{x0:.2f}' y='{y0:.2f}' width='{fw * W * s:.2f}' height='{fh * H * s:.2f}'"
            o += f"<rect {r} class='dshs'/><rect {r} class='dsh'/>"
            if label:
                o += f"<text x='{x0 + .6:.2f}' y='{y0 - 1.1:.2f}' class='afs'>{label}</text>"
        return o
    return m


# ── A · Where people stop. — 사람이 멈춘 자리 여섯 ────────────────────────────────────────
A = [('PH-01', '얕은 물', 'IN SHALLOW WATER', (0.42, 0.52, 0.12, 0.16)),
     ('PH-17', '파라솔 옆', 'BY A PARASOL', (0.27, 0.53, 0.17, 0.2)),
     ('PH-11', '가게 계단', 'ON A SHOP STEP', (0.47, 0.28, 0.2, 0.58)),
     ('PH-07', '불판 앞', 'AT THE GRILL', (0.16, 0.02, 0.36, 0.9)),
     ('PH-04', '간판 앞', 'UNDER THE SIGN', (0.44, 0.56, 0.32, 0.43)),
     ('PH-06', '메뉴판 앞', 'BEFORE THE MENU', (0.22, 0.32, 0.18, 0.66))]


def p_a():
    gx, gy, cw, ch, gap = 100, 22, 89.5, 46.5, 4
    o = [t(14, 22, 80, 10, 'Where people stop', 'h2'),
         t(14, 36, 80, 30, '<p>사람들이 멈춘 자리를 본다.</p><p>얕은 물, 파라솔 옆, 가게 계단,</p><p>불판 앞, 간판 앞, 메뉴판 앞.</p>', 'kb'),
         t(14, 70, 80, 20, '<p>I look at where people stop — in shallow water, by a parasol, on a shop step, at the grill, under a sign, before a menu.</p>', 'enb')]
    for i, (pid, ko, en, b) in enumerate(A):
        r, c = divmod(i, 2)
        x, y = gx + c * (cw + gap), gy + r * (ch + 10)
        o.append(photo(pid, x, y, cw, ch, marks=marks_for(pid, [b + (en,)])))
        o.append(t(x, y + ch + 1.8, cw, 4, f"N°{i + 1:02d}&nbsp;&nbsp;{ko}{sw(accent(pid))}", 'data'))
    o.append(t(14, 148, 80, 40, "<p>17 FRAMES / 06 SHOWN</p><p>SEA → STREET → SHOP</p><p>&nbsp;</p>"
                                "<p>EACH FRAME, ONE BOX —</p><p>WHERE SOMEONE STOPPED.</p>", 'letter'))
    return ''.join(o)


# ── B · What they look at. — 등 뒤에서, 그 사람이 보는 것 ─────────────────────────────────
B = [('PH-06', '메뉴판 앞에 선 사람', '메뉴 사진', (0.22, 0.32, 0.18, 0.66), (0.66, 0.5), 2.4),
     ('PH-04', '노점 앞에 줄 선 사람들', '네온 메뉴', (0.5, 0.45, 0.32, 0.55), (0.36, 0.45), 2.4),
     ('PH-07', '불판 앞에 선 사람', '불판의 불', (0.16, 0.02, 0.36, 0.9), (0.6, 0.8), 2.8)]


def p_b():
    wx, ww, cx, cwid, h = 100, 122, 230, 53, 46
    o = [t(14, 22, 80, 10, 'What they look at', 'h2'),
         t(14, 36, 80, 30, '<p>가게 안에서는 얼굴이 보였다.</p><p>밖에서는 등 뒤에서,</p><p>그 사람이 보는 것을 본다.</p>', 'kb'),
         t(14, 70, 80, 20, '<p>Inside, I saw faces. Outside, from behind, I see what they see.</p>', 'enb')]
    for i, (pid, who, what, pb, cf, cz) in enumerate(B):
        y = 22 + i * (h + 10)
        W, H = size(pid)
        rx, ry, rw, rh = region(pid, cwid, h, cf, cz)  # 오른쪽 칸이 보여 주는 원본 영역
        o.append(photo(pid, wx, y, ww, h, marks=marks_for(pid, [pb + ('',), (rx / W, ry / H, rw / W, rh / H, 'LOOKING AT')])))
        o.append(photo(pid, cx, y, cwid, h, focus=cf, zoom=cz))
        o.append(b7.svg(f"<line x1='{wx + ww + .8}' y1='{y + h / 2}' x2='{cx - .8}' y2='{y + h / 2}' class='lk'/>"))
        o.append(t(wx, y + h + 1.8, ww, 4, f"N°{i + 1:02d}&nbsp;&nbsp;{who}", 'data'))
        o.append(t(cx, y + h + 1.8, cwid, 4, f"{what}{sw(accent_in(pid, (rx, ry, rw, rh)))}", 'data'))
    o.append(t(14, 148, 80, 40, "<p>17 FRAMES / 03 SHOWN</p><p>ALL THREE FROM BEHIND</p><p>&nbsp;</p>"
                                "<p>NOT THE FACE —</p><p>WHAT THE FACE SEES.</p>", 'letter'))
    return ''.join(o)


# ── C · From far to near. — 줄마다 가까워진다 ────────────────────────────────────────────
C = [('FAR', 30, [('PH-03', '노 젓는 여섯 사람', (0.3, 0.55)), ('PH-01', '물에 모인 사람들', (0.5, 0.6)), ('PH-05', '헤엄치는 사람들', (0.5, 0.55))]),
     ('NEAR', 44, [('PH-17', '파라솔 옆에 앉은 사람', (0.36, 0.6)), ('PH-11', '가게 계단에 앉은 사람', (0.55, 0.5))]),
     ('CLOSE', 64, [('PH-07', '불판 앞', (0.32, 0.45)), ('PH-04', '간판 앞', (0.6, 0.6)), ('PH-06', '메뉴판 앞', (0.36, 0.5))])]


def p_c():
    gx, gw, gap = 100, 183, 4
    o = [t(14, 22, 80, 10, 'From far to near', 'h2'),
         t(14, 36, 80, 30, '<p>멀리서는 무리가,</p><p>다가가면 한 사람이,</p><p>바로 뒤에서는 그 사람이 보는 것이 보인다.</p>', 'kb'),
         t(14, 70, 80, 20, '<p>From far, a crowd. Closer, one person. Right behind, what they see.</p>', 'enb')]
    y, n = 22, 0
    for row, h, cells in C:
        cw = (gw - gap * (len(cells) - 1)) / len(cells)
        for j, (pid, cap, f) in enumerate(cells):
            n += 1
            x = gx + j * (cw + gap)
            o.append(photo(pid, x, y, cw, h, focus=f))
            o.append(t(x, y + h + 1.6, cw, 4, f"{row}&nbsp;&nbsp;N°{n:02d}&nbsp;&nbsp;{cap}", 'data'))
        y += h + 8.5
    o.append(t(14, 148, 80, 40, "<p>17 FRAMES / 08 SHOWN</p><p>FAR → NEAR → CLOSE</p><p>&nbsp;</p>"
                                "<p>EACH ROW, ONE STEP CLOSER.</p>", 'letter'))
    return ''.join(o)


OPTIONS = [('A', p_a, 'WHERE PEOPLE STOP'), ('B', p_b, 'WHAT THEY LOOK AT'), ('C', p_c, 'FROM FAR TO NEAR')]
CSS = b7.CSS + """
.ov .dshs{fill:none;stroke:rgba(21,18,15,.55);stroke-width:.9}
.ov .dsh{fill:none;stroke:#EFE7DA;stroke-width:.35;stroke-dasharray:1.4 .9}
.ov.grid .lk{stroke:rgba(239,231,218,.6);stroke-width:.25;stroke-dasharray:1 .8}
.optag{font-family:Mono,monospace;font-size:7pt;letter-spacing:.12em;color:#D9773A}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    sheets = []
    for tag, fn, name in OPTIONS:
        html, g = b7.page(3, fn, 'g0')
        html = html.replace('>WHERE PEOPLE STOP<', f'>{name}<')
        html += t(243, 4, 40, 4, f'03 · 안 {tag}', 'optag r')
        sheets.append(f"<div class='sheet {g}'>{html}</div>")
    h = os.path.join(TMP, 'p03_options.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p03 options</title><style>{CSS}</style></head><body>{''.join(sheets)}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p03_options.pdf'), os.path.join(TMP, 'p03_options')], check=True)


if __name__ == '__main__':
    main()
