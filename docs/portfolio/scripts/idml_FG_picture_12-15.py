"""v2 펼침 F · G (12–15쪽) · (002) PICTURE — IDML 의 템플릿 글을 원고로 바꾸고, 빠진 글을 새로 넣는다.

원고: docs/portfolio/v2_FG_picture_12-15.md
쓰는 법: python3 idml_FG_picture_12-15.py 원본.idml 결과.idml
결과 IDML 을 InDesign 에서 열고 .indd 로 저장한다.

IDML 안의 쪽 번호는 1–5 다(1 = 커버, 2–3 = 책 12–13쪽, 4–5 = 책 14–15쪽).
XML 은 문자열 그대로 고친다(InDesign 이 쓴 서식 · 속성을 건드리지 않으려고).
"""
import html
import re
import sys
import zipfile
import xml.dom.minidom

SPREAD_F = "Spreads/Spread_u31c6.xml"  # 책 12–13쪽
SPREAD_G = "Spreads/Spread_u37ea.xml"  # 책 14–15쪽

# 스토리 id: [(지금 글, 바꿀 글)] — 글자 서식(굵기 · 크기)은 그대로
TEXT = {
    "u3876": [("column grids", "Color"), ("(multiple vertical columns)", "(a food truck, Guam)")],          # 푸드트럭 캡션
    "u390b": [("modular grids", "Bulbs"), ("(rows and columns forming modules)", "(a rooftop, Haebangchon)")],  # 루프탑 캡션
    "u38ae": [("modular grids", "Sprout"), ("(rows and columns forming modules)", "(on the sand, Guam)")],    # 새싹 캡션
}

# 지울 글 상자: (펼침, 프레임 id, 스토리 id) — 모두 템플릿 글
REMOVE = [
    (SPREAD_F, "u3827", "u382a"),  # download now / www.template.systems
    (SPREAD_F, "u383e", "u3841"),  # (003) — ARCHITECTURE 번호라 PICTURE 지면에 두지 않는다
    (SPREAD_F, "u3855", "u3858"),  # © 2026 Template.Systems — 이 자리에 Q1 제목이 온다
    (SPREAD_F, "u388a", "u388d"),  # Experimental Grid Exploration
]

# 13쪽 큰 제목 PICUTRE → 12쪽 왼쪽 위의 Q1 제목 (큰 제목 PICTURE 는 E-10 으로 간다)
TITLE_STORY, TITLE_FRAME = "u38c6", "u38c2"
TITLE_LINES = ["Why do I", "take pictures?"]
TITLE_SIZE, TITLE_LEADING = 56, 58
TITLE_X_OLD, TITLE_X_NEW = "653.2570270333416", "-364.3707874015748"  # 왼쪽 끝 → 12쪽 왼쪽 여백(-810.7)

# 13쪽 새싹 캡션 상자가 오른쪽 재단선 밖(865pt)까지 나가 있다 → 오른쪽 여백(810.7pt)까지로
SPROUT_FRAME, SPROUT_RIGHT_OLD, SPROUT_RIGHT_NEW = "u38ab", "233.00000000000006", "178.58267716535431"

# 13쪽 새싹 사진이 오른쪽 재단선(841.9pt)에서 끝난다 → 재단 여유(19.84pt)까지 늘린다. 사진은 상자 밖으로 370pt 넘게 남아 있다
SPROUT_PHOTO, SPROUT_PHOTO_RIGHT_OLD, SPROUT_PHOTO_RIGHT_NEW = "u38a6", "-448.149606299213", "-428.30708661417363"

# 12쪽 본문 상자: 여섯 줄 넘게 흐르면 넘치므로 아래로 60pt 늘린다
BODY_FRAME, BODY_BOTTOM_OLD, BODY_BOTTOM_NEW = "u3810", "103.58267716535194", "163.58267716535194"

# 14–15쪽 사진: 위아래 재단 여유(19.84pt)가 없다 → 상자를 재단 여유까지 늘리고 사진을 같은 비율로 키운다
PHOTO_FRAME, PHOTO_IMAGE = "u3ad2", "u3ad3"
PAGE_HALF, BLEED = 595.2755905511812, 19.84251968503937

