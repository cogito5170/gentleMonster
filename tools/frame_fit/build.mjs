// node tools/frame_fit/build.mjs   (runs render.py first)
// The corner frame with PH-01 inside: why it looks stretched, the shape the frame really wants, three ways to fill it
// with the applicant's own photos, and the steps. Previews come from render.py (photos laid on the walls by homography).
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const D = path.join(repo, 'docs/frame_fit'), TMP = path.join(repo, 'out/frame_fit');
fs.mkdirSync(TMP, { recursive: true });
const log = execFileSync('python3', ['tools/frame_fit/render.py'], { cwd: repo }).toString().trim(); console.log(log);
const num = re => +log.match(re)[1];
const ASPECT = num(/wall ([\d.]+):1/), PANO = num(/panorama ([\d.]+):1/), STRETCH = num(/\/ x([\d.]+) \(whole\)/);

const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff', OK = '#8fe3a8', NAVY = '#123f73';
const f = n => (+n).toFixed(2);
let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const PL = (pts, sw = .35, fill = 'none', ex = '') => o += `<polygon points="${pts.map(p => p.map(f).join(',')).join(' ')}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo s') => o += `<foreignObject x="${f(x)}" y="${f(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const IMG = (file, x, y, w, h, fit = 'meet') => { o += `<image href="${pathToFileURL(path.join(D, file)).href}" x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" preserveAspectRatio="xMidYMid ${fit}"/>`; R(x, y, w, h, .3); };
const bold = 'font-weight="700"', dim = 'class="d"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const arrow = (x, y, ang = 0, col = INK, s = 1.4) => { const a = ang * Math.PI / 180; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };
const tag = (x, y, t, col) => { const w = [...t].reduce((a, c) => a + (/[가-힣]/.test(c) ? 1.85 : 1.1), 0) + 2.4; o += `<rect x="${f(x)}" y="${f(y - 2.8)}" width="${f(w)}" height="3.7" fill="${col}" stroke="none"/>`; T(x + 1.1, y, t, 1.75, `fill="${NAVY}" ${bold}`); };
const dimH = (x1, x2, y, t) => { L(x1, y, x2, y, .15); [x1, x2].forEach(v => L(v - .6, y + .6, v + .6, y - .6, .3)); T((x1 + x2) / 2, y - 1, t, 1.5, `${dim} text-anchor="middle"`); };
const dimV = (x, y1, y2, t) => { L(x, y1, x, y2, .15); [y1, y2].forEach(v => L(x - .6, v + .6, x + .6, v - .6, .3)); T(x - 1, (y1 + y2) / 2 + .5, t, 1.5, `${dim} text-anchor="end"`); };
const FW = 1806, FH = 1008, LEFT = [[247, 330], [933, 103], [933, 862], [250, 800]], RIGHT = [[933, 103], [1617, 328], [1615, 796], [933, 862]];

// ---------- 01 NOW ----------
{ const X = 10, Y = 22, W = 120, k = W / FW, H = FH * k, p = ([u, v]) => [X + u * k, Y + v * k];
  head(X, 14, '01', 'NOW — 지금 이미지', 'the photo is squeezed sideways to fill two walls');
  IMG('current.jpg', X, Y, W, H);
  PL(LEFT.map(p), .45, 'none', `stroke="${EYE}" stroke-dasharray="1.2 .8"`); PL(RIGHT.map(p), .45, 'none', `stroke="${EYE}" stroke-dasharray="1.2 .8"`);
  const [mx, my] = p([965, 640]); C(mx, my, 4, .5, 'none', `stroke="${RED}"`); T(mx + 5, my - 3, 'fold through the man', 1.6, `${bold} fill="${RED}"`);
  const [bx, by] = p([1330, 330]); C(bx, by, 5, .5, 'none', `stroke="${RED}"`); T(bx - 4, by - 6.5, 'hotel · people too wide', 1.6, `${bold} fill="${RED}"`);
  [['사진', `PH-01 은 1.78 : 1`], ['틀', `두 벽을 펴면 ${PANO.toFixed(2)} : 1`], ['결과', `가로로 약 ${STRETCH.toFixed(1)}배 늘어남 — 사람 · 호텔이 넓적하다`], ['접힘', '모서리가 서 있는 사람을 가른다']].forEach(([a, b], i) => {
    const yy = Y + H + 5 + i * 4.4; T(X, yy, a, 1.9, `${bold} fill="${RED}"`); T(X + 10, yy, b, 1.9); });
}

// ---------- 02 GEOMETRY ----------
{ const X = 142, Y = 22; head(X, 14, '02', 'GEOMETRY — 틀이 원하는 비율', 'measured on the frame, read as a 90° corner seen head-on');
  // front view of the opening with measured sizes
  const k = .05, ox = X + 4, oy = Y + 6, p = ([u, v]) => [ox + (u - 247) * k, oy + (v - 103) * k];
  PL(LEFT.map(p), .45, 'rgba(159,211,255,.12)'); PL(RIGHT.map(p), .45, 'rgba(159,211,255,.08)'); L(...p([933, 103]), ...p([933, 862]), .5, `stroke="${EYE}"`);
  dimV(p([247, 330])[0] - 2, p([247, 330])[1], p([250, 800])[1], '470'); const [cx0, cy0] = p([933, 103]), [, cy1] = p([933, 862]);
  L(cx0 + 2, cy0, cx0 + 2, cy1, .15); T(cx0 + 3, (cy0 + cy1) / 2, '759 px', 1.5, dim); dimH(p([247, 862])[0], cx0, cy1 + 4, '686'); dimH(cx0, p([1617, 862])[0], cy1 + 4, '684');
  T(ox, cy1 + 9.5, 'front: the corner is nearer, so it is taller', 1.6, dim);
  // plan view
  const px = X + 104, py = Y + 18; L(px - 18, py + 18, px, py, .8, `stroke="${EYE}"`); L(px, py, px + 18, py + 18, .8, `stroke="${EYE}"`);
  T(px - 21, py + 6, 'wall L', 1.6, dim); T(px + 13, py + 6, 'wall R', 1.6, dim); T(px - 3, py - 2, '90°', 1.6, dim);
  C(px, py + 42, 1.4, .4, NAVY); T(px + 3, py + 43, 'viewer', 1.6); L(px, py + 40.5, px, py + 2, .25, 'stroke-dasharray="1 .8"'); arrow(px, py + 2, -90);
  T(px + 8, py + 47, 'plan: two walls at 45° to the picture', 1.6, dim);
  // unfolded
  const uy = Y + 66, uh = 12, uw = uh * PANO, ux = X + 4;
  R(ux, uy, uw / 2, uh, .45, 'rgba(159,211,255,.15)'); R(ux + uw / 2, uy, uw / 2, uh, .45, 'rgba(159,211,255,.1)');
  T(ux + uw / 4, uy + 8.5, `${ASPECT.toFixed(2)} : 1`, 2, `text-anchor="middle" ${bold}`); T(ux + uw * .75, uy + 8.5, `${ASPECT.toFixed(2)} : 1`, 2, `text-anchor="middle" ${bold}`);
  dimH(ux, ux + uw, uy - 2, `both walls unfolded  ${PANO.toFixed(2)} : 1`);
  const ph = uh, pw = ph * 1.78; R(ux + uw + 6, uy, pw, ph, .45, 'rgba(255,107,91,.15)', `stroke="${RED}"`); T(ux + uw + 6 + pw / 2, uy + 8.5, '1.78 : 1', 2, `text-anchor="middle" ${bold} fill="${RED}"`);
  T(ux + uw + 6 + pw + 1.5, uy + 7, 'PH-01', 1.6, `fill="${RED}"`);
  FO(X, uy + 15.5, 128, 10, `벽 하나는 가로가 세로의 약 ${ASPECT.toFixed(1)}배, 두 벽을 합치면 ${PANO.toFixed(1)}배다. 16:9 사진을 그대로 넣으면 가로로 늘어난다. 사진 쪽을 이 비율로 만들어야 한다 — 자르거나, 옆을 채우거나, 사진 두 장을 나란히 둔다.`);
}

// ---------- 03 OPTIONS ----------
{ const Y = 128; head(10, Y - 6, '03', 'OPTIONS — 비율을 맞추는 세 가지', 'top: the strip made from the photos · bottom: the same strip on the walls (exact plane mapping)');
  const opts = [
    ['A', 'CROP — 한 장을 띠로 자르기', 'flat_a.jpg', 'opt_a.jpg', '생성 없음. 하지만 4:1 띠라 사진의 37 % 만 남고 크게 확대돼 거칠다. 사람 아래가 잘린다', '비추천', RED],
    ['B', 'EXPAND — 한 장을 그대로, 양옆을 채우기', 'flat_b.jpg', 'opt_b.jpg', 'PH-01 을 비율 그대로 두고, 빗금 부분(바다 · 하늘 · 해안선)만 생성형 확장으로 채운다. 모서리는 사람 사이 빈 물에 온다', '추천', OK],
    ['C', 'PAIR — 사진 두 장, 벽마다 한 장', 'flat_c.jpg', 'opt_c.jpg', 'AI 없이 내 사진만. 왼쪽 PH-03 노을 카누, 오른쪽 PH-01. 수평선을 48 % 높이로 맞춰 모서리에서 만난다. 색이 바뀌는 이음이 생긴다', 'AI 없이', EYE],
  ];
  opts.forEach(([n, title, flat, warped, note, v, col], i) => {
    const x = 10 + i * 136, w = 130;
    T(x, Y + 2, n, 3.2, `${bold} fill="${col}"`); T(x + 6, Y + 2, title, 2.1, bold); tag(x + w - [...v].reduce((a, c) => a + (/[가-힣]/.test(c) ? 1.85 : 1.1), 0) - 2.4, Y + 2, v, col);
    const fh = w / PANO; IMG(flat, x, Y + 5, w, fh, 'none');
    if (n === 'B') { T(x + 2, Y + 5 + fh / 2 + .6, 'expand', 1.5, `fill="${RED}"`); T(x + w - 11, Y + 5 + fh / 2 + .6, 'expand', 1.5, `fill="${RED}"`); }
    L(x + w / 2, Y + 4, x + w / 2, Y + 6 + fh, .3, `stroke="${EYE}" stroke-dasharray=".8 .6"`);
    const ih = 49, iw = ih * 1530 / 900; IMG(warped.replace('.jpg', '_c.jpg'), x + (w - iw) / 2, Y + 8 + fh, iw, ih);
    FO(x, Y + 9 + fh + ih, w, 11, note);
  });
}

// ---------- 04 STEPS (option B) ----------
{ const X = 10, Y = 236; head(X, Y, '04', 'STEPS — B 로 만드는 순서', 'Photoshop (generative expand) or Midjourney V7 Editor (no --cw / --ow)');
  [['1', 'Crop', 'PH-01 을 위 60 px · 아래 164 px 잘라 1500 × 620 (모래를 줄인다)'],
   ['2', 'Canvas', `캔버스 2561 × 620 (${PANO.toFixed(2)} : 1), 사진을 x 400 에 — 모서리(1280)가 서 있는 사람 오른쪽 빈 물에 온다`],
   ['3', 'Expand', '빈 양옆을 생성형 확장: continue the calm evening sea, the soft clouds and the coastline with the hillside hotel, same light and grain'],
   ['4', 'Split', '가운데 1280 에서 반으로 — 왼쪽 반은 왼쪽 벽, 오른쪽 반은 오른쪽 벽'],
   ['5', 'Place', '각 반을 벽 네 귀퉁이에 맞춰 Distort: 왼쪽 247,330 · 933,103 · 933,862 · 250,800 / 오른쪽 933,103 · 1617,328 · 1615,796 · 933,862']].forEach(([n, a, b], i) => {
    const yy = Y + 9 + i * 8.6; C(X + 2.4, yy - .8, 2.2, .35, NAVY, `stroke="${OK}"`); T(X + 2.4, yy - .05, n, 1.9, `text-anchor="middle" ${bold} fill="${OK}"`);
    T(X + 7, yy, a.toUpperCase(), 1.8, bold); FO(X + 22, yy - 3.2, 248, 8.4, b); });
}

// ---------- 05 title ----------
{ const X = 290, Y = 236; L(286, 232, 286, 291, .3);
  T(X, Y + 6, 'FRAME FIT', 6.4, `${bold} letter-spacing="-.1"`); T(X, Y + 12, 'JEONG HYEOKJU — PH-01 in the corner frame', 2.5, bold);
  T(X, Y + 18, `틀은 ${PANO.toFixed(1)} : 1 을 원한다. 늘리지 말고 맞춘다.`, 2.3, bold);
  [['Photos', "PH-01 · PH-03 (applicant's own)"], ['Frame', 'current.jpg · opening measured in px'], ['Script', 'tools/frame_fit/render.py · build.mjs'], ['Note', 'B is a preview: the hatched sides are filled later']].forEach(([a, b], i) => {
    T(X, Y + 27 + i * 6, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(X + 15, Y + 27 + i * 6, b, 1.75); });
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Frame fit blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}}
.fo{font-family:${F};color:#eef4fa;font-size:2.3px;line-height:1.45;padding-top:.6px} .fo.s{font-size:1.8px;color:#dbe7f2;padding-top:1px;line-height:1.45}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="6" y1="114" x2="414" y2="114" stroke-width=".3"/><line x1="137" y1="6" x2="137" y2="114" stroke-width=".2"/>
<line x1="6" y1="229" x2="414" y2="229" stroke-width=".3"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'sheet.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(400);
const pdf = path.join(D, 'frame_fit_blueprint.pdf'), jpg = path.join(D, 'frame_fit_blueprint.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
