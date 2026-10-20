// node tools/edit_blueprint/build.mjs
// FROM THE INSIDE — edit plan for the Midjourney image (docs/shinsegae_vmd/edit_blueprint/source_midjourney.jpg).
// The user edits the image in Midjourney; this script only lays out the A3 sheet: the image as it is with the edit
// regions, a line drawing of the target, the edit steps with their prompts, and which sentence each part carries.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const OUT = path.join(repo, 'docs/shinsegae_vmd/edit_blueprint');
const TMP = path.join(repo, 'out/edit_blueprint');
const IMG = path.join(OUT, 'source_midjourney.jpg');
fs.mkdirSync(TMP, { recursive: true });
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE_FROM || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const exe = (() => { const b = process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers';
  for (const d of fs.existsSync(b) ? fs.readdirSync(b).sort().reverse() : []) { const p = path.join(b, d, 'chrome-linux/chrome'); if (/^chromium-\d/.test(d) && fs.existsSync(p)) return p; } })();

// where things sit on the source image (fractions of width / height), read off the 1296x912 image
const A = {
  mannequin: [0, .07, .30, 1], scarf: [.255, .34, .335, 1],
  lettering: [0, .02, .84, .155], person: [.575, .14, .86, .62], face: [.61, .22, .71, .46], eyes: .30, mouth: .40,
  whiteScarf: [.59, .53, .79, 1], fence: [.335, .63, 1, 1], passL: [.36, .36, .58, .66], passR: [.88, .36, 1, .62],
};
// the edit steps: region on the image, tool, Midjourney prompt for that region
const STEPS = [
  ['1', 'fence', 'FENCE → 진열 안쪽 어둠', 'Vary Region', 'dark empty display interior seen from behind, soft shadow, no railing'],
  ['2', 'whiteScarf', 'WHITE SCARF → 코트 깃', 'Vary Region', 'plain dark wool coat collar, no scarf'],
  ['3', 'pass', 'PASSERS-BY → 얼굴 없는 행인', 'Vary Region', 'faceless passers-by with smooth blank faces, walking past, long motion blur'],
  ['4', 'lettering', 'OLD LETTERING → 빈 유리', 'Vary Region', 'plain bright glass, soft blurred lights of the indoor aisle, no letters'],
  ['5', 'person', 'PERSON → 누군가', 'Vary Region', 'androgynous person with short dark hair in a plain dark coat, no makeup, leaning toward the window, looking down at the red scarf, faint smile'],
  ['6', '', 'ZOOM OUT 1.5× (선택)', 'Zoom Out', '인물이 작아지고 유리 · 통로의 여백이 늘어난다. 인물 사진처럼 읽히면 쓴다'],
  ['7', 'eyes', 'NAME AT EYE LEVEL → 후보정', 'Photoshop', '좌우반전한 JEONG HYEOKJU 를 눈 높이에. 마네킹 뒤로 마스크 · 불투명도 70% · 흐림 1px · 커브로 검정을 누른다'],
];

const F = "'Liberation Sans','WenQuanYi Zen Hei',Arial,sans-serif", MONO = "'Liberation Mono','WenQuanYi Zen Hei',monospace";
const RED = '#ff6b5b', INK = '#f4f8fb', DIM = '#bcd2e6', EYE = '#9fd3ff', NAVY = '#123f73';
const f = n => (+n).toFixed(2);
let o = '';
const L = (x1, y1, x2, y2, w = .25, ex = '') => o += `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke-width="${w}" ${ex}/>`;
const R = (x, y, w, h, sw = .25, fill = 'none', ex = '') => o += `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const C = (x, y, r, sw = .25, fill = 'none', ex = '') => o += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" stroke-width="${sw}" fill="${fill}" ${ex}/>`;
const T = (x, y, t, sz = 2.2, ex = '') => o += `<text x="${f(x)}" y="${f(y)}" font-size="${sz}" ${ex}>${t}</text>`;
const FO = (x, y, w, h, t, cls = 'fo') => o += `<foreignObject x="${f(x)}" y="${f(y)}" width="${w}" height="${h}"><div xmlns="http://www.w3.org/1999/xhtml" class="${cls}">${t}</div></foreignObject>`;
const dim = 'class="d"', bold = 'font-weight="700"';
const head = (x, y, n, t, s) => { T(x, y, `${n}  ${t}`, 2.6, bold); if (s) T(x, y + 3.2, s, 1.85, dim); };
const arrow = (x, y, ang, col = RED, s = 1.6) => { const a = ang * Math.PI / 180; o += `<polygon points="${f(x)},${f(y)} ${f(x - s * Math.cos(a - .45))},${f(y - s * Math.sin(a - .45))} ${f(x - s * Math.cos(a + .45))},${f(y - s * Math.sin(a + .45))}" fill="${col}" stroke="none"/>`; };
const num = (x, y, n, col = RED) => { C(x, y, 2.2, .35, NAVY, `stroke="${col}"`); T(x, y + .75, n, 1.9, `text-anchor="middle" ${bold} fill="${col}"`); };
const frame = (X, Y, W, H) => ({ x: u => X + u * W, y: v => Y + v * H, box: ([u0, v0, u1, v1]) => [X + u0 * W, Y + v0 * H, (u1 - u0) * W, (v1 - v0) * H] });

