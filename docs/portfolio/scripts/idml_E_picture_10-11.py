"""v2 펼침 E (10–11쪽) · (002) PICTURE — IDML 의 템플릿 글을 원고로 바꾼다.

원고: docs/portfolio/v2_E_fix.md
쓰는 법: python3 idml_E_picture_10-11.py 원본.idml 결과.idml
결과 IDML 을 InDesign 에서 열고 .indd 로 저장한다.

독립: 10·11쪽 펼침(Spread)과 그 펼침의 스토리만 고친다. 다른 펼침 · 마스터는 한 글자도 바꾸지 않는다.
글 상자는 id 가 아니라 글 내용으로 찾는다 — 책 전체 IDML 이든 10–11쪽만 내보낸 IDML 이든,
A–D 를 먼저 고쳤든 아니든, 몇 번을 돌리든 결과가 같다.

XML 은 문자열 그대로 고친다(InDesign 이 쓴 서식 · 속성을 건드리지 않으려고).
"""
import html
import re
import sys
import zipfile
import xml.dom.minidom
import xml.etree.ElementTree as ET

LEFT, RIGHT = "10", "11"

# 큰 제목: MOMENT LIKE A PHOTOGRAPH → PICTURE, 2쪽 STYLE 과 같은 글자 · 같은 자리
TITLE = "PICTURE"
TITLE_PARTS = re.compile(r"MOMENT|PHOTOGR|LIKEA")  # 공백을 지우고 대문자로 본 제목 조각
TITLE_MIN_SIZE = 40  # 이보다 작은 글은 제목이 아니다 (부제 A Moment like A Photograph 를 건드리지 않게)
# 2쪽 STYLE (포트폴리오 2-3 수정.idml, 스토리 u1a0e · 상자 u1a08 에서 잰 값)
STYLE_FONT, STYLE_FONT_STYLE, STYLE_SIZE = "Helvetica", "Bold", "136.02373887240356"
STYLE_BOX = (56.69, 100.28, 961.69, 338.32)  # 왼쪽 쪽 왼쪽 위에서: 왼쪽 · 위 · 오른쪽 · 아래 (pt)
MATCH_STYLE_TITLE = True

OPENING_KO = [
    "두 번째로, 내가 멈추는 곳은 멋진 장면 앞이다. 빛, 색, 사람, 장소가 한순간에 맞아떨어질 때가 있다. 그때 나는 카메라를 꺼낸다.",
    "앞의 거리 사진도 그랬다. 헤드폰을 쓴 사람, 체크 셔츠와 슬리퍼, 그리고 그 뒤의 화분과 칠판. 사람과 장소가 함께 맞아떨어진 순간이었다.",
    "그래서 내 두 번째 이야기는 사진이다.",
]
SCENE_LINE = ["I stop for a scene.", "(My second story is about pictures.)"]

# (찾는 글, 바꿀 줄들, 설명) — 줄마다 원래 그 줄의 글자 서식을 그대로 쓴다
LINE_REPLACEMENTS = [
    (re.compile(r"Template Systems|Grid Systems Series"), ["A Moment like A Photograph"], "10 오른쪽 라벨 → 부제"),
    (re.compile(r"Grid Exploration"), SCENE_LINE, "11 아래 → 영어 한 줄"),
    (re.compile(r"카메라를 꺼낸다|두 번째 이야기는 사진이다|^빛, 색"), OPENING_KO, "11 본문 → 여는 글"),
]

# 이 글이 들어 있는 글 상자를 지운다: 10 가운데 라벨 · 10 왼쪽 아래 잘린 글
REMOVE = re.compile(r"download now|template\.systems|plate\.systems", re.I)

# 11 기차 사진: 테두리를 빼고 캡션(단어 하나)을 단다. 캡션이 필요 없으면 "".
CAPTION = "Puddle"
CAPTION_GAP = 6.0

LEFTOVER = re.compile(r"template|grid|download|www\.", re.I)
LEFTOVER_TITLE = re.compile(r"MOMENT|PHOTOGR")

