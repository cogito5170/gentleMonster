// 30-second first-person walkthrough. Page contract (render.py):
// window.__ready === true and window.renderAt(t) draws the frame for time t (deterministic).
// 0-6 s aerial of the cutaway with the drawn circulation in red and a title card,
// 6-27.4 s first-person walk along layout.flows[0] exactly, holding at the three synopsis stops,
// 27.4-30 s the philosophy line.
import * as THREE from 'three';
import { build } from 'gm/scene';

export function tour(job) {
  const B = build(job, { w: 1280, h: 720 }), { scene, renderer, HIDE, Wd, Dp, Ht } = B, L = job.layout, $ = id => document.getElementById(id);
  document.documentElement.style.setProperty('--acc', job.accent);
  const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  $('bug').textContent = `${job.brand} · first-person walkthrough`;
  $('card').innerHTML = `<div class="k">${esc(job.brand)}</div><div class="t">${esc(job.title)}</div><div class="l">${esc(job.line)}</div><div class="m">${Wd.toFixed(1)} × ${Dp.toFixed(1)} m · ceiling ${Ht} m · ${(Wd * Dp).toFixed(0)} m² · red line = blueprint circulation · dimensions assumed</div>`;
  $('end').innerHTML = `<div class="k">${esc(job.brand)}</div><div class="t">${esc(job.title)}</div><div class="q">${esc(job.quote)}</div><div class="m">concept walkthrough · not a survey</div>`;

  const FP = L.flows[0].pts;
  const curve = new THREE.CatmullRomCurve3(FP.map(([x, y]) => new THREE.Vector3(x, 0, y)), false, 'catmullrom', .15);
  const route = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(FP.map(([x, y]) => new THREE.Vector3(x, .05, y)), false, 'catmullrom', .15), 300, .07, 8), new THREE.MeshBasicMaterial({ color: job.accent }));
  scene.add(route);
  { const s = 230 / Math.max(Wd, Dp); let g = `<svg width="${Wd * s}" height="${Dp * s}" viewBox="0 0 ${Wd} ${Dp}" style="display:block;transform:scaleY(-1)"><rect x="0" y="0" width="${Wd}" height="${Dp}" fill="none" stroke="#fff" stroke-width=".12"/>`;
    for (const it of L.items) if (!['zone', 'door', 'window'].includes(it.type)) g += `<rect x="${it.x0}" y="${it.y0}" width="${it.x1 - it.x0}" height="${it.y1 - it.y0}" fill="rgba(255,255,255,.22)" stroke="rgba(255,255,255,.5)" stroke-width=".05"/>`;
    g += `<polyline points="${FP.map(p => p.join(',')).join(' ')}" fill="none" stroke="${job.accent}" stroke-width=".14"/><circle id="dot" r=".38" fill="#fff" stroke="${job.accent}" stroke-width=".12"/><line id="ray" stroke="#fff" stroke-width=".1"/></svg><div class="lb">Plan · you are here</div>`;
    $('mini').innerHTML = g; }

  const NS = 1200, samp = []; for (let i = 0; i <= NS; i++) samp.push(curve.getPointAt(i / NS));
  const uOf = ([x, y]) => { let b = 0, bd = 1e9; for (let i = 0; i <= NS; i++) { const d = (samp[i].x - x) ** 2 + (samp[i].z - y) ** 2; if (d < bd) { bd = d; b = i; } } return b / NS; };
  const ST = job.stops.map(s => ({ ...s, u: uOf(s.at), L: new THREE.Vector3(...s.look) })).sort((a, b) => a.u - b.u);
  const A1 = 6.0, W0 = 6.4, W1 = 27.4, hold = ST.reduce((a, s) => a + s.d, 0), move = (W1 - W0) - hold;
  const KF = []; { let t = W0, u = 0, prev = null;
    for (const s of [...ST, { u: 1, d: 0, end: true }]) { const dt = move * (s.u - u); KF.push([t, t + dt, u, s.u, prev, s.end ? null : s, false]); t += dt;
      if (!s.end) { KF.push([t, t + s.d, s.u, s.u, s, s, true]); t += s.d; prev = s; } u = s.u; } }
  const sm = x => { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };
  const win = (t, a, b, f = .6) => Math.min(sm((t - a) / f), 1 - sm((t - (b - f)) / f));
  const cam = new THREE.PerspectiveCamera(56, B.W / B.H, .05, 200), ctrv = new THREE.Vector3(Wd / 2, .3, Dp / 2), Rm = Math.max(Wd, Dp);
  let hidden = null; const setHidden = h => { if (h === hidden) return; hidden = h; for (const o of HIDE) o.visible = !h; route.visible = h; renderer.shadowMap.needsUpdate = true; };
  renderer.shadowMap.autoUpdate = false; renderer.shadowMap.needsUpdate = true;
  const moving = !!(B.HD.joint || B.HD.wire);             // breathing structures move their shadows

  function walk(t) {
    const k = KF.find(k => t < k[1]) || KF[KF.length - 1], f = Math.max(0, Math.min(1, (t - k[0]) / Math.max(1e-6, k[1] - k[0])));
    const u = k[2] + (k[3] - k[2]) * sm(f), p = curve.getPointAt(Math.min(1, u)), ahead = curve.getPointAt(Math.min(1, u + .045)).setY(1.45);
    let look, h = 1.62, active = null, act = 0;
    if (k[6]) { const s = k[4]; look = s.L.clone(); h = s.h; p.add(s.L.clone().sub(p).setY(0).normalize().multiplyScalar(.35 * sm(f))); active = s; act = win(t, k[0] - .2, k[1] + .1, .5); }
    else { const wp = k[4] ? 1 - sm(f / .35) : 0, wn = k[5] ? sm((f - .5) / .5) : 0;
      look = ahead.clone().multiplyScalar(1 - wp - wn); if (k[4]) look.addScaledVector(k[4].L, wp); if (k[5]) look.addScaledVector(k[5].L, wn);
      h = 1.62 + (k[4] ? (k[4].h - 1.62) * wp : 0) + (k[5] ? (k[5].h - 1.62) * wn : 0); }
    p.y = h + (k[6] ? 0 : .018 * Math.sin(t * 7.5));
    return { p, look, active, act };
  }
  function renderAt(t) {
    B.animate(t);
    let pos, look, info = null;
    if (t < W0) { setHidden(true); const u = sm(t / A1), ang = -2.2 + u * 1.1, r = Rm * (1.2 - .15 * u), hh = Rm * (1.05 - .25 * u);
      pos = new THREE.Vector3(ctrv.x + Math.cos(ang) * r, hh, ctrv.z + Math.sin(ang) * r); look = ctrv; cam.fov = 36; }
    else { setHidden(false); info = walk(t); pos = info.p; look = info.look; cam.fov = 56; }
    if (moving) renderer.shadowMap.needsUpdate = true;
    const last = ST[ST.length - 1], g = info && info.active === last ? info.act : 0;       // the last stop's products light up when reached for
    for (const b of B.HD.prod || []) { b.material.emissive.set('#ffb468'); b.material.emissiveIntensity = 3 * g; }
    cam.updateProjectionMatrix(); cam.position.copy(pos); cam.lookAt(look);
    B.frame(cam, look, t, t >= W0);
    $('card').style.opacity = win(t, .4, W0 - .3, .7);
    const cp = $('cap'); if (info && info.active) { cp.querySelector('b').textContent = info.active.cap; cp.querySelector('span').textContent = info.active.sub; } cp.style.opacity = info ? info.act : 0;
    $('mini').style.opacity = t >= W0 && t < W1 + .3 ? Math.min(sm((t - W0) / .6), 1 - sm((t - W1) / .5)) * .95 : 0;
    if (info) { const d = $('dot'), r = $('ray'), v = look.clone().sub(pos).setY(0).normalize(); d.setAttribute('cx', pos.x); d.setAttribute('cy', pos.z);
      r.setAttribute('x1', pos.x); r.setAttribute('y1', pos.z); r.setAttribute('x2', pos.x + v.x * 1.6); r.setAttribute('y2', pos.z + v.z * 1.6); }
    $('end').style.opacity = sm((t - W1) / .8);
    $('fade').style.opacity = Math.max(1 - sm(t / .5), Math.min(sm((t - (W0 - .5)) / .4), 1 - sm((t - W0) / .4)), sm((t - 29.4) / .6));
    $('bar').style.width = (100 * t / 30).toFixed(2) + '%';
  }
  window.__path = () => samp.map(v => [v.x, v.z]);
  return { renderAt, canvas: renderer.domElement };
}