# 15쪽 새로 넣는 글: Q2 (흰 카드, 사진 위)
CARD_FRAME, CARD_STORY = "u9f001", "u9f002"
CARD_LEFT, CARD_TOP, CARD_WIDTH, CARD_HEIGHT = 362.7, -564.1, 448.0, 330.0  # 15쪽 오른쪽 위, 여백 안
CARD_INSET = 24
CARD_TITLE = "What makes a good picture?"
CARD_BODY = [
    "첫째, 오래 보게 되는 사진이다. 한 번 보고 넘기지 않고, 계속 들여다보게 되는 것.",
    "둘째, 하나의 이야기가 되는 사진이다. 사람, 빛, 색, 장소가 서로 어울려 한 장면이 되는 것.",
    "좋은 사진은 좋은 스타일, 좋은 공간과 같다. 멈추게 하고, 다시 떠오르게 한다.",
]
CARD_CAPTION = ("Water", "(people in the sea, Guam)")


def story_path(sid):
    return f"Stories/Story_{sid}.xml"


def replace_content(xml_text, old, new):
    def sub(m):
        if html.unescape(m.group(1)).strip() == old:
            sub.hits += 1
            return f"<Content>{html.escape(new, quote=False)}</Content>"
        return m.group(0)
    sub.hits = 0
    out = re.sub(r"<Content>(.*?)</Content>", sub, xml_text, flags=re.S)
    if sub.hits != 1:
        raise SystemExit(f"'{old}' 를 {sub.hits}번 찾음 (1번이어야 함)")
    return out


def frame_block(spread, fid, tag="TextFrame"):
    m = re.search(rf'<{tag} Self="{fid}".*?</{tag}>', spread, re.S)
    if not m:
        raise SystemExit(f"{tag} {fid} 를 못 찾음")
    return m.group(0)


def replace_once(text, old, new, what):
    if text.count(old) != 1:
        raise SystemExit(f"{what}: '{old[:40]}' 를 {text.count(old)}번 찾음")
    return text.replace(old, new)


def anchors(points):
    """[(x, y)…] → PathPointArray"""
    return "".join(
        f'\n\t\t\t\t\t\t\t<PathPointType Anchor="{x} {y}" LeftDirection="{x} {y}" RightDirection="{x} {y}" />'
        for x, y in points
    )


def rewrite_title(xml_text):
    xml_text = replace_content(xml_text, "PICUTRE", TITLE_LINES[0])
    xml_text = replace_once(
        xml_text,
        f"<Content>{TITLE_LINES[0]}</Content>",
        f"<Content>{TITLE_LINES[0]}</Content>\n\t\t\t\t<Br />\n\t\t\t\t<Content>{html.escape(TITLE_LINES[1], quote=False)}</Content>",
        "제목",
    )
    xml_text = re.sub(r'PointSize="136\.\d+"', f'PointSize="{TITLE_SIZE}"', xml_text)
    xml_text = re.sub(r'<Leading type="unit">136\.\d+</Leading>', f'<Leading type="unit">{TITLE_LEADING}</Leading>', xml_text)
    return xml_text


def char_range(font, style, size, leading, parts, br_before=False, br_after=False):
    lead = f'\n\t\t\t\t\t<Leading type="unit">{leading}</Leading>' if leading else ""
    lang = "$ID/English: USA" if font != "본고딕 KR" else "$ID/ko_KR"
    body = "\n\t\t\t\t<Br />".join(f"\n\t\t\t\t<Content>{html.escape(p, quote=False)}</Content>" for p in parts)
    return (
        f'\n\t\t\t<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" '
        f'FontStyle="{style}" PointSize="{size}" FillColor="Color/Black" AppliedLanguage="{lang}">'
        f"\n\t\t\t\t<Properties>{lead}"
        f'\n\t\t\t\t\t<AppliedFont type="string">{font}</AppliedFont>'
        "\n\t\t\t\t</Properties>"
        + ("\n\t\t\t\t<Br />" if br_before else "")
        + body
        + ("\n\t\t\t\t<Br />" if br_after else "")
        + "\n\t\t\t</CharacterStyleRange>"
    )


def para(space_after, *ranges):
    return (
        f'\n\t\t<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle" '
        f'Hyphenation="false" SpaceAfter="{space_after}">'
        + "".join(ranges) + "\n\t\t</ParagraphStyleRange>"
    )