# Helvetica Bold 글자 너비 (1/1000 em) — 제목 겹침을 어림할 때만 쓴다
HELV_BOLD = {"P": 667, "I": 278, "C": 722, "T": 611, "U": 722, "R": 722, "E": 667}

GRAPHIC_TAGS = {"Rectangle", "Polygon", "Oval"}
IMAGE_TAGS = {"Image", "PDF", "EPS", "ImportedPage", "WMF", "PICT"}


# ---------- 읽기 ----------

def story_path(sid):
    return f"Stories/Story_{sid}.xml"


def story_text(xml_text):
    out = []
    for m in re.finditer(r"<Content>(.*?)</Content>|<Br\s*/>", xml_text, re.S):
        out.append(html.unescape(m.group(1)) if m.group(1) is not None else "\n")
    return "".join(out)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def first_size(xml_text):
    m = re.search(r'<CharacterStyleRange [^>]*PointSize="([^"]+)"', xml_text)
    return float(m.group(1)) if m else 12.0


def matrix(s):
    a, b, c, d, tx, ty = (float(v) for v in s.split())
    return (a, b, c, d, tx, ty)


def mul(m, n):
    # 먼저 n, 다음 m (IDML: 자식 변환 → 부모 변환)
    a, b, c, d, tx, ty = m
    a2, b2, c2, d2, tx2, ty2 = n
    return (a2 * a + b2 * c, a2 * b + b2 * d, c2 * a + d2 * c, c2 * b + d2 * d,
            tx2 * a + ty2 * c + tx, tx2 * b + ty2 * d + ty)


def apply(m, x, y):
    a, b, c, d, tx, ty = m
    return (a * x + c * y + tx, b * x + d * y + ty)


class Item:
    def __init__(self, el, m, in_group):
        self.tag = el.tag
        self.id = el.get("Self")
        self.story = el.get("ParentStory")
        self.in_group = in_group
        self.stroke = float(el.get("StrokeWeight") or 0)
        self.has_image = any(ch.tag in IMAGE_TAGS for ch in el.iter())
        pts = [apply(m, *map(float, a.get("Anchor").split()))
               for a in el.iter("PathPointType")]
        xs, ys = [p[0] for p in pts] or [0], [p[1] for p in pts] or [0]
        self.box = (min(xs), min(ys), max(xs), max(ys))  # 왼 · 위 · 오른 · 아래 (펼침 좌표)
        self.page = None


def walk(el, m, in_group, out):
    for ch in el:
        if ch.tag == "TextFrame" or ch.tag in GRAPHIC_TAGS or ch.tag == "Group":
            cm = mul(m, matrix(ch.get("ItemTransform", "1 0 0 1 0 0")))
            if ch.tag == "Group":
                walk(ch, cm, True, out)
            else:
                out.append(Item(ch, cm, in_group))


def pages_of(spread_el):
    pages = {}
    for p in spread_el.iter("Page"):
        tx, ty = matrix(p.get("ItemTransform"))[4:]
        y1, x1, y2, x2 = map(float, p.get("GeometricBounds").split())
        pages[p.get("Name")] = (tx + x1, ty + y1, tx + x2, ty + y2)
    return pages


