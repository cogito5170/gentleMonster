"""The four-card page as an InDesign file, 1920 x 1080 px (web intent, 1 px = 1 pt).

python3 tools/web_cards/indesign.py

  docs/web_cards/indesign/cards_1920x1080.idml   open in InDesign (File > Open), save as .indd
  docs/web_cards/indesign/cards_1920x1080.jsx    builds the same page inside InDesign (File > Scripts)
  docs/web_cards/indesign/Links/*.jpg            the three photos, cropped to their frames at 2x, dark fade baked in
  docs/web_cards/indesign/cards_1920x1080.pdf/.jpg  preview of the same coordinates
  docs/web_cards/cards_1920x1080_indesign.zip    all of the above in one folder

Copy: docs/web_cards/card_copy.md. Photos: the tone-matched copies in docs/tone_match (the applicant's own).
Everything is live in InDesign: frames, rounded corners, pills, text in paragraph styles, linked images.
"""
import html
import json
import os
import subprocess
import zipfile

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
OUT = os.path.join(REPO, 'docs/web_cards/indesign')
LINKS = os.path.join(OUT, 'Links')
TM = os.path.join(REPO, 'docs/tone_match')
W, H = 1920, 1080
FONT = 'Pretendard'

# layout (px): four cards in a row, the outer two... same rhythm as the draft: tall, short, tall, short
M, GAP = 40, 12
CW = (W - 2 * M - 3 * GAP) / 4
TALL, SHORT = (360, 600), (540, 500)          # (top, height)
CARDS = [
    dict(label='Passion', img=None, row=TALL, t=['Clothes came first,', 'buildings came after'],
         b='I grew up wandering shops, asking how things should be placed to sell better.'),
    dict(label='Observe', img='graded_cafe.jpg', focus=(.5, .62), row=SHORT, t=['I look from the inside,', 'out to the people'],
         b='Behind the glass I watch what makes someone stop, look in and smile.'),
    dict(label='Display', img='graded_shop.jpg', focus=(.5, .72), row=TALL, t=['A window should hold', 'the passer-by'],
         b='Light, height and one point of colour — architecture taught me where the eye lands.'),
    dict(label='Styling', img='graded_park.jpg', focus=(.5, .48), row=SHORT, t=['Dressed for the place,', 'toned to the hour'],
         b='I match an outfit to where it will be seen, the way a store matches its season.'),
]
R_CARD, PAD = 44, 28
COLORS = {'Card Black': (18, 18, 18), 'White': (255, 255, 255), 'Ink': (17, 17, 17), 'Page': (255, 255, 255)}
STYLES = {
    'Label Dark': dict(size=17, lead=20, color='Ink', align='center'),
    'Label Light': dict(size=17, lead=20, color='White', align='center'),
    'Card Title': dict(size=29, lead=34, color='White', align='left', track=-5),
    'Card Body': dict(size=16.5, lead=21, color='White', align='left', tint=90),
}


def items():
    """Every object on the page, in drawing order (x, y, w, h in px)."""
    out = [dict(kind='rect', name='page', x=0, y=0, w=W, h=H, fill='Page')]
    for i, c in enumerate(CARDS):
        x, (y, h) = M + i * (CW + GAP), c['row']
        tag = f'card {i + 1} {c["label"]}'
        if c['img']:
            out.append(dict(kind='image', name=f'{tag} photo', x=x, y=y, w=CW, h=h, link=f'card{i + 1}.jpg', src=c['img'], focus=c['focus']))
        else:
            out.append(dict(kind='rect', name=f'{tag} background', x=x, y=y, w=CW, h=h, fill='Card Black', radius=R_CARD))
        pw = round(len(c['label']) * 9.4 + 52)
        out.append(dict(kind='rect', name=f'{tag} label pill', x=x + PAD, y=y + 26, w=pw, h=44, radius=22,
                        fill='Swatch/None' if c['img'] else 'White', stroke='White' if c['img'] else None))
        out.append(dict(kind='text', name=f'{tag} label', x=x + PAD, y=y + 26, w=pw, h=44, valign='center',
                        paras=[('Label Light' if c['img'] else 'Label Dark', c['label'])]))
        by = y + h - 40 - 44
        ty = by - 16 - 70
        py = ty - 28 - 26
        out.append(dict(kind='rect', name=f'{tag} plus v', x=x + PAD + 12, y=py, w=2, h=26, fill='White'))
        out.append(dict(kind='rect', name=f'{tag} plus h', x=x + PAD, y=py + 12, w=26, h=2, fill='White'))
        out.append(dict(kind='text', name=f'{tag} title', x=x + PAD, y=ty, w=CW - PAD - 40, h=70, valign='top',
                        paras=[('Card Title', c['t'][0]), ('Card Title', c['t'][1])]))
        out.append(dict(kind='text', name=f'{tag} body', x=x + PAD, y=by, w=360, h=46, valign='top', paras=[('Card Body', c['b'])]))
    return out


