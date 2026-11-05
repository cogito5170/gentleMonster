// Portfolio mockup board, 1920 x 1080 px. InDesign: File > Scripts > Scripts panel. Keep the Links folder next to this file.
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
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [30, 40, 360, 540], fillColor: C["Cream"], strokeWeight: 0, name: "OBSERVE spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [60.5, 62.0, 340.5, 518.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "OBSERVE spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [59.0, 63.5, 338.0, 516.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "OBSERVE spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [57.5, 65.0, 336.5, 290.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "OBSERVE spread left page"});
var f = File(here + "/Links/observe_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [57.5, 290.0, 336.5, 515.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "OBSERVE spread right page"});
var f = File(here + "/Links/observe_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [375, 40, 705, 540], fillColor: C["Cream"], strokeWeight: 0, name: "MATCH MOOD spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [405.5, 62.0, 685.5, 518.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "MATCH MOOD spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [404.0, 63.5, 683.0, 516.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "MATCH MOOD spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [402.5, 65.0, 681.5, 290.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "MATCH MOOD spread left page"});
var f = File(here + "/Links/match_mood_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [402.5, 290.0, 681.5, 515.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "MATCH MOOD spread right page"});
var f = File(here + "/Links/match_mood_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [720, 40, 1050, 540], fillColor: C["Cream"], strokeWeight: 0, name: "CONTAIN spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [750.5, 62.0, 1030.5, 518.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "CONTAIN spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [749.0, 63.5, 1028.0, 516.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "CONTAIN spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [747.5, 65.0, 1026.5, 290.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "CONTAIN spread left page"});
var f = File(here + "/Links/contain_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [747.5, 290.0, 1026.5, 515.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "CONTAIN spread right page"});
var f = File(here + "/Links/contain_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [30, 1380, 360, 1880], fillColor: C["Cream"], strokeWeight: 0, name: "WHERE PEOPLE STOP spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [60.5, 1402.0, 340.5, 1858.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "WHERE PEOPLE STOP spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [59.0, 1403.5, 338.0, 1856.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "WHERE PEOPLE STOP spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [57.5, 1405.0, 336.5, 1630.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "WHERE PEOPLE STOP spread left page"});
var f = File(here + "/Links/where_people_stop_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [57.5, 1630.0, 336.5, 1855.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "WHERE PEOPLE STOP spread right page"});
var f = File(here + "/Links/where_people_stop_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [375, 1380, 705, 1880], fillColor: C["Cream"], strokeWeight: 0, name: "MATCH spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [405.5, 1402.0, 685.5, 1858.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "MATCH spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [404.0, 1403.5, 683.0, 1856.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "MATCH spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [402.5, 1405.0, 681.5, 1630.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "MATCH spread left page"});
var f = File(here + "/Links/match_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [402.5, 1630.0, 681.5, 1855.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "MATCH spread right page"});
var f = File(here + "/Links/match_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Background"], undefined, undefined, {geometricBounds: [720, 1380, 1050, 1880], fillColor: C["Cream"], strokeWeight: 0, name: "ARCHITECTURE TO INTERIOR spread panel"});
shadow(r, 35, 0, 2, 5);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [750.5, 1402.0, 1030.5, 1858.0], fillColor: C["Paper Edge"], strokeWeight: 0, name: "ARCHITECTURE TO INTERIOR spread page edge"});
shadow(r, 40, 0, 6, 8);
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [749.0, 1403.5, 1028.0, 1856.5], fillColor: C["Paper Edge Light"], strokeWeight: 0, name: "ARCHITECTURE TO INTERIOR spread page edge light"});
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [747.5, 1405.0, 1026.5, 1630.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "ARCHITECTURE TO INTERIOR spread left page"});
var f = File(here + "/Links/architecture_interior_L.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Spreads"], undefined, undefined, {geometricBounds: [747.5, 1630.0, 1026.5, 1855.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "ARCHITECTURE TO INTERIOR spread right page"});
var f = File(here + "/Links/architecture_interior_R.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
var r = pg.rectangles.add(LY["Cover"], undefined, undefined, {geometricBounds: [144.0, 641.0, 944.0, 1287.0], fillColor: C["Cover Edge"], strokeWeight: 0, name: "cover thickness"});
rot(r, 6);
var r = pg.rectangles.add(LY["Cover"], undefined, undefined, {geometricBounds: [140.0, 637.0, 940.0, 1283.0], fillColor: doc.swatches.itemByName("None"), strokeWeight: 0, name: "cover"});
var f = File(here + "/Links/cover.jpg"); if (f.exists) { r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }
shadow(r, 75, 16, 22, 34);
rot(r, 6);
})();
