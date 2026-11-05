// apply_blue_elephant.jsx — JAJU 이력서(.indd)를 블루엘리펀트 Creative Intern 내용으로 바꾸는 InDesign 스크립트
//
// 쓰는 법: InDesign 에서 'JAJU 라운딩 VMD 이력서.indd' 를 연 뒤
//   창 > 유틸리티 > 스크립트 > 사용자 폴더에 이 파일을 넣고 두 번 클릭 (또는 파일 > 스크립트 > 스크립트 찾아보기).
// 하는 일: 글자만 바꿉니다. 틀의 자리 · 크기 · 글꼴 · 크기 · 색은 그대로입니다(바꾼 글은 원래 글의 서식을 이어받음).
//   바꾼 글이 틀을 넘치면 그 한 줄짜리 틀만 오른쪽으로 조금 넓힙니다(왼쪽 사이드바는 1/3 선을 넘지 않게).
//   전부 한 번의 실행 취소(⌘Z)로 되돌릴 수 있고, 끝나면 같은 폴더에 '…_BLUE ELEPHANT.indd' 로 따로 저장합니다(원본은 그대로).
// 근거: 블루엘리펀트 자기소개서 확정본 — 1번(2026-11-04) · 2번(2026-11-05) · 3번 v6(2026-11-05).
// 경력에 'PROTEAN' 항목을 더하는 일은 줄 수가 늘어 레이아웃이 바뀌므로 하지 않습니다.

#target indesign

