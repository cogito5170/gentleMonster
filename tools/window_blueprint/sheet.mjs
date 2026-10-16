// A3 landscape blueprint sheet for cover concept 1-D "SEE · PICK · KEEP": one SVG in millimetres.
// Every drawing is computed from dims.mjs, the same numbers the render used.
const F = '"Liberation Sans","Archivo",Arial,sans-serif', MONO = '"Liberation Mono",monospace';
const fx = n => (+n).toFixed(2);

export function sheet(D, renderUrl) {
  const { win, stage, frame, depth, base, man, cam, tag, bag, spots } = D;
  const top = stage.h + win.h, b = stage.h + base.h, mx = man.x, mz = man.z;
  const prof = [[.30, .48], [.285, .7], [.25, .95], [.215, 1.12], [.215, 1.25], [.235, 1.33], [.17, 1.39], [.075, 1.41]];
  const cuff = s => [mx + s * .275, b + .8], sh = s => [mx + s * .185, b + 1.24];
  const hx = mx - .285, cy = b + cam.y, tx = tag.gx + .03;
  let o = '';
  const L = (x1, y1, x2, y2, w = .25, extra = '') => o += `<line x1="${fx(x1)}" y1="${fx(y1)}" x2="${fx(x2)}" y2="${fx(y2)}" stroke-width="${w}" ${extra}/>`;
  const P = (pts, w = .25, extra = '') => o += `<polyline points="${pts.map(p => p.map(fx).join(',')).join(' ')}" stroke-width="${w}" fill="none" ${extra}/>`;
  const G = (pts, w = .25, fill = 'none', extra = '') => o += `<polygon points="${pts.map(p => p.map(fx).join(',')).join(' ')}" stroke-width="${w}" fill="${fill}" ${extra}/>`;
  const T = (x, y, s, t, sz = 2.2, extra = '') => o += `<text x="${fx(x)}" y="${fx(y)}" font-size="${sz}" ${s} ${extra}>${t}</text>`;
  const C = (x, y, r, w = .25, fill = 'none') => o += `<circle cx="${fx(x)}" cy="${fx(y)}" r="${fx(r)}" stroke-width="${w}" fill="${fill}"/>`;
  const tick = (x, y) => L(x - .8, y + .8, x + .8, y - .8, .3);
  const dimH = (x1, x2, y, t, up = true) => { L(x1, y, x2, y, .15); tick(x1, y); tick(x2, y); T((x1 + x2) / 2, y + (up ? -.8 : 2.6), 'text-anchor="middle" class="m"', t, 1.9); };
  const dimV = (x, y1, y2, t, left = true) => { L(x, y1, x, y2, .15); tick(x, y1); tick(x, y2); const ym = (y1 + y2) / 2; T(x + (left ? -.9 : 2.4), ym, `text-anchor="middle" class="m" transform="rotate(-90 ${fx(x + (left ? -.9 : 2.4))} ${fx(ym)})"`, t, 1.9); };
  const tagNo = (x, y, n, label) => { C(x, y, 2.4, .3, '#123f73'); T(x, y + .75, 'text-anchor="middle" font-weight="700"', n, 2.2); T(x + 3.4, y + .75, 'font-weight="700" letter-spacing=".2"', label, 2); };
  const head = (x, y, n, t, s) => { T(x, y, 'font-weight="700"', `${n}  ${t}`, 2.6); T(x, y + 3.2, 'class="dim"', s, 1.9); };
  const hatch = (pts) => G(pts, .2, 'url(#hatch)');
  const mm = m => Math.round(m * 1000);

  // ---------- 02 front elevation 1:40 ----------
  { const k = 25, ox = 257, oy = 120, X = x => ox + x * k, Y = y => oy - y * k;
    head(235, 14, '02', 'FRONT ELEVATION', 'from the sidewalk · 1:40');
    L(X(-.6), Y(0), X(3.6), Y(0), .4);
    hatch([[X(-frame.side), Y(0)], [X(0), Y(0)], [X(0), Y(top)], [X(3), Y(top)], [X(3), Y(0)], [X(3 + frame.side), Y(0)], [X(3 + frame.side), Y(top + frame.top)], [X(-frame.side), Y(top + frame.top)]]);
    hatch([[X(0), Y(0)], [X(3), Y(0)], [X(3), Y(stage.h)], [X(0), Y(stage.h)]]);
    G([[X(0), Y(stage.h)], [X(3), Y(stage.h)], [X(3), Y(top)], [X(0), Y(top)]], .35);
    L(X(.2), Y(top - .04), X(2.8), Y(top - .04), .4);
    spots.forEach(s => { G([[X(s.x - .035), Y(top - .04)], [X(s.x + .035), Y(top - .04)], [X(s.x + .03), Y(top - .16)], [X(s.x - .03), Y(top - .16)]], .2); L(X(s.x), Y(top - .16), X(s.aim[0]), Y(s.aim[1]), .12, 'stroke-dasharray="1 .8"'); T(X(s.x) + 1.2, Y(top - .1), 'class="dim"', s.name.split(' ')[0], 1.7); });
    G([[X(base.x0), Y(stage.h)], [X(base.x1), Y(stage.h)], [X(base.x1), Y(b)], [X(base.x0), Y(b)]], .25);
    [-1, 1].forEach(s => G([[X(mx + s * .1 - .095), Y(b)], [X(mx + s * .1 + .095), Y(b)], [X(mx + s * .1 + .085), Y(b + .62)], [X(mx + s * .1 - .085), Y(b + .62)]], .2));
    const coat = prof.map(([r, y]) => [X(mx + r), Y(b + y)]); G([...coat, ...prof.slice().reverse().map(([r, y]) => [X(mx - r), Y(b + y)])], .3, 'rgba(255,255,255,.06)');
    G([[X(mx - .05), Y(b + 1.41)], [X(mx + .05), Y(b + 1.41)], [X(mx + .045), Y(b + 1.53)], [X(mx - .045), Y(b + 1.53)]], .2);
    [-1, 1].forEach(s => { const a = sh(s), c = cuff(s); G([[X(a[0] - .06), Y(a[1])], [X(a[0] + .06), Y(a[1])], [X(c[0] + .058), Y(c[1])], [X(c[0] - .058), Y(c[1])]], .2); });
    G([[X(hx - .11), Y(cy - .05)], [X(hx + .05), Y(cy - .05)], [X(hx + .05), Y(cy + .05)], [X(hx - .11), Y(cy + .05)]], .25, 'rgba(255,255,255,.15)'); L(X(hx), Y(b + .7), X(hx - .03), Y(cy + .05), .15);
    G([[X(bag.x - bag.w / 2), Y(stage.h)], [X(bag.x + bag.w / 2), Y(stage.h)], [X(bag.x + bag.w / 2), Y(stage.h + bag.h)], [X(bag.x - bag.w / 2), Y(stage.h + bag.h)]], .25);
    P([[X(cuff(1)[0]), Y(cuff(1)[1])], [X(tag.gx), Y(tag.gy)], [X(tx), Y(tag.y + tag.h)]], .15);
    G([[X(tx - tag.w / 2), Y(tag.y)], [X(tx + tag.w / 2), Y(tag.y)], [X(tx + tag.w / 2), Y(tag.y + tag.h)], [X(tx - tag.w / 2), Y(tag.y + tag.h)]], .3, '#fff');
    dimH(X(0), X(3), Y(-.28), `${mm(win.w)}`, false);
    dimV(X(-frame.side - .25), Y(0), Y(stage.h), `${mm(stage.h)}`); dimV(X(-frame.side - .25), Y(stage.h), Y(top), `${mm(win.h)}`);
    dimV(X(3 + frame.side + .2), Y(0), Y(tag.y), `${mm(tag.y)}`, false); dimV(X(-frame.side - .6), Y(0), Y(b + 1.53), `${mm(b + 1.53)}`);
    tagNo(X(mx) - 2, Y(b + 1.85), '1', 'SEE'); tagNo(X(tx) + 4, Y(tag.y + tag.h) - 2, '2', 'PICK'); tagNo(X(bag.x + bag.w / 2) + 4, Y(stage.h + bag.h / 2), '3', 'KEEP');
  }

  // ---------- 03 section 1:40 (cut through the mannequin, street on the right) ----------
  { const k = 25, z0 = -depth, ox = 353, oy = 120, X = z => ox + (z - z0) * k, Y = y => oy - y * k;
    head(351, 14, '03', 'SECTION', 'through the mannequin · 1:40');
    L(X(z0 - .1), Y(0), X(.85), Y(0), .4);
    hatch([[X(z0), Y(0)], [X(0), Y(0)], [X(0), Y(stage.h)], [X(z0), Y(stage.h)]]);
    hatch([[X(-.06), Y(top)], [X(0), Y(top)], [X(0), Y(top + frame.top)], [X(-.06), Y(top + frame.top)]]);
    L(X(z0), Y(stage.h), X(z0), Y(top), .35); L(X(z0), Y(top), X(0), Y(top), .35);
    L(X(0), Y(stage.h), X(0), Y(top), .2); L(X(.012), Y(stage.h), X(.012), Y(top), .2);
    T(X(.05), Y(top - .25), 'class="dim"', 'glass 12', 1.7);
    spots.forEach(s => { G([[X(-.43), Y(top - .04)], [X(-.37), Y(top - .04)], [X(-.37), Y(top - .16)], [X(-.43), Y(top - .16)]], .2); L(X(-.4), Y(top - .16), X(s.aim[2]), Y(s.aim[1]), .12, 'stroke-dasharray="1 .8"'); });
    G([[X(base.z0), Y(stage.h)], [X(base.z1), Y(stage.h)], [X(base.z1), Y(b)], [X(base.z0), Y(b)]], .25);
    G([[X(mz - .07), Y(b)], [X(mz + .07), Y(b)], [X(mz + .06), Y(b + .62)], [X(mz - .06), Y(b + .62)]], .2);
    const cs = prof.map(([r, y]) => [X(mz + r * .6), Y(b + y)]); G([...cs, ...prof.slice().reverse().map(([r, y]) => [X(mz - r * .6), Y(b + y)])], .3, 'rgba(255,255,255,.06)');
    G([[X(mz - .05), Y(b + 1.41)], [X(mz + .05), Y(b + 1.41)], [X(mz + .045), Y(b + 1.53)], [X(mz - .045), Y(b + 1.53)]], .2);
    P([[X(mz + .03), Y(cuff(1)[1])], [X(mz + .25), Y(cuff(1)[1] - .02)], [X(0), Y(tag.gy)], [X(tag.out), Y(tag.y + tag.h)]], .2);
    G([[X(tag.out - .004), Y(tag.y)], [X(tag.out + .004), Y(tag.y)], [X(tag.out + .004), Y(tag.y + tag.h)], [X(tag.out - .004), Y(tag.y + tag.h)]], .4, '#fff');
    C(X(.006), Y(tag.gy), .9, .2);
    dimH(X(z0), X(0), Y(-.28), `${mm(depth)}`, false); dimH(X(0), X(tag.out), Y(tag.y - .18), `${mm(tag.out)}`, false);
    dimV(X(.62), Y(0), Y(tag.gy), `${mm(tag.gy)}`, false);
    T(X(.85), Y(1.64), 'text-anchor="end" class="dim"', 'eye 1500, 3600 out →', 1.7);
    L(X(.45), Y(1.5), X(.85), Y(1.5), .15, 'stroke-dasharray="1 .8"');
    tagNo(X(tag.out) + 2.5, Y(tag.y + tag.h) - 5, '2', 'PICK');
  }

  // ---------- 04 plan 1:40 ----------
  { const k = 25, ox = 257, oy = 141, X = x => ox + x * k, Y = z => oy + (z + depth) * k;
    head(235, 136, '04', 'PLAN', 'window bed · 1:40');
    hatch([[X(-frame.side), Y(-.06)], [X(0), Y(-.06)], [X(0), Y(0)], [X(-frame.side), Y(0)]]); hatch([[X(3), Y(-.06)], [X(3 + frame.side), Y(-.06)], [X(3 + frame.side), Y(0)], [X(3), Y(0)]]);
    G([[X(0), Y(-depth)], [X(3), Y(-depth)], [X(3), Y(0)], [X(0), Y(0)]], .35); L(X(0), Y(.006), X(3), Y(.006), .2);
    G([[X(base.x0), Y(base.z0)], [X(base.x1), Y(base.z0)], [X(base.x1), Y(base.z1)], [X(base.x0), Y(base.z1)]], .25);
    o += `<ellipse cx="${fx(X(mx))}" cy="${fx(Y(mz))}" rx="${fx(.3 * k)}" ry="${fx(.18 * k)}" stroke-width=".3" fill="rgba(255,255,255,.06)"/>`;
    G([[X(hx - .11), Y(mz + .05)], [X(hx + .05), Y(mz + .05)], [X(hx + .05), Y(mz + .1)], [X(hx - .11), Y(mz + .1)]], .2);
    G([[X(bag.x - bag.w / 2), Y(bag.z - bag.d / 2)], [X(bag.x + bag.w / 2), Y(bag.z - bag.d / 2)], [X(bag.x + bag.w / 2), Y(bag.z + bag.d / 2)], [X(bag.x - bag.w / 2), Y(bag.z + bag.d / 2)]], .25);
    spots.forEach(s => { C(X(s.x), Y(-.4), .9, .25); L(X(s.x), Y(-.4), X(s.aim[0]), Y(s.aim[2]), .12, 'stroke-dasharray="1 .8"'); T(X(s.x) + 1.4, Y(-.4) - .8, 'class="dim"', s.name.split(' ')[0], 1.7); });
    P([[X(cuff(1)[0]), Y(mz + .03)], [X(tag.gx), Y(0)], [X(tx), Y(tag.out)]], .15, 'stroke-dasharray="1.2 .6"');
    L(X(tx - tag.w / 2), Y(tag.out), X(tx + tag.w / 2), Y(tag.out), .6);
    T(X(1.5), Y(.75), 'text-anchor="middle" class="dim" letter-spacing=".6"', 'SIDEWALK', 1.8);
    L(X(1.5), Y(.45), X(1.5), Y(.62), .2); T(X(1.5) + 1.2, Y(.6), 'class="dim"', '↓ eye 3600', 1.7);
    dimH(X(0), X(3), Y(-depth) - 2.5, `${mm(win.w)}`); dimV(X(3 + frame.side) + 3, Y(-depth), Y(0), `${mm(depth)}`, false);
    tagNo(X(mx) - 2, Y(mz) - 6.5, '1', 'SEE'); tagNo(X(bag.x) + 4, Y(bag.z) - 4.5, '3', 'KEEP');
  }

  // ---------- 05 hang tag 1:2 ----------
  { const k = 1000 / 2.5, w = tag.w * k, h = tag.h * k, x1 = 351, x2 = x1 + w + 5, y = 145;
    head(351, 136, '05', 'HANG TAG', 'front · back · 1:2.5');
    [x1, x2].forEach(x => { G([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], .35, 'rgba(255,255,255,.08)'); C(x + w / 2, y + 4, 1.2, .3); });
    T(x1 + w / 2, y + 14, 'text-anchor="middle" font-weight="700"', 'JEONG', 2.8); T(x1 + w / 2, y + 17.6, 'text-anchor="middle" font-weight="700"', 'HYEOKJU', 2.8);
    T(x1 + w / 2, y + 22, 'text-anchor="middle" class="dim"', 'visual merchandiser', 1.6);
    L(x1 + 4, y + h - 13, x1 + w - 4, y + h - 13, .15);
    T(x1 + w / 2, y + h - 8.5, 'text-anchor="middle" font-weight="700"', 'SEE · PICK · KEEP', 1.7);
    T(x1 + w / 2, y + h - 4.5, 'text-anchor="middle" class="dim"', 'size: one of one', 1.6);
    ['TEL  ____', 'MAIL ____', 'WEB  ____'].forEach((t, i) => T(x2 + 3, y + 12 + i * 4, 'class="m"', t, 1.7));
    G([[x2 + w / 2 - 6, y + h - 20], [x2 + w / 2 + 6, y + h - 20], [x2 + w / 2 + 6, y + h - 8], [x2 + w / 2 - 6, y + h - 8]], .25); T(x2 + w / 2, y + h - 13.2, 'text-anchor="middle" class="dim"', 'QR', 1.8);
    T(x2 + w / 2, y + h - 4.5, 'text-anchor="middle" class="dim"', 'portfolio link', 1.6);
    T(x1, y + h + 4, 'class="dim"', `${mm(tag.w)} × ${mm(tag.h)} · 350 g/m² off-white · cotton string Ø1.5`, 1.7);
  }

  // ---------- 06 glass detail 1:2 ----------
  { const ox = 172, oy = 205, x = v => ox + v / 3, Y = v => oy + v / 3;
    head(126, 176, '06', 'STRING THROUGH GLASS', 'detail · 1:3 · no drilling');
    hatch([[x(0), Y(-55)], [x(12), Y(-55)], [x(12), Y(75)], [x(0), Y(75)]]);
    T(x(6), Y(-60), 'text-anchor="middle" class="dim"', 'glass 12', 1.7);
    G([[x(-2), Y(-10)], [x(0), Y(-10)], [x(0), Y(10)], [x(-2), Y(10)]], .25); T(x(-75), Y(-36), 'class="dim"', 'clear adhesive dot Ø20 (inside face)', 1.6);
    P([[x(12), Y(-18)], [x(18), Y(-18)], [x(20), Y(-10)], [x(20), Y(10)], [x(18), Y(18)], [x(12), Y(18)]], .25); L(x(20), Y(0), x(26), Y(0), .3);
    T(x(27), Y(-22), 'class="dim"', 'clear suction hook Ø36', 1.6);
    P([[x(-70), Y(-24)], [x(-30), Y(-8)], [x(-2), Y(0)]], .3); T(x(-72), Y(-28), 'class="dim"', '← from the sleeve', 1.6);
    P([[x(26), Y(0)], [x(34), Y(20)], [x(38), Y(48)]], .3);
    G([[x(30), Y(48)], [x(46), Y(48)], [x(46), Y(76)], [x(30), Y(76)]], .35, 'rgba(255,255,255,.1)'); T(x(48), Y(64), 'class="dim"', 'tag', 1.6);
    T(x(-72), Y(46), 'class="dim"', 'INSIDE', 1.8); T(x(16), Y(84), 'class="dim"', 'OUTSIDE (street)', 1.8);
    L(x(-75), Y(0), x(90), Y(0), .12, 'stroke-dasharray="3 1 .5 1"'); T(x(68), Y(-2), 'class="dim"', 'one axis', 1.6);
  }

  const props = [
    ['Mannequin', 'headless, matte white, on the model base'],
    ['Look', "applicant's own: black oversized wool long coat · grey knit · wide beige trousers"],
    ['Camera', 'film camera, silver/black, leather strap from the right hand'],
    ['Model base', `${mm(base.x1 - base.x0)} × ${mm(base.z1 - base.z0)} × ${mm(base.h)}, white foam board 5, cut-out walls 45`],
    ['Hang tag', `${mm(tag.w)} × ${mm(tag.h)}, string ${mm(tag.out)} outside the glass (06)`],
    ['Bag', `${mm(bag.w)} × ${mm(bag.d)} × ${mm(bag.h)} white paper, slate lining, white tissue`],
    ['Light', spots.map(s => `${s.name} ${s.beam}`).join(' · ') + ' · 3000 K track'],
    ['Backdrop', 'off-white matte, window bed and walls the same'],
  ];
  const steps = [
    ['1', 'SEE', 'VP', 'The window. A mannequin styled in my own wardrobe holds the camera I take pictures with, standing on a model of a space I drew.'],
    ['2', 'PICK', 'PP', `The tag hangs ${mm(tag.out)} outside the glass at ${mm(tag.y)}–${mm(tag.y + tag.h)} above the sidewalk: within reach. Name on the front, contact on the back.`],
    ['3', 'KEEP', 'IP', 'The paper bag already waits at its feet, tissue in. The purchase is packed; you take the contact home.'],
  ];
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ON DISPLAY cover blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:#123f73}
svg{display:block;width:420mm;height:297mm} text{fill:#f4f8fb;stroke:none;font-family:${F}}
.fo{font-family:${F};color:#dbe7f2;font-size:2.5px;line-height:1.5;padding-top:.5px} .fo.s{font-size:1.85px;line-height:1.35;padding-top:.3px} .dim{fill:#bcd2e6} .m{font-family:${MONO};fill:#dbe7f2}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="#f4f8fb" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern>
<pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.6" stroke="rgba(255,255,255,.45)" stroke-width=".18"/></pattern></defs>
<rect width="420" height="297" fill="#123f73" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="231" y1="6" x2="231" y2="291" stroke-width=".3"/><line x1="231" y1="131" x2="414" y2="131" stroke-width=".2"/><line x1="6" y1="170" x2="231" y2="170" stroke-width=".2"/><line x1="231" y1="222" x2="414" y2="222" stroke-width=".3"/><line x1="122" y1="170" x2="122" y2="291" stroke-width=".2"/>
<text x="10" y="13" font-size="2.6" font-weight="700" fill="#f4f8fb" stroke="none">01  CONCEPT RENDER</text><text x="10" y="16.2" font-size="1.9" class="dim" stroke="none">eye 1500 above the sidewalk, 3600 from the glass · three.js r170, reflection of the stone facade across the street composited on the pane</text>
<image href="${renderUrl}" x="10" y="19" width="212" height="${fx(212 * 210 / 297)}" preserveAspectRatio="xMidYMid slice"/><rect x="10" y="19" width="212" height="${fx(212 * 210 / 297)}" stroke-width=".4"/>
<g stroke="#f4f8fb">${o}</g>
<g stroke="none">
<text x="10" y="176" font-size="2.6" font-weight="700">07  SEE · PICK · KEEP</text><text x="10" y="179.2" font-size="1.9" class="dim">three shopping acts, three moments of VMD</text>
${steps.map(([n, a, v, t], i) => { const y = 186 + i * 33; return `<circle cx="13" cy="${y + 1.5}" r="2.6" fill="#123f73" stroke="#f4f8fb" stroke-width=".3"/><text x="13" y="${y + 2.3}" font-size="2.3" font-weight="700" text-anchor="middle">${n}</text>
<text x="18" y="${y + 2.4}" font-size="3.6" font-weight="700" letter-spacing=".3">${a}</text><text x="${18 + a.length * 2.9}" y="${y + 2.4}" font-size="2" class="dim"> · ${v}</text>
<foreignObject x="18" y="${y + 4}" width="100" height="26"><div xmlns="http://www.w3.org/1999/xhtml" class="fo">${t}</div></foreignObject>`; }).join('')}
<text x="126" y="236" font-size="2.6" font-weight="700">08  PROPS · MATERIALS</text>
${props.map(([a, t], i) => `<text x="126" y="${241 + i * 6}" font-size="1.9" font-weight="700">${a}</text><foreignObject x="146" y="${238.3 + i * 6}" width="82" height="6"><div xmlns="http://www.w3.org/1999/xhtml" class="fo s">${t}</div></foreignObject>`).join('')}
<text x="236" y="231" font-size="7.2" font-weight="700" letter-spacing="-.1">ON DISPLAY</text><text x="236" y="238.5" font-size="4" font-weight="700">JEONG HYEOKJU — visual merchandiser</text>
<text x="236" y="245" font-size="2.1" class="dim">Portfolio cover concept 1-D · the shop window that displays me</text>
${[['Sheet', 'Render, front elevation, section, plan, hang tag, glass detail'], ['Scale', 'drawings 1:40 · tag 1:2.5 · glass detail 1:3 (on A3)'], ['Units', 'millimetres'], ['Date', '2026-10-15'], ['Status', 'Concept. Dimensions assumed, not surveyed: measure the real window before building'], ['Source', 'tools/window_blueprint (dims.mjs drives the render and every drawing)'], ['Note', 'Personal proposal, not affiliated with Shinsegae']].map(([a, t], i) => `<text x="236" y="${252 + i * 5}" font-size="1.8" class="dim" letter-spacing=".25">${a.toUpperCase()}</text><text x="252" y="${252 + i * 5}" font-size="1.95">${t}</text>`).join('')}
</g></svg></body></html>`;
}
