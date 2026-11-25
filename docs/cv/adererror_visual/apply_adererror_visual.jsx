// apply_adererror_visual.jsx — 젠틀몬스터 공간 오브제 이력서(.indd)를 아더에러 VISUAL 인턴 내용으로 바꾸는 InDesign 스크립트
//
// 쓰는 법: InDesign 에서 젠틀몬스터 공간 오브제 이력서 .indd 를 연 뒤
//   창 > 유틸리티 > 스크립트 → '사용자' 폴더를 오른쪽 클릭 > Finder에서 표시 → 이 파일을 그 폴더에 넣고 패널에서 두 번 클릭.
// 하는 일: 처음 창에서 한 줄 소개 · ABOUT 제목 · KEYWORDS 04 의 안을 고른 뒤, 글자만 바꿉니다
//   (틀 · 글꼴 · 색은 그대로, 바꾼 글은 원래 글의 서식을 이어받음).
//   SKILLS 배지 글자를 옆의 툴 이름에 맞춥니다 (Ps · Ai · Id · En · Rh · AI).
//   크기가 어긋난 두 곳을 같은 급에 맞춥니다: KEYWORDS 01 제목(11pt → 02 제목 크기), SKILLS 제목(12pt → ABOUT 제목 크기).
//   넘치는 한 줄짜리 틀만 오른쪽으로 조금 넓힙니다(왼쪽 사이드바는 1/3 선을 넘지 않게).
//   끝에 '젠틀몬스터 · 오브제 · 블루엘리펀트' 가 남은 곳을 찾아 알려 줍니다.
//   한 번의 실행 취소(⌘Z)로 되돌릴 수 있고, 같은 폴더에 '…_ADERERROR VISUAL.indd' 로 따로 저장합니다(원본 그대로).
// 근거: ADER_VISUAL_CV_proposal.pdf (2026-11-25) — 아더에러 VISUAL 인턴 공고(기업 분석 K0) + 혁주님이 이미 쓴 글.

#target indesign

