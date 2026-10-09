"""gentle_monster.magazine: catalogue -> drift -> plan -> assets -> HTML/PDF -> QA.

What this holds:
  1. Each gate is shown to FAIL on input broken in a known way (RED), not only to pass the real build (GREEN).
     A checker that only ever says green has not been shown to check anything.
  2. Drift keeps the SE_NEW rules it claims: lineage enforced, one operator per step, seed-reproducible,
     intrusions on schedule, inheritance needs >= 2 shared words, fiction-as-brand-fact refused.
  3. Rights: only cleared + verified + on-disk assets are printed; references never are.
  4. NOT_CHECKED is never a pass.
Browser parts are skipped with '건너뜀' when Chromium is not there.
Run: python3 tests/test_magazine.py
"""
from __future__ import annotations

import copy
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

뿌리 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(뿌리))
임시 = tempfile.mkdtemp(prefix="gmmag-")
os.environ["GENTLE_MONSTER_OUT"] = 임시

from gentle_monster.magazine import assets as A, build as MB, catalogue as CAT, drift as D, pdf as PDF, planner as PL, qa as QA  # noqa: E402

FAIL = []
BRIEF = ("Gentle Monster의 브랜드 세계관을 중심으로, 미래의 유물과 인간의 감각을 주제로 한 실험적 매거진을 제작해줘. "
         "실제 이미지와 출처를 사용하고, 관련 패션·예술 매거진의 편집 원리를 조사해 Drift 방식으로 변형해줘. 웹용 HTML과 인쇄용 PDF를 생성해줘.")


def ok(cond, what):
    print(("  ok  " if cond else "  FAIL ") + what)
    if not cond:
        FAIL.append(what)


def status(checks, name):
    return next((c["status"] for c in checks if c["check"].startswith(name)), None)


print("[catalogue]")
cat = CAT.load()
ok(CAT.validate(cat) == [], f"the repository catalogue is sound ({len(cat['sources'])} sources, {len(cat['claims'])} claims)")
bad = copy.deepcopy(cat)
c0 = bad["claims"][0]
c0["source_ids"] = []
ok(any("no source" in b for b in CAT.validate(bad)), "RED: a claim without a source is caught")
bad = copy.deepcopy(cat)
off = next(c for c in bad["claims"] if c["kind"] == "official_statement")
off["source_ids"] = [next(s["id"] for s in bad["sources"] if s["kind"] == "press")]
ok(any("without an official source" in b for b in CAT.validate(bad)), "RED: an 'official statement' cited only to the press is caught")
bad = copy.deepcopy(cat)
bad["claims"][1]["confidence"] = "high"
ok(any("snippet only" in b for b in CAT.validate(bad)), "RED: high confidence on a snippet-only claim is caught")
bad = copy.deepcopy(cat)
bad["sources"][0]["url"] = "gentlemonster.com"
ok(any("URL" in b for b in CAT.validate(bad)), "RED: a source without an http(s) URL is caught")
docs = CAT.markdown(cat)
ok("comparative_analysis/matrix.md" in docs and "No scores, no ranking" in docs["comparative_analysis/matrix.md"],
   "comparison is a matrix of what was found, not a ranking")

print("[drift]")
L = D.Ledger()
try:
    L.add({"id": "x", "origin": "op", "terms": {"a"}, "parents": ["nowhere"]})
    ok(False, "RED: a node whose parent is not in the ledger is refused")
except D.LineageError:
    ok(True, "RED: a node whose parent is not in the ledger is refused")
try:
    D.guard_text("Gentle Monster announced a relic collection in 2031.")
    ok(False, "RED: fiction stated as a brand fact is refused")
except D.ContradictionError:
    ok(True, "RED: fiction stated as a brand fact is refused")
ok(D.guard_text("Treat eyewear the way auction cataloguing treats lots.") is not None, "GREEN: a drift rule passes the guard")
m = D.measure({"a", "b", "x"}, {"a", "q", "r", "s"})
ok(m["kept"] == 1 and not m["diffusion"], "one shared word is not inheritance (mathdrift KEEP_MIN)")
m = D.measure({"a", "b", "x"}, {"a", "b", "r", "s"})
ok(m["kept"] == 2 and m["new"] == 1 and m["diffusion"], "two kept + something new is diffusion")
ok([D.draw_op("s", i) for i in range(20)] == [D.draw_op("s", i) for i in range(20)], "operator draws are seed-bound (rerun = same walk)")
jumps = sum(D.draw_op("seed", i) in D.JUMP for i in range(2000)) / 2000
ok(0.15 < jumps < 0.25, f"far jumps stay rare: {jumps:.3f} of draws (JUMP_SHARE {D.JUMP_SHARE})")

