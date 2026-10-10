"""포트폴리오 8-11 — 펼침 D(책 8–9쪽, 다리 ①) · E(책 10–11쪽, PICTURE 여는 펼침).
IDML 파일 안에서는 표지 다음 2–3쪽이 D, 4–5쪽이 E 다.

원고: docs/portfolio/v2_01_style.md (D) · docs/portfolio/v2_02_picture.md (E)
쓰는 법: python3 idml_D-E_8-11.py 원본.idml 결과.idml
결과 IDML 을 InDesign 에서 열고 .indd 로 저장한다. 이 파일 하나로 돌고 다른 스크립트가 필요 없다.

XML 은 문자열 그대로 고친다(InDesign 이 쓴 서식 · 속성을 건드리지 않으려고).
"""
import html
import re
import sys
import zipfile
import xml.dom.minidom

SPREAD_D = "Spreads/Spread_u21e.xml"
SPREAD_E = "Spreads/Spread_u26d.xml"

# ── D: 풀쿼트 두 줄. 흰 글자(Paper)가 겨자색 바탕(RGB 220 213 59) 위에서 1.5 : 1 이라 읽히지 않는다 → [Black]
D_STORIES = ["u242", "u258"]
D_TEXT_FROM, D_TEXT_TO = "Color/Paper", "Color/Black"   # 마젠타 강조 단어는 그대로

# ── E: PICTURE 여는 펼침
OPENING = [
    "두 번째로, 내가 멈추는 곳은 멋진 장면 앞이다. 빛, 색, 사람, 장소가 한순간에 맞아떨어질 때가 있다. "
    "그때 나는 카메라를 꺼낸다. 앞의 거리 사진도 그랬다. 헤드폰을 쓴 사람, 체크 셔츠와 슬리퍼, "
    "그리고 그 뒤의 화분과 칠판. 사람과 장소가 함께 맞아떨어진 순간이었다. ",
    "그래서 내 두 번째 이야기는 사진이다.",
]
OPENING_OLD = [
    "빛, 색, 사람, 장소가 한순간에 맞아떨어질 때가 있다. 그때 나는 카메라를 꺼낸다. 앞 페이지의 사진도 그랬다. "
    "헤드폰을 쓴 사람, 체크 셔츠와 슬리퍼, 그리고 그 뒤의 화분과 사람, 장소가 함께 맞아떨어진 순간이었다. ",
    "그래서 내 두 번째 이야기는 사진이다.",
]

TEXT = {  # 스토리 id: [(지금 글, 바꿀 글)]
    "u2f0": [("MOMENT", "PICTURE")],                                  # 큰 제목
    "u2c4": [("Template Systems ", "A Moment like A Photograph"),    # 부제 (커버 문구)
             ("Grid Systems Series", "")],
    "u348": [("Series", "Puddle")],                                   # 기차 사진 캡션 (웅덩이)
}
# 11쪽 아래 라벨: A 의 "I stop on the street. / (My first story is about style.)" 와 짝
LABEL_STORY = "u332"
LABEL = [("Bold", "I stop for a scene."), ("Regular", "(My second story is about pictures.)")]
LABEL_SIZE = 14

# 상자 위치 · 크기 (스프레드 좌표: 왼쪽, 위, 오른쪽, 아래). 2쪽 왼쪽 끝 x = -841.9, 3쪽 오른쪽 끝 x = 841.9
BOUNDS = {
    "u2d6": (-322.7, -173.3, 5.8, -152.0),   # 부제 → A 의 "A Person with Style" 자리
    "u32e": (319.2, 178.3, 606.7, 445.0),    # 여는 글 → 아래로 늘림 (글 9–10줄)
    "u344": (319.1, 459.0, 606.7, 495.0),    # 라벨 → 두 줄 들어가게 위로 늘림
    "u35a": (627.4, 141.0, 810.7, 158.3),    # 캡션 → 기차 사진 오른쪽, 사진 아래 끝에 맞춤
}
# 큰 제목: A 의 STYLE 상자와 같은 자리 · 크기 · 글자 크기(Helvetica Bold 136)
TITLE_FRAME, TITLE_STORY = "u302", "u2f0"
TITLE_TRANSFORM = "1.0000000000000002 0 0 1.0000000000000002 -338.8689572186265 -229.56478733926804"
TITLE_ANCHORS = [(-446.3278931750743, -265.4352126607319), (-446.3278931750743, -27.39366963402567),
                 (458.672106824926, -27.39366963402567), (458.672106824926, -265.4352126607319)]
