// node tools/tekton_banner/build.mjs
// TEKTON brand banner drafts on the user's lobby-screen mockup (docs/tekton_banner/source_banner.jpg).
// Text is set in HTML (Inter); the cube is the user's own TEKTON mark cut from docs/tekton_nova/source_screen.jpg.
// Out: docs/tekton_banner/banner_<A|D|E>.jpg (1764 x 984 at 2x, source frame trimmed)
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const OUT = path.join(ROOT, 'docs/tekton_banner');
const TMP = path.join(ROOT, 'out/tekton_banner'); fs.mkdirSync(TMP, { recursive: true });
const W = 1776, H = 1026;
const SCREEN = { x: 416, y: 318, w: 955, h: 413 };   // the black screen in the mockup
const INK = '#F2EEE8';

// cube mark: crop and cut out (transparent PNG)
const cube = path.join(TMP, 'cube.png');
execFileSync('python3', ['-c', `
from PIL import Image; import numpy as np
im = Image.open(${JSON.stringify(path.join(ROOT, 'docs/tekton_nova/source_screen.jpg'))}).convert('RGB').crop((34, 24, 102, 96))
a = np.asarray(im).astype(int); mx, mn = a.max(2), a.min(2)
alpha = np.clip((mx - mn - 50) * 4, 0, 255)   # keep the saturated faces only (drops black ground and white star specks)
rgba = np.dstack([a, alpha]).astype('uint8')
Image.fromarray(rgba, 'RGBA').resize((408, 432), Image.LANCZOS).save(${JSON.stringify(cube)})`]);

const V = {
  A: { h: ['Designing Objects.', 'Building Experiences.'], s: ['From products to exhibitions,', 'we shape the moments people stop for.'] },
  D: { h: ['Every Object Has a Stage.', 'We Build Both.'], s: ['Designing what you hold', 'and the space where you meet it.'] },
  E: { h: ['The Builder of Moments.', 'Designed to Be Remembered.'], s: ['A design studio for products,', 'exhibitions and brand spaces.'] },
};

const page = v => `<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px;overflow:hidden;background:#000}
.bg{position:absolute;inset:0;background:url(${pathToFileURL(path.join(OUT, 'source_banner.jpg')).href}) 0 0/100% 100%}
.screen{position:absolute;left:${SCREEN.x}px;top:${SCREEN.y}px;width:${SCREEN.w}px;height:${SCREEN.h}px;overflow:hidden;
  background:radial-gradient(ellipse 34% 62% at 79% 52%,rgba(236,226,214,.30),rgba(236,226,214,0) 70%),
             linear-gradient(90deg,#030303 0%,#0b0b0c 38%,#2b2a29 78%,#3a3836 100%)}
.lines{position:absolute;inset:0;opacity:.18}
.txt{position:absolute;left:${Math.round(SCREEN.w * .055)}px;top:${Math.round(SCREEN.h * .15)}px;color:${INK};font-family:Inter,sans-serif}
h1{font-size:33px;line-height:1.2;font-weight:300;letter-spacing:-.01em}
p{margin-top:12px;font-size:12.5px;line-height:19px;font-weight:400;opacity:.78}
.name{position:absolute;left:${Math.round(SCREEN.w * .055)}px;bottom:${Math.round(SCREEN.h * .1)}px;color:${INK};font-family:Inter,sans-serif;font-size:10.5px;font-weight:500;letter-spacing:.22em;opacity:.9}
.mark{position:absolute;left:${Math.round(SCREEN.w * .79 - 51)}px;top:${Math.round(SCREEN.h * .52 - 54)}px;width:102px;height:108px;
  background:url(${pathToFileURL(cube).href}) center/contain no-repeat;filter:drop-shadow(0 0 22px rgba(255,180,110,.40))}
.glow{position:absolute;left:${SCREEN.x}px;top:${SCREEN.y + SCREEN.h}px;width:${SCREEN.w}px;height:150px;
  background:radial-gradient(ellipse 40% 60% at 79% 0%,rgba(236,226,214,.10),rgba(0,0,0,0) 70%);mix-blend-mode:screen}
</style></head><body>
<div class="bg"></div>
<div class="screen">
  <svg class="lines" width="${SCREEN.w}" height="${SCREEN.h}"><g stroke="#cfc8bf" stroke-width=".6" fill="none">
    ${[[.30, .30], [.55, .62], [.30, .95], [.55, .05]].map(([x, y]) => { const cx = SCREEN.w * x, cy = SCREEN.h * y; return `<path d="M${cx} ${cy - 60}V${cy}M${cx} ${cy}L${cx - 52} ${cy + 30}M${cx} ${cy}L${cx + 52} ${cy + 30}"/>`; }).join('')}
  </g></svg>
  <div class="txt"><h1>${v.h.join('<br>')}</h1><p>${v.s.join('<br>')}</p></div>
  <div class="name">TEKTON DESIGNMENT</div>
  <div class="mark"></div>
</div>
<div class="glow"></div>
</body></html>`;

const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();
const br = await chromium.launch({ executablePath: exe });
const ctx = await br.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage();
for (const [k, v] of Object.entries(V)) {
  const f = path.join(TMP, `banner_${k}.html`); fs.writeFileSync(f, page(v));
  await pg.goto(pathToFileURL(f).href, { waitUntil: 'load' }); await pg.waitForTimeout(200);
  // trim the screenshot frame of the source (dark band top/bottom, white selection line top-right)
  await pg.screenshot({ path: path.join(OUT, `banner_${k}.jpg`), type: 'jpeg', quality: 90, clip: { x: 0, y: 23, width: 1764, height: 984 } });
  console.log('ok', k);
}
await br.close();
