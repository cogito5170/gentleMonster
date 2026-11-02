// Four cards, 1920 x 1080 px. InDesign: File > Scripts > Scripts panel. Keep the Links folder next to this file.
#target indesign
(function () {
var here = File($.fileName).parent;
app.scriptPreferences.measurementUnit = MeasurementUnits.PIXELS;
var doc = app.documents.add({documentPreferences: {pageWidth: 1920, pageHeight: 1080, facingPages: false, pagesPerDocument: 1, intent: DocumentIntentOptions.WEB_INTENT}});
doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.PIXELS; doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.PIXELS;
doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN; doc.zeroPoint = [0, 0];
var pg = doc.pages[0];
function color(n, v) { var c = doc.colors.itemByName(n); if (!c.isValid) c = doc.colors.add({name: n, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: v}); return c; }
var C = {};
C["Card Black"] = color("Card Black", [18, 18, 18]);
C["White"] = color("White", [255, 255, 255]);
C["Ink"] = color("Ink", [17, 17, 17]);
C["Page"] = color("Page", [255, 255, 255]);
function ps(n, size, lead, col, j, tr, tint) { var s = doc.paragraphStyles.add({name: n}); try { s.appliedFont = "Pretendard"; } catch (e) {} s.pointSize = size; s.leading = lead; s.fillColor = C[col]; if (tint > 0) s.fillTint = tint; s.justification = j; s.hyphenation = false; s.tracking = tr; return s; }
var S = {};
S["Label Dark"] = ps("Label Dark", 17, 20, "Ink", Justification.CENTER_ALIGN, 0, -1);
S["Label Light"] = ps("Label Light", 17, 20, "White", Justification.CENTER_ALIGN, 0, -1);
S["Card Title"] = ps("Card Title", 29, 34, "White", Justification.LEFT_ALIGN, -5, -1);
S["Card Body"] = ps("Card Body", 16.5, 21, "White", Justification.LEFT_ALIGN, 0, 90);
function round(r, rad) { if (!rad) return; r.topLeftCornerOption = r.topRightCornerOption = r.bottomLeftCornerOption = r.bottomRightCornerOption = CornerOptions.ROUNDED_CORNER; r.topLeftCornerRadius = r.topRightCornerRadius = r.bottomLeftCornerRadius = r.bottomRightCornerRadius = rad; }
var r = pg.rectangles.add({geometricBounds: [0, 0, 1080, 1920], fillColor: C["Page"], strokeWeight: 0, name: "page"}); round(r, 0);
var r = pg.rectangles.add({geometricBounds: [360, 40.0, 960, 491.0], fillColor: C["Card Black"], strokeWeight: 0, name: "card 1 Passion background"}); round(r, 44);
var r = pg.rectangles.add({geometricBounds: [386, 68.0, 430, 186.0], fillColor: C["White"], strokeWeight: 0, name: "card 1 Passion label pill"}); round(r, 22);
var t = pg.textFrames.add({geometricBounds: [386, 68.0, 430, 186.0], contents: "Passion", name: "card 1 Passion label"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
t.paragraphs[0].appliedParagraphStyle = S["Label Dark"];
var r = pg.rectangles.add({geometricBounds: [736, 80.0, 762, 82.0], fillColor: C["White"], strokeWeight: 0, name: "card 1 Passion plus v"}); round(r, 0);
var r = pg.rectangles.add({geometricBounds: [748, 68.0, 750, 94.0], fillColor: C["White"], strokeWeight: 0, name: "card 1 Passion plus h"}); round(r, 0);
var t = pg.textFrames.add({geometricBounds: [790, 68.0, 860, 451.0], contents: "Clothes came first,\rbuildings came after", name: "card 1 Passion title"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Card Title"];
t.paragraphs[1].appliedParagraphStyle = S["Card Title"];
var t = pg.textFrames.add({geometricBounds: [876, 68.0, 922, 428.0], contents: "I grew up wandering shops, asking how things should be placed to sell better.", name: "card 1 Passion body"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Card Body"];
var r = pg.rectangles.add({geometricBounds: [540, 503.0, 1040, 954.0], fillColor: C["Card Black"], strokeWeight: 0, name: "card 2 Observe photo"}); round(r, 44);
var f = File(here + "/Links/card2.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.FILL_PROPORTIONALLY); r.fit(FitOptions.CENTER_CONTENT); }
var r = pg.rectangles.add({geometricBounds: [566, 531.0, 610, 649.0], fillColor: doc.swatches.itemByName("None"), strokeColor: C["White"], strokeWeight: 2, name: "card 2 Observe label pill"}); round(r, 22);
var t = pg.textFrames.add({geometricBounds: [566, 531.0, 610, 649.0], contents: "Observe", name: "card 2 Observe label"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
t.paragraphs[0].appliedParagraphStyle = S["Label Light"];
var r = pg.rectangles.add({geometricBounds: [816, 543.0, 842, 545.0], fillColor: C["White"], strokeWeight: 0, name: "card 2 Observe plus v"}); round(r, 0);
var r = pg.rectangles.add({geometricBounds: [828, 531.0, 830, 557.0], fillColor: C["White"], strokeWeight: 0, name: "card 2 Observe plus h"}); round(r, 0);
var t = pg.textFrames.add({geometricBounds: [870, 531.0, 940, 914.0], contents: "I look from the inside,\rout to the people", name: "card 2 Observe title"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Card Title"];
t.paragraphs[1].appliedParagraphStyle = S["Card Title"];
var t = pg.textFrames.add({geometricBounds: [956, 531.0, 1002, 891.0], contents: "Behind the glass I watch what makes someone stop, look in and smile.", name: "card 2 Observe body"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Card Body"];
var r = pg.rectangles.add({geometricBounds: [360, 966.0, 960, 1417.0], fillColor: C["Card Black"], strokeWeight: 0, name: "card 3 Display photo"}); round(r, 44);
var f = File(here + "/Links/card3.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.FILL_PROPORTIONALLY); r.fit(FitOptions.CENTER_CONTENT); }
var r = pg.rectangles.add({geometricBounds: [386, 994.0, 430, 1112.0], fillColor: doc.swatches.itemByName("None"), strokeColor: C["White"], strokeWeight: 2, name: "card 3 Display label pill"}); round(r, 22);
var t = pg.textFrames.add({geometricBounds: [386, 994.0, 430, 1112.0], contents: "Display", name: "card 3 Display label"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
t.paragraphs[0].appliedParagraphStyle = S["Label Light"];
var r = pg.rectangles.add({geometricBounds: [736, 1006.0, 762, 1008.0], fillColor: C["White"], strokeWeight: 0, name: "card 3 Display plus v"}); round(r, 0);
var r = pg.rectangles.add({geometricBounds: [748, 994.0, 750, 1020.0], fillColor: C["White"], strokeWeight: 0, name: "card 3 Display plus h"}); round(r, 0);
var t = pg.textFrames.add({geometricBounds: [790, 994.0, 860, 1377.0], contents: "A window should hold\rthe passer-by", name: "card 3 Display title"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Card Title"];
t.paragraphs[1].appliedParagraphStyle = S["Card Title"];
var t = pg.textFrames.add({geometricBounds: [876, 994.0, 922, 1354.0], contents: "Light, height and one point of colour \u2014 architecture taught me where the eye lands.", name: "card 3 Display body"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Card Body"];
var r = pg.rectangles.add({geometricBounds: [540, 1429.0, 1040, 1880.0], fillColor: C["Card Black"], strokeWeight: 0, name: "card 4 Styling photo"}); round(r, 44);
var f = File(here + "/Links/card4.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.FILL_PROPORTIONALLY); r.fit(FitOptions.CENTER_CONTENT); }
var r = pg.rectangles.add({geometricBounds: [566, 1457.0, 610, 1575.0], fillColor: doc.swatches.itemByName("None"), strokeColor: C["White"], strokeWeight: 2, name: "card 4 Styling label pill"}); round(r, 22);
var t = pg.textFrames.add({geometricBounds: [566, 1457.0, 610, 1575.0], contents: "Styling", name: "card 4 Styling label"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
t.paragraphs[0].appliedParagraphStyle = S["Label Light"];
var r = pg.rectangles.add({geometricBounds: [816, 1469.0, 842, 1471.0], fillColor: C["White"], strokeWeight: 0, name: "card 4 Styling plus v"}); round(r, 0);
var r = pg.rectangles.add({geometricBounds: [828, 1457.0, 830, 1483.0], fillColor: C["White"], strokeWeight: 0, name: "card 4 Styling plus h"}); round(r, 0);
var t = pg.textFrames.add({geometricBounds: [870, 1457.0, 940, 1840.0], contents: "Dressed for the place,\rtoned to the hour", name: "card 4 Styling title"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Card Title"];
t.paragraphs[1].appliedParagraphStyle = S["Card Title"];
var t = pg.textFrames.add({geometricBounds: [956, 1457.0, 1002, 1817.0], contents: "I match an outfit to where it will be seen, the way a store matches its season.", name: "card 4 Styling body"});
t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
t.paragraphs[0].appliedParagraphStyle = S["Card Body"];
})();
