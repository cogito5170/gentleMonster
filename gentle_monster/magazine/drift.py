"""Drift -- the SE_NEW DRIFT rules carried over from prose to editorial concepts.

The source is not a guess. It is in the se_new repository (novel/DRIFT.md, novel/shock.py, novel/diffusion.py,
mathdrift/README.md, mathdrift/measure.py, mathdrift/ops.py) and is recorded with commit and quotes in
research/drift/se_new_drift.json. What carries over, rule by rule:

  ledger (원장)            every concept is a node; once placed it stays true. A child must name a parent that
                           is already in the ledger -- add() refuses a broken lineage (mathdrift: space.add()).
  one operator per step    a step applies exactly one operator from a fixed list (mathdrift: Evol-Instruct rule);
                           far jumps are rare (JUMP_SHARE, same value as mathdrift).
  conservative extension   a step keeps part of its parent and adds something new. Both are MEASURED (new terms,
                           kept terms, share of the parent kept; kept >= 2 words -- one shared word is not
                           inheritance) and reported, never used to kill a step ("재서 돌려주되 죽이지 않는다").
  cold props (식은 소품)   a node not touched in the last steps but not too old is brought back (revive).
  intrusion (충격)         every EVERY steps a third party breaks the escalation -- drawn from axes
                           WHO x HOW x MARK, seeded, so a rerun gives the same sequence. It never solves
                           anything: it opens a question.
  two hard gates only      lineage (above) and non-contradiction. Here non-contradiction means: generated text
                           may not present a fiction as a fact about the brand (no "Gentle Monster announced ...").
                           Everything else is measured and left to the editor.

What is NOT carried over: the prose model. DRIFT writes with Gemini; this engine writes no prose at all --
its outputs are structured hypotheses whose text is composed from the ledger. That is a limit, not a feature.
"""
from __future__ import annotations

import hashlib
import re

from gentle_monster.magazine import catalogue as CAT

EVERY = 4            # intrusion after this many steps (DRIFT: ~2,000 chars; one step here ~ one concept move)
JUMP_SHARE = 0.2     # mathdrift.ops.JUMP_SHARE
KEEP_MIN = 2         # mathdrift.measure.KEEP_MIN -- one shared word is not inheritance
KEEP_SHARE = 0.10    # mathdrift.measure.KEEP_SHARE
FUEL_AGE = 8         # novel/diffusion.FUEL_AGE -- older than this, going back is regression
CARRY = 6            # parent terms a child carries forward (oldest first, so the seed's words survive)

# (name, what it does, distance)
OPS = [
    ("detach", "drop the subject's names; keep the working principle", 1),
    ("refine", "narrow to one facet of the parent (material / form / space / sequence)", 1),
    ("associate", "join the nearest outside discipline that already shares words with the parent", 1),
    ("invert", "turn the parent's main term into its opposite", 1),
    ("revive", "bring back a cooling node: not used in the last steps, not too old", 1),
    ("fold", "join two separately grown branches; what they share becomes the rule", 2),
    ("leap", "join a far discipline that shares almost nothing with the parent", 2),
]
NEAR = [n for n, _, d in OPS if d == 1]
JUMP = [n for n, _, d in OPS if d >= 2]

FACET = {"brand_philosophy": "concept", "product_concept": "form", "material_language": "material",
         "visual_identity": "form", "art_direction": "mood", "campaign_narrative": "narrative",
         "spatial_experience": "space", "collaboration_strategy": "concept", "cultural_positioning": "concept"}
FACET_WORDS = {"material": {"material", "surface", "acetate", "metal", "texture"},
               "form": {"form", "silhouette", "outline", "proportion"},
               "space": {"space", "room", "floor", "threshold"},
               "sequence": {"sequence", "order", "rhythm", "series"}}
SUBJECT_NAMES = {"gentle", "monster", "haus", "dosan", "skp", "nowhere", "tamburin", "nudake", "mykita", "kuboraum",
                 "dazed", "032c", "purple", "apartamento", "kaleidoscope", "seoul", "beijing", "shanghai", "london"}
