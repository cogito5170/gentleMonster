// node tools/p1_layout/layer_shots.mjs <in.html> <prefix> <dpi>
// HTML 의 .sheet 마다(층마다) 배경 없이 PNG 로 굽는다: <prefix>_1.png … — 포토샵 층 파일용. 쪽 크기는 .sheet 의 CSS 크기.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const [, , inHtml, prefix, dpi = '300'] = process.argv;
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const b = await chromium.launch({ executablePath: exe });
const pg = await b.newPage({ viewport: { width: 1300, height: 800 }, deviceScaleFactor: +dpi / 96 });
await pg.goto(pathToFileURL(path.resolve(inHtml)).href, { waitUntil: 'load' });
await pg.evaluate(() => document.fonts.ready);
const s = await pg.$$('body > .sheet');
for (let i = 0; i < s.length; i++) await s[i].screenshot({ path: `${prefix}_${i + 1}.png`, omitBackground: true });
await b.close();
console.log('wrote', s.length, 'layers');
