// v2 펼침 A (2–3쪽) · (001) STYLE — 템플릿 글을 원고로 바꾼다
// 원고: docs/portfolio/v2_01_style.md
//
// 쓰는 법: InDesign 에서 문서를 연 채로 창 → 유틸리티 → 스크립트 → 사용자 폴더에 이 파일을 넣고 두 번 클릭.
//          (또는 파일 → 스크립트 → 스크립트 찾아보기)
// 되돌리기: 편집 → 실행 취소 한 번으로 전부 되돌린다.
// 2·3쪽 밖의 글 상자는 건드리지 않는다. 끝나면 바꾼 것 · 못 찾은 것 · 넘친 글 상자를 알려 준다.

var KOREAN_FONT_FALLBACKS = ["Source Han Sans KR\tRegular", "AppleGothic\tRegular"];

var OPENING_KO =  // 이름은 그대로 두었다 — 본문은 영어(지원자 결정)
    "The first place I stop is the street. When someone with good style walks by, I stop: " +
    "their hair, their glasses, their clothes and shoes, the accessories they wear, and how the colors go together. " +
    "Sometimes it's the scent they leave behind that makes me turn around." +
    "\rSo my first story is about style.";

// [쪽, 찾을 글, 바꿀 글] — 같은 글 상자 안에서 글자 서식을 그대로 두고 글만 바꾼다
var REPLACEMENTS = [
        ["2", "© 2026 Template.Systems", "Jeong Hyeokju"],
    ["2", "A Person With Style", "A Person with Style"],
    ["2", "column grids", "Sunglasses"],
    ["2", "(multiple vertical columns)", "(on a wet street, at night)"],
    ["3", "modular grids", "Where I stop"],
    ["3", "(rows and columns forming modules)", "(on the street)"]
];

// [쪽, 이 글이 들어 있는 글 상자를 지운다]
var REMOVALS = [
    ["2", "www.template.systems"],
    ["2", "Grid Systems 001"]  // 3쪽에 큰 (001) 이 있다
];

// [쪽, 이 글로 시작하는 글 상자의 글 전체를 바꾼다, 바꿀 글, 한글 글꼴 적용]
var BODY_REPLACEMENTS = [
    ["3", "A grid system is a structured framework", OPENING_KO, false]
];

var LEFTOVER_PATTERN = /template|grid|download|www\./i;

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

function resetFind() {
    app.findTextPreferences = NothingEnum.NOTHING;
    app.changeTextPreferences = NothingEnum.NOTHING;
}

function run() {
    if (app.documents.length === 0) { alert("열린 문서가 없습니다."); return; }
    var doc = app.activeDocument;
    var log = [], missing = [], i, j;

    var pages = { "2": pageByName(doc, "2"), "3": pageByName(doc, "3") };
    if (!pages["2"] || !pages["3"]) { alert("2쪽 또는 3쪽을 찾지 못했습니다."); return; }

    var saved = app.findChangeTextOptions.properties;
    app.findChangeTextOptions.caseSensitive = true;
    app.findChangeTextOptions.wholeWord = false;
    app.findChangeTextOptions.includeMasterPages = false;

    for (i = 0; i < REPLACEMENTS.length; i++) {
        var r = REPLACEMENTS[i], frames = textFramesOn(pages[r[0]]), done = false;
        for (j = 0; j < frames.length && !done; j++) {
            if (frames[j].contents.indexOf(r[1]) < 0) continue;
            resetFind();
            app.findTextPreferences.findWhat = r[1];
            app.changeTextPreferences.changeTo = r[2];
            if (frames[j].texts[0].changeText().length > 0) {
                log.push(r[0] + "쪽: " + r[1] + " → " + r[2]);
                done = true;
            }
        }
        if (!done) missing.push(r[0] + "쪽: " + r[1]);
    }
    resetFind();

    for (i = 0; i < REMOVALS.length; i++) {
        var rm = REMOVALS[i], rmFrames = textFramesOn(pages[rm[0]]), removed = false;
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

    var koFont = findKoreanFont(doc);
    for (i = 0; i < BODY_REPLACEMENTS.length; i++) {
        var b = BODY_REPLACEMENTS[i], bFrames = textFramesOn(pages[b[0]]), replaced = false;
        for (j = 0; j < bFrames.length; j++) {
            if (norm(bFrames[j].contents).indexOf(b[1]) !== 0) continue;
            var t = bFrames[j].texts[0];
            t.contents = b[2];
            if (b[3]) {
                if (koFont) t.appliedFont = koFont;
                else missing.push(b[0] + "쪽: 한글 글꼴을 못 찾음 — 본문 글꼴을 직접 바꿔 주세요");
            }
            var fontName = koFont ? String(typeof koFont === "string" ? koFont : koFont.name).replace("\t", " ") : "";
            log.push(b[0] + "쪽: 본문 → 여는 글" + (b[3] && koFont ? " (글꼴 " + fontName + ")" : ""));
            replaced = true;
            break;
        }
        if (!replaced) missing.push(b[0] + "쪽: \"" + b[1] + "…\" 본문");
    }

    app.findChangeTextOptions.properties = saved;

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

app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "v2 A · STYLE 2–3쪽");
