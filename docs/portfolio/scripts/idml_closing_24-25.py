"""마지막 장(24–25) — 지원자 IDML 에 v2_04_closing.md 청사진을 넣는다.

쓰는 법: python3 idml_closing_24-25.py 마지막페이지.idml 결과.idml
- 사진을 오른쪽으로 40pt 옮긴다 (차가 접힘에서 떨어지게).
- 글 상자 네 개를 새로 만든다. 글 상자 틀과 글자 서식은 표지(1쪽)의 질문 · 이름 · 문구 상자를 그대로 복제한다.
"""
import html
import re
import sys
import zipfile
import xml.dom.minidom

SPREAD = "Spreads/Spread_u431d.xml"
PHOTO, PHOTO_SHIFT = "u4a15", 40.0
TEMPLATE_FRAME = ("Spreads/Spread_u145.xml", "u4ff")  # 표지 질문 상자
TEMPLATE_STORY = "Stories/Story_u502.xml"


def run(text, font, style, size, scale=None, leading=None):
    attrs = f'FontStyle="{style}" PointSize="{size}"' + (f' HorizontalScale="{scale}"' if scale else "")
    props = (f'\n\t\t\t\t\t<Leading type="unit">{leading}</Leading>' if leading else "") + \
        f'\n\t\t\t\t\t<AppliedFont type="string">{font}</AppliedFont>'
    body = "\n\t\t\t\t<Br />".join(f"\n\t\t\t\t<Content>{html.escape(t, quote=False)}</Content>" if t else "" for t in text)
    return (f'\n\t\t\t<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" {attrs}>'
            f"\n\t\t\t\t<Properties>{props}\n\t\t\t\t</Properties>{body}\n\t\t\t</CharacterStyleRange>")


def para(align, *runs):
    return (f'\n\t\t<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle" '
            f'Justification="{align}">' + "".join(runs) + "\n\t\t</ParagraphStyleRange>")


# (frame id, story id, x0, y0, x1, y1 — 펼침 좌표 pt, 접힘 = x 0, 쪽 가운데 = y 0, 글)
FRAMES = [
    ("uc0f1", "uc0e1", -670, 402, -330, 442,   # 캡션: 사진 왼쪽 아래
     para("LeftAlign",
          run(["Stop"], "Helvetica Neue", "Bold", 16),
          run(["", "(an empty lot, after the rain)"], "Helvetica Neue", "Regular", 16))),
    ("uc0f2", "uc0e2", -811, 527, -386, 564,   # 닫는 문장: 표지 문구 서식
     para("LeftAlign",
          run(["People shape spaces, and spaces shape people back.",
               "I design the moment in between, when someone stops."], "Anth", "Italic", 16, 105, 21))),
    ("uc0f3", "uc0e3", 399.685, 431.133, 810.709, 454.963,   # 질문: 표지와 같은 자리 · 서식
     para("RightAlign",
          run(["“Where Did You Last Stop?”"], "Oriya Sangam MN", "Bold", 21, 107, 20))),
    ("uc0f4", "uc0e4", 606, 552, 811, 564,     # 이름: 표지 이름 서식
     para("RightAlign",
          run(["Jeong Hyeokju"], "Oriya Sangam MN", "Regular", 11, 118, 12))),
]


def make_frame(template, fid, sid, x0, y0, x1, y1):
    f = template.replace('Self="u4ff"', f'Self="{fid}"', 1).replace('ParentStory="u502"', f'ParentStory="{sid}"', 1)
    f = re.sub(r'ItemTransform="[^"]*"', 'ItemTransform="1 0 0 1 0 0"', f, count=1)
    pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
    anchors = iter(pts)
    f = re.sub(r'<PathPointType [^>]*/>',
               lambda m: (lambda p: f'<PathPointType Anchor="{p[0]} {p[1]}" LeftDirection="{p[0]} {p[1]}" '
                                    f'RightDirection="{p[0]} {p[1]}" />')(next(anchors)), f)
    return re.sub(r'TextColumnFixedWidth="[^"]*"', f'TextColumnFixedWidth="{x1 - x0}"', f)


def make_story(template, sid, body):
    s = template.replace('Self="u502"', f'Self="{sid}"', 1)
    a = s.index("<ParagraphStyleRange")
    b = s.rindex("</ParagraphStyleRange>") + len("</ParagraphStyleRange>")
    return s[:a].rstrip("\t") + body.lstrip("\n") + s[b:]


def main(src, dst):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist()}
    t = lambda n: files[n].decode("utf-8")

    everything = "".join(t(n) for n in files if n.endswith(".xml"))
    for fid, sid, *_ in FRAMES:
        assert f'"{fid}"' not in everything and f'"{sid}"' not in everything, f"id {fid}/{sid} 이미 있음"

    tframe = re.search(r'<TextFrame Self="u4ff".*?</TextFrame>', t(TEMPLATE_FRAME[0]), re.S).group(0)
    tstory = t(TEMPLATE_STORY)

    spread = t(SPREAD)
    # 사진 오른쪽으로
    m = re.search(rf'(<Rectangle Self="{PHOTO}"[^>]*ItemTransform=")([^"]*)(")', spread)
    a, b, c, d, tx, ty = map(float, m.group(2).split())
    spread = spread[:m.start(2)] + f"{a:g} {b:g} {c:g} {d:g} {tx + PHOTO_SHIFT} {ty}" + spread[m.end(2):]
    # 글 상자 넣기 (사진 위)
    new = "".join("\n\t\t" + make_frame(tframe, fid, sid, x0, y0, x1, y1) for fid, sid, x0, y0, x1, y1, _ in FRAMES)
    i = spread.rindex("</Spread>")
    spread = spread[:i].rstrip() + new + "\n\t" + spread[i:]
    files[SPREAD] = spread.encode("utf-8")

    dm = t("designmap.xml")
    for fid, sid, *_, body in FRAMES:
        path = f"Stories/Story_{sid}.xml"
        files[path] = make_story(tstory, sid, body).encode("utf-8")
        dm = dm.replace('StoryList="', f'StoryList="{sid} ', 1)
        dm = dm.replace('\t<idPkg:Story src="Stories/Story_u502.xml" />',
                        f'\t<idPkg:Story src="{path}" />\n\t<idPkg:Story src="Stories/Story_u502.xml" />', 1)
    files["designmap.xml"] = dm.encode("utf-8")

    for n, b in files.items():
        if n.endswith(".xml"):
            xml.dom.minidom.parseString(b)

    order = zin.namelist() + [n for n in files if n not in zin.namelist()]
    with zipfile.ZipFile(dst, "w") as zout:
        zout.writestr(zipfile.ZipInfo("mimetype"), files["mimetype"], compress_type=zipfile.ZIP_STORED)
        for n in order:
            if n != "mimetype":
                zout.writestr(n, files[n], compress_type=zipfile.ZIP_DEFLATED)
    print("ok", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
