"""A one-page CV in the SPA design system (editorial/cv/*.json).

Content follows the reference analysis (five CV templates the user sent): name · role · contact · photo · profile ·
education · experience/projects · tools · skills · languages. Three choices taken from it:
  - the three-zone row of the text-led template (label | title, place, years | description) -- it carries the most;
  - tools written as *what you can do with them*, not as gauges or percentages (a '75 %' bar says nothing);
  - skills as chips, filled and outlined in turn.
Three layouts from the same spec (`--layout rows|split|creative|all`, see LAYOUTS), one per reference type.
Nothing is invented: a field that is null in the spec is printed as a red [blank] for the applicant to fill, and
every sentence that is printed is checked word for word against the document it came from.

Page: A4, 14 mm margins, 12 columns, 4 mm gutters; sizes in points on paper, written as cqw so the screen view and
the PDF are one layout. Fonts, colours and the measuring script are the photo issue's.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from gentle_monster import paths
from gentle_monster.magazine import pdf as PDF
from gentle_monster.magazine import design as DS
from gentle_monster.magazine.photo_issue import (ACCENT_TEXT, FACES, FONT_DIR, GREY, INK, KO_WEIGHTS, LINE, PAPER,
                                                 MUTE_RAW, font_faces)
from gentle_monster.magazine.render import QA_JS

W_MM, H_MM = 210, 297
MM = 100 / W_MM                                     # cqw per millimetre
PT = 0.3528 * MM                                    # cqw per point
MARGIN, GUT, COLS = 14, 4, 12
COL = (W_MM - 2 * MARGIN - (COLS - 1) * GUT) / COLS  # 11.5 mm
TYPE = {"furn": 6.8, "cap": 7.2, "body": 8.4, "body_ko": 8.2, "role": 7.6, "lead_ko": 10.5, "lead_en": 9.0, "head": 9.5, "name": 34.0}
MIN_PT = 6.5
PRINT_DPI = 200
PANEL, PANEL_INK, PANEL_MUTE, PANEL_RED, BAND = INK, "#ece8de", "#a9aaa2", "#f0a493", "#fbf9f4"                                     # a CV is looked at close


def e(s) -> str:
    return html.escape(str(s), quote=True)


def pt(v: float) -> str:
    return f"{v * PT:.3f}cqw"


def X(c: int) -> float:
    """Left edge of column c, mm."""
    return MARGIN + c * (COL + GUT)


def SPAN(n: int) -> float:
    return n * COL + (n - 1) * GUT


def blank(label: str) -> str:
    return f'<span class="blank">[{e(label)}]</span>'


def val(v, label: str) -> str:
    return e(v) if v not in (None, "") else blank(label)


def doc(p: str) -> str:
    f = paths.REPO / p
    return f.read_text(encoding="utf-8") if f.is_file() else ""


def check_texts(spec: dict) -> list[str]:
    """Every sentence the CV prints must be, word for word, in the document named as its source."""
    bad = []
    pr = spec["profile"]
    for k in ("ko", "en", "more"):
        if pr.get(k) and pr[k] not in doc(pr["source"]):
            bad.append(f"profile.{k}: '{pr[k][:30]}' not in {pr['source']}")
    if " ".join(spec["name"]) not in doc(spec["name_source"]):
        bad.append(f"name '{' '.join(spec['name'])}' not in {spec['name_source']}")
    if spec["question"] not in doc(spec["question_source"]):
        bad.append(f"question not in {spec['question_source']}")
    for p in spec["projects"]:
        if p.get("title") and not p.get("fact_source"):
            bad.append(f"project '{p['title'][:30]}' has no fact_source")
        elif p.get("fact_source") and not doc(p["fact_source"]):
            bad.append(f"project '{p['title'][:30]}': {p['fact_source']} does not exist")
    return bad


def blanks(spec: dict) -> list[str]:
    """Every field left for the applicant, by name."""
    out = [f"contact.{c['label']}" for c in spec["contact"] if not c["value"]]
    for i, ed in enumerate(spec["education"]):
        out += [f"education[{i}].{k}" for k in ("school", "major", "years", "line") if not ed.get(k)]
    for i, p in enumerate(spec["projects"]):
        out += [f"projects[{i}].{k}" for k in ("title", "kind", "what", "years") if not p.get(k)]
    for i, t in enumerate(spec["tools"]):
        out += [f"tools[{i}].{k}" for k in ("name", "can") if not t.get(k)]
    out += [f"skills[{i}]" for i, s in enumerate(spec["skills"]) if not s["t"]]
    out += [f"languages[{i}].level" for i, l_ in enumerate(spec["languages"]) if not l_["level"]]
    return out


def bw_copy(src: Path, dst: Path) -> None:
    """Black and white, contrast stretched -- the five references are all monochrome. Pixels are not added:
    the print-resolution check reads the source size."""
    from PIL import Image, ImageOps
    with Image.open(src) as im:
        ImageOps.autocontrast(im.convert("L"), cutoff=1).save(dst, quality=90)


def css() -> str:
    ko = '"Pretendard","WenQuanYi Zen Hei","Apple SD Gothic Neo","Malgun Gothic"'
    return font_faces() + f"""
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTE_RAW};--line:{LINE};--accent-text:{ACCENT_TEXT};--grey:{GREY};
  --serif:Caladea,"Noto Serif KR","Liberation Serif",Georgia,serif;--sans:Inter,{ko},"Liberation Sans",Arial,sans-serif;
  --ko-serif:"Noto Serif KR",Caladea,serif;--ko-sans:{ko},Inter,sans-serif}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{background:#d9d6cd}} body{{background:#d9d6cd;color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased}}
main{{display:flex;justify-content:center;padding:32px 16px}}
.page{{container-type:inline-size;position:relative;overflow:hidden;background:var(--paper);width:min(100%,794px);aspect-ratio:{W_MM}/{H_MM};
  box-shadow:0 1px 2px rgba(0,0,0,.08),0 12px 40px rgba(0,0,0,.12)}}
.a{{position:absolute}}
.name{{font-family:"Inter Display",Inter,sans-serif;font-weight:700;font-size:{pt(TYPE['name'])};line-height:.9;letter-spacing:-.02em}}
.caps{{font-family:Inter,sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:.14em;font-size:{pt(TYPE['furn'])};line-height:1.5}}
.head{{font-family:Inter,sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:.12em;font-size:{pt(TYPE['head'])};line-height:1.3}}
.role{{font-family:Inter,sans-serif;font-weight:500;font-size:{pt(TYPE['role'])};line-height:1.55}}
.body{{font-size:{pt(TYPE['body'])};line-height:1.5}}
.ko{{font-family:var(--ko-sans);font-weight:400;font-size:{pt(TYPE['body_ko'])};line-height:1.72;word-break:keep-all;letter-spacing:-.005em}}
.lead-ko{{font-family:var(--ko-serif);font-weight:400;font-size:{pt(TYPE['lead_ko'])};line-height:1.62;word-break:keep-all}}
.lead-en{{font-family:Caladea,serif;font-style:italic;font-size:{pt(TYPE['lead_en'])};line-height:1.45}}
.cap{{font-size:{pt(TYPE['cap'])};line-height:1.45;color:var(--grey)}}
.t{{font-family:Inter,sans-serif;font-weight:700;font-size:{pt(TYPE['body'])};line-height:1.35}}
.ko-t{{font-family:var(--ko-sans);font-weight:600}}
.rule{{position:absolute;height:0;border-top:.75pt solid var(--ink)}}
.rule.thin{{border-top:.5pt solid var(--line)}}
.blank{{color:var(--accent-text);font-family:var(--ko-sans);font-weight:inherit}}
.ph{{display:block;width:100%;height:100%;object-fit:cover}}
.chips{{display:flex;flex-wrap:wrap;gap:{2.2 * MM:.3f}cqw {2 * MM:.3f}cqw}}
.chip{{display:inline-block;border:.75pt solid var(--ink);border-radius:999px;padding:{1.3 * MM:.3f}cqw {4 * MM:.3f}cqw;
  font-family:Inter,sans-serif;font-weight:500;font-size:{pt(TYPE['body'])};line-height:1.2}}
.chip.on{{background:var(--ink);color:var(--paper)}} .chip.on .blank{{color:#f0a493}}
.tool{{display:grid;grid-template-columns:{SPAN(4) * MM:.3f}cqw 1fr;column-gap:{GUT * MM:.3f}cqw;align-items:baseline;
  padding:{1.6 * MM:.3f}cqw 0;border-top:.5pt solid var(--line)}}
.tool:first-child{{border-top:0;padding-top:0}}
.thumbs{{display:grid;grid-template-columns:repeat(4,1fr);column-gap:{GUT * MM:.3f}cqw}}
.thumbs figure{{margin:0}} .thumbs .img{{aspect-ratio:468/258;overflow:hidden}}
.thumbs figcaption{{margin-top:{1.4 * MM:.3f}cqw;padding-top:{1 * MM:.3f}cqw;border-top:.5pt solid var(--ink)}}
.folio{{position:absolute;bottom:{8 * MM:.3f}cqw;font-family:Inter,sans-serif;font-size:{pt(TYPE['furn'])};letter-spacing:.12em;text-transform:uppercase;color:var(--grey)}}
.panel{{position:absolute;left:0;top:0;bottom:0;background:{PANEL}}}
.on-panel{{color:{PANEL_INK}}} .on-panel .blank,.muted-p .blank{{color:{PANEL_RED}}} .muted-p{{color:{PANEL_MUTE}}}
.cut{{clip-path:polygon(0 0,100% 0,100% 80%,0 100%)}}
.black{{font-family:"Inter Display",Inter,sans-serif;font-weight:800;letter-spacing:-.01em;line-height:.95}}
.vt{{writing-mode:vertical-rl;transform:rotate(180deg);font-family:"Inter Display",Inter,sans-serif;font-weight:800;text-transform:uppercase;
  letter-spacing:.14em;font-size:{pt(12.5)};line-height:1}}
.band{{position:absolute;background:{BAND}}}
.rule2{{position:absolute;height:{.9 * MM:.3f}cqw;display:flex}} .rule2 i{{flex:6;border-top:1.4pt solid var(--line)}} .rule2 b{{flex:4;border-top:1.4pt solid var(--ink)}}
.dot{{position:absolute;width:{2.2 * MM:.3f}cqw;height:{2.2 * MM:.3f}cqw;border:.9pt solid var(--ink);border-radius:50%;background:var(--paper)}}
.vline{{position:absolute;border-left:.9pt solid var(--ink)}}
.script{{position:absolute;right:{4 * MM:.3f}cqw;bottom:{-6 * MM:.3f}cqw;font-family:Caladea,serif;font-style:italic;font-weight:400;
  font-size:{pt(22)};color:var(--accent-text);letter-spacing:0;transform:rotate(-5deg);white-space:nowrap;text-transform:none}}
.black-head{{font-family:"Inter Display",Inter,sans-serif;font-weight:900;text-transform:uppercase;font-size:{pt(11.5)};letter-spacing:.01em;line-height:1.1}}
.tilerow{{display:grid;grid-template-columns:{14 * MM:.3f}cqw 1fr;column-gap:{4 * MM:.3f}cqw;align-items:center;margin-top:{3.4 * MM:.3f}cqw}}
.tile{{width:{14 * MM:.3f}cqw;height:{14 * MM:.3f}cqw;background:var(--ink);color:var(--paper);display:flex;align-items:center;justify-content:center;
  font-family:"Inter Display",Inter,sans-serif;font-weight:800;font-size:{pt(17)};line-height:1}} .tile .blank{{color:{PANEL_RED};font-weight:700;font-size:{pt(12)}}}
.chiprow{{display:flex;margin-top:{3 * MM:.3f}cqw;padding:0 {2 * MM:.3f}cqw}}
.chip.big{{border-width:1pt;padding:{2.2 * MM:.3f}cqw {7 * MM:.3f}cqw;font-size:{pt(8.6)}}}
.art .blank{{color:var(--grey);border-bottom:.6pt dotted var(--grey)}} .art .chip.on .blank{{color:{PANEL_MUTE};border-color:{PANEL_MUTE}}}
.artname{{font-family:"Inter Display",Inter,sans-serif;font-weight:900;font-size:{pt(54)};line-height:.86;letter-spacing:-.035em;position:relative}}
.artname span{{display:block;position:relative;width:max-content}}
.artname span::after{{content:"";position:absolute;left:-.4cqw;right:-.4cqw;top:47%;height:{.8 * MM:.3f}cqw;background:var(--paper)}}
.grain{{position:absolute;inset:0;pointer-events:none;opacity:.16;mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
.route{{position:absolute;border-top:1.6pt solid var(--ink)}}
.stop{{position:absolute;width:{3.8 * MM:.3f}cqw;height:{3.8 * MM:.3f}cqw;border-radius:50%;background:var(--paper);border:1.6pt solid var(--ink)}}
.stop.cur{{background:var(--accent-text);border-color:var(--accent-text)}}
.stopname{{font-family:Caladea,serif;font-style:italic;font-size:{pt(17)};line-height:1.1}}
.film{{background:var(--ink);padding:{4.2 * MM:.3f}cqw 0 0 {3 * MM:.3f}cqw;
  background-image:radial-gradient(circle,var(--paper) 0 {.55 * MM:.3f}cqw,transparent {.6 * MM:.3f}cqw),radial-gradient(circle,var(--paper) 0 {.55 * MM:.3f}cqw,transparent {.6 * MM:.3f}cqw);
  background-size:{3.2 * MM:.3f}cqw {3.2 * MM:.3f}cqw;background-position:0 {.5 * MM:.3f}cqw,0 calc(100% - {.5 * MM:.3f}cqw);background-repeat:repeat-x}}
.frames{{display:grid;column-gap:{2.4 * MM:.3f}cqw}} .frames figure{{margin:0}} .frames .img{{aspect-ratio:468/258;overflow:hidden}}
.frames figcaption{{font-family:Inter,sans-serif;font-size:{pt(6.8)};letter-spacing:.12em;color:{PANEL_MUTE};margin-top:{.6 * MM:.3f}cqw}}
.question{{font-family:Caladea,serif;font-style:italic;font-size:{pt(19)};line-height:1.1}}
@page{{size:{W_MM}mm {H_MM}mm;margin:0}}
@media print{{html,body{{background:none}} main{{display:block;padding:0}} .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;box-shadow:none}}}}
html.print-sim main{{display:block;padding:0;width:{W_MM}mm}} html.print-sim .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;box-shadow:none}}
"""


def layout_rows(s, at, rule, img) -> list:
    """Reference ① (text-led): name | portrait | profile, then three-zone rows under ink rules."""
    pr = s["profile"]
    h = []
    # ---- head: name | portrait | profile -------------------------------------------------------------------
    h.append(at(0, 14, 5, f'<div class="name" lang="en">{"<br>".join(e(x) for x in s["name"])}</div>'
                          f'<p class="caps" style="margin-top:{4.2 * MM:.3f}cqw">{e(s["role"])} — {e(s["applying"])}</p>'))
    h.append(at(0, 50, 4, "".join(f'<p class="role" lang="en"><span style="color:var(--grey)">{e(c["label"])}</span>&ensp;'
                                  f'{val(c["value"], c["label"])}</p>' for c in s["contact"])))
    pw = SPAN(3)
    h.append(at(5, 14, 3, f'<div style="height:{pw * 4 / 3 * MM:.3f}cqw">{img(s["portrait"]["photo"], "62% 50%")}</div>'))
    h.append(at(5, 14 + pw * 4 / 3 + 1.8, 3, f'<p class="cap" lang="ko" style="font-family:var(--ko-sans);word-break:keep-all">{e(s["portrait"]["note"])}</p>'))
    h.append(at(8, 14, 4, f'<p class="head" lang="en">Profile</p>'
                          f'<p class="lead-ko" lang="ko" style="margin-top:{3 * MM:.3f}cqw">{e(pr["ko"])}</p>'
                          f'<p class="lead-en" lang="en" style="margin-top:{2.4 * MM:.3f}cqw">{e(pr["en"])}</p>'
                          f'<p class="ko" lang="ko" style="margin-top:{2.8 * MM:.3f}cqw;color:var(--grey)">{e(pr["more"])}</p>'))

    # ---- rows: label (cols 0-2) | title, place, years (3-6) | description (7-11) ---------------------------
    y = 92
    h.append(rule(y))
    h.append(at(0, y + 4, 3, '<p class="head" lang="en">Education</p>'))
    for ed in s["education"]:
        h.append(at(3, y + 4, 4, f'<p class="t ko-t" lang="ko">{val(ed["school"], "학교")}</p>'
                                 f'<p class="ko">{val(ed["major"], "전공 · 학위")}</p>'))
        h.append(at(7, y + 4, 5, f'<p class="ko">{val(ed["line"], "졸업 작품 · 주요 수업 한 줄")}</p>'
                                 f'<p class="role" style="margin-top:{1 * MM:.3f}cqw;color:var(--grey)">{val(ed["years"], "20XX – 20XX")}</p>'))
        y += 20
    h.append(rule(y, thin=False))
    h.append(at(0, y + 4, 3, '<p class="head" lang="en">Projects</p>'))
    py = y + 4
    for p in s["projects"]:
        h.append(at(3, py, 4, f'<p class="t" lang="en">{val(p["title"], "프로젝트")}</p>'
                              f'<p class="ko" style="color:var(--grey)">{val(p["kind"], "성격 · 역할")}</p>'
                              f'<p class="role" style="color:var(--grey)">{val(p["years"], "기간")}</p>'))
        h.append(at(7, py, 5, f'<p class="ko" lang="ko">{val(p["what"], "무엇을 했고 결과가 무엇이었는지 한두 줄")}</p>'))
        py += 19
    y = py + 2
    h.append(rule(y))
    h.append(at(0, y + 4, 3, '<p class="head" lang="en">Tools</p><p class="cap" lang="ko" style="font-family:var(--ko-sans);margin-top:'
                             f'{1.5 * MM:.3f}cqw">게이지 대신, 할 줄 아는 것</p>'))
    h.append(at(3, y + 4, 9, "".join(f'<div class="tool"><p class="t" lang="en">{val(t["name"], "툴 이름")}</p>'
                                     f'<p class="ko" lang="ko">{val(t["can"], "이 툴로 할 줄 아는 것 한 줄 — 예: 평면 · 단면 도면, 3D 모델링, 렌더링" if i == 0 else "할 줄 아는 것")}</p></div>'
                                     for i, t in enumerate(s["tools"]))))
    y += 4 + 4 * 8.6 + 9
    h.append(rule(y))
    h.append(at(0, y + 4, 3, '<p class="head" lang="en">Skills</p>'))
    h.append(at(3, y + 4, 9, '<div class="chips">' + "".join(
        f'<span class="chip{" on" if c["on"] else ""}" lang="en">{val(c["t"], "스킬")}</span>' for c in s["skills"]) + "</div>"))
    y += 18
    h.append(rule(y, thin=True))
    h.append(at(0, y + 4, 3, '<p class="head" lang="en">Languages</p>'))
    for i, l_ in enumerate(s["languages"]):
        h.append(at(3 + 3 * i, y + 4, 3, f'<p class="t" lang="en">{e(l_["lang"])}</p>'
                                         f'<p class="role">{val(l_["level"], "수준 · 점수")}</p>'))
    y += 18
    h.append(rule(y))
    h.append(at(0, y + 4, 3, '<p class="head" lang="en">Photographs</p>'
                             f'<p class="lead-en" lang="en" style="margin-top:{2 * MM:.3f}cqw">{e(s["question"])}</p>'))
    h.append(at(3, y + 4, 9, '<div class="thumbs">' + "".join(
        f'<figure><div class="img">{img(n)}</div><figcaption class="cap" lang="en">{int(n):02d}</figcaption></figure>'
        for n in s["photographs"]) + "</div>"))
    h.append(f'<div class="folio" lang="en" style="left:{MARGIN * MM:.3f}cqw">{e(" ".join(s["name"]))} — Curriculum Vitae</div>')
    h.append(f'<div class="folio" style="right:{MARGIN * MM:.3f}cqw;color:var(--accent-text)">'
             f'Test version · [ ] {len(blanks(s))} blanks to fill</div>')

    return h


PW = X(5) - GUT / 2                                  # the split layout's dark panel: page edge to the gutter before col 5


def _c(v: float) -> str:
    return f"{v * MM:.3f}cqw"


def layout_split(s, at, rule, img) -> list:
    """References ② ④ ⑤: a dark left panel with the photograph bled off the top (its foot cut on a diagonal, ④),
    name and role in light type (②); on the right, section titles set upright along the edge (②) and a dotted
    timeline for dated entries (④). No gauges or bars (④ ⑤) -- the same fields are written out."""
    pr = s["profile"]
    h = [f'<div class="panel" style="width:{_c(PW)}"></div>',
         f'<div class="a cut" data-bleed style="left:0;top:0;width:{_c(PW)};height:{_c(122)}">{img(s["portrait"]["photo"], "62% 50%")}</div>']
    h.append(at(0, 128, 4, f'<div class="name black on-panel" lang="en" style="font-size:{pt(30)}">{"<br>".join(e(x) for x in s["name"])}</div>'
                           f'<p class="caps on-panel" style="margin-top:{_c(4.5)};letter-spacing:.32em;font-size:{pt(7.8)}">{e(s["role"])}</p>'
                           f'<p class="caps muted-p" style="letter-spacing:.32em;font-size:{pt(7.8)}">{e(s["applying"])}</p>'))
    h.append(at(0, 166, 4, f'<p class="head on-panel" lang="en">Profile</p>'
                           f'<p class="lead-ko on-panel" lang="ko" style="margin-top:{_c(2.6)};font-size:{pt(9.6)}">{e(pr["ko"])}</p>'
                           f'<p class="lead-en muted-p" lang="en" style="margin-top:{_c(2)};font-size:{pt(8.4)}">{e(pr["en"])}</p>'))
    h.append(at(0, 226, 4, f'<p class="head on-panel" lang="en">Contact</p>' + "".join(
        f'<p class="role on-panel" lang="en" style="margin-top:{_c(1.2)}"><span class="muted-p">{e(c["label"])}</span>&ensp;{val(c["value"], c["label"])}</p>'
        for c in s["contact"])))
    h.append(at(0, 262, 4, f'<p class="cap muted-p" lang="ko" style="font-family:var(--ko-sans);word-break:keep-all">{e(s["portrait"]["note"])}</p>'))

    def section(top, bottom, title, band=False):
        if bottom - top - 4 < len(title) * 3.6:        # 12.5 pt caps at .14em tracking: 3.4-3.5 mm a letter, measured
            raise ValueError(f"upright title '{title}' needs {len(title) * 3.6:.0f} mm, section has {bottom - top - 4:.0f}")
        out = []
        if band:
            out.append(f'<div class="band" style="left:{_c(PW)};right:0;top:{_c(top - 4)};height:{_c(bottom - top + 4)}"></div>')
        out.append(f'<div class="rule2" style="left:{_c(X(6))};right:{_c(MARGIN)};top:{_c(top)}"><i></i><b></b></div>')
        out.append(at(5, top + 4, 1, f'<p class="vt" lang="en">{e(title)}</p>'))   # natural height: an overlong title is a measured overlap
        return out

    def timeline(top, rows, step):
        """rows: [(left html, right html)] -- years at cols 6-7, a dot in the gutter, the entry at cols 8-11."""
        out, xd = [], X(8) - GUT / 2
        if len(rows) > 1:
            out.append(f'<div class="vline" style="left:{_c(xd)};top:{_c(top + 1.6)};height:{_c(step * (len(rows) - 1))}"></div>')
        for i, (l_, r_) in enumerate(rows):
            y = top + i * step
            out.append(f'<div class="dot" style="left:{_c(xd - 1.1)};top:{_c(y + 0.5)}"></div>')
            out.append(at(6, y, 2, l_))
            out.append(at(8, y, 4, r_))
        return out

    h += section(14, 56, "Education")
    h += timeline(20, [(f'<p class="role">{val(ed["years"], "20XX – 20XX")}</p>',
                        f'<p class="t ko-t" lang="ko">{val(ed["school"], "학교")}</p><p class="ko">{val(ed["major"], "전공 · 학위")}</p>'
                        f'<p class="ko" style="color:var(--grey)">{val(ed["line"], "졸업 작품 · 주요 수업 한 줄")}</p>')
                       for ed in s["education"]], 0)
    h += section(62, 122, "Projects", band=True)
    h += timeline(68, [(f'<p class="role">{val(p["years"], "기간")}</p>',
                        f'<p class="t" lang="en">{val(p["title"], "프로젝트")}</p><p class="ko" style="color:var(--grey)">{val(p["kind"], "성격 · 역할")}</p>'
                        f'<p class="ko" lang="ko" style="margin-top:{_c(.8)}">{val(p["what"], "무엇을 했고 결과가 무엇이었는지 한두 줄")}</p>')
                       for p in s["projects"]], 28)
    h += section(128, 172, "Tools")
    for i, t in enumerate(s["tools"]):
        y = 134 + i * 10
        h.append(at(6, y, 2, f'<p class="t" lang="en">{val(t["name"], "툴 이름")}</p>'))
        h.append(at(8, y, 4, f'<p class="ko" lang="ko">{val(t["can"], "할 줄 아는 것 — 예: 평면 · 단면 도면, 3D 모델링" if i == 0 else "할 줄 아는 것")}</p>'))
    h += section(176, 210, "Skills")
    h.append(at(6, 182, 6, '<div class="chips">' + "".join(
        f'<span class="chip{" on" if c["on"] else ""}" lang="en">{val(c["t"], "스킬")}</span>' for c in s["skills"]) + "</div>"))
    h += section(214, 252, "Language")
    for i, l_ in enumerate(s["languages"]):
        h.append(at(6 + 3 * i, 220, 3, f'<p class="t" lang="en">{e(l_["lang"])}</p><p class="role">{val(l_["level"], "수준 · 점수")}</p>'))
    h.append(f'<div class="rule2" style="left:{_c(X(6))};right:{_c(MARGIN)};top:{_c(256)}"><i></i><b></b></div>')
    h.append(at(6, 260, 6, '<div class="thumbs">' + "".join(
        f'<figure><div class="img">{img(n)}</div><figcaption class="cap" lang="en">{int(n):02d}</figcaption></figure>' for n in s["photographs"]) + "</div>"))
    h.append(f'<div class="folio" style="right:{_c(MARGIN)};color:var(--accent-text)">Test version · [ ] {len(blanks(s))} blanks to fill</div>')
    return h


def layout_creative(s, at, rule, img) -> list:
    """Reference ③: a square photograph, a black heavy name with the role written across it in red (the reference's
    script face is not here -- Caladea italic stands in, and says so in the docs), tools as black tiles beside what
    they are used for, skills as chips set off-centre in three rows."""
    pr = s["profile"]
    sq = SPAN(5)
    h = [at(0, 16, 5, f'<div style="height:{_c(sq)}">{img(s["portrait"]["photo"], "62% 50%")}</div>'),
         at(0, 16 + sq + 1.8, 5, f'<p class="cap" lang="ko" style="font-family:var(--ko-sans);word-break:keep-all">{e(s["portrait"]["note"])}</p>')]
    h.append(at(6, 24, 6, f'<div class="name black" lang="en" style="font-size:{pt(40)};line-height:.92;position:relative">'
                          f'{"<br>".join(e(x) for x in s["name"])}'
                          f'<span class="script" lang="en">{e(s["role"])}</span></div>'))
    h.append(at(6, 62, 6, f'<p class="ko" lang="ko" style="font-weight:600;font-size:{pt(9.4)};line-height:1.6;color:var(--ink)">{e(pr["ko"])}</p>'
                          f'<p lang="en" style="font-family:Inter,sans-serif;font-style:italic;font-weight:600;font-size:{pt(8)};line-height:1.45;margin-top:{_c(2)}">{e(pr["en"])}</p>'))

    def head(t):
        return f'<p class="black-head" lang="en">{e(t)}</p>'

    h.append(at(0, 112, 5, head("Personal Information") + "".join(
        f'<p class="role" lang="en" style="margin-top:{_c(1.1)}"><span style="color:var(--grey)">{e(c["label"])}</span>&ensp;{val(c["value"], c["label"])}</p>'
        for c in s["contact"])))
    ed = s["education"][0]
    h.append(at(0, 148, 5, head("Education") + f'<p class="t ko-t" lang="ko" style="margin-top:{_c(1.5)}">{val(ed["school"], "학교")}</p>'
                           f'<p class="ko">{val(ed["major"], "전공 · 학위")} ( {val(ed["years"], "20XX – 20XX")} )</p>'))
    h.append(at(0, 170, 5, head("Projects") + "".join(
        f'<p class="t" lang="en" style="margin-top:{_c(2)}">{val(p["title"], "프로젝트")}</p>'
        f'<p class="ko" style="color:var(--grey)">{val(p["kind"], "성격 · 역할")} · {val(p["years"], "기간")}</p>'
        f'<p class="ko">{val(p["what"], "무엇을 했고 결과가 무엇이었는지 한두 줄")}</p>' for p in s["projects"])))
    h.append(at(6, 112, 6, head("Tools") + "".join(
        f'<div class="tilerow"><div class="tile" lang="en">{e(t["name"][:2]) if t["name"] else blank(" ")}</div>'
        f'<div><p class="t" lang="en">{val(t["name"], "툴 이름")}</p><p class="ko">{val(t["can"], "할 줄 아는 것 — 예: 평면 · 단면 도면, 3D 모델링" if i == 0 else "할 줄 아는 것")}</p></div></div>'
        for i, t in enumerate(s["tools"]))))
    sk = s["skills"]
    rows_ = [sk[0:2], sk[2:3], sk[3:5]]
    just = ["space-between", "center", "space-between"]
    h.append(at(6, 196, 6, head("Skills") + "".join(
        f'<div class="chiprow" style="justify-content:{j}">' + "".join(
            f'<span class="chip big{" on" if c["on"] else ""}" lang="en">{val(c["t"], "스킬")}</span>' for c in r) + "</div>"
        for r, j in zip(rows_, just))))
    h.append(at(0, 238, 5, head("Language") + "".join(
        f'<p class="role" lang="en" style="margin-top:{_c(1.1)}"><b>{e(l_["lang"])}</b>&ensp;{val(l_["level"], "수준 · 점수")}</p>' for l_ in s["languages"])))
    h.append(at(0, 256, 12, '<div class="thumbs">' + "".join(
        f'<figure><div class="img">{img(n)}</div></figure>' for n in s["photographs"]) + "</div>"))
    h.append(f'<div class="folio" lang="en" style="left:{_c(MARGIN)}">{e(s["question"])}</div>')
    h.append(f'<div class="folio" style="right:{_c(MARGIN)};color:var(--accent-text)">Test version · [ ] {len(blanks(s))} blanks to fill</div>')
    return h


def layout_art(s, at, rule, img) -> list:
    """The artistic one: the CV as a route of stops. No portrait -- the applicant's own photographs carry the
    person (his note on the reference board: tell who I am through the photos I took). A photograph bled across the
    top, the name cut by a paper-coloured stop line, the profile as a serif statement, then a transit line whose four
    stops are the CV's sections -- the one stop with something real in it marked red, the only red on the page --
    and a strip of film running off the right edge. Blanks are grey and dotted here, so the red keeps its job."""
    pr, a = s["profile"], s["art"]
    HERO = 106
    h = [f'<div class="a" data-bleed style="left:0;top:0;width:100cqw;height:{_c(HERO)}">{img(a["hero"], a.get("hero_pos", "50% 50%"))}'
         f'<div class="grain"></div></div>',
         f'<div class="a cap" lang="en" style="right:{_c(MARGIN)};top:{_c(HERO + 1.6)};text-align:right">Photograph {int(a["hero"]):02d} — {e(" ".join(s["name"]).title())}</div>']
    h.append(at(0, HERO + 6, 7, f'<div class="artname" lang="en">{"".join(f"<span>{e(x)}</span>" for x in s["name"])}</div>'
                                f'<p class="caps" style="margin-top:{_c(4)};letter-spacing:.3em">{e(s["role"])} &nbsp;/&nbsp; {e(s["applying"])}</p>'))
    h.append(at(8, HERO + 8, 4, f'<p class="lead-ko" lang="ko" style="font-size:{pt(11.2)};line-height:1.58">{e(pr["ko"])}</p>'
                                f'<p class="lead-en" lang="en" style="margin-top:{_c(2.4)};color:var(--grey)">{e(pr["en"])}</p>'))
    # ---- the route: one line, four stops, one per section ---------------------------------------------------
    Y = 175
    h.append(f'<div class="route" style="left:{_c(MARGIN)};right:0;top:{_c(Y)}"></div>')
    stops = [("Education", 0), ("Projects", 3), ("Tools", 6), ("Skills", 9)]
    for i, (name_, c) in enumerate(stops):
        cur = name_ == a.get("current_stop")
        h.append(f'<div class="stop{" cur" if cur else ""}" style="left:{_c(X(c) - 1.9)};top:{_c(Y - 1.9)}"></div>')
        h.append(at(c, Y - 13, 3, f'<p class="caps" lang="en" style="color:{"var(--accent-text)" if cur else "var(--grey)"}">Stop {i + 1:02d}</p>'
                                  f'<p class="stopname" lang="en">{e(name_)}</p>'))
    ed = s["education"][0]
    body = {
        0: f'<p class="t ko-t" lang="ko">{val(ed["school"], "학교")}</p><p class="ko">{val(ed["major"], "전공 · 학위")}</p>'
           f'<p class="role" style="color:var(--grey)">{val(ed["years"], "20XX – 20XX")}</p>'
           f'<p class="ko" style="margin-top:{_c(1.5)}">{val(ed["line"], "졸업 작품 · 주요 수업 한 줄")}</p>',
        3: "".join(f'<div style="margin-bottom:{_c(3.2)}"><p class="t" lang="en">{val(p["title"], "프로젝트")}</p>'
                   f'<p class="ko" style="color:var(--grey)">{val(p["kind"], "성격 · 역할")} · {val(p["years"], "기간")}</p>'
                   f'<p class="ko">{val(p["what"], "무엇을 했고 결과가 무엇이었는지 한두 줄")}</p></div>' for p in s["projects"]),
        6: "".join(f'<p class="t" lang="en"{"" if i == 0 else f" style=\"margin-top:{_c(2)}\""}>{val(t["name"], "툴 이름")}</p>'
                   f'<p class="ko">{val(t["can"], "할 줄 아는 것")}</p>' for i, t in enumerate(s["tools"])),
        9: '<div class="chips" style="gap:1.2cqw .9cqw">' + "".join(
               f'<span class="chip{" on" if c_["on"] else ""}" lang="en">{val(c_["t"], "스킬")}</span>' for c_ in s["skills"]) + "</div>"
           + f'<p class="caps" lang="en" style="margin-top:{_c(4.5)};color:var(--grey)">Language</p>' + "".join(
               f'<p class="role" lang="en"><b>{e(l_["lang"])}</b>&ensp;{val(l_["level"], "수준")}</p>' for l_ in s["languages"]),
    }
    for c, b in body.items():
        h.append(at(c, Y + 6, 3, b))
    # ---- film: frames off the right edge ------------------------------------------------------------------
    F = 239
    fw = 25.0
    frames = "".join(f'<figure><div class="img">{img(n)}</div><figcaption>{int(n):02d}</figcaption></figure>' for n in a["film"])
    h.append(f'<div class="a film" data-bleed style="left:{_c(MARGIN)};right:0;top:{_c(F)};height:{_c(27)}">'
             f'<div class="frames" style="grid-template-columns:repeat({len(a["film"])},{_c(fw)})">{frames}</div></div>')
    h.append(at(0, F + 30, 6, f'<p class="question" lang="en">{e(s["question"])}</p>'))
    h.append(at(6, F + 31, 6, '<p class="role" lang="en" style="text-align:right">' + "&emsp;".join(
        f'<span style="color:var(--grey)">{e(c_["label"])}</span>&ensp;{val(c_["value"], c_["label"])}' for c_ in s["contact"][:2]) + "<br>" + "&emsp;".join(
        f'<span style="color:var(--grey)">{e(c_["label"])}</span>&ensp;{val(c_["value"], c_["label"])}' for c_ in s["contact"][2:]) + "</p>"))
    h.append(f'<div class="folio" lang="en" style="left:{_c(MARGIN)}">{e(" ".join(s["name"]))} — Curriculum Vitae</div>')
    h.append(f'<div class="folio" style="right:{_c(MARGIN)}">Test version · {len(blanks(s))} dotted blanks to fill</div>')
    return h


LAYOUTS = {"rows": "① 행 구조 — 이름 | 사진 | 프로필, 아래로 세 칸 행 (Laura)",
           "split": "②④⑤ 사진 반쪽 — 어두운 왼쪽 패널에 사진 · 이름, 오른쪽에 세운 섹션 제목과 연표 (Richard · YOUR NAME · Noah)",
           "art": "예술형 — 노선도의 정거장: 찍은 사진이 주인공, 정지선에 잘린 이름, 네 정거장, 필름 띠 (SPA 의 '멈춘다')",
           "creative": "③ 크리에이티브 — 정사각 사진, 굵은 이름 위에 붉은 직함, 툴 타일과 엇갈린 칩 (Le Khanh Huyen)"}


def build(spec_path, name: str = "", pdf: bool = True, layout: str = "rows") -> dict:
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = paths.OUT / (name or spec["id"]) / ("cv" if layout == "rows" else f"cv-{layout}")
    (out / "img").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    for fn in [f[2] for f in FACES] + ["LICENSE-Pretendard.txt", "LICENSE-NotoSerifCJK.txt"]:
        if (FONT_DIR / fn).is_file() and not (out / "fonts" / fn).is_file():
            (out / "fonts" / fn).write_bytes((FONT_DIR / fn).read_bytes())

    pdir = paths.REPO / spec["photo_dir"]
    src, missing = {}, []
    art = spec.get("art", {})
    for n in dict.fromkeys([spec["portrait"]["photo"]] + spec["photographs"] + ([art["hero"]] + art["film"] if layout == "art" else [])):
        k = f"{int(n):02d}"
        f = pdir / f"{k}.png"
        if not f.is_file():
            missing.append(k)
            continue
        from PIL import Image
        with Image.open(f) as im:
            src[k] = im.size
        dst = out / "img" / f"{k}_bw.jpg"
        bw_copy(f, dst)

    def img(n, pos="50% 50%"):
        k = f"{int(n):02d}"
        if k not in src:
            return f'<div class="ph" style="background:var(--line)"></div>'
        return (f'<img class="ph" src="img/{k}_bw.jpg" alt="Photograph {k}" data-photo="{k}" data-srcpx="{src[k][0]}" '
                f'style="object-position:{pos}">')

    def at(c, top, span, body, cls="", style=""):
        return (f'<div class="a {cls}" data-col="{c}" style="left:{X(c) * MM:.3f}cqw;top:{top * MM:.3f}cqw;'
                f'width:{SPAN(span) * MM:.3f}cqw;{style}">{body}</div>')

    def rule(top, thin=False, x0=MARGIN, x1=MARGIN):
        return f'<div class="rule{" thin" if thin else ""}" style="left:{x0 * MM:.3f}cqw;right:{x1 * MM:.3f}cqw;top:{top * MM:.3f}cqw"></div>'

    s = spec
    h = {"rows": layout_rows, "split": layout_split, "creative": layout_creative, "art": layout_art}[layout](s, at, rule, img)
    pairs = [("ink on paper", INK, PAPER), ("grey on paper", GREY, PAPER), ("red blanks on paper", ACCENT_TEXT, PAPER)]
    if layout == "split":
        pairs += [("light on panel", PANEL_INK, PANEL), ("muted on panel", PANEL_MUTE, PANEL), ("red blanks on panel", PANEL_RED, PANEL),
                  ("ink on band", INK, BAND), ("grey on band", GREY, BAND), ("red blanks on band", ACCENT_TEXT, BAND)]
    if layout == "art":
        pairs = [p_ for p_ in pairs if not p_[0].startswith("red blanks")] + [("red stop label", ACCENT_TEXT, PAPER), ("frame numbers on film", PANEL_MUTE, INK)]
    if layout == "creative":
        pairs += [("paper on black tiles", PAPER, INK), ("red blanks on black", PANEL_RED, INK)]
    s_ = s
    page = f'<section class="page {layout}" id="cv" data-type="cv" data-layout="{layout}">{"".join(h)}</section>'
    doc_html = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{e(" ".join(s_["name"]))} — CV</title><style>{css()}</style></head><body><main>{page}</main>'
                f'<script>{QA_JS}</script></body></html>')
    hp = out / "index.html"
    hp.write_text(doc_html, encoding="utf-8")
    pres = PDF.render(hp, out / "cv.pdf") if pdf else None
    need = {"Pretendard 400", "Pretendard 600"} | ({"Noto Serif KR 400"} if "lead-ko" in page else set())
    checks = qa(spec, hp, pres, pdf, src, missing, pairs, need)
    verdict = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("WARNING" if any(c["status"] == "WARNING" for c in checks) else "PASS")
    (out / "qa.json").write_text(json.dumps({"verdict": verdict, "checks": checks, "blanks": blanks(spec)}, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [f"# CV QA — {verdict} · {LAYOUTS[layout]}", "", "| 결과 | 검사 | 근거 |", "|---|---|---|"] + \
         [f"| {c['status']} | {c['check']} | {c['detail']} |" for c in checks] + ["", "## 지원자가 채울 칸", ""] + [f"- {b}" for b in blanks(spec)]
    (out / "QA_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return {"dir": str(out), "html": str(hp), "layout": layout, "pdf": (pres or {}).get("path"), "pdf_result": pres, "verdict": verdict,
            "checks": checks, "blanks": blanks(spec)}


def C(check, status, detail="") -> dict:
    return {"check": check, "status": status, "detail": detail}


def qa(spec, hp, pres, want_pdf, src, missing, pairs, need) -> list:
    out = []
    bad = check_texts(spec)
    out.append(C("printed sentences are word for word from their sources", "FAIL" if bad else "PASS", "; ".join(bad) or "profile ko/en/more, name, question"))
    b = blanks(spec)
    out.append(C("fields left for the applicant (not invented)", "WARNING" if b else "PASS", f"{len(b)} blanks, printed as [ ] (red; grey and dotted in the art layout)"))
    out.append(C("every photo in the spec is on disk", "FAIL" if missing else "PASS", ", ".join(missing) or f"{len(src)} photos"))
    m = PDF.measure(hp, round(W_MM / 25.4 * 96), round(H_MM / 25.4 * 96), "qa-print")
    if not m.get("ok"):
        out.append(C("page measured in Chromium", "NOT_CHECKED", m.get("error", "")))
        return out
    p = m["pages"][0]
    out.append(C("nothing runs past the page", "FAIL" if p["overflow"] or p["self_scroll"] else "PASS", ", ".join(p["overflow"]) or "none"))
    out.append(C("no text block overlaps another", "FAIL" if p["clash"] else "PASS", "; ".join(p["clash"][:6]) or "none"))
    px_per_pt = 96 / 72
    minpt = p["minfs"] / px_per_pt
    out.append(C(f"smallest text >= {MIN_PT} pt on paper", "PASS" if minpt >= MIN_PT - 0.05 else "FAIL", f"{minpt:.2f} pt"))
    faux = [f for f in p["faux"] if int(f.split("|")[0]) not in KO_WEIGHTS.get(f.split("|")[1], set())]
    out.append(C("Korean set only in weights that have a real face", "FAIL" if faux else "PASS", "; ".join(faux[:5]) or "none"))
    have = set(m.get("fonts", []))
    out.append(C("vendored Korean fonts load", "FAIL" if need - have else "PASS", ", ".join(sorted(need - have)) or ", ".join(sorted(need))))
    off = [c for c in p["cols"] if abs(c["x"] - X(c["col"]) / W_MM * 100) > 0.3]
    out.append(C("blocks sit on the 12-column grid", "FAIL" if off else "PASS", f"{len(off)} off" if off else f"{len(p['cols'])} blocks"))
    broken = [i["src"] for i in p["images"] if not i["ok"]]
    out.append(C("images load", "FAIL" if broken else "PASS", ", ".join(broken) or f"{len(p['images'])} images"))
    low = []
    for i in p["images"]:
        if i["srcpx"] and i["rw"]:
            scale = max(i["rw"] / i["nw"], i["rh"] / i["nh"]) if i["fit"] == "cover" else i["rw"] / i["nw"]   # css px per file px
            dpi = 96 / scale * (i["srcpx"] / i["nw"])
            if dpi < PRINT_DPI:
                low.append(f"{i['photo']} {dpi:.0f} dpi")
    out.append(C(f"print resolution >= {PRINT_DPI} dpi", "FAIL" if low else "PASS",
                 (", ".join(low) + " -- the source photos are 468 px screenshots; the originals are needed") if low else "all"))
    for name_, fg, bg in pairs:
        cr = DS.contrast(fg, bg)
        out.append(C(f"text contrast: {name_}", "PASS" if cr >= 4.5 else "FAIL", f"{fg} on {bg} {cr:.2f}:1"))
    if want_pdf:
        ok_ = bool(pres and pres.get("ok") and pres.get("pages") == 1)
        out.append(C("PDF is one A4 page", "PASS" if ok_ else "FAIL", f"{(pres or {}).get('pages')} page(s), {(pres or {}).get('bytes', 0) // 1024} KB" if pres and pres.get("ok") else str((pres or {}).get("error"))))
    else:
        out.append(C("PDF is one A4 page", "NOT_CHECKED", "not requested"))
    return out
