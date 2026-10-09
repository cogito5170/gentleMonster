"""Photo issue: a magazine built around the user's own photographs, in the grammar of a museum magazine
(the MCA Magazine reference board: stencil masthead, one strong cover photograph, a numbered contents page, a
gallery wall, one-word pages, a collage with an index, a rotated manifesto, a full-bleed spread, a back cover with
a framed text box) and read through Gentle Monster (research/sources.json).

    python3 -m gentle_monster photo-issue editorial/issues/spa_00_stops.json --name spa00

The issue spec holds the editorial decisions (which photo goes where, which words); the texts in it are the
user's own, copied verbatim from docs/portfolio/ -- check_texts() proves each one is still there. This module
measures the photos (light, colour, brightness), orders and labels them, lays the pages out, prints the PDF and
runs QA. It writes no prose with a model (no Gemini, no other model).

One layout, two sizes: every length on a page is in container units (cqw), so the 230 x 300 mm print page and
the screen page are the same composition. Text-heavy pages reflow on phones.
"""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

from gentle_monster import paths, photos as PH
from gentle_monster.magazine import assets as A, catalogue as CAT, pdf as PDF, qa as QA, render as R

e = lambda s: html.escape(str(s if s is not None else ""))
W_MM, H_MM = 230, 300
PRINT_DPI_MIN = 150          # below this a photograph prints visibly soft


def load(spec_path) -> dict:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    spec["_path"] = str(spec_path)
    return spec


def check_texts(spec: dict) -> list[str]:
    """Every user text in the spec must still be, word for word, in the document it came from."""
    bad = []
    doc = lambda p: (paths.REPO / p).read_text(encoding="utf-8") if (paths.REPO / p).is_file() else ""
    c = spec["cover"]
    for t in c["left"] + c["right"] + c["byline"] + [c["question"]]:
        if t not in doc(c["source"]):
            bad.append(f"cover: '{t}' not in {c['source']}")
    for t in spec["intro"]["ko"] + [spec["intro"]["en"]]:
        if t not in doc(spec["intro"]["source"]):
            bad.append(f"intro: '{t[:30]}' not in {spec['intro']['source']}")
    if spec["manifesto"]["check"] not in doc(spec["manifesto"]["source"]):
        bad.append("manifesto not in its source")
    if " ".join(spec["manifesto"]["lines"]) != spec["manifesto"]["check"]:
        bad.append("manifesto lines do not add up to the checked sentence")
    for b in spec["qa_text"]:
        for t in b["a"]:
            if t not in doc(spec["qa_source"]):
                bad.append(f"Q&A: '{t[:30]}' not in {spec['qa_source']}")
    for t in (spec["back"]["ko"], spec["back"]["en"]):
        if t not in doc(spec["back"]["source"]):
            bad.append(f"back: '{t[:30]}' not in {spec['back']['source']}")
    return bad


def light(m: dict) -> str:
    """Measured, not guessed: 밤 / 흑백 / 해 질 녘 / 흐림 / 낮."""
    if m["mono"]:
        return "흑백" + (" · 밤" if m["dark"] > 0.5 else "")
    if m["dark"] > 0.45 or m["brightness"] < 0.2:
        return "밤"
    if m["warmth"] > 0.06:
        return "해 질 녘"
    if m["saturation"] < 0.12:
        return "흐림"
    return "낮"


def measure_all(spec: dict) -> dict:
    d = paths.REPO / spec["photo_dir"] if not Path(spec["photo_dir"]).is_absolute() else Path(spec["photo_dir"])
    out = {}
    for k in sorted(spec["photos"]):
        f = next((d / f"{k}{x}" for x in (".jpg", ".jpeg", ".png", ".webp") if (d / f"{k}{x}").is_file()), None)
        if f is None:
            out[k] = {"missing": True, "path": str(d / k)}
            continue
        m = PH.measure(f)
        m["light"] = light(m)
        m["palette"] = PH.palette(f, 6)
        out[k] = m
    return out


def _k(n) -> str:
    return f"{int(n):02d}"


# ------------------------------------------------------------------ design system
# ① Layout: 230 x 300 mm, 12 columns, 8 cqw margins, 2 cqw gutters. Every block's left edge sits on a column
#    line (data-col); QA measures it. Left and right pages mirror their outer margins.
# ② Type: one scale in cqw (1 cqw = 2.3 mm on paper). Korean has one weight here (WenQuanYi Zen Hei has no bold),
#    so Korean is never set bold -- emphasis is size and ink, not weight. Latin uses Liberation Sans.
# ③ Image: photos keep their aspect unless a page is a bleed; crops carry a focal point (spec "focus").
# ④ Colour: the pages are paper / ink / grey; colour comes from the photographs. One accent, measured from
#    the cover photograph, marks the cover choice. The index prints each photo's measured palette.
# ⑤ Structure: spec "story" -- a day walked through, ending at a red light.
MARGIN, GUTTER, COLS = 8.0, 2.0, 12
COL = (100 - 2 * MARGIN - (COLS - 1) * GUTTER) / COLS            # 5.1667 cqw
PAGE_H = 100 * H_MM / W_MM                                       # 130.43 cqw
TYPE = {"cap": 1.15, "body": 1.6, "lead": 2.3, "title": 3.6, "word": 12.0}
INK, PAPER, MUTE, RULE, NIGHT, NIGHT_INK = "#141414", "#f7f6f2", "#6b6963", "#d9d7d0", "#0b0b0c", "#e8e6e0"