TITLE_WIDTH, TITLE_SIZE = "905.0000000000002", "136.02373887240356"

PHOTO = "u35d"  # 기차 사진: 3pt 검은 테두리(StrokeWeight 3 + 객체 스타일의 검은 선)와 검은 채움을 뺀다

REMOVE = [  # (프레임 id, 스토리 id)
    ("u318", "u306"),  # LIKE A
    ("u294", "u282"),  # PHOTOGRAPH
    ("u2c0", "u2ae"),  # download now / www.template.systems
    ("u2ec", "u2da"),  # 잘린 download now (왼쪽 재단선 밖)
]


def story_path(sid):
    return f"Stories/Story_{sid}.xml"


def replace_content(xml_text, old, new):
    def sub(m):
        if html.unescape(m.group(1)) == old:
            sub.hits += 1
            return f"<Content>{html.escape(new, quote=False)}</Content>"
        return m.group(0)
    sub.hits = 0
    out = re.sub(r"<Content>(.*?)</Content>", sub, xml_text, flags=re.S)
    if sub.hits != 1:
        raise SystemExit(f"'{old}' 를 {sub.hits}번 찾음 (1번이어야 함)")
    return out


def set_attr(tag, name, value):
    if re.search(rf'\b{name}="[^"]*"', tag):
        return re.sub(rf'\b{name}="[^"]*"', f'{name}="{value}"', tag)
    return tag[:-1] + f' {name}="{value}">'


def frame_match(spread, tag, fid):
    m = re.search(rf'\n?[ \t]*<{tag} Self="{fid}" .*?</{tag}>', spread, re.S)
    if not m:
        raise SystemExit(f"{tag} {fid} 를 못 찾음")
    return m


def set_anchors(block, points):
    """상자의 네 꼭짓점(PathPointType 4개)을 바꾼다."""
    pts = list(re.finditer(r'<PathPointType Anchor="[^"]*" LeftDirection="[^"]*" RightDirection="[^"]*" />', block))
    if len(pts) != 4:
        raise SystemExit("꼭짓점이 4개가 아님")
    out, last = [], 0
    for m, (x, y) in zip(pts, points):
        v = f"{x!r} {y!r}"
        out.append(block[last:m.start()])
        out.append(f'<PathPointType Anchor="{v}" LeftDirection="{v}" RightDirection="{v}" />')
        last = m.end()
    return "".join(out) + block[last:]


def set_bounds(block, bounds):
    """스프레드 좌표 (왼, 위, 오른, 아래)로 상자를 옮긴다. ItemTransform 은 이동만 있는 상자여야 한다."""
    t = [float(v) for v in re.search(r'ItemTransform="([^"]*)"', block).group(1).split()]
    if abs(t[0] - 1) > 1e-9 or t[1] or t[2] or abs(t[3] - 1) > 1e-9:
        raise SystemExit("회전 · 크기 변환이 있는 상자")
    x0, y0, x1, y1 = bounds
    e, f = t[4], t[5]
    block = set_anchors(block, [(x0 - e, y0 - f), (x0 - e, y1 - f), (x1 - e, y1 - f), (x1 - e, y0 - f)])
    return re.sub(r'TextColumnFixedWidth="[^"]*"', f'TextColumnFixedWidth="{x1 - x0!r}"', block, count=1)


def remove_story(files, dm, sid):
    del files[story_path(sid)]
    n = len(dm)
    dm = dm.replace(f'\t<idPkg:Story src="{story_path(sid)}" />\n', "")
    if len(dm) == n:
        raise SystemExit(f"designmap 에서 {sid} 를 못 지움")
    return re.sub(r'(StoryList="[^"]*?)\b' + sid + r' ?', r"\1", dm)