OPPOSITES = {"future": "relic", "relic": "future", "digital": "analog", "analog": "digital", "human": "machine",
             "machine": "human", "robot": "human", "wear": "specimen", "eyewear": "specimen", "retail": "archive",
             "store": "archive", "shop": "archive", "motion": "stillness", "moving": "still", "light": "dark",
             "dark": "light", "new": "worn", "sight": "touch", "vision": "touch", "visible": "hidden",
             "product": "artifact", "nostalgia": "forecast", "experiment": "record", "experience": "record",
             "installation": "inventory", "art": "evidence", "space": "surface", "fantasy": "survey",
             "sense": "measurement", "memory": "forecast", "luxury": "salvage"}

# Outside disciplines. Each one is a way of *documenting* things -- that is what makes it editorial.
DOMAINS = [
    {"name": "archaeological excavation", "reads_as": "an excavation find", "subject": "finds",
     "terms": {"relic", "artifact", "layer", "stratum", "find", "excavation", "site", "past", "future", "object", "record", "ruin", "time"},
     "devices": ["find_number", "site_grid", "scale_bar"],
     "experience": "the reader handles today's products as if dug up later -- time is read backwards",
     "image": "objects isolated on neutral ground at 1:1, a scale bar in every plate; one site plan per section",
     "type": "monospaced find numbers; a quiet serif for field notes; captions longer than headlines",
     "content": "find records (number, layer, condition, inferred use) next to sourced facts about the real object",
     "palette": {"paper": "#e9e4da", "ink": "#1d1b18", "accent": "#9c3d1c"}},
    {"name": "museum conservation", "reads_as": "an object under conservation", "subject": "objects in care",
     "terms": {"condition", "conservation", "fragment", "restoration", "damage", "care", "material", "surface", "archive", "object", "artifact"},
     "devices": ["condition_table", "before_after", "material_swatch"],
     "experience": "slowness: the reader looks at wear, repair and surface instead of novelty",
     "image": "raking-light macro of surfaces; paired states of the same object",
     "type": "tabular condition reports; small caps for status words",
     "content": "condition reports, material notes, what would be lost if the object were cleaned",
     "palette": {"paper": "#f1f0ec", "ink": "#22252a", "accent": "#3f6b5c"}},
    {"name": "industrial maintenance", "reads_as": "a machine on a service log", "subject": "machines",
     "terms": {"machine", "robot", "maintenance", "service", "part", "wear", "inspection", "interval", "technology", "motion", "engine", "repair"},
     "devices": ["exploded_parts", "log_column", "cue_sheet"],
     "experience": "the reader sees the object as a mechanism with a life cycle, not an image",
     "image": "exploded part drawings; timestamped stills of moving parts",
     "type": "condensed sans for part codes; log entries in a narrow column",
     "content": "service intervals, part lists, failure notes -- for installations that move",
     "palette": {"paper": "#e6e8e8", "ink": "#16191c", "accent": "#d44b1f"}},
    {"name": "optometry", "reads_as": "an eye examination", "subject": "eyes",
     "terms": {"sight", "vision", "eye", "lens", "acuity", "test", "chart", "sense", "human", "measurement", "eyewear", "glasses"},
     "devices": ["acuity_chart", "scale_bar", "typographic_test"],
     "experience": "the page tests the reader's eyes -- reading itself becomes the subject",
     "image": "letters as images; a few photographs printed deliberately small",
     "type": "type sizes stepping down by a fixed ratio like an acuity chart",
     "content": "what seeing is, measured; the frame as an instrument before it is an accessory",
     "palette": {"paper": "#f4f4f1", "ink": "#101010", "accent": "#c21f3a"}},
    {"name": "geological survey", "reads_as": "a core sample", "subject": "ground",
     "terms": {"layer", "stratum", "core", "ground", "survey", "depth", "time", "material", "floor", "concrete", "space", "building"},
     "devices": ["strata_column", "site_grid", "log_column"],
     "experience": "a building read vertically, floor by floor, like sediment",
     "image": "vertical sections; one long image cut across several pages",
     "type": "depth markers in the margin; section titles as layer names",
     "content": "a store's floors described as layers deposited in time",
     "palette": {"paper": "#ece6dc", "ink": "#2a2620", "accent": "#7a5a2e"}},
    {"name": "theatre prompt book", "reads_as": "a staged scene", "subject": "scenes",
     "terms": {"stage", "scene", "cue", "light", "performance", "theatrical", "narrative", "audience", "space", "installation", "story", "experience"},
     "devices": ["cue_sheet", "blocking_plan", "full_bleed_scene"],
     "experience": "the reader moves through spreads as an audience through cues",
     "image": "wide establishing frames followed by close details, numbered as cues",
     "type": "cue numbers set large in the margin; stage directions in italics",
     "content": "an installation narrated as a sequence of cues: light, sound, movement",
     "palette": {"paper": "#141414", "ink": "#eeeae2", "accent": "#e3b341"}},
    {"name": "auction cataloguing", "reads_as": "a lot in a sale", "subject": "lots",
     "terms": {"lot", "provenance", "estimate", "collection", "luxury", "object", "collaboration", "artist", "value", "edition", "catalogue"},
     "devices": ["lot_entry", "provenance_list", "scale_bar"],
     "experience": "the reader weighs where an object came from before what it looks like",
     "image": "frontal object photographs on one background, numbered",
     "type": "lot numbers, small italic provenance lines, generous margins",
     "content": "provenance chains -- who made, who collaborated, where it was shown",
     "palette": {"paper": "#fbfaf7", "ink": "#1b1b1b", "accent": "#5a4bb0"}},
    {"name": "astronomical observation", "reads_as": "an observation log", "subject": "distant bodies",
     "terms": {"mars", "planet", "orbit", "observation", "distance", "future", "space", "light", "dark", "signal", "wormhole", "telescope"},
     "devices": ["orbit_plate", "log_column", "acuity_chart"],
     "experience": "distance: the object is far away and only partly visible",
     "image": "dark fields with small bright subjects; diagrams of orbits",
     "type": "coordinates and timestamps; light text on dark pages",
     "content": "the future-as-elsewhere theme handled as observation, not fantasy",
     "palette": {"paper": "#0d0f14", "ink": "#e7e9ee", "accent": "#e86a3a"}},
    {"name": "natural-history field guide", "reads_as": "a species plate", "subject": "species",
     "terms": {"species", "specimen", "nature", "animal", "sheep", "farm", "plant", "habitat", "field", "guide", "creature", "living"},
     "devices": ["specimen_plate", "find_number", "material_swatch"],
     "experience": "classification: the reader learns to tell similar things apart",
     "image": "many small specimens on one plate, each numbered",
     "type": "Latin-style binomials for frame families; index-like captions",
     "content": "frame families described as species: traits, habitat, near relatives",
     "palette": {"paper": "#efeadf", "ink": "#23261f", "accent": "#55703a"}},
    {"name": "patent drafting", "reads_as": "an invention disclosure", "subject": "inventions",
     "terms": {"invention", "claim", "figure", "mechanism", "design", "product", "hinge", "structure", "technology", "innovation", "form"},
     "devices": ["exploded_parts", "numbered_figures", "claims_list"],
     "experience": "precision: every part has a number and a reason",
     "image": "line drawings only, numbered parts with leader lines",
     "type": "numbered claims; figure labels in caps",
     "content": "what is new about a design, stated as claims, separate from what is shown",
     "palette": {"paper": "#ffffff", "ink": "#111111", "accent": "#1f4fc2"}},
    {"name": "lost-property office", "reads_as": "an unclaimed item", "subject": "lost things",
     "terms": {"lost", "tag", "owner", "found", "memory", "nostalgia", "personal", "everyday", "trace", "time", "forgotten"},
     "devices": ["tag_entry", "find_number", "blank_page"],
     "experience": "absence: the owner is missing and the reader fills the gap",
     "image": "objects alone, slightly off-centre, with a paper tag",
     "type": "handwritten-style labels are avoided; plain typewriter-like tags",
     "content": "short notes on where an object was found and what it suggests about its wearer",
     "palette": {"paper": "#e7e2d3", "ink": "#2b2a26", "accent": "#b5452b"}},
    {"name": "film continuity", "reads_as": "a continuity report", "subject": "takes",
     "terms": {"film", "frame", "sequence", "shot", "continuity", "campaign", "image", "motion", "scene", "video", "time"},
     "devices": ["contact_sheet", "cue_sheet", "log_column"],
     "experience": "sequence over single image: the reader compares frames for what changed",
     "image": "contact sheets; the same frame repeated with one change",
     "type": "timecodes; frame numbers on every image",
     "content": "a campaign read as takes: what stayed, what moved",
     "palette": {"paper": "#f2efe8", "ink": "#1a1a1a", "accent": "#2c7a7b"}},
]

