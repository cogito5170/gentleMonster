# -*- coding: utf-8 -*-
"""!젠몬 자연어 해석 -- free text -> what to run. No model call, no heavy imports.

    parse("!젠몬 방금 거 영상도 뽑아줘", jobs=[...])  -> {"action": "video", "job": "<latest>", ...}

Actions
    help · list · status             말 그대로
    example                          번들 시놉시스(gm|tb|ac|ae) -- "예제/샘플" 과 브랜드
    make                             새 브리프 -> 시놉시스 + 레이아웃 PDF + 무드보드 (기본)
    layout                           있는 작업의 레이아웃·무드보드 다시 (새 사진·레퍼런스로)
    blueprint · video · site         있는 작업에 대해 (요청 시). site = frontend engine (웹 페이지)
    revise                           있는 작업을 고친다 -- "방금 거 벽은 나무로" · "아니 콘크리트 말고 나무로" (memory 를 거친다)
    memory                           작업의 기억(누가 말했나 · 아직 유효한가)을 본다
`steps` lists the on-request steps asked for on top (blueprint, video, site) -- "전부" asks for blueprint + video.

Job reference: an existing job name in the text, or 방금/최근/아까/그거/이거/마지막/직전 -> the newest job.
A request for blueprint/video with no job and a long enough brief becomes make + those steps.
"""
from __future__ import annotations

import re

BRANDS = {                       # words -> (example id or "", brand name for the synopsis)
    "젠틀몬스터": ("gm", "Gentle Monster"), "gentle monster": ("gm", "Gentle Monster"),
    "탬버린즈": ("tb", "Tamburins"), "탬버린": ("tb", "Tamburins"), "tamburins": ("tb", "Tamburins"),
    "아크네": ("ac", "Acne Studios"), "acne": ("ac", "Acne Studios"),
    "이솝": ("ae", "Aesop"), "aesop": ("ae", "Aesop"),
    "누데이크": ("", "Nudake"), "nudake": ("", "Nudake"),
}
_W = {
    "help": ("도움", "도움말", "help", "사용법", "뭐 할 수"),
    "list": ("목록", "리스트", "list", "작업들"),
    "status": ("상태", "진행", "다 됐", "됐어", "status"),
    "example": ("예제", "샘플", "example", "예시"),
    "video": ("영상", "동영상", "mp4", "비디오", "워크스루", "walkthrough", "video", "걸어가는"),
    "blueprint": ("청사진", "도면", "렌더", "blueprint", "실사", "평면도"),
    "site": ("사이트", "웹페이지", "웹 페이지", "홈페이지", "랜딩", "프론트", "frontend", "website", "web page", "site"),
    "full": ("전부", "풀세트", "다 만들어", "다 뽑아", "모두", "full"),
    "layout": ("무드보드", "레이아웃", "moodboard", "layout", "다시", "재구성", "바꿔", "넣어"),
    "latest": ("방금", "최근", "아까", "그거", "이거", "마지막", "직전", "위에 거", "위의"),
    "ref": ("레퍼런스", "참고", "reference", "처럼", "같은 레이아웃", "이런 레이아웃"),
    "memory": ("기억", "메모리", "memory"),
}
# a change asked of an existing job -- before memory these fell through to `layout` or `status` and were dropped
_CHANGE = re.compile(r"바꿔|바꾸|고쳐|고치|수정|옮겨|늘려|줄여|넓혀|좁혀|키워|낮춰|높여|추가|빼|없애|대신|말고|아니라|아니고|정정|instead|change|make it", re.I)
_FILLER = r"(해줘|해 줘|해주세요|만들어 줘|만들어줘|뽑아줘|뽑아 줘|줘|주세요|좀|도|로|으로|이걸로|이 사진들?로|사진으로|사진들로|첨부한)"


def _has(t: str, key: str) -> bool:
    return any(w in t for w in _W[key])


def _act(steps) -> str:
    """One on-request action for an existing job. site rides along with the others (discord_cmd chains it)."""
    core = [s for s in steps if s != "site"]
    if not core:
        return "site"
    return core[0] if len(core) == 1 else "full"


