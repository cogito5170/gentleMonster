// v2 펼침 D (8–9쪽) · 다리 ① STYLE → PICTURE — 풀쿼트 글자 색 · 강조 · 줄 나눔을 고치고 템플릿 글을 지운다
// 원고: docs/portfolio/v2_D_bridge_8-9.md
//
// 쓰는 법: InDesign 에서 문서를 연 채로 창 → 유틸리티 → 스크립트 → 사용자 폴더에 이 파일을 넣고 두 번 클릭.
//          (또는 파일 → 스크립트 → 스크립트 찾아보기)
// 되돌리기: 편집 → 실행 취소 한 번으로 전부 되돌린다.
// 8·9쪽 밖의 글 상자는 건드리지 않는다. 끝나면 바꾼 것 · 못 찾은 것 · 넘친 글 상자 · 접힘을 넘는 상자를 알려 준다.

// 풀쿼트: 1줄 · 2줄
var QUOTE_LINES = ["I stop for people", "whose style is their own."];

// 마젠타로 칠할 말. 세 곳으로 하려면 "whose" 를 더한다
var EMPHASIS = ["stop", "their own"];

// 바탕 글자 색: "Black" = [Black] 견본, "#1D1B19" 처럼 쓰면 그 색 견본을 만든다
var BASE = "Black";

// 줄 나눔을 QUOTE_LINES 대로 맞춘다. 지금 줄 나눔을 그대로 두려면 false
var FIX_LINE_BREAK = true;

// 지금 쓰는 마젠타를 못 찾을 때 만드는 견본 (CMYK)
var MAGENTA_NAME = "SPA Magenta", MAGENTA_CMYK = [0, 100, 0, 0];

// 이 글만으로 된 글 상자는 템플릿 글이라 지운다
var TEMPLATE_PHRASES = [
    /©\s*\d{4}\s*Template\.?\s*Systems/gi,
    /www\.template\.systems/gi,
    /download now/gi,
    /Template\s+Systems/gi,
    /(Experimental\s+)?Grid\s+(Systems|Exploration)(\s+Series)?(\s+\d+)?/gi,
    /\bSeries\b/gi,
    /(column|modular|manuscript|baseline|hierarchical)\s+grids/gi,
    /\([^)]*(column|row|layout|module)s?[^)]*\)/gi
];
var EMPTY_AFTER_STRIP = /^[\s.,·:;|\/()\-\u2013\u2014]*$/;
var LEFTOVER_PATTERN = /template|grid|download|www\.|^\s*series\s*$/i;

function norm(s) {
    return String(s).replace(/[\r\n\u2028\u2029]+/g, " ").replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
}

