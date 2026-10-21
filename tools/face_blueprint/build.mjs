// node tools/face_blueprint/build.mjs [task]
// THE FACE IS YOURS — the v5 story (docs/shinsegae_vmd/storyline_blank_face.md) as one image + one A3 blueprint.
// The image is made by Codex (.relay/tasks/009-the-face-is-yours, codex-image skill); this script lays out the sheet:
// the image with its sentence map, the forced-perspective section that puts the face on the empty neck, the plan,
// the story, what it says about the applicant, and how to shoot it.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/shinsegae_vmd/blueprint');
const TMP = path.join(repo, 'out/face_blueprint');
const TASK = process.argv[2] || '009-the-face-is-yours';
const IMG = path.join(repo, '.relay/tasks', TASK, 'image.png');
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

// one source for section + plan (metres). x: toward the aisle (glass at 0, inside < 0), y: up, z: across the window
const D = {
  cam: { x: -4.6, z: 0 },                                       // camera deep inside the boutique, long lens
  form: { x: -0.6, z: 0, neck: 1.45, head: 1.56, shoulder: 1.32, w: .42 },   // headless dress form; `head` = where a head's centre would be
  glass: { x: 0, top: 2.8, bed: .35 },
  face: { x: .6, z: 0 },                                        // the one who stops, just beyond the glass
  lanes: [1.7, 2.6],                                            // everyone else walking past
  lens: { f: 56, N: 5.6, coc: .02, sensorW: 23.5 },             // Fujifilm APS-C, XF56mm
};
// the face lands on the neck when camera eye, the head point over the neck and the face are on one line.
// Fix the face at an ordinary standing height and solve for the camera height.
const FACE_Y = 1.58;
const r = (D.face.x - D.cam.x) / (D.form.x - D.cam.x);           // distance ratio face : form, seen from the camera
D.cam.eye = (FACE_Y - r * D.form.head) / (1 - r);
D.face.y = FACE_Y;
const scale = 1 / r;                                             // how big their head looks, relative to a head on the form
const focus = (D.form.x + D.face.x) / 2 - D.cam.x, H = (D.lens.f / 1000) ** 2 / (D.lens.N * D.lens.coc / 1000);
const near = H * focus / (H + focus), far = H * focus / (H - focus);
const fov = 2 * Math.atan(D.lens.sensorW / 2 / D.lens.f), frameW = 2 * (D.form.x - D.cam.x) * Math.tan(fov / 2);

const SPOTF = path.join(here, `spots_${TASK}.json`);
const SPOTS = JSON.parse(fs.existsSync(SPOTF) ? fs.readFileSync(SPOTF, 'utf8') : '{}');

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff', NAVY = '#123f73';
const f = n => (+n).toFixed(2), m = n => (+n).toFixed(2);
let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, rr, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(rr)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const P = (pts, sw = .25, ex = '') => o += `<polyline points="${pts.map(p => p.map(f).join(',')).join(' ')}" fill="none" stroke-width="${sw}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo') => o += `<foreignObject x="${f(x)}" y="${f(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const dim = 'class="d"', bold = 'font-weight="700"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const arrow = (x, y, ang, col = RED, s = 1.6) => { const a = ang * Math.PI / 180; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };
const num = (x, y, n, col = RED) => { C(x, y, 2.2, .35, NAVY, `stroke="${col}"`); T(x, y + .75, n, 1.9, `text-anchor="middle" ${bold} fill="${col}"`); };