brief = PL.read_brief(BRIEF)
ok({"future", "relic", "human", "sense"} <= set(brief["terms"]), f"Korean brief read for theme words: {brief['terms'][:8]}")
ok(brief["outputs"] == {"html": True, "pdf": True}, "brief asks for HTML and PDF")
ledger, hyps = PL.directions(cat, brief)
ledger2, hyps2 = PL.directions(cat, brief)
ok([h["hypothesis_id"] for h in hyps] == [h["hypothesis_id"] for h in hyps2], "the same brief gives the same directions")
ok(len([h for h in hyps if h["status"] == "kept"]) >= 3, f"at least three directions to compare ({len(hyps)} drawn)")
for h in hyps:
    ops = [s["op"] for s in h["path"][1:]]
    ok(all(o in [n for n, _, _ in D.OPS] + ["intrusion"] for o in ops), f"{h['hypothesis_id']}: every step is one listed operator")
    ok(ops[D.EVERY - 1] == "intrusion", f"{h['hypothesis_id']}: intrusion at step {D.EVERY}")
    ok(all(p in ledger.nodes for s in h["path"] for p in ledger.nodes[s["id"]].get("parents", [])),
       f"{h['hypothesis_id']}: every parent is in the ledger")
    ok(h["research_sources"]["sources"], f"{h['hypothesis_id']}: traces back to sources")

plan = PL.make_plan(BRIEF, cat)
types = [p["type"] for p in plan["pages"]]
ok(not any(types[i] == types[i - 1] == types[i - 2] for i in range(2, len(types))), "no page type three times in a row")
plates = [p["plate"] for p in plan["pages"] if p.get("plate")]
ok(len(plates) == len(set(plates)), f"no plate kind printed twice: {plates}")
ok(all(p.get("purpose") for p in plan["pages"]), "every page has a stated purpose")

print("[assets]")
gen_dir = Path(임시) / "a"
gen_dir.mkdir()
f = gen_dir / "x.svg"
f.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>')
ok(A.publishable(A.generated(f, "specimen", "H")), "a generated plate on disk is publishable")
refs = A.from_sources(cat)
ok(not any(A.publishable(a) for a in refs), f"none of the {len(refs)} reference assets is publishable")
ok(not A.publishable(A.user_image(str(f), "me", "unknown")), "a user image with unknown rights is not publishable")
ok(A.publishable(A.user_image(str(f), "me", "own")), "a user image declared 'own' is publishable (declaration recorded)")
ok(not A.publishable(A.generated(gen_dir / "missing.svg", "specimen", "H")), "an asset whose file is missing is not publishable")
ok(all(not A.problems(a) for a in refs), "every reference asset carries the full metadata set")

print("[schemas]")
sch = {n: json.loads((뿌리 / "schemas" / f"{n}.schema.json").read_text()) for n in ("source", "claim", "asset", "hypothesis")}
ok(sch["asset"]["required"] == list(A.FIELDS), "asset schema lists exactly the fields the code writes")
ok(all(set(sch["claim"]["required"]) <= set(c) for c in cat["claims"]), "every claim has the schema's required fields")
ok(all(set(sch["source"]["required"]) <= set(s) for s in cat["sources"]), "every source has the schema's required fields")
ok(all(set(sch["hypothesis"]["required"]) <= set(h) for h in hyps), "every hypothesis has the schema's required fields")

print("[QA verdict]")
ok(QA.verdict([QA._c("x", "a", "PASS"), QA._c("x", "b", "NOT_CHECKED")]) == "WARNING", "NOT_CHECKED is not a pass")
ok(QA.verdict([QA._c("x", "a", "PASS"), QA._c("x", "b", "FAIL"), QA._c("x", "c", "WARNING")]) == "FAIL", "one FAIL fails the issue")

print("[no Gemini]")
pkg = 뿌리 / "gentle_monster" / "magazine"
hits = [f.name for f in pkg.glob("*.py") if re.search(r"\bimport\s+llm\b|from\s+gentle_monster\s+import[^\n]*\bllm\b|gentle_monster\.llm|generativelanguage|gemini",
                                                      f.read_text(encoding="utf-8").replace("DRIFT writes with Gemini", ""), re.I)]
