"""P1 표지 + 1쪽(이야기 단락) — 한 벌의 레이아웃 데이터에서 세 가지를 만든다.

  python3 tools/p1_layout/cover_p1.py

  docs/shinsegae_vmd/p1_layout/cover_p1.pdf    시안 PDF (Chromium 으로 인쇄)
  docs/shinsegae_vmd/p1_layout/cover_p1.idml   InDesign 문서 (파일 > 열기 → .indd 로 저장)
  docs/shinsegae_vmd/p1_layout/cover_p1.jsx    같은 문서를 InDesign 안에서 짓는 스크립트 (IDML 이 열리지 않을 때)
  docs/shinsegae_vmd/p1_layout/Links/cover.jpg 표지 이미지 (사용자 제공)

문법: ETÉREO — 표지는 OPEN(전면 사진 + 흰 세리프 제목), 1쪽은 TITLE-a(R1 Women of the mountain:
위에 리드 문단, 가운데 오른쪽에 작은 캡션, 아래에 대형 세리프 제목, 오른쪽 면에 여백 안 사진). 단위 mm, A4 가로.
"""
import html
import json
import os
import shutil
import subprocess
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
OUT = os.path.join(REPO, 'docs/shinsegae_vmd/p1_layout')
TMP = os.path.join(REPO, 'out/p1_layout')
IMG_SRC = os.environ.get('COVER_IMAGE', os.path.join(OUT, 'Links/cover.jpg'))
IMG_PX = (1296, 912)  # 72 ppi -> 1 px = 1 pt 로 InDesign 이 읽는다

W, H, BLEED = 297.0, 210.0, 3.0
MM = 72 / 25.4

# ── 글 (p1_text.md 편집본. 4 · 5번째 줄은 판면 폭에 맞춰 문장 경계에서 나눴다) ─────────────
LEAD_KO = [
    '사람들은 쇼윈도를 밖에서 본다. 나는 안에서 본다.',
    '안에서 보면 가게 이름은 거꾸로 읽히고, 진열은 등을 보인다.',
    '대신 유리 너머로 사람들의 얼굴이 보인다.',
    '대부분은 그냥 지나간다.',
    '가끔 누군가 걸음을 멈추고, 들여다보고, 웃는다.',
    '나는 그 사람이 무엇을 보고 웃었는지 본다.',
    '진열의 답은 상품이 아니라 그 표정에 있기 때문이다.',
    '그래서 나는 안에서 밖을 보는 VMD가 되려 한다.',
]
CAP_EN = ('People look at a shop window from outside. I look from inside. From inside, the shop’s name reads '
          'backwards and the display shows its back. Instead, I see faces through the glass. Most people walk past. '
          'Now and then someone stops, looks in, and smiles. I watch what made them smile. The answer to a display '
          'is in that face, not in the product. So I want to be a VMD who looks out from the inside.')

# ── 문단 스타일: InDesign 글꼴(최종) / PDF 시안 글꼴 ─────────────────────────────────
#   EB Garamond = ETÉREO 의 Garamond Premier Pro 자리, Pretendard = Acumin 자리(한글 포함).
STYLES = {
    'Header Bold':   dict(font='Pretendard', style='Bold', size=9.5, lead=12, color='Ink', align='left'),
    'Header':        dict(font='Pretendard', style='Regular', size=9.5, lead=12, color='Ink', align='left'),
    'Header Right':  dict(font='Pretendard', style='Regular', size=9.5, lead=12, color='Ink', align='right'),
    'Header Bold Right': dict(font='Pretendard', style='Bold', size=9.5, lead=12, color='Ink', align='right'),
    'Cover Title':   dict(font='EB Garamond', style='Regular', size=56, lead=52, color='White', align='left'),
    'Cover Name':    dict(font='Pretendard', style='Regular', size=8.5, lead=11, color='White', align='left'),
    'Lead KO':       dict(font='Pretendard', style='Regular', size=9.5, lead=16.5, color='Ink', align='left'),
    'Caption EN':    dict(font='Pretendard', style='Regular', size=6.6, lead=9, color='Ink', align='justify'),
    'Title':         dict(font='EB Garamond', style='Regular', size=78, lead=70, color='Ink', align='left'),
    'Folio':         dict(font='EB Garamond', style='Italic', size=7, lead=8, color='Ink', align='left'),
}
COLORS = {'Ink': (27, 26, 24), 'Stock': (230, 225, 218), 'White': (255, 255, 255)}

