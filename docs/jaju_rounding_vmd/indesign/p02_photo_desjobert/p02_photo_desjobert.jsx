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
C["White"] = color("White", [242, 242, 242]);
C["Label"] = color("Label", [140, 140, 140]);
C["Body"] = color("Body", [181, 181, 181]);
C["English"] = color("English", [126, 126, 126]);
C["Edge"] = color("Edge", [90, 90, 90]);
function ps(n, f, fs, size, lead, fill, j, tr, sc, sw, sb) { var s = doc.paragraphStyles.itemByName(n); if (!s.isValid) s = doc.paragraphStyles.add({name: n}); try { s.appliedFont = f; } catch (e) {} try { s.fontStyle = fs; } catch (e) {} s.pointSize = size; s.leading = lead; s.fillColor = fill; s.justification = j; s.hyphenation = false; s.tracking = tr; s.spaceBefore = sb + "pt"; if (sc) { s.strokeColor = sc; s.strokeWeight = sw; } return s; }
var S = {};
S["Label"] = ps("Label", "IBM Plex Mono", "Regular", 5.6, 7, C["Label"], Justification.LEFT_ALIGN, 140, null, 0, 0);
S["Title"] = ps("Title", "Pretendard", "SemiBold", 13, 18, C["White"], Justification.LEFT_ALIGN, 0, null, 0, 0);
S["Body"] = ps("Body", "Pretendard", "Regular", 7.8, 13, C["Body"], Justification.LEFT_ALIGN, 0, null, 0, 0);
S["Body Next"] = ps("Body Next", "Pretendard", "Regular", 7.8, 13, C["Body"], Justification.LEFT_ALIGN, 0, null, 0, 4);
S["Body Last"] = ps("Body Last", "Pretendard", "Regular", 7.8, 13, C["White"], Justification.LEFT_ALIGN, 0, null, 0, 4);
S["English"] = ps("English", "Lora", "Italic", 6.4, 9.6, C["English"], Justification.LEFT_ALIGN, 0, null, 0, 0);
var r = pg.rectangles.add({geometricBounds: [-3.0, -3.0, 213.0, 300.0], fillColor: C["Black"], strokeWeight: 0, name: "background (black)"});
var r = pg.rectangles.add({geometricBounds: [-3.0, -3.0, 213.0, 300.0], strokeWeight: 0, name: "photo"});
var img = File(File($.fileName).parent + "/Links/opening_book_dark.jpg"); if (img.exists) { r.place(img); r.graphics[0].geometricBounds = [-3.0000, -16.2522, 213.0000, 313.2522]; } else alert("Links/opening_book_dark.jpg missing");
var r = pg.rectangles.add({geometricBounds: [24, 203, 188, 285], fillColor: C["Black"], strokeWeight: 0, name: "text box"});
r.strokeColor = C["Edge"]; r.strokeWeight = "0.15mm";
r.transparencySettings.blendingSettings.opacity = 72;
var t = pg.textFrames.add({geometricBounds: [32.247, 210, 36.247, 280], contents: "PROLOGUE", name: "label top"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["Label"];
var t = pg.textFrames.add({geometricBounds: [41.882, 210, 65.882, 280], contents: "\ubc16\uc5d0\uc11c \ubcf4\uba74 \uc0c1\ud488\uc774 \ubcf4\uc774\uace0,\r\uc548\uc5d0\uc11c \ubcf4\uba74 \uc0ac\ub78c\uc774 \ubcf4\uc778\ub2e4.", name: "title"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["Title"];
t.paragraphs[1].appliedParagraphStyle = S["Title"];
var t = pg.textFrames.add({geometricBounds: [68.917, 210, 134.917, 278], contents: "\uc0ac\ub78c\ub4e4\uc740 \uc1fc\uc708\ub3c4\ub97c \ubc16\uc5d0\uc11c \ubcf8\ub2e4. \ub098\ub294 \uc548\uc5d0\uc11c \ubcf8\ub2e4.\r\uc548\uc5d0\uc11c \ubcf4\uba74 \uac00\uac8c \uc774\ub984\uc740 \uac70\uafb8\ub85c \uc77d\ud788\uace0, \uc9c4\uc5f4\uc740 \ub4f1\uc744 \ubcf4\uc778\ub2e4.\r\ub300\uc2e0 \uc720\ub9ac \ub108\uba38\ub85c \uc0ac\ub78c\ub4e4\uc758 \uc5bc\uad74\uc774 \ubcf4\uc778\ub2e4.\r\ub300\ubd80\ubd84\uc740 \uadf8\ub0e5 \uc9c0\ub098\uac04\ub2e4. \uac00\ub054 \ub204\uad70\uac00 \uac78\uc74c\uc744 \uba48\ucd94\uace0, \ub4e4\uc5ec\ub2e4\ubcf4\uace0, \uc6c3\ub294\ub2e4.\r\ub098\ub294 \uadf8 \uc0ac\ub78c\uc774 \ubb34\uc5c7\uc744 \ubcf4\uace0 \uc6c3\uc5c8\ub294\uc9c0 \ubcf8\ub2e4.\r\uc9c4\uc5f4\uc758 \ub2f5\uc740 \uc0c1\ud488\uc774 \uc544\ub2c8\ub77c \uadf8 \ud45c\uc815\uc5d0 \uc788\uae30 \ub54c\ubb38\uc774\ub2e4.\r\uadf8\ub798\uc11c \ub098\ub294 \uc548\uc5d0\uc11c \ubc16\uc744 \ubcf4\ub294 VMD\uac00 \ub418\ub824 \ud55c\ub2e4.", name: "body"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["Body"];
t.paragraphs[1].appliedParagraphStyle = S["Body Next"];
t.paragraphs[2].appliedParagraphStyle = S["Body Next"];
t.paragraphs[3].appliedParagraphStyle = S["Body Next"];
t.paragraphs[4].appliedParagraphStyle = S["Body Next"];
t.paragraphs[5].appliedParagraphStyle = S["Body Next"];
t.paragraphs[6].appliedParagraphStyle = S["Body Last"];
var t = pg.textFrames.add({geometricBounds: [136.564, 210, 170.564, 278], contents: "People look at a shop window from outside. I look from inside. From inside, the shop\u2019s name reads backwards and the display shows its back. Instead, I see faces through the glass. Most people walk past. Now and then someone stops, looks in, and smiles. I watch what made them smile. The answer to a display is in that face, not in the product. So I want to be a VMD who looks out from the inside.", name: "english"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["English"];
var t = pg.textFrames.add({geometricBounds: [180.247, 210, 184.247, 280], contents: "FROM THE INSIDE", name: "label bottom"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;
t.paragraphs[0].appliedParagraphStyle = S["Label"];
})();
