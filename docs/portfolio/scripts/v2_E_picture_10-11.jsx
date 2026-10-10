// v2 펼침 E (10–11쪽) · (002) PICTURE — 템플릿 글을 원고로 바꾼다
// 원고: docs/portfolio/v2_E_fix.md
//
// 쓰는 법: InDesign 에서 문서를 연 채로 창 → 유틸리티 → 스크립트 → 사용자 폴더에 이 파일을 넣고 두 번 클릭.
//          (또는 파일 → 스크립트 → 스크립트 찾아보기)
// 되돌리기: 편집 → 실행 취소 한 번으로 전부 되돌린다.
//
// 독립: 10–11쪽 펼침 안의 것만 고친다. 다른 펼침 · 마스터 페이지는 건드리지 않는다.
//       글 상자는 id 가 아니라 글 내용으로 찾는다 — A–D 를 먼저 고쳤든 아니든, 몇 번을 돌리든 결과가 같다.
// 끝나면 바꾼 것 · 못 찾은 것 · 넘친 글 상자 · 겹침 · 남은 템플릿 글을 알려 준다.

var LEFT = "10", RIGHT = "11";

// 큰 제목: MOMENT LIKE A PHOTOGRAPH → PICTURE. 2쪽 STYLE 과 같은 글자 · 같은 자리로 맞춘다.
var TITLE = "PICTURE";
var TITLE_PARTS = /MOMENT|PHOTOGR|LIKEA/;     // 공백 · 줄바꿈을 지우고 대문자로 본 제목 조각
var TITLE_MIN_SIZE = 40;                      // 이보다 작은 글은 제목이 아니다 (부제 A Moment like A Photograph 를 건드리지 않게)
var MATCH_STYLE_TITLE = true;                 // false 면 글만 바꾸고 크기 · 자리는 그대로 둔다

var OPENING_KO = [
    "두 번째로, 내가 멈추는 곳은 멋진 장면 앞이다. 빛, 색, 사람, 장소가 한순간에 맞아떨어질 때가 있다. 그때 나는 카메라를 꺼낸다.",
    "앞의 거리 사진도 그랬다. 헤드폰을 쓴 사람, 체크 셔츠와 슬리퍼, 그리고 그 뒤의 화분과 칠판. 사람과 장소가 함께 맞아떨어진 순간이었다.",
    "그래서 내 두 번째 이야기는 사진이다."
];

// [찾는 글(이 글이 들어 있는 상자), 바꿀 줄들, 설명] — 줄마다 원래 그 줄의 글자 서식을 그대로 쓴다
var LINE_REPLACEMENTS = [
    [/Template Systems|Grid Systems Series/, ["A Moment like A Photograph"], "10 오른쪽 라벨 → 부제"],
    [/Grid Exploration/, ["I stop for a scene.", "(My second story is about pictures.)"], "11 아래 → 영어 한 줄"],
    [/카메라를 꺼낸다|두 번째 이야기는 사진이다|^빛, 색/, OPENING_KO, "11 본문 → 여는 글"]
];

// 이 글이 들어 있는 글 상자를 지운다: 10 가운데 라벨 · 10 왼쪽 아래 잘린 글
var REMOVE_PATTERN = /download now|template\.systems|plate\.systems/i;

// 11 기차 사진: 검은 테두리를 빼고 캡션(단어 하나)을 단다. 캡션이 필요 없으면 "" 로.
var CAPTION = "Puddle";
var CAPTION_GAP = 6;                          // 사진 아래 끝과 캡션 사이 (pt)

var LEFTOVER_PATTERN = /template|grid|download|www\./i;
var LEFTOVER_TITLE = /MOMENT|PHOTOGR/;

function norm(s) {
    return String(s).replace(/[\r\n\u2028\u2029]+/g, " ").replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
}

function squash(s) {
    return String(s).replace(/\s+/g, "").toUpperCase();
}

function firstSize(frame) {
    try { return frame.parentStory.characters[0].pointSize; } catch (e) { return 0; }
}

function startsWith(frame, text) {
    return norm(frame.contents).indexOf(text) === 0;
}