const W = 196, H = W * 912 / 1296, Y0 = 22;

// ---------- 01 BEFORE: the image with the edit regions ----------
{ const X = 10, g = frame(X, Y0, W, H);
  head(X, 14, '01', 'BEFORE — 지금 이미지와 고칠 영역', 'Midjourney image · red = edit region (number = step in 03) · blue = keep');
  o += `<image href="${pathToFileURL(IMG).href}" x="${X}" y="${Y0}" width="${W}" height="${f(H)}" preserveAspectRatio="none"/>`; R(X, Y0, W, H, .4);
  const box = (k, col, lab, n, low) => { const [x, y, w, h] = g.box(A[k]); R(x + .4, y + .4, w - .8, h - .8, .45, 'none', `stroke="${col}" stroke-dasharray="1.4 .8"`);
    const ly = low ? y + h - 4.2 : y + .4;
    if (lab) { o += `<rect x="${f(x + .4)}" y="${f(ly)}" width="${f(lab.length * 1.25 + 2)}" height="3.4" fill="${col}" stroke="none"/>`; T(x + 1.2, ly + 2.6, lab, 1.8, `fill="${col === EYE ? NAVY : '#fff'}" ${bold} font-family="${MONO}"`); }
    if (n) num(x + w - 3.2, y + 3.4 + 2, n, col); };
  box('mannequin', EYE, 'KEEP mannequin back', '', true); box('scarf', EYE, '');
  { const [x, y] = g.box(A.mannequin); o += `<rect x="${f(x + .4)}" y="${f(y + (1 - .07) * H - 8.4)}" width="18" height="3.4" fill="${EYE}" stroke="none"/>`; T(x + 1.2, y + (1 - .07) * H - 5.8, 'KEEP red scarf', 1.8, `fill="${NAVY}" ${bold} font-family="${MONO}"`); }
  box('fence', RED, 'fence', '1'); box('whiteScarf', RED, 'white scarf', '2'); box('passL', RED, 'passers-by', '3'); box('passR', RED, '', '3');
  box('lettering', RED, '"SHOP NAME" mirrored', '4'); box('person', RED, 'specific person', '5');
  const ey = g.y(A.eyes); L(g.x(.56), ey, g.x(.88), ey, .5, `stroke="${RED}"`); T(g.x(.885), ey + .7, '7 eye level', 1.7, `${bold} fill="${RED}"`);
}

