"""v2 16–19쪽 (PICTURE 끝 두 펼침) — IDML 의 템플릿 글을 원고로 바꾸고, 빈 자리를 채운다.

  16–17  Q2 · What makes a good picture?   (바다 사진)
  18–19  다리 ② PICTURE → ARCHITECTURE    (그릴 · 미술관 사진, 큰 글자 한 줄)

원본: 지원자가 보낸 "포트폴리오 16-19.idml" (IDML 안에서는 쪽 이름이 2–5 로 나온다)
원고: docs/portfolio/v2_picture_16-19.md
쓰는 법: python3 idml_picture_16-19.py 원본.idml 결과.idml
결과 IDML 을 InDesign 에서 열고 .indd 로 저장한다.

독립: 이 두 펼침과 그 스토리만 고친다. 표지 펼침 · 마스터 · 다른 파일은 그대로 둔다.
고치기 전에 상자마다 원래 글이 맞는지 확인하고, 다르면 아무것도 쓰지 않고 멈춘다.
XML 은 문자열 그대로 고친다(InDesign 이 쓴 서식 · 속성을 건드리지 않으려고).
"""
import html
import re
import sys
import zipfile
import xml.dom.minidom

SPREAD_Q2 = "Spreads/Spread_u3aa8.xml"      # 16–17
SPREAD_BRIDGE = "Spreads/Spread_u3aba.xml"  # 18–19

KO = {"font": "AppleGothic", "style": "Regular", "size": 13, "leading": 20.8}   # A 3쪽 본문과 같다
EN_BODY = {"font": "Helvetica Neue", "style": "Regular", "size": 13, "leading": 20.8}
EN_HEAD = {"font": "Helvetica Neue", "style": "Bold", "size": 16, "leading": 20.8}
ACCENT = "Color/Magenta"  # 8–9쪽 풀쿼트의 강조색

# 스토리 id → (원래 글의 앞부분, 새 단락들). 단락 = [(글, 서식)] — 서식이 None 이면 그 스토리의 원래 서식
STORIES = {
    # 16 왼쪽 위: © 2026 Template.Systems → 머리말 (v1 PICTURE 의 머리말 짝 PICTURE / MOMENT)
    "u3a49": ("© 2026 Template.Systems", [[("PICTURE", None)]]),
    # 17 오른쪽 위: Grid Exploration 003 → 머리말
    "u39a5": ("Grid Exploration 003", [[("MOMENT", None)]]),
    # 16 본문: Q2 질문 + 답 두 가지
    "u3a18": ("A grid system is", [
        [("What makes a good picture?", EN_HEAD)],
        [("첫째, 오래 보게 되는 사진이다. 한 번 보고 넘기지 않고, 계속 들여다보게 되는 것.", KO)],
        [("둘째, 하나의 이야기가 되는 사진이다. 사람, 빛, 색, 장소가 서로 어울려 한 장면이 되는 것.", KO)],
    ]),
    # 17 본문: Q2 마무리 + 영어 한 줄
    "u3a2f": ("A grid system is", [
        [("좋은 사진은 좋은 스타일, 좋은 공간과 같다. 멈추게 하고, 다시 떠오르게 한다.", KO)],
        [("A good picture is like good style and a good space: it makes me stop, and it comes back to me.", EN_BODY)],
    ]),
    # 16 아래 download now 상자 → 바다 사진 캡션 (상자는 사진 아래로 옮긴다)
    "u39bc": ("download now", [[("Sea", None)], [("(September, 5:37 pm)", None)]]),
    # 18 왼쪽 위: Grid Exploration 001 → 머리말. PICTURE 의 MOMENT 에서 ARCHITECTURE 의 PLACE 로 넘어간다
    # (화살표는 Helvetica Neue 에 글리프가 없을 수 있어 / 로 쓴다)
    "u3c33": ("Grid Exploration 001", [[("MOMENT / PLACE", None)]]),
    # 18 본문: 다리 글
    "u3c4a": ("A grid system is", [
        [("좋은 사진을 다시 보면, 늘 그 뒤에 좋은 장소가 있었다. 사람이 멈춘 자리에는 언제나 그 사람을 붙잡아 둔 공간이 있었다.", KO)],
    ]),
    # 18 그릴 사진 캡션
    "u3c05": ("manuscript grids", [[("Smoke", None)], [("(September, 5:22 pm)", None)]]),
    # 19 큰 글자: 다리 한 줄 (D 의 풀쿼트처럼 두 단어를 강조색으로)
    "u3be9": ("A grid system is", [
        [("Every good picture had a ", None), ("good place", {"fill": ACCENT}), (" behind it.", None)],
    ]),
    # 19 미술관 사진 캡션
    "u3c1c": ("column grids", [[("Gathering", None)], [("(June, 3:53 pm)", None)]]),
}

