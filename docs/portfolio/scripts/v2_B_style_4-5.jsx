// v2 펼침 B (4–5쪽) · (001) STYLE — 템플릿 글을 원고로 바꾼다 (질문 두 개 + MY STYLE)
// 원고: docs/portfolio/v2_01_style.md 의 "B · 4–5쪽"
//
// 쓰는 법: InDesign 에서 문서를 연 채로 창 → 유틸리티 → 스크립트 → 사용자 폴더에 이 파일을 넣고 두 번 클릭.
//          (또는 파일 → 스크립트 → 스크립트 찾아보기)
// 되돌리기: 편집 → 실행 취소 한 번으로 전부 되돌린다.
// 4·5쪽 밖의 글 상자는 건드리지 않는다. 끝나면 바꾼 것 · 못 찾은 것 · 넘친 글 상자를 알려 준다.
// 펼침 A 스크립트(v2_A_style_2-3.jsx)와 순서는 상관없다.

var KOREAN_FONT_FALLBACKS = ["Source Han Sans KR\tRegular", "AppleGothic\tRegular"];

// 5쪽 오른쪽 위 머리말. 지우려면 "" 로 둔다
var HEADER_5 = "MOOD";

var Q1 =
    "Why is style important?" +
    "\r같은 흰 셔츠도 누가 입느냐에 따라 전혀 다르게 보인다. 소매를 걷는지, 단추를 어디까지 채우는지, 무엇과 같이 입는지. 그 차이가 스타일이다. " +
    "나는 그 사람이 무엇을 고르고, 무엇을 빼고, 무엇을 강조했는지를 본다. 좋은 공간도 무엇을 넣고 무엇을 뺄지 고르는 데서 시작한다.";

var Q2 =
    "What makes a good style?" +
    "\r좋은 스타일은 유행을 따라가는 것이 아니다. 그 사람에게 맞고, 꾸준하고, 편안한 것. " +
    "그런 사람은 멀리서 봐도 그 사람인 줄 안다. 좋은 공간도 그렇다. 들어가자마자 어디인지 알 수 있다.";

// 색 다섯 개 — 지면 캡처에서 잰 대략값. 인쇄 전에 원본 사진에서 다시 뽑아 여기만 고친다
var MY_STYLE_COLORS = [
    ["Black", "#1D1B19"],
    ["Olive", "#2C2716"],
    ["Beige", "#C4B29B"],
    ["Off-white", "#C3BFB1"],
    ["Slate", "#445162"]
];
var MY_STYLE_LINE = "헤어 스타일, 옷의 톤과 향의 무드를 그날 갈 장소에 맞춘다.";
var CHIP = "\u25A0"; // ■ — 글자색을 그 색으로 칠한다

// [쪽, 찾을 글, 바꿀 글] — 같은 글 상자 안에서 글자 서식을 그대로 두고 글만 바꾼다
// 템플릿 본문에도 "modular grids" 같은 말이 있어서, 본문을 먼저 바꾸고 라벨은 가장 짧은 글 상자에서 찾는다
var REPLACEMENTS = [
    ["4", "manuscript grids", "Shop front, evening"],
    ["4", "(single-column layouts)", "(black long coat)"],
    ["4", "column grids", "Riverside, night"],
    ["4", "(multiple vertical columns)", "(olive parka)"],
    ["5", "modular grids", "Park, sunset"],
    ["5", "(rows and columns forming modules)", "(light jacket)"]
];

// [쪽, 이 글이 들어 있는 글 상자를 지운다]
var REMOVALS = [
    ["4", "www.template.systems"],
    ["4", "Template.Systems"]
];

var LEFTOVER_PATTERN = /template|grid|download|www\./i;
var HANGUL = /[가-힣]/;

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

