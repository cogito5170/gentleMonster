"""포트폴리오 8-11 — 파일의 8–9쪽(바다 사진 펼침) · 10–11쪽(Q2 What makes a good picture?)
템플릿 글을 원고로 바꾼다.

원고: docs/portfolio/v2_02_picture.md (G · H) — 펼침 지도의 G(Q2) · H(사진만)에 해당한다.
쓰는 법: python3 idml_picture_8-11.py 원본.idml 결과.idml
결과 IDML 을 InDesign 에서 열고 .indd 로 저장한다. 이 파일 하나로 돌고 다른 스크립트가 필요 없다.

XML 은 문자열 그대로 고친다(InDesign 이 쓴 서식 · 속성을 건드리지 않으려고).
8–11쪽 밖의 펼침은 건드리지 않는다.
"""
import html
import re
import sys
import zipfile
import xml.dom.minidom

SPREAD_89 = "Spreads/Spread_u37ea.xml"    # 8–9쪽: 바다 사진 한 장이 펼침 전체
SPREAD_1011 = "Spreads/Spread_u3aa8.xml"  # 10–11쪽: Q2 + 가운데 바다 사진

KO_FONT, KO_SIZE, KO_LEADING = "본고딕 KR", 16, 30   # 6쪽 "카메라를 들면…" 과 같은 글꼴 · 크기
EN_FONT, EN_SIZE = "Helvetica Neue", 16              # 이 문서 라벨 · 머리말과 같은 글꼴 · 크기

# 본문 상자: 스토리 id → [(글꼴, 굵기, 글)] 문단 목록
BODY = {
    # 10쪽 왼쪽 위
    "u3a18": [
        (EN_FONT, "Bold", "What makes a good picture?"),
        (KO_FONT, "Regular", "첫째, 오래 보게 되는 사진이다. 한 번 보고 넘기지 않고, 계속 들여다보게 되는 것."),
        (KO_FONT, "Regular", "둘째, 하나의 이야기가 되는 사진이다. 사람, 빛, 색, 장소가 서로 어울려 한 장면이 되는 것."),
    ],
    # 11쪽 오른쪽 위 — 02_picture.md 의 "사진은 왜 중요한가" 답을 Q2 의 마무리로 이었다
    "u3a2f": [
        (KO_FONT, "Regular", "사람은 쉽게 잊는다. 좋았던 장소도, 그날의 빛도 시간이 지나면 흐려진다. "
                             "좋은 사진은 그 순간으로 나를 다시 데려다 놓는다. "
                             "사진 한 장을 보면 그날의 날씨, 소리, 냄새까지 같이 떠오른다."),
        (KO_FONT, "Regular", "좋은 사진은 좋은 스타일, 좋은 공간과 같다. 멈추게 하고, 다시 떠오르게 한다."),
    ],
}
# 두 본문 상자를 위아래로 늘린다(상자 안 좌표). 스프레드 좌표로 위 -326.7 → -365, 아래 -178.3 → -170
BODY_FRAMES = {"u3a15": "u3a18", "u3a2c": "u3a2f"}
BODY_TOP_OLD, BODY_TOP_NEW = "-113.83333333333312", "-152.16666666666663"
BODY_BOTTOM_OLD, BODY_BOTTOM_NEW = "34.50000000000008", "42.83333333333337"

# 한 줄 글: 스토리 id → [(지금 글, 바꿀 글)]
TEXT = {
    "u3a49": [("© 2026 Template.Systems", "PICTURE")],   # 10쪽 머리말
    "u39a5": [("Grid Exploration 003", "MOMENT")],       # 11쪽 머리말 (STYLE 의 MOOD 와 짝)
    "u3a8f": [("(003)", "Two")],                          # 10–11 바다 사진 캡션 (두 사람)
    "u39ea": [("Experimental Grid Exploration", "Dusk")], # 8쪽 캡션 (노을)
    "u3a01": [("Series", "Lights")],                      # 9쪽 캡션 (불빛)
}

# 상자 옮기기: 프레임 id → (지금 ItemTransform, 바꿀 ItemTransform)
MOVE = {
    # (003) → 바다 사진 왼쪽 아래 끝 바로 밑 (사진 상자 왼쪽 x -298.3, 아래 y 158.3)
    "u3a8c": ("1 0 0 1 -38.53149606299212 614.1752059498831", "1 0 0 1 -88.83333333333331 302.57513270769596"),
    # 8쪽 캡션: 왼쪽 아래 바깥 구석 (여백 안)
    "u39e7": ("1 0 0 1 424.2919947506557 643.975279192071", "1 0 0 1 -601.2086614173229 643.975279192071"),
}
# 10–11 펼침에서 8–9 펼침으로 옮길 상자 (사진 위 캡션)
TO_89 = ["u39e7", "u39fe"]
# 사진 위에 놓이는 캡션은 흰 글자, 9쪽 캡션은 오른쪽 맞춤 / 11쪽 머리말도 오른쪽 맞춤
PAPER = ["u39ea", "u3a01"]
RIGHT_ALIGN = ["u3a01", "u39a5"]