for _d in DOMAINS:   # the same tokeniser as the evidence, so 'glasses' and 'Mars' meet their evidence spelling
    _d["terms"] = CAT.tokens(" ".join(_d["terms"]))

DEVICES = {   # device -> (label, page type, plate kind or None)
    "find_number": ("find number + layer in every caption", "catalogue", "specimen"),
    "site_grid": ("grid-square site plan", "full_bleed", "site_grid"),
    "scale_bar": ("object at stated scale with a scale bar", "product_study", "specimen"),
    "condition_table": ("condition report table", "multi_column", None),
    "before_after": ("paired states of one object", "image_essay", "material"),
    "material_swatch": ("material swatches as evidence", "image_essay", "material"),
    "exploded_parts": ("exploded part drawing", "product_study", "exploded"),
    "log_column": ("timestamped log column", "multi_column", None),
    "cue_sheet": ("numbered cues", "asymmetric", "cue"),
    "acuity_chart": ("type stepping down like an acuity chart", "typographic", "acuity"),
    "typographic_test": ("reading test spread", "typographic", "acuity"),
    "strata_column": ("vertical layer section", "asymmetric", "strata"),
    "blocking_plan": ("blocking plan of a space", "full_bleed", "site_grid"),
    "full_bleed_scene": ("full-bleed establishing scene", "full_bleed", "orbit"),
    "lot_entry": ("lot entries with provenance", "catalogue", "specimen"),
    "provenance_list": ("provenance chain", "single_column", None),
    "orbit_plate": ("orbit diagram", "full_bleed", "orbit"),
    "specimen_plate": ("specimen plate of many small objects", "catalogue", "specimen"),
    "numbered_figures": ("numbered figures with leader lines", "product_study", "exploded"),
    "claims_list": ("numbered claims", "single_column", None),
    "tag_entry": ("tag-style entries", "catalogue", "specimen"),
    "blank_page": ("a deliberately empty page with one line", "typographic", None),
    "contact_sheet": ("contact sheet", "image_essay", "cue"),
}

