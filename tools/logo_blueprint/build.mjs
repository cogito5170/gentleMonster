// node tools/logo_blueprint/build.mjs
// "The crown shines" logo: the user's sketch, the three Codex options (.relay/tasks/012-014), each shown large, on
// white and on orange, at small sizes, with its idea; plus the shared rules (colour, circle, clear space).
// The logos are Codex images; this script only lays out the A3 sheet.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/logo_crown'), TMP = path.join(repo, 'out/logo_blueprint');
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const ORANGE = '#D9480F';
const OPTS = [
  { k: 'A', task: '012-logo-crown-shine-a', name: '면 · Solid', idea: '스케치를 가장 충실하게. 주황 원 안 흰 마크 — 물결 셋의 그릇 왕관, 보석 점 셋, 빛줄기 셋', good: '작은 크기에서 가장 잘 읽힌다 · 앱 아이콘 · 스탬프', care: '빛줄기 셋이 왕관 봉우리와 줄을 맞춰야 한다' },
  { k: 'B', task: '013-logo-crown-shine-b', name: '선 · Line', idea: '주황 테두리 + 같은 굵기의 선. 봉우리 셋 왕관 윤곽, 보석, 부채꼴 빛줄기 다섯', good: '가볍고 정돈된 인상 · 인쇄물 · 패턴 반복', care: '16–24 px 에서는 선이 뭉친다 — 작은 크기용은 A' },
  { k: 'C', task: '014-logo-crown-shine-c', name: '해 뜨는 왕관 · Rising', idea: '아래 반원 왕관이 떠오르는 해처럼, 위로 빛줄기 일곱이 후광처럼', good: "'빛나다'가 가장 강하다 · 포스터 · 굿즈", care: '해돋이로만 읽히지 않게 물결 셋이 분명해야 한다' },
];
const IMG = t => path.join(repo, '.relay/tasks', t, 'image.png');
const SKETCH = path.join(OUT, 'sketch.png');

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono',monospace";
const INK = '#f4f8fb', DIM = '#bcd2e6', NAVY = '#123f73', OK = '#8fe3a8', RED = '#ff6b5b';
const fx = n => (+n).toFixed(2); let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${fx(x1)}" y1="${fx(y1)}" x2="${fx(x2)}" y2="${fx(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${fx(x)}" y="${fx(y)}" width="${fx(w)}" height="${fx(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${fx(x)}" cy="${fx(y)}" r="${fx(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${fx(x)}" y="${fx(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo s') => o += `<foreignObject x="${fx(x)}" y="${fx(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const PIC = (file, x, y, w, h, ex = '') => { if (fs.existsSync(file)) o += `<image href="${pathToFileURL(file).href}" x="${fx(x)}" y="${fx(y)}" width="${fx(w)}" height="${fx(h)}" preserveAspectRatio="xMidYMid meet" ${ex}/>`;
  else { R(x, y, w, h, .3, 'none', 'stroke-dasharray="1 .8"'); T(x + w / 2, y + h / 2, 'waiting for Codex', 1.8, `class="d" text-anchor="middle"`); } };
const bold = 'font-weight="700"', dim = 'class="d"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };

// 00 sketch + concept
{ const X = 10, Y = 22; head(X, 14, '00', 'SKETCH — 출발점', "the user's sketch · 왕관이 빛나다");
  R(X, Y, 56, 50, .1, '#000', 'stroke="none"'); PIC(SKETCH, X, Y, 56, 50); R(X, Y, 56, 50, .3);
  [['아래', '그릇 모양 왕관 — 윗선의 봉긋한 물결 셋'], ['점', '물결 위의 보석 셋'], ['위', '위로 퍼지는 빛줄기 셋 = 빛나다'], ['틀', '원 안에 들어간다'], ['색', `진한 주황 ${ORANGE} + 흰색`]].forEach(([a, b], i) => {
    T(X + 61, Y + 5 + i * 6.4, a, 1.9, `${bold} fill="${OK}"`); T(X + 70, Y + 5 + i * 6.4, b, 1.9); });
  R(X + 61, Y + 36, 10, 10, .2, ORANGE, 'stroke="none"'); T(X + 73, Y + 40, ORANGE, 2, `font-family="${MONO}"`); T(X + 73, Y + 44, 'deep orange · RGB 217 72 15', 1.6, dim);
  R(X + 105, Y + 36, 10, 10, .2, '#fff', 'stroke="none"'); T(X + 117, Y + 40, '#FFFFFF', 2, `font-family="${MONO}"`);
}
// rules
{ const X = 150, Y = 22; head(X, 14, '', 'RULES — 세 안 공통', 'circle · clear space · minimum size');
  const cx = X + 22, cy = Y + 24, r = 18; C(cx, cy, r + 5, .3, 'none', 'stroke-dasharray="1 .8"'); C(cx, cy, r, .5, ORANGE, 'stroke="none"');
  C(cx, cy, r * .62, .3, 'none', 'stroke="#fff" stroke-dasharray=".8 .6"'); T(cx, cy + 1, 'mark 62 %', 1.6, 'text-anchor="middle" fill="#fff"');
  T(cx - r - 2, cy + r + 13, 'clear space = 1/4 of the radius', 1.6, dim); L(cx + r, cy, cx + r + 5, cy, .3); T(cx, cy + r + 9, 'circle Ø = 1', 1.6, `${dim} text-anchor="middle"`);
  [['원 안', '마크는 지름의 약 60 % · 중심에서 살짝 아래 (빛줄기가 위 여백을 쓴다)'], ['여백', '원 바깥으로 반지름의 1/4 은 비운다'], ['최소', '화면 24 px · 인쇄 8 mm (B 안은 12 mm)'], ['반전', '흰 바탕엔 주황 원 · 주황 바탕엔 흰 원 + 주황 마크'], ['금지', '그라데이션 · 그림자 · 다른 색 · 원을 찌그러뜨리기']].forEach(([a, b], i) => {
    T(X + 50, Y + 5 + i * 6.4, a, 1.9, `${bold} fill="${OK}"`); FO(X + 60, Y + 1.8 + i * 6.4, 130, 7, b); });
}

// 01-03 options
OPTS.forEach((op, i) => {
  const X = 10 + i * 136, Y = 92, img = IMG(op.task);
  head(X, Y, `0${i + 1}`, `${op.k} — ${op.name}`, `Codex · .relay/tasks/${op.task}`);
  R(X, Y + 6, 130, 84, .1, '#fff', 'stroke="none"'); PIC(img, X + 23, Y + 6, 84, 84); R(X, Y + 6, 130, 84, .35);
  // on orange + small sizes
  const sy = Y + 95; R(X, sy, 40, 40, .1, ORANGE, 'stroke="none"'); PIC(img, X + 4, sy + 4, 32, 32, 'style="mix-blend-mode:normal"'); T(X, sy + 44, 'on orange', 1.6, dim);
  R(X + 44, sy, 86, 40, .1, '#fff', 'stroke="none"');
  [[24, 8], [14, 34], [8, 54], [5, 68]].forEach(([s, ox]) => { PIC(img, X + 44 + ox, sy + 20 - s / 2, s, s); });
  T(X + 44, sy + 44, 'sizes  ≈ 96 · 56 · 32 · 20 px', 1.6, dim);
  FO(X, sy + 47, 130, 9, `<b>생각</b> ${op.idea}`);
  FO(X, sy + 56, 130, 7, `<b>강점</b> ${op.good}`);
  FO(X, sy + 63, 130, 7, `<b>주의</b> ${op.care}`, 'fo s r');
});

// title
{ const X = 10, Y = 270; L(6, Y - 4, 414, Y - 4, .3);
  T(X, Y + 5, 'THE CROWN SHINES', 6.4, `${bold} letter-spacing="-.1"`); T(X + 82, Y + 5, '왕관이 빛나다 — 원형 심볼 로고 세 안', 2.6, bold);
  T(X, Y + 12, 'logos generated with Codex from short specs (.relay/tasks/012–014) · vector redraw (Illustrator) recommended before use · check trademark before registering', 1.6, dim);
  T(X + 300, Y + 5, 'docs/logo_crown · tools/logo_blueprint/build.mjs', 1.6, dim);
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Logo blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}}
.fo{font-family:${F};color:#eef4fa;font-size:2.3px;line-height:1.45;padding-top:.6px} .fo.s{font-size:1.9px;color:#dbe7f2;padding-top:1px;line-height:1.5} .fo b{color:${OK}} .fo.r b{color:${RED}}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="6" y1="84" x2="414" y2="84" stroke-width=".3"/><line x1="144" y1="6" x2="144" y2="84" stroke-width=".2"/>
<line x1="143" y1="86" x2="143" y2="264" stroke-width=".2"/><line x1="279" y1="86" x2="279" y2="264" stroke-width=".2"/>
${o}</svg></body></html>`;
const sf = path.join(TMP, 'sheet.html'); fs.writeFileSync(sf, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(sf).href, { waitUntil: 'load' }); await pg.waitForTimeout(400);
await pg.pdf({ path: path.join(OUT, 'logo_crown_blueprint.pdf'), width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: path.join(OUT, 'logo_crown_blueprint.jpg'), type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: docs/logo_crown/logo_crown_blueprint.pdf · .jpg');