function pageByName(doc, name) {
    var p = doc.pages.itemByName(name);
    if (p.isValid) return p;
    var i = parseInt(name, 10) - 1;
    return (i >= 0 && i < doc.pages.length) ? doc.pages[i] : null;
}

function itemsOf(spread, ctor) {
    var out = [], items = spread.allPageItems;
    for (var i = 0; i < items.length; i++) {
        if (!ctor || items[i].constructor.name === ctor) out.push(items[i]);
    }
    return out;
}

function onPage(item, page) {
    var pp = item.parentPage;
    return pp !== null && pp.isValid && pp.name === page.name;
}

function intersects(a, b) {
    // geometricBounds = [위, 왼쪽, 아래, 오른쪽]
    return a[1] < b[3] && b[1] < a[3] && a[0] < b[2] && b[0] < a[2];
}

// 글 상자의 글을 lines 로 바꾼다. i 번째 줄은 원래 i 번째 단락의 서식(넘치면 마지막 단락의 서식)을 쓴다.
function setLines(story, lines) {
    var i, n = story.paragraphs.length;
    for (i = 0; i < lines.length; i++) {
        if (i < n) {
            var p = story.paragraphs[i];
            p.contents = lines[i] + (/\r$/.test(p.contents) ? "\r" : "");
        } else {
            story.insertionPoints[-1].contents = "\r" + lines[i];
        }
    }
    while (story.paragraphs.length > lines.length) story.paragraphs[-1].remove();
    while (story.characters.length > 0 && /\r$/.test(story.contents)) story.characters[-1].remove();
}

function findStyleTitle(doc) {
    // 2쪽 STYLE 큰 제목 — 읽기만 한다
    var page = pageByName(doc, "2");
    if (!page) return null;
    var frames = itemsOf(page.parent, "TextFrame");
    for (var i = 0; i < frames.length; i++) {
        if (onPage(frames[i], page) && norm(frames[i].contents) === "STYLE") return { frame: frames[i], page: page };
    }
    return null;
}

function run() {
    if (app.documents.length === 0) { alert("열린 문서가 없습니다."); return; }
    var doc = app.activeDocument;
    // 좌표를 펼침 기준으로 재야 2쪽 STYLE 자리를 10쪽으로 옮길 수 있다. 끝나면 되돌린다.
    var origin = doc.viewPreferences.rulerOrigin;
    doc.viewPreferences.rulerOrigin = RulerOrigin.SPREAD_ORIGIN;
    try { fix(doc); } finally { doc.viewPreferences.rulerOrigin = origin; }
}