# Intrusion axes (novel/shock.py WHO x HOW x MARK, re-cast for a magazine). Everything here could really happen.
WHO = ("a conservator", "a customs inspector", "a child", "a sorting machine", "an archivist from later",
       "the building itself", "a misdelivered parcel", "a translator", "the weather", "a stranger's margin note",
       "an insurance assessor", "a night guard", "a printer's error", "a visitor who stayed too long")
HOW = ("re-measures everything", "misfiles one object", "annotates the margin", "turns the lights off",
       "relabels by weight", "removes the captions", "enlarges one detail", "counts instead of describing",
       "reads the reverse side", "asks who owned it", "puts two objects in one box", "stops the sequence halfway")
MARK = ("a blank page with one number", "an outline where an object was", "a corrected caption",
        "a tag with no object", "one detail enlarged past recognition", "a list with no images",
        "a question nobody on the page answers", "a page set in the wrong order")

FICTION_AS_FACT = re.compile(r"\b(gentle\s*monster|gm)\b[^.]{0,40}\b(announced|launched|said|says|stated|confirmed|"
                             r"presents|released|commissioned|partnered|endorsed|official(ly)?)\b", re.I)


class LineageError(ValueError):
    pass


class ContradictionError(ValueError):
    pass


def _h(seed: str, *parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, (seed, *parts))).encode()).digest()[:8], "big")


