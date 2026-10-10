"""The job spec -- one JSON that every step reads: synopsis text, layout (render3d format plus
`shape`/`material` for the photoreal scene), camera stops for the walkthrough.

**The validator is the outside of the loop.** The synopsis is written by a model, so its layout
is checked by code here: a path that walks through a sculpture, a door that is not on the street
edge, a stop that is not on the path. In the first hand-built version of these four spaces the
drawn circulation collided with objects in four places (a closed wire gate, two candle
sculptures, a basin rim) and nobody saw it until a camera tried to walk it. So clearance is
measured, not assumed.

Problems come back as **facts about the layout**, never as rule names -- a model told "rule X
failed" learns to satisfy the checker, a model told "the path passes 0.1 m inside candle2
(x 3.4-5.0, y 8.8-10.2)" learns where the candle is.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

from gentle_monster import paths

# render3d plan types (render3d/scene.py BOX_TYPES) -- the plan renderer rejects anything else
TYPES = {"wall_shelf", "island", "gondola", "checkout", "figure", "media", "stock", "kiosk", "room", "stair",
         "elevator", "tables", "window", "bin", "zone", "queue", "door", "dead", "block"}
# photoreal shapes (web/scene.js builds each one)
SHAPES = {
    "box": "plain block: counter, plinth, back-of-house, fitting room",
    "rock": "rough-cut stone block; optional `cloth` colour drapes a garment over it",
    "bust": "hyperreal android head on a plinth, eyelids tremble, tears fall",
    "creature": "faceted white quadruped frozen before a leap, muscles twitch",
    "cone_tree": "metal conifer, stacked open cones",
    "joint_column": "stacked steel joints that breathe (contract/expand)",
    "cable_curtain": "curtain of catenary steel cables along x, breathing; leave a passage by using two items",
    "candle_cluster": "cluster of wax candles with small products hidden in the cracks, flames flicker",
    "basin": "round brass basin with running water, drops and ripples",
    "shelf_wall": "wall shelving with amber bottles set into the wall material",
    "display": "dark plinth with eyewear/products on a glass top",
    "shards": "volume of floating glass shards that drift (not an obstacle, use type zone)",
    "mirror_wall": "thin mirror-aluminium wall; the longest one becomes a true mirror",
    "light_ceiling": "luminous textile ceiling over the item footprint (use type zone)",
    "floor_patch": "floor finish patch over the footprint, e.g. graphite + wax (use type zone)",
    "memory_frame": "asymmetric open polyhedron of acrylic rods and glass tubes with polished silver nodes, one red node; optional nodes/edges/red; form \"eyewear\" builds a half-made pair of glasses instead",
    "robot_arm": "matte white ceramic six-axis arm that reaches for the open edge of a memory_frame (from/to node names); build it beside one",
    "reflect_basin": "shallow black-edged basin of still water, a true mirror; put a memory_frame inside it (they may overlap)",
    "zone": "no geometry; a named area",
    "door": "entrance opening on the street edge (y = 0)",
}
MATERIALS = {"concrete", "polished_concrete", "granite", "steel", "mirror_aluminium", "aluminium", "brass", "red_wax",
             "graphite_wax", "mineral_white", "strata_clay", "lime_plaster", "wood", "amber_glass", "glass", "skin",
             "textile_light", "black_stone", "white_gloss", "candle_wax",
             "pale_concrete", "ceramic_white", "black_chrome", "titanium", "dark_titanium", "oxidized_silver"}
LIGHTS = {"dark_gallery", "white_gallery", "daylight", "warm_spot", "cold_spot"}
NON_OBSTACLE = {"zone", "shards", "light_ceiling", "floor_patch", "door"}
CLEAR = 0.30              # metres a visitor needs between the path centre line and any object
HANGUL = re.compile("[가-힣]")


def load(p) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def examples() -> "dict[str, dict]":
    return {p.stem: load(p) for p in sorted(paths.EXAMPLES.glob("*.json"))}


def _rect_dist(x, y, it) -> float:
    """Signed distance from point to the item footprint (negative = inside). Round shapes use their circle."""
    if it.get("shape") == "basin":
        cx, cy = (it["x0"] + it["x1"]) / 2, (it["y0"] + it["y1"]) / 2
        return math.hypot(x - cx, y - cy) - min(it["x1"] - it["x0"], it["y1"] - it["y0"]) / 2
    dx = max(it["x0"] - x, 0, x - it["x1"])
    dy = max(it["y0"] - y, 0, y - it["y1"])
    if dx or dy:
        return math.hypot(dx, dy)
    return -min(x - it["x0"], it["x1"] - x, y - it["y0"], it["y1"] - y)


def obstacles(L: dict) -> "list[dict]":
    obs = [i for i in L["items"] if i.get("shape", "box") not in NON_OBSTACLE and i["type"] not in ("zone", "door", "window") and i.get("h", 0) > 0]
    obs += [dict(id="column@%.1f,%.1f" % (c[0], c[1]), x0=c[0] - .2, x1=c[0] + .2, y0=c[1] - .2, y1=c[1] + .2) for c in L.get("columns", [])]
    return obs


def path_points(L: dict, step: float = 0.05) -> "list[tuple[float, float]]":
    P = L["flows"][0]["pts"]
    out = []
    for a, b in zip(P, P[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    out.append(tuple(P[-1]))
    return out


def clearance(L: dict) -> "tuple[float, str, tuple]":
    """Smallest distance between the drawn circulation and any object: (metres, item id, where)."""
    best = (1e9, "", (0, 0))
    for x, y in path_points(L):
        for it in obstacles(L):
            d = _rect_dist(x, y, it)
            if d < best[0]:
                best = (d, it["id"], (round(x, 2), round(y, 2)))
    return best


def _fmt(it) -> str:
    return "%s (x %.1f-%.1f, y %.1f-%.1f)" % (it["id"], it["x0"], it["x1"], it["y0"], it["y1"])


def check(job: dict) -> "list[str]":
    """Everything wrong with the job, as facts. Empty list = usable."""
    bad = []
    for k in ("brand", "title", "line", "synopsis", "keywords", "quote", "why", "palette", "materials", "accent", "layout", "room", "stops"):
        if k not in job:
            bad.append(f"the field `{k}` is missing")
    if bad:
        return bad
    for k in ("brand", "title", "subtitle", "line", "synopsis", "quote"):
        if HANGUL.search(str(job.get(k, ""))):
            bad.append(f"`{k}` contains Korean text; the printed pages are English only")
    if not (60 <= len(job["synopsis"]) <= 900):
        bad.append(f"the synopsis is {len(job['synopsis'])} characters; it should be 60-900")
    if len(job["keywords"]) != 3:
        bad.append(f"there are {len(job['keywords'])} keywords; give exactly 3")
    if not (3 <= len(job["why"]) <= 4):
        bad.append(f"there are {len(job['why'])} design reasons; give 3 or 4")
    if len(job["palette"]) != 5 or not all(re.fullmatch(r"#[0-9a-fA-F]{6}", p.get("hex", "")) for p in job["palette"]):
        bad.append("the palette needs exactly 5 colours, each with a #rrggbb `hex`")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(job["accent"])):
        bad.append(f"accent {job['accent']!r} is not a #rrggbb colour")
    if len(job["materials"]) != 4:
        bad.append(f"there are {len(job['materials'])} materials; give exactly 4, each with `name` and `where`")
    for m in job["materials"]:
        if m.get("preset") not in MATERIALS:
            bad.append(f"material {m.get('name')!r} has preset {m.get('preset')!r}; the swatch preset must be one of: {', '.join(sorted(MATERIALS))}")
    R = job["room"]
    for k in ("floor", "wall", "ceiling"):
        if R.get(k) not in MATERIALS:
            bad.append(f"room.{k} is {R.get(k)!r}; use one of: {', '.join(sorted(MATERIALS))}")
    if R.get("light") not in LIGHTS:
        bad.append(f"room.light is {R.get('light')!r}; use one of: {', '.join(sorted(LIGHTS))}")

    L = job["layout"]
    W, D, H = L.get("W", 0), L.get("D", 0), L.get("H", 0)
    if not (6 <= W <= 40 and 6 <= D <= 40 and 2.8 <= H <= 8):
        bad.append(f"the envelope is {W} x {D} m, ceiling {H} m; keep width and depth 6-40 m and ceiling 2.8-8 m")
        return bad
    ids = [i.get("id") for i in L.get("items", [])]
    for d in {x for x in ids if ids.count(x) > 1}:
        bad.append(f"two items share the id {d!r}")
    doors = []
    for it in L.get("items", []):
        s, t = it.get("shape", "box"), it.get("type")
        if t not in TYPES:
            bad.append(f"item {it.get('id')} has type {t!r}; plan types are: {', '.join(sorted(TYPES))}")
        if s not in SHAPES:
            bad.append(f"item {it.get('id')} has shape {s!r}; shapes are: {', '.join(sorted(SHAPES))}")
        if s not in ("zone", "door") and it.get("material") not in MATERIALS:
            bad.append(f"item {it.get('id')} has material {it.get('material')!r}; materials are: {', '.join(sorted(MATERIALS))}")
        if s in ("shards", "light_ceiling", "floor_patch") and t != "zone":
            bad.append(f"item {it.get('id')} is a {s}; give it type zone (people walk under or over it)")
        if not (it.get("x1", 0) > it.get("x0", 0) and it.get("y1", 0) > it.get("y0", 0)):
            bad.append(f"item {it.get('id')} has an empty footprint x {it.get('x0')}-{it.get('x1')}, y {it.get('y0')}-{it.get('y1')}")
            continue
        if t == "door" or s == "door":
            doors.append(it)
            if abs(it["y0"]) > .2 or it["x0"] < 0 or it["x1"] > W:
                bad.append(f"door {_fmt(it)} is not on the street edge y = 0")
            continue
        if it["x0"] < -.01 or it["y0"] < -.01 or it["x1"] > W + .01 or it["y1"] > D + .01:
            bad.append(f"item {_fmt(it)} sticks out of the {W} x {D} m envelope")
        if it.get("h", 0) > H + .01 and s != "light_ceiling":
            bad.append(f"item {it['id']} is {it['h']} m tall but the ceiling is {H} m")
    if len(doors) != 1:
        bad.append(f"there are {len(doors)} doors; give exactly one entrance on y = 0")
    solid = obstacles(L)
    for i, a in enumerate(solid):
        for b in solid[i + 1:]:
            ox = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
            oy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
            joined = (ox <= .25 and oy <= .25) or "cable_curtain" in (a.get("shape"), b.get("shape")) \
                or {a.get("shape"), b.get("shape")} == {"memory_frame", "reflect_basin"}   # wall corners, cables fixed to posts, a frame standing in its basin
            if ox > .05 and oy > .05 and not joined and not (a["id"].startswith("column@") or b["id"].startswith("column@")):
                bad.append(f"{_fmt(a)} and {_fmt(b)} overlap by {ox:.2f} x {oy:.2f} m")

    flows = L.get("flows") or []
    if not flows or len(flows[0].get("pts", [])) < 3:
        bad.append("the layout needs flows[0].pts: the visitor's circulation, at least 3 points from the door")
        return bad
    P = flows[0]["pts"]
    if doors:
        d = doors[0]
        if not (d["x0"] - .1 <= P[0][0] <= d["x1"] + .1 and P[0][1] <= 1.0):
            bad.append(f"the circulation starts at {P[0]} but the door is at x {d['x0']}-{d['x1']} on y = 0; start within 1 m of it")
    for p in P:
        if not (0.3 <= p[0] <= W - .3 and 0.3 <= p[1] <= D - .3):
            bad.append(f"circulation point {p} is within 0.3 m of the outer wall or outside it")
    pts = path_points(L)
    for it in solid:                                   # every conflicting item, at its worst point
        dd, x, y = min((_rect_dist(x, y, it), x, y) for x, y in pts)
        if dd < CLEAR:
            where = "inside" if dd < 0 else "only %.2f m from" % dd
            bad.append(f"the circulation passes {where} {_fmt(it)} near ({x:.2f}, {y:.2f}); keep {CLEAR} m clear")

    st = job["stops"]
    if len(st) != 3:
        bad.append(f"there are {len(st)} walkthrough stops; give exactly 3")
    pp = path_points(L)
    for i, s in enumerate(st):
        ax, ay = s.get("at", [None, None])
        if ax is None:
            bad.append(f"stop {i + 1} has no `at` point"); continue
        dmin = min(math.hypot(ax - x, ay - y) for x, y in pp)
        if dmin > .6:
            bad.append(f"stop {i + 1} at ({ax}, {ay}) is {dmin:.2f} m off the circulation; put it on the path")
        lx, ly, lz = s.get("look", [0, 0, 0])
        if not (0 <= lx <= W and 0 <= lz <= D and 0 <= ly <= H):
            bad.append(f"stop {i + 1} looks at ({lx}, {ly}, {lz}) which is outside the room (x, height, y)")
        if not (1.0 <= s.get("h", 1.6) <= 1.8):
            bad.append(f"stop {i + 1} eye height {s.get('h')} m; use 1.0-1.8 m")
        for k in ("cap", "sub"):
            if not s.get(k) or HANGUL.search(s.get(k, "")):
                bad.append(f"stop {i + 1} needs an English `{k}`")
    if sum(s.get("d", 0) for s in st) > 11:
        bad.append("the stops hold for more than 11 seconds in total; the walk has 21 seconds")
    return bad