function fix(doc) {
    var log = [], missing = [], warn = [], i, j;

    var left = pageByName(doc, LEFT), right = pageByName(doc, RIGHT);
    if (!left || !right) { alert(LEFT + "쪽 또는 " + RIGHT + "쪽을 찾지 못했습니다."); return; }
    var spread = left.parent;
    if (right.parent !== spread && right.parent.id !== spread.id) {
        alert(LEFT + "쪽과 " + RIGHT + "쪽이 한 펼침이 아닙니다. 쪽 번호를 확인하세요."); return;
    }

    // 1. 큰 제목
    var frames = itemsOf(spread, "TextFrame"), titleFrame = null, seen = {};
    for (i = 0; i < frames.length; i++) {
        var f = frames[i];
        if (!f.isValid) continue;
        var s = squash(f.contents);
        if (s.length > 40 || !TITLE_PARTS.test(s) || firstSize(f) < TITLE_MIN_SIZE) continue;
        var sid = f.parentStory.id;
        if (seen[sid]) continue;
        seen[sid] = true;
        if (!titleFrame) { titleFrame = f; continue; }
        // 제목이 여러 상자로 나뉘어 있으면 첫 상자에 모으고 나머지는 지운다
        log.push("제목 조각 상자 지움 (" + norm(f.contents) + ")");
        var fs = f.parentStory.textContainers;
        for (j = fs.length - 1; j >= 0; j--) fs[j].remove();
    }
    if (titleFrame) {
        var story = titleFrame.parentStory, before = norm(story.contents);
        setLines(story, [TITLE]);
        var conts = story.textContainers;
        if (conts.length > 1) {
            titleFrame = conts[0];
            for (j = conts.length - 1; j >= 1; j--) conts[j].remove();
        }
        log.push("큰 제목: " + before + " → " + TITLE);

        var ref = MATCH_STYLE_TITLE ? findStyleTitle(doc) : null;
        if (ref) {
            var src = ref.frame.parentStory.characters[0], dst = story.texts[0];
            var props = ["appliedFont", "fontStyle", "pointSize", "leading", "tracking", "horizontalScale", "verticalScale", "capitalization"];
            for (j = 0; j < props.length; j++) {
                try { dst[props[j]] = src[props[j]]; } catch (e) { warn.push("제목 " + props[j] + " 를 못 옮김"); }
            }
            var gb = ref.frame.geometricBounds, pb = ref.page.bounds, lb = left.bounds;
            titleFrame.geometricBounds = [
                gb[0] - pb[0] + lb[0], gb[1] - pb[1] + lb[1],
                gb[2] - pb[0] + lb[0], gb[3] - pb[1] + lb[1]
            ];
            log.push("큰 제목: 2쪽 STYLE 과 같은 글자 (" + String(src.pointSize).substr(0, 6) + "pt) · 같은 자리");
        } else if (MATCH_STYLE_TITLE) {
            warn.push("2쪽 STYLE 제목을 못 찾아 크기 · 자리는 그대로 둠 — 2쪽 STYLE 에 맞춰 주세요");
        }
    } else {
        var titled = false;
        for (i = 0; i < frames.length; i++) if (frames[i].isValid && norm(frames[i].contents) === TITLE) titled = true;
        if (titled) log.push("큰 제목 " + TITLE + " (이미 되어 있음)");
        else missing.push("큰 제목 MOMENT LIKE A PHOTOGRAPH");
    }

    // 2. 줄 바꾸기 (라벨 · 본문)
    for (i = 0; i < LINE_REPLACEMENTS.length; i++) {
        var r = LINE_REPLACEMENTS[i], done = false;
        frames = itemsOf(spread, "TextFrame");
        for (j = 0; j < frames.length && !done; j++) {
            if (!r[0].test(norm(frames[j].contents))) continue;
            setLines(frames[j].parentStory, r[1]);
            log.push(r[2]);
            done = true;
        }
        if (!done) {
            // 이미 고친 문서면 바꿀 글이 들어 있다
            var already = false;
            for (j = 0; j < frames.length; j++) if (startsWith(frames[j], r[1][0])) already = true;
            if (already) log.push(r[2] + " (이미 되어 있음)");
            else missing.push(r[2]);
        }
    }

    // 3. 템플릿 글 상자 지우기
    frames = itemsOf(spread, "TextFrame");
    for (i = frames.length - 1; i >= 0; i--) {
        if (REMOVE_PATTERN.test(frames[i].contents)) {
            log.push("글 상자 지움 (" + norm(frames[i].contents).substr(0, 40) + ")");
            frames[i].remove();
        }
    }

    // 4. 11쪽 사진: 테두리 빼기 · 캡션
    var all = itemsOf(spread), photos = [], stroked = [];
    for (i = 0; i < all.length; i++) {
        var it = all[i];
        if (it.constructor.name === "TextFrame" || !onPage(it, right)) continue;
        var hasGraphic = false;
        try { hasGraphic = it.graphics.length > 0; } catch (e) {}
        if (!hasGraphic) continue;
        photos.push(it);
        if (it.strokeWeight > 0) stroked.push(it);
    }
    for (i = 0; i < stroked.length; i++) {
        log.push(RIGHT + "쪽 사진 테두리 뺌 (" + stroked[i].strokeWeight + "pt)");
        stroked[i].strokeWeight = 0;
    }
    if (stroked.length === 0) warn.push(RIGHT + "쪽 사진에 InDesign 테두리가 없음 — 이미 뺐거나, 테두리가 그림 파일 안에 있으면 그림 원본에서 지우세요");

    var saveFrame = null;  // 캡션 서식을 빌릴 상자: 11 아래 라벨 (I stop for a scene.)
    frames = itemsOf(spread, "TextFrame");
    for (j = 0; j < frames.length; j++) if (startsWith(frames[j], LINE_REPLACEMENTS[1][1][0])) saveFrame = frames[j];
    if (saveFrame) {
        // 둘째 줄(괄호 줄)을 Regular 로 — A 3쪽 라벨(굵은 줄 + 보통 괄호 줄)과 맞춘다
        var lp = saveFrame.parentStory.paragraphs;
        if (lp.length > 1 && lp[1].fontStyle === lp[0].fontStyle && lp[1].fontStyle !== "Regular") {
            try { lp[1].fontStyle = "Regular"; } catch (e) { warn.push("11 아래 둘째 줄을 Regular 로 못 바꿈"); }
        }
    }
    var photo = stroked.length === 1 ? stroked[0] : (photos.length === 1 ? photos[0] : null);
    if (CAPTION) {
        var hasCaption = false;
        frames = itemsOf(spread, "TextFrame");
        for (j = 0; j < frames.length; j++) if (norm(frames[j].contents) === CAPTION) hasCaption = true;
        if (hasCaption) log.push("캡션 " + CAPTION + " (이미 있음)");
        else if (!photo) warn.push("캡션: " + RIGHT + "쪽 기차 사진을 하나로 정하지 못함 (사진 " + photos.length + "장) — 직접 다세요");
        else if (!saveFrame) warn.push("캡션: 서식을 빌릴 라벨을 못 찾음 — 직접 다세요");
        else {
            var cap = saveFrame.duplicate();
            setLines(cap.parentStory, [CAPTION]);
            var pg = photo.geometricBounds, sg = saveFrame.geometricBounds;
            cap.geometricBounds = [pg[2] + CAPTION_GAP, pg[1], pg[2] + CAPTION_GAP + (sg[2] - sg[0]), Math.max(pg[3], pg[1] + 120)];
            log.push("캡션 " + CAPTION + " 을 사진 아래에 닮");
        }
    }

    // 5. 확인: (002) · 넘침 · 겹침 · 남은 템플릿 글 · 마스터
    frames = itemsOf(spread, "TextFrame");
    var overflow = [], leftover = [], overlap = [], hasNumber = false;
    for (j = 0; j < frames.length; j++) {
        var c = norm(frames[j].contents);
        if (c === "(002)") hasNumber = true;
        if (frames[j].overflows) overflow.push(norm(frames[j].contents).substr(0, 30) + "…");
        if (LEFTOVER_PATTERN.test(c) || LEFTOVER_TITLE.test(c)) leftover.push(c.substr(0, 40));
    }
    if (!hasNumber) warn.push("(002) 를 못 찾음 — 10쪽 섹션 번호를 확인하세요");
    if (titleFrame && titleFrame.isValid) {
        all = itemsOf(spread);
        for (j = 0; j < all.length; j++) {
            if (all[j] === titleFrame || all[j].id === titleFrame.id) continue;
            if (!onPage(all[j], left)) continue;
            if (intersects(titleFrame.geometricBounds, all[j].geometricBounds)) {
                var what = all[j].constructor.name === "TextFrame" ? norm(all[j].contents).substr(0, 20) : all[j].constructor.name;
                overlap.push("큰 제목 상자 ↔ " + what);
            }
        }
    }
    var pages = [left, right];
    for (i = 0; i < pages.length; i++) {
        var m = pages[i].masterPageItems;
        for (j = 0; j < m.length; j++) {
            if (m[j].constructor.name === "TextFrame" && LEFTOVER_PATTERN.test(m[j].contents)) {
                leftover.push(pages[i].name + "쪽 마스터: " + norm(m[j].contents).substr(0, 30) + " (마스터라 손대지 않음)");
            }
        }
    }

    var msg = "바꾼 것 (" + log.length + ")\n" + log.join("\n");
    if (missing.length) msg += "\n\n못 찾은 것 (" + missing.length + ")\n" + missing.join("\n");
    if (warn.length) msg += "\n\n확인할 것\n" + warn.join("\n");
    if (overflow.length) msg += "\n\n넘친 글 상자 — 상자를 키우거나 글을 줄이세요\n" + overflow.join("\n");
    if (overlap.length) msg += "\n\n겹침 후보 — 지면에서 보세요\n" + overlap.join("\n");
    if (leftover.length) msg += "\n\n남은 템플릿 글\n" + leftover.join("\n");
    alert(msg);
}

app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "v2 E · PICTURE 10–11쪽");
