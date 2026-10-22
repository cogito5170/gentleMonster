// JAJU 포트폴리오 3쪽(Prologue) — InDesign: 창 > 유틸리티 > 스크립트 패널에서 실행. 생성: tools/jaju_layout/indd_p03.py
#target indesign
(function () {
app.scriptPreferences.measurementUnit = MeasurementUnits.MILLIMETERS;
var doc = app.documents.add({documentPreferences: {pageWidth: 297.0, pageHeight: 210.0, facingPages: false, pagesPerDocument: 1, documentBleedUniformSize: true, documentBleedTopOffset: 3.0}});
doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS; doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;
doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN; doc.zeroPoint = [0, 0];
doc.sections[0].continueNumbering = false; doc.sections[0].pageNumberStart = 2;
var pg = doc.pages[0];
function color(n, v) { var c = doc.colors.itemByName(n); if (!c.isValid) c = doc.colors.add({name: n, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: v}); return c; }
var C = {None: doc.swatches.itemByName("None")};
C["Black"] = color("Black", [10, 10, 10]);
C["Title"] = color("Title", [207, 207, 207]);
C["Body"] = color("Body", [189, 189, 189]);
C["Mute"] = color("Mute", [140, 140, 140]);
C["White"] = color("White", [242, 242, 242]);
function ps(n, f, fs, size, lead, fill, j, tr, sc, sw, sb) { var s = doc.paragraphStyles.itemByName(n); if (!s.isValid) s = doc.paragraphStyles.add({name: n}); try { s.appliedFont = f; } catch (e) {} try { s.fontStyle = fs; } catch (e) {} s.pointSize = size; s.leading = lead; s.fillColor = fill; s.justification = j; s.hyphenation = false; s.tracking = tr; s.spaceBefore = sb + "pt"; if (sc) { s.strokeColor = sc; s.strokeWeight = sw; } return s; }
var S = {};
S["Title"] = ps("Title", "Noto Serif KR", "Regular", 17, 22, C["Title"], Justification.CENTER_ALIGN, 20, null, 0, 0);
S["Subtitle"] = ps("Subtitle", "Crimson Pro", "Regular", 9, 11, C["Mute"], Justification.CENTER_ALIGN, 140, null, 0, 0);
S["Body KO"] = ps("Body KO", "Noto Serif KR", "Light", 9.6, 17, C["Body"], Justification.CENTER_ALIGN, 0, null, 0, 0);
S["Body KO Next"] = ps("Body KO Next", "Noto Serif KR", "Light", 9.6, 17, C["Body"], Justification.CENTER_ALIGN, 0, null, 0, 8);
S["Body KO Last"] = ps("Body KO Last", "Noto Serif KR", "Regular", 9.6, 17, C["White"], Justification.CENTER_ALIGN, 0, null, 0, 8);
S["Body EN"] = ps("Body EN", "Instrument Sans", "Regular", 8, 13, C["Mute"], Justification.CENTER_ALIGN, 0, null, 0, 0);
pg.rectangles.add({geometricBounds: [-3.0, -3.0, 213.0, 300.0], fillColor: C["Black"], strokeWeight: 0, name: "background"});
var t = pg.textFrames.add({geometricBounds: [34.882, 20, 44.882, 277], contents: "\ubc16\uc5d0\uc11c \ubcf4\uba74 \uc0c1\ud488\uc774 \ubcf4\uc774\uace0, \uc548\uc5d0\uc11c \ubcf4\uba74 \uc0ac\ub78c\uc774 \ubcf4\uc778\ub2e4.", name: "title"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["Title"];
var t = pg.textFrames.add({geometricBounds: [46.353, 20, 52.353, 277], contents: "FROM THE STREET YOU SEE THE PRODUCTS. FROM INSIDE, YOU SEE THE PEOPLE.", name: "subtitle"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["Subtitle"];
var t = pg.textFrames.add({geometricBounds: [67.305, 48.5, 131.305, 248.5], contents: "\uc0ac\ub78c\ub4e4\uc740 \uc1fc\uc708\ub3c4\ub97c \ubc16\uc5d0\uc11c \ubcf8\ub2e4. \ub098\ub294 \uc548\uc5d0\uc11c \ubcf8\ub2e4.\r\uc548\uc5d0\uc11c \ubcf4\uba74 \uac00\uac8c \uc774\ub984\uc740 \uac70\uafb8\ub85c \uc77d\ud788\uace0, \uc9c4\uc5f4\uc740 \ub4f1\uc744 \ubcf4\uc778\ub2e4.\r\ub300\uc2e0 \uc720\ub9ac \ub108\uba38\ub85c \uc0ac\ub78c\ub4e4\uc758 \uc5bc\uad74\uc774 \ubcf4\uc778\ub2e4.\r\ub300\ubd80\ubd84\uc740 \uadf8\ub0e5 \uc9c0\ub098\uac04\ub2e4. \uac00\ub054 \ub204\uad70\uac00 \uac78\uc74c\uc744 \uba48\ucd94\uace0, \ub4e4\uc5ec\ub2e4\ubcf4\uace0, \uc6c3\ub294\ub2e4.\r\ub098\ub294 \uadf8 \uc0ac\ub78c\uc774 \ubb34\uc5c7\uc744 \ubcf4\uace0 \uc6c3\uc5c8\ub294\uc9c0 \ubcf8\ub2e4.\r\uc9c4\uc5f4\uc758 \ub2f5\uc740 \uc0c1\ud488\uc774 \uc544\ub2c8\ub77c \uadf8 \ud45c\uc815\uc5d0 \uc788\uae30 \ub54c\ubb38\uc774\ub2e4.\r\uadf8\ub798\uc11c \ub098\ub294 \uc548\uc5d0\uc11c \ubc16\uc744 \ubcf4\ub294 VMD\uac00 \ub418\ub824 \ud55c\ub2e4.", name: "body ko"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["Body KO"];
t.paragraphs[1].appliedParagraphStyle = S["Body KO"];
t.paragraphs[2].appliedParagraphStyle = S["Body KO"];
t.paragraphs[3].appliedParagraphStyle = S["Body KO Next"];
t.paragraphs[4].appliedParagraphStyle = S["Body KO"];
t.paragraphs[5].appliedParagraphStyle = S["Body KO"];
t.paragraphs[6].appliedParagraphStyle = S["Body KO Last"];
var t = pg.textFrames.add({geometricBounds: [134.882, 63.5, 164.882, 233.5], contents: "People look at a shop window from outside. I look from inside. From inside, the shop\u2019s name reads backwards and the display shows its back. Instead, I see faces through the glass. Most people walk past. Now and then someone stops, looks in, and smiles. I watch what made them smile. The answer to a display is in that face, not in the product. So I want to be a VMD who looks out from the inside.", name: "body en"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["Body EN"];
})();