# 지울 글 상자: (펼침, 프레임 id, 스토리 id, 원래 글)
REMOVE = [
    (SPREAD_Q2, "u3a8c", "u3a8f", "(003)"),                          # ARCHITECTURE 번호 — PICTURE 지면에 있으면 안 된다
    (SPREAD_Q2, "u39e7", "u39ea", "Experimental Grid Exploration"),
    (SPREAD_Q2, "u39fe", "u3a01", "Series"),
]

# 상자 자리 (펼침 좌표: 왼쪽 · 위 · 오른쪽 · 아래, pt). 펼침 = 왼쪽 쪽 x -841.9–0, 오른쪽 쪽 x 0–841.9, y -595.3–595.3
MOVE = [
    # 캡션: 바다 사진(x -298–298, 아래 끝 y 158) 아래 8pt, 16쪽 안에서
    (SPREAD_Q2, "u39b9", (-298.0, 166.0, -9.0, 201.0)),
    # 18 머리말: 137pt 폭에 MOMENT / PLACE 가 빠듯하다 — 본문 상자(-579) 앞까지 넓힌다
    (SPREAD_BRIDGE, "u3c30", (-810.7086614173229, -495.0, -600.0, -481.3501281738272)),
    # 18 그릴 캡션: 접힘을 넘어 19쪽 캡션 상자와 겹치던 것을 18쪽 안(-30)으로
    (SPREAD_BRIDGE, "u3c02", (-402.18503937007813, 464.55012817382624, -30.0, 494.9999999999978)),
    # 19 큰 글자: 오른쪽 재단선(841.9) 밖 915 까지 나가 있던 것을 다른 상자와 같은 여백(811)으로
    (SPREAD_BRIDGE, "u3be5", (10.0, 193.0, 811.0, 330.0)),
]


def story_path(sid):
    return f"Stories/Story_{sid}.xml"


def story_text(xml_text):
    return "".join(html.unescape(m.group(1)) if m.group(1) is not None else "\n"
                   for m in re.finditer(r"<Content>(.*?)</Content>|<Br\s*/>", xml_text, re.S))


def char_head(head, props, fmt):
    """원래 글자 범위의 머리 · 속성에 fmt 를 덧씌운다."""
    if not fmt:
        return head, props
    def attr(h, name, val):
        if f' {name}="' in h:
            return re.sub(rf' {name}="[^"]*"', f' {name}="{val}"', h)
        return h[:-1] + f' {name}="{val}">'
    if "style" in fmt:
        head = attr(head, "FontStyle", fmt["style"])
    if "size" in fmt:
        head = attr(head, "PointSize", fmt["size"])
    if "fill" in fmt:
        head = attr(head, "FillColor", fmt["fill"])
    if "font" in fmt:
        props = re.sub(r'<AppliedFont type="string">[^<]*</AppliedFont>',
                       f'<AppliedFont type="string">{fmt["font"]}</AppliedFont>', props)
    if "leading" in fmt:
        if "<Leading " in props:
            props = re.sub(r'<Leading type="unit">[^<]*</Leading>', f'<Leading type="unit">{fmt["leading"]}</Leading>', props)
        else:
            props = props.replace("<Properties>", f'<Properties>\n\t\t\t\t\t<Leading type="unit">{fmt["leading"]}</Leading>', 1)
    return head, props


