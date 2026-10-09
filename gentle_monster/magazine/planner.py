"""Brief -> directions -> one chosen -> page-by-page editorial plan. No model call.

    plan = make_plan("Gentle Monster의 브랜드 세계관을 중심으로, 미래의 유물과 인간의 감각을 ...", cat)

1. The brief is read for theme words (Korean or English, small fixed lexicon) and requested outputs.
2. At least three Gentle Monster research nodes closest to the theme seed three Drift walks (drift.walk).
3. Each walk becomes a design hypothesis; they are compared on the seven criteria and one is chosen. The
   comparison, including the losers and why, goes into the plan and onto a page.
4. Pages: every section has a stated purpose; facts come from claims (cited), experiments are labelled as such.
"""
from __future__ import annotations

import hashlib
import re

from gentle_monster.magazine import catalogue as CAT, drift as D

THEMES = {
    "미래": ["future"], "유물": ["relic", "artifact"], "인간": ["human"], "사람": ["human"], "감각": ["sense", "touch", "sight"],
    "시각": ["sight", "vision"], "촉각": ["touch"], "기억": ["memory"], "공간": ["space"], "빛": ["light"], "어둠": ["dark"],
    "기계": ["machine"], "로봇": ["robot", "machine"], "고고학": ["excavation", "relic"], "박물관": ["archive", "conservation"],
    "실험": ["experiment"], "노스탤지어": ["nostalgia"], "향수": ["nostalgia"], "화성": ["mars", "planet"], "시간": ["time"],
    "재료": ["material"], "소재": ["material"], "몸": ["body"], "소리": ["sound"], "자연": ["nature"], "동물": ["animal"],
    "도시": ["city"], "꿈": ["dream"], "분실": ["lost"], "잃어버린": ["lost"], "관찰": ["observation"], "우주": ["planet", "space"],
    "패션": ["fashion"], "예술": ["art"], "아이웨어": ["eyewear"], "안경": ["eyewear", "glasses"], "선글라스": ["sunglasses", "eyewear"],
}
OBJECTS = {"향수병": "fragrance", "향": "fragrance", "디저트": "dessert", "안경": "eyewear", "eyewear": "eyewear"}
N_DIRECTIONS = 4
STEPS = 6
RETRIES = 3      # re-drifts allowed when a walk lands on a reading another direction already has
WEIGHTS = {"source_traceability": 1.0, "brand_relevance": 1.0, "editorial_coherence": 1.0, "feasibility": 1.0,
           "visual_originality": 1.0, "conceptual_distance": 0.5}


def read_brief(text: str) -> dict:
    t = text or ""
    terms = set()
    for k, v in THEMES.items():
        if k in t:
            terms |= set(v)
    terms |= CAT.tokens(t) - D.SUBJECT_NAMES - {"magazine", "brand", "make", "create", "please", "using", "real", "image",
                                                 "source", "related", "html", "pdf", "web", "print", "drift", "method"}
    want_pdf = bool(re.search(r"pdf|인쇄|print", t, re.I))
    want_html = bool(re.search(r"html|웹|web|사이트", t, re.I))
    if not (want_pdf or want_html):
        want_pdf = want_html = True
    obj = next((v for k, v in OBJECTS.items() if k in t.lower() and v != "eyewear"), "eyewear")
    themes_ko = [k for k in THEMES if k in t]
    return {"text": t, "terms": sorted(terms), "themes_ko": themes_ko, "outputs": {"html": want_html or want_pdf, "pdf": want_pdf}, "object": obj,
            "seed": hashlib.sha256(t.encode()).hexdigest()[:12]}


def _seeds(ledger: D.Ledger, brief: set, n: int) -> list:
    gm = [x for x in (ledger.nodes[i] for i in ledger.order) if x["origin"] == "claim" and x["subject"] in CAT.GM_SUBJECTS]
    def affinity(x):
        t = set(x["terms"])
        dom = max(len(t & d["terms"]) for d in D.DOMAINS)
        return (len(t & brief) * 3 + dom, x["id"])
    gm.sort(key=affinity, reverse=True)
    out, subj = [], []
    for x in gm:                                      # spread across subjects before doubling up on one
        if x["subject"] not in subj or len(out) >= len({g["subject"] for g in gm}):
            out.append(x); subj.append(x["subject"])
        if len(out) == n:
            break
    for x in gm:
        if len(out) == n:
            break
        if x not in out:
            out.append(x)
    return out


