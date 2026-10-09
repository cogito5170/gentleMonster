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
        out[k] = m
    return out


def _k(n) -> str:
    return f"{int(n):02d}"


def css() -> str:
    paper, ink, mute = "#fbfbf9", "#111111", "#6d6d6a"
    ko = '"WenQuanYi Zen Hei","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic"'
    return f"""
:root{{--paper:{paper};--ink:{ink};--mute:{mute};--sans:"Liberation Sans","Helvetica Neue",Arial,{ko},sans-serif}}
*{{box-sizing:border-box}} html{{background:#2a2a28}}
body{{margin:0;color:var(--ink);font-family:var(--sans);word-break:keep-all;overflow-wrap:break-word;-webkit-font-smoothing:antialiased}}
main{{display:flex;flex-wrap:wrap;justify-content:center;gap:0;padding:24px 0}}
.page{{container-type:inline-size;position:relative;overflow:hidden;background:var(--paper);width:min(46vw,560px);aspect-ratio:{W_MM}/{H_MM};margin-bottom:28px}}
.page.dark{{background:#0c0c0c;color:#f2f2ee}}
.page.cover{{margin-right:46vw}} @media (max-width:1100px){{.page{{width:min(100vw - 32px,560px)}} .page.cover{{margin-right:0}}}}
.abs{{position:absolute}} img{{display:block;width:100%;height:100%;object-fit:cover}} img.ph{{height:auto;aspect-ratio:468/258}}
.s{{font-size:1.55cqw;line-height:1.35}} .xs{{font-size:1.2cqw;line-height:1.35;color:var(--mute)}}
.folio{{position:absolute;bottom:3cqw;font-size:1.2cqw;color:var(--mute)}} .folio.l{{left:6cqw}} .folio.r{{right:6cqw}}
.dark .folio,.dark .xs{{color:#9a9a96}}
figcaption{{font-size:1.15cqw;line-height:1.35;color:var(--mute);margin-top:.8cqw}}
/* cover */
.mast{{position:absolute;left:4cqw;right:4cqw;top:2.5cqw;font-weight:700;font-size:37cqw;line-height:.8;letter-spacing:-.06em;margin:0}}
.mast::after{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 9.6cqw,var(--paper) 9.6cqw 11.4cqw),
  repeating-linear-gradient(0deg,transparent 0 5.6cqw,var(--paper) 5.6cqw 7cqw);mix-blend-mode:normal}}
.cover-photo{{left:8cqw;right:8cqw;top:36cqw;height:52cqw}}
.cover-meta{{left:8cqw;top:96cqw;width:30cqw}} .cover-lines{{left:40cqw;top:96cqw;right:8cqw}}
.cover-q{{right:8cqw;bottom:6cqw;font-size:3.2cqw;font-weight:700;text-align:right}}
.cover-by{{left:8cqw;bottom:6cqw}}
/* contents + intro */
.toc{{left:8cqw;top:10cqw;right:30cqw;list-style:none;margin:0;padding:0}} .toc li{{display:grid;grid-template-columns:6cqw 1fr;gap:1cqw;margin-bottom:2.2cqw}}
.toc .t{{text-transform:uppercase}} .toc .t i{{text-transform:none;font-style:normal;color:var(--mute)}}
.intro-h{{right:8cqw;top:10cqw;text-transform:uppercase}} .intro{{left:46cqw;right:8cqw;bottom:14cqw}} .intro p{{margin:0 0 1.6cqw}}
.intro .en{{color:var(--mute)}}
/* gallery wall */
.wall{{left:8cqw;right:8cqw;top:16cqw;display:grid;grid-template-columns:repeat(2,1fr);gap:2.6cqw 3cqw}} .wall figure{{margin:0}} .wall .ph{{aspect-ratio:468/258}}
.wall-h{{left:6cqw;top:6cqw;font-size:5.4cqw;font-weight:700;letter-spacing:-.03em}}
/* word page */
.word-photo{{left:12cqw;right:12cqw;top:16cqw;height:40cqw}}
.word{{left:0;right:0;top:82cqw;text-align:center;font-size:12cqw;font-weight:700;letter-spacing:-.02em}}
.word-ghost{{left:0;right:0;top:82cqw;text-align:center;font-size:12cqw;font-weight:700;opacity:.08;transform:scaleX(-1)}}
/* collage + index */
.collage{{inset:0;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:0}}
.index{{left:8cqw;right:8cqw;top:9cqw}} .index table{{width:100%;border-collapse:collapse}}
.index td,.index th{{text-align:left;vertical-align:top;padding:.7cqw .8cqw .7cqw 0;border-bottom:.12cqw solid #d8d8d4;font-size:1.3cqw;line-height:1.35}}
.index th{{font-weight:700;text-transform:uppercase;font-size:1.1cqw}} .index td.n{{font-variant-numeric:tabular-nums;white-space:nowrap}}
/* manifesto */
.mani{{left:9cqw;bottom:12cqw;height:110cqw;writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;font-size:6.2cqw;line-height:1.15;font-weight:500;letter-spacing:-.02em}}
.mani div{{display:block}}
.mani sup{{font-size:2.6cqw;vertical-align:top;margin-left:.4cqw}}
.mani-src{{left:72cqw;right:8cqw;top:8cqw}}
.mani-photo{{inset:0}}
/* full-bleed spread across two pages */
.split{{top:0;height:100%;width:200%}} .split.l{{left:0}} .split.r{{left:-100%}}
.over{{left:8cqw;bottom:8cqw;right:40cqw;color:#f2f2ee}}
/* sequence */
.seq{{left:8cqw;right:8cqw;top:12cqw;display:grid;gap:2.4cqw}} .seq.narrow{{left:30cqw}} .seq .ph{{aspect-ratio:468/258}}
.seq-h{{left:8cqw;top:5cqw;text-transform:uppercase}}
/* Q&A + lens */
.qa{{left:8cqw;right:8cqw;top:10cqw}} .qa h3{{font-size:2.4cqw;margin:0 0 1.2cqw}} .qa p{{margin:0 0 1cqw}} .qa section{{margin-bottom:4.4cqw}}
.lens{{left:8cqw;right:8cqw;top:9cqw}} .lens h2{{font-size:4.4cqw;margin:0 0 2.6cqw;letter-spacing:-.02em}}
.lens .cands{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.6cqw;margin-bottom:2.4cqw}} .lens .cands .ph{{aspect-ratio:468/258}}
.lens .cands figure{{margin:0}} .lens .chosen .ph{{outline:.5cqw solid var(--ink);outline-offset:.4cqw}}
.lens p{{margin:0 0 1.3cqw}} sup a{{color:inherit;text-decoration:none;font-size:.8em}}
.refs{{margin-top:2cqw;padding-left:3cqw}} .refs li{{margin-bottom:.6cqw}} .refs a{{color:inherit;word-break:break-all}}
/* back cover */
.back-box{{left:9cqw;right:9cqw;top:42cqw;border:.25cqw solid rgba(255,255,255,.85);padding:4cqw;color:#fff;background:rgba(0,0,0,.18)}}
.back-box .ko{{font-size:2.6cqw;line-height:1.5;margin:0 0 2cqw;font-weight:700}} .back-box .en{{font-size:1.6cqw;margin:0 0 3cqw}}
.back-meta{{left:9cqw;bottom:8cqw;color:#fff}}
@media (max-width:600px){{
  .page.text{{aspect-ratio:auto;padding:28px 20px 48px}} .page.text .abs{{position:static;transform:none;width:auto}}
  .page.text .s,.page.text .index td,.page.text .index th{{font-size:14px}} .page.text .xs,.page.text figcaption{{font-size:12px}}
  .page.text .qa h3{{font-size:17px}} .page.text .lens h2{{font-size:22px}} .page.text .folio{{font-size:12px}}
  .page.text .mani{{font-size:24px;writing-mode:horizontal-tb;transform:none;height:auto;white-space:normal}} .page.text .back-box .ko{{font-size:16px}} .page.text .back-box .en{{font-size:13px}}
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

    assets = {}
    for k, m in meas.items():
        if m.get("missing"):
            continue
        dst = out / "img" / Path(m["path"]).name
        if not dst.exists() or dst.stat().st_mtime < Path(m["path"]).stat().st_mtime:
            dst.write_bytes(Path(m["path"]).read_bytes())
        a = A.user_image(str(dst), spec["credit"], spec["rights"], title=f"{k} — {spec['photos'][k]}")
        assets[k] = a

    def img(n, cls="ph", extra=""):
        k = _k(n)
        a = assets.get(k)
        if not a:
            return f'<div class="{cls} withheld">사진 {k} 없음</div>'
        return f'<img class="{cls}" src="img/{e(Path(a["local_path"]).name)}" alt="{e(spec["photos"][k])}" data-photo="{k}" {extra}>'

    pages, refs = [], {}

    def cite(ids):
        out_ = []
        for i in ids:
            for s in claims.get(i, {}).get("source_ids", [])[:1]:
                n = refs.setdefault(s, len(refs) + 1)
                out_.append(f'<a href="#lref-{n}">{n}</a>')
        return f"<sup>{','.join(out_)}</sup>" if out_ else ""

    def page(inner, cls="", kind="photo", photos=(), label=""):
        n = len(pages) + 1
        fol = "" if "cover" in cls else f'<div class="folio {"l" if n % 2 == 0 else "r"}">{n:02d}</div>'
        pages.append({"n": n, "kind": kind, "label": label, "photos": [_k(p) for p in photos],
                      "html": f'<section class="page {cls}" id="p{n:02d}" data-type="{kind}">{inner}{fol}</section>'})

    c = spec["cover"]
    cov = c["photo"]
    # 1 cover
    page(f'<h1 class="mast" lang="en">{e(spec["masthead"])}</h1><figure class="abs cover-photo" style="margin:0">{img(cov, "")}</figure>'
         f'<div class="abs cover-meta s" lang="en">{e(spec["masthead"])}<br>MAGAZINE<br><br>ISSUE 00<br><br>' + "<br>".join(e(x) for x in c["left"]) + "</div>"
         f'<div class="abs cover-lines s" lang="en">' + "<br>".join(e(x) for x in c["right"]) + "</div>"
         f'<div class="abs cover-by s" lang="en">' + "<br>".join(e(x) for x in c["byline"]) + "</div>"
         f'<div class="abs cover-q" lang="en">“{e(c["question"])}”</div>', "cover", "cover", [cov], "표지")
    toc_items = [("여는 글", "Introduction", "여는 글"), ("15 Stops", "15 Stops", "열다섯 번 멈춘 자리"),
                 (spec["words"][0]["word"], "One to One", "단어 한 장"), ("Index", "Index", "보이는 것과 잰 것"),
                 ("Manifesto", "Manifesto", "선언"), ("Night", "Night", "밤"), ("Water", "Water", "물 — 밝은 데서 어두운 데로"),
                 ("Why Pictures", "Why Pictures", "사진에 관한 세 물음"), ("Lens", "The Gentle Monster Lens", "젠틀몬스터의 눈으로 고른 표지"),
                 ("뒤표지", "Back Cover", "뒤표지")]
    # 2 contents | 3 intro  (page numbers are filled in once every page exists)
    page('<ol class="abs toc s">TOC</ol>', "text", "contents", [], "차례")
    it = spec["intro"]
    page(f'<div class="abs intro-h s" lang="en">Introduction</div><div class="abs intro s">' + "".join(f"<p>{e(x)}</p>" for x in it["ko"])
         + f'<p class="en" lang="en">{e(it["en"])}</p><p class="xs">{e(spec["credit"])}</p></div>', "text", "intro", [], "여는 글")
    # 4-5 gallery wall: all photos
    ks = sorted(k for k in spec["photos"] if k in assets)
    half = (len(ks) + 1) // 2
    for side, chunk in (("l", ks[:half]), ("r", ks[half:])):
        head = '<div class="abs wall-h" lang="en">15 Stops</div>' if side == "l" else '<div class="abs wall-h xs">열다섯 번 멈춘 자리</div>'
        page(head + f'<div class="abs wall {side}">' + "".join(f'<figure>{img(k)}<figcaption>{k}</figcaption></figure>' for k in chunk) + "</div>",
             "", "wall", chunk, "15 Stops")
    # 6-7 one to one
    ws = spec["words"]
    for i, w in enumerate(ws):
        ghost = ws[i + 1]["word"] if i + 1 < len(ws) else ""
        page(f'<figure class="abs word-photo" style="margin:0">{img(w["photo"], "")}</figure>'
             + (f'<div class="abs word-ghost" aria-hidden="true">{e(ghost)}</div>' if ghost else "")
             + f'<div class="abs word">{e(w["word"])}</div>', "", "word", [w["photo"]], w["word"])
    # 8 collage | 9 index
    page('<div class="abs collage">' + "".join(img(n, "") for n in spec["collage"]) + "</div>", "", "collage", spec["collage"], "Collage")
    rows = "".join(f'<tr><td class="n">{k}</td><td>{e(spec["photos"][k])}</td><td>{e(meas[k].get("light", "—"))}</td>'
                   f'<td class="n">{meas[k].get("brightness", 0):.2f}</td><td class="n">{meas[k].get("saturation", 0):.2f}</td></tr>'
                   for k in ks)
    page(f'<div class="abs index"><p class="s" lang="en" style="margin:0 0 2cqw;text-transform:uppercase">Index</p>'
         f'<table><tr><th>No.</th><th>보이는 것</th><th>빛 (잰 값)</th><th>밝기</th><th>채도</th></tr>{rows}</table>'
         f'<p class="xs" style="margin-top:2cqw">{e(spec["photos_note"])} 빛 · 밝기 · 채도는 사진에서 잰 값이다(0–1). {e(spec["credit"])}.</p></div>',
         "text", "index", [], "Index")
    # 10 manifesto | 11 photo
    mf = spec["manifesto"]
    page(f'<div class="abs mani" lang="en">' + "".join(f"<div>{e(l)}<sup>{i}</sup></div>" for i, l in enumerate(mf["lines"], 1)) + "</div>"
         f'<div class="abs mani-src xs">{e(spec["credit"])}</div>', "text", "manifesto", [], "Manifesto")
    page(f'<div class="abs mani-photo">{img(mf["photo"], "")}</div>', "", "photo", [mf["photo"]], "Manifesto photo")
    # 12-13 night spread
    ns = spec["night_spread"]
    page(f'<div class="abs split l" data-bleed>{img(ns, "", "")}</div>', "dark", "spread", [ns], "Night")
    page(f'<div class="abs split r" data-bleed>{img(ns, "", "")}</div><div class="abs over xs">{_k(ns)} — {e(spec["photos"][_k(ns)])}</div>',
         "dark", "spread", [ns], "Night")
    # 14 water sequence (bright -> dark, measured)
    seq = sorted(spec["sea_sequence"], key=lambda n: -meas[_k(n)].get("brightness", 0))
    page(f'<div class="abs seq-h s" lang="en">Water</div><div class="abs seq">' + "".join(
        f'<figure style="margin:0">{img(n)}<figcaption>{_k(n)} · {e(meas[_k(n)].get("light"))} · 밝기 {meas[_k(n)].get("brightness", 0):.2f}</figcaption></figure>'
        for n in seq[:2]) + "</div>", "", "sequence", seq[:2], "Water")
    page(f'<div class="abs seq narrow" style="top:8cqw">' + "".join(
        f'<figure style="margin:0">{img(n)}<figcaption>{_k(n)} · {e(meas[_k(n)].get("light"))} · 밝기 {meas[_k(n)].get("brightness", 0):.2f}</figcaption></figure>'
        for n in seq[2:]) + '</div><div class="abs xs" style="left:8cqw;width:18cqw;bottom:9cqw">물 — 잰 밝기 순서대로, 밝은 데서 어두운 데로.</div>',
         "", "sequence", seq[2:], "Water")
    # 16 Q&A (user's text)
    qa_html = "".join(f'<section><h3>{e(b["q"])}</h3>' + "".join(
        f'<p class="s">{"<b>" + e(a) + "</b>" if a.startswith(("첫째", "둘째")) else e(a)}</p>' for a in b["a"]) + "</section>" for b in spec["qa_text"])
    page(f'<div class="abs qa">{qa_html}<p class="xs">{e(spec["credit"])}</p></div>', "text", "qa", [], "Why Pictures")
    # 17 lens (editor's reading, cited)
    L = spec["lens"]
    cands = "".join(f'<figure class="{"chosen" if n == L["chosen"] else ""}">{img(n)}<figcaption>{_k(n)}'
                    f'{" — 표지" if n == L["chosen"] else ""}</figcaption></figure>' for n in L["candidates"])
    paras = "".join(f'<p class="s">{e(r["text"])}{cite(r["claims"])}</p>' for r in L["reading"])
    others = "".join(f'<p class="xs"><b>{k}</b> {e(t)}</p>' for k, t in L["others"].items())
    lens_html = (f'<div class="abs lens"><h2>{e(L["title"])}</h2><div class="cands">{cands}</div>{paras}{others}'
                 f'<p class="xs">{e(L["note"])}</p><ol class="refs xs">REFS</ol></div>')
    page(lens_html, "text", "lens", L["candidates"], "Lens")
    # 18 back cover
    b = spec["back"]
    page(f'<div class="abs" style="inset:0">{img(b["photo"], "")}</div><div class="abs back-box"><p class="ko">{e(b["ko"])}</p>'
         f'<p class="en" lang="en">{e(b["en"])}</p><p class="en" lang="en" style="margin:0;font-weight:700">“{e(c["question"])}”</p></div>'
         f'<div class="abs back-meta xs" style="color:#eee">{e(spec["masthead"])} 00 · {e(spec["credit"])} · 독립 콘셉트 매거진 — 젠틀몬스터가 발행 · 승인하지 않았습니다</div>',
         "dark text", "back", [b["photo"]], "뒤표지")

    ref_html = "".join(f'<li id="lref-{n}" value="{n}" lang="en">{e(src[s]["title"])} — <a href="{e(src[s]["url"])}">{e(src[s]["url"])}</a> '
                       f'(검색 조각만 봄)</li>' for s, n in sorted(refs.items(), key=lambda kv: kv[1]))
    first = {}
    for p in pages:
        first.setdefault(p["label"], p["n"])
    toc = "".join(f'<li><span>{first[l]:02d}</span><span class="t" lang="en"><a href="#p{first[l]:02d}" style="color:inherit;text-decoration:none">'
                  f'{e(t)}</a><br><i lang="ko">{e(k)}</i></span></li>' for l, t, k in toc_items if l in first)
    pages[1]["html"] = pages[1]["html"].replace("TOC", toc, 1)
    body = "".join(p["html"] for p in pages).replace('<ol class="refs xs">REFS</ol>', f'<ol class="refs xs">{ref_html}</ol>')
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(spec["title"])}</title><style>{css()}</style></head><body><main>{body}</main><script>{R.QA_JS}</script></body></html>')
    hp = out / "index.html"
    hp.write_text(doc, encoding="utf-8")
    pres = PDF.render(hp, out / "magazine.pdf") if pdf else None
    checks = qa(spec, pages, hp, pres, meas, assets, bad_text, missing, pdf)
    QA.save(checks, out, spec["title"])
    (out / "photos.json").write_text(json.dumps(meas, ensure_ascii=False, indent=1), encoding="utf-8")
    A.save(list(assets.values()), out / "assets.json")
    ranking = sorted((k for k in meas if not meas[k].get("missing")), key=lambda k: -meas[k]["strength"])
    return {"dir": str(out), "html": str(hp), "pdf": (pres or {}).get("path"), "pdf_result": pres, "pages": len(pages),
            "verdict": QA.verdict(checks), "checks": checks, "measured_cover_rank": ranking[:5], "measures": meas}


def qa(spec, pages, html_path, pres, meas, assets, bad_text, missing, want_pdf) -> list:
    C = QA._c
    out = [C("content", "user texts are verbatim from docs/portfolio", "FAIL" if bad_text else "PASS", "; ".join(bad_text[:4]) or "cover · intro · manifesto · Q&A · back"),
           C("content", "every photo in the spec is on disk", "FAIL" if missing else "PASS", ", ".join(missing) or f"{len(assets)} photos"),
           C("content", "every photo is printed with the user's rights", "PASS" if all(A.publishable(a) for a in assets.values()) else "FAIL",
             f"rights '{spec['rights']}', credit '{spec['credit']}'")]
    used = {k for p in pages for k in p["photos"]}
    out.append(C("content", "every photo appears", "PASS" if used >= set(assets) else "FAIL", f"{len(used)} of {len(assets)}"))
    lens_txt = " ".join(r["text"] for r in spec["lens"]["reading"])
    try:
        from gentle_monster.magazine import drift as D
        D.guard_text(lens_txt)
        out.append(C("content", "the lens page states no fiction as brand fact", "PASS"))
    except Exception as ex:                                                    # noqa: BLE001
        out.append(C("content", "the lens page states no fiction as brand fact", "FAIL", str(ex)))
    out.append(C("content", "brand claims on the lens page read in full", "WARNING", "all cited claims are search snippets"))
    html_text = Path(html_path).read_text(encoding="utf-8")
    out.append(C("production", "independence line on the back cover", "PASS" if "독립 콘셉트 매거진" in html_text else "FAIL"))
    if not PDF.available():
        out.append(C("production", "browser measurements", "NOT_CHECKED", "Chromium not available"))
    else:
        pr = PDF.measure(html_path, 869, 1134, "qa-print")
        mob = PDF.measure(html_path, 375, 800, "qa")
        if not pr.get("ok"):
            out.append(C("production", "HTML renders in a browser", "FAIL", pr.get("error")))
        else:
            out.append(C("production", "HTML renders in a browser", "PASS", f"{len(pr['pages'])} pages"))
            over = [f"p{p['i']}" for p in pr["pages"] if p["overflow"] or p["self_scroll"]]
            out.append(C("production", "text overflow at print size", "FAIL" if over else "PASS", ", ".join(over) or "none"))
            broken = [i["src"] for p in pr["pages"] for i in p["images"] if not i["ok"]]
            out.append(C("production", "images load", "FAIL" if broken else "PASS", ", ".join(broken[:4]) or f"{sum(len(p['images']) for p in pr['pages'])} placements"))
            dpis = []
            for p in pr["pages"]:
                for i in p["images"]:
                    if i.get("nw") and i.get("rw"):
                        s = max(i["rw"] / i["nw"], i["rh"] / i["nh"]) if i["fit"] == "cover" else i["rw"] / i["nw"]
                        dpis.append((round(96 / s), p["i"], round(i["nw"] * PRINT_DPI_MIN * s / 96)))
            low = sorted(d for d in dpis if d[0] < PRINT_DPI_MIN)
            out.append(C("production", f"print resolution >= {PRINT_DPI_MIN} dpi", "FAIL" if low else "PASS",
                         (f"{len(low)} of {len(dpis)} placements below; lowest {low[0][0]} dpi (p{low[0][1]}). The photos are 468 px "
                          f"screenshot crops -- print needs originals of at least {max(d[2] for d in low)} px on the long edge. "
                          f"The web version is unaffected") if low else
                         f"lowest {min(dpis)[0] if dpis else '—'} dpi"))
            han = [p for p in pr["pages"] if p["hangul"]]
            fonts = [f for f in QA.ko_fonts() if f.startswith("WenQuanYi")]
            out.append(C("production", "Hangul has a font", "PASS" if fonts or not han else "FAIL", ", ".join(fonts[:1]) or "none"))
        if mob.get("ok"):
            if mob["viewport"][0] != 375:
                out.append(C("production", "phone width 375 px", "NOT_CHECKED", f"viewport {mob['viewport'][0]}"))
            else:
                out.append(C("production", "phone width 375 px: no sideways scroll", "PASS" if mob["doc_scroll_w"] <= 375 else "FAIL",
                             f"document {mob['doc_scroll_w']}px"))
    if want_pdf:
        ok = pres and pres.get("ok") and pres["pages"] == len(pages)
        out.append(C("production", "PDF output", "PASS" if ok else "FAIL",
                     f"{(pres or {}).get('pages')} PDF pages for {len(pages)}" if pres and pres.get("ok") else (pres or {}).get("error", "not built")))
    return out
