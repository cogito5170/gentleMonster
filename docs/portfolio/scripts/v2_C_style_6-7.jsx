// v2 펼침 C (6–7쪽) · (001) STYLE 작업: DAILY LookBook — 템플릿 글을 원고로 바꾼다
// 원고: docs/portfolio/v2_01_style.md
//
// 쓰는 법: InDesign 에서 문서를 연 채로 창 → 유틸리티 → 스크립트 → 사용자 폴더에 이 파일을 넣고 두 번 클릭.
//          (또는 파일 → 스크립트 → 스크립트 찾아보기)
// 되돌리기: 편집 → 실행 취소 한 번으로 전부 되돌린다.
// 이 파일 하나로 돈다. 다른 펼침 스크립트(A 등)를 먼저 돌리지 않아도 되고, 순서도 상관없다.
// 6·7쪽 밖의 글 상자는 건드리지 않는다. 화면 그림 안의 오타는 그림 원본에서 고친다(6단계).
// 끝나면 바꾼 것 · 못 찾은 것 · 넘친 글 상자 · 남은 템플릿 글 · 채울 빈칸(____)을 알려 준다.

var KOREAN_FONT_FALLBACKS = ["Source Han Sans KR\tRegular", "AppleGothic\tRegular"];

var WORK_INTRO =
    "DAILY LookBook" +
    "\rWeb design · University project · ____ · Photoshop + Illustrator" +
    "\r사람의 스타일을 고르는 눈으로 화면도 만들었다. " +
    "DAILY LookBook 은 매일의 옷차림을 모아 보는 스타일 사이트다. " +
    "다른 사람의 하루 옷차림을 보고, 스타일 범주(Dandy · Casual · Street · Amekaji · Office)로 고르고, " +
    "마음에 든 옷을 바로 찾는다.";

var MARKET_NOTE = "MARKET 화면은 색 · 핏 · 길이 · 무늬 · 소재로 옷을 거른다. ____";

// [이 글로 시작하는 본문, 바꿀 글] — 같은 상자에 두 본문이 함께 있어도 각 본문 자리만 바꾼다
var BODIES = [
    ["Grid systems are widely used", WORK_INTRO, "본문 → 작업 소개"],
    ["Common types include", MARKET_NOTE, "본문 → MARKET 화면 설명"]
];

// 라벨 두 개는 같은 템플릿 글이다. MAIN 화면(7쪽 안에 들어 있는 작은 그림)에 가까운 쪽이 MAIN.
var LABEL_FIND = ["manuscript grids", "(single-column layouts)"];
var LABEL_MARKET = ["MARKET", "(product list)"];
var LABEL_MAIN = ["MAIN", "(home)"];

var LEFTOVER_PATTERN = /template|grid|download|www\.|manuscript|common types/i;

function norm(s) {
    return String(s).replace(/[\r\n\u2028\u2029]+/g, " ").replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
}

function pageByName(doc, name) {
    var p = doc.pages.itemByName(name);
    if (p.isValid) return p;
    var i = parseInt(name, 10) - 1;
    return (i >= 0 && i < doc.pages.length) ? doc.pages[i] : null;
}

function textFramesOn(page) {
    var out = [];
    var items = page.allPageItems;
    for (var i = 0; i < items.length; i++) {
        if (items[i].constructor.name === "TextFrame") out.push(items[i]);
    }
    return out;
}

function resetFind() {
    app.findTextPreferences = NothingEnum.NOTHING;
    app.changeTextPreferences = NothingEnum.NOTHING;
}

function findKoreanFont(doc) {
    // 이미 지면에 있는 한글 본문(PICTURE 의 "카메라를 들면…")과 같은 글꼴을 쓴다
    resetFind();
    app.findTextPreferences.findWhat = "카메라를";
    var hits = doc.findText();
    resetFind();
    if (hits.length > 0) return hits[0].appliedFont;
    for (var i = 0; i < KOREAN_FONT_FALLBACKS.length; i++) {
        var f = app.fonts.itemByName(KOREAN_FONT_FALLBACKS[i]);
        if (f.isValid) return f;
    }
    return null;
}

