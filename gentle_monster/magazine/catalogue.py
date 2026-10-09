"""Research catalogue: sources, claims and the comparison built on them.

A claim is one piece of evidence about one subject on one dimension. It says what kind of thing it is:
  official_statement  -- the brand / publisher says so about itself (needs an official source)
  reported_fact       -- a third party reports it as fact
  interpretation      -- someone's reading of it (a critic, us)
and how far it was read (`verification` on the source): `fulltext` (the page was read) or `snippet` (only a
search-result fragment was seen). A snippet never carries `high` confidence -- validate() says so.

Nothing here ranks brands. compare() lays claims out per subject x dimension; empty cells stay empty and are
reported as not covered, never filled.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from gentle_monster import paths

RESEARCH = paths.REPO / "research"
SOURCES = RESEARCH / "sources.json"
DRIFT_SOURCE = RESEARCH / "drift" / "se_new_drift.json"

KINDS = ("official_statement", "reported_fact", "interpretation")
SOURCE_KINDS = ("official", "press", "secondary", "blog", "retailer", "repository")
VERIFICATION = ("fulltext", "snippet")
CONFIDENCE = ("high", "medium", "low")

BRAND_DIMS = ("brand_philosophy", "product_concept", "material_language", "visual_identity", "art_direction",
              "campaign_narrative", "spatial_experience", "collaboration_strategy", "cultural_positioning")
EDITORIAL_DIMS = ("editorial_voice", "cover_strategy", "typography", "grid_system", "image_sequencing", "photography",
                  "color_system", "pacing", "long_form", "visual_essays", "caption_credit", "print_materiality")
DIMENSIONS = BRAND_DIMS + EDITORIAL_DIMS

GM_SUBJECTS = ("gentle_monster", "haus_dosan", "skp_s", "haus_nowhere")
GROUPS = {   # subject -> research group; anything unknown is 'other'
    **{s: "gentle_monster" for s in GM_SUBJECTS},
    **{s: "brands" for s in ("mykita", "jacques_marie_mage", "kuboraum", "retrosuperfuture", "maison_margiela", "prada",
                             "oakley", "celine", "tamburins", "nudake")},
    **{s: "magazines" for s in ("032c", "dazed", "the_face", "a_magazine_curated_by", "purple", "document_journal",
                                "kaleidoscope", "system", "apartamento", "pin_up")},
    "drift_studio": "disambiguation",
}

_TOK = re.compile(r"[A-Za-z][A-Za-z\-]+")
STOP = set("""a an the and or of to in on at for by with from as is are was were be been being it its this that these those
which who whom whose into than then there their they them he she his her our we you your not no but if so such can
could would should may might will also more most very just over under about after before through between each other
some any all both only own same new one two three first has have had do does did said says per via upon while where
when what how than within without among across s
january february march april may june july august september october november december year
brand official source page reported describe described describes search summary relayed according called
opened open website site say said note noted""".split())


KEEP_S = {"series", "species", "glasses", "sunglasses", "mars", "lens", "focus", "nowhere"}


def tokens(text: str) -> set[str]:
    """Content words, lower-cased, crude singular. Shared by drift (inheritance is counted on these)."""
    out = set()
    for t in _TOK.findall(text or ""):
        t = t.lower().strip("-")
        if len(t) < 3 or t in STOP:
            continue
        if t in KEEP_S:
            pass
        elif t.endswith("ies") and len(t) > 4:
            t = t[:-3] + "y"
        elif t.endswith("s") and not t.endswith(("ss", "us", "is")) and len(t) > 3:
            t = t[:-1]
        if t not in STOP:                 # 'brands' -> 'brand' must meet the stop list too
            out.add(t)
    return out


def josa(word: str, pair: str) -> str:
    """Korean particle by the last syllable: josa('기계', '을/를') -> '기계를'. '으로/로' treats ㄹ as no batchim."""
    a, b = pair.split("/")
    ch = (word or " ")[-1]
    if not ("가" <= ch <= "힣"):
        return word + b
    final = (ord(ch) - 0xAC00) % 28
    if pair == "으로/로":
        return word + (b if final in (0, 8) else a)
    return word + (a if final else b)


def load(path=None) -> dict:
    p = Path(path or SOURCES)
    cat = json.loads(p.read_text(encoding="utf-8"))
    cat.setdefault("sources", []); cat.setdefault("claims", []); cat.setdefault("not_checked", [])
    cat["_path"] = str(p)
    return cat


def load_drift(path=None) -> "dict | None":
    p = Path(path or DRIFT_SOURCE)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def by_id(cat: dict) -> dict:
    return {s["id"]: s for s in cat["sources"]}


def claim_verification(cat: dict, claim: dict) -> str:
    """A claim is as read as its best-read source."""
    src = by_id(cat)
    levels = [src[i].get("verification") for i in claim.get("source_ids", []) if i in src]
    return "fulltext" if "fulltext" in levels else ("snippet" if levels else "none")


def validate(cat: dict) -> list[str]:
    """Problems, each one line. Empty = the catalogue is internally sound (not that it is true)."""
    bad = []
    src = by_id(cat)
    for s in cat["sources"]:
        if not re.match(r"^https?://", s.get("url") or ""):
            bad.append(f"{s.get('id')}: source has no http(s) URL")
        if s.get("verification") not in VERIFICATION:
            bad.append(f"{s.get('id')}: verification must be one of {VERIFICATION}")
        if s.get("kind") not in SOURCE_KINDS:
            bad.append(f"{s.get('id')}: kind '{s.get('kind')}' not in {SOURCE_KINDS}")
    seen = set()
    for c in cat["claims"]:
        cid = c.get("id")
        if cid in seen:
            bad.append(f"{cid}: duplicate claim id")
        seen.add(cid)
        ids = c.get("source_ids") or []
        if not ids:
            bad.append(f"{cid}: claim has no source")
        for i in ids:
            if i not in src:
                bad.append(f"{cid}: cites unknown source {i}")
        if c.get("kind") not in KINDS:
            bad.append(f"{cid}: kind '{c.get('kind')}' not in {KINDS}")
        if c.get("dimension") not in DIMENSIONS:
            bad.append(f"{cid}: dimension '{c.get('dimension')}' not in the analysis axes")
        if not (c.get("evidence") or "").strip():
            bad.append(f"{cid}: empty evidence")
        if c.get("kind") == "official_statement" and not any(src.get(i, {}).get("kind") == "official" for i in ids):
            bad.append(f"{cid}: official_statement without an official source")
        if c.get("confidence") == "high" and claim_verification(cat, c) != "fulltext":
            bad.append(f"{cid}: 'high' confidence on a claim nobody read in full (snippet only)")
    return bad


def group(subject: str) -> str:
    return GROUPS.get(subject, "other")


def compare(cat: dict) -> dict:
    """subject -> dimension -> [claim ids]. Only what was found; no scores."""
    m: dict = {}
    for c in cat["claims"]:
        m.setdefault(c["subject"], {}).setdefault(c["dimension"], []).append(c["id"])
    return m


def coverage(cat: dict) -> dict:
    """Per group: subjects seen, dimensions covered, share read in full. Used to say what is NOT known."""
    out: dict = {}
    for c in cat["claims"]:
        g = out.setdefault(group(c["subject"]), {"subjects": set(), "dimensions": set(), "claims": 0, "fulltext": 0})
        g["subjects"].add(c["subject"]); g["dimensions"].add(c["dimension"]); g["claims"] += 1
        g["fulltext"] += claim_verification(cat, c) == "fulltext"
    return {k: {"subjects": sorted(v["subjects"]), "dimensions": sorted(v["dimensions"]), "claims": v["claims"],
                "fulltext_share": round(v["fulltext"] / v["claims"], 2) if v["claims"] else 0.0} for k, v in out.items()}


def principle_yield(cat: dict) -> list[dict]:
    """Saturation proxy for 'is more research still finding new principles?': in source order, how many new
    content words each further source brings to the claims. A long tail of near-zero means the current queries
    are saturated -- NOT that the field is covered (unread, paywalled and blocked sources are not in here)."""
    seen: set = set()
    rows = []
    for s in cat["sources"]:
        words = set()
        for c in cat["claims"]:
            if s["id"] in c.get("source_ids", []):
                words |= tokens(c.get("evidence", ""))
        new = words - seen
        seen |= words
        rows.append({"source": s["id"], "new_terms": len(new)})
    return rows


def markdown(cat: dict) -> dict:
    """research/*.md bodies generated from the catalogue -- evidence, kind and reading level side by side."""
    src = by_id(cat)

    def row(c):
        refs = ", ".join(f"[{i}]({src[i]['url']})" for i in c.get("source_ids", []) if i in src)
        return (f"| {c['dimension']} | {c['evidence'].replace('|', '/')} | {c['kind']} | {claim_verification(cat, c)} | "
                f"{c.get('confidence', '')} | {refs} | {(c.get('conflicts') or '').replace('|', '/')} |")

    head = "| dimension | evidence | kind | read | confidence | source | conflicts |\n|---|---|---|---|---|---|---|"
    docs = {}
    for grp, folder in (("gentle_monster", "gentle_monster"), ("brands", "brands"), ("magazines", "magazines"),
                        ("disambiguation", "drift"), ("other", "brands")):
        subs = sorted({c["subject"] for c in cat["claims"] if group(c["subject"]) == grp})
        if not subs:
            continue
        parts = [f"# {grp.replace('_', ' ').title()} -- evidence table\n",
                 "Generated by `python3 -m gentle_monster research` from `research/sources.json`. Do not edit by hand.\n",
                 "`read` = how far the source was read: `fulltext` (page read) or `snippet` (search fragment only). "
                 "`kind` separates what the subject says about itself (official_statement) from what others report "
                 "(reported_fact) and readings (interpretation).\n"]
        for s in subs:
            parts.append(f"\n## {s}\n\n{head}")
            parts += [row(c) for c in cat["claims"] if c["subject"] == s]
        name = "evidence.md" if grp != "disambiguation" else "drift_studio_disambiguation.md"
        docs[f"{folder}/{name}" if grp != "other" else "brands/other_evidence.md"] = "\n".join(parts) + "\n"
    m = compare(cat)
    cov = coverage(cat)
    dims_brand = [d for d in BRAND_DIMS]
    lines = ["# Comparative analysis -- subject x dimension\n",
             "Cells count claims found; `.` = nothing found (not 'absent' -- just not found). No scores, no ranking: "
             "a brand close to Gentle Monster on product can be far on space, so compare per purpose.\n"]
    for title, dims in (("Brand dimensions", dims_brand), ("Editorial dimensions", list(EDITORIAL_DIMS))):
        lines.append(f"\n## {title}\n\n| subject | " + " | ".join(d.replace("_", " ") for d in dims) + " |\n|---|" + "---|" * len(dims))
        for s in sorted(m):
            if any(m[s].get(d) for d in dims):
                lines.append(f"| {s} | " + " | ".join(str(len(m[s].get(d, []))) if m[s].get(d) else "." for d in dims) + " |")
    lines.append("\n## Coverage by group\n")
    for g, v in sorted(cov.items()):
        lines.append(f"- **{g}**: {v['claims']} claims, {len(v['subjects'])} subjects, {len(v['dimensions'])} dimensions, "
                     f"read in full {int(v['fulltext_share'] * 100)}%")
    py = principle_yield(cat)
    tail = py[-5:]
    lines.append("\n## Saturation (new content words per further source, in catalogue order)\n")
    lines.append("Last five sources: " + ", ".join(f"{r['source']} +{r['new_terms']}" for r in tail) +
                 ". A tail near zero would mean these queries are saturated, not that the field is covered.")
    lines.append("\n## Not checked\n")
    lines += [f"- {x}" for x in cat.get("not_checked", [])] or ["- (none recorded)"]
    docs["comparative_analysis/matrix.md"] = "\n".join(lines) + "\n"
    return docs
