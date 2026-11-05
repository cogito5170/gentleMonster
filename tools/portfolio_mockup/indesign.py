"""Portfolio mockup board as an InDesign file, 1920 x 1080 px (web intent, 1 px = 1 pt).
Cover in the middle, three open spreads on each side.

python3 tools/portfolio_mockup/indesign.py [spa|vmd]      (default spa)

  spa  docs/portfolio_mockup/        — SPA portfolio (A4 pages, portrait cover)
  vmd  docs/portfolio_mockup_vmd/    — VMD portfolio (landscape pages read as spreads; cover = right half of page 1)

  <dir>/indesign/<name>.idml   open in InDesign (File > Open), save as .indd
  <dir>/indesign/<name>.jsx    builds the same page inside InDesign (File > Scripts)
  <dir>/indesign/Links/*.jpg   background, cover and the 12 half-pages (2x)
  <dir>/indesign/<name>.pdf/.jpg  preview of the same coordinates
  <dir>/<name>_indesign.zip    all of the above in one folder

Pages: <dir>/pages (rendered from the applicant's own portfolio PDF).
Live in InDesign: three layers (Background / Spreads / Cover), cream panels, page edges, every half-page
as its own linked frame (relink to swap a spread), the cover rotated -6 deg with a drop shadow.
Baked into the links only: the gutter shade on each half-page and the spine/gloss on the cover.
"""
import html
import json
import math
import os
import subprocess
import sys
import zipfile

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
CONFIGS = {
    'spa': dict(dir='docs/portfolio_mockup', name='portfolio_mockup_1920x1080', ratio=1.4155, sw=430, cover_h=860, cover_ratio=1273 / 1800,
                left=[('STYLE', 'style.jpg'), ('PICTURE', 'picture.jpg'), ('I STOP', 'i_stop.jpg')],
                right=[('ARCHITECTURE', 'architecture.jpg'), ('WEB DESIGN', 'web_design.jpg'), ('HAND-MADE MODEL', 'model.jpg')]),
    # rows = chapters: left the opener, right its content page
    'vmd': dict(dir='docs/portfolio_mockup_vmd', name='portfolio_vmd_mockup_1920x1080', ratio=2000 / 1238, sw=450, cover_h=800, cover_ratio=1303 / 1613,
                left=[('OBSERVE', 'observe.jpg'), ('MATCH MOOD', 'match_mood.jpg'), ('CONTAIN', 'contain.jpg')],
                right=[('WHERE PEOPLE STOP', 'where_people_stop.jpg'), ('MATCH', 'match.jpg'), ('ARCHITECTURE TO INTERIOR', 'architecture_interior.jpg')]),
}
CFG = CONFIGS[sys.argv[1] if len(sys.argv) > 1 else 'spa']
BASE = os.path.join(REPO, CFG['dir'])
PAGES = os.path.join(BASE, 'pages')
OUT = os.path.join(BASE, 'indesign')
LINKS = os.path.join(OUT, 'Links')
NAME = CFG['name']
W, H = 1920, 1080

# layout (px)
PANEL_W, PANEL_H = 500, 330
ROWS = [30, 375, 720]
COLX = {'L': 40, 'R': W - 40 - PANEL_W}
SW = CFG['sw']
SH = round(SW / CFG['ratio'])
LEFT, RIGHT = CFG['left'], CFG['right']
COVER_H = CFG['cover_h']
COVER_W = round(COVER_H * CFG['cover_ratio'])
COVER_ANGLE = 6          # degrees, counter-clockwise (top leans left)
COLORS = {'Board': (27, 27, 28), 'Cream': (238, 232, 216), 'Paper Edge': (217, 212, 200), 'Paper Edge Light': (243, 240, 233), 'Cover Edge': (190, 186, 178)}
SHADOW = {'panel': (35, 0, 2, 5), 'spread': (40, 0, 6, 8), 'cover': (75, 16, 22, 34)}   # opacity, x, y, size


