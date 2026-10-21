// node tools/prologue_preview/build.mjs [task]
// Prologue preview for the JAJU book: PH-08 in one colour on the left page, the Prologue text on the right, shown as a
// hand-held open book. Steps: tone.py (re-colour the photo) -> spread.mjs (flat spread) -> composite.py (lay the spread
// on the Codex mock-up .relay/tasks/<task>) -> this A3 sheet: preview, flat spread with sizes, tone, place in the book,
// how to shoot the real one.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { SP } from './spread.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const TASK = process.argv[2] || '011-prologue-book-mockup';
const TMP = path.join(repo, 'out/prologue_preview'), OUT = path.join(repo, 'docs/jaju_rounding_vmd/prologue_preview');
const run = (cmd, args) => execFileSync(cmd, args, { cwd: repo, stdio: ['ignore', 'pipe', 'inherit'] }).toString().trim();
console.log(run('python3', ['tools/prologue_preview/tone.py']));
console.log(run('node', ['tools/prologue_preview/spread.mjs']));
const PREVIEW = path.join(OUT, 'prologue_preview.jpg');
console.log(run('python3', ['tools/prologue_preview/composite.py', `.relay/tasks/${TASK}/image.png`, `tools/prologue_preview/corners_${TASK}.json`, PREVIEW]));

const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff', NAVY = '#123f73';
const f = n => (+n).toFixed(2);
let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo') => o += `<foreignObject x="${f(x)}" y="${f(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const IMG = (file, x, y, w, h) => o += `<image href="${pathToFileURL(file).href}" x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" preserveAspectRatio="xMidYMid slice"/>`;
const dim = 'class="d"', bold = 'font-weight="700"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const arrow = (x, y, ang, col = INK, s = 1.5) => { const a = ang * Math.PI / 180; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };
const dimH = (x1, x2, y, t) => { L(x1, y, x2, y, .15); [x1, x2].forEach(v => L(v - .6, y + .6, v + .6, y - .6, .3)); T((x1 + x2) / 2, y - 1, t, 1.5, `${dim} text-anchor="middle"`); };
const dimV = (x, y1, y2, t) => { L(x, y1, x, y2, .15); [y1, y2].forEach(v => L(x - .6, v + .6, x + .6, v - .6, .3)); T(x - 1, (y1 + y2) / 2, t, 1.5, `${dim} text-anchor="end"`); };

// ---------- 01 preview ----------
{ const X = 10, Y = 21, W = 250, H = W * 1024 / 1536;
  head(X, 13, '01', 'PREVIEW — 펼친 책 속의 Prologue', `Codex mock-up .relay/tasks/${TASK} + the flat spread (02) laid onto its pages · preview, not the final photo`);
  IMG(PREVIEW, X, Y, W, H); R(X, Y, W, H, .4);
  const tag = (u, v, t, col = RED) => { const x = X + u * W, y = Y + v * H; o += `<rect x="${f(x - 1)}" y="${f(y - 2.8)}" width="${f(t.length * 1.05 + 2)}" height="3.7" fill="${NAVY}" fill-opacity=".9" stroke="none"/>`; T(x, y, t, 1.9, `${bold} fill="${col}"`); };
  tag(.07, .63, 'PH-08 · one colour, red kept'); tag(.58, .43, 'Prologue — the B6 text, unchanged', EYE); tag(.04, .975, 'thumb stays in front of the page', DIM);
}

// ---------- 02 the flat spread ----------
{ const X = 276, Y = 27, W = 122, k = W / SP.w, H = SP.h * k;
  head(268, 13, '02', 'SPREAD — A4 가로 = A5 두 쪽', `${SP.w} × ${SP.h} mm · fold at ${SP.gutter} mm · the JAJU book's page`);
  IMG(path.join(TMP, 'spread.png'), X, Y, W, H); R(X, Y, W, H, .35);
  L(X + SP.gutter * k, Y - 1.5, X + SP.gutter * k, Y + H + 1.5, .35, `stroke="${EYE}" stroke-dasharray="1.2 .8"`); T(X + SP.gutter * k + 1, Y + H + 3.2, 'fold', 1.5, `fill="${EYE}"`);
  R(X, Y, SP.gutter * k, SP.photo.h * k, .45, 'none', `stroke="${RED}" stroke-dasharray="1.2 .7"`);
  R(X + SP.text.x * k, Y + (SP.text.y - 1) * k, SP.text.w * k, 72 * k, .35, 'none', `stroke="${EYE}" stroke-dasharray="1 .7"`);
  dimH(X, X + W, Y - 2.5, `${SP.w}`); dimV(X - 2, Y, Y + H, `${SP.h}`); dimV(X - 2, Y, Y + SP.photo.h * k, '');
  T(268, Y + H + 7, `<tspan fill="${RED}">red</tspan>  photo ${SP.gutter} × ${SP.photo.h} mm, bleeds off the top, the outer edge and the fold · name and PROLOGUE on the outer edge`, 1.6, dim);
  T(268, Y + H + 10, `<tspan fill="${EYE}">blue</tspan>  text ${SP.text.w} mm from x ${SP.text.x} · Prologue. Lora italic, olive · 국문 10.6 pt · English 8.4 pt`, 1.6, dim);
}

