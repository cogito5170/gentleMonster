// node tools/window_blueprint/build.mjs [render|sheet|all]
// render: three.js still of the window (headless Chromium, swiftshader) -> cover_concept_render.jpg
// sheet:  A3 landscape blueprint (render + elevation + section + plan + details) -> PDF + preview PNG
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { D } from './dims.mjs';
import { sheet } from './sheet.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/shinsegae_vmd/blueprint');
const TMP = path.join(repo, 'out/window_blueprint');
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();
const du = p => 'data:text/javascript;base64,' + fs.readFileSync(p).toString('base64');
const W = 2400, H = Math.round(2400 * 210 / 297);

async function render() {
  const V = path.join(repo, 'gentle_monster/vendor');
  const map = { imports: { three: du(path.join(V, 'three.module.min.js')), 'three/addons/environments/RoomEnvironment.js': du(path.join(V, 'RoomEnvironment.js')), 'wb/scene': du(path.join(here, 'scene.js')) } };
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#000}</style><script type="importmap">${JSON.stringify(map)}</script></head><body>
<script type=module>import { render } from 'wb/scene'; try { const c = render(${JSON.stringify(D)}, ${W}, ${H}); document.body.appendChild(c); window.__done = true; } catch (e) { window.__err = String(e && e.stack || e); }</script></body></html>`;
  const page = path.join(TMP, 'render.html'); fs.writeFileSync(page, html);
  const b = await chromium.launch({ executablePath: exe, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 800, height: 600 } });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.goto(pathToFileURL(page).href, { waitUntil: 'commit', timeout: 180000 });
  await pg.waitForFunction('window.__done === true || window.__err', null, { timeout: 900000 });
  const err = await pg.evaluate('window.__err') || errs[0];
  if (err) throw new Error('scene error: ' + err);
  const url = await pg.evaluate(() => document.getElementById('out').toDataURL('image/jpeg', .92));
  const f = path.join(OUT, 'cover_concept_render.jpg'); fs.writeFileSync(f, Buffer.from(url.split(',')[1], 'base64'));
  await b.close(); console.log('산출물: ' + path.relative(repo, f));
}

async function print() {
  const html = path.join(TMP, 'sheet.html');
  fs.writeFileSync(html, sheet(D, pathToFileURL(path.join(OUT, 'cover_concept_render.jpg')).href));
  const b = await chromium.launch({ executablePath: exe });
  const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
  await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
  const pg = await ctx.newPage(); await pg.goto(pathToFileURL(html).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
  const pdf = path.join(OUT, 'cover_blueprint.pdf'), png = path.join(OUT, 'cover_blueprint_preview.jpg');
  await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
  await pg.screenshot({ path: png, type: 'jpeg', quality: 88 });
  await b.close(); console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, png));
}

const what = process.argv[2] || 'all';
if (what === 'render' || what === 'all') await render();
if (what === 'sheet' || what === 'all') await print();
