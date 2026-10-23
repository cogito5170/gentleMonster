"""html2idml_extract.mjs 가 뽑은 쪽 목록(JSON)으로 여러 쪽짜리 IDML 을 짓는다.

  python3 tools/jaju_layout/html2idml.py <items.json> <out.idml> <첫 쪽 번호> <끝 쪽 번호> <판 폭 mm> <판 높이 mm>

옮기는 것: 쪽 바탕 · 사각형 · 원 · 그레이디언트(검정 사각형 + 그레이디언트 페더) · 사진(틀 + 링크, Links/ 에 복사) · 선 · 꺾인 선 · 글 문단.
글은 문단 하나가 글 틀 하나다(자리를 정확히 지키려고). 글꼴은 시안의 대체 글꼴을 최종 글꼴로 바꾼다(FONT_MAP).
그레이디언트 페더 · 반투명은 IDML 에 값으로 넣는다 — InDesign 에서 한 번 확인해야 한다.
"""
import html
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image

MM = 72 / 25.4
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="8.0"'
HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
q = lambda s: html.escape(s, quote=True)
K = 0.5523


def rgba(s):
    m = re.match(r'rgba?\(([^)]*)\)', s or '')
    if not m:
        return None
    v = [float(x) for x in re.split(r'[,\s/]+', m.group(1).strip()) if x]
    return (round(v[0]), round(v[1]), round(v[2]), v[3] if len(v) > 3 else 1.0)


def font_of(r):
    if r.get('dataFont'):
        f, s = r['dataFont'].split('|')
        return f, s
    fam = r['family'].split(',')[0].strip().strip('"\'')
    bold = r['weight'] >= 600
    if fam == 'Young':
        return 'Young Serif', 'Regular'
    if fam == 'Lora':
        return 'Lora', ('Bold Italic' if bold else 'Italic') if r['italic'] else ('Bold' if bold else 'Regular')
    if fam == 'Mono':
        return 'IBM Plex Mono', 'Bold' if bold else 'Regular'
    if fam == 'Inst':
        return 'Instrument Sans', 'Bold' if bold else 'Regular'
    if fam == 'Crimson':
        return 'Crimson Pro', 'Italic' if r['italic'] else 'Regular'
    if fam == 'Gloock':
        return 'Gloock', 'Regular'
    # 한글 대체 글꼴(문천역정흑) → Pretendard. 획을 더해 굵게 보이던 글은 Medium
    return 'Pretendard', 'Bold' if bold else ('Medium' if r.get('stroke', 0) > 0 else 'Regular')


