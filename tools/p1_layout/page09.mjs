// node tools/p1_layout/page09.mjs
// P1 9쪽(장 4 · 하나의 창 · 제안) 레이아웃 시안 -> docs/shinsegae_vmd/p1_layout/page09_layout.pdf + 미리보기 PNG
// 1쪽: 지면 시안 (이미지 자리는 회색 슬롯). 2쪽: 명세 (그리드 · 슬롯 치수 · 글 · 서체).
// 문법: ETÉREO R4(COLLAGE) — p1_types.md · p1_assets_direction.md. 단위는 mm, A4 가로 297×210.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/shinsegae_vmd/p1_layout');
const TMP = path.join(repo, 'out/p1_layout');
fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();
const font = f => pathToFileURL(path.join(here, 'fonts', f)).href;

// ── 그리드 (ETÉREO 펼침면 하나 = A4 가로 한 쪽) ──────────────────────────────
const G = { W: 297, H: 210, mid: 148.5, outer: 10, inner: 8, top: 22, bottom: 12, head: 7 };
G.L0 = G.outer; G.L1 = G.mid - G.inner; G.R0 = G.mid + G.inner; G.R1 = G.W - G.outer;

// ── 이미지 슬롯 ────────────────────────────────────────────────────────────────
const SLOTS = [
  { id: 'A', x: 22, y: 80, w: 70, h: 60, mat: '건축학과 작업물', what: '창의 평면 · 단면 (건축 작업의 도면 방식으로, 코드로 그림)', verb: '짓다', color: '흑백', marks: 'Zoning · Circulation 화살표' },
  { id: 'B', x: 10, y: 158, w: 34, h: 40, mat: '직접 찍은 사진', what: '빛의 방향과 빨간 한 점이 있는 한 장', verb: '비추다', color: '필름 컬러', marks: 'Focal point 원' },
  { id: 'C', x: 104, y: 146, w: 36.5, h: 52, mat: '나의 패션 사진', what: '착장 한 벌 (전신) — 마네킹에 입힐 조합', verb: '조합하다', color: '필름 컬러', marks: 'Triangle · 색 비율 띠' },
  { id: 'D', x: 156.5, y: 22, w: 130.5, h: 88, mat: '코드 도면 + A · B · C', what: '창 정면 — 세 재료를 한 장에 (도면 위에 사진의 빛 · 착장 도식)', verb: '셋을 합침', color: '흑백 + 빨간 한 점', marks: 'a) – d) 표시 (아래)' },
];

// ── 글 (책 전체 글자 예산: 문장 10개 안팎 — 이 쪽은 문장 4개) ───────────────────
const T = {
  headL: 'FROM THE INSIDE', headL2: 'PROPOSAL', headR: '2026', headR2: 'JEONG HYEOKJU',
  title: 'One <i>window</i>',
  lead: '세 재료로 창 하나를 짓는다.',
  capA: ['Build', '건축 작업의 평면 · 단면으로 창의 깊이와 동선을 그린다.'],
  capB: ['Light', '내 사진에서 빛의 방향과 빨간 한 점을 가져온다.'],
  capC: ['Combine', '내 착장 한 벌을 마네킹에 입힌다.'],
  keys: [['a)', 'Eye level', '가장 보여 줄 것은 눈높이에'], ['b)', 'Focal point', '시선이 처음 닿는 빨간 한 점'], ['c)', 'Triangle', '마네킹 · 소품 · 빛을 삼각으로'], ['d)', 'Light', '빛은 안에서 밖으로']],
  body: '공간을 나누는 손, 볼 곳을 고르는 눈, 아이템을 합치는 감각. 해 온 세 가지를 창 하나에 모았다.',
  capD: ['Proposal', '실제 진열이 아닌 제안이다. 도면은 직접 그린 것이고, 사진과 착장은 지원자 본인의 것이다.'],
};

const box = (x, y, w, h, cls, html, style = '') => `<div class="${cls}" style="left:${x}mm;top:${y}mm;${w != null ? `width:${w}mm;` : ''}${h != null ? `height:${h}mm;` : ''}${style}">${html}</div>`;