def card_story():
    paragraphs = para(14, char_range("Helvetica Neue", "Bold", 16, None, [CARD_TITLE], br_after=True))
    for i, p in enumerate(CARD_BODY):
        last = i == len(CARD_BODY) - 1
        paragraphs += para(18 if last else 8, char_range("본고딕 KR", "Regular", 16, 30, [p], br_after=True))
    paragraphs += para(0,
                       char_range("Helvetica Neue", "Bold", 16, None, [CARD_CAPTION[0] + " "]),
                       char_range("Helvetica Neue", "Regular", 16, None, [CARD_CAPTION[1]], br_before=True))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="21.5">\n'
        f'\t<Story Self="{CARD_STORY}" UserText="true" IsEndnoteStory="false" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">\n'
        '\t\t<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection" />\n'
        '\t\t<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false" />'
        f"{paragraphs}\n"
        "\t</Story>\n"
        "</idPkg:Story>\n"
    )


def card_frame(template):
    """12쪽 본문 상자(u3810)를 본떠 15쪽 카드 상자를 만든다: 흰 바탕, 안쪽 여백, 글에 맞춰 높이가 자란다."""
    f = template
    f = f.replace('Self="u3810" ParentStory="u3813"', f'Self="{CARD_FRAME}" ParentStory="{CARD_STORY}"', 1)
    f = re.sub(r'ItemLayer="[^"]*"', 'ItemLayer="ua80"', f, count=1)
    f = re.sub(r'ItemTransform="[^"]*"', 'ItemTransform="1 0 0 1 0 0" FillColor="Color/Paper"', f, count=1)
    x0, y0 = CARD_LEFT, CARD_TOP
    x1, y1 = x0 + CARD_WIDTH, y0 + CARD_HEIGHT
    f = re.sub(r"<PathPointArray>.*?</PathPointArray>",
               "<PathPointArray>" + anchors([(x0, y0), (x0, y1), (x1, y1), (x1, y0)]) + "\n\t\t\t\t\t\t</PathPointArray>",
               f, count=1, flags=re.S)
    inner = CARD_WIDTH - 2 * CARD_INSET
    f = re.sub(r'<TextFramePreference [^>]*>',
               f'<TextFramePreference TextColumnCount="1" TextColumnFixedWidth="{inner}" TextColumnMaxWidth="0" '
               'AutoSizingType="HeightOnly" AutoSizingReferencePoint="TopCenterPoint" UseMinimumHeightForAutoSizing="false">',
               f, count=1)
    f = re.sub(r'(<InsetSpacing type="list">).*?(</InsetSpacing>)',
               lambda m: m.group(1) + "".join(f'\n\t\t\t\t\t\t<ListItem type="unit">{CARD_INSET}</ListItem>' for _ in range(4)) + "\n\t\t\t\t\t" + m.group(2),
               f, count=1, flags=re.S)
    return f


def bleed_photo(spread):
    rect = frame_block(spread, PHOTO_FRAME, "Rectangle")
    path = re.search(r"<PathPointArray>.*?</PathPointArray>", rect, re.S).group(0)
    lo, hi = f"{PAGE_HALF + BLEED}", f"{-(PAGE_HALF + BLEED)}"
    new_path = path.replace(f" -{PAGE_HALF}\"", f" {hi}\"").replace(f" {PAGE_HALF}\"", f" {lo}\"")
    if new_path.count(lo) != 12 or new_path.count(hi) != 6:  # lo 는 hi 안에도 들어 있다
        raise SystemExit("사진 상자 위아래 끝을 못 고침")
    new = rect.replace(path, new_path, 1)
    img = re.search(rf'<Image Self="{PHOTO_IMAGE}"[^>]*ItemTransform="([^"]*)"', new)
    a, b, c, d, tx, ty = map(float, img.group(1).split())
    k = (PAGE_HALF + BLEED) / PAGE_HALF  # 높이가 재단 여유까지 덮도록
    cx = tx + 2764 * a / 2  # 2764 = 사진 픽셀 너비(GraphicBounds)
    a2 = a * k
    tx2 = cx - 2764 * a2 / 2
    ty2 = -(PAGE_HALF + BLEED)
    new = new.replace(f'ItemTransform="{img.group(1)}"', f'ItemTransform="{a2} 0 0 {a2} {tx2} {ty2}"', 1)
    new = re.sub(r'EffectivePpi="\d+ \d+"', f'EffectivePpi="{round(72 / a2)} {round(72 / a2)}"', new, count=1)
    return spread.replace(rect, new)


