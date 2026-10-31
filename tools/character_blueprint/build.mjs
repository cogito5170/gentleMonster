// node tools/character_blueprint/build.mjs
// The character-image process (docs/character/midjourney_character.md) as one A3 blueprint: what went in at each
// step, which tool and settings, what came out and what was learned. The pictures are the user's own photos and the
// results they generated (thumbnails in docs/character/blueprint/thumbs); this script only lays out the sheet.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/character/blueprint'), TH = path.join(OUT, 'thumbs'), TMP = path.join(repo, 'out/character_blueprint');
fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff', OK = '#8fe3a8', NAVY = '#123f73';
const f = n => (+n).toFixed(2);
let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo s') => o += `<foreignObject x="${f(x)}" y="${f(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const IMG = (name, x, y, w, h, fit = 'slice') => { o += `<image href="${pathToFileURL(path.join(TH, name + '.jpg')).href}" x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" preserveAspectRatio="xMidYMid ${fit}"/>`; R(x, y, w, h, .3); };
const dim = 'class="d"', bold = 'font-weight="700"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const arrow = (x, y, ang = 0, col = INK, s = 1.6) => { const a = ang * Math.PI / 180; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };
const tag = (x, y, t, col) => { o += `<rect x="${f(x)}" y="${f(y - 2.8)}" width="${f([...t].reduce((w, c) => w + (/[가-힣]/.test(c) ? 1.85 : 1.1), 0) + 2.4)}" height="3.7" fill="${col}" stroke="none"/>`; T(x + 1.1, y, t, 1.75, `fill="${NAVY}" ${bold} font-family="${MONO}"`); };

// one card per step: [n, title, tool, inputs, result thumb, verdict, verdict colour, notes]
const STEPS = [
  ['01', 'SOURCE', '사진 다섯 장', null, null, '얼굴의 기준', OK, '안경원 셀카 · 거울 셀카. 둥근 얼굴, 볼살, 가운데 가르마, 홑꺼풀, 수염, 회색 반투명 안경'],
  ['02', 'CHARACTER 3D', 'Midjourney · --cref (V6.1)', ['src1'], 'r02_3d', '얼굴 특징이 사라짐', RED, '갸름한 얼굴 · 큰 눈의 일반 캐릭터. --stylize 150 과 화풍 문구가 얼굴을 다듬었다'],
  ['03', 'FEATURES', 'Midjourney · --style raw · --stylize 50', ['src1', 'src3'], 'r03_painted', '닮음은 늘고 그림체', EYE, '특징을 하나씩 적고 --no 로 미화를 막았다. 다음은 실사 판 (카메라 · 렌즈 문구, --no 3D)'],
  ['04', 'GRAPHIC STYLE', 'Midjourney --sw · Gemini', ['ref_style', 'src1'], null, '프롬프트만 (결과 대기)', DIM, '참고에서 스타일만: 은빛 머리, 투명 바이저, 주황 · 분홍 · 파랑 빛, 젖은 피부, 비닐 옷. 얼굴은 셀카에서'],
  ['05', 'EDIT', 'Gemini (편집)', ['coat', 'r03_painted'], null, '안경 · 카메라 각도', DIM, '코트 이미지에 셀카의 안경만 씌우기 / 그림체 셀카를 살짝 위에서 찍은 각도로. 나머지는 그대로'],
  ['06', 'MAGAZINE', 'Midjourney · 이미지 칸 혼동', ['ref_hero', 'r03_painted'], 'r06_magazine', '얼굴이 다른 모델로', RED, '웹 캡처가 이미지 칸에 → 그 모델의 얼굴 · 타원 선글라스가 섞임. 그림체 얼굴은 실사로 안 옮겨짐. Weird 4 · Chaos 5'],
  ['07', 'FACE FIX', 'V7 --iw 3 · Gemini', ['face_crop'], null, '진행 중', OK, '코트 이미지 얼굴을 크게 잘라 이미지 프롬프트로. V7 은 --cw · --ow 없음. Gemini 판은 첨부 순서로 역할을 나눈다'],
];

