"""JAJU 포트폴리오 3쪽(Prologue, 표지부터 센 번호) — InDesign 파일.

  python3 tools/jaju_layout/indd_p03.py

  docs/jaju_rounding_vmd/indesign/p03_prologue/
    p03_prologue.idml     InDesign 문서 (파일 > 열기 → .indd 로 저장)
    p03_prologue.jsx      같은 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 열리지 않을 때)
    p03_prologue.pdf      기준 시안 — plan_b17.pdf 의 3쪽
    Document Fonts/       Young Serif · Lora · IBM Plex Mono (OFL). Pretendard 는 따로 설치
  docs/jaju_rounding_vmd/indesign/p03_prologue.zip   위 폴더 그대로

값은 plan_b17 의 3쪽(HTML · mm)과 같다. 글자는 시안의 글꼴을 최종 글꼴로 옮긴다:
  WenQuanYi Zen Hei(한글, 이 환경의 대체 글꼴) → Pretendard, Young Serif · Lora · IBM Plex Mono 는 그대로.
반투명(유령 글자 22% · 기준선 16% · 십자 55%)은 바탕 #15120F 위에 섞은 단색으로 — InDesign 에서 투명도 없이 같은 색.
HTML 은 줄 높이의 위아래 반을 글 위에 두므로, 틀을 (행간 − 글자 크기) / 2 만큼 내리고 첫 기준선을 '어센트'로 둔다.
"""
import html
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
NAME = 'p03_prologue'
DIR = os.path.join(REPO, 'docs/jaju_rounding_vmd/indesign', NAME)
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
W, H, BLEED = 297.0, 210.0, 3.0
MM = 72 / 25.4
PT = 25.4 / 72

import plan_c as pc  # noqa: E402

BG = (21, 18, 15)


def mix(c, a):
    return tuple(round(b + a * (x - b)) for x, b in zip(c, BG))


CREAM, MUTE, ORANGE = (239, 231, 218), (154, 143, 130), (217, 119, 58)
COLORS = {'Night': BG, 'Cream': CREAM, 'Mute': MUTE, 'Orange': ORANGE,
          'Ghost': mix(CREAM, .22), 'Rule': mix(CREAM, .16), 'Cross': mix(CREAM, .55)}

P, YS, LO, MO = 'Pretendard', 'Young Serif', 'Lora', 'IBM Plex Mono'
STYLES = {  # 글꼴, 굵기, 크기, 행간(pt), 색, 정렬, 자간, (외곽선 색, 굵기)
    'Ghost':       dict(font=YS, style='Regular', size=96, lead=96, color='Swatch/None', align='left', stroke=('Ghost', .35)),
    'Title':       dict(font=YS, style='Regular', size=32, lead=34, color='Cream', align='left'),
    'Pull KO':     dict(font=P, style='Bold', size=30, lead=40, color='Cream', align='left'),
    'Body KO':     dict(font=P, style='Regular', size=10, lead=17, color='Cream', align='left'),
    'Body KO Bold': dict(font=P, style='Bold', size=10.5, lead=17, color='Cream', align='left'),
    'Body EN':     dict(font=LO, style='Italic', size=8.6, lead=13, color='Mute', align='left'),
    'Part Num':    dict(font=LO, style='Italic', size=10, lead=12.8, color='Orange', align='left'),
    'Part Word':   dict(font=YS, style='Regular', size=15, lead=19, color='Cream', align='left'),
    'Part Key':    dict(font=P, style='Regular', size=7, lead=9.5, color='Mute', align='left'),
    'Folio':       dict(font=MO, style='Regular', size=6, lead=8, color='Mute', align='left', track=100),
    'Folio Center': dict(font=MO, style='Regular', size=6, lead=8, color='Mute', align='center', track=100),
    'Folio Right': dict(font=MO, style='Regular', size=6, lead=8, color='Mute', align='right', track=100),
}

KO = pc.LEAD_KO
EN = pc.LEAD_EN


def T(x, y, w, h, paras, name):
    """paras = [(style, text)], y 는 HTML 의 틀 위치 — 첫 문단 스타일의 반 행간만큼 내린다."""
    s = STYLES[paras[0][0]]
    return dict(kind='text', x=x, y=y + (s['lead'] - s['size']) / 2 * PT, w=w, h=h, paras=paras, name=name)