// the story, sentence by sentence; each sentence points at a part of the image
const S = [
  ['마네킹에는 얼굴이 없다.', 'neck'],
  ['나는 그 빈자리를 채우지 않는다.', 'neck'],
  ['대신 그 아래를 짓는다.', 'form'],
  ['어깨에 맞춰 코트를 고르고, 니트의 결을 맞추고, 스카프 하나로 색을 정한다.', 'form'],
  ['건축이 사람이 들어설 자리를 남겨 두듯, 나는 한 벌의 옷에 사람이 들어설 자리를 남긴다.', 'neck'],
  ['그 자리에 얼굴을 넣는 것은 유리 앞에 선 사람이다.', 'face'],
  ['걸음을 멈춘 누군가가 웃는다면, 그는 마네킹이 아니라 그 옷을 입은 자신을 본 것이다.', 'face'],
  ['나는 얼굴 없는 사람을 만든다.', 'form'],
  ['얼굴은 보는 사람이 가져온다.', 'face'],
];
const KEY = { neck: '1', form: '2', face: '3', name: '4', pass: '5' };

// ---------- 01 the image ----------
const IX = 10, IY = 21, IW = 250, IH = IW * 1024 / 1536;
head(IX, 13, '01', 'THE IMAGE — THE FACE IS YOURS', `concept image, generated with Codex from .relay/tasks/${TASK} · numbers = sentences in 04`);
if (fs.existsSync(IMG)) o += `<image href="${pathToFileURL(IMG).href}" x="${IX}" y="${IY}" width="${IW}" height="${f(IH)}" preserveAspectRatio="xMidYMid slice"/>`;
R(IX, IY, IW, IH, .4);
const at = k => SPOTS[k] ? [IX + SPOTS[k][0] * IW, IY + SPOTS[k][1] * IH] : null;
(SPOTS.tags || []).forEach(([label, u0, v0, u1, v1, col]) => {
  const c = col === 'eye' ? EYE : RED, x = IX + u0 * IW, y = IY + v0 * IH, w = (u1 - u0) * IW, h = (v1 - v0) * IH;
  R(x, y, w, h, .5, 'none', `stroke="${c}"`); o += `<rect x="${f(x)}" y="${f(y - 3.8)}" width="${f(label.length * 1.3 + 2)}" height="3.8" fill="${c}" stroke="none"/>`;
  T(x + 1, y - 1, label, 2, `fill="${c === EYE ? NAVY : '#fff'}" ${bold} font-family="${MONO}"`); });
if (SPOTS.neck) { const [x, y] = at('neck');                    // where the face lands: crosshair on the empty neck
  C(x, y, 4.2, .45, 'none', `stroke="${RED}" stroke-dasharray="1.2 .8"`); L(x - 6.5, y, x - 4.6, y, .45, `stroke="${RED}"`); L(x + 4.6, y, x + 6.5, y, .45, `stroke="${RED}"`); L(x, y - 6.5, x, y - 4.6, .45, `stroke="${RED}"`); L(x, y + 4.6, x, y + 6.5, .45, `stroke="${RED}"`); }
if (SPOTS.name && SPOTS.nameOverlay) { const [x, y] = at('name');
  o += `<text x="0" y="0" font-size="7" font-weight="700" letter-spacing="1.6" fill="rgba(255,255,255,.8)" stroke="none" text-anchor="middle" transform="translate(${f(x)} ${f(y)}) scale(-1 1)">HYEOK JU</text>`; }
Object.entries(KEY).forEach(([k, n]) => { const p = at(k + 'Label'); if (p) num(p[0], p[1], n); });