def X(c: float, mirror: bool = False) -> float:
    """Left edge of column c (0-11). On a mirrored (left-hand) page the grid is the same: outer margins are equal."""
    return round(MARGIN + c * (COL + GUTTER), 3)


def SPAN(n: int) -> float:
    return round(n * COL + (n - 1) * GUTTER, 3)


def accent_of(measure: dict, path: str) -> dict:
    """The cover photograph's most vivid colour, measured per pixel (a median-cut palette averages small vivid
    areas away: it returned a brown #6c554b for the cover whose punctum is an orange cone). Pixels with high
    saturation and value are binned by hue; the bin with the highest mean s*v (and at least 0.2% of the frame)
    wins. Because the accent is used on text, it is then darkened -- hue kept -- until it reaches 4.5:1 on paper."""
    import colorsys
    import numpy as np
    from gentle_monster.magazine import design as DS
    im = PH._load(path, 600)
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255
    rgb = np.asarray(im).astype(float)
    m = (hsv[..., 1] > 0.55) & (hsv[..., 2] > 0.45)
    if m.mean() < 0.002:
        return {"raw": INK, "text": INK, "share": 0.0}
    hue = (hsv[..., 0][m] * 12).astype(int) % 12
    sv = (hsv[..., 1] * hsv[..., 2])[m]
    best, bs = None, -1.0
    for bin_ in range(12):
        sel = hue == bin_
        if sel.mean() * m.mean() < 0.002:
            continue
        sc = float(sv[sel].mean())
        if sc > bs:
            best, bs = bin_, sc
    px = rgb[m][hue == best]
    r, g, b_ = (float(np.median(px[:, i])) for i in range(3))
    raw = "#%02x%02x%02x" % (round(r), round(g), round(b_))
    h, l, s_ = colorsys.rgb_to_hls(r / 255, g / 255, b_ / 255)
    txt = raw
    while DS.contrast(txt, PAPER) < 4.5 and l > 0.05:
        l -= 0.02
        txt = "#%02x%02x%02x" % tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s_))
    return {"raw": raw, "text": txt, "share": round(float((hue == best).sum()) / hue.size * float(m.mean()), 4)}


def masthead_svg(word: str) -> str:
    """A stencil masthead: Liberation Sans Bold with bridges cut where a stencil needs them -- the P's bowl
    lifted off its stem, the A's apex split, the S's curves broken top and bottom. Positions come from the
    glyphs' measured strokes at 1000 units (see tests), not from a repeating stripe."""
    adv = {"S": 667, "P": 667, "A": 722}
    # x, y, w, h in glyph units (y from the ascender line). Measured at 1000 units (tests/test_photo_issue.py):
    # S strokes cross x 316-350 at rows 208-310 (top) and 808-915 (bottom); P's bowl meets the stem at rows
    # 218-329 and 553-663; A's centre column is solid from the apex down to the counter (~440).
    cuts = {"S": [(316, 200, 34, 120), (316, 800, 34, 125)],
            "P": [(210, 210, 34, 462)],
            "A": [(344, 210, 34, 250)]}
    track, x, glyphs, holes = -24, 0, [], []
    for ch in word:
        glyphs.append(f'<text x="{x}" y="906">{html.escape(ch)}</text>')
        for (cx, cy, cw, chh) in cuts.get(ch, []):
            holes.append(f'<rect x="{x + cx}" y="{cy}" width="{cw}" height="{chh}" fill="#000"/>')
        x += adv.get(ch, 667) + track
    w = x - track
    return (f'<svg class="mast" data-bleed viewBox="0 200 {w} 720" preserveAspectRatio="xMinYMin meet" role="img" aria-label="{e(word)}">'
            f'<defs><mask id="stencil"><rect x="0" y="0" width="{w}" height="1000" fill="#fff"/>{"".join(holes)}</mask></defs>'
            f'<g mask="url(#stencil)" fill="{INK}" font-family="Liberation Sans, Arial, Helvetica, sans-serif" font-weight="700" '
            f'font-size="1000">{"".join(glyphs)}</g></svg>')


