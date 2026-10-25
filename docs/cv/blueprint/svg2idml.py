"""Convert one of our A4 drawing SVGs (bp.py output, units mm) to an InDesign IDML file.

    python3 docs/cv/blueprint/svg2idml.py docs/cv/ai/CV_TYPE2C_SIDEBAR.svg docs/cv/indesign/CV_TYPE2C_SIDEBAR.idml

What is carried over: rectangles (with rounded corners), circles, lines, the dashed proficiency arcs (as open
paths), and every <text> as its own one-line text frame, placed on the same baseline. Fonts in InDesign:
Latin text -> Inter (weights by name), any text with Hangul -> Noto Sans KR. Zone groups (<g id>) become
InDesign groups named after the zone. The IDML writer is the portfolio session's html2idml.Doc.
"""
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import idml_writer as IW  # noqa: E402

PT = 0.3528
SVG = "{http://www.w3.org/2000/svg}"
HANGUL = re.compile(r"[ㄱ-ㆎ가-힣]")
INTER_W = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}
NOTO_W = {100: "Thin", 200: "Light", 300: "Light", 400: "Regular", 500: "Medium", 600: "Bold", 700: "Bold", 800: "Black"}
INTER_FILE = {"Thin": "Inter-Thin", "ExtraLight": "Inter-ExtraLight", "Light": "Inter-Light", "Regular": "Inter-Regular",
              "Medium": "Inter-Medium", "SemiBold": "Inter-SemiBold", "Bold": "Inter-Bold", "ExtraBold": "Inter-ExtraBold"}
_fonts = {}


def measure(text, family, style, size_pt):
    key = (family, style)
    if key not in _fonts:
        if family == "Inter":
            _fonts[key] = ImageFont.truetype(f"/usr/share/fonts/opentype/inter/{INTER_FILE[style]}.otf", 1000)
        else:
            f = "Bold" if style in ("Bold", "Black") else "Regular"
            _fonts[key] = ImageFont.truetype(f"/usr/share/fonts/opentype/noto/NotoSansCJK-{f}.ttc", 1000, index=1)
    return _fonts[key].getlength(text) / 1000 * size_pt * PT


def rgb(hexs, op=1.0):
    if not hexs or hexs == "none" or hexs.startswith("url("):
        return None
    h = hexs.lstrip("#")
    return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {op})"


class Doc(IW.Doc):
    """adds rounded corners and named groups to the portfolio writer."""

    def rect(self, it):
        out = super().rect(it)
        rx = it.get("rx", 0)
        if out and rx:
            r = rx * IW.MM
            corners = "".join(f' {c}CornerOption="RoundedCorner" {c}CornerRadius="{r:.4f}"' for c in ("TopLeft", "TopRight", "BottomLeft", "BottomRight"))
            out = out.replace(' ContentType="Unassigned"', ' ContentType="Unassigned"' + corners, 1)
        return out

    def page(self, pg):
        o = []
        for name, items in pg["groups"]:
            body = "".join({"rect": self.rect, "line": self.line, "text": self.text}[it["kind"]](it) for it in items)
            if not body:
                continue
            if name and body.count("Self=") > 1:
                o.append(f'<Group Self="{self.uid("grp")}" Name="{IW.q(name)}" ItemLayer="uL" ItemTransform="1 0 0 1 0 0">{body}</Group>')
            else:
                o.append(body)
        return "".join(o)


