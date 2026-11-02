// node tools/web_hero/build.mjs
// The web hero draft (docs/web_hero/current.jpg) with new copy: the old left-hand text is covered with patches of the
// page's own plain background, the new headline / label / two cards are set in HTML on top, and an A3 sheet compares
// the copy options. Only the user's own page is used; nothing is drawn as a picture.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const D = path.join(repo, 'docs/web_hero'), TMP = path.join(repo, 'out/web_hero');
fs.mkdirSync(TMP, { recursive: true });

// 1. cover the old text with the page's own background (patch boxes read off the 1812 x 1014 draft)
execFileSync('python3', ['-c', `
from PIL import Image, ImageFilter
im = Image.open('${D}/current.jpg').convert('RGB')
def cover(box, src):
    x0, y0, x1, y1 = box; p = im.crop(src); w, h = x1 - x0, y1 - y0
    tile = Image.new('RGB', (w, h))
    for yy in range(0, h, p.height):
        for xx in range(0, w, p.width): tile.paste(p, (xx, yy))
    im.paste(tile.filter(ImageFilter.GaussianBlur(1.2)), (x0, y0))
cover((36, 290, 236, 332), (440, 120, 690, 290))      # small label
cover((36, 345, 670, 655), (440, 120, 690, 290))      # headline
cover((50, 818, 232, 862), (60, 880, 232, 980))       # card 1 label
cover((272, 813, 452, 888), (274, 895, 452, 985))     # card 2 number
im.save('${TMP}/clean.png')
`]);

const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

// copy options: headline lines (about the same 46-49 characters as the draft's 48), label, two cards
export const OPTS = {
  A: { lines: ['SEEN FROM', 'THE INSIDE,', 'MADE FOR THE ONE', 'WHO STOPS.'], ko: '안에서 보고, 걸음을 멈춘 한 사람을 위해 만든다.', note: '지원자의 스토리(FROM THE INSIDE)를 한 줄로. 추천' },
  B: { lines: ['FRAMES THAT', 'CATCH THE EYE', '& STAY ON', 'YOUR MIND.'], ko: '눈길을 잡고, 기억에 남는 프레임.', note: '아이웨어 직접형. 제품 페이지에 잘 맞는다' },
  C: { lines: ['I WATCH', 'WHAT MAKES', 'PEOPLE STOP,', 'THEN I BUILD IT.'], ko: '사람을 멈추게 하는 것을 보고, 그것을 짓는다.', note: '일하는 방식(관찰 → 제작)을 문장으로' },
};
const LABEL = '| Jeong Hyeokju', CARD1 = { k: '| About', t: 'Architecture student who photographs people and styles looks — then builds what makes them stop.' },
  CARD2 = { n: '03', t: 'ways of seeing<br>Photo · Architecture · Fashion' };

const F = "'Liberation Sans',Arial,sans-serif";
const page = o => `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1812px;height:1014px;overflow:hidden} body{position:relative;background:url(${pathToFileURL(path.join(TMP, 'clean.png')).href}) 0 0/1812px 1014px;color:#fff;font-family:${F}}
.a{position:absolute} .lab{left:44px;top:296px;font-size:21px;transform:scaleX(.88);transform-origin:0 0;text-shadow:0 1px 6px rgba(80,40,0,.25)}
.h{left:44px;top:352px;font-weight:700;font-size:72px;line-height:75px;letter-spacing:-.5px;transform:scaleX(.84);transform-origin:0 0;white-space:nowrap;text-shadow:0 2px 14px rgba(80,40,0,.25)}
.k{font-size:20px;transform:scaleX(.88);transform-origin:0 0} .ct{font-size:15.5px;line-height:21px;margin-top:12px;width:180px;opacity:.95}
.n{font-weight:700;font-size:62px;line-height:62px;transform:scaleX(.86);transform-origin:0 0} .nt{font-size:15.5px;line-height:21px;margin-top:8px;width:180px;opacity:.95}
</style></head><body>
<div class="a lab">${LABEL}</div>
<div class="a h">${o.lines.join('<br>')}</div>
<div class="a" style="left:58px;top:824px"><div class="k">${CARD1.k}</div><div class="ct">${CARD1.t}</div></div>
<div class="a" style="left:278px;top:814px"><div class="n">${CARD2.n}</div><div class="nt">${CARD2.t}</div></div>
</body></html>`;