def css(accent: str) -> str:
    ko = '"WenQuanYi Zen Hei","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic"'
    T = TYPE
    return f"""
:root{{--paper:{PAPER};--ink:{INK};--mute:{MUTE};--rule:{RULE};--night:{NIGHT};--night-ink:{NIGHT_INK};--accent:{accent};
  --sans:"Liberation Sans","Helvetica Neue",Arial,{ko},sans-serif}}
*{{box-sizing:border-box;font-synthesis:none}} html{{background:#2b2b29}}
body{{margin:0;color:var(--ink);font-family:var(--sans);word-break:keep-all;overflow-wrap:break-word;-webkit-font-smoothing:antialiased;
  font-kerning:normal;text-rendering:optimizeLegibility}}
main{{display:flex;flex-wrap:wrap;justify-content:center;padding:28px 0}}
.page{{container-type:inline-size;position:relative;overflow:hidden;background:var(--paper);width:min(46vw,560px);aspect-ratio:{W_MM}/{H_MM};margin-bottom:32px}}
.page.night{{background:var(--night);color:var(--night-ink)}}
.page.cover{{margin-right:46vw}} @media (max-width:1100px){{.page{{width:min(100vw - 32px,560px)}} .page.cover{{margin-right:0}}}}
.a{{position:absolute}} img{{display:block;width:100%;height:100%;object-fit:cover}} img.nat{{height:auto;aspect-ratio:468/258}}
p{{margin:0}}
.cap{{font-size:max({T['cap']}cqw,8.5px);line-height:1.45;color:var(--mute);letter-spacing:.01em}}
.body{{font-size:max({T['body']}cqw,10.5px);line-height:1.72}} .body:lang(en),.en{{line-height:1.5}}
.lead{{font-size:{T['lead']}cqw;line-height:1.6;letter-spacing:-.01em}}
.title{{font-size:{T['title']}cqw;line-height:1.2;letter-spacing:-.02em;font-weight:400}}
.title:lang(en){{font-weight:700;letter-spacing:-.03em}}
.up{{text-transform:uppercase;letter-spacing:.08em}}
.night .cap{{color:#9a988f}}
.rh{{top:5cqw;left:{X(0)}cqw;right:{MARGIN}cqw;display:flex;justify-content:space-between}}
.folio{{position:absolute;bottom:5cqw;font-size:{T['cap']}cqw;color:var(--mute);font-variant-numeric:tabular-nums}}
.folio.l{{left:{X(0)}cqw}} .folio.r{{right:{MARGIN}cqw}}
.mast{{position:absolute;left:-3cqw;top:3cqw;width:103cqw;height:auto;display:block}}
.rule{{border-top:.14cqw solid var(--ink)}} .hair{{border-top:1px solid var(--rule)}}
.sw{{display:inline-block;width:1.5cqw;height:1.5cqw;margin-right:.35cqw;vertical-align:-.25cqw}}
sup{{font-size:.68em;line-height:0;vertical-align:.5em;margin-left:.08em}} sup a{{color:inherit;text-decoration:none}}
.refs{{margin:0;padding:0 0 0 2.4cqw}} .refs li{{margin-bottom:.5cqw}} .refs a{{color:inherit;text-decoration:none;word-break:break-all}}
.mani{{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;font-size:6.2cqw;line-height:1.16;letter-spacing:-.02em}}
.mani sup{{font-size:.36em;vertical-align:0;margin:0 0 .3em 0}}
.split{{top:0;height:100%;width:200%}} .split.l{{left:0}} .split.r{{left:-100%}}
.ghost{{opacity:.1;transform:scaleX(-1)}}
.box{{border:.18cqw solid rgba(255,255,255,.9);color:#fff;background:rgba(10,10,10,.22)}}
.row{{display:grid;grid-template-columns:{COL}cqw {SPAN(2)}cqw {SPAN(5)}cqw {SPAN(2)}cqw {COL}cqw {COL}cqw;column-gap:{GUTTER}cqw;
  align-items:baseline;border-bottom:1px solid var(--rule);padding:1.25cqw 0}}
.row.h{{border-bottom:.14cqw solid var(--ink);padding-top:0}}
.num{{font-variant-numeric:tabular-nums}}
@media (max-width:600px){{
  .page.text{{aspect-ratio:auto;padding:32px 20px 56px}} .page.text .a{{position:static;width:auto!important;transform:none;margin-bottom:18px}}
  .page.text .body{{font-size:15px}} .page.text .lead{{font-size:18px}} .page.text .title{{font-size:24px}} .page.text .cap{{font-size:12px}}
  .page.text .folio{{font-size:12px;bottom:18px}} .page.text .mani{{writing-mode:horizontal-tb;font-size:26px;white-space:normal}}
  .page.cover{{aspect-ratio:auto;padding:39cqw 0 48px}} .page.cover .a:not(.mast){{position:static;width:auto!important;margin:0 {X(0)}cqw 16px}}
  .page.cover .a:not(.mast) > div{{height:auto!important}} .page.cover img{{height:auto;aspect-ratio:468/258}}
  .page.text .row{{grid-template-columns:32px 1fr 64px;font-size:13px}} .page.text .row > :nth-child(2),.page.text .row > :nth-child(5),
  .page.text .row > :nth-child(6){{display:none}} .page.text .rh{{display:flex}}
}}
@page{{size:{W_MM}mm {H_MM}mm;margin:0}}
@media print{{ html{{background:none}} main{{display:block;padding:0}} .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;margin:0;break-after:page}}
  *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}} }}
html.print-sim main{{display:block;padding:0;width:{W_MM}mm}} html.print-sim .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;margin:0}}
"""


