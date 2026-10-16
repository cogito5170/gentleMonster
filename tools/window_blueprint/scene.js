// Cover concept ①-D "SEE · PICK · KEEP" as a three.js still: a shop window seen from the sidewalk.
// One dims object (build.mjs) drives this render and the drawings, so the picture and the blueprint agree.
//
// World: x across the window (0 = left jamb), y up from the sidewalk, z toward the viewer (glass at z = 0,
// window interior is z < 0). Metres. Deterministic (seeded noise).
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export function render(D, W, H) {
  let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const tex = (size, draw, rep = [1, 1]) => {
    const c = document.createElement('canvas'); c.width = c.height = size; draw(c.getContext('2d'), size);
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); t.colorSpace = THREE.SRGBColorSpace; return t;
  };
  const grain = (g, s, base, amt, n, sz) => { g.fillStyle = base; g.fillRect(0, 0, s, s); for (let i = 0; i < n; i++) { const v = (rnd() - .5) * amt; g.fillStyle = v > 0 ? `rgba(255,255,255,${v})` : `rgba(0,0,0,${-v})`; const q = sz * (.4 + rnd()); g.fillRect(rnd() * s, rnd() * s, q, q); } };
  const std = o => new THREE.MeshStandardMaterial(o);
  const M = {
    granite: std({ map: tex(1024, (g, s) => { grain(g, s, '#3d3c3a', .5, 220000, 2.2); for (let i = 0; i < 3000; i++) { g.fillStyle = rnd() > .5 ? 'rgba(10,10,10,.7)' : 'rgba(200,198,190,.35)'; g.fillRect(rnd() * s, rnd() * s, 2 + rnd() * 4, 2 + rnd() * 4); } }, [2, 2]), roughness: .7 }),
    pavement: std({ map: tex(1024, (g, s) => { grain(g, s, '#6f706c', .18, 90000, 2); g.strokeStyle = 'rgba(30,30,30,.35)'; g.lineWidth = 3; for (let k = 0; k <= s; k += s / 2) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k, s); g.stroke(); g.beginPath(); g.moveTo(0, k); g.lineTo(s, k); g.stroke(); } }, [4, 2]), roughness: .9 }),
    wall: std({ color: '#ecebe6', roughness: .95 }),
    stage: std({ color: '#e4e1da', roughness: .85 }),
    model: std({ color: '#f7f6f2', roughness: .9 }),
    mannequin: std({ color: '#f1f0ec', roughness: .45 }),
    coat: std({ color: '#191817', roughness: .92 }),
    knit: std({ color: '#8b8d8c', roughness: 1 }),
    trousers: std({ color: '#c8b69b', roughness: .95 }),
    silver: std({ color: '#c7c9cb', metalness: 1, roughness: .3 }),
    black: std({ color: '#151515', roughness: .5 }),
    lens: std({ color: '#0d0f12', roughness: .15, metalness: .4 }),
    strap: std({ color: '#5a3b26', roughness: .7 }),
    tag: std({ color: '#f4f1ea', roughness: .9, side: THREE.DoubleSide }),
    string: std({ color: '#efe9dc', roughness: 1 }),
    bag: std({ color: '#f5f4f0', roughness: .9 }),
    bagIn: std({ color: '#4a5563', roughness: .9 }),
    tissue: std({ color: '#ffffff', roughness: 1 }),
    track: std({ color: '#1c1c1c', roughness: .5 }),
  };

  const S = new THREE.Scene();
  S.background = new THREE.Color('#1d232b');
  const R = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  R.setPixelRatio(1); R.setSize(W, H);
  R.toneMapping = THREE.ACESFilmicToneMapping; R.toneMappingExposure = 1.0;
  R.outputColorSpace = THREE.SRGBColorSpace;
  R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap;
  const pm = new THREE.PMREMGenerator(R);
  S.environment = pm.fromScene(new RoomEnvironment(), .04).texture;
  S.environmentIntensity = .22;

  const add = (geo, mat, x, y, z, o = {}) => {
    const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z);
    if (o.rx) m.rotation.x = o.rx; if (o.ry) m.rotation.y = o.ry; if (o.rz) m.rotation.z = o.rz;
    if (o.sz) m.scale.z = o.sz;
    m.castShadow = o.cast !== false; m.receiveShadow = true; S.add(m); return m;
  };
  const box = (x0, x1, y0, y1, z0, z1, mat, o) => add(new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), mat, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, o);
  const tube = (pts, r, mat) => add(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map(p => new THREE.Vector3(...p))), 80, r, 8, false), mat, 0, 0, 0);

  const { win, stage, frame, depth, base, man, cam, tag, bag, spots, eye } = D;
  const Wn = win.w, top = stage.h + win.h;
  // street side: sidewalk, granite surround with the opening cut out
  box(-4, Wn + 4, -.05, 0, 0, 6, M.pavement);
  box(-frame.side - 1.5, -.03, 0, top + frame.top, -.06, .0, M.granite);
  box(Wn + .03, Wn + frame.side + 1.5, 0, top + frame.top, -.06, .0, M.granite);
  box(-.03, Wn + .03, top + .03, top + frame.top + 1, -.06, .0, M.granite);
  box(-.03, Wn + .03, 0, stage.h - .02, -.06, .0, M.granite);
  // window box
  box(0, Wn, stage.h - .02, stage.h, -depth, 0, M.stage);
  box(0, Wn, stage.h, top, -depth - .02, -depth, M.wall);
  box(-.02, 0, stage.h, top, -depth, 0, M.wall); box(Wn, Wn + .02, stage.h, top, -depth, 0, M.wall);
  box(0, Wn, top, top + .02, -depth, 0, M.wall);
  box(.2, Wn - .2, top - .05, top - .02, -.42, -.38, M.track, { cast: false });

  // architectural model base with cut-out walls (BUILD)
  const b = stage.h + base.h, mz = man.z;
  box(base.x0, base.x1, stage.h, b, base.z0, base.z1, M.model);
  [[.05, .45, .02, .03], [.62, .86, .02, .03], [.05, .03, .02, .55], [.86, .03, .02, .4], [.3, .35, .4, .02], [.55, .28, .2, .02]].forEach(([u, du, v, dv]) => {
    const x = base.x0 + u, z = base.z0 + v; box(x, x + Math.max(du, .006), b, b + .045, z, z + Math.max(dv, .006), M.model);
  });

  // headless mannequin dressed in the applicant's own palette (WEAR)
  const mx = man.x;
  [-1, 1].forEach(s => {
    add(new THREE.CylinderGeometry(.095, .11, .6, 24), M.trousers, mx + s * .1, b + .32, mz);
    add(new THREE.CapsuleGeometry(.04, .1, 4, 12), M.mannequin, mx + s * .1, b + .04, mz + .05, { rx: Math.PI / 2 });
  });
  const prof = [[.30, .48], [.285, .7], [.25, .95], [.215, 1.12], [.215, 1.25], [.235, 1.33], [.17, 1.39], [.075, 1.41]].map(([r, y]) => new THREE.Vector2(r, y));
  add(new THREE.LatheGeometry(prof, 48), M.coat, mx, b, mz, { sz: .6 });
  box(mx - .006, mx + .006, b + .5, b + 1.28, mz + .175, mz + .185, M.black, { cast: false });       // front opening seam
  add(new THREE.TorusGeometry(.07, .028, 12, 32), M.knit, mx, b + 1.405, mz, { rx: Math.PI / 2 });     // grey knit collar
  add(new THREE.CylinderGeometry(.045, .055, .09, 24), M.mannequin, mx, b + 1.46, mz);                  // neck stub
  add(new THREE.SphereGeometry(.047, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), M.mannequin, mx, b + 1.5, mz, { sz: 1 }); // neck cap
  const sh = (s) => [mx + s * .185, b + 1.24, mz], cuff = (s) => [mx + s * .275, b + .8, mz + .03];
  [-1, 1].forEach(s => {
    const a = new THREE.Vector3(...sh(s)), c = new THREE.Vector3(...cuff(s)), d = c.clone().sub(a);
    const m = add(new THREE.CylinderGeometry(.062, .07, d.length(), 20), M.coat, (a.x + c.x) / 2, (a.y + c.y) / 2, (a.z + c.z) / 2);
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().normalize());
    add(new THREE.CapsuleGeometry(.035, .07, 4, 12), M.mannequin, c.x + s * .01, c.y - .08, c.z);
  });

  // film camera hanging from the right hand (SEE)
  const hx = mx - .285, hy = b + .7;
  tube([[hx, hy, mz + .03], [hx - .02, hy - .1, mz + .06], [hx - .03, b + cam.y + .06, mz + .07]], .006, M.strap);
  const cy = b + cam.y;
  box(hx - .11, hx + .05, cy - .05, cy + .05, mz + .05, mz + .1, M.black);
  box(hx - .11, hx + .05, cy + .02, cy + .05, mz + .05, mz + .1, M.silver);
  add(new THREE.CylinderGeometry(.03, .032, .05, 28), M.lens, hx - .03, cy - .01, mz + .125, { rx: Math.PI / 2 });

  // hang tag: string from the left cuff, through the glass, the tag dangles outside within reach (PICK)
  const c = cuff(1), g = [tag.gx, tag.gy, 0];
  tube([[c[0], c[1] - .02, c[2]], [c[0] + .1, c[1] - .03, c[2] + .2], [(c[0] + g[0]) / 2 + .05, (c[1] + g[1]) / 2 - .01, c[2] / 2 + .1], g], .0018, M.string);
  const outside = [
    tube([g, [g[0] + .02, g[1] - .02, tag.out * .5], [g[0] + .03, tag.y + tag.h + .005, tag.out]], .0018, M.string),
    add(new THREE.BoxGeometry(tag.w, tag.h, .002), M.tag, g[0] + .03, tag.y + tag.h / 2, tag.out, { rz: .06, ry: -.35, cast: false }),
    add(new THREE.CylinderGeometry(.006, .006, .003, 16), M.black, g[0] + .03, tag.y + tag.h - .01, tag.out + .002, { rx: Math.PI / 2, ry: -.35, cast: false }),

    add(new THREE.CylinderGeometry(.018, .018, .004, 24), new THREE.MeshStandardMaterial({ color: '#e8eef2', transparent: true, opacity: .55, roughness: .1 }), g[0], g[1], .003, { rx: Math.PI / 2, cast: false }),
  ];

  // shopping bag waiting at the mannequin's feet (KEEP)
  const bx = bag.x, bz = bag.z, by = stage.h;
  [[bag.w, bag.h, .004, 0, bag.d / 2], [bag.w, bag.h, .004, 0, -bag.d / 2], [.004, bag.h, bag.d, bag.w / 2, 0], [.004, bag.h, bag.d, -bag.w / 2, 0]].forEach(([w, h, d, ox, oz]) =>
    add(new THREE.BoxGeometry(w, h, d), M.bag, bx + ox, by + h / 2, bz + oz));
  box(bx - bag.w / 2, bx + bag.w / 2, by + bag.h - .03, by + bag.h - .028, bz - bag.d / 2, bz + bag.d / 2, M.bagIn, { cast: false });
  [-1, 1].forEach(s => add(new THREE.TorusGeometry(.045, .004, 8, 24, Math.PI), M.black, bx + s * .07, by + bag.h, bz + s * .0, {}));
  for (let i = 0; i < 7; i++) {
    const t = add(new THREE.IcosahedronGeometry(.05 + rnd() * .03, 0), M.tissue, bx + (rnd() - .5) * bag.w * .7, by + bag.h + .01 + rnd() * .05, bz + (rnd() - .5) * bag.d * .5);
    t.rotation.set(rnd() * 3, rnd() * 3, rnd() * 3); t.scale.y = .6;
  }

  // light: two narrow spots on the track, a soft wash on the backdrop, dusk outside
  spots.forEach(sp => {
    const L = new THREE.SpotLight('#ffe7c4', sp.cd, 8, sp.angle, .55, 1.6);
    L.position.set(sp.x, top - .07, -.4); L.target.position.set(...sp.aim); S.add(L.target);
    L.castShadow = true; L.shadow.mapSize.set(2048, 2048); L.shadow.bias = -.0004; L.shadow.radius = 4; S.add(L);
    add(new THREE.CylinderGeometry(.03, .035, .12, 16), M.track, sp.x, top - .1, -.4, { cast: false });
  });
  const fill = new THREE.PointLight('#fff3e2', 2.2, 4, 2); fill.position.set(Wn / 2, top - .3, -.25); S.add(fill);
  const sky = new THREE.HemisphereLight('#7d8da3', '#2a2622', .35); S.add(sky);

  // glass: almost invisible pane; the reflection is composited below
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(Wn, win.h), new THREE.MeshStandardMaterial({ color: '#cfd8e0', transparent: true, opacity: .05, roughness: .05, metalness: .3 }));
  glass.position.set(Wn / 2, stage.h + win.h / 2, 0); S.add(glass);

  const C = new THREE.PerspectiveCamera(eye.fov, W / H, .05, 60);
  C.position.set(...eye.pos); C.lookAt(...eye.at);
  R.render(S, C);

  // faint reflection of the classical stone facade across the street, mirrored on the glass
  const out = document.createElement('canvas'); out.width = W; out.height = H; out.id = 'out';
  const o = out.getContext('2d'); o.drawImage(R.domElement, 0, 0);
  const P = ([x, y, z]) => { const v = new THREE.Vector3(x, y, z).project(C); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; };
  const q = [[0, stage.h, 0], [Wn, stage.h, 0], [Wn, top, 0], [0, top, 0]].map(P);
  o.save(); o.beginPath(); q.forEach(([x, y], i) => i ? o.lineTo(x, y) : o.moveTo(x, y)); o.closePath(); o.clip();
  o.globalCompositeOperation = 'screen';
  const [x0, y1] = q[0], [x1] = q[1], y0 = q[3][1], gw = x1 - x0, gh = y1 - y0;
  const sf = o.createLinearGradient(0, y0, 0, y0 + gh * .7); sf.addColorStop(0, 'rgba(201,194,180,.16)'); sf.addColorStop(1, 'rgba(201,194,180,0)');
  o.globalAlpha = 1; o.fillStyle = sf; o.fillRect(x0, y0, gw, gh * .7);                                   // stone face, fading down
  o.globalAlpha = .05; o.fillStyle = '#fff3dc';
  for (let i = 0; i < 4; i++) {                                                                          // arched windows
    const ax = x0 + gw * (.08 + i * .24), aw = gw * .12, ay = y0 + gh * .1, ah = gh * .3;
    o.beginPath(); o.moveTo(ax, ay + ah); o.lineTo(ax, ay + aw / 2); o.arc(ax + aw / 2, ay + aw / 2, aw / 2, Math.PI, 0); o.lineTo(ax + aw, ay + ah); o.closePath(); o.fill();
  }
  o.globalAlpha = .05; o.fillStyle = '#e9e2d2'; o.fillRect(x0, y0 + gh * .5, gw, gh * .012);            // cornice
  [[.18, .62], [.86, .58]].forEach(([u, v]) => {                                                          // street lamps
    const lx = x0 + gw * u, ly = y0 + gh * v, r = gw * .045, gr = o.createRadialGradient(lx, ly, 0, lx, ly, r);
    gr.addColorStop(0, 'rgba(255,200,130,.35)'); gr.addColorStop(1, 'rgba(255,200,130,0)'); o.globalAlpha = 1; o.fillStyle = gr; o.fillRect(lx - r, ly - r, 2 * r, 2 * r);
  });
  const gl = o.createLinearGradient(x0, y0, x1, y1); gl.addColorStop(0, 'rgba(255,255,255,0)'); gl.addColorStop(.42, 'rgba(255,255,255,.07)'); gl.addColorStop(.5, 'rgba(255,255,255,0)');
  o.globalAlpha = 1; o.fillStyle = gl; o.fillRect(x0, y0, gw, gh);
  o.restore();

  // second pass: only what hangs outside the glass, drawn over the reflection (it is in front of the pane)
  S.traverse(m => { if (m.isMesh) m.userData.v = m.visible, m.visible = outside.includes(m); });
  S.background = null; R.setClearColor(0x000000, 0); R.shadowMap.autoUpdate = false; R.clear(); R.render(S, C);
  o.drawImage(R.domElement, 0, 0);
  S.traverse(m => { if (m.isMesh) m.visible = m.userData.v; });
  return out;
}
