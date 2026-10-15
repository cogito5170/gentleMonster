"""relay(cogito5170/effiency) 컨텍스트 보관소를 이 저장소의 Claude Code 세션에 거는 배선.

What this holds:
  1. .claude/settings.json 이 SessionStart · UserPromptSubmit · PreCompact 를 scripts/relay_hook.sh 로 보낸다.
  2. relay 가 없어도 hook 은 0 으로 끝나고 아무것도 출력하지 않는다 -- 세션을 막지 않는다(fail-open).
  3. relay 가 깔려 있으면 실제로 돈다: 큰 실내 디자인 대화가 보관되고, 새 세션에서 의류 디자인을 물으면
     실내 기억 대신 '주제 전환' 안내가 붙고, 실내를 다시 물으면 실내 기록만 붙는다.
relay 가 없으면 3 은 '건너뜀'.
Run: python3 tests/test_relay_hooks.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "scripts" / "relay_hook.sh"
FAIL: list = []


def ok(cond, what):
    print(("  ok  " if cond else "  FAIL ") + what)
    if not cond:
        FAIL.append(what)


def run(event: str, data: dict, cwd: Path, path_env: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(cwd))
    if path_env is not None:
        env["PATH"] = path_env
    return subprocess.run([shutil.which("bash") or "/bin/bash", str(HOOK), event], input=json.dumps({"cwd": str(cwd), **data}),
                          capture_output=True, text=True, cwd=cwd, env=env, timeout=60)


def transcript(path: Path, asks: list[str], ctx: int) -> Path:
    rows = []
    for i, ask in enumerate(asks):
        rows.append({"type": "user", "message": {"role": "user", "content": ask}})
        rows.append({"type": "assistant", "requestId": f"r{i}", "message": {
            "id": f"m{i}", "usage": {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": ctx},
            "content": [{"type": "text", "text": "알겠습니다. 그렇게 진행할게요."}]}})
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return path


print("1. settings.json")
settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
for ev, arg in (("SessionStart", "session"), ("UserPromptSubmit", "prompt"), ("PreCompact", "precompact")):
    cmds = [h["command"] for e in settings["hooks"].get(ev, []) for h in e["hooks"]]
    ok(any("scripts/relay_hook.sh " + arg in c for c in cmds), f"{ev} -> relay_hook.sh {arg}")
ok(os.access(HOOK, os.X_OK), "relay_hook.sh is executable")

print("2. relay 없이")
tmp = Path(tempfile.mkdtemp())
for ev in ("prompt", "precompact"):
    r = run(ev, {"prompt": "벽은 나무로"}, tmp, path_env="/nonexistent")
    ok(r.returncode == 0 and r.stdout == "", f"{ev}: exit 0, no output without relay")

print("3. relay 로 실제 실행")
has_relay = shutil.which("relay") and subprocess.run(["relay", "recall", "--help"], capture_output=True).returncode == 0
if not has_relay:
    print("  건너뜀 (relay 없음 또는 보관소 없는 판 -- pip install git+https://github.com/cogito5170/effiency.git)")
else:
    work = tmp / "repo"
    (work / ".relay").mkdir(parents=True)
    shutil.copy(ROOT / ".relay" / "config.toml", work / ".relay" / "config.toml")
    old = transcript(work / "old.jsonl", ["젠틀몬스터 성수 플래그십 매장 무드보드 레이아웃, 벽면은 노출 콘크리트",
                                          "매장 동선 여유 0.3m 로 도면 다시"], ctx=70_000)
    r = run("prompt", {"prompt": "계속", "transcript_path": str(old)}, work)
    ok(r.returncode == 0 and (work / ".relay" / "archive" / "index.jsonl").is_file(), "a 70k session is archived")
    fresh = work / "new.jsonl"
    fresh.write_text("")
    r = run("prompt", {"prompt": "이제 의류 컬렉션 무드보드 레이아웃 잡아줘", "transcript_path": str(fresh)}, work)
    ctx = json.loads(r.stdout or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
    ok("주제 전환" in ctx and "interior → fashion" in ctx, "switching to fashion adds a topic-shift notice")
    ok("콘크리트" not in ctx and "젠틀몬스터" not in ctx, "and pulls no interior memory")
    fresh2 = work / "new2.jsonl"
    fresh2.write_text("")
    r = run("prompt", {"prompt": "젠틀몬스터 매장 벽면 재료 다시 보자", "transcript_path": str(fresh2)}, work)
    ctx = json.loads(r.stdout or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
    ok("[relay recall]" in ctx and "콘크리트" in ctx, "asking about the store again recalls the interior record")
    r = run("session", {"source": "clear"}, work)
    ctx = json.loads(r.stdout or "{}").get("hookSpecificOutput", {}).get("additionalContext", "")
    ok(".relay/archive" in ctx and len(ctx) < 400, "after /clear only a one-line pointer is injected")

shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{'실패 ' + str(len(FAIL)) if FAIL else '전부 통과'}")
sys.exit(1 if FAIL else 0)
