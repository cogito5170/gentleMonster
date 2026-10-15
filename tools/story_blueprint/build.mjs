// node tools/story_blueprint/build.mjs
// The whole ON DISPLAY story (docs/shinsegae_vmd/story_text.md) drawn as one A3 blueprint:
// the book is a store, each chapter is a zone, the reader's walk is the red line.
// Not to scale. Output: docs/shinsegae_vmd/blueprint/story_blueprint.pdf + story_blueprint_preview.jpg
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/shinsegae_vmd/blueprint');
const TMP = path.join(repo, 'out/story_blueprint');
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6';
const f = n => (+n).toFixed(2);
let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const P = (pts, sw = .25, ex = '') => o += `<polyline points="${pts.map(p => p.map(f).join(',')).join(' ')}" fill="none" stroke-width="${sw}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const dim = 'class="d"', bold = 'font-weight="700"';
const stop = (x, y, n, red = true) => { C(x, y, 2.6, .35, '#123f73', `stroke="${red ? RED : INK}"`); T(x, y + .8, n, 2, `text-anchor="middle" ${bold} fill="${red ? RED : INK}"`); };
const zone = (x, y, w, h, n, name, line, kr) => { R(x, y, w, h, .2, 'rgba(255,255,255,.03)', 'stroke-dasharray="1.2 .8"'); T(x + 2, y + 4, `${n}  ${name}`, 2.3, bold); T(x + 2, y + 7.2, line, 1.75, dim); if (kr) T(x + 2, y + 10.2, kr, 1.75, dim); };
const hatch = (x, y, w, h) => R(x, y, w, h, .2, 'url(#hatch)');
const arrow = (x, y, ang, col = RED) => { const a = ang * Math.PI / 180, s = 1.6; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };

// ================= 01 THE BOOK AS A STORE (plan, not to scale) =================
T(14, 13, '01  THE BOOK AS A STORE', 2.6, bold); T(14, 16.4, 'each chapter is a zone · the red line is the reader’s walk · not to scale', 1.9, dim);
const X0 = 16, Y0 = 24, X1 = 286, Y1 = 212;
R(X0, Y0, X1 - X0, Y1 - Y0, .6);
// street side: entrance, four windows (WINDOWS OF TIME), exit
L(X0, Y1, X1, Y1, 1.1, 'stroke="#123f73"');                                   // erase wall under openings, redraw pieces
const wall = [[X0, 42], [58, 64], [92, 96], [120, 124], [148, 152], [176, 200], [216, X1]];
wall.forEach(([a, b]) => L(a, Y1, b, Y1, .6));
[[64, 92, 'SPRING · sprout'], [96, 120, 'SUMMER · puddle'], [124, 148, 'AUTUMN · dusk'], [152, 176, 'WINTER · bulb']].forEach(([a, b, t]) => {
  L(a, Y1 - .5, b, Y1 - .5, .2); L(a, Y1 + .5, b, Y1 + .5, .2); T((a + b) / 2, Y1 + 5, t, 1.6, `text-anchor="middle" ${dim}`); });
T(140, Y1 + 13, 'WINDOWS OF TIME — the street runway', 1.8, `text-anchor="middle" ${bold}`);
T(50, Y1 + 9, 'ENTRANCE', 1.7, `text-anchor="middle" ${dim} letter-spacing=".3"`); T(203, Y1 + 9, 'EXIT', 1.7, `text-anchor="end" ${dim} letter-spacing=".3"`);
for (let i = 0; i < 7; i++) L(22 + i * 6, Y1 + 13.5, 26 + i * 6, Y1 + 13.5, .25, `stroke="${DIM}" opacity=".7"`);   // passers-by on the street
T(14, Y1 + 13.2, 'passers-by →', 1.5, dim);

// zones
zone(18, 26, 64, 28, '05–06', 'READING SHINSEGAE', 'store directory · how Shinsegae stops a walking city', '신세계는 걷는 사람을 멈추게 하는 법을 안다');
zone(18, 58, 64, 98, '03–04', 'SEE', 'the walking eye only recognises what belongs together', '걷는 눈은 어울리는 덩어리만 알아본다');
zone(18, 160, 64, 50, '01–02', 'PROLOGUE', 'clothes walk in a show · I walk in a store', '패션쇼에서는 옷이 걷는다. 매장에서는 내가 걷는다');
zone(90, 26, 92, 60, '09–10', 'STYLING', 'a mannequin never walks: a posture tells the day', '서 있는 자세 하나가 그 사람의 하루를 말한다');
zone(90, 92, 92, 82, '07–08', 'PICK', 'four reasons a step turns', '걸음은 이유 없이 꺾이지 않는다');
zone(188, 26, 96, 146, '11–16', 'PROJECT · REVERSE RUNWAY', 'mannequins sit, shoppers walk', '마네킹은 앉고, 손님이 걷는다');
zone(186, 176, 46, 34, '17', 'KEEP', 'something stays in your hand', '걸음이 끝나면 손에 무언가가 남는다');
hatch(240, 176, 44, 34); R(240, 176, 44, 34, .35); T(242, 181, '18–19  BACKSTAGE', 2.1, bold); T(242, 184.2, 'staff only · after closing', 1.7, dim); T(242, 187.2, '몇 초를 위한 밤', 1.7, dim);

// SEE: racks seen at walking speed (blur lines) and one detected cluster
for (let r = 0; r < 4; r++) for (let i = 0; i < 9; i++) L(24 + r * 14, 72 + i * 8.5, 30 + r * 14, 72 + i * 8.5, .5, `stroke="${DIM}" opacity="${.25 + .1 * (i % 3)}"`);
R(44, 104, 16, 14, .35, 'none', `stroke="${RED}"`); o += `<rect x="44" y="101" width="14" height="3" fill="${RED}" stroke="none"/>`; T(45, 103.3, 'LOOKBOOK', 1.4, `${bold} fill="#123f73"`);
['HAIR', 'EYEWEAR', 'COAT', 'COLOR', 'WATCH', 'SCENT'].forEach((t, i) => T(62, 106 + i * 2.6, t, 1.4, `fill="${RED}"`));
C(52, 111, 2.2, .3); C(48.5, 113.5, 1.2, .25); C(55.5, 113.5, 1.2, .25);
// directory board
R(24, 40, 52, 7, .3); ['2014 facade', '1935 heritage', 'light · award', 'spread'].forEach((t, i) => T(25.5 + i * 13, 44.4, t, 1.4, dim));
// prologue: the runway vs store wall panel
R(24, 176, 52, 26, .25); L(24, 189, 76, 189, .15);
R(28, 180, 20, 4, .2); for (let i = 0; i < 5; i++) { C(30 + i * 4, 178.5, .6, .15); C(30 + i * 4, 185.5, .6, .15); } L(29, 182, 46, 182, .3, `stroke="${INK}"`); arrow(47, 182, 0, INK); T(50, 183, 'show', 1.5, dim);
for (let i = 0; i < 6; i++) C(30 + i * 3.4, 194 + (i % 2) * 3, .6, .15); C(46, 199, .6, .15); C(48, 199, .6, .15); C(47, 197.4, .6, .15);
P([[29, 199], [36, 196], [41, 199.5], [45.2, 198.6]], .3, `stroke="${RED}"`); arrow(45.6, 198.4, -15); T(50, 198.5, 'store', 1.5, dim);
// PICK: four display tables, the path bends toward them
[['COLOR', 'carries', 100, 116], ['HEIGHT', 'steps', 134, 116], ['REPEAT', 'a beat of three', 100, 146], ['ONE DIFFERENT', 'one red point', 134, 146]].forEach(([a, b, x, y], i) => {
  R(x, y, 26, 16, .3); T(x + 1.5, y + 4, a, 1.7, bold); T(x + 1.5, y + 7, b, 1.5, dim);
  if (i === 0) { R(x + 3, y + 9, 4, 5, .2); R(x + 8, y + 9, 4, 5, .2); R(x + 13, y + 9, 4, 5, .2); }
  if (i === 1) { R(x + 3, y + 8, 4, 6, .2); R(x + 8, y + 10, 4, 4, .2); R(x + 13, y + 12, 4, 2, .2); }
  if (i === 2) [0, 1, 2].forEach(k => C(x + 6 + k * 6, y + 11.5, 1.6, .2));
  if (i === 3) [0, 1, 2].forEach(k => C(x + 6 + k * 6, y + 11.5, 1.6, .2, k === 1 ? RED : 'none', k === 1 ? `stroke="${RED}"` : ''));
});
T(100, 169, 'the step turns toward what belongs together', 1.6, `fill="${RED}"`);
// STYLING: five mannequins on plinths
for (let i = 0; i < 5; i++) { R(96 + i * 17, 52, 12, 12, .2); C(102 + i * 17, 58, 2.6, .3); T(102 + i * 17, 69, `LOOK 0${i + 1}`, 1.5, `text-anchor="middle" ${dim}`); }
T(96, 79, 'silhouette · colour ratio · material · accent', 1.5, dim);
// REVERSE RUNWAY: runway, tiers of seated mannequins, photo point
R(228, 44, 18, 118, .5, 'rgba(255,255,255,.08)');
for (let row = 0; row < 2; row++) {
  R(205 + row * 11, 46, 10, 114, .15); R(249 + row * 11, 46, 10, 114, .15);
  for (let k = 0; k < 11; k++) { C(210 + row * 11, 51 + k * 10.4, 1.5, .2); C(254 + row * 11, 51 + k * 10.4, 1.5, .2); }
}
[[210, 'BLACK'], [221, 'CHARCOAL'], [254, 'CHARCOAL'], [265, 'GREY']].forEach(([x, t]) => T(x, 164.5, t, 1.2, `text-anchor="middle" ${dim}`));
T(196, 100, 'seated like an audience', 1.4, `text-anchor="middle" ${dim} transform="rotate(-90 196 100)"`);
R(231, 37, 12, 5, .3); C(237, 39.5, 1.3, .25); T(237, 35.5, 'PHOTO POINT', 1.5, `text-anchor="middle" fill="${RED}" ${bold}`);
T(237, 100, 'RUNWAY', 1.6, `text-anchor="middle" ${dim} letter-spacing=".4" transform="rotate(-90 237 100)"`);

// the reader's walk
const walk = [[50, 230], [50, 207], [79, 204], [79, 190], [80, 158], [40, 140], [40, 111], [40, 85], [78, 80], [78, 56], [70, 50], [86, 60], [86, 110], [130, 110], [130, 139], [168, 139], [174, 100], [152, 74], [185, 64], [186, 170], [237, 172], [237, 46], [279, 46], [279, 172], [226, 174], [226, 196], [208, 204], [208, 230]];
P(walk, .45, `stroke="${RED}" stroke-dasharray="2 1"`);
[[40, 98, -90], [110, 110, 0], [237, 140, -90], [279, 120, 90], [208, 205, 90], [186, 120, 90]].forEach(([x, y, a]) => arrow(x, y, a));
P([[262, 174], [262, 190]], .3, `stroke="${INK}" stroke-dasharray=".6 .8"`);
stop(64, 222, '00', false); T(68, 221, 'COVER · THE STILL RUNWAY', 1.7, bold); T(68, 223.8, 'everything walks past, one stays still', 1.5, dim);
stop(79, 190, '01'); stop(40, 111, '03'); stop(70, 50, '05'); stop(130, 139, '07'); stop(152, 74, '09'); stop(237, 120, '11'); stop(237, 46, '16'); stop(226, 196, '17'); stop(262, 194, '18', false); stop(208, 218, 'BC');
T(213, 219, 'RECEIPT', 1.7, bold); T(213, 221.6, 'thank you for shopping', 1.5, dim);

// ================= 02 THE WALK (timeline) =================
T(14, 240, '02  THE WALK', 2.6, bold); T(14, 243.4, 'four verbs carry the book', 1.9, dim);
const steps = [
  ['WALK', '걷다', '00–06', 'COVER · PROLOGUE · SEE · READING', '모두 지나가는데, 하나만 가만히 있다.'],
  ['TURN', '꺾이다', '07–10', 'PICK · STYLING', '어울리는 몇 가지가 모이면 걸음이 꺾인다.'],
  ['PICK UP', '집다', '11–16', 'PROJECT · REVERSE RUNWAY', '마음에 드는 줄 앞에서 옷을 바로 집는다.'],
  ['KEEP', '챙기다', '17–BC', 'KEEP · BACKSTAGE · RECEIPT', '좋은 진열은 매장을 나선 뒤에도 따라간다.'],
];
L(16, 252, 286, 252, .35, `stroke="${RED}"`);
steps.forEach(([en, kr, pg, ch, line], i) => {
  const x = 16 + i * 67.5; C(x + 2, 252, 1.4, .3, '#123f73', `stroke="${RED}"`); if (i) arrow(x - .6, 252, 0);
  T(x + 5, 258.5, en, 3.4, `${bold} letter-spacing=".2"`); T(x + 7 + en.length * 2.6, 258.5, kr, 2.6, dim);
  T(x + 5, 263, `p. ${pg}`, 1.8, `class="m"`); T(x + 5, 266.5, ch, 1.7, dim);
  T(x + 5, 272, line, 2.1);
});
arrow(286, 252, 0);
T(14, 284, '* 꺾이는 걸음 = VMD 가 설계하는 것. 빨간색은 손님의 눈이 멈춘 곳.', 1.9, dim);

// ================= right column =================
const RX = 298;
T(RX, 26, 'STORY BLUEPRINT', 2, `${dim} letter-spacing=".5"`);
T(RX, 37, 'ON DISPLAY', 9.5, `${bold} letter-spacing="-.2"`);
T(RX, 44.5, 'JEONG HYEOKJU — visual merchandiser', 3.1, bold);
T(RX, 51, '패션쇼에서는 옷이 걷는다. 매장에서는 내가 걷는다.', 3.1, bold);
T(RX, 55.6, 'In a show the clothes walk. In a store, you do.', 2.1, dim);

// show vs store, larger
T(RX, 66, '03  SHOW / STORE', 2.6, bold);
const sx = RX, sy = 70;
R(sx, sy, 52, 36, .3); R(sx + 22, sy + 4, 8, 28, .25, 'rgba(255,255,255,.08)');
for (let k = 0; k < 6; k++) { C(sx + 17, sy + 7 + k * 4.6, .9, .2); C(sx + 35, sy + 7 + k * 4.6, .9, .2); }
L(sx + 26, sy + 30, sx + 26, sy + 8, .45); arrow(sx + 26, sy + 7, -90, INK);
T(sx, sy + 40, 'SHOW', 2.3, bold); T(sx, sy + 43.2, 'clothes walk · I sit', 1.8, dim); T(sx, sy + 46.4, '옷이 걷고, 나는 앉아 있다', 1.8, dim);
const tx = RX + 58;
R(tx, sy, 52, 36, .3);
[[6, 8], [14, 6], [22, 10], [9, 20], [18, 26], [28, 22], [42, 8], [44, 28]].forEach(([a, b]) => C(tx + a, sy + b, .9, .2));
R(tx + 33, sy + 13, 12, 9, .3, 'none', `stroke="${RED}"`); [[36, 18], [39, 16], [42, 18.5]].forEach(([a, b]) => C(tx + a, sy + b, .9, .2, INK));
P([[tx + 4, sy + 33], [tx + 12, sy + 28], [tx + 20, sy + 31], [tx + 28, sy + 24], [tx + 32, sy + 21]], .45, `stroke="${RED}"`); arrow(tx + 32.6, sy + 20.6, -40);
T(tx, sy + 40, 'STORE', 2.3, bold); T(tx, sy + 43.2, 'clothes stay · I walk', 1.8, dim); T(tx, sy + 46.4, '옷은 가만히, 내가 걷는다', 1.8, dim);

// the story in one paragraph
T(RX, 128, '04  THE STORY', 2.6, bold);
['백화점에 들어서면 수많은 옷이 한꺼번에 눈에 들어온다.', '패션쇼 같다. 그런데 패션쇼에서는 옷이 걸어 지나가고,', '나는 앉아 있다. 매장은 반대다. 옷은 가만히 있고, 내가 걷는다.',
 '걷는 동안 대부분은 스쳐 지나간다. 그러다 서로 어울리는', '몇 가지가 한자리에 모여 있으면, 그쪽으로 발걸음을 옮긴다.', '그 한 걸음을 만드는 사람이 VMD 다.',
 '이 책은 그 일을 나에게 먼저 해 본 기록이다. 나를 진열해 두었다.', '걷다가 걸음이 꺾이면, 집어 들고, 챙겨 가 주길.'].forEach((l, i) => T(RX, 134 + i * 4.3, l, 2.25));

// legend
T(RX, 178, '05  LEGEND', 2.6, bold);
L(RX, 184, RX + 10, 184, .45, `stroke="${RED}" stroke-dasharray="2 1"`); T(RX + 13, 184.7, 'the reader’s walk', 1.9);
stop(RX + 5, 190, '07'); T(RX + 13, 190.7, 'a stop = a spread (page numbers)', 1.9);
R(RX, 194.5, 10, 5, .35, 'none', `stroke="${RED}"`); T(RX + 13, 198, 'red = where the eye stops', 1.9);
R(RX, 202, 10, 5, .2, 'url(#hatch)'); T(RX + 13, 205.5, 'backstage, unseen by shoppers', 1.9);
R(RX, 210, 10, 5, .2, 'rgba(255,255,255,.03)', 'stroke-dasharray="1.2 .8"'); T(RX + 13, 213.5, 'a chapter zone', 1.9);

// title block
L(RX - 4, 222, 414, 222, .3);
[['Sheet', 'The ON DISPLAY story as one plan'], ['Scale', 'not to scale — the book drawn as a store'], ['Date', '2026-10-15'], ['Text', 'docs/shinsegae_vmd/story_text.md'],
 ['Source', 'tools/story_blueprint/build.mjs'], ['Status', 'Story draft · images to follow'], ['Note', 'Personal proposal, not affiliated with Shinsegae']].forEach(([a, t], i) => {
  T(RX, 231 + i * 7, a.toUpperCase(), 1.8, `${dim} letter-spacing=".3"`); T(RX + 16, 231 + i * 7, t, 2); });

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>ON DISPLAY story blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:#123f73} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}} .m{font-family:${MONO};fill:#dbe7f2}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern>
<pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.6" stroke="rgba(255,255,255,.4)" stroke-width=".18"/></pattern></defs>
<rect width="420" height="297" fill="#123f73" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="292" y1="6" x2="292" y2="291" stroke-width=".3"/><line x1="6" y1="233" x2="292" y2="233" stroke-width=".3"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'story.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
const pdf = path.join(OUT, 'story_blueprint.pdf'), jpg = path.join(OUT, 'story_blueprint_preview.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