def items():
    """Every object in drawing order. x, y, w, h in px; rot = counter-clockwise degrees about the centre."""
    out = [dict(kind='image', layer='Background', name='board texture', x=0, y=0, w=W, h=H, link='background.jpg', scale=1)]
    for side, lst in (('L', LEFT), ('R', RIGHT)):
        for (title, src), y in zip(lst, ROWS):
            x = COLX[side]
            sx, sy = x + (PANEL_W - SW) / 2, y + (PANEL_H - SH) / 2 + 2
            tag = f'{title} spread'
            out.append(dict(kind='rect', layer='Background', name=f'{tag} panel', x=x, y=y, w=PANEL_W, h=PANEL_H, fill='Cream', shadow='panel'))
            out.append(dict(kind='rect', layer='Spreads', name=f'{tag} page edge', x=sx - 3, y=sy + 3, w=SW + 6, h=SH + 1, fill='Paper Edge', shadow='spread'))
            out.append(dict(kind='rect', layer='Spreads', name=f'{tag} page edge light', x=sx - 1.5, y=sy + 1.5, w=SW + 3, h=SH, fill='Paper Edge Light'))
            stem = os.path.splitext(src)[0]
            out.append(dict(kind='image', layer='Spreads', name=f'{tag} left page', x=sx, y=sy, w=SW / 2, h=SH, link=f'{stem}_L.jpg', src=src, half='L', scale=.5))
            out.append(dict(kind='image', layer='Spreads', name=f'{tag} right page', x=sx + SW / 2, y=sy, w=SW / 2, h=SH, link=f'{stem}_R.jpg', src=src, half='R', scale=.5))
    cx, cy = W / 2, H / 2
    out.append(dict(kind='rect', layer='Cover', name='cover thickness', x=cx - COVER_W / 2 + 4, y=cy - COVER_H / 2 + 4, w=COVER_W, h=COVER_H, fill='Cover Edge', rot=COVER_ANGLE, pivot=(cx, cy)))
    out.append(dict(kind='image', layer='Cover', name='cover', x=cx - COVER_W / 2, y=cy - COVER_H / 2, w=COVER_W, h=COVER_H, link='cover.jpg', src='cover.jpg', scale=.5, rot=COVER_ANGLE, pivot=(cx, cy), shadow='cover'))
    return out