// ---------- 02 AFTER: the target as a line drawing ----------
{ const X = 214, g = frame(X, Y0, W, H), x = g.x, y = g.y;
  head(X, 14, '02', 'AFTER — 고친 뒤의 화면', 'line drawing of the target · same frame as 01 · red dashed = their gaze · blue = my eye (the camera)');
  R(X, Y0, W, H, .4, '#0d2f57');
  R(x(0), y(.15), W, (.62 - .15) * H, .1, 'rgba(255,255,255,.13)', 'stroke="none"');              // bright indoor aisle beyond the glass
  for (let i = 0; i < 6; i++) C(x(.38 + i * .1), y(.2 + (i % 2) * .05), 1.2, .15, 'rgba(255,255,255,.25)', 'stroke="none"');
  T(x(.36), y(.18), 'bright indoor aisle', 1.6, dim);
  // faceless passers-by, smeared along the aisle
  [[.40, .43], [.46, .45], [.52, .42], [.94, .44]].forEach(([u, v], i) => {
    o += `<ellipse cx="${f(x(u))}" cy="${f(y(v))}" rx="1.6" ry="2.1" stroke-width=".3" fill="rgba(255,255,255,.08)"/>`;
    R(x(u) - 2.2, y(v) + 2.5, 4.4, 10, .25, 'rgba(255,255,255,.05)'); [0, 1, 2].forEach(k => L(x(u) - 2.2 - 3 - k * 1.6, y(v) + 4.5 + k * 2.6, x(u) - 2.8, y(v) + 4.5 + k * 2.6, .25, `stroke="${DIM}" opacity=".7"`)); });
  T(x(.37), y(.67), 'faceless, walking past', 1.6, `${dim}`);
  num(x(.45), y(.33), '3');
  // the one who stopped: short hair, plain coat, leaning toward the window
  const hx = x(.665), hy = y(.34), ey = y(A.eyes);
  o += `<path d="M${f(hx - 10)} ${f(hy + 3)} Q${f(hx - 10.5)} ${f(hy - 13)} ${f(hx)} ${f(hy - 13.5)} Q${f(hx + 10.5)} ${f(hy - 13)} ${f(hx + 10)} ${f(hy + 3)}" stroke-width=".4" fill="rgba(0,0,0,.35)"/>`;
  o += `<ellipse cx="${f(hx)}" cy="${f(hy + 1)}" rx="8.6" ry="11.5" stroke-width=".4" fill="rgba(255,255,255,.1)"/>`;
  o += `<path d="M${f(hx - 2.6)} ${f(y(A.mouth) - .4)} Q${f(hx)} ${f(y(A.mouth) + 1.6)} ${f(hx + 2.6)} ${f(y(A.mouth) - .4)}" stroke="${RED}" stroke-width=".45"/>`;
  L(hx - 3, y(.44), hx - 3.4, y(.5), .4); L(hx + 3, y(.44), hx + 3.4, y(.5), .4);
  o += `<path d="M${f(x(.575))} ${f(y(1))} L${f(x(.6))} ${f(y(.6))} Q${f(x(.62))} ${f(y(.52))} ${f(hx - 3.4)} ${f(y(.5))} L${f(hx + 3.4)} ${f(y(.5))} Q${f(x(.73))} ${f(y(.52))} ${f(x(.76))} ${f(y(.6))} L${f(x(.85))} ${f(y(1))} Z" stroke-width=".4" fill="rgba(0,0,0,.45)"/>`;
  L(hx - 3.4, y(.5), hx, y(.6), .3); L(hx + 3.4, y(.5), hx, y(.6), .3); T(x(.69), y(.86), 'plain dark coat · collar', 1.5, dim);
  num(x(.83), y(.17), '5'); T(x(.725), y(.12), 'someone, not a portrait', 1.6, `${bold} fill="${RED}"`);
  T(hx + 7.5, y(A.mouth) + 1, 'smile kept', 1.6, `fill="${RED}"`); T(hx + 7.5, ey - 3.8, 'eyes behind the name', 1.5, dim);
  // mirrored name on the glass at eye level (drawn first: it sits behind the mannequin)
  R(x(.18), ey - 4, (.97 - .18) * W, 8, .2, 'rgba(255,236,200,.06)', `stroke="rgba(255,236,200,.4)" stroke-dasharray=".8 .6"`);
  o += `<text x="0" y="0" font-size="7" font-weight="700" letter-spacing="1.4" fill="rgba(255,236,200,.85)" stroke="none" text-anchor="middle" transform="translate(${f(x(.6))} ${f(ey + 2.5)}) scale(-1 1)">JEONG HYEOKJU</text>`;
  num(x(.955), ey - 5.5, '7');
  // dark display interior instead of the fence
  R(x(.3), y(.66), W * .7, H * .34, .1, 'url(#hatch)', 'stroke="none" opacity=".55"'); T(x(.36), y(.95), 'dark display interior (fence removed)', 1.6, dim); num(x(.95), y(.93), '1');
  // mannequin back + red scarf (kept)
  o += `<path d="M${f(x(0))} ${f(y(1))} L${f(x(0))} ${f(y(.22))} Q${f(x(.06))} ${f(y(.12))} ${f(x(.14))} ${f(y(.13))} L${f(x(.14))} ${f(y(.07))} L${f(x(.17))} ${f(y(.07))} L${f(x(.17))} ${f(y(.14))} Q${f(x(.27))} ${f(y(.17))} ${f(x(.295))} ${f(y(.36))} L${f(x(.27))} ${f(y(1))} Z" stroke-width=".45" fill="#081f3b"/>`;
  o += `<path d="M${f(x(.27))} ${f(y(.34))} Q${f(x(.31))} ${f(y(.38))} ${f(x(.33))} ${f(y(.55))} L${f(x(.335))} ${f(y(1))} L${f(x(.275))} ${f(y(1))} Z" stroke="none" fill="${RED}" opacity=".9"/>`;
  T(x(.03), y(.5), 'mannequin, from behind', 1.6, dim); T(x(.03), y(.54), '(kept)', 1.6, dim);
  // their gaze → the red scarf ; my eye (camera) → their face
  const sx = x(.33), sy = y(.5); o += `<path d="M${f(hx - 5)} ${f(ey + 2)} Q${f(x(.45))} ${f(y(.45))} ${f(sx + 1)} ${f(sy)}" stroke="${RED}" stroke-width=".5" stroke-dasharray="1.6 1"/>`; arrow(sx + 1, sy, 175);
  T(x(.36), y(.585), 'their gaze → the scarf', 1.6, `fill="${RED}"`);
  const cx = x(.5), cy = y(1) - 2; L(cx, cy, hx - 2, y(A.mouth) + 4, .5, `stroke="${EYE}" stroke-dasharray="1.6 1"`); arrow(hx - 2, y(A.mouth) + 4, Math.atan2(y(A.mouth) + 4 - cy, hx - 2 - cx) * 180 / Math.PI, EYE);
  C(cx, cy, 1.3, .35, NAVY, `stroke="${EYE}"`); T(cx + 2.2, cy - .3, 'my eye (camera, inside)', 1.6, `fill="${EYE}"`);
}

