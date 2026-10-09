"""Read a flat A4 layout (SVG in page millimetres) so a sheet can be rebuilt in the 3D set.

The layout stays the single source of positions: rects become panels or openings, circles become ring
badges or button outlines, text becomes sharp type runs for post.py. Group ids (T1_03_HERO, ...) tell the
builder what each part is.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2000/svg}"
HANGUL = re.compile(r"[가-힣]")


def _f(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def read(path):
    root = ET.parse(path).getroot()
    groups = {}
    for g in root.iter(NS + "g"):
        items = []
        for el in g:
            tag = el.tag.replace(NS, "")
            a = el.attrib
            if tag == "rect":
                items.append(dict(kind="rect", x=_f(a.get("x")), y=_f(a.get("y")), w=_f(a.get("width")), h=_f(a.get("height")),
                                  rx=_f(a.get("rx")), fill=a.get("fill"), stroke=a.get("stroke")))
            elif tag == "circle":
                items.append(dict(kind="circle", cx=_f(a.get("cx")), cy=_f(a.get("cy")), r=_f(a.get("r")), stroke=a.get("stroke"),
                                  w=_f(a.get("stroke-width"), 0.25)))
            elif tag == "line":
                items.append(dict(kind="line", x0=_f(a.get("x1")), y0=_f(a.get("y1")), x1=_f(a.get("x2")), y1=_f(a.get("y2")),
                                  color=a.get("stroke"), w=_f(a.get("stroke-width"), 0.25)))
            elif tag == "text":
                items.append(dict(kind="text", s=el.text or "", x=_f(a.get("x")), y=_f(a.get("y")), size=_f(a.get("font-size")),
                                  weight=int(_f(a.get("font-weight"), 400)), color=a.get("fill"), anchor=a.get("text-anchor", "start"),
                                  ls=_f(a.get("letter-spacing"))))
            elif tag == "path":
                items.append(dict(kind="path", d=a.get("d"), stroke=a.get("stroke")))
        groups[g.get("id")] = items
    return groups


def font_for(s, weight):
    """Korean (or mixed) strings use Noto Sans KR; Latin-only strings use Archivo at normal width."""
    if HANGUL.search(s):
        return "NotoSansKR-Bold.ttf" if weight >= 600 else "NotoSansKR-Med.ttf" if weight >= 500 else "NotoSansKR-Reg.ttf"
    return "Archivo-Bold.ttf" if weight >= 700 else "Archivo-Semi.ttf" if weight >= 600 else "Archivo-Med.ttf" if weight >= 500 else "Archivo-Med.ttf"


def run(t, **over):
    """An SVG text item as a post.py type run."""
    r = dict(s=t["s"], font=font_for(t["s"], t["weight"]), size=t["size"], x=t["x"], y=t["y"],
             align={"middle": "CENTER", "end": "RIGHT"}.get(t["anchor"], "LEFT"),
             track=(t["ls"] / t["size"]) if t["size"] else 0.0, color=t["color"] or "#ECE8E1")
    r.update(over)
    return r