def parse(text: str, jobs=(), n_images: int = 0) -> dict:
    t = (text or "").strip()
    if t.startswith("!젠몬"):
        t = t[len("!젠몬"):].strip()
    low = t.lower()
    jobs = list(jobs)
    r = {"action": "", "job": "", "example": "", "brand": "", "brief": "", "steps": [], "wants_ref": _has(low, "ref"), "why": []}
    if not t:
        return dict(r, action="help")
    if low in ("도움", "help", "도움말", "?"):
        return dict(r, action="help")

    named = next((j for j in sorted(jobs, key=len, reverse=True) if re.search(r"(?<![\w])" + re.escape(j) + r"(?![\w])", t)), "")
    if named:
        r["job"] = named; r["why"].append(f"job named: {named}")
    elif _has(low, "latest") and jobs:
        r["job"] = jobs[-1]; r["why"].append(f"'{next(w for w in _W['latest'] if w in low)}' -> newest job {jobs[-1]}")

    for w, (ex, b) in BRANDS.items():
        if w in low:
            r["example"], r["brand"] = r["example"] or ex, r["brand"] or b
    m = re.search(r"(?<![a-z0-9_])(gm|tb|ac|ae)(?![a-z0-9_])", low.replace(named.lower(), " ") if named else low)
    if m and not r["example"]:
        r["example"] = m.group(1)
    if _has(low, "full"):
        r["steps"] = ["blueprint", "video"]
    else:
        r["steps"] = [s for s in ("blueprint", "video") if _has(low, s)]
    if _has(low, "site"):
        r["steps"].append("site")

    # brief = text minus job name, command words and fillers
    b = t.replace(r["job"], " ") if r["job"] else t
    for k in ("list", "status", "example", "video", "blueprint", "site", "full", "latest", "layout", "ref"):
        for w in _W[k]:
            b = re.sub(re.escape(w), " ", b, flags=re.I)
    if r["example"]:
        b = re.sub(r"(?<![a-z0-9_])(gm|tb|ac|ae)(?![a-z0-9_])", " ", b, flags=re.I)
    b = re.sub(_FILLER, " ", b)
    b = re.sub(r"\s+", " ", b).strip(" ,.!?")
    brief_ok = len(b) >= 12 and not re.fullmatch(r"[\s\w]{0,3}", b)

    if _has(low, "list") and len(t) <= 12:
        return dict(r, action="list")
    if _has(low, "status") and not brief_ok:
        return dict(r, action="status")
    if _has(low, "memory") and len(b) <= 6:
        if not r["job"] and jobs:
            r["job"] = jobs[-1]; r["why"].append(f"memory of the newest job {jobs[-1]}")
        return dict(r, action="memory")
    from gentle_monster import memory as _mem             # regex only; no model call
    slots = _mem.extract(t)
    change = bool(slots or _mem.correction_span(t) or (_CHANGE.search(t) and len(b) >= 4))
    if _has(low, "example") and r["example"] and not r["job"]:
        r["why"].append(f"bundled example {r['example']}")
        return dict(r, action="example")
    if r["job"]:
        if r["steps"]:
            return dict(r, action=_act(r["steps"]))
        if change:
            r["why"].append("a change to the job" + (f" ({', '.join(s['key'] for s in slots)})" if slots else ""))
            r["brief"] = t
            return dict(r, action="revise")
        if _has(low, "layout") or n_images:
            return dict(r, action="layout")
        return dict(r, action="status")
    a_brief = re.search(r"매장|플래그십|스토어|공간|숍|쇼룸|store|flagship|shop|showroom", low)   # "흰 큐브 말고 동굴 같은 매장" is a new brief
    leading = re.match(r"\s*(?:아니|아냐|정정|수정|잘못|no\b)", low)
    if jobs and not a_brief and (leading or len(t) <= 16) and _mem.CORRECTION_CUE.search(t) and (slots or _mem.correction_span(t)):
        r["job"] = jobs[-1]; r["brief"] = t   # "아니, 콘크리트 말고 나무로" corrects the newest job; it is not a new brief
        r["why"].append(f"a correction -> newest job {jobs[-1]}")
        return dict(r, action="revise")
    if brief_ok:
        r["brief"] = t                       # the model gets the user's own words, not the stripped form
        return dict(r, action="make")
    if not r["job"] and re.fullmatch(r"[A-Za-z][A-Za-z0-9_\-]{2,}", b) and b.lower() not in ("gm", "tb", "ac", "ae"):
        r["why"].append(f"no job named {b!r}")
        return dict(r, action="missing_job", job=b)        # a name was given and it does not exist -- never guess another job
    if r["steps"] and jobs and not brief_ok:
        r["job"] = jobs[-1]; r["why"].append(f"no job named -> newest job {jobs[-1]}")
        return dict(r, action=_act(r["steps"]))
    if n_images and jobs:
        r["job"] = jobs[-1]; r["why"].append(f"images with no brief -> rebuild newest job {jobs[-1]}")
        return dict(r, action="layout")
    if r["example"] and not brief_ok:
        r["why"].append(f"brand only -> bundled example {r['example']}")
        return dict(r, action="example")
    return dict(r, action="unclear")
