#!/usr/bin/env python3
"""SessionStart hook: 이 세션이 이어 하는 작업 공간(W1~W6)의 짧은 요약 RESUME.md 를 컨텍스트에 넣는다.

시작 · 재개 · /clear · 자동 압축 뒤마다 돈다. 의뢰인은 아무것도 하지 않아도 된다:
요약은 백엔드(WorkSpace 프로젝트)가 effiency 저장소 docs/workspace-context/modules/ 에 최신으로 유지한다.

어느 모듈인가: 환경 변수 WS_MODULE(W1~W6) > 지금 브랜치가 모듈 state.json 의 checkpoint.refs 에 있음 > 없으면 모듈 목록 한 줄씩.
요약은 2000자 이하, 목록은 700자 이하로만 넣는다. 무엇이 실패해도 세션을 막지 않는다 (항상 0 으로 끝난다).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/cogito5170/effiency.git"
REFS = ("claude/project-thread-uqkc04", "main")  # 매시간 동기화가 먼저 푸시되는 백엔드 브랜치, 없으면 main
BASE = "docs/workspace-context/modules"
MAX_RESUME, MAX_INDEX = 2000, 700


def git(*args, cwd=None, timeout=25):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.stdout if r.returncode == 0 else None


def fetch_tree(project: Path):
    """모듈 폴더를 {상대경로: 내용} 으로. 가까운 클론이 아니라 원격 최신을 얕게 받아 읽는다."""
    common = (git("-C", str(project), "rev-parse", "--git-common-dir") or "").strip()
    cache = (project / common if common else project / ".git") / "ws-resume"
    if not (cache / "HEAD").exists():
        git("init", "-q", "--bare", str(cache))
    for ref in REFS:
        if git("-C", str(cache), "fetch", "-q", "--depth=1", REPO, ref) is None:
            continue
        names = git("-C", str(cache), "ls-tree", "-r", "--name-only", "FETCH_HEAD", BASE)
        if not names or "/RESUME.md" not in names:
            continue  # 요약이 아직 없는 ref (예: 백엔드 PR 머지 전 main) 는 건너뛴다
        files = {}
        for n in names.split():
            if n.endswith(("/state.json", "/RESUME.md")):
                files[n[len(BASE) + 1:]] = git("-C", str(cache), "show", f"FETCH_HEAD:{n}") or ""
        return ref, files
    return None, {}


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or ".")
    ref, files = fetch_tree(project)
    if not files:
        return
    states = {}
    for name, text in files.items():
        if name.endswith("/state.json"):
            try:
                s = json.loads(text)
                states[s["module"]] = (name.split("/")[0], s)
            except Exception:
                pass
    want = (os.environ.get("WS_MODULE") or "").upper()
    branch = (git("-C", str(project), "rev-parse", "--abbrev-ref", "HEAD") or "").strip()
    if not want and branch and branch != "main":
        for mid, (_, s) in sorted(states.items()):
            if f"gentleMonster@{branch}" in s.get("checkpoint", {}).get("refs", {}):
                want = mid
                break
    src = f"effiency@{ref}:{BASE}"
    if want in states:
        folder = states[want][0]
        text = files.get(f"{folder}/RESUME.md", "")[:MAX_RESUME]
        out = (f"[작업 공간 {want} 요약 · {event.get('source', 'startup')} · {src}/{folder}/RESUME.md]\n"
               "아래는 백엔드가 저장소 커밋에서 만든 최신 요약이다. 이 대화의 앞부분보다 이것을 기준으로 이어 간다.\n\n" + text)
    else:
        rows = [f"- {m} {s.get('title', '')[:40]} → `{s.get('resume_point', {}).get('op')}`" for m, (_, s) in sorted(states.items())]
        out = (f"[작업 공간 목록 · {src}] 이 브랜치({branch})는 어느 모듈에도 없다. 작업이 정해지면 그 모듈의 RESUME.md 를 읽는다.\n"
               + "\n".join(rows))[:MAX_INDEX]
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": out}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