# ── links ────────────────────────────────────────────────────────────────────────────
def make_links(its):
    os.makedirs(LINKS, exist_ok=True)
    rng = np.random.default_rng(7)
    # board: dark charcoal, soft vignette, fine grain (code-rendered texture)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .7)) ** 2)
    base = 42 - 20 * np.clip(r, 0, 1.2) ** 1.6
    coarse = np.asarray(Image.fromarray(rng.normal(128, 40, (H // 3, W // 3)).clip(0, 255).astype('uint8')).resize((W, H), Image.BICUBIC), float) - 128
    grain = rng.normal(0, 5.5, (H, W)) + coarse * .08
    g = np.clip(base + grain, 0, 255)
    Image.fromarray(np.dstack([g, g, g * 1.01]).clip(0, 255).astype('uint8')).save(os.path.join(LINKS, 'background.jpg'), quality=88, dpi=(72, 72))
    for it in its:
        if it['kind'] != 'image' or 'src' not in it:
            continue
        im = Image.open(os.path.join(PAGES, it['src'])).convert('RGB')
        tw, th = round(it['w'] * 2), round(it['h'] * 2)
        if 'half' in it:
            hw = im.width // 2
            im = im.crop((0, 0, hw, im.height) if it['half'] == 'L' else (im.width - hw, 0, im.width, im.height)).resize((tw, th), Image.LANCZOS)
            a = np.asarray(im, float)
            t = np.linspace(0, 1, tw)[None, :, None]
            if it['half'] == 'R':
                t = t[:, ::-1]
            # t = 0 outer edge … 1 gutter
            dark = np.where(t > .72, .30 * (np.clip(t - .72, 0, None) / .28) ** 1.7, 0) + np.where(t < .1, -.05 * (1 - t / .1), 0)
            a = a * (1 - dark)
        else:
            im = im.resize((tw, th), Image.LANCZOS)
            a = np.asarray(im, float)
            u = np.linspace(0, 1, tw)[None, :, None]
            spine = np.where(u < .07, np.interp(u, [0, .012, .03, .07], [-.28, .30, -.10, 0]), 0)
            gx, gy = np.meshgrid(np.linspace(0, 1, tw), np.linspace(0, 1, th))
            d = (gx * .8 + gy * .45) / 1.25
            gloss = np.interp(d, [0, .32, .62, 1], [.14, 0, 0, -.12])[:, :, None]
            a = a + (255 - a) * np.clip(spine + gloss, 0, None) - a * np.clip(-(spine + gloss), 0, None)
        Image.fromarray(a.clip(0, 255).astype('uint8')).save(os.path.join(LINKS, it['link']), quality=90, dpi=(144, 144))
        it['px'] = (tw, th)
    for it in its:
        if it.get('link') == 'background.jpg':
            it['px'] = (W, H)


# ── IDML ─────────────────────────────────────────────────────────────────────────────
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="8.0"'
HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
T0 = f'1 0 0 1 {-W / 2} {-H / 2}'
LAYERS = [('Background', 'Gray'), ('Spreads', 'LightBlue'), ('Cover', 'Red')]
LID = {n: f'uL{i}' for i, (n, _) in enumerate(LAYERS)}
q = lambda s: html.escape(s, quote=True)


def geom(x, y, w, h):
    pts = [(x, y), (x, y + h), (x + w, y + h), (x + w, y)]
    pp = ''.join(f'<PathPointType Anchor="{a:.3f} {b:.3f}" LeftDirection="{a:.3f} {b:.3f}" RightDirection="{a:.3f} {b:.3f}"/>' for a, b in pts)
    return f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pp}</PathPointArray></GeometryPathType></PathGeometry></Properties>'


def placement(it):
    """(geometry in inner coords, ItemTransform, inner top-left) — rotated items use centre-origin inner coords."""
    if not it.get('rot'):
        return geom(it['x'], it['y'], it['w'], it['h']), T0, (it['x'], it['y'])
    a = math.radians(it['rot'])
    c, s = math.cos(a), math.sin(a)
    px, py = it['pivot']
    # inner origin at the pivot; the item's own offset from the pivot stays in inner coords
    ix, iy = it['x'] - px, it['y'] - py
    tr = f'{c:.6f} {-s:.6f} {s:.6f} {c:.6f} {px - W / 2:.3f} {py - H / 2:.3f}'
    return geom(ix, iy, it['w'], it['h']), tr, (ix, iy)


def shadow_xml(key):
    if not key:
        return ''
    o, x, y, sz = SHADOW[key]
    return (f'<TransparencySetting><DropShadowSetting Mode="Drop" BlendMode="Multiply" Opacity="{o}" XOffset="{x}" YOffset="{y}" Size="{sz}" '
            'Spread="0" Noise="0" EffectColor="Color/Black" KnockedOut="true" UseGlobalLight="false"/></TransparencySetting>')


def build_idml(its, path):
    graphic = (HDR + f'<idPkg:Graphic {NS}>'
               '<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               + ''.join(f'<Color Self="Color/{n}" Model="Process" Space="RGB" ColorValue="{r} {g} {b}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="{n}" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>' for n, (r, g, b) in COLORS.items())
               + '<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/></idPkg:Graphic>')
    styles = (HDR + f'<idPkg:Styles {NS}>'
              '<RootCharacterStyleGroup Self="u79"><CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" Name="$ID/[No character style]"/></RootCharacterStyleGroup>'
              '<RootParagraphStyleGroup Self="u78"><ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false"/>'
              '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle></RootParagraphStyleGroup>'
              '<RootCellStyleGroup Self="u8e"><CellStyle Self="CellStyle/$ID/[None]" Name="$ID/[None]"/></RootCellStyleGroup>'
              '<RootTableStyleGroup Self="u90"><TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/><TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"/></RootTableStyleGroup>'
              '<RootObjectStyleGroup Self="u97"><ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/></RootObjectStyleGroup>'
              '</idPkg:Styles>')
    prefs = (HDR + f'<idPkg:Preferences {NS}>'
             f'<DocumentPreference PageHeight="{H}" PageWidth="{W}" PagesPerDocument="1" FacingPages="false" DocumentBleedTopOffset="0" DocumentBleedBottomOffset="0" '
             'DocumentBleedInsideOrLeftOffset="0" DocumentBleedOutsideOrRightOffset="0" DocumentBleedUniformSize="true" PageBinding="LeftToRight" AllowPageShuffle="true" Intent="WebIntent"/>'
             '<MarginPreference ColumnCount="1" ColumnGutter="12" Top="30" Bottom="30" Left="40" Right="40" ColumnDirection="Horizontal"/>'
             '<ViewPreference HorizontalMeasurementUnits="Pixels" VerticalMeasurementUnits="Pixels" RulerOrigin="PageOrigin"/>'
             '</idPkg:Preferences>')
    els = []
    for n, it in enumerate(its, 1):
        g, tr, (ix, iy) = placement(it)
        common = f'Self="uR{n}" Name="{q(it["name"])}" ItemLayer="{LID[it["layer"]]}" Locked="false" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{tr}"'
        if it['kind'] == 'rect':
            els.append(f'<Rectangle {common} ContentType="Unassigned" FillColor="Color/{it["fill"]}">{g}{shadow_xml(it.get("shadow"))}</Rectangle>')
        else:
            pw, ph = it['px']
            sc = it['scale']
            ppi = round(72 / sc)
            els.append(f'<Rectangle {common} ContentType="GraphicType" FillColor="Swatch/None">{g}{shadow_xml(it.get("shadow"))}'
                       f'<Image Self="uI{n}" ItemTransform="{sc} 0 0 {sc} {ix:.3f} {iy:.3f}" Space="RGB" ActualPpi="{ppi} {ppi}" EffectivePpi="{ppi} {ppi}">'
                       f'<Properties><Profile type="string">$ID/Embedded</Profile><GraphicBounds Left="0" Top="0" Right="{pw}" Bottom="{ph}"/></Properties>'
                       f'<Link Self="uK{n}" LinkResourceURI="file:Links/{it["link"]}" LinkResourceFormat="$ID/JPEG" StoredState="Normal"/></Image></Rectangle>')
    spread = (HDR + f'<idPkg:Spread {NS}><Spread Self="uSp0" PageCount="1" BindingLocation="0" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" ShowMasterItems="true">'
              f'<Page Self="uP0" Name="1" AppliedMaster="n" GeometricBounds="0 0 {H} {W}" ItemTransform="{T0}" OverrideList="" TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true"/>'
              + ''.join(els) + '</Spread></idPkg:Spread>')
    layers = ''.join(f'<Layer Self="{LID[n]}" Name="{n}" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true">'
                     f'<Properties><LayerColor type="enumeration">{c}</LayerColor></Properties></Layer>' for n, c in LAYERS)
    design = (HDR + '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="8.0(370)" ?>\n'
              f'<Document {NS} Self="d" StoryList="" ZeroPoint="0 0" ActiveLayer="{LID["Cover"]}">'
              '<idPkg:Graphic src="Resources/Graphic.xml"/><idPkg:Styles src="Resources/Styles.xml"/><idPkg:Preferences src="Resources/Preferences.xml"/>'
              + layers + '<idPkg:Spread src="Spreads/Spread_uSp0.xml"/>'
              '<Section Self="uSec" Length="1" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageNumberStart="1" Marker="" PageStart="uP0" SectionPrefix=""/>'
              '</Document>')
    container = (HDR + '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>')
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/vnd.adobe.indesign-idml-package', compress_type=zipfile.ZIP_STORED)
        put = lambda n, d: z.writestr(n, d.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)
        put('META-INF/container.xml', container); put('designmap.xml', design)
        put('Resources/Graphic.xml', graphic); put('Resources/Styles.xml', styles); put('Resources/Preferences.xml', prefs)
        put('Spreads/Spread_uSp0.xml', spread)


# ── JSX ──────────────────────────────────────────────────────────────────────────────
def build_jsx(its, path):
    js = lambda v: json.dumps(v, ensure_ascii=True)
    L = ['// Portfolio mockup board, 1920 x 1080 px. InDesign: File > Scripts > Scripts panel. Keep the Links folder next to this file.',
         '#target indesign', '(function () {', 'var here = File($.fileName).parent;',
         'app.scriptPreferences.measurementUnit = MeasurementUnits.PIXELS;',
         f'var doc = app.documents.add({{documentPreferences: {{pageWidth: {W}, pageHeight: {H}, facingPages: false, pagesPerDocument: 1, intent: DocumentIntentOptions.WEB_INTENT}}}});',
         'doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.PIXELS; doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.PIXELS;',
         'doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN; doc.zeroPoint = [0, 0];',
         'var pg = doc.pages[0];',
         'function color(n, v) { var c = doc.colors.itemByName(n); if (!c.isValid) c = doc.colors.add({name: n, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: v}); return c; }',
         'var C = {};']
    L += [f'C[{js(n)}] = color({js(n)}, {list(c)});' for n, c in COLORS.items()]
    L.append('var LY = {}; var l0 = doc.layers[0];')
    for i, (n, _) in enumerate(LAYERS):
        L.append(f'LY[{js(n)}] = ' + (f'l0; l0.name = {js(n)};' if i == 0 else f'doc.layers.add({{name: {js(n)}}}); LY[{js(n)}].move(LocationOptions.AT_BEGINNING);'))
    L.append('function shadow(r, o, x, y, s) { var d = r.transparencySettings.dropShadowSettings; d.mode = ShadowMode.DROP; d.blendMode = BlendMode.MULTIPLY;'
             ' d.opacity = o; d.xOffset = x; d.yOffset = y; d.size = s; d.effectColor = doc.colors.itemByName("Black"); }')
    L.append('function rot(r, a) { r.transform(CoordinateSpaces.PASTEBOARD_COORDINATES, AnchorPoint.CENTER_ANCHOR, app.transformationMatrices.add({counterclockwiseRotationAngle: a})); }')
    for it in its:
        b = [round(it['y'], 3), round(it['x'], 3), round(it['y'] + it['h'], 3), round(it['x'] + it['w'], 3)]
        fill = f'C[{js(it["fill"])}]' if it['kind'] == 'rect' else 'doc.swatches.itemByName("None")'
        L.append(f'var r = pg.rectangles.add(LY[{js(it["layer"])}], undefined, undefined, {{geometricBounds: {b}, fillColor: {fill}, strokeWeight: 0, name: {js(it["name"])}}});')
        if it['kind'] == 'image':
            L.append(f'var f = File(here + "/Links/{it["link"]}"); if (f.exists) {{ r.place(f); r.fit(FitOptions.CONTENT_TO_FRAME); }}')
        if it.get('shadow'):
            L.append('shadow(r, %s, %s, %s, %s);' % SHADOW[it['shadow']])
        if it.get('rot'):
            L.append(f'rot(r, {it["rot"]});')   # about the frame centre (= board centre for the cover)
    L.append('})();')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


# ── preview (same coordinates, HTML) ─────────────────────────────────────────────────
def build_preview(its, base):
    from pathlib import Path
    el = []
    for it in its:
        box = f'left:{it["x"]}px;top:{it["y"]}px;width:{it["w"]}px;height:{it["h"]}px'
        tf = ''
        if it.get('rot'):
            px, py = it['pivot']
            tf = f'transform-origin:{px - it["x"]}px {py - it["y"]}px;transform:rotate({-it["rot"]}deg);'
        sh = ''
        if it.get('shadow'):
            o, x, y, s = SHADOW[it['shadow']]
            sh = f'box-shadow:{x}px {y}px {s * 1.2}px rgba(0,0,0,{o / 100});'
        bg = f'background:rgb{COLORS[it["fill"]]}' if it['kind'] == 'rect' else f'background:url({Path(LINKS, it["link"]).as_uri()}) 0 0/100% 100%'
        el.append(f'<div style="{box};{bg};{sh}{tf}"></div>')
    page = ('<!doctype html><html><head><meta charset="utf-8"><style>@page{size:1920px 1080px;margin:0}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#1b1b1c}'
            'div{position:absolute}</style></head><body>' + ''.join(el) + '</body></html>')
    h = base + '.html'
    with open(h, 'w', encoding='utf-8') as f:
        f.write(page)
    return h


def main():
    os.makedirs(OUT, exist_ok=True)
    its = items(); make_links(its)
    build_idml(its, os.path.join(OUT, NAME + '.idml'))
    build_jsx(its, os.path.join(OUT, NAME + '.jsx'))
    tmp = os.path.join(REPO, 'out', os.path.basename(BASE)); os.makedirs(tmp, exist_ok=True)
    h = build_preview(its, os.path.join(tmp, NAME))
    subprocess.run(['node', os.path.join(REPO, 'tools/web_cards/preview.mjs'), h, os.path.join(OUT, NAME)], check=True)
    z = os.path.join(BASE, NAME + '_indesign.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zz:
        for ext in ('.idml', '.jsx', '.pdf', '.jpg'):
            zz.write(os.path.join(OUT, NAME + ext), f'{NAME}/{NAME}{ext}')
        for f in sorted(os.listdir(LINKS)):
            zz.write(os.path.join(LINKS, f), f'{NAME}/Links/{f}')
    print('산출물:', os.path.relpath(OUT, REPO), '·', os.path.relpath(z, REPO))


if __name__ == '__main__':
    main()