// ---------- 02 section: forced perspective ----------
const sx = 272, k = 17.5, X = d => sx + (d + 4.9) * k;
{ const gy = 100, Y = h => gy - h * k;
  head(268, 13, '02', 'SECTION — 얼굴이 빈 목에 올라오는 선', 'one line: my eye → over the empty neck → their face · metres');
  L(X(-4.9), gy, X(2.9), gy, .4); o += `<rect x="${f(X(-4.9))}" y="${gy}" width="${f(7.8 * k)}" height="1.6" fill="url(#hatch)" stroke="none"/>`;
  L(X(-4.9), Y(3.05), X(0), Y(3.05), .3); T(X(-4.8), Y(3.05) - 1, 'boutique ceiling', 1.5, dim);
  R(X(0) - .5, Y(D.glass.top), 1, (D.glass.top - D.glass.bed) * k, .35, 'rgba(159,211,255,.25)'); R(X(-.9), Y(D.glass.bed), .9 * k, D.glass.bed * k, .3, 'url(#hatch)');
  T(X(0) + 1, Y(D.glass.top) + 2.5, 'glass', 1.6, dim); T(X(0) + 1, Y(D.glass.top) + 5, 'HYEOK JU (mirrored)', 1.4, dim);
  // dress form: base, pole, torso, empty neck
  const fx = X(D.form.x); L(fx - 2.5, Y(D.glass.bed), fx + 2.5, Y(D.glass.bed), .5); L(fx, Y(D.glass.bed), fx, Y(.95), .4);
  o += `<path d="M${f(fx - 3.2)} ${f(Y(.95))} L${f(fx - 3.6)} ${f(Y(1.2))} Q${f(fx - 3.8)} ${f(Y(D.form.shoulder))} ${f(fx - 1)} ${f(Y(D.form.neck - .04))} L${f(fx - .8)} ${f(Y(D.form.neck))} L${f(fx + .8)} ${f(Y(D.form.neck))} L${f(fx + 1)} ${f(Y(D.form.neck - .04))} Q${f(fx + 3.8)} ${f(Y(D.form.shoulder))} ${f(fx + 3.6)} ${f(Y(1.2))} L${f(fx + 3.2)} ${f(Y(.95))} Z" stroke-width=".4" fill="rgba(255,255,255,.12)"/>`;
  L(fx + 3.4, Y(1.22), fx + 2.2, Y(1.38), .9, `stroke="${RED}"`);   // the red scarf
  o += `<ellipse cx="${f(fx)}" cy="${f(Y(D.form.head))}" rx="${f(.075 * k)}" ry="${f(.11 * k)}" stroke-width=".35" fill="none" stroke="${RED}" stroke-dasharray=".8 .6"/>`;
  T(fx - 13, Y(D.form.head) - 3, 'empty neck', 1.6, `fill="${RED}"`);
  // the face, just beyond the glass
  const px = X(D.face.x); C(px, Y(D.face.y), .1 * k, .4, 'rgba(255,255,255,.12)'); L(px, Y(D.face.y - .12), px, Y(.9), .4); L(px, Y(.9), px - 1.5, Y(0), .4); L(px, Y(.9), px + 1.5, Y(0), .4);
  T(px + 2.6, Y(D.face.y) - .5, 'their face', 1.6, `fill="${RED}"`); T(px + 2.6, Y(D.face.y) + 2, `${m(D.face.y)} m`, 1.5, dim);
  D.lanes.forEach(x => { L(X(x), Y(0), X(x), Y(1.5), .5, `stroke="${DIM}" opacity=".45"`); C(X(x), Y(1.6), .1 * k, .3, 'none', `stroke="${DIM}" opacity=".45"`); L(X(x) - 2.5, Y(.8), X(x) + 2.5, Y(.8), .3, `stroke="${DIM}" opacity=".6"`); arrow(X(x) + 2.9, Y(.8), 0, DIM, 1.1); });
  T(X(1.6), Y(1.85), 'walking past', 1.5, dim);
  // camera + the line
  const cx = X(D.cam.x), cy = Y(D.cam.eye); L(cx, cy, cx - 1.6, Y(0), .3); L(cx, cy, cx + 1.6, Y(0), .3); R(cx - 1.4, cy - 1, 2.8, 2, .4, NAVY, `stroke="${EYE}"`);
  L(cx, cy, px, Y(D.face.y), .5, `stroke="${EYE}" stroke-dasharray="1.6 1"`); arrow(px - 1.2, Y(D.face.y) + .02, Math.atan2(Y(D.face.y) - cy, px - cx) * 180 / Math.PI, EYE);
  T(cx - 1, cy - 3, 'my eye · camera', 1.6, `fill="${EYE}"`); T(cx - 1, cy + 4.5, `${m(D.cam.eye)} m`, 1.5, dim);
  const dimH = (a, b, y, t) => { L(X(a), y, X(b), y, .15); [a, b].forEach(v => L(X(v) - .7, y + .7, X(v) + .7, y - .7, .3)); T((X(a) + X(b)) / 2, y + 2.8, t, 1.5, `${dim} text-anchor="middle"`); };
  dimH(D.cam.x, D.form.x, gy + 4, `${m(D.form.x - D.cam.x)} m`); dimH(D.form.x, D.face.x, gy + 4, `${m(D.face.x - D.form.x)} m`);
  T(272, 31, `their head looks ×${m(r === 0 ? 0 : 1 / r)} the size of a head on the form`, 1.6, dim);
  T(272, 34, 'camera far back + long lens → the two distances read as one', 1.6, dim);
}

