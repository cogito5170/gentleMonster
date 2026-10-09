"""QA: research, creative, production. Each check is PASS, WARNING, FAIL or NOT_CHECKED.

NOT_CHECKED is never counted as a pass: the overall verdict is PASS only when every check is PASS.
Measurements come from the browser (pdf.measure) wherever the question is about what a reader sees.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from gentle_monster.magazine import assets as A, catalogue as CAT, drift as D, pdf as PDF

STATUSES = ("PASS", "WARNING", "FAIL", "NOT_CHECKED")


def _c(area, name, status, detail=""):
    assert status in STATUSES
    return {"area": area, "check": name, "status": status, "detail": detail}


def ko_fonts() -> list:
    """Fonts that cover Korean, asked of fontconfig. The first version of this check grepped font names for
    cjk|noto|nanum and concluded there was none -- WenQuanYi Zen Hei covers Hangul and was missed."""
    import subprocess
    try:
        p = subprocess.run(["fc-list", ":lang=ko", "family"], capture_output=True, text=True, timeout=20)
        return sorted({l.split(",")[0].strip() for l in p.stdout.splitlines() if l.strip()})
    except (OSError, subprocess.TimeoutExpired):
        return []


def research(cat: dict, drift_src: "dict | None", se_new: "Path | None" = None, check_links: bool = False) -> list:
    out = []
    bad = CAT.validate(cat)
    url_bad = [b for b in bad if "URL" in b]
    out.append(_c("research", "every source has a URL", "FAIL" if url_bad else "PASS", "; ".join(url_bad[:5])))
    out.append(_c("research", "catalogue is internally sound (kinds, citations, confidence)", "FAIL" if bad else "PASS",
                  "; ".join(bad[:6]) or f"{len(cat['sources'])} sources, {len(cat['claims'])} claims"))
    kinds = Counter(s["kind"] for s in cat["sources"])
    out.append(_c("research", "official vs secondary sources are distinguished", "PASS" if kinds.get("official") else "WARNING",
                  ", ".join(f"{k} {v}" for k, v in kinds.most_common())))
    ck = Counter(c["kind"] for c in cat["claims"])
    out.append(_c("research", "facts and interpretation are separated", "PASS" if all(c.get("kind") in CAT.KINDS for c in cat["claims"]) else "FAIL",
                  ", ".join(f"{k} {v}" for k, v in ck.most_common())))
    full = sum(CAT.claim_verification(cat, c) == "fulltext" for c in cat["claims"])
    out.append(_c("research", "sources read in full", "PASS" if full == len(cat["claims"]) else "WARNING",
                  f"{full} of {len(cat['claims'])} claims rest on a page read in full; the rest on search snippets"))
    if not drift_src:
        out.append(_c("research", "SE_NEW Drift primary source verified", "FAIL", "research/drift/se_new_drift.json missing"))
    else:
        missing, checked = [], 0
        if se_new and Path(se_new).is_dir():
            for q in drift_src.get("quotes", []):
                f = Path(se_new) / q["file"]
                if not f.is_file() or q["text"] not in f.read_text(encoding="utf-8", errors="replace"):
                    missing.append(f"{q['file']}: '{q['text'][:40]}'")
                checked += 1
            out.append(_c("research", "SE_NEW Drift primary source verified", "FAIL" if missing else "PASS",
                          "; ".join(missing) or f"{checked} quotes found verbatim in {se_new} (commit {drift_src.get('commit', '?')[:10]})"))
        else:
            out.append(_c("research", "SE_NEW Drift primary source verified", "WARNING",
                          "recorded with quotes and commit, but no se_new checkout here to re-check them (set SE_NEW_DIR)"))
    out.append(_c("research", "external source URLs reachable", "NOT_CHECKED",
                  "outbound access to the brand and magazine sites is blocked from this machine" if not check_links else ""))
    return out


def creative(plan: dict, rendered: list, html_text: str, assets: list) -> list:
    out = []
    by = {a["asset_id"]: a for a in assets}
    printed = [by[a] for r in rendered for a in r["assets"] if a in by and A.publishable(by[a])]
    foreign = [a for a in printed if a["asset_type"] in ("official_campaign", "editorial", "reference_page")]
    out.append(_c("creative", "no reference image or campaign asset is reproduced", "FAIL" if foreign else "PASS",
                  f"printed: {Counter(a['asset_type'] for a in printed)}"))
    chosen = next(h for h in plan["hypotheses"] if h["hypothesis_id"] == plan["chosen"])
    devs = {d["device"] for d in chosen["layout_implications"]}
    exp = [r for r in rendered if r["kind"] == "experiment" and r.get("device")]
    mism = [r["section"] for r in exp if r["device"] not in devs or r["hypothesis"] != chosen["hypothesis_id"]]
    out.append(_c("creative", "experiment pages follow the chosen hypothesis", "FAIL" if mism or not exp else "PASS",
                  "; ".join(mism) or f"{len(exp)} pages use {sorted({r['device'] for r in exp})}"))
    unl = []
    for r in rendered:
        if r["kind"] == "experiment":
            m = re.search(rf'<section[^>]*id="{r["id"]}".*?</section>', html_text, re.S)
            if not m or 'class="tag exp"' not in m.group(0):
                unl.append(r["section"])
    out.append(_c("creative", "every experiment is labelled as fiction", "FAIL" if unl else "PASS", "; ".join(unl)))
    try:
        for h in plan["hypotheses"]:
            for f in ("title", "transformation_rule", "intended_reader_experience", "content_implications"):
                D.guard_text(h[f])
        out.append(_c("creative", "no drift text presents fiction as brand fact", "PASS"))
    except D.ContradictionError as ex:
        out.append(_c("creative", "no drift text presents fiction as brand fact", "FAIL", str(ex)))
    rel = chosen["scores"]["brand_relevance"]
    out.append(_c("creative", "brand relevance of the chosen direction", "PASS" if rel >= 0.5 else ("WARNING" if rel >= 0.25 else "FAIL"),
                  f"{rel} (recurring brand-research words surviving the drift, /4)"))
    types = [r["type"] for r in rendered if not r["section"].startswith("References")]
    run = max(len(m.group(0)) for m in re.finditer(r"(.)\1*", "".join(chr(65 + sorted(set(types)).index(t)) for t in types)))
    top, n = Counter(types).most_common(1)[0]
    rep = "FAIL" if run >= 3 else ("WARNING" if n / len(types) > 0.35 else "PASS")
    out.append(_c("creative", "visual repetition", rep, f"longest run of one page type: {run}; most common: {top} {n}/{len(types)}"))
    kinds = Counter(by[a]["source_title"] for r in rendered for a in r["assets"] if a in by and by[a]["asset_type"] == "generated_plate")
    top_k = kinds.most_common(1)
    out.append(_c("creative", "plate kinds not repeated", "WARNING" if top_k and top_k[0][1] > 1 else "PASS",
                  ", ".join(f"{k} x{n}" for k, n in kinds.most_common())))
    uses = Counter(re.findall(r'href="#ref-(\d+)"', html_text))
    if uses:
        top_ref, k = uses.most_common(1)[0]
        frac = k / sum(uses.values())
        out.append(_c("creative", "no over-dependence on one source", "WARNING" if frac > 0.25 else "PASS",
                      f"most-cited reference [{top_ref}] carries {frac:.0%} of {sum(uses.values())} citations"))
    else:
        out.append(_c("creative", "no over-dependence on one source", "FAIL", "no citations rendered"))
    ind = html_text.count("독립 콘셉트 매거진")
    out.append(_c("creative", "independence statement on cover and colophon", "PASS" if ind >= 2 else "FAIL", f"{ind} occurrences"))
    return out


def production(rendered: list, html_path: Path, pdf_res: "dict | None", tokens: dict, want_pdf: bool) -> list:
    out = []
    html_text = Path(html_path).read_text(encoding="utf-8")
    n_html = html_text.count('<section class="page ')
    out.append(_c("production", "page count (plan / HTML)", "PASS" if n_html == len(rendered) else "FAIL", f"{len(rendered)} / {n_html}"))
    figs = re.findall(r"<figure.*?</figure>", html_text, re.S)
    nocap = [f[:60] for f in figs if "<figcaption>" not in f or "<b>" not in f]
    out.append(_c("production", "every figure has a caption and credit", "FAIL" if nocap else "PASS", f"{len(figs)} figures; {len(nocap)} without"))
    ids = set(re.findall(r'id="([^"]+)"', html_text))
    dead = sorted({h for h in re.findall(r'href="#([^"]+)"', html_text) if h not in ids})
    out.append(_c("production", "internal links resolve", "FAIL" if dead else "PASS", ", ".join(dead[:8]) or f"{html_text.count('href=\"#')} links"))
    out.append(_c("production", "external links", "NOT_CHECKED", f"{len(set(re.findall(r'href=\"(https?://[^\"]+)\"', html_text)))} URLs; network blocked"))
    cr = tokens["contrast"]
    out.append(_c("production", "text contrast (tokens)", "PASS" if cr["ink/paper"] >= 7 and cr["muted/paper"] >= 4.5 else "WARNING",
                  f"ink/paper {cr['ink/paper']}, muted/paper {cr['muted/paper']}"))

    if not PDF.available():
        for name in ("HTML renders in a browser", "text overflow at print size", "images load", "grid alignment",
                     "image ratios", "no horizontal scroll at 375 px", "no unrenderable Hangul"):
            out.append(_c("production", name, "NOT_CHECKED", "Chromium not available"))
    else:
        pr = PDF.measure(html_path, 869, 1134, "qa-print")
        mob = PDF.measure(html_path, 375, 800, "qa")
        out.append(_c("production", "HTML renders in a browser", "PASS" if pr.get("ok") and mob.get("ok") else "FAIL",
                      pr.get("error") or mob.get("error") or f"{len(pr['pages'])} pages measured"))
        if pr.get("ok"):
            over = [f"p{p['i']}({','.join(p['overflow'][:3])})" for p in pr["pages"] if p["overflow"] or p["self_scroll"]]
            out.append(_c("production", "text overflow at print size", "FAIL" if over else "PASS", "; ".join(over) or "none"))
            broken = [i["src"] for p in pr["pages"] for i in p["images"] if not i["ok"]]
            out.append(_c("production", "images load", "FAIL" if broken else "PASS", ", ".join(broken[:5]) or
                          f"{sum(len(p['images']) for p in pr['pages'])} images"))
            off = [f"p{p['i']}:{o['el']}+{o['dx']}px" for p in pr["pages"] for o in p["grid_off"]]
            out.append(_c("production", "grid alignment", "WARNING" if off else "PASS", "; ".join(off[:6]) or "all grid children on column lines"))
            bad_ratio = [f"p{p['i']}" for p in pr["pages"] for i in p["images"]
                         if i["nat"] and i["shown"] and i["fit"] != "cover" and abs(i["shown"] - i["nat"]) / i["nat"] > 0.02]
            crops = [f"p{p['i']}" for p in pr["pages"] for i in p["images"] if i["fit"] == "cover" and p["type"] != "full_bleed"]
            out.append(_c("production", "image ratios (no distortion; crops only on full-bleed)", "FAIL" if bad_ratio or crops else "PASS",
                          "; ".join(bad_ratio + crops) or "ok"))
            han = [f"p{p['i']}" for p in pr["pages"] if p["hangul"]]
            fonts = ko_fonts()
            from gentle_monster.magazine import design as DS
            ours = [f for f in fonts if f'"{f}"' in DS.KO]          # a real face from our stack, not a bitmap fallback
            out.append(_c("production", "Hangul has a font", "PASS" if ours or not han else ("WARNING" if fonts else "FAIL"),
                          f"{len(han)} pages show Hangul; from our stack: {', '.join(ours) or 'none'}"
                          + ("" if ours else f"; fallback only: {', '.join(fonts[:3]) or 'none'}")))
        if mob.get("ok"):
            vw, w, wide = mob["viewport"][0], mob["doc_scroll_w"], mob.get("too_wide", [])
            if vw != 375:   # the browser refused the size; a pass at another width says nothing about 375
                out.append(_c("production", "no horizontal scroll or clipped content at 375 px", "NOT_CHECKED",
                              f"browser gave a {vw} px viewport, not 375"))
            else:
                out.append(_c("production", "no horizontal scroll or clipped content at 375 px",
                              "PASS" if w <= vw and not wide else "FAIL",
                              f"document width {w}px" + (f"; past the edge: {', '.join(wide)}" if wide else "")))
    if not want_pdf:
        out.append(_c("production", "PDF output", "NOT_CHECKED", "not requested"))
    elif not pdf_res or not pdf_res.get("ok"):
        out.append(_c("production", "PDF output", "FAIL", (pdf_res or {}).get("error", "not built")))
    else:
        same = pdf_res["pages"] == len(rendered)
        out.append(_c("production", "PDF output", "PASS" if same else "FAIL",
                      f"{pdf_res['pages']} PDF pages for {len(rendered)} HTML pages, {pdf_res['bytes'] // 1024} KB"))
    return out


def verdict(checks: list) -> str:
    s = {c["status"] for c in checks}
    return "FAIL" if "FAIL" in s else ("PASS" if s == {"PASS"} else "WARNING")


def report_md(checks: list, title: str) -> str:
    v = verdict(checks)
    cnt = Counter(c["status"] for c in checks)
    lines = [f"# QA report -- {title}\n", f"**Overall: {v}** -- " + ", ".join(f"{k} {cnt.get(k, 0)}" for k in STATUSES) +
             ". NOT_CHECKED is not a pass.\n"]
    for area in dict.fromkeys(c["area"] for c in checks):          # every area, in the order checks were made
        lines.append(f"\n## {area.capitalize()} QA\n\n| status | check | detail |\n|---|---|---|")
        lines += [f"| {c['status']} | {c['check']} | {str(c['detail']).replace('|', '/')} |" for c in checks if c["area"] == area]
    return "\n".join(lines) + "\n"


def save(checks, out_dir, title):
    Path(out_dir, "qa.json").write_text(json.dumps({"verdict": verdict(checks), "checks": checks}, ensure_ascii=False, indent=1), encoding="utf-8")
    Path(out_dir, "QA_REPORT.md").write_text(report_md(checks, title), encoding="utf-8")