(function () {
    // [찾을 글, 바꿀 글, 옵션]  side: "left" = 왼쪽 1/3 사이드바만, "right" = 오른쪽만 / whole: 문단 전체가 그 글일 때만
    // spaced: 자간이 넓은 영문 제목이 글자 사이 공백으로 들어가 있어도 찾기
    var CHANGES = [
        ["ROUNDING VMD", "CREATIVE INTERN", {spaced: true}],
        ["JAJU 라운딩 VMD 지원", "블루엘리펀트 콘텐츠 디자인 인턴", {side: "left"}],
        ["건축에서 배운 공간감과 패션에 대한 안목을 접목하려는 지원자", "레퍼런스에서 찾은 아이디어를 이미지로 옮기려는 지원자", {side: "left"}],
        ["자기소개서 1번", "자기소개서 2번", {whole: true}],
        ["일상의 불편에서", "리서치로 생각하고,", {whole: true}],
        ["진열의 가능성을 찾다", "시각화로 먼저 확인하는 디자이너", {whole: true}],
        ["옷에 대한 관심은 건축보다 먼저", "건축을 공부하며 파사드 디자인에 관심", {}],
        ["건축으로 공간의 크기와 거리를 가늠하는 감각", "포토샵 · 일러스트 · 렌더링으로 시각화", {}],
        ["옷과 매장이 어떻게 보일지 기획하는 VMD를 목표로", "고객이 매장과 화면에서 처음 만나는 이미지를 목표로", {}],
        ["패션 · 공간", "사진 · 패션", {whole: true}],
        ["가구와 조명", "파사드 디자인", {whole: true}],
        ["물건의 배치 방식", "해외 레퍼런스 리서치", {whole: true}],
        ["일상의 작은 불편을 먼저 알아채고, 있는 것에서 바꿀 가능성을 찾습니다", "리서치로 컨셉을 세우고, 해외 자료를 하나의 컨셉으로 묶어 정리합니다", {}],
        ["상품 하나보다 매장 전체의 흐름 안에서 자리를 봅니다", "만들기 전에 렌더링과 후보정으로 재료와 색을 미리 확인합니다", {}],
        ["스타일을 가리지 않고 입어 보며 기른 안목 — 원단 · 디자인 · 색감", "포토샵 · 일러스트 · 인디자인으로 시각화와 후보정, AI 툴도 적극 활용", {}],
        ["진열을 바꾸기 전에 배치를 3D로 미리 그려 확인합니다", "평소 찍은 사진과 패션 사진을 개인 SNS에 올립니다", {}],
        ["일상의 불편", "기획력", {whole: true}],
        ["공간감", "미리 확인", {whole: true, side: "right"}],
        ["패션에 대한 안목", "이미지 작업", {whole: true}],
        ["구상을 미리 확인", "사진과 패션", {whole: true}],
        ["2026.10", "2026.11", {side: "right"}],
        ["JAJU 라운딩 VMD 지원", "블루엘리펀트 인턴 지원", {side: "right"}]
    ];

    if (app.documents.length === 0) { alert("먼저 JAJU 이력서 .indd 를 열어 주세요."); return; }
    var doc = app.activeDocument;
    if (!confirm("블루엘리펀트 내용으로 " + CHANGES.length + "곳의 글을 바꿉니다.\n레이아웃 · 서식은 그대로이고, 끝나면 '_BLUE ELEPHANT' 이름으로 따로 저장합니다.\n계속할까요?")) return;

    function esc(s) { return s.replace(/([\\^$.*+?()\[\]{}|~])/g, "\\$1"); }
    function pattern(src, opt) {
        var p;
        if (opt.spaced) {
            var chars = src.replace(/ /g, "").split(""), parts = [];
            for (var i = 0; i < chars.length; i++) parts.push(esc(chars[i]));
            p = parts.join("\\s*");
        } else {
            p = esc(src).replace(/ +/g, "\\s+");      // 원래 글이 줄바꿈된 자리도 찾도록
        }
        return opt.whole ? "^\\s*" + p + "\\s*$" : p;
    }
    function frameOf(t) {
        try { var f = t.parentTextFrames; return f && f.length ? f[0] : null; } catch (e) { return null; }
    }
    function side(frame) {                              // 쪽 폭의 1/3 왼쪽이면 left
        try {
            var pb = frame.parentPage.bounds, gb = frame.geometricBounds;   // [y1, x1, y2, x2]
            return (gb[1] - pb[1]) < (pb[3] - pb[1]) / 3 - 1 ? "left" : "right";
        } catch (e) { return "right"; }
    }
    function unfit(frame) {                             // 넘치면 오른쪽으로 넓힘
        if (!frame || !frame.overflows) return true;
        var pb = frame.parentPage.bounds, W = pb[3] - pb[1];
        var limit = side(frame) === "left" ? pb[1] + W / 3 - W * 0.03 : pb[3] - W * 0.03;
        var gb = frame.geometricBounds, step = W / 210;  // 약 1mm
        while (frame.overflows && gb[3] + step <= limit) {
            gb = [gb[0], gb[1], gb[2], gb[3] + step];
            frame.geometricBounds = gb;
        }
        return !frame.overflows;
    }

    var report = [], warn = [];
    function run() {
        for (var i = 0; i < CHANGES.length; i++) {
            var src = CHANGES[i][0], dst = CHANGES[i][1], opt = CHANGES[i][2];
            app.findGrepPreferences = NothingEnum.nothing;
            app.changeGrepPreferences = NothingEnum.nothing;
            app.findChangeGrepOptions.includeMasterPages = false;
            app.findGrepPreferences.findWhat = pattern(src, opt);
            var found = doc.findGrep(), n = 0;
            for (var k = found.length - 1; k >= 0; k--) {
                var t = found[k], f = frameOf(t);
                if (opt.side && f && side(f) !== opt.side) continue;
                var lead = "", trail = "";
                if (opt.whole) {                         // 문단 앞뒤 공백 · 문단 끝은 남김
                    var c = t.contents, m1 = c.match(/^\s*/), m2 = c.match(/\s*$/);
                    lead = m1 ? m1[0] : ""; trail = m2 ? m2[0] : "";
                }
                t.contents = lead + dst + trail;
                n++;
                if (f && !unfit(f)) warn.push("넘침 — 직접 확인: " + dst);
            }
            report.push((n ? "✓ " : "✗ 못 찾음 ") + src + "  →  " + dst + (n > 1 ? "  (" + n + "곳)" : ""));
        }
        app.findGrepPreferences = NothingEnum.nothing;
        app.changeGrepPreferences = NothingEnum.nothing;
    }
    app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "블루엘리펀트 내용으로 바꾸기");

    var saved = "";
    try {
        if (doc.saved) {
            var p = doc.fullName.fsName.replace(/\.indd$/i, "") + "_BLUE ELEPHANT.indd";
            doc.save(new File(p));
            saved = "\n\n저장: " + p;
        } else { saved = "\n\n(저장되지 않은 문서라 따로 저장하지 않았습니다 — 다른 이름으로 저장해 주세요.)"; }
    } catch (e) { saved = "\n\n저장하지 못했습니다: " + e; }
    alert(report.join("\n") + (warn.length ? "\n\n" + warn.join("\n") : "") + saved);
})();