// ---------- 03 the edit steps ----------
{ const x = 10, y = 175; head(x, y, '03', 'EDIT STEPS — 미드저니 수정 순서', 'Editor → upload the image → select the region → replace the prompt with the line below → submit · reroll until it reads right');
  const cols = [x, x + 8, x + 58, x + 80];
  ['#', 'REGION', 'TOOL', 'PROMPT FOR THE REGION'].forEach((t, i) => T(cols[i], y + 9, t, 1.6, `${dim} letter-spacing=".3"`)); L(x, y + 10.5, x + 250, y + 10.5, .2);
  STEPS.forEach(([n, , region, tool, pr], i) => { const yy = y + 16 + i * 12.6;
    num(cols[0] + 2.4, yy - .8, n, n === '7' || n === '6' ? EYE : RED); T(cols[1], yy, region, 1.9, bold); T(cols[2], yy, tool, 1.8, `font-family="${MONO}" class="m"`);
    FO(cols[3], yy - 3.2, 172, 11, pr, /[가-힣]/.test(pr) ? 'fo s' : 'fo s m2'); L(x, yy + 7.5, x + 250, yy + 7.5, .1, 'opacity=".5"'); });
  T(x, y + 112, '고치는 순서: 배경 → 소품 → 인물. 인물(5)은 가장 많이 다시 뽑으므로 마지막에. 이름(7)은 미드저니가 아니라 후보정에서 — 글자가 깨지지 않는다.', 1.75, dim);
}