// ---------- 01 the process ----------
head(10, 14, '01', 'PROCESS — 캐릭터 이미지를 만든 일곱 단계', 'input → tool → result · red = failed, green = keep, blue = partly · thumbnails are the user\'s photos and generated results');
const cw = 56.2, ch = 120, cy = 24;
STEPS.forEach(([n, title, tool, ins, res, verdict, vc, note], i) => {
  const x = 8.5 + i * (cw + 1.6);
  R(x, cy, cw, ch, .4, 'rgba(255,255,255,.03)');
  T(x + 2, cy + 5, n, 3.4, `${bold} fill="${vc === RED ? RED : INK}"`); T(x + 10, cy + 5, title, 2.3, bold);
  T(x + 2, cy + 9.2, tool, 1.6, `font-family="${MONO}" class="d"`);
  T(x + 2, cy + 14, 'IN', 1.5, `${dim} letter-spacing=".3"`);
  if (!ins) { ['src1', 'src2', 'src3', 'src4', 'src5'].forEach((s, k) => IMG(s, x + 2 + (k % 3) * 17.6, cy + 16 + Math.floor(k / 3) * 23, 16.6, 22)); }
  else ins.forEach((s, k) => IMG(s, x + 2 + k * 26.6, cy + 16, 25.6, 32));
  const ry = cy + 66;
  T(x + 2, ry - 2, 'OUT', 1.5, `${dim} letter-spacing=".3"`);
  if (res) IMG(res, x + 2, ry, cw - 4, res === 'r03_painted' ? 30 : 24, res === 'r03_painted' ? 'slice' : 'meet');
  else { R(x + 2, ry, cw - 4, 24, .3, 'none', 'stroke-dasharray="1 .8"'); T(x + cw / 2, ry + 13, ins ? '—' : 'reference set', 1.8, `${dim} text-anchor="middle"`); }
  tag(x + 2, cy + 105, verdict, vc);
  FO(x + 2, cy + 107, cw - 4, 13, note);
  if (i < STEPS.length - 1) { L(x + cw + .1, cy + 40, x + cw + 1.3, cy + 40, .4); arrow(x + cw + 1.6, cy + 40, 0, INK, 1.1); }
});

// ---------- 02 why faces drift ----------
{ const x = 10, y = 156; head(x, y, '02', 'WHY THE FACE DRIFTS — 얼굴이 바뀐 이유', 'what pushed the result away from the applicant');
  [['다듬기', '--stylize 높음 · 화풍 문구 → 미드저니가 얼굴을 예쁘게 고친다', '--style raw · --stylize 30 이하 · --no idealized face, slim face, big eyes'],
   ['칸 혼동', '참고 사진이 이미지 프롬프트 칸에 → 그 사람의 얼굴과 소품이 섞인다', '스타일은 스타일 참조 칸에만, 로고 · 메뉴는 잘라 낸다'],
   ['그림체 얼굴', '셀 셰이딩 이미지는 실사 얼굴로 옮겨지지 않는다', '실사 얼굴을 크게 잘라 넣는다 (face_crop)'],
   ['무작위', 'Weird · Chaos 가 켜져 있다', '0 으로'],
   ['버전', 'V7 에는 --cw · --ow 가 없다', '--iw 3 + 글의 얼굴 묘사, 그래도 다르면 아래 03 의 편집 단계']].forEach(([a, b, c], i) => {
    const yy = y + 9 + i * 9.4; T(x, yy, a, 2, `${bold} fill="${RED}"`); FO(x + 22, yy - 3.2, 108, 9, b); FO(x + 132, yy - 3.2, 118, 9, '→ ' + c, 'fo s g'); });
}

