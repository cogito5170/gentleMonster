# -*- coding: utf-8 -*-
"""Does the draft do what the user said? Code first, a separate model call only where code cannot read.

    code_check(job, store)   every active user slot (brand, layout.W/D/H, room.floor/wall/ceiling/light)
                             compared with the job read from the file -> supported | violated
    problems(job, store)     the violated ones as facts for the retry prompt ("you were told ... ; room.wall is concrete")
    model_check(question, sources, claim, ask)
                             a fresh call that sees ONLY the question, the source and the claim -- no conversation,
                             no earlier drafts (Dhuliawala et al. 2023: verification answered apart from the draft
                             copies fewer of its errors). Verdict: supported | contradicted | insufficient.

A model verifier's "supported" is still a model's opinion: it is reported, never promoted to a fact
(memory.Store.promote refuses model evidence). A code "supported" is a measurement.
"""
from __future__ import annotations

import json
import re

CHECKABLE = ("brand", "layout.W", "layout.D", "layout.H", "room.floor", "room.wall", "room.ceiling", "room.light")


def _got(job: dict, key: str):
    if key == "brand":
        return job.get("brand")
    a, b = key.split(".", 1)
    return (job.get(a) or {}).get(b)


def code_check(job: dict, store) -> "list[dict]":
    out = []
    for r in store.active("user_stated"):
        if r["key"] not in CHECKABLE:
            continue
        got = _got(job, r["key"])
        if r["key"].startswith("layout."):
            ok = got is not None and abs(float(got) - float(r["value"])) <= 0.05
        elif r["key"] == "brand":
            ok = got is not None and str(r["value"]).lower() in str(got).lower()
        else:
            ok = got == r["value"]
        out.append({"id": r["id"], "turn": r["turn"], "key": r["key"], "want": r["value"], "got": got,
                    "verdict": "supported" if ok else "violated", "by": "code"})
    return out


def problems(job: dict, store) -> "list[str]":
    return [f"the user said {c['key']} = {c['want']} ({c['turn']}); in your answer {c['key']} is {c['got']!r}"
            for c in code_check(job, store) if c["verdict"] == "violated"]


def model_prompt(question: str, sources: str, claim: str) -> str:
    return ("You check one claim against one source. Use only the source below; do not use outside knowledge.\n"
            f"Question the user asked:\n{question}\n\nSource:\n{sources}\n\nClaim to check:\n{claim}\n\n"
            'Answer with JSON only: {"verdict": "supported" | "contradicted" | "insufficient", "evidence": "<the words of '
            'the source that decide it, or empty>"}. If the source does not settle it, the verdict is insufficient.')


def model_check(question: str, sources: str, claim: str, ask) -> dict:
    try:
        txt = ask(model_prompt(question, sources, claim))
        t = re.sub(r"^```(?:json)?\s*|\s*```$", "", (txt or "").strip())
        d = json.loads(t[t.find("{"):t.rfind("}") + 1])
        v = d.get("verdict")
        if v not in ("supported", "contradicted", "insufficient"):
            v = "insufficient"
        return {"verdict": v, "evidence": str(d.get("evidence", ""))[:300], "by": "model"}
    except Exception as e:                                     # noqa: BLE001 -- a failed check is reported as such, not as a pass
        return {"verdict": "unchecked", "evidence": f"{type(e).__name__}: {e}"[:200], "by": "model"}
