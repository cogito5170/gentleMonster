#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""context eval -- the same cases, three ways of building the model input. See eval/README.md (criteria were
committed before the first run).

    python3 eval/context_eval.py                 input-level metrics, no model call (deterministic)
    python3 eval/context_eval.py --live --repeat 3   + send each input to Gemini N times, code-judge the JSON

before = the code before this change, loaded from git (4eb4ffa); naive = whole transcript + keyword notes;
after  = pipeline.revise run for real with a model that only records the prompt.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["GENTLE_MONSTER_OUT"] = tempfile.mkdtemp(prefix="gm-eval-")

from gentle_monster import context as C, memory as M, paths, pipeline, spec, synopsis as SY  # noqa: E402

BEFORE = "4eb4ffa"
REAL = json.loads((ROOT / "data/user_questions/questions.semantic.json").read_text(encoding="utf-8"))["questions"]
Q = {q["id"]: q["text"] for q in REAL}


def old_module(name: str):
    src = subprocess.run(["git", "show", f"{BEFORE}:gentle_monster/{name}.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    m = types.ModuleType(f"old_{name}")
    exec(compile(src, f"{BEFORE}:{name}.py", "exec"), m.__dict__)
    return m


def chatter(n: int) -> list:
    """n turns of the real session's portfolio work (Q22-Q44) with short assistant replies -- unrelated to the space."""
    ids = list(range(22, 45))
    out = []
    for i in range(n // 2):
        q = ids[i % len(ids)]
        out.append(("user", Q[q]))
        out.append(("model", f"네, 정리했습니다. {Q[q][:40]} 에 대해 세 가지 안을 제안합니다: 첫째 문장을 짧게, 둘째 사진을 하나로, 셋째 흐름을 유지."))
    return out


def ex(over=None) -> dict:
    j = copy.deepcopy(spec.examples()["gm"])
    for k, v in (over or {}).items():
        a, b = k.split(".")
        j[a][b] = v
    return j


CASES = [
    dict(id="S1", case="초기 사실을 나중에 정정", job=ex(),
         turns=[("user", "비 오는 밤의 성수 플래그십. 벽은 노출 콘크리트로 마감해줘"),
                ("model", "벽을 노출 콘크리트로 마감한 초안입니다. 입구에는 철제 관절 두 개가 섭니다."),
                ("user", "좋아. 정지점은 세 개면 돼"), ("model", "네, 정지점 세 개로 두었습니다."),
                ("user", "아니, 벽은 콘크리트 말고 나무로 해줘"), ("model", "알겠습니다.")],
         final="방금 거 입구 쪽 조명을 조금 더 어둡게 바꿔줘",
         inn=[["room.wall = wood", "콘크리트 말고 나무로"]], not_in=["노출 콘크리트로 마감"],
         out={"room.wall": "wood"}, out_not={"room.wall": "concrete"}),
    dict(id="S2", case="모델의 과거 추론 ↔ 원자료", job=ex(),
         turns=[("user", "런웨이가 있는 성수 플래그십으로 해줘"),
                ("model", "이 공간은 폭 24m라서 30m 런웨이가 충분히 들어갑니다."),
                ("user", "좋아")],
         final="방금 거 런웨이 동선을 공간 크기에 맞게 다시 잡아줘",
         inn=[["layout.W: 20"]], not_in=["폭 24m"], out={"layout.W": 20}, out_not={"layout.W": 24}),
    dict(id="S3", case="오래된 기억 ↔ 현재 지시", job=ex(),
         turns=[("user", "어두운 극장 같은 매장. 조명은 어두운 갤러리로 해줘"), ("model", "어두운 갤러리 조명으로 잡았습니다."),
                ("user", "입구는 좁게")],
         final="방금 거 이번엔 조명을 자연광으로 바꿔줘",
         inn=[["room.light = daylight", "자연광"]], not_in=["어두운 갤러리로 해줘", "어두운 갤러리 조명으로 잡았"],
         out={"room.light": "daylight"}, out_not={"room.light": "dark_gallery"}),
    dict(id="S4a", case="관련 없는 대화 40턴", job=ex(),
         turns=[("user", "비 오는 밤의 성수 플래그십. 벽은 석회로 마감해줘"), ("model", "석회 벽으로 잡았습니다.")] + chatter(40),
         final="방금 거 동선을 더 길게 바꿔줘", inn=[["lime_plaster", "석회"]], not_in=[], out={"room.wall": "lime_plaster"}, out_not={}),
    dict(id="S4b", case="관련 없는 대화 160턴", job=ex(),
         turns=[("user", "비 오는 밤의 성수 플래그십. 벽은 석회로 마감해줘"), ("model", "석회 벽으로 잡았습니다.")] + chatter(160),
         final="방금 거 동선을 더 길게 바꿔줘", inn=[["lime_plaster", "석회"]], not_in=[], out={"room.wall": "lime_plaster"}, out_not={}),
    dict(id="S5", case="근거가 없거나 검색 안 됨", job=ex(),
         turns=[("user", "어두운 극장 같은 성수 매장"), ("model", "초안입니다."), ("user", "입구는 좁게")],
         final="방금 거 지난번에 정한 색온도 그대로 유지해서 조명 바꿔줘",
         inn=[["NOT IN MEMORY"]], not_in=[], out={}, out_not={}, out_text_not=[r"\b\d{4}\s?K\b"]),
    dict(id="S6", case="요약에 잘못된 과거 답", job=ex({"room.floor": "granite"}),
         turns=[("user", "비 오는 밤 플래그십, 폭 20m, 바닥은 화강암으로 해줘"), ("model", "초안입니다.")] + chatter(6)
         + [("summary", "대화 간추림 -- 마지막 답 머리: 폭 24m, 바닥은 콘크리트로 확정했습니다. 동선은 시계 방향.", ["t2"])],
         final="방금 거 천장만 더 어둡게 바꿔줘",
         inn=[["room.floor = granite", "화강암"]], not_in=["폭 24m", "콘크리트로 확정"],
         out={"room.floor": "granite", "layout.W": 20}, out_not={"layout.W": 24, "room.floor": "concrete"}),
    # S6b was added after the first run: in S6 the request shares no words with the note, so the note is left out
    # as irrelevant and its cut-out path is never exercised. Here the request names the floor and the width.
    dict(id="S6b", case="요약에 잘못된 과거 답 (요약이 검색될 때)", job=ex({"room.floor": "granite"}),
         turns=[("user", "비 오는 밤 플래그십, 폭 20m, 바닥은 화강암으로 해줘"), ("model", "초안입니다.")] + chatter(6)
         + [("summary", "대화 간추림 -- 마지막 답 머리: 폭 24m, 바닥은 콘크리트로 확정했습니다. 동선은 시계 방향.", ["t2"])],
         final="방금 거 바닥 마감과 폭은 확정한 대로 두고 천장만 더 어둡게 바꿔줘",
         inn=[["room.floor = granite", "화강암"]], not_in=["폭 24m", "콘크리트로 확정"],
         out={"room.floor": "granite", "layout.W": 20}, out_not={"layout.W": 24, "room.floor": "concrete"}),
    dict(id="S7", case="정정 범위 불명확", job=ex(),
         turns=[("user", "벽은 노출 콘크리트, 바닥도 콘크리트로 해줘"), ("model", "초안입니다.")],
         final="아니 콘크리트 말고 나무로", inn=[], not_in=[], ask=True, out={}, out_not={}),
    dict(id="S8", case="실제 대화의 정정 (Q25→Q34)", job=ex(), direct=True,
         turns=[("user", Q[25]), ("model", "SPA는 STYLIST, PHOTOGRAPHER, ARCHITECT를 뜻하므로 'Where did you last stop?' 과 잘 연결됩니다.")]
         + [x for q in range(26, 34) for x in (("user", Q[q]), ("model", "네, 반영했습니다."))] + [("user", Q[34])],
         final="커버 페이지의 SPA 풀이 문구를 정리해줘",
         inn=[["STYLE, PASSION, ARCHITECTURE"]], not_in=["STYLIST, PHOTOGRAPHER, ARCHITECT"], out={}, out_not={}),
]


def frame(block: str, job: dict) -> str:
    return SY.revise_prompt(block, job)


def context_block(prompt: str) -> str:
    return prompt.split("\n\nKeep everything in the draft")[0]


# ---------------------------------------------------------------- the three conditions
def build_before(c, old_intent, old_syn) -> dict:
    jobs = ["case"]
    routes = [old_intent.parse(t, jobs)["action"] for r, t, *_ in c["turns"] if r == "user" and re.search(r"말고|아니라|대신", t)]
    it = old_intent.parse("!젠몬 " + c["final"], jobs)
    if it["action"] == "make":
        return {"prompt": old_syn.prompt(it["brief"], ""), "block": it["brief"], "route": it["action"], "correction_routes": routes, "called": True}
    return {"prompt": "", "block": "", "route": it["action"], "correction_routes": routes, "called": False}


def build_naive(c) -> dict:
    lines, notes = [], []
    for r, t, *rest in c["turns"]:
        if r == "summary":
            notes.append(t)
        else:
            lines.append(("User: " if r == "user" else "Assistant: ") + t)
            notes.append(t)
    terms = set(re.findall(r"[0-9a-z가-힣]{2,}", c["final"].lower()))
    hits = sorted(notes, key=lambda n: -sum(n.lower().count(w) for w in terms))[:5]
    block = "Conversation so far:\n" + "\n".join(lines) + "\n\nRelevant memory:\n" + "\n".join(f"- {h}" for h in hits) + f"\n\nUser: {c['final']}"
    return {"prompt": frame(block, c["job"]), "block": block, "called": True}


def build_after(c) -> dict:
    name = f"eval_{c['id']}"
    pipeline.save_job(name, c["job"])
    st = M.open_job(name)
    pipeline._record_draft(st, c["job"], "model:eval-setup", log=lambda s: None)
    for r, t, *rest in c["turns"]:
        if r == "user":
            st.ingest_user(t)
        elif r == "model":
            st.add_model_turn(t)
        else:
            st.add_summary(t, rest[0] if rest else [])
    if c.get("direct"):                                        # not a space revision: the same builder, called directly
        eff = st.ingest_user(c["final"])
        fixed = C.estimate_tokens(frame("", c["job"]))
        ctx = C.build(st, c["final"], fixed_tokens=fixed, sources=C.job_facts(c["job"]), turn=eff["turn"])
        return {"prompt": frame(ctx["text"], c["job"]), "block": ctx["text"], "trace": ctx["trace"], "called": True, "store": st}
    seen = []

    def capture(p):
        seen.append(p)
        j = copy.deepcopy(c["job"])                            # the eval measures the input; a job that passes the code checks will do
        for k, v in c["out"].items():
            a, b = k.split(".")
            j[a][b] = v
        return json.dumps(j)
    r = pipeline.revise(name, c["final"], ask=capture, verify_ask=False, log=lambda s: None)
    st = M.open_job(name)
    if r["asked"]:
        return {"prompt": "", "block": "", "asked": r["asked"], "called": bool(seen), "store": st, "trace": None}
    return {"prompt": seen[0], "block": context_block(seen[0]), "trace": r["trace"], "called": True, "store": st}


# ---------------------------------------------------------------- metrics
def model_texts(c) -> "list[str]":
    """Distinctive pieces of what only a model (or a summary) said -- each sentence's first 18 characters,
    leaving out pieces that also occur in a user turn (a reply that quotes the user is not a model claim)."""
    users = " ".join(t for r, t, *_ in c["turns"] if r == "user") + " " + c["final"]
    out = []
    for r, t, *_ in c["turns"]:
        if r in ("model", "summary"):
            out += [s.strip()[:18] for s in re.split(r"(?<=[.!?다])\s+", t) if len(s.strip()) >= 12]
    return sorted({p for p in out if p not in users})


def measure(c, b: dict) -> dict:
    block = b["block"]
    fact = block.split("## MODEL'S EARLIER OUTPUT")[0]
    inn = all(any(alt in block for alt in alts) for alts in c["inn"]) if c["inn"] else None
    bad = [s for s in c["not_in"] if s in block]
    as_fact = [s for s in model_texts(c) if s in fact]
    return {"called": b["called"], "in": inn, "stale_in_input": len(bad), "stale": bad, "model_as_fact": len(as_fact),
            "tokens_block": C.estimate_tokens(block), "tokens_input": C.estimate_tokens(b["prompt"]) if b["prompt"] else 0}


def trace_check(c, b) -> "list[str]":
    """after only: every superseded/retracted record is in the trace's excluded list (id level, not strings)."""
    if not b.get("trace"):
        return []
    st = b["store"]
    # records the new draft replaced *after* the context was built (the old draft, its checks) were valid at build time
    post = {r["id"] for r in st.all() if r["key"] == "draft" and r["status"] == "active"}
    gone = {r["id"] for r in st.all() if r["status"] != "active" and r.get("superseded_by") not in post}
    excl = {e["id"] for e in b["trace"]["excluded"]}
    shown = {s["id"] for s in b["trace"]["selected"]}
    return sorted(gone - excl) + sorted(gone & shown)


# ---------------------------------------------------------------- live (needs GEMINI_API_KEY)
def judge(c, job: dict) -> dict:
    def got(k):
        a, b = k.split(".")
        return (job.get(a) or {}).get(b)
    ok = all(str(got(k)) == str(v) or (isinstance(v, (int, float)) and got(k) is not None and abs(float(got(k)) - v) < .05) for k, v in c["out"].items())
    bad = [k for k, v in c["out_not"].items() if str(got(k)) == str(v) or (isinstance(v, (int, float)) and got(k) is not None and abs(float(got(k)) - v) < .05)]
    txt = json.dumps(job, ensure_ascii=False)
    invented = [p for p in c.get("out_text_not", []) if re.search(p, txt)]
    return {"correct": ok, "adopted_wrong": bool(bad), "invented": bool(invented)}


def live(cases, built, repeat: int) -> dict:
    from gentle_monster import llm
    if not llm.key():
        return {"ran": False, "why": "no GEMINI_API_KEY in this environment -- output-level metrics were NOT measured"}
    pin, pout = float(os.environ.get("GM_PRICE_IN", "0.30")), float(os.environ.get("GM_PRICE_OUT", "2.50"))
    rows = {}
    for c in cases:
        if c.get("direct") or c.get("ask"):
            continue
        for cond in ("before", "naive", "after"):
            b = built[c["id"]][cond]
            res = []
            for _ in range(repeat):
                if not b["called"] or not b["prompt"]:
                    res.append(dict(judge(c, c["job"]), latency=0.0, tin=0, tout=0, note="no model call"))
                    continue
                t = time.time()
                try:
                    job = SY._parse(llm.ask(b["prompt"]))
                    j = judge(c, job)
                except Exception as e:                       # noqa: BLE001 -- a failed call is a result, not a skip
                    j = {"correct": False, "adopted_wrong": False, "invented": False, "error": f"{type(e).__name__}"}
                res.append(dict(j, latency=time.time() - t, tin=llm.LAST.get("prompt_tokens") or 0, tout=llm.LAST.get("output_tokens") or 0))
            rate = [1.0 if r["correct"] else 0.0 for r in res]
            rows[(c["id"], cond)] = {"correct_rate": sum(rate) / len(rate), "sd": statistics.pstdev(rate),
                                     "adopted_wrong": sum(r["adopted_wrong"] for r in res), "invented": sum(r["invented"] for r in res),
                                     "latency_s": statistics.mean(r["latency"] for r in res),
                                     "tokens_in": statistics.mean(r["tin"] for r in res), "tokens_out": statistics.mean(r["tout"] for r in res),
                                     "usd": sum(r["tin"] * pin + r["tout"] * pout for r in res) / 1e6}
    return {"ran": True, "rows": rows, "price_assumed": (pin, pout)}


# ---------------------------------------------------------------- run
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--json", default="", help="write the results here")
    a = ap.parse_args(argv)
    old_intent, old_syn = old_module("intent"), old_module("synopsis")
    built, res, fails = {}, {}, []
    for c in CASES:
        built[c["id"]] = {"before": build_before(c, old_intent, old_syn), "naive": build_naive(c), "after": build_after(c)}
        res[c["id"]] = {k: measure(c, v) for k, v in built[c["id"]].items()}
        res[c["id"]]["after"]["trace_mismatch"] = trace_check(c, built[c["id"]]["after"])
        b = built[c["id"]]["after"]
        res[c["id"]]["after"]["asked"] = bool(b.get("asked"))
        if b.get("store"):
            res[c["id"]]["after"]["superseded_now"] = sum(1 for r in b["store"].all() if r["status"] != "active" and r["kind"] == "user_stated")

    print(f"{'case':<5} {'cond':<7} {'call':<5} {'in':<6} {'stale':<6} {'model→fact':<11} {'tok(ctx)':>9} {'tok(input)':>10}  note")
    for c in CASES:
        for cond in ("before", "naive", "after"):
            m = res[c["id"]][cond]
            note = ""
            if cond == "before":
                note = f"route {built[c['id']]['before']['route']}" + (f"; corrections routed to {built[c['id']]['before']['correction_routes']}" if built[c['id']]['before']['correction_routes'] else "")
            if cond == "after" and m.get("asked"):
                note = "asked the user; no model call"
            if cond == "after" and m.get("trace_mismatch"):
                note += f" TRACE MISMATCH {m['trace_mismatch']}"
            print(f"{c['id']:<5} {cond:<7} {str(m['called']):<5} {str(m['in']):<6} {m['stale_in_input']:<6} {m['model_as_fact']:<11} {m['tokens_block']:>9} {m['tokens_input']:>10}  {note}")

    # criteria (eval/README.md), after only
    A = {k: v["after"] for k, v in res.items()}
    N = {k: v["naive"] for k, v in res.items()}
    crit = [
        ("1 correction retained (S1 S3 S6 S8; S6b added later)", all(A[k]["in"] for k in ("S1", "S3", "S6", "S6b", "S8"))),
        ("2 stale memory in input = 0, trace agrees", all(A[k]["stale_in_input"] == 0 and not A[k]["trace_mismatch"] for k in A)),
        ("3 model claims in fact sections = 0", all(A[k]["model_as_fact"] == 0 for k in A)),
        ("4a S5 says 'not in memory'", bool(A["S5"]["in"])),
        ("4b S7 asks, no model call, nothing replaced", A["S7"]["asked"] and A["S7"]["superseded_now"] == 0),
        ("5a S4b input <= 50% of naive and <= 12000", A["S4b"]["tokens_input"] <= .5 * N["S4b"]["tokens_input"] and A["S4b"]["tokens_input"] <= 12000),
        ("5b S4 40->160 turns: after grows <= 10%", A["S4b"]["tokens_input"] <= 1.10 * A["S4a"]["tokens_input"]),
    ]
    print("\ncriteria (after):")
    for name, ok in crit:
        print(("  PASS " if ok else "  FAIL ") + name)
        if not ok:
            fails.append(name)
    print(f"\nS4 tokens (input est.): naive 40->160 turns {N['S4a']['tokens_input']} -> {N['S4b']['tokens_input']} · "
          f"after {A['S4a']['tokens_input']} -> {A['S4b']['tokens_input']}")
    L = live(CASES, built, a.repeat) if a.live else {"ran": False, "why": "not requested (--live)"}
    if L["ran"]:
        print(f"\nlive ({a.repeat} repeats, price assumed USD/1M in {L['price_assumed'][0]} out {L['price_assumed'][1]}):")
        for (cid, cond), r in L["rows"].items():
            print(f"  {cid:<5} {cond:<7} correct {r['correct_rate']:.2f} (sd {r['sd']:.2f}) · adopted wrong {r['adopted_wrong']} · invented {r['invented']} · "
                  f"{r['latency_s']:.1f} s · in {r['tokens_in']:.0f} / out {r['tokens_out']:.0f} tok · ${r['usd']:.4f}")
    else:
        print(f"\nlive: not run -- {L['why']}")
    if a.json:
        Path(a.json).write_text(json.dumps({"input": res, "criteria": dict(crit), "live": {"ran": L["ran"], "why": L.get("why", ""),
                                            "rows": {f"{k[0]}/{k[1]}": v for k, v in L.get("rows", {}).items()}}},
                                           ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