def build(spec_path, name: str = "", pdf: bool = True) -> dict:
    spec = load(spec_path)
    bad_text = check_texts(spec)
    meas = measure_all(spec)
    missing = [k for k, m in meas.items() if m.get("missing")]
    out = paths.job_dir(name or spec["id"]) / "photo_issue"
    (out / "img").mkdir(parents=True, exist_ok=True)
    cat = CAT.load()
    src = CAT.by_id(cat)
    claims = {c["id"]: c for c in cat["claims"]}
    focus = spec.get("focus", {})
    story = {s["id"]: s for s in spec["story"]}

    assets = {}
    for k, m in meas.items():
        if m.get("missing"):
            continue
        dst = out / "img" / Path(m["path"]).name
        if not dst.exists() or dst.stat().st_mtime < Path(m["path"]).stat().st_mtime:
            dst.write_bytes(Path(m["path"]).read_bytes())
        assets[k] = A.user_image(str(dst), spec["credit"], spec["rights"], title=f"{k} — {spec['photos'][k]}")
    cov = _k(spec["cover"]["photo"])
    acc = accent_of(meas[cov], meas[cov]["path"]) if cov in assets else {"raw": INK, "text": INK, "share": 0}
    accent = acc["text"]

    def img(n, natural=False, pos=None):
        k = _k(n)
        a = assets.get(k)
        if not a:
            return f'<div class="cap">사진 {k} 없음</div>'
        style = f' style="object-position:{pos or focus.get(k, "50% 50%")}"' if not natural else ""
        return (f'<img class="{"nat" if natural else ""}" src="img/{e(Path(a["local_path"]).name)}" alt="{e(spec["photos"][k])}" '
                f'data-photo="{k}"{style}>')

    def at(col, top, span=None, cls="", inner="", right=None, bottom=None, extra=""):
        pos = f"left:{X(col)}cqw;" + (f"top:{top}cqw;" if top is not None else "") + (f"bottom:{bottom}cqw;" if bottom is not None else "")
        pos += f"width:{SPAN(span)}cqw;" if span else ""
        pos += f"right:{right}cqw;" if right is not None else ""
        return f'<div class="a {cls}" data-col="{col}" style="{pos}{extra}">{inner}</div>'

    pages, refs = [], {}

    def cite(ids):
        out_ = []
        for i in ids:
            for s_ in claims.get(i, {}).get("source_ids", [])[:1]:
                n = refs.setdefault(s_, len(refs) + 1)
                out_.append(f'<a href="#lref-{n}">{n}</a>')
        return f"<sup>{','.join(out_)}</sup>" if out_ else ""

    def page(inner, cls="", kind="photo", photos=(), label="", rh=None):
        n = len(pages) + 1
        side = "l" if n % 2 == 0 else "r"
        fol = "" if kind in ("cover", "back") else f'<div class="folio {side} num">{n:02d}</div>'
        head = ""
        if rh:
            head = (f'<div class="a rh cap up" lang="en"><span>{e(spec["masthead"])} 00</span><span>{e(rh)}</span></div>')
        pages.append({"n": n, "kind": kind, "label": label, "photos": [_k(p) for p in photos], "side": side,
                      "html": f'<section class="page {cls}" id="p{n:02d}" data-type="{kind}" data-label="{e(label)}">{head}{inner}{fol}</section>'})

    c = spec["cover"]
    # 1 ---------------------------------------------------------------- cover
    ph_h = round(SPAN(12) / (468 / 258), 3)
    top = 45
    page(masthead_svg(spec["masthead"])
         + at(0, top, 12, "", f'<div style="height:{ph_h}cqw">{img(cov)}</div>')
         + at(0, top + ph_h + 1.6, 6, "cap up", f'<p lang="en">{e(spec["masthead"])} Magazine — Issue <span style="color:var(--accent)">00</span></p>')
         + at(0, top + ph_h + 9, 5, "body up", '<p lang="en">' + "<br>".join(e(x) for x in c["left"]) + "</p>")
         + at(6, top + ph_h + 9, 6, "body", '<p lang="en">' + "<br>".join(e(x) for x in c["right"]) + "</p>")
         + at(0, None, 5, "body up", '<p lang="en">' + "<br>".join(e(x) for x in c["byline"]) + "</p>", bottom=8)
         + at(6, None, 6, "body", f'<p lang="en" style="font-weight:700">“{e(c["question"])}”</p>', bottom=8),
         "cover", "cover", [cov], "표지")
    # 2 contents | 3 intro ------------------------------------------------
    page(at(0, 16, 12, "", "TOC")
         + at(0, None, 6, "cap", f'<p lang="en" class="up">Contributors</p><p>사진과 글 — {e(spec["credit"].split(": ")[-1])}</p>'
              f'<p>편집과 레이아웃 — gentle_monster magazine (이 도구)</p><p style="margin-top:1em">독립 콘셉트 매거진. 젠틀몬스터가 발행 · 승인하지 않았습니다.</p>',
              bottom=12), "text", "contents", [], "Contents", rh="Contents")
    it = spec["intro"]
    page(at(4, 16, 8, "title up", '<p lang="en">Introduction</p>')
         + at(4, 66, 8, "lead", "".join(f'<p style="margin-bottom:.9em">{e(x)}</p>' for x in it["ko"]))
         + at(4, 104, 7, "body en", f'<p lang="en" style="color:var(--mute)">{e(it["en"])}</p>')
         + at(4, None, 7, "cap", f'<p>{e(spec["credit"])}</p>', bottom=12),
         "text", "intro", [], "Introduction", rh="Introduction")
    # 4-5 15 stops --------------------------------------------------------
    ks = sorted(k for k in spec["photos"] if k in assets)
    half = (len(ks) + 1) // 2
    st = story["stops"]
    th = round(SPAN(5) / (468 / 258), 3)
    for side, chunk in (("l", ks[:half]), ("r", ks[half:])):
        cols = (0, 6) if side == "l" else (1, 7)
        head = at(0, 13, 12, "title", f'<p lang="en">{e(st["en"])}</p>') if side == "l" else at(1, 13, 11, "title", f'<p>{e(st["ko"])}</p>')
        cells = "".join(at(cols[i % 2], 24 + (i // 2) * (th + 4.6), 5, "", f'<div style="height:{th}cqw">{img(k, pos="50% 50%")}</div>'
                           f'<p class="cap num" style="margin-top:.9cqw">{k}</p>') for i, k in enumerate(chunk))
        page(head + cells, "", "wall", chunk, "stops", rh=st["en"])
    # 6-7 day -> dusk (measured brightness order) ---------------------------
    seq = sorted(spec["sea_sequence"], key=lambda n: -meas[_k(n)].get("brightness", 0))
    d = story["day"]
    big = round(SPAN(12) / (468 / 258), 3)
    capt = lambda n: f'<p class="cap num" style="margin-top:.9cqw">{_k(n)} · {e(meas[_k(n)]["light"])} · 밝기 {meas[_k(n)]["brightness"]:.2f}</p>'
    page(at(0, 13, 12, "title", f'<p lang="en">{e(d["en"])}</p>')
         + "".join(at(0, 24 + i * (big + 6.5), 12, "", f'<div style="height:{big}cqw">{img(n)}</div>{capt(n)}') for i, n in enumerate(seq[:2])),
         "", "sequence", seq[:2], "day", rh=d["en"])
    mid = round(SPAN(8) / (468 / 258), 3)
    page(at(4, 13, 8, "title", f'<p>{e(d["ko"])}</p>')
         + "".join(at(4, 24 + i * (mid + 5.8), 8, "", f'<div style="height:{mid}cqw">{img(n)}</div>{capt(n)}') for i, n in enumerate(seq[2:])),
         "", "sequence", seq[2:], "day", rh=d["en"])
    # 8-9 one to one --------------------------------------------------------
    ws = spec["words"]
    wh = round(SPAN(10) / (468 / 258), 3)
    for i, w in enumerate(ws):
        ghost = ws[i + 1]["word"] if i + 1 < len(ws) else ""
        page(at(1, 20, 10, "", f'<div style="height:{wh}cqw">{img(w["photo"])}</div>')
             + (at(0, 76, 12, "ghost", f'<p style="font-size:{TYPE["word"]}cqw;text-align:center;line-height:1">{e(ghost)}</p>') if ghost else "")
             + at(0, 76, 12, "", f'<p style="font-size:{TYPE["word"]}cqw;text-align:center;line-height:1;letter-spacing:-.02em">{e(w["word"])}</p>'),
             "", "word", [w["photo"]], "turn")
    # 10-11 night spread ------------------------------------------------------
    ns = spec["night_spread"]
    page(f'<div class="a split l" data-bleed>{img(ns)}</div>', "night", "spread", [ns], "night")
    page(f'<div class="a split r" data-bleed>{img(ns)}</div>'
         + at(1, None, 6, "cap", f'<p class="num" style="color:#cfcdc6">{_k(ns)} — {e(spec["photos"][_k(ns)])}</p>', bottom=8),
         "night", "spread", [ns], "night")
    # 12-13 manifesto | photo -------------------------------------------------
    mf = spec["manifesto"]
    page(f'<div class="a mani" lang="en" data-col="1" style="left:{X(1)}cqw;bottom:14cqw;height:100cqw">'
         + "".join(f"<div>{e(l)}<sup>{i}</sup></div>" for i, l in enumerate(mf["lines"], 1)) + "</div>"
         + at(8, 16, 4, "cap", f'<p>{e(spec["credit"])}</p>'), "text", "manifesto", [], "manifesto", rh=story["manifesto"]["en"])
    page(f'<div class="a" style="inset:0" data-bleed>{img(mf["photo"])}</div>', "", "photo", [mf["photo"]], "manifesto")
    # 14-15 collage | index ---------------------------------------------------
    cells = "".join(f'<div style="overflow:hidden">{img(n)}</div>' for n in spec["collage"])
    page(f'<div class="a" data-bleed style="inset:0;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:.4cqw;'
         f'background:var(--paper)">{cells}</div>', "", "collage", spec["collage"], "index")
    ix = story["index"]
    rows = "".join(
        f'<div class="row body"><span class="num">{k}</span><span>'
        + "".join(f'<i class="sw" style="background:{hx}"></i>' for hx, _ in meas[k].get("palette", [])[:5])
        + f'</span><span>{e(spec["photos"][k])}</span><span>{e(meas[k]["light"])}</span><span class="num">{meas[k]["brightness"]:.2f}</span>'
          f'<span class="num">{meas[k]["saturation"]:.2f}</span></div>' for k in ks)
    page(at(0, 13, 12, "title", f'<p lang="en">{e(ix["en"])}</p>')
         + at(0, 22, 12, "", '<div class="row h cap up"><span>No.</span><span>색 (잰 값)</span><span>보이는 것</span><span>빛</span>'
              f'<span>밝기</span><span>채도</span></div>{rows}')
         + at(0, None, 12, "cap", f'<p>{e(spec["photos_note"])} 색 · 빛 · 밝기 · 채도는 사진에서 잰 값이다(밝기 · 채도 0–1).</p>', bottom=9),
         "text", "index", [], "index", rh=ix["en"])
    # 16 why pictures (the user's words) ---------------------------------------
    wy = story["why"]
    blocks = ""
    for i, b in enumerate(spec["qa_text"]):
        top = 16 + i * 36
        paras, cur = [], []
        for a_ in b["a"]:                                 # '첫째, …' opens a new paragraph; its sentence follows
            if a_.startswith(("첫째", "둘째")) and cur:
                paras.append(cur); cur = []
            cur.append(a_)
        paras.append(cur)
        body = "".join(f'<p style="margin-bottom:1em">' + " ".join(
            (f'<span style="color:var(--ink)">{e(x)}</span>' if x.startswith(("첫째", "둘째")) else e(x)) for x in p_) + "</p>" for p_ in paras)
        blocks += (at(0, top, 1, "cap num", f'<p>{i + 1}</p>') + at(1, top - 0.6, 4, "lead", f'<p>{e(b["q"])}</p>')
                   + at(6, top, 6, "body", body))
    page(blocks + at(6, None, 6, "cap", f'<p>{e(spec["credit"])}</p>', bottom=9), "text", "qa", [], "why", rh=wy["en"])
    # 17 lens ------------------------------------------------------------------
    L = spec["lens"]
    cw = round(SPAN(3) / (468 / 258), 3)
    cands = "".join(at(i * 3, 26, 3, "", f'<div style="height:{cw}cqw">{img(n, pos="50% 50%")}</div>'
                       f'<p class="cap num" style="margin-top:.9cqw{";color:var(--accent)" if n == L["chosen"] else ""}">{_k(n)}'
                       f'{" — 표지" if n == L["chosen"] else ""}</p>') for i, n in enumerate(L["candidates"]))
    paras = "".join(f'<p style="margin-bottom:1.1em">{e(r["text"])}{cite(r["claims"])}</p>' for r in L["reading"])
    others = "".join(f'<p style="margin-bottom:1em"><span class="num" style="color:var(--ink)">{k}</span>  {e(t)}</p>' for k, t in L["others"].items())
    page(at(0, 13, 12, "title", f'<p>{e(L["title"])}</p>') + cands
         + at(0, 26 + cw + 7, 7, "body", paras)
         + at(8, 26 + cw + 7, 4, "cap", f'<p class="up" lang="en" style="margin-bottom:1em">Other candidates</p>{others}<p>{e(L["note"])}</p>')
         + at(0, None, 12, "cap", '<ol class="refs">REFS</ol>', bottom=9), "text", "lens", L["candidates"], "lens", rh="The Gentle Monster Lens")
    # 18 back ------------------------------------------------------------------
    b = spec["back"]
    page(f'<div class="a" style="inset:0" data-bleed>{img(b["photo"])}</div>'
         + at(1, 12, 10, "box", f'<div style="padding:3.4cqw 3.6cqw"><p class="lead" style="margin-bottom:1.2em">{e(b["ko"])}</p>'
              f'<p class="body en" lang="en" style="margin-bottom:1.6em">{e(b["en"])}</p>'
              f'<p class="body" lang="en" style="font-weight:700">“{e(c["question"])}”</p></div>')
         + at(1, None, 10, "cap", f'<p style="color:#f1efe9">{e(spec["masthead"])} 00 · {e(spec["credit"])}</p>'
              f'<p style="color:#f1efe9">독립 콘셉트 매거진 — 젠틀몬스터가 발행 · 승인하지 않았습니다</p>', bottom=8),
         "text", "back", [b["photo"]], "back")

    # contents, filled from where each story section really starts
    first = {}
    for p in pages:
        first.setdefault(p["label"], p["n"])
    toc_rows = [("Introduction", "여는 글", first.get("Introduction"))] + [
        (s_["en"], s_["ko"], first.get(s_["id"])) for s_ in spec["story"]] + [("Back Cover", "뒤표지 — 멈춘 뒤 남는 자리", first.get("back"))]
    toc = "".join(f'<div style="display:grid;grid-template-columns:max({COL}cqw,2.4em) minmax(0,{SPAN(8)}cqw);column-gap:{GUTTER}cqw;margin-bottom:2.7cqw">'
                  f'<span class="body num">{n:02d}</span><a href="#p{n:02d}" style="color:inherit;text-decoration:none">'
                  f'<span class="body up" lang="en" style="display:block">{e(t)}</span><span class="cap" style="display:block">{e(k)}</span></a></div>'
                  for t, k, n in toc_rows if n)
    pages[1]["html"] = pages[1]["html"].replace("TOC", toc, 1)
    ref_html = "".join(f'<li id="lref-{n}" value="{n}"><span lang="en">{e(src[s_]["title"])}</span> — {e(src[s_]["url"])} '
                       f'(검색 결과의 조각만 확인)</li>' for s_, n in sorted(refs.items(), key=lambda kv: kv[1]))
    body = "".join(p["html"] for p in pages).replace('<ol class="refs">REFS</ol>', f'<ol class="refs">{ref_html}</ol>')
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(spec["title"])}</title><style>{css(accent)}</style></head><body><main>{body}</main><script>{R.QA_JS}</script></body></html>')
    hp = out / "index.html"
    hp.write_text(doc, encoding="utf-8")
    pres = PDF.render(hp, out / "magazine.pdf") if pdf else None
    checks = qa(spec, pages, hp, pres, meas, assets, bad_text, missing, pdf, first, accent)
    QA.save(checks, out, spec["title"])
    (out / "photos.json").write_text(json.dumps(meas, ensure_ascii=False, indent=1), encoding="utf-8")
    A.save(list(assets.values()), out / "assets.json")
    ranking = sorted((k for k in meas if not meas[k].get("missing")), key=lambda k: -meas[k]["strength"])
    return {"dir": str(out), "html": str(hp), "pdf": (pres or {}).get("path"), "pdf_result": pres, "pages": len(pages),
            "verdict": QA.verdict(checks), "checks": checks, "measured_cover_rank": ranking[:5], "measures": meas, "accent": acc}


