# -*- coding: utf-8 -*-
"""Per-request context: what the model is shown, chosen from the session memory under a token budget.

The stored record (memory.Store: every turn, every statement, every draft) and the model input are two
different things. The input is rebuilt for each request in this order, and each part says what it is:

    CURRENT INSTRUCTION          the user's words in this turn                      always kept
    HOW TO TREAT THIS MESSAGE    a displeasure signal, sorted by memory.classify     always kept
    USER CORRECTIONS             active statements that replaced earlier ones        always kept
    SETTLED BY THE USER          active slots (room.wall = wood, layout.W = 18, ...) always kept
    UNRESOLVED                   conflicts kept as conflicts, never merged           always kept
    NOT IN MEMORY                "그대로/지난번에 정한 ..." with nothing to back it     always kept
    SOURCE FACTS                 read by code from job.json, spec.check, ...          budget
    EARLIER USER STATEMENTS      reference material, recent turns, then relevant     budget
                                 or imperative ones ("고쳐"-only turns take no slot)
    MODEL'S EARLIER OUTPUT       the latest output first (what "고쳐" points at),    budget, last
                                 then drafts / summaries, labelled unverified

Left out, each with a reason in the trace: superseded / retracted records, duplicates, model or summary
claims that contradict an active user statement or a source fact (the contradicting words are cut out;
a record with no span is dropped), old chatter that shares no words with the request and gives no
instruction, and whatever does not fit the budget. Superseded words inside a still-active turn are cut
out too ("벽은 노출 콘크리트" -> "⟨changed later, t5⟩"), so the turn's other content survives.

Budget: min(model window - output reserve, GM_CONTEXT_TOKENS) minus the fixed task prompt. The window is
not the target -- accuracy falls off well before it (Liu et al., TACL 2024) -- so the working cap is far
below it. Tokens are *estimated* (no tokenizer offline: ASCII/4 + 1 per other character, on the high side);
when the model answers, its own usageMetadata count goes into the trace next to the estimate.

The trace (out/<job>/context_trace.jsonl) holds ids, kinds, reasons, token counts and source refs --
no conversation text, only 12-character hashes.
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from pathlib import Path

from gentle_monster import memory as M

WINDOW = {"gemini-2.5-flash": 1_048_576, "gemini-2.5-pro": 1_048_576, "gemini-2.0-flash": 1_048_576}
OUTPUT_RESERVE = 8192                 # = llm.ask maxOutputTokens
DEFAULT_CAP = 12000
RECENT_TURNS = 4
DOMAIN = re.compile(r"공간|매장|벽|바닥|천장|조명|동선|입구|출구|출입문|(?<![가-힣])문(?:을|은|이|의)|재료|마감재|색상|색감|팔레트|오브제|조형|레이아웃|평면|시놉시스|브랜드|폭|깊이|높이|"
                    r"층고|천장고|정지점|space|store|wall|floor|ceiling|light|circulation|door|material|palette|layout", re.I)
IMPERATIVE = re.compile(r"해줘|해 줘|해라|하라|하세요|해야|하지 마|말 것|없이|빼고|빼줘|반드시|꼭|만 써|로 해|으로 해|must|never|don't|do not|always|only", re.I)


def estimate_tokens(s: str) -> int:
    s = s or ""
    a = sum(1 for c in s if ord(c) < 128)
    return math.ceil(a / 4 + (len(s) - a))


def budget(fixed_tokens: int, model: str = "", cap: int = None) -> dict:
    model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    win = WINDOW.get(model, 128_000)
    cap = cap or int(os.environ.get("GM_CONTEXT_TOKENS", "0") or 0) or DEFAULT_CAP
    limit = min(win - OUTPUT_RESERVE, cap)
    return {"model": model, "window": win, "output_reserve": OUTPUT_RESERVE, "cap": cap, "limit": limit,
            "fixed": fixed_tokens, "memory": max(0, limit - fixed_tokens)}


def job_facts(job: dict, ref: str = "job.json") -> "list[dict]":
    """Source facts about the current draft, read by code from the file (not from what the model said about it)."""
    if not job:
        return []
    from gentle_monster import spec
    L, R = job.get("layout", {}), job.get("room", {})
    out = [{"key": "brand", "value": job.get("brand"), "content": f"brand: {job.get('brand')}"}]
    out += [{"key": f"layout.{k}", "value": float(L[k]), "content": f"layout.{k}: {L[k]} m"} for k in ("W", "D", "H") if k in L]
    out += [{"key": f"room.{k}", "value": R[k], "content": f"room.{k}: {R[k]}"} for k in ("floor", "wall", "ceiling", "light") if k in R]
    door = next((i for i in L.get("items", []) if i.get("type") == "door"), None)
    if door:
        out.append({"key": "layout.door", "value": [door["x0"], door["x1"]], "content": f"door: x {door['x0']}-{door['x1']} on the street edge"})
    try:
        bad = spec.check(job)
        d, where, _ = spec.clearance(L) if not bad else (None, "", None)
        out.append({"key": "check.layout", "value": len(bad),
                    "content": "spec.check: no problems" + (f"; path clearance {d:.2f} m (nearest {where})" if d is not None else "")
                    if not bad else f"spec.check: {len(bad)} problem(s): " + "; ".join(bad[:3])})
    except Exception as e:                                     # noqa: BLE001 -- a broken draft is still described
        out.append({"key": "check.layout", "value": -1, "content": f"spec.check could not run: {type(e).__name__}"})
    for f in out:
        f["ref"] = ref
    return out


def _slots(rec: dict) -> "list[dict]":
    if rec.get("slots"):
        return rec["slots"]
    if rec["kind"] in ("model_inference", "summary"):
        return M.extract(rec["content"])
    return []


def _redact(text: str, spans, label: str = "changed later") -> str:
    for a, b, by in sorted(spans, key=lambda s: -s[0]):
        text = text[:a] + f"⟨{label}, {by}⟩" + text[b:]
    return text


def build(store: "M.Store", instruction: str, *, fixed_tokens: int = 0, sources=(), cap: int = None,
          model: str = "", turn: str = "", recent: int = RECENT_TURNS, draft_in_frame: str = "") -> dict:
    """-> {text, trace}. `turn` is the id of the current user turn (already ingested); `sources` are fresh
    source facts ({key, value, content, ref}) such as job_facts(job). draft_in_frame: the hash of a draft the
    caller shows in full (the revise prompt does) -- records about that draft would only repeat it."""
    B = budget(fixed_tokens, model, cap)
    trace = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "turn": turn, "instruction": M.digest(instruction),
             "budget": B, "selected": [], "excluded": [], "redacted": [], "sources": sorted({s.get("ref", "") for s in sources}),
             "tokens": {}, "over_budget": False}
    recs = store.all()
    signal = M.classify(instruction, store, sources, exclude_turn=turn)
    trace["followup"] = {"case": signal["case"], "key": signal["key"], "backing": len(signal["backing"])}
    active_user_slots = {r["key"]: r for r in store.active("user_stated") if r["key"]}
    source_by_key = {s["key"]: s for s in sources if s.get("key")}
    for r in store.active("source_fact"):
        if r["key"]:
            source_by_key.setdefault(r["key"], {"key": r["key"], "value": r["value"], "ref": r["id"]})

    def keep(rec, section, why):
        trace["selected"].append({"id": rec["id"], "kind": rec["kind"], "section": section, "why": why})

    def drop(rec, why):
        trace["excluded"].append({"id": rec["id"], "kind": rec["kind"], "why": why})

    # 1. status, duplicates, contradictions -- decided before anything is ranked
    fresh_keys = {s.get("key") for s in sources if s.get("key")}
    seen, live = {}, []
    for r in recs:
        if r["status"] != "active":
            drop(r, f"{r['status']} by {r.get('superseded_by') or '?'}")
            continue
        if r["turn"] == turn and r["kind"] == "user_stated" and not r["key"] and not r.get("conflicts_with"):
            continue                                         # the current instruction itself; shown in its own section
        if r.get("about") and store.recs.get(r["about"], {}).get("status") != "active":
            drop(r, f"about {r['about']}, which is no longer valid")   # a check of a statement the user replaced
            continue
        if draft_in_frame and r.get("draft") == draft_in_frame and r["kind"] == "model_inference":
            drop(r, "duplicate of the current draft, shown in full")
            continue
        if r["kind"] == "source_fact" and r["key"] in fresh_keys:
            drop(r, "duplicate of a fresh source read")
            continue
        h = M.digest(r["content"])
        if h in seen:
            drop(r, f"duplicate of {seen[h]}")
            continue
        seen[h] = r["id"]
        live.append(r)

    texts = {}
    for r in live:
        spans = []
        if r["kind"] == "user_stated" and not r["key"]:      # a turn whose slot was later replaced: cut that slot out
            for c in recs:
                if c.get("parent") == r["id"] and c["status"] != "active" and c.get("span"):
                    by = store.recs.get(c.get("superseded_by") or "", {}).get("turn") or c.get("superseded_by")
                    spans.append((c["span"][0], c["span"][1], by))
                    trace["redacted"].append({"id": r["id"], "key": c["key"], "by": c.get("superseded_by")})
        if r["kind"] in ("model_inference", "summary"):
            bad = []
            for s in _slots(r):
                for auth in (active_user_slots.get(s["key"]), source_by_key.get(s["key"])):
                    if auth and auth.get("value") is not None and str(auth["value"]) != str(s["value"]):
                        bad.append((s, auth.get("id") or auth.get("ref")))
                        break
            if bad and all(s.get("span") for s, _ in bad):
                for s, by in bad:
                    spans.append((s["span"][0], s["span"][1], by))
                    trace["redacted"].append({"id": r["id"], "key": s["key"], "by": by})
            elif bad:
                drop(r, "contradicted by " + ", ".join(sorted({str(by) for _, by in bad})))
                continue
        label = "contradicted by" if r["kind"] in ("model_inference", "summary") else "changed later"
        texts[r["id"]] = _redact(r["content"], spans, label) if spans else r["content"]
        if spans and not re.sub(r"⟨[^⟩]*⟩|[\s,.;:]", "", texts[r["id"]]):
            del texts[r["id"]]                               # nothing left but "changed later": the newer record says it
            drop(r, "every part of it was replaced later")
    live = [r for r in live if r["id"] in texts]

    # 2. sections
    def line(r):
        tag = r["turn"] or r["source"].get("ref", "")
        return f"- [{tag} {r['id']}] {texts[r['id']]}"

    sec = {}
    sec["instruction"] = [f"({turn}) {instruction}"]
    corrections = [r for r in live if r["kind"] == "user_stated" and not r["key"] and (r.get("supersedes") or r.get("correction"))
                   and not r.get("conflicts_with")]
    for r in corrections:
        keep(r, "corrections", "user correction")
    sec["corrections"] = [line(r) for r in corrections]
    slots = [r for r in live if r["kind"] == "user_stated" and r["key"]]
    for r in slots:
        keep(r, "settled", "active user slot")
    sec["settled"] = [line(r) for r in slots]
    conflicts = [r for r in live if r.get("conflicts_with") and r["kind"] == "user_stated" and not r["key"]]
    sec["unresolved"] = []
    for r in conflicts:
        others = [store.recs[o] for o in r["conflicts_with"] if store.recs[o]["status"] == "active"]
        sec["unresolved"].append(f"- [{r['turn']} {r['id']}] the user said \"{texts[r['id']]}\" -- it could refer to: "
                                 + "; ".join(f"[{o['turn']} {o['id']}] {o['content']}" for o in others)
                                 + ". Do not choose silently: keep both as they are and ask which one is meant.")
        keep(r, "unresolved", "correction with unclear scope")
    outputs = sorted((r for r in live if r["kind"] == "model_inference"),
                     key=lambda r: (int((r.get("turn") or "t0")[1:] or 0), int(r["id"][1:])))
    latest = outputs[-1] if outputs else None
    working = {r["id"]: tag for r, tag in zip(outputs[::-1], ("latest output", "the output before it"))}   # a draft, then its critique
    sec["treat"] = []
    case = signal["case"]
    if case == "bare":
        sec["treat"].append("- The user is not satisfied and gave no reason. Do not guess silently and do not start over: check the "
                            "two latest outputs (marked under MODEL'S EARLIER OUTPUT) against the user's material and their last feedback, "
                            "state in one line what you assume is wrong, then revise. Add no fact that no user statement or source gives.")
    elif case == "unsupported":
        sec["treat"].append(f"- The user disputes {signal['key']} but gives no new value. It is backed by: "
                            + "; ".join(f"[{b['by']}] {signal['key']} = {b['value']}" for b in signal["backing"])
                            + ". Displeasure is not evidence: do not change it. Show this and ask one question -- which part is "
                            "wrong, and what should it be?")
    elif case == "usability":
        sec["treat"].append("- The user says something is hard to use but not what or why. Do not apologise and do not change anything "
                            "to please them. Say in one line which part you think they mean, and ask what made it hard and why.")
    elif case == "unclear":
        sec["treat"].append("- The user objects, but to what is unclear" + ("" if latest else " (nothing has been made yet)")
                            + ". Do not revise anything. Ask one short question: what should change, and how?")
    sec["gaps"] = []
    ref = M.REFERS_BACK.search(instruction or "")
    if ref:
        tail = instruction[ref.end():ref.end() + 40]
        terms = [re.sub(r"(?:은|는|이|가|을|를|도|의)$", "", w) for w in re.findall(r"[0-9A-Za-z가-힣]{2,}", tail)
                 if not re.fullmatch(r"(?:그대로|해줘|유지해서|유지|거|것|대로)", w)][:1]
        support = [r for r in live if r["kind"] in ("user_stated", "source_fact") and terms and
                   any(t.lower() in r["content"].lower() for t in terms)] + \
                  [s for s in sources if terms and any(t.lower() in s["content"].lower() for t in terms)]
        if terms and not support:
            sec["gaps"].append(f"- The user refers to an earlier decision about \"{' '.join(terms)}\". Nothing the user said and no "
                               "source fact records it. Do not invent a value; leave that part as it is and say it was not found.")
            trace["gap"] = M.digest(" ".join(terms))

    protected = sum(estimate_tokens(x) for k in ("instruction", "treat", "corrections", "settled", "unresolved", "gaps") for x in sec[k])
    room = B["memory"] - protected - 120                    # headers
    if room < 0:
        trace["over_budget"] = True                          # protected parts are never cut to fit

    def fill(name, items, render, why):
        nonlocal room
        sec[name] = []
        for it, r in items:
            t = render(it)
            n = estimate_tokens(t)
            if n > room:
                if r is not None:
                    drop(r, "over budget")
                continue
            room -= n
            sec[name].append(t)
            if r is not None:
                keep(r, name, why(it))

    src_recs = [r for r in live if r["kind"] == "source_fact"]
    fill("sources", [(s, None) for s in sources] + [(r, r) for r in src_recs],
         lambda s: f"- [{s.get('ref') or s['source'].get('ref')}] {s['content']}" if "kind" not in s else line(s), lambda s: "source fact")

    earlier = [r for r in live if r["kind"] == "user_stated" and not r["key"] and r not in corrections and r not in conflicts]
    user_turns = [t["id"] for t in store.turns if t["role"] == "user" and t["id"] != turn]
    terse_turns = {r["turn"] for r in recs if r["kind"] == "user_stated" and r.get("terse")}
    recent_ids = set([t for t in user_turns if t not in terse_turns][-recent:])
    ranked = []
    for r in earlier:
        if r.get("pinned"):
            ranked.append((-1, r, "reference material the user gave"))
        elif r["turn"] in recent_ids:
            ranked.append((0, r, "recent turn"))
        elif M.overlap(instruction, r["content"]) >= 0.5:
            ranked.append((1, r, "shares terms with the request"))
        elif IMPERATIVE.search(r["content"]) and DOMAIN.search(r["content"]):
            ranked.append((2, r, "earlier instruction about the space"))
        else:
            drop(r, "not recent, no shared terms, not an instruction about the space")
    ranked.sort(key=lambda x: (x[0], -int((x[1]["turn"] or "t0")[1:])))
    whys = {r["id"]: w for _, r, w in ranked}
    fill("earlier", [(r, r) for _, r, _ in ranked], line, lambda r: whys[r["id"]])

    mscore = {r["id"]: s for s, r in store.search(instruction, k=len(recs) or 1, kinds=("model_inference", "summary"))}
    model_recs = []
    for r in live:
        if r["kind"] not in ("model_inference", "summary"):
            continue
        if r["id"] in working or (r["key"] or "").startswith("draft") or M.overlap(instruction, r["content"]) >= 0.5:
            model_recs.append(r)                             # the current draft's own claims, or relevant to the request
        else:
            drop(r, "model output not relevant to this request")
    model_recs.sort(key=lambda r: (r["id"] not in working, r is not latest, -mscore.get(r["id"], 0), -int((r.get("turn") or "t0")[1:] or 0), r["id"]))
    fill("model", [(r, r) for r in model_recs], lambda r: line(r) + (f"  ({working[r['id']]})" if r["id"] in working else "") + (f"  (summary of {', '.join(r['sources'])})" if r["kind"] == "summary" and r["sources"] else ""),
         lambda r: "latest outputs (what a short follow-up refers to)" if r["id"] in working
         else "unverified model output" if r["kind"] == "model_inference" else "summary, sources kept")

    skipped = [t for t in user_turns if t not in {r["turn"] for r in live if r["id"] in {s['id'] for s in trace['selected']}}]
    heads = {"instruction": "CURRENT INSTRUCTION (the user, now) -- this comes first",
             "treat": "HOW TO TREAT THIS MESSAGE (decided by code from the words and the memory)",
             "corrections": "USER CORRECTIONS -- newest wins; they override everything below, including the current draft",
             "settled": "SETTLED BY THE USER (still valid)",
             "unresolved": "UNRESOLVED -- conflicting statements kept as they are",
             "gaps": "NOT IN MEMORY",
             "sources": "SOURCE FACTS (read by code from files, not by a model -- they describe the current draft; the user's corrections above say what must change)",
             "earlier": "EARLIER USER STATEMENTS (selected; the full conversation is kept on disk, not shown)",
             "model": "MODEL'S EARLIER OUTPUT -- UNVERIFIED. It may be wrong. Never cite it as a fact; the sections above win"}
    parts = []
    for k in ("instruction", "treat", "corrections", "settled", "unresolved", "gaps", "sources", "earlier", "model"):
        if sec.get(k):
            parts.append(f"## {heads[k]}\n" + "\n".join(sec[k]))
            trace["tokens"][k] = sum(estimate_tokens(x) for x in sec[k])
    if skipped:
        parts.append(f"({len(skipped)} earlier user turn(s) not shown: not relevant to this request or replaced.)")
    text = "\n\n".join(parts)
    trace["tokens"]["context"] = estimate_tokens(text)
    trace["tokens"]["total_est"] = trace["tokens"]["context"] + fixed_tokens
    return {"text": text, "trace": trace}


def write_trace(path, trace: dict, **extra) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(trace, **extra), ensure_ascii=False) + "\n")