I, B, R = {'FontStyle': 'Italic'}, {'FontStyle': 'Bold'}, {'FontStyle': 'Regular'}


def para(style, *runs):
    return (style, [r if isinstance(r, tuple) else (r, {}) for r in runs])


def text(page, x, y, w, h, paras, valign='top', rotate=0, name=''):
    return dict(page=page, kind='text', x=x, y=y, w=w, h=h, paras=paras, valign=valign, rotate=rotate, name=name)


# ── 지면 ─────────────────────────────────────────────────────────────────────────────
ITEMS = [
    # 표지 · OPEN: 전면 사진(재단 여유 3mm), 어두운 마네킹 위에 흰 제목
    dict(page=0, kind='image', x=-BLEED, y=-BLEED, w=W + 2 * BLEED, h=H + 2 * BLEED, fit='center', name='cover image'),
    text(0, 12, 116, 140, 74, [para('Cover Title', 'From ', ('the', I)), para('Cover Title', 'inside')], valign='bottom', name='cover title'),
    text(0, 12, 193, 70, 10, [para('Cover Name', ('JEONG HYEOKJU', B)), para('Cover Name', 'Visual Merchandiser Portfolio · 2026')], name='cover name'),

    # 1쪽 · TITLE-a
    dict(page=1, kind='rect', x=-BLEED, y=-BLEED, w=W + 2 * BLEED, h=H + 2 * BLEED, fill='Stock', name='paper'),
    text(1, 10, 7, 80, 6, [para('Header Bold', 'FROM THE INSIDE')], name='header L1'),
    text(1, 90.5, 7, 50, 6, [para('Header Right', 'PROLOGUE')], name='header L2'),
    text(1, 156.5, 7, 60, 6, [para('Header Bold', '2026')], name='header R1'),
    text(1, 217, 7, 70, 6, [para('Header Bold Right', 'JEONG HYEOKJU')], name='header R2'),
    text(1, 10, 24, 128, 50, [para('Lead KO', line) for line in LEAD_KO], name='lead ko'),
    text(1, 78, 82, 62.5, 36, [para('Caption EN', ('From the inside — ', B), CAP_EN)], name='caption en'),
    text(1, 10, 118, 130, 80, [para('Title', 'Inside,'), para('Title', ('looking', I)), para('Title', 'out')], valign='bottom', name='title'),
    dict(page=1, kind='image', x=156.5, y=24, w=130.5, h=168, fit='left', name='photo (cover detail)'),
    # 쪽 번호 — ETÉREO 처럼 바깥 여백에 세로로: 왼쪽은 아래에서 위로, 오른쪽은 위에서 아래로
    text(1, 5.2, 112, 20, 3.4, [para('Folio', 'page  ', ('1', R))], rotate=-90, name='folio L'),
    text(1, 291.8, 98, 20, 3.4, [para('Folio', 'page  ', ('1', R))], rotate=90, name='folio R'),
]


def image_box(it):
    """그림 틀 안에서 그림의 위치 · 크기(mm): 틀을 가득 채우고, center 는 가운데 · left 는 왼쪽에 맞춘다."""
    s = max(it['w'] / IMG_PX[0], it['h'] / IMG_PX[1])
    iw, ih = IMG_PX[0] * s, IMG_PX[1] * s
    if it.get('crop'):  # (cx, cy): 원본에서 틀 가운데에 올 점(0–1), 틀 밖으로 비지 않게 막는다
        cx, cy = it['crop']
        ox = it['x'] + min(0, max(it['w'] - iw, it['w'] / 2 - cx * iw))
        oy = it['y'] + min(0, max(it['h'] - ih, it['h'] / 2 - cy * ih))
        return ox, oy, iw, ih, s
    ox = it['x'] + ((it['w'] - iw) / 2 if it['fit'] == 'center' else 0)
    oy = it['y'] + (it['h'] - ih) / 2
    return ox, oy, iw, ih, s


