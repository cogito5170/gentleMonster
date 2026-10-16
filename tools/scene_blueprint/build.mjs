// node tools/scene_blueprint/build.mjs [render|sheet|all]
// One scene, THE STILL RUNWAY: a long-exposure render (three.js, averaged over the shutter time) and an A3 blueprint
// of how to make it (plan, section, camera, cast, the four verbs, graphic layer).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { D } from './dims.mjs';
import { sheet } from './sheet.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/shinsegae_vmd/blueprint');
const TMP = path.join(repo, 'out/scene_blueprint');
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();
const du = p => 'data:text/javascript;base64,' + fs.readFileSync(p).toString('base64');
const W = 2400, H = Math.round(2400 * 210 / 297);
const IMG = path.join(OUT, 'still_runway_render.jpg'), BOX = path.join(TMP, 'boxes.json');

async function render() {
  const V = path.join(repo, 'gentle_monster/vendor');
  const map = { imports: { three: du(path.join(V, 'three.module.min.js')), 'three/addons/environments/RoomEnvironment.js': du(path.join(V, 'RoomEnvironment.js')), 'sb/scene': du(path.join(here, 'scene.js')) } };
  const html = `<!doctype html><html><head><meta charset="utf-8"><script type="importmap">${JSON.stringify(map)}</script></head><body>
<script type=module>import { render } from 'sb/scene'; try { document.body.appendChild(render(${JSON.stringify(D)}, ${W}, ${H})); window.__done = true; } catch (e) { window.__err = String(e && e.stack || e); }</script></body></html>`;
  const page = path.join(TMP, 'render.html'); fs.writeFileSync(page, html);
  const b = await chromium.launch({ executablePath: exe, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage(); const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.goto(pathToFileURL(page).href, { waitUntil: 'commit' });
  await pg.waitForFunction('window.__done === true || window.__err', null, { timeout: 900000 });
  const err = await pg.evaluate('window.__err') || errs[0]; if (err) throw new Error('scene error: ' + err);
  const url = await pg.evaluate(() => document.getElementById('out').toDataURL('image/jpeg', .92));
  fs.writeFileSync(IMG, Buffer.from(url.split(',')[1], 'base64'));
  fs.writeFileSync(BOX, JSON.stringify(await pg.evaluate('window.__boxes')));
  await b.close(); console.log('산출물: ' + path.relative(repo, IMG));
}

async function print() {
  const html = path.join(TMP, 'sheet.html');
  const concept = path.join(repo, '.relay/tasks/002-still-runway/image.png');   // Codex image (codex-image skill)
  fs.writeFileSync(html, sheet(D, pathToFileURL(IMG).href, pathToFileURL(concept).href));
  const b = await chromium.launch({ executablePath: exe });
  const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
  await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
  const pg = await ctx.newPage(); await pg.goto(pathToFileURL(html).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
  const pdf = path.join(OUT, 'still_runway_blueprint.pdf'), jpg = path.join(OUT, 'still_runway_blueprint_preview.jpg');
  await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
  await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
  await b.close(); console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
}

const what = process.argv[2] || 'all';
if (what === 'render' || what === 'all') await render();
if (what === 'sheet' || what === 'all') await print();