def draw_op(seed: str, n: int) -> str:
    """Seed-bound draw: same (seed, n) -> same operator, so a rerun reproduces the walk."""
    if _h(seed, n, "jump") % 1000 < JUMP_SHARE * 1000:
        return JUMP[_h(seed, n, "j") % len(JUMP)]
    return NEAR[_h(seed, n, "n") % len(NEAR)]


def draw_intrusion(seed: str, n: int) -> dict:
    return {"who": WHO[_h(seed, n, "who") % len(WHO)], "how": HOW[_h(seed, n, "how") % len(HOW)],
            "mark": MARK[_h(seed, n, "mark") % len(MARK)]}


def measure(child_terms, parent_terms) -> dict:
    """mathdrift.measure on concept terms: new, kept, share of the PARENT kept. Observation, not a verdict."""
    c, p = set(child_terms), set(parent_terms)
    if not p:
        return {"new": len(c), "kept": 0, "share": 0.0, "diffusion": False, "seed": True}
    new, kept = len(c - p), len(c & p)
    share = round(kept / len(p), 3)
    return {"new": new, "kept": kept, "share": share,
            "diffusion": bool(new and kept >= KEEP_MIN and share >= KEEP_SHARE), "seed": False}


class Ledger:
    """원장. Nodes are only ever added. A node's parents must already be here."""

    def __init__(self):
        self.nodes: dict = {}
        self.order: list = []
        self.used_at: dict = {}

    def add(self, node: dict, step: int = 0) -> dict:
        for p in node.get("parents", []):
            if p not in self.nodes:
                raise LineageError(f"{node['id']}: parent {p} is not in the ledger -- lineage broken")
        if node["id"] in self.nodes:
            return self.nodes[node["id"]]
        node.setdefault("born", step)
        node["terms"] = sorted(set(node["terms"]))
        self.nodes[node["id"]] = node
        self.order.append(node["id"])
        return node

    def touch(self, nid: str, step: int):
        self.used_at[nid] = step

    def cold(self, now: int, recent: set, keep: int = 12) -> list:
        """식은 소품: not touched in the recent steps, and not older than FUEL_AGE."""
        out = []
        for nid in self.order:
            n = self.nodes[nid]
            if nid in recent or n["origin"] in ("intrusion",):
                continue
            if now - n.get("born", 0) > FUEL_AGE and n["origin"] != "claim":
                continue
            if now - self.used_at.get(nid, n.get("born", 0)) >= 2:
                out.append(nid)
        return out[-keep:]

    def ancestry(self, nid: str) -> list:
        seen, todo = [], [nid]
        while todo:
            x = todo.pop()
            if x in seen:
                continue
            seen.append(x)
            todo += self.nodes[x].get("parents", [])
        return seen


def seed_nodes(cat: dict, ledger: Ledger, brief_terms: set) -> list:
    """One node per brand-dimension claim (editorial-dimension claims feed the planner, not the walk)."""
    out = []
    for c in cat["claims"]:
        if c.get("dimension") not in FACET:
            continue
        terms = CAT.tokens(c.get("evidence", "")) | {c["dimension"].split("_")[0]}
        n = ledger.add({"id": f"C:{c['id']}", "origin": "claim", "label": c["evidence"][:90], "terms": terms,
                        "facet": FACET[c["dimension"]], "claims": [c["id"]], "subject": c["subject"], "parents": []})
        out.append(n)
    if brief_terms:
        ledger.add({"id": "B:brief", "origin": "brief", "label": "the brief", "terms": set(brief_terms), "facet": "concept",
                    "claims": [], "subject": "brief", "parents": []})
    return out


