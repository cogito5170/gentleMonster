// SPA portfolio mockup board, 1920 x 1080 px. InDesign: File > Scripts > Scripts panel. Keep the Links folder next to this file.
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
C["Board"] = color("Board", [27, 27, 28]);
C["Cream"] = color("Cream", [238, 232, 216]);
C["Paper Edge"] = color("Paper Edge", [217, 212, 200]);
C["Paper Edge Light"] = color("Paper Edge Light", [243, 240, 233]);
C["Cover Edge"] = color("Cover Edge", [190, 186, 178]);
var LY = {}; var l0 = doc.layers[0];
LY["Background"] = l0; l0.name = "Background";
LY["Spreads"] = doc.layers.add({name: "Spreads"}); LY["Spreads"].move(LocationOptions.AT_BEGINNING);
LY["Cover"] = doc.layers.add({name: "Cover"}); LY["Cover"].move(LocationOptions.AT_BEGINNING);
function shadow(r, o, x, y, s) { var d = r.transparencySettings.dropShadowSettings; d.mode = ShadowMode.DROP; d.blendMode = BlendMode.MULTIPLY; d.opacity = o; d.xOffset = x; d.yOffset = y; d.size = s; d.effectColor = doc.colors.itemByName("Black"); }
function rot(r, a) { r.transform(CoordinateSpaces.PASTEBOARD_COORDINATES, AnchorPoint.CENTER_ANCHOR, app.transformationMatrices.add({counterclockwiseRotationAngle: a})); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [0, 0, 1080, 1920], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "board texture"});
var f = File(here + "/Links/background.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [30, 40, 360, 540], fillColor: C["Cream"], strokeWeight: 0, name: "STYLE spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [48.0, 72.0, 353.0, 508.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "STYLE spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [46.5, 73.5, 350.5, 506.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "STYLE spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [45.0, 75.0, 349.0, 290.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "STYLE spread left page"});
var f = File(here + "/Links/style_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [45.0, 290.0, 349.0, 505.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "STYLE spread right page"});
var f = File(here + "/Links/style_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [375, 40, 705, 540], fillColor: C["Cream"], strokeWeight: 0, name: "PICTURE spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [393.0, 72.0, 698.0, 508.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "PICTURE spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [391.5, 73.5, 695.5, 506.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "PICTURE spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [390.0, 75.0, 694.0, 290.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "PICTURE spread left page"});
var f = File(here + "/Links/picture_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [390.0, 290.0, 694.0, 505.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "PICTURE spread right page"});
var f = File(here + "/Links/picture_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [720, 40, 1050, 540], fillColor: C["Cream"], strokeWeight: 0, name: "I STOP spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [738.0, 72.0, 1043.0, 508.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "I STOP spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [736.5, 73.5, 1040.5, 506.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "I STOP spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [735.0, 75.0, 1039.0, 290.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "I STOP spread left page"});
var f = File(here + "/Links/i_stop_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [735.0, 290.0, 1039.0, 505.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "I STOP spread right page"});
var f = File(here + "/Links/i_stop_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [30, 1380, 360, 1880], fillColor: C["Cream"], strokeWeight: 0, name: "ARCHITECTURE spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [48.0, 1412.0, 353.0, 1848.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "ARCHITECTURE spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [46.5, 1413.5, 350.5, 1846.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "ARCHITECTURE spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [45.0, 1415.0, 349.0, 1630.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "ARCHITECTURE spread left page"});
var f = File(here + "/Links/architecture_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [45.0, 1630.0, 349.0, 1845.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "ARCHITECTURE spread right page"});
var f = File(here + "/Links/architecture_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [375, 1380, 705, 1880], fillColor: C["Cream"], strokeWeight: 0, name: "WEB DESIGN spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [393.0, 1412.0, 698.0, 1848.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "WEB DESIGN spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [391.5, 1413.5, 695.5, 1846.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "WEB DESIGN spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [390.0, 1415.0, 694.0, 1630.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "WEB DESIGN spread left page"});
var f = File(here + "/Links/web_design_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [390.0, 1630.0, 694.0, 1845.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "WEB DESIGN spread right page"});
var f = File(here + "/Links/web_design_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [720, 1380, 1050, 1880], fillColor: C["Cream"], strokeWeight: 0, name: "HAND-MADE MODEL spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [738.0, 1412.0, 1043.0, 1848.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "HAND-MADE MODEL spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [736.5, 1413.5, 1040.5, 1846.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "HAND-MADE MODEL spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [735.0, 1415.0, 1039.0, 1630.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "HAND-MADE MODEL spread left page"});
var f = File(here + "/Links/model_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [735.0, 1630.0, 1039.0, 1845.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "HAND-MADE MODEL spread right page"});
var f = File(here + "/Links/model_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Cover"], undefined, undefined, {geometricBounds: [114.0, 660.0, 974.0, 1268.0], fillColor: C["Cover Edge"], strokeWeight: 0, name: "cover thickness"});
rot(r, 6);
var r = pg.rectangles.add(LY["Cover"], undefined, undefined, {geometricBounds: [110.0, 656.0, 970.0, 1264.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "cover SPA"});
var f = File(here + "/Links/cover.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
shadow(r, 75, 16, 22, 34);
rot(r, 6);
})();
