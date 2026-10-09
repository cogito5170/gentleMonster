"""The sheets of the CV: cover, plan, picture, object, experience (+ three photo re-stagings).

Each sheet is a 3D set built with engine.Page. Images, big type and objects are rendered; small type and
the architectural drawing layer are set afterwards on the flat page by post.py, so they stay sharp over
the vintage grain. Every sheet function returns a spec: runs (type), lines (drawing), exposures (double
exposures, each optionally rendered from a second camera of the same set).

Facts on the sheets come from docs/portfolio (the applicant's own notes). Blank record lines are left blank.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Vector

from gentle_monster.cv3d import engine as E
from gentle_monster.cv3d.engine import Page
from gentle_monster.cv3d.objects import OBJECTS, spec_lines

INK = "#110f08"
PAPER = "#ceccbe"
STONE = "#848484"
BLUE = "#5a7e91"
RED = "#a8392c"


# ---------------------------------------------------------------- shared props

def _acetate():
    return E.mat_basic("acetate", "#0a0a0a", rough=0.3, coat=0.55, coat_rough=0.14)


def _head_with_glasses(pg: Page, H, at, yaw, skin=True, lens="#1a1a1a", glasses=True):
    head = E.load_head(E.mat_skin("skin") if skin else E.mat_basic("plaster", "#dcd8cf", 0.75), H)
    rig = bpy.data.objects.new("rig", None); pg.link(rig)
    head.parent = rig
    if glasses:
        g = E.glasses(_acetate(), E.mat_acrylic("lens", lens, 0.75), scale=0.30 * H, temples=1.1)
        g.location = (-0.012 * H, -0.30 * H, 0.705 * H); g.parent = rig
    rig.location = at; rig.rotation_euler = (0, 0, yaw)
    return rig, head


def _probe(cx, cy, scale=1.0, glasses_lens="#1a1a1a", z0=0.0, arm=True):
    """Kinetic sculpture after Haus Dosan: black mesh pods hanging in a chrome scaffold, an arm holding a frame."""
    k = scale
    chrome = E.mat_basic("chrome", "#d6d6d4", rough=0.08, metal=1.0)
    graphite = E.mat_basic("graphite", "#2b2b2a", rough=0.35, metal=0.8)
    mesh = E.mat_mesh("mesh", "#0e0e0e", scale=900 / k, solid=True)
    E.cage(cx, cy, 1.6 * k, 0.95 * k, 2.0 * k, 0.011 * k, chrome, bays=3, z0=z0)
    for i, (dx, dy, h, w, tx, ty, yaw) in enumerate([(-0.48, 0.12, 1.35, 0.30, 0.10, -0.06, 0.4), (0.0, -0.05, 1.55, 0.34, -0.04, 0.05, -0.2), (0.46, 0.15, 1.25, 0.28, -0.12, 0.08, 0.9)]):
        base = (cx + dx * k, cy + dy * k, z0 + 0.28 * k)
        E.pod(base, h * k, w * k, mesh, twist=0.25, tilt=(tx, ty), yaw=yaw)
        top = Vector(base) + Vector((0, 0, h * k))
        E.tube(top, (top.x, top.y, z0 + 2.0 * k), 0.008 * k, graphite)
        E.ball(top, 0.03 * k, graphite)
    if arm:
        j0 = Vector((cx + 0.2 * k, cy - 0.1 * k, z0 + 2.0 * k)); j1 = Vector((cx + 0.32 * k, cy - 0.32 * k, z0 + 1.55 * k))
        j2 = Vector((cx + 0.18 * k, cy - 0.62 * k, z0 + 1.22 * k))
        for a, b in ((j0, j1), (j1, j2)):
            E.tube(a, b, 0.022 * k, graphite); E.ball(b, 0.04 * k, graphite)
        g = E.glasses(_acetate(), E.mat_acrylic("lensP", glasses_lens, 0.8), scale=0.16 * k, temples=1.0)
        g.location = (j2.x, j2.y - 0.05 * k, j2.z - 0.07 * k); g.rotation_euler = (0, 0, math.radians(-18))
        return j2
    return None


def _cube(loc, scale, mat, bevel=0.004, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1)
    ob = bpy.context.active_object; ob.location = loc; ob.scale = scale; ob.rotation_euler = rot
    if mat:
        ob.data.materials.append(mat)
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2
    return ob


def _cyl(loc, r, h, mat, verts=96, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h)
    ob = bpy.context.active_object; ob.location = loc; ob.rotation_euler = rot
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return ob


def _sphere(loc, r, mat, scale=(1, 1, 1), seg=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r)
    ob = bpy.context.active_object; ob.location = loc; ob.scale = scale; ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def _plinth(x, y, w, d, h, mat):
    return _cube((x, y, h / 2), (w, d, h), mat, bevel=0.003)


def _light_studio(pg, target=(0, -1.0, 0.8), key=600, red=None):
    t = Vector(target)
    pg.area(Vector((-3.0, -4.4, 3.4)), t, 2.6, key, "#fff3e8")
    pg.area(Vector((3.4, -3.8, 1.8)), t, 2.0, key * 0.3, "#eef3ff")
    pg.area(Vector((0, -2.0, 5.4)), Vector((0, 0, 1.2)), 4.0, key * 0.3, "#ffffff")
    if red:
        pg.spot(Vector(red[0]), Vector(red[1]), red[2], "#ff3a26", angle=red[3] if len(red) > 3 else 26, blend=0.55, radius=0.04)


def _shot_xy(pg, px, py, d):
    return tuple(pg.at(px, py, d))


# ---------------------------------------------------------------- 01 cover

def cover(pg: Page):
    """A head in black acetate frames on a cut plinth, a red stop lamp, the name as a wall relief."""
    pg.world("hdri/moonless_golf_1k.hdr", 0.12)
    lacquer = E.mat_basic("lacquer", INK, rough=0.25, coat=0.8)
    concrete = E.mat_stone("concrete", "#a8a69e", "#8d8b84", "#c4c2ba", scale=6, rough=0.9, bump=0.15)
    lamp = E.mat_emit("lamp", "#e0261a", 1.6)
    pg.text("JEONG", "ArchivoExp-Thin.ttf", 47, 13, 66, d=0.06, extrude=0.035, mat=lacquer, bevel=0.002)
    pg.text("HYEOKJU", "ArchivoExp-Thin.ttf", 47, 13, 109, d=0.06, extrude=0.035, mat=lacquer, bevel=0.002)
    disc = _cyl(pg.at(48, 172, 0.2), 1, 1, lamp, 128, rot=(math.radians(90), 0, 0))
    disc.scale = (0.2 * pg.k(0.2), 0.2 * pg.k(0.2), 0.012)
    ring = _cyl(pg.at(48, 172, 0.215), 1, 1, lacquer, 128, rot=(math.radians(90), 0, 0))
    ring.scale = (0.225 * pg.k(0.215), 0.225 * pg.k(0.215), 0.02)
    eye = _probe(0.62, -0.75, 0.66)
    pg.area(Vector((-3.0, -4.2, 3.0)), Vector((0.4, -1.0, 1.0)), 2.4, 560, "#fff1e4")
    pg.spot(Vector((3.2, -3.0, 1.6)), eye, 2600, "#ff3a26", angle=16, blend=0.6, radius=0.04)
    pg.area(Vector((1.6, 1.2, 3.4)), Vector((0.4, -1.0, 1.0)), 1.2, 300, "#e8eef5")
    pg.area(Vector((0, -2.2, 5.2)), Vector((0, 0, 1.5)), 4.0, 200, "#ffffff")
    return dict(
        runs=[
            dict(s="SPA", font="ArchivoExp-Semi.ttf", size=6.5, x=13, y=24, track=0.32),
            dict(s="ISSUE 01 · 2026 · SEOUL", font="ArchivoExp-Reg.ttf", size=2.6, x=197, y=24, align="RIGHT", track=0.25),
            dict(s="Where did you\nlast stop?", font="InstrumentSerif-Italic.ttf", size=17, x=13, y=252, leading=0.95),
            dict(s="정혁주 — 건축을 전공한 공간 디자이너", font="NotoSerifKR-Bold.ttf", size=3.3, x=197, y=271, align="RIGHT"),
            dict(s="A PROPOSAL FOR GENTLE MONSTER", font="ArchivoExp-Reg.ttf", size=2.4, x=197, y=278, align="RIGHT", track=0.25),
            dict(s="PLAN · PICTURE · OBJECT · EXPERIENCE", font="ArchivoExp-Reg.ttf", size=2.4, x=13, y=278, track=0.25),
        ],
        lines=[
            dict(kind="crop", m=5, n=4),
            dict(kind="rule", x0=13, y0=29, x1=197, y1=29, w=0.12),
            dict(kind="axis", x0=148, y0=122, x1=148, y1=262),
            dict(kind="dim", x0=13, y0=116, x1=105, y1=116, label="1:10  —  H 1,840"),
        ],
        exposures=[
            dict(src="cover_x1.png", box=[13, 135, 90, 60], opacity=0.5, mode="screen",
                 shot=dict(loc=tuple(eye + Vector((-0.45, -1.3, 0.1))), target=tuple(eye), lens=70, res=(900, 600))),
            dict(src="cover_x2.png", box=[45, 165, 75, 60], opacity=0.32, mode="multiply",
                 shot=dict(loc=(-1.6, -3.2, 0.5), target=(0.4, -0.95, 1.2), lens=28, res=(750, 600))),
        ],
    )


# ---------------------------------------------------------------- 02 plan

def plan(pg: Page):
    """Gentle Monster, re-planned: a white study model of the store, its plan pinned to the wall, the STOP frames."""
    pg.world("hdri/royal_esplanade_1k.hdr", 0.18)
    foam = E.mat_basic("foam", "#e9e6de", rough=0.85, sss=0.05)
    lacquer = E.mat_basic("lacquer", INK, rough=0.25, coat=0.8)
    plaster = E.mat_basic("plaster", "#d6d2c8", rough=0.8)
    # plan drawing mounted 3 cm off the wall (2.5D)
    pg.image(pg.asset("plan_titan.png"), 112, 40, 85, 85, d=0.03, thickness=0.004, rough=0.85)
    # the headline set in 3D: lacquer serif standing off the wall
    pg.text("Gentle,", "InstrumentSerif-Regular.ttf", 30, 13, 66, d=0.04, extrude=0.012, mat=lacquer)
    pg.text("then Monster.", "InstrumentSerif-Italic.ttf", 30, 13, 92, d=0.04, extrude=0.012, mat=lacquer)
    # the study model: a foam box with a void, a section cut on the camera side, a small head inside
    base = _cube((0.0, -1.15, 0.36), (1.3, 0.9, 0.72), plaster, bevel=0.002)   # table
    cx, cy, z0 = 0.0, -1.15, 0.72
    for (x, y, w, d, h) in [(-0.5, 0.0, 0.08, 0.7, 0.3), (0.5, 0.0, 0.08, 0.7, 0.3), (0.0, 0.31, 1.08, 0.08, 0.3),
                            (-0.33, -0.31, 0.42, 0.08, 0.3), (0.33, -0.31, 0.42, 0.08, 0.3)]:
        _cube((cx + x, cy + y, z0 + h / 2), (w, d, h), foam, bevel=0.002)
    _cube((cx, cy, z0 + 0.01), (1.08, 0.7, 0.02), foam, bevel=0.001)
    _cyl((cx, cy + 0.02, z0 + 0.03), 0.22, 0.02, E.mat_basic("void", "#6f6d66", rough=0.9))
    mini = E.mat_mesh("minimesh", "#151515", scale=3000, solid=True)
    for (dx, h, yaw) in ((-0.08, 0.2, 0.3), (0.0, 0.24, -0.2), (0.08, 0.18, 0.8)):
        E.pod((cx + dx, cy + 0.02, z0 + 0.06), h, 0.045, mini, twist=0.2, yaw=yaw)
    # three STOP frames on the table edge
    lens_specs = [("#1a1a1a", 0.8), ("#a8392c", 0.45), ("#0b0b0b", 0.95)]
    for i, (lc, la) in enumerate(lens_specs):
        g = E.glasses(_acetate(), E.mat_acrylic(f"lens{i}", lc, la), scale=0.11, temples=1.0, fold=0.35)
        g.location = (-0.42 + i * 0.42, -1.52, 0.72 + 0.03); g.rotation_euler = (math.radians(-8), 0, math.radians(12 - i * 12))
    _light_studio(pg, (0, -1.15, 0.9), key=650, red=((2.8, -3.2, 2.0), (0.42, -1.52, 0.78), 900, 12))
    return dict(
        runs=[
            dict(s="01  PLAN", font="ArchivoExp-Semi.ttf", size=3.2, x=13, y=24, track=0.3),
            dict(s="SPA — ISSUE 01", font="ArchivoExp-Reg.ttf", size=2.4, x=197, y=24, align="RIGHT", track=0.25),
            dict(s="젠틀몬스터는 안경이 아니라\n멈추는 순간을 판다.", font="NotoSerifKR-Bold.ttf", size=5.2, x=13, y=116, leading=1.45),
            dict(s="PRODUCT", font="ArchivoExp-Semi.ttf", size=2.4, x=13, y=243, track=0.25),
            dict(s="STOP 01 · 02 · 03\n뿔테 · 반투명 레드 · 검정", font="NotoSerifKR-Reg.ttf", size=3.0, x=13, y=250, leading=1.5),
            dict(s="CAMPAIGN", font="ArchivoExp-Semi.ttf", size=2.4, x=74, y=243, track=0.25),
            dict(s="Where did you last stop?\n비 오는 밤, 두 개의 빨간불", font="NotoSerifKR-Reg.ttf", size=3.0, x=74, y=250, leading=1.5),
            dict(s="SPACE", font="ArchivoExp-Semi.ttf", size=2.4, x=136, y=243, track=0.25),
            dict(s="The Synthetic Titan\n거인의 뇌 속에서 안경을 채집한다", font="NotoSerifKR-Reg.ttf", size=3.0, x=136, y=250, leading=1.5),
            dict(s="PLAN 1:200 — THE SYNTHETIC TITAN", font="ArchivoExp-Reg.ttf", size=2.1, x=112, y=130, track=0.2),
        ],
        lines=[
            dict(kind="crop", m=5, n=4),
            dict(kind="rule", x0=13, y0=29, x1=197, y1=29, w=0.12),
            dict(kind="rule", x0=13, y0=236, x1=197, y1=236, w=0.12),
            dict(kind="dim", x0=13, y0=283, x1=197, y1=283, label="A4  210 × 297  —  GRID 15"),
        ],
        exposures=[
            dict(src="plan_x1.png", box=[13, 128, 75, 50], opacity=0.38, mode="multiply",
                 shot=dict(loc=(0.6, -1.9, 1.35), target=(0.0, -1.1, 0.8), lens=40, res=(900, 600))),
        ],
    )


# ---------------------------------------------------------------- 03 picture (prints of three re-staged photographs)

def picture(pg: Page):
    pg.world("hdri/royal_esplanade_1k.hdr", 0.16)
    lacquer = E.mat_basic("lacquer", INK, rough=0.25, coat=0.8)
    xs = [13, 77, 141]
    for i, n in enumerate(("photo_puddle", "photo_sprout", "photo_bulb")):
        pg.image(pg.out(n + ".png"), xs[i], 48, 56, 70, d=0.02 + 0.01 * i, thickness=0.002, rough=0.3)
    for i, w in enumerate(("웅덩이", "새싹", "전구")):
        pg.text(w, "NotoSerifKR-Bold.ttf", 16, xs[i], 146, d=0.03, extrude=0.01, mat=lacquer)
    # a camera on a plinth: the instrument
    body = E.mat_basic("body", "#1b1b1b", rough=0.45)
    chrome = E.mat_basic("chrome", "#d8d8d8", rough=0.12, metal=1.0)
    ph = 0.5; cx = 0.68
    _plinth(cx, -1.0, 0.36, 0.36, ph, E.mat_basic("plinth", "#bdbab1", rough=0.8))
    cam_body = _cube((cx, -1.0, ph + 0.075), (0.26, 0.09, 0.15), body, bevel=0.012)
    _cyl((cx + 0.03, -1.1, ph + 0.07), 0.05, 0.1, body, rot=(math.radians(90), 0, 0))
    _cyl((cx + 0.03, -1.155, ph + 0.07), 0.042, 0.012, E.mat_acrylic("glass", "#2a3a40", 0.9), rot=(math.radians(90), 0, 0))
    _cube((cx - 0.08, -1.0, ph + 0.16), (0.05, 0.05, 0.03), chrome, bevel=0.004)
    _light_studio(pg, (0, -0.6, 1.4), key=600)
    return dict(
        runs=[
            dict(s="02  PICTURE", font="ArchivoExp-Semi.ttf", size=3.2, x=13, y=24, track=0.3),
            dict(s="ONE TO ONE — A PHOTOGRAPH, A WORD", font="ArchivoExp-Reg.ttf", size=2.4, x=197, y=24, align="RIGHT", track=0.25),
            dict(s="puddle", font="InstrumentSerif-Italic.ttf", size=5, x=13, y=156),
            dict(s="sprout", font="InstrumentSerif-Italic.ttf", size=5, x=77, y=156),
            dict(s="bulb", font="InstrumentSerif-Italic.ttf", size=5, x=141, y=156),
            dict(s="단어는 사진의 주인공이 아니라\n내가 실제로 멈춰서 본 것을 부른다.", font="NotoSerifKR-Bold.ttf", size=4.6, x=13, y=196, leading=1.5),
            dict(s="밤의 불빛, 해 질 녘, 거리의 사람.\n좋은 사진 뒤에는 늘 좋은 장소가 있었다.", font="NotoSerifKR-Reg.ttf", size=3.1, x=13, y=222, leading=1.6),
            dict(s="Prints: the author's photographs re-staged in 3D. Originals are not reproduced.", font="InstrumentSerif-Italic.ttf", size=3.0, x=13, y=279),
        ],
        lines=[
            dict(kind="crop", m=5, n=4),
            dict(kind="rule", x0=13, y0=29, x1=197, y1=29, w=0.12),
            dict(kind="dim", x0=13, y0=40, x1=69, y1=40, label="56"),
            dict(kind="dim", x0=77, y0=40, x1=133, y1=40, label="56"),
            dict(kind="dim", x0=141, y0=40, x1=197, y1=40, label="56"),
        ],
        exposures=[],
    )


def _photo_cam(pg: Page, loc, target, lens):
    cam = pg.sc.camera; cam.location = loc; pg._aim(cam, Vector(target)); cam.data.lens = lens; cam.data.sensor_fit = "AUTO"


def photo_puddle(pg: Page):
    """Dusk: blue and black barrel carts, red tail lights, all of it in a rain puddle."""
    pg.world("hdri/blouberg_sunrise_2_1k.hdr", 0.5, rot=1.2)
    asphalt = E.mat_stone("asphalt", "#2c2d2e", "#1a1b1c", "#4a4b4c", scale=40, rough=0.8, bump=0.3)
    _cube((0, 0, -0.01), (20, 20, 0.02), asphalt, bevel=0)
    water = E.mat_basic("water", "#0c1114", rough=0.02, coat=1.0)
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1.4, fill_type="NGON"); pud = bpy.context.active_object
    pud.location = (0.2, -1.0, 0.002); pud.scale = (1.6, 0.8, 1); pud.data.materials.append(water)
    blue = E.mat_basic("blue", "#3f6f95", rough=0.4, coat=0.4); black = E.mat_basic("blk", "#141414", rough=0.4)
    tail = E.mat_emit("tail", "#ff2a1a", 18)
    for i in range(5):
        x = -1.2 + i * 0.62
        _cyl((x, 0.6, 0.38), 0.24, 0.62, blue if i % 2 == 0 else black, rot=(0, math.radians(90), 0))
        _sphere((x - 0.31, 0.4, 0.42), 0.035, tail)
    _cube((1.9, -0.2, 0.25), (0.25, 0.25, 0.5), E.mat_basic("cone", "#e0602a", rough=0.5), bevel=0.02)
    pg.point((0, 3, 2.5), 300, "#9fb9d6", 1.5)
    _photo_cam(pg, (0.4, -4.6, 0.55), (0.0, 0.4, 0.3), 45)


def photo_sprout(pg: Page):
    """Backlit coconut sprout on a beach among dry fronds."""
    pg.world("hdri/venice_sunset_1k.hdr", 0.9, rot=3.4)
    sand = E.mat_stone("sand", "#c9c1a3", "#a69c7c", "#e3dcc3", scale=60, rough=0.95, bump=0.35)
    _cube((0, 0, -0.01), (20, 20, 0.02), sand, bevel=0)
    husk = E.mat_stone("husk", "#6b5d3b", "#423621", "#9c946e", scale=12, rough=0.9, bump=0.5)
    _sphere((0, 0, 0.12), 0.16, husk, scale=(1.2, 1, 0.8))
    leaf = E.mat_basic("leaf", "#6f8f30", rough=0.5, sss=0.3)
    stem = E.mat_basic("stem", "#5f7a2c", rough=0.6)
    _cyl((0, 0, 0.32), 0.012, 0.3, stem, 16)
    for a, s in ((25, 1), (-30, -1)):
        lf = _sphere((s * 0.09, 0, 0.47), 0.11, leaf, scale=(1.0, 0.18, 0.32)); lf.rotation_euler = (0, math.radians(a), 0)
    frond = E.mat_basic("frond", "#9c8a5e", rough=0.9)
    for i in range(6):
        f = _cube((-1.2 + i * 0.5, 0.8 + (i % 2) * 0.4, 0.01), (1.2, 0.05, 0.01), frond, bevel=0, rot=(0, 0, math.radians(20 * i)))
    pg.sun_light = pg.spot(Vector((0.4, 3.0, 0.6)), Vector((0, 0, 0.4)), 2500, "#fff2d8", angle=50, radius=0.3)
    _photo_cam(pg, (0.15, -1.6, 0.35), (0, 0, 0.35), 70)


def photo_bulb(pg: Page):
    """Black and white night: string lights over a rooftop, people seated below, seen through a dark frame."""
    pg.world(None, 0.0, color="#000000")
    pg.ground.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = E.hexrgb("#1a1a1a")
    bulb = E.mat_emit("bulb", "#fff4e0", 28)
    wire = E.mat_basic("wire", "#111111", rough=0.6)
    for row in range(2):
        for i in range(14):
            t = i / 13; x = -2.6 + 5.2 * t; z = 2.3 - 0.45 * math.sin(math.pi * t) + row * 0.2
            _sphere((x, -0.6 - row * 1.2, z), 0.035, bulb, seg=16)
    for row in range(2):
        pass
    body = E.mat_basic("people", "#202020", rough=0.8)
    for i in range(5):
        _sphere((-1.6 + i * 0.8, -0.9, 0.9), 0.11, body); _cube((-1.6 + i * 0.8, -0.9, 0.55), (0.32, 0.22, 0.5), body, bevel=0.05)
    pg.point((0, -0.8, 2.5), 120, "#fff4e0", 2.0)
    frame = E.mat_basic("frame", "#050505", rough=0.9)
    _cube((-1.4, -3.0, 1.2), (0.2, 0.2, 4), frame, bevel=0)
    _photo_cam(pg, (-0.4, -4.4, 1.0), (0.2, -0.6, 1.6), 32)


# ---------------------------------------------------------------- 04 object

def object_(pg: Page):
    """Four store synopses rebuilt in the grammar of Gentle Monster's own stores, on one stainless counter."""
    pg.world("hdri/royal_esplanade_1k.hdr", 0.22)
    steel = E.mat_basic("steel", "#b8b8b6", rough=0.28, metal=1.0)
    dark = E.mat_basic("counterbase", "#2a2a29", rough=0.6)
    chrome = E.mat_basic("chrome", "#d6d6d4", rough=0.08, metal=1.0)
    _cube((0, -0.3, 0.77), (2.04, 0.6, 0.03), steel, bevel=0.002)                # cantilevered stainless shelf
    top = 0.785; xs = [-0.74, -0.25, 0.25, 0.74]; cy = -0.3; K = 1.5
    _mark = set(bpy.data.objects)
    # 1 The Synthetic Titan: a faceted black-mesh head in a chrome cage
    T = OBJECTS["titan"]["params"]
    rig, head = _head_with_glasses(pg, 0.24, Vector((xs[0], cy, top)), math.radians(16), skin=False, glasses=False)
    head.data.materials.clear(); head.data.materials.append(E.mat_mesh("titanmesh", "#121212", scale=2500, solid=True))
    st = head.modifiers.new("st", "SIMPLE_DEFORM"); st.deform_method = "STRETCH"; st.factor = T["stretch"]; st.deform_axis = "Z"
    tw = head.modifiers.new("tw", "SIMPLE_DEFORM"); tw.deform_method = "TWIST"; tw.angle = math.radians(T["twist_deg"]); tw.deform_axis = "Z"
    E.faceted(head, T["facets"])
    E.cage(xs[0], cy, 0.34, 0.3, 0.46, 0.004, chrome, bays=2, z0=top)
    acr = E.mat_acrylic("shards", "#9aa3a8", 0.35)
    import random; rnd = random.Random(7)
    for i in range(T["shards"]):
        a = rnd.random() * math.tau; r = 0.08 + rnd.random() * 0.05
        E.shard((xs[0] + r * math.cos(a), cy + r * math.sin(a), top + 0.1 + rnd.random() * 0.3), 0.012 + rnd.random() * 0.018, acr,
                (rnd.random() * 3, rnd.random() * 3, rnd.random() * 3))
    E.group_scale([o for o in bpy.data.objects if o not in _mark], (xs[0], cy, top), K); _mark = set(bpy.data.objects)
    # 2 Residue of Scent: a porous bone-white cluster, red wax settling at its foot
    P = OBJECTS["scent"]["params"]
    bone = E.mat_bone("bone", "#e4ded0", scale=90)
    import random; rnd = random.Random(3)
    cells = [((0.0, 0.0, P["r0"]), P["r0"])]
    for i in range(1, P["cells"]):
        (px, py, pz), pr = cells[rnd.randrange(len(cells))]
        r = max(0.018, pr * P["growth"] * (0.85 + 0.3 * rnd.random()))
        a = rnd.random() * math.tau; up = 0.25 + rnd.random() * 0.6
        d = (pr + r) * 0.82
        cells.append(((px + d * math.cos(a) * (1 - up), py + d * math.sin(a) * (1 - up) * 0.6, max(r, pz + d * up)), r))
    for (dx, dy, dz), r in cells:
        b = E.rough_ball((xs[1] + dx, cy + dy, top + dz), r, P["bumps"], bone, seed=int(r * 1000))
    _sphere((xs[1] + 0.05, cy - 0.12, top + 0.003), 0.06, E.mat_basic("redwax", "#8e1712", rough=0.3, coat=0.5), scale=(1, 0.8, 0.06))
    E.group_scale([o for o in bpy.data.objects if o not in _mark], (xs[1], cy, top), K); _mark = set(bpy.data.objects)
    # 3 Monolithic Fusion: a rough granite ball on a slatted steel ramp, cables hanging from above
    granite = E.mat_stone("granite", "#77726b", "#2a2826", "#cfc8bc", scale=40, rough=0.85, bump=0.5)
    for i in range(7):
        _cube((xs[2] - 0.15 + i * 0.05, cy, top + 0.01 + i * 0.006), (0.03, 0.3, 0.012), steel, bevel=0.001)
    E.rough_ball((xs[2] + 0.06, cy - 0.02, top + 0.13), 0.085, 0.025, granite)
    for i in range(5):
        E.tube((xs[2] - 0.12 + i * 0.06, cy + 0.1, top + 0.06 + (i % 3) * 0.04), (xs[2] - 0.12 + i * 0.06, cy + 0.1, 3.0), 0.0025, dark)
    E.group_scale([o for o in bpy.data.objects if o not in _mark], (xs[2], cy, top), K); _mark = set(bpy.data.objects)
    # 4 The Stratified Apothecary: a stratified vessel on three steel stilts over a brass basin
    cols = ["#a5532f", "#6b4a33", "#b8743f", "#7a3a22", "#9b4a2b", "#8a3b24", "#a86a3c"]
    z = top + 0.16
    for i in range(8):
        h = 0.018 + 0.012 * ((i * 7) % 4)
        _cyl((xs[3], cy, z + h / 2), 0.07 + 0.004 * ((i * 5) % 3), h, E.mat_stone(f"clay{i}", cols[i % 7], cols[(i + 3) % 7], cols[(i + 1) % 7], scale=30, rough=0.95, bump=0.4), 64)
        z += h
    for a in (0, 120, 240):
        x = xs[3] + 0.06 * math.cos(math.radians(a)); y = cy + 0.06 * math.sin(math.radians(a))
        E.tube((x, y, top), (x, y, top + 0.16), 0.004, chrome)
    alu_cast = E.mat_basic("castalu", "#a9abab", rough=0.35, metal=1.0)
    E.basin(xs[3], cy - 0.01, top + 0.002, 0.13, 0.085, alu_cast, wobble=0.16, beads=OBJECTS["apothecary"]["params"]["beads"])
    _sphere((xs[3], cy - 0.01, top + 0.012), 0.08, E.mat_basic("water2", "#10181b", rough=0.02, coat=1), scale=(1.4, 0.9, 0.02))
    E.group_scale([o for o in bpy.data.objects if o not in _mark], (xs[3], cy, top), K); _mark = set(bpy.data.objects)
    _light_studio(pg, (0, -0.3, 1.0), key=700)
    return dict(
        runs=[
            dict(s="03  OBJECT", font="ArchivoExp-Semi.ttf", size=3.2, x=13, y=24, track=0.3),
            dict(s="FOUR STORES, FOUR OBJECTS — 1:20", font="ArchivoExp-Reg.ttf", size=2.4, x=197, y=24, align="RIGHT", track=0.25),
            dict(s="Objects that\nmake you stop.", font="InstrumentSerif-Italic.ttf", size=15, x=13, y=62, leading=0.98),
            dict(s="The Synthetic Titan", font="InstrumentSerif-Regular.ttf", size=4.2, x=13, y=255),
            dict(s="Residue of Scent", font="InstrumentSerif-Regular.ttf", size=4.2, x=60, y=255),
            dict(s="Monolithic Fusion", font="InstrumentSerif-Regular.ttf", size=4.2, x=107, y=255),
            dict(s="The Stratified Apothecary", font="InstrumentSerif-Regular.ttf", size=4.2, x=154, y=255),
            dict(s="GENTLE MONSTER\n늘이고 비튼 다면체 · 렌즈 파편", font="NotoSerifKR-Reg.ttf", size=2.4, x=13, y=262, leading=1.6),
            dict(s="TAMBURINS\n증식하는 세포 군집", font="NotoSerifKR-Reg.ttf", size=2.4, x=60, y=262, leading=1.6),
            dict(s="ACNE STUDIOS\n화강암 구체 · 강철 레일", font="NotoSerifKR-Reg.ttf", size=2.4, x=107, y=262, leading=1.6),
            dict(s="AESOP\n지층 · 액체형 주조 수반", font="NotoSerifKR-Reg.ttf", size=2.4, x=154, y=262, leading=1.6),
            *[dict(s="\n".join(spec_lines(k)), font="ArchivoExp-Reg.ttf", size=1.5, x=13 + i * 47, y=272, leading=1.75, color="#3e3e39")
              for i, k in enumerate(("titan", "scent", "monolith", "apothecary"))],
        ],
        lines=[
            dict(kind="crop", m=5, n=4),
            dict(kind="rule", x0=13, y0=29, x1=197, y1=29, w=0.12),
            dict(kind="rule", x0=13, y0=248, x1=197, y1=248, w=0.12),
            dict(kind="dim", x0=13, y0=241, x1=197, y1=241, label="SHELF 2,040 — STAINLESS"),
        ],
        exposures=[
            dict(src="object_x1.png", box=[120, 38, 77, 52], opacity=0.4, mode="multiply",
                 shot=dict(loc=(-0.3, -1.3, 1.15), target=(-0.74, -0.3, 1.05), lens=55, res=(900, 600))),
        ],
    )