def _carry(ledger: Ledger, parent: dict) -> list:
    """Parent terms in order of first appearance along the lineage -- the seed's words go first and survive."""
    first: dict = {}
    for nid in reversed(ledger.ancestry(parent["id"])):
        for t in ledger.nodes[nid]["terms"]:
            first.setdefault(t, ledger.nodes[nid].get("born", 0))
    return sorted(parent["terms"], key=lambda t: (first.get(t, 99), t))[:CARRY]


def _domain(parent_terms: set, brief: set, used: set, far: bool, seed: str, n: int) -> dict:
    cand = [d for d in DOMAINS if d["name"] not in used] or DOMAINS
    def near(d):
        return len(d["terms"] & parent_terms) * 2 + len(d["terms"] & brief)
    ranked = sorted(cand, key=lambda d: (near(d), _h(seed, n, d["name"]) % 97), reverse=not far)
    return ranked[0]


def step(ledger: Ledger, parent: dict, op: str, n: int, seed: str, brief: set, used: set, others: list) -> dict:
    """Apply exactly one operator. Returns the child node (already in the ledger)."""
    carry = _carry(ledger, parent)
    pid = parent["id"]
    parents = [pid]
    domain = None
    note = ""
    if op == "detach":
        terms = set(t for t in parent["terms"] if t not in SUBJECT_NAMES) | {"principle"}
        label = "principle without the name: " + ", ".join(sorted(terms - {"principle"})[:5])
    elif op == "refine":
        facet = parent.get("facet") if parent.get("facet") in FACET_WORDS else "sequence"
        if facet == parent.get("facet"):
            facet = ("material", "form", "space", "sequence")[_h(seed, n, "facet") % 4]
        terms = set(carry) | FACET_WORDS[facet]
        label = f"the {facet} of it"
    elif op in ("associate", "leap"):
        domain = _domain(set(parent["terms"]), brief, used, op == "leap", seed, n)
        via = sorted(domain["terms"] & set(parent["terms"]))
        terms = set(carry) | domain["terms"]
        label = f"read as {domain['reads_as']}"
        note = "via " + (", ".join(via) if via else "nothing shared -- a leap")
    elif op == "invert":
        hit = next((t for t in carry + sorted(parent["terms"]) if t in OPPOSITES), None)
        if hit is None:
            hit = next((t for t in sorted(brief) if t in OPPOSITES), None)
        if hit is None:
            return step(ledger, parent, "associate", n, seed, brief, used, others)
        terms = (set(carry) - {hit}) | {OPPOSITES[hit], hit + "-inverted"}
        label = f"{hit} turned into {OPPOSITES[hit]}"
    elif op == "revive":
        recent = {pid} | set(ledger.ancestry(pid)[:3])
        cold = [c for c in ledger.cold(n, recent) if ledger.nodes[c]["origin"] == "op"
                or (ledger.nodes[c]["origin"] == "claim" and ledger.nodes[c]["subject"] in CAT.GM_SUBJECTS)]
        if not cold:
            return step(ledger, parent, "associate", n, seed, brief, used, others)
        cid = cold[_h(seed, n, "cold") % len(cold)]
        c = ledger.nodes[cid]
        parents.append(cid)
        terms = set(carry[:4]) | set(c["terms"][:6])
        label = f"brings back: {c['label'][:50]}"
        ledger.touch(cid, n)
    elif op == "fold":
        other = next((o for o in others if o["id"] != pid and o["id"] not in ledger.ancestry(pid)), None)
        if other is None:
            return step(ledger, parent, "associate", n, seed, brief, used, others)
        parents.append(other["id"])
        shared = set(parent["terms"]) & set(other["terms"])
        terms = set(carry[:4]) | set(other["terms"][:4]) | shared | {"fold"}
        label = f"folded with: {other['label'][:50]}"
        note = "shared: " + (", ".join(sorted(shared)) or "none -- the fold is the claim")
    else:
        raise ValueError(f"unknown operator {op}")
    m = measure(terms, parent["terms"])
    nid = f"N{_h(seed, n, pid, op) % 10**8:08d}"
    child = {"id": nid, "origin": "op", "op": op, "label": label, "terms": terms, "facet": parent.get("facet"),
             "claims": [], "subject": "drift", "parents": parents, "domain": domain["name"] if domain else None,
             "note": note, "measure": m}
    ledger.add(child, n)
    ledger.touch(pid, n)
    return ledger.nodes[nid]