(function () {
    var SIDE = ["한 장면이 하나의 이야기가 되게 하려는 지원자",
                "스쳐 지나가던 일상을 사진으로 관찰해 온 지원자",
                "분위기를 이미지로 직관적으로 전하려는 지원자"];
    var ABOUT = [["스쳐 지나가던 일상을", "사진으로 관찰하는 건축학도"],
                 ["사진으로 관찰하고,", "이미지로 다듬는 건축학도"],
                 ["건축의 공간감에", "패션의 안목을 더하는 지원자"]];
    var KW4 = [["정리", "품목마다 자리를 정해, 찾는 시간을 줄이는 정리를 해 왔습니다"],
               ["툴 습득", "여러 툴을 써 온 만큼 프리미어 · 애프터 이펙트도 빠르게 익히겠습니다"]];

    if (app.documents.length === 0) { alert("먼저 젠틀몬스터 공간 오브제 이력서 .indd 를 열어 주세요."); return; }
    var doc = app.activeDocument;

    // ── 안 고르기 ──
    function labels(a) { var o = []; for (var i = 0; i < a.length; i++) o.push((i + 1) + ". " + (a[i] instanceof Array ? a[i].join(" / ") : a[i])); return o; }
    var dlg = app.dialogs.add({name: "아더에러 VISUAL 인턴으로 바꾸기", canCancel: true});
    var col = dlg.dialogColumns.add();
    col.staticTexts.add({staticLabel: "한 줄 소개 (사이드바)"});
    var dSide = col.dropdowns.add({stringList: labels(SIDE), selectedIndex: 0, minWidth: 420});
    col.staticTexts.add({staticLabel: "ABOUT 제목 (2줄)"});
    var dAbout = col.dropdowns.add({stringList: labels(ABOUT), selectedIndex: 0, minWidth: 420});
    col.staticTexts.add({staticLabel: "KEYWORDS 04"});
    var dKw4 = col.dropdowns.add({stringList: labels(KW4), selectedIndex: 0, minWidth: 420});
    col.staticTexts.add({staticLabel: "레이아웃은 그대로이고, 끝나면 '_ADERERROR VISUAL' 이름으로 따로 저장합니다."});
    if (!dlg.show()) { dlg.destroy(); return; }
    var side_ = SIDE[dSide.selectedIndex], about = ABOUT[dAbout.selectedIndex], kw4 = KW4[dKw4.selectedIndex];
    dlg.destroy();

    // [찾을 글(여럿이면 차례로 시도), 바꿀 글, 옵션]
    // side: "left" 사이드바만 / "right" 오른쪽만, whole: 문단 전체가 그 글일 때만, spaced: 자간 넓은 영문,
    // regex: 찾을 글이 GREP 식, word: 앞뒤에 한글이 붙지 않은 낱말만, optional: 없어도 됨(이미 고친 판일 때)
    var CHANGES = [
        [["SPACE OBJECT DESIGNER"], "VISUAL INTERN", {spaced: true}],
        [["젠틀몬스터 공간 오브제 디자이너"], "아더에러 VISUAL 인턴 지원", {side: "left"}],
        [["오브제가 공간 속에서 하나의 장면이 되게 하려는 지원자"], side_, {side: "left"}],
        [["건축에서 배운 감각으로", "틀을 배우고,"], about[0], {}],
        [["공간을 디자인하는 지원자", "그 안을 채우는 건축학도"], about[1], {}],
        [["어릴적 부터의 옷에 대한 관심", "어릴 적부터의 옷에 대한 관심", "어릴 적 부터의 옷에 대한 관심", "어릴적부터의 옷에 대한 관심"], "옷에 대한 관심은 건축보다 먼저", {}],
        [["건축으로 배운 공간에 대한 이해와 구현", "건축으로 공간의 크기와 거리를 가늠하는 감각"], "평소 찍은 사진과 패션 사진을 SNS에 기록", {}],
        [["아트 오브제와 가구, 마감재 기획을 목표로"], "촬영과 보정으로 옷의 분위기를 전하는 일을 목표로", {}],
        [["공간의 실내 마감", "실내 마감재와 마감 방식"], "해외 레퍼런스 리서치", {whole: true}],
        [["가구와 조명 수집"], "사진 촬영", {whole: true, optional: true}],
        [["패션 · 공간"], "패션", {whole: true, optional: true}],
        [["리서치와 분석으로 컨셉을 세우고, 하나의 생각을 끝까지 형태로 밀고 갑니다"], "학부 리서치를 대부분 영어 자료로 해 와, 해외 레퍼런스 찾기에 익숙합니다", {}],
        [["기획"], "영어 리서치", {word: true}],
        [["꼴라주, 렌더링, 이미지 구현을 통해 실현 이전에 시각적으로 확인합니다", "콜라주, 렌더링, 이미지 구현을 통해 실현 이전에 시각적으로 확인합니다",
          "만들기 전에 3D로 먼저 구현해 크기와 배치를 확인합니다"], "포토샵 · 일러스트 · 인디자인으로 시각화와 후보정을 해 왔습니다", {}],
        [["사전 확인"], "이미지 보정", {word: true}],
        [["건축학과에서 배운 다양한 툴을 바탕으로 작업이 가능합니다", "원색 대신 채도를 낮춘 색으로 포인트를 주고 주변과 어우러지게 합니다"], kw4[1], {}],
        [["다양한 툴의 사용", "컬러 감도"], kw4[0], {}],
        [["젠틀몬스터[^\\r\\n]*?지원"], "아더에러 VISUAL 인턴 지원", {side: "right", regex: true}],
        [["실물\\s*모형\\s*제작[^\\r]*"], "실물 모형 제작 → 문화역서울284 《돌봄의 디자인》 전시", {regex: true}],
        [["2D → 3D → RENDER → RETOUCH → GRAPHIC → EDITORIAL"], "RETOUCH · GRAPHIC · EDITORIAL · RENDER · 3D · AI", {}]
    ];
    // SKILLS: 툴 이름 → 배지 글자
    var BADGE = {"Photoshop": "Ps", "Illustrator": "Ai", "InDesign": "Id", "Enscape": "En", "Rhino": "Rh", "AI": "AI"};

    function esc(s) { return s.replace(/([\\^$.*+?()\[\]{}|~])/g, "\\$1"); }
    function pattern(src, opt) {
        var p;
        if (opt.regex) p = src;
        else if (opt.spaced) {
            var chars = src.replace(/ /g, "").split(""), parts = [];
            for (var i = 0; i < chars.length; i++) parts.push(esc(chars[i]));
            p = parts.join("\\s*");
        } else p = esc(src).replace(/ +/g, "\\s+");
        if (opt.word) p = "(?<![\\x{AC00}-\\x{D7A3}])" + p + "(?![\\x{AC00}-\\x{D7A3}])";
        return opt.whole ? "^\\s*" + p + "\\s*$" : p;
    }
    function frameOf(t) { try { var f = t.parentTextFrames; return f && f.length ? f[0] : null; } catch (e) { return null; } }
    function side(frame) {
        try {
            var pb = frame.parentPage.bounds, gb = frame.geometricBounds;
            return (gb[1] - pb[1]) < (pb[3] - pb[1]) / 3 - 1 ? "left" : "right";
        } catch (e) { return "right"; }
    }
    function unfit(frame) {
        if (!frame || !frame.overflows) return true;
        var pb = frame.parentPage.bounds, W = pb[3] - pb[1];
        var limit = side(frame) === "left" ? pb[1] + W / 3 - W * 0.03 : pb[3] - W * 0.03;
        var gb = frame.geometricBounds, step = W / 210;
        while (frame.overflows && gb[3] + step <= limit) { gb = [gb[0], gb[1], gb[2], gb[3] + step]; frame.geometricBounds = gb; }
        return !frame.overflows;
    }
    function grep(p) {
        app.findGrepPreferences = NothingEnum.nothing;
        app.changeGrepPreferences = NothingEnum.nothing;
        app.findChangeGrepOptions.includeMasterPages = false;
        app.findGrepPreferences.findWhat = p;
        return doc.findGrep();
    }
    function one(p) { var f = grep(p); return f.length ? f[0] : null; }
    function center(fr) { var g = fr.geometricBounds; return [(g[0] + g[2]) / 2, (g[1] + g[3]) / 2]; }

    var report = [], warn = [];
    function run() {
        for (var i = 0; i < CHANGES.length; i++) {
            var srcs = CHANGES[i][0], dst = CHANGES[i][1], opt = CHANGES[i][2], n = 0, hit = "";
            for (var s = 0; s < srcs.length && n === 0; s++) {
                var found = grep(pattern(srcs[s], opt));
                for (var k = found.length - 1; k >= 0; k--) {
                    var t = found[k], f = frameOf(t);
                    if (opt.side && f && side(f) !== opt.side) continue;
                    var lead = "", trail = "";
                    if (opt.whole) { var c = t.contents, m1 = c.match(/^\s*/), m2 = c.match(/\s*$/); lead = m1 ? m1[0] : ""; trail = m2 ? m2[0] : ""; }
                    t.contents = lead + dst + trail;
                    n++; hit = srcs[s];
                    if (f && !unfit(f)) warn.push("넘침 — 직접 확인: " + dst);
                }
            }
            if (n || !opt.optional) report.push((n ? "✓ " : "✗ 못 찾음 ") + (opt.regex ? dst : (hit || srcs[0])) + (opt.regex ? "" : "  →  " + dst) + (n > 1 ? "  (" + n + "곳)" : ""));
        }

        // SKILLS 배지: 툴 이름 틀마다 가장 가까운 배지(대문자+소문자 두 글자) 틀을 찾아 글자를 맞춤
        var frames = [], items = doc.allPageItems;
        for (var a = 0; a < items.length; a++) if (items[a] instanceof TextFrame) frames.push(items[a]);
        var names = [], badges = [];
        for (var b = 0; b < frames.length; b++) {
            var txt = String(frames[b].contents).replace(/^\s+|\s+$/g, ""), first = txt.split(/[\r\n]/)[0].replace(/\s+$/, "");
            if (BADGE.hasOwnProperty(first)) names.push([frames[b], first]);
            else if (/^[A-Z][a-z]$/.test(txt)) badges.push(frames[b]);
        }
        var fixed = 0, used = {};
        for (var c2 = 0; c2 < names.length; c2++) {
            var ng = names[c2][0].geometricBounds, best = -1, bd = 1e9;
            for (var d = 0; d < badges.length; d++) {
                if (used[d]) continue;
                var bc = center(badges[d]), dy = Math.abs(bc[0] - (ng[0] + 4)), dx = ng[1] - bc[1];
                if (dx <= 0 || dy > 8 || dx > 20) continue;   // 배지는 이름 틀 왼쪽, 같은 줄 근처
                if (dx + dy < bd) { bd = dx + dy; best = d; }
            }
            if (best < 0) continue;
            used[best] = true;
            var want = BADGE[names[c2][1]], tf = badges[best], cur = String(tf.contents).replace(/^\s+|\s+$/g, "");
            if (cur !== want) { tf.texts[0].contents = String(tf.contents).replace(cur, want); fixed++; }
        }
        report.push(names.length && badges.length ? "✓ SKILLS 배지: " + fixed + "곳 고침 (툴 이름 " + names.length + "개 확인)" : "✗ SKILLS 배지를 찾지 못함 — 직접 바꿔 주세요: Ps · Ai · Id · En · Rh · AI");

        // 같은 급 크기 맞추기
        var k1 = one("(?<![\\x{AC00}-\\x{D7A3}])영어\\s+리서치(?![\\x{AC00}-\\x{D7A3}])"), k2 = one("이미지\\s+보정");
        if (k1 && k2 && k1.pointSize !== k2.pointSize) { k1.pointSize = k2.pointSize; report.push("✓ KEYWORDS 01 제목 크기 → " + k2.pointSize + "pt (02 제목과 같게)"); }
        var sk = one("^S\\s*K\\s*I\\s*L\\s*L\\s*S$"), ab = one("^A\\s*B\\s*O\\s*U\\s*T$");
        if (sk && ab && sk.pointSize !== ab.pointSize) { sk.pointSize = ab.pointSize; report.push("✓ SKILLS 제목 크기 → " + ab.pointSize + "pt (ABOUT 제목과 같게)"); }

        // 남은 다른 회사 · 직무 언급
        var left = grep("젠틀몬스터|GENTLE\\s*MONSTER|오브제|S\\s*P\\s*A\\s*C\\s*E\\s+O\\s*B\\s*J\\s*E\\s*C\\s*T|블루엘리펀트|BLUE\\s*ELEPHANT|PROTEAN");
        for (var r = 0; r < left.length; r++) {
            var para = "";
            try { para = left[r].paragraphs[0].contents.replace(/[\r\n]+/g, " "); } catch (e) {}
            warn.push("남은 언급 — 아더에러 지원서에서 빼 주세요: " + para.substring(0, 60));
        }
        app.findGrepPreferences = NothingEnum.nothing;
        app.changeGrepPreferences = NothingEnum.nothing;
    }
    app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "아더에러 VISUAL 인턴 내용으로 바꾸기");

    var saved = "";
    try {
        if (doc.saved) {
            var base = doc.fullName.fsName.replace(/\.indd$/i, "").replace(/_GENTLE MONSTER OBJECT$/i, "");
            var p = base + "_ADERERROR VISUAL.indd";
            doc.save(new File(p));
            saved = "\n\n저장: " + p;
        } else { saved = "\n\n(저장되지 않은 문서라 따로 저장하지 않았습니다 — 다른 이름으로 저장해 주세요.)"; }
    } catch (e) { saved = "\n\n저장하지 못했습니다: " + e; }
    alert(report.join("\n") + (warn.length ? "\n\n" + warn.join("\n") : "") + saved);
})();
