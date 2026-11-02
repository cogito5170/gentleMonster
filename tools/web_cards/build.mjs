// node tools/web_cards/build.mjs
// The four-card row with the copy from docs/web_cards/card_copy.md: the page set in HTML at the draft's size and
// card positions, using the applicant's photos (tone-matched copies from docs/tone_match), then an A3 sheet with the
// page, each card's English copy and Korean meaning, and the type spec.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const D = path.join(repo, 'docs/web_cards'), TM = path.join(repo, 'docs/tone_match'), TMP = path.join(repo, 'out/web_cards');
fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

// card boxes read off the draft (1956 x 1132), copy from card_copy.md
const CARDS = [
  { box: [40, 363, 472, 613], img: null, pos: '', label: 'Passion', solid: true,
    t: ['Clothes came first,', 'buildings came after'], b: 'I grew up wandering shops, asking how things should be placed to sell better.',
    tk: '옷이 먼저였고, 건축은 그다음이었다', bk: '매장을 돌아다니며, 어떻게 놓아야 더 잘 팔릴지 고민하며 자랐다.', src: '자기소개서 · 옷이 건축보다 먼저' },
  { box: [519, 564, 472, 514], img: 'graded_cafe.jpg', pos: '50% 62%', label: 'Observe',
    t: ['I look from the inside,', 'out to the people'], b: 'Behind the glass I watch what makes someone stop, look in and smile.',
    tk: '나는 안에서, 밖의 사람들을 본다', bk: '유리 안쪽에서, 무엇이 사람을 멈추게 하고 들여다보고 웃게 하는지 본다.', src: 'FROM THE INSIDE · 카페 창가' },
  { box: [1000, 366, 471, 617], img: 'graded_shop.jpg', pos: '50% 55%', label: 'Display',
    t: ['A window should hold', 'the passer-by'], b: 'Light, height and one point of colour — architecture taught me where the eye lands.',
    tk: '쇼윈도는 지나가는 사람을 붙잡아야 한다', bk: '빛, 높이, 색 한 점. 시선이 어디에 닿는지 건축에서 배웠다.', src: '건축 · 진열 · 가게 앞' },
  { box: [1480, 564, 472, 514], img: 'graded_park.jpg', pos: '50% 48%', label: 'Styling',
    t: ['Dressed for the place,', 'toned to the hour'], b: 'I match an outfit to where it will be seen, the way a store matches its season.',
    tk: '장소에 맞춰 입고, 시간에 맞춰 톤을 고른다', bk: '매장이 시즌에 맞추듯, 옷이 보일 장소에 맞춰 착장을 고른다.', src: '패션 기록 · 장소에 톤을 맞춘다' },
];
const F = "'Liberation Sans',Arial,sans-serif";
const card = c => { const [x, y, w, h] = c.box, bg = c.img ? `background:#111 url(${pathToFileURL(path.join(TM, c.img)).href}) ${c.pos}/cover` : 'background:#121212';
  return `<div class="c" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;${bg}">${c.img ? '<div class="sh"></div>' : ''}
  <div class="pill ${c.img ? 'o' : ''}">${c.label}</div>
  <div class="txt"><div class="plus"></div><div class="t">${c.t.join('<br>')}</div><div class="b">${c.b}</div></div></div>`; };
const page = `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1956px;height:1132px;background:#fff;font-family:${F}}
.c{position:absolute;border-radius:44px;overflow:hidden;color:#fff}
.sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 45%,rgba(0,0,0,.72) 100%)}
.pill{position:absolute;left:28px;top:26px;height:44px;padding:0 26px;border-radius:22px;background:#fff;color:#111;font-size:17px;line-height:44px}
.pill.o{background:transparent;border:2px solid #fff;color:#fff;line-height:40px}
.txt{position:absolute;left:28px;right:40px;bottom:40px}
.plus{width:26px;height:26px;position:relative;margin-bottom:28px}.plus:before,.plus:after{content:'';position:absolute;background:#fff}
.plus:before{left:12px;top:0;width:2px;height:26px}.plus:after{top:12px;left:0;height:2px;width:26px}
.t{font-size:29px;line-height:34px;letter-spacing:-.2px;margin-bottom:16px}.b{font-size:16.5px;line-height:21px;opacity:.9;max-width:360px}
</style></head><body>${CARDS.map(card).join('')}</body></html>`;

