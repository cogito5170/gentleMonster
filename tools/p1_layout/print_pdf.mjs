// node tools/p1_layout/print_pdf.mjs <in.html> <out.pdf> [preview-prefix]
// HTML(.sheet 마다 A4 가로 한 쪽) -> PDF, 그리고 쪽마다 미리보기 PNG(<prefix>_1.png …).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const [, , inHtml, outPdf, prefix] = process.argv;
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const b = await chromium.launch({ executablePath: exe });
const pg = await b.newPage({ viewport: { width: 1123, height: 794 }, deviceScaleFactor: 2 });
await pg.goto(pathToFileURL(path.resolve(inHtml)).href, { waitUntil: 'load' });
await pg.evaluate(() => document.fonts.ready);
await pg.pdf({ path: outPdf, width: '297mm', height: '210mm', printBackground: true, preferCSSPageSize: true });
if (prefix) { const s = await pg.$$('body > .sheet'); for (let i = 0; i < s.length; i++) await s[i].screenshot({ path: `${prefix}_${i + 1}.png` }); }
await b.close();
console.log('wrote', outPdf);