function frameStartingWith(page, start) {
    var frames = textFramesOn(page);
    for (var i = 0; i < frames.length; i++) {
        if (norm(frames[i].contents).indexOf(start) === 0) return frames[i];
    }
    return null;
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

// 한글이 든 단락에만 한글 글꼴을 입힌다. 영어 질문 제목 · MY STYLE 은 지면 글꼴 그대로
function applyKoreanFont(text, koFont) {
    var ps = text.paragraphs;
    for (var i = 0; i < ps.length; i++) {
        if (HANGUL.test(ps[i].contents)) ps[i].appliedFont = koFont;
    }
}

function swatchFor(doc, name, hex) {
    var swatchName = "MY STYLE " + name + " " + hex;
    var c = doc.colors.itemByName(swatchName);
    if (c.isValid) return c;
    var v = [parseInt(hex.substr(1, 2), 16), parseInt(hex.substr(3, 2), 16), parseInt(hex.substr(5, 2), 16)];
    return doc.colors.add({ name: swatchName, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: v });
}

function myStyleText() {
    // 칩 하나(■ 이름 값)는 줄바꿈되지 않게 붙인다
    var chips = [];
    for (var i = 0; i < MY_STYLE_COLORS.length; i++) {
        chips.push(CHIP + "\u00A0" + MY_STYLE_COLORS[i][0] + "\u00A0" + MY_STYLE_COLORS[i][1]);
    }
    return "MY STYLE\r" + chips.join("   ") + "\r" + MY_STYLE_LINE;
}

function colorChips(doc, text, koFont) {
    var s = text.contents, k = 0;
    for (var i = 0; i < s.length && k < MY_STYLE_COLORS.length; i++) {
        if (s.charAt(i) !== CHIP) continue;
        var ch = text.characters.item(i);
        ch.fillColor = swatchFor(doc, MY_STYLE_COLORS[k][0], MY_STYLE_COLORS[k][1]);
        if (koFont) ch.appliedFont = koFont; // 영문 글꼴에 ■ 가 없을 때를 막는다
        k++;
    }
    return k;
}

function run() {
    if (app.documents.length === 0) { alert("열린 문서가 없습니다."); return; }
    var doc = app.activeDocument;
    var log = [], missing = [], i, j;

    var pages = { "4": pageByName(doc, "4"), "5": pageByName(doc, "5") };
    if (!pages["4"] || !pages["5"]) { alert("4쪽 또는 5쪽을 찾지 못했습니다."); return; }

    var koFont = findKoreanFont(doc);
    if (!koFont) missing.push("한글 글꼴을 못 찾음 — 5쪽 한글 본문 글꼴을 직접 바꿔 주세요");

    // 1. 5쪽 본문 — 오른쪽 두 단락 → Q1 · Q2, 아래 한 단락 → MY STYLE
    var qFrame = frameStartingWith(pages["5"], "Common types include");
    var oFrame = frameStartingWith(pages["5"], "Overall, grid systems");
    if (qFrame && !oFrame && norm(qFrame.contents).indexOf("Overall, grid systems") > 0) {
        // 두 단락이 한 글 상자에 있다
        qFrame.texts[0].contents = Q1 + "\r" + Q2;
        if (koFont) applyKoreanFont(qFrame.texts[0], koFont);
        log.push("5쪽: 오른쪽 본문 두 단락 → Q1 · Q2");
    } else {
        if (qFrame) {
            qFrame.texts[0].contents = Q1;
            if (koFont) applyKoreanFont(qFrame.texts[0], koFont);
            log.push("5쪽: 오른쪽 첫째 단락 → Q1");
        } else missing.push("5쪽: \"Common types include…\" 본문");
        if (oFrame) {
            oFrame.texts[0].contents = Q2;
            if (koFont) applyKoreanFont(oFrame.texts[0], koFont);
            log.push("5쪽: 오른쪽 둘째 단락 → Q2");
        } else missing.push("5쪽: \"Overall, grid systems…\" 본문");
    }

    var mFrame = frameStartingWith(pages["5"], "A grid system is");
    if (mFrame) {
        var mt = mFrame.texts[0];
        mt.contents = myStyleText();
        if (koFont) applyKoreanFont(mt, koFont);
        var n = colorChips(doc, mt, koFont);
        log.push("5쪽: 아래 본문 → MY STYLE (색 칩 " + n + "개, 견본 'MY STYLE …' 추가)");
    } else missing.push("5쪽: \"A grid system is…\" 본문");

    // 2. 라벨 — 사진 캡션
    var saved = app.findChangeTextOptions.properties;
    app.findChangeTextOptions.caseSensitive = true;
    app.findChangeTextOptions.wholeWord = false;
    app.findChangeTextOptions.includeMasterPages = false;

    var reps = REPLACEMENTS.slice(0);
    reps.push(HEADER_5 ? ["5", "Grid Exploration 001", HEADER_5] : null);
    for (i = 0; i < reps.length; i++) {
        var r = reps[i];
        if (!r) continue;
        var frames = textFramesOn(pages[r[0]]), best = null;
        for (j = 0; j < frames.length; j++) {
            if (frames[j].contents.indexOf(r[1]) < 0) continue;
            if (!best || frames[j].contents.length < best.contents.length) best = frames[j];
        }
        resetFind();
        if (best) {
            app.findTextPreferences.findWhat = r[1];
            app.changeTextPreferences.changeTo = r[2];
        }
        if (best && best.texts[0].changeText().length > 0) log.push(r[0] + "쪽: " + r[1] + " → " + r[2]);
        else missing.push(r[0] + "쪽: " + r[1]);
    }
    resetFind();
    app.findChangeTextOptions.properties = saved;

    // 3. 템플릿 글 상자 지움
    var removals = REMOVALS.slice(0);
    if (!HEADER_5) removals.push(["5", "Grid Exploration 001"]);
    for (i = 0; i < removals.length; i++) {
        var rm = removals[i], rmFrames = textFramesOn(pages[rm[0]]), removed = false;
        for (j = 0; j < rmFrames.length; j++) {
            if (rmFrames[j].contents.indexOf(rm[1]) >= 0) {
                log.push(rm[0] + "쪽: 글 상자 지움 (" + norm(rmFrames[j].contents) + ")");
                rmFrames[j].remove();
                removed = true;
                break;
            }
        }
        if (!removed) missing.push(rm[0] + "쪽: " + rm[1] + " 상자");
    }

    if (koFont) log.push("한글 글꼴: " + fontLabel(koFont));

    var overflow = [], leftover = [];
    for (var pn in pages) {
        var fs = textFramesOn(pages[pn]);
        for (j = 0; j < fs.length; j++) {
            if (fs[j].overflows) overflow.push(pn + "쪽: " + norm(fs[j].contents).substr(0, 30) + "…");
            if (LEFTOVER_PATTERN.test(fs[j].contents)) leftover.push(pn + "쪽: " + norm(fs[j].contents).substr(0, 40));
        }
    }

    var msg = "바꾼 것 (" + log.length + ")\n" + log.join("\n");
    if (missing.length) msg += "\n\n못 찾은 것 (" + missing.length + ")\n" + missing.join("\n");
    if (overflow.length) msg += "\n\n넘친 글 상자 — 상자를 키우거나 글을 줄이세요\n" + overflow.join("\n");
    if (leftover.length) msg += "\n\n남은 템플릿 글\n" + leftover.join("\n");
    alert(msg);
}

app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "v2 B · STYLE 4–5쪽");
