"""One call from a brief to a checked magazine.

    out/<name>/magazine/
        index.html  magazine.pdf  assets/*.svg
        plan.json        brief reading, every direction, the chosen one, page plan
        hypotheses.json  the design hypotheses (with drift paths and measures)
        assets.json      the asset catalogue (printed and withheld)
        qa.json  QA_REPORT.md
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from gentle_monster import paths
from gentle_monster.magazine import assets as A, catalogue as CAT, design as DS, pdf as PDF, planner as PL, plates as PT, qa as QA, render as R


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def se_new_dir() -> "Path | None":
    for c in (os.environ.get("SE_NEW_DIR"), paths.REPO.parent / "se_new", paths.REPO.parent / "SE", Path("/home/ubuntu/SE")):
        if c and Path(c, "novel", "DRIFT.md").is_file():
            return Path(c)
    return None


def build(brief: str, name: str = "", images=(), pdf: "bool | None" = None, cat_path=None, check_links: bool = False) -> dict:
    cat = CAT.load(cat_path)
    plan = PL.make_plan(brief, cat)
    want_pdf = plan["brief"]["outputs"]["pdf"] if pdf is None else pdf
    chosen = next(h for h in plan["hypotheses"] if h["hypothesis_id"] == plan["chosen"])
    name = name or time.strftime("mag_%Y%m%d_%H%M%S")
    out = paths.job_dir(name) / "magazine"
    (out / "assets").mkdir(parents=True, exist_ok=True)
    tokens = DS.tokens(chosen["palette"])

    plates, gen = {}, []
    for p in plan["pages"]:
        kind = p.get("plate")
        if not kind:
            continue
        f = out / "assets" / f"{p['folio']:02d}-{_slug(p['section'])}-{kind}.svg"
        f.write_text(PT.svg(kind, f"{plan['brief']['seed']}:{p['folio']}", tokens["color"], f"{kind} plate (generated drawing)"),
                     encoding="utf-8")
        a = A.generated(f, kind, chosen["hypothesis_id"])
        plates[p["section"]] = a
        gen.append(a)
    user = [A.user_image(*im) for im in images]
    if user and A.publishable(user[0]):
        plates["Cover"] = user[0]                         # a cleared photograph beats a drawing on the cover
    refs = A.from_sources(cat)
    assets = user + gen + refs
    for h in plan["hypotheses"]:
        need = [d for d in h["layout_implications"] if PL.D.DEVICES[d["device"]][2]]
        h["scores"]["rights_compliance"] = 1.0 if need else None     # its plates are generated here, so ours to print
    chosen["scores"]["rights_compliance"] = 1.0
    bad_assets = [b for a in assets for b in A.problems(a)]

    title = f"Gentle Monster Field Notes -- {chosen['title']}"
    res = R.build(plan, cat, assets, plates, tokens, out, title)
    pdf_res = PDF.render(res["html"], out / "magazine.pdf") if want_pdf else None
    html_text = Path(res["html"]).read_text(encoding="utf-8")
    checks = (QA.research(cat, CAT.load_drift(), se_new_dir(), check_links)
              + QA.creative(plan, res["pages"], html_text, assets)
              + QA.production(res["pages"], Path(res["html"]), pdf_res, tokens, want_pdf))
    checks.append(QA._c("production", "asset metadata complete", "FAIL" if bad_assets else "PASS",
                        "; ".join(bad_assets[:5]) or f"{len(assets)} assets, {len(A.FIELDS)} fields each"))
    QA.save(checks, out, title)

    plan_out = {k: v for k, v in plan.items() if k != "hypotheses"}
    plan_out["rendered_pages"] = res["pages"]
    plan_out["directions"] = [{k: h[k] for k in ("hypothesis_id", "title", "status", "total", "strength", "weakness", "scores")}
                              | {"excluded_because": h.get("excluded_because")} for h in plan["hypotheses"]]
    (out / "plan.json").write_text(json.dumps(plan_out, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "hypotheses.json").write_text(json.dumps(plan["hypotheses"], ensure_ascii=False, indent=1), encoding="utf-8")
    A.save(assets, out / "assets.json")
    (out / "tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"dir": str(out), "html": res["html"], "pdf": (pdf_res or {}).get("path"), "pdf_result": pdf_res,
            "verdict": QA.verdict(checks), "checks": checks, "chosen": chosen["title"], "pages": len(res["pages"]),
            "directions": [(h["hypothesis_id"], h["title"], h["status"], h["total"]) for h in plan["hypotheses"]]}


def write_research_docs(cat_path=None) -> list:
    """research/*.md from the catalogue (tracked files -- generated, not hand-edited)."""
    cat = CAT.load(cat_path)
    written = []
    for rel, text in CAT.markdown(cat).items():
        p = CAT.RESEARCH / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        written.append(str(p.relative_to(paths.REPO)))
    return written
