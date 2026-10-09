// Render one magazine variant and measure it in Chromium.
//   NODE_PATH=$(npm root -g) node docs/portfolio/magazine/render.js docs/portfolio/magazine/variant_a_stopline
// Writes <variant>/magazine.pdf, <variant>/render/spread_*.png and <variant>/render/checks.json.
// Exit code 1 when a check fails. The checks measure layout; they do not judge taste.
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const dir = path.resolve(process.argv[2] || '.');
const html = 'file://' + path.join(dir, 'magazine.html');
const out = path.join(dir, 'render');
fs.mkdirSync(out, { recursive: true });

const MEASURE = () => {
  const PT = 96 / 72, MM = 96 / 25.4;
  const lum = c => { const [r, g, b] = c.map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }); return .2126 * r + .7152 * g + .0722 * b; };
  const rgb = s => (s.match(/[\d.]+/g) || []).map(Number);
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c.length === 3 || (c.length === 4 && c[3] > .5)) return c.slice(0, 3); } return [255, 255, 255]; };
  const res = [], manual = [];
  for (const pg of document.querySelectorAll('.page')) {
    const id = pg.dataset.page, P = pg.getBoundingClientRect();
    const live = pg.querySelector('.live'), L = live && live.getBoundingClientRect();
    const fail = (check, msg) => res.push({ page: id, check, msg });
    // leaf text elements
    const texts = [...pg.querySelectorAll('*')].filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
    for (const e of texts) {
      const cs = getComputedStyle(e), r = e.getBoundingClientRect();
      if (e.closest('[aria-hidden="true"]')) continue;
      const pt = parseFloat(cs.fontSize) / PT;
      if (pt < 6.5 - 1e-6) fail('min_type', `${pt.toFixed(2)} pt < 6.5 pt: "${e.textContent.trim().slice(0, 40)}"`);
      // inside the trim, and text that is not running head/folio/placeholder label inside the live area (1 px tolerance)
      if (r.left < P.left - 1 || r.right > P.right + 1 || r.top < P.top - 1 || r.bottom > P.bottom + 1) fail('trim', `outside trim: "${e.textContent.trim().slice(0, 40)}"`);
      if (L && e.closest('.live') && !e.closest('.ph') && (r.left < L.left - 1 || r.right > L.right + 1 || r.bottom > L.bottom + 1)) fail('live_area', `outside live area by ${Math.max(L.left - r.left, r.right - L.right, r.bottom - L.bottom).toFixed(1)} px: "${e.textContent.trim().slice(0, 40)}"`);
      if (e.scrollWidth > e.clientWidth + 1 && cs.overflow !== 'visible') fail('clip', `clipped: "${e.textContent.trim().slice(0, 40)}"`);
      // contrast against the nearest opaque background (placeholder hatch ignored: it is <6% alpha)
      const fg = rgb(cs.color), bg = bgOf(e), a = fg.length === 4 ? fg[3] : 1;
      const mix = fg.slice(0, 3).map((v, i) => v * a + bg[i] * (1 - a));
      const L1 = lum(mix), L2 = lum(bg), cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
      const large = pt >= 18 || (pt >= 14 && parseInt(cs.fontWeight) >= 700);
      if (cr < (large ? 3 : 4.5)) fail('contrast', `${cr.toFixed(2)}:1 at ${pt.toFixed(1)} pt: "${e.textContent.trim().slice(0, 40)}"`);
    }
    // grid blocks in the live area must not collide
    if (live) {
      const kids = [...live.children].map(k => [k, k.getBoundingClientRect()]);
      for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) {
        const [, a] = kids[i], [, b] = kids[j];
        const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ox > 1 && oy > 1) fail('overlap', `blocks ${i + 1} and ${j + 1} overlap ${(ox / MM).toFixed(1)} x ${(oy / MM).toFixed(1)} mm`);
      }
      // live-area children whose content is taller than their grid area (overflow into the next block)
      // Display type (>= 18 pt, line-height < 1) overflows its line box by design: Chromium counts the font's whole
      // content area, not the ink. Those blocks are listed for a visual check instead of being passed or failed here.
      for (const [k, r] of kids) {
        if (k.scrollHeight <= r.height + 1) continue;
        const big = [...k.querySelectorAll('*'), k].some(e => parseFloat(getComputedStyle(e).fontSize) / PT >= 18);
        if (big) manual.push({ page: id, check: 'display_type_ink', msg: `"${k.textContent.trim().slice(0, 30)}" content area exceeds box by ${((k.scrollHeight - r.height) / MM).toFixed(1)} mm -- inspect the PNG` });
        else fail('overflow', `block "${k.textContent.trim().slice(0, 30)}" overflows by ${((k.scrollHeight - r.height) / MM).toFixed(1)} mm`);
      }
    }
  }
  const pages = [...document.querySelectorAll('.page')].map(p => ({ page: p.dataset.page, src: p.dataset.src, assets: [...new Set([...p.querySelectorAll('[data-asset]')].map(a => a.dataset.asset))] }));
  return { failures: res, manual, pages };
};

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1800, height: 1400 }, deviceScaleFactor: 2 });
  await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());   // no network: what renders is what ships
  const pg = await ctx.newPage();
  await pg.goto(html, { waitUntil: 'load' });
  await pg.evaluate(() => document.fonts.ready);
  const spreads = await pg.$$('.spread');
  for (let i = 0; i < spreads.length; i++) await spreads[i].screenshot({ path: path.join(out, `spread_${i}.png`) });
  const checks = await pg.evaluate(MEASURE);
  await pg.emulateMedia({ media: 'print' });
  const printChecks = await pg.evaluate(MEASURE);
  await pg.pdf({ path: path.join(dir, 'magazine.pdf'), printBackground: true, preferCSSPageSize: true });
  await b.close();
  const pdfPages = (fs.readFileSync(path.join(dir, 'magazine.pdf'), 'latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
  const report = { html: path.relative(process.cwd(), path.join(dir, 'magazine.html')), pdf_pages: pdfPages, page_count_expected: checks.pages.length,
                   spreads: spreads.length, screen: checks.failures, print: printChecks.failures, manual_visual_checks: checks.manual, pages: checks.pages };
  fs.writeFileSync(path.join(out, 'checks.json'), JSON.stringify(report, null, 1));
  const bad = checks.failures.length + printChecks.failures.length + (pdfPages !== checks.pages.length ? 1 : 0);
  console.log(`pdf pages ${pdfPages}/${checks.pages.length} · spreads ${spreads.length} · failures screen ${checks.failures.length} print ${printChecks.failures.length}`);
  for (const f of [...checks.failures, ...printChecks.failures]) console.log(`  [${f.page}] ${f.check}: ${f.msg}`);
  for (const f of checks.manual) console.log(`  manual [${f.page}] ${f.msg}`);
  process.exit(bad ? 1 : 0);
})();
