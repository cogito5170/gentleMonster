// node tools/jaju_layout/html2idml_extract.mjs <in.html> <out.json>
// 쪽(.sheet)마다 그려진 것을 InDesign 으로 옮길 수 있는 목록(mm)으로 뽑는다: 사각형 · 그레이디언트 · 사진 · 선 · 원 · 글 문단.
// html2idml.py 가 이 JSON 으로 IDML 을 짓는다.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const [, , inHtml, outJson] = process.argv;
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const b = await chromium.launch({ executablePath: exe });
const pg = await b.newPage({ viewport: { width: 1400, height: 900 } });
await pg.goto(pathToFileURL(path.resolve(inHtml)).href, { waitUntil: 'load' });
await pg.evaluate(() => document.fonts.ready);
const data = await pg.evaluate(() => {
  const PX = 25.4 / 96;
  const out = [];
  const sheets = [...document.querySelectorAll('body > .sheet')];
  const INLINE = new Set(['inline', 'inline-block']);
  for (const sh of sheets) {
    const S = sh.getBoundingClientRect();
    const mm = (r) => ({ x: (r.left - S.left) * PX, y: (r.top - S.top) * PX, w: r.width * PX, h: r.height * PX });
    const pt = (x, y) => [(x - S.left) * PX, (y - S.top) * PX];
    const items = [];
    const page = { bg: getComputedStyle(sh).backgroundColor, items };

    const runStyle = (el) => {
      const c = getComputedStyle(el);
      const df = el.closest('[data-font]');
      return { family: c.fontFamily, weight: +c.fontWeight, italic: c.fontStyle === 'italic', size: parseFloat(c.fontSize) * 0.75,
               color: c.color, stroke: parseFloat(c.webkitTextStrokeWidth) || 0, strokeColor: c.webkitTextStrokeColor,
               ls: c.letterSpacing === 'normal' ? 0 : parseFloat(c.letterSpacing) / parseFloat(c.fontSize),
               upper: c.textTransform === 'uppercase', dataFont: df ? df.getAttribute('data-font') : null,
               clip: (c.webkitBackgroundClip || c.backgroundClip) === 'text' };
    };
    // CSS scaleX → 장평: 문단 상자 또는 그 위 상자(쪽 안)의 transform 에서 찾는다
    const hscaleOf = (el) => {
      for (let e = el; e && !e.classList.contains('sheet'); e = e.parentElement) {
        const m = getComputedStyle(e).transform.match(/^matrix\(([-\d.e]+)/);
        if (m) return +m[1];
      }
      return 1;
    };
    const isInline = (n) => n.nodeType === 3 || (n.nodeType === 1 && INLINE.has(getComputedStyle(n).display) && n.tagName !== 'IMG' && n.tagName.toLowerCase() !== 'svg');
    const collectRuns = (nodes, runs) => {
      for (const n of nodes) {
        if (n.nodeType === 3) {
          const t = n.data.replace(/[ \t\n\r]+/g, ' ');
          if (t) runs.push({ text: t, ...runStyle(n.parentElement) });
        } else if (n.nodeType === 1) {
          if (n.tagName === 'BR') { runs.push({ text: '\n', ...runStyle(n.parentElement) }); continue; }
          const c = getComputedStyle(n);
          if (c.display === 'inline-block' && !n.textContent.trim()) {  // 색 견본 같은 빈 칸
            visitBox(n); continue;
          }
          if (c.display === 'inline-block' && parseFloat(c.borderTopWidth) > 0) {  // 동그라미 기호 — 테두리와 글자를 따로
            visitBox(n); para(n, [...n.childNodes]); continue;
          }
          collectRuns([...n.childNodes], runs);
        }
      }
    };
    const para = (container, nodes) => {
      const runs = [];
      collectRuns(nodes, runs);
      if (!runs.some((r) => r.text.trim())) return;
      while (runs.length && !runs[0].text.trim()) runs.shift();
      runs[0].text = runs[0].text.replace(/^ +/, '');
      while (runs.length && !runs[runs.length - 1].text.trim()) runs.pop();
      runs[runs.length - 1].text = runs[runs.length - 1].text.replace(/ +$/, '');
      const rg = document.createRange();
      rg.setStartBefore(nodes[0]); rg.setEndAfter(nodes[nodes.length - 1]);
      const rects = [...rg.getClientRects()].filter((r) => r.width > 0 && r.height > 0);
      if (!rects.length) return;
      const box = rg.getBoundingClientRect();
      const cc = getComputedStyle(container);
      const cr = container.getBoundingClientRect();
      const padL = parseFloat(cc.paddingLeft) || 0, padR = parseFloat(cc.paddingRight) || 0;
      const lh = cc.lineHeight === 'normal' ? parseFloat(cc.fontSize) * 1.2 : parseFloat(cc.lineHeight);
      const lines = Math.max(1, Math.round(box.height / lh));
      items.push({ kind: 'text', box: mm(box), container: mm({ left: cr.left + padL, top: cr.top, width: cr.width - padL - padR, height: cr.height }),
                   align: cc.textAlign, lead: lh * 0.75, wrap: cc.whiteSpace !== 'nowrap' && lines > 1, lines, runs,
                   hscale: hscaleOf(container),
                   opacity: +cc.opacity });
    };
    const visitBox = (el) => {  // 배경 · 테두리
      const c = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      if (r.width < 0.5 || r.height < 0.5) return;
      const bi = c.backgroundImage;
      if (bi && bi !== 'none' && bi.includes('gradient')) items.push({ kind: 'gradient', rect: mm(r), css: bi });
      const bg = c.backgroundColor;
      if (bg && !/rgba\(.*,\s*0\)$/.test(bg) && bg !== 'transparent' && el !== sh)
        items.push({ kind: 'rect', rect: mm(r), fill: bg, oval: c.borderTopLeftRadius.endsWith('%') ? parseFloat(c.borderTopLeftRadius) >= 50 : parseFloat(c.borderTopLeftRadius) >= r.width / 2 - 0.5, opacity: +c.opacity });
      const sides = ['Top', 'Right', 'Bottom', 'Left'].map((s) => ({ s, w: parseFloat(c['border' + s + 'Width']) || 0, col: c['border' + s + 'Color'], st: c['border' + s + 'Style'] }));
      const on = sides.filter((x) => x.w > 0 && x.st !== 'none');
      if (on.length === 4) items.push({ kind: 'rect', rect: mm(r), fill: null, stroke: on[0].col, sw: on[0].w * PX, dashed: on[0].st === 'dashed',
                                        oval: c.borderTopLeftRadius.endsWith('%') ? parseFloat(c.borderTopLeftRadius) >= 50 : parseFloat(c.borderTopLeftRadius) >= r.width / 2 - 0.5 });
      else for (const x of on) {
        const p = { Top: [[r.left, r.top], [r.right, r.top]], Bottom: [[r.left, r.bottom], [r.right, r.bottom]],
                    Left: [[r.left, r.top], [r.left, r.bottom]], Right: [[r.right, r.top], [r.right, r.bottom]] }[x.s];
        items.push({ kind: 'line', pts: p.map(([a, b2]) => pt(a, b2)), stroke: x.col, sw: x.w * PX, dashed: x.st === 'dashed', opacity: 1 });
      }
    };
    const visitSvg = (svg) => {
      for (const el of svg.querySelectorAll('line,polyline,path,rect,circle,text')) {
        const c = getComputedStyle(el);
        if (c.display === 'none') continue;
        const M = el.getScreenCTM();
        const tp = (x, y) => { const p = new DOMPoint(x, y).matrixTransform(M); return pt(p.x, p.y); };
        const scale = Math.sqrt(Math.abs(M.a * M.d - M.b * M.c));
        const sw = (parseFloat(c.strokeWidth) || 0) * scale * PX;
        const common = { stroke: c.stroke, sw, fill: c.fill, sop: +c.strokeOpacity, fop: +c.fillOpacity, opacity: +c.opacity, dashed: c.strokeDasharray !== 'none' };
        const tag = el.tagName;
        if (tag === 'line') items.push({ kind: 'line', pts: [tp(+el.getAttribute('x1'), +el.getAttribute('y1')), tp(+el.getAttribute('x2'), +el.getAttribute('y2'))], ...common });
        else if (tag === 'polyline') {
          const nums = el.getAttribute('points').trim().split(/[\s,]+/).map(Number);
          const pts = []; for (let i = 0; i + 1 < nums.length; i += 2) pts.push(tp(nums[i], nums[i + 1]));
          items.push({ kind: 'line', pts, ...common });
        } else if (tag === 'path') {
          const tok = el.getAttribute('d').match(/[MLHVZ]|-?[\d.]+(?:e-?\d+)?/gi);
          let x = 0, y = 0, cmd = 'M', i = 0; const pts = [];
          while (i < tok.length) {
            if (/[MLHVZ]/i.test(tok[i])) { cmd = tok[i++]; if (/z/i.test(cmd)) continue; }
            if (cmd === 'M' || cmd === 'L') { x = +tok[i++]; y = +tok[i++]; }
            else if (cmd === 'H') x = +tok[i++];
            else if (cmd === 'V') y = +tok[i++];
            else { i++; continue; }
            pts.push(tp(x, y));
          }
          items.push({ kind: 'line', pts, ...common });
        } else if (tag === 'rect') {
          const x = +el.getAttribute('x'), y = +el.getAttribute('y'), w = +el.getAttribute('width'), h = +el.getAttribute('height');
          const a = tp(x, y), d = tp(x + w, y + h);
          items.push({ kind: 'rect', rect: { x: a[0], y: a[1], w: d[0] - a[0], h: d[1] - a[1] }, fill: c.fill === 'none' ? null : c.fill, stroke: c.stroke, sw,
                       sop: +c.strokeOpacity, fop: +c.fillOpacity, opacity: +c.opacity, dashed: c.strokeDasharray !== 'none' });
        } else if (tag === 'circle') {
          items.push({ kind: 'rect', oval: true, rect: mm(el.getBoundingClientRect()), fill: c.fill === 'none' ? null : c.fill, stroke: c.stroke, sw,
                       sop: +c.strokeOpacity, fop: +c.fillOpacity, opacity: +c.opacity });
        } else if (tag === 'text') {
          const fs = parseFloat(c.fontSize) * scale * 0.75;
          const runs = [];
          for (const n of el.childNodes) {
            const pe = n.nodeType === 3 ? el : n;
            const cs = getComputedStyle(pe);
            const t = (n.textContent || '').replace(/\s+/g, ' ');
            if (t) runs.push({ text: t, family: cs.fontFamily, weight: +cs.fontWeight, italic: cs.fontStyle === 'italic', size: parseFloat(cs.fontSize) * scale * 0.75,
                               color: cs.fill, stroke: 0, ls: 0, upper: false, dataFont: null, clip: false });
          }
          if (!runs.length) continue;
          runs[0].text = runs[0].text.replace(/^ +/, '');
          const anchor = el.getAttribute('text-anchor') || 'start';
          items.push({ kind: 'text', box: mm(el.getBoundingClientRect()), container: null, align: anchor === 'end' ? 'right' : anchor === 'middle' ? 'center' : 'left',
                       lead: fs * 1.2, wrap: false, lines: 1, runs, opacity: +c.opacity * (+c.fillOpacity) });
        }
      }
    };
    const visit = (el) => {
      const c = getComputedStyle(el);
      if (c.display === 'none' || c.visibility === 'hidden') return;
      if (el.tagName === 'IMG') {
        const fr = el.parentElement.getBoundingClientRect();
        let ir = el.getBoundingClientRect();
        let x = ir.left, y = ir.top, w = ir.width, h = ir.height;
        if (c.objectFit === 'cover') {
          const s = Math.max(w / el.naturalWidth, h / el.naturalHeight);
          const nw = el.naturalWidth * s, nh = el.naturalHeight * s;
          x += (w - nw) / 2; y += (h - nh) / 2; w = nw; h = nh;
        }
        items.push({ kind: 'image', src: decodeURIComponent(el.src.replace('file://', '')), frame: mm(fr), img: mm({ left: x, top: y, width: w, height: h }),
                     px: [el.naturalWidth, el.naturalHeight], flip: c.transform.startsWith('matrix(-1') });
        return;
      }
      if (el.tagName.toLowerCase() === 'svg') { visitSvg(el); return; }
      visitBox(el);
      const kids = [...el.childNodes].filter((n) => n.nodeType === 1 || (n.nodeType === 3 && n.data.trim()) || (n.nodeType === 3 && n.data.length));
      const st = runStyle(el);
      if (st.clip) {  // 사진을 채운 글자 — 글로 옮기고 표시해 둔다
        const before = items.length; para(el, [...el.childNodes]);
        if (items.length > before) items[items.length - 1].clipImage = decodeURIComponent((c.backgroundImage.match(/url\("?(.*?)"?\)/) || [])[1] || '').replace('file://', '');
        return;
      }
      let group = [];
      const flush = () => { if (group.length) { para(el, group); group = []; } };
      for (const n of kids) {
        if (isInline(n)) group.push(n);
        else { flush(); if (n.nodeType === 1) visit(n); }
      }
      flush();
    };
    for (const ch of sh.children) visit(ch);
    out.push(page);
  }
  return out;
});
fs.writeFileSync(outJson, JSON.stringify(data));
await b.close();
console.log('wrote', outJson, data.length, 'pages');
