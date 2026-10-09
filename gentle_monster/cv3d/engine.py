"""cv3d engine: a 2D page laid out inside a 3D set and rendered with Blender Cycles.

The page is A4 (210 x 297 mm). One page millimetre is one world centimetre, so the page is a 2.10 x 2.97 m
wall with a floor sweeping out in front of it. The camera looks straight at the wall with a long lens.

Every element is placed in PAGE coordinates (px, py in mm from the top-left) plus a depth `d` (metres in
front of the wall). `Page.at()` slides the point along the camera ray and `Page.k()` gives the matching
scale, so an element keeps its page position and apparent size at any depth:

    d = 0          printed on the wall                 2D
    0 < d < 0.3    mounted, extruded, casting shadows  2.5D
    on the floor   objects standing in the room        3D

Runs inside Blender's Python (pip `bpy` 5.x). Assets (fonts, HDRI, head scan) come from GM_CV3D_ASSETS.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ASSETS = Path(os.environ.get("GM_CV3D_ASSETS", Path(__file__).with_name("assets")))
PW, PH = 2.10, 2.97          # page in metres (1 page mm = 1 cm)
MM = 0.01                    # one page millimetre in metres


def hexrgb(h: str, a: float = 1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*c, a)


# ---------------------------------------------------------------- materials

def _bsdf(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes["Principled BSDF"], m.node_tree


def mat_basic(name, color, rough=0.5, metal=0.0, coat=0.0, coat_rough=0.05, spec=0.5, sss=0.0):
    m, p, _ = _bsdf(name)
    p.inputs["Base Color"].default_value = hexrgb(color)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = coat_rough
    p.inputs["Specular IOR Level"].default_value = spec
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
    return m


def mat_paper(name, color, grain=0.15):
    m, p, nt = _bsdf(name)
    p.inputs["Base Color"].default_value = hexrgb(color)
    p.inputs["Roughness"].default_value = 0.92
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 900; n.inputs["Detail"].default_value = 6
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = grain; b.inputs["Distance"].default_value = 0.0004
    nt.links.new(n.outputs["Fac"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_acrylic(name, color, alpha=0.55):
    """Tinted acrylic: transparent (coloured shadows) + glossy surface."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = hexrgb(color)
    gl = nt.nodes.new("ShaderNodeBsdfPrincipled"); gl.inputs["Base Color"].default_value = hexrgb(color); gl.inputs["Roughness"].default_value = 0.06
    gl.inputs["Coat Weight"].default_value = 1
    fr = nt.nodes.new("ShaderNodeLayerWeight"); fr.inputs["Blend"].default_value = 0.35
    mix = nt.nodes.new("ShaderNodeMixShader")
    mt = nt.nodes.new("ShaderNodeMath"); mt.operation = "MAXIMUM"; mt.inputs[1].default_value = alpha
    nt.links.new(fr.outputs["Fresnel"], mt.inputs[0]); nt.links.new(mt.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(gl.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def mat_emit(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = hexrgb(color); e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m


def mat_image(name, path, rough=0.35, coat=0.0):
    m, p, nt = _bsdf(name)
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(str(path)); t.extension = "EXTEND"
    nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough; p.inputs["Coat Weight"].default_value = coat
    return m


def mat_stone(name, base, dark, light, scale=18.0, rough=0.85, bump=0.6):
    m, p, nt = _bsdf(name)
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = 12; n.inputs["Roughness"].default_value = 0.7
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = scale * 9
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexrgb(dark); ramp.color_ramp.elements[1].color = hexrgb(light)
    e = ramp.color_ramp.elements.new(0.5); e.color = hexrgb(base)
    mix = nt.nodes.new("ShaderNodeMath"); mix.operation = "MULTIPLY_ADD"; mix.inputs[1].default_value = 0.6
    nt.links.new(v.outputs["Distance"], mix.inputs[0]); nt.links.new(n.outputs["Fac"], mix.inputs[2])
    nt.links.new(mix.outputs[0], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = bump; b.inputs["Distance"].default_value = 0.01
    nt.links.new(n.outputs["Fac"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    return m


def mat_skin(name):
    m, p, nt = _bsdf(name)
    col = nt.nodes.new("ShaderNodeTexImage"); col.image = bpy.data.images.load(str(ASSETS / "Map-COL.jpg"))
    nrm = nt.nodes.new("ShaderNodeTexImage"); nrm.image = bpy.data.images.load(str(ASSETS / "Infinite-Level_02_Tangent_SmoothUV.jpg")); nrm.image.colorspace_settings.name = "Non-Color"
    spec = nt.nodes.new("ShaderNodeTexImage"); spec.image = bpy.data.images.load(str(ASSETS / "Map-SPEC.jpg")); spec.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.0
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "MULTIPLY_ADD"; inv.inputs[1].default_value = -0.35; inv.inputs[2].default_value = 0.62
    nt.links.new(col.outputs["Color"], p.inputs["Base Color"]); nt.links.new(nrm.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], p.inputs["Normal"]); nt.links.new(spec.outputs["Color"], inv.inputs[0]); nt.links.new(inv.outputs[0], p.inputs["Roughness"])
    p.inputs["Subsurface Weight"].default_value = 0.22
    p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
    p.inputs["Subsurface Scale"].default_value = 0.012
    return m


# ---------------------------------------------------------------- page

class Page:
    def __init__(self, ground="#ececea", lens=85.0, res=(1240, 1754), samples=96, floor_from=None, sweep=0.45, exposure=0.0):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.sc = bpy.context.scene
        self.fonts = {}
        self.res = res
        self.lens = lens
        self.D = (PH * lens) / 36.0                       # camera distance so the frame is the page at the wall
        self.Zb = -(floor_from if floor_from is not None else 0.0)  # page bottom height on the wall plane
        self.C = Vector((0.0, -self.D, self.Zb + PH / 2))
        cam_data = bpy.data.cameras.new("cam"); cam_data.lens = lens; cam_data.sensor_fit = "VERTICAL"; cam_data.sensor_height = 36.0
        cam_data.clip_start = 0.05; cam_data.clip_end = 100
        cam = bpy.data.objects.new("cam", cam_data); cam.location = self.C; cam.rotation_euler = (math.radians(90), 0, 0)
        self.sc.collection.objects.link(cam); self.sc.camera = cam
        self.sc.render.engine = "CYCLES"; self.sc.cycles.device = "CPU"
        self.sc.cycles.samples = samples; self.sc.cycles.use_denoising = True; self.sc.cycles.use_adaptive_sampling = True
        self.sc.cycles.max_bounces = 8; self.sc.cycles.transparent_max_bounces = 16
        self.sc.render.resolution_x, self.sc.render.resolution_y = res; self.sc.render.resolution_percentage = 100
        self.sc.view_settings.view_transform = "AgX"; self.sc.view_settings.look = "AgX - Medium High Contrast"
        self.sc.view_settings.exposure = exposure
        self.sc.render.image_settings.file_format = "PNG"
        self.ground = mat_paper("ground", ground)
        if sweep is not None:
            self._sweep(sweep)
        self.world(None, 0.0)

    # page mm -> world point on the wall plane, then slid toward the camera by depth d (m)
    def at(self, px, py, d=0.0):
        w = Vector(((px - 105) * MM, 0.0, self.Zb + (297 - py) * MM))
        return self.C + (w - self.C) * ((self.D - d) / self.D)

    def k(self, d):
        return (self.D - d) / self.D

    def _sweep(self, R):
        """Wall (y=0) + floor (z=0) joined by a quarter-cylinder of radius R: one seamless ground."""
        bm = bmesh.new()
        prof = [(-12.0, 0.0)]
        prof += [(-R + R * math.sin(a), R - R * math.cos(a)) for a in [i * (math.pi / 2) / 24 for i in range(25)]]
        prof = [(y - 0.0, z) for y, z in prof]
        prof = [(y, z) for y, z in prof] + [(0.0, 12.0)]
        # profile in (y, z): floor from y=-12 to y=-R, arc up to wall at y=0, z=R, then up
        pts = [(-12.0, 0.0)] + [(-R + R * math.sin(t), R - R * math.cos(t)) for t in [i * (math.pi / 2) / 24 for i in range(25)]] + [(0.0, 12.0)]
        rows = []
        for y, z in pts:
            rows.append([bm.verts.new((x, y, z)) for x in (-8.0, 8.0)])
        for a, b in zip(rows, rows[1:]):
            bm.faces.new((a[0], a[1], b[1], b[0]))
        me = bpy.data.meshes.new("sweep"); bm.to_mesh(me); bm.free()
        for p in me.polygons:
            p.use_smooth = True
        ob = bpy.data.objects.new("sweep", me); ob.data.materials.append(self.ground)
        # the sweep sits so its floor is at z = 0 and its wall at y = 0, below the page bottom if Zb < 0
        ob.location = (0, 0, min(0.0, 0.0))
        self.sc.collection.objects.link(ob)
        self.floor_z = 0.0

    def world(self, hdri, strength=0.3, rot=0.0, color="#000000"):
        w = bpy.data.worlds.new("w"); w.use_nodes = True; self.sc.world = w
        nt = w.node_tree; bg = nt.nodes["Background"]
        if hdri:
            env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(str(ASSETS / hdri))
            mp = nt.nodes.new("ShaderNodeMapping"); tc = nt.nodes.new("ShaderNodeTexCoord"); mp.inputs["Rotation"].default_value[2] = rot
            nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
            nt.links.new(env.outputs["Color"], bg.inputs["Color"])
        else:
            bg.inputs["Color"].default_value = hexrgb(color)
        bg.inputs["Strength"].default_value = strength

    # ---------------------------------------------------------------- lights
    def area(self, loc, target, size, power, color="#ffffff", shape="RECTANGLE", size_y=None, spread=180):
        ld = bpy.data.lights.new("area", "AREA"); ld.energy = power; ld.color = hexrgb(color)[:3]; ld.shape = shape
        ld.size = size; ld.size_y = size_y or size; ld.spread = math.radians(spread)
        ob = bpy.data.objects.new("area", ld); ob.location = loc; self.sc.collection.objects.link(ob)
        self._aim(ob, target); return ob

    def spot(self, loc, target, power, color="#ffffff", angle=35, blend=0.4, radius=0.1):
        ld = bpy.data.lights.new("spot", "SPOT"); ld.energy = power; ld.color = hexrgb(color)[:3]
        ld.spot_size = math.radians(angle); ld.spot_blend = blend; ld.shadow_soft_size = radius
        ob = bpy.data.objects.new("spot", ld); ob.location = loc; self.sc.collection.objects.link(ob)
        self._aim(ob, target); return ob

    def point(self, loc, power, color="#ffffff", radius=0.05):
        ld = bpy.data.lights.new("pt", "POINT"); ld.energy = power; ld.color = hexrgb(color)[:3]; ld.shadow_soft_size = radius
        ob = bpy.data.objects.new("pt", ld); ob.location = loc; self.sc.collection.objects.link(ob); return ob

    @staticmethod
    def _aim(ob, target):
        d = Vector(target) - Vector(ob.location)
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

    def studio(self, key=900, fill=250, top=300, warm="#fff6ec"):
        self.area(Vector((-2.6, -4.2, 4.2)), Vector((0, 0, 1.0)), 2.4, key, warm)
        self.area(Vector((3.4, -3.6, 1.8)), Vector((0, 0, 1.0)), 2.0, fill, "#f2f5ff")
        self.area(Vector((0, -1.6, 5.2)), Vector((0, -1.0, 0)), 3.0, top, "#ffffff")

    # ---------------------------------------------------------------- type
    def font(self, file):
        if file not in self.fonts:
            self.fonts[file] = bpy.data.fonts.load(str(ASSETS / "fonts" / file))
        return self.fonts[file]

    def text(self, s, font, size, px, py, d=0.0015, extrude=0.0, mat=None, align="LEFT", track=0.0, leading=1.2,
             width=None, bevel=0.0, upper=False):
        """size = em in page mm; (px, py) = left (or align point) of the first BASELINE in page mm."""
        cu = bpy.data.curves.new("t", "FONT"); cu.body = s.upper() if upper else s
        cu.font = self.font(font); cu.size = size * MM; cu.space_character = 1.0 + track
        cu.space_line = leading; cu.align_x = align
        if width:
            cu.text_boxes[0].width = width * MM
        cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = 3
        ob = bpy.data.objects.new("t", cu)
        if mat:
            ob.data.materials.append(mat)
        dd = d + extrude
        ob.location = self.at(px, py, dd)
        ob.scale = (self.k(dd),) * 3
        ob.rotation_euler = (math.radians(90), 0, 0)
        self.sc.collection.objects.link(ob)
        if width and align in ("RIGHT", "CENTER"):
            pass
        return ob

    def rule(self, px, py, w, h, mat, d=0.0012, depth=0.001):
        ob = self.box(px, py, w, h, depth, mat, d)
        return ob

    def box(self, px, py, w, h, depth, mat, d=0.0):
        """Axis-aligned slab whose FRONT face shows as the page rect (px, py, w, h), standing `d` off the wall."""
        bpy.ops.mesh.primitive_cube_add(size=1)
        ob = bpy.context.active_object
        kk = self.k(d)
        c = self.at(px + w / 2, py + h / 2, d + depth / 2)
        ob.location = c
        ob.scale = (w * MM * kk, depth, h * MM * kk)
        if mat:
            ob.data.materials.append(mat)
        return ob

    def image(self, path, px, py, w, h, d=0.004, thickness=0.004, mat=None, rough=0.4):
        """A print mounted off the wall: front face = page rect, image mapped onto it."""
        ob = self.box(px, py, w, h, thickness, None, d)
        m = mat or mat_image(f"img_{Path(path).stem}", path, rough=rough)
        ob.data.materials.append(m)
        # UV: map the front face (-Y) 0..1
        me = ob.data
        uv = me.uv_layers[0] if len(me.uv_layers) else me.uv_layers.new()
        for poly in me.polygons:
            for li in poly.loop_indices:
                v = me.vertices[me.loops[li].vertex_index].co
                uv.data[li].uv = (v.x + 0.5, v.z + 0.5)
        return ob

    # ---------------------------------------------------------------- files
    out_dir = None

    def out(self, name):
        """A file written earlier into the render folder (a re-staged photo, a drawing)."""
        return Path(self.out_dir) / name

    asset = out

    # ---------------------------------------------------------------- objects
    def link(self, ob):
        self.sc.collection.objects.link(ob); return ob

    def render(self, out):
        self.sc.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        return out

    def shot(self, out, loc, target, lens=50.0, res=(1000, 750), samples=None):
        """Extra exposure from another camera (used by post.py as a double exposure)."""
        cd = bpy.data.cameras.new("shot"); cd.lens = lens
        ob = bpy.data.objects.new("shot", cd); ob.location = loc; self.link(ob); self._aim(ob, target)
        main, r0, s0 = self.sc.camera, (self.sc.render.resolution_x, self.sc.render.resolution_y), self.sc.cycles.samples
        self.sc.camera = ob; self.sc.render.resolution_x, self.sc.render.resolution_y = res
        if samples:
            self.sc.cycles.samples = samples
        self.render(out)
        self.sc.camera = main; self.sc.render.resolution_x, self.sc.render.resolution_y = r0; self.sc.cycles.samples = s0
        return out


# ---------------------------------------------------------------- props

def rounded_rect(cx, cy, w, h, r, n=8):
    pts = []
    for (x, y, a0) in ((cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)):
        for i in range(n + 1):
            t = math.radians(a0 + 90 * i / n)
            pts.append((x + r * math.cos(t), y + r * math.sin(t)))
    return pts


def _curve_shape(name, loops, extrude, bevel):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "2D"; cu.fill_mode = "BOTH"
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = 4
    for loop in loops:
        sp = cu.splines.new("POLY"); sp.points.add(len(loop) - 1); sp.use_cyclic_u = True
        for i, (x, y) in enumerate(loop):
            sp.points[i].co = (x, y, 0, 1)
    return cu


def glasses(mat, lens_mat=None, scale=1.0, temples=1.05, fold=0.0, sunglasses=False):
    """Horn-rimmed frame, 1.24 units wide, front in the XZ plane facing -Y, temples running to +Y."""
    rimW, rimH, r, t, cx = 0.54, 0.40, 0.15, 0.066, 0.315
    outer = rounded_rect(0, 0, 1.24, 0.47, 0.17, 10)
    holes = [rounded_rect(s * cx, -0.02, rimW - 2 * t, rimH - 2 * t, r - t * 0.6, 10) for s in (-1, 1)]
    cu = _curve_shape("frame", [outer] + holes, 0.025, 0.012)
    front = bpy.data.objects.new("frame", cu); front.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(front)
    front.rotation_euler = (math.radians(90), 0, 0)
    parts = [front]
    if lens_mat:
        lcu = _curve_shape("lens", holes, 0.004, 0.0)
        lens = bpy.data.objects.new("lens", lcu); lens.data.materials.append(lens_mat)
        bpy.context.scene.collection.objects.link(lens); lens.rotation_euler = (math.radians(90), 0, 0); lens.location.y = -0.002
        parts.append(lens)
    for s in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1)
        tmp = bpy.context.active_object
        tmp.scale = (0.045, temples, 0.062); tmp.location = (s * 0.6, temples / 2, 0.09)
        tmp.rotation_euler = (0, 0, s * -fold)
        bev = tmp.modifiers.new("b", "BEVEL"); bev.width = 0.014; bev.segments = 3
        tmp.data.materials.append(mat)
        parts.append(tmp)
    root = bpy.data.objects.new("glasses", None); bpy.context.scene.collection.objects.link(root)
    for p in parts:
        p.parent = root
    root.scale = (scale,) * 3
    return root


def load_head(material, height=1.0):
    """Lee Perry-Smith head scan (Infinite-Realities, CC BY 3.0), normalised: bust `height` tall, base at z=0, face toward -Y."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ASSETS / "LeePerrySmith.glb"))
    new = [o for o in bpy.data.objects if o not in before]
    mesh = [o for o in new if o.type == "MESH"][0]
    for o in new:
        if o is not mesh:
            mesh.parent = None
    bpy.context.view_layer.update()
    mw = mesh.matrix_world
    pts = [mw @ v.co for v in mesh.data.vertices]
    zmin = min(p.z for p in pts); zmax = max(p.z for p in pts)
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2; cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    s = height / (zmax - zmin)
    mesh.data.transform(mw)
    mesh.matrix_world.identity()
    for v in mesh.data.vertices:
        v.co = Vector(((v.co.x - cx) * s, (v.co.y - cy) * s, (v.co.z - zmin) * s))
    mesh.data.materials.clear(); mesh.data.materials.append(material)
    for p in mesh.data.polygons:
        p.use_smooth = True
    for o in new:
        if o is not mesh:
            bpy.data.objects.remove(o, do_unlink=True)
    return mesh


def mat_fabric(name, color):
    m, p, nt = _bsdf(name)
    p.inputs["Base Color"].default_value = hexrgb(color); p.inputs["Roughness"].default_value = 0.88
    p.inputs["Sheen Weight"].default_value = 0.6; p.inputs["Sheen Roughness"].default_value = 0.5
    w = nt.nodes.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value = 260; w.inputs["Distortion"].default_value = 1.5
    w2 = nt.nodes.new("ShaderNodeTexWave"); w2.inputs["Scale"].default_value = 260; w2.bands_direction = "Y"
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.25; b.inputs["Distance"].default_value = 0.0006
    nt.links.new(w.outputs["Fac"], add.inputs[0]); nt.links.new(w2.outputs["Fac"], add.inputs[1])
    nt.links.new(add.outputs[0], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def cloth(pg, px, py, w, h, d=0.03, color="#444444", seed=0, nx=64, ny=90):
    """A cloth hung from its top edge in front of the wall: vertical folds that open toward the hem."""
    bm = bmesh.new(); grid = []
    for j in range(ny + 1):
        v = j / ny; row = []
        for i in range(nx + 1):
            u = i / nx
            f = (0.014 * math.sin(u * math.tau * 2.6 + seed) + 0.006 * math.sin(u * math.tau * 6.3 + seed * 2.1)) * (0.25 + 0.75 * v)
            sway = 0.004 * math.sin(v * 3.1 + seed) * v
            pxx = px + u * w + (u - 0.5) * 4 * v + sway * 100
            row.append(bm.verts.new(pg.at(pxx, py + v * h, d + 0.02 + f)))
        grid.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    me = bpy.data.meshes.new("cloth"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("cloth", me); pg.link(ob)
    sol = ob.modifiers.new("s", "SOLIDIFY"); sol.thickness = 0.003
    ob.data.materials.append(mat_fabric(f"fabric{seed}", color))
    uv = me.uv_layers.new()
    return ob


def mat_mesh(name, color="#0d0d0d", scale=60.0, open_=0.35, solid=False):
    """Black woven wire mesh (the Haus Dosan pods): dark metal threads with open cells you can see through."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = hexrgb(color); p.inputs["Metallic"].default_value = 0.7; p.inputs["Roughness"].default_value = 0.38
    tc = nt.nodes.new("ShaderNodeTexCoord")
    w1 = nt.nodes.new("ShaderNodeTexWave"); w1.inputs["Scale"].default_value = scale; w1.wave_profile = "TRI"
    w2 = nt.nodes.new("ShaderNodeTexWave"); w2.inputs["Scale"].default_value = scale; w2.wave_profile = "TRI"; w2.bands_direction = "Y"
    for w in (w1, w2):
        nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    nt.links.new(w1.outputs["Fac"], mx.inputs[0]); nt.links.new(w2.outputs["Fac"], mx.inputs[1])
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 1 - open_
    nt.links.new(mx.outputs[0], gt.inputs[0])
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.6; b.inputs["Distance"].default_value = 0.003
    nt.links.new(mx.outputs[0], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(gt.outputs[0], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(p.outputs[0], mix.inputs[2])
    nt.links.new((p if solid else mix).outputs[0], out.inputs["Surface"])
    return m


def group_scale(objs, pivot, k):
    """Scale a set of freshly made objects about a pivot (model-scale objects on a shelf)."""
    e = bpy.data.objects.new("grp", None); e.location = pivot; bpy.context.scene.collection.objects.link(e)
    bpy.context.view_layer.update()
    for o in objs:
        if o.parent is None:
            mw = o.matrix_world.copy(); o.parent = e; o.matrix_world = mw
    e.scale = (k, k, k)
    return e


def mat_bone(name, color="#e6e0d2", scale=30.0):
    """Porous bone-white surface (the coral cluster): voronoi pits in the bump."""
    m, p, nt = _bsdf(name)
    p.inputs["Base Color"].default_value = hexrgb(color); p.inputs["Roughness"].default_value = 0.8
    p.inputs["Subsurface Weight"].default_value = 0.1
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = scale; v.feature = "SMOOTH_F1"
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 1.0; b.inputs["Distance"].default_value = 0.01
    nt.links.new(v.outputs["Distance"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def tube(a, b, r, mat, verts=24):
    """A cylinder from point a to point b."""
    a, b = Vector(a), Vector(b); d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length)
    ob = bpy.context.active_object; ob.location = (a + b) / 2
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return ob


def ball(loc, r, mat, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r)
    ob = bpy.context.active_object; ob.location = loc; ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def cage(cx, cy, w, d, h, r, mat, bays=3, z0=0.0):
    """Chrome scaffold: a box frame of tubes with intermediate bays (the Haus Dosan truss)."""
    xs = [cx - w / 2 + w * i / bays for i in range(bays + 1)]
    ys = (cy - d / 2, cy + d / 2)
    for x in xs:
        for y in ys:
            tube((x, y, z0), (x, y, z0 + h), r, mat)
        tube((x, ys[0], z0 + h), (x, ys[1], z0 + h), r, mat)
    for y in ys:
        tube((xs[0], y, z0 + h), (xs[-1], y, z0 + h), r, mat)
        tube((xs[0], y, z0 + h * 0.08), (xs[-1], y, z0 + h * 0.08), r * 0.8, mat)


def pod(base, height, width, mat, twist=0.0, tilt=(0.0, 0.0), yaw=0.0):
    """A tall faceted leaf hanging point-down (the Haus Dosan pods): five facets, widest near the top."""
    bm = bmesh.new(); n = 5; rings = []
    for z, k in [(1.0, 0.62), (0.9, 0.9), (0.62, 1.0), (0.25, 0.45)]:
        ring = []
        for i in range(n):
            a = i / n * math.tau + twist * z
            ring.append(bm.verts.new((math.cos(a) * width * k, math.sin(a) * width * k * 0.55, z * height)))
        rings.append(ring)
    tip = bm.verts.new((0, 0, 0))
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            bm.faces.new((r0[i], r0[(i + 1) % n], r1[(i + 1) % n], r1[i]))
    for i in range(n):
        bm.faces.new((rings[-1][i], rings[-1][(i + 1) % n], tip))
    bm.faces.new(rings[0][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("pod"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("pod", me); bpy.context.scene.collection.objects.link(ob)
    ob.location = base; ob.rotation_euler = (tilt[0], tilt[1], yaw)
    ob.data.materials.append(mat)
    bev = ob.modifiers.new("b", "BEVEL"); bev.width = 0.004; bev.segments = 2
    return ob


def faceted(ob, ratio=0.02):
    """Planar low-poly facets (decimate), flat shaded: turns a scan into a faceted sculpture."""
    dm = ob.modifiers.new("dec", "DECIMATE"); dm.ratio = ratio
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


def rough_ball(loc, r, amp, mat, seed=0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=6, radius=r)
    ob = bpy.context.active_object; ob.location = loc
    tex = bpy.data.textures.new(f"rb{seed}", "CLOUDS"); tex.noise_scale = r * 0.5; tex.noise_depth = 4
    dm = ob.modifiers.new("d", "DISPLACE"); dm.texture = tex; dm.strength = amp; dm.mid_level = 0.5
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def shard(loc, size, mat, rot):
    """A thin triangular acrylic fragment (a broken lens)."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=size, depth=size * 0.08)
    ob = bpy.context.active_object; ob.location = loc; ob.rotation_euler = rot; ob.scale = (1.0, 0.7, 1.0)
    ob.data.materials.append(mat)
    return ob


def basin(cx, cy, z, rx, ry, mat, wobble=0.18, beads=36, bead_mat=None, seed=1.3, n=96):
    """Free-form cast basin (the Nudake tray): a liquid outline, a rolled rim, a shallow floor, a beaded edge."""
    pts = []
    for i in range(n):
        a = i / n * math.tau
        k = 1 + wobble * (0.6 * math.sin(2 * a + seed) + 0.4 * math.sin(3 * a + seed * 2.3))
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    cu = bpy.data.curves.new("rim", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = min(rx, ry) * 0.09; cu.bevel_resolution = 6
    sp = cu.splines.new("POLY"); sp.points.add(n - 1); sp.use_cyclic_u = True
    for i, (x, y) in enumerate(pts):
        sp.points[i].co = (x, y, z + min(rx, ry) * 0.12, 1)
    rim = bpy.data.objects.new("rim", cu); rim.data.materials.append(mat); bpy.context.scene.collection.objects.link(rim)
    fl = _curve_shape("floor", [[(x - cx, y - cy) for x, y in pts]], min(rx, ry) * 0.04, 0.0)
    floor = bpy.data.objects.new("floor", fl); floor.data.materials.append(mat); floor.location = (cx, cy, z); bpy.context.scene.collection.objects.link(floor)
    if beads:
        for i in range(beads):
            x, y = pts[int(i * n / beads)]
            dx, dy = x - cx, y - cy; L = math.hypot(dx, dy)
            ball((x + dx / L * min(rx, ry) * 0.12, y + dy / L * min(rx, ry) * 0.12, z + min(rx, ry) * 0.05), min(rx, ry) * 0.05, bead_mat or mat, 16)
    return rim, floor


def rough_block(name, size, amp, seed, mat, subdiv=5):
    bpy.ops.mesh.primitive_cube_add(size=1)
    ob = bpy.context.active_object; ob.name = name; ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    m = ob.modifiers.new("s", "SUBSURF"); m.levels = subdiv; m.render_levels = subdiv; m.subdivision_type = "SIMPLE"
    tex = bpy.data.textures.new(name + "n", "CLOUDS"); tex.noise_scale = 0.35; tex.noise_depth = 4
    dm = ob.modifiers.new("d", "DISPLACE"); dm.texture = tex; dm.strength = amp; dm.mid_level = 0.5
    tex2 = bpy.data.textures.new(name + "n2", "CLOUDS"); tex2.noise_scale = 0.08; tex2.noise_depth = 2
    dm2 = ob.modifiers.new("d2", "DISPLACE"); dm2.texture = tex2; dm2.strength = amp * 0.25
    ob.data.materials.append(mat)
    return ob