def rewrite_story(xml_text, paragraphs):
    """스토리 글을 paragraphs 로 바꾼다. 단락 i 는 원래 i 번째 줄의 글자 서식(없으면 마지막 줄)에서 출발한다."""
    psr = re.search(r"(<ParagraphStyleRange[^>]*>\s*(?:<Properties>.*?</Properties>)?)(.*?)(</ParagraphStyleRange>)", xml_text, re.S)
    lines, new_line = [], True  # 원래 줄마다 첫 글자 범위의 (머리, 속성)
    for cm in re.finditer(r"(<CharacterStyleRange[^>]*>)(\s*<Properties>.*?</Properties>)?(.*?)</CharacterStyleRange>", psr.group(2), re.S):
        for tok in re.finditer(r"<Content>.*?</Content>|<Br\s*/>", cm.group(3), re.S):
            if tok.group(0).startswith("<Br"):
                new_line = True
            elif new_line:
                lines.append((cm.group(1), cm.group(2) or ""))
                new_line = False
    if not lines:
        raise SystemExit("글이 없는 스토리")
    out = []
    for i, runs in enumerate(paragraphs):
        base = lines[min(i, len(lines) - 1)]
        for j, (txt, fmt) in enumerate(runs):
            head, props = char_head(base[0], base[1], fmt)
            br = "\n\t\t\t\t<Br />" if (i < len(paragraphs) - 1 and j == len(runs) - 1) else ""
            out.append(f"\n\t\t\t{head}{props}\n\t\t\t\t<Content>{html.escape(txt, quote=False)}</Content>{br}\n\t\t\t</CharacterStyleRange>")
    return xml_text[:psr.start(2)] + "".join(out) + "\n\t\t" + xml_text[psr.start(3):]


def element_span(xml_text, tag, sid):
    m = re.search(rf'<{tag} Self="{sid}"[^>]*>', xml_text)
    if not m:
        raise SystemExit(f"{tag} {sid} 가 없다")
    depth, pos = 1, m.end()
    pat = re.compile(rf"<{tag}\b[^>]*?(/?)>|</{tag}>")
    while depth:
        n = pat.search(xml_text, pos)
        depth += -1 if n.group(0).startswith("</") else (0 if n.group(1) == "/" else 1)
        pos = n.end()
    return m.start(), pos


def set_box(frame_xml, box):
    x0, y0, x1, y1 = box
    frame_xml = re.sub(r'ItemTransform="[^"]*"', 'ItemTransform="1 0 0 1 0 0"', frame_xml, count=1)
    corners = iter([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])

    def pt(_):
        x, y = next(corners)
        a = f"{x:g} {y:g}"
        return f'<PathPointType Anchor="{a}" LeftDirection="{a}" RightDirection="{a}" />'
    frame_xml, n = re.subn(r"<PathPointType [^>]*/>", pt, frame_xml)
    if n != 4:
        raise SystemExit(f"사각형이 아닌 상자 (점 {n}개)")
    return re.sub(r'TextColumnFixedWidth="[^"]*"', f'TextColumnFixedWidth="{x1 - x0:g}"', frame_xml)


def main(src, dst):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist()}
    text = lambda n: files[n].decode("utf-8")

    # 먼저 전부 확인한다 — 하나라도 다르면 아무것도 쓰지 않는다
    for sid, (old, _) in STORIES.items():
        got = story_text(text(story_path(sid)))
        if not got.startswith(old):
            raise SystemExit(f"스토리 {sid}: '{old}…' 가 아니라 '{got[:30]}…' — 다른 IDML 이다")
    for sp, fid, sid, old in REMOVE:
        if story_text(text(story_path(sid))) != old or f'<TextFrame Self="{fid}" ParentStory="{sid}"' not in text(sp):
            raise SystemExit(f"지울 상자 {fid} ({old}) 를 못 찾음")

    for sid, (_, paragraphs) in STORIES.items():
        files[story_path(sid)] = rewrite_story(text(story_path(sid)), paragraphs).encode("utf-8")
        print("바꿈", sid, "→", " / ".join("".join(t for t, _ in p) for p in paragraphs)[:70])

    spreads = {SPREAD_Q2: text(SPREAD_Q2), SPREAD_BRIDGE: text(SPREAD_BRIDGE)}
    dm = text("designmap.xml")
    for sp, fid, sid, old in REMOVE:
        a, b = element_span(spreads[sp], "TextFrame", fid)
        spreads[sp] = spreads[sp][:a] + spreads[sp][b:]
        del files[story_path(sid)]
        dm = dm.replace(f'\t<idPkg:Story src="{story_path(sid)}" />\n', "")
        dm = re.sub(rf'(StoryList="[^"]*?)(?<!\w){sid}(?!\w) ?', r"\1", dm)
        print("지움", fid, old)
    for sp, fid, box in MOVE:
        a, b = element_span(spreads[sp], "TextFrame", fid)
        spreads[sp] = spreads[sp][:a] + set_box(spreads[sp][a:b], box) + spreads[sp][b:]
        print("옮김", fid, box)
    for sp, t in spreads.items():
        files[sp] = t.encode("utf-8")
    files["designmap.xml"] = dm.encode("utf-8")

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