// ---------- 03 the face-keeping ladder ----------
{ const x = 268, y = 156; head(x, y, '03', 'KEEP THE FACE — 얼굴을 지키는 순서', 'from cheapest to surest');
  [['1', 'Midjourney V7 생성', '이미지 프롬프트 face_crop · --iw 3 · 글의 얼굴 묘사', EYE],
   ['2', 'Midjourney Editor', '얼굴 · 머리 · 안경은 칠하지 않고 배경 · 옷만 바꾼다', EYE],
   ['3', 'Gemini 편집', '첨부 순서로 역할: 1 얼굴 · 2 안경 · 3 분위기. 같은 대화에서 고치는 말', OK],
   ['4', 'Gemini 얼굴 교체', '좋은 결과 + face_crop → 얼굴만 바꾸기', OK],
   ['5', 'Photoshop', '얼굴을 얹고 커브 · 그레인으로 빛을 맞춘다', OK]].forEach(([n, a, b, c], i) => {
    const yy = y + 10 + i * 8.6; C(x + 2.4, yy - .8, 2.2, .35, NAVY, `stroke="${c}"`); T(x + 2.4, yy - .05, n, 1.9, `text-anchor="middle" ${bold} fill="${c}"`);
    T(x + 7, yy, a, 2, bold); FO(x + 40, yy - 3.2, 106, 8.4, b); if (i < 4) L(x + 2.4, yy + 1.6, x + 2.4, yy + 5.6, .3, 'stroke-dasharray=".8 .6"'); });
}

// ---------- 04 rules + title ----------
{ const x = 10, y = 214; head(x, y, '04', 'RULES — 다음 프롬프트에서 지킬 것', 'saved in CLAUDE.md and docs/character/midjourney_character.md');
  [['Midjourney V7', '--iw (0–3) · --sw · --ar · --style raw · --stylize · --no · Weird / Chaos 0. --cw · --cref · --ow · --oref 는 쓰지 않는다'],
   ['Prompt text', 'URL 자리표시 · 한글 · 따옴표 · 세미콜론 · :: 없이. 이미지는 칸에 첨부'],
   ['Gemini', '설정 대신 문장. 첨부 순서 = 역할. "가져올 것 / 가져오지 않을 것"을 따로 적는다. 비율은 문장으로 (보장되지 않음)'],
   ['Brand', '참고 캡처의 로고 · 메뉴 · 글자는 잘라 낸다. 실제 제품을 따라 그리지 않는다. 시안에는 \'지원용 시안 (비공식)\''],
   ['Label', '결과는 본인 사진이 아니라 \'본인을 참고한 AI 이미지\'로 표기']].forEach(([a, b], i) => {
    const yy = y + 9 + i * 8.2; T(x, yy, a.toUpperCase(), 1.65, `${dim} letter-spacing=".3"`); FO(x + 28, yy - 3.2, 222, 8, b); });
}
{ const x = 268, y = 214; L(264, y - 4, 414, y - 4, .3);
  T(x, y + 6, 'CHARACTER PROCESS', 6.4, `${bold} letter-spacing="-.1"`); T(x, y + 12, 'JEONG HYEOKJU — character image, Midjourney + Gemini', 2.6, bold);
  T(x, y + 18, '얼굴은 사진에서, 스타일은 참고에서, 고치는 것은 편집으로.', 2.3, bold);
  [['Photos', 'applicant\'s own selfies (5) · coat image (AI) · face_crop'], ['References', 'futuristic beauty portrait · brand web hero (logo cut off)'],
   ['Prompts', 'docs/character/midjourney_character.md'], ['Status', '07 face fix in progress · no final image yet']].forEach(([a, b], i) => {
    T(x, y + 27 + i * 6, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(x + 18, y + 27 + i * 6, b, 1.75); });
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Character process blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}}
.fo{font-family:${F};color:#eef4fa;font-size:2.3px;line-height:1.45;padding-top:.6px} .fo.s{font-size:1.75px;color:#dbe7f2;padding-top:1px;line-height:1.45} .fo.g{color:${OK}}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="6" y1="149" x2="414" y2="149" stroke-width=".3"/><line x1="264" y1="149" x2="264" y2="291" stroke-width=".3"/>
<line x1="6" y1="207" x2="264" y2="207" stroke-width=".2"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'sheet.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(400);
const pdf = path.join(OUT, 'character_process_blueprint.pdf'), jpg = path.join(OUT, 'character_process_blueprint.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