def overlaps(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


# ---------- 쓰기 ----------

def set_lines(xml_text, lines):
    """스토리 글을 lines 로 바꾼다. i 번째 줄은 원래 i 번째 줄의 단락 · 글자 서식(넘치면 마지막 줄의 서식)."""
    psrs = list(re.finditer(r"(<ParagraphStyleRange[^>]*>)(\s*<Properties>.*?</Properties>)?(.*?)</ParagraphStyleRange>",
                            xml_text, re.S))
    if not psrs:
        raise SystemExit("단락이 없는 스토리")
    styles, cur = [], None  # 줄마다 (단락 머리, 글자 머리)
    for pm in psrs:
        p_head = pm.group(1) + (pm.group(2) or "")
        for cm in re.finditer(r"(<CharacterStyleRange[^>]*>)(\s*<Properties>.*?</Properties>)?(.*?)</CharacterStyleRange>",
                              pm.group(3), re.S):
            c_head = cm.group(1) + (cm.group(2) or "")
            for tok in re.finditer(r"<Content>.*?</Content>|<Br\s*/>", cm.group(3), re.S):
                if cur is None:
                    cur = (p_head, c_head)
                if tok.group(0).startswith("<Br"):
                    styles.append(cur)
                    cur = None
            if cur is None and not styles:
                cur = (p_head, c_head)  # 빈 글자 범위만 있는 스토리
    if cur is not None:
        styles.append(cur)
    if not styles:
        raise SystemExit("글자 범위가 없는 스토리")

    out, open_p = [], None
    for i, line in enumerate(lines):
        p_head, c_head = styles[min(i, len(styles) - 1)]
        if p_head != open_p:
            if open_p is not None:
                out.append("\n\t\t</ParagraphStyleRange>")
            out.append("\n\t\t" + p_head)
            open_p = p_head
        br = "\n\t\t\t\t<Br />" if i < len(lines) - 1 else ""
        out.append(f"\n\t\t\t{c_head}\n\t\t\t\t<Content>{html.escape(line, quote=False)}</Content>{br}\n\t\t\t</CharacterStyleRange>")
    out.append("\n\t\t</ParagraphStyleRange>")
    start, end = psrs[0].start(), psrs[-1].end()
    return xml_text[:start].rstrip() + "".join(out) + "\n\t" + xml_text[end:].lstrip()


def regular_second_line(xml_text):
    """둘째 줄(괄호 줄)을 첫 줄과 같은 굵기에서 Regular 로 — A 3쪽 라벨(굵은 줄 + 보통 괄호 줄)과 맞춘다."""
    heads = list(re.finditer(r"<CharacterStyleRange [^>]*>", xml_text))
    if len(heads) < 2:
        return xml_text
    style = lambda h: (re.search(r' FontStyle="([^"]*)"', h.group(0)) or [None, None])[1]
    if style(heads[1]) != style(heads[0]) or style(heads[1]) in (None, "Regular"):
        return xml_text
    h = heads[1]
    return xml_text[:h.start()] + re.sub(r' FontStyle="[^"]*"', ' FontStyle="Regular"', h.group(0)) + xml_text[h.end():]


def set_char(xml_text, font, font_style, size):
    def head(m):
        h = m.group(0)
        for attr, val in (("FontStyle", font_style), ("PointSize", size)):
            if f' {attr}="' in h:
                h = re.sub(rf' {attr}="[^"]*"', f' {attr}="{val}"', h)
            else:
                h = h[:-1] + f' {attr}="{val}">'
        return h
    xml_text = re.sub(r"<CharacterStyleRange [^>]*>", head, xml_text)
    xml_text = re.sub(r'<AppliedFont type="string">[^<]*</AppliedFont>',
                      f'<AppliedFont type="string">{font}</AppliedFont>', xml_text)
    xml_text = re.sub(r'<Leading type="unit">[^<]*</Leading>', f'<Leading type="unit">{size}</Leading>', xml_text)
    return xml_text


def element_span(xml_text, tag, sid):
    """<tag Self="sid" ...> ... </tag> 의 위치. 같은 태그가 안에 겹쳐 있어도 짝을 맞춘다."""
    m = re.search(rf'<{tag} Self="{sid}"[^>]*?(/?)>', xml_text)
    if not m:
        return None
    if m.group(1) == "/":
        return m.start(), m.end()
    depth, pos = 1, m.end()
    pat = re.compile(rf"<{tag}\b[^>]*?(/?)>|</{tag}>")
    while depth:
        n = pat.search(xml_text, pos)
        if n.group(0).startswith("</"):
            depth -= 1
        elif n.group(1) != "/":
            depth += 1
        pos = n.end()
    return m.start(), pos


def set_box(frame_xml, box):
    """상자를 펼침 좌표 box(왼 · 위 · 오른 · 아래)로 옮긴다 (그룹 밖 상자만)."""
    x0, y0, x1, y1 = box
    frame_xml = re.sub(r'ItemTransform="[^"]*"', 'ItemTransform="1 0 0 1 0 0"', frame_xml, count=1)
    corners = iter([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])

    def pt(m):
        x, y = next(corners)
        a = f"{x:.4f} {y:.4f}"
        return f'<PathPointType Anchor="{a}" LeftDirection="{a}" RightDirection="{a}" />'
    frame_xml, n = re.subn(r"<PathPointType [^>]*/>", pt, frame_xml)
    if n != 4:
        raise SystemExit(f"사각형이 아닌 상자 (점 {n}개)")
    return frame_xml


def new_id(files, used):
    k = 0xe000
    blob = None
    while True:
        cand = f"u{k:x}"
        if cand not in used:
            if blob is None:
                blob = b"".join(files.values())
            if f'"{cand}"'.encode() not in blob and f"_{cand}.xml".encode() not in blob:
                used.add(cand)
                return cand
        k += 1


# ---------- 실행 ----------

def main(src, dst):
    zin = zipfile.ZipFile(src)
    names = zin.namelist()
    files = {n: zin.read(n) for n in names}
    text = lambda n: files[n].decode("utf-8")
    log, missing, warn = [], [], []

    dm = text("designmap.xml")
    spread_name = None
    for sp in re.findall(r'<idPkg:Spread src="([^"]+)"', dm):
        root = ET.fromstring(files[sp])
        pg = pages_of(root)
        if LEFT in pg and RIGHT in pg:
            spread_name, pages = sp, pg
            break
    if not spread_name:
        raise SystemExit(f"{LEFT}·{RIGHT}쪽이 한 펼침으로 들어 있지 않다")
    spread = text(spread_name)
    removed_stories = set()

    def scan():
        root = ET.fromstring(spread.encode("utf-8"))
        sp_el = root.find("Spread")
        items = []
        walk(sp_el, (1, 0, 0, 1, 0, 0), False, items)  # 상자 좌표 = 펼침 안쪽 좌표 (Page 와 같은 기준)
        for it in items:
            cx, cy = (it.box[0] + it.box[2]) / 2, (it.box[1] + it.box[3]) / 2
            for name, b in pages.items():
                if b[0] <= cx <= b[2] and b[1] <= cy <= b[3]:
                    it.page = name
        return items

    def stext(sid):
        return story_text(text(story_path(sid))) if story_path(sid) in files else ""

    def remove_story_frames(sid, why):
        nonlocal spread, dm
        while True:
            m = re.search(rf'<TextFrame Self="(\w+)" ParentStory="{sid}"', spread)
            if not m:
                break
            a, b = element_span(spread, "TextFrame", m.group(1))
            spread = spread[:a] + spread[b:]
        files.pop(story_path(sid), None)
        dm = dm.replace(f'\t<idPkg:Story src="{story_path(sid)}" />\n', "")
        dm = re.sub(rf'(StoryList="[^"]*?)(?<!\w){sid}(?!\w) ?', r"\1", dm)
        removed_stories.add(sid)
        log.append(f"글 상자 지움 ({why})")

    def put_story(sid, xml_text):
        files[story_path(sid)] = xml_text.encode("utf-8")

    # 1. 큰 제목
    items = scan()
    title_sid, title_item = None, None
    for it in items:
        if it.tag != "TextFrame" or it.story in removed_stories:
            continue
        t = stext(it.story)
        s = re.sub(r"\s+", "", t).upper()
        if len(s) > 40 or not TITLE_PARTS.search(s) or first_size(text(story_path(it.story))) < TITLE_MIN_SIZE:
            continue
        if title_sid is None:
            title_sid, title_item = it.story, it
        elif it.story != title_sid:
            remove_story_frames(it.story, f"제목 조각 {norm(t)}")
    if title_sid:
        before = norm(stext(title_sid))
        xt = set_lines(text(story_path(title_sid)), [TITLE])
        if MATCH_STYLE_TITLE:
            xt = set_char(xt, STYLE_FONT, STYLE_FONT_STYLE, STYLE_SIZE)
        put_story(title_sid, xt)
        log.append(f"큰 제목: {before} → {TITLE}")
        frames = re.findall(rf'<TextFrame Self="(\w+)" ParentStory="{title_sid}"', spread)
        for fid in frames[1:]:  # 이어진 상자는 첫 상자만 남긴다
            a, b = element_span(spread, "TextFrame", fid)
            spread = spread[:a] + spread[b:]
        if len(frames) > 1:
            spread = re.sub(rf'(<TextFrame Self="{frames[0]}"[^>]*?) NextTextFrame="\w+"', r'\1 NextTextFrame="n"', spread)
        if MATCH_STYLE_TITLE:
            if title_item.in_group:
                warn.append("큰 제목 상자가 그룹 안에 있어 자리는 그대로 둠 — 2쪽 STYLE 자리에 맞춰 주세요")
            else:
                lx, ly = pages[LEFT][0], pages[LEFT][1]
                box = (lx + STYLE_BOX[0], ly + STYLE_BOX[1], lx + STYLE_BOX[2], ly + STYLE_BOX[3])
                a, b = element_span(spread, "TextFrame", frames[0])
                spread = spread[:a] + set_box(spread[a:b], box) + spread[b:]
                log.append(f"큰 제목: 2쪽 STYLE 과 같은 글자 ({STYLE_FONT} {STYLE_FONT_STYLE} {float(STYLE_SIZE):.2f}pt) · 같은 자리")
    else:
        if any(it.tag == "TextFrame" and norm(stext(it.story)) == TITLE for it in items):
            log.append(f"큰 제목 {TITLE} (이미 되어 있음)")
        else:
            missing.append("큰 제목 MOMENT LIKE A PHOTOGRAPH")

    # 2. 줄 바꾸기 (라벨 · 본문)
    spread_stories = []
    for it in scan():
        if it.tag == "TextFrame" and it.story not in spread_stories and story_path(it.story) in files:
            spread_stories.append(it.story)
    for pat, lines, what in LINE_REPLACEMENTS:
        hit = next((s for s in spread_stories if pat.search(norm(stext(s)))), None)
        if hit:
            xt = set_lines(text(story_path(hit)), lines)
            put_story(hit, regular_second_line(xt) if lines is SCENE_LINE else xt)
            log.append(what)
        elif any(norm(stext(s)).startswith(lines[0]) for s in spread_stories):
            log.append(what + " (이미 되어 있음)")
        else:
            missing.append(what)

    # 3. 템플릿 글 상자 지우기
    for s in list(spread_stories):
        t = stext(s)
        if REMOVE.search(t):
            remove_story_frames(s, norm(t)[:40])
            spread_stories.remove(s)

    # 4. 11쪽 사진: 테두리 빼기 · 캡션
    items = scan()
    photos = [it for it in items if it.tag in GRAPHIC_TAGS and it.has_image and it.page == RIGHT]
    stroked = [it for it in photos if it.stroke > 0]
    for it in stroked:
        spread = re.sub(rf'(<{it.tag} Self="{it.id}"[^>]*?) StrokeWeight="[^"]*"', r'\1 StrokeWeight="0"', spread, count=1)
        log.append(f"{RIGHT}쪽 사진 테두리 뺌 ({it.stroke:g}pt)")
    if not stroked:
        warn.append(f"{RIGHT}쪽 사진에 InDesign 테두리가 없음 — 이미 뺐거나, 테두리가 그림 파일 안에 있으면 그림 원본에서 지우세요")

    if CAPTION:
        photo = stroked[0] if len(stroked) == 1 else (photos[0] if len(photos) == 1 else None)
        label = next((it for it in items if it.tag == "TextFrame" and norm(stext(it.story)).startswith(SCENE_LINE[0])), None)
        if any(it.tag == "TextFrame" and norm(stext(it.story)) == CAPTION for it in items):
            log.append(f"캡션 {CAPTION} (이미 있음)")
        elif not photo:
            warn.append(f"캡션: {RIGHT}쪽 기차 사진을 하나로 정하지 못함 (사진 {len(photos)}장) — 직접 다세요")
        elif not label:
            warn.append("캡션: 서식을 빌릴 라벨을 못 찾음 — 직접 다세요")
        else:
            used = set()
            sid, fid = new_id(files, used), new_id(files, used)
            st = text(story_path(label.story))
            st = re.sub(rf'<Story Self="{label.story}"', f'<Story Self="{sid}"', st, count=1)
            put_story(sid, set_lines(st, [CAPTION]))
            a, b = element_span(spread, "TextFrame", label.id)
            fx = spread[a:b]
            fx = fx.replace(f'Self="{label.id}"', f'Self="{fid}"', 1).replace(f'ParentStory="{label.story}"', f'ParentStory="{sid}"', 1)
            fx = re.sub(r'PreviousTextFrame="\w+"', 'PreviousTextFrame="n"', fx)
            fx = re.sub(r'NextTextFrame="\w+"', 'NextTextFrame="n"', fx)
            for other in set(re.findall(r' Self="(\w+)"', fx)) - {fid}:
                fx = fx.replace(f'Self="{other}"', f'Self="{new_id(files, used)}"')
            h = label.box[3] - label.box[1]
            px0, _, px1, py1 = photo.box
            fx = set_box(fx, (px0, py1 + CAPTION_GAP, max(px1, px0 + 120), py1 + CAPTION_GAP + h))
            end = spread.rindex("</Spread>")
            spread = spread[:end] + "\t" + fx.strip() + "\n\t" + spread[end:]
            dm = dm.replace('<idPkg:Story src="', f'<idPkg:Story src="{story_path(sid)}" />\n\t<idPkg:Story src="', 1)
            dm = re.sub(r'StoryList="', f'StoryList="{sid} ', dm, count=1)
            log.append(f"캡션 {CAPTION} 을 사진 아래에 닮")

    # 5. 확인
    items = scan()
    texts = {it.story: norm(stext(it.story)) for it in items if it.tag == "TextFrame"}
    if "(002)" not in texts.values():
        warn.append("(002) 를 못 찾음 — 10쪽 섹션 번호를 확인하세요")
    title = next((it for it in items if it.tag == "TextFrame" and texts.get(it.story) == TITLE), None)
    if title:
        size = first_size(text(story_path(title.story)))
        w = sum(HELV_BOLD.get(ch, 667) for ch in TITLE) / 1000 * size
        ink = (title.box[0], title.box[1], title.box[0] + w, title.box[1] + size)
        for it in items:
            if it is title or it.page != LEFT or not overlaps(ink, it.box):
                continue
            what = texts.get(it.story, it.tag)[:20] if it.tag == "TextFrame" else it.tag
            warn.append(f"겹침 후보: 큰 제목 ↔ {what} — 지면에서 보세요")
        if title.box[0] + w > pages[LEFT][2]:
            warn.append("큰 제목 글자가 접힘을 넘어감 — 지면에서 보세요")
    leftovers = [t[:40] for t in texts.values() if LEFTOVER.search(t) or LEFTOVER_TITLE.search(t)]
    body = next((s for s, t in texts.items() if t.startswith(OPENING_KO[0][:10])), None)
    if body:
        st = text(story_path(body))
        font = re.search(r'<AppliedFont type="string">([^<]*)', st)
        warn.append(f"본문 글꼴 {font.group(1) if font else '?'} {first_size(st):g}pt — A 3쪽 본문(AppleGothic 13pt · 행간 20.8)과 같은지 보세요")

    files[spread_name] = spread.encode("utf-8")
    files["designmap.xml"] = dm.encode("utf-8")
    for n, b in files.items():
        if n.endswith(".xml"):
            xml.dom.minidom.parseString(b)  # 깨진 XML 이면 여기서 멈춘다

    with zipfile.ZipFile(dst, "w") as zout:
        zout.writestr(zipfile.ZipInfo("mimetype"), files.pop("mimetype"), compress_type=zipfile.ZIP_STORED)
        order = [n for n in names if n in files] + [n for n in files if n not in names]
        for n in order:
            zout.writestr(n, files[n], compress_type=zipfile.ZIP_DEFLATED)

    print(f"바꾼 것 ({len(log)})\n" + "\n".join(log))
    if missing:
        print(f"\n못 찾은 것 ({len(missing)})\n" + "\n".join(missing))
    if warn:
        print("\n확인할 것\n" + "\n".join(warn))
    if leftovers:
        print("\n남은 템플릿 글\n" + "\n".join(leftovers))
    print("\nok", dst)
    return log, missing, warn, leftovers


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