function slot(s, guides) {
  const lines = s.id === 'D' ? '' : `<svg class="ph" viewBox="0 0 ${s.w} ${s.h}" preserveAspectRatio="none"><line x1="0" y1="0" x2="${s.w}" y2="${s.h}"/><line x1="${s.w}" y1="0" x2="0" y2="${s.h}"/></svg>`;
  const label = `<div class="phl"><b>${s.id}</b><span>${s.mat}</span><span>${s.what}</span></div>`;
  return box(s.x, s.y, s.w, s.h, 'slot' + (guides ? ' g' : ''), lines + label + (s.id === 'D' ? overlayD(s) : ''));
}

// D 위의 VMD 표시: 가는 선 + 낱말 하나. 색은 빨간 한 점뿐.
function overlayD(s) {
  const w = s.w, h = s.h, fx = [0.63 * w, 0.5 * h], ey = 0.42 * h;
  const tri = [[0.30 * w, 0.86 * h], [0.63 * w, 0.27 * h], [0.90 * w, 0.86 * h]];
  return `<svg class="ov" viewBox="0 0 ${w} ${h}">
<line x1="2" y1="${ey}" x2="${w - 2}" y2="${ey}" class="dash"/><text x="3" y="${ey - 1.4}">a) Eye level</text>
<polygon points="${tri.map(p => p.join(',')).join(' ')}" class="dash"/><text x="${tri[2][0] - 15}" y="${tri[2][1] + 4.2}">c) Triangle</text>
<line x1="${fx[0]}" y1="3" x2="${fx[0]}" y2="${0.27 * h - 2}" class="solid"/><polygon points="${fx[0] - 1.2},${0.27 * h - 3.8} ${fx[0] + 1.2},${0.27 * h - 3.8} ${fx[0]},${0.27 * h - 1.8}" class="fill"/><text x="${fx[0] + 2}" y="7">d) Light</text>
<circle cx="${fx[0]}" cy="${fx[1]}" r="6.2" class="solid"/><circle cx="${fx[0]}" cy="${fx[1]}" r="1.5" class="red"/><text x="${fx[0]}" y="${fx[1] + 10.5}" text-anchor="middle">b) Focal point</text>
</svg>`;
}

function page(guides = false) {
  const S = Object.fromEntries(SLOTS.map(s => [s.id, s]));
  let o = '';
  // 머리말
  o += box(G.L0, G.head, null, null, 'hd b', T.headL) + box(G.L1 - 40, G.head, 40, null, 'hd r', T.headL2);
  o += box(G.R0, G.head, null, null, 'hd b', T.headR) + box(G.R1 - 60, G.head, 60, null, 'hd b r', T.headR2);
  // 쪽 번호 (바깥 여백, 세로)
  o += box(3.2, 100, null, null, 'folio', '<i>page</i>&nbsp;&nbsp;9') + box(G.W - 3.2, 100, null, null, 'folio rr', '<i>page</i>&nbsp;&nbsp;9');
  // 왼쪽 면: 헤드라인 + 한 문장 (ETÉREO R4 의 2단 본문 자리 — 글을 줄여 비운다)
  o += box(G.L0, 24, 120, null, 'title', T.title) + box(G.L0 + 0.6, 44.5, 110, null, 'lead', T.lead);
  // 왼쪽 면: 크기가 다른 사진 셋, 엇갈리게
  o += slot(S.A, guides) + box(S.A.x + S.A.w + 4, S.A.y + 1, 40, null, 'cap', `<i class="ct">${T.capA[0]}</i><span>${T.capA[1]}</span>`);
  o += slot(S.B, guides) + box(S.B.x + S.B.w + 3.5, S.B.y + 1, 22, null, 'cap', `<i class="ct">${T.capB[0]}</i><span>${T.capB[1]}</span>`);
  o += slot(S.C, guides) + box(S.C.x - 30, S.C.y + S.C.h - 15, 26.5, null, 'cap r', `<i class="ct">${T.capC[0]}</i><span>${T.capC[1]}</span>`);
  // 오른쪽 면: 가로 큰 그림 + 표시 열쇠 + 두 문장 + 굵은 캡션
  o += slot(S.D, guides);
  o += box(G.R0, 115, 130.5, null, 'keys', T.keys.map(([k, a, b]) => `<div><b>${k} ${a}</b><span>${b}</span></div>`).join(''));
  o += box(G.R0, 141, 100, null, 'body', T.body);
  o += box(G.R0, 183, 130.5, null, 'capb', `<b>${T.capD[0]}</b><span>${T.capD[1]}</span>`);
  if (guides) o += guideLayer();
  return `<div class="sheet${guides ? ' guides' : ''}">${o}</div>`;
}