def walk(ledger: Ledger, start: dict, seed: str, brief: set, steps: int = 6, others=()) -> list:
    """A path from one seed node. Every EVERY steps the escalation is broken by an intrusion node."""
    path, cur, used = [start], start, set()
    for i in range(1, steps + 1):
        if i % EVERY == 0:
            x = draw_intrusion(seed, i)
            node = ledger.add({"id": f"X{_h(seed, i, 'x') % 10**8:08d}", "origin": "intrusion", "op": "intrusion",
                               "label": f"{x['who']} {x['how']}; what remains: {x['mark']}", "terms": set(cur["terms"]),
                               "facet": cur.get("facet"), "claims": [], "subject": "drift", "parents": [cur["id"]],
                               "intrusion": x, "measure": measure(cur["terms"], cur["terms"])}, i)
            path.append(node)
            continue
        op = draw_op(seed, i)
        cur = step(ledger, cur, op, i, seed, brief, used, list(others))
        if cur.get("domain"):
            used.add(cur["domain"])
        path.append(cur)
    return path


def guard_text(text: str) -> str:
    """Hard gate 2 -- a generated sentence may not present a fiction as a fact about the brand."""
    if FICTION_AS_FACT.search(text or ""):
        raise ContradictionError(f"generated text attributes something to the brand: {text[:120]}")
    return text


def brand_vocabulary(cat: dict) -> dict:
    """Words that recur (in >= 2 claims) across the Gentle Monster research -> how many claims use them.
    A word used once is an accident of phrasing; recurring words are what the research keeps saying."""
    df: dict = {}
    for c in cat["claims"]:
        if c["subject"] in CAT.GM_SUBJECTS:
            for t in CAT.tokens(c.get("evidence", "")) - SUBJECT_NAMES:
                df[t] = df.get(t, 0) + 1
    return {t: n for t, n in df.items() if n >= 2 and not t.isdigit()}


def gm_terms(ledger: Ledger, path: list) -> set:
    out = set()
    for n in path:
        for a in ledger.ancestry(n["id"]):
            x = ledger.nodes[a]
            if x["origin"] == "claim" and x["subject"] in CAT.GM_SUBJECTS:
                out |= set(x["terms"]) - SUBJECT_NAMES
    return out