def total(h: dict) -> float:
    return round(sum(WEIGHTS[k] * (h["scores"].get(k) or 0) for k in WEIGHTS), 3)


def directions(cat: dict, brief: dict, n: int = N_DIRECTIONS) -> tuple[D.Ledger, list]:
    ledger = D.Ledger()
    bt = set(brief["terms"])
    D.seed_nodes(cat, ledger, bt)
    seeds = _seeds(ledger, bt, n)
    if len(seeds) < 3:
        raise ValueError(f"only {len(seeds)} Gentle Monster research nodes -- need 3 to compare directions")
    hyps, taken = [], set()
    for i, s in enumerate(seeds):
        others = [o for o in seeds if o is not s]
        for k in range(RETRIES + 1):                 # a walk that ends in a reading already taken drifts again
            path = D.walk(ledger, s, f"{brief['seed']}:{i}" + (f":r{k}" if k else ""), bt, steps=STEPS, others=others)
            h = D.hypothesis(ledger, path, cat, brief["object"])
            if h["title"] not in taken:
                break
        h["attempts"] = k + 1
        taken.add(h["title"])
        hyps.append(h)
    D.originality(hyps)
    seen = {}
    for h in hyps:                                    # two walks that ended in the same reading are one direction
        seen.setdefault(h["title"], []).append(h)
    for title, hs in seen.items():
        for dup in hs[1:]:
            dup["status"], dup["excluded_because"] = "excluded", f"same reading as {hs[0]['hypothesis_id']}"
    for h in hyps:
        h["total"] = total(h)
        sc = {k: v for k, v in h["scores"].items() if v is not None}
        h["strength"] = max(sc, key=sc.get)
        h["weakness"] = min(sc, key=sc.get)
    return ledger, hyps


def choose(hyps: list) -> dict:
    kept = [h for h in hyps if h["status"] == "kept"]
    if not kept:
        raise ValueError("every direction was excluded -- see excluded_because on each")
    return sorted(kept, key=lambda h: (h["total"], h["hypothesis_id"]), reverse=True)[0]


def _claims(cat, pred, limit=6):
    return [c for c in cat["claims"] if pred(c)][:limit]