// ---------- 03 plan ----------
{ const cy0 = 158, Z = z => cy0 + z * k;
  head(268, 117, '03', 'PLAN', 'camera, empty neck and face on one straight line · the lens frame at the form');
  L(X(0), Z(-1.3), X(0), Z(1.3), .8, `stroke="${EYE}" opacity=".6"`); T(X(0) + 1, Z(-1.3) + 2, 'glass', 1.5, dim);
  L(X(-4.9), Z(-1.3), X(0), Z(-1.3), .3); L(X(-4.9), Z(1.3), X(0), Z(1.3), .3); T(X(-4.8), Z(-1.3) - 1, 'boutique', 1.5, dim);
  R(X(-.9), Z(-1.1), .9 * k, 2.2 * k, .3, 'url(#hatch)'); T(X(-.88), Z(1.1) + 2.4, 'display bed', 1.4, dim);
  const fx = X(D.form.x); o += `<ellipse cx="${f(fx)}" cy="${f(Z(0))}" rx="${f(.14 * k)}" ry="${f(D.form.w / 2 * k)}" stroke-width=".4" fill="rgba(255,255,255,.12)"/>`; C(fx, Z(0), .06 * k, .35, 'none', `stroke="${RED}"`);
  T(fx - 5, Z(-.42) - 1.2, 'dress form', 1.5, dim);
  const px = X(D.face.x); C(px, Z(0), .12 * k, .4, 'rgba(255,255,255,.12)'); T(px - 2, Z(.42) + 2, 'their face', 1.5, `fill="${RED}"`);
  D.lanes.forEach((x, i) => { const z0 = i ? 1.2 : -1.2, z1 = -z0; L(X(x), Z(z0), X(x), Z(z1), .35, `stroke="${DIM}" stroke-dasharray="1.4 .9"`); arrow(X(x), Z(z1), z1 > 0 ? 90 : -90, DIM, 1.2); });
  const cx = X(D.cam.x); R(cx - 1.4, Z(0) - 1, 2.8, 2, .4, NAVY, `stroke="${EYE}"`); T(cx - 1, Z(0) - 2.4, 'camera', 1.5, `fill="${EYE}"`);
  const half = Math.tan(fov / 2); [-1, 1].forEach(s => L(cx, Z(0), X(D.face.x + .3), Z(s * half * (D.face.x + .3 - D.cam.x)), .25, `stroke="${EYE}" opacity=".5"`));
  L(cx, Z(0), px, Z(0), .5, `stroke="${EYE}" stroke-dasharray="1.6 1"`);
  T(cx + 4, Z(0) + 9, `56 mm frame at the form ≈ ${m(frameW)} m wide`, 1.5, dim);
}

