"""memory · context · verify · revise: the rules of the session memory, each held by a case that breaks it.
No model, no browser, no network. Run: python3 tests/test_memory.py
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
from pathlib import Path

뿌리 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(뿌리))
임시 = tempfile.mkdtemp(prefix="gmmem-")
os.environ["GENTLE_MONSTER_OUT"] = 임시

from gentle_monster import context as C, discord_cmd, intent, memory as M, pipeline, spec, synopsis, verify  # noqa: E402

FAIL = []


def ok(cond, what):
    print(("  ok  " if cond else "  FAIL ") + what)
    if not cond:
        FAIL.append(what)


def store():
    return M.Store(Path(tempfile.mkdtemp(dir=임시)) / "memory.jsonl")


print("== memory: a correction replaces, nothing is deleted ==")
s = store()
e1 = s.ingest_user("비 오는 밤의 성수 플래그십. 벽은 노출 콘크리트로 마감, 바닥은 폴리싱 콘크리트")
wall1 = next(r for r in s.all() if r["key"] == "room.wall")
e2 = s.ingest_user("아니, 벽은 콘크리트 말고 나무로 해줘")
wall2 = next(r for r in s.active("user_stated") if r["key"] == "room.wall")
ok(wall2["value"] == "wood" and s.get(wall1["id"])["status"] == "superseded", "the newer user statement wins (room.wall concrete -> wood)")
ok(s.get(wall1["id"])["superseded_by"] == wall2["id"] and wall1["id"] in wall2["supersedes"], "the replacement is linked both ways")
ok(len(s.all()) >= 5 and wall1["id"] in {r["id"] for r in s.all()}, "the old record is kept, not deleted")
floor = next(r for r in s.active() if r["key"] == "room.floor")
ok(floor["value"] == "polished_concrete", "a correction of the wall leaves the floor alone")
s2 = M.Store(s.path)
ok({r["id"]: r["status"] for r in s2.all()} == {r["id"]: r["status"] for r in s.all()} and len(s2.turns) == 2, "the log reloads to the same state")
ok(all(set(r) >= {"id", "content", "kind", "source", "created_at", "updated_at", "status"} for r in s.all()),
   "every record has id · content · kind · source · created/updated · status")

print("\n== memory: what may not become a fact ==")
for kind, src, why in (("user_stated", {"type": "model", "ref": "x"}, "user_stated from a model"),
                       ("source_fact", {"type": "model", "ref": "x"}, "source_fact from a model"),
                       ("bogus", {"type": "turn", "ref": "t1"}, "an unknown kind")):
    try:
        s.put(kind, "x", src)
        ok(False, f"{why} is refused")
    except ValueError:
        ok(True, f"{why} is refused")
inf = s.put("model_inference", "the room is 24 m wide", {"type": "model", "ref": "gemini"}, confidence=0.99)
ok("confidence" not in s.get(inf), "a model's confidence about itself is not stored")
for ev, why in (([], "no evidence"), ([inf], "its own record"),
                ([s.put("model_inference", "verifier: supported", {"type": "model", "ref": "verify"})], "a model verifier's verdict")):
    try:
        s.promote(inf, ev)
        ok(False, f"promotion on {why} is refused")
    except M.PromotionRefused:
        ok(True, f"promotion on {why} is refused")
code = s.put("source_fact", "layout.W read from job.json: 24", {"type": "code", "ref": "job.json"})
s.promote(inf, [code])
ok(s.get(inf)["kind"] == "source_fact" and s.get(inf)["evidence"] == [code], "promotion on a code measurement is allowed and cites it")

print("\n== memory: an unclear correction overwrites nothing ==")
s = store()
s.ingest_user("벽은 노출 콘크리트, 바닥도 콘크리트로 해줘")
before = {r["id"]: r["status"] for r in s.all()}
ok(len(s.ambiguity("콘크리트 말고 나무로")) == 2, "ambiguity() sees two candidates without writing")
e = s.ingest_user("콘크리트 말고 나무로")
ok(e["ambiguous"] and not e["superseded"], "'콘크리트 말고 나무로' with floor AND wall in concrete is ambiguous")
ok(all(s.get(i)["status"] == st for i, st in before.items()), "... and no earlier record changed status")
ok(set(s.get(e["record"])["conflicts_with"]) == set(e["ambiguous"][0]["candidates"]), "the conflict is kept as a link, not merged")
amb = e["record"]
e = s.ingest_user("벽은 나무로")
ok(not s.get(amb)["conflicts_with"] and s.get(amb).get("resolved_by") == e["turn"], "a clear statement of one candidate closes the open question")
ok(next(r for r in s.active() if r["key"] == "room.floor")["value"] == "concrete", "... and the floor stays concrete")
s = store()
s.ingest_user("바닥은 콘크리트로")
e = s.ingest_user("콘크리트 말고 화강암으로")
ok(next(r for r in s.active() if r["key"] == "room.floor")["value"] == "granite" and e["superseded"], "with one candidate the correction applies to it")

print("\n== slots read from words (no model) ==")
for t, want in (("폭 24m 말고 18m로", {"layout.W": 18.0}), ("아크네 느낌으로 폭 20m, 천장고 5m", {"brand": "Acne Studios", "layout.W": 20.0, "layout.H": 5.0}),
                ("조명은 자연광으로", {"room.light": "daylight"}), ("입구에 거울 벽을 추가", {}),
                ("SPA (STYLE, PASSION, ARCHITECTURE)", {"def:SPA": "STYLE, PASSION, ARCHITECTURE"}),
                # units: converted to metres; a unit glued to more letters is not one
                ("폭은 1800mm로", {"layout.W": 1.8}), ("폭 24m 말고 1800cm", {"layout.W": 18.0}), ("천장고 5.5미터", {"layout.H": 5.5}),
                ("폭 18ms", {}),
                # boundaries: 'A' of 'A 말고 B' is only the clause before the cue
                ("폭 20m, 깊이 15m 말고 12m", {"layout.W": 20.0, "layout.D": 12.0}), ("천장고 5.5m 말고 6m", {"layout.H": 6.0}),
                ("폭 20m. 벽은 콘크리트 말고 나무로", {"layout.W": 20.0, "room.wall": "wood"}),
                ("벽은 콘크리트 말고 바닥을 나무로", {"room.floor": "wood"}),
                ("조명은 자연광, 벽은 콘크리트 말고 나무로", {"room.light": "daylight", "room.wall": "wood"}),
                ("벽은 나무로 하고 대신 바닥은 콘크리트로", {"room.wall": "wood", "room.floor": "concrete"}),
                ("벽이 아니라 바닥을 나무로", {"room.floor": "wood"}), ("벽과 바닥은 나무로", {"room.wall": "wood", "room.floor": "wood"})):
    got = {o["key"]: o["value"] for o in M.extract(t)}
    ok(got == want, f"{t!r} -> {want}  [got {got}]")
ok(M.correction_parts("벽은 나무로 하고 대신 바닥은 콘크리트로") is None, "'하고 대신' joins two statements -- it takes nothing back")
ok(M.correction_parts("아니, 벽은 콘크리트 말고 나무로 해줘") == ("벽은 콘크리트", "나무로 해줘"), "the taken-back part is the clause before the cue")

print("\n== correction wins, turn after turn: only the newest value is shown ==")
s = store()
for t in ("벽은 노출 콘크리트, 바닥은 폴리싱 콘크리트, 폭 24m", "폭 24m 말고 1800cm로", "벽은 콘크리트 말고 나무로", "벽은 나무 말고 화강암으로"):
    e = s.ingest_user(t)
live = {r["key"]: r["value"] for r in s.active("user_stated") if r["key"]}
ok(live == {"room.floor": "polished_concrete", "layout.W": 18.0, "room.wall": "granite"}, f"one active value per slot, the newest [{live}]")
walls = [r for r in s.all() if r["key"] == "room.wall"]
ok([r["value"] for r in walls] == ["concrete", "wood", "granite"] and [r["status"] for r in walls] == ["superseded", "superseded", "active"],
   "each older wall value is kept and marked superseded")
slot = next(r for r in s.active() if r["key"] == "room.wall")
ok("나무" not in slot["content"] and "콘크리트" not in slot["content"], f"the slot record holds only the new words [{slot['content']}]")
T = C.build(s, "벽은 나무 말고 화강암으로", turn=e["turn"])["text"]
settled = T.split("## SETTLED BY THE USER")[1].split("##")[0]
ok("room.wall = granite" in settled and "wood" not in settled and "room.wall = concrete" not in settled, "settled shows granite, not wood or concrete")
ok("콘크리트 말고 나무로" not in T and "24m," not in T, "a replaced correction and a replaced width are not shown as if still valid")
s = store()
s.ingest_user("벽은 나무로, 폭 20m")
s.ingest_user("폭 20m, 깊이 15m 말고 12m")
live = {r["key"]: r["value"] for r in s.active("user_stated") if r["key"]}
ok(live == {"room.wall": "wood", "layout.W": 20.0, "layout.D": 12.0}, f"a restated value next to a correction stays [{live}]")

print("\n== context: what the model is shown ==")
s = store()
s.ingest_user("비 오는 밤의 성수 플래그십. 벽은 노출 콘크리트로 마감해줘")
s.add_model_turn("벽을 노출 콘크리트로 마감했고 폭 24m 공간에 30m 런웨이가 들어갑니다.")
s.add_summary("간추림: 마지막 답 머리 -- 런웨이 바닥은 콘크리트로 확정, 폭 24m.", ["t2"])
s.ingest_user("벽은 콘크리트 말고 나무로")
e = s.ingest_user("방금 거 런웨이 조명 좀 더 어둡게 해줘")
job = spec.examples()["gm"]
ctx = C.build(s, "방금 거 런웨이 조명 좀 더 어둡게 해줘", sources=C.job_facts(job), turn=e["turn"], fixed_tokens=2000)
T, tr = ctx["text"], ctx["trace"]
ok("room.wall = wood" in T and "노출 콘크리트로 마감" not in T, "the correction is in; the replaced words are not")
ok("⟨changed later" in T and "비 오는 밤의 성수 플래그십" in T, "the replaced span is cut out of the old turn; the rest of the turn stays")
ok("폭 24m" not in T and "⟨contradicted by" in T, "a model claim that contradicts the job file (W 20 m) is cut out")
fact, model = T.split("## MODEL'S EARLIER OUTPUT")
ok("30m 런웨이" not in fact and "30m 런웨이" in model, "what is left of the model's reply sits only under UNVERIFIED")
ok("(summary of t2)" in model, "a summary keeps its sources")
ex_ids = {x["id"] for x in tr["excluded"]}
ok(all(r["id"] in ex_ids for r in s.all() if r["status"] != "active"), "every superseded record is in the trace's excluded list")
ok("조명" not in json.dumps(tr, ensure_ascii=False) and "벽" not in json.dumps(tr, ensure_ascii=False), "the trace holds ids, hashes and counts -- no conversation text")
ok(tr["tokens"]["total_est"] == tr["tokens"]["context"] + 2000 and tr["budget"]["limit"] == 12000, "token counts and budget are in the trace")

tiny = C.build(s, "방금 거 조명 좀 더 어둡게 해줘", sources=C.job_facts(job), turn=e["turn"], fixed_tokens=11950)
ok(tiny["trace"]["over_budget"] and "room.wall = wood" in tiny["text"] and "조명 좀 더 어둡게" in tiny["text"],
   "over budget: the instruction and the user's settled slots are still in")
ok("MODEL'S EARLIER OUTPUT" not in tiny["text"] and any(x["why"] == "over budget" for x in tiny["trace"]["excluded"]),
   "over budget: the model's output goes first, with the reason 'over budget'")
s.ingest_user("비 오는 밤의 성수 플래그십. 벽은 노출 콘크리트로 마감해줘")
d = C.build(s, "x", turn="t99")
ok(any(x["why"].startswith("duplicate") for x in d["trace"]["excluded"]), "a repeated statement is shown once")
g = C.build(s, "지난번에 정한 색온도 그대로 해줘", turn="t99")
ok("NOT IN MEMORY" in g["text"] and "색온도" in g["text"], "a pointer to a decision nobody recorded is said to be missing")
g = C.build(s, "지난번에 정한 벽 그대로 해줘", turn="t99")
ok("NOT IN MEMORY" not in g["text"], "... but not when a user statement records it")
s = store()
s.ingest_user("벽은 석회로 마감해줘")
for i in range(150):
    s.ingest_user(f"포트폴리오 표지 문구 후보 {i}번을 다시 써라")
    s.add_model_turn(f"표지 문구 후보 {i}번입니다: 멈춘 자리에 내가 있다.")
e = s.ingest_user("방금 거 동선을 길게 바꿔줘")
L = C.build(s, "방금 거 동선을 길게 바꿔줘", turn=e["turn"])
ok("석회" in L["text"] and L["trace"]["tokens"]["context"] < 1500, f"300 unrelated turns: the wall constraint stays, the context stays small ({L['trace']['tokens']['context']} tokens est.)")

print("\n== verify: code first, a separate model call only with question · source · claim ==")
s = store()
s.ingest_user("벽은 나무로, 폭 20m")
j = copy.deepcopy(spec.examples()["gm"])
cc = {c["key"]: c["verdict"] for c in verify.code_check(j, s)}
ok(cc == {"room.wall": "violated", "layout.W": "supported"}, f"code_check reads the job file [{cc}]")
ok(any("room.wall = wood" in p and "concrete" in p for p in verify.problems(j, s)), "a violation is told as a fact about the answer")
seen = []
v = verify.model_check("벽은 나무로", '{"room":{"wall":"wood"}}', "the wall is wood", lambda p: (seen.append(p), '{"verdict":"supported","evidence":"wall wood"}')[1])
ok(v["verdict"] == "supported" and v["by"] == "model", "the verifier's verdict is reported as the model's")
ok("Question" in seen[0] and "Source" in seen[0] and "Claim" in seen[0] and "폭 20m" not in seen[0], "the verifier sees question, source and claim -- not the conversation")
ok(verify.model_check("q", "s", "c", lambda p: "I think it is fine")["verdict"] == "unchecked", "an unreadable verdict is 'unchecked', never 'supported'")
calls = []
good = copy.deepcopy(j); good["room"]["wall"] = "wood"
r = synopsis.generate("", ask=lambda p: (calls.append(p), json.dumps(j if len(calls) == 1 else good))[1], base="BASE", checks=lambda x: verify.problems(x, s))
ok(r["job"]["room"]["wall"] == "wood" and r["rounds"] == 2 and "the user said room.wall = wood" in calls[1], "a draft that ignores the user is retried with that fact")

print("\n== revise: the request path ==")
ex = spec.examples()["gm"]
asks = []


def fake(p):
    asks.append(p)
    out = copy.deepcopy(ex)
    if "room.wall = wood" in p:
        out["room"]["wall"] = "wood"
    return json.dumps(out)


pipeline.synopsis("r1", brief="비 오는 밤의 성수 플래그십. 벽은 노출 콘크리트로 마감, 바닥은 폴리싱 콘크리트", ask=fake, log=lambda x: None)
ms = M.open_job("r1")
ok(any(r["kind"] == "user_stated" for r in ms.all()) and any(r["kind"] == "model_inference" and r["key"] == "draft" for r in ms.all()),
   "make records the brief as the user's and the draft as a model inference")
out = pipeline.revise("r1", "아니, 벽은 콘크리트 말고 나무로", ask=fake, verify_ask=lambda q: '{"verdict":"insufficient","evidence":""}', log=lambda x: None)
d = Path(임시) / "r1"
ok(out["job"]["room"]["wall"] == "wood" and (d / "job.v1.json").is_file(), "the revised job is saved; the previous version is kept as job.v1.json")
ok("CURRENT INSTRUCTION" in asks[-1] and "room.wall = wood" in asks[-1] and "노출 콘크리트로 마감" not in asks[-1], "the model got the built context, without the replaced words")
md = (d / "synopsis.md").read_text(encoding="utf-8")
ok("Checked against your instructions" in md and "NOT SHOWN (model)" in md, "the verifier's 'insufficient' reaches the synopsis as NOT SHOWN")
tr = [json.loads(x) for x in (d / "context_trace.jsonl").read_text(encoding="utf-8").splitlines()]
ok(tr[-1]["action"] == "revise" and tr[-1]["selected"] and "rounds" in tr[-1], "a trace line is written per request")
ok(any(x["why"].startswith("duplicate of the current draft") for x in tr[-1]["excluded"]) and "design reason:" not in asks[-1],
   "the draft is shown once (in full), not again as memory")
pipeline.synopsis("r2", brief="벽은 노출 콘크리트, 바닥도 콘크리트로 한 매장", ask=lambda p: json.dumps(dict(copy.deepcopy(ex), room=dict(ex["room"], floor="concrete"))), log=lambda x: None)
n = len(asks)
a = pipeline.revise("r2", "콘크리트 말고 나무로", ask=fake, verify_ask=False, log=lambda x: None)
ok(a["asked"] and len(asks) == n, "an unclear correction is asked back; no model call")

print("\n== !젠몬: corrections reach the job ==")
J = ["gm_1"]
for 말, 기대 in (("!젠몬 방금 거 벽은 콘크리트 말고 나무로", ("revise", "gm_1")), ("!젠몬 아니 콘크리트 말고 나무로", ("revise", "gm_1")),
                 ("!젠몬 방금 거 폭 18m로 줄여줘", ("revise", "gm_1")), ("!젠몬 기억", ("memory", "gm_1")),
                 ("!젠몬 방금 거 영상도 뽑아줘", ("video", "gm_1")), ("!젠몬 비 오는 밤의 문턱을 주제로 한 성수 플래그십", ("make", "")),
                 ("!젠몬 벽은 콘크리트 말고 나무로", ("revise", "gm_1")),
                 ("!젠몬 흰 큐브 말고 동굴 같은 한남동 매장, 바닥은 흙으로", ("make", ""))):
    r = intent.parse(말, J)
    ok((r["action"], r["job"]) == 기대, f"{말!r} -> {기대}  [got {r['action']}, {r['job']!r}]")
launched = []
runner = lambda argv, log, what: (launched.append(argv), "시작 (가짜)")[1]       # noqa: E731
discord_cmd.run("!젠몬 r1 벽은 석회로 바꿔줘", runner)
ok(launched and launched[-1][3:5] == ["revise", "r1"], "a change to a named job launches `revise`")
n = len(launched)
reply = discord_cmd.run("!젠몬 r2 콘크리트 말고 나무로", runner)
ok(len(launched) == n and "불분명" in reply, "an unclear correction is asked back before anything is launched")
ok("기억" in discord_cmd.run("!젠몬 r1 기억", runner), "`!젠몬 기억` shows the memory")

print("\n== follow-ups: '고쳐' points at the latest output; displeasure is not evidence ==")
s = store()
s.ingest_user("아래 자소서 사례 3개를 참고해.\n\n" + "[사례] 동아리 회장으로 설문 21건을 모아 모집 방식을 바꿨습니다. " * 6)
s.ingest_user("문항: 지원 동기와 포부를 800자 이내로 작성하시오.")
s.add_model_turn("[초안 v1] 저는 고객의 말을 먼저 듣는 기획자입니다.")
for i in range(6):
    e = s.ingest_user("고쳐")
    last = s.add_model_turn(f"[초안 v{i + 2}] 고친 초안")
e = s.ingest_user("고쳐")
G = C.build(s, "고쳐", turn=e["turn"])
sel = {x["id"]: x["section"] for x in G["trace"]["selected"]}
ok(sel.get(last) == "model" and "(latest output)" in G["text"], "'고쳐' with no shared words: the latest output is still in the input")
ok("사례" in G["text"] and "문항" in G["text"], "after six '고쳐' turns the pasted 사례 and the 문항 are still in (pinned; terse turns take no recent slot)")
ok("USER CORRECTIONS" not in G["text"], "a bare '고쳐' is not shown as a correction that overrides everything")
ok(G["trace"]["followup"]["case"] == "bare" and "state in one line what you assume" in G["text"], "bare displeasure: self-diagnose and say the assumption")
s = store()
s.ingest_user("벽은 노출 콘크리트로 마감해줘")
s.add_model_turn("벽을 노출 콘크리트로 마감했습니다.")
e = s.ingest_user("벽이 잘못됐어")
ok({r["key"]: r["value"] for r in s.active("user_stated") if r["key"]} == {"room.wall": "concrete"}, "'벽이 잘못됐어' changes no stored value")
D = C.build(s, "벽이 잘못됐어", turn=e["turn"])
ok(D["trace"]["followup"]["case"] == "unsupported" and "do not change it" in D["text"] and "room.wall = concrete" in D["text"].split("## HOW TO TREAT")[1],
   "a dispute with no new value: keep the value, show what backs it, ask")
e = s.ingest_user("다음 안 보여줘")
ok("USER CORRECTIONS" not in C.build(s, "다음 안 보여줘", turn=e["turn"])["text"], "... and on the next turn it is not a correction either")
ok(M.classify("틀렸어", s)["case"] == "unclear" and M.classify("고쳐", store())["case"] == "unclear",
   "no target, or nothing made yet: ask once")
ok(M.classify("벽은 콘크리트 말고 나무로", s)["case"] == "correction", "a new value is a correction, applied as before")

print("\n" + ("전부 통과" if not FAIL else f"실패 {len(FAIL)}: " + "; ".join(FAIL)))
sys.exit(1 if FAIL else 0)
