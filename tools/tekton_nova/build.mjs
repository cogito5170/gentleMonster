// node tools/tekton_nova/build.mjs   (run tools/tekton_nova/clean.py first)
// TEKTON NOVA screen artwork draft for the Photoshop LED-wall mockup (smart object content).
// Base: the user's own screen artwork with the draft text removed. Text is set in HTML (Inter), not drawn.
// Out: docs/tekton_nova/screen_draft.jpg (1980 x 650 at 2x = 3960 x 1300) + .pdf
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const OUT = path.join(ROOT, 'docs/tekton_nova');
const base = pathToFileURL(path.join(ROOT, 'out/tekton_nova/clean.jpg')).href;
const src = pathToFileURL(path.join(OUT, 'source_screen.jpg')).href;  // logo stays above the shade
const W = 1980, H = 650, ORANGE = '#ff8a3d';

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px;overflow:hidden;background:#000}
.bg{position:absolute;inset:0;background:url(${base}) 0 0/100% 100%}
.shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.88) 0%,rgba(0,0,0,.80) 28%,rgba(0,0,0,.45) 42%,rgba(0,0,0,0) 56%)}
.txt{position:absolute;left:110px;top:128px;width:600px;color:#fff;font-family:Inter,sans-serif}
.eyebrow{font-size:14px;font-weight:600;letter-spacing:.32em;color:rgba(255,255,255,.72)}
.eyebrow b{color:${ORANGE};font-weight:600}
h1{margin-top:14px;font-family:'Inter Display',Inter,sans-serif;font-size:66px;line-height:.98;font-weight:700;letter-spacing:-.025em}
.body{margin-top:24px;font-size:19px;line-height:28px;font-weight:400;color:rgba(255,255,255,.86)}
.sub{margin-top:34px;font-size:20px;font-weight:600;color:${ORANGE};letter-spacing:-.005em}
.body2{margin-top:8px;font-size:17px;line-height:25px;color:rgba(255,255,255,.78)}
.logo{position:absolute;left:30px;top:20px;width:250px;height:76px;background:url(${src}) -30px -20px/${W}px ${H}px}
.foot{position:absolute;left:110px;top:588px;display:flex;align-items:center;gap:16px;font-family:Inter,sans-serif;font-size:13px;font-weight:600;letter-spacing:.3em;color:#fff}
.foot i{display:block;width:44px;height:1.5px;background:${ORANGE}}
</style></head><body>
<div class="bg"></div><div class="shade"></div><div class="logo"></div>
<div class="txt">
  <div class="eyebrow">INTRODUCING <b>TEKTON NOVA</b></div>
  <h1>A Universe<br>In Your Hand.</h1>
  <p class="body">Designed from the edge of light to the curve of glass,<br>NOVA brings the depth of the night sky<br>to the screen you hold every day.</p>
  <p class="sub">Crafted Form. Endless Display.</p>
  <p class="body2">A frameless display, a warm metal body<br>and a design that fits the way you move.</p>
</div>
<div class="foot"><i></i>EXPERIENCE NOVA — NOW ON DISPLAY</div>
</body></html>`;

fs.mkdirSync(path.join(ROOT, 'out/tekton_nova'), { recursive: true });
const htmlPath = path.join(ROOT, 'out/tekton_nova/screen_draft.html');
fs.writeFileSync(htmlPath, html);

const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();
const br = await chromium.launch({ executablePath: exe });
const ctx = await br.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage();
await pg.goto(pathToFileURL(htmlPath).href, { waitUntil: 'load' });
await pg.waitForTimeout(300);
await pg.screenshot({ path: path.join(OUT, 'screen_draft.jpg'), type: 'jpeg', quality: 92 });
await pg.pdf({ path: path.join(OUT, 'screen_draft.pdf'), width: W + 'px', height: H + 'px', printBackground: true });
await br.close();
console.log('ok', path.join(OUT, 'screen_draft.jpg'));
