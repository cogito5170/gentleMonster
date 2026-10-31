// node tools/eyewear_blueprint/build.mjs
// The coat image turned into an eyewear campaign shot, as an A3 plan: the image as it is with the new 4:5 crop and
// what to change, a line drawing of the target, the light plan, the glasses to use, and the Gemini / Midjourney V7
// steps (docs/character/midjourney_character.md). Pictures are the user's (docs/character/eyewear); the sheet is code.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/character/eyewear'), TMP = path.join(repo, 'out/eyewear_blueprint');
fs.mkdirSync(TMP, { recursive: true });
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
const P = (d, sw = .35, fill = 'none', ex = '') => o += `<path d="${d}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo s') => o += `<foreignObject x="${f(x)}" y="${f(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const IMG = (file, x, y, w, h, fit = 'meet') => { o += `<image href="${pathToFileURL(path.join(OUT, file)).href}" x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" preserveAspectRatio="xMidYMid ${fit}"/>`; R(x, y, w, h, .35); };
const bold = 'font-weight="700"', dim = 'class="d"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const arrow = (x, y, ang = 0, col = INK, s = 1.5) => { const a = ang * Math.PI / 180; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };
const num = (x, y, n, col = RED) => { C(x, y, 2.2, .35, NAVY, `stroke="${col}"`); T(x, y + .75, n, 1.9, `text-anchor="middle" ${bold} fill="${col}"`); };
const chip = (x, y, t, col = RED) => { o += `<rect x="${f(x - 1)}" y="${f(y - 2.7)}" width="${f([...t].reduce((a, c) => a + (/[가-힣]/.test(c) ? 1.8 : 1.05), 0) + 2)}" height="3.6" fill="${NAVY}" fill-opacity=".88" stroke="none"/>`; T(x, y, t, 1.8, `${bold} fill="${col}"`); };

// the source image is 1254 x 1254; the new crop (4:5) from the top of the head to the chest
const SRC = 1254, CROP = { x: 352, y: 112, w: 464, h: 580 }, GL = { x: 488, y: 292, w: 160, h: 52 };

// ---------- 01 BEFORE ----------
{ const X = 10, Y = 22, W = 120, k = W / SRC, x = u => X + u * k, y = v => Y + v * k;
  head(X, 14, '01', 'BEFORE — 지금 이미지와 바꿀 것', 'red = change · blue dashed = new 4:5 crop');
  IMG('before.jpg', X, Y, W, W);
  R(x(CROP.x), y(CROP.y), CROP.w * k, CROP.h * k, .6, 'none', `stroke="${EYE}" stroke-dasharray="1.6 1"`); chip(x(CROP.x) + 1, y(CROP.y) - 1.6, 'crop 4:5', EYE);
  R(x(GL.x), y(GL.y), GL.w * k, GL.h * k, .5, 'none', `stroke="${RED}"`); num(x(GL.x + GL.w) + 4, y(GL.y) + 2, '1');
  R(x(20), y(20), 105 * k, 85 * k, .5, 'none', `stroke="${RED}"`); num(x(130) + 3, y(60), '2');
  R(x(0), y(380), 260 * k, 560 * k, .4, 'none', `stroke="${RED}" stroke-dasharray="1 .7"`); R(x(1000), y(380), 254 * k, 560 * k, .4, 'none', `stroke="${RED}" stroke-dasharray="1 .7"`); num(x(130), y(960), '3');
  [['1', '안경을 씌운다 — 셀카의 회색 반투명 사각 뿔테 (04)'], ['2', "왼쪽 위 'AI' 표시를 지운다"], ['3', '양옆의 흐린 사람 그림자를 지우고 깨끗한 배경으로'],
   ['', '그대로: 얼굴 · 머리 · 적갈색 코트 · 검정 하이넥']].forEach(([n, t], i) => { const yy = Y + W + 6 + i * 4.6; if (n) num(X + 2.2, yy - .8, n); else C(X + 2.2, yy - .8, .7, .3, OK, `stroke="${OK}"`); T(X + 6.5, yy, t, 1.9); });
}

// ---------- 02 AFTER (line drawing of the target) ----------
{ const X = 140, Y = 22, W = 96, H = 120, cx = X + W / 2;
  head(X, 14, '02', 'AFTER — 아이웨어 화보', 'line drawing · 4:5 · the frame is the sharpest thing in the picture');
  R(X, Y, W, H, .45, 'rgba(255,255,255,.07)');
  for (let i = 0; i < 12; i++) R(X, Y + i * H / 12, W, H / 12, 0, `rgba(255,255,255,${(.01 * i).toFixed(3)})`, 'stroke="none"');   // soft backdrop gradient
  // coat + shoulders
  P(`M${f(X + 4)} ${f(Y + H)} L${f(X + 10)} ${f(Y + 92)} Q${f(cx - 22)} ${f(Y + 80)} ${f(cx - 9)} ${f(Y + 79)} L${f(cx + 9)} ${f(Y + 79)} Q${f(cx + 24)} ${f(Y + 80)} ${f(X + W - 8)} ${f(Y + 93)} L${f(X + W - 3)} ${f(Y + H)} Z`, .4, 'rgba(255,107,91,.18)');
  P(`M${f(cx - 9)} ${f(Y + 79)} L${f(cx - 15)} ${f(Y + H)} M${f(cx + 9)} ${f(Y + 79)} L${f(cx + 18)} ${f(Y + H)}`, .35);
  P(`M${f(cx - 8)} ${f(Y + 79)} Q${f(cx)} ${f(Y + 83)} ${f(cx + 8)} ${f(Y + 79)} L${f(cx + 9)} ${f(Y + H)} L${f(cx - 8)} ${f(Y + H)} Z`, .3, 'rgba(0,0,0,.35)');
  T(X + 7, Y + H - 4, 'rust wool coat · black high neck (kept)', 1.5, dim);
  // neck, face, hair
  R(cx - 6, Y + 66, 12, 14, .35, 'rgba(255,255,255,.08)');
  o += `<ellipse cx="${f(cx - 1)}" cy="${f(Y + 48)}" rx="15" ry="20" stroke-width=".45" fill="rgba(255,255,255,.1)"/>`;
  P(`M${f(cx - 17)} ${f(Y + 44)} Q${f(cx - 19)} ${f(Y + 20)} ${f(cx)} ${f(Y + 19)} Q${f(cx + 18)} ${f(Y + 20)} ${f(cx + 15)} ${f(Y + 42)} Q${f(cx + 4)} ${f(Y + 28)} ${f(cx - 17)} ${f(Y + 44)} Z`, .4, 'rgba(0,0,0,.45)');
  [[-6, 14], [2, 12], [9, 15]].forEach(([dx, dy]) => P(`M${f(cx + dx)} ${f(Y + 20)} q${f(dx / 3)} ${f(-dy / 3)} ${f(dx / 2 + 2)} ${f(-dy / 2)}`, .2));
  P(`M${f(cx - 6)} ${f(Y + 60)} Q${f(cx - 1)} ${f(Y + 62)} ${f(cx + 4)} ${f(Y + 60)}`, .35); L(cx - 1, Y + 48, cx - 2.5, Y + 55, .3);
  // the glasses: the hero
  const gy = Y + 45; [[-10.5, 9], [8.5, 9]].forEach(([dx]) => o += `<rect x="${f(cx + dx - 7)}" y="${f(gy - 4.2)}" width="14" height="8.4" rx="2.4" stroke-width="1.1" stroke="${EYE}" fill="rgba(159,211,255,.18)"/>`);
  L(cx - 3.5, gy - 1, cx + 1.5, gy - 1, .9, `stroke="${EYE}"`); L(cx - 17.5, gy - 2, cx - 20, gy - 1, .8, `stroke="${EYE}"`); L(cx + 15.5, gy - 2, cx + 17, gy - 1, .8, `stroke="${EYE}"`);
  L(cx - 14, gy - 3.6, cx - 8, gy - 3.6, .35, 'stroke="#fff"'); L(cx + 5, gy - 3.6, cx + 11, gy - 3.6, .35, 'stroke="#fff"');           // rim highlights
  C(cx - 10.5, gy + .3, 1, .3, '#0b2c52'); C(cx + 8.5, gy + .3, 1, .3, '#0b2c52');                                             // eyes visible
  [[cx - 21, gy - 6], [cx + 18.5, gy - 6]].forEach(([a, b]) => C(a, b, .5, .2, '#d9dde2', 'stroke="none"'));
  // focus marks
  [[cx - 25, gy - 9], [cx + 23, gy - 9], [cx - 25, gy + 8], [cx + 23, gy + 8]].forEach(([a, b], i) => { const sx = i % 2 ? -1 : 1, sy = i < 2 ? 1 : -1; L(a, b, a + 3 * sx, b, .5, `stroke="${RED}"`); L(a, b, a, b + 3 * sy, .5, `stroke="${RED}"`); });
  chip(X + W + 2, gy - 6, 'FOCUS — frame, razor sharp'); chip(X + W + 2, gy - 1.5, 'clean highlight on rims', EYE); chip(X + W + 2, gy + 3, 'eyes visible through lenses', EYE);
  chip(X + W + 2, Y + 24, 'face turned slightly left', DIM); chip(X + W + 2, Y + 28.5, 'eyes into the lens', DIM); chip(X + W + 2, Y + 66, 'face · hair unchanged', OK);
  chip(X + W + 2, Y + 8, 'warm off-white backdrop', DIM); chip(X + W + 2, Y + 12.5, 'soft gradient, no people', DIM);
  L(X - 2, Y, X - 2, Y + H, .15); T(X - 3, Y + H / 2, '5', 1.6, `${dim} text-anchor="end"`); L(X, Y + H + 2, X + W, Y + H + 2, .15); T(X + W / 2, Y + H + 5, '4', 1.6, `${dim} text-anchor="middle"`);
}

// ---------- 03 LIGHT PLAN ----------
{ const X = 282, Y = 22; head(X, 14, '03', 'LIGHT — 빛과 카메라 (평면)', 'what the prompt describes, as a studio plan');
  const ox = X + 62, oy = Y + 46;
  P(`M${f(X + 12)} ${f(Y + 8)} Q${f(ox)} ${f(Y + 2)} ${f(X + 112)} ${f(Y + 8)}`, 1.2, 'none', `stroke="${DIM}"`); T(ox, Y + 12, 'off-white backdrop · soft gradient', 1.6, `${dim} text-anchor="middle"`);
  C(ox, oy, 4, .45, 'rgba(255,255,255,.12)'); T(ox + 5.5, oy + .6, 'model', 1.7);
  R(ox - 34, oy + 10, 14, 4, .45, 'rgba(255,236,200,.35)', 'transform="rotate(-35 ' + f(ox - 27) + ' ' + f(oy + 12) + ')"'); T(ox - 48, oy + 22, 'KEY · large softbox, front left', 1.6, `fill="#ffe2b8"`);
  [0, 1, 2].forEach(i => L(ox - 20 + i * 1.5, oy + 8 - i * 1.5, ox - 6, oy + 2, .25, 'stroke="#ffe2b8" stroke-dasharray="1 .8"'));
  R(ox + 14, oy - 22, 4, 9, .45, 'rgba(159,211,255,.35)'); T(ox + 20, oy - 17, 'RIM · behind right', 1.6, `fill="${EYE}"`); L(ox + 14, oy - 14, ox + 3, oy - 3, .25, `stroke="${EYE}" stroke-dasharray="1 .8"`);
  R(ox - 3, oy + 38, 6, 4, .45, NAVY, `stroke="${INK}"`); P(`M${f(ox - 9)} ${f(oy + 30)} L${f(ox)} ${f(oy + 38)} L${f(ox + 9)} ${f(oy + 30)}`, .25, 'none', 'stroke-dasharray="1 .8"');
  T(ox + 5, oy + 44, 'CAMERA · 85 mm · eye level', 1.6); L(ox, oy + 38, ox, oy + 5, .3, 'stroke-dasharray="1.2 .8"'); arrow(ox, oy + 5, -90);
  R(ox - 30, oy - 6, 9, 3, .35, 'rgba(255,255,255,.25)'); T(ox - 44, oy - 8, 'white card · fills shadow under the frame', 1.4, dim);
  [['Lens', '85 mm · shallow depth of field, focus on the front of the frame'], ['Key', 'large soft light front left · soft shadow under the frame on the cheeks'],
   ['Rim', 'gentle light from behind right · separates hair and shoulders from the backdrop'], ['Finish', 'natural skin texture · subtle film grain · no text, no logo']].forEach(([a, b], i) => {
    T(X, Y + 98 + i * 6.2, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(X + 13, Y + 98 + i * 6.2, b, 1.75); });
}

// ---------- 04 THE GLASSES ----------
{ const X = 10, Y = 176; head(X, Y, '04', 'GLASSES — 씌울 안경', "from the applicant's own selfie · Gemini takes only the glasses from it");
  IMG('glasses_ref.jpg', X, Y + 6, 90, 33.6);
  [['Frame', 'grey translucent acetate · soft rectangle · medium-thick rims'], ['Detail', 'small silver rivets at the front corners'], ['Lens', 'clear, faint lavender reflection'],
   ['Not', 'sunglasses · oval frames · tortoiseshell']].forEach(([a, b], i) => { T(X + 95, Y + 10 + i * 7, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); FO(X + 108, Y + 7.2 + i * 7, 60, 7, b); });
}

// ---------- 05 STEPS ----------
{ const X = 10, Y = 224; head(X, Y, '05', 'STEPS — 만드는 순서', 'prompts: docs/character/midjourney_character.md · "코트 이미지를 아이웨어 모델 화보로"');
  [['1', 'Gemini', '첨부 1 코트 이미지 · 2 안경 셀카 → 프롬프트 붙여 넣기 (얼굴 · 코트 유지, 안경만 가져오기, 4:5 크롭, 스튜디오 빛)', OK],
   ['2', 'Gemini 이어서', '얼굴이 바뀜 → 얼굴 되돌리기 · 안경이 다름 → 셀카 안경 그대로 · 안경이 약함 → 더 가깝게, 테에 하이라이트', OK],
   ['3', 'Midjourney V7', '대안: 이미지 프롬프트 face_crop.jpg · --iw 3 · --style raw · --stylize 30 · --cw · --ow 없음 · Weird · Chaos 0', EYE],
   ['4', 'Photoshop', '얼굴이 끝까지 다르면 원본 얼굴을 얹고 커브 · 그레인으로 빛을 맞춘다', EYE]].forEach(([n, a, b, c], i) => {
    const yy = Y + 10 + i * 13; num(X + 2.4, yy - .8, n, c); T(X + 7, yy, a, 2.1, bold); FO(X + 33, yy - 3.2, 215, 12, b); });
}

// ---------- 06 title ----------
{ const X = 282, Y = 176; L(278, 172, 278, 291, .3);
  T(X, Y + 6, 'EYEWEAR CAMPAIGN', 6.2, `${bold} letter-spacing="-.1"`); T(X, Y + 12, 'JEONG HYEOKJU — coat image as an eyewear model shot', 2.5, bold);
  T(X, Y + 18, '얼굴은 그대로, 안경이 주인공.', 2.4, bold);
  [['Source', 'coat image (AI, earlier work) · selfie for the glasses'], ['Tool', 'Gemini (recommended) · Midjourney V7 (alternative)'],
   ['Crop', `4:5 · head top to chest · source px ${CROP.x},${CROP.y} ${CROP.w}×${CROP.h}`], ['Status', 'plan · no result yet'],
   ['Note', 'label the result as an AI image based on the applicant · not affiliated with any eyewear brand']].forEach(([a, b], i) => {
    T(X, Y + 28 + i * 7, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); FO(X + 15, Y + 25.2 + i * 7, 112, 7, b); });
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Eyewear campaign blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}}
.fo{font-family:${F};color:#eef4fa;font-size:2.3px;line-height:1.45;padding-top:.6px} .fo.s{font-size:1.8px;color:#dbe7f2;padding-top:1px;line-height:1.45}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="6" y1="168" x2="414" y2="168" stroke-width=".3"/><line x1="135" y1="6" x2="135" y2="168" stroke-width=".2"/>
<line x1="278" y1="6" x2="278" y2="168" stroke-width=".2"/><line x1="6" y1="218" x2="278" y2="218" stroke-width=".2"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'sheet.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(400);
const pdf = path.join(OUT, 'eyewear_campaign_blueprint.pdf'), jpg = path.join(OUT, 'eyewear_campaign_blueprint.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