// ---------- 04 the story ----------
{ const x = 10, y = 202; head(x, y, '04', 'STORY — 얼굴은 보는 사람이 가져온다', 'v5 · 255 characters · number = part of the image');
  S.forEach(([s, kk], i) => { const yy = y + 10 + i * 8.6; num(x + 2.5, yy - .8, KEY[kk]); FO(x + 7, yy - 4.4, 158, 9, s, "fo t"); });
}

// ---------- 05 who it is about ----------
{ const x = 180, y = 202; head(x, y, '05', 'THE APPLICANT', 'what each part says about me');
  [['COMBINE · 조합한다', '코트 · 니트 · 스카프. 단일 아이템이 아니라 한 벌의 합을 짓는 VMD'],
   ['BUILD · 짓는다', '건축이 사람이 들어설 자리를 남기듯, 옷에 사람이 들어설 자리를 남긴다'],
   ['LEAVE ROOM · 비워 둔다', '얼굴을 채우지 않는다. 진열은 보는 사람이 와야 완성된다'],
   ['THE SMILE · 입은 나', '손님은 마네킹이 아니라 그 옷을 입은 자신을 보고 웃는다']].forEach(([a, t], i) => {
    const yy = y + 10 + i * 19; T(x, yy, a, 2.1, `${bold} fill="${RED}"`); FO(x, yy + 1, 80, 15, t, 'fo s'); });
}

// ---------- 06 shoot it + title block ----------
{ const x = 268, y = 204; L(x - 4, y - 4, 414, y - 4, .3);
  T(x, y + 5, 'THE FACE IS YOURS', 6.4, `${bold} letter-spacing="-.1"`); T(x, y + 11, 'HYEOK JU — visual merchandiser', 3, bold);
  T(x, y + 17, '나는 얼굴 없는 사람을 만든다. 얼굴은 보는 사람이 가져온다.', 2.3, bold);
  [['Camera', `Fujifilm, XF56mm, f/${D.lens.N}, focus ${m(focus)} m (sharp ${m(near)}–${m(far)} m), 1/30 s, tripod`],
   ['Height', `lens ${m(D.cam.eye)} m · face ${m(D.face.y)} m · neck point ${m(D.form.head)} m`],
   ['Distance', `camera → form ${m(D.form.x - D.cam.x)} m · form → face ${m(D.face.x - D.form.x)} m`],
   ['Align', 'grid on the rear screen; the person outside steps until the face sits on the neck'],
   ['Light', 'boutique dim, aisle bright; rim light on the form from the aisle'],
   ['Glass', 'HYEOK JU in white cut vinyl, read from inside (mirrored)'],
   ['Image', `Codex concept · .relay/tasks/${TASK} · AI person, fictional`],
   ['Note', 'final shot with my own styling · not affiliated with Shinsegae']].forEach(([a, t], i) => {
    T(x, y + 24 + i * 7.6, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); FO(x + 15, y + 21.2 + i * 7.6, 130, 7.4, t, 'fo s'); });
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>THE FACE IS YOURS blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}}
.fo{font-family:${F};color:#eef4fa;font-size:2.35px;line-height:1.4;padding-top:.6px} .fo.s{font-size:1.85px;color:#dbe7f2;padding-top:1.1px} .fo.t{padding-top:1.6px}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern>
<pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.6" stroke="rgba(255,255,255,.35)" stroke-width=".18"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="264" y1="6" x2="264" y2="291" stroke-width=".3"/><line x1="6" y1="194" x2="264" y2="194" stroke-width=".3"/>
<line x1="264" y1="110" x2="414" y2="110" stroke-width=".2"/><line x1="176" y1="194" x2="176" y2="291" stroke-width=".2"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'sheet.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), rr => rr.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
const pdf = path.join(OUT, 'the_face_is_yours_blueprint.pdf'), jpg = path.join(OUT, 'the_face_is_yours_blueprint_preview.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log(`camera eye ${m(D.cam.eye)} m · head scale ×${m(1 / r)} · sharp ${m(near)}–${m(far)} m · frame ${m(frameW)} m`);
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
