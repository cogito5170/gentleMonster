// P1 표지 + 1쪽 — InDesign: 파일 > 스크립트 > 스크립트 패널에서 실행하거나, 이 파일을 스크립트 패널 폴더에 두고 두 번 클릭.
// Links/cover.jpg 가 이 파일 옆에 있어야 한다. 생성: tools/p1_layout/cover_p1.py
#target indesign
(function () {
var here = File($.fileName).parent;
app.scriptPreferences.measurementUnit = MeasurementUnits.MILLIMETERS;
var doc = app.documents.add({documentPreferences: {pageWidth: 297.0, pageHeight: 210.0, facingPages: false, pagesPerDocument: 2, documentBleedUniformSize: true, documentBleedTopOffset: 3.0}});
doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS;
doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;
doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN; doc.zeroPoint = [0, 0];
function color(n, v) { var c = doc.colors.itemByName(n); if (!c.isValid) c = doc.colors.add({name: n, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: v}); return c; }
var C = {};
C["Ink"] = color("Ink", [27, 26, 24]);
C["Stock"] = color("Stock", [230, 225, 218]);
C["White"] = color("White", [255, 255, 255]);
function pstyle(n, f, fs, size, lead, col, j) { var s = doc.paragraphStyles.itemByName(n); if (!s.isValid) s = doc.paragraphStyles.add({name: n}); try { s.appliedFont = f; } catch (e) {} try { s.fontStyle = fs; } catch (e) {} s.pointSize = size; s.leading = lead; s.fillColor = C[col]; s.justification = j; s.hyphenation = false; return s; }
var S = {};
S["Header Bold"] = pstyle("Header Bold", "Pretendard", "Bold", 9.5, 12, "Ink", Justification.LEFT_ALIGN);
S["Header"] = pstyle("Header", "Pretendard", "Regular", 9.5, 12, "Ink", Justification.LEFT_ALIGN);
S["Header Right"] = pstyle("Header Right", "Pretendard", "Regular", 9.5, 12, "Ink", Justification.RIGHT_ALIGN);
S["Header Bold Right"] = pstyle("Header Bold Right", "Pretendard", "Bold", 9.5, 12, "Ink", Justification.RIGHT_ALIGN);
S["Cover Title"] = pstyle("Cover Title", "EB Garamond", "Regular", 56, 52, "White", Justification.LEFT_ALIGN);
S["Cover Name"] = pstyle("Cover Name", "Pretendard", "Regular", 8.5, 11, "White", Justification.LEFT_ALIGN);
S["Lead KO"] = pstyle("Lead KO", "Pretendard", "Regular", 9.5, 16.5, "Ink", Justification.LEFT_ALIGN);
S["Caption EN"] = pstyle("Caption EN", "Pretendard", "Regular", 6.6, 9, "Ink", Justification.LEFT_JUSTIFIED);
S["Title"] = pstyle("Title", "EB Garamond", "Regular", 78, 70, "Ink", Justification.LEFT_ALIGN);
S["Folio"] = pstyle("Folio", "EB Garamond", "Italic", 7, 8, "Ink", Justification.LEFT_ALIGN);
var img = File(here + '/Links/cover.jpg');
var r = doc.pages[0].rectangles.add({geometricBounds: [-3.0, -3.0, 213.0, 300.0], strokeWeight: 0, name: "cover image"});
if (img.exists) { r.place(img); r.graphics[0].geometricBounds = [-3.0000, -4.9737, 213.0000, 301.9737]; } else alert("Links/cover.jpg \uC5C6\uC74C");
var t = doc.pages[0].textFrames.add({geometricBounds: [116, 12, 190, 152], contents: "From the\rinside", name: "cover title"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
t.paragraphs[0].appliedParagraphStyle = S["Cover Title"];
t.paragraphs[1].appliedParagraphStyle = S["Cover Title"];
try { t.parentStory.characters.itemByRange(5, 7).fontStyle = "Italic"; } catch (e) {}
var t = doc.pages[0].textFrames.add({geometricBounds: [193, 12, 203, 82], contents: "JEONG HYEOKJU\rVisual Merchandiser Portfolio \u00b7 2026", name: "cover name"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Cover Name"];
t.paragraphs[1].appliedParagraphStyle = S["Cover Name"];
try { t.parentStory.characters.itemByRange(0, 12).fontStyle = "Bold"; } catch (e) {}
var r = doc.pages[1].rectangles.add({geometricBounds: [-3.0, -3.0, 213.0, 300.0], fillColor: C["Stock"], strokeWeight: 0, name: "paper"}); r.sendToBack();
var t = doc.pages[1].textFrames.add({geometricBounds: [7, 10, 13, 90], contents: "FROM THE INSIDE", name: "header L1"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Header Bold"];
var t = doc.pages[1].textFrames.add({geometricBounds: [7, 90.5, 13, 140.5], contents: "PROLOGUE", name: "header L2"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Header Right"];
var t = doc.pages[1].textFrames.add({geometricBounds: [7, 156.5, 13, 216.5], contents: "2026", name: "header R1"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Header Bold"];
var t = doc.pages[1].textFrames.add({geometricBounds: [7, 217, 13, 287], contents: "JEONG HYEOKJU", name: "header R2"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Header Bold Right"];
var t = doc.pages[1].textFrames.add({geometricBounds: [24, 10, 74, 138], contents: "\uc0ac\ub78c\ub4e4\uc740 \uc1fc\uc708\ub3c4\ub97c \ubc16\uc5d0\uc11c \ubcf8\ub2e4. \ub098\ub294 \uc548\uc5d0\uc11c \ubcf8\ub2e4.\r\uc548\uc5d0\uc11c \ubcf4\uba74 \uac00\uac8c \uc774\ub984\uc740 \uac70\uafb8\ub85c \uc77d\ud788\uace0, \uc9c4\uc5f4\uc740 \ub4f1\uc744 \ubcf4\uc778\ub2e4.\r\ub300\uc2e0 \uc720\ub9ac \ub108\uba38\ub85c \uc0ac\ub78c\ub4e4\uc758 \uc5bc\uad74\uc774 \ubcf4\uc778\ub2e4.\r\ub300\ubd80\ubd84\uc740 \uadf8\ub0e5 \uc9c0\ub098\uac04\ub2e4.\r\uac00\ub054 \ub204\uad70\uac00 \uac78\uc74c\uc744 \uba48\ucd94\uace0, \ub4e4\uc5ec\ub2e4\ubcf4\uace0, \uc6c3\ub294\ub2e4.\r\ub098\ub294 \uadf8 \uc0ac\ub78c\uc774 \ubb34\uc5c7\uc744 \ubcf4\uace0 \uc6c3\uc5c8\ub294\uc9c0 \ubcf8\ub2e4.\r\uc9c4\uc5f4\uc758 \ub2f5\uc740 \uc0c1\ud488\uc774 \uc544\ub2c8\ub77c \uadf8 \ud45c\uc815\uc5d0 \uc788\uae30 \ub54c\ubb38\uc774\ub2e4.\r\uadf8\ub798\uc11c \ub098\ub294 \uc548\uc5d0\uc11c \ubc16\uc744 \ubcf4\ub294 VMD\uac00 \ub418\ub824 \ud55c\ub2e4.", name: "lead ko"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Lead KO"];
t.paragraphs[1].appliedParagraphStyle = S["Lead KO"];
t.paragraphs[2].appliedParagraphStyle = S["Lead KO"];
t.paragraphs[3].appliedParagraphStyle = S["Lead KO"];
t.paragraphs[4].appliedParagraphStyle = S["Lead KO"];
t.paragraphs[5].appliedParagraphStyle = S["Lead KO"];
t.paragraphs[6].appliedParagraphStyle = S["Lead KO"];
t.paragraphs[7].appliedParagraphStyle = S["Lead KO"];
var t = doc.pages[1].textFrames.add({geometricBounds: [82, 78, 118, 140.5], contents: "From the inside \u2014 People look at a shop window from outside. I look from inside. From inside, the shop\u2019s name reads backwards and the display shows its back. Instead, I see faces through the glass. Most people walk past. Now and then someone stops, looks in, and smiles. I watch what made them smile. The answer to a display is in that face, not in the product. So I want to be a VMD who looks out from the inside.", name: "caption en"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Caption EN"];
try { t.parentStory.characters.itemByRange(0, 17).fontStyle = "Bold"; } catch (e) {}
var t = doc.pages[1].textFrames.add({geometricBounds: [118, 10, 198, 140], contents: "Inside,\rlooking\rout", name: "title"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
t.paragraphs[0].appliedParagraphStyle = S["Title"];
t.paragraphs[1].appliedParagraphStyle = S["Title"];
t.paragraphs[2].appliedParagraphStyle = S["Title"];
try { t.parentStory.characters.itemByRange(8, 14).fontStyle = "Italic"; } catch (e) {}
var r = doc.pages[1].rectangles.add({geometricBounds: [24, 156.5, 192, 287.0], strokeWeight: 0, name: "photo (cover detail)"});
if (img.exists) { r.place(img); r.graphics[0].geometricBounds = [24.0000, 156.5000, 192.0000, 395.2368]; } else alert("Links/cover.jpg \uC5C6\uC74C");
var t = doc.pages[1].textFrames.add({geometricBounds: [100.3, -3.1, 103.7, 16.9], contents: "page  1", name: "folio L"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Folio"];
try { t.parentStory.characters.itemByRange(6, 6).fontStyle = "Regular"; } catch (e) {}
t.transform(CoordinateSpaces.PASTEBOARD_COORDINATES, AnchorPoint.CENTER_ANCHOR, app.transformationMatrices.add({counterclockwiseRotationAngle: 90}));
var t = doc.pages[1].textFrames.add({geometricBounds: [106.3, 280.1, 109.7, 300.1], contents: "page  1", name: "folio R"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Folio"];
try { t.parentStory.characters.itemByRange(6, 6).fontStyle = "Regular"; } catch (e) {}
t.transform(CoordinateSpaces.PASTEBOARD_COORDINATES, AnchorPoint.CENTER_ANCHOR, app.transformationMatrices.add({counterclockwiseRotationAngle: -90}));
})();
