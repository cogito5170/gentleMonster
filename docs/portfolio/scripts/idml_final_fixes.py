"""최종 검토에서 나온 확실한 오류만 IDML 에 고친다 (레이아웃 · 판단이 필요한 것은 건드리지 않는다).

쓰는 법: python3 idml_final_fixes.py 원본.idml 결과.idml
검토 내용: docs/portfolio/v2_final_review.md
"""
import html
import re
import sys
import zipfile
import xml.dom.minidom

# 스토리 id: [(지금 Content, 바꿀 Content)] — Content 한 조각씩, 글자 서식은 그대로
RUNS = {
    # 5쪽 — 남은 템플릿 글 → 두 화면 설명 (원고 v2_01_style.md C)
    "u222d": [("Grid systems are widely used in graphic design, web design, and user interface (UI) design. "
               "In print, grids help maintain alignment across pages, while in digital products they ensure "
               "layouts adapt smoothly to different screen sizes.",
               ["MAIN — Today's looks, five style categories, users' daily outfits and sale picks.",
                "MARKET — Filter by color, fit, length, pattern and material; the matching pieces line up in a three-column grid."])],
    # 5쪽 — 남은 템플릿 라벨 두 개
    "u21ff": [("manuscript grids", "Web design"),
              ("(single-column layouts)", "(University project · Photoshop + Illustrator)")],
    "u2216": [("manuscript grids", "MARKET"),
              ("(single-column layouts)", "(product list · filter by color, fit, length, pattern, material)")],
    # 5쪽 — 작은 화면은 MAIN(메인 화면)
    "u4728": [("MARKET ", "MAIN")],
    # 8쪽 — 3쪽 "A good space starts the same way." 와 겹치는 끝 문장
    "u3813": [("With a camera in hand, I notice what I usually walk past: the color of a wall, the direction of the light, "
               "where people stand. As I shoot, I keep watching, and even an ordinary street starts to tell a story. "
               "Making a space works the same way. A good space starts with seeing where the light comes in and where people will stand.",
               "With a camera in hand, I notice what I usually walk past: the color of a wall, the direction of the light, "
               "where people stand. As I shoot, I keep watching, and even an ordinary street starts to tell a story. "
               "Making a space works the same way: I begin by looking at where the light comes in and where people will stand.")],
    # 캡션 첫 글자 대문자로 통일 (지원자 지면 Bulbs · Sprout 형식)
    "u3876": [("color", "Color")],
    "u3c05": [("smoke", "Smoke")],

    "u3c1c": [("curve ", "Curve")],
    # 23쪽 — 오타 · 띄어쓰기
    "u4065": [("(concept model · see p. 20) ", "(concept model · see p. 20)"),
              ("02–03 House interiors ", "02–03 House interiors"),
              ("annex projcect ", "annex project "),
              ("p", "p. "),
              (".18", "18"),
              (" ", "")],
}


def fix_story(text, pairs, sid):
    for old, new in pairs:
        target = f"<Content>{html.escape(old, quote=False)}</Content>"
        if text.count(target) != 1:
            raise SystemExit(f"{sid}: '{old}' 를 {text.count(target)}번 찾음 (1번이어야 함)")
        if isinstance(new, list):
            indent = re.search(r"\n(\t*)" + re.escape(target), text).group(1)
            repl = f"\n{indent}<Br />\n{indent}".join(
                f"<Content>{html.escape(p, quote=False)}</Content>" for p in new)
        else:
            repl = f"<Content>{html.escape(new, quote=False)}</Content>" if new else ""
        text = text.replace(target, repl)
    return text


def main(src, dst):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist()}
    for sid, pairs in RUNS.items():
        path = f"Stories/Story_{sid}.xml"
        files[path] = fix_story(files[path].decode("utf-8"), pairs, sid).encode("utf-8")
        xml.dom.minidom.parseString(files[path])
    with zipfile.ZipFile(dst, "w") as zout:
        zout.writestr(zipfile.ZipInfo("mimetype"), files["mimetype"], compress_type=zipfile.ZIP_STORED)
        for n in zin.namelist():
            if n != "mimetype":
                zout.writestr(n, files[n], compress_type=zipfile.ZIP_DEFLATED)
    print("ok", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
