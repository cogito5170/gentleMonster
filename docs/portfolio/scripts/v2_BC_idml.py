"""v2 펼침 B · C (책 4–7쪽) — IDML 의 템플릿 글을 원고로 바꾼 새 IDML 을 만든다.

원고: docs/portfolio/v2_01_style.md 의 "B · 4–5쪽" · "C · 6–7쪽"
입력: 지원자가 InDesign 에서 내보낸 4-7.idml (1쪽 표지 + 2–3쪽 펼침 B + 4–5쪽 펼침 C)

    python3 v2_BC_idml.py 4-7.idml 4-7_v2.idml [--preview 미리보기폴더]

- 글 상자는 Self id 로 찾는다(아래 STORIES · FRAMES). 다른 IDML 에 쓰려면 id 를 맞춘다.
- 한글은 본고딕 KR Regular, 영어 제목 · 라벨은 지면 글꼴(Helvetica Neue 14pt) 그대로.
- 한글이 영어 템플릿 상자보다 길어서 상자 세 개(Q1·Q2, MY STYLE, MARKET)는 빈 자리 쪽으로 키운다.
- 넘침은 글꼴 폭으로 어림한다(한글 1em, 영문은 Helvetica 폭). 최종 확인은 InDesign 에서 한다.
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- 원고

KO_FONT = ("본고딕 KR", "Regular")
LATIN = "Helvetica Neue"
SIZE = 14
KO_LEADING = 22  # 14pt 한글에 157% — 템플릿 자동 행간(120%)은 한글에 좁다

Q1_KO = ("같은 흰 셔츠도 누가 입느냐에 따라 전혀 다르게 보인다. 소매를 걷는지, 단추를 어디까지 채우는지, 무엇과 같이 입는지. "
         "그 차이가 스타일이다. 나는 그 사람이 무엇을 고르고, 무엇을 빼고, 무엇을 강조했는지를 본다. "
         "좋은 공간도 무엇을 넣고 무엇을 뺄지 고르는 데서 시작한다.")
Q2_KO = ("좋은 스타일은 유행을 따라가는 것이 아니다. 그 사람에게 맞고, 꾸준하고, 편안한 것. "
         "그런 사람은 멀리서 봐도 그 사람인 줄 안다. 좋은 공간도 그렇다. 들어가자마자 어디인지 알 수 있다.")

# 색 다섯 개 — 지면 캡처에서 잰 대략값. 인쇄 전에 원본 사진에서 다시 뽑아 여기만 고친다
MY_STYLE_COLORS = [("Black", "#1D1B19"), ("Olive", "#2C2716"), ("Beige", "#C4B29B"),
                   ("Off-white", "#C3BFB1"), ("Slate", "#445162")]
MY_STYLE_LINE = "헤어 스타일, 옷의 톤과 향의 무드를 그날 갈 장소에 맞춘다."
CHIP_TAB = 88.5  # 칩 다섯 개를 상자 폭(442.5pt)에 고르게

# 지원자가 채울 사실 — 비워 두면 그 칸은 지면에 나오지 않는다
C_YEAR = ""   # 예: "2023"
C_ROLE = ""   # 예: "Solo project"

C_INTRO_KO = ("사람의 스타일을 고르는 눈으로 화면도 만들었다. DAILY LookBook은 매일의 옷차림을 모아 보는 스타일 사이트다. "
              "다른 사람의 하루 옷차림을 보고, 스타일 범주(Dandy · Casual · Street · Amekaji · Office)로 고르고, "
              "마음에 든 옷을 바로 찾는다.")
# 화면(MARKET)에 실제로 있는 것만 쓴다: FILTER 의 Color · Fit · Length · Pattern · Material, "이름_색" 상품명, 원래 값 > 할인된 값
C_MARKET_KO = ("MARKET 화면은 색 · 핏 · 길이 · 무늬 · 소재로 옷을 거른다. 길에서 사람을 볼 때 눈에 들어오는 것들이다. "
               "상품 이름 뒤에는 색을 붙이고(Balmacan\u00A0Wool\u00A0Coat_Black), 값 옆에 할인된 값을 함께 두어 "
               "룩북에서 본 옷을 바로 찾게 했다.")


def c_meta():
    parts = ["Web design", "University project"] + [p for p in (C_YEAR, C_ROLE) if p] + ["Photoshop + Illustrator"]
    return " · ".join(parts)


# 단락 = (단락 속성, [글 조각]) · 글 조각 = (글, 종류) — 종류: "b" 영어 굵게, "r" 영어 보통, "s" 영어 작게, "ko" 한글, ("chip", 색)
def label(title, sub):
    return [({}, [(title, "b")]), ({}, [(sub, "r")])]


def chips_row():
    runs = []
    for i, (name, hexv) in enumerate(MY_STYLE_COLORS):
        if i:
            runs.append(("\t", "r"))
        runs += [("■", ("chip", name, hexv)), (" " + name, "r")]
    return runs


def hex_row():
    return [("\t".join(h for _, h in MY_STYLE_COLORS), "s")]


TABS = [round(CHIP_TAB * i, 2) for i in range(1, len(MY_STYLE_COLORS))]

STORIES = {
    # 펼침 B (IDML 2–3쪽 = 책 4–5쪽)
    "u32d": label("Shop front, evening", "(black long coat)"),
    "u343": label("Riverside, night", "(olive parka)"),          # 한강이면 "Han River, night"
    "u391": label("Park, sunset", "(light jacket)"),
    "u3bd": [({}, [("MOOD", "b")])],
    "u3d3": [({"SpaceAfter": 6}, [("Why is style important?", "b")]),
             ({}, [(Q1_KO, "ko")]),
             ({"SpaceBefore": 22, "SpaceAfter": 6}, [("What makes a good style?", "b")]),
             ({}, [(Q2_KO, "ko")])],
    "u3a7": [({"SpaceAfter": 6}, [("MY STYLE", "b")]),
             ({"Tabs": TABS}, chips_row()),
             ({"Tabs": TABS, "SpaceAfter": 8}, hex_row()),
             ({}, [(MY_STYLE_LINE, "ko")])],
    # 펼침 C (IDML 4–5쪽 = 책 6–7쪽)
    "u442": [({}, [("DAILY LookBook", "b")]),
             ({"SpaceAfter": 10}, [(c_meta(), "r")]),
             ({}, [(C_INTRO_KO, "ko")])],
    "u458": [({}, [(C_MARKET_KO, "ko")])],
    "u416": label("MAIN", "(home)"),            # 위 라벨: 작은 메인 화면 윗선에 맞춰 있다
    "u42c": label("MARKET", "(product list)"),  # 아래 라벨: 큰 MARKET 화면 아랫선에 붙어 있다
}

# 지우는 템플릿 글 상자: 글 상자 id → 이야기 id
REMOVE = {"u36b": "u359",   # download now / www.template.systems
          "u381": "u36f"}   # © 2026 Template.Systems

# 키우는 상자: 글 상자 id → (펼침 좌표 x1, y1, x2, y2, 세로 정렬)
FRAMES = {
    # Q1·Q2: 재킷 사진 오른쪽 단, 사진 위·아래 끝에 맞춘다
    "u3e5": (576.79, -356.67, 810.71, 173.33, "TopAlign"),
    # MY STYLE: 아랫선(495)은 그대로, 위로 키우고 글은 아래에 붙인다
    "u3b9": (368.21, 330.0, 810.71, 495.0, "BottomAlign"),
    # MARKET 설명: 메인 화면 위 20pt 까지, 글은 아래에 붙인다
    "u46a": (599.50, -150.0, 810.71, 163.5, "BottomAlign"),
}

# ---------------------------------------------------------------- 이야기 XML

PSR_ATTRS = ('AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle" Composer="HL Composer" Hyphenation="false" '
             'HyphenationZone="36" RuleAboveLineWeight="1" RuleBelowLineWeight="1" Justification="LeftAlign" DropcapDetail="1" '
             'ParagraphShadingTopOrigin="AscentTopOrigin" ParagraphShadingBottomOrigin="DescentBottomOrigin" '
             'ParagraphBorderTopOrigin="AscentTopOrigin" ParagraphBorderBottomOrigin="DescentBottomOrigin"')


def color_id(name):
    return "Color/MY STYLE " + name


def run_style(kind):
    """(FontStyle, PointSize, 글꼴, 언어, 행간, 글자색)"""
    if kind == "b":
        return "Bold", SIZE, LATIN, "$ID/English: USA", None, None
    if kind == "r":
        return "Regular", SIZE, LATIN, "$ID/English: USA", None, None
    if kind == "s":
        return "Regular", 11, LATIN, "$ID/English: USA", None, None
    if kind == "ko":
        return KO_FONT[1], SIZE, KO_FONT[0], "$ID/Korean", KO_LEADING, None
    if kind[0] == "chip":
        return KO_FONT[1], SIZE, KO_FONT[0], "$ID/English: USA", None, color_id(kind[1])
    raise ValueError(kind)


def csr(text, kind, br):
    style, size, font, lang, leading, fill = run_style(kind)
    attrs = ('AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FontStyle="%s" PointSize="%s" '
             'KerningMethod="$ID/Optical" StrokeWeight="1" AppliedLanguage="%s"' % (style, size, lang))
    if fill:
        attrs += ' FillColor="%s"' % escape(fill, {'"': "&quot;"})
    props = '<AppliedFont type="string">%s</AppliedFont>' % escape(font)
    if leading:
        props = '<Leading type="unit">%s</Leading>' % leading + props
    parts = text.split("\t")
    content = "".join(("<Content>%s</Content>" % escape(p) if p else "") + ("<Content>&#9;</Content>" if i < len(parts) - 1 else "")
                      for i, p in enumerate(parts))
    return ('\t\t\t<CharacterStyleRange %s>\n\t\t\t\t<Properties>%s</Properties>\n\t\t\t\t%s%s\n\t\t\t</CharacterStyleRange>\n'
            % (attrs, props, content, "<Br />" if br else ""))


def psr(pattrs, runs, last):
    extra = ""
    for k in ("SpaceBefore", "SpaceAfter"):
        if k in pattrs:
            extra += ' %s="%s"' % (k, pattrs[k])
    props = ""
    if "Tabs" in pattrs:
        props = "\t\t\t<Properties><TabList type=\"list\">%s</TabList></Properties>\n" % "".join(
            '<ListItem type="record"><Alignment type="enumeration">LeftAlign</Alignment>'
            '<AlignmentCharacter type="string">.</AlignmentCharacter><Leader type="string"></Leader>'
            '<Position type="unit">%s</Position></ListItem>' % t for t in pattrs["Tabs"])
    out = "\t\t<ParagraphStyleRange %s%s>\n%s" % (PSR_ATTRS, extra, props)
    for i, (text, kind) in enumerate(runs):
        out += csr(text, kind, br=(not last and i == len(runs) - 1))
    return out + "\t\t</ParagraphStyleRange>\n"


def write_story(path, paragraphs):
    x = open(path, encoding="utf-8").read()
    head = x[:x.index("<ParagraphStyleRange")]
    tail = x[x.rindex("</ParagraphStyleRange>") + len("</ParagraphStyleRange>"):]
    body = "".join(psr(p, r, i == len(paragraphs) - 1) for i, (p, r) in enumerate(paragraphs))
    open(path, "w", encoding="utf-8").write(head.rstrip("\t") + body.rstrip("\n") + tail)


# ---------------------------------------------------------------- 펼침 XML

def frame_block(x, fid):
    m = re.search(r'<TextFrame Self="%s".*?</TextFrame>\s*' % fid, x, re.S)
    if not m:
        raise SystemExit("글 상자 %s 를 못 찾음" % fid)
    return m


def resize_frame(x, fid, box):
    m = frame_block(x, fid)
    blk = m.group(0)
    t = [float(v) for v in re.search(r'ItemTransform="([^"]*)"', blk).group(1).split()]
    if t[:4] != [1, 0, 0, 1]:
        raise SystemExit("글 상자 %s 가 돌아가 있음 — 손으로 키운다" % fid)
    x1, y1, x2, y2, vj = box
    lx1, ly1, lx2, ly2 = x1 - t[4], y1 - t[5], x2 - t[4], y2 - t[5]
    pts = [(lx1, ly1), (lx1, ly2), (lx2, ly2), (lx2, ly1)]
    new_pts = "".join('<PathPointType Anchor="{0} {1}" LeftDirection="{0} {1}" RightDirection="{0} {1}" />'.format(*p) for p in pts)
    blk = re.sub(r"<PathPointArray>.*?</PathPointArray>", "<PathPointArray>%s</PathPointArray>" % new_pts, blk, flags=re.S)
    blk = re.sub(r'TextColumnFixedWidth="[^"]*"', 'TextColumnFixedWidth="%s"' % (x2 - x1), blk)
    blk = re.sub(r' VerticalJustification="[^"]*"', "", blk)
    blk = blk.replace("<TextFramePreference ", '<TextFramePreference VerticalJustification="%s" ' % vj, 1)
    return x[:m.start()] + blk + x[m.end():]


def remove_frame(x, fid):
    m = frame_block(x, fid)
    return x[:m.start()] + x[m.end():]


# ---------------------------------------------------------------- 색 견본

def add_colors(src):
    g = os.path.join(src, "Resources", "Graphic.xml")
    x = open(g, encoding="utf-8").read()
    d = os.path.join(src, "designmap.xml")
    dm = open(d, encoding="utf-8").read()
    colors, swatches = "", ""
    for i, (name, hexv) in enumerate(MY_STYLE_COLORS):
        cid = color_id(name)
        if 'Self="%s"' % cid in x:
            continue
        rgb = " ".join(str(int(hexv[k:k + 2], 16)) for k in (1, 3, 5))
        ref = "uMyStyleSwatch%d" % i
        colors += ('\t<Color Self="%s" Model="Process" Space="RGB" ColorValue="%s" ColorOverride="Normal" ConvertToHsb="false" '
                   'AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="MY STYLE %s %s" ColorEditable="true" '
                   'ColorRemovable="true" Visible="true" SwatchCreatorID="7937" SwatchColorGroupReference="%s" />\n'
                   % (cid, rgb, name, hexv, ref))
        swatches += '\t\t<ColorGroupSwatch Self="%s" SwatchItemRef="%s" />\n' % (ref, cid)
    i = x.index("\t<Swatch ")
    open(g, "w", encoding="utf-8").write(x[:i] + colors + x[i:])
    i = dm.index("\t</ColorGroup>")
    open(d, "w", encoding="utf-8").write(dm[:i] + swatches + dm[i:])


# ---------------------------------------------------------------- 넘침 어림 · 미리보기

def _fonts():
    from PIL import ImageFont
    def f(path, size):
        return ImageFont.truetype(path, size)
    return {
        "lat": lambda s: f("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", s),
        "latb": lambda s: f("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", s),
        "ko": lambda s: f("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", s),
    }


def layout(paragraphs, width, scale=1.0):
    """글을 상자 폭에 흘려 [(y, [(x, 글, 글꼴, 크기, 색)])] 과 전체 높이를 돌려준다. 단어(띄어쓰기) 단위로 나눈다."""
    F = _fonts()
    # InDesign 처럼 첫 줄은 행간이 아니라 글꼴 윗선(약 0.8em)에, 마지막 줄 아래로 아랫선(약 0.2em)
    lines, y, first, last_size = [], 0.0, True, SIZE
    for pi, (pattrs, runs) in enumerate(paragraphs):
        y += pattrs.get("SpaceBefore", 0) if pi else 0
        tokens = []
        for text, kind in runs:
            style, size, font, _, leading, fill = run_style(kind)
            fkey = "ko" if font == KO_FONT[0] else ("latb" if style == "Bold" else "lat")
            lead = leading or size * 1.2
            for tok in re.split(r"(\t| )", text):
                if tok:
                    tokens.append((tok, fkey, size, lead, fill))
        line, x, lead_max, size_max = [], 0.0, 0, 0
        tabs = pattrs.get("Tabs", [])
        for tok, fkey, size, lead, fill in tokens:
            if tok == "\t":
                nxt = [t for t in tabs if t > x + 0.1]
                x = nxt[0] if nxt else x
                continue
            w = F[fkey](int(size * 10)).getlength(tok) / 10.0
            if tok != " " and x + w > width and line:
                y += lead_max if not first else 0.8 * size_max
                first = False
                lines.append((y, line))
                line, x, lead_max, size_max = [], 0.0, 0, 0
            if tok == " " and not line:
                continue
            line.append((x, tok, fkey, size, fill))
            x += w
            lead_max = max(lead_max, lead)
            size_max = max(size_max, size)
        y += lead_max if not first else 0.8 * size_max
        first = False
        last_size = size_max
        lines.append((y, line))
        y += pattrs.get("SpaceAfter", 0)
    return lines, y + 0.2 * last_size


def preview(src, outdir):
    from PIL import Image, ImageDraw
    import xml.etree.ElementTree as ET
    F = _fonts()
    os.makedirs(outdir, exist_ok=True)
    S = 1.2  # px / pt
    stories = {sid: STORIES[sid] for sid in STORIES}
    for name in sorted(os.listdir(os.path.join(src, "Spreads"))):
        root = ET.parse(os.path.join(src, "Spreads", name)).getroot().find("Spread")
        pages = root.findall("Page")
        if len(pages) < 2:
            continue
        W, H = 841.89 * 2, 1190.55
        img = Image.new("RGB", (int(W * S), int(H * S)), "white")
        dr = ImageDraw.Draw(img)
        ox, oy = 841.89, 595.28

        def P(px, py):
            return ((px + ox) * S, (py + oy) * S)
        for el in root.iter():
            if el.tag not in ("Rectangle", "TextFrame"):
                continue
            t = [float(v) for v in el.get("ItemTransform").split()]
            pts = [tuple(map(float, a.get("Anchor").split())) for a in el.iter("PathPointType")]
            xs = [p[0] + t[4] for p in pts]
            ys = [p[1] + t[5] for p in pts]
            box = (min(xs), min(ys), max(xs), max(ys))
            if el.tag == "Rectangle":
                fill = el.get("FillColor")
                img_el = el.find("Image")
                if img_el is not None:
                    dr.rectangle([P(box[0], box[1]), P(box[2], box[3])], fill=(70, 70, 70))
                    link = img_el.find("Link").get("LinkResourceURI")
                    dr.text((P(box[0], box[1])[0] + 8, P(box[0], box[1])[1] + 8), os.path.basename(link), fill="white", font=F["lat"](16))
                elif fill and fill.startswith("Color/u11"):
                    dr.rectangle([P(box[0], box[1]), P(box[2], box[3])], fill=(220, 213, 59))
                continue
            sid = el.get("ParentStory")
            paragraphs = stories.get(sid)
            if paragraphs is None:
                x = open(os.path.join(src, "Stories", "Story_%s.xml" % sid), encoding="utf-8").read()
                txt = "".join(re.findall(r"<Content>([^<]*)</Content>", x))
                paragraphs = [({}, [(txt, "r")])]
            lines, h = layout(paragraphs, box[2] - box[0])
            vj = (el.find("TextFramePreference").get("VerticalJustification") or "TopAlign")
            top = box[1] + (box[3] - box[1] - h if vj == "BottomAlign" else 0)
            over = h > box[3] - box[1] + 0.5
            dr.rectangle([P(box[0], box[1]), P(box[2], box[3])], outline=(220, 0, 0) if over else (0, 140, 255), width=2)
            for ly, segs in lines:
                for sx, tok, fkey, size, fill in segs:
                    col = (0, 0, 0)
                    if fill:
                        hexv = dict((("Color/MY STYLE " + n), h_) for n, h_ in MY_STYLE_COLORS)[fill]
                        col = tuple(int(hexv[k:k + 2], 16) for k in (1, 3, 5))
                    f = F[fkey](int(size * S))
                    px, py = P(box[0] + sx, top + ly)
                    dr.text((px, py), tok, fill=col, font=f, anchor="ls")
            if over:
                print("  넘침 %s (%s): 글 %.0fpt > 상자 %.0fpt" % (el.get("Self"), sid, h, box[3] - box[1]))
        for i, pg in enumerate(pages):
            dr.line([P(0, -595.28), P(0, 595.28)], fill=(150, 150, 150), width=1)
        out = os.path.join(outdir, name.replace(".xml", ".png"))
        img.save(out)
        print("  미리보기", out)


# ---------------------------------------------------------------- 실행

def build(src_idml, out_idml, preview_dir=None):
    work = tempfile.mkdtemp()
    src = os.path.join(work, "src")
    with zipfile.ZipFile(src_idml) as z:
        z.extractall(src)

    for sid, paragraphs in STORIES.items():
        write_story(os.path.join(src, "Stories", "Story_%s.xml" % sid), paragraphs)

    for name in os.listdir(os.path.join(src, "Spreads")):
        p = os.path.join(src, "Spreads", name)
        x = open(p, encoding="utf-8").read()
        for fid in REMOVE:
            if 'Self="%s"' % fid in x:
                x = remove_frame(x, fid)
        for fid, box in FRAMES.items():
            if 'Self="%s"' % fid in x:
                x = resize_frame(x, fid, box)
        open(p, "w", encoding="utf-8").write(x)

    d = os.path.join(src, "designmap.xml")
    dm = open(d, encoding="utf-8").read()
    for sid in REMOVE.values():
        os.remove(os.path.join(src, "Stories", "Story_%s.xml" % sid))
        dm = re.sub(r'\s*<idPkg:Story src="Stories/Story_%s.xml" />' % sid, "", dm)
        dm = re.sub(r'(StoryList="[^"]*?)\b%s ?' % sid, r"\1", dm)
    open(d, "w", encoding="utf-8").write(dm)
    add_colors(src)

    # 모두 XML 로 읽히는지 확인
    import xml.etree.ElementTree as ET
    for dp, _, fs in os.walk(src):
        for f in fs:
            if f.endswith(".xml"):
                ET.parse(os.path.join(dp, f))

    # IDML: mimetype 이 맨 앞, 압축 없이
    with zipfile.ZipFile(out_idml, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(src, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
        for dp, _, fs in os.walk(src):
            for f in sorted(fs):
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, src)
                if rel != "mimetype":
                    z.write(full, rel)
    print("만듦", out_idml)
    if preview_dir:
        preview(src, preview_dir)
    shutil.rmtree(work)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--preview")
    a = ap.parse_args()
    build(a.src, a.out, a.preview)
