// node tools/web_cards/preview.mjs <page.html> <out-base>  ->  <out-base>.pdf and .jpg at 1920 x 1080
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const [page, base] = process.argv.slice(2);
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
await pg.pdf({ path: base + '.pdf', width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: base + '.jpg', type: 'jpeg', quality: 90 });
await b.close();