const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1956, height: 1132 }, deviceScaleFactor: 1 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); const pf = path.join(TMP, 'page.html'); fs.writeFileSync(pf, page);
await pg.goto(pathToFileURL(pf).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
await pg.screenshot({ path: path.join(D, 'cards_page.jpg'), type: 'jpeg', quality: 90 });

// ---------- A3 sheet ----------
const SF = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff', OK = '#8fe3a8', NAVY = '#123f73';
const fx = n => (+n).toFixed(2); let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${fx(x1)}" y1="${fx(y1)}" x2="${fx(x2)}" y2="${fx(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${fx(x)}" y="${fx(y)}" width="${fx(w)}" height="${fx(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${fx(x)}" cy="${fx(y)}" r="${fx(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${fx(x)}" y="${fx(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo s') => o += `<foreignObject x="${fx(x)}" y="${fx(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const bold = 'font-weight="700"', dim = 'class="d"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const num = (x, y, n, col = OK) => { C(x, y, 2.2, .35, NAVY, `stroke="${col}"`); T(x, y + .75, n, 1.9, `text-anchor="middle" ${bold} fill="${col}"`); };

{ const X = 10, Y = 22, W = 240, k = W / 1956, H = 1132 * k;
  head(X, 14, '01', 'PAGE — 카드 네 장에 문구를 얹은 화면', 'draft size 1956 × 1132 · same card positions · photos tone-matched (docs/tone_match)');
  R(X, Y, W, H, .1, '#fff', 'stroke="none"');
  o += `<image href="${pathToFileURL(path.join(D, 'cards_page.jpg')).href}" x="${X}" y="${Y}" width="${W}" height="${fx(H)}"/>`; R(X, Y, W, H, .35);
  CARDS.forEach((c, i) => { const [x, y] = c.box; num(X + (x + 30) * k, Y + (y - 30) * k, String(i + 1)); });
}
// right column: flow, type, title
{ const X = 262, Y = 14;
  T(X, Y, '03  FLOW — 네 장을 이어 읽으면', 2.6, bold);
  [['1 Passion', '관심 — 옷'], ['2 Observe', '관찰 — 안에서 본다'], ['3 Display', '진열 — 시선이 닿는 곳'], ['4 Styling', '착장 — 장소에 맞춘다']].forEach(([a, b2], i) => {
    const yy = Y + 8 + i * 6.4; num(X + 2.2, yy - .8, String(i + 1)); T(X + 6.5, yy, a.slice(2), 2.1, `${bold} fill="${OK}"`); T(X + 26, yy, b2, 1.95); });
  const ty = Y + 40; T(X, ty, '04  TYPE — 카드 안 글자', 2.6, bold);
  [['Label', 'pill 44 px · 17 px · 사진 카드는 테두리만'], ['Title', '29 / 34 px · 두 줄 · 아래쪽 왼쪽'], ['Body', '16.5 / 21 px · 90 % 흰색 · 최대 360 px'],
   ['Photo', '아래 40 % 검정 그라데이션 — 글이 읽히게'], ['Case', 'passion → Passion (다른 라벨과 맞춤)']].forEach(([a, b2], i) => {
    T(X, ty + 7 + i * 5.4, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(X + 14, ty + 7 + i * 5.4, b2, 1.8); });
  const tt = ty + 42; L(258, tt - 5, 414, tt - 5, .3);
  T(X, tt + 3, 'CARD COPY', 6, `${bold} letter-spacing="-.1"`); T(X, tt + 9, 'JEONG HYEOKJU — four cards, English + Korean', 2.3, bold);
  T(X, tt + 14.5, 'sources: self-introduction · FROM THE INSIDE · fashion notes · no invented numbers', 1.6, dim);
}
// 02 COPY as a table
{ const Y = 172; head(10, Y, '02', 'COPY — 영어 · 해석 (표)', 'label · title (2 lines) · body (2 lines on the card) · where the line comes from');
  const rows = CARDS.map((c, i) => `<tr><td class="n">${i + 1}</td><td class="lb">${c.label}</td><td class="en"><b>${c.t.join('<br>')}</b></td><td class="ko">${c.tk}</td><td class="en">${c.b}</td><td class="ko">${c.bk}</td><td class="sr">${c.src}</td></tr>`).join('');
  FO(10, Y + 6, 400, 110, `<table><tr><th>#</th><th>LABEL</th><th>TITLE (EN)</th><th>제목 해석</th><th>BODY (EN)</th><th>내용 해석</th><th>근거</th></tr>${rows}</table>`, 'tb');
}
const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Card copy blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${SF}} .d{fill:${DIM}}
.fo{font-family:${SF};color:#eef4fa;font-size:2.3px;line-height:1.45;padding-top:.6px} .fo.s{font-size:1.9px;color:#dbe7f2;padding-top:1px;line-height:1.5}
.fo.t{font-size:2.9px;line-height:1.35;color:#fff} .fo.k{color:${EYE}}
.tb{font-family:${SF};color:#eef4fa} .tb table{border-collapse:collapse;width:100%;font-size:2.15px;line-height:1.45}
.tb th{text-align:left;font-weight:400;color:${DIM};font-size:1.6px;letter-spacing:.3px;border-bottom:.3px solid #f4f8fb;padding:1.2px 1.6px}
.tb td{vertical-align:top;border-bottom:.15px solid rgba(255,255,255,.35);padding:2.6px 1.6px} .tb .n{color:${OK};font-weight:700;width:3%} .tb .lb{color:${OK};font-weight:700;width:8%}
.tb .en{width:22%} .tb .en b{font-size:2.6px;color:#fff} .tb .ko{color:${EYE};width:17%} .tb .sr{color:${DIM};font-size:1.8px;width:11%}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="6" y1="166" x2="414" y2="166" stroke-width=".3"/><line x1="256" y1="6" x2="256" y2="166" stroke-width=".2"/>
${o}</svg></body></html>`;
const sf = path.join(TMP, 'sheet.html'); fs.writeFileSync(sf, html);
const ctx2 = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx2.route(u => !u.href.startsWith('file:'), r => r.abort());
const p2 = await ctx2.newPage(); await p2.goto(pathToFileURL(sf).href, { waitUntil: 'load' }); await p2.waitForTimeout(400);
await p2.pdf({ path: path.join(D, 'card_copy_blueprint.pdf'), width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await p2.screenshot({ path: path.join(D, 'card_copy_blueprint.jpg'), type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: docs/web_cards/cards_page.jpg · card_copy_blueprint.pdf · .jpg');