function guideLayer() {
  const r = (x, y, w, h, c = '') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" class="${c}"/>`;
  return `<svg class="gl" viewBox="0 0 ${G.W} ${G.H}">
${r(G.L0, G.top, G.L1 - G.L0, G.H - G.bottom - G.top)}${r(G.R0, G.top, G.R1 - G.R0, G.H - G.bottom - G.top)}
<line x1="${G.mid}" y1="0" x2="${G.mid}" y2="${G.H}" class="mid"/>
<line x1="0" y1="${G.head}" x2="${G.W}" y2="${G.head}" class="hl"/>
</svg>`;
}

const len = s => s.replace(/<[^>]+>/g, '').length;
const words = [T.title, T.lead, ...[T.capA, T.capB, T.capC].map(c => c.join(' ')), ...T.keys.map(k => k.join(' ')), T.body, T.capD.join(' ')];
const totalChars = words.reduce((a, s) => a + len(s), 0);

function spec() {
  const row = c => `<tr>${c.map(x => `<td>${x}</td>`).join('')}</tr>`;
  const slotRows = SLOTS.map(s => row([`<b>${s.id}</b>`, `${s.x}, ${s.y}`, `${s.w} × ${s.h}`, s.mat, s.what, s.verb, s.color, s.marks])).join('');
  const textRows = [
    ['머리말', `${T.headL} · ${T.headL2} | ${T.headR} · ${T.headR2}`, 'Sans Bold / Regular 9.5pt'],
    ['헤드라인', T.title.replace(/<\/?i>/g, '*'), 'Serif 40pt, 한 낱말 이탤릭'],
    ['한 문장', T.lead, 'Sans 9.5pt'],
    ['캡션 A · B · C', 'Build · Light · Combine + 한 줄씩', 'Serif Italic 11pt + Sans 6.8pt'],
    ['표시 열쇠', 'a) Eye level · b) Focal point · c) Triangle · d) Light', 'Sans Bold 6.8pt + Regular'],
    ['본문', T.body, 'Sans 9.5pt'],
    ['굵은 캡션', T.capD.join(' — '), 'Sans Bold 9pt + Sans 7pt'],
    ['쪽 번호', 'page 9 (바깥 여백, 세로)', 'Serif Italic 7pt'],
  ].map(row).join('');
  return `<div class="sheet spec">
<div class="sh1">9쪽 레이아웃 명세 — 장 4 · 하나의 창 (제안)</div>
<div class="sh2">타입 COLLAGE (ETÉREO R4 · 8–9쪽) · A4 가로 297 × 210 mm · 단위 mm · 원점은 왼쪽 위</div>
<div class="mini">${page(true)}</div>
<div class="minicap">시안 1/2 축소 · 붉은 선 = 판면(여백 안쪽), 점선 = 가운데(펼침면의 접는 자리), 파란 선 = 머리말 기준선</div>
<div class="col l">
<h4>그리드</h4>
<table class="kv">
${[['판형', 'A4 가로 297 × 210 — ETÉREO 펼침면 하나 = 이 한 쪽'], ['가운데', `x ${G.mid} (접는 선 없음, 양쪽 ${G.inner} 띄움)`], ['여백', `바깥 ${G.outer} · 안 ${G.inner} · 위 ${G.top} (머리말 ${G.head}) · 아래 ${G.bottom}`], ['판면', `왼쪽 x ${G.L0}–${G.L1} · 오른쪽 x ${G.R0}–${G.R1}`], ['종이 · 글자', '미색 #E6E1DA · 검정 #1B1A18 · 빨강은 b) 한 점만 #C8322B'], ['출처', '여백은 ETÉREO R4 를 눈대중으로 옮긴 값. 실측 아님']].map(([a, b]) => `<tr><th>${a}</th><td>${b}</td></tr>`).join('')}
</table>
<h4>서체</h4>
<table class="kv">
<tr><th>시안</th><td>영문 세리프 Crimson Pro · 영문 산세리프 Instrument Sans · 한글 WenQuanYi Zen Hei (이 환경에 있는 글꼴)</td></tr>
<tr><th>최종</th><td>ETÉREO 짝(Garamond Premier Pro + Acumin)에 가깝게: 영문 EB Garamond · 한글 본명조(제목 · 인용) / Pretendard(머리말 · 본문 · 캡션)</td></tr>
</table>
</div>
<div class="col cr">
<h4>이미지 슬롯 — 세 재료 = 세 능력</h4>
<table class="grid"><tr><th></th><th>x, y</th><th>w × h</th><th>재료</th><th>무엇</th><th>능력</th><th>색</th><th>표시</th></tr>${slotRows}</table>
<h4>글 — 이 쪽 문장 4개 · ${totalChars}자 (머리말 · 쪽 번호 빼고)</h4>
<table class="grid">${textRows}</table>
<h4>규칙</h4>
<ul>
<li>ETÉREO R4 의 2단 본문 자리는 <b>비운다</b>. 헤드라인 + 한 문장만 둔다 (글자 예산).</li>
<li>사진 셋은 크기를 달리해 엇갈리게: 큰 것(A) 위 · 작은 것 둘(B · C) 아래 양 끝. 캡션은 이탤릭 세리프 한 낱말 + 산세리프 한 줄.</li>
<li>표시는 가는 선(0.25) + 낱말 하나. 문장을 쓰지 않는다. A · B · C 에도 같은 방식의 표시를 하나씩 (표의 '표시').</li>
<li>'제안'을 두 곳에 밝힌다: 머리말 PROPOSAL, 굵은 캡션 Proposal. 실제 시공 · 진열처럼 보이게 하지 않는다.</li>
<li>D 의 도면은 저장소 청사진 도구(tools/window_blueprint)로 그린다. 생성 이미지를 쓰지 않는다.</li>
</ul>
</div>
</div>`;
}

