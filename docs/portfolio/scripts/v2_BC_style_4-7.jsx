// v2 펼침 B · C (4–7쪽) · (001) STYLE — 템플릿 글을 원고로 바꾼다
// 원고: docs/portfolio/v2_01_style.md 의 "B · 4–5쪽" · "C · 6–7쪽"
//
// 쓰는 법: InDesign 에서 문서를 연 채로 창 → 유틸리티 → 스크립트 → 사용자 폴더에 이 파일을 넣고 두 번 클릭.
//          (또는 파일 → 스크립트 → 스크립트 찾아보기)
// 되돌리기: 편집 → 실행 취소 한 번으로 전부 되돌린다.
// 쪽 번호가 아니라 템플릿 글로 펼침을 찾는다. 그래서 4–7쪽만 떼어 낸 문서에서도, 28쪽 전체 문서에서도 같다.
// B · C 펼침 밖의 글 상자는 건드리지 않는다. 끝나면 바꾼 것 · 못 찾은 것 · 넘친 글 상자 · 다른 쪽의 글을 알려 준다.

var KOREAN_FONT_FALLBACKS = ["Source Han Sans KR\tRegular", "Apple SD Gothic Neo\tRegular", "AppleGothic\tRegular"];

var NBSP = String.fromCharCode(0x00A0);
var CHIP = String.fromCharCode(0x25A0); // ■ — 글자색을 그 색으로 칠한다
var LINE_BREAKS = new RegExp("[\\r\\n" + String.fromCharCode(0x2028, 0x2029) + "]+", "g");
var HANGUL = new RegExp("[" + String.fromCharCode(0xAC00) + "-" + String.fromCharCode(0xD7A3) + "]");

// ---------------------------------------------------------------- B · 4–5쪽

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

// [찾을 글, 바꿀 글] — 펼침 안에서 이 글이 든 가장 짧은 글 상자(라벨)를 찾아 글만 바꾼다
// 파카 사진이 한강이면 "Riverside, night" 를 "Han River, night" 로
var B_LABELS = [
    ["manuscript grids", "Shop front, evening"],
    ["(single-column layouts)", "(black long coat)"],
    ["column grids", "Riverside, night"],
    ["(multiple vertical columns)", "(olive parka)"],
    ["modular grids", "Park, sunset"],
    ["(rows and columns forming modules)", "(light jacket)"]
];

// 이 글이 든 글 상자를 지운다
var B_REMOVALS = ["www.template.systems", "Template.Systems"];

// ---------------------------------------------------------------- C · 6–7쪽

// 지원자가 채울 사실 — 비워 두면 그 칸은 지면에 나오지 않는다
var C_YEAR = "";   // 예: "2023"
var C_ROLE = "";   // 예: "Solo project" 또는 "Team of 4 — UI design"

function cMetaLine() {
    var parts = ["Web design", "University project"];
    if (C_YEAR) parts.push(C_YEAR);
    if (C_ROLE) parts.push(C_ROLE);
    parts.push("Photoshop + Illustrator");
    return parts.join(" · ");
}

function cIntro() {
    return "DAILY LookBook" +
        "\r" + cMetaLine() +
        "\r사람의 스타일을 고르는 눈으로 화면도 만들었다. " +
        "DAILY LookBook은 매일의 옷차림을 모아 보는 스타일 사이트다. 다른 사람의 하루 옷차림을 보고, " +
        "스타일 범주(Dandy · Casual · Street · Amekaji · Office)로 고르고, 마음에 든 옷을 바로 찾는다.";
}

// 화면(MARKET)에 실제로 있는 것만 쓴다: FILTER 의 Color · Fit · Length · Pattern · Material,
// "이름_색" 상품명, 원래 값 > 할인된 값
var C_MARKET =
    "MARKET 화면은 색 · 핏 · 길이 · 무늬 · 소재로 옷을 거른다. 길에서 사람을 볼 때 눈에 들어오는 것들이다. " +
    "상품 이름 뒤에는 색을 붙이고(Balmacan Wool Coat_Black), 값 옆에 할인된 값을 함께 두어 룩북에서 본 옷을 바로 찾게 했다.";

