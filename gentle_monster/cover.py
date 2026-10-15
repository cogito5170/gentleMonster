"""The blueprint's cover: one photoreal render of the room, made by Codex on the user's VM (not three.js).

This machine never calls OpenAI. It writes a short semantic image spec from the job into
`.relay/tasks/<NNN>-cover-<job>/` (see .claude/skills/codex-image/SKILL.md); the VM inbox runs Codex and
pushes `image.png` back to the same branch. `attach` copies that image into the job as `cover.png`, and
the next `blueprint` puts it on page 1, in front of the three.js drawing sheet (which stays as it was)."""
from __future__ import annotations

import json
import math
import re
import shutil
import time
from pathlib import Path

from gentle_monster import paths

TASKS = paths.REPO / ".relay" / "tasks"
# the same presets web/scene.js builds, said in words an image model can light
LIGHT = {"dark_gallery": "어두운 갤러리: 차가운 약한 앰비언트, 히어로 위 좁은 스팟, 깊은 그림자",
         "white_gallery": "흰 갤러리: 밝고 고른 확산광, 옅은 그림자", "daylight": "입구 쪽에서 드는 낮 자연광, 실내는 어둡게",
         "warm_spot": "따뜻한 스팟 조명 몇 개, 주변은 어둡게"}
MAT = {"concrete": "거친 노출 콘크리트", "polished_concrete": "폴리싱 콘크리트(젖은 듯 반사)", "granite": "그라나이트",
       "steel": "헤어라인 스테인리스(강한 금속 반사)", "mirror_aluminium": "거울 같은 알루미늄", "aluminium": "무광 알루미늄",
       "brass": "브러시드 황동", "red_wax": "붉은 왁스", "graphite_wax": "흑연+왁스", "mineral_white": "흰 미네랄 도장",
       "strata_clay": "지층 무늬 흙벽", "lime_plaster": "석회 미장", "wood": "원목", "amber_glass": "호박색 유리",
       "glass": "투명 렌즈 유리(무지갯빛 반사)", "skin": "실리콘 피부(반투명 살결, 땀 같은 광)",
       "textile_light": "빛나는 직물 천장", "black_stone": "광택 검은 석재", "white_gloss": "흰 유광 면",
       "candle_wax": "양초 왁스", "black": "검정"}
FOV_V, EYE_H = 58, 1.62           # web/scene.js still('eye'): PerspectiveCamera(58) at eye height on the path
_cap = lambda s, n=600: str(s)[:n]


def file(name: str) -> Path:
    return paths.job_dir(name) / "cover.png"


def find(name: str) -> "Path | None":
    p = file(name)
    return p if p.is_file() else None


def _fit(parts, n: int = 600) -> str:
    """Join whole parts until the field is full (the VM rejects a field over 600 characters)."""
    out = ""
    for x in parts:
        nxt = f"{out} {x}".strip()
        if len(nxt) > n:
            break
        out = nxt
    return out