def main(src, dst):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist()}
    text = lambda n: files[n].decode("utf-8")
    put = lambda n, t: files.__setitem__(n, t.encode("utf-8"))

    # D
    for sid in D_STORIES:
        t = text(story_path(sid))
        if f'FillColor="{D_TEXT_FROM}"' not in t:
            raise SystemExit(f"{sid} 에 흰 글자가 없음")
        put(story_path(sid), t.replace(f'FillColor="{D_TEXT_FROM}"', f'FillColor="{D_TEXT_TO}"'))

    # E — 글
    body = text(story_path("u31c"))
    for old, new in zip(OPENING_OLD, OPENING):
        body = replace_content(body, old, new)
    put(story_path("u31c"), body)

    for sid, pairs in TEXT.items():
        t = text(story_path(sid))
        for old, new in pairs:
            t = replace_content(t, old, new)
        put(story_path(sid), t)
    # 부제: 두 줄 → 한 줄, 오른쪽 맞춤 → 왼쪽 맞춤, A 의 부제와 같은 14pt
    t = text(story_path("u2c4"))
    t = re.sub(r"\s*<Content></Content>", "", t).replace("<Br />", "", 1)
    t = re.sub(r"<ParagraphStyleRange [^>]*>", lambda m: set_attr(m.group(0), "Justification", "LeftAlign"), t)
    t = re.sub(r"<CharacterStyleRange [^>]*>", lambda m: set_attr(m.group(0), "PointSize", "14"), t)
    put(story_path("u2c4"), t)
    # 캡션: 14pt (A 의 캡션과 같게), 사진 쪽으로 붙게 왼쪽 맞춤
    t = text(story_path("u348"))
    t = re.sub(r"<CharacterStyleRange [^>]*>", lambda m: set_attr(m.group(0), "PointSize", "14"), t)
    t = re.sub(r"<ParagraphStyleRange [^>]*>", lambda m: set_attr(m.group(0), "Justification", "LeftAlign"), t)
    put(story_path("u348"), t)
    # 큰 제목 글자 크기
    t = text(story_path(TITLE_STORY))
    put(story_path(TITLE_STORY), re.sub(r'(<CharacterStyleRange [^>]*?)PointSize="[^"]*"', rf'\1PointSize="{TITLE_SIZE}"', t))
    # 라벨 두 줄
    t = text(story_path(LABEL_STORY))
    m = re.search(r"(<CharacterStyleRange [^>]*>)(.*?)(</CharacterStyleRange>)", t, re.S)
    props = re.search(r"\s*<Properties>.*?</Properties>", m.group(2), re.S).group(0)
    runs = []
    for i, (style, line) in enumerate(LABEL):
        head = set_attr(set_attr(m.group(1), "FontStyle", style), "PointSize", str(LABEL_SIZE))
        br = "\n\t\t\t\t<Br />" if i < len(LABEL) - 1 else ""
        runs.append(f"{head}{props}\n\t\t\t\t<Content>{html.escape(line, quote=False)}</Content>{br}\n\t\t\t</CharacterStyleRange>")
    put(story_path(LABEL_STORY), t[: m.start()] + "\n\t\t\t".join(runs) + t[m.end():])

    # E — 상자
    s = text(SPREAD_E)
    blk = frame_match(s, "TextFrame", TITLE_FRAME).group(0)
    new = re.sub(r'ItemTransform="[^"]*"', f'ItemTransform="{TITLE_TRANSFORM}"', blk, count=1)
    new = set_anchors(new, TITLE_ANCHORS)
    new = re.sub(r'TextColumnFixedWidth="[^"]*"', f'TextColumnFixedWidth="{TITLE_WIDTH}"', new, count=1)
    s = s.replace(blk, new)

    for fid, b in BOUNDS.items():
        blk = frame_match(s, "TextFrame", fid).group(0)
        s = s.replace(blk, set_bounds(blk, b))

    m = re.search(rf'<Rectangle Self="{PHOTO}" [^>]*>', s)
    tag = set_attr(set_attr(set_attr(m.group(0), "FillColor", "Swatch/None"), "StrokeWeight", "0"), "StrokeColor", "Swatch/None")
    s = s[: m.start()] + tag + s[m.end():]

    dm = text("designmap.xml")
    for fid, sid in REMOVE:
        m = frame_match(s, "TextFrame", fid)
        if f'ParentStory="{sid}"' not in m.group(0):
            raise SystemExit(f"글 상자 {fid} 의 스토리가 {sid} 가 아님")
        s = s[: m.start()] + s[m.end():]
        dm = remove_story(files, dm, sid)
    put(SPREAD_E, s)
    put("designmap.xml", dm)

    for n, b in files.items():
        if n.endswith(".xml"):
            xml.dom.minidom.parseString(b)  # 깨진 XML 이면 여기서 멈춘다

    with zipfile.ZipFile(dst, "w") as zout:
        zout.writestr(zipfile.ZipInfo("mimetype"), files.pop("mimetype"), compress_type=zipfile.ZIP_STORED)
        for n in zin.namelist():
            if n in files:
                zout.writestr(n, files[n], compress_type=zipfile.ZIP_DEFLATED)
    print("ok", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
