// gentle_monster photoreal scene: builds a physically based three.js scene from a job spec
// (layout items carry `shape` and `material`). One builder serves the stills (eye / cutaway)
// and the walkthrough video, so the blueprint and the mp4 always show the same room.
//
// Coordinates: layout (x, y) -> world (x, z), y up, metres. The door is on y = 0.
// Everything is deterministic (seeded noise) -- render.py draws frame t in parallel workers
// and the parts must join without a seam.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { Reflector } from 'three/addons/objects/Reflector.js';

export function build(job, opt = {}) {
  const W = opt.w || 1280, H = opt.h || 720;
  const L = job.layout, R = job.room, Wd = L.W, Dp = L.D, Ht = L.H;
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

  // ---------------- procedural textures ----------------
  function canvasTex(size, draw, repeat = [1, 1]) {
    const c = document.createElement('canvas'); c.width = c.height = size; draw(c.getContext('2d'), size);
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
  }
  const grain = (g, s, base, amt, n, sz = 2) => { g.fillStyle = base; g.fillRect(0, 0, s, s); for (let i = 0; i < n; i++) { const v = (rnd() - .5) * amt; g.fillStyle = v > 0 ? `rgba(255,255,255,${v})` : `rgba(0,0,0,${-v})`; const q = sz * (.4 + rnd()); g.fillRect(rnd() * s, rnd() * s, q, q); } };
  const blotch = (g, s, col, n, r0, r1) => { for (let i = 0; i < n; i++) { const x = rnd() * s, y = rnd() * s, r = r0 + rnd() * (r1 - r0); const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, col); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r); } };
  const TX = {
    concrete: r => canvasTex(1024, (g, s) => { grain(g, s, '#8f918e', .16, 90000, 2); blotch(g, s, 'rgba(60,60,58,.12)', 40, 40, 200); blotch(g, s, 'rgba(255,255,255,.07)', 30, 40, 160); for (let i = 0; i < 60; i++) { g.fillStyle = 'rgba(40,40,40,.35)'; g.beginPath(); g.arc(rnd() * s, rnd() * s, 1 + rnd() * 3, 0, 7); g.fill(); } g.strokeStyle = 'rgba(0,0,0,.18)'; g.lineWidth = 2; g.strokeRect(0, 0, s, s); }, r),
    polished: r => canvasTex(1024, (g, s) => { grain(g, s, '#6d6f6d', .1, 60000, 2); blotch(g, s, 'rgba(30,30,30,.18)', 50, 60, 260); }, r),
    granite: r => canvasTex(1024, (g, s) => { grain(g, s, '#5c5b58', .55, 260000, 2.2); for (let i = 0; i < 4000; i++) { g.fillStyle = rnd() > .5 ? 'rgba(18,18,18,.75)' : 'rgba(215,212,205,.55)'; g.fillRect(rnd() * s, rnd() * s, 2 + rnd() * 5, 2 + rnd() * 5); } }, r),
    brushed: (r, base) => canvasTex(1024, (g, s) => { g.fillStyle = base; g.fillRect(0, 0, s, s); for (let y = 0; y < s; y++) { const v = (rnd() - .5) * .14; g.fillStyle = v > 0 ? `rgba(255,255,255,${v})` : `rgba(0,0,0,${-v})`; g.fillRect(0, y, s, 1); } }, r),
    plaster: (r, base) => canvasTex(1024, (g, s) => { grain(g, s, base, .05, 70000, 3); blotch(g, s, 'rgba(120,110,95,.05)', 40, 60, 240); }, r),
    strata: r => canvasTex(1024, (g, s) => { let y = 0; const cols = ['#9a4a32', '#b86a4a', '#7b5a40', '#c89a72', '#8a3f2b', '#6d5237', '#a8795a']; while (y < s) { const t = 8 + rnd() * 46; g.fillStyle = cols[(rnd() * cols.length) | 0]; g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= s; x += 32) g.lineTo(x, y + (rnd() - .5) * 9); g.lineTo(s, y + t); g.lineTo(0, y + t); g.fill(); y += t; } for (let i = 0; i < 90000; i++) { g.fillStyle = `rgba(0,0,0,${rnd() * .1})`; g.fillRect(rnd() * s, rnd() * s, 1.5, 1.5); } }, r),
    graphite: r => canvasTex(1024, (g, s) => { grain(g, s, '#2a2826', .38, 300000, 1.8); blotch(g, s, 'rgba(120,20,15,.55)', 26, 8, 38); }, r),
    wood: r => canvasTex(1024, (g, s) => { g.fillStyle = '#6b4a32'; g.fillRect(0, 0, s, s); for (let x = 0; x < s; x += 2) { g.fillStyle = `rgba(${40 + rnd() * 40 | 0},${25 + rnd() * 20 | 0},10,${.15 + rnd() * .2})`; g.fillRect(x, 0, 1 + rnd() * 2, s); } }, r),
    pale_concrete: r => canvasTex(1024, (g, s) => { grain(g, s, '#d3d1cb', .09, 90000, 2); blotch(g, s, 'rgba(110,108,100,.06)', 40, 60, 240); for (let y = 0; y < s; y += s / 4) { g.fillStyle = 'rgba(90,88,82,.10)'; g.fillRect(0, y, s, 2); } for (let i = 0; i < 40; i++) { g.fillStyle = 'rgba(80,80,78,.22)'; g.beginPath(); g.arc(rnd() * s, rnd() * s, 1 + rnd() * 2.5, 0, 7); g.fill(); } }, r),
    textile: r => canvasTex(512, (g, s) => { g.fillStyle = '#fff7e6'; g.fillRect(0, 0, s, s); for (let x = 0; x < s; x += 3) { g.fillStyle = `rgba(190,170,130,${.08 + rnd() * .06})`; g.fillRect(x, 0, 1, s); } for (let y = 0; y < s; y += 3) { g.fillStyle = `rgba(190,170,130,${.06 + rnd() * .05})`; g.fillRect(0, y, s, 1); } }, r),
  };
  const std = o => new THREE.MeshStandardMaterial(o), phys = o => new THREE.MeshPhysicalMaterial(o);
  // span: metres the texture should repeat over, so a 20 m wall and a 1 m plinth show the same grain size
  function MAT(name, span = 4) {
    const r = [Math.max(1, span / 4), Math.max(1, span / 6)];
    switch (name) {
      case 'concrete': return std({ map: TX.concrete(r), roughness: .92 });
      case 'polished_concrete': return phys({ map: TX.polished(r), roughness: .25, clearcoat: .6, clearcoatRoughness: .2 });
      case 'granite': return std({ map: TX.granite([1, 1]), roughness: .88 });
      case 'steel': return phys({ map: TX.brushed([1, 4], '#9aa3a8'), metalness: 1, roughness: .26 });
      case 'mirror_aluminium': return phys({ map: TX.brushed([1, 1], '#d9dde1'), metalness: 1, roughness: .07 });
      case 'aluminium': return phys({ map: TX.brushed([1, 1], '#c9cdd1'), metalness: 1, roughness: .2 });
      case 'brass': return phys({ color: '#b58d4f', metalness: 1, roughness: .28, map: TX.brushed([1, 1], '#c09a5c') });
      case 'red_wax': return phys({ color: '#5a0f0f', roughness: .7, clearcoat: .1, sheen: .3 });
      case 'graphite_wax': return std({ map: TX.graphite([1, 2]), roughness: .75, metalness: .25 });
      case 'mineral_white': return std({ color: '#f1efea', roughness: .95 });
      case 'strata_clay': return std({ map: TX.strata([Math.max(1, span / 6), 1]), roughness: .95 });
      case 'lime_plaster': return std({ map: TX.plaster(r, '#e6dfd2'), roughness: .95 });
      case 'wood': return std({ map: TX.wood(r), roughness: .6 });
      case 'amber_glass': return phys({ color: '#6b3510', transmission: .75, roughness: .06, thickness: .08, ior: 1.5, attenuationColor: new THREE.Color('#7a3a0a'), attenuationDistance: .15 });
      case 'glass': return phys({ transmission: 1, roughness: .02, ior: 1.52, thickness: .03, iridescence: .6 });
      case 'skin': return phys({ color: '#cfa591', roughness: .4, sheen: .6, sheenColor: new THREE.Color('#ffd9c8'), clearcoat: .15, clearcoatRoughness: .5 });
      case 'textile_light': { const t = TX.textile([6, 4]); return std({ map: t, emissive: '#fff3dc', emissiveIntensity: 1.3, emissiveMap: t, roughness: 1, side: THREE.DoubleSide }); }
      case 'black_stone': return phys({ color: '#141414', roughness: .35, clearcoat: .3 });
      case 'white_gloss': return phys({ color: '#f1f0ec', roughness: .35, clearcoat: .6, clearcoatRoughness: .2, flatShading: true });
      case 'pale_concrete': return std({ map: TX.pale_concrete(r), roughness: .9 });
      case 'ceramic_white': return phys({ color: '#eeede9', roughness: .5, clearcoat: .25, clearcoatRoughness: .45 });
      case 'dark_titanium': return phys({ map: TX.brushed([1, 3], '#5a5d60'), metalness: .6, roughness: .38, clearcoat: .35, clearcoatRoughness: .25 });
      case 'black_chrome': return phys({ color: '#1b1c1e', metalness: 1, roughness: .07, clearcoat: .5 });
      case 'titanium': return phys({ map: TX.brushed([1, 3], '#9a9c9d'), metalness: 1, roughness: .3 });
      case 'oxidized_silver': return phys({ map: TX.plaster([1, 1], '#aaa59a'), metalness: 1, roughness: .2 });
      case 'candle_wax': return phys({ color: '#efe6cf', roughness: .55, sheen: .5, sheenColor: new THREE.Color('#fff4dd'), transmission: .08, thickness: .5 });
      default: return std({ color: '#888', roughness: .8 });
    }
  }

  // ---------------- renderer ----------------
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(opt.ss || 1); renderer.setSize(W, H);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = R.exposure || 1;
  renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
  const HD = {}, HIDE = [], push = (k, o) => ((HD[k] || (HD[k] = [])).push(o), o);
  const add = (m, cast = true, recv = true) => { m.castShadow = cast; m.receiveShadow = recv; scene.add(m); return m; };
  function box(x0, z0, x1, z1, y0, y1, mat) { const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), mat); m.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); return add(m); }
  const ctr = it => [(it.x0 + it.x1) / 2, (it.y0 + it.y1) / 2];
  const heroes = [];

  // ---------------- shell ----------------
  const light = R.light, dark = light === 'dark_gallery';
  scene.background = new THREE.Color({ dark_gallery: '#0b0b0b', white_gallery: '#f2f1ed', daylight: '#101010', warm_spot: '#1b120c', cold_spot: '#e6e8ea' }[light]);
  scene.environmentIntensity = { dark_gallery: .55, white_gallery: .9, daylight: .8, warm_spot: .6, cold_spot: .7 }[light];
  { const f = new THREE.Mesh(new THREE.PlaneGeometry(Wd, Dp), MAT(R.floor, Math.max(Wd, Dp))); f.rotation.x = -Math.PI / 2; f.position.set(Wd / 2, 0, Dp / 2); add(f, false, true);
    if (R.wet) {   // wet floor: a true mirror just under a partly transparent floor finish
      f.material.transparent = true; f.material.opacity = 1 - R.wet; f.material.roughness = .35; f.material.depthWrite = true;
      const fm = new Reflector(new THREE.PlaneGeometry(Wd, Dp), { textureWidth: 2048, textureHeight: 2048, color: 0x9a9da1, clipBias: .002 }); fm.rotation.x = -Math.PI / 2; fm.position.set(Wd / 2, -.003, Dp / 2); scene.add(fm); }
    const wall = MAT(R.wall, Math.max(Wd, Dp)), t = .2, door = L.items.find(i => i.shape === 'door' || i.type === 'door');
    box(-t, 0, 0, Dp, 0, Ht, wall); box(Wd, 0, Wd + t, Dp, 0, Ht, wall); box(-t, Dp, Wd + t, Dp + t, 0, Ht, wall);
    HIDE.push(box(-t, -t, door.x0, 0, 0, Ht, wall), box(door.x1, -t, Wd + t, 0, 0, Ht, wall), box(door.x0, -t, door.x1, 0, Math.min(2.8, Ht - .2), Ht, wall));
    if (!R.dome) { const c = new THREE.Mesh(new THREE.PlaneGeometry(Wd, Dp), MAT(R.ceiling, Math.max(Wd, Dp))); c.rotation.x = Math.PI / 2; c.position.set(Wd / 2, Ht, Dp / 2); HIDE.push(add(c, false, true)); }
    else { const r = Math.min(Wd, Dp) * .46, dm = new THREE.Mesh(new THREE.SphereGeometry(r, 64, 32, 0, Math.PI * 2, 0, Math.PI / 2), MAT(R.ceiling, 8)); dm.material.side = THREE.BackSide; dm.scale.y = .38; dm.position.set(Wd / 2, Ht - .1, Dp / 2); HIDE.push(add(dm, false, true)); }
    if (R.beams) { const m = std({ color: '#151515', roughness: .6, metalness: .3 }); for (let x = 2; x < Wd; x += 4) HIDE.push(box(x - .15, 0, x + .15, Dp, Ht - .5, Ht - .1, m)); }
    if (R.fog) scene.fog = new THREE.FogExp2(dark ? '#0d0d0e' : (light === 'cold_spot' ? '#e3e7ec' : '#f2f1ed'), R.fog);
    const cm = std({ color: '#151515', roughness: .6, metalness: .3 }); for (const [x, y] of L.columns || []) box(x - .2, y - .2, x + .2, y + .2, 0, Ht, cm); }

  // ---------------- shapes ----------------
  const S = {
    box(it) { box(it.x0, it.y0, it.x1, it.y1, 0, it.h, MAT(it.material, Math.max(it.x1 - it.x0, it.y1 - it.y0))); },
    rock(it) {
      const g = new THREE.BoxGeometry(1, 1, 1, 18, 18, 18), p = g.attributes.position, v = new THREE.Vector3();
      for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i); const n = Math.sin(v.x * 7.1 + v.y * 3.3) * .018 + Math.sin(v.z * 9.7 + v.x * 2.1) * .016 + Math.sin((v.x + v.y + v.z) * 17.3) * .008;
        const ch = (Math.abs(v.x) > .49 && Math.abs(v.y) > .49) || (Math.abs(v.z) > .49 && Math.abs(v.y) > .49) ? .06 : 0; v.multiplyScalar(1 + n - ch); p.setXYZ(i, v.x, v.y, v.z); }
      g.computeVertexNormals(); const m = new THREE.Mesh(g, MAT(it.material || 'granite')); m.scale.set(it.x1 - it.x0, it.h, it.y1 - it.y0); const [x, z] = ctr(it); m.position.set(x, it.h / 2, z); m.rotation.y = (rnd() - .5) * .3; add(m);
      if (it.cloth) { const gw = Math.min(1.1, (it.x1 - it.x0) * .7), gl = Math.min(1.6, (it.y1 - it.y0) * 1.1), cg = new THREE.PlaneGeometry(gw, gl, 40, 60), cp = cg.attributes.position;
        for (let i = 0; i < cp.count; i++) { const u = cp.getX(i) / gw * 1.1, w = cp.getY(i); cp.setZ(i, Math.sin(u * 11 + w * 3) * .018 + Math.cos(w * 1.8) * .05 - Math.max(0, Math.abs(u) - .38) * 1.6); }
        cg.computeVertexNormals(); const cm = new THREE.Mesh(cg, phys({ color: it.cloth, roughness: .85, sheen: .8, sheenRoughness: .7, sheenColor: new THREE.Color(it.cloth).offsetHSL(0, 0, .15), side: THREE.DoubleSide }));
        cm.rotation.x = -Math.PI / 2; cm.rotation.z = rnd() * .4; cm.position.set(x, it.h + .02, z); add(cm); }
    },
    bust(it) {
      const [hx, hz] = ctr(it); heroes.push(new THREE.Vector3(hx, Math.min(it.h * .75, Ht - .5), hz));
      box(it.x0 + .2, it.y0 + .2, it.x1 - .2, it.y1 - .2, 0, .9, MAT('black_stone'));
      const skin = MAT(it.material || 'skin'), sc = Math.max(.5, (it.h - .9) / 2.56);
      const prof = new THREE.SplineCurve([[0, 0], [.95, 0], [1.05, .12], [1.02, .3], [.62, .48], [.42, .62], [.4, .9], [.46, 1.05], [.62, 1.2], [.74, 1.45], [.78, 1.75], [.74, 2.05], [.6, 2.3], [.38, 2.48], [0, 2.56]].map(([x, y]) => new THREE.Vector2(x, y))).getPoints(90);
      const lg = new THREE.LatheGeometry(prof, 220), p = lg.attributes.position, v = new THREE.Vector3(), G = (x, y, cx, cy, sx, sy) => Math.exp(-(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2));
      for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i); if (v.y < 1.0 || v.z > -0.05) continue; const f = Math.min(1, -v.z / .5), x = v.x, y = v.y;
        const d = .085 * G(x, y, 0, 1.62, .07, .2) + .05 * G(x, y, 0, 1.84, .28, .06) - .06 * G(x, y, -.26, 1.75, .13, .07) - .06 * G(x, y, .26, 1.75, .13, .07) + .03 * G(x, y, 0, 1.38, .13, .035) + .045 * G(x, y, 0, 1.2, .16, .08) + .02 * G(x, y, -.36, 1.5, .12, .14) + .02 * G(x, y, .36, 1.5, .12, .14);
        v.z -= 2.2 * d * f; p.setXYZ(i, v.x, v.y, v.z); }
      lg.computeVertexNormals(); const b = new THREE.Mesh(lg, skin); b.scale.set(sc, sc, sc * .86); b.position.set(hx, .9, hz); add(b);
      for (const s of [-1, 1]) { const lid = new THREE.Mesh(new THREE.TorusGeometry(.1 * sc, .008 * sc, 8, 32, Math.PI * .8), std({ color: '#6b4a40', roughness: .6 })); lid.position.set(hx + s * .26 * sc, .9 + 1.74 * sc, hz - .66 * sc); lid.rotation.set(-.2, 0, Math.PI * 1.1); push('lid', add(lid, false, false));
        const tr = new THREE.Mesh(new THREE.CapsuleGeometry(.018 * sc, .42 * sc, 8, 16), phys({ color: '#ffffff', transmission: 1, roughness: 0, ior: 1.33, thickness: .03, clearcoat: 1 })); tr.position.set(hx + s * .27 * sc, .9 + 1.48 * sc, hz - .67 * sc); tr.rotation.x = -.22; push('tear', add(tr, false, false)); }
    },
    creature(it) {
      const [cx, cz] = ctr(it), sc = Math.max(.4, (it.x1 - it.x0) / 3.2); heroes.push(new THREE.Vector3(cx, 2.2 * sc, cz));
      const shell = MAT(it.material || 'white_gloss'), joint = phys({ color: '#d8d6d0', metalness: .9, roughness: .25 });
      const grp = new THREE.Group(); grp.position.set(cx, 0, cz); grp.rotation.y = -.5; grp.scale.setScalar(sc); scene.add(grp); HD.creature = grp;
      const facet = (sx, sy, sz, p, rot = [0, 0, 0], det = 1) => { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1, det), shell); m.scale.set(sx, sy, sz); m.position.set(...p); m.rotation.set(...rot); m.castShadow = m.receiveShadow = true; grp.add(m); return m; };
      facet(1.25, .62, .55, [0, 2.05, 0], [0, 0, .22]); facet(.55, .5, .45, [.95, 2.45, 0], [0, 0, .5]); facet(.22, .62, .24, [1.35, 2.95, 0], [0, 0, -.55]); facet(.48, .2, .2, [1.72, 3.38, 0], [0, 0, -.35]); facet(.5, .45, .45, [-.95, 1.8, 0], [0, 0, .1]);
      const leg = (hip, a1, a2) => { const [x, y, z] = hip; facet(.12, .5, .14, [x + Math.sin(a1) * .45, y - Math.cos(a1) * .45, z], [0, 0, a1], 0); const kx = x + Math.sin(a1) * .9, ky = y - Math.cos(a1) * .9;
        const kn = new THREE.Mesh(new THREE.SphereGeometry(.09, 24, 16), joint); kn.position.set(kx, ky, z); kn.castShadow = true; grp.add(kn); facet(.08, .5, .09, [kx + Math.sin(a2) * .45, ky - Math.cos(a2) * .45, z], [0, 0, a2], 0); };
      leg([1.0, 2.1, .22], 1.15, .25); leg([1.0, 2.1, -.22], .85, -.2); leg([-1.0, 1.65, .22], -.35, .45); leg([-1.0, 1.65, -.22], -.1, .15);
      facet(.5, .07, .07, [-1.55, 2.0, 0], [0, 0, .9], 0);
      const ped = new THREE.Mesh(new THREE.CylinderGeometry(.05, .05, .75, 16), joint); ped.position.set(-.95, .6, 0); ped.castShadow = true; grp.add(ped);
    },
    cone_tree(it) {
      const [cx, cz] = ctr(it), r = Math.max(.4, (it.x1 - it.x0) * 1.25), h = it.h || 4, mat = MAT(it.material || 'steel');
      const tr = new THREE.Mesh(new THREE.CylinderGeometry(.05, .07, h, 16), mat); tr.position.set(cx, h / 2, cz); add(tr);
      for (let k = 0; k < 6; k++) { const c = new THREE.Mesh(new THREE.ConeGeometry(r * (1 - k * .13), h * .23, 7, 1, true), phys({ color: '#9fa8ad', metalness: 1, roughness: .15, side: THREE.DoubleSide })); c.position.set(cx, h * .25 + k * h * .125, cz); c.rotation.y = k * .6; add(c); }
    },
    joint_column(it) {
      const [cx, cz] = ctr(it), n = Math.max(2, Math.floor(it.h / .95)), r = Math.min(it.x1 - it.x0, it.y1 - it.y0) * .38, mat = MAT(it.material || 'steel');
      for (let k = 0; k < n; k++) { const y = .5 + k * .95, c = new THREE.Mesh(new THREE.CylinderGeometry(r - k * .03, r + .04 - k * .03, .7, 48), mat); c.position.set(cx, y, cz); push('joint', add(c));
        const j = new THREE.Mesh(new THREE.SphereGeometry(r * .88 - k * .025, 48, 24), phys({ color: '#2b2e30', metalness: 1, roughness: .18 })); j.position.set(cx, y + .45, cz); push('ball', add(j)); }
      if (dark) { const p = new THREE.PointLight('#ff2a18', 6, 5, 1.8); p.position.set(cx, .4, cz + .6); scene.add(p); push('led', p); }
    },
    cable_curtain(it) {
      const mat = MAT(it.material || 'steel'), z = (it.y0 + it.y1) / 2;
      for (let k = 0; k < 26; k++) { const y = 1.0 + k * (it.h - 1.2) / 26, pts = []; for (let s = 0; s <= 14; s++) { const u = s / 14; pts.push(new THREE.Vector3(it.x0 + u * (it.x1 - it.x0), y - Math.sin(u * Math.PI) * (.18 + k * .006), z + Math.sin(u * 5 + k) * .05)); }
        push('wire', add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 40, .012, 6), mat), true, false)); }
    },
    candle_cluster(it) {
      const [x, z] = ctr(it), cw = MAT(it.material || 'candle_wax'), wax = MAT('red_wax'), sx = (it.x1 - it.x0) * .55, sz = (it.y1 - it.y0) * .5;
      for (let k = 0; k < 7; k++) { const r = .18 + rnd() * .32, h = Math.min(it.h, .6 + rnd() * 1.3), c = new THREE.Mesh(new THREE.CylinderGeometry(r * .92, r, h, 40), cw); c.position.set(x + (rnd() - .5) * sx, h / 2, z + (rnd() - .5) * sz); add(c);
        const d = new THREE.Mesh(new THREE.CylinderGeometry(r * .7, r * .95, .05 + rnd() * .08, 32), wax); d.position.set(c.position.x, h, c.position.z); add(d);
        const f = new THREE.Mesh(new THREE.SphereGeometry(.018, 8, 6), std({ emissive: '#ffb35a', emissiveIntensity: 6, color: '#000' })); f.position.set(c.position.x, h + .06, c.position.z); push('flame', f); scene.add(f); }
      for (let k = 0; k < 3; k++) { const b = new THREE.Mesh(new THREE.CylinderGeometry(.035, .035, .16, 24), phys({ color: '#2a1a12', transmission: .6, roughness: .1, thickness: .05 })); b.position.set(x + (rnd() - .5) * sx * .7, .3 + rnd() * .6, z + (rnd() - .5) * sz * .7); push('prod', add(b)); }
      const p = new THREE.PointLight('#ffbe7a', 3, 3, 1.8); p.position.set(x, 1.6, z); scene.add(p);
    },
    basin(it) {
      const [bx, bz] = ctr(it), s = Math.min(it.x1 - it.x0, it.y1 - it.y0) / 2 / 1.05, brass = MAT(it.material || 'brass'); heroes.push(new THREE.Vector3(bx, .9, bz));
      const lathe = new THREE.LatheGeometry([[0, 0], [.55, 0], [.62, .6], [.95, .82], [1.05, .9], [1.0, .92], [.9, .86], [0, .8]].map(([x, y]) => new THREE.Vector2(x * s, y)), 96);
      const bm = new THREE.Mesh(lathe, brass); bm.position.set(bx, 0, bz); add(bm);
      const water = new THREE.Mesh(new THREE.CircleGeometry(.9 * s, 64), phys({ color: '#4f605d', transmission: .55, roughness: .02, ior: 1.33, thickness: .2 })); water.rotation.x = -Math.PI / 2; water.position.set(bx, .86, bz); add(water, false, true);
      const tap = new THREE.Mesh(new THREE.TorusGeometry(.25, .035, 16, 48, Math.PI), brass); tap.position.set(bx, 1.45, bz); tap.rotation.y = Math.PI / 2; add(tap);
      const post = new THREE.Mesh(new THREE.CylinderGeometry(.035, .035, .6, 16), brass); post.position.set(bx, 1.15, bz - .25); add(post);
      const st = new THREE.Mesh(new THREE.CylinderGeometry(.012, .018, .55, 12), phys({ transmission: 1, roughness: 0, ior: 1.33, thickness: .02 })); st.position.set(bx, 1.17, bz + .25); add(st, false, false);
      HD.basin = [bx, bz];
    },
    shelf_wall(it) {
      const wm = MAT(it.material || 'strata_clay', Math.max(it.x1 - it.x0, it.y1 - it.y0)); box(it.x0, it.y0, it.x1, it.y1, 0, it.h, wm);
      const along = (it.x1 - it.x0) >= (it.y1 - it.y0), [cx, cz] = ctr(it), amber = MAT('amber_glass'), cap = std({ color: '#141414', roughness: .4 }), wood = MAT('wood', 2);
      const inward = along ? [0, (Dp / 2 > cz) ? 1 : -1] : [(Wd / 2 > cx) ? 1 : -1, 0];
      const face = along ? (inward[1] > 0 ? it.y1 : it.y0) : (inward[0] > 0 ? it.x1 : it.x0);
      const a0 = along ? it.x0 + .4 : it.y0 + .4, a1 = along ? it.x1 - .4 : it.y1 - .4, n = Math.floor((a1 - a0) / .16);
      for (let r = 0; r < Math.min(4, Math.floor((it.h - .6) / .5)); r++) { const y = .7 + r * .5;
        if (along) box(a0, Math.min(face, face + inward[1] * .3), a1, Math.max(face, face + inward[1] * .3), y - .03, y, wood);
        else box(Math.min(face, face + inward[0] * .3), a0, Math.max(face, face + inward[0] * .3), a1, y - .03, y, wood);
        for (let i = 0; i < n; i++) { if (rnd() < .18) continue; const u = a0 + (i + .5) * (a1 - a0) / n, px = along ? u : face + inward[0] * .12, pz = along ? face + inward[1] * .12 : u;
          const b = new THREE.Mesh(new THREE.CylinderGeometry(.045, .045, .2, 24), amber); b.position.set(px, y + .1, pz); add(b); const c = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, .05, 16), cap); c.position.set(px, y + .225, pz); add(c); } }
    },
    display(it) {
      const [cx, cz] = ctr(it); box(it.x0, it.y0, it.x1, it.y1, 0, .95, MAT(it.material || 'black_stone'));
      box(it.x0 + .05, it.y0 + .05, it.x1 - .05, it.y1 - .05, .95, .97, phys({ transmission: 1, roughness: .05, thickness: .02 }));
      const fr = std({ color: '#0b0b0b', roughness: .25 }), w = (it.x1 - it.x0) * .25;
      for (const dx of [-w, w]) for (const s of [-1, 1]) { const t = new THREE.Mesh(new THREE.TorusGeometry(.07, .012, 12, 48), fr); t.position.set(cx + dx + s * .085, 1.02, cz); t.rotation.x = -Math.PI / 2.4; push('eyewear', add(t)); }
      const sp = new THREE.SpotLight('#fff1dc', dark ? 45 : 20, 0, .35, .5, 1.6); sp.position.set(cx, Ht - .3, cz); sp.target.position.set(cx, 1, cz); scene.add(sp, sp.target);
    },
    shards(it) {
      const g = MAT('glass'), [cx, cz] = ctr(it); HD.shardCenter = [cx, cz];
      for (let n = 0; n < 90; n++) { const a = rnd() * Math.PI * 2, rx = (it.x1 - it.x0) / 2, rz = (it.y1 - it.y0) / 2, r = .55 + rnd() * .45;
        const m = new THREE.Mesh(new THREE.CircleGeometry(.08 + rnd() * .22, 3 + (rnd() * 4 | 0)), g); m.position.set(cx + Math.cos(a) * rx * r, 1 + rnd() * (it.h - 1.2), cz + Math.sin(a) * rz * r); m.rotation.set(rnd() * 6, rnd() * 6, rnd() * 6); push('shard', add(m, false, false)); }
    },
    mirror_wall(it) { push('aluwall', box(it.x0, it.y0, it.x1, it.y1, 0, it.h, MAT(it.material || 'mirror_aluminium'))); push('mirrorItem', it); },
    light_ceiling(it) {
      const [cx, cz] = ctr(it), mat = MAT('textile_light'), pl = new THREE.Mesh(new THREE.PlaneGeometry(it.x1 - it.x0, it.y1 - it.y0), mat); pl.rotation.x = Math.PI / 2; pl.position.set(cx, Ht - .25, cz); scene.add(pl); HIDE.push(pl); HD.ceil = mat;
      const d = new THREE.DirectionalLight('#fff4e2', 1.6); d.position.set(cx, 12, cz - 1); d.target.position.set(cx, 0, cz); d.castShadow = true; Object.assign(d.shadow.camera, { left: -12, right: 12, top: 12, bottom: -12 }); d.shadow.mapSize.set(4096, 4096); d.shadow.radius = 10; d.shadow.bias = -.0003; scene.add(d, d.target); HD.sun = d;
    },
    floor_patch(it) {
      const mat = MAT(it.material || 'graphite_wax', 4), g = new THREE.Mesh(new THREE.PlaneGeometry(it.x1 - it.x0, it.y1 - it.y0), mat); g.rotation.x = -Math.PI / 2; g.position.set(...(([x, z]) => [x, .004, z])(ctr(it))); add(g, false, true);
      if ((it.material || 'graphite_wax') === 'graphite_wax') { const wax = MAT('red_wax'); for (let n = 0; n < 60; n++) { const b = new THREE.Mesh(new THREE.SphereGeometry(.03 + rnd() * .09, 18, 12), wax); b.scale.set(1 + rnd() * .8, .12, .6 + rnd() * .6); b.position.set(it.x0 + rnd() * (it.x1 - it.x0), .01, it.y0 + rnd() * (it.y1 - it.y0)); add(b); } }
    },
    // ---- FRAME & INTERIOR: the maker, the made, the memory ----
    reflect_basin(it) {   // shallow black-edged basin of still water under the frame; the water is a true (slightly imperfect) mirror
      const [cx, cz] = ctr(it), w = it.x1 - it.x0, d = it.y1 - it.y0, rim = .05, hh = it.h || .12, edge = phys({ color: '#141414', roughness: .4, clearcoat: .4 });
      box(it.x0, it.y0, it.x1, it.y0 + rim, 0, hh, edge); box(it.x0, it.y1 - rim, it.x1, it.y1, 0, hh, edge);
      box(it.x0, it.y0 + rim, it.x0 + rim, it.y1 - rim, 0, hh, edge); box(it.x1 - rim, it.y0 + rim, it.x1, it.y1 - rim, 0, hh, edge);
      box(it.x0 + rim, it.y0 + rim, it.x1 - rim, it.y1 - rim, 0, .02, std({ color: '#0e0e0f', roughness: .9 }));
      const mir = new Reflector(new THREE.PlaneGeometry(w - 2 * rim, d - 2 * rim), { textureWidth: 2048, textureHeight: 1536, color: 0x8d9094, clipBias: .002 });
      mir.rotation.x = -Math.PI / 2; mir.position.set(cx, hh - .025, cz); scene.add(mir);
      const nt = canvasTex(512, (g, s) => { g.fillStyle = 'rgb(128,128,255)'; g.fillRect(0, 0, s, s); for (let i = 0; i < 26; i++) { const x = rnd() * s, y = rnd() * s, r = 30 + rnd() * 160;
        for (let k = 0; k < 5; k++) { g.strokeStyle = `rgba(${150 + k * 6},${120 - k * 4},255,${.10 - k * .015})`; g.lineWidth = 2; g.beginPath(); g.arc(x, y, r * (1 - k * .16), 0, 7); g.stroke(); } } }, [2, 2]);
      nt.colorSpace = THREE.NoColorSpace;
      const film = new THREE.Mesh(new THREE.PlaneGeometry(w - 2 * rim, d - 2 * rim), phys({ color: '#ffffff', transparent: true, opacity: .1, roughness: .04, normalMap: nt, normalScale: new THREE.Vector2(.35, .35), depthWrite: false }));
      film.rotation.x = -Math.PI / 2; film.position.set(cx, hh - .022, cz); scene.add(film); HD.water = [cx, hh - .025, cz];
    },
    memory_frame(it) {   // asymmetric open polyhedron: acrylic rods + glass tubes, polished silver nodes, one red node (the first one)
      if (it.form === 'eyewear') return S.eyewear_frame(it);
      const [cx, cz] = ctr(it), y0 = (it.base || .1), sc = it.scale || 1, P = {};
      const N = it.nodes || { A: [-.48, .32, -.18], B: [.42, .26, -.36], C: [.12, .34, .46], D: [-.22, 1.0, .08], E: [.52, .9, .12], F: [-.58, 1.32, -.42], G: [.16, 1.68, -.16], H: [.36, 1.3, .56] };
      for (const k in N) P[k] = new THREE.Vector3(cx + N[k][0] * sc, y0 + N[k][1] * sc, cz + N[k][2] * sc);
      const E = it.edges || ['AB', 'BC', 'CA', 'AD', 'BE', 'CD', 'DE', 'AF', 'DF', 'FG', 'DG', 'EG', 'EH', 'GH'];
      heroes.push(new THREE.Vector3(cx, y0 + .95 * sc, cz));
      const acrylic = phys({ color: '#f4fbff', transmission: 1, roughness: .03, ior: 1.49, thickness: .02, attenuationColor: new THREE.Color('#cfe9f2'), attenuationDistance: .35, specularIntensity: 1 });
      const tube = phys({ color: '#ffffff', transmission: 1, roughness: .01, ior: 1.52, thickness: .004, iridescence: .15, side: THREE.DoubleSide });
      const silver = it.node ? MAT(it.node) : phys({ color: '#d6d9dc', metalness: 1, roughness: .07 }), up = new THREE.Vector3(0, 1, 0);
      const rod = (a, b, r, m) => { const v = b.clone().sub(a), g = new THREE.Mesh(new THREE.CylinderGeometry(r, r, v.length(), 28, 1, m === tube), m); g.position.copy(a).add(b).multiplyScalar(.5); g.quaternion.setFromUnitVectors(up, v.normalize()); return add(g, true, false); };
      E.forEach((e, i) => { const a = P[e[0]], b = P[e[1]], d = b.clone().sub(a).normalize(), r0 = .045 * sc;
        rod(a.clone().addScaledVector(d, r0), b.clone().addScaledVector(d, -r0), i % 3 === 1 ? .016 : .011, i % 3 === 1 ? tube : acrylic); });
      for (const k of ['A', 'B', 'C']) rod(new THREE.Vector3(P[k].x, y0 - .08, P[k].z), P[k].clone().setY(P[k].y - .04 * sc), .009, acrylic);   // clear posts into the water: nothing floats
      const red = it.red || 'A';
      for (const k in P) { const isRed = k === red, m = isRed ? phys({ color: '#7a2a22', roughness: .25, emissive: '#b8382a', emissiveIntensity: .9, transmission: .2, thickness: .05 }) : silver;
        const s = new THREE.Mesh(new THREE.SphereGeometry(.045 * sc, 48, 32), m); s.position.copy(P[k]); add(s, true, false);
        if (isRed) { const pl = new THREE.PointLight('#ff6a52', .9, 1.4, 2); pl.position.copy(P[k]); scene.add(pl); } }
      HD.frameNodes = P; HD.frameScale = sc;
    },
    eyewear_frame(it) {   // a pair of glasses at architectural scale, half built: left rim done with its lens, right rim open, one arc in the arm
      const [cx, cz] = ctr(it), y0 = it.base || .1, sc = it.scale || 1, up = new THREE.Vector3(0, 1, 0);
      const acrylic = phys({ color: '#f4fbff', transmission: 1, roughness: .03, ior: 1.49, thickness: .05, attenuationColor: new THREE.Color('#cfe9f2'), attenuationDistance: .5, specularIntensity: 1 });
      const silver = it.node ? MAT(it.node) : phys({ color: '#d6d9dc', metalness: 1, roughness: .07 });
      const lensM = phys({ color: '#c9d0d4', transmission: .92, roughness: .04, ior: 1.5, thickness: .012, attenuationColor: new THREE.Color('#8f9aa0'), attenuationDistance: .25, side: THREE.DoubleSide });
      const zf = cz - .7 * sc, A = .5 * sc, Bh = .38 * sc, yc = y0 + 1.12 * sc, xo = .62 * sc, n = 4, R = .026 * sc, NR = .05 * sc;
      const rimPt = (side, t) => { const c = Math.cos(t), s_ = Math.sin(t); return new THREE.Vector3(cx + side * xo + A * Math.sign(c) * Math.abs(c) ** (2 / n), yc + Bh * Math.sign(s_) * Math.abs(s_) ** (2 / n), zf); };
      const tube = (pts, r = R, m = acrylic) => add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 64, r, 20), m), true, false);
      const node = (p, red) => { const m = red ? phys({ color: '#7a2a22', roughness: .25, emissive: '#b8382a', emissiveIntensity: .9 }) : silver; const s = new THREE.Mesh(new THREE.SphereGeometry(NR, 40, 28), m); s.position.copy(p); add(s, true, false);
        if (red) { const pl = new THREE.PointLight('#ff6a52', .9, 1.4, 2); pl.position.copy(p); scene.add(pl); } };
      const rod = (a, b, r) => { const v = b.clone().sub(a), g = new THREE.Mesh(new THREE.CylinderGeometry(r, r, v.length(), 20), acrylic); g.position.copy(a).add(b).multiplyScalar(.5); g.quaternion.setFromUnitVectors(up, v.normalize()); add(g, true, false); };
      const SEG = 6, T0 = -Math.PI / 6, arc = (side, k, lift = null) => { const pts = []; for (let i = 0; i <= 16; i++) { const p = rimPt(side, T0 + (k + i / 16) * 2 * Math.PI / SEG); if (lift) p.add(lift); pts.push(p); } return pts; };
      // screen-left lens (world +x) is finished: six arcs and its lens -- frame and interior
      for (let k = 0; k < SEG; k++) tube(arc(1, k));
      { const sh = new THREE.Shape(); for (let i = 0; i <= 96; i++) { const p = rimPt(1, i / 96 * 2 * Math.PI); sh[i ? 'lineTo' : 'moveTo'](p.x - cx, p.y - yc); }
        const lens = new THREE.Mesh(new THREE.ShapeGeometry(sh, 2), lensM); lens.position.set(cx, yc, zf); scene.add(lens); }
      // the other rim (world -x, toward the arm) is open: arc 3 (outer side) is in the gripper, arc 4 is not made yet
      const held = 3, missing = 4;
      for (let k = 0; k < SEG; k++) if (k !== held && k !== missing) tube(arc(-1, k));
      for (const side of [1, -1]) for (let k = 0; k < SEG; k++) node(rimPt(side, T0 + k * 2 * Math.PI / SEG), false);   // a silver node at every joint between arcs
      // bridge, hinges + temples back to the water, posts under the rims: nothing floats
      const bt = Math.PI * .5 - .5, b0 = rimPt(1, Math.PI - bt), b1 = rimPt(-1, bt);
      tube([b0, b0.clone().lerp(b1, .5).add(new THREE.Vector3(0, .07 * sc, 0)), b1], R * 1.1);
      for (const side of [1, -1]) {
        const hg = rimPt(side, side > 0 ? .28 : Math.PI - .28).add(new THREE.Vector3(side * .08 * sc, 0, 0)), back = cz + .62 * sc;
        tube([rimPt(side, side > 0 ? .28 : Math.PI - .28), hg], R);
        tube([hg, new THREE.Vector3(hg.x, hg.y - .02 * sc, (zf + back) / 2), new THREE.Vector3(hg.x, hg.y - .12 * sc, back), new THREE.Vector3(hg.x, hg.y - .5 * sc, back + .16 * sc), new THREE.Vector3(hg.x, y0 - .06, back + .2 * sc)], R * .9);
        node(hg, side > 0 && (it.red || 'hinge') === 'hinge');
        const bot = rimPt(side, -Math.PI / 2 + (side > 0 ? 0 : 0)); rod(new THREE.Vector3(bot.x, y0 - .08, bot.z), bot.clone().setY(bot.y - NR), .011 * sc);
      }
      // the arc in the gripper, held 12 cm out toward the arm (world -x) and a little forward
      const lift = new THREE.Vector3(-.12, .02, -.06), hp = arc(-1, held, lift); tube(hp);
      const mid = hp[8], tan = hp[9].clone().sub(hp[7]).normalize();
      HD.armPick = { grip: mid.clone(), dir: tan, out: new THREE.Vector3(-1, 0, 0) };
      heroes.push(new THREE.Vector3(cx, yc - .2 * sc, cz)); HD.frameScale = sc;
    },
    robot_arm(it) {   // matte white ceramic-coated six-axis arm beside the frame, holding the next rod toward the open edge
      const [bx, bz] = ctr(it), up = new THREE.Vector3(0, 1, 0);
      const ceramic = MAT(it.material || 'ceramic_white'), band = MAT(it.joint || 'aluminium'), seam = it.joint === 'black_chrome' ? MAT('black_chrome') : std({ color: '#2a2a2a', roughness: .6 });
      const acrylic = phys({ color: '#f4fbff', transmission: 1, roughness: .03, ior: 1.49, thickness: .02, attenuationColor: new THREE.Color('#cfe9f2'), attenuationDistance: .35 });
      const limb = (a, b, r0, r1, m) => { const v = b.clone().sub(a), g = new THREE.Mesh(new THREE.CylinderGeometry(r1, r0, v.length(), 48), m); g.position.copy(a).add(b).multiplyScalar(.5); g.quaternion.setFromUnitVectors(up, v.clone().normalize()); return add(g); };
      const hub = (p, axis, r, len, m) => { const g = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 48), m); g.position.copy(p); g.quaternion.setFromUnitVectors(up, axis); return add(g); };
      // target: the open edge the frame is waiting for (from node `from` toward node `to`)
      let grip, dir, rs, re;
      if (HD.armPick) { grip = HD.armPick.grip; dir = HD.armPick.dir; }
      else { const P = HD.frameNodes, sc = HD.frameScale || 1, A = P[it.from || 'C'], B = P[it.to || 'H'], r0 = .045 * sc; dir = B.clone().sub(A).normalize();
        rs = A.clone().addScaledVector(dir, r0); re = B.clone().addScaledVector(dir, -r0 - .1);    // the rod stops 10 cm short: still being placed
        grip = rs.clone().lerp(re, .62); }
      box(it.x0 + .05, it.y0 + .05, it.x1 - .05, it.y1 - .05, 0, .04, MAT('aluminium'));                 // floor plate
      const K = it.size || 1, shY = it.sh || .78 * K, base = new THREE.Vector3(bx, 0, bz);
      limb(base.clone().setY(.04), base.clone().setY(.22 * K), .36 * K, .33 * K, ceramic); hub(base.clone().setY(.225 * K), up, .332 * K, .014, seam);
      limb(base.clone().setY(.23 * K), base.clone().setY(shY - .16 * K), .27 * K, .24 * K, ceramic);
      const sh = base.clone().setY(shY);
      const boxLimb = (a, b, w, d, m) => { const v = b.clone().sub(a), y = v.clone().normalize(), z = side.clone(), x = new THREE.Vector3().crossVectors(y, z).normalize();
        const g = new THREE.Mesh(new THREE.BoxGeometry(w, v.length(), d), m); g.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z)); g.position.copy(a).add(b).multiplyScalar(.5); return add(g); };
      const yawV = grip.clone().sub(sh).setY(0).normalize(), side = new THREE.Vector3().crossVectors(up, yawV).normalize();
      // wrist sits behind the grip, approaching slightly from above
      const app = yawV.clone().multiplyScalar(Math.cos(.55)).add(new THREE.Vector3(0, -Math.sin(.55), 0)).normalize(), wr = grip.clone().addScaledVector(app, -.3);
      const l1 = it.l1 || .95, l2 = it.l2 || .82, dv = wr.clone().sub(sh), dd = Math.min(dv.length(), l1 + l2 - .01);
      const a = Math.acos(Math.max(-1, Math.min(1, (l1 * l1 + dd * dd - l2 * l2) / (2 * l1 * dd)))), u = dv.clone().normalize(), perp = new THREE.Vector3().crossVectors(side, u).normalize();
      const el = sh.clone().addScaledVector(u, l1 * Math.cos(a)).addScaledVector(perp, l1 * Math.sin(a) * (perp.y > 0 ? 1 : -1));
      hub(sh, side, .25 * K, .5 * K, ceramic); hub(sh.clone().addScaledVector(side, .255 * K), side, .2 * K, .025, band); hub(sh.clone().addScaledVector(side, -.255 * K), side, .2 * K, .025, band);
      boxLimb(sh.clone().addScaledVector(el.clone().sub(sh).normalize(), -.32 * K), sh, .3 * K, .36 * K, seam);          // motor housing behind the shoulder
      boxLimb(sh, el, .26 * K, .3 * K, ceramic); hub(el, side, .19 * K, .36 * K, ceramic); hub(el.clone().addScaledVector(side, .185 * K), side, .15 * K, .02, band);
      boxLimb(el, wr, .17 * K, .2 * K, ceramic); hub(wr, side, .11 * K, .22 * K, ceramic); hub(wr.clone().addScaledVector(side, .115 * K), side, .085 * K, .014, band);
      const fl = wr.clone().addScaledVector(app, .12); limb(wr, fl, .075 * K, .066 * K, ceramic); limb(fl, fl.clone().addScaledVector(app, .025), .066, .066, band);
      const palm = fl.clone().addScaledVector(app, .07); limb(fl.clone().addScaledVector(app, .025), palm, .05, .05, seam);
      const rodPerp = new THREE.Vector3().crossVectors(dir, app).normalize();
      for (const s of [-1, 1]) { const f0 = palm.clone().addScaledVector(rodPerp, s * .03), f1 = grip.clone().addScaledVector(rodPerp, s * .019); limb(f0, f1, .012, .009, band); }
      if (rs) { const v = re.clone().sub(rs), g = new THREE.Mesh(new THREE.CylinderGeometry(.011, .011, v.length(), 28), acrylic); g.position.copy(rs).add(re).multiplyScalar(.5); g.quaternion.setFromUnitVectors(up, v.normalize()); add(g, true, false); }
    },
    zone() {}, door() {},
  };
  const ORDER = { memory_frame: 0, eyewear_frame: 0, robot_arm: 2 };   // the arm reaches for the frame, so the frame is built first
  for (const it of L.items.slice().sort((a, b) => (ORDER[a.shape] ?? 1) - (ORDER[b.shape] ?? 1))) (S[it.shape] || S.box)(it);

  // the longest mirror wall becomes a true mirror (the visitor sees their own silhouette in it)
  if (HD.mirrorItem) { const it = HD.mirrorItem.slice().sort((a, b) => Math.max(b.x1 - b.x0, b.y1 - b.y0) - Math.max(a.x1 - a.x0, a.y1 - a.y0))[0];
    const along = (it.x1 - it.x0) >= (it.y1 - it.y0), len = along ? it.x1 - it.x0 : it.y1 - it.y0, [cx, cz] = ctr(it);
    const mir = new Reflector(new THREE.PlaneGeometry(len - .1, it.h - .1), { textureWidth: 1024, textureHeight: 400, color: 0xb9bdc2, clipBias: .003 });
    if (along) { const inY = Dp / 2 > cz ? it.y1 + .012 : it.y0 - .012; mir.position.set(cx, it.h / 2, inY); mir.rotation.y = Dp / 2 > cz ? 0 : Math.PI; }
    else { const inX = Wd / 2 > cx ? it.x1 + .012 : it.x0 - .012; mir.position.set(inX, it.h / 2, cz); mir.rotation.y = Wd / 2 > cx ? Math.PI / 2 : -Math.PI / 2; }
    scene.add(mir); HIDE.push(mir);
    const rt = new THREE.WebGLCubeRenderTarget(256, { type: THREE.HalfFloatType }); HD.cube = new THREE.CubeCamera(.1, 60, rt);
    HD.aluwall.forEach(w => { w.material.envMap = rt.texture; w.material.envMapIntensity = 1.1; w.material.needsUpdate = true; }); }

  // ---------------- light ----------------
  const spot = (color, inten, pos, target, angle = .5, pen = .6, shadow = true) => { const s = new THREE.SpotLight(color, inten, 0, angle, pen, 1.6); s.position.set(...pos); s.target.position.set(...target); scene.add(s, s.target); s.castShadow = shadow; s.shadow.mapSize.set(2048, 2048); s.shadow.bias = -.0004; s.shadow.radius = 4; return s; };
  const hero = heroes[0] || new THREE.Vector3(Wd / 2, 1.5, Dp / 2), door = L.items.find(i => i.shape === 'door' || i.type === 'door'), dx = (door.x0 + door.x1) / 2;
  if (light === 'dark_gallery') { scene.add(new THREE.HemisphereLight('#9fb2c0', '#1a1410', .25));
    for (const h of heroes) { spot('#ffe2c8', 300, [h.x - 3.2, Ht - 1.2, h.z - 2.6], [h.x, h.y, h.z], .3, .6); spot('#cfdcff', 120, [h.x + 4, Ht - .2, h.z + 3], [h.x, h.y * .8, h.z], .5, .8); }
    spot('#ffffff', 60, [dx, Ht - .2, 1.2], [dx, 0, 2.2], .8, .7); }
  if (light === 'white_gallery') { scene.add(new THREE.HemisphereLight('#ffffff', '#dcd6cc', .9));
    const d = new THREE.DirectionalLight('#fffaf2', 2.2); d.position.set(hero.x - 6, 14, hero.z - 8); d.target.position.set(Wd / 2, 0, Dp / 2); d.castShadow = true; Object.assign(d.shadow.camera, { left: -Wd, right: Wd, top: Dp, bottom: -Dp, far: 80 }); d.shadow.mapSize.set(4096, 4096); d.shadow.radius = 6; d.shadow.bias = -.0003; scene.add(d, d.target);
    for (const h of heroes) spot('#ffffff', 700, [h.x, Ht - .1, h.z - 2], [h.x, h.y, h.z], .55, .9); }
  if (light === 'cold_spot') {   // bright pale room, one cold blue-white key with a hard edge, a thin rim from behind, a faint beam
    scene.add(new THREE.HemisphereLight('#f4f7fb', '#cdc8c0', .55));
    const d = new THREE.DirectionalLight('#f5f8ff', 1.1); d.position.set(hero.x - 5, 12, hero.z - 9); d.target.position.set(hero.x, 0, hero.z); d.castShadow = true; Object.assign(d.shadow.camera, { left: -Wd, right: Wd, top: Dp, bottom: -Dp, far: 80 }); d.shadow.mapSize.set(4096, 4096); d.shadow.radius = 3; d.shadow.bias = -.0003; scene.add(d, d.target);
    for (const h of heroes) { const kp = [h.x - .3, Ht - .05, h.z - .2]; spot('#dbe7ff', 650, kp, [h.x, 0, h.z], .3, .4);
      const sky = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 2.2), new THREE.MeshBasicMaterial({ color: '#f4f8ff' })); sky.rotation.x = Math.PI / 2; sky.position.set(kp[0], Ht - .01, kp[2]); scene.add(sky); HIDE.push(sky);
      spot('#cfe0ff', 420, [h.x + 1.2, Ht * .55, h.z + 3.2], [h.x, h.y, h.z], .22, .5, false);
      const top = new THREE.Vector3(...kp), bot = new THREE.Vector3(kp[0], 0, kp[2]), v = bot.clone().sub(top), L_ = v.length(), cone = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0 + L_ * Math.tan(.12), L_, 48, 1, true), new THREE.MeshBasicMaterial({ color: '#dfe8ff', transparent: true, opacity: .022, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
      cone.position.copy(top).addScaledVector(v, .5); cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), v.normalize()); scene.add(cone); HIDE.push(cone); } }
  if (light === 'daylight') { scene.add(new THREE.HemisphereLight('#ffffff', '#3a3632', .35)); spot('#ffffff', 300, [dx, Ht - .2, 1], [dx + 3, 0, 5], .9, .9); }
  if (light === 'warm_spot') { scene.add(new THREE.HemisphereLight('#fff2de', '#5a3a26', .5));
    for (const h of heroes) spot('#ffd8a8', 420, [h.x, Ht + 1.2, h.z - .6], [h.x, .8, h.z], .45, .6);
    spot('#ffe6c4', 160, [2, Ht - .2, Dp / 2], [.6, 1.5, Dp / 2], .7, .8); spot('#ffe6c4', 160, [Wd - 2, Ht - .2, Dp / 2], [Wd - .6, 1.5, Dp / 2], .7, .8); spot('#ffe6c4', 160, [Wd / 2, Ht - .2, Dp * .65], [Wd / 2, 1.5, Dp - .6], .8, .8); }

  // ---------------- motion (the synopsis moving) ----------------
  const AN = [], base = o => (o.userData.b || (o.userData.b = { p: o.position.clone(), s: o.scale.clone(), r: o.rotation.clone() }));
  (HD.joint || []).forEach((o, i) => AN.push(t => { const b = base(o); o.scale.y = b.s.y * (1 + .16 * Math.sin(t * 2.1 - i * .55)); }));
  (HD.ball || []).forEach((o, i) => AN.push(t => { const b = base(o); o.position.y = b.p.y + .05 * Math.sin(t * 2.1 - i * .55); }));
  (HD.wire || []).forEach((o, i) => AN.push(t => { const b = base(o); o.position.y = b.p.y + .07 * Math.sin(t * 2.1 - (i % 26) * .12); o.position.z = b.p.z + .04 * Math.sin(t * 1.3 + i); }));
  (HD.lid || []).forEach(o => AN.push(t => { const b = base(o); o.rotation.x = b.r.x + .12 * Math.sin(t * 23) * (.5 + .5 * Math.sin(t * 1.7)); }));
  (HD.tear || []).forEach((o, i) => AN.push(t => { const b = base(o), f = (t * .22 + i * .5) % 1; o.position.y = b.p.y + .1 - f * .5; o.scale.set(1, .4 + .6 * f, 1); }));
  if (HD.shard) { const [sx, sz] = HD.shardCenter; HD.shard.forEach((o, i) => AN.push(t => { const b = base(o), ex = b.p.x - sx, ez = b.p.z - sz, a = t * (.05 + (i % 7) * .006);
    o.position.set(sx + ex * Math.cos(a) - ez * Math.sin(a), b.p.y + .15 * Math.sin(t * .7 + i), sz + ex * Math.sin(a) + ez * Math.cos(a)); o.rotation.y = b.r.y + t * .4; o.rotation.x = b.r.x + t * .23; })); }
  (HD.led || []).forEach(o => AN.push(t => { o.intensity = 3 + 5 * (.5 + .5 * Math.sin(t * 2.1)); }));
  if (HD.creature) HD.creature.children.forEach((o, i) => AN.push(t => { const b = base(o), k = 1 + .018 * Math.sin(t * 11 + i * 1.7) * (.5 + .5 * Math.sin(t * .9 + i)); o.scale.set(b.s.x * k, b.s.y * (2 - k), b.s.z * k); }));
  (HD.flame || []).forEach((o, i) => AN.push(t => { o.material.emissiveIntensity = 4 + 2.5 * Math.sin(t * 13 + i * 2.1) * Math.sin(t * 7.3 + i); }));
  if (HD.ceil) AN.push(t => { HD.ceil.emissiveIntensity = 1.25 + .15 * Math.sin(t * .8); HD.sun.intensity = 1.55 + .18 * Math.sin(t * .8); });
  if (HD.basin) { const [bx, bz] = HD.basin, wm = phys({ color: '#dfeeee', transmission: 1, roughness: 0, ior: 1.33, thickness: .02 });
    for (let i = 0; i < 5; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(.018, 12, 8), wm); d.scale.y = 1.6; scene.add(d); AN.push(t => { const f = (t * 1.3 + i / 5) % 1; d.position.set(bx, 1.4 - f * f * .54, bz + .25); }); }
    for (let i = 0; i < 3; i++) { const r = new THREE.Mesh(new THREE.RingGeometry(.9, 1, 64), new THREE.MeshBasicMaterial({ color: '#ffffff', transparent: true, side: THREE.DoubleSide })); r.rotation.x = -Math.PI / 2; scene.add(r);
      AN.push(t => { const f = (t * .45 + i / 3) % 1; r.position.set(bx, .872, bz + .25); r.scale.setScalar(.03 + f * .55); r.material.opacity = .45 * (1 - f); }); } }
  // the visitor's silhouette: kept just behind the camera, so it is never in view but always in the mirror
  const self = new THREE.Group(); { const m = std({ color: '#1d1d1f', roughness: .6 }); const b = new THREE.Mesh(new THREE.CapsuleGeometry(.22, 1.1, 8, 24), m); b.position.y = .8; const h = new THREE.Mesh(new THREE.SphereGeometry(.12, 24, 16), m); h.position.y = 1.62; self.add(b, h); self.visible = false; scene.add(self); }

  function animate(t) { for (const a of AN) a(t); }
  function frame(cam, look, t, walking) {
    if (HD.cube) { const v = look.clone().sub(cam.position).setY(0).normalize(); self.visible = walking; self.position.set(cam.position.x - v.x * .32, 0, cam.position.z - v.z * .32); self.rotation.y = Math.atan2(v.x, v.z);
      for (const w of HD.aluwall) w.visible = false; HD.cube.position.set(Wd / 2, 1.6, Dp / 2); HD.cube.update(renderer, scene); for (const w of HD.aluwall) w.visible = true; }
    renderer.render(scene, cam);
  }
  return { THREE, renderer, scene, HD, HIDE, heroes, animate, frame, W, H, Wd, Dp, Ht, door };
}

