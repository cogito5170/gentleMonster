// node tools/mj_results_blueprint/build.mjs
// Every image the user generated with Midjourney in this workspace, as one A3 sheet: what was asked, the key prompt
// settings, what came back and what it taught. The pictures are the user's results (docs/midjourney_results/thumbs);
// this script only lays out the sheet.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/midjourney_results'), TH = path.join(OUT, 'thumbs'), TMP = path.join(repo, 'out/mj_results_blueprint');
fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff', OK = '#8fe3a8', NAVY = '#123f73';
const V = { ok: [OK, '쓸 만함'], part: [EYE, '일부'], fail: [RED, '고침 필요'] };
const f = n => (+n).toFixed(2);
let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo s') => o += `<foreignObject x="${f(x)}" y="${f(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const IMG = (name, x, y, w, h, fit = 'meet') => { R(x, y, w, h, .1, '#0b2c52', 'stroke="none"'); o += `<image href="${pathToFileURL(path.join(TH, name + '.jpg')).href}" x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" preserveAspectRatio="xMidYMid ${fit}"/>`; R(x, y, w, h, .3); };
const bold = 'font-weight="700"', dim = 'class="d"';
const tag = (x, y, t, col) => { const w = [...t].reduce((a, c) => a + (/[가-힣]/.test(c) ? 1.85 : 1.1), 0) + 2.4; o += `<rect x="${f(x)}" y="${f(y - 2.8)}" width="${f(w)}" height="3.7" fill="${col}" stroke="none"/>`; T(x + 1.1, y, t, 1.75, `fill="${NAVY}" ${bold}`); };
const band = (y, n, title, sub) => { T(10, y, `${n}  ${title}`, 2.6, bold); T(10, y + 3.2, sub, 1.85, dim); };

// a card: image + number/title + request + settings + result
function card(x, y, w, ih, c, n) {
  const [img, title, ask, set, res, v, fit] = c;
  IMG(img, x, y, w, ih, fit || 'meet');
  T(x, y + ih + 4, n, 2.6, `${bold} fill="${V[v][0]}"`); T(x + 6, y + ih + 4, title, 2.1, bold); tag(x + w - [...V[v][1]].length * 1.85 - 2.4, y + ih + 4, V[v][1], V[v][0]);
  FO(x, y + ih + 5.2, w, 7, '<b>요청</b> ' + ask);
  FO(x, y + ih + 11.2, w, 7, set, 'fo s m');
  FO(x, y + ih + 17.2, w, 9, '<b>결과</b> ' + res);
}

// ---------- A. FROM THE INSIDE cover ----------
band(14, 'A', 'FROM THE INSIDE — 신세계 VMD 커버', 'Midjourney · generate, Editor and Vary Region · 297:210');
const A = [
  ['mj09', '추상 컨셉', '스토리를 추상적 · 컨셉적으로', 'view from inside a dark display window · blur · one red point · --style raw', '극장 같은 띠 구도. 빨간 점이 불빛처럼 떠서 스토리와 끊김', 'part'],
  ['mj10', '스토리 기준', '문장에 있는 것만 그리기', 'mannequin back · red scarf · woman leaning in, looking at the scarf', '스토리는 읽힘. 웃는 사람이 특정 인물(여성)처럼 보임', 'part'],
  ['mj12', '누군가로', 'Editor 로 인물 · 행인 · 울타리 고치기', 'Vary Region · faceless passers-by · androgynous person', '구도는 좋아짐. 유리 글자가 SHOP NAME 으로 남음', 'part'],
  ['mj13', '글자 HYEOK JU', '유리 글자만 HYEOK JU 로', 'Editor · lettering "HYEOK JU" · warm beige', '바로 읽히고 분홍색. 반전 → 수정 → 반전으로 고침', 'fail'],
  ['mj15', '지원자와의 연결', '창 안에서 보는 스토리 + 지원자', '(판단) 진열의 등 · 기록하는 유리 · 진열 속의 나', '안에서 본다는 담았지만 지원자와 연결이 약함 → v5 스토리', 'part'],
];
A.forEach((c, i) => card(10 + i * 81.2, 21, 77.6, 54.6, c, String(i + 1).padStart(2, '0')));

// ---------- B. book mock-ups ----------
band(110, 'B', 'BOOK MOCK-UPS — 펼친 책 속 사진 (JAJU 포트폴리오)', 'Midjourney · generate with 2–3 attached images · --ow not available');
const B = [
  ['mj19', '책 속 커버', '책 이미지 + 커버 두 장으로', 'Image Prompt ×2 · Style Ref book · --iw 1.2', '책 · 손 · 초록빛 유지, 커버가 쪽에 들어감', 'ok'],
  ['mj23', '방 두 장 · 1', '왼쪽 거실 AR-07 · 오른쪽 주방 AR-08', 'magazine + 2 photos · --iw 1.2 · --no text', '거실 좋음. 주방 작업대가 하나로 단순', 'part'],
  ['mj24', '방 두 장 · 2', '같은 프롬프트 다시', 'same', '주방 두 대 · 굴뚝 둘로 원본에 가까움', 'ok'],
  ['mj25', '두 결과 합치기', '1 의 왼쪽 + 2 의 오른쪽', 'two results as Image Prompt · weird 8 · chaos 5', '한 방으로 이어지고 주방 하나 → 순서 · 접힘 문장', 'fail'],
  ['mj33', '착장 펼침', 'FA-02 · FA-04 / FA-02 · FA-03', '3:2 flat (top) vs 16:9 oblique (bottom)', '프롬프트 차이로 책 배치가 바뀜 → 구도를 글로 고정', 'part'],
  ['mj34', 'FA-02 · FA-04', '구도 고정판', '--iw 2 · oblique angle written · --no flat lay', '왼쪽 정상. 오른쪽 가게는 거의 새로 그려짐', 'part'],
];
B.forEach((c, i) => card(10 + i * 67.6, 117, 64.4, 36.2, c, String(i + 1).padStart(2, '0')));

