# -*- coding: utf-8 -*-
"""!젠몬 -- gentle_monster fixed command.

Contract: PREFIX and run(text, runner=None, allow_write=True). **Unknown text returns None.**
Imports stay light: the model call, Chromium and ffmpeg run only in a background child process
(a host bot may pass its own `runner`; otherwise a detached subprocess logs to logs/gentle_monster.log).

The text is read as natural language by gentle_monster.intent (no model call):

    !젠몬 <브리프>                       시놉시스 + 레이아웃 PDF + 무드보드 PDF (기본)
    !젠몬 탬버린즈 예제로 무드보드         번들 시놉시스 (모델 호출 없음)
    !젠몬 방금 거 청사진 / 영상도          최근 작업에 청사진 / MP4 (요청 시)
    !젠몬 (사진·레퍼런스 첨부) 이 레이아웃처럼 무드보드 다시
    !젠몬 <브리프>, 청사진이랑 영상까지 전부
    !젠몬 목록 · !젠몬 상태 <작업>

Attached images (run(..., images=[paths])) are passed as --image; the child process measures which
are photos and which are reference layouts (photos.split).

Outputs go to out/ (ignored by git) -- no command changes the repository.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

PREFIX = "!젠몬"
_LOG = Path(__file__).resolve().parent / "logs" / "gentle_monster.log"
_EX = ("gm", "tb", "ac", "ae")
HELP = (f"`{PREFIX} <브리프>` — 공간 **시놉시스**(Gemini, 코드가 동선·간섭 검사) + **레이아웃 PDF**(A3 한 장) + **잡지형 무드보드 PDF**(A3 펼침 8장, 영문). 2~3분.\n"
        "사진을 첨부하면 무드보드에 배치한다(가장 강한 사진이 표지, 가장 어두운 사진이 풀블리드). 3장 미만이면 공간 실사 렌더로 채우고 '생성' 이라 적는다.\n"
        "**레퍼런스 레이아웃** 그림을 같이 첨부하면 종이색·여백·밀도를 재서 따른다(Gemini 가 있으면 펼침 순서도 읽는다).\n"
        f"`{PREFIX} 탬버린즈 예제로 무드보드` — 들어 있는 시놉시스(젠틀몬스터·탬버린즈·아크네·이솝). 모델 호출 없음.\n"
        f"`{PREFIX} 방금 거 청사진` · `{PREFIX} 방금 거 영상도` — 요청 시: 실사 렌더 + A3 도면 / 동선을 걷는 30초 MP4(수십 분).\n"
        f"`{PREFIX} 방금 거 이 사진들로 무드보드 다시` · `{PREFIX} <브리프>, 청사진이랑 영상까지 전부` · `{PREFIX} 목록` · `{PREFIX} 상태 <작업>`.\n"
        "치수는 가정이고 실측이 아니다. 청사진·영상은 요청이 있을 때만 만든다.")


def _cmd(t: str):
    if not t.startswith(PREFIX):
        return None
    tail = t[len(PREFIX):]
    if tail and tail[0] not in " \t":
        return None
    return tail.strip()


def _detach(argv, log: Path, findword: str) -> str:
    """Default runner: a new session so the job outlives the caller; says it started only if it is alive."""
    import subprocess
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "ab") as f:
        p = subprocess.Popen(argv, cwd=str(Path(__file__).resolve().parent.parent), stdout=f, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    time.sleep(1)
    if p.poll() is not None:
        return f"띄웠는데 곧바로 끝났다 (exit {p.returncode}) -- 로그를 보라: {log}"
    return f"백그라운드로 시작했다 (PID {p.pid}). 로그: {log}"


def _launch(runner, argv, findword):
    launch = runner or _detach
    try:
        return launch(argv, _LOG, findword)
    except Exception as e:                                       # noqa: BLE001
        return f"못 띄웠다: {type(e).__name__}: {e}"


def _job(name: str) -> "str | None":
    from gentle_monster import paths
    return name if (paths.OUT / name / "job.json").is_file() else None


def _jobs() -> "list[str]":
    """Existing jobs, oldest first (newest last -- '방금 거' is the last one)."""
    from gentle_monster import paths
    if not paths.OUT.is_dir():
        return []
    return [p.parent.name for p in sorted(paths.OUT.glob("*/job.json"), key=lambda q: q.stat().st_mtime)]


def _images(images=None) -> "list[str]":
    """Image attachments of this message: passed by the host bot as `images`, else read from an
    `agent_context.current_images` contextvar if the host provides that module."""
    if images is None:
        try:
            import agent_context
            images = agent_context.current_images.get()
        except Exception:                                        # noqa: BLE001 -- no context: no images
            images = ()
    return [p for p in images if str(p).lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]


_KO = {"make": "시놉시스 → 레이아웃 PDF → 무드보드 PDF", "example": "번들 시놉시스 → 레이아웃 PDF → 무드보드 PDF",
       "layout": "레이아웃·무드보드 다시 짓기", "blueprint": "청사진(실사 렌더 + A3 도면)", "video": "30초 1인칭 MP4", "full": "청사진 → MP4"}


def run(text, runner=None, allow_write: bool = True, images=None):
    rest = _cmd((text or "").strip())
    if rest is None:
        return None
    from gentle_monster import intent
    jobs, imgs = _jobs(), _images(images)
    it = intent.parse(rest, jobs, n_images=len(imgs))
    act, job = it["action"], it["job"]
    py = [sys.executable, "-m", "gentle_monster"]
    if act == "help":
        return HELP
    if act == "unclear":
        return "무엇을 할지 못 읽었다 -- 공간 브리프를 한두 문장으로 주거나 아래처럼 말해 달라.\n\n" + HELP
    if act == "list":
        from gentle_monster import pipeline
        if not jobs:
            return "아직 작업이 없다. `!젠몬 <브리프>` 로 시작한다."
        return "\n".join(f"`{j}` " + " · ".join(k for k, v in pipeline.status(j).items() if v) for j in jobs[-20:])
    if act == "missing_job":
        return f"작업 `{job}` 이(가) 없다. `{PREFIX} 목록` 으로 이름을 확인하라." + (f" 가장 최근: `{jobs[-1]}`" if jobs else "")
    if act == "status":
        if not job:
            return f"어느 작업인지 모르겠다. `{PREFIX} 목록` 으로 이름을 확인하라." + (f" 가장 최근: `{jobs[-1]}`" if jobs else "")
        from gentle_monster import pipeline
        return f"`{job}`: " + " · ".join(f"{k} {'있음' if v else '없음'}" for k, v in pipeline.status(job).items())

    img = [x for p in imgs for x in ("--image", p)] + (["--text", rest] if imgs else [])
    seen = f"첨부 그림 {len(imgs)}장 -- 사진과 레퍼런스 레이아웃은 작업 안에서 픽셀로 가른다.\n" if imgs else ""
    why = ("해석: " + "; ".join(it["why"]) + "\n") if it["why"] else ""
    if act == "example":
        ex = it["example"] or "gm"
        name = f"ex_{ex}_{time.strftime('%m%d%H%M%S')}"
        argv = py + ["example", ex, "--name", name] + img + (["--full"] if it["steps"] == ["blueprint", "video"] else ["--blueprint"] if "blueprint" in it["steps"] else [])
        return f"작업 `{name}` — {_KO['example']}.\n{why}{seen}" + _launch(runner, argv, name)
    if act == "make":
        name = f"gm_{time.strftime('%m%d%H%M%S')}"
        steps = it["steps"]
        argv = py + ["make", it["brief"], "--name", name] + img + (["--full"] if "video" in steps else ["--blueprint"] if steps else [])
        more = " → 청사진" if steps else ""
        more += " → MP4" if "video" in steps else ""
        return (f"작업 `{name}` — {_KO['make']}{more}.\n{why}{seen}"
                + ("" if "video" in steps else f"청사진·영상은 요청 시에만: `{PREFIX} 방금 거 청사진` · `{PREFIX} 방금 거 영상`\n") + _launch(runner, argv, name))
    if not job or not _job(job):
        return f"작업을 못 찾았다. 먼저 `{PREFIX} <브리프>` 로 시놉시스를 만든다 (`{PREFIX} 목록`)."
    if act == "layout":
        return f"작업 `{job}` — {_KO['layout']}.\n{why}{seen}" + _launch(runner, py + ["layout", job] + img, f"gentle_monster layout {job}")
    if act in ("blueprint", "video", "full"):
        what = {"blueprint": ["blueprint", job], "video": ["video", job], "full": ["blueprint", job, "--then-video"]}[act]
        note = "수 분 걸린다." if act == "blueprint" else "30초 영상, 수십 분 걸린다. 끝나면 이 채널에 올린다."
        return f"작업 `{job}` — {_KO[act]}. {note}\n{why}" + _launch(runner, py + what, f"gentle_monster {what[0]} {job}")
    return HELP
