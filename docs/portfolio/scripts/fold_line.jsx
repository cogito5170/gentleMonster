// 대화형 PDF 를 책처럼 보이게: 펼침마다 가운데 접힘선(+ 선택: 접힘 그림자)을 그린다.
//
// 쓰는 법: InDesign 에서 문서를 연 채로 파일 → 스크립트 → 스크립트 찾아보기 → 이 파일.
// - 새 레이어 "Fold" 맨 위에 그린다. 두 쪽짜리 펼침에만 그리고, 표지처럼 한 쪽인 펼침은 건너뛴다.
// - 다시 실행하면 "Fold" 레이어를 지우고 새로 그린다(설정을 바꿔 다시 돌려도 된다).
// - 인쇄용 PDF 를 뽑을 때는 레이어 패널에서 "Fold" 의 눈을 끄면 된다.
// - 실행 취소 한 번으로 전부 되돌린다.

var LINE_WEIGHT = 0.3;   // pt
var LINE_TINT = 45;      // 검정 %
var SHADOW = true;       // 접힘 양옆에 옅은 그림자
var SHADOW_WIDTH = 28;   // pt (한쪽)
var SHADOW_OPACITY = 14; // %

function run() {
    if (app.documents.length === 0) { alert("열린 문서가 없습니다."); return; }
    var doc = app.activeDocument;
    var vp = doc.viewPreferences;
    var saved = { h: vp.horizontalMeasurementUnits, v: vp.verticalMeasurementUnits, o: vp.rulerOrigin };
    vp.horizontalMeasurementUnits = MeasurementUnits.POINTS;
    vp.verticalMeasurementUnits = MeasurementUnits.POINTS;
    vp.rulerOrigin = RulerOrigin.SPREAD_ORIGIN;

    var layer = doc.layers.itemByName("Fold");
    if (layer.isValid) {
        layer.locked = false;
        while (layer.pageItems.length > 0) layer.pageItems[0].remove();
    } else {
        layer = doc.layers.add({ name: "Fold" });
    }
    layer.move(LocationOptions.AT_BEGINNING);
    layer.visible = true;
    layer.printable = true;

    var black = doc.swatches.itemByName("Black");
    var none = doc.swatches.itemByName("None");
    var count = 0;

    for (var i = 0; i < doc.spreads.length; i++) {
        var spread = doc.spreads[i];
        if (spread.pages.length !== 2) continue;
        var b = spread.pages[0].bounds; // [위, 왼, 아래, 오른]
        var x = b[3], top = b[0], bottom = b[2];

        if (SHADOW) {
            shade(spread, layer, [top, x - SHADOW_WIDTH, bottom, x], 180, black, none);
            shade(spread, layer, [top, x, bottom, x + SHADOW_WIDTH], 0, black, none);
        }
        var line = spread.graphicLines.add(layer);
        line.geometricBounds = [top, x, bottom, x];
        line.strokeWeight = LINE_WEIGHT;
        line.strokeColor = black;
        line.strokeTint = LINE_TINT;
        count++;
    }
    layer.locked = true;

    vp.horizontalMeasurementUnits = saved.h;
    vp.verticalMeasurementUnits = saved.v;
    vp.rulerOrigin = saved.o;
    alert("접힘선을 " + count + "개 펼침에 그렸습니다. (레이어: Fold)");
}

// 접힘 쪽이 진하고 바깥으로 갈수록 사라지는 사각형
function shade(spread, layer, bounds, angle, black, none) {
    var r = spread.rectangles.add(layer);
    r.geometricBounds = bounds;
    r.fillColor = black;
    r.strokeColor = none;
    r.strokeWeight = 0;
    r.transparencySettings.blendingSettings.blendMode = BlendMode.MULTIPLY;
    r.transparencySettings.blendingSettings.opacity = SHADOW_OPACITY;
    var g = r.transparencySettings.gradientFeatherSettings;
    g.applied = true;
    g.type = GradientType.LINEAR;
    g.angle = angle; // 0: 왼쪽이 진함, 180: 오른쪽이 진함
}

app.doScript(run, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT, "가운데 접힘선");