// ---------- 04 sentence → part ----------
{ const x = 268, y = 175; head(x, y, '04', 'STORY → PART', 'each sentence of the storyline and the part that carries it');
  [['나는 안에서 본다.', 'camera inside', EYE],
   ['가게 이름은 거꾸로 읽히고,', '7 name at eye level', RED],
   ['진열은 등을 보인다.', 'mannequin back · 1', EYE],
   ['유리 너머로 사람들의 얼굴이 보인다.', 'bright aisle', EYE],
   ['대부분은 그냥 지나간다.', '3 faceless passers-by', RED],
   ['가끔 누군가 걸음을 멈추고, 들여다보고, 웃는다.', '5 someone · smile kept', RED],
   ['나는 그 사람이 무엇을 보고 웃었는지 본다.', 'gaze → red scarf', RED],
   ['안에서 밖으로 쳐다보는 VMD가 되겠다.', 'my eye → their face', EYE]].forEach(([s, p, c], i) => {
    const yy = y + 10 + i * 6; C(x + 1.2, yy - .7, .6, .3, c, `stroke="${c}"`); FO(x + 3.5, yy - 3.1, 84, 6, s, 'fo s'); T(x + 90, yy, p, 1.7, `fill="${c}"`); });
}

// ---------- 05 title block ----------
{ const x = 268, y = 236; L(x - 4, y - 4, 414, y - 4, .3);
  T(x, y + 4, 'FROM THE INSIDE', 6.5, `${bold} letter-spacing="-.1"`); T(x, y + 10.5, 'JEONG HYEOKJU — visual merchandiser · cover edit plan', 2.6, bold);
  T(x, y + 16, '누구인지는 지우고, 미소는 남긴다.', 2.5, bold);
  [['Source', 'Midjourney image · edit_blueprint/source_midjourney.jpg'], ['Keep', 'mannequin back · red scarf · gaze to the scarf · black-and-white + one red'],
   ['Remove', 'fence · white scarf · "SHOP NAME" · faces of passers-by · portrait-like person'],
   ['Note', 'AI-generated person (fictional) · label as AI image · not affiliated with Shinsegae']].forEach(([a, t], i) => {
    T(x, y + 24 + i * 5.6, a.toUpperCase(), 1.6, `${dim} letter-spacing=".3"`); T(x + 14, y + 24 + i * 5.6, t, 1.75); });
}

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Cover edit blueprint</title><style>
@page{size:420mm 297mm;margin:0} html,body{margin:0;background:${NAVY}} svg{display:block;width:420mm;height:297mm}
text{fill:${INK};stroke:none;font-family:${F}} .d{fill:${DIM}} .m{font-family:${MONO};fill:#dbe7f2}
.fo{font-family:${F};color:#eef4fa;font-size:2.45px;line-height:1.4;padding-top:.6px} .fo.s{font-size:1.85px;color:#dbe7f2;padding-top:1.1px} .fo.m2{font-family:${MONO};color:#eef4fa}
</style></head><body><svg viewBox="0 0 420 297" xmlns="http://www.w3.org/2000/svg" stroke="${INK}" fill="none">
<defs><pattern id="g5" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M5 0H0V5" stroke="rgba(255,255,255,.05)" stroke-width=".15"/></pattern>
<pattern id="g25" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" stroke="rgba(255,255,255,.09)" stroke-width=".2"/></pattern>
<pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.6" stroke="rgba(255,255,255,.35)" stroke-width=".18"/></pattern></defs>
<rect width="420" height="297" fill="${NAVY}" stroke="none"/><rect width="420" height="297" fill="url(#g5)" stroke="none"/><rect width="420" height="297" fill="url(#g25)" stroke="none"/>
<rect x="6" y="6" width="408" height="285" stroke-width=".5"/><line x1="6" y1="167" x2="414" y2="167" stroke-width=".3"/><line x1="264" y1="167" x2="264" y2="291" stroke-width=".3"/>
${o}</svg></body></html>`;
const page = path.join(TMP, 'sheet.html'); fs.writeFileSync(page, html);
const b = await chromium.launch({ executablePath: exe });
const ctx = await b.newContext({ viewport: { width: 1587, height: 1123 }, deviceScaleFactor: 2 });
await ctx.route(u => !u.href.startsWith('file:'), r => r.abort());
const pg = await ctx.newPage(); await pg.goto(pathToFileURL(page).href, { waitUntil: 'load' }); await pg.waitForTimeout(300);
const pdf = path.join(OUT, 'cover_edit_blueprint.pdf'), jpg = path.join(OUT, 'cover_edit_blueprint_preview.jpg');
await pg.pdf({ path: pdf, width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
await pg.screenshot({ path: jpg, type: 'jpeg', quality: 88 });
await b.close();
console.log('산출물: ' + path.relative(repo, pdf)); console.log('산출물: ' + path.relative(repo, jpg));