def L(x1, y1, x2, y2, color, wmm, name):
    return dict(kind='line', x1=x1, y1=y1, x2=x2, y2=y2, color=color, weight=wmm * MM, name=name)


def cross(x, y, r, name):
    return [L(x - r, y, x + r, y, 'Cross', .2, name + ' h'), L(x, y - r, x, y + r, 'Cross', .2, name + ' v')]


ITEMS = [dict(kind='rect', x=-BLEED, y=-BLEED, w=W + 2 * BLEED, h=H + 2 * BLEED, fill='Night', name='background')]
# 격자: 위 · 아래 기준선 + 십자 여섯
ITEMS += [L(14, 12, 283, 12, 'Rule', .15, 'rule top'), L(14, 195, 283, 195, 'Rule', .15, 'rule bottom')]
for x in (14, 148.5, 283):
    for y in (12, 195):
        ITEMS += cross(x, y, 1.8, f'cross {x:g},{y:g}')
# 세 파트 줄 위의 선 + 십자 넷
ITEMS.append(L(14, 157, 148, 157, 'Rule', .15, 'parts rule'))
for i in range(4):
    ITEMS += cross(14 + i * 46, 157, 1.6, f'parts cross {i + 1}')
ITEMS += [
    T(10, 12, 280, 40, [('Ghost', 'Prologue')], 'ghost word'),
    T(14, 32, 120, 14, [('Title', 'Prologue.')], 'title'),
    T(14, 62, 140, 60, [('Pull KO', s) for s in ('밖에서 보면', '상품이 보이고,', '안에서 보면', '사람이 보인다.')], 'pull'),
    T(162, 62, 122, 62, [('Body KO', s) for s in KO[:-1]], 'body ko'),
    T(162, 126, 122, 8, [('Body KO Bold', KO[-1])], 'body ko last'),
    T(162, 146, 112, 40, [('Body EN', EN)], 'body en'),
]
for i, (n, w, k, p) in enumerate([('/01', 'Observe.', '관찰하다 — 사진', '04'), ('/02', 'Contain.', '담다 — 건축', '08'),
                                  ('/03', 'Fill.', '채우다 — 패션', '11')]):
    ITEMS.append(T(14 + i * 46, 160, 42, 26, [('Part Num', n), ('Part Word', w), ('Part Key', f'{k}  ·  p.{p}')], f'part {n}'))
ITEMS += [T(14, 199, 160, 4, [('Folio', 'FROM THE INSIDE')], 'folio left'),
          T(98.5, 199, 100, 4, [('Folio Center', 'PROLOGUE')], 'folio center'),
          T(243, 199, 40, 4, [('Folio Right', '03')], 'folio number')]


# ── IDML ─────────────────────────────────────────────────────────────────────────────
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="8.0"'
HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
WP, HP = W * MM, H * MM
SPREAD_T = f'1 0 0 1 {-WP / 2:.4f} {-HP / 2:.4f}'
q = lambda s: html.escape(s, quote=True)
col = lambda c: c if c.startswith('Swatch/') else f'Color/{c}'


def geom(pts, closed=True):
    pp = ''.join(f'<PathPointType Anchor="{a * MM:.4f} {b * MM:.4f}" LeftDirection="{a * MM:.4f} {b * MM:.4f}" RightDirection="{a * MM:.4f} {b * MM:.4f}"/>' for a, b in pts)
    return (f'<Properties><PathGeometry><GeometryPathType PathOpen="{"false" if closed else "true"}"><PathPointArray>{pp}'
            '</PathPointArray></GeometryPathType></PathGeometry></Properties>')


def box(x, y, w, h):
    return geom([(x, y), (x, y + h), (x + w, y + h), (x + w, y)])


