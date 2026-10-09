"""Generated plates: SVG drawings made by this system, so their rights are ours ('generated').

They are drawings, not photographs, and every caption says so. They stand in where real images could not be
retrieved or cleared -- the gap is shown, not hidden. A plate is deterministic in (kind, seed).
"""
from __future__ import annotations

import hashlib
import html
import math

KINDS = ("specimen", "site_grid", "strata", "acuity", "exploded", "orbit", "cue", "material")
e = lambda s: html.escape(str(s))


def _rng(seed: str):
    state = [int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], "big")]

    def r():
        state[0] = (state[0] * 6364136223846793005 + 1442695040888963407) % 2**64
        return (state[0] >> 11) / 2**53
    return r


def _frame(cx, cy, w, h, r, ink, sw=2.2, bridge=True):
    """An eyewear front in outline: two lenses, a bridge, two temples' stubs. Parametric, not traced."""
    lw = w * 0.42
    rx = min(r, lw / 2, h / 2)
    left = f'<rect x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{lw:.1f}" height="{h:.1f}" rx="{rx:.1f}"/>'
    right = f'<rect x="{cx + w/2 - lw:.1f}" y="{cy - h/2:.1f}" width="{lw:.1f}" height="{h:.1f}" rx="{rx:.1f}"/>'
    br = (f'<path d="M{cx - w/2 + lw:.1f},{cy - h*0.18:.1f} Q{cx:.1f},{cy - h*0.42:.1f} {cx + w/2 - lw:.1f},{cy - h*0.18:.1f}"/>'
          if bridge else "")
    temples = (f'<path d="M{cx - w/2:.1f},{cy - h*0.35:.1f} l{-w*0.08:.1f},{-h*0.04:.1f}"/>'
               f'<path d="M{cx + w/2:.1f},{cy - h*0.35:.1f} l{w*0.08:.1f},{-h*0.04:.1f}"/>')
    return f'<g fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round">{left}{right}{br}{temples}</g>'


