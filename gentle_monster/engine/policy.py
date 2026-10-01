"""se_new policy, applied to design: a page is changed only when the change is measured to be better.

    (genome, page) -> operator -> (genome', page') -> judge -> decide -> ACCEPT | REJECT

    ACCEPT  <=>  same content  ∧  V(page')  ∧  no J component fell  ∧  J(page') > J(page) + ε

Order matters (se_new policy.py): the invariants come **before** the objective. If content differs or
V does not hold, ΔJ is not even computed -- a number computed there would read like evidence.

  * same content   a candidate may change how the room is told, never what is told. Different visible
                   text means the judge measured a different thing (se_new: bias check) -> REJECT
  * V              every invariant of the judge holds on the candidate. Unknown is not a pass
  * no regression  every J component >= the base's. A page that gains drama by losing measure is not an
                   improvement, it is an oscillation (se_new: R(S') >= R(S) is a condition, not a term)
  * ΔJ > ε         and at least the mean must rise
  * same page      a genome step that produces byte-identical HTML is rejected as "nothing changed"

**The default is REJECT.** Every decision, rejections included, is appended to a ledger -- what was
tried and failed is the material for the next choice.

π -- how the engine chooses what to try -- learns from the global ledger: an operator's weight is its
Laplace-smoothed acceptance rate over the mean, clamped to [0.25, 4] so no operator is ever dropped
(an operator never tried again can never prove itself again) and none takes over. π0 is uniform:
a fair policy first, a clever one only once it is earned.
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

from gentle_monster.engine.tokens import GENES

EPS = 0.0
FLOOR, CEIL = 0.25, 4.0


def _step(g: dict, gene: str, d: int) -> dict:
    vals = GENES[gene]
    i = vals.index(g[gene]) + d
    if gene in ("mast", "voice", "motion", "order"):          # categorical: cycle
        i %= len(vals)
    if not 0 <= i < len(vals):
        return dict(g)
    return dict(g, **{gene: vals[i]})


OPERATORS = {
    "scale-up": lambda g: _step(g, "ratio", 1), "scale-down": lambda g: _step(g, "ratio", -1),
    "air-up": lambda g: _step(g, "air", 1), "air-down": lambda g: _step(g, "air", -1),
    "grid-finer": lambda g: _step(g, "cols", 1), "grid-coarser": lambda g: _step(g, "cols", -1),
    "tension-up": lambda g: _step(g, "tension", 1), "tension-down": lambda g: _step(g, "tension", -1),
    "masthead": lambda g: _step(g, "mast", 1), "voice": lambda g: _step(g, "voice", 1),
    "motion": lambda g: _step(g, "motion", 1), "sequence": lambda g: _step(g, "order", 1),
}


def decide(base: dict, cand: dict, same_page: bool = False, eps: float = EPS) -> dict:
    """base, cand: judge.measure results. Returns {decision, why, dJ}."""
    if not (base and cand):
        return {"decision": "REJECT", "why": ["both measurements are needed"], "dJ": None}
    if same_page:
        return {"decision": "REJECT", "why": ["the operator produced the same page -- nothing changed"], "dJ": None}
    if base.get("content") != cand.get("content"):
        return {"decision": "REJECT", "why": ["visible content differs -- the judge would be comparing two different pages"], "dJ": None}
    failed = [k for k, ok in cand["V"].items() if not ok]
    if failed:
        return {"decision": "REJECT", "why": ["invariant failed: " + ", ".join(failed) + " -- J not measured against the base"], "dJ": None}
    fell = [f"{k} {base['J'][k]} -> {cand['J'][k]}" for k in base["J"] if cand["J"].get(k, -1) < base["J"][k]]
    dJ = round(cand["score"] - base["score"], 4)
    if fell:
        return {"decision": "REJECT", "why": ["regression: " + "; ".join(fell)], "dJ": dJ}
    if dJ <= eps:
        return {"decision": "REJECT", "why": [f"ΔJ {dJ:+.4f} does not clear ε {eps}"], "dJ": dJ}
    up = [f"{k} {base['J'][k]} -> {cand['J'][k]}" for k in base["J"] if cand["J"][k] > base["J"][k]]
    return {"decision": "ACCEPT", "why": ["V holds, content unchanged, no component fell", "up: " + "; ".join(up), f"ΔJ {dJ:+.4f}"], "dJ": dJ}


# ---------------------------------------------------------------- ledger + π
def append(ledger: Path, row: dict) -> dict:
    ledger = Path(ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    row = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **row}
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read(ledger: Path) -> "list[dict]":
    ledger = Path(ledger)
    if not ledger.is_file():
        return []
    out = []
    for line in ledger.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def weights(rows) -> "dict[str, float]":
    """π from decisions. No rows -> π0 (every weight 1.0)."""
    tried = {k: 0 for k in OPERATORS}
    acc = {k: 0 for k in OPERATORS}
    for r in rows:
        op = r.get("op")
        if op in tried and r.get("decision") in ("ACCEPT", "REJECT"):
            tried[op] += 1
            acc[op] += r["decision"] == "ACCEPT"
    rate = {k: (acc[k] + 1) / (tried[k] + 2) for k in OPERATORS}
    mean = sum(rate.values()) / len(rate)
    return {k: round(min(CEIL, max(FLOOR, rate[k] / mean)), 3) for k in OPERATORS}


def choose(g: dict, w: dict, rng: random.Random, exclude=()) -> "tuple[str, dict] | tuple[None, None]":
    """A weighted draw among operators that change the genome and were not already refused on this base."""
    ops = [k for k in sorted(OPERATORS) if k not in exclude and OPERATORS[k](g) != g]
    if not ops:
        return None, None
    op = rng.choices(ops, weights=[w.get(k, 1.0) for k in ops])[0]
    return op, OPERATORS[op](g)