def main(src, dst):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist()}
    text = lambda n: files[n].decode("utf-8")

    for sid, pairs in TEXT.items():
        t = text(story_path(sid))
        for old, new in pairs:
            t = replace_content(t, old, new)
        files[story_path(sid)] = t.encode("utf-8")

    files[story_path(TITLE_STORY)] = rewrite_title(text(story_path(TITLE_STORY))).encode("utf-8")

    spreads = {SPREAD_F: text(SPREAD_F), SPREAD_G: text(SPREAD_G)}
    dm = text("designmap.xml")
    for sp, fid, sid in REMOVE:
        spreads[sp], n = re.subn(rf'\s*<TextFrame Self="{fid}" ParentStory="{sid}".*?</TextFrame>', "", spreads[sp], flags=re.S)
        if n != 1:
            raise SystemExit(f"글 상자 {fid} 를 {n}번 찾음")
        del files[story_path(sid)]
        dm = replace_once(dm, f'\t<idPkg:Story src="{story_path(sid)}" />\n', "", "designmap")
        dm = re.sub(r'(StoryList="[^"]*?)\b' + sid + r' ?', r"\1", dm)

    f = spreads[SPREAD_F]
    title = frame_block(f, TITLE_FRAME)
    f = f.replace(title, replace_once(title, f" {TITLE_X_OLD} ", f" {TITLE_X_NEW} ", "제목 위치"))
    sprout = frame_block(f, SPROUT_FRAME)
    f = f.replace(sprout, sprout.replace(f'"{SPROUT_RIGHT_OLD} ', f'"{SPROUT_RIGHT_NEW} '))
    if frame_block(f, SPROUT_FRAME).count(SPROUT_RIGHT_NEW) != 6:
        raise SystemExit("새싹 캡션 상자 오른쪽 끝을 못 고침")
    photo = frame_block(f, SPROUT_PHOTO, "Rectangle")
    path = re.search(r"<PathPointArray>.*?</PathPointArray>", photo, re.S).group(0)
    new_path = path.replace(f'"{SPROUT_PHOTO_RIGHT_OLD} ', f'"{SPROUT_PHOTO_RIGHT_NEW} ')
    if new_path.count(SPROUT_PHOTO_RIGHT_NEW) != 6:
        raise SystemExit("새싹 사진 상자 오른쪽 끝을 못 고침")
    f = f.replace(photo, photo.replace(path, new_path, 1))
    body = frame_block(f, BODY_FRAME)
    f = f.replace(body, body.replace(f" {BODY_BOTTOM_OLD}\"", f" {BODY_BOTTOM_NEW}\""))
    if frame_block(f, BODY_FRAME).count(BODY_BOTTOM_NEW) != 6:
        raise SystemExit("본문 상자 아래 끝을 못 고침")
    spreads[SPREAD_F] = f

    g = bleed_photo(spreads[SPREAD_G])
    g = replace_once(g, "\t</Spread>", card_frame(frame_block(spreads[SPREAD_F], BODY_FRAME)) + "\n\t</Spread>", "카드 넣기")
    spreads[SPREAD_G] = g
    files[story_path(CARD_STORY)] = card_story().encode("utf-8")
    dm = replace_once(dm, 'StoryList="', f'StoryList="{CARD_STORY} ', "StoryList")
    dm = replace_once(dm, f'\t<idPkg:Story src="{story_path("u3813")}" />\n',
                      f'\t<idPkg:Story src="{story_path("u3813")}" />\n\t<idPkg:Story src="{story_path(CARD_STORY)}" />\n', "designmap")

    for sp, t in spreads.items():
        files[sp] = t.encode("utf-8")
    files["designmap.xml"] = dm.encode("utf-8")

    for n, b in files.items():
        if n.endswith(".xml"):
            xml.dom.minidom.parseString(b)  # 깨진 XML 이면 여기서 멈춘다

    order = [n for n in zin.namelist() if n in files] + [story_path(CARD_STORY)]
    with zipfile.ZipFile(dst, "w") as zout:
        zout.writestr(zipfile.ZipInfo("mimetype"), files["mimetype"], compress_type=zipfile.ZIP_STORED)
        for n in order:
            if n != "mimetype":
                zout.writestr(n, files[n], compress_type=zipfile.ZIP_DEFLATED)
    print("ok", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