def hypothesis(ledger: Ledger, path: list, cat: dict, obj: str = "eyewear") -> dict:
    """A design hypothesis from one path. Text is composed from the ledger -- no model writes it."""
    src = CAT.by_id(cat)
    claims = {c["id"]: c for c in cat["claims"]}
    seed, final = path[0], path[-1]
    if final["origin"] == "intrusion":
        final = ledger.nodes[final["parents"][0]]
    anc = []
    for n in path:
        anc += [a for a in ledger.ancestry(n["id"]) if a not in anc]
    cids = [cid for a in anc for cid in ledger.nodes[a].get("claims", [])]
    cids = list(dict.fromkeys(cids))
    sids = list(dict.fromkeys(s for c in cids for s in claims.get(c, {}).get("source_ids", [])))
    byname = {d["name"]: d for d in DOMAINS}
    domains = [byname[n["domain"]] for n in path if n.get("domain")]          # in path order
    dom = domains[-1] if domains else DOMAINS[_h(seed["id"], "fallback") % len(DOMAINS)]
    devices = list(dict.fromkeys(dv for d in [dom] + domains[::-1] for dv in d["devices"]))   # the reading it ends in first
    intrusions = [n for n in path if n["origin"] == "intrusion"]
    vocab = brand_vocabulary(cat)
    kept = sorted(set(final["terms"]) & set(vocab), key=lambda t: (-vocab[t], t))
    rule = guard_text(f"Treat {obj} the way {dom['name']} treats {dom['subject']}: "
                      + "; ".join(DEVICES[d][0] for d in devices[:3])
                      + (f". Carry over from the research: {', '.join(kept[:5])}." if kept else "."))
    principles = [{"claim": c, "kind": claims[c]["kind"], "evidence": claims[c]["evidence"],
                   "read": CAT.claim_verification(cat, claims[c])} for c in cids if c in claims]
    assoc = [{"domain": n["domain"], "operator": n["op"], "via": n.get("note", "")} for n in path if n.get("domain")]
    pages = list(dict.fromkeys(DEVICES[d][1] for d in devices))
    relevance = round(min(1.0, len(kept) / 4), 2)     # words the brand's own research uses more than once
    snippet_only = sum(p["read"] != "fulltext" for p in principles)
    dist = 1 - (len(set(seed["terms"]) & set(final["terms"])) / max(1, len(set(seed["terms"]) | set(final["terms"]))))
    traced = sum(1 for p in principles if p["read"] != "none")
    risks = []
    if snippet_only:
        risks.append(f"{snippet_only} of {len(principles)} research principles rest on search snippets, not read pages")
    if relevance < 0.5:
        risks.append("brand relevance is thin: few research words survive to the final concept")
    if any(n.get("op") == "leap" for n in path):
        risks.append("contains a leap: the association is deliberately far and may read as arbitrary")
    risks.append("rights: real campaign imagery is not cleared; pages fall back to generated plates and cited references")
    h = {
        "hypothesis_id": f"H-{_h(seed['id'], final['id']) % 10**6:06d}",
        "title": f"{obj.capitalize()} read as {dom['reads_as']}",
        "research_sources": {"claims": cids, "sources": sids},
        "observed_principles": principles,
        "cross_domain_associations": assoc,
        "transformation_rule": rule,
        "intended_reader_experience": dom["experience"],
        "layout_implications": [{"device": d, "label": DEVICES[d][0], "page_type": DEVICES[d][1]} for d in devices],
        "image_direction": dom["image"],
        "typography_implications": dom["type"],
        "content_implications": dom["content"],
        "risks": risks,
        "validation_criteria": [
            "every page built from this hypothesis uses at least one of its devices",
            "every factual sentence on those pages cites a claim in research/sources.json",
            "no page presents a drift experiment as a real campaign, product or interview",
            "no reference image is published without cleared rights",
        ],
        "palette": dom["palette"],
        "intrusions": [n["intrusion"] for n in intrusions],
        "path": [{"id": n["id"], "op": n.get("op") or n["origin"], "label": n["label"], "domain": n.get("domain"),
                  "measure": n.get("measure")} for n in path],
        "scores": {
            "source_traceability": round(traced / len(principles), 2) if principles else 0.0,
            "conceptual_distance": round(dist, 2),
            "editorial_coherence": round(len([d for d in devices if DEVICES[d][1]]) / max(1, len(devices)) * (1 if len(pages) >= 2 else 0.5), 2),
            "visual_originality": None,          # set by compare(): needs the other directions
            "brand_relevance": relevance,
            "feasibility": round(len([d for d in devices if DEVICES[d][2] or DEVICES[d][1] in ("multi_column", "single_column", "typographic")]) / max(1, len(devices)), 2),
            "rights_compliance": None,           # set by the planner once assets are known
        },
    }
    h["status"] = "kept" if relevance >= 0.25 and h["scores"]["source_traceability"] > 0 else "excluded"
    if h["status"] == "excluded":
        h["excluded_because"] = "brand relevance < 0.25" if relevance < 0.25 else "no traceable source"
    return h


def originality(hyps: list) -> None:
    """Visual originality relative to the other candidates: share of a hypothesis' devices no other candidate uses."""
    for h in hyps:
        mine = {d["device"] for d in h["layout_implications"]}
        others = {d["device"] for o in hyps if o is not h for d in o["layout_implications"]}
        h["scores"]["visual_originality"] = round(len(mine - others) / max(1, len(mine)), 2)