const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1812, height: 1014 }, deviceScaleFactor: 1 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage();
for (const [k, o] of Object.entries(OPTS)) {
  const f = path.join(TMP, `page_${k}.html`); fs.writeFileSync(f, page(o)); await pg.goto(pathToFileURL(f).href, { waitUntil: 'load' }); await pg.waitForTimeout(200);
  await pg.screenshot({ path: path.join(D, `after_${k}.jpg`), type: 'jpeg', quality: 90 });
}

// 2. the A3 sheet
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff', OK = '#8fe3a8', NAVY = '#123f73', MONO = "'Liberation Mono',monospace";
const SF = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif";
const fx = n => (+n).toFixed(2); let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${fx(x1)}" y1="${fx(y1)}" x2="${fx(x2)}" y2="${fx(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${fx(x)}" y="${fx(y)}" width="${fx(w)}" height="${fx(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${fx(x)}" cy="${fx(y)}" r="${fx(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${fx(x)}" y="${fx(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo s') => o += `<foreignObject x="${fx(x)}" y="${fx(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const IMG = (file, x, y, w, h) => { o += `<image href="${pathToFileURL(path.join(D, file)).href}" x="${fx(x)}" y="${fx(y)}" width="${fx(w)}" height="${fx(h)}" preserveAspectRatio="xMidYMid meet"/>`; R(x, y, w, h, .3); };
const bold = 'font-weight="700"', dim = 'class="d"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const num = (x, y, n, col = RED) => { C(x, y, 2.1, .35, NAVY, `stroke="${col}"`); T(x, y + .72, n, 1.85, `text-anchor="middle" ${bold} fill="${col}"`); };
const PW = 1812, PH = 1014;

// 01 NOW
{ const X = 10, Y = 22, W = 120, k = W / PW, H = PH * k, bx = (x0, y0, x1, y1, n) => { R(X + x0 * k, Y + y0 * k, (x1 - x0) * k, (y1 - y0) * k, .5, 'none', `stroke="${RED}"`); num(X + x1 * k + 3, Y + y0 * k + 2, n); };
  head(X, 14, '01', 'NOW — 지금 시안', 'red = text to replace or fill');
  IMG('current.jpg', X, Y, W, H);
  bx(36, 290, 236, 332, '1'); bx(36, 345, 670, 655, '2'); bx(32, 804, 245, 998, '3'); bx(256, 804, 469, 998, '4');
  [['1', '작은 라벨 · 템플릿 문구 (I Creative Agency)'], ['2', '헤드라인 · 48자, 4줄 · 오타 TOMORRW'], ['3', '카드 1 · 라벨만 있고 본문이 비어 있음'], ['4', '카드 2 · 근거 없는 숫자 95 %, 설명 없음']].forEach(([n, t], i) => {
    const yy = Y + H + 5 + i * 4.3; num(X + 2.2, yy - .8, n); T(X + 6.5, yy, t, 1.85); });
}

// 02 COPY
{ const X = 142, Y = 22; head(X, 14, '02', 'COPY — 헤드라인 대안 (지금 48자 → 46–49자, 4줄)', 'same line rhythm as the draft: short · long · short · short');
  T(X, Y + 3, 'NOW', 1.6, `${dim} letter-spacing=".3"`); T(X + 12, Y + 3, 'DESIGN THAT / CAPTIVATES TODAY / &amp; INSPIRES / TOMORRW.', 2, `font-family="${MONO}"`); T(X + 128, Y + 3, '48', 1.8, `fill="${RED}"`);
  Object.entries(OPTS).forEach(([k, op], i) => { const yy = Y + 11 + i * 17, s = op.lines.join(' '), col = k === 'A' ? OK : EYE;
    T(X, yy, k, 3.2, `${bold} fill="${col}"`); T(X + 6, yy, op.lines.join(' / ').replace(/&/g, '&amp;'), 2.15, `${bold} font-family="${MONO}"`); T(X + 128, yy, String(s.length), 1.8, `fill="${col}"`);
    T(X + 6, yy + 4.6, op.ko, 1.9); T(X + 6, yy + 8.6, op.note, 1.7, dim); });
  T(X, Y + 64, 'ALSO', 1.6, `${dim} letter-spacing=".3"`);
  FO(X + 12, Y + 61.2, 118, 22, `<b>라벨</b> I Creative Agency → <b>${LABEL}</b><br><b>카드 1</b> ${CARD1.k} — ${CARD1.t}<br><b>카드 2</b> <b>${CARD2.n}</b> ${CARD2.t.replace('<br>', ' — ')}<br>숫자는 지어내지 않는다: 95 % 대신 포트폴리오의 세 장(사진 · 건축 · 패션)`);
}

// 03 AFTER (A, recommended) + B / C
{ const Y = 116; head(10, Y, '03', 'AFTER — A 반영 (추천)', 'the old text covered with the page\'s own background · new copy set on top');
  const W = 250, H = W * PH / PW; IMG('after_A.jpg', 10, Y + 6, W, H);
  head(268, Y, '', 'B · C', 'same layout, other headlines');
  const w2 = 112, h2 = w2 * PH / PW; IMG('after_B.jpg', 284, Y + 6, w2, h2); T(284, Y + 9 + h2, 'B — FRAMES THAT CATCH THE EYE', 1.8, `${bold} fill="${EYE}"`);
  IMG('after_C.jpg', 284, Y + 14 + h2, w2, h2); T(284, Y + 17 + 2 * h2, 'C — I WATCH WHAT MAKES PEOPLE STOP', 1.8, `${bold} fill="${EYE}"`);
}

// 04 cards spec + title
{ const X = 10, Y = 270; L(6, Y - 5, 414, Y - 5, .3);
  T(X, Y, '04  CARDS — 좌측 하단 두 칸', 2.6, bold);
  FO(X, Y + 2, 250, 16, `<b>카드 1 ${CARD1.k}</b> — 한 문장 소개: 건축을 공부하며 사람을 찍고 착장을 맞춘다, 그리고 사람을 멈추게 하는 것을 짓는다. · <b>카드 2 ${CARD2.n}</b> — 보는 방식 세 가지 (사진 · 건축 · 패션), 포트폴리오의 세 장과 같다. 카드를 누르면 각 장으로 간다.`);
  const tx = 268; T(tx, Y, 'WEB HERO COPY', 5.4, `${bold} letter-spacing="-.1"`); T(tx, Y + 6, 'JEONG HYEOKJU — headline, label and cards for the hero draft', 2.2, bold);
  T(tx, Y + 11, 'font: draft is a condensed sans; preview uses Liberation Sans narrowed (scaleX .84)', 1.6, dim);
  T(tx, Y + 15, 'docs/web_hero · tools/web_hero/build.mjs', 1.6, dim);
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Web hero copy blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${SF}} .d{fill:${DIM}}
.fo{font-family:${SF};color:#eef4fa;font-size:2.3px;line-height:1.45;padding-top:.6px} .fo.s{font-size:1.85px;color:#dbe7f2;padding-top:1px;line-height:1.55} .fo b{color:#fff}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="6" y1="110" x2="414" y2="110" stroke-width=".3"/><line x1="137" y1="6" x2="137" y2="110" stroke-width=".2"/><line x1="264" y1="110" x2="264" y2="265" stroke-width=".2"/>
${o}</svg></body></html>`;
const sheet = path.join(TMP, 'sheet.html'); fs.writeFileSync(sheet, html);
const ctx2 = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx2.route(u => !u.href.startsWith('file:'), r => r.abort());
const p2 = await ctx2.newPage(); await p2.goto(pathToFileURL(sheet).href, { waitUntil: 'load' }); await p2.waitForTimeout(400);
await p2.pdf({ path: path.join(D, 'web_hero_blueprint.pdf'), width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await p2.screenshot({ path: path.join(D, 'web_hero_blueprint.jpg'), type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: docs/web_hero/web_hero_blueprint.pdf · .jpg · after_A/B/C.jpg');
