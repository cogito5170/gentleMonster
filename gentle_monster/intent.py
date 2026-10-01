# -*- coding: utf-8 -*-
"""!젠몬 자연어 해석 -- free text -> what to run. No model call, no heavy imports.

    parse("!젠몬 방금 거 영상도 뽑아줘", jobs=[...])  -> {"action": "video", "job": "<latest>", ...}

Actions
    help · list · status             말 그대로
    example                          번들 시놉시스(gm|tb|ac|ae) -- "예제/샘플" 과 브랜드
    make                             새 브리프 -> 시놉시스 + 레이아웃 PDF + 무드보드 (기본)
    layout                           있는 작업의 레이아웃·무드보드 다시 (새 사진·레퍼런스로)
    blueprint · video                있는 작업에 대해 (요청 시)
`steps` lists the on-request steps asked for on top (blueprint, video) -- "전부" asks for both.

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
    "full": ("전부", "풀세트", "다 만들어", "다 뽑아", "모두", "full"),
    "layout": ("무드보드", "레이아웃", "moodboard", "layout", "다시", "재구성", "바꿔", "넣어"),
    "latest": ("방금", "최근", "아까", "그거", "이거", "마지막", "직전", "위에 거", "위의"),
    "ref": ("레퍼런스", "참고", "reference", "처럼", "같은 레이아웃", "이런 레이아웃"),
}
_FILLER = r"(해줘|해 줘|해주세요|만들어 줘|만들어줘|뽑아줘|뽑아 줘|줘|주세요|좀|도|로|으로|이걸로|이 사진들?로|사진으로|사진들로|첨부한)"


def _has(t: str, key: str) -> bool:
    return any(w in t for w in _W[key])


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

    # brief = text minus job name, command words and fillers
    b = t.replace(r["job"], " ") if r["job"] else t
    for k in ("list", "status", "example", "video", "blueprint", "full", "latest", "layout", "ref"):
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
    if _has(low, "example") and r["example"] and not r["job"]:
        r["why"].append(f"bundled example {r['example']}")
        return dict(r, action="example")
    if r["job"]:
        if r["steps"]:
            act = r["steps"][0] if len(r["steps"]) == 1 else "full"
            return dict(r, action=act)
        if _has(low, "layout") or n_images:
            return dict(r, action="layout")
        return dict(r, action="status")
    if brief_ok:
        r["brief"] = t                       # the model gets the user's own words, not the stripped form
        return dict(r, action="make")
    if not r["job"] and re.fullmatch(r"[A-Za-z][A-Za-z0-9_\-]{2,}", b) and b.lower() not in ("gm", "tb", "ac", "ae"):
        r["why"].append(f"no job named {b!r}")
        return dict(r, action="missing_job", job=b)        # a name was given and it does not exist -- never guess another job
    if r["steps"] and jobs and not brief_ok:
        r["job"] = jobs[-1]; r["why"].append(f"no job named -> newest job {jobs[-1]}")
        return dict(r, action=r["steps"][0] if len(r["steps"]) == 1 else "full")
    if n_images and jobs:
        r["job"] = jobs[-1]; r["why"].append(f"images with no brief -> rebuild newest job {jobs[-1]}")
        return dict(r, action="layout")
    if r["example"] and not brief_ok:
        r["why"].append(f"brand only -> bundled example {r['example']}")
        return dict(r, action="example")
    return dict(r, action="unclear")