// 7쪽 라벨 두 개("manuscript grids" ×2). 작은 화면(메인)에 가까운 라벨이 MAIN, 다른 하나가 MARKET
var C_LABEL_MARKET = ["MARKET", "(product list)"];
var C_LABEL_MAIN = ["MAIN", "(home)"];

var LEFTOVER_PATTERN = /template|grid|download|www\./i;

// ---------------------------------------------------------------- 도구

function norm(s) {
    return String(s).replace(LINE_BREAKS, " ").replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
}

function textFramesIn(container) {
    var out = [];
    var items = container.allPageItems;
    for (var i = 0; i < items.length; i++) {
        if (items[i].constructor.name === "TextFrame") out.push(items[i]);
    }
    return out;
}

function frameStartingWith(container, start) {
    var frames = textFramesIn(container);
    for (var i = 0; i < frames.length; i++) {
        if (norm(frames[i].contents).indexOf(start) === 0) return frames[i];
    }
    return null;
}

// 서명 글이 모두 든 쪽을 찾는다. 여러 쪽이면 이름이 preferName 인 쪽을 고른다
function findPage(doc, starts, preferName) {
    var hits = [];
    for (var i = 0; i < doc.pages.length; i++) {
        var ok = true;
        for (var k = 0; k < starts.length && ok; k++) ok = frameStartingWith(doc.pages[i], starts[k]) !== null;
        if (ok) hits.push(doc.pages[i]);
    }
    for (i = 0; i < hits.length; i++) if (hits[i].name === preferName) return hits[i];
    return hits.length ? hits[0] : null;
}

function spreadLabel(spread) {
    var names = [];
    for (var i = 0; i < spread.pages.length; i++) names.push(spread.pages[i].name);
    return names.join("–") + "쪽";
}

function resetFind() {
    app.findTextPreferences = NothingEnum.NOTHING;
    app.changeTextPreferences = NothingEnum.NOTHING;
}

function changeInFrame(frame, from, to) {
    resetFind();
    app.findTextPreferences.findWhat = from;
    app.changeTextPreferences.changeTo = to;
    var n = frame.texts[0].changeText().length;
    resetFind();
    return n > 0;
}

function shortestFrameWith(spread, text) {
    var frames = textFramesIn(spread), best = null;
    for (var j = 0; j < frames.length; j++) {
        if (frames[j].contents.indexOf(text) < 0) continue;
        if (!best || frames[j].contents.length < best.contents.length) best = frames[j];
    }
    return best;
}