// ---------- C. character ----------
band(186, 'C', 'CHARACTER — 지원자 캐릭터 · 잡지 커버', 'Midjourney · character from the applicant\'s selfies');
const C = [
  ['mj42', '3D 캐릭터', '1번 셀카 구도로 캐릭터화', '--cref (V6.1) · --cw 100 · --stylize 150', '갸름한 얼굴 · 큰 눈의 일반 캐릭터. 특징 사라짐', 'fail', 'meet'],
  ['mj47', '특징 · 그림체', '얼굴 특징이 드러나는 강한 이미지', 'features listed · --style raw · --no idealized face', '닮음은 늘었지만 그림체 (도구 기록 없음)', 'part', 'slice'],
  ['mj51', '잡지 커버', '웹 히어로 스타일로, 얼굴 그대로', 'web capture + selfie in Image slots · weird 4 · chaos 5', '다른 모델의 얼굴 · 타원 선글라스로 바뀜', 'fail', 'meet'],
];
[[10, 76], [90, 40], [134, 120]].forEach(([x, w], i) => card(x, 193, w, i === 1 ? 44 : 44, C[i], String(i + 1).padStart(2, '0')));

// ---------- lessons + title ----------
{ const x = 262, y = 186; L(258, 182, 258, 291, .3);
  T(x, y, 'LESSONS — 결과에서 배운 것', 2.6, bold);
  [['글자', '미드저니는 거꾸로 된 글자 · 정확한 철자를 못 쓴다 → 반전 후 수정, 또는 후보정에서 얹기'],
   ['칸', '참고 사진을 Image Prompt 에 넣으면 그 사람 · 물건이 섞인다 → 스타일은 Style Reference 에만'],
   ['구도', '책 각도 · 배치는 글로 적어 고정한다. 3:2 · flat 같은 말은 구도를 바꾼다'],
   ['두 쪽', '뒤에 적은 쪽 · 뒤에 첨부한 쪽이 약하다 → 약한 쪽을 앞에, 원본 배치대로 자세히'],
   ['얼굴', '다듬기 · 무작위(Weird · Chaos)를 끄고, V7 은 --iw 3 + 얼굴 묘사. 똑같아야 하면 Gemini · 포토샵'],
   ['버전', 'V7: --cw · --cref · --ow · --oref 없음']].forEach(([a, b], i) => {
    const yy = y + 7 + i * 7.4; T(x, yy, a, 1.9, `${bold} fill="${RED}"`); FO(x + 11, yy - 3.1, 140, 7.4, b); });
  const ty = 241; L(258, ty - 4, 414, ty - 4, .3);
  T(x, ty + 6, 'MIDJOURNEY RESULTS', 6.2, `${bold} letter-spacing="-.1"`);
  T(x, ty + 12, 'JEONG HYEOKJU — 14 results from the user\'s Midjourney sessions', 2.5, bold);
  T(x, ty + 18, `쓸 만함 ${[...A, ...B, ...C].filter(c => c[5] === 'ok').length} · 일부 ${[...A, ...B, ...C].filter(c => c[5] === 'part').length} · 고침 필요 ${[...A, ...B, ...C].filter(c => c[5] === 'fail').length}`, 2.2);
  [['Source', 'images the user generated and sent in this conversation'], ['Prompts', 'docs/shinsegae_vmd/midjourney_prompt_inside.md · docs/jaju_rounding_vmd/midjourney_room_spread.md · docs/character/midjourney_character.md'],
   ['Note', 'people in A and B are AI-generated · brand pages cropped out']].forEach(([a, b], i) => {
    T(x, ty + 26 + i * 7, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); FO(x + 15, ty + 23.2 + i * 7, 135, 7, b); });
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Midjourney results blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}}
.fo{font-family:${F};color:#eef4fa;font-size:2.3px;line-height:1.45;padding-top:.6px} .fo.s{font-size:1.72px;color:#dbe7f2;padding-top:1px;line-height:1.42}
.fo.m{font-family:${MONO};color:${DIM};font-size:1.55px} .fo b{color:${INK}}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="6" y1="104" x2="414" y2="104" stroke-width=".3"/><line x1="6" y1="181" x2="414" y2="181" stroke-width=".3"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'sheet.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(400);
const pdf = path.join(OUT, 'midjourney_results_blueprint.pdf'), jpg = path.join(OUT, 'midjourney_results_blueprint.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