def camera(job: dict) -> dict:
    """The 'eye' still of web/scene.js: the stop that looks nearest the hero, seen 2 m back along the path."""
    L = job["layout"]
    pts = [tuple(p) for p in L["flows"][0]["pts"]]
    hero = next((i for i in L["items"] if i.get("hero")), None)
    hx, hy = ((hero["x0"] + hero["x1"]) / 2, (hero["y0"] + hero["y1"]) / 2) if hero else (L["W"] / 2, L["D"] / 2)
    stops = job.get("stops") or [{"at": pts[len(pts) // 2], "look": [hx, 1.5, hy]}]
    stop = min(stops, key=lambda s: (s["look"][0] - hx) ** 2 + (s["look"][2] - hy) ** 2)
    # walk the path to the point nearest the stop, then 2 m back
    seg = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    best, along, run = 1e9, 0.0, 0.0
    for (x0, y0), (x1, y1) in seg:
        ln = math.hypot(x1 - x0, y1 - y0) or 1e-9
        t = max(0.0, min(1.0, ((stop["at"][0] - x0) * (x1 - x0) + (stop["at"][1] - y0) * (y1 - y0)) / ln ** 2))
        d = math.hypot(x0 + t * (x1 - x0) - stop["at"][0], y0 + t * (y1 - y0) - stop["at"][1])
        if d < best:
            best, along = d, run + t * ln
        run += ln
    want, run, pos = max(0.0, along - 2.0), 0.0, pts[0]
    for (x0, y0), (x1, y1) in seg:
        ln = math.hypot(x1 - x0, y1 - y0) or 1e-9
        if run + ln >= want:
            t = (want - run) / ln
            pos = (x0 + t * (x1 - x0), y0 + t * (y1 - y0))
            break
        run += ln
    look = (stop["look"][0], stop["look"][2])
    fx, fy = look[0] - pos[0], look[1] - pos[1]
    n = math.hypot(fx, fy) or 1.0
    return {"pos": pos, "look": look, "look_h": stop["look"][1], "f": (fx / n, fy / n), "stop": stop}


def in_view(job: dict, cam: dict, aspect: float = 1.5) -> "list[tuple[float, float, dict]]":
    """(ahead, right, item) for every built item in the frame, nearest first. Right = the viewer's right, as three.js draws it."""
    half = math.degrees(math.atan(math.tan(math.radians(FOV_V / 2)) * aspect))
    (px, py), (fx, fy) = cam["pos"], cam["f"]
    rx, ry = -fy, fx
    out = []
    for it in job["layout"]["items"]:
        if it.get("shape", "box") in ("zone", "door", "floor_patch") or it["type"] == "door":
            continue
        cx, cy = (it["x0"] + it["x1"]) / 2 - px, (it["y0"] + it["y1"]) / 2 - py
        ahead, right = cx * fx + cy * fy, cx * rx + cy * ry
        if ahead > 0.3 and abs(math.degrees(math.atan2(right, ahead))) < half + 8:
            out.append((ahead, right, it))
    return sorted(out, key=lambda t: (not t[2].get("hero"), t[0]))


def _shape(it: dict) -> str:
    from gentle_monster.spec import SHAPES
    return re.split(r"[;(]", SHAPES.get(it.get("shape", "box"), ""))[0].strip()


def _where(ahead: float, right: float) -> str:
    side = "정면" if abs(right) < 0.6 else f"{'오른쪽' if right > 0 else '왼쪽'} {abs(right):.1f} m"
    return f"앞 {ahead:.1f} m·{side}"


def spec(job: dict) -> dict:
    """image-spec.json for the codex-image skill, from the data three.js gets (room presets, items with shape,
    material, size and place, the camera) and the data the blueprint sheet prints (envelope, area programme,
    intent). Codex expands it into the long prompt; this only says what is where."""
    L, room = job["layout"], job.get("room", {})
    cam = camera(job)
    seen = in_view(job, cam)
    groups: "dict[str, list]" = {}
    for a, r, it in seen:                               # six conifers are one line, not six
        groups.setdefault(it["label"], []).append((a, r, it))
    things = []
    for label, g in groups.items():
        a, r, it = g[0]
        where = _where(a, r) if len(g) == 1 else f"{len(g)}개, 가장 가까운 것 {_where(a, r)}, 먼 것 앞 {max(x[0] for x in g):.1f} m"
        things.append(f"[{where}] {label} ({_shape(it)}): "
                      f"{it['x1'] - it['x0']:.1f}×{it['y1'] - it['y0']:.1f} m, 높이 {it['h']:g} m, {MAT.get(it.get('material', ''), it.get('material', ''))}.")
    shell = (f"실내 {L['W']}×{L['D']} m, 천장 {L['H']} m. 바닥 {MAT.get(room.get('floor'), room.get('floor', ''))}, "
             f"벽 {MAT.get(room.get('wall'), room.get('wall', ''))}, 천장 {MAT.get(room.get('ceiling'), room.get('ceiling', ''))}"
             + (", 노출 보" if room.get("beams") else "") + f", 기둥 {len(L.get('columns', []))}개.")
    try:
        from render3d import layout as LY
        area = LY.area_program(LY.to_scene(L))
        prog = "면적: " + ", ".join(f"{k} {v:.0f}㎡" for k, v in area.items() if v > 0) + "."
    except Exception:                                   # noqa: BLE001 -- the plan is a nicety here, not a requirement
        prog = ""
    (px, py), (lx, ly) = cam["pos"], cam["look"]
    hero = next((i for i in L["items"] if i.get("hero")), None)
    return {
        "subject": _fit([f"{job['brand']} 플래그십 '{job['title']}' 내부의 실사 사진.", job.get("line", "")]
                        + ([f"주인공: {hero['label']} ({_shape(hero)})."] if hero else [])
                        + [job.get("synopsis", "")]),
        "purpose": "청사진(A3 도면) 표지. 도면·three.js 렌더와 같은 공간이 실제로 지어진 것처럼 보이는 사진",
        "style": "실사 건축 인테리어 사진(풀프레임, 광각 약 20 mm, 수직선 보정, 자연스러운 노이즈). CG·3D 렌더·일러스트 느낌 금지",
        "mood": _fit([", ".join(job.get("keywords", [])) + ".", job.get("quote", ""), cam["stop"].get("cap", ""), cam["stop"].get("sub", "")]),
        "composition": _fit([f"눈높이 {EYE_H} m, 세로 화각 {FOV_V}°. 평면 좌표 ({px:.1f}, {py:.1f}) 에서 ({lx:.1f}, {ly:.1f}) 높이 {cam['look_h']:g} m 를 본다"
                             f" (입구 벽 y=0, 안쪽으로 y 증가). 화면 안 배치(카메라 기준):"] + things),
        "palette": _fit([", ".join(f"{c['name']} {c['hex']}" for c in job.get("palette", [])) + ".", f"포인트 색 {job.get('accent', '')}."]),
        "lighting": _fit([LIGHT.get(room.get("light", ""), room.get("light", "")) + "."]
                         + ([f"옅은 안개(밀도 {room['fog']}), 빛줄기가 보이게."] if room.get("fog") else [])
                         + ["바닥·금속·유리에 실제 반사, 접지 그림자."]),
        "text": "",
        "size": "1536x1024",
        "avoid": ["글자", "로고", "워터마크", "사람 얼굴", "도면 선·치수", "CG 같은 매끈한 표면", "배치에 없는 가구"],
        "notes": _fit([shell, prog, "의도:"] + [w["t"] + "." for w in job.get("why", [])]
                      + ["재료: " + ", ".join(f"{m['name']}({m['where']})" for m in job.get("materials", [])) + "."]),
    }


def request(name: str, job: dict, tasks: Path = TASKS) -> Path:
    """Write the spec and an image request for the VM inbox. Returns the task folder (commit + push it)."""
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", name).strip("-")[:40] or "job"
    nums = [int(m.group(1)) for d in tasks.glob("*") if (m := re.match(r"(\d{3})-", d.name))] if tasks.is_dir() else []
    d = tasks / f"{max(nums, default=0) + 1:03d}-cover-{slug}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "image-spec.json").write_text(json.dumps(spec(job), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (d / "request.json").write_text(json.dumps({"action": "image", "id": time.strftime("%Y%m%dT%H%M%S")}) + "\n", encoding="utf-8")
    return d


def attach(name: str, image) -> Path:
    """Use `image` (a task folder or a PNG/JPEG) as the job's cover."""
    src = Path(image)
    if src.is_dir():
        src = src / "image.png"
    if not src.is_file():
        raise FileNotFoundError(f"no cover image at {src} -- has the VM inbox answered yet? (response.json)")
    return Path(shutil.copyfile(src, file(name)))
