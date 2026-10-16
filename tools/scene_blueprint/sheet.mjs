// A3 blueprint of one image: THE STILL RUNWAY. The Codex concept image is the hero; the three.js long-exposure
// render, plan, section and numbers come from dims.mjs, so the picture and how to shoot it agree.
const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6';
const f = n => (+n).toFixed(2);

export function sheet(D, renderUrl, conceptUrl) {
  let o = '';
  const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
  const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
  const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
  const P = (pts, sw = .25, ex = '') => o += `<polyline points="${pts.map(p => p.map(f).join(',')).join(' ')}" fill="none" stroke-width="${sw}" ${ex}/>`;
  const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
  const dim = 'class="d"', bold = 'font-weight="700"';
  const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
  const arrow = (x, y, ang, col = RED, s = 1.6) => { const a = ang * Math.PI / 180; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };
  const mark = (x, y, n, label, col = RED) => { C(x, y, 2.3, .35, '#123f73', `stroke="${col}"`); T(x, y + .75, n, 1.9, `text-anchor="middle" ${bold} fill="${col}"`); if (label) { o += `<rect x="${f(x + 3)}" y="${f(y - 1.9)}" width="${f(label.length * 1.25 + 2)}" height="3.6" fill="${col}" stroke="none"/>`; T(x + 4, y + .7, label, 1.8, `${bold} fill="#123f73" font-family="${MONO}"`); } };
  const { cam, cube, walkers, turner, studio } = D, T3 = cam.shutter;

  // ---------- 01 the image (Codex concept) with the recognition layer ----------
  const IX = 10, IY = 21, IW = 250, IH = IW * 1024 / 1536;
  head(IX, 13, '01', 'THE IMAGE — THE STILL RUNWAY', 'concept image, generated with Codex from the spec in .relay/tasks/002-still-runway · the final is shot with the applicant (07)');
  o += `<image href="${conceptUrl}" x="${IX}" y="${IY}" width="${IW}" height="${f(IH)}" preserveAspectRatio="xMidYMid slice"/>`;
  R(IX, IY, IW, IH, .4);
  const bx = (u0, v0, u1, v1, label) => { const x = IX + u0 * IW, y = IY + v0 * IH, w = (u1 - u0) * IW, h = (v1 - v0) * IH;
    R(x, y, w, h, .45, 'none', `stroke="${RED}"`); o += `<rect x="${f(x)}" y="${f(y - 3.6)}" width="${f(label.length * 1.18 + 2)}" height="3.6" fill="${RED}" stroke="none"/>`; T(x + 1, y - 1, label, 1.75, `fill="#fff" font-family="${MONO}"`); };
  bx(.372, .325, .612, .825, 'COAT · BLACK WOOL');
  bx(.452, .508, .505, .567, 'CAMERA · FILM');
  bx(.327, .54, .378, .825, 'PLAN · 1:40');
  bx(.548, .528, .567, .571, 'TAG');
  T(IX + .46 * IW, IY + .3 * IH - 4.6, '#JHJ0001', 1.9, `fill="${RED}" font-family="${MONO}" ${bold}`);
  mark(IX + .06 * IW, IY + .2 * IH, '1', 'WALK'); mark(IX + .645 * IW, IY + .5 * IH, '2', 'TURN · PICK UP'); mark(IX + .8 * IW, IY + .8 * IH, '3', 'KEEP');
  T(IX, IY + IH + 5.5, 'THE STILL RUNWAY', 4.4, `${bold} letter-spacing=".2"`);
  T(IX + 52, IY + IH + 5.5, '모두 지나가는데, 하나만 가만히 있다.  Everything walks past. One thing stays still.', 2.5);

  // ---------- 02 staging render ----------
  const RX = 268, RW = 142, RH = RW * 210 / 297;
  head(RX, 13, '02', 'STAGING RENDER', `three.js · ${D.samples} instants averaged over ${'1/' + Math.round(1 / T3)} s`);
  o += `<image href="${renderUrl}" x="${RX}" y="21" width="${RW}" height="${f(RH)}" preserveAspectRatio="xMidYMid slice"/>`; R(RX, 21, RW, RH, .4);
  T(RX, 21 + RH + 3.5, 'positions, speeds and light from dims.mjs — the same numbers as 03 · 04', 1.75, dim);

  // ---------- 03 plan 1:125 ----------
  { const k = 8, ox = 270, oy = 137, X = x => ox + (x + studio.w / 2) * k, Y = z => oy + (studio.d + z) * k;
    head(RX, 131, '03', 'PLAN', 'studio · 1:125');
    R(X(-4), Y(-studio.d), 8 * k, studio.d * k, .35); L(X(-4), Y(-studio.d), X(4), Y(-studio.d), 1);
    const hf = Math.atan(Math.tan(cam.vfov / 2 * Math.PI / 180) * 297 / 210);
    P([[X(-Math.tan(hf) * 7.5), Y(-7.5)], [X(0), Y(0)], [X(Math.tan(hf) * 7.5), Y(-7.5)]], .15, 'stroke-dasharray="1 .8"');
    o += `<polygon points="${f(X(0))},${f(Y(0) - 1.6)} ${f(X(0) - 1.6)},${f(Y(0) + 1)} ${f(X(0) + 1.6)},${f(Y(0) + 1)}" fill="${INK}" stroke="none"/>`; T(X(0) + 2.5, Y(0) + .3, 'camera · h 1200', 1.6, dim);
    R(X(cube.x - cube.s / 2), Y(cube.z - cube.s / 2), cube.s * k, cube.s * k, .35); C(X(cube.x), Y(cube.z + .1), 1.6, .3, INK);
    walkers.forEach(w => { const x1 = w.x0 + w.dir * w.v * T3; L(X(-3.9), Y(w.z), X(3.9), Y(w.z), .12, `stroke="${DIM}" stroke-dasharray=".8 .8"`);
      L(X(w.x0), Y(w.z), X(x1), Y(w.z), 1.6, `stroke="${w.col === '#c8302a' ? RED : INK}" stroke-linecap="round" opacity=".85"`); arrow(X(x1) + w.dir * 1.6, Y(w.z), w.dir > 0 ? 0 : 180, INK, 1.4); T(X(w.x0) + (w.dir > 0 ? -1 : 1), Y(w.z) - 1.4, w.id, 1.5, `${dim} text-anchor="${w.dir > 0 ? 'end' : 'start'}"`); });
    const bz = u => [0, 1].map(i => (1 - u) ** 2 * turner.p0[i] + 2 * (1 - u) * u * turner.p1[i] + u * u * turner.p2[i]);
    P(Array.from({ length: 21 }, (_, i) => { const [x, z] = bz(i / 20); return [X(x), Y(z)]; }), .45, `stroke="${RED}"`);
    const [ex, ez] = bz(1); C(X(ex), Y(ez), 1.4, .35, 'none', `stroke="${RED}"`); T(X(ex) + 2, Y(ez) + 3.2, 'turns · slows · reaches', 1.5, `fill="${RED}"`);
    C(X(D.light.key[0]), Y(D.light.key[2]), 1.2, .3, '#ffe9b0'); T(X(D.light.key[0]) - 1, Y(D.light.key[2]) - 2, 'key', 1.5, `${dim} text-anchor="end"`);
    C(X(D.light.fill[0]), Y(D.light.fill[2]), 1, .3); T(X(D.light.fill[0]) + 1.8, Y(D.light.fill[2]) + .5, 'fill', 1.5, dim);
    T(X(-4), Y(0) + 4, `${studio.w * 1000} × ${studio.d * 1000} white seamless`, 1.6, `class="m"`);
  }

  // ---------- 04 section 1:125 ----------
  { const k = 8, sx = 341, sy = 172, X = d => sx + d * k, Y = y => sy - y * k;
    head(341, 131, '04', 'SECTION', 'camera to wall · 1:125');
    L(X(0), Y(0), X(studio.d), Y(0), .35); L(X(studio.d), Y(0), X(studio.d), Y(studio.h), .9);
    R(X(0) - 1.2, Y(cam.pos[1]) - .8, 2.4, 1.6, .3, INK); L(X(0), Y(cam.pos[1]), X(-cam.at[2]), Y(cam.at[1]), .15, 'stroke-dasharray="1 .8"');
    R(X(-(cube.z - cube.s / 2)), Y(cube.s), cube.s * k, cube.s * k, .3);
    P([[X(-cube.z), Y(cube.s)], [X(-cube.z), Y(cube.s + .62)], [X(-cube.z - .05), Y(1.42)]], .45); C(X(-cube.z), Y(1.5), .9, .3);
    walkers.forEach(w => { L(X(-w.z), Y(0), X(-w.z), Y(1.72), .9, `stroke="${w.col === '#c8302a' ? RED : DIM}" opacity=".55"`); });
    L(X(-turner.p2[1]), Y(0), X(-turner.p2[1]), Y(1.7), .9, `stroke="${RED}"`);
    L(X(0) - 2, Y(cam.pos[1]), X(0) - 2, Y(0), .15); T(X(0) - 2.8, Y(.6), '1200', 1.5, `${dim} text-anchor="end"`);
    T(X(-cube.z) - 1, Y(0) + 3.4, '5000', 1.5, `${dim} text-anchor="middle"`); L(X(0), Y(0) + 1.5, X(-cube.z), Y(0) + 1.5, .15);
    T(X(-cube.z) + 2.5, Y(cube.s / 2), '450', 1.5, dim);
  }

  // ---------- 05 four verbs in one frame ----------
  { const x = 10, y = 200; head(x, y, '05', 'FOUR VERBS IN ONE FRAME', '이야기 전체를 한 장에');
    [['1', 'WALK · 걷다', 'Four people walk past at ~1.3 m/s. At 1/3 s each smears ~0.4 m: clothes in motion, like a show.'],
     ['2', 'TURN · 꺾이다', 'One person in beige slows and bends her path toward the still one. Less blur = she is choosing.'],
     ['3', 'PICK UP · 집다', 'Her hand reaches for the tag on his sleeve: name on the front, contact on the back.'],
     ['4', 'KEEP · 챙기다', 'The white shopping bag in her other hand. The purchase is already packed.']].forEach(([n, a, t], i) => {
      const yy = y + 9 + i * 19; C(x + 2.5, yy, 2.3, .35, '#123f73', `stroke="${RED}"`); T(x + 2.5, yy + .75, n, 1.9, `text-anchor="middle" ${bold} fill="${RED}"`);
      T(x + 7, yy + .9, a, 2.6, bold); o += `<foreignObject x="${x + 7}" y="${yy + 2.4}" width="74" height="15"><div xmlns="http://www.w3.org/1999/xhtml" class="fo">${t}</div></foreignObject>`; });
  }

  // ---------- 06 cast & wardrobe ----------
  { const x = 96, y = 200; head(x, y, '06', 'CAST · WARDROBE', '팔레트 + 빨강 한 점');
    [['STILL · 나', 'black oversized wool long coat · grey knit · wide beige trousers · red socks · film camera in the lap · tag on a red string · rolled plan against the cube'],
     ['W1–W4', 'walk straight across at normal pace, never looking at the camera: black · charcoal · red · grey'],
     ['TURNER', 'beige long coat, white paper shopping bag; enters right, slows over the last 2 m, reaches for the tag'],
     ['SET', `white seamless ${studio.w} × ${studio.d} m · white cube ${cube.s * 1000} · soft key from front-left, fill right`]].forEach(([a, t], i) => {
      const yy = y + 9 + i * 19; T(x, yy, a, 2.1, bold); o += `<foreignObject x="${x}" y="${yy + 1.2}" width="78" height="16"><div xmlns="http://www.w3.org/1999/xhtml" class="fo">${t}</div></foreignObject>`; });
    const pal = [['#161514', 'black'], ['#4a4a32', 'olive'], ['#c8b69b', 'beige'], ['#8b8d8c', 'grey'], ['#efede8', 'off-white'], ['#c8302a', 'red · the eye']];
    pal.forEach(([c, n], i) => { R(x + i * 13, 280, 12, 4, .2, c); T(x + i * 13, 287.4, n, 1.4, dim); });
  }

  // ---------- 07 camera & exposure ----------
  { const x = 180, y = 200; head(x, y, '07', 'SHOOT IT', '생성 이미지는 시안, 최종은 직접 촬영');
    [['Camera', 'Fujifilm on a tripod, locked'], ['Lens', cam.lens], ['Height', `${cam.pos[1] * 1000} mm, ${Math.abs(cube.z) * 1000} mm from the cube`],
     ['Exposure', `${cam.f} · 1/${Math.round(1 / T3)} s · ISO ${cam.iso} · ND if too bright`], ['Focus', 'manual, on the seated eyes; drive: single, 20–30 takes'],
     ['Streak', `1.3 m/s × ${'1/' + Math.round(1 / T3)} s ≈ ${(1.3 * T3 * 1000).toFixed(0)} mm per walker`], ['Still one', 'hold breath on the shutter; elbows on the knees'],
     ['Post', 'red recognition boxes (01) in InDesign / Figma; grain light']].forEach(([a, t], i) => {
      T(x, y + 9 + i * 7.2, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(x + 15, y + 9 + i * 7.2, t, 1.9); });
  }

  // ---------- title block ----------
  { const x = 268, y = 214; L(x - 4, y - 4, 414, y - 4, .3);
    T(x, y + 4, 'ON DISPLAY', 7, `${bold} letter-spacing="-.1"`); T(x, y + 11, 'JEONG HYEOKJU — visual merchandiser', 3, bold);
    T(x, y + 17, '패션쇼에서는 옷이 걷는다. 매장에서는 내가 걷는다.', 2.6, bold);
    [['Sheet', 'One image: THE STILL RUNWAY (cover)'], ['Image', 'Codex concept · .relay/tasks/002-still-runway'], ['Render', 'tools/scene_blueprint (dims.mjs → render + drawings)'],
     ['Date', '2026-10-15'], ['Status', 'Concept. To be shot with the applicant'], ['Note', 'Personal proposal, not affiliated with Shinsegae']].forEach(([a, t], i) => {
      T(x, y + 25 + i * 5.6, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(x + 14, y + 25 + i * 5.6, t, 1.85); });
  }

  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>THE STILL RUNWAY blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:#123f73} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}} .m{font-family:${MONO};fill:#dbe7f2}
.fo{font-family:${F};color:#dbe7f2;font-size:2.05px;line-height:1.45;padding-top:.4px}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="#123f73" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="264" y1="6" x2="264" y2="291" stroke-width=".3"/><line x1="6" y1="194" x2="264" y2="194" stroke-width=".3"/>
<line x1="264" y1="127" x2="414" y2="127" stroke-width=".2"/><line x1="92" y1="194" x2="92" y2="291" stroke-width=".2"/><line x1="176" y1="194" x2="176" y2="291" stroke-width=".2"/>
${o}</svg></body></html>`;
}
