// apply_gm_object.jsx — 블루엘리펀트 이력서(.indd)를 젠틀몬스터 공간 오브제 디자이너 내용으로 바꾸는 InDesign 스크립트
//
// 쓰는 법: InDesign 에서 블루엘리펀트 이력서 .indd 를 연 뒤
//   창 > 유틸리티 > 스크립트 → '사용자' 폴더를 오른쪽 클릭 > Finder에서 표시 → 이 파일을 그 폴더에 넣고 패널에서 두 번 클릭.
// 하는 일: 글자만 바꿉니다(틀 · 글꼴 · 크기 · 색은 그대로, 바꾼 글은 원래 글의 서식을 이어받음).
//   넘치는 한 줄짜리 틀만 오른쪽으로 조금 넓힙니다(왼쪽 사이드바는 1/3 선을 넘지 않게).
//   인턴 설명 두 줄의 순서를 바꿔 '실물 모형 제작' 줄을 먼저 둡니다(글은 그대로).
//   끝에 '블루엘리펀트 · PROTEAN' 이 남은 곳을 찾아 알려 줍니다(지원서에서 빼야 함 — 줄을 지우는 일은 레이아웃이 바뀌어 직접).
//   한 번의 실행 취소(⌘Z)로 되돌릴 수 있고, 같은 폴더에 '…_GENTLE MONSTER OBJECT.indd' 로 따로 저장합니다(원본 그대로).
// 근거: GM_OBJECT_CV_proposal.pdf (2026-11-25) — 모집요강(기업 분석 K0) + 혁주님이 이미 쓴 글(젠틀몬스터 문항 2 · 자주 · 젠틀몬스터 CV).

#target indesign

