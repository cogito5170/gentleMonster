"""Drawing kit for the CV blueprint sheets (SVG in mm). Used by cv_types.py.

Inside an A4 drawing every size is the real printed size; colours are named by the current theme
("text", "sub", "card", ...) so one layout can be drawn dark or light.
"""
from html import escape

PT = 0.3528  # 1 pt in mm
SANS = "Inter, 'Noto Sans CJK KR', sans-serif"
KR = "'Noto Sans CJK KR', Inter, sans-serif"
MONO = "'Noto Sans Mono', 'Noto Sans Mono CJK KR', monospace"

DARK = dict(bg="#0B0B0B", card="#1E1E1E", side="#151515", photo="#2E2E2E", px="#454545",
            text="#ECE8E1", sub="#8E8B86", line="#3A3A3A", grid="#262626")
LIGHT = dict(bg="#E6E2DA", card="#DAD5CB", side="#DAD5CB", photo="#BDB7AC", px="#A39D92",
             text="#141414", sub="#5E5A54", line="#B4AEA4", grid="#CFC9BF")
INK, INK2, RULE, RED = "#15191B", "#5B656B", "#C5CDD1", "#9A4A3A"

OUT: list = []
TH = dict(DARK)


def theme(d):
    TH.clear(); TH.update(d)


def c(v):
    return TH.get(v, v) if isinstance(v, str) else v


def w(s):
    OUT.append(s)


def width(s, pt):
    """rough advance width in mm (Hangul ~1 em, Latin ~0.58 em)."""
    em = pt * PT
    return sum((1.0 if ord(ch) > 0x1100 else 0.3 if ch == " " else 0.6 if ch.isupper() else 0.55) for ch in s) * em


def wrap(s, maxw, pt):
    out, cur = [], ""
    for word in s.split(" "):
        trial = (cur + " " + word).strip()
        if cur and width(trial, pt) > maxw:
            out.append(cur); cur = word
        else:
            cur = trial
    if cur:
        out.append(cur)
    return out


def t(x, y, s, pt=6, fill="text", weight=400, anchor="start", fam=SANS, ls=0, op=1):
    w(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" font-size="{pt * PT:.3f}" font-weight="{weight}" '
      f'fill="{c(fill)}" text-anchor="{anchor}" letter-spacing="{ls:.3f}" opacity="{op}">{escape(s)}</text>')


def lines(x, y, rows, pt=5.4, lh=1.45, **k):
    for i, s in enumerate(rows):
        t(x, y + i * pt * PT * lh, s, pt, **k)
    return y + len(rows) * pt * PT * lh


def para(x, y, s, maxw, pt=5.4, lh=1.45, **k):
    return lines(x, y, wrap(s, maxw, pt), pt, lh, **k)