def make_links(its):
    """Crop each photo to its frame (2x pixels) and bake the bottom dark fade in, so text reads on any photo."""
    os.makedirs(LINKS, exist_ok=True)
    for it in its:
        if it['kind'] != 'image':
            continue
        im = Image.open(os.path.join(TM, it['src'])).convert('RGB')
        tw, th = round(it['w'] * 2), round(it['h'] * 2)
        s = max(tw / im.width, th / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        fx, fy = it['focus']; left = min(max(round(im.width * fx - tw / 2), 0), im.width - tw); top = min(max(round(im.height * fy - th / 2), 0), im.height - th)
        a = np.asarray(im.crop((left, top, left + tw, top + th)), float)
        t = np.linspace(0, 1, th)[:, None, None]
        dark = np.where(t < .22, .15 * (1 - t / .22), np.where(t < .45, 0, .72 * (np.clip(t - .45, 0, None) / .55) ** 1.2))
        Image.fromarray((a * (1 - dark)).astype('uint8')).save(os.path.join(LINKS, it['link']), quality=90, dpi=(144, 144))
        it['px'] = (tw, th)


# ── IDML ─────────────────────────────────────────────────────────────────────────────
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="8.0"'
HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
T0 = f'1 0 0 1 {-W / 2} {-H / 2}'
q = lambda s: html.escape(s, quote=True)


def geom(x, y, w, h):
    pts = [(x, y), (x, y + h), (x + w, y + h), (x + w, y)]
    pp = ''.join(f'<PathPointType Anchor="{a:.3f} {b:.3f}" LeftDirection="{a:.3f} {b:.3f}" RightDirection="{a:.3f} {b:.3f}"/>' for a, b in pts)
    return f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pp}</PathPointArray></GeometryPathType></PathGeometry></Properties>'


def corners(r):
    if not r:
        return ''
    return ''.join(f' {k}CornerOption="RoundedCorner" {k}CornerRadius="{r}"' for k in ('TopLeft', 'TopRight', 'BottomLeft', 'BottomRight'))


def color_ref(n):
    return n if n.startswith('Swatch/') else f'Color/{n}'