def svg(kind: str, seed: str, pal: dict, label: str = "") -> str:
    r = _rng(f"{kind}|{seed}")
    ink, paper, acc = pal["ink"], pal["paper"], pal["accent"]
    W, H = 1200, 900
    body = []
    if kind == "specimen":
        cols, rows = 3, 2
        for i in range(cols * rows):
            cx = 200 + (i % cols) * 400 + (r() - .5) * 30
            cy = 250 + (i // cols) * 380
            w, h, rr = 230 + r() * 90, 70 + r() * 60, 6 + r() * 40
            body.append(_frame(cx, cy, w, h, rr, ink))
            body.append(f'<text x="{cx - w/2:.0f}" y="{cy + h/2 + 46:.0f}" class="m">F-{int(r()*900+100)} · L{1 + i % 4}</text>')
        body.append(f'<g stroke="{ink}" stroke-width="3"><line x1="80" y1="860" x2="380" y2="860"/>'
                    f'<line x1="80" y1="848" x2="80" y2="872"/><line x1="380" y1="848" x2="380" y2="872"/></g>'
                    f'<text x="80" y="840" class="m">50 mm (drawn, not measured)</text>')
    elif kind == "site_grid":
        for i in range(13):
            body.append(f'<line x1="{60 + i*90}" y1="60" x2="{60 + i*90}" y2="840" stroke="{ink}" stroke-opacity=".25"/>')
        for j in range(10):
            body.append(f'<line x1="60" y1="{60 + j*87}" x2="1140" y2="{60 + j*87}" stroke="{ink}" stroke-opacity=".25"/>')
        for k in range(14):
            x, y = 60 + r() * 1080, 60 + r() * 780
            body.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{5 + r()*9:.0f}" fill="{acc if k % 4 == 0 else ink}"/>'
                        f'<text x="{x+14:.0f}" y="{y+5:.0f}" class="m">{chr(65 + k % 12)}{k+1}</text>')
    elif kind == "strata":
        y = 60
        for i in range(7):
            h = 70 + r() * 70
            pts = " ".join(f"{x},{y + h + math.sin(x / (60 + r()*40)) * 10:.0f}" for x in range(200, 1001, 50))
            body.append(f'<polygon points="200,{y:.0f} 1000,{y:.0f} {pts.replace(" 1000", " 1000")} 1000,{y+h:.0f} 200,{y+h:.0f}" '
                        f'fill="{acc if i == 3 else ink}" fill-opacity="{0.08 + 0.1 * (i % 3)}" stroke="{ink}" stroke-width="1.5"/>')
            body.append(f'<text x="1020" y="{y + h/2:.0f}" class="m">layer {i+1} · {int(y)} cm</text>')
            y += h
            if y > 820:
                break
    elif kind == "acuity":
        size, y = 150, 170
        letters = "EFPTOZLPEDPECFDEDFCZP"
        k = 0
        for row in range(7):
            n = row + 1
            line = letters[k:k + n]; k += n
            body.append(f'<text x="600" y="{y:.0f}" text-anchor="middle" font-size="{size:.0f}" class="a">{e(line)}</text>')
            y += size * 0.95 + 18
            size *= 0.68
        body.append(f'<line x1="140" y1="{y - 10:.0f}" x2="1060" y2="{y - 10:.0f}" stroke="{acc}" stroke-width="3"/>')
    elif kind == "exploded":
        body.append(_frame(600, 380, 560, 170, 50, ink, 3))
        parts = [(260, 680, "temple L"), (940, 680, "temple R"), (600, 160, "bridge"), (380, 760, "hinge"), (820, 760, "lens")]
        for i, (x, y, name) in enumerate(parts):
            body.append(f'<rect x="{x-60}" y="{y-14}" width="120" height="28" rx="6" fill="none" stroke="{ink}" stroke-width="2"/>'
                        f'<line x1="{x}" y1="{y - 14}" x2="{600 + (x-600)*0.4:.0f}" y2="{380 + (y-380)*0.35:.0f}" stroke="{acc}" stroke-dasharray="6 6"/>'
                        f'<text x="{x+70}" y="{y+6}" class="m">{i+1} {name}</text>')
    elif kind == "orbit":
        body.append(f'<rect width="{W}" height="{H}" fill="{ink}"/>')
        for i in range(5):
            body.append(f'<ellipse cx="600" cy="450" rx="{120 + i*95}" ry="{70 + i*55}" fill="none" stroke="{paper}" stroke-opacity="{0.5 - i*0.07:.2f}"/>')
        for i in range(60):
            body.append(f'<circle cx="{r()*W:.0f}" cy="{r()*H:.0f}" r="{r()*1.8+.3:.1f}" fill="{paper}" fill-opacity=".7"/>')
        body.append(f'<circle cx="600" cy="450" r="26" fill="{acc}"/>')
        a = r() * 6.28
        body.append(f'<circle cx="{600 + math.cos(a)*405:.0f}" cy="{450 + math.sin(a)*235:.0f}" r="10" fill="{paper}"/>')
    elif kind == "cue":
        body.append(f'<line x1="80" y1="450" x2="1120" y2="450" stroke="{ink}" stroke-width="2"/>')
        x = 100
        for i in range(9):
            x += 60 + r() * 70
            if x > 1100:
                break
            h = 80 + r() * 220
            up = i % 2 == 0
            body.append(f'<line x1="{x:.0f}" y1="450" x2="{x:.0f}" y2="{450 - h if up else 450 + h:.0f}" stroke="{acc if i == 4 else ink}" stroke-width="2"/>'
                        f'<text x="{x+8:.0f}" y="{(450 - h + 18) if up else (450 + h):.0f}" class="m">Q{i+1}</text>')
    elif kind == "material":
        for i in range(4):
            x0, y0 = 60 + (i % 2) * 560, 60 + (i // 2) * 410
            body.append(f'<rect x="{x0}" y="{y0}" width="520" height="370" fill="{paper}" stroke="{ink}"/>')
            for k in range(140 if i % 2 else 50):
                x, y = x0 + r() * 520, y0 + r() * 370
                if i % 2:
                    body.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + 30 + r()*80:.0f}" y2="{y + (r()-.5)*6:.0f}" stroke="{ink}" stroke-opacity=".35"/>')
                else:
                    body.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r()*22+3:.0f}" fill="{acc if k % 9 == 0 else ink}" fill-opacity=".12"/>')
            body.append(f'<text x="{x0+12}" y="{y0+360}" class="m">swatch {i+1}</text>')
    else:
        raise ValueError(f"unknown plate kind {kind}")
    bg = "" if kind == "orbit" else f'<rect width="{W}" height="{H}" fill="{paper}"/>'
    style = (f'<style>.m{{font:500 22px "Liberation Mono","DejaVu Sans Mono",monospace;fill:{paper if kind == "orbit" else ink}}}'
             f'.a{{font-family:"Liberation Sans","DejaVu Sans",sans-serif;font-weight:700;fill:{ink}}}</style>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{e(label or kind + " plate (generated drawing)")}">{style}{bg}{"".join(body)}</svg>')
