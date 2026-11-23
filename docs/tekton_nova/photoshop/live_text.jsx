// TEKTON NOVA - live type layers. Open tekton_nova_screen.psd, then File > Scripts > Browse... > this file.
// Adds the group "COPY (live text)" at the same positions as the raster preview and hides the preview.
// If Inter is not installed, Photoshop substitutes a font: select the group and change the font.
#target photoshop
(function () {
if (!app.documents.length) { alert("Open tekton_nova_screen.psd first."); return; }
var doc = app.activeDocument;
var ru = app.preferences.rulerUnits, tu = app.preferences.typeUnits;
app.preferences.rulerUnits = Units.PIXELS; app.preferences.typeUnits = TypeUnits.PIXELS;
var set = doc.layerSets.add(); set.name = "COPY (live text)";
function px(v) { return v.as ? v.as("px") : v; }
function add(name, txt, font, size, leading, tracking, rgb, opacity, box) {
  var l = set.artLayers.add(); l.kind = LayerKind.TEXT; l.name = name;
  var t = l.textItem; t.contents = txt;
  try { t.font = font; } catch (e) {}
  t.size = new UnitValue(size, "px");
  if (leading > 0) { t.useAutoLeading = false; t.leading = new UnitValue(leading, "px"); }
  t.tracking = tracking;
  var c = new SolidColor(); c.rgb.red = rgb[0]; c.rgb.green = rgb[1]; c.rgb.blue = rgb[2]; t.color = c;
  t.position = [new UnitValue(box[0], "px"), new UnitValue(box[1] + size, "px")];
  l.opacity = opacity;
  var b = l.bounds; l.translate(new UnitValue(box[0] - px(b[0]), "px"), new UnitValue(box[1] - px(b[1]), "px"));
}
add("Eyebrow", "INTRODUCING", "Inter-SemiBold", 28, 0, 320, [255, 255, 255], 72, [222, 261]);
add("Eyebrow - product", "TEKTON NOVA", "Inter-SemiBold", 28, 0, 320, [255, 138, 61], 100, [534, 261]);
add("Headline", "A Universe\rIn Your Hand.", "InterDisplay-Bold", 132, 129, -25, [255, 255, 255], 100, [220, 333]);
add("Body 1", "Designed from the edge of light to the curve of glass,\rNOVA brings the depth of the night sky\rto the screen you hold every day.", "Inter-Regular", 38, 56, 0, [255, 255, 255], 86, [220, 635]);
add("Subhead", "Crafted Form. Endless Display.", "Inter-SemiBold", 40, 0, -5, [255, 138, 61], 100, [222, 867]);
add("Body 2", "A frameless display, a warm metal body\rand a design that fits the way you move.", "Inter-Regular", 34, 50, 0, [255, 255, 255], 78, [221, 932]);
add("Footer text", "EXPERIENCE NOVA \u2014 NOW ON DISPLAY", "Inter-SemiBold", 26, 0, 300, [255, 255, 255], 100, [342, 1180]);
try { doc.layerSets.getByName("COPY (raster preview)").visible = false; } catch (e) {}
app.preferences.rulerUnits = ru; app.preferences.typeUnits = tu;
})();
