// node tools/inside_blueprint/build.mjs
// FROM THE INSIDE — the v4 story (docs/shinsegae_vmd/storyline_inside.md, paragraph A) as one image + one A3 blueprint.
// The image is made by Codex (.relay/tasks/003-from-the-inside, codex-image skill); this script only lays out the
// sheet: the image with its sentence map, two sightlines in section, the plan, the paragraph and how to shoot it.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/shinsegae_vmd/blueprint');
const TMP = path.join(repo, 'out/inside_blueprint');
const TASK = process.argv[2] || '008-combine-light-build';           // which Codex image to lay out
const IMG = path.join(repo, '.relay/tasks', TASK, 'image.png');
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

// one source for section + plan (metres). x: toward the street (glass at 0, inside < 0), y: up
const D = {
  me: { x: -2.4, eye: 1.6 },                                   // where I stand, inside the store
  combine: { x: -1.05, z: -0.7, h: 1.85 },                     // COMBINE: mannequin dressed in a combination, pinned at the back
  options: { x: -0.55, z: 0.15, top: 0.72, w: 0.75 },          //          the candidates left on a low table, one gap
  light: { x: -0.75, y: 2.95, aim: [-1.0, 1.45] },             // LIGHT: one narrow ceiling spot, a pool of light on the red point
  build: { x: -0.3, z: 0.9, plinth: 0.95 },                    // BUILD: 1:10 mock-up of this window + tape measure
  glass: { x: 0, top: 3.0, bed: 0.45 },
  stopper: { x: 0.55, z: -0.45, eye: 1.42 },                   // the one who stops in front of the combination and smiles
  lanes: [1.5, 2.4],
  curb: 3.4,
};
// where the elements sit on the Codex image (fractions of width / height) -- set after looking at the image
const SPOTF = path.join(here, `spots_${TASK}.json`);
const SPOTS = JSON.parse(fs.existsSync(SPOTF) ? fs.readFileSync(SPOTF, 'utf8') : '{}');

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff';
const f = n => (+n).toFixed(2);
let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const P = (pts, sw = .25, ex = '') => o += `<polyline points="${pts.map(p => p.map(f).join(',')).join(' ')}" fill="none" stroke-width="${sw}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const dim = 'class="d"', bold = 'font-weight="700"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const arrow = (x, y, ang, col = RED, s = 1.6) => { const a = ang * Math.PI / 180; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };
const num = (x, y, n, col = RED) => { C(x, y, 2.2, .35, '#123f73', `stroke="${col}"`); T(x, y + .75, n, 1.9, `text-anchor="middle" ${bold} fill="${col}"`); };

// the paragraph, sentence by sentence; each sentence points at something in the image
const S = [
  ['사람들은 쇼윈도를 밖에서 본다.', ''],
  ['나는 안에서 본다.', 'me'],
  ['안에서 보면 가게 이름은 거꾸로 읽히고,', 'name'],
  ['진열은 등을 보인다.', 'back'],
  ['대신 유리 너머로 사람들의 얼굴이 보인다.', 'face'],
  ['대부분은 그냥 지나간다.', 'pass'],
  ['가끔 누군가 걸음을 멈추고, 들여다보고, 웃는다.', 'face'],
  ['나는 그 사람이 무엇을 보고 웃었는지 본다.', 'bag'],
  ['진열이 맞았는지는 상품이 아니라 그 표정이 알려 주기 때문이다.', 'face'],
  ['밖에서 상품만 들여다보는 VMD가 아니라, 안에서 사람들의 표정과 반응을 살피는 VMD가 되겠다.', 'me'],
];
const KEY = { name: '1', back: '2', face: '3', pass: '4', bag: '5', me: '6' };

// ---------- 01 the image ----------
const IX = 10, IY = 21, IW = 250, IH = IW * 1024 / 1536;
head(IX, 13, '01', 'THE IMAGE — FROM THE INSIDE', `concept image, generated with Codex from .relay/tasks/${TASK} · numbers = sentences in 04`);
o += `<image href="${pathToFileURL(IMG).href}" x="${IX}" y="${IY}" width="${IW}" height="${f(IH)}" preserveAspectRatio="xMidYMid slice"/>`; R(IX, IY, IW, IH, .4);
const at = (k) => SPOTS[k] ? [IX + SPOTS[k][0] * IW, IY + SPOTS[k][1] * IH] : null;
if (SPOTS.name) { const [x, y] = at('name');   // mirrored name, as if cut in vinyl on the glass and read from inside
  o += `<text x="0" y="0" font-size="6" font-weight="700" letter-spacing="1.2" fill="rgba(255,236,200,.82)" stroke="none" text-anchor="middle" transform="translate(${f(x)} ${f(y)}) scale(-1 1)">JEONG HYEOKJU</text>`;
  o += `<text x="0" y="0" font-size="2" letter-spacing=".8" fill="rgba(255,236,200,.7)" stroke="none" text-anchor="middle" transform="translate(${f(x)} ${f(y + 4)}) scale(-1 1)">VISUAL MERCHANDISER</text>`; }
if (SPOTS.face && SPOTS.bag) { const [fx_, fy] = at('face'), [bx, by] = at('bag'); P([[fx_, fy], [bx, by]], .5, `stroke="${RED}" stroke-dasharray="1.6 1"`); arrow(bx, by, Math.atan2(by - fy, bx - fx_) * 180 / Math.PI); }
if (SPOTS.me && SPOTS.face) { const [mx, my] = at('me'), [fx_, fy] = at('face'); P([[mx, my], [fx_, fy + 2]], .5, `stroke="${EYE}" stroke-dasharray="1.6 1"`); arrow(fx_, fy + 2, Math.atan2(fy + 2 - my, fx_ - mx) * 180 / Math.PI, EYE); }
(SPOTS.tags || []).forEach(([label, u0, v0, u1, v1]) => {          // the three maker elements, boxed like product recognition
  const x = IX + u0 * IW, y = IY + v0 * IH, w = (u1 - u0) * IW, h = (v1 - v0) * IH;
  R(x, y, w, h, .5, 'none', `stroke="${RED}"`); o += `<rect x="${f(x)}" y="${f(y - 3.8)}" width="${f(label.length * 1.45 + 2)}" height="3.8" fill="${RED}" stroke="none"/>`;
  T(x + 1, y - 1, label, 2, `fill="#fff" ${bold} font-family="${MONO}"`); });
Object.entries(KEY).forEach(([k, n]) => { const p = at(k + 'Label') || at(k); if (p) num(p[0], p[1], n, k === 'me' ? EYE : RED); });
T(IX, IY + IH + 5.5, 'FROM THE INSIDE', 4.4, `${bold} letter-spacing=".2"`);
T(IX + 47, IY + IH + 5.5, '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.', 2.6);

// ---------- 02 section: two sightlines ----------
{ const k = 19, sx = 284, sy = 98, X = x => sx + (x - D.me.x + .4) * k, Y = y => sy - y * k, bed = D.glass.bed;
  head(268, 13, '02', 'TWO SIGHTLINES', 'section · approx. 1:55 · boutique ← glass → department store aisle');
  L(X(-2.9), Y(0), X(D.curb), Y(0), .4); T(X(-2.8), Y(0) + 3.4, 'STORE', 1.6, `${dim} letter-spacing=".4"`); T(X(1.2), Y(0) + 3.4, 'AISLE', 1.6, `${dim} letter-spacing=".4"`);
  L(X(-2.9), Y(3.2), X(D.curb), Y(3.2), .3, 'stroke-dasharray="2 1"'); T(X(-2.8), Y(3.2) - 1.2, 'ceiling — indoors on both sides', 1.5, dim);
  L(X(D.curb), Y(0), X(D.curb), Y(3.2), .3, `stroke="${DIM}"`); T(X(D.curb) - 1, Y(1.2), 'shop front', 1.4, `${dim} text-anchor="end"`);
  R(X(-1.5), Y(bed), 1.5 * k, bed * k, .3, 'url(#hatch)');
  L(X(0), Y(bed), X(0), Y(D.glass.top), .5); L(X(.012), Y(bed), X(.012), Y(D.glass.top), .25); T(X(0) + 1.2, Y(D.glass.top) + 2.5, 'glass', 1.6, dim);
  L(X(D.me.x), Y(0), X(D.me.x), Y(1.48), .6, `stroke="${EYE}"`); C(X(D.me.x), Y(1.62), 1.6, .4, 'none', `stroke="${EYE}"`); T(X(D.me.x) - 2, Y(1.95), 'ME', 1.8, `${bold} fill="${EYE}" text-anchor="middle"`);
  const w = D.combine.x; P([[X(w - .14), Y(bed)], [X(w - .15), Y(bed + 1.3)], [X(w), Y(bed + 1.42)], [X(w + .15), Y(bed + 1.3)], [X(w + .14), Y(bed)]], .4, `stroke="${RED}"`);
  C(X(w + .1), Y(bed + 1.25), .7, .3, RED, `stroke="${RED}"`); T(X(w) - 3, Y(bed + 1.62), 'COMBINE', 1.6, `${bold} fill="${RED}" text-anchor="middle"`);
  R(X(D.options.x - .2), Y(D.options.top), .4 * k, (D.options.top - bed) * k, .3); [0, 1, 2].forEach(i => R(X(D.options.x - .16 + i * .12), Y(D.options.top + .06), .09 * k, .06 * k, .25));
  T(X(D.options.x), Y(D.options.top) - 1.4, 'options', 1.4, `${dim} text-anchor="middle"`);
  R(X(D.light.x - .05), Y(3.2) - .2, .1 * k, .12 * k, .4, 'none', `stroke="${RED}"`); o += `<polygon points="${f(X(D.light.x))},${f(Y(D.light.y))} ${f(X(D.light.aim[0] - .17))},${f(Y(D.light.aim[1]))} ${f(X(D.light.aim[0] + .17))},${f(Y(D.light.aim[1]))}" fill="rgba(255,233,176,.18)" stroke="rgba(255,233,176,.6)" stroke-width=".2"/>`;
  T(X(D.light.x) + 2.4, Y(3.2) + 3, 'LIGHT', 1.6, `${bold} fill="${RED}"`);
  R(X(D.build.x - .1), Y(D.build.plinth), .2 * k, (D.build.plinth - bed) * k, .3); R(X(D.build.x - .09), Y(D.build.plinth + .14), .18 * k, .14 * k, .4, 'none', `stroke="${RED}"`);
  T(X(D.build.x) + 2.4, Y(D.build.plinth + .42), 'BUILD', 1.6, `${bold} fill="${RED}"`);
  P([[X(D.stopper.x + .1), Y(0)], [X(D.stopper.x + .08), Y(.95)], [X(D.stopper.x), Y(1.3)]], .6); C(X(D.stopper.x - .03), Y(D.stopper.eye), 1.5, .4);
  D.lanes.forEach(x => { L(X(x), Y(0), X(x), Y(1.62), .6, `stroke="${DIM}" opacity=".5"`); C(X(x), Y(1.72), 1.4, .3, 'none', `stroke="${DIM}" opacity=".5"`); L(X(x) - 3, Y(.8), X(x) + 3, Y(.8), .3, `stroke="${DIM}" opacity=".6"`); arrow(X(x) + 3.4, Y(.8), 0, DIM, 1.2); });
  P([[X(D.stopper.x - .05), Y(D.stopper.eye)], [X(w + .14), Y(bed + 1.25)]], .45, `stroke="${RED}" stroke-dasharray="1.6 1"`); arrow(X(w + .14) + .5, Y(bed + 1.25) + .1, 186);
  P([[X(D.me.x) + 1.6, Y(D.me.eye) - .5], [X(D.stopper.x - .08), Y(D.stopper.eye)]], .45, `stroke="${EYE}" stroke-dasharray="1.6 1"`); arrow(X(D.stopper.x - .08) - 1.6, Y(D.stopper.eye), 4, EYE);
  T(X(-2.3), Y(.55), 'my eye → their face', 1.6, `fill="${EYE}" ${bold}`); T(X(.25), Y(2.35), 'their eye → the combination', 1.6, `fill="${RED}" ${bold}`);
  const dimH = (a, b, y, t) => { L(X(a), Y(y), X(b), Y(y), .15); [a, b].forEach(v => L(X(v) - .7, Y(y) + .7, X(v) + .7, Y(y) - .7, .3)); T((X(a) + X(b)) / 2, Y(y) + 2.8, t, 1.5, `${dim} text-anchor="middle"`); };
  dimH(D.me.x, 0, -.35, `${Math.round(-D.me.x * 1000)}`); dimH(0, D.stopper.x, -.35, `${Math.round(D.stopper.x * 1000)}`);
}

// ---------- 03 plan ----------
{ const k = 14, ox = 296, oy = 158, X = x => ox + (x + 2.9) * k, Y = z => oy + z * k;
  head(268, 126, '03', 'PLAN', 'combine · light · build along the glass · approx. 1:70');
  R(X(-2.9), Y(-1.6), 2.9 * k, 3.6 * k, .3); L(X(0), Y(-1.6), X(0), Y(2), .6); T(X(-2.8), Y(-1.6) - 1.2, 'STORE', 1.6, `${dim} letter-spacing=".4"`);
  R(X(-1.5), Y(-1.4), 1.5 * k, 3.2 * k, .25, 'url(#hatch)'); T(X(-1.45), Y(1.75), 'window bed', 1.4, dim);
  C(X(D.combine.x), Y(D.combine.z), 2.4, .45, 'none', `stroke="${RED}"`); T(X(D.combine.x) - 3.3, Y(D.combine.z) + .6, 'COMBINE', 1.4, `fill="${RED}" ${bold} text-anchor="end"`);
  R(X(D.options.x - .2), Y(D.options.z - D.options.w / 2), .4 * k, D.options.w * k, .35); [0, 1, 2, 3].forEach(i => R(X(D.options.x - .14), Y(D.options.z - .32 + i * .17), .28 * k, .12 * k, .2, i === 2 ? 'none' : 'rgba(255,255,255,.12)', i === 2 ? 'stroke-dasharray=".6 .5"' : ''));
  T(X(D.options.x) + 3.5, Y(D.options.z + D.options.w / 2) + 2.6, 'options · one gap', 1.3, dim);
  C(X(D.light.x), Y(D.combine.z + .15), 1, .4, 'none', `stroke="${RED}"`); L(X(D.light.x), Y(D.combine.z + .15), X(D.combine.x), Y(D.combine.z), .3, `stroke="${RED}" stroke-dasharray=".8 .6"`); T(X(D.light.x) + 1.6, Y(D.combine.z + .15) + .5, 'LIGHT (ceiling)', 1.3, `fill="${RED}" ${bold}`);
  R(X(D.build.x - .1), Y(D.build.z - .1), .2 * k, .2 * k, .45, 'none', `stroke="${RED}"`); T(X(D.build.x) - 3, Y(D.build.z) + .6, 'BUILD', 1.4, `fill="${RED}" ${bold} text-anchor="end"`);
  C(X(D.me.x), Y(.1), 1.6, .4, 'none', `stroke="${EYE}"`); T(X(D.me.x) - 2.2, Y(.1) + 4, 'ME', 1.6, `${bold} fill="${EYE}"`);
  D.lanes.forEach((x, i) => { const y0 = i ? 1.9 : -1.5, y1 = i ? -1.5 : 1.9; L(X(x), Y(y0), X(x), Y(y1), .35, `stroke="${DIM}" stroke-dasharray="1.4 .9"`); arrow(X(x), Y(y1), i ? -90 : 90, DIM, 1.3); });
  P([[X(1.95), Y(1.9)], [X(1.6), Y(.6)], [X(D.stopper.x + .15), Y(D.stopper.z + .2)], [X(D.stopper.x), Y(D.stopper.z)]], .5, `stroke="${RED}"`); C(X(D.stopper.x), Y(D.stopper.z), 1.4, .4, 'none', `stroke="${RED}"`);
  T(X(D.stopper.x) + 2.4, Y(D.stopper.z) - 2.4, 'stops at the combination · smiles', 1.3, `fill="${RED}"`);
  P([[X(D.me.x) + 1.6, Y(.1)], [X(D.stopper.x) - 1.5, Y(D.stopper.z)]], .35, `stroke="${EYE}" stroke-dasharray="1.2 .8"`);
  L(X(D.curb), Y(-1.6), X(D.curb), Y(2), .3, `stroke="${DIM}"`); T(X(D.curb) + 1, Y(2) - 1, 'shop front', 1.4, dim); T(X(1.95), Y(2) + 3, 'AISLE', 1.4, `${dim} letter-spacing=".4" text-anchor="middle"`);
}

// ---------- 04 the paragraph, sentence → image ----------
{ const x = 10, y = 200; head(x, y, '04', 'THE STORY IN ONE IMAGE', '확정 문단(A) · 문장마다 이미지 속 자리');
  S.forEach(([s, k], i) => { const yy = y + 9 + i * 8.3; if (k) num(x + 2.5, yy - .8, KEY[k], k === 'me' ? EYE : RED); else C(x + 2.5, yy - .8, .6, .3, INK);
    o += `<foreignObject x="${x + 7}" y="${yy - 3.4}" width="${i === 9 ? 160 : 160}" height="7.5"><div xmlns="http://www.w3.org/1999/xhtml" class="fo">${s}</div></foreignObject>`; });
}
// ---------- 05 the three elements ----------
{ const x = 180, y = 200; head(x, y, '05', 'FOR SALE: THE MAKER', '상품 대신 VMD 인 나를 파는 세 요소');
  [['COMBINE · 조합하다', '여러 아이템의 합을 만든다. 코트 · 니트 · 바지 · 안경 · 시계에 빨간 스카프 한 점. 옆 테이블에는 고르고 남은 후보와 빈 한 칸 — 고른 흔적까지 보인다'],
   ['LIGHT · 비추다', '천장 스폿 하나가 조합의 빨간 한 점에 떨어진다. 무엇을 먼저 볼지 빛이 정하고, 밝은 통로 앞에서도 유리가 거울이 되지 않게 한다'],
   ['BUILD · 짓다', '이 쇼윈도의 1:10 목업과 줄자. 건축으로 익힌 감각으로, 공간에 맞게 진열한다']].forEach(([a, t], i) => {
    const yy = y + 9 + i * 15; T(x, yy, a, 2.3, `${bold} fill="${RED}"`); o += `<foreignObject x="${x}" y="${yy + 1}" width="82" height="13"><div xmlns="http://www.w3.org/1999/xhtml" class="fo s">${t}</div></foreignObject>`; });
  T(x, y + 58, '조합하고, 비추고, 짓는다.', 2.8, bold);
  T(x, y + 62, '손님이 웃는 것은 하나의 아이템이 아니라 그 합이다.', 1.9, dim);
  [['1', 'shop name, mirrored on the glass'], ['3', 'the face that stopped and smiled'], ['4', 'everyone else walks past'], ['5', 'what she smiled at: the combination']].forEach(([n, t], i) => {
    const yy = y + 70 + i * 5; num(x + 2.5, yy - .8, n); T(x + 7, yy, t, 1.75); });
}

// ---------- 06 shoot it + title block ----------
{ const x = 268, y = 214; L(x - 4, y - 4, 414, y - 4, .3);
  T(x, y + 4, 'ON DISPLAY', 7, `${bold} letter-spacing="-.1"`); T(x, y + 11, 'JEONG HYEOKJU — visual merchandiser', 3, bold);
  T(x, y + 17, '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.', 2.5, bold);
  [['Shoot', 'inside a boutique in the department store (with permission), behind the mannequin, facing the aisle'], ['Camera', 'Fujifilm, 35 mm, f/2.8, focus on the face outside, 1/250 s'],
   ['Light', 'expose for the bright aisle; keep the boutique dimmer so the glass shows faces'], ['Glass', 'name in reversed cut vinyl, read from inside'],
   ['Image', `Codex concept · .relay/tasks/${TASK}`], ['Note', 'concept; final shot with the applicant · not affiliated with Shinsegae']].forEach(([a, t], i) => {
    T(x, y + 25 + i * 5.6, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(x + 14, y + 25 + i * 5.6, t, 1.8); });
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>FROM THE INSIDE blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:#123f73} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}} .m{font-family:${MONO};fill:#dbe7f2}
.fo{font-family:${F};color:#eef4fa;font-size:2.45px;line-height:1.4;padding-top:.6px} .fo.s{font-size:1.95px;color:#dbe7f2;padding-top:1.1px}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern>
<pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.6" stroke="rgba(255,255,255,.35)" stroke-width=".18"/></pattern></defs>
<rect width="420" height="297" fill="#123f73" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="264" y1="6" x2="264" y2="291" stroke-width=".3"/><line x1="6" y1="194" x2="264" y2="194" stroke-width=".3"/>
<line x1="264" y1="121" x2="414" y2="121" stroke-width=".2"/><line x1="176" y1="194" x2="176" y2="291" stroke-width=".2"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'sheet.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
const pdf = path.join(OUT, 'from_the_inside_blueprint.pdf'), jpg = path.join(OUT, 'from_the_inside_blueprint_preview.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