# ---------------------------------------------------------------- 05 experience

def experience(pg: Page):
    """Sector A: five cloths in the applicant's colours, his frames and a vintage watch; the record."""
    pg.world("hdri/royal_esplanade_1k.hdr", 0.2)
    cols = [("#1d1b19", "Black"), ("#2c2716", "Olive"), ("#c4b29b", "Beige"), ("#c3bfb1", "Off-white"), ("#445162", "Slate")]
    rod = E.mat_basic("rod", "#2a2a2a", rough=0.3, metal=1.0)
    for i, (c, n) in enumerate(cols):
        px = 13 + i * 37
        cloth = E.cloth(pg, px, 40, 32, 92, d=0.03, color=c, seed=i)
        _cyl(pg.at(px + 16, 39, 0.035), 0.004, 0.36, rod, 16, rot=(0, math.radians(90), 0))
    plinth = E.mat_basic("plinth", "#bdbab1", rough=0.85)
    _plinth(0.45, -1.0, 0.5, 0.36, 0.8, plinth)
    g = E.glasses(_acetate(), E.mat_acrylic("lensE", "#1a1a1a", 0.8), scale=0.16, temples=1.0, fold=0.4)
    g.location = (0.35, -1.0, 0.8 + 0.035); g.rotation_euler = (math.radians(-6), 0, math.radians(18))
    steel = E.mat_basic("steel", "#b9b6ae", rough=0.2, metal=1.0)
    dial = E.mat_basic("dial", "#e8e1cf", rough=0.5)
    leather = E.mat_basic("leather", "#3a2416", rough=0.55)
    _cyl((0.6, -1.02, 0.8 + 0.008), 0.03, 0.012, steel, 64)
    _cyl((0.6, -1.02, 0.8 + 0.0145), 0.026, 0.002, dial, 64)
    _cube((0.6, -0.95, 0.803), (0.026, 0.11, 0.004), leather, bevel=0.001)
    _cube((0.6, -1.09, 0.803), (0.026, 0.11, 0.004), leather, bevel=0.001)
    _light_studio(pg, (0, -0.8, 1.2), key=650)
    return dict(
        runs=[
            dict(s="04  EXPERIENCE", font="ArchivoExp-Semi.ttf", size=3.2, x=13, y=24, track=0.3),
            dict(s="SECTOR A — MY STYLE", font="ArchivoExp-Reg.ttf", size=2.4, x=197, y=24, align="RIGHT", track=0.25),
            *[dict(s=f"{n.upper()}\n{c.upper()}", font="ArchivoExp-Reg.ttf", size=2.1, x=13 + i * 37, y=140, leading=1.6, track=0.15) for i, (c, n) in enumerate(cols)],
            dict(s="헤어 스타일, 옷의 톤과 향의 무드를\n그날 갈 장소에 맞춘다.", font="NotoSerifKR-Bold.ttf", size=4.6, x=13, y=166, leading=1.5),
            dict(s="뿔테 안경 · 반투명 선글라스 · 검정 선글라스\n빈티지 시계 · 딥디크, 조말론, 버버리", font="NotoSerifKR-Reg.ttf", size=2.9, x=13, y=186, leading=1.6),
            dict(s="사람은 공간을 만들고, 공간은 다시 사람을 만든다.\n나는 그 사이에서, 사람이 발걸음을 멈추는 순간을 설계한다.", font="NotoSerifKR-Reg.ttf", size=3.1, x=13, y=214, leading=1.6),
            dict(s="EDUCATION", font="ArchivoExp-Semi.ttf", size=2.2, x=13, y=246, track=0.25),
            dict(s="건축학 전공 — 학교 · 기간", font="NotoSerifKR-Reg.ttf", size=2.8, x=46, y=246),
            dict(s="EXPERIENCE", font="ArchivoExp-Semi.ttf", size=2.2, x=13, y=256, track=0.25),
            dict(s="회사 · 역할 · 기간", font="NotoSerifKR-Reg.ttf", size=2.8, x=46, y=256),
            dict(s="CONTACT", font="ArchivoExp-Semi.ttf", size=2.2, x=13, y=266, track=0.25),
            dict(s="이메일 · 전화 · 인스타그램", font="NotoSerifKR-Reg.ttf", size=2.8, x=46, y=266),
            dict(s="Jeong Hyeokju, 2026", font="InstrumentSerif-Italic.ttf", size=4, x=197, y=279, align="RIGHT"),
        ],
        lines=[
            dict(kind="crop", m=5, n=4),
            dict(kind="rule", x0=13, y0=29, x1=197, y1=29, w=0.12),
            dict(kind="rule", x0=46, y0=247.5, x1=120, y1=247.5, w=0.1, color="#848484"),
            dict(kind="rule", x0=46, y0=257.5, x1=120, y1=257.5, w=0.1, color="#848484"),
            dict(kind="rule", x0=46, y0=267.5, x1=120, y1=267.5, w=0.1, color="#848484"),
        ],
        exposures=[
            dict(src="experience_x1.png", box=[120, 150, 77, 60], opacity=0.42, mode="multiply",
                 shot=dict(loc=(0.75, -1.45, 1.2), target=(0.45, -1.0, 0.82), lens=55, res=(900, 700))),
        ],
    )


PAGES = {
    "cover": (cover, dict(ground="#c9c7bd", floor_from=0.9, exposure=-0.35)),
    "plan": (plan, dict(ground="#c9c7bd", floor_from=0.75, exposure=-0.3)),
    "picture": (picture, dict(ground="#c9c7bd", floor_from=0.75, exposure=-0.3)),
    "object": (object_, dict(ground="#c9c7bd", floor_from=0.45, exposure=-0.3)),
    "experience": (experience, dict(ground="#c9c7bd", floor_from=0.75, exposure=-0.3)),
    "photo_puddle": (photo_puddle, dict(sweep=None, ground="#2c2d2e", floor_from=0.0, exposure=-0.2)),
    "photo_sprout": (photo_sprout, dict(sweep=None, ground="#c9c1a3", floor_from=0.0, exposure=-0.4)),
    "photo_bulb": (photo_bulb, dict(sweep=None, ground="#1a1a1a", floor_from=0.0, exposure=0.0)),
}


def build(name, res=(1240, 1754), samples=96, out_dir=None):
    fn, kw = PAGES[name]
    pg = Page(res=res, samples=samples, **kw)
    pg.out_dir = out_dir
    spec = fn(pg) or {}
    return pg, spec
