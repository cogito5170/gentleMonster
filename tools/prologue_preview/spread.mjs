// node tools/prologue_preview/spread.mjs
// The Prologue spread laid flat: A4 landscape = two A5 pages folded at the middle (the JAJU book's page size).
// Left page: PH-08 in one colour (tone.py), bleeding off the top, outer edge and gutter. Right page: the Prologue text.
// Writes out/prologue_preview/spread.png (the texture composite.py lays onto the mock-up) and a flat PDF.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const TMP = path.join(repo, 'out/prologue_preview'), OUT = path.join(repo, 'docs/jaju_rounding_vmd/prologue_preview');
fs.mkdirSync(TMP, { recursive: true }); fs.mkdirSync(OUT, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

// mm, one source for the spread and the sheet's SPREAD drawing
export const SP = { w: 297, h: 210, gutter: 148.5, photo: { h: 122, pos: '48% 50%' }, text: { x: 163, w: 120, y: 40 } };
export const LEAD_KO = [                                   // same text as the B6 Prologue (claude/magical-bell-u02os9, plan_c.py)
  '사람들은 쇼윈도를 밖에서 본다. 나는 안에서 본다.',
  '안에서 보면 가게 이름은 거꾸로 읽히고, 진열은 등을 보인다.',
  '대신 유리 너머로 사람들의 얼굴이 보인다.',
  '대부분은 그냥 지나간다. 가끔 누군가 걸음을 멈추고, 들여다보고, 웃는다.',
  '나는 그 사람이 무엇을 보고 웃었는지 본다.',
  '진열의 답은 상품이 아니라 그 표정에 있기 때문이다.',
  '그래서 나는 안에서 밖을 보는 VMD가 되려 한다.',
];
export const LEAD_EN = 'People look at a shop window from outside. I look from inside. From inside, the shop’s name reads backwards and the display shows its back. Instead, I see faces through the glass. Most people walk past. Now and then someone stops, looks in, and smiles. I watch what made them smile. The answer to a display is in that face, not in the product. So I want to be a VMD who looks out from the inside.';
export const INK = '#1b1a18', PAPER = '#f1eee6', RED = '#c8322b', MID = '#77726a', OLIVE = '#4d5a22';

const font = f => pathToFileURL(path.join(repo, 'tools/p1_layout/fonts', f)).href;
export function spreadHTML() {
  const img = pathToFileURL(path.join(TMP, 'ph08_tone.jpg')).href, { w, h, gutter, photo, text } = SP;
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
@font-face{font-family:Gloock;src:url(${font('Gloock-Regular.ttf')})} @font-face{font-family:Lora;src:url(${font('Lora-Regular.ttf')})}
@font-face{font-family:Lora;font-style:italic;src:url(${font('Lora-Italic.ttf')})}
@page{size:${w}mm ${h}mm;margin:0} html,body{margin:0} body{width:${w}mm;height:${h}mm;position:relative;background:${PAPER};overflow:hidden;color:${INK}}
.a{position:absolute} .ko{font-family:'WenQuanYi Zen Hei',sans-serif}
</style></head><body>
<img class="a" src="${img}" style="left:0;top:0;width:${gutter}mm;height:${photo.h}mm;object-fit:cover;object-position:${photo.pos}">
<div class="a" style="left:7mm;top:${h - 8}mm;transform:rotate(-90deg);transform-origin:0 0;font:7.5pt Lora;letter-spacing:.28em;white-space:nowrap">JEONG HYEOKJU</div>
<div class="a" style="left:7mm;top:${photo.h + 34}mm;transform:rotate(-90deg);transform-origin:0 0;font:7.5pt Lora;letter-spacing:.28em;white-space:nowrap;color:${MID}">PROLOGUE</div>
<div class="a" style="left:${gutter - 60}mm;top:${photo.h + 5}mm;width:52mm;text-align:right;font:6.5pt Lora;color:${MID}">PH-08 — outside, at night</div>
<div class="a" style="left:${text.x}mm;top:20mm;font:italic 13pt Lora;color:${OLIVE}">Prologue.</div>
<div class="a ko" style="left:${text.x}mm;top:${text.y}mm;width:${text.w}mm;font-size:10.6pt;line-height:1.85;text-align:justify;word-break:keep-all">${LEAD_KO.join(' ')}</div>
<div class="a" style="left:${text.x}mm;top:${text.y + 50}mm;width:${text.w}mm;font:8.4pt/1.6 Lora;color:${MID};text-align:justify;hyphens:auto">${LEAD_EN}</div>
<div class="a" style="left:${text.x}mm;top:${h - 12}mm;font:6.5pt Lora;letter-spacing:.2em;color:${MID}">FROM THE INSIDE</div>
<div class="a" style="left:${w - 22}mm;top:${h - 12}mm;width:10mm;text-align:right;font:6.5pt Lora;color:${MID}">01</div>
</body></html>`;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const page = path.join(TMP, 'spread.html'); fs.writeFileSync(page, spreadHTML());
  const b = await chromium.launch({ executablePath: exe });
  const ctx = await b.newContext({ viewport: { width: 1123, height: 794 }, deviceScaleFactor: 3 });
  await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
  const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
  await pg.screenshot({ path: path.join(TMP, 'spread.png') });
  await pg.pdf({ path: path.join(OUT, 'prologue_spread.pdf'), width: '297mm', height: '210mm', printBackground: true, preferCSSPageSize: true });
  await b.close();
  console.log('산출물: out/prologue_preview/spread.png'); console.log('산출물: docs/jaju_rounding_vmd/prologue_preview/prologue_spread.pdf');
}