KO_SPACING = re.compile(r"[A-Za-z0-9’”')\]] (은|는|이|가|을|를|의|에|에서|에는|도|로|으로|와|과)(?=[\s.,·])")


def qa(spec, pages, html_path, pres, meas, assets, bad_text, missing, want_pdf, first, accent) -> list:
    C = QA._c
    out = [C("content", "user texts are verbatim from docs/portfolio", "FAIL" if bad_text else "PASS", "; ".join(bad_text[:4]) or "cover · intro · manifesto · Q&A · back"),
           C("content", "every photo in the spec is on disk", "FAIL" if missing else "PASS", ", ".join(missing) or f"{len(assets)} photos"),
           C("content", "every photo is printed with the user's rights", "PASS" if all(A.publishable(a) for a in assets.values()) else "FAIL",
             f"rights '{spec['rights']}', credit '{spec['credit']}'")]
    used = {k for p in pages for k in p["photos"]}
    out.append(C("content", "every photo appears", "PASS" if used >= set(assets) else "FAIL", f"{len(used)} of {len(assets)}"))
    from gentle_monster.magazine import drift as D
    lens_txt = " ".join(r["text"] for r in spec["lens"]["reading"])
    try:
        D.guard_text(lens_txt)
        out.append(C("content", "the lens page states no fiction as brand fact", "PASS"))
    except D.ContradictionError as ex:
        out.append(C("content", "the lens page states no fiction as brand fact", "FAIL", str(ex)))
    out.append(C("content", "brand claims on the lens page read in full", "WARNING", "all cited claims are search snippets"))
    # ⑤ structure
    order = [p["label"] for p in pages]
    story_ok = all(first.get(s["id"]) for s in spec["story"]) and [first[s["id"]] for s in spec["story"]] == sorted(first[s["id"]] for s in spec["story"])
    out.append(C("structure", "story sections appear in the spec's order", "PASS" if story_ok else "FAIL", " → ".join(dict.fromkeys(order))))
    br = [meas[k]["brightness"] for p in pages if p["label"] == "day" for k in p["photos"]]
    out.append(C("structure", "Day → Dusk runs bright to dark (measured)", "PASS" if br == sorted(br, reverse=True) else "FAIL",
                 " > ".join(f"{x:.2f}" for x in br)))
    day_end, night_at = max((p["n"] for p in pages if p["label"] == "day"), default=0), first.get("night", 0)
    out.append(C("structure", "the night stop comes after the day", "PASS" if 0 < day_end < night_at else "FAIL", f"day ends p{day_end}, night p{night_at}"))
    html_text = Path(html_path).read_text(encoding="utf-8")
    toc_bad = [n for n in re.findall(r'href="#p(\d\d)"', html_text.split("</section>", 2)[1]) if f'id="p{n}"' not in html_text]
    out.append(C("structure", "contents page numbers point at real pages", "FAIL" if toc_bad else "PASS", ", ".join(toc_bad)))
    # ② typography (text-level)
    vis = re.sub(r"<[^>]+>", " ", html_text.split("<main>", 1)[-1].split("<script>", 1)[0])
    sp = sorted(set(m.group(0) for m in KO_SPACING.finditer(html.unescape(vis))))
    out.append(C("typography", "no space between a Latin word and its Korean particle", "FAIL" if sp else "PASS", ", ".join(sp[:6])))
    out.append(C("typography", "curly quotes, no straight quotes in Korean text", "FAIL" if re.search(r"[가-힣][^<]{0,40}'[^<]{0,40}'", html.unescape(vis)) else "PASS"))
    out.append(C("production", "independence line", "PASS" if "독립 콘셉트 매거진" in html_text else "FAIL"))
    # ④ colour
    from gentle_monster.magazine import design as DS
    cr = {"ink/paper": DS.contrast(INK, PAPER), "grey/paper": DS.contrast(MUTE, PAPER), "night-ink/night": DS.contrast(NIGHT_INK, NIGHT),
          "accent/paper": DS.contrast(accent, PAPER)}
    acc_uses = html_text.count("var(--accent)") - 0
    out.append(C("colour", "text contrast", "PASS" if cr["ink/paper"] >= 7 and cr["grey/paper"] >= 4.5 and cr["night-ink/night"] >= 7 else "FAIL",
                 ", ".join(f"{k} {v}" for k, v in cr.items())))
    out.append(C("colour", "one accent, measured from the cover photo, used sparingly",
                 "PASS" if acc_uses <= 3 else "WARNING", f"{accent} × {acc_uses}"))
    out.append(C("colour", "accent is legible as text (≥ 4.5:1 on paper)", "PASS" if cr["accent/paper"] >= 4.5 else "FAIL", f"{cr['accent/paper']}:1"))
    if not PDF.available():
        out.append(C("production", "browser measurements", "NOT_CHECKED", "Chromium not available"))
    else:
        pr = PDF.measure(html_path, 869, 1134, "qa-print")
        mob = PDF.measure(html_path, 375, 800, "qa")
        if not pr.get("ok"):
            out.append(C("production", "HTML renders in a browser", "FAIL", pr.get("error")))
        else:
            P = pr["pages"]
            out.append(C("production", "HTML renders in a browser", "PASS", f"{len(P)} pages"))
            over = [f"p{p['i']}" for p in P if p["overflow"] or p["self_scroll"]]
            clash = [f"p{p['i']}: {c_}" for p in P for c_ in p.get("clash", [])]
            out.append(C("layout", "no text block overlaps another (print size)", "FAIL" if clash else "PASS", "; ".join(clash[:4]) or "none"))
            out.append(C("layout", "text overflow at print size", "FAIL" if over else "PASS", ", ".join(over) or "none"))
            off = [f"p{p['i']}:c{c_['col']:g}{c_['x'] - X(c_['col']):+.2f}" for p in P for c_ in p.get("cols", []) if abs(c_["x"] - X(c_["col"])) > 0.3]
            n_cols = sum(len(p.get("cols", [])) for p in P)
            out.append(C("layout", "blocks sit on the 12-column grid (±0.3 cqw)", "FAIL" if off else "PASS", ", ".join(off[:6]) or f"{n_cols} blocks"))
            faux = [f"p{p['i']}:{f}" for p in P for f in p.get("faux", [])]
            out.append(C("typography", "no faux-bold Korean (the Korean face has one weight)", "FAIL" if faux else "PASS", ", ".join(faux[:4]) or "none"))
            mins = min(p.get("minfs", 99) for p in P)
            out.append(C("typography", "smallest text at print size ≥ 6.5 pt", "PASS" if mins * 0.75 >= 6.5 else "FAIL", f"{mins * 0.75:.1f} pt"))
            broken = [i["src"] for p in P for i in p["images"] if not i["ok"]]
            out.append(C("image", "images load", "FAIL" if broken else "PASS", ", ".join(broken[:4]) or f"{sum(len(p['images']) for p in P)} placements"))
            dpis, crops = [], []
            for p in P:
                for i in p["images"]:
                    if i.get("nw") and i.get("rw"):
                        s = max(i["rw"] / i["nw"], i["rh"] / i["nh"]) if i["fit"] == "cover" else i["rw"] / i["nw"]
                        dpis.append((round(96 / s), p["i"], round(i["nw"] * PRINT_DPI_MIN * s / 96)))
                        if i["fit"] == "cover":
                            crops.append((round(i["rw"] * i["rh"] / (i["nw"] * s * i["nh"] * s), 2), p["i"]))
            low = sorted(d for d in dpis if d[0] < PRINT_DPI_MIN)
            out.append(C("image", f"print resolution >= {PRINT_DPI_MIN} dpi", "FAIL" if low else "PASS",
                         (f"{len(low)} of {len(dpis)} placements below; lowest {low[0][0]} dpi (p{low[0][1]}). The photos are 468 px "
                          f"screenshot crops -- print needs originals of at least {max(d[2] for d in low)} px on the long edge. "
                          f"The web version is unaffected") if low else f"lowest {min(dpis)[0] if dpis else '—'} dpi"))
            # a spread split over two pages shows half of its image on each page -- count the pair, not the half
            heavy = sorted(c_ for c_ in crops if c_[0] < 0.4 and pages[c_[1] - 1]["kind"] != "spread")
            out.append(C("image", "no photo cropped to less than 40% of its frame (spreads excepted)", "WARNING" if heavy else "PASS",
                         ", ".join(f"p{p_} keeps {f:.0%}" for f, p_ in heavy[:5]) or f"smallest kept {min(crops)[0]:.0%}" if crops else "—"))
            han = [p for p in P if p["hangul"]]
            fonts = [f for f in QA.ko_fonts() if f.startswith("WenQuanYi")]
            out.append(C("typography", "Hangul has a font", "PASS" if fonts or not han else "FAIL", ", ".join(fonts[:1]) or "none"))
        if mob.get("ok"):
            if mob["viewport"][0] != 375:
                out.append(C("layout", "phone width 375 px", "NOT_CHECKED", f"viewport {mob['viewport'][0]}"))
            else:
                out.append(C("layout", "phone width 375 px: no sideways scroll", "PASS" if mob["doc_scroll_w"] <= 375 else "FAIL",
                             f"document {mob['doc_scroll_w']}px"))
                mclash = [f"p{p['i']}: {c_}" for p in mob["pages"] for c_ in p.get("clash", [])]
                out.append(C("layout", "no text block overlaps another (375 px)", "FAIL" if mclash else "PASS", "; ".join(mclash[:4]) or "none"))
    if want_pdf:
        ok = pres and pres.get("ok") and pres["pages"] == len(pages)
        out.append(C("production", "PDF output", "PASS" if ok else "FAIL",
                     f"{(pres or {}).get('pages')} PDF pages for {len(pages)}" if pres and pres.get("ok") else (pres or {}).get("error", "not built")))
    return out