def build_idml(its, path):
    graphic = (HDR + f'<idPkg:Graphic {NS}>'
               '<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               + ''.join(f'<Color Self="Color/{n}" Model="Process" Space="RGB" ColorValue="{r} {g} {b}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="{n}" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>' for n, (r, g, b) in COLORS.items())
               + '<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/></idPkg:Graphic>')
    just = {'left': 'LeftAlign', 'center': 'CenterAlign'}
    ps = ''.join(f'<ParagraphStyle Self="ParagraphStyle/{q(n)}" Name="{q(n)}" Imported="false" NextStyle="ParagraphStyle/{q(n)}" KeyboardShortcut="0 0" '
                 f'FontStyle="Regular" PointSize="{s["size"]}" FillColor="Color/{s["color"]}" FillTint="{s.get("tint", -1)}" Justification="{just[s["align"]]}" Hyphenation="false" Tracking="{s.get("track", 0)}">'
                 f'<Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn><PreviewColor type="enumeration">Nothing</PreviewColor>'
                 f'<AppliedFont type="string">{FONT}</AppliedFont><Leading type="unit">{s["lead"]}</Leading></Properties></ParagraphStyle>' for n, s in STYLES.items())
    styles = (HDR + f'<idPkg:Styles {NS}>'
              '<RootCharacterStyleGroup Self="u79"><CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" Name="$ID/[No character style]"/></RootCharacterStyleGroup>'
              '<RootParagraphStyleGroup Self="u78"><ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false"/>'
              '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>'
              + ps + '</RootParagraphStyleGroup>'
              '<RootCellStyleGroup Self="u8e"><CellStyle Self="CellStyle/$ID/[None]" Name="$ID/[None]"/></RootCellStyleGroup>'
              '<RootTableStyleGroup Self="u90"><TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/><TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"/></RootTableStyleGroup>'
              '<RootObjectStyleGroup Self="u97"><ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/></RootObjectStyleGroup>'
              '</idPkg:Styles>')
    prefs = (HDR + f'<idPkg:Preferences {NS}>'
             f'<DocumentPreference PageHeight="{H}" PageWidth="{W}" PagesPerDocument="1" FacingPages="false" DocumentBleedTopOffset="0" DocumentBleedBottomOffset="0" '
             'DocumentBleedInsideOrLeftOffset="0" DocumentBleedOutsideOrRightOffset="0" DocumentBleedUniformSize="true" PageBinding="LeftToRight" AllowPageShuffle="true" Intent="WebIntent"/>'
             f'<MarginPreference ColumnCount="4" ColumnGutter="{GAP}" Top="{M}" Bottom="{M}" Left="{M}" Right="{M}" ColumnDirection="Horizontal"/>'
             '<ViewPreference HorizontalMeasurementUnits="Pixels" VerticalMeasurementUnits="Pixels" RulerOrigin="PageOrigin"/>'
             '</idPkg:Preferences>')
    els, stories = [], []
    for n, it in enumerate(its, 1):
        g = geom(it['x'], it['y'], it['w'], it['h'])
        if it['kind'] == 'rect':
            st = f'StrokeColor="Color/{it["stroke"]}" StrokeWeight="2"' if it.get('stroke') else 'StrokeColor="Swatch/None" StrokeWeight="0"'
            els.append(f'<Rectangle Self="uR{n}" Name="{q(it["name"])}" ContentType="Unassigned" ItemLayer="uL" Locked="false" FillColor="{color_ref(it["fill"])}" {st}{corners(it.get("radius"))} ItemTransform="{T0}">{g}</Rectangle>')
        elif it['kind'] == 'image':
            pw, ph = it['px']
            els.append(f'<Rectangle Self="uR{n}" Name="{q(it["name"])}" ContentType="GraphicType" ItemLayer="uL" Locked="false" FillColor="Color/Card Black" StrokeColor="Swatch/None" StrokeWeight="0"{corners(R_CARD)} ItemTransform="{T0}">{g}'
                       f'<Image Self="uI{n}" ItemTransform="0.5 0 0 0.5 {it["x"]:.3f} {it["y"]:.3f}" Space="RGB" ActualPpi="144 144" EffectivePpi="144 144">'
                       f'<Properties><Profile type="string">$ID/Embedded</Profile><GraphicBounds Left="0" Top="0" Right="{pw}" Bottom="{ph}"/></Properties>'
                       f'<Link Self="uK{n}" LinkResourceURI="file:Links/{it["link"]}" LinkResourceFormat="$ID/JPEG" StoredState="Normal"/></Image></Rectangle>')
        else:
            sid = f'uS{n}'
            vj = {'top': 'TopAlign', 'center': 'CenterAlign'}[it['valign']]
            els.append(f'<TextFrame Self="uT{n}" Name="{q(it["name"])}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" ContentType="TextType" ItemLayer="uL" Locked="false" '
                       f'FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{T0}">{g}'
                       f'<TextFramePreference TextColumnCount="1" VerticalJustification="{vj}" AutoSizingType="Off" InsetSpacing="0 0 0 0"/></TextFrame>')
            rs = ''.join(f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{q(s)}"><CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">'
                         f'<Content>{q(t)}</Content>{"<Br/>" if i < len(it["paras"]) - 1 else ""}</CharacterStyleRange></ParagraphStyleRange>' for i, (s, t) in enumerate(it['paras']))
            stories.append((sid, HDR + f'<idPkg:Story {NS}><Story Self="{sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="{q(it["name"])}" AppliedNamedGrid="n">'
                            '<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>'
                            + rs + '</Story></idPkg:Story>'))
    spread = (HDR + f'<idPkg:Spread {NS}><Spread Self="uSp0" PageCount="1" BindingLocation="0" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" ShowMasterItems="true">'
              f'<Page Self="uP0" Name="1" AppliedMaster="n" GeometricBounds="0 0 {H} {W}" ItemTransform="{T0}" OverrideList="" TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true"/>'
              + ''.join(els) + '</Spread></idPkg:Spread>')
    design = (HDR + '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="8.0(370)" ?>\n'
              f'<Document {NS} Self="d" StoryList="{" ".join(s for s, _ in stories)}" ZeroPoint="0 0" ActiveLayer="uL">'
              '<idPkg:Graphic src="Resources/Graphic.xml"/><idPkg:Styles src="Resources/Styles.xml"/><idPkg:Preferences src="Resources/Preferences.xml"/>'
              '<Layer Self="uL" Name="Cards" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"><Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>'
              '<idPkg:Spread src="Spreads/Spread_uSp0.xml"/>'
              '<Section Self="uSec" Length="1" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageNumberStart="1" Marker="" PageStart="uP0" SectionPrefix=""/>'
              + ''.join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s, _ in stories) + '</Document>')
    container = (HDR + '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>')
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/vnd.adobe.indesign-idml-package', compress_type=zipfile.ZIP_STORED)
        put = lambda n, d: z.writestr(n, d.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)
        put('META-INF/container.xml', container); put('designmap.xml', design)
        put('Resources/Graphic.xml', graphic); put('Resources/Styles.xml', styles); put('Resources/Preferences.xml', prefs)
        put('Spreads/Spread_uSp0.xml', spread)
        for sid, x in stories:
            put(f'Stories/Story_{sid}.xml', x)