def pages(cat: dict, brief: dict, chosen: dict, hyps: list) -> list:
    """Page-by-page plan. Each page: type, section, purpose, kind (fact | experiment | apparatus), claims, plate."""
    gm = lambda c: c["subject"] in CAT.GM_SUBJECTS
    space = lambda c: c["subject"] in ("haus_dosan", "skp_s", "haus_nowhere") or c["dimension"] == "spatial_experience"
    prod = lambda c: gm(c) and c["dimension"] in ("product_concept", "material_language", "visual_identity", "collaboration_strategy")
    other = lambda c: CAT.group(c["subject"]) in ("brands", "magazines")
    devs = chosen["layout_implications"]
    plate_of = lambda dev: D.DEVICES[dev][2]
    P = [
        {"section": "Cover", "type": "cover", "kind": "apparatus", "purpose": "name the issue and its question; say it is an independent concept",
         "plate": plate_of(devs[0]["device"]) or "specimen"},
        {"section": "Contents", "type": "contents", "kind": "apparatus", "purpose": "the order of the issue: features first, apparatus at the back"},
        {"section": "Editor's Letter", "type": "single_column", "kind": "apparatus",
         "purpose": "state the brief, the method, and which pages are fact and which are experiment"},
        {"section": "Brand and Culture", "type": "multi_column", "kind": "fact",
         "purpose": "what Gentle Monster says about itself vs what others report -- kept apart",
         "claims": [c["id"] for c in _claims(cat, lambda c: gm(c) and not space(c), 8)]},
        {"section": "Spatial Experiments", "type": "asymmetric", "kind": "fact", "plate": "site_grid" if "site_grid" not in [plate_of(d["device"]) for d in devs] else "strata",
         "purpose": "the stores as staged worlds: floors, installations, machines", "claims": [c["id"] for c in _claims(cat, lambda c: gm(c) and space(c), 7)]},
        {"section": "Eyewear as Object", "type": "product_study", "kind": "fact", "plate": "exploded",
         "purpose": "the product as a made object -- what the sources say about it", "claims": [c["id"] for c in _claims(cat, prod, 5)]},
    ]
    for i, d in enumerate(devs[:3]):
        P.append({"section": f"Drift Experiment {i + 1}", "type": d["page_type"], "kind": "experiment", "device": d["device"],
                  "plate": plate_of(d["device"]), "hypothesis": chosen["hypothesis_id"],
                  "purpose": f"{chosen['title']}: {d['label']}"})
        if i == 1 and chosen.get("intrusions"):
            x = chosen["intrusions"][0]
            P.append({"section": "Intrusion", "type": "intrusion", "kind": "experiment", "hypothesis": chosen["hypothesis_id"],
                      "purpose": f"break the escalation: {x['who']} {x['how']}", "intrusion": x})
    P += [
        {"section": "Cross-disciplinary Research", "type": "multi_column", "kind": "fact",
         "purpose": "principles found in other brands and magazines -- as principles, not as looks to copy",
         "claims": [c["id"] for c in _claims(cat, other, 12)]},
        {"section": "Directions Not Taken", "type": "catalogue", "kind": "apparatus",
         "purpose": "the other drift directions and why this one was chosen", "hypotheses": [h["hypothesis_id"] for h in hyps]},
        {"section": "Image Catalogue", "type": "catalogue", "kind": "apparatus",
         "purpose": "every image and reference with its rights status -- printed or withheld"},
        {"section": "Critical Review", "type": "single_column", "kind": "apparatus",
         "purpose": "what this issue could not verify, and the risks of the chosen direction"},
        {"section": "References", "type": "references", "kind": "apparatus", "purpose": "every source, with how far it was read"},
        {"section": "Colophon", "type": "colophon", "kind": "apparatus", "purpose": "method, tools, independence statement"},
    ]
    _rhythm(P)
    _plates(P)
    back = False
    for p in P:
        p["title_ko"] = TITLE_KO.get(p["section"]) or p["section"].replace("Drift Experiment", "표류 실험")
        back = back or p["section"] == "Directions Not Taken"
        p["part"] = "부록" if back else ("앞" if p["type"] in ("cover", "contents") else "본문")
    for i, p in enumerate(P, 1):
        p["folio"] = i
    return P


TITLE_KO = {"Cover": "표지", "Contents": "차례", "Editor's Letter": "편집자의 글", "Brand and Culture": "브랜드와 문화",
            "Spatial Experiments": "공간의 실험", "Eyewear as Object": "사물로서의 안경", "Intrusion": "끼어들기",
            "Cross-disciplinary Research": "다른 분야에서 온 원리", "Directions Not Taken": "가지 않은 방향",
            "Image Catalogue": "이미지 목록", "Critical Review": "비평 — 확인하지 못한 것", "References": "참고 문헌",
            "Colophon": "판권"}
PLATE_FALLBACK = ("material", "cue", "strata", "site_grid", "exploded", "acuity", "orbit", "specimen")


def _plates(P: list) -> None:
    """One plate kind per issue where possible: a device that asks for a kind already printed gets the next
    unused kind, and the plan says so (plate_requested). The cover takes what is left last."""
    used: dict = {}
    for p in [q for q in P if q["type"] != "cover"] + [q for q in P if q["type"] == "cover"]:
        k = p.get("plate")
        if not k:
            continue
        if used.get(k):
            alt = next((f for f in PLATE_FALLBACK if not used.get(f)), None)
            if alt:
                p["plate_requested"], p["plate"] = k, alt
        used[p["plate"]] = used.get(p["plate"], 0) + 1


def _rhythm(P: list) -> None:
    """No page type three times in a row; experiments not glued to the same type as the page before.
    Moves a later page forward rather than inventing one."""
    for i in range(2, len(P)):
        if P[i]["type"] == P[i - 1]["type"] == P[i - 2]["type"]:
            for j in range(i + 1, len(P) - 3):
                if P[j]["type"] != P[i]["type"] and P[j]["kind"] == P[i]["kind"]:
                    P[i], P[j] = P[j], P[i]
                    break


def make_plan(text: str, cat: dict) -> dict:
    brief = read_brief(text)
    ledger, hyps = directions(cat, brief)
    chosen = choose(hyps)
    return {"brief": brief, "hypotheses": hyps, "chosen": chosen["hypothesis_id"], "pages": pages(cat, brief, chosen, hyps),
            "ledger_size": len(ledger.nodes)}
