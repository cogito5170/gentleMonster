// THE STILL RUNWAY as a long exposure: everything that moves is rendered at `samples` instants inside the
// shutter time and averaged, so walkers smear and the seated figure stays sharp -- the same physics as the shoot.
// Returns the composited canvas and the screen boxes of the three elements (coat, camera, plan) for the overlay.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export function render(D, W, H) {
  const std = o => new THREE.MeshStandardMaterial(o);
  const S = new THREE.Scene(); S.background = new THREE.Color('#efede8');
  const R = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  R.setPixelRatio(1); R.setSize(W, H); R.toneMapping = THREE.ACESFilmicToneMapping; R.toneMappingExposure = 1.05;
  R.outputColorSpace = THREE.SRGBColorSpace; R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap;
  S.environment = new THREE.PMREMGenerator(R).fromScene(new RoomEnvironment(), .04).texture; S.environmentIntensity = .55;

  const add = (parent, geo, mat, x, y, z, o = {}) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); if (o.rx) m.rotation.x = o.rx; if (o.rz) m.rotation.z = o.rz; if (o.ry) m.rotation.y = o.ry; m.castShadow = o.cast !== false; m.receiveShadow = true; parent.add(m); return m; };
  const { studio, cam, cube, me } = D;
  const white = std({ color: '#f2f0eb', roughness: .95 });
  add(S, new THREE.PlaneGeometry(40, 40), white, 0, 0, -10, { rx: -Math.PI / 2, cast: false });
  add(S, new THREE.PlaneGeometry(40, 12), white, 0, 6, -studio.d, { cast: false });

  // the still one, seated on the cube
  const M = { coat: std({ color: me.coat, roughness: .92 }), knit: std({ color: me.knit, roughness: 1 }), tr: std({ color: me.trousers, roughness: .95 }),
    skin: std({ color: '#d8cbbf', roughness: .6 }), shoe: std({ color: '#121212', roughness: .4 }), red: std({ color: me.accent, roughness: .8 }),
    cubeM: std({ color: '#e4e1da', roughness: .8 }), black: std({ color: '#141414', roughness: .45 }), silver: std({ color: '#c6c8ca', metalness: 1, roughness: .3 }),
    paper: std({ color: '#f4f1ea', roughness: .9 }), plan: std({ color: '#e9e4d8', roughness: .9 }) };
  const cx = cube.x, cz = cube.z, s = cube.s;
  add(S, new THREE.BoxGeometry(s, s, s), M.cubeM, cx, s / 2, cz);
  const seat = s, hip = [cx, seat + .1, cz + .02];
  [-1, 1].forEach(k => {
    add(S, new THREE.CylinderGeometry(.085, .09, .44, 20), M.tr, cx + k * .11, seat + .09, cz + .2, { rx: Math.PI / 2 });        // thighs
    add(S, new THREE.CylinderGeometry(.08, .095, .44, 20), M.tr, cx + k * .12, seat - .2, cz + .42);                              // shins
    add(S, new THREE.CylinderGeometry(.05, .05, .04, 16), M.red, cx + k * .12, .1, cz + .43);                                      // red socks
    add(S, new THREE.BoxGeometry(.1, .08, .27), M.shoe, cx + k * .12, .04, cz + .49);
  });
  add(S, new THREE.LatheGeometry([[.21, 0], [.2, .25], [.2, .45], [.22, .55], [.16, .61], [.07, .63]].map(([r, y]) => new THREE.Vector2(r, y)), 40), M.coat, hip[0], hip[1], hip[2], {}).scale.z = .62;
  add(S, new THREE.BoxGeometry(.46, .03, .36), M.coat, cx, seat + .19, cz + .16);                                                  // coat over the lap
  [-1, 1].forEach(k => add(S, new THREE.BoxGeometry(.03, .42, .38), M.coat, cx + k * .225, seat + .02, cz + .15));                    // long coat falling past the cube
  add(S, new THREE.TorusGeometry(.065, .025, 10, 28), M.knit, cx, hip[1] + .63, hip[2], { rx: Math.PI / 2 });
  add(S, new THREE.CylinderGeometry(.045, .05, .1, 16), M.skin, cx, hip[1] + .69, hip[2]);
  const head = add(S, new THREE.SphereGeometry(.1, 32, 20), M.skin, cx, hip[1] + .84, hip[2] + .01); head.scale.set(.9, 1.15, 1);
  [-1, 1].forEach(k => {                                                                                                            // arms down to the lap
    const a = new THREE.Vector3(cx + k * .2, hip[1] + .55, hip[2]), c = new THREE.Vector3(cx + k * .13, seat + .25, cz + .3), d = c.clone().sub(a);
    const m = add(S, new THREE.CylinderGeometry(.06, .065, d.length(), 16), M.coat, (a.x + c.x) / 2, (a.y + c.y) / 2, (a.z + c.z) / 2); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize());
    add(S, new THREE.SphereGeometry(.04, 14, 10), M.skin, c.x, c.y - .02, c.z + .03);
  });
  const camBody = add(S, new THREE.BoxGeometry(.15, .09, .06), M.black, cx, seat + .27, cz + .36);
  add(S, new THREE.BoxGeometry(.15, .025, .06), M.silver, cx, seat + .32, cz + .36);
  add(S, new THREE.CylinderGeometry(.03, .032, .05, 24), M.black, cx + .02, seat + .27, cz + .41, { rx: Math.PI / 2 });
  const plan = add(S, new THREE.CylinderGeometry(.04, .04, .72, 20), M.plan, cx + .33, .33, cz + .05, { rz: -.32 });                // rolled plan leaning on the cube
  const tagS = new THREE.TubeGeometry(new THREE.CatmullRomCurve3([[cx - .14, seat + .25, cz + .33], [cx - .2, seat + .13, cz + .38], [cx - .22, seat + .05, cz + .4]].map(p => new THREE.Vector3(...p))), 20, .0035, 6);
  add(S, tagS, M.red, 0, 0, 0, { cast: false });
  add(S, new THREE.BoxGeometry(.055, .09, .002), M.paper, cx - .22, seat - .01, cz + .4, { rz: .1, cast: false });

  // walkers: simple figures; `pose(t)` moves them inside the exposure
  const person = (col, bag) => {
    const g = new THREE.Group(), cm = std({ color: col, roughness: .9 }), lg = std({ color: '#1b1b1b', roughness: .85 });
    const legs = [-1, 1].map(k => { const p = new THREE.Group(); p.position.set(k * .09, .86, 0); add(p, new THREE.CylinderGeometry(.065, .07, .86, 14), lg, 0, -.43, 0); add(p, new THREE.BoxGeometry(.1, .07, .26), lg, 0, -.84, .05); g.add(p); return p; });
    add(g, new THREE.CylinderGeometry(.19, .23, .72, 24), cm, 0, 1.2, 0).scale.z = .6;
    add(g, new THREE.SphereGeometry(.1, 20, 14), M.skin, 0, 1.68, 0).scale.set(.9, 1.15, 1);
    add(g, new THREE.CylinderGeometry(.05, .055, .08, 12), M.skin, 0, 1.58, 0);
    const arms = [-1, 1].map(k => { const p = new THREE.Group(); p.position.set(k * .23, 1.5, 0); add(p, new THREE.CylinderGeometry(.055, .06, .66, 12), cm, 0, -.33, 0); g.add(p); return p; });
    if (bag) { const b = new THREE.Group(); b.position.set(.27, .72, .02); add(b, new THREE.BoxGeometry(.26, .32, .1), std({ color: '#f6f5f1', roughness: .9 }), 0, -.05, 0); add(b, new THREE.TorusGeometry(.05, .004, 6, 16, Math.PI), M.black, 0, .11, 0); g.add(b); }
    S.add(g); return { g, legs, arms };
  };
  const P = D.walkers.map(w => ({ w, p: person(w.col) }));
  const T = D.turner, tp = person(T.col, T.bag);
  const bez = (u, i) => (1 - u) ** 2 * T.p0[i] + 2 * (1 - u) * u * T.p1[i] + u * u * T.p2[i];
  const pose = (t) => {
    const u = t / cam.shutter;
    P.forEach(({ w, p }) => { const x = w.x0 + w.dir * w.v * t, ph = (x * 4.3); p.g.position.set(x, Math.abs(Math.sin(ph)) * .02, w.z); p.g.rotation.y = w.dir * Math.PI / 2;
      p.legs.forEach((l, k) => l.rotation.x = (k ? 1 : -1) * .38 * Math.sin(ph)); p.arms.forEach((a, k) => a.rotation.x = (k ? -1 : 1) * .3 * Math.sin(ph)); });
    const v = T.s0 + (1 - T.s0) * (1 - (1 - u) ** 3), x = bez(v, 0), z = bez(v, 1), dx = bez(Math.min(1, v + .01), 0) - x, dz = bez(Math.min(1, v + .01), 1) - z;
    tp.g.position.set(x, 0, z); tp.g.rotation.y = Math.atan2(dx, dz) * .6 + Math.atan2(-x, -(z - cz)) * .4;
    tp.legs.forEach((l, k) => l.rotation.x = (k ? 1 : -1) * .22 * (1 - u)); tp.arms[0].rotation.x = -.5 * u; tp.arms[0].rotation.z = .25 * u;   // left hand starts to reach
  };

  const key = new THREE.DirectionalLight('#fff6ea', 2.2); key.position.set(...D.light.key); key.target.position.set(0, .6, cz); S.add(key.target);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5, near: .5, far: 20 }); key.shadow.radius = 8; key.shadow.bias = -.0005; S.add(key);
  const fill = new THREE.DirectionalLight('#eef2ff', .6); fill.position.set(...D.light.fill); S.add(fill);
  S.add(new THREE.HemisphereLight('#ffffff', '#d8d3ca', .55));

  const C = new THREE.PerspectiveCamera(cam.vfov, W / H, .05, 60); C.position.set(...cam.pos); C.lookAt(...cam.at);
  const out = document.createElement('canvas'); out.width = W; out.height = H; out.id = 'out';
  const o = out.getContext('2d');
  for (let k = 0; k < D.samples; k++) { pose(cam.shutter * (k + .5) / D.samples); R.render(S, C); o.globalAlpha = 1 / (k + 1); o.drawImage(R.domElement, 0, 0); }
  o.globalAlpha = 1;

  // screen boxes of the three elements (for the red recognition layer)
  const box = obj => { const b = new THREE.Box3().setFromObject(obj), pts = []; for (const X of [b.min.x, b.max.x]) for (const Y of [b.min.y, b.max.y]) for (const Z of [b.min.z, b.max.z]) { const v = new THREE.Vector3(X, Y, Z).project(C); pts.push([(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]); }
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]); return [Math.min(...xs) / W, Math.min(...ys) / H, Math.max(...xs) / W, Math.max(...ys) / H]; };
  const coatG = new THREE.Group(); S.children.filter(m => m.material === M.coat).forEach(m => coatG.add(m.clone()));
  window.__boxes = { coat: box(coatG), camera: box(camBody), plan: box(plan) };
  return out;
}