def build_idml(path_out):
    colors = ''.join(f'<Color Self="Color/{n}" Model="Process" Space="RGB" ColorValue="{c[0]} {c[1]} {c[2]}" ColorOverride="Normal" '
                     f'AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="{n}" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>'
                     for n, c in COLORS.items())
    graphic = (HDR + f'<idPkg:Graphic {NS}>'
               '<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               + colors +
               '<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/></idPkg:Graphic>')
    just = {'left': 'LeftAlign', 'right': 'RightAlign', 'center': 'CenterAlign'}
    ps = ''
    for n, s in STYLES.items():
        st = f' StrokeColor="Color/{s["stroke"][0]}" StrokeWeight="{s["stroke"][1]}"' if s.get('stroke') else ''
        ps += (f'<ParagraphStyle Self="ParagraphStyle/{q(n)}" Name="{q(n)}" Imported="false" NextStyle="ParagraphStyle/{q(n)}" KeyboardShortcut="0 0" '
               f'FontStyle="{s["style"]}" PointSize="{s["size"]}" FillColor="{col(s["color"])}"{st} Justification="{just[s["align"]]}" '
               f'Hyphenation="false" Tracking="{s.get("track", 0)}" NoBreak="false">'
               f'<Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn><PreviewColor type="enumeration">Nothing</PreviewColor>'
               f'<AppliedFont type="string">{q(s["font"])}</AppliedFont><Leading type="unit">{s["lead"]}</Leading></Properties></ParagraphStyle>')
    styles = (HDR + f'<idPkg:Styles {NS}>'
              '<RootCharacterStyleGroup Self="u79"><CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" Name="$ID/[No character style]"/></RootCharacterStyleGroup>'
              '<RootParagraphStyleGroup Self="u78"><ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false"/>'
              '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>'
              + ps + '</RootParagraphStyleGroup>'
              '<RootCellStyleGroup Self="u8e"><CellStyle Self="CellStyle/$ID/[None]" Name="$ID/[None]"/></RootCellStyleGroup>'
              '<RootTableStyleGroup Self="u90"><TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/><TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"/></RootTableStyleGroup>'
              '<RootObjectStyleGroup Self="u97"><ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/></RootObjectStyleGroup>'
              '</idPkg:Styles>')
    b = BLEED * MM
    prefs = (HDR + f'<idPkg:Preferences {NS}>'
             f'<DocumentPreference PageHeight="{HP:.4f}" PageWidth="{WP:.4f}" PagesPerDocument="1" FacingPages="false" '
             f'DocumentBleedTopOffset="{b:.4f}" DocumentBleedBottomOffset="{b:.4f}" DocumentBleedInsideOrLeftOffset="{b:.4f}" DocumentBleedOutsideOrRightOffset="{b:.4f}" '
             'DocumentBleedUniformSize="true" PageBinding="LeftToRight" AllowPageShuffle="true" Intent="PrintIntent"/>'
             f'<MarginPreference ColumnCount="1" ColumnGutter="{5 * MM:.4f}" Top="{12 * MM:.4f}" Bottom="{15 * MM:.4f}" Left="{14 * MM:.4f}" Right="{14 * MM:.4f}" ColumnDirection="Horizontal"/>'
             '<ViewPreference HorizontalMeasurementUnits="Millimeters" VerticalMeasurementUnits="Millimeters" RulerOrigin="PageOrigin"/>'
             '</idPkg:Preferences>')

    spread, stories = [], []
    for n, it in enumerate(ITEMS, 1):
        if it['kind'] == 'rect':
            spread.append(f'<Rectangle Self="uR{n}" Name="{q(it["name"])}" ContentType="Unassigned" ItemLayer="uL" Locked="false" FillColor="Color/{it["fill"]}" '
                          f'StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{SPREAD_T}">{box(it["x"], it["y"], it["w"], it["h"])}</Rectangle>')
        elif it['kind'] == 'line':
            spread.append(f'<GraphicLine Self="uG{n}" Name="{q(it["name"])}" ItemLayer="uL" Locked="false" FillColor="Swatch/None" '
                          f'StrokeColor="Color/{it["color"]}" StrokeWeight="{it["weight"]:.4f}" ItemTransform="{SPREAD_T}">'
                          f'{geom([(it["x1"], it["y1"]), (it["x2"], it["y2"])], closed=False)}</GraphicLine>')
        else:
            sid = f'uS{n}'
            spread.append(f'<TextFrame Self="uT{n}" Name="{q(it["name"])}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" ContentType="TextType" ItemLayer="uL" Locked="false" '
                          f'FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{SPREAD_T}">{box(it["x"], it["y"], it["w"], it["h"])}'
                          '<TextFramePreference TextColumnCount="1" VerticalJustification="TopAlign" FirstBaselineOffset="AscentOffset" AutoSizingType="Off" '
                          'InsetSpacing="0 0 0 0"/></TextFrame>')
            rng = ''.join(f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{q(st)}"><CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">'
                          f'<Content>{q(txt)}</Content>{"<Br/>" if i < len(it["paras"]) - 1 else ""}</CharacterStyleRange></ParagraphStyleRange>'
                          for i, (st, txt) in enumerate(it['paras']))
            stories.append((sid, HDR + f'<idPkg:Story {NS}><Story Self="{sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="{q(it["name"])}" AppliedNamedGrid="n">'
                                  '<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>'
                            + rng + '</Story></idPkg:Story>'))
    spread_xml = (HDR + f'<idPkg:Spread {NS}><Spread Self="uSp0" PageCount="1" BindingLocation="0" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" ShowMasterItems="true">'
                  f'<Page Self="uP0" Name="3" AppliedMaster="n" GeometricBounds="0 0 {HP:.4f} {WP:.4f}" ItemTransform="{SPREAD_T}" OverrideList="" TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true"/>'
                  + ''.join(spread) + '</Spread></idPkg:Spread>')
    design = (HDR + '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="8.0(370)" ?>\n'
              f'<Document {NS} Self="d" StoryList="{" ".join(s for s, _ in stories)}" ZeroPoint="0 0" ActiveLayer="uL">'
              '<idPkg:Graphic src="Resources/Graphic.xml"/><idPkg:Styles src="Resources/Styles.xml"/><idPkg:Preferences src="Resources/Preferences.xml"/>'
              '<Layer Self="uL" Name="Layer 1" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"><Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>'
              '<idPkg:Spread src="Spreads/Spread_uSp0.xml"/>'
              '<Section Self="uSec" Length="1" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageNumberStart="3" Marker="" PageStart="uP0" SectionPrefix=""/>'
              + ''.join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s, _ in stories) + '</Document>')
    container = (HDR + '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                 '<rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>')
    parts = {'META-INF/container.xml': container, 'designmap.xml': design, 'Resources/Graphic.xml': graphic,
             'Resources/Styles.xml': styles, 'Resources/Preferences.xml': prefs, 'Spreads/Spread_uSp0.xml': spread_xml}
    parts.update({f'Stories/Story_{s}.xml': x for s, x in stories})
    for name, x in parts.items():  # 모두 올바른 XML 인지
        ET.fromstring(x.split('?>', 1)[1].split('?>', 1)[-1] if name == 'designmap.xml' else x.split('?>', 1)[1])
    with zipfile.ZipFile(path_out, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/vnd.adobe.indesign-idml-package', compress_type=zipfile.ZIP_STORED)
        for name, x in parts.items():
            z.writestr(name, x.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)


# ── JSX ──────────────────────────────────────────────────────────────────────────────
def build_jsx(path_out):
    js = lambda v: json.dumps(v, ensure_ascii=True)
    just = {'left': 'Justification.LEFT_ALIGN', 'right': 'Justification.RIGHT_ALIGN', 'center': 'Justification.CENTER_ALIGN'}
    o = ['// JAJU 포트폴리오 3쪽(Prologue) — InDesign: 창 > 유틸리티 > 스크립트 패널에서 실행. 생성: tools/jaju_layout/indd_p03.py',
         '#target indesign', '(function () {',
         'app.scriptPreferences.measurementUnit = MeasurementUnits.MILLIMETERS;',
         f'var doc = app.documents.add({{documentPreferences: {{pageWidth: {W}, pageHeight: {H}, facingPages: false, pagesPerDocument: 1, documentBleedUniformSize: true, documentBleedTopOffset: {BLEED}}}}});',
         'doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS; doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;',
         'doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN; doc.zeroPoint = [0, 0];',
         'doc.sections[0].continueNumbering = false; doc.sections[0].pageNumberStart = 3;',
         'var pg = doc.pages[0];',
         'function color(n, v) { var c = doc.colors.itemByName(n); if (!c.isValid) c = doc.colors.add({name: n, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: v}); return c; }',
         'var C = {None: doc.swatches.itemByName("None")};']
    o += [f'C[{js(n)}] = color({js(n)}, {list(c)});' for n, c in COLORS.items()]
    o.append('function ps(n, f, fs, size, lead, fill, j, tr, sc, sw) { var s = doc.paragraphStyles.itemByName(n); if (!s.isValid) s = doc.paragraphStyles.add({name: n});'
             ' try { s.appliedFont = f; } catch (e) {} try { s.fontStyle = fs; } catch (e) {}'
             ' s.pointSize = size; s.leading = lead; s.fillColor = fill; s.justification = j; s.hyphenation = false; s.tracking = tr;'
             ' if (sc) { s.strokeColor = sc; s.strokeWeight = sw; } return s; }')
    o.append('var S = {};')
    for n, s in STYLES.items():
        fill = 'C.None' if s['color'] == 'Swatch/None' else f'C[{js(s["color"])}]'
        sc = f'C[{js(s["stroke"][0])}], {s["stroke"][1]}' if s.get('stroke') else 'null, 0'
        o.append(f'S[{js(n)}] = ps({js(n)}, {js(s["font"])}, {js(s["style"])}, {s["size"]}, {s["lead"]}, {fill}, {just[s["align"]]}, {s.get("track", 0)}, {sc});')
    for it in ITEMS:
        if it['kind'] == 'rect':
            o.append(f'pg.rectangles.add({{geometricBounds: [{it["y"]}, {it["x"]}, {it["y"] + it["h"]}, {it["x"] + it["w"]}], fillColor: C[{js(it["fill"])}], strokeWeight: 0, name: {js(it["name"])}}});')
        elif it['kind'] == 'line':
            o.append(f'var l = pg.graphicLines.add({{name: {js(it["name"])}}}); l.paths[0].pathPoints[0].anchor = [{it["x1"]}, {it["y1"]}]; '
                     f'l.paths[0].pathPoints[1].anchor = [{it["x2"]}, {it["y2"]}]; l.strokeColor = C[{js(it["color"])}]; l.strokeWeight = "{it["weight"]:.3f}pt";')
        else:
            content = '\r'.join(t for _, t in it['paras'])
            o.append(f'var t = pg.textFrames.add({{geometricBounds: [{it["y"]:.3f}, {it["x"]}, {it["y"] + it["h"]:.3f}, {it["x"] + it["w"]}], contents: {js(content)}, name: {js(it["name"])}}});')
            o.append('t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.textFramePreferences.firstBaselineOffset = FirstBaseline.ASCENT_OFFSET;')
            o += [f't.paragraphs[{i}].appliedParagraphStyle = S[{js(st)}];' for i, (st, _) in enumerate(it['paras'])]
    o.append('})();')
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(o) + '\n')


def main():
    os.makedirs(os.path.join(DIR, 'Document Fonts'), exist_ok=True)
    build_idml(os.path.join(DIR, NAME + '.idml'))
    build_jsx(os.path.join(DIR, NAME + '.jsx'))
    for f in ('YoungSerif-Regular.ttf', 'Lora-Regular.ttf', 'Lora-Italic.ttf', 'Lora-Bold.ttf', 'IBMPlexMono-Regular.ttf',
              'YoungSerif-OFL.txt', 'Lora-OFL.txt', 'IBMPlexMono-OFL.txt'):  # OFL: 글꼴과 사용 허락서를 함께
        shutil.copyfile(os.path.join(FONTS, f), os.path.join(DIR, 'Document Fonts', f))
    pdf = os.path.join(REPO, 'docs/jaju_rounding_vmd/layout/plan_b17.pdf')
    subprocess.run(['pdfseparate', '-f', '3', '-l', '3', pdf, os.path.join(DIR, NAME + '.pdf')], check=True)
    with zipfile.ZipFile(os.path.join(os.path.dirname(DIR), NAME + '.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