# 지울 글 상자: (프레임 id, 스토리 id)
REMOVE = [("u39b9", "u39bc")]  # download now / www.template.systems


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


def rewrite_body(xml_text, paragraphs):
    """스토리의 문단 범위 하나를 문단 목록으로 바꾼다. 문단 속성(정렬 등)은 그대로."""
    m = re.search(r"(<ParagraphStyleRange [^>]*>)(.*)(</ParagraphStyleRange>)", xml_text, re.S)
    char = re.search(r"<CharacterStyleRange [^>]*>", m.group(2)).group(0)
    runs = []
    for i, (font, style, text) in enumerate(paragraphs):
        head = set_attr(set_attr(char, "FontStyle", style), "PointSize", str(KO_SIZE if font == KO_FONT else EN_SIZE))
        lang = "$ID/Korean" if font == KO_FONT else "$ID/English: USA"
        head = set_attr(head, "AppliedLanguage", lang)
        br = "\n\t\t\t\t<Br />" if i < len(paragraphs) - 1 else ""
        runs.append(
            f"\n\t\t\t{head}"
            "\n\t\t\t\t<Properties>"
            f'\n\t\t\t\t\t<Leading type="unit">{KO_LEADING}</Leading>'
            f'\n\t\t\t\t\t<AppliedFont type="string">{font}</AppliedFont>'
            "\n\t\t\t\t</Properties>"
            f"\n\t\t\t\t<Content>{html.escape(text, quote=False)}</Content>{br}"
            "\n\t\t\t</CharacterStyleRange>"
        )
    return xml_text[: m.start()] + m.group(1) + "".join(runs) + "\n\t\t" + m.group(3) + xml_text[m.end():]


def frame_block(spread, fid):
    m = re.search(rf'\n?\s*<TextFrame Self="{fid}" .*?</TextFrame>', spread, re.S)
    if not m:
        raise SystemExit(f"글 상자 {fid} 를 못 찾음")
    return m


def main(src, dst):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist()}
    text = lambda n: files[n].decode("utf-8")
    put = lambda n, t: files.__setitem__(n, t.encode("utf-8"))

    for sid, pars in BODY.items():
        put(story_path(sid), rewrite_body(text(story_path(sid)), pars))

    for sid, pairs in TEXT.items():
        t = text(story_path(sid))
        for old, new in pairs:
            t = replace_content(t, old, new)
        if sid in PAPER:
            t = re.sub(r"<CharacterStyleRange [^>]*>", lambda m: set_attr(m.group(0), "FillColor", "Color/Paper"), t)
        if sid in RIGHT_ALIGN:
            t = re.sub(r"<ParagraphStyleRange [^>]*>", lambda m: set_attr(m.group(0), "Justification", "RightAlign"), t)
        put(story_path(sid), t)

    s1011 = text(SPREAD_1011)
    s89 = text(SPREAD_89)

    for fid in BODY_FRAMES:
        blk = frame_block(s1011, fid).group(0)
        new = blk.replace(BODY_TOP_OLD, BODY_TOP_NEW).replace(BODY_BOTTOM_OLD, BODY_BOTTOM_NEW)
        if new.count(BODY_TOP_NEW) != 6 or new.count(BODY_BOTTOM_NEW) != 6:
            raise SystemExit(f"본문 상자 {fid} 높이를 못 고침")
        s1011 = s1011.replace(blk, new)

    for fid, (old, new) in MOVE.items():
        blk = frame_block(s1011, fid).group(0)
        if blk.count(f'ItemTransform="{old}"') != 1:
            raise SystemExit(f"글 상자 {fid} 위치를 못 찾음")
        s1011 = s1011.replace(blk, blk.replace(f'ItemTransform="{old}"', f'ItemTransform="{new}"', 1))

    moved = []
    for fid in TO_89:
        m = frame_block(s1011, fid)
        moved.append(m.group(0).strip("\n"))
        s1011 = s1011[: m.start()] + s1011[m.end():]
    end = s89.rindex("\t</Spread>")
    s89 = s89[:end] + "\n".join(moved) + "\n" + s89[end:]  # 사진 위에 놓이도록 맨 뒤(맨 앞 층)에 붙인다

    dm = text("designmap.xml")
    for fid, sid in REMOVE:
        m = frame_block(s1011, fid)
        if f'ParentStory="{sid}"' not in m.group(0):
            raise SystemExit(f"글 상자 {fid} 의 스토리가 {sid} 가 아님")
        s1011 = s1011[: m.start()] + s1011[m.end():]
        del files[story_path(sid)]
        n_before = len(dm)
        dm = dm.replace(f'\t<idPkg:Story src="{story_path(sid)}" />\n', "")
        if len(dm) == n_before:
            raise SystemExit(f"designmap 에서 {sid} 를 못 지움")
        dm = re.sub(r'(StoryList="[^"]*?)\b' + sid + r' ?', r"\1", dm)
    put("designmap.xml", dm)
    put(SPREAD_1011, s1011)
    put(SPREAD_89, s89)

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