class Doc:
    def __init__(self, W, H, links_dir):
        self.W, self.H = W, H
        self.WP, self.HP = W * MM, H * MM
        self.T = f'1 0 0 1 {-self.WP / 2:.4f} {-self.HP / 2:.4f}'
        self.colors, self.pstyles, self.links = {}, {}, {}
        self.links_dir = links_dir
        self.n = 0
        self.stories = []

    def color(self, c):
        key = c[:3]
        if key not in self.colors:
            self.colors[key] = f'C {key[0]} {key[1]} {key[2]}'
        return 'Color/' + self.colors[key]

    def uid(self, p):
        self.n += 1
        return f'{p}{self.n}'

    def path(self, pts, closed=True):
        pp = ''.join(f'<PathPointType Anchor="{x * MM:.4f} {y * MM:.4f}" LeftDirection="{x * MM:.4f} {y * MM:.4f}" '
                     f'RightDirection="{x * MM:.4f} {y * MM:.4f}"/>' for x, y in pts)
        return (f'<Properties><PathGeometry><GeometryPathType PathOpen="{"false" if closed else "true"}"><PathPointArray>{pp}'
                '</PathPointArray></GeometryPathType></PathGeometry></Properties>')

    def oval(self, r):
        cx, cy, rx, ry = r['x'] + r['w'] / 2, r['y'] + r['h'] / 2, r['w'] / 2, r['h'] / 2
        pts = [((cx, cy - ry), (cx - K * rx, cy - ry), (cx + K * rx, cy - ry)), ((cx + rx, cy), (cx + rx, cy - K * ry), (cx + rx, cy + K * ry)),
               ((cx, cy + ry), (cx + K * rx, cy + ry), (cx - K * rx, cy + ry)), ((cx - rx, cy), (cx - rx, cy + K * ry), (cx - rx, cy - K * ry))]
        f = lambda p: f'{p[0] * MM:.4f} {p[1] * MM:.4f}'
        pp = ''.join(f'<PathPointType Anchor="{f(a)}" LeftDirection="{f(l)}" RightDirection="{f(rr)}"/>' for a, l, rr in pts)
        return f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pp}</PathPointArray></GeometryPathType></PathGeometry></Properties>'

    def box(self, r):
        x, y, w, h = r['x'], r['y'], r['w'], r['h']
        return self.path([(x, y), (x, y + h), (x + w, y + h), (x + w, y)])

    @staticmethod
    def blend(op):
        return '' if op is None or op >= 0.995 else f'<TransparencySetting><BlendingSetting BlendMode="Normal" Opacity="{op * 100:.1f}"/></TransparencySetting>'

    # ── 항목 ──
    def rect(self, it):
        fill = rgba(it.get('fill')) if it.get('fill') else None
        stroke = rgba(it.get('stroke')) if it.get('stroke') and it.get('sw') else None
        if fill and fill[3] * it.get('fop', 1) == 0:
            fill = None
        if stroke and stroke[3] * it.get('sop', 1) == 0:
            stroke = None
        if not fill and not stroke:
            return ''
        op = it.get('opacity', 1) * (fill[3] * it.get('fop', 1) if fill else stroke[3] * it.get('sop', 1))
        geom = self.oval(it['rect']) if it.get('oval') else self.box(it['rect'])
        tag = 'Oval' if it.get('oval') else 'Rectangle'
        st = f' StrokeType="StrokeStyle/$ID/Canned Dashed 3x2"' if it.get('dashed') and stroke else ''
        return (f'<{tag} Self="{self.uid("r")}" ContentType="Unassigned" ItemLayer="uL" FillColor="{self.color(fill) if fill else "Swatch/None"}" '
                f'StrokeColor="{self.color(stroke) if stroke else "Swatch/None"}" StrokeWeight="{(it["sw"] * MM if stroke else 0):.4f}"{st} '
                f'ItemTransform="{self.T}">{geom}{self.blend(op)}</{tag}>')

    def line(self, it):
        c = rgba(it.get('stroke'))
        if not c or not it.get('sw'):
            return ''
        op = c[3] * it.get('sop', 1) * it.get('opacity', 1)
        if op == 0:
            return ''
        st = ' StrokeType="StrokeStyle/$ID/Canned Dashed 3x2"' if it.get('dashed') else ''
        return (f'<GraphicLine Self="{self.uid("g")}" ItemLayer="uL" FillColor="Swatch/None" StrokeColor="{self.color(c)}" '
                f'StrokeWeight="{it["sw"] * MM:.4f}"{st} ItemTransform="{self.T}">{self.path(it["pts"], closed=False)}{self.blend(op)}</GraphicLine>')

    def gradient(self, it):
        out = ''
        for g in split_top(it['css']):
            m = re.match(r'linear-gradient\((.*)\)$', g.strip())
            if not m:
                continue
            parts = split_top(m.group(1))
            d = 'to bottom'
            if parts[0].strip().startswith('to ') or parts[0].strip().endswith('deg'):
                d = parts.pop(0).strip()
            stops = []
            for p in parts:
                mm_ = re.match(r'\s*(rgba?\([^)]*\))\s*([\d.]+%)?', p)
                stops.append([rgba(mm_.group(1)), float(mm_.group(2)[:-1]) if mm_.group(2) else None])
            stops[0][1] = 0 if stops[0][1] is None else stops[0][1]
            stops[-1][1] = 100 if stops[-1][1] is None else stops[-1][1]
            for i, s in enumerate(stops):  # 빠진 자리는 고르게
                if s[1] is None:
                    j = next(k for k in range(i + 1, len(stops)) if stops[k][1] is not None)
                    s[1] = stops[i - 1][1] + (stops[j][1] - stops[i - 1][1]) / (j - i + 1)
            amax = max(s[0][3] for s in stops)
            if amax == 0:
                continue
            col = max(stops, key=lambda s: s[0][3])[0]
            r = it['rect']
            ang, length, start = {
                'to bottom': (-90, r['h'], (r['x'] + r['w'] / 2, r['y'])), 'to top': (90, r['h'], (r['x'] + r['w'] / 2, r['y'] + r['h'])),
                'to right': (0, r['w'], (r['x'], r['y'] + r['h'] / 2)), 'to left': (180, r['w'], (r['x'] + r['w'], r['y'] + r['h'] / 2)),
            }.get(d, (-90, r['h'], (r['x'] + r['w'] / 2, r['y'])))
            ogs = ''.join(f'<OpacityGradientStop Self="{self.uid("o")}" Opacity="{s[0][3] / amax * 100:.1f}" Location="{s[1]:.1f}" Midpoint="50"/>' for s in stops)
            out += (f'<Rectangle Self="{self.uid("r")}" Name="gradient {d}" ContentType="Unassigned" ItemLayer="uL" FillColor="{self.color(col)}" '
                    f'StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{self.T}">{self.box(r)}'
                    f'<TransparencySetting><BlendingSetting BlendMode="Normal" Opacity="{amax * 100:.1f}"/>'
                    f'<GradientFeatherSetting Applied="true" Type="Linear" Angle="{ang}" Length="{length * MM:.4f}" '
                    f'GradientStart="{start[0] * MM:.4f} {start[1] * MM:.4f}" HiliteAngle="0" HiliteLength="0">{ogs}</GradientFeatherSetting>'
                    '</TransparencySetting></Rectangle>')
        return out

    def image(self, it):
        src = it['src']
        if src not in self.links:
            name = os.path.basename(src)
            base, k = name, 1
            while name in self.links.values():
                name = f'{os.path.splitext(base)[0]}_{k}{os.path.splitext(base)[1]}'
                k += 1
            self.links[src] = name
            shutil.copyfile(src, os.path.join(self.links_dir, name))
        name = self.links[src]
        pw, ph = Image.open(src).size
        im = it['img']
        k = im['w'] * MM / pw
        tr = (f'{-k:.6f} 0 0 {k:.6f} {(im["x"] + im["w"]) * MM:.4f} {im["y"] * MM:.4f}' if it.get('flip')
              else f'{k:.6f} 0 0 {k:.6f} {im["x"] * MM:.4f} {im["y"] * MM:.4f}')
        return (f'<Rectangle Self="{self.uid("r")}" Name="{q(name)}" ContentType="GraphicType" ItemLayer="uL" FillColor="Swatch/None" '
                f'StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{self.T}">{self.box(it["frame"])}'
                f'<Image Self="{self.uid("i")}" ItemTransform="{tr}" Space="RGB" ActualPpi="72 72"><Properties><Profile type="string">$ID/Embedded</Profile>'
                f'<GraphicBounds Left="0" Top="0" Right="{pw}" Bottom="{ph}"/></Properties>'
                f'<Link Self="{self.uid("k")}" LinkResourceURI="file:Links/{q(name)}" LinkResourceFormat="$ID/JPEG" StoredState="Normal"/></Image></Rectangle>')

    def pstyle(self, font, style, size, lead, color, align, track):
        key = (font, style, round(size, 2), round(lead, 2), color, align, track)
        if key not in self.pstyles:
            self.pstyles[key] = f'{len(self.pstyles) + 1:02d} {font} {style} {size:g}/{lead:g}'
        return self.pstyles[key]

    def text(self, it):
        runs = it['runs']
        r0 = runs[0]
        lead = it['lead']
        b = it['box']
        lines = max(1, round(b['h'] * MM / lead)) if lead else 1
        wrap = it['wrap'] and lines > 1 and it.get('container')
        al = {'start': 'left', 'end': 'right', 'left': 'left', 'right': 'right', 'center': 'center', 'justify': 'left'}.get(it['align'], 'left')
        if wrap:
            x, w = it['container']['x'], it['container']['w']
        else:
            w = b['w'] * 1.06 + 3  # 글꼴이 바뀌어 조금 넓어져도 한 줄로
            x = b['x'] if al == 'left' else b['x'] + b['w'] - w if al == 'right' else b['x'] - 1.5
        y, h = b['y'], b['h'] + lead / MM * 0.8
        font, fstyle = font_of(r0)
        c0 = rgba(r0['color'])
        if it.get('clipImage'):  # 사진을 채운 글자 → 크림색 글자로 (InDesign 에서 윤곽선 만들기 후 사진을 넣는다)
            c0 = (239, 231, 218, 1.0)
            runs = [dict(r, color='rgb(239, 231, 218)') for r in runs]
        ghost = c0 and c0[3] == 0 and r0.get('stroke', 0) > 0
        fill0 = 'Swatch/None' if ghost else self.color(c0)
        track = round(r0['ls'] * 1000)
        ps = self.pstyle(font, fstyle, round(r0['size'], 2), round(lead, 2), fill0, al, track)
        op = it.get('opacity', 1)
        if ghost:
            op *= rgba(r0['strokeColor'])[3]
        elif c0 and c0[3] < 1 and all((rgba(r['color']) or (0, 0, 0, 1))[3] == c0[3] for r in runs):
            op *= c0[3]
        crs = ''
        for r in runs:
            f, s = font_of(r)
            c = rgba(r['color'])
            attrs = ''
            if (f, s) != (font, fstyle):
                attrs += f' FontStyle="{s}"'
            if abs(r['size'] - r0['size']) > 0.01:
                attrs += f' PointSize="{r["size"]:.2f}"'
            if not ghost and c and c[:3] != c0[:3]:
                attrs += f' FillColor="{self.color(c)}"'
            if ghost:
                sc = rgba(r['strokeColor'])
                attrs += f' FillColor="Swatch/None" StrokeColor="{self.color(sc)}" StrokeWeight="{r["stroke"] * 0.75:.3f}"'
            if it.get('hscale', 1) < 0.99:  # CSS scaleX → 장평
                attrs += f' HorizontalScale="{it["hscale"] * 100:.0f}"'
            props = f'<Properties><AppliedFont type="string">{q(f)}</AppliedFont></Properties>' if f != font else ''
            txt = r['text'].upper() if r.get('upper') else r['text']
            parts = txt.split('\n')
            body = '<Br/>'.join(f'<Content>{q(p)}</Content>' for p in parts)
            crs += f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"{attrs}>{props}{body}</CharacterStyleRange>'
        sid = self.uid('s')
        name = (''.join(r['text'] for r in runs))[:40]
        if it.get('clipImage'):
            name = f'{name} — 원래는 글자 안에 사진({os.path.basename(it["clipImage"])}). 윤곽선 만들기 후 사진을 안에 붙여 넣기'
        self.stories.append((sid, HDR + f'<idPkg:Story {NS}><Story Self="{sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="{q(name)}" AppliedNamedGrid="n">'
                             '<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>'
                             f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{q(ps)}">{crs}</ParagraphStyleRange></Story></idPkg:Story>'))
        return (f'<TextFrame Self="{self.uid("t")}" Name="{q(name)}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" ContentType="TextType" '
                f'ItemLayer="uL" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="{self.T}">'
                f'{self.box(dict(x=x, y=y, w=w, h=h))}<TextFramePreference TextColumnCount="1" VerticalJustification="TopAlign" '
                f'FirstBaselineOffset="AscentOffset" AutoSizingType="Off" InsetSpacing="0 0 0 0"/>{self.blend(op)}</TextFrame>')

    def page(self, pg):
        BL = 3
        bg = rgba(pg['bg'])
        o = [self.rect(dict(rect=dict(x=-BL, y=-BL, w=self.W + 2 * BL, h=self.H + 2 * BL), fill=pg['bg']))] if bg else []
        for it in pg['items']:
            o.append({'rect': self.rect, 'line': self.line, 'gradient': self.gradient, 'image': self.image, 'text': self.text}[it['kind']](it))
        return ''.join(o)


def split_top(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    out.append(cur)
    return out


def build(items_json, out_idml, first, last, W, H):
    pages = json.load(open(items_json))[first - 1:last]
    d = os.path.dirname(out_idml)
    links = os.path.join(d, 'Links')
    os.makedirs(links, exist_ok=True)
    doc = Doc(W, H, links)
    spreads = []
    for i, pg in enumerate(pages):
        body = doc.page(pg)
        spreads.append(HDR + f'<idPkg:Spread {NS}><Spread Self="uSp{i}" PageCount="1" BindingLocation="0" AllowPageShuffle="true" '
                       f'ItemTransform="1 0 0 1 0 {i * (doc.HP + 40):.4f}" ShowMasterItems="true">'
                       f'<Page Self="uP{i}" Name="{first + i}" AppliedMaster="n" GeometricBounds="0 0 {doc.HP:.4f} {doc.WP:.4f}" ItemTransform="{doc.T}" '
                       'OverrideList="" TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true"/>' + body + '</Spread></idPkg:Spread>')
    colors = ''.join(f'<Color Self="Color/{n}" Model="Process" Space="RGB" ColorValue="{c[0]} {c[1]} {c[2]}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" '
                     f'AlternateColorValue="" Name="{n}" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>' for c, n in doc.colors.items())
    graphic = (HDR + f'<idPkg:Graphic {NS}>'
               '<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               + colors + '<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
               '<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/><StrokeStyle Self="StrokeStyle/$ID/Canned Dashed 3x2" Name="$ID/Canned Dashed 3x2"/>'
               '</idPkg:Graphic>')
    just = {'left': 'LeftAlign', 'right': 'RightAlign', 'center': 'CenterAlign'}
    ps = ''.join(f'<ParagraphStyle Self="ParagraphStyle/{q(n)}" Name="{q(n)}" Imported="false" NextStyle="ParagraphStyle/{q(n)}" KeyboardShortcut="0 0" '
                 f'FontStyle="{q(s)}" PointSize="{size}" FillColor="{col}" Justification="{just[al]}" Hyphenation="false" Tracking="{tr}">'
                 f'<Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn><PreviewColor type="enumeration">Nothing</PreviewColor>'
                 f'<AppliedFont type="string">{q(f)}</AppliedFont><Leading type="unit">{lead}</Leading></Properties></ParagraphStyle>'
                 for (f, s, size, lead, col, al, tr), n in doc.pstyles.items())
    styles = (HDR + f'<idPkg:Styles {NS}>'
              '<RootCharacterStyleGroup Self="u79"><CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" Name="$ID/[No character style]"/></RootCharacterStyleGroup>'
              '<RootParagraphStyleGroup Self="u78"><ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false"/>'
              '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>'
              + ps + '</RootParagraphStyleGroup>'
              '<RootCellStyleGroup Self="u8e"><CellStyle Self="CellStyle/$ID/[None]" Name="$ID/[None]"/></RootCellStyleGroup>'
              '<RootTableStyleGroup Self="u90"><TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/><TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"/></RootTableStyleGroup>'
              '<RootObjectStyleGroup Self="u97"><ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/><ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/></RootObjectStyleGroup>'
              '</idPkg:Styles>')
    b = 3 * MM
    prefs = (HDR + f'<idPkg:Preferences {NS}>'
             f'<DocumentPreference PageHeight="{doc.HP:.4f}" PageWidth="{doc.WP:.4f}" PagesPerDocument="{len(pages)}" FacingPages="false" '
             f'DocumentBleedTopOffset="{b:.4f}" DocumentBleedBottomOffset="{b:.4f}" DocumentBleedInsideOrLeftOffset="{b:.4f}" DocumentBleedOutsideOrRightOffset="{b:.4f}" '
             'DocumentBleedUniformSize="true" PageBinding="LeftToRight" AllowPageShuffle="true" Intent="PrintIntent"/>'
             f'<MarginPreference ColumnCount="1" ColumnGutter="{5 * MM:.4f}" Top="{12 * MM:.4f}" Bottom="{15 * MM:.4f}" Left="{14 * MM:.4f}" Right="{14 * MM:.4f}" ColumnDirection="Horizontal"/>'
             '<ViewPreference HorizontalMeasurementUnits="Millimeters" VerticalMeasurementUnits="Millimeters" RulerOrigin="PageOrigin"/>'
             '</idPkg:Preferences>')
    design = (HDR + '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="8.0(370)" ?>\n'
              f'<Document {NS} Self="d" StoryList="{" ".join(s for s, _ in doc.stories)}" ZeroPoint="0 0" ActiveLayer="uL">'
              '<idPkg:Graphic src="Resources/Graphic.xml"/><idPkg:Styles src="Resources/Styles.xml"/><idPkg:Preferences src="Resources/Preferences.xml"/>'
              '<Layer Self="uL" Name="Layer 1" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"><Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>'
              + ''.join(f'<idPkg:Spread src="Spreads/Spread_uSp{i}.xml"/>' for i in range(len(spreads)))
              + f'<Section Self="uSec" Length="{len(spreads)}" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageNumberStart="{first}" Marker="" PageStart="uP0" SectionPrefix=""/>'
              + ''.join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s, _ in doc.stories) + '</Document>')
    container = (HDR + '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                 '<rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>')
    parts = {'META-INF/container.xml': container, 'designmap.xml': design, 'Resources/Graphic.xml': graphic, 'Resources/Styles.xml': styles,
             'Resources/Preferences.xml': prefs}
    parts.update({f'Spreads/Spread_uSp{i}.xml': x for i, x in enumerate(spreads)})
    parts.update({f'Stories/Story_{s}.xml': x for s, x in doc.stories})
    for name, x in parts.items():
        body = x.split('?>', 1)[1]
        if name == 'designmap.xml':
            body = body.split('?>', 1)[1]
        ET.fromstring(body)
    with zipfile.ZipFile(out_idml, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/vnd.adobe.indesign-idml-package', compress_type=zipfile.ZIP_STORED)
        for name, x in parts.items():
            z.writestr(name, x.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)
    return doc


if __name__ == '__main__':
    a = sys.argv
    d = build(a[1], a[2], int(a[3]), int(a[4]), float(a[5]), float(a[6]))
    print('wrote', a[2], len(d.stories), 'text frames', len(d.links), 'links', len(d.pstyles), 'paragraph styles', len(d.colors), 'colours')