function fontLabel(f) {
    return String(typeof f === "string" ? f : f.name).replace("\t", " ");
}

function center(item) {
    var b = item.geometricBounds; // [위, 왼쪽, 아래, 오른쪽]
    return [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
}

function distance(a, b) {
    var ca = center(a), cb = center(b);
    return Math.sqrt(Math.pow(ca[0] - cb[0], 2) + Math.pow(ca[1] - cb[1], 2));
}

// 7쪽 안에 완전히 들어 있는 그림 중 가장 작은 것 = MAIN 화면 (MARKET 화면은 6쪽에서 넘어온다)
function mainScreenFrame(page) {
    var pb = page.bounds, best = null, bestArea = 0;
    var graphics = page.allGraphics;
    for (var i = 0; i < graphics.length; i++) {
        var fr = graphics[i].parent, b = fr.geometricBounds;
        if (b[1] < pb[1] || b[3] > pb[3]) continue;
        var area = (b[2] - b[0]) * (b[3] - b[1]);
        if (!best || area < bestArea) { best = fr; bestArea = area; }
    }
    return best;
}

// 본문 자리 하나: key 로 시작하는 문단부터, 다음 본문 key 로 시작하는 문단 앞까지(없으면 상자 끝까지)
function replaceBody(frames, keyIndex) {
    var key = BODIES[keyIndex][0];
    for (var j = 0; j < frames.length; j++) {
        var paras = frames[j].paragraphs, start = -1, end = -1, k, m;
        for (k = 0; k < paras.length; k++) {
            if (norm(paras[k].contents).indexOf(key) === 0) { start = k; break; }
        }
        if (start < 0) continue;
        end = paras.length - 1;
        for (k = start + 1; k < paras.length && end === paras.length - 1; k++) {
            for (m = 0; m < BODIES.length; m++) {
                if (m !== keyIndex && norm(paras[k].contents).indexOf(BODIES[m][0]) === 0) { end = k - 1; break; }
            }
        }
        var range = paras.itemByRange(start, end);
        var keepBreak = /\r$/.test(range.contents);
        range.contents = BODIES[keyIndex][1] + (keepBreak ? "\r" : "");
        return frames[j].paragraphs.itemByRange(start, start + BODIES[keyIndex][1].split("\r").length - 1);
    }
    return null;
}

function changeIn(frame, from, to) {
    resetFind();
    app.findTextPreferences.findWhat = from;
    app.changeTextPreferences.changeTo = to;
    var n = frame.texts[0].changeText().length;
    resetFind();
    return n > 0;
}

function run() {
    if (app.documents.length === 0) { alert("열린 문서가 없습니다."); return; }
    var doc = app.activeDocument;
    var log = [], missing = [], i, j;

    var pages = { "6": pageByName(doc, "6"), "7": pageByName(doc, "7") };
    if (!pages["6"] || !pages["7"]) { alert("6쪽 또는 7쪽을 찾지 못했습니다."); return; }

    var saved = app.findChangeTextOptions.properties;
    app.findChangeTextOptions.caseSensitive = true;
    app.findChangeTextOptions.wholeWord = false;
    app.findChangeTextOptions.includeMasterPages = false;

    // 본문 두 자리 (7쪽에 있다. 접힘 쪽으로 옮겨 놓았을 수 있어 6쪽도 본다)
    var bodyFrames = textFramesOn(pages["7"]).concat(textFramesOn(pages["6"]));
    var koFont = findKoreanFont(doc);
    for (i = 0; i < BODIES.length; i++) {
        var replaced = replaceBody(bodyFrames, i);
        if (!replaced) { missing.push("7쪽: \"" + BODIES[i][0] + "…\" 본문"); continue; }
        if (koFont) replaced.appliedFont = koFont;
        else missing.push("7쪽: 한글 글꼴을 못 찾음 — " + BODIES[i][2].replace("본문 → ", "") + " 글꼴을 직접 바꿔 주세요");
        log.push("7쪽: " + BODIES[i][2] + (koFont ? " (글꼴 " + fontLabel(koFont) + ")" : ""));
    }

    // 라벨 두 개
    var labels = [];
    for (var pn in pages) {
        var lf = textFramesOn(pages[pn]);
        for (j = 0; j < lf.length; j++) {
            if (lf[j].contents.indexOf(LABEL_FIND[0]) >= 0) labels.push(lf[j]);
        }
    }
    if (labels.length < 2) {
        missing.push("6·7쪽: \"" + LABEL_FIND[0] + "\" 라벨 두 개 (찾은 것 " + labels.length + "개)");
    }
    if (labels.length > 0) {
        var mainFrame = mainScreenFrame(pages["7"]), mainIndex = -1, rule = "";
        if (labels.length > 1 && mainFrame) {
            mainIndex = 0;
            for (j = 1; j < labels.length; j++) {
                if (distance(labels[j], mainFrame) < distance(labels[mainIndex], mainFrame)) mainIndex = j;
            }
            rule = "MAIN 화면 그림에 가까운 라벨";
        } else if (labels.length > 1) {
            // 그림을 못 찾으면 아래쪽(같으면 오른쪽) 라벨을 MAIN 으로 둔다 — MAIN 화면이 오른쪽 아래에 있다
            mainIndex = 0;
            for (j = 1; j < labels.length; j++) {
                var a = labels[j].geometricBounds, c = labels[mainIndex].geometricBounds;
                if (a[0] > c[0] || (a[0] === c[0] && a[1] > c[1])) mainIndex = j;
            }
            rule = "MAIN 화면 그림을 못 찾아 아래쪽 라벨";
        }
        var marketIndex = (mainIndex === 0) ? 1 : 0;
        var plan = [[marketIndex, LABEL_MARKET, ""]];
        if (mainIndex >= 0) plan.push([mainIndex, LABEL_MAIN, " (" + rule + " — 반대면 두 라벨 글을 맞바꿔 주세요)"]);
        for (j = 0; j < plan.length; j++) {
            var fr = labels[plan[j][0]], to = plan[j][1];
            var ok = changeIn(fr, LABEL_FIND[0], to[0]);
            changeIn(fr, LABEL_FIND[1], to[1]);
            if (ok) log.push("7쪽: 라벨 → " + to[0] + " " + to[1] + plan[j][2]);
        }
    }

    app.findChangeTextOptions.properties = saved;

    var overflow = [], leftover = [], blanks = [];
    for (var qn in pages) {
        var fs = textFramesOn(pages[qn]);
        for (j = 0; j < fs.length; j++) {
            var line = norm(fs[j].contents);
            if (fs[j].overflows) overflow.push(qn + "쪽: " + line.substr(0, 30) + "…");
            if (LEFTOVER_PATTERN.test(line.replace(/DAILY LookBook/g, ""))) leftover.push(qn + "쪽: " + line.substr(0, 40));
            for (var at = line.indexOf("____"); at >= 0; at = line.indexOf("____", at + 4)) {
                blanks.push(qn + "쪽: …" + line.substr(Math.max(0, at - 20), 24) + "…");
            }
        }
    }

    var msg = "바꾼 것 (" + log.length + ")\n" + log.join("\n");
    if (missing.length) msg += "\n\n못 찾은 것 (" + missing.length + ")\n" + missing.join("\n");
    if (overflow.length) msg += "\n\n넘친 글 상자 — 상자를 키우거나 글을 줄이세요\n" + overflow.join("\n");
    if (leftover.length) msg += "\n\n남은 템플릿 글\n" + leftover.join("\n");
    if (blanks.length) msg += "\n\n채울 빈칸 (____) — 연도 · MARKET 화면에서 정한 것\n" + blanks.join("\n");
    alert(msg);
}

app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "v2 C · STYLE 6–7쪽");