const css = `
@font-face{font-family:Crimson;src:url(${font('CrimsonPro-Regular.ttf')})}
@font-face{font-family:Crimson;font-style:italic;src:url(${font('CrimsonPro-Italic.ttf')})}
@font-face{font-family:Inst;src:url(${font('InstrumentSans-Regular.ttf')})}
@font-face{font-family:Inst;font-weight:700;src:url(${font('InstrumentSans-Bold.ttf')})}
@page{size:297mm 210mm;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#888}
body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{position:relative;width:297mm;height:210mm;background:#E6E1DA;color:#1B1A18;overflow:hidden;page-break-after:always;font-family:Inst,'WenQuanYi Zen Hei',sans-serif}
.sheet>div{position:absolute}
.hd{font-size:9.5pt;letter-spacing:.02em;white-space:nowrap}.hd.b{font-weight:700}.r{text-align:right}
.folio{font-family:Crimson,serif;font-size:7pt;transform:rotate(90deg);transform-origin:left top;white-space:nowrap;color:#4a463f}.folio.rr{transform:rotate(-90deg);transform-origin:left top;margin-top:12mm}
.title{font-family:Crimson,'WenQuanYi Zen Hei',serif;font-size:40pt;line-height:1;letter-spacing:-.01em}.title i{font-style:italic}
.lead{font-size:9.5pt;line-height:1.5}
.slot{background:#CFC8BE;overflow:hidden}.slot .ph{position:absolute;inset:0;width:100%;height:100%}.slot .ph line{stroke:#BDB5AA;stroke-width:.25}
.phl{position:absolute;left:2mm;bottom:1.6mm;right:2mm;font-size:6pt;line-height:1.35;color:#5d574e}.phl b{display:block;font-size:12pt;line-height:1;color:#3f3a33;margin-bottom:.8mm}.phl span{display:block}
.ov{position:absolute;inset:0;width:100%;height:100%;overflow:visible}.ov text{font-family:Inst,sans-serif;font-size:2.35px;fill:#1B1A18}
.ov .dash{fill:none;stroke:#1B1A18;stroke-width:.25;stroke-dasharray:1.2 .9}.ov .solid{fill:none;stroke:#1B1A18;stroke-width:.25}.ov .fill{fill:#1B1A18}.ov .red{fill:#C8322B}
.cap{font-size:6.8pt;line-height:1.4}.cap .ct{display:block;font-family:Crimson,serif;font-style:italic;font-size:11pt;margin-bottom:.8mm}.cap span{display:block}
.keys{display:grid;grid-template-columns:1fr 1fr;column-gap:8mm;row-gap:2.2mm;font-size:6.8pt;line-height:1.35}.keys b{display:block}
.body{font-size:9.5pt;line-height:1.6}
.capb{font-size:7pt;line-height:1.45}.capb b{display:block;font-size:9pt;margin-bottom:1mm}
.guides .gl{position:absolute;inset:0;width:100%;height:100%}.gl rect{fill:none;stroke:#C8322B;stroke-width:.35}.gl .mid{stroke:#1B1A18;stroke-width:.3;stroke-dasharray:2 1.5}.gl .hl{stroke:#2a5db0;stroke-width:.3}
.slot.g{outline:.35mm solid #1B1A18}
.spec{background:#F4F2EE}
.sh1{left:10mm;top:8mm;font-size:13pt;font-weight:700}.sh2{left:10mm;top:15mm;font-size:7.5pt;color:#5d574e}
.mini{left:10mm;top:22mm;width:148.5mm;height:105mm;outline:.2mm solid #999}.mini .sheet{transform:scale(.5);transform-origin:0 0;position:absolute;left:0;top:0}
.minicap{left:10mm;top:128.5mm;width:148.5mm;font-size:6.3pt;color:#5d574e}
.col{font-size:7pt;line-height:1.4}.col.l{left:10mm;top:136mm;width:148.5mm}.col.cr{left:166mm;top:22mm;width:121mm}
h4{font-size:8pt;margin:0 0 1.2mm;padding-top:1.6mm;border-top:.2mm solid #1B1A18}
table{border-collapse:collapse;width:100%;margin-bottom:3mm}td,th{vertical-align:top;text-align:left;padding:.6mm 1.2mm .6mm 0;font-weight:400}
.kv th{width:16mm;font-weight:700}.grid th{font-weight:700;border-bottom:.15mm solid #999}.grid td{border-bottom:.1mm solid #d5d0c8}.grid td:nth-child(6){white-space:nowrap}
ul{padding-left:3.5mm}li{margin-bottom:.8mm}
`;

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>P1 page 9 layout</title><style>${css}</style></head><body>${page(false)}${spec()}</body></html>`;
const htmlPath = path.join(TMP, 'page09.html');
fs.writeFileSync(htmlPath, html);

const b = await chromium.launch({ executablePath: exe });
const pg = await b.newPage({ viewport: { width: 1123, height: 794 }, deviceScaleFactor: 2 });
await pg.goto(pathToFileURL(htmlPath).href, { waitUntil: 'load' });
await pg.evaluate(() => document.fonts.ready);
await pg.pdf({ path: path.join(OUT, 'page09_layout.pdf'), width: '297mm', height: '210mm', printBackground: true, preferCSSPageSize: true });
const sheets = await pg.$$('body > .sheet');
await sheets[0].screenshot({ path: path.join(OUT, 'page09_layout_preview.png') });
await sheets[1].screenshot({ path: path.join(TMP, 'page09_spec_preview.png') });
await b.close();
console.log('wrote', path.relative(repo, path.join(OUT, 'page09_layout.pdf')), '·', totalChars, 'chars');
