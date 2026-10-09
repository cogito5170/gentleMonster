"""A one-page CV in the SPA design system (editorial/cv/*.json).

Content follows the reference analysis (five CV templates the user sent): name · role · contact · photo · profile ·
education · experience/projects · tools · skills · languages. Three choices taken from it:
  - the three-zone row of the text-led template (label | title, place, years | description) -- it carries the most;
  - tools written as *what you can do with them*, not as gauges or percentages (a '75 %' bar says nothing);
  - skills as chips, filled and outlined in turn.
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
PRINT_DPI = 200                                     # a CV is looked at close


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
@page{{size:{W_MM}mm {H_MM}mm;margin:0}}
@media print{{html,body{{background:none}} main{{display:block;padding:0}} .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;box-shadow:none}}}}
html.print-sim main{{display:block;padding:0;width:{W_MM}mm}} html.print-sim .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;box-shadow:none}}
"""


def build(spec_path, name: str = "", pdf: bool = True) -> dict:
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = paths.OUT / (name or spec["id"]) / "cv"
    (out / "img").mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(exist_ok=True)
    for fn in [f[2] for f in FACES] + ["LICENSE-Pretendard.txt", "LICENSE-NotoSerifCJK.txt"]:
        if (FONT_DIR / fn).is_file() and not (out / "fonts" / fn).is_file():
            (out / "fonts" / fn).write_bytes((FONT_DIR / fn).read_bytes())

    pdir = paths.REPO / spec["photo_dir"]
    src, missing = {}, []
    for n in [spec["portrait"]["photo"]] + spec["photographs"]:
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

    def rule(top, thin=False):
        return f'<div class="rule{" thin" if thin else ""}" style="left:{MARGIN * MM:.3f}cqw;right:{MARGIN * MM:.3f}cqw;top:{top * MM:.3f}cqw"></div>'

    s = spec
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

    page = f'<section class="page" id="cv" data-type="cv">{"".join(h)}</section>'
    doc_html = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{e(" ".join(s["name"]))} — CV</title><style>{css()}</style></head><body><main>{page}</main>'
                f'<script>{QA_JS}</script></body></html>')
    hp = out / "index.html"
    hp.write_text(doc_html, encoding="utf-8")
    pres = PDF.render(hp, out / "cv.pdf") if pdf else None
    checks = qa(spec, hp, pres, pdf, src, missing)
    verdict = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("WARNING" if any(c["status"] == "WARNING" for c in checks) else "PASS")
    (out / "qa.json").write_text(json.dumps({"verdict": verdict, "checks": checks, "blanks": blanks(spec)}, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [f"# CV QA — {verdict}", "", "| 결과 | 검사 | 근거 |", "|---|---|---|"] + \
         [f"| {c['status']} | {c['check']} | {c['detail']} |" for c in checks] + ["", "## 지원자가 채울 칸", ""] + [f"- {b}" for b in blanks(spec)]
    (out / "QA_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return {"dir": str(out), "html": str(hp), "pdf": (pres or {}).get("path"), "pdf_result": pres, "verdict": verdict,
            "checks": checks, "blanks": blanks(spec)}


def C(check, status, detail="") -> dict:
    return {"check": check, "status": status, "detail": detail}


def qa(spec, hp, pres, want_pdf, src, missing) -> list:
    out = []
    bad = check_texts(spec)
    out.append(C("printed sentences are word for word from their sources", "FAIL" if bad else "PASS", "; ".join(bad) or "profile ko/en/more, name, question"))
    b = blanks(spec)
    out.append(C("fields left for the applicant (not invented)", "WARNING" if b else "PASS", f"{len(b)} blanks, printed in red as [ ]"))
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
    need = {"Pretendard 400", "Pretendard 600", "Noto Serif KR 400"}
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
    for name_, col in (("ink", INK), ("grey", GREY), ("red blanks", ACCENT_TEXT)):
        cr = DS.contrast(col, PAPER)
        out.append(C(f"text contrast on paper: {name_}", "PASS" if cr >= 4.5 else "FAIL", f"{cr:.2f}:1"))
    if want_pdf:
        ok_ = bool(pres and pres.get("ok") and pres.get("pages") == 1)
        out.append(C("PDF is one A4 page", "PASS" if ok_ else "FAIL", f"{(pres or {}).get('pages')} page(s), {(pres or {}).get('bytes', 0) // 1024} KB" if pres and pres.get("ok") else str((pres or {}).get("error"))))
    else:
        out.append(C("PDF is one A4 page", "NOT_CHECKED", "not requested"))
    return out