ok(not hits, f"no file in gentle_monster/magazine calls Gemini or imports llm: {hits}")

print("[build]")
r = MB.build(BRIEF, name="t1")
ok("gentle_monster.llm" not in sys.modules, "importing and building the magazine never loads gentle_monster.llm (Gemini)")
out = Path(r["dir"])
ok(r["verdict"] != "FAIL", f"the real build does not FAIL QA (verdict {r['verdict']})")
for fn in ("index.html", "plan.json", "hypotheses.json", "assets.json", "qa.json", "QA_REPORT.md", "tokens.json"):
    ok((out / fn).is_file(), f"wrote {fn}")
ok(status(r["checks"], "SE_NEW Drift primary source verified") in ("PASS", "WARNING"),
   f"Drift source check ran: {status(r['checks'], 'SE_NEW Drift primary source verified')}")
html_text = (out / "index.html").read_text(encoding="utf-8")
pl = json.loads((out / "plan.json").read_text())
rendered = pl["rendered_pages"]
assets = json.loads((out / "assets.json").read_text())
plan_full = dict(pl, hypotheses=json.loads((out / "hypotheses.json").read_text()))

broken = re.sub(r'<span class="tag exp">.*?</span>', "", html_text, flags=re.S)
ok(status(QA.creative(plan_full, rendered, broken, assets), "every experiment is labelled") == "FAIL",
   "RED: removing the EXPERIMENT tags fails creative QA")
leak = copy.deepcopy(assets)
ref = next(a for a in leak if a["asset_type"] == "official_campaign")
ref.update(rights_status="licensed", verification_status="verified", local_path=str(f))
rend = copy.deepcopy(rendered)
rend[0]["assets"].append(ref["asset_id"])
ok(status(QA.creative(plan_full, rend, html_text, leak), "no reference image") == "FAIL",
   "RED: printing a brand campaign asset fails creative QA, even when marked licensed")
rend = copy.deepcopy(rendered)
next(p for p in rend if p["kind"] == "experiment" and p.get("device"))["device"] = "orbit_plate_not_chosen"
ok(status(QA.creative(plan_full, rend, html_text, assets), "experiment pages follow") == "FAIL",
   "RED: an experiment page using a device outside the chosen hypothesis fails")
ok(status(QA.creative(plan_full, rendered, html_text.replace("independent concept magazine", "magazine"), assets),
          "independence statement") == "FAIL", "RED: dropping the independence statement fails")

if PDF.available():
    ok(r["pdf_result"] and r["pdf_result"]["pages"] == r["pages"], f"PDF has one page per HTML page ({r['pdf_result'] and r['pdf_result']['pages']})")
    ok(status(r["checks"], "text overflow") == "PASS", "GREEN: no overflow at print size")
    red = out.parent / "red"
    shutil.copytree(out, red)
    h = (red / "index.html").read_text(encoding="utf-8")
    h = h.replace("<h2>Letter</h2>", "<h2>Letter</h2>" + "<p>overflow overflow overflow overflow overflow</p>" * 120, 1)
    h = h.replace("<figcaption>", "<figcaption-x>", 1)
    h = h.replace('<div class="span-12"><h2>Cross-disciplinary Research</h2>',
                  '<div class="span-12" style="width:900px;min-width:900px"><h2>Cross-disciplinary Research</h2>', 1)
    (red / "index.html").write_text(h, encoding="utf-8")
    pc = QA.production(rendered, red / "index.html", None, json.loads((out / "tokens.json").read_text()), True)
    ok(status(pc, "text overflow") == "FAIL", "RED: a page stuffed with text fails the print overflow check")
    ok(status(pc, "every figure has a caption") == "FAIL", "RED: a figure without a caption fails")
    narrow = status(pc, "no horizontal scroll or clipped content at 375")
    ok(narrow in ("FAIL", "NOT_CHECKED"), f"RED: a 900 px block is caught at 375 px (or honestly not checked): {narrow}")
    ok(status(pc, "PDF output") == "FAIL", "RED: a requested PDF that was not built fails")
else:
    print("  건너뜀  browser checks (Chromium not found)")

shutil.rmtree(임시, ignore_errors=True)
print(f"\n{'FAILED ' + str(len(FAIL)) if FAIL else 'ALL OK'}")
sys.exit(1 if FAIL else 0)
