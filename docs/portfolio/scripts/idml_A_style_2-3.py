"""v2 펼침 A (2–3쪽) · (001) STYLE — IDML 의 템플릿 글을 원고로 바꾼다.

원고: docs/portfolio/v2_01_style.md
쓰는 법: python3 idml_A_style_2-3.py 원본.idml 결과.idml
결과 IDML 을 InDesign 에서 열고 .indd 로 저장한다.

XML 은 문자열 그대로 고친다(InDesign 이 쓴 서식 · 속성을 건드리지 않으려고).
"""
import html
import re
import sys
import zipfile
import xml.dom.minidom

SPREAD = "Spreads/Spread_u45fc.xml"

# 스토리 id: [(지금 글, 바꿀 글)] — 글자 서식(굵기 · 크기)은 그대로
TEXT = {
    "u1af5": [("© 2026 Template.Systems", "Jeong Hyeokju")],
    "u1ac7": [("A Person With Style", "A Person with Style")],
    "u1a99": [("column grids ", "Sunglasses "),
              ("(multiple vertical columns)", "(on a wet street, at night)")],
    "u1ab0": [("modular grids", "I stop on the street."),
              ("(rows and columns forming modules)", "(My first story is about style.)")],
}

# 지울 글 상자: (프레임 id, 스토리 id)
REMOVE = [
    ("u1adb", "u1ade"),  # Grid Systems 001 — 3쪽에 큰 (001) 이 이미 있다
    ("u1a7f", "u1a82"),  # download now / www.template.systems
]

# 3쪽 본문: 영어 자리 글 → 한국어 여는 글
BODY_STORY, BODY_FRAME = "u1a3d", "u1a3a"
BODY_FONT, BODY_SIZE, BODY_LEADING = "AppleGothic", 13, 20.8
BODY = [
    "첫 번째로, 내가 멈추는 곳은 길 위다. 스타일이 좋은 사람이 지나가면 나는 걸음을 멈추곤 한다. "
    "어떤 머리를 했는지, 어떤 안경을 썼는지, 무슨 옷과 신발을 신었는지, 어떤 액세서리를 했는지. "
    "그리고 그 색들이 어떻게 어울리는지. 가끔은 그 사람이 지나간 뒤에 남은 향에 뒤를 돌아보기도 한다.",
    "그래서 내 첫 번째 이야기는 스타일이다.",
]
# 본문 상자 아래 끝을 큰 (001) 상자(위 끝 y=-357) 위로 올린다: 스프레드 좌표 -365 → 상자 안 좌표
BODY_BOTTOM_OLD, BODY_BOTTOM_NEW = "187.8333333333334", "16.16666666666663"


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


def rewrite_body(xml_text):
    m = re.search(r"(<CharacterStyleRange [^>]*>)(.*?)(</CharacterStyleRange>)", xml_text, re.S)
    head = m.group(1)
    head = re.sub(r'FontStyle="[^"]*"', 'FontStyle="Regular"', head)
    head = re.sub(r'PointSize="[^"]*"', f'PointSize="{BODY_SIZE}"', head)
    props = (
        "\n\t\t\t\t<Properties>"
        f'\n\t\t\t\t\t<AppliedFont type="string">{BODY_FONT}</AppliedFont>'
        f'\n\t\t\t\t\t<Leading type="unit">{BODY_LEADING}</Leading>'
        '\n\t\t\t\t\t<RubyFontStyle type="enumeration">Nothing</RubyFontStyle>'
        '\n\t\t\t\t\t<KentenFontStyle type="enumeration">Nothing</KentenFontStyle>'
        "\n\t\t\t\t</Properties>"
    )
    body = "\n\t\t\t\t<Br />".join(
        f"\n\t\t\t\t<Content>{html.escape(p, quote=False)}</Content>" for p in BODY
    )
    return xml_text[: m.start()] + head + props + body + "\n\t\t\t" + m.group(3) + xml_text[m.end():]


def main(src, dst):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist()}
    text = lambda n: files[n].decode("utf-8")

    for sid, pairs in TEXT.items():
        t = text(story_path(sid))
        for old, new in pairs:
            t = replace_content(t, old, new)
        files[story_path(sid)] = t.encode("utf-8")

    files[story_path(BODY_STORY)] = rewrite_body(text(story_path(BODY_STORY))).encode("utf-8")

    spread = text(SPREAD)
    for fid, sid in REMOVE:
        spread, n = re.subn(rf'\s*<TextFrame Self="{fid}" ParentStory="{sid}".*?</TextFrame>', "", spread, flags=re.S)
        if n != 1:
            raise SystemExit(f"글 상자 {fid} 를 {n}번 찾음")
        del files[story_path(sid)]
        dm = text("designmap.xml")
        dm = dm.replace(f'\t<idPkg:Story src="{story_path(sid)}" />\n', "")
        dm = re.sub(r'(StoryList="[^"]*?)\b' + sid + r' ?', r"\1", dm)
        files["designmap.xml"] = dm.encode("utf-8")

    frame = re.search(rf'<TextFrame Self="{BODY_FRAME}".*?</PathPointArray>', spread, re.S)
    fixed = frame.group(0).replace(f" {BODY_BOTTOM_OLD}", f" {BODY_BOTTOM_NEW}")
    if fixed.count(BODY_BOTTOM_NEW) != 6:
        raise SystemExit("본문 상자 아래 끝을 못 고침")
    spread = spread.replace(frame.group(0), fixed)
    files[SPREAD] = spread.encode("utf-8")

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