# ── HTML → PDF ───────────────────────────────────────────────────────────────────────
def build_html():
    fonts = os.path.join(HERE, 'fonts')
    face = lambda fam, f, extra='': f"@font-face{{font-family:{fam};{extra}src:url('file://{fonts}/{f}')}}"
    css = [face('Crimson', 'CrimsonPro-Regular.ttf'), face('Crimson', 'CrimsonPro-Italic.ttf', 'font-style:italic;'),
           face('Inst', 'InstrumentSans-Regular.ttf'), face('Inst', 'InstrumentSans-Bold.ttf', 'font-weight:700;'),
           '@page{size:297mm 210mm;margin:0}*{box-sizing:border-box;margin:0;padding:0}html,body{background:#777}',
           'body{-webkit-print-color-adjust:exact;print-color-adjust:exact}',
           '.sheet{position:relative;width:297mm;height:210mm;overflow:hidden;page-break-after:always;background:#000}',
           '.sheet>div{position:absolute}.tf{display:flex;flex-direction:column}.tf.bottom{justify-content:flex-end}',
           '.im{overflow:hidden}.im img{position:absolute;display:block}p{white-space:nowrap}p.wrap{white-space:normal}']
    fam = {'EB Garamond': "Crimson,'WenQuanYi Zen Hei',serif", 'Pretendard': "Inst,'WenQuanYi Zen Hei',sans-serif"}
    for n, s in STYLES.items():
        r, g, b = COLORS[s['color']]
        al = {'left': 'left', 'right': 'right', 'justify': 'justify'}[s['align']]
        css.append(f".s-{n.replace(' ', '_')}{{font-family:{fam[s['font']]};font-size:{s['size']}pt;line-height:{s['lead']}pt;"
                   f"color:rgb({r},{g},{b});text-align:{al};font-style:{'italic' if s['style'] == 'Italic' else 'normal'};"
                   f"font-weight:{700 if s['style'] == 'Bold' else 400}}}")
    img = 'file://' + IMG_SRC
    pages = [[], []]
    for it in ITEMS:
        if it['kind'] == 'rect':
            r, g, b = COLORS[it['fill']]
            pages[it['page']].append(f"<div style='left:{it['x']}mm;top:{it['y']}mm;width:{it['w']}mm;height:{it['h']}mm;background:rgb({r},{g},{b})'></div>")
        elif it['kind'] == 'image':
            ox, oy, iw, ih, _ = image_box(it)
            pages[it['page']].append(f"<div class=im style='left:{it['x']}mm;top:{it['y']}mm;width:{it['w']}mm;height:{it['h']}mm'>"
                                     f"<img src='{img}' style='left:{ox - it['x']}mm;top:{oy - it['y']}mm;width:{iw}mm;height:{ih}mm'></div>")
        else:
            ps = []
            for st, runs in it['paras']:
                inner = ''.join(f"<span style='{run_css(o)}'>{html.escape(t)}</span>" for t, o in runs)
                ps.append(f"<p class='s-{st.replace(' ', '_')}{' wrap' if st == 'Caption EN' else ''}'>{inner}</p>")
            rot = f"transform:rotate({it['rotate']}deg);transform-origin:0 0;" if it['rotate'] else ''
            pages[it['page']].append(f"<div class='tf {it['valign']}' style='left:{it['x']}mm;top:{it['y']}mm;width:{it['w']}mm;height:{it['h']}mm;{rot}'>{''.join(ps)}</div>")
    body = ''.join(f"<div class=sheet>{''.join(p)}</div>" for p in pages)
    return f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>P1 cover + page 1</title><style>{''.join(css)}</style></head><body>{body}</body></html>"


def run_css(o):
    fs = o.get('FontStyle')
    return {'Italic': 'font-style:italic', 'Bold': 'font-weight:700', 'Regular': 'font-style:normal;font-weight:400'}.get(fs, '')