// ---------------- stills (blueprint) ----------------
export function still(job, view, opt = {}) {
  const B = build(job, opt), { THREE, Wd, Dp } = B;
  const cam = new THREE.PerspectiveCamera(view === 'cut' ? 38 : 58, B.W / B.H, .05, 200);
  let look;
  if (view === 'hero' && job.camera) { const C = job.camera; cam.fov = C.fov || 32; cam.updateProjectionMatrix(); cam.position.set(C.pos[0], C.pos[1], C.pos[2]); look = new THREE.Vector3(C.look[0], C.look[1], C.look[2]); }
  else if (view === 'cut') { B.HIDE.forEach(o => o.visible = false); cam.position.set(Wd * 1.05, Math.max(Wd, Dp) * .95, -Dp * .55); look = new THREE.Vector3(Wd * .48, .4, Dp * .52); }
  else {   // 'eye': the stop that looks nearest the hero (else the middle stop); 'stopN': stop N -- seen from 2 m back along the path
    const P = job.layout.flows[0].pts, c = new THREE.CatmullRomCurve3(P.map(([x, y]) => new THREE.Vector3(x, 1.62, y)), false, 'catmullrom', .15), len = c.getLength();
    const st = job.stops.map(s => ({ s, L: new THREE.Vector3(...s.look) })), h = B.heroes[0];
    const m = /^stop(\d)$/.exec(view || '');
    const pick = m ? st[Math.min(+m[1], st.length - 1)] : (h ? st.slice().sort((a, b) => a.L.distanceTo(h) - b.L.distanceTo(h))[0] : st[1] || st[0]);
    let bu = 0, bd = 1e9; for (let i = 0; i <= 600; i++) { const q = c.getPointAt(i / 600), d = (q.x - pick.s.at[0]) ** 2 + (q.z - pick.s.at[1]) ** 2; if (d < bd) { bd = d; bu = i / 600; } }
    cam.position.copy(c.getPointAt(Math.max(0, bu - 2 / len))); look = pick.L.clone(); }
  cam.lookAt(look); B.animate(0); B.frame(cam, look, 0, false); B.frame(cam, look, 0, false);
  return B;
}
