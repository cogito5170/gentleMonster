"""gentle_monster frontend engine -- a job (the room) becomes a web page that is measured before it is kept.

Gentle Monster's stores are told as rooms you walk through: a threshold, a void, one hero object, a
route, a few materials pushed to the extreme, one hot accent. The engine carries that into the browser:

    philosophy (Gentle Monster)           what the engine must carry                 where
    ----------------------------------    ---------------------------------------    -------------------------
    the space is the story                content comes only from the job            compose (content-invariant)
    the threshold / the walk              scroll = walking; the route draws itself   compose: threshold, walk
    one hero, a void around it            scale drama + air, measured                judge: drama, air
    materials pushed to the extreme       procedural surfaces from material presets  tokens.matter, _TEX_JS
    one hot accent                        accent share 0.3-4 %                       judge: accent
    kinetic, breathing objects            motion as a gene; never under reduced-motion  tokens.motion, judge V
    experiment, not decoration            genome + operators + measured acceptance   policy (se_new)

and what any frontend tool must carry regardless of taste: design tokens (exported as W3C DTCG),
fluid type, a grid, contrast, phone width, accessible names, heading order, offline, page weight.

    build(job, out_dir, rounds=6) -> {html, tokens, report, ledger, accepted, rejected}

The loop (se_new policy, policy.py): genome0 is read from the job; each round one operator proposes a
genome', the page is composed and judged, and it replaces the base only when V holds, nothing regressed
and J rose. Every decision is appended to `<out>/ledger.jsonl` and to the global π ledger
(`paths.OUT/_engine/policy.jsonl`) that weights which operator is tried next.
"""
from __future__ import annotations

import json
import random
import shutil
from pathlib import Path

from gentle_monster import paths
from gentle_monster.engine import compose, judge, policy, tokens as T


def global_ledger() -> Path:
    return paths.OUT / "_engine" / "policy.jsonl"


def build(job: dict, out_dir, rounds: int = 6, log=print, measure=None) -> dict:
    """`measure(html_path, tokens)` defaults to the browser judge (tests may pass a fake)."""
    measure = measure or judge.measure
    out = Path(out_dir)
    work = out / "_candidates"
    work.mkdir(parents=True, exist_ok=True)
    ledger = out / "ledger.jsonl"
    rng = random.Random(T.seed(job))

    def make(g, name):
        t = T.tokens(job, g)
        h = compose.page(job, t)
        p = work / f"{name}.html"
        p.write_text(h, encoding="utf-8")
        return t, h, p, measure(p, t)

    g = T.genome0(job)
    t, h, p, m = make(g, "r0")
    bad = [k for k, ok in m["V"].items() if not ok]
    policy.append(ledger, {"round": 0, "op": None, "genome": g, "decision": "BASE", "V": m["V"], "J": m["J"], "score": m["score"]})
    log(f"[engine] base {m['score']:.4f} · V {'holds' if not bad else 'fails: ' + ', '.join(bad)} · J {m['J']}")
    best = (g, t, h, p, m)
    refused, acc, rej = set(), 0, 0
    w = policy.weights(policy.read(global_ledger()))
    for r in range(1, rounds + 1):
        op, g2 = policy.choose(best[0], w, rng, exclude=refused)
        if op is None:
            log("[engine] no operator left that changes the genome on this base -- stopping")
            break
        t2, h2, p2, m2 = make(g2, f"r{r}_{op}")
        d = policy.decide(best[4], m2, same_page=(h2 == best[2]))
        row = {"round": r, "op": op, "genome": g2, "decision": d["decision"], "why": d["why"], "dJ": d["dJ"],
               "V": m2["V"], "J": m2["J"], "score": m2["score"], "brand": job["brand"], "title": job["title"]}
        policy.append(ledger, row)
        policy.append(global_ledger(), {k: row[k] for k in ("op", "decision", "dJ", "brand", "title")})
        log(f"[engine] r{r} {op:<13} {d['decision']:<6} {m2['score']:.4f} · {d['why'][0]}")
        if d["decision"] == "ACCEPT":
            best, refused, acc = (g2, t2, h2, p2, m2), set(), acc + 1
        else:
            refused.add(op); rej += 1
    g, t, h, p, m = best
    (out / "index.html").write_text(h, encoding="utf-8")           # exactly the page that was measured
    (out / "tokens.json").write_text(json.dumps(T.dtcg(t), ensure_ascii=False, indent=1), encoding="utf-8")
    report = {"genome": g, "V": m["V"], "J": m["J"], "score": m["score"], "facts": m["facts"], "accepted": acc, "rejected": rej,
              "pi": policy.weights(policy.read(global_ledger())), "ships": all(m["V"].values())}
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    return {"html": str(out / "index.html"), "tokens": str(out / "tokens.json"), "report": str(out / "report.json"),
            "ledger": str(ledger), **report}
