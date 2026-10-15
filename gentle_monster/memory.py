# -*- coding: utf-8 -*-
"""Session memory of one design conversation (one job) -- what was said, by whom, and whether it still holds.

Why this exists. Until now every `!젠몬` turn was stateless: a follow-up such as "벽은 콘크리트 말고 나무로"
was routed to a moodboard rebuild or a status reply and the correction never reached the model, and a
follow-up brief started a new job that had lost every earlier constraint. The obvious fix -- paste the whole
conversation, or keyword-search old notes that include the model's own answers -- is the failure the
literature keeps measuring: models commit to early guesses and build on their own earlier answers
(Laban et al. 2025, arXiv:2505.06120; Zhang et al. 2023, arXiv:2305.13534), and long inputs bury what matters
(Liu et al., TACL 2024). So this store keeps the *full* record but marks every entry with what it is:

    kind     user_stated      the user said it (a turn of theirs is the source)
             source_fact      read or measured by code from a file (job.json, spec.check, photos)
             model_inference  a model wrote it -- a draft, a design reason, a verifier's opinion
             summary          a digest of other records; never a fact on its own, keeps `sources`
    status   active · superseded (a newer user statement replaced it) · retracted (shown wrong)

Rules the code enforces (tests/test_memory.py holds each one):
  * nothing is deleted. A correction writes a new record and marks the old one superseded, with links both ways.
  * a model's output, or a confidence it gives itself, never becomes a fact. promote() needs non-model
    evidence (a user turn or a code measurement) and refuses otherwise.
  * a correction whose scope is unclear ("콘크리트 말고 나무" while floor AND wall are concrete) does not
    overwrite anything. It is stored with `conflicts_with` and the caller asks the user.

The store is an append-only JSONL log (out/<job>/memory.jsonl, ignored by git); the current state is the
last version of each id. A design session holds tens to a few hundred records, so retrieval is a linear
scan with token overlap -- no vector database: it would add a dependency and an index to keep in step,
and similarity does not say whether a record is still true anyway (status and kind do).
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

KINDS = ("user_stated", "source_fact", "model_inference", "summary")
STATUSES = ("active", "superseded", "retracted")
# how much a record may be relied on -- by where it came from, never by what the model said about itself
TRUST = {"user_stated": 3, "source_fact": 3, "summary": 1, "model_inference": 0}

# ---------------------------------------------------------------- slot extraction (no model call)
SURFACES = {"바닥": "room.floor", "floor": "room.floor", "벽": "room.wall", "wall": "room.wall", "천장": "room.ceiling", "ceiling": "room.ceiling"}
MATERIAL_WORDS = [   # longest first when matching; values are spec.MATERIALS presets
    ("폴리싱 콘크리트", "polished_concrete"), ("연마 콘크리트", "polished_concrete"), ("polished concrete", "polished_concrete"),
    ("노출 콘크리트", "concrete"), ("노출콘크리트", "concrete"), ("콘크리트", "concrete"), ("concrete", "concrete"),
    ("화강암", "granite"), ("granite", "granite"), ("스테인리스", "steel"), ("스틸", "steel"), ("강철", "steel"), ("steel", "steel"),
    ("거울", "mirror_aluminium"), ("미러", "mirror_aluminium"), ("mirror", "mirror_aluminium"),
    ("알루미늄", "aluminium"), ("aluminium", "aluminium"), ("aluminum", "aluminium"),
    ("황동", "brass"), ("브라스", "brass"), ("brass", "brass"), ("붉은 왁스", "red_wax"), ("red wax", "red_wax"),
    ("석회", "lime_plaster"), ("라임 플라스터", "lime_plaster"), ("plaster", "lime_plaster"),
    ("원목", "wood"), ("목재", "wood"), ("나무", "wood"), ("우드", "wood"), ("wood", "wood"),
    ("호박색 유리", "amber_glass"), ("amber glass", "amber_glass"), ("유리", "glass"), ("glass", "glass"),
    ("검은 돌", "black_stone"), ("흑석", "black_stone"), ("black stone", "black_stone"),
    ("흙", "strata_clay"), ("점토", "strata_clay"), ("clay", "strata_clay"), ("흰 광택", "white_gloss"), ("white gloss", "white_gloss"),
]
LIGHT_WORDS = [("어두운 갤러리", "dark_gallery"), ("어둡", "dark_gallery"), ("dark gallery", "dark_gallery"),
               ("화이트 갤러리", "white_gallery"), ("하얀 갤러리", "white_gallery"), ("white gallery", "white_gallery"),
               ("자연광", "daylight"), ("daylight", "daylight"), ("따뜻한 스팟", "warm_spot"), ("warm spot", "warm_spot")]
DIMS = [(r"(?:폭|가로|너비|width)", "layout.W"), (r"(?:깊이|세로|depth)", "layout.D"), (r"(?:천장고|층고|천장 높이|높이|height)", "layout.H")]
# "A 말고 B" -- A is what the user takes back, B what replaces it. A is only the clause right before the cue:
# "폭 20m, 깊이 15m 말고 12m" takes back the depth, not the width; "벽은 나무로 하고 대신 바닥은 ..." takes back nothing.
CORRECTION = re.compile(r"\s*(?:말고|아니고|(?:이|가)?\s*아니라|대신에?|->|→|instead of)\s*", re.I)
CLAUSE_BREAK = re.compile(r"[,;\n]|\.(?!\d)|그리고|하고")    # not the point in "2.4m"
_LEAD = re.compile(r"^(?:아니(?:야)?|no|정정|수정)(?:[\s,:.]+|$)", re.I)
CORRECTION_CUE = re.compile(r"말고|아니고|아니라|대신|->|→|instead of|정정|고쳐|잘못|틀렸", re.I)
# "지난번에 정한 색온도" -- an explicit pointer to an earlier decision; the word after it is what must be found
REFERS_BACK = re.compile(r"(?:지난번에?|아까|전에|앞서|예전에|이미)\s*(?:정한|말한|얘기한|결정한|정했던|말했던|골랐던|고른)|as (?:we )?(?:agreed|decided) (?:on )?", re.I)
_PARTICLES = r"(?:은|는|이|가|을|를|로|으로|도|만|의|에|에서|과|와|랑|이랑)?"
# a length and its unit, converted to metres. Longest unit first; a unit glued to more Latin letters is not one ("18ms")
LENGTH = re.compile(r"(\d+(?:\.\d+)?)\s*(밀리미터|밀리|mm|센티미터|센티|cm|미터|m)(?![A-Za-z])", re.I)
_TO_M = {"밀리미터": .001, "밀리": .001, "mm": .001, "센티미터": .01, "센티": .01, "cm": .01, "미터": 1, "m": 1}


def _metres(m: "re.Match") -> float:
    return round(float(m.group(1)) * _TO_M[m.group(2).lower()], 4)


def correction_span(text: str) -> "tuple[int, int, int] | None":
    """(old_from, old_to, new_from) of 'A 말고 B', A cut to the clause before the cue; None when A is empty."""
    t = text or ""
    for c in CORRECTION.finditer(t):
        head = t[:c.start()]
        brk = list(CLAUSE_BREAK.finditer(head))
        a = brk[-1].end() if brk else 0
        old = head[a:]
        lead = _LEAD.match(old.strip())
        if lead:
            a += len(old) - len(old.lstrip()) + lead.end()
            old = t[a:c.start()]
        if old.strip(" ,.:") and c.end() < len(t.rstrip()):
            return a, c.start(), c.end()
    return None


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def digest(s: str) -> str:
    """Stable short hash -- what the trace logs instead of text."""
    return hashlib.sha256(_norm(s).encode("utf-8")).hexdigest()[:12]


def _find_word(text: str, table) -> "tuple[str, int, int] | None":
    low = text.lower()
    best = None
    for w, v in sorted(table, key=lambda t: -len(t[0])):
        i = low.find(w.lower())
        if i >= 0 and (best is None or i < best[1]):
            best = (v, i, i + len(w))
    return best


def _acronyms(text: str) -> "list[dict]":
    """'SPA (STYLE, PASSION, ARCHITECTURE)' / 'SPA는 STYLIST, PHOTOGRAPHER, ARCHITECT' -> def:SPA.
    Only when the following capitalised words spell the acronym -- otherwise it is not a definition."""
    out = []
    for m in re.finditer(r"(?<![A-Za-z])([A-Z]{2,6})(?![A-Za-z])", text):
        ac = m.group(1)
        words = list(re.finditer(r"(?<![A-Za-z])([A-Z][A-Za-z]+)(?![A-Za-z])", text[m.end():m.end() + 200]))
        for k in range(len(words) - len(ac) + 1):
            seq = words[k:k + len(ac)]
            if "".join(w.group(1)[0] for w in seq) == ac and all(w.group(1) != ac for w in seq):
                a, b = m.end() + seq[0].start(), m.end() + seq[-1].end()
                out.append({"key": f"def:{ac}", "value": ", ".join(w.group(1) for w in seq), "span": [m.start(), b]})
                break
    return out


def extract(text: str) -> "list[dict]":
    """Slots a sentence sets: [{key, value, span:[a,b]}]. Pure regex; what it cannot read stays free text.
    With a correction cue only the replacing part ('B' of 'A 말고 B') supplies values."""
    t = text or ""
    cs = correction_span(t)
    old_from, old_to, new_from = cs if cs else (0, 0, 0)
    taken_back = lambda i: old_from <= i < new_from          # a value inside A is what the user takes back
    out = []
    from gentle_monster import intent                     # light module; BRANDS lives there
    low = t.lower()
    for w, (_, brand) in intent.BRANDS.items():
        i = next((i for i in (m.start() for m in re.finditer(re.escape(w), low)) if not taken_back(i)), -1)
        if i >= 0 and not any(o["key"] == "brand" for o in out):
            out.append({"key": "brand", "value": brand, "span": [i, i + len(w)]})
    for pat, key in DIMS:
        for d in re.finditer(pat + _PARTICLES + r"\s*[:=]?\s*" + LENGTH.pattern, t, re.I):
            if not taken_back(d.start(1)):
                out.append({"key": key, "value": _metres(LENGTH.match(t, d.start(1))), "span": [d.start(), d.end()]})
                break
    if cs:                                               # "폭 24m 말고 18m": the key is in A, the number in B
        for pat, key in DIMS:
            if re.search(pat, t[old_from:old_to], re.I) and not any(o["key"] == key for o in out):
                n = LENGTH.search(t, new_from)
                if n:
                    out.append({"key": key, "value": _metres(n), "span": [n.start(), n.end()]})
                break
    for w, key in SURFACES.items():
        for s in re.finditer(re.escape(w), t, re.I):
            stop = CLAUSE_BREAK.search(t, s.end())
            seg_end = stop.start() if stop else len(t)
            seg_from = new_from if taken_back(s.end()) else s.end()   # "벽은 콘크리트 말고 나무로": A's surface, B's material
            other = re.search("|".join(re.escape(o) for o, k in SURFACES.items() if k != key), t[seg_from:seg_end], re.I)
            if other and taken_back(s.end()):                # "벽이 아니라 바닥을 나무로": the material belongs to the floor
                seg_end = seg_from + other.start()
            hit = _find_word(t[seg_from:seg_end], MATERIAL_WORDS) if seg_from < seg_end else None
            if hit and not any(o["key"] == key for o in out):
                end = seg_from + hit[2]
                end += len(re.match(r"(?:으로|로)?", t[end:]).group(0))
                out.append({"key": key, "value": hit[0], "span": [s.start(), end]})
    if re.search(r"조명|빛|light|갤러리|gallery", t, re.I):
        hit = _find_word(t[new_from:], LIGHT_WORDS)
        base = new_from
        if not hit and cs:
            hit, base = _find_word(t[:old_from], LIGHT_WORDS), 0
        if hit:
            out.append({"key": "room.light", "value": hit[0], "span": [base + hit[1], base + hit[2]]})
    out += _acronyms(t)
    return out


# A displeasure signal is not evidence. classify() sorts it so the context can say what to do with it:
#   correction   a new value is given ("A 말고 B", a slot)           -> apply it (ingest_user already does)
#   bare         an evaluation with no reason ("고쳐", "재미없어")    -> self-diagnose the latest output, say the assumption
#   unsupported  "X is wrong" about a value a user statement or a source backs, with no new value -> keep it, show why, ask
#   usability    "불편해", "헷갈려" with no reason                    -> change nothing; ask what and why (user rule 2026-10-15)
#   unclear      nothing to revise yet, or a dispute/pointer with no target ("틀렸어", "이 부분")  -> ask once
DISSATISFIED = re.compile(r"고쳐|다시\s*(?:해|써|만들|짜|작성)|별로|재미\s*없|마음에\s*안|맘에\s*안|이상해|어색|밋밋|약해|아쉬|구려|부족해|싫어|"
                          r"\bredo\b|fix (?:it|this)|not good|boring", re.I)
DISPUTE = re.compile(r"틀렸|틀린|틀려|아니잖|잘못|wrong|that's not|that is not", re.I)
DEICTIC = re.compile(r"(?:이|그|저)\s*부분|여기|거기|저기|(?<![가-힣])(?:이거|그거|저거|이것|그것)(?![가-힣]*(?:로|으로))")
USABILITY = re.compile(r"불편|어렵|어려워|복잡|헷갈|못\s*찾|모르겠|답답|안\s*돼|안\s*되|쓰기\s*힘들|confusing|hard to use", re.I)
REASON = re.compile(r"때문|이라서|라서|어서|아서|해서|니까|너무|말고|대신|보다|안\s*보|작아|커서|길어|짧아|많아|because|too ", re.I)
MENTIONS = dict(SURFACES, **{"폭": "layout.W", "가로": "layout.W", "너비": "layout.W", "깊이": "layout.D", "세로": "layout.D",
                             "천장고": "layout.H", "층고": "layout.H", "높이": "layout.H", "조명": "room.light", "브랜드": "brand"})
TERSE = 12                                                # non-space characters: "고쳐", "마음에 안 들어"


def classify(text: str, store: "Store | None" = None, sources=(), exclude_turn: str = "") -> dict:
    """-> {case, key, backing}. Code only. backing = [{by, value}] for an unsupported dispute."""
    t = text or ""
    out = {"case": "none", "key": None, "backing": []}
    if extract(t) or correction_parts(t):
        out["case"] = "correction"
        return out
    if USABILITY.search(t) and not REASON.search(t):
        out["case"] = "usability"                        # do not bend toward pleasing: ask what is hard and why
        return out
    dispute, unhappy = DISPUTE.search(t), DISSATISFIED.search(t)
    if not (dispute or unhappy):
        return out
    has_output = bool(store) and any(r["kind"] == "model_inference" and r["status"] == "active" for r in store.recs.values())
    if not has_output and not sources:
        out["case"] = "unclear"                          # nothing has been made yet: there is nothing to revise
        return out
    key = next((k for w, k in sorted(MENTIONS.items(), key=lambda x: -len(x[0])) if w in t.lower()), None)
    out["key"] = key
    if dispute and key:
        backing = [{"by": f"{r['turn']} {r['id']} (user)", "value": r["value"]} for r in (store.active("user_stated") if store else [])
                   if r["key"] == key and r["turn"] != exclude_turn]
        backing += [{"by": s.get("ref", "source"), "value": s.get("value")} for s in sources if s.get("key") == key]
        if store:
            backing += [{"by": f"{r['id']} (source)", "value": r["value"]} for r in store.active("source_fact") if r["key"] == key]
        if backing:
            out["case"], out["backing"] = "unsupported", backing
            return out
    if (dispute or DEICTIC.search(t)) and not key:
        out["case"] = "unclear"                          # "틀렸어", "이 부분 이상해": which part?
        return out
    out["case"] = "bare"
    return out


def terse(text: str) -> bool:
    return len(re.sub(r"\s", "", text or "")) <= TERSE


def overlap(query: str, text: str) -> float:
    """Shared words; 0.5 for a word inside another (Korean particles: 런웨이 / 런웨이가)."""
    terms = set(re.findall(r"[0-9a-z가-힣]{2,}", _norm(query)))
    words = set(re.findall(r"[0-9a-z가-힣]{2,}", _norm(text)))
    return len(terms & words) + .5 * sum(1 for t in terms for w in words if t != w and (t in w or w in t))


REFERENCE = re.compile(r"참고|아래|다음은|다음 (?:글|자료|내용)|문항|사례|원문|자료|reference|below|attached", re.I)


def _reference(text: str) -> bool:
    """Material the user hands over to work from (a pasted 사례, a 문항, a source text): kept until replaced."""
    n = len((text or "").strip())
    return n >= 400 or (n >= 30 and bool(REFERENCE.search(text or "")) and ("\n" in text or n >= 120 or "문항" in text))


def correction_parts(text: str) -> "tuple[str, str] | None":
    cs = correction_span(text)
    if not cs:
        return None
    return text[cs[0]:cs[1]].strip(" ,.:"), text[cs[2]:].strip(" ,.:")


def _value_for(key: str, text: str):
    """The value the replacing words give for a known slot, or None."""
    if key and key.startswith("room.") and key != "room.light":
        hit = _find_word(text, MATERIAL_WORDS)
    elif key == "room.light":
        hit = _find_word(text, LIGHT_WORDS)
    elif key and key.startswith("layout."):
        n = LENGTH.search(text)
        return _metres(n) if n else None
    else:
        return None
    return hit[0] if hit else None


# ---------------------------------------------------------------- the store
class PromotionRefused(ValueError):
    pass


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.recs: "dict[str, dict]" = {}
        self.turns: "list[dict]" = []
        if self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                e = json.loads(line)
                if e.get("op") == "turn":
                    self.turns.append(e["turn"])
                elif e.get("op") == "put":
                    self.recs[e["rec"]["id"]] = e["rec"]

    # -- log
    def _append(self, entry: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _save(self, rec: dict) -> dict:
        self.recs[rec["id"]] = rec
        self._append({"op": "put", "rec": rec})
        return rec

    @staticmethod
    def _now() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # -- turns (the full conversation, kept; the model gets a selection of it -- context.build)
    def turn(self, role: str, text: str) -> str:
        tid = f"t{len(self.turns) + 1}"
        t = {"id": tid, "role": role, "text": text, "at": self._now()}
        self.turns.append(t)
        self._append({"op": "turn", "turn": t})
        return tid

    # -- records
    def put(self, kind: str, content: str, source: dict, key: str = None, value=None, turn: str = None,
            span=None, sources=None, **meta) -> str:
        if kind not in KINDS:
            raise ValueError(f"unknown kind {kind!r}")
        if not isinstance(source, dict) or not source.get("type"):
            raise ValueError("every record needs a source {type, ref}")
        if kind == "user_stated" and source["type"] != "turn":
            raise ValueError("a user_stated record must come from a user turn")
        if kind == "source_fact" and source["type"] == "model":
            raise ValueError("a model's output is not a source fact")
        meta.pop("confidence", None)        # a model's confidence about itself is not evidence -- not stored
        now = self._now()
        rid = f"m{len(self.recs) + 1}"
        rec = {"id": rid, "kind": kind, "content": content, "key": key, "value": value, "source": source, "turn": turn,
               "span": span, "sources": list(sources or []), "created_at": now, "updated_at": now, "status": "active",
               "supersedes": [], "superseded_by": None, "conflicts_with": [], "evidence": [], **meta}
        self._save(rec)
        return rid

    def get(self, rid: str) -> dict:
        return self.recs[rid]

    def all(self) -> "list[dict]":
        return list(self.recs.values())

    def active(self, kind: str = None) -> "list[dict]":
        return [r for r in self.recs.values() if r["status"] == "active" and (kind is None or r["kind"] == kind)]

    def update(self, rid: str, **changes) -> dict:
        rec = dict(self.recs[rid], **changes, updated_at=self._now())
        return self._save(rec)

    def supersede(self, old_ids, new_id: str, why: str = "") -> None:
        for o in old_ids:
            if o == new_id or self.recs[o]["status"] != "active":
                continue
            self.update(o, status="superseded", superseded_by=new_id, why=why)
        new = self.recs[new_id]
        self.update(new_id, supersedes=sorted(set(new["supersedes"]) | set(old_ids) - {new_id}))

    def retract(self, rid: str, by: str, why: str) -> None:
        if self.recs[rid]["status"] == "active":
            self.update(rid, status="retracted", superseded_by=by, why=why)

    def link_conflict(self, a: str, b_ids) -> None:
        for b in b_ids:
            self.update(b, conflicts_with=sorted(set(self.recs[b]["conflicts_with"]) | {a}))
        self.update(a, conflicts_with=sorted(set(self.recs[a]["conflicts_with"]) | set(b_ids)))

    def promote(self, rid: str, evidence) -> None:
        """A model inference becomes a source fact only on non-model evidence: an active user statement or
        a code measurement. The model's own word (or a model verifier) is never enough."""
        rec = self.recs[rid]
        if rec["kind"] != "model_inference":
            raise PromotionRefused(f"{rid} is {rec['kind']}, not a model inference")
        ok = [e for e in evidence or () if e in self.recs and self.recs[e]["status"] == "active"
              and self.recs[e]["kind"] in ("user_stated", "source_fact") and self.recs[e]["source"]["type"] != "model"]
        if not ok:
            raise PromotionRefused(f"{rid}: no active non-model evidence -- a model's answer is not verified by itself")
        self.update(rid, kind="source_fact", evidence=ok, promoted_from="model_inference")

    # -- ingest a user turn: record it, read its slots, apply corrections
    def ingest_user(self, text: str) -> dict:
        """Returns {turn, record, facts, superseded, ambiguous, unmatched}.
        ambiguous = [{record, candidates}] -- a correction that could mean more than one earlier statement.
        Nothing is overwritten for those; the caller asks."""
        tid = self.turn("user", text)
        slots = extract(text)
        corr = correction_parts(text)
        eff = {"turn": tid, "record": "", "facts": [], "superseded": [], "ambiguous": [], "unmatched": []}
        whole = self.put("user_stated", text, {"type": "turn", "ref": tid}, turn=tid,
                         correction=bool(corr or (CORRECTION_CUE.search(text) and slots)),
                         pinned=_reference(text), terse=terse(text) and bool(DISSATISFIED.search(text) or DISPUTE.search(text)))
        eff["record"] = whole
        cs = correction_span(text)
        for s in slots:
            a = max(s["span"][0], cs[2]) if cs and cs[0] <= s["span"][0] < cs[2] else s["span"][0]
            said = text[a:s["span"][1]].strip(" ,.:") or text[s["span"][0]:s["span"][1]]
            rid = self.put("user_stated", f"{s['key']} = {s['value']}  (user: \"{said}\")", {"type": "turn", "ref": tid},
                           key=s["key"], value=s["value"], turn=tid, span=s["span"], parent=whole)
            eff["facts"].append(rid)
            older = [r["id"] for r in self.active("user_stated") if r["key"] == s["key"] and r["id"] != rid]
            if older:                                        # same slot, newer user statement wins
                self.supersede(older, rid, why=f"user restated {s['key']} in {tid}")
                eff["superseded"] += older
        new_keys = {s["key"] for s in slots}
        for r in self.active("user_stated"):                  # a clear statement answers an open "which one?"
            open_c = [c for c in r["conflicts_with"] if c in self.recs and self.recs[c]["key"]]
            if r["id"] != whole and open_c and new_keys & {self.recs[c]["key"] for c in open_c}:
                for c in r["conflicts_with"]:
                    if c in self.recs:
                        self.update(c, conflicts_with=[x for x in self.recs[c]["conflicts_with"] if x != r["id"]])
                self.update(r["id"], conflicts_with=[], resolved_by=tid)
        if corr:
            old_text, _ = corr
            keys_set = {s["key"] for s in slots}
            cands = self._candidates(old_text, exclude_keys=keys_set, exclude_turn=tid)
            if keys_set:
                pass                                         # the slot told us exactly what changed -- done above
            elif len({c["key"] or c["id"] for c in cands}) == 1:
                key, by = cands[0]["key"], whole
                val = _value_for(key, corr[1])
                if val is not None:                          # "콘크리트 말고 화강암" with only the floor in concrete
                    by = self.put("user_stated", f"{key} = {val}  (user: \"{corr[1]}\")", {"type": "turn", "ref": tid},
                                  key=key, value=val, turn=tid, parent=whole)
                    eff["facts"].append(by)
                self.supersede([c["id"] for c in cands], by, why=f"user correction {tid}")
                eff["superseded"] += [c["id"] for c in cands]
            elif cands:
                self.link_conflict(whole, [c["id"] for c in cands])
                eff["ambiguous"].append({"record": whole, "candidates": [c["id"] for c in cands]})
            else:
                eff["unmatched"].append(old_text)
        return eff

    def add_model_turn(self, text: str, ref: str = "model") -> str:
        """A model's reply: kept in the turn log, and as a model_inference (its slots read, so a later context
        can cut what contradicts the user or a source). Never user_stated, never source_fact."""
        tid = self.turn("model", text)
        return self.put("model_inference", text, {"type": "model", "ref": ref}, turn=tid)

    def add_summary(self, text: str, sources, ref: str = "summary") -> str:
        """A digest of other turns/records (e.g. a host bot's compaction note). It keeps its sources and stays a summary."""
        return self.put("summary", text, {"type": "summary", "ref": ref}, sources=sources)

    def ambiguity(self, text: str) -> "list[dict]":
        """Without writing anything: the earlier statements an unclear correction could mean ([] if clear)."""
        corr = correction_parts(text)
        if not corr or extract(text):
            return []
        cands = self._candidates(corr[0])
        return cands if len({c["key"] or c["id"] for c in cands}) > 1 else []

    def _candidates(self, old_text: str, exclude_keys=(), exclude_turn: str = "") -> "list[dict]":
        """Active user statements the 'A' of 'A 말고 B' can refer to: by material/light/brand value, else by words."""
        val = _find_word(old_text, MATERIAL_WORDS) or _find_word(old_text, LIGHT_WORDS)
        surf = next((k for w, k in SURFACES.items() if w in old_text.lower()), None)
        recs = [r for r in self.active("user_stated") if r["turn"] != exclude_turn]
        if val:
            hits = [r for r in recs if r["key"] and r["value"] == val[0] and (surf is None or r["key"] == surf)]
            if hits:
                return hits
        words = [w for w in re.findall(r"[0-9A-Za-z가-힣]{2,}", old_text) if not re.fullmatch(r"(?:아니|정정|수정)", w)]
        if not words:
            return []
        return [r for r in recs if r["key"] and r["key"] not in exclude_keys and all(w.lower() in r["content"].lower() for w in words)]

    # -- retrieval: lexical, filtered by status; trust decides order among the relevant, similarity never decides truth
    def search(self, query: str, k: int = 8, kinds=None) -> "list[tuple[float, dict]]":
        out = []
        n = len(self.turns) or 1
        for r in self.active():
            if kinds and r["kind"] not in kinds:
                continue
            ov = overlap(query, r["content"])
            if not ov:
                continue
            age = n - int((r.get("turn") or "t0")[1:] or 0)
            out.append((ov + .1 * TRUST[r["kind"]] - .01 * age, r))
        out.sort(key=lambda x: -x[0])
        return out[:k]


def open_job(name: str) -> Store:
    from gentle_monster import paths
    return Store(paths.job_dir(name) / "memory.jsonl")
