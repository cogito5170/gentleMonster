#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""follow-up eval -- short follow-ups ("고쳐") and displeasure, before vs after. Criteria: docs/FOLLOWUP.md §4,
committed before this script (583b017). Input level only, no model call:

    python3 eval/followup_eval.py

before = memory.py + context.py of BEFORE, loaded from git; after = the working tree.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gentle_monster import context as C_new, memory as M_new, spec  # noqa: E402

BEFORE = "6acff99"


def old_pair():
    def load(name, extra=None):
        src = subprocess.run(["git", "show", f"{BEFORE}:gentle_monster/{name}.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        m = types.ModuleType(f"old_{name}")
        exec(compile(src, f"{BEFORE}:{name}.py", "exec"), m.__dict__)
        m.__dict__.update(extra or {})
        return m
    M = load("memory")
    return M, load("context", {"M": M})


CASES_10 = "아래 자소서 사례 10개를 참고해.\n\n" + "\n\n".join(
    f"[사례 {i}] 저는 대학 {i}학년 때 동아리 회장을 맡아 설문 {20 + i}건으로 모집 방식을 바꿨고, 지원자가 {10 + i}명에서 {25 + i}명으로 늘었습니다. "
    "이 경험에서 고객의 말을 먼저 듣는 태도를 배웠습니다." for i in range(1, 11))
QUESTION = "문항: 우리 회사에 지원한 동기와 입사 후 포부를 800자 이내로 작성하시오. 지원 직무는 서비스 기획."
LETTER = [("user", CASES_10), ("model", "사례 10개를 읽었습니다. 공통 구조는 경험-수치-포부입니다."),
          ("user", QUESTION), ("model", "[초안 v1] 저는 고객의 말을 먼저 듣는 기획자입니다.")]
for v in range(2, 6):
    LETTER += [("user", "고쳐"), ("model", f"[초안 v{v}] 저는 고객의 말을 먼저 듣는 기획자입니다. (v{v})"),
               ("user", "자소서 보고 스스로 피드백 해봐"), ("model", f"[자기 피드백 {v}] 둘째 문단의 수치가 약합니다.")]


def letter_run(M, C):
    """C1 latest output kept, C2 사례 · 문항 kept, C3 value-less records under USER CORRECTIONS."""
    st = M.Store(Path(tempfile.mkdtemp()) / "m.jsonl")
    ids, latest, c1, c2, c3 = {}, None, [0, 0], [0, 0], 0
    for role, text in LETTER:
        if role == "model":
            latest = st.add_model_turn(text)
            continue
        e = st.ingest_user(text)
        ids.setdefault(text, e["record"])
        tr = C.build(st, text, turn=e["turn"])["trace"]
        sel = {x["id"]: x["section"] for x in tr["selected"]}
        if latest and len(text) < 30:
            c1[1] += 1
            c1[0] += latest in sel
        if text not in (CASES_10, QUESTION):
            c2[1] += 1
            c2[0] += ids[CASES_10] in sel and ids[QUESTION] in sel
        c3 += sum(1 for i, sec in sel.items() if sec == "corrections" and no_value(st.get(i)["content"]))
    return c1, c2, c3


def no_value(text):
    return not M_new.extract(text) and not M_new.correction_parts(text)


def design(M):
    st = M.Store(Path(tempfile.mkdtemp()) / "m.jsonl")
    st.ingest_user("비 오는 밤의 성수 플래그십. 벽은 노출 콘크리트로 마감해줘")
    st.add_model_turn("벽을 노출 콘크리트로 마감한 초안입니다.")
    return st


def letter(M):
    st = M.Store(Path(tempfile.mkdtemp()) / "m.jsonl")
    st.ingest_user(CASES_10)
    st.ingest_user(QUESTION)
    st.add_model_turn("[초안 v1] 저는 고객의 말을 먼저 듣는 기획자입니다.")
    return st


def dispute_run(M, C, cases):
    """C3 (pressure on the next turn), C4 stored value flipped, C5 hold-and-ask directive with its backing."""
    src = C_new.job_facts(spec.examples()["gm"])
    pressure = flips = hold = n = 0
    for c in cases:
        if c["case"] != "unsupported":
            continue
        n += 1
        st = design(M)
        slots = lambda: {r["key"]: r["value"] for r in st.active("user_stated") if r["key"]}  # noqa: E731
        was = slots()
        e = st.ingest_user(c["text"])
        T = C.build(st, c["text"], sources=src, turn=e["turn"])["text"]
        flips += slots() != was
        hold += "do not change it" in T and c["key"] in T.split("## HOW TO TREAT")[-1] if "## HOW TO TREAT" in T else 0
        e2 = st.ingest_user("다음 안 보여줘")
        tr = C.build(st, "다음 안 보여줘", sources=src, turn=e2["turn"])["trace"]
        pressure += any(x["section"] == "corrections" and no_value(st.get(x["id"])["content"]) for x in tr["selected"])
    return n, pressure, flips, hold


def accuracy(cases):
    src = C_new.job_facts(spec.examples()["gm"])
    good, miss = 0, []
    for c in cases:
        st = {"design": design, "letter": letter}.get(c["session"], lambda M: M.Store(Path(tempfile.mkdtemp()) / "m.jsonl"))(M_new)
        e = st.ingest_user(c["text"])
        r = M_new.classify(c["text"], st, src if c["session"] == "design" else (), exclude_turn=e["turn"])
        hit = r["case"] == c["case"] and (c["case"] != "unsupported" or r["key"] == c.get("key"))
        good += hit
        if not hit:
            miss.append(f"{c['text']!r}: want {c['case']}, got {r['case']}")
    return good, len(cases), miss


def main():
    cases = json.loads((ROOT / "eval/followup_cases.json").read_text(encoding="utf-8"))["cases"]
    rows = {}
    for name, (M, C) in (("before", old_pair()), ("after", (M_new, C_new))):
        c1, c2, c3 = letter_run(M, C)
        n, pressure, flips, hold = dispute_run(M, C, cases)
        rows[name] = dict(c1=c1, c2=c2, c3=c3, n=n, pressure=pressure, flips=flips, hold=hold)
    print(f"{'criterion':58} {'before':>10} {'after':>10}")
    f = lambda a: f"{a[0]}/{a[1]}"  # noqa: E731
    print(f"{'C1 short follow-up turn: latest output in the input':58} {f(rows['before']['c1']):>10} {f(rows['after']['c1']):>10}")
    print(f"{'C2 later turns: 사례 and 문항 both in the input':58} {f(rows['before']['c2']):>10} {f(rows['after']['c2']):>10}")
    print(f"{'C3 value-less lines under USER CORRECTIONS (letter run)':58} {rows['before']['c3']:>10} {rows['after']['c3']:>10}")
    print(f"{'C3 unsupported dispute shown as a correction next turn':58} "
          f"{rows['before']['pressure']:>8}/{rows['before']['n']} {rows['after']['pressure']:>8}/{rows['after']['n']}")
    print(f"{'C4 unsupported dispute changed a stored value':58} "
          f"{rows['before']['flips']:>8}/{rows['before']['n']} {rows['after']['flips']:>8}/{rows['after']['n']}")
    print(f"{'C5 hold-and-ask directive with its backing':58} "
          f"{rows['before']['hold']:>8}/{rows['before']['n']} {rows['after']['hold']:>8}/{rows['after']['n']}")
    g, n, miss = accuracy(cases)
    print(f"{'C6 classify() on eval/followup_cases.json':58} {'-':>10} {f'{g}/{n}':>10}")
    for m in miss:
        print("   miss:", m)
    return rows, (g, n)


if __name__ == "__main__":
    main()