# ── JSX ──────────────────────────────────────────────────────────────────────────────
def build_jsx(its, path):
    js = lambda v: json.dumps(v, ensure_ascii=True)
    just = {'left': 'Justification.LEFT_ALIGN', 'center': 'Justification.CENTER_ALIGN'}
    L = ['// Four cards, 1920 x 1080 px. InDesign: File > Scripts > Scripts panel. Keep the Links folder next to this file.',
         '#target indesign', '(function () {', 'var here = File($.fileName).parent;',
         'app.scriptPreferences.measurementUnit = MeasurementUnits.PIXELS;',
         f'var doc = app.documents.add({{documentPreferences: {{pageWidth: {W}, pageHeight: {H}, facingPages: false, pagesPerDocument: 1, intent: DocumentIntentOptions.WEB_INTENT}}}});',
         'doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.PIXELS; doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.PIXELS;',
         'doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN; doc.zeroPoint = [0, 0];',
         'var pg = doc.pages[0];',
         'function color(n, v) { var c = doc.colors.itemByName(n); if (!c.isValid) c = doc.colors.add({name: n, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: v}); return c; }',
         'var C = {};']
    L += [f'C[{js(n)}] = color({js(n)}, {list(c)});' for n, c in COLORS.items()]
    L.append('function ps(n, size, lead, col, j, tr, tint) { var s = doc.paragraphStyles.add({name: n}); try { s.appliedFont = ' + js(FONT) + '; } catch (e) {}'
             ' s.pointSize = size; s.leading = lead; s.fillColor = C[col]; if (tint > 0) s.fillTint = tint; s.justification = j; s.hyphenation = false; s.tracking = tr; return s; }')
    L.append('var S = {};')
    L += [f'S[{js(n)}] = ps({js(n)}, {s["size"]}, {s["lead"]}, {js(s["color"])}, {just[s["align"]]}, {s.get("track", 0)}, {s.get("tint", -1)});' for n, s in STYLES.items()]
    L.append('function round(r, rad) { if (!rad) return; r.topLeftCornerOption = r.topRightCornerOption = r.bottomLeftCornerOption = r.bottomRightCornerOption = CornerOptions.ROUNDED_CORNER;'
             ' r.topLeftCornerRadius = r.topRightCornerRadius = r.bottomLeftCornerRadius = r.bottomRightCornerRadius = rad; }')
    for it in its:
        b = [round(it['y'], 3), round(it['x'], 3), round(it['y'] + it['h'], 3), round(it['x'] + it['w'], 3)]
        if it['kind'] == 'rect':
            fill = 'doc.swatches.itemByName("None")' if it['fill'].startswith('Swatch/') else f'C[{js(it["fill"])}]'
            stroke = f', strokeColor: C[{js(it["stroke"])}], strokeWeight: 2' if it.get('stroke') else ', strokeWeight: 0'
            L.append(f'var r = pg.rectangles.add({{geometricBounds: {b}, fillColor: {fill}{stroke}, name: {js(it["name"])}}}); round(r, {it.get("radius", 0)});')
        elif it['kind'] == 'image':
            L.append(f'var r = pg.rectangles.add({{geometricBounds: {b}, fillColor: C["Card Black"], strokeWeight: 0, name: {js(it["name"])}}}); round(r, {R_CARD});')
            L.append(f'var f = File(here + "/Links/{it["link"]}"); if (f.exists) {{ r.place(f); r.fit(FitOptions.FILL_PROPORTIONALLY); r.fit(FitOptions.CENTER_CONTENT); }}')
        else:
            L.append(f'var t = pg.textFrames.add({{geometricBounds: {b}, contents: {js(chr(13).join(p for _, p in it["paras"]))}, name: {js(it["name"])}}});')
            L.append('t.textFramePreferences.insetSpacing = [0, 0, 0, 0];' + (' t.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;' if it['valign'] == 'center' else ''))
            L += [f't.paragraphs[{i}].appliedParagraphStyle = S[{js(s)}];' for i, (s, _) in enumerate(it['paras'])]
    L.append('})();')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