# ── IDML ─────────────────────────────────────────────────────────────────────────────
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="8.0"'
HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
WP, HP = W * MM, H * MM
SPREAD_T = f'1 0 0 1 {-WP / 2:.4f} {-HP / 2:.4f}'
q = lambda s: html.escape(s, quote=True)


def path_geom(x, y, w, h):
    x1, y1, x2, y2 = x * MM, y * MM, (x + w) * MM, (y + h) * MM
    pts = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]
    pp = ''.join(f'<PathPointType Anchor="{a:.4f} {b:.4f}" LeftDirection="{a:.4f} {b:.4f}" RightDirection="{a:.4f} {b:.4f}"/>' for a, b in pts)
    return f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pp}</PathPointArray></GeometryPathType></PathGeometry></Properties>'


def idml_color(name, rgb):
    return (f'<Color Self="Color/{name}" Model="Process" Space="RGB" ColorValue="{rgb[0]} {rgb[1]} {rgb[2]}" ColorOverride="Normal" '
            f'AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="{name}" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>')


def build_idml(path_out):
    graphic = (HDR + f'<idPkg:Graphic {NS}>'
               '<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               + ''.join(idml_color(n, c) for n, c in COLORS.items()) +
               '<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/>'
               '</idPkg:Graphic>')
    just = {'left': 'LeftAlign', 'right': 'RightAlign', 'justify': 'LeftJustified'}
    pstyles = ''.join(
        f'<ParagraphStyle Self="ParagraphStyle/{q(n)}" Name="{q(n)}" Imported="false" NextStyle="ParagraphStyle/{q(n)}" KeyboardShortcut="0 0" '
        f'FontStyle="{s["style"]}" PointSize="{s["size"]}" FillColor="Color/{s["color"]}" Justification="{just[s["align"]]}" Hyphenation="false" Tracking="{s.get('track', 0)}">'
        f'<Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn><PreviewColor type="enumeration">Nothing</PreviewColor>'
        f'<AppliedFont type="string">{s["font"]}</AppliedFont><Leading type="unit">{s["lead"]}</Leading></Properties></ParagraphStyle>'
        for n, s in STYLES.items())
    styles = (HDR + f'<idPkg:Styles {NS}>'
              '<RootCharacterStyleGroup Self="u79"><CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" Name="$ID/[No character style]"/></RootCharacterStyleGroup>'
              '<RootParagraphStyleGroup Self="u78"><ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false"/>'
              '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>'
              + pstyles + '</RootParagraphStyleGroup>'
              '<RootCellStyleGroup Self="u8e"><CellStyle Self="CellStyle/$ID/[None]" Name="$ID/[None]"/></RootCellStyleGroup>'
              '<RootTableStyleGroup Self="u90"><TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/><TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"/></RootTableStyleGroup>'
              '<RootObjectStyleGroup Self="u97"><ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/></RootObjectStyleGroup>'
              '</idPkg:Styles>')
    b = BLEED * MM
    prefs = (HDR + f'<idPkg:Preferences {NS}>'
             f'<DocumentPreference PageHeight="{HP:.4f}" PageWidth="{WP:.4f}" PagesPerDocument="2" FacingPages="false" '
             f'DocumentBleedTopOffset="{b:.4f}" DocumentBleedBottomOffset="{b:.4f}" DocumentBleedInsideOrLeftOffset="{b:.4f}" DocumentBleedOutsideOrRightOffset="{b:.4f}" '
             'DocumentBleedUniformSize="true" PageBinding="LeftToRight" AllowPageShuffle="true" Intent="PrintIntent"/>'
             f'<MarginPreference ColumnCount="1" ColumnGutter="{8 * MM:.4f}" Top="{22 * MM:.4f}" Bottom="{12 * MM:.4f}" Left="{10 * MM:.4f}" Right="{10 * MM:.4f}" ColumnDirection="Horizontal"/>'
             '<ViewPreference HorizontalMeasurementUnits="Millimeters" VerticalMeasurementUnits="Millimeters" RulerOrigin="PageOrigin"/>'
             '</idPkg:Preferences>')

    spreads, stories = [[], []], []
    n = 0
    for it in ITEMS:
        n += 1
        pg = it['page']
        if it['kind'] == 'rect':
            spreads[pg].append(f'<Rectangle Self="uR{n}" Name="{q(it["name"])}" ContentType="Unassigned" ItemLayer="uL" Locked="false" FillColor="Color/{it["fill"]}" '
                               f'StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{SPREAD_T}">{path_geom(it["x"], it["y"], it["w"], it["h"])}</Rectangle>')
        elif it['kind'] == 'image':
            ox, oy, iw, ih, s = image_box(it)
            k = s * MM  # pt per px
            spreads[pg].append(
                f'<Rectangle Self="uR{n}" Name="{q(it["name"])}" ContentType="GraphicType" ItemLayer="uL" Locked="false" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{SPREAD_T}">'
                f'{path_geom(it["x"], it["y"], it["w"], it["h"])}'
                f'<Image Self="uI{n}" ItemTransform="{k:.6f} 0 0 {k:.6f} {ox * MM:.4f} {oy * MM:.4f}" Space="RGB" ActualPpi="72 72">'
                f'<Properties><Profile type="string">$ID/Embedded</Profile><GraphicBounds Left="0" Top="0" Right="{IMG_PX[0]}" Bottom="{IMG_PX[1]}"/></Properties>'
                f'<Link Self="uK{n}" LinkResourceURI="file:Links/cover.jpg" LinkResourceFormat="$ID/JPEG" StoredState="Normal"/></Image></Rectangle>')
        else:
            sid = f'uS{n}'
            if it['rotate']:
                a, bb, c, d = (0, 1, -1, 0) if it['rotate'] == 90 else (0, -1, 1, 0)
                tr = f'{a} {bb} {c} {d} {it["x"] * MM - WP / 2:.4f} {it["y"] * MM - HP / 2:.4f}'
                geom = path_geom(0, 0, it['w'], it['h'])
            else:
                tr, geom = SPREAD_T, path_geom(it['x'], it['y'], it['w'], it['h'])
            vj = 'BottomAlign' if it['valign'] == 'bottom' else 'TopAlign'
            spreads[pg].append(
                f'<TextFrame Self="uT{n}" Name="{q(it["name"])}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" ContentType="TextType" ItemLayer="uL" Locked="false" '
                f'FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{tr}">{geom}'
                f'<TextFramePreference TextColumnCount="1" VerticalJustification="{vj}" AutoSizingType="Off"/></TextFrame>')
            ranges = []
            for i, (st, runs) in enumerate(it['paras']):
                crs = []
                for j, (t, o) in enumerate(runs):
                    attrs = ''.join(f' {k2}="{v}"' for k2, v in o.items())
                    br = '<Br/>' if (j == len(runs) - 1 and i < len(it['paras']) - 1) else ''
                    crs.append(f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"{attrs}><Content>{q(t)}</Content>{br}</CharacterStyleRange>')
                ranges.append(f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{q(st)}">{"".join(crs)}</ParagraphStyleRange>')
            stories.append((sid, HDR + f'<idPkg:Story {NS}><Story Self="{sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="{q(it["name"])}" AppliedNamedGrid="n">'
                                  '<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>'
                            + ''.join(ranges) + '</Story></idPkg:Story>'))

    spread_xml = []
    for i, items in enumerate(spreads):
        spread_xml.append(HDR + f'<idPkg:Spread {NS}><Spread Self="uSp{i}" PageCount="1" BindingLocation="0" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 {i * (HP + 30):.4f}" ShowMasterItems="true">'
                          + f'<Page Self="uP{i}" Name="{"C" if i == 0 else "1"}" AppliedMaster="n" GeometricBounds="0 0 {HP:.4f} {WP:.4f}" ItemTransform="{SPREAD_T}" OverrideList="" TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true"/>'
                          + ''.join(items) + '</Spread></idPkg:Spread>')

    design = (HDR + '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="8.0(370)" ?>\n'
              f'<Document {NS} Self="d" StoryList="{" ".join(s for s, _ in stories)}" ZeroPoint="0 0" ActiveLayer="uL">'
              '<idPkg:Graphic src="Resources/Graphic.xml"/><idPkg:Styles src="Resources/Styles.xml"/><idPkg:Preferences src="Resources/Preferences.xml"/>'
              '<Layer Self="uL" Name="Layer 1" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"><Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>'
              + ''.join(f'<idPkg:Spread src="Spreads/Spread_uSp{i}.xml"/>' for i in range(2))
              + '<Section Self="uSec" Length="2" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageNumberStart="1" Marker="" PageStart="uP0" SectionPrefix=""/>'
              + ''.join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s, _ in stories)
              + '</Document>')
    container = (HDR + '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                 '<rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>')

    with zipfile.ZipFile(path_out, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/vnd.adobe.indesign-idml-package', compress_type=zipfile.ZIP_STORED)
        put = lambda name, data: z.writestr(name, data.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)
        put('META-INF/container.xml', container)
        put('designmap.xml', design)
        put('Resources/Graphic.xml', graphic)
        put('Resources/Styles.xml', styles)
        put('Resources/Preferences.xml', prefs)
        for i, x in enumerate(spread_xml):
            put(f'Spreads/Spread_uSp{i}.xml', x)
        for sid, x in stories:
            put(f'Stories/Story_{sid}.xml', x)
    return [design, graphic, styles, prefs, *spread_xml, *[x for _, x in stories]]


# ── JSX (InDesign 안에서 같은 문서를 짓는다) ───────────────────────────────────────────
def build_jsx(path_out):
    js = lambda v: json.dumps(v, ensure_ascii=True)
    just = {'left': 'Justification.LEFT_ALIGN', 'right': 'Justification.RIGHT_ALIGN', 'justify': 'Justification.LEFT_JUSTIFIED'}
    L = ['// P1 표지 + 1쪽 — InDesign: 파일 > 스크립트 > 스크립트 패널에서 실행하거나, 이 파일을 스크립트 패널 폴더에 두고 두 번 클릭.',
         '// Links/cover.jpg 가 이 파일 옆에 있어야 한다. 생성: tools/p1_layout/cover_p1.py',
         '#target indesign', '(function () {',
         'var here = File($.fileName).parent;',
         'app.scriptPreferences.measurementUnit = MeasurementUnits.MILLIMETERS;',
         f'var doc = app.documents.add({{documentPreferences: {{pageWidth: {W}, pageHeight: {H}, facingPages: false, pagesPerDocument: 2, documentBleedUniformSize: true, documentBleedTopOffset: {BLEED}}}}});',
         'doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS;',
         'doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;',
         'doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN; doc.zeroPoint = [0, 0];',
         'function color(n, v) { var c = doc.colors.itemByName(n); if (!c.isValid) c = doc.colors.add({name: n, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: v}); return c; }',
         'var C = {};']
    for n, c in COLORS.items():
        L.append(f'C[{js(n)}] = color({js(n)}, {list(c)});')
    L.append('function pstyle(n, f, fs, size, lead, col, j, tr) { var s = doc.paragraphStyles.itemByName(n); if (!s.isValid) s = doc.paragraphStyles.add({name: n});'
             ' try { s.appliedFont = f; } catch (e) {} try { s.fontStyle = fs; } catch (e) {}'
             ' s.pointSize = size; s.leading = lead; s.fillColor = C[col]; s.justification = j; s.hyphenation = false; s.tracking = tr; return s; }')
    L.append('var S = {};')
    for n, s in STYLES.items():
        L.append(f'S[{js(n)}] = pstyle({js(n)}, {js(s["font"])}, {js(s["style"])}, {s["size"]}, {s["lead"]}, {js(s["color"])}, {just[s["align"]]}, {s.get('track', 0)});')
    L.append("var img = File(here + '/Links/cover.jpg');")
    for it in ITEMS:
        pg = f'doc.pages[{it["page"]}]'
        x1, y1, x2, y2 = it['x'], it['y'], it['x'] + it['w'], it['y'] + it['h']
        if it['kind'] == 'rect':
            L.append(f'var r = {pg}.rectangles.add({{geometricBounds: [{y1}, {x1}, {y2}, {x2}], fillColor: C[{js(it["fill"])}], strokeWeight: 0, name: {js(it["name"])}}}); r.sendToBack();')
        elif it['kind'] == 'image':
            ox, oy, iw, ih, _ = image_box(it)
            L.append(f'var r = {pg}.rectangles.add({{geometricBounds: [{y1}, {x1}, {y2}, {x2}], strokeWeight: 0, name: {js(it["name"])}}});')
            L.append(f'if (img.exists) {{ r.place(img); r.graphics[0].geometricBounds = [{oy:.4f}, {ox:.4f}, {oy + ih:.4f}, {ox + iw:.4f}]; }} else alert("Links/cover.jpg \\uC5C6\\uC74C");')
            if it.get('fade'):  # 왼쪽이 투명, 폭의 fade 비율부터 불투명 — 그레이디언트 페더
                L.append('var g = r.transparencySettings.gradientFeatherSettings; g.applied = true; g.type = GradientType.LINEAR; g.angle = 180;'
                         f' g.opacityGradientStops[0].location = {round((1 - it["fade"]) * 100)}; g.opacityGradientStops[0].opacity = 100;'
                         ' g.opacityGradientStops[1].location = 100; g.opacityGradientStops[1].opacity = 0;')
        else:
            content = '\r'.join(''.join(t for t, _ in runs) for _, runs in it['paras'])
            if it['rotate']:
                cx = it['x'] - it['h'] / 2 if it['rotate'] == 90 else it['x'] + it['h'] / 2
                cy = it['y'] + it['w'] / 2 if it['rotate'] == 90 else it['y'] - it['w'] / 2
                bx = [cy - it['h'] / 2, cx - it['w'] / 2, cy + it['h'] / 2, cx + it['w'] / 2]
            else:
                bx = [y1, x1, y2, x2]
            L.append(f'var t = {pg}.textFrames.add({{geometricBounds: {[round(v, 4) for v in bx]}, contents: {js(content)}, name: {js(it["name"])}}});')
            L.append('t.textFramePreferences.insetSpacing = [0, 0, 0, 0];')
            if it['valign'] == 'bottom':
                L.append('t.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;')
            pos = 0
            for i, (st, runs) in enumerate(it['paras']):
                L.append(f't.paragraphs[{i}].appliedParagraphStyle = S[{js(st)}];')
            for i, (st, runs) in enumerate(it['paras']):
                for t, o in runs:
                    if o.get('FontStyle'):
                        L.append(f'try {{ t.parentStory.characters.itemByRange({pos}, {pos + len(t) - 1}).fontStyle = {js(o["FontStyle"])}; }} catch (e) {{}}')
                    pos += len(t)
                pos += 1  # 문단 끝
            if it['rotate']:
                L.append(f't.transform(CoordinateSpaces.PASTEBOARD_COORDINATES, AnchorPoint.CENTER_ANCHOR, app.transformationMatrices.add({{counterclockwiseRotationAngle: {-it["rotate"]}}}));')
    L += ['})();']
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


def main():
    os.makedirs(os.path.join(OUT, 'Links'), exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    dst = os.path.join(OUT, 'Links/cover.jpg')
    if os.path.abspath(IMG_SRC) != dst:
        shutil.copyfile(IMG_SRC, dst)
    globals()['IMG_SRC'] = dst
    h = os.path.join(TMP, 'cover_p1.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(build_html())
    xmls = build_idml(os.path.join(OUT, 'cover_p1.idml'))
    build_jsx(os.path.join(OUT, 'cover_p1.jsx'))
    subprocess.run(['node', os.path.join(HERE, 'print_pdf.mjs'), h, os.path.join(OUT, 'cover_p1.pdf'), os.path.join(TMP, 'cover_p1')], check=True)
    return xmls


if __name__ == '__main__':
    main()