(function () {
    // [찾을 글(여럿이면 차례로 시도), 바꿀 글, 옵션]
    // side: "left" 사이드바만 / "right" 오른쪽만, whole: 문단 전체가 그 글일 때만, spaced: 자간 넓은 영문, regex: 찾을 글이 GREP 식
    var CHANGES = [
        [["CREATIVE INTERN"], "SPACE OBJECT DESIGNER", {spaced: true}],
        [["블루엘리펀트 콘텐츠 디자인 인턴", "블루엘리펀트 비주얼 콘텐츠 디자인 인턴 지원"], "젠틀몬스터 공간 오브제 디자이너", {side: "left"}],
        [["레퍼런스에서 찾은 아이디어를 이미지로 옮기려는 지원자"], "오브제가 공간 속에서 하나의 장면이 되게 하려는 지원자", {side: "left"}],
        [["리서치로 생각하고,"], "틀을 배우고,", {whole: true}],
        [["시각화로 먼저 확인하는 디자이너"], "그 안을 채우는 건축학도", {whole: true}],
        [["건축을 공부하며 파사드 디자인에 관심"], "옷에 대한 관심은 건축보다 먼저", {}],
        [["포토샵 · 일러스트 · 렌더링으로 시각화"], "건축으로 공간의 크기와 거리를 가늠하는 감각", {whole: true}],
        [["고객이 매장과 화면에서 처음 만나는 이미지를 목표로", "파사드부터 썸네일까지 비주얼 콘텐츠 디자인을 목표로",
          "브랜드의 분위기를 이미지로 전하는 디자이너를 목표로", "상상을 정확한 크기의 이미지로 옮기는 일을 목표로"],
         "아트 오브제와 가구, 마감재 기획을 목표로", {}],
        [["사진 · 패션"], "패션 · 공간", {whole: true}],
        [["파사드 디자인"], "가구와 조명 수집", {whole: true}],
        [["해외 레퍼런스 리서치"], "실내 마감재와 마감 방식", {whole: true}],
        [["리서치로 컨셉을 세우고, 해외 자료를 하나의 컨셉으로 묶어 정리합니다"], "리서치와 분석으로 컨셉을 세우고, 하나의 생각을 끝까지 형태로 밀고 갑니다", {}],
        [["만들기 전에 렌더링과 후보정으로 재료와 색을 미리 확인합니다"], "원색 대신 채도를 낮춘 색으로 포인트를 주고 주변과 어우러지게 합니다", {}],
        [["포토샵 · 일러스트 · 인디자인으로 시각화와 후보정, AI 툴도 적극 활용"], "스타일을 가리지 않고 입어 보며 기른 안목 — 원단 · 디자인 · 색감", {}],
        [["평소 찍은 사진과 패션 사진을 개인 SNS에 올립니다"], "만들기 전에 3D로 먼저 구현해 크기와 배치를 확인합니다", {}],
        [["기획력"], "기획", {whole: true}],
        [["미리 확인"], "컬러 감도", {whole: true}],
        [["이미지 작업"], "패션에 대한 안목", {whole: true}],
        [["사진과 패션"], "구상을 미리 확인", {whole: true}],
        [["블루엘리펀트[^\\r\\n]*?지원"], "젠틀몬스터 공간 오브제 디자이너 지원", {side: "right", regex: true}]
    ];

    if (app.documents.length === 0) { alert("먼저 블루엘리펀트 이력서 .indd 를 열어 주세요."); return; }
    var doc = app.activeDocument;
    if (!confirm("젠틀몬스터 공간 오브제 디자이너 내용으로 " + CHANGES.length + "곳의 글을 바꿉니다.\n레이아웃 · 서식은 그대로이고, 끝나면 '_GENTLE MONSTER OBJECT' 이름으로 따로 저장합니다.\n계속할까요?")) return;

    function esc(s) { return s.replace(/([\\^$.*+?()\[\]{}|~])/g, "\\$1"); }
    function pattern(src, opt) {
        var p;
        if (opt.regex) p = src;
        else if (opt.spaced) {
            var chars = src.replace(/ /g, "").split(""), parts = [];
            for (var i = 0; i < chars.length; i++) parts.push(esc(chars[i]));
            p = parts.join("\\s*");
        } else p = esc(src).replace(/ +/g, "\\s+");
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
            report.push((n ? "✓ " : "✗ 못 찾음 ") + (hit || srcs[0]) + "  →  " + dst + (n > 1 ? "  (" + n + "곳)" : ""));
        }
        // 인턴 설명 두 줄: '실물 모형 제작' 을 '현장 실측' 앞으로 (같은 글 상자 안에서 문단 내용만 맞바꿈)
        var a = grep("현장\\s*실측[^\\r]*"), b = grep("실물\\s*모형\\s*제작[^\\r]*"), swapped = false;
        if (a.length === 1 && b.length === 1) {
            var pa = a[0].paragraphs[0], pb2 = b[0].paragraphs[0];
            if (pa.parentStory === pb2.parentStory && pa.index < pb2.index) {
                var ta = a[0].contents, tb = b[0].contents;
                b[0].contents = ta; a[0].contents = tb; swapped = true;
            } else if (pa.parentStory !== pb2.parentStory) {
                var ga = pa.parentTextFrames[0].geometricBounds, gb2 = pb2.parentTextFrames[0].geometricBounds;
                if (ga[0] < gb2[0]) { var xa = a[0].contents, xb = b[0].contents; b[0].contents = xa; a[0].contents = xb; swapped = true; }
            }
        }
        report.push(swapped ? "✓ 인턴 설명 순서: 실물 모형 제작 → 현장 실측" : "– 인턴 설명 순서: 이미 바뀌어 있거나 찾지 못해 그대로");
        // 남은 블루엘리펀트 · PROTEAN
        var left = grep("블루엘리펀트|BLUE\\s*ELEPHANT|Blue\\s*Elephant|PROTEAN");
        for (var r = 0; r < left.length; r++) {
            var para = "";
            try { para = left[r].paragraphs[0].contents.replace(/[\r\n]+/g, " "); } catch (e) {}
            warn.push("남은 언급 — 지원서에서 빼 주세요: " + para.substring(0, 60));
        }
        app.findGrepPreferences = NothingEnum.nothing;
        app.changeGrepPreferences = NothingEnum.nothing;
    }
    app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "젠틀몬스터 공간 오브제 내용으로 바꾸기");

    var saved = "";
    try {
        if (doc.saved) {
            var p = doc.fullName.fsName.replace(/\.indd$/i, "") + "_GENTLE MONSTER OBJECT.indd";
            doc.save(new File(p));
            saved = "\n\n저장: " + p;
        } else { saved = "\n\n(저장되지 않은 문서라 따로 저장하지 않았습니다 — 다른 이름으로 저장해 주세요.)"; }
    } catch (e) { saved = "\n\n저장하지 못했습니다: " + e; }
    alert(report.join("\n") + (warn.length ? "\n\n" + warn.join("\n") : "") + saved);
})();