function findKoreanFont(doc) {
    // 지면에 이미 한글 본문(PICTURE 의 "카메라를 들면…")이 있으면 같은 글꼴을 쓴다
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

// 한글이 든 단락에만 한글 글꼴을 입힌다. 영어 제목 · 라벨 · MY STYLE 은 지면 글꼴 그대로
function setText(text, contents, koFont) {
    text.contents = contents;
    if (!koFont) return;
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
        chips.push(CHIP + NBSP + MY_STYLE_COLORS[i][0] + NBSP + MY_STYLE_COLORS[i][1]);
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

function center(item) {
    var b = item.geometricBounds; // [y1, x1, y2, x2]
    return [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
}

function area(item) {
    var b = item.geometricBounds;
    return Math.abs((b[2] - b[0]) * (b[3] - b[1]));
}

function dist(a, b) {
    return Math.sqrt((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]));
}

// ---------------------------------------------------------------- 펼침 B

function runB(doc, koFont, log, missing) {
    var p5 = findPage(doc, ["A grid system is", "Common types include"], "5");
    if (!p5) { missing.push("펼침 B: 5쪽 템플릿 본문(A grid system is… · Common types include…)이 없다 — 이미 바꿨을 수 있다"); return null; }
    var spread = p5.parent, where = spreadLabel(spread);

    // 1. 5쪽 본문 — 오른쪽 두 단락 → Q1 · Q2, 아래 한 단락 → MY STYLE
    var qFrame = frameStartingWith(p5, "Common types include");
    var oFrame = frameStartingWith(p5, "Overall, grid systems");
    if (!oFrame && norm(qFrame.contents).indexOf("Overall, grid systems") > 0) {
        setText(qFrame.texts[0], Q1 + "\r" + Q2, koFont);
        log.push(where + ": 오른쪽 본문 두 단락 → Q1 · Q2");
    } else {
        setText(qFrame.texts[0], Q1, koFont);
        log.push(where + ": 오른쪽 첫째 단락 → Q1");
        if (oFrame) {
            setText(oFrame.texts[0], Q2, koFont);
            log.push(where + ": 오른쪽 둘째 단락 → Q2");
        } else missing.push(where + ": \"Overall, grid systems…\" 본문");
    }

    var mt = frameStartingWith(p5, "A grid system is").texts[0];
    setText(mt, myStyleText(), koFont);
    var n = colorChips(doc, mt, koFont);
    log.push(where + ": 아래 본문 → MY STYLE (색 칩 " + n + "개, 견본 'MY STYLE …' 추가)");

    // 2. 라벨 — 사진 캡션 · 머리말 (본문을 먼저 바꿔야 본문 안의 "modular grids" 를 라벨로 잘못 잡지 않는다)
    var labels = B_LABELS.slice(0);
    if (HEADER_5) labels.push(["Grid Exploration 001", HEADER_5]);
    for (var i = 0; i < labels.length; i++) {
        var f = shortestFrameWith(spread, labels[i][0]);
        if (f && changeInFrame(f, labels[i][0], labels[i][1])) log.push(where + ": " + labels[i][0] + " → " + labels[i][1]);
        else missing.push(where + ": " + labels[i][0]);
    }

    // 3. 템플릿 글 상자 지움
    var removals = B_REMOVALS.slice(0);
    if (!HEADER_5) removals.push("Grid Exploration 001");
    for (i = 0; i < removals.length; i++) {
        var rf = shortestFrameWith(spread, removals[i]);
        if (rf) {
            log.push(where + ": 글 상자 지움 (" + norm(rf.contents) + ")");
            rf.remove();
        } else missing.push(where + ": " + removals[i] + " 상자");
    }
    return spread;
}

// ---------------------------------------------------------------- 펼침 C

function runC(doc, koFont, log, missing) {
    var p7 = findPage(doc, ["Grid systems are widely used"], "7");
    if (!p7) { missing.push("펼침 C: 7쪽 템플릿 본문(Grid systems are widely used…)이 없다 — 이미 바꿨을 수 있다"); return null; }
    var spread = p7.parent, where = spreadLabel(spread);

    setText(frameStartingWith(p7, "Grid systems are widely used").texts[0], cIntro(), koFont);
    log.push(where + ": 첫 본문 → DAILY LookBook 소개");

    var mk = frameStartingWith(spread, "Common types include");
    if (mk) {
        setText(mk.texts[0], C_MARKET, koFont);
        log.push(where + ": 둘째 본문 → MARKET 화면 설명");
    } else missing.push(where + ": \"Common types include…\" 본문");

    // 라벨 두 개 — 같은 템플릿 글이라 자리로 가른다
    var labels = [], frames = textFramesIn(spread), i;
    for (i = 0; i < frames.length; i++) {
        if (frames[i].contents.indexOf("manuscript grids") >= 0 && frames[i].contents.length < 80) labels.push(frames[i]);
    }
    if (labels.length === 0) {
        missing.push(where + ": 라벨 manuscript grids");
    } else {
        var mainIdx = -1;
        var graphics = spread.allGraphics;
        if (labels.length >= 2 && graphics.length >= 2) {
            // 가장 작은 그림 = 메인 화면. 그 그림에 가까운 라벨이 MAIN
            var small = graphics[0].parent;
            for (i = 1; i < graphics.length; i++) if (area(graphics[i].parent) < area(small)) small = graphics[i].parent;
            mainIdx = 0;
            for (i = 1; i < labels.length; i++) {
                if (dist(center(labels[i]), center(small)) < dist(center(labels[mainIdx]), center(small))) mainIdx = i;
            }
        } else if (labels.length >= 2) {
            // 그림을 못 찾으면 아래쪽 라벨이 MAIN (메인 화면은 7쪽 오른쪽 아래)
            mainIdx = 0;
            for (i = 1; i < labels.length; i++) if (center(labels[i])[0] > center(labels[mainIdx])[0]) mainIdx = i;
        }
        for (i = 0; i < labels.length; i++) {
            var t = (i === mainIdx) ? C_LABEL_MAIN : C_LABEL_MARKET;
            changeInFrame(labels[i], "manuscript grids", t[0]);
            changeInFrame(labels[i], "(single-column layouts)", t[1]);
            log.push(where + ": 라벨 → " + t[0] + " " + t[1]);
        }
        if (labels.length === 1) missing.push(where + ": 라벨이 하나뿐 — MARKET 으로 넣었다. MAIN 라벨은 직접 넣어 주세요");
    }
    return spread;
}

// ---------------------------------------------------------------- 실행

function run() {
    if (app.documents.length === 0) { alert("열린 문서가 없습니다."); return; }
    var doc = app.activeDocument;
    var log = [], missing = [], i, j;

    var saved = app.findChangeTextOptions.properties;
    app.findChangeTextOptions.caseSensitive = true;
    app.findChangeTextOptions.wholeWord = false;
    app.findChangeTextOptions.includeMasterPages = false;

    var koFont = findKoreanFont(doc);
    if (koFont) log.push("한글 글꼴: " + fontLabel(koFont));
    else missing.push("한글 글꼴을 못 찾음 — 한글 본문 글꼴을 직접 바꿔 주세요");

    var spreads = [runB(doc, koFont, log, missing), runC(doc, koFont, log, missing)];
    app.findChangeTextOptions.properties = saved;

    var overflow = [], leftover = [], others = [];
    for (i = 0; i < spreads.length; i++) {
        if (!spreads[i]) continue;
        var fs = textFramesIn(spreads[i]), where = spreadLabel(spreads[i]);
        for (j = 0; j < fs.length; j++) {
            if (fs[j].overflows) overflow.push(where + ": " + norm(fs[j].contents).substr(0, 30) + "…");
            if (LEFTOVER_PATTERN.test(fs[j].contents)) leftover.push(where + ": " + norm(fs[j].contents).substr(0, 40));
        }
    }
    // B · C 밖에 있는 글 — 다음 단계(전체 수정)를 위해 알려만 준다
    for (i = 0; i < doc.pages.length; i++) {
        var pg = doc.pages[i], skip = false;
        for (j = 0; j < spreads.length; j++) if (spreads[j] && pg.parent === spreads[j]) skip = true;
        if (skip) continue;
        var pf = textFramesIn(pg);
        for (j = 0; j < pf.length; j++) others.push(pg.name + "쪽: " + norm(pf[j].contents).substr(0, 40));
    }

    var msg = "바꾼 것 (" + log.length + ")\n" + log.join("\n");
    if (missing.length) msg += "\n\n못 찾은 것 (" + missing.length + ")\n" + missing.join("\n");
    if (overflow.length) msg += "\n\n넘친 글 상자 — 상자를 키우거나 글을 줄이세요\n" + overflow.join("\n");
    if (leftover.length) msg += "\n\n남은 템플릿 글\n" + leftover.join("\n");
    if (others.length) msg += "\n\nB · C 밖의 글 (건드리지 않음)\n" + others.join("\n");
    alert(msg);
}

app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "v2 B · C · STYLE 4–7쪽");