def r(x, y, wd, h, fill="none", stroke="none", sw=0.25, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    w(f'<rect x="{x:.2f}" y="{y:.2f}" width="{wd:.2f}" height="{h:.2f}" rx="{rx}" fill="{c(fill)}" stroke="{c(stroke)}" stroke-width="{sw}"{d}/>')


def ln(x1, y1, x2, y2, stroke="line", sw=0.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    w(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{c(stroke)}" stroke-width="{sw}"{d}/>')


def photo(x, y, wd, h, tag, note, rx=0, at=None, fixed_text=None):
    r(x, y, wd, h, "photo", rx=rx)
    ln(x, y, x + wd, y + h, "px", 0.25); ln(x + wd, y, x, y + h, "px", 0.25)
    cx, cy = at or (x + wd / 2, y + h / 2)
    bw = max(width(note, 5.0), width(tag, 6)) + 6
    r(cx - bw / 2, cy - 5, bw, 10, "photo", rx=1)
    t(cx, cy - 0.6, tag, 6, fixed_text or "text", 600, "middle", ls=0.3)
    t(cx, cy + 3.2, note, 5.0, fixed_text or "sub", 400, "middle", KR)


def arrow(cx, cy, label, rr=1.9, pt=4.8, fill="text"):
    w(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{c("sub")}" stroke-width="0.25"/>')
    ln(cx - 0.7, cy + 0.7, cx + 0.7, cy - 0.7, fill, 0.25)
    ln(cx - 0.1, cy - 0.7, cx + 0.7, cy - 0.7, fill, 0.25); ln(cx + 0.7, cy - 0.7, cx + 0.7, cy + 0.1, fill, 0.25)
    if label:
        t(cx + rr + 1.4, cy + 0.7, label, pt, fill, 500, ls=0.15)


def hatch_pill(x, y, wd, h, label, pt=4.6):
    r(x, y, wd, h, "url(#hatch)", "text", 0.25, 0.8, "0.6 0.4")
    t(x + wd / 2, y + h / 2 + pt * PT * 0.36, label, pt, "text", 600, "middle", ls=0.2)


# tools in workflow order: (badge, name, stage). Stage = what the tool is for; the applicant's own line is ____.
TOOLS = [("Ac", "AutoCAD", "2D 도면"), ("Rh", "Rhino", "3D 모델링"), ("En", "Enscape", "렌더링"),
         ("Ps", "Photoshop", "후보정"), ("Ai", "Illustrator", "벡터 그래픽"), ("Id", "InDesign", "편집 · 레이아웃")]
FLOW = "2D → 3D → RENDER → RETOUCH → GRAPHIC → EDITORIAL"


def ring(cx, cy, rr, mono, pt=None, sw=0.7):
    pt = pt or rr * 1.75
    w(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rr}" fill="none" stroke="{c("line")}" stroke-width="{sw}"/>')
    # proficiency arc: value not decided -> dashed 3/4 placeholder
    w(f'<path d="M{cx:.2f},{cy - rr:.2f} A{rr},{rr} 0 1 1 {cx - rr:.2f},{cy:.2f}" fill="none" stroke="{c("sub")}" '
      f'stroke-width="{sw}" stroke-dasharray="{rr * 0.21:.2f} {rr * 0.14:.2f}"/>')
    t(cx, cy + pt * PT * 0.37, mono, pt, "text", 700, "middle")


def skill_h(x, y, tool, rr=4.2, name_pt=5.6, small=4.8, maxw=None, line="____ (이 툴로 할 수 있는 일)"):
    """ring left, text right (skill ref B)."""
    mono, name, stage = tool
    ring(x + rr + 0.1, y + rr + 0.4, rr, mono)
    tx = x + 2 * rr + 2.2
    t(tx, y + rr * 0.62, name, name_pt, "text", 600, ls=0.1)
    t(tx, y + rr * 0.62 + small * PT * 1.55, stage, small, "sub", 500, fam=KR)
    t(tx, y + rr * 0.62 + small * PT * 3.1, line, small, "sub", 400, fam=KR, op=0.75)


def skill_v(x, y, wd, tool, rr=5, center=True):
    """ring on top, text below (skill ref A)."""
    mono, name, stage = tool
    cx = x + wd / 2 if center else x + rr + 0.2
    a = "middle" if center else "start"
    ring(cx, y + rr + 0.4, rr, mono)
    ty = y + 2 * rr + 4.2
    tx = cx if center else x
    t(tx, ty, name, 5.6, "text", 600, a, ls=0.1)
    t(tx, ty + 2.8, stage, 4.8, "sub", 500, a, KR)
    t(tx, ty + 5.4, "____", 4.8, "sub", 400, a, KR, op=0.75)


def crosshair(x, y, s=1.4, stroke="sub"):
    ln(x - s, y, x + s, y, stroke, 0.2); ln(x, y - s, x, y + s, stroke, 0.2)


def tag(cx, cy, n, rr=2.3):
    w(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rr}" fill="{INK}"/>')
    t(cx, cy + 0.95 * rr / 2.3, n, 7 * rr / 2.3, "#FFFFFF", 700, "middle")


# ------------------------------------------------------------------ sheet
def sheet_open():
    OUT.clear()
    w('<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">')
    w('<defs><pattern id="hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
      '<rect width="1.2" height="1.2" fill="#262626"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#8E8B86" stroke-width="0.4"/></pattern>'
      '<marker id="ar" viewBox="0 0 6 6" refX="3" refY="3" markerWidth="3" markerHeight="3" orient="auto-start-reverse">'
      f'<path d="M0,0 L6,3 L0,6 z" fill="{INK}"/></marker></defs>')
    r(0, 0, 420, 297, "#FFFFFF")
    r(6, 6, 408, 285, stroke=INK, sw=0.5)


def sheet_close(path):
    w('</svg>')
    path.write_text("\n".join(OUT), encoding="utf-8")


def drawing(fn, ox, oy, s, th):
    theme(th)
    w(f'<g transform="translate({ox},{oy}) scale({s})">')
    fn()
    w('</g>')
    theme(DARK)


def dimline(x1, y1, x2, y2, label, vertical=False):
    w(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{INK}" stroke-width="0.2" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    if vertical:
        w(f'<text transform="translate({x1 - 1.2:.2f},{(y1 + y2) / 2:.2f}) rotate(-90)" font-family="{SANS}" font-size="{5.6 * PT}" '
          f'fill="{INK}" text-anchor="middle" font-weight="500">{escape(label)}</text>')
    else:
        t((x1 + x2) / 2, y1 - 1.1, label, 5.6, INK, 500, "middle")


def dims(ox, oy, s, zones, xsplits=None, note=""):
    D = lambda v: v * s
    dimline(ox, oy - 3.5, ox + D(210), oy - 3.5, "210")
    dimline(ox - 4, oy, ox - 4, oy + D(297), "297", True)
    if xsplits:  # horizontal divisions under the page
        yy = oy + D(297) + 3
        for a, b in zip(xsplits, xsplits[1:]):
            dimline(ox + D(a), yy, ox + D(b), yy, f"{b - a:g}")
    if note:
        t(ox, oy + D(297) + (8.5 if xsplits else 5.6), note, 5.2, INK2, 400, fam=KR)
    zx = ox + D(210) + 3
    for n, name, y0, y1 in zones:
        a, b = oy + D(y0), oy + D(y1)
        ln(zx, a, zx + 2, a, INK, 0.2); ln(zx, b, zx + 2, b, INK, 0.2); ln(zx + 1, a, zx + 1, b, INK, 0.2)
        tag(zx + 5.5, (a + b) / 2, n)
        t(zx + 8.8, (a + b) / 2 - 0.2, name, 5.2, INK, 600, ls=0.15)
        t(zx + 8.8, (a + b) / 2 + 2.4, f"{y1 - y0:g}", 5.0, INK2, 400)


def table(x, y, cols, rows, pt=5.3, lh=2.65, head=None, gap=1.9, colors=None):
    """cols: [(dx, width)], rows: tuples of strings. returns new y."""
    if head:
        for (dx, _), h in zip(cols, head):
            t(x + dx, y, h, pt, INK, 700, fam=KR)
        ln(x, y + 1.4, x + cols[-1][0] + cols[-1][1], y + 1.4, INK, 0.3)
        y += 4.6
    for row in rows:
        n = 1
        for i, ((dx, wd), cell) in enumerate(zip(cols, row)):
            ls = wrap(cell, wd - 1.5, pt)
            fill = (colors[i] if colors else INK)
            if "____" in cell and i == len(cols) - 1:
                fill = RED
            for j, s in enumerate(ls):
                t(x + dx, y + j * lh, s, pt, fill, 700 if i == 0 and colors is None else 400, fam=KR)
            n = max(n, len(ls))
        y += n * lh + gap
        ln(x, y - gap / 2 - 1.2, x + cols[-1][0] + cols[-1][1], y - gap / 2 - 1.2, RULE, 0.2)
    return y


def heading(x, y, en, ko=""):
    t(x, y, en, 8, INK, 700, ls=0.3)
    if ko:
        t(x + width(en, 8) * 1.3 + 4, y, ko, 5.6, INK2, 400, fam=KR)
    return y + 5


def scale_bar(x, y, wd, pos, labels=("절제", "과감"), marks=None):
    """restraint <-> bold scale; pos in 1..5."""
    ln(x, y, x + wd, y, INK, 0.3)
    for i in range(5):
        xx = x + i * wd / 4
        ln(xx, y - 1, xx, y + 1, INK, 0.25)
    t(x, y + 4.2, labels[0], 5.2, INK, 600, fam=KR)
    t(x + wd, y + 4.2, labels[1], 5.2, INK, 600, "end", fam=KR)
    if marks:
        for p, lab in marks:
            xx = x + (p - 1) * wd / 4
            w(f'<circle cx="{xx:.2f}" cy="{y:.2f}" r="1.5" fill="#FFFFFF" stroke="{INK}" stroke-width="0.3"/>')
            t(xx, y - 2.6, lab, 5, INK, 700, "middle")
    else:
        xx = x + (pos - 1) * wd / 4
        w(f'<circle cx="{xx:.2f}" cy="{y:.2f}" r="1.7" fill="{INK}"/>')