def convert(svg_path):
    root = ET.parse(svg_path).getroot()
    groups, cur = [], [None, []]
    groups.append(cur)

    def walk(el, zone):
        nonlocal cur
        for ch in el:
            tag = ch.tag.replace(SVG, "")
            if tag == "g":
                z = ch.get("id")
                if z:
                    cur = [z, []]
                    groups.append(cur)
                walk(ch, z or zone)
                if z:
                    cur = [None, []]
                    groups.append(cur)
                continue
            items = cur[1]
            op = float(ch.get("opacity", 1))
            if tag == "rect":
                fill = ch.get("fill")
                if fill and fill.startswith("url("):
                    fill = "#262626"
                items.append(dict(kind="rect", rect=dict(x=float(ch.get("x")), y=float(ch.get("y")), w=float(ch.get("width")), h=float(ch.get("height"))),
                                  fill=rgb(fill), stroke=rgb(ch.get("stroke")), sw=float(ch.get("stroke-width", 0)) if rgb(ch.get("stroke")) else 0,
                                  dashed=bool(ch.get("stroke-dasharray")), rx=float(ch.get("rx", 0)), opacity=op))
            elif tag == "circle":
                cx, cy, rr = float(ch.get("cx")), float(ch.get("cy")), float(ch.get("r"))
                items.append(dict(kind="rect", oval=True, rect=dict(x=cx - rr, y=cy - rr, w=2 * rr, h=2 * rr),
                                  fill=rgb(ch.get("fill")), stroke=rgb(ch.get("stroke")), sw=float(ch.get("stroke-width", 0)), opacity=op))
            elif tag == "line":
                items.append(dict(kind="line", pts=[(float(ch.get("x1")), float(ch.get("y1"))), (float(ch.get("x2")), float(ch.get("y2")))],
                                  stroke=rgb(ch.get("stroke")), sw=float(ch.get("stroke-width", 0.2)), dashed=bool(ch.get("stroke-dasharray")), opacity=op))
            elif tag == "path":   # the 3/4 proficiency arc: M x,y A r,r 0 1 1 x2,y2
                m = re.match(r"M([\d.\-]+),([\d.\-]+) A([\d.]+),([\d.]+) 0 1 1 ([\d.\-]+),([\d.\-]+)", ch.get("d", ""))
                if m:
                    x0, y0, rr = float(m.group(1)), float(m.group(2)), float(m.group(3))
                    cx, cy = x0, y0 + rr
                    pts = [(cx + rr * math.cos(math.radians(-90 + a)), cy + rr * math.sin(math.radians(-90 + a))) for a in range(0, 271, 6)]
                    items.append(dict(kind="line", pts=pts, stroke=rgb(ch.get("stroke")), sw=float(ch.get("stroke-width", 0.5)), dashed=True, opacity=op))
            elif tag == "text":
                s = "".join(ch.itertext())
                if not s.strip():
                    continue
                size = float(ch.get("font-size")) / PT
                wgt = int(ch.get("font-weight", 400))
                if HANGUL.search(s):
                    fam, style = "Noto Sans KR", NOTO_W.get(wgt, "Regular")
                else:
                    fam, style = "Inter", INTER_W.get(wgt, "Regular")
                ls_mm = float(ch.get("letter-spacing", 0))
                w_ = measure(s, fam, style, size) + ls_mm * len(s)
                anchor = ch.get("text-anchor", "start")
                x = float(ch.get("x"))
                x0 = x if anchor == "start" else x - w_ if anchor == "end" else x - w_ / 2
                base = float(ch.get("y"))
                asc = (0.969 if fam == "Inter" else 0.88) * size * PT
                items.append(dict(kind="text", runs=[dict(text=s, size=size, family=fam, weight=wgt, italic=False, color=rgb(ch.get("fill")),
                                                          ls=ls_mm / (size * PT), dataFont=f"{fam}|{style}")],
                                  lead=size * 1.2, box=dict(x=x0, y=base - asc, w=w_, h=asc + 0.25 * size * PT),
                                  align={"start": "left", "end": "right", "middle": "center"}[anchor], wrap=False, opacity=op))
    walk(root, None)
    return dict(bg=None, groups=[(n, it) for n, it in groups if it])


def main(svg, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    page = convert(svg)
    doc = IW.build_pages([page], str(out), 1, 210, 297, doc_cls=Doc)
    links = out.parent / "Links"
    if links.exists() and not any(links.iterdir()):
        links.rmdir()
    print("wrote", out, len(doc.stories), "text frames", len(doc.colors), "colours", len(doc.pstyles), "paragraph styles")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