// ---------- 03 tone ----------
{ const x = 268, y = 132; head(x, y, '03', 'TONE — 한 색으로, 빨강만 남긴다', 'tools/prologue_preview/tone.py · the photo is re-coloured, nothing is drawn');
  const w = 58, h = w * 843 / 1500;
  IMG(path.join(repo, 'docs/jaju_rounding_vmd/assets/photo/PH-08.jpg'), x, y + 6, w, h); R(x, y + 6, w, h, .3); T(x, y + 6 + h + 3, 'PH-08 as shot', 1.6, dim);
  L(x + w + 3, y + 6 + h / 2, x + w + 11, y + 6 + h / 2, .4); arrow(x + w + 11.5, y + 6 + h / 2, 0);
  IMG(path.join(TMP, 'ph08_tone.jpg'), x + w + 14, y + 6, w, h); R(x + w + 14, y + 6, w, h, .3); T(x + w + 14, y + 6 + h + 3, 'olive ramp · red signal + red shopfront kept', 1.6, dim);
  [['#0f1407', 'shadow'], ['#2f3a14', 'dark olive'], ['#7d8a45', 'olive'], ['#eef0dc', 'paper'], ['#c8322b', 'red · only the signal']].forEach(([c, t], i) => {
    const sx = x + i * 27; R(sx, y + 46, 7, 5, .2, c); T(sx + 8.5, y + 49.5, c, 1.5, `font-family="${MONO}"`); T(sx + 8.5, y + 52, t, 1.4, dim); });
}

// ---------- 04 place in the book ----------
{ const x = 10, y = 202; head(x, y, '04', 'FLOW — 책 속의 자리', 'B6 (claude/magical-bell-u02os9) · the Prologue gets the image it was planned with');
  const w = 50, h = w * 210 / 297, ref = n => path.join(OUT, 'ref', n);
  [[ref('b6_01_cover.jpg'), 'Cover · From the Inside', '안에서 본 유리'], [path.join(TMP, 'spread.png'), 'Prologue. — this', '밖에서 본 밤의 진열창'], [ref('b6_03_observe.jpg'), '/01 Observe.', '틈 너머의 사람들']].forEach(([img, a, b], i) => {
    const sx = x + i * (w + 9); IMG(img, sx, y + 7, w, h); R(sx, y + 7, w, h, i === 1 ? .6 : .3, 'none', i === 1 ? `stroke="${RED}"` : '');
    T(sx, y + 7 + h + 3.5, a, 1.9, `${bold} ${i === 1 ? `fill="${RED}"` : ''}`); T(sx, y + 7 + h + 6.6, b, 1.75, dim);
    if (i < 2) { L(sx + w + 1.5, y + 7 + h / 2, sx + w + 7, y + 7 + h / 2, .35); arrow(sx + w + 7.5, y + 7 + h / 2, 0); } });
  FO(x, y + 55, 170, 30, 'Prologue 의 첫 문장은 "밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다." 표지는 안에서 본 유리, Prologue 는 <b>밖에서 본 밤의 진열창</b> — 불빛만 있고 사람은 없다. 다음 쪽 Observe 에서 틈 너머의 사람들이 보인다. 빨간 신호등은 표지의 스카프와 이어지는 빨간 한 점이다.', 'fo s');
}

// ---------- 05 how to shoot the real one ----------
{ const x = 186, y = 202; head(x, y, '05', 'SHOOT — 실제 사진으로', 'the preview is a composite; the final is a photograph of the printed page');
  [['Print', 'Prologue 펼침면만 A4 가로로 인쇄 · 무광 160–190 g · 반으로 접는다'],
   ['Hold', '왼손 엄지로 왼쪽 쪽 아래를 잡는다 · 책을 30° 기울여 가운데 골이 대각선'],
   ['Light', '창가 옆 빛 + 올리브 천 · 초록 반사판 (장면 전체에 초록이 돈다)'],
   ['Camera', 'Fujifilm XF35mm f/2 · f/2.8 · 사진 쪽에 초점, 오른쪽 끝은 흐리게'],
   ['Check', '빨간 신호등이 또렷하고, 오른쪽 글의 첫 줄이 읽힌다']].forEach(([a, t], i) => {
    T(x, y + 10 + i * 7.6, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); FO(x + 13, y + 7.2 + i * 7.6, 62, 7.4, t, 'fo s'); });
}

// ---------- 06 title ----------
{ const x = 268, y = 236; L(264, y - 4, 414, y - 4, .3);
  T(x, y + 5, 'PROLOGUE, OPEN', 6.4, `${bold} letter-spacing="-.1"`); T(x, y + 11, 'JEONG HYEOKJU — JAJU rounding VMD portfolio', 2.8, bold);
  T(x, y + 17, '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.', 2.3, bold);
  [['Photo', 'PH-08 · applicant\'s own photo, re-coloured only'], ['Mock-up', `Codex .relay/tasks/${TASK} · hand and book are generated`],
   ['Warp', 'mesh per page · the curl is approximate'], ['Files', 'prologue_spread.pdf (flat) · prologue_preview.jpg']].forEach(([a, t], i) => {
    T(x, y + 25 + i * 6, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(x + 15, y + 25 + i * 6, t, 1.75); });
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Prologue preview blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}}
.fo{font-family:${F};color:#eef4fa;font-size:2.35px;line-height:1.45;padding-top:.6px} .fo.s{font-size:1.9px;color:#dbe7f2;padding-top:1.1px} .fo b{color:${RED}}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="264" y1="6" x2="264" y2="291" stroke-width=".3"/><line x1="6" y1="194" x2="264" y2="194" stroke-width=".3"/>
<line x1="264" y1="124" x2="414" y2="124" stroke-width=".2"/><line x1="181" y1="194" x2="181" y2="291" stroke-width=".2"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'sheet.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(400);
const pdf = path.join(OUT, 'prologue_preview_blueprint.pdf'), jpg = path.join(OUT, 'prologue_preview_blueprint.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
