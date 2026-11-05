// node tools/portfolio_mockup/build.mjs
// Presentation board: SPA cover in the middle, three open spreads on each side (like a magazine showcase).
// Input: docs/portfolio_mockup/pages/*.jpg (pages rendered from the user's own portfolio PDF).
// Output: docs/portfolio_mockup/portfolio_mockup.jpg / .pdf (3000 x 1800).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const OUT = path.join(ROOT, 'docs/portfolio_mockup');
const PG = f => pathToFileURL(path.join(OUT, 'pages', f)).href;

const W = 3000, H = 1800;
// panels: x, y, w, h of the cream backing card; spreads sit centered inside
const COL = { L: 60, R: W - 60 - 820 };
const ROWS = [50, 625, 1200];
const PANEL = { w: 820, h: 550 };
const LEFT = ['style.jpg', 'picture.jpg', 'i_stop.jpg'];
const RIGHT = ['architecture.jpg', 'web_design.jpg', 'model.jpg'];

const spread = (img, x, y) => {
  const sw = 700, sh = Math.round(sw / 1.4155), sx = x + (PANEL.w - sw) / 2, sy = y + (PANEL.h - sh) / 2 + 4;
  return `
  <div class="panel" style="left:${x}px;top:${y}px;width:${PANEL.w}px;height:${PANEL.h}px"></div>
  <div class="spread" style="left:${sx}px;top:${sy}px;width:${sw}px;height:${sh}px">
    <div class="edge el"></div><div class="edge er"></div>
    <div class="half l" style="background-image:url(${PG(img)})"><i class="shade"></i></div>
    <div class="half r" style="background-image:url(${PG(img)})"><i class="shade"></i></div>
  </div>`;
};

const coverH = 1340, coverW = Math.round(coverH * 1273 / 1800);
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px;overflow:hidden}
body{position:relative;background:#1b1b1c}
.bg{position:absolute;inset:0;background:radial-gradient(ellipse 70% 75% at 50% 50%,#2a2a2b 0%,#1c1c1d 60%,#121213 100%)}
.bg svg{position:absolute;inset:0;width:100%;height:100%;opacity:.55;mix-blend-mode:overlay}
.panel{position:absolute;background:linear-gradient(180deg,#f1ebdc,#e9e2d1);box-shadow:0 2px 6px rgba(0,0,0,.35)}
.spread{position:absolute;perspective:2400px;filter:drop-shadow(0 10px 10px rgba(60,45,20,.35)) drop-shadow(0 2px 2px rgba(0,0,0,.25))}
.half{position:absolute;top:0;width:50%;height:100%;background-size:200% 100%;background-repeat:no-repeat;overflow:hidden}
.half.l{left:0;background-position:0 0;transform-origin:100% 50%;transform:rotateY(5deg)}
.half.r{right:0;background-position:100% 0;transform-origin:0 50%;transform:rotateY(-5deg)}
.half .shade{position:absolute;inset:0}
.half.l .shade{background:linear-gradient(90deg,rgba(255,255,255,.06) 0%,rgba(0,0,0,0) 70%,rgba(0,0,0,.10) 88%,rgba(0,0,0,.32) 100%)}
.half.r .shade{background:linear-gradient(270deg,rgba(255,255,255,.04) 0%,rgba(0,0,0,0) 72%,rgba(0,0,0,.12) 90%,rgba(0,0,0,.30) 100%)}
.edge{position:absolute;top:3px;bottom:-5px;width:50%;background:repeating-linear-gradient(180deg,#f4f1ea 0 1px,#d9d4c8 1px 2px)}
.edge.el{left:-4px;transform:skewY(0deg)}
.edge.er{right:-4px}
.cover{position:absolute;left:${(W - coverW) / 2}px;top:${(H - coverH) / 2}px;width:${coverW}px;height:${coverH}px;
  transform:perspective(3000px) rotateZ(-6deg) rotateY(-4deg) rotateX(2deg);transform-style:preserve-3d}
.cover .shadow{position:absolute;inset:0;transform:translate(28px,34px);background:rgba(0,0,0,.78);filter:blur(34px)}
.cover .thick{position:absolute;inset:0;transform:translate(7px,7px);background:linear-gradient(135deg,#d8d4cc,#a9a49b);}
.cover .face{position:absolute;inset:0;background:url(${PG('cover.jpg')}) center/cover no-repeat}
.cover .spine{position:absolute;top:0;bottom:0;left:0;width:42px;background:linear-gradient(90deg,rgba(0,0,0,.28),rgba(255,255,255,.35) 18%,rgba(0,0,0,.10) 34%,rgba(0,0,0,0) 100%)}
.cover .gloss{position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,.16) 0%,rgba(255,255,255,0) 32%,rgba(0,0,0,0) 62%,rgba(0,0,0,.14) 100%)}
</style></head><body>
<div class="bg"><svg xmlns="http://www.w3.org/2000/svg"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg></div>
${LEFT.map((f, i) => spread(f, COL.L, ROWS[i])).join('')}
${RIGHT.map((f, i) => spread(f, COL.R, ROWS[i])).join('')}
<div class="cover"><div class="shadow"></div><div class="thick"></div><div class="face"></div><div class="spine"></div><div class="gloss"></div></div>
</body></html>`;

const htmlPath = path.join(OUT, 'portfolio_mockup.html');
fs.writeFileSync(htmlPath, html);

const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();
const br = await chromium.launch({ executablePath: exe });
const ctx = await br.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage();
await pg.goto(pathToFileURL(htmlPath).href, { waitUntil: 'load' });
await pg.waitForTimeout(400);
await pg.screenshot({ path: path.join(OUT, 'portfolio_mockup.jpg'), type: 'jpeg', quality: 90 });
// PDF = the finished JPG on one page (the live page's blur/noise filters would make a ~100 MB PDF)
await pg.setContent(`<style>*{margin:0}</style><img src="${pathToFileURL(path.join(OUT, 'portfolio_mockup.jpg')).href}" style="width:${W}px;height:${H}px;display:block">`, { waitUntil: 'load' });
await pg.pdf({ path: path.join(OUT, 'portfolio_mockup.pdf'), width: W + 'px', height: H + 'px', printBackground: true, pageRanges: '1' });
await br.close();
fs.unlinkSync(htmlPath);
console.log('ok', path.join(OUT, 'portfolio_mockup.jpg'));