// 비교용: 따옴표 빼고, 줄바꿈 · 띄어쓰기 하나로, 소문자
function qnorm(s) {
    return norm(String(s).replace(/[\u201C\u201D\u2018\u2019"']/g, "")).toLowerCase();
}

function caseLike(original, line) {
    var letters = String(original).replace(/[^A-Za-z]/g, "");
    return (letters.length && letters === letters.toUpperCase()) ? line.toUpperCase() : line;
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

function resetGrep() {
    app.findGrepPreferences = NothingEnum.NOTHING;
    app.changeGrepPreferences = NothingEnum.NOTHING;
}

function baseSwatch(doc) {
    if (BASE.charAt(0) === "#") {
        var hex = BASE.substr(1).toUpperCase(), name = "SPA " + hex;
        var c = doc.colors.itemByName(name);
        if (c.isValid) return c;
        return doc.colors.add({
            name: name, model: ColorModel.PROCESS, space: ColorSpace.RGB,
            colorValue: [parseInt(hex.substr(0, 2), 16), parseInt(hex.substr(2, 2), 16), parseInt(hex.substr(4, 2), 16)]
        });
    }
    var s = doc.swatches.itemByName(BASE);
    if (s.isValid) return s;
    // 견본 이름이 다른 언어판일 때: CMYK 0/0/0/100 견본
    for (var i = 0; i < doc.colors.length; i++) {
        try {
            var v = doc.colors[i].colorValue;
            if (doc.colors[i].space === ColorSpace.CMYK && v[0] === 0 && v[1] === 0 && v[2] === 0 && v[3] === 100) return doc.colors[i];
        } catch (e) {}
    }
    return null;
}

// 강조색 = 풀쿼트에서 가장 적은 글자에 쓰인 색 (바탕 글자보다 강조 글자가 적다)
function emphasisSwatch(doc, stories) {
    var count = {}, swatch = {}, names = [], i, j;
    for (i = 0; i < stories.length; i++) {
        var ranges = stories[i].textStyleRanges;
        for (j = 0; j < ranges.length; j++) {
            var fc = ranges[j].fillColor, name = fc.name;
            if (name === "None" || !norm(ranges[j].contents)) continue;
            if (!(name in count)) { count[name] = 0; swatch[name] = fc; names.push(name); }
            count[name] += ranges[j].characters.length;
        }
    }
    if (names.length >= 2) {
        var pick = names[0];
        for (i = 1; i < names.length; i++) if (count[names[i]] < count[pick]) pick = names[i];
        return { swatch: swatch[pick], found: true };
    }
    var m = doc.colors.itemByName(MAGENTA_NAME);
    if (!m.isValid) {
        m = doc.colors.add({ name: MAGENTA_NAME, model: ColorModel.PROCESS, space: ColorSpace.CMYK, colorValue: MAGENTA_CMYK });
    }
    return { swatch: m, found: false };
}

function topLeft(frame) {
    var b = frame.visibleBounds;
    return [b[0], b[1]];
}

function byPosition(a, b) {
    var pa = topLeft(a.frame), pb = topLeft(b.frame);
    if (Math.abs(pa[0] - pb[0]) > 1) return pa[0] - pb[0];
    return pa[1] - pb[1];
}

function fixLineBreak(units, full, log, missing) {
    if (units.length === 1) {
        var text = units[0].story.texts[0], c = String(text.contents);
        if (qnorm(c) !== full) { missing.push("줄 나눔: 풀쿼트 상자에 문장 전체가 없어 그대로 둠"); return; }
        var sep = c.indexOf("\r") >= 0 ? "\r" : "\n";
        var target = caseLike(c, QUOTE_LINES[0]) + sep + caseLike(c, QUOTE_LINES[1]);
        if (c !== target) {
            text.contents = target;
            log.push("줄 나눔: " + QUOTE_LINES[0] + " / " + QUOTE_LINES[1]);
        }
        return;
    }
    if (units.length === QUOTE_LINES.length) {
        var joined = [], i;
        for (i = 0; i < units.length; i++) joined.push(units[i].story.contents);
        if (qnorm(joined.join(" ")) !== full) { missing.push("줄 나눔: 풀쿼트 상자들을 이어도 문장이 되지 않아 그대로 둠"); return; }
        for (i = 0; i < units.length; i++) {
            var t = units[i].story.texts[0], line = caseLike(t.contents, QUOTE_LINES[i]);
            if (qnorm(t.contents) !== qnorm(line)) {
                t.contents = line;
                log.push("줄 나눔: " + (i + 1) + "줄 → " + line);
            }
        }
        return;
    }
    missing.push("줄 나눔: 풀쿼트 상자가 " + units.length + "개라 그대로 둠");
}

function stripTemplate(s) {
    var out = String(s);
    for (var i = 0; i < TEMPLATE_PHRASES.length; i++) out = out.replace(TEMPLATE_PHRASES[i], "");
    return out;
}

function run() {
    if (app.documents.length === 0) { alert("열린 문서가 없습니다."); return; }
    var doc = app.activeDocument;
    var log = [], missing = [], i, j, pn;

    var pages = { "8": pageByName(doc, "8"), "9": pageByName(doc, "9") };
    if (!pages["8"] || !pages["9"]) { alert("8쪽 또는 9쪽을 찾지 못했습니다."); return; }

    var savedOrigin = doc.viewPreferences.rulerOrigin;
    doc.viewPreferences.rulerOrigin = RulerOrigin.SPREAD_ORIGIN;  // 8 · 9쪽 상자 위치를 한 좌표로 비교한다

    try {
        // 1. 풀쿼트 찾기: 문장의 일부(또는 전체)만 들어 있는 글 상자. 이어진 상자는 한 글로 본다
        var full = qnorm(QUOTE_LINES.join(" "));
        var units = [], seen = {}, frames = [], quoteFrames = [];
        for (pn in pages) frames = frames.concat(textFramesOn(pages[pn]));
        for (i = 0; i < frames.length; i++) {
            var story = frames[i].parentStory, n = qnorm(story.contents);
            if (n.length < 4 || full.indexOf(n) < 0) continue;
            quoteFrames.push(frames[i]);
            if (seen[story.id]) continue;
            seen[story.id] = true;
            units.push({ story: story, frame: story.textContainers[0] });
        }
        if (!units.length) {
            missing.push("풀쿼트 \"" + QUOTE_LINES.join(" ") + "\" 글 상자");
        } else {
            units.sort(byPosition);
            var stories = [];
            for (i = 0; i < units.length; i++) stories.push(units[i].story);

            // 2. 색 — 줄 나눔을 바꾸면 글자 색이 하나로 합쳐지므로 강조색을 먼저 읽어 둔다
            var emph = emphasisSwatch(doc, stories), base = baseSwatch(doc);
            log.push("강조색: " + emph.swatch.name + (emph.found ? " (지면에서 읽음)" : " (새로 만듦)"));

            // 3. 줄 나눔
            if (FIX_LINE_BREAK) fixLineBreak(units, full, log, missing);

            // 4. 바탕 글자 → 짙은 색, 강조 말 → 마젠타
            if (base) {
                for (i = 0; i < stories.length; i++) stories[i].texts[0].fillColor = base;
                log.push("바탕 글자: " + base.name);
            } else {
                missing.push("바탕 글자 색 견본 " + BASE + " — 글자 색을 직접 바꿔 주세요");
            }
            for (j = 0; j < EMPHASIS.length; j++) {
                var hits = 0;
                for (i = 0; i < stories.length; i++) {
                    resetGrep();
                    app.findGrepPreferences.findWhat = "(?i)\\b" + EMPHASIS[j].replace(/ /g, "\\s+") + "\\b";
                    var found = stories[i].findGrep();
                    for (var k = 0; k < found.length; k++) found[k].fillColor = emph.swatch;
                    hits += found.length;
                }
                resetGrep();
                if (hits) log.push("강조: " + EMPHASIS[j]);
                else missing.push("강조할 말 \"" + EMPHASIS[j] + "\"");
            }
        }

        // 5. 템플릿 글 상자 지우기
        for (pn in pages) {
            var fs = textFramesOn(pages[pn]);
            for (j = 0; j < fs.length; j++) {
                var c = String(fs[j].contents);
                if (!norm(c) || !LEFTOVER_PATTERN.test(c)) continue;
                if (EMPTY_AFTER_STRIP.test(stripTemplate(c))) {
                    log.push(pn + "쪽: 글 상자 지움 (" + norm(c) + ")");
                    fs[j].remove();
                }
            }
        }

        // 6. 확인: 넘친 상자 · 남은 템플릿 글 · 접힘을 넘는 풀쿼트 상자
        var overflow = [], leftover = [], fold = [];
        for (pn in pages) {
            var rest = textFramesOn(pages[pn]);
            for (j = 0; j < rest.length; j++) {
                if (rest[j].overflows) overflow.push(pn + "쪽: " + norm(rest[j].contents).substr(0, 30) + "…");
                if (LEFTOVER_PATTERN.test(rest[j].contents)) leftover.push(pn + "쪽: " + norm(rest[j].contents).substr(0, 40));
            }
        }
        for (i = 0; i < quoteFrames.length; i++) {
            var f = quoteFrames[i], fb = f.visibleBounds, page = f.parentPage;
            if (!page) continue;
            var pb = page.bounds;
            if (fb[1] < pb[1] - 0.5 || fb[3] > pb[3] + 0.5) fold.push(page.name + "쪽: " + norm(f.contents).substr(0, 30));
        }
    } finally {
        doc.viewPreferences.rulerOrigin = savedOrigin;
    }

    var msg = "바꾼 것 (" + log.length + ")\n" + log.join("\n");
    if (missing.length) msg += "\n\n못 찾은 것 (" + missing.length + ")\n" + missing.join("\n");
    if (overflow.length) msg += "\n\n넘친 글 상자 — 상자를 키우거나 글을 줄이세요\n" + overflow.join("\n");
    if (fold.length) msg += "\n\n쪽 밖으로 나간 풀쿼트 상자 — 접힘에 걸리는 글자가 없는지 보세요\n" + fold.join("\n");
    if (leftover.length) msg += "\n\n남은 템플릿 글\n" + leftover.join("\n");
    alert(msg);
}

app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "v2 D · 다리 8–9쪽");