# ── preview (same coordinates, HTML) ─────────────────────────────────────────────────
def build_preview(its, base):
    from pathlib import Path
    css = {n: f'font-size:{s["size"]}px;line-height:{s["lead"]}px;color:rgb{COLORS[s["color"]]};opacity:{s.get("tint", 100) / 100};text-align:{s["align"]};letter-spacing:{s.get("track", 0) / 1000}em' for n, s in STYLES.items()}
    el = []
    for it in its:
        box = f'left:{it["x"]}px;top:{it["y"]}px;width:{it["w"]}px;height:{it["h"]}px'
        if it['kind'] == 'rect':
            bg = 'transparent' if it['fill'].startswith('Swatch/') else f'rgb{COLORS[it["fill"]]}'
            bd = f'border:2px solid #fff;box-sizing:border-box;' if it.get('stroke') else ''
            el.append(f'<div style="{box};background:{bg};{bd}border-radius:{it.get("radius", 0)}px"></div>')
        elif it['kind'] == 'image':
            el.append(f'<div style="{box};border-radius:{R_CARD}px;background:url({Path(LINKS, it["link"]).as_uri()}) 0 0/100% 100%"></div>')
        else:
            vj = 'display:flex;flex-direction:column;justify-content:center;' if it['valign'] == 'center' else ''
            el.append(f'<div style="{box};{vj}">' + ''.join(f'<div style="{css[s]}">{html.escape(t)}</div>' for s, t in it['paras']) + '</div>')
    page = ('<!doctype html><html><head><meta charset="utf-8"><style>@page{size:1920px 1080px;margin:0}html,body{margin:0;width:1920px;height:1080px;overflow:hidden}'
            "div{position:absolute;font-family:'Liberation Sans',Arial,sans-serif}div div{position:static}</style></head><body>" + ''.join(el) + '</body></html>')
    h = base + '.html'
    with open(h, 'w', encoding='utf-8') as f:
        f.write(page)
    return h


def main():
    os.makedirs(OUT, exist_ok=True)
    its = items(); make_links(its)
    build_idml(its, os.path.join(OUT, 'cards_1920x1080.idml'))
    build_jsx(its, os.path.join(OUT, 'cards_1920x1080.jsx'))
    tmp = os.path.join(REPO, 'out/web_cards'); os.makedirs(tmp, exist_ok=True)
    h = build_preview(its, os.path.join(tmp, 'cards_1920x1080'))
    subprocess.run(['node', os.path.join(os.path.dirname(__file__), 'preview.mjs'), h, os.path.join(OUT, 'cards_1920x1080')], check=True)
    z = os.path.join(REPO, 'docs/web_cards/cards_1920x1080_indesign.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zz:
        for f in ('cards_1920x1080.idml', 'cards_1920x1080.jsx', 'cards_1920x1080.pdf', 'cards_1920x1080.jpg'):
            zz.write(os.path.join(OUT, f), 'cards_1920x1080/' + f)
        for f in sorted(os.listdir(LINKS)):
            zz.write(os.path.join(LINKS, f), 'cards_1920x1080/Links/' + f)
    print('산출물: docs/web_cards/indesign/ · docs/web_cards/cards_1920x1080_indesign.zip')


if __name__ == '__main__':
    main()
