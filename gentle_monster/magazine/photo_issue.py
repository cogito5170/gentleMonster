"""Photo issue: a magazine built around the user's own photographs, in the grammar of a museum magazine
(the MCA Magazine reference board: stencil masthead, one strong cover photograph, a numbered contents page, a
gallery wall, one-word pages, a collage with an index, a rotated manifesto, a full-bleed spread, a back cover with
a framed text box) and read through Gentle Monster (research/sources.json).

    python3 -m gentle_monster photo-issue editorial/issues/spa_00_stops.json --name spa00

The issue spec holds the editorial decisions (which photo goes where, which words); the texts in it are the
user's own, copied verbatim from docs/portfolio/ -- check_texts() proves each one is still there. This module
measures the photos (light, colour, brightness), orders and labels them, lays the pages out, prints the PDF and
runs QA. It writes no prose with a model (no Gemini, no other model).

One layout, two sizes: every length on a page is in container units (cqw), so the 230 x 300 mm print page and
the screen page are the same composition. Text-heavy pages reflow on phones.
"""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

from gentle_monster import paths, photos as PH
from gentle_monster.magazine import assets as A, catalogue as CAT, pdf as PDF, qa as QA, render as R

e = lambda s: html.escape(str(s if s is not None else ""))
W_MM, H_MM = 230, 300
PRINT_DPI_MIN = 150          # below this a photograph prints visibly soft


def load(spec_path) -> dict:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    spec["_path"] = str(spec_path)
    return spec


def check_texts(spec: dict) -> list[str]:
    """Every user text in the spec must still be, word for word, in the document it came from."""
    bad = []
    doc = lambda p: (paths.REPO / p).read_text(encoding="utf-8") if (paths.REPO / p).is_file() else ""
    c = spec["cover"]
    for t in c["left"] + c["right"] + c["byline"] + [c["question"]]:
        if t not in doc(c["source"]):
            bad.append(f"cover: '{t}' not in {c['source']}")
    for t in spec["intro"]["ko"] + [spec["intro"]["en"]]:
        if t not in doc(spec["intro"]["source"]):
            bad.append(f"intro: '{t[:30]}' not in {spec['intro']['source']}")
    if spec["manifesto"]["check"] not in doc(spec["manifesto"]["source"]):
        bad.append("manifesto not in its source")
    if " ".join(spec["manifesto"]["lines"]) != spec["manifesto"]["check"]:
        bad.append("manifesto lines do not add up to the checked sentence")
    for b in spec["qa_text"]:
        for t in b["a"]:
            if t not in doc(spec["qa_source"]):
                bad.append(f"Q&A: '{t[:30]}' not in {spec['qa_source']}")
    if spec.get("last_question_ko") and spec["last_question_ko"] not in doc(c["source"]):
        bad.append(f"last page: '{spec['last_question_ko']}' not in {c['source']}")
    for k_, t in spec.get("layout", {}).get("pull_quotes", {}).items():
        if t not in doc(spec["layout"]["pull_source"]):
            bad.append(f"pull quote {k_}: '{t[:30]}' not in {spec['layout']['pull_source']}")
    for t in (spec["back"]["ko"], spec["back"]["en"]):
        if t not in doc(spec["back"]["source"]):
            bad.append(f"back: '{t[:30]}' not in {spec['back']['source']}")
    return bad


def light(m: dict) -> str:
    """Measured, not guessed: 밤 / 흑백 / 해 질 녘 / 흐림 / 낮."""
    if m["mono"]:
        return "흑백" + (" · 밤" if m["dark"] > 0.5 else "")
    if m["dark"] > 0.45 or m["brightness"] < 0.2:
        return "밤"
    if m["warmth"] > 0.06:
        return "해 질 녘"
    if m["saturation"] < 0.12:
        return "흐림"
    return "낮"


def measure_all(spec: dict) -> dict:
    d = paths.REPO / spec["photo_dir"] if not Path(spec["photo_dir"]).is_absolute() else Path(spec["photo_dir"])
    out = {}
    for k in sorted(spec["photos"]):
        f = next((d / f"{k}{x}" for x in (".jpg", ".jpeg", ".png", ".webp") if (d / f"{k}{x}").is_file()), None)
        if f is None:
            out[k] = {"missing": True, "path": str(d / k)}
            continue
        m = PH.measure(f)
        m["light"] = light(m)
        m["palette"] = PH.palette(f, 6)
        out[k] = m
    return out


def _k(n) -> str:
    return f"{int(n):02d}"


# ------------------------------------------------------------------ design system
# Mood: the VISUAL INDEX catalogue (spec "mood_reference"): warm paper, green-black ink, a serif display over
#   tracked sans capitals, ink rules, photographs desaturated to .78, one red.
# Fonts: Caladea (Latin serif, TrueType -- Bitstream Charter is Type 1 and Chromium silently swapped it for Times),
#   Inter / Inter Display (Latin sans), and two vendored OFL Korean families (fonts/SOURCE.md): Noto Serif KR
#   (명조 -- Korean body, standfirst, pull quotes) and Pretendard (고딕, Inter-based -- labels, captions, the
#   One-to-One words in bold as 02_picture.md asks). Korean now has real weights; QA fails a weight with no face.
# Page: 230 x 300 mm. Mirrored margins as in a bound magazine -- inner 20 mm, outer 16 mm, top 14, bottom 18 --
#   12 columns, 4 mm gutters. Every block declares its column and page side; QA measures its left edge.
# Type, in points on paper: body 9.5 (Korean 9, leading 1.75), standfirst 13, title 54, section 30, pull quote 22,
#   caption 7, furniture 6.8. 1 pt = 0.1534 cqw on a 230 mm page.
PT = 0.3528 / 2.3                                   # cqw per point
MM = 1 / 2.3                                        # cqw per millimetre
INNER, OUTER, TOP, BOTTOM, GUT = 20 * MM, 16 * MM, 14 * MM, 18 * MM, 4 * MM
COLS = 12
COL = (100 - INNER - OUTER - (COLS - 1) * GUT) / COLS
PAGE_H = 100 * H_MM / W_MM
TYPE = {"furn": 6.8, "cap": 7.0, "body": 9.5, "body_ko": 9.0, "lead": 13.0, "pull": 22.0, "section": 30.0, "title": 54.0, "word": 78.0}
PAPER, INK, MUTE_RAW, LINE, ACCENT_RAW, GREY = "#f3f0e8", "#1e211e", "#73766e", "#c9c7bd", "#c64c32", "#555850"
NIGHT, NIGHT_INK = "#141614", "#ece8de"
MARGIN = OUTER                                       # kept for callers that want 'the' margin
GUTTER = GUT


def pt(v: float) -> float:
    return round(v * PT, 3)


def X(c: float, side: str = "r") -> float:
    """Left edge of column c on a left ('l') or right ('r') page. The binding side gets the wider margin."""
    left = OUTER if side == "l" else INNER
    return round(left + c * (COL + GUT), 3)


def SPAN(n: int) -> float:
    return round(n * COL + (n - 1) * GUT, 3)


def RIGHT(side: str) -> float:
    """Right margin of a page side."""
    return round(INNER if side == "l" else OUTER, 3)


# technique id -> (name, where it comes from)
TECHNIQUES = {
    "masthead_overlap": ("마스트헤드 오버랩 — 제호가 사진 위에 놓인다", "매거진 URL 카탈로그 · 레이아웃"),
    "masthead_top": ("마스트헤드 상단 배치", "매거진 URL 카탈로그 · 레이아웃 (12/29)"),
    "coverlines": ("커버라인", "매거진 URL 카탈로그 · 레이아웃 (7/29)"),
    "newsstand": ("가판대 표지 — 커버라인과 쪽 번호, 호수 · 계절, 바코드 칸", "매거진 URL 카탈로그 · 커버라인 + 판매 잡지의 관례"),
    "full_bleed": ("풀블리드", "매거진 URL 카탈로그 · 레이아웃 (14/29)"),
    "split_spread": ("두 쪽에 걸친 한 장", "MCA 레퍼런스 보드"),
    "white_space": ("화이트 스페이스 · 넓은 마진", "매거진 URL 카탈로그 · 레이아웃"),
    "mirrored_margins": ("좌우 대칭 여백 — 제본 쪽을 넓게(안 20 mm · 바깥 16 mm)", "판매 잡지의 관례"),
    "asymmetric": ("비대칭 배치 — 넓은 여백 속 한 장 + 맞은편 풀블리드", "매거진 URL 카탈로그 · 비대칭 레이아웃"),
    "feature_opener": ("피처 오프너 — 키커 · 제목 · 스탠드퍼스트 · 바이라인", "판매 잡지의 관례"),
    "text_columns": ("두 단 본문", "매거진 URL 카탈로그 · 텍스트 중심 지면"),
    "serif_display": ("세리프 디스플레이 + 산세리프 메타데이터 — 한글 본문은 명조(Noto Serif KR), 라벨은 고딕(Pretendard)", "VISUAL INDEX · Typography"),
    "grotesk_caps": ("그로테스크 올캡스 · 넓은 트래킹", "매거진 URL 카탈로그 · 타이포그래피"),
    "pull_quote": ("풀쿼트", "판매 잡지의 관례"),
    "drop_cap": ("드롭캡", "판매 잡지의 관례"),
    "experimental_type": ("실험적 타이포그래피 — 세운 글줄", "매거진 URL 카탈로그 · 타이포그래피"),
    "image_in_type": ("글자 속 이미지 — 사진으로 채운 낱말", "편집자 추가 (고전 기법)"),
    "show_through": ("비침 — 뒷장 단어를 좌우 반전해 10%", "docs/portfolio/02_picture.md (사용자 지시)"),
    "closeup": ("클로즈업 — 한 장을 세 번 당겨 보기", "매거진 URL 카탈로그 · 이미지 (3/29)"),
    "chromatic_timeline": ("색의 연대기 — 잰 팔레트를 밝기 순서로", "편집자 추가 (측정 데이터의 시각화)"),
    "duotone": ("듀오톤 — 잉크 · 시그니처 레드 · 종이", "매거진 URL 카탈로그 · 색상 ‘시그니처 레드’"),
    "desaturate": ("채도 낮추기 .78", "VISUAL INDEX · 이미지"),
    "grain": ("필름 그레인", "편집자 추가 (무드)"),
    "scrim": ("스크림 — 사진 위 글자를 위한 그라데이션", "편집자 추가 (가독성)"),
    "caption_line": ("캡션 — 위에 괘선, 번호와 설명", "VISUAL INDEX · Image treatment"),
    "section_head": ("섹션 머리 — 잉크 괘선 + 세리프 제목 + 작은 대문자 라벨", "VISUAL INDEX · section-head"),
    "running_furniture": ("러닝 헤드 · 폴리오 — ‘SPA — Autumn 2026’", "판매 잡지의 관례"),
    "contact_sheet": ("사진 색인 — 썸네일과 잰 값", "MCA 레퍼런스 보드 · 갤러리 벽"),
    "pill_tags": ("태그 칩", "VISUAL INDEX · tags (낱말은 무드보드 색인의 분위기 8개)"),
    "masthead_box": ("마스트헤드 상자 — 만든 이 · 출처 · 독립 선언", "판매 잡지의 관례 + VISUAL INDEX · specs"),
    "footer_band": ("어두운 하단 띠", "VISUAL INDEX · footer"),
}
NOT_USED = {"디돈 세리프 · 고대비 획": "이 환경에 디돈 글꼴이 없다 — 흉내 내지 않는다",
            "Bitstream Charter": "설치돼 있지만 Type 1 형식이라 Chromium에서 쓸 수 없다(조용히 Times로 바뀐다) — Caladea로 대신했다",
            "셀러브리티 커버 · 스튜디오 · 포트레이트": "사진의 성격(거리 · 바다 · 밤의 스냅숏)과 다르다",
            "모노그램 마스트헤드 · 핸드레터링": "제호 SPA는 사용자가 확정한 글자다(cover.md)"}


def darken_to(hexc: str, bg: str, target: float = 4.5) -> str:
    import colorsys
    from gentle_monster.magazine import design as DS
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s_ = colorsys.rgb_to_hls(r, g, b)
    out = hexc
    while DS.contrast(out, bg) < target and l > 0.05:
        l -= 0.01
        out = "#%02x%02x%02x" % tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s_))
    return out


ACCENT_TEXT = darken_to(ACCENT_RAW, PAPER)

def accent_of(measure: dict, path: str) -> dict:
    """The cover photograph's most vivid colour, measured per pixel (a median-cut palette averages small vivid
    areas away: it returned a brown #6c554b for the cover whose punctum is an orange cone). Pixels with high
    saturation and value are binned by hue; the bin with the highest mean s*v (and at least 0.2% of the frame)
    wins. Because the accent is used on text, it is then darkened -- hue kept -- until it reaches 4.5:1 on paper."""
    import colorsys
    import numpy as np
    from gentle_monster.magazine import design as DS
    im = PH._load(path, 600)
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255
    rgb = np.asarray(im).astype(float)
    m = (hsv[..., 1] > 0.55) & (hsv[..., 2] > 0.45)
    if m.mean() < 0.002:
        return {"raw": INK, "text": INK, "share": 0.0}
    hue = (hsv[..., 0][m] * 12).astype(int) % 12
    sv = (hsv[..., 1] * hsv[..., 2])[m]
    best, bs = None, -1.0
    for bin_ in range(12):
        sel = hue == bin_
        if sel.mean() * m.mean() < 0.002:
            continue
        sc = float(sv[sel].mean())
        if sc > bs:
            best, bs = bin_, sc
    px = rgb[m][hue == best]
    r, g, b_ = (float(np.median(px[:, i])) for i in range(3))
    raw = "#%02x%02x%02x" % (round(r), round(g), round(b_))
    h, l, s_ = colorsys.rgb_to_hls(r / 255, g / 255, b_ / 255)
    txt = raw
    while DS.contrast(txt, PAPER) < 4.5 and l > 0.05:
        l -= 0.02
        txt = "#%02x%02x%02x" % tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s_))
    return {"raw": raw, "text": txt, "share": round(float((hue == best).sum()) / hue.size * float(m.mean()), 4)}


def masthead_svg(word: str) -> str:
    """A stencil masthead: Liberation Sans Bold with bridges cut where a stencil needs them -- the P's bowl
    lifted off its stem, the A's apex split, the S's curves broken top and bottom. Positions come from the
    glyphs' measured strokes at 1000 units (see tests), not from a repeating stripe."""
    adv = {"S": 667, "P": 667, "A": 722}
    # x, y, w, h in glyph units (y from the ascender line). Measured at 1000 units (tests/test_photo_issue.py):
    # S strokes cross x 316-350 at rows 208-310 (top) and 808-915 (bottom); P's bowl meets the stem at rows
    # 218-329 and 553-663; A's centre column is solid from the apex down to the counter (~440).
    cuts = {"S": [(316, 200, 34, 120), (316, 800, 34, 125)],
            "P": [(210, 210, 34, 462)],
            "A": [(344, 210, 34, 250)]}
    track, x, glyphs, holes = -24, 0, [], []
    for ch in word:
        glyphs.append(f'<text x="{x}" y="906">{html.escape(ch)}</text>')
        for (cx, cy, cw, chh) in cuts.get(ch, []):
            holes.append(f'<rect x="{x + cx}" y="{cy}" width="{cw}" height="{chh}" fill="#000"/>')
        x += adv.get(ch, 667) + track
    w = x - track
    return (f'<svg class="mast" data-bleed viewBox="0 200 {w} 720" preserveAspectRatio="xMinYMin meet" role="img" aria-label="{e(word)}">'
            f'<defs><mask id="stencil"><rect x="0" y="0" width="{w}" height="1000" fill="#fff"/>{"".join(holes)}</mask></defs>'
            f'<g mask="url(#stencil)" fill="{INK}" font-family="Liberation Sans, Arial, Helvetica, sans-serif" font-weight="700" '
            f'font-size="1000">{"".join(glyphs)}</g></svg>')


CODE39 = {"0": "nnnwwnwnn", "1": "wnnwnnnnw", "2": "nnwwnnnnw", "3": "wnwwnnnnn", "4": "nnnwwnnnw", "5": "wnnwwnnnn",
          "6": "nnwwwnnnn", "7": "nnnwnnwnw", "8": "wnnwnnwnn", "9": "nnwwnnwnn", "A": "wnnnnwnnw", "P": "nnwnwnnwn",
          "S": "nnwnnnwwn", "-": "nwnnnnwnw", "*": "nwnnwnwnn"}


DESAT = 0.78


def smooth_copy(src: Path, dst: Path, factor: int = 2) -> None:
    """A display copy resampled (Lanczos) so viewers that scale with nearest-neighbour do not show stair-steps.
    It adds no detail: print resolution is still judged on the source pixels (data-srcpx), never on this copy."""
    from PIL import Image, ImageEnhance, ImageFilter
    im = Image.open(src).convert("RGB")
    # the catalogue's saturate(.78), baked into the file: a CSS filter makes Chromium rasterise every placement
    # into the PDF (35 MB). Measured afterwards by qa() on the files themselves.
    im = ImageEnhance.Color(im).enhance(DESAT)
    if im.width < 1600:
        im = im.resize((im.width * factor, im.height * factor), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))
    im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)


def image_in_type(word: str, href: str, band=(0.4, 0.86), size=360) -> str:
    """A word whose letters are filled with a photograph (SVG pattern fill -- background-clip:text leaves edge seams
    in Chromium's PDF). The photo's lit band (fractions of its height) is lined up with the capital height."""
    w = round(len(word) * size * 0.74)
    cap_top, base = round(size * 0.34), round(size * 0.99)
    img_h = round((base - cap_top) / (band[1] - band[0]))
    img_w = round(img_h * 468 / 258)
    y = round(cap_top - band[0] * img_h)
    x = round((w - img_w) / 2)
    return (f'<svg viewBox="0 0 {w} {round(size * 1.05)}" style="width:100%;height:auto;display:block" role="img" aria-label="{e(word)}">'
            f'<defs><filter id="lift"><feComponentTransfer><feFuncR type="linear" slope="1.7" intercept=".02"/><feFuncG type="linear" slope="1.7" intercept=".02"/>'
            f'<feFuncB type="linear" slope="1.7" intercept=".02"/></feComponentTransfer></filter>'
            f'<pattern id="fill-{e(word)}" patternUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{round(size * 1.05)}">'
            f'<rect width="{w}" height="{round(size * 1.05)}" fill="{INK}"/>'
            f'<image href="{e(href)}" x="{x}" y="{y}" width="{img_w}" height="{img_h}" preserveAspectRatio="none" filter="url(#lift)"/></pattern></defs>'
            f'<text x="{w / 2:.0f}" y="{base}" text-anchor="middle" font-family="Caladea, Liberation Serif, Georgia, serif" font-weight="700" '
            f'font-size="{size}" letter-spacing="-8" textLength="{w - 20}" lengthAdjust="spacingAndGlyphs" fill="url(#fill-{e(word)})">{e(word)}</text></svg>')


def barcode_svg(text: str) -> str:
    """Code 39 of the issue label only (no ISSN, no price -- this is a concept issue, and the bars say only 'SPA-00')."""
    x, bars = 0, []
    for ch in f"*{text}*":
        for i, w in enumerate(CODE39[ch]):
            ww = 3 if w == "w" else 1
            if i % 2 == 0:
                bars.append(f'<rect x="{x}" y="0" width="{ww}" height="40"/>')
            x += ww
        x += 1                                       # inter-character gap
    return f'<svg viewBox="0 0 {x} 40" preserveAspectRatio="none" aria-label="barcode {e(text)}" fill="#111">{"".join(bars)}</svg>'


def duotone_svg() -> str:
    """Tritone gradient map: shadows -> ink, mid -> the catalogue red, highlights -> paper."""
    ch = lambda hx: [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    a, b = ch(INK), ch(PAPER)
    m = [x * 0.72 + y * 0.28 for x, y in zip(ch(ACCENT_RAW), ch(INK))]      # a deeper red in the mid-tones
    f = lambda i: f"{a[i]:.3f} {m[i]:.3f} {b[i]:.3f}"
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="duotone" color-interpolation-filters="sRGB">'
            '<feColorMatrix type="saturate" values="0"/><feComponentTransfer>'
            f'<feFuncR type="table" tableValues="{f(0)}"/><feFuncG type="table" tableValues="{f(1)}"/><feFuncB type="table" tableValues="{f(2)}"/>'
            '</feComponentTransfer></filter></svg>')


FONT_DIR = Path(__file__).resolve().parent / "fonts"
FACES = [("Pretendard", w, f"Pretendard-{n}.woff2", "woff2") for w, n in ((300, "Light"), (400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"))] + \
        [("Noto Serif KR", w, f"NotoSerifKR-{n}.otf", "opentype") for w, n in ((400, "Regular"), (600, "SemiBold"))]
KO_WEIGHTS = {"Pretendard": {300, 400, 500, 600, 700}, "Noto Serif KR": {400, 600}}


def font_faces() -> str:
    return "".join(f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:normal;font-display:block;src:url("fonts/{fn}") format("{fmt}")}}'
                   for fam, w, fn, fmt in FACES)


def css() -> str:
    ko = '"Pretendard","WenQuanYi Zen Hei","Apple SD Gothic Neo","Malgun Gothic"'
    T = {k: pt(v) for k, v in TYPE.items()}
    return font_faces() + f"""
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTE_RAW};--line:{LINE};--accent:{ACCENT_RAW};--accent-text:{ACCENT_TEXT};--grey:{GREY};
  --night:{NIGHT};--night-ink:{NIGHT_INK};
  --serif:Caladea,"Noto Serif KR","Liberation Serif",Georgia,serif;--sans:Inter,{ko},"Liberation Sans",Arial,sans-serif;
  --gothic:{ko},Inter,sans-serif;--display:"Inter Display",Inter,{ko},sans-serif}}
*{{box-sizing:border-box;font-synthesis:none}} html{{background:#262724}}
body{{margin:0;color:var(--ink);font-family:var(--serif);word-break:keep-all;overflow-wrap:break-word;-webkit-font-smoothing:antialiased;
  font-kerning:normal;text-rendering:optimizeLegibility;hanging-punctuation:first}}
main{{display:flex;flex-wrap:wrap;justify-content:center;padding:28px 0}}
.page{{container-type:inline-size;position:relative;overflow:hidden;background:var(--paper);width:min(46vw,560px);aspect-ratio:{W_MM}/{H_MM};margin-bottom:36px}}
.page.night{{background:var(--night);color:var(--night-ink)}}
.page.cover{{margin-right:46vw}} @media (max-width:1100px){{.page{{width:min(100vw - 32px,560px)}} .page.cover{{margin-right:0}}}}
.a{{position:absolute}} p{{margin:0}}
img{{display:block;width:100%;height:100%;object-fit:cover}}
.duo img{{filter:url(#duotone)}}
/* type scale (pt on paper) */
.furn{{font-family:var(--sans);font-size:{T['furn']}cqw;letter-spacing:.12em;text-transform:uppercase;font-weight:500;color:var(--grey)}}
.cap{{font-family:var(--sans);font-size:max({T['cap']}cqw,8.5px);line-height:1.45;color:var(--grey)}}
.cap b{{font-weight:500;color:var(--ink);margin-right:.6em}}
.kicker{{font-family:var(--sans);font-size:max({T['furn']}cqw,8.5px);letter-spacing:.16em;text-transform:uppercase;font-weight:600;color:var(--accent-text)}}
.body{{font-size:max({T['body']}cqw,10.5px);line-height:1.52}}
.body:lang(ko),.ko{{font-family:var(--serif);font-size:max({T['body_ko']}cqw,10.5px);line-height:1.8;letter-spacing:-.01em}}
.gothic{{font-family:var(--gothic)}}
.lead{{font-size:{T['lead']}cqw;line-height:1.5}} .lead:lang(ko),.lead .ko{{line-height:1.66;letter-spacing:-.01em}}
.pull{{font-size:{T['pull']}cqw;line-height:1.3;letter-spacing:-.015em}}
.section{{font-size:{T['section']}cqw;line-height:1.02;letter-spacing:-.025em}}
.title{{font-size:{T['title']}cqw;line-height:.96;letter-spacing:-.03em}}
.num-l{{font-family:var(--display);font-weight:300;font-variant-numeric:tabular-nums;letter-spacing:-.02em}}
.byline{{font-family:var(--sans);font-size:max({T['furn']}cqw,8.5px);letter-spacing:.12em;text-transform:uppercase;font-weight:500}}
.dropcap::first-letter{{float:left;font-size:4.15em;line-height:.8;margin:.06em .07em 0 0;font-weight:400}}
.rule{{border-top:1px solid var(--ink)}} .hair{{border-top:1px solid var(--line)}}
.sh{{border-top:1px solid var(--ink);padding-top:{pt(9)}cqw;display:flex;justify-content:space-between;align-items:baseline;gap:2cqw}}
.night .cap,.on-photo .cap{{color:#d9d5cb}} .night .cap b,.on-photo .cap b{{color:#f6f3ec}}
.on-photo{{color:#f6f3ec}}
.folio{{position:absolute;bottom:{pt(14)}cqw;display:flex;gap:1.4cqw;align-items:baseline}}
.folio .n{{font-family:var(--display);font-weight:400;font-size:{pt(8)}cqw;color:var(--ink);font-variant-numeric:tabular-nums}}
.night .folio .n,.bleed-page .folio .n{{color:#f6f3ec}} .night .folio .furn,.bleed-page .folio .furn{{color:#d9d5cb}}
.pill{{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:0 .7cqw;font-family:var(--sans);font-size:max({pt(6.6)}cqw,8.5px);
  line-height:1.6;color:var(--grey)}}
.grain{{position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply;opacity:.2;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.1 -.2'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");background-size:22cqw 22cqw}}
.scrim-t{{position:absolute;left:0;right:0;top:0;height:42%;background:linear-gradient(rgba(10,11,10,.42),rgba(10,11,10,0))}}
.scrim-b{{position:absolute;left:0;right:0;bottom:0;height:40%;background:linear-gradient(rgba(10,11,10,0),rgba(10,11,10,.62))}}
.cline{{border-top:1px solid rgba(246,243,236,.7);padding:.8cqw 0 1.1cqw;display:grid;grid-template-columns:{pt(30)}cqw 1fr;align-items:baseline}}
.barcode{{background:#fff;padding:1.2cqw 1.4cqw .8cqw;color:#111}} .barcode svg{{display:block;width:100%;height:5.4cqw}}
.mast-ov{{color:#f6f3ec;font-family:var(--serif);font-weight:400;line-height:.8;letter-spacing:-.06em;white-space:nowrap}}
.mani{{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;font-size:{pt(44)}cqw;line-height:1.08;letter-spacing:-.025em}}
.mani sup{{font-family:var(--sans);font-size:.24em;vertical-align:0;margin:0 0 .5em;color:var(--accent-text)}}
sup{{font-size:.78em;line-height:0;vertical-align:.45em;margin-left:.06em;font-family:var(--sans)}} sup a{{color:inherit;text-decoration:none}}
.split{{top:0;height:100%;width:200%}} .split.l{{left:0}} .split.r{{left:-100%}}
.ghost{{opacity:.1;transform:scaleX(-1)}}
.box{{border:1px solid rgba(255,255,255,.9);color:#fff;background:rgba(15,16,14,.24)}}
.band{{left:0;right:0;bottom:0;background:var(--ink);color:var(--paper);padding:2cqw {OUTER}cqw;display:flex;justify-content:space-between;gap:2cqw}}
.zoom{{overflow:hidden;position:relative;background:#ddd8cc}} .zoom img{{position:absolute;height:auto;max-width:none}}
.cols2{{columns:2;column-gap:{GUT}cqw}} .cols2 > *{{break-inside:avoid}}
.irow{{display:grid;grid-template-columns:{pt(36)}cqw {pt(16)}cqw 1fr {pt(48)}cqw {pt(26)}cqw {pt(26)}cqw {pt(62)}cqw;column-gap:{GUT * .7:.3f}cqw;
  align-items:center;border-bottom:1px solid var(--line);padding:.55cqw 0}}
.irow.h{{border-bottom:1px solid var(--ink);padding-top:0}}
.sw{{display:inline-block;width:1.25cqw;height:1.25cqw;margin-right:.25cqw;vertical-align:-.2cqw}}
.toc{{display:grid;grid-template-columns:{SPAN(2)}cqw {SPAN(7)}cqw {SPAN(3)}cqw;column-gap:{GUT}cqw;align-items:baseline;border-top:1px solid var(--line);
  padding:{pt(4)}cqw 0 {pt(4.5)}cqw;color:inherit;text-decoration:none}}
.mbox{{display:grid;grid-template-columns:repeat(3,1fr);column-gap:{GUT}cqw;row-gap:1.2cqw}} .mbox div{{border-top:1px solid var(--line);padding-top:.7cqw}}
.mbox b{{display:block;font-weight:600;color:var(--accent-text);letter-spacing:.1em;text-transform:uppercase;margin-bottom:.3cqw}}
.tlist{{columns:2;column-gap:{GUT}cqw}} .tlist p{{break-inside:avoid;padding:.35cqw 0;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:1cqw}}
.refs{{margin:0;padding:0 0 0 1.6cqw}} .refs li{{margin-bottom:.35cqw}} .refs a{{color:inherit;text-decoration:none;word-break:break-all}}
@media (hover:hover){{ .hz img{{transition:transform .6s cubic-bezier(.2,.7,.2,1)}} .hz:hover img{{transform:scale(1.03)}} }}
@media (max-width:600px){{
  .page.text{{aspect-ratio:auto;padding:30px 20px 56px}} .page.text .a{{position:static;width:auto!important;transform:none;margin-bottom:18px}}
  .page.text .body{{font-size:15px}} .page.text .ko,.page.text .body:lang(ko){{font-size:15px}} .page.text .lead{{font-size:18px}}
  .page.text .pull{{font-size:22px}} .page.text .section{{font-size:28px}} .page.text .title{{font-size:40px}}
  .page.text .cap,.page.text .furn,.page.text .kicker,.page.text .byline{{font-size:12px}} .page.text .folio{{position:absolute;bottom:16px}}
  .page.text .mani{{writing-mode:horizontal-tb;font-size:26px;white-space:normal}} .page.text .cols2,.page.text .tlist{{columns:1}}
  .page.text .irow{{grid-template-columns:56px 28px 1fr;font-size:13px}} .page.text .irow > :nth-child(n+4){{display:none}}
  .page.text .toc{{grid-template-columns:44px 1fr}} .page.text .toc > :nth-child(3){{display:none}} .page.text .mbox{{grid-template-columns:1fr}}
  .page.cover{{aspect-ratio:auto;min-height:133cqw;padding:58cqw 20px 28px}}
  .page.cover .a:not(.mast-ov):not([data-bleed]):not(.top){{position:static;width:auto!important;margin:0 0 18px}}
}}
@page{{size:{W_MM}mm {H_MM}mm;margin:0}}
@media print{{ html{{background:none}} main{{display:block;padding:0}} .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;margin:0;break-after:page}}
  *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}} }}
html.print-sim main{{display:block;padding:0;width:{W_MM}mm}} html.print-sim .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;margin:0}}
"""


def build(spec_path, name: str = "", pdf: bool = True) -> dict:
    spec = load(spec_path)
    bad_text = check_texts(spec)
    meas = measure_all(spec)
    missing = [k for k, m in meas.items() if m.get("missing")]
    out = paths.job_dir(name or spec["id"]) / "photo_issue"
    (out / "img").mkdir(parents=True, exist_ok=True)
    cat = CAT.load()
    src = CAT.by_id(cat)
    claims = {c["id"]: c for c in cat["claims"]}
    focus = spec.get("focus", {})
    story = {s["id"]: s for s in spec["story"]}
    moods = spec.get("moods", {}).get("photo", {})
    L_ = spec["layout"]
    T = {k: pt(v) for k, v in TYPE.items()}

    assets = {}
    for k, m in meas.items():
        if m.get("missing"):
            continue
        dst = out / "img" / (Path(m["path"]).stem + ".jpg")
        if not dst.exists() or dst.stat().st_mtime < Path(m["path"]).stat().st_mtime:
            smooth_copy(Path(m["path"]), dst)
        assets[k] = A.user_image(str(dst), spec["credit"], spec["rights"], title=f"{k} — {spec['photos'][k]}")
        from PIL import Image as _I
        with _I.open(m["path"]) as _im:                       # the file's own size -- measure() works on a 1000 px thumbnail
            assets[k]["source_pixels"] = list(_im.size)
    cov = _k(spec["cover"]["photo"])
    measured_accent = accent_of(meas[cov], meas[cov]["path"]) if cov in assets else {"raw": INK, "text": INK, "share": 0}
    src_of = lambda k: f'img/{Path(assets[k]["local_path"]).name}' if k in assets else ""
    aspect = 468 / 258
    credit_name = spec["credit"].split(": ")[-1]

    def img(n, pos=None):
        k = _k(n)
        if k not in assets:
            return f'<div class="cap">사진 {k} 없음</div>'
        return (f'<img src="{e(src_of(k))}" alt="{e(spec["photos"][k])}" data-photo="{k}" data-srcpx="{assets[k]["source_pixels"][0]}" '
                f'style="object-position:{pos or focus.get(k, "50% 50%")}">')

    pages, refs = [], {}
    side_of = lambda: "l" if (len(pages) + 1) % 2 == 0 else "r"

    def at(col, top, span=None, cls="", inner="", bottom=None, tech="", extra="", side=None, lang=None):
        sd = side or side_of()
        pos = f"left:{X(col, sd)}cqw;" + (f"top:{top}cqw;" if top is not None else "") + (f"bottom:{bottom}cqw;" if bottom is not None else "")
        pos += f"width:{SPAN(span)}cqw;" if span else ""
        t = f' data-technique="{tech}"' if tech else ""
        lg = f' lang="{lang}"' if lang else ""
        return f'<div class="a {cls}" data-col="{col}" data-mirror="{sd}"{t}{lg} style="{pos}{extra}">{inner}</div>'

    def caption(n, text=None, light=False):
        k = _k(n)
        return (f'<p class="cap" data-technique="caption_line" style="margin-top:{pt(5)}cqw;border-top:1px solid {"rgba(246,243,236,.6)" if light else "var(--ink)"};'
                f'padding-top:{pt(3)}cqw"><b>{k}</b>{e(text or spec["photos"][k])}</p>')

    def fig(n, col, top, span, h=None, pos=None, cap=True, light=False):
        hh = h or round(SPAN(span) / aspect, 3)
        return at(col, top, span, "hz", f'<div style="height:{hh}cqw;overflow:hidden" data-technique="desaturate">{img(n, pos)}</div>'
                  + (caption(n, light=light) if cap else ""))

    def bleed(n, pos=None, extra_cls=""):
        return (f'<div class="a {extra_cls}" style="inset:0" data-bleed data-technique="full_bleed">{img(n, pos)}<div class="grain" data-technique="grain"></div>'
                f'<div class="scrim-b" data-technique="scrim"></div></div>')

    def section(title, label, top=None, lang="en", span=12):
        return at(0, top if top is not None else round(TOP, 3), span, "", f'<div class="sh" data-technique="section_head"><p class="section" lang="{lang}">{e(title)}</p>'
                  f'<p class="furn" lang="en">{e(label)}</p></div>', tech="serif_display")

    def cite(ids):
        out_ = []
        for i in ids:
            for s_ in claims.get(i, {}).get("source_ids", [])[:1]:
                n = refs.setdefault(s_, len(refs) + 1)
                out_.append(f'<a href="#lref-{n}">{n}</a>')
        return f"<sup>{','.join(out_)}</sup>" if out_ else ""

    def page(inner, cls="", kind="photo", photos=(), label="", furn=None):
        n = len(pages) + 1
        side = "l" if n % 2 == 0 else "r"
        f = ""
        if kind not in ("cover", "back"):
            sec = e(furn or story.get(label, {}).get("en", ""))
            num = f'<span class="n">{n:02d}</span>'
            txt = f'<span class="furn" lang="en">{e(spec["masthead"])} — Autumn 2026&ensp;·&ensp;{sec}</span>'
            pos = f"left:{OUTER}cqw" if side == "l" else f"right:{OUTER}cqw"
            f = f'<div class="folio" data-technique="running_furniture" style="{pos}">{num + txt if side == "l" else txt + num}</div>'
        pages.append({"n": n, "kind": kind, "label": label, "photos": [_k(p) for p in photos], "side": side,
                      "html": f'<section class="page {cls}" id="p{n:02d}" data-type="{kind}" data-label="{e(label)}" data-side="{side}">{inner}{f}</section>'})

    c = spec["cover"]
    # ===== 1 cover (newsstand) ===============================================================================
    lines = [("Where Did You Last Stop?", "포토 에세이 — 열다섯 번의 멈춤", "opener"), ("Night", "빨간불 앞에서 멈춘다", "night"),
             ("Why Pictures", "사진에 관한 세 물음", "why"), ("Looking Closer", "한 장을 세 번, 하루의 색", "closer"),
             ("The Gentle Monster Lens", "왜 이 표지인가", "lens")]
    page(f'<div class="a" style="inset:0" data-bleed data-technique="full_bleed">{img(cov, pos=spec.get("cover_focus", "80% 55%"))}'
         f'<div class="grain" data-technique="grain"></div><div class="scrim-t" data-technique="scrim"></div><div class="scrim-b"></div></div>'
         + f'<div class="a top furn on-photo" lang="en" data-technique="masthead_top" style="left:{INNER}cqw;right:{OUTER}cqw;top:{pt(16)}cqw;display:flex;'
           f'justify-content:space-between;border-bottom:1px solid rgba(246,243,236,.7);padding-bottom:{pt(5)}cqw;color:#f6f3ec">'
           f'<span>Issue 00 — Autumn 2026</span><span>Independent concept magazine</span></div>'
         + f'<div class="a mast-ov" lang="en" data-bleed data-technique="masthead_overlap" style="left:{INNER - 1.8:.2f}cqw;top:7.4cqw;font-size:45cqw">'
           f'{e(spec["masthead"])}</div>'
         + at(0, 47, 4, "furn on-photo", '<p style="color:#f6f3ec;line-height:1.8">' + "<br>".join(e(x) for x in c["left"]) + "</p>",
              tech="grotesk_caps", lang="en")
         + at(7, 47, 5, "on-photo", "CLINES", tech="newsstand")
         + at(0, None, 8, "on-photo", f'<p data-technique="serif_display" lang="en" class="title" style="font-size:{pt(44)}cqw;margin-bottom:{pt(12)}cqw">'
              f'“{e(c["question"])}”</p><p class="lead" lang="en" style="margin-bottom:{pt(12)}cqw">' + "<br>".join(e(x) for x in c["right"])
              + '</p><p class="byline" lang="en" style="color:#f6f3ec">' + " ".join(e(x) for x in c["byline"]) + "</p>", bottom=round(BOTTOM, 3), tech="coverlines")
         + at(9, None, 3, "barcode", f'{barcode_svg("SPA-00")}<p class="furn" lang="en" style="color:#111;margin-top:.5cqw;line-height:1.5">'
              f'SPA-00 · Concept issue<br>Not for sale</p>', bottom=round(BOTTOM, 3)),
         "cover", "cover", [cov], "표지")
    # ===== 2 | 3 contents ==================================================================================
    cp = L_["contents_photo"]
    page(bleed(cp) + at(0, None, 6, "on-photo", caption(cp, light=True), bottom=round(BOTTOM + 2.5, 3)), "bleed-page", "photo", [cp], "contents",
         furn="Contents")
    lc = sum(1 for k in meas if not meas[k].get("missing") and meas[k]["light"].startswith(("밤", "흑백")))
    mbox = [("Photographs & words", credit_name), ("Edit & layout", "gentle_monster magazine"), ("Mood", "VISUAL INDEX catalogue"),
            ("Type", "Caladea · Noto Serif KR · Inter · Pretendard"), ("Format", f"{W_MM} × {H_MM} mm · 26 pp."),
            ("Independent", "젠틀몬스터가 발행 · 승인하지 않은 독립 콘셉트 매거진")]
    page(at(0, round(TOP, 3), 12, "", f'<p class="kicker" lang="en">Issue 00 — Autumn 2026</p>'
            f'<p class="section" lang="en" style="font-size:{pt(40)}cqw;margin-top:{pt(6)}cqw">Contents</p>', tech="serif_display")
         + at(0, 22, 12, "", "TOC")
         + at(0, None, 12, "cap mbox", "".join(f'<div><b lang="en">{e(k)}</b>{e(v)}</div>' for k, v in mbox), bottom=round(BOTTOM + 3, 3),
              tech="masthead_box"),
         "text", "contents", [], "contents", furn="Contents")
    # ===== 4 | 5 feature opener ================================================================================
    op = L_["opener_photo"]
    page(bleed(op) + at(0, None, 6, "on-photo", caption(op, light=True), bottom=round(BOTTOM + 2.5, 3)), "bleed-page", "photo", [op], "opener")
    it = spec["intro"]
    n_dark = lc
    page(at(0, round(TOP + 2, 3), 12, "", f'<p class="kicker" lang="en">Photo essay</p>', tech="feature_opener")
         + at(0, round(TOP + 7, 3), 11, "title", f'<p lang="en">Where Did You<br>Last Stop?</p>', tech="serif_display")
         + at(0, 44, 9, "lead", "".join(f'<p class="ko" lang="ko" style="font-size:{T["lead"]}cqw;line-height:1.66;margin-bottom:.35em">{e(x)}</p>'
                                         for x in it["ko"]))
         + at(0, 66, 12, "", f'<p class="byline" lang="en" style="border-top:1px solid var(--ink);padding-top:{pt(6)}cqw">Words &amp; photographs — {e(credit_name)}</p>')
         + at(0, 74, 5, "cap", f'<p class="kicker" lang="en" style="color:var(--ink);margin-bottom:.8em">In this issue</p>'
              f'<p>사진 {len(assets)}장 — 그중 {n_dark}장은 밤이거나 흑백이다(잰 값). 단어 두 개, 선언 하나, 물음 세 개.</p>', tech="white_space")
         + at(6, 74, 6, "body", f'<p lang="en" class="dropcap" data-technique="drop_cap">{e(it["en"])}</p>', tech="text_columns", lang="en"),
         "text", "opener", [], "opener", furn="Photo essay")
    # ===== 6 | 7 day spread (canoe across the gutter) ============================================================
    ds = L_["day_spread"]
    dk = _k(ds)
    page(f'<div class="a split l" data-bleed data-technique="split_spread">{img(ds)}<div class="grain"></div></div>', "bleed-page", "spread", [ds], "day")
    page(f'<div class="a split r" data-bleed data-technique="full_bleed">{img(ds)}<div class="grain"></div><div class="scrim-b"></div></div>'
         + at(6, None, 6, "on-photo", caption(ds, light=True), bottom=round(BOTTOM + 2.5, 3)), "bleed-page", "spread", [ds], "day")
    # ===== 8 | 9 small-in-white + full bleed =======================================================================
    s1, s2 = L_["sea_pair"]
    page(fig(s1, 3, round(TOP + 8, 3), 9)
         + at(0, 72, 10, "pull ko", f'<p lang="ko" data-technique="pull_quote">“{e(L_["pull_quotes"]["day"])}”</p>', tech="asymmetric")
         + at(0, 98, 4, "cap", f'<p>— {e(credit_name)}, 02 PICTURE</p>'),
         "", "photo", [s1], "day")
    page(bleed(s2) + at(0, None, 6, "on-photo", caption(s2, light=True), bottom=round(BOTTOM + 2.5, 3)), "bleed-page", "photo", [s2], "day")
    # ===== 10 | 11 one to one (show-through) =========================================================================
    ws = spec["words"]
    for i, w in enumerate(ws):
        ghost = ws[i + 1]["word"] if i + 1 < len(ws) else ""
        page(fig(w["photo"], 1, 22, 10, cap=False)
             + (at(0, 80, 12, "ghost", f'<p style="font-family:var(--gothic);font-weight:700;font-size:{T["word"]}cqw;text-align:center;line-height:1">{e(ghost)}</p>',
                   tech="show_through") if ghost else "")
             + at(0, 80, 12, "", f'<p style="font-family:var(--gothic);font-weight:700;font-size:{T["word"]}cqw;text-align:center;line-height:1;letter-spacing:-.03em">{e(w["word"])}</p>',
                  tech="white_space"),
             "", "word", [w["photo"]], "turn")
    # ===== 12 | 13 night ===================================================================================
    ns = spec["night_spread"]
    nk = _k(ns)
    page(f'<div class="a split l" data-bleed data-technique="split_spread">{img(ns)}<div class="grain"></div></div>', "night", "spread", [ns], "night")
    page(f'<div class="a split r" data-bleed>{img(ns)}<div class="grain"></div></div>'
         + at(6, None, 6, "on-photo", caption(ns, light=True), bottom=round(BOTTOM + 2.5, 3)), "night", "spread", [ns], "night")
    # ===== 14 stop | 15 manifesto =============================================================================
    so = story["stop"]
    page(at(0, round(TOP, 3), 12, "", f'<p class="kicker" lang="en">Stop — Fig. {nk}</p>')
         + at(0, 36, 12, "", image_in_type("STOP", src_of(nk), band=(0.40, 0.86)), tech="image_in_type")
         + at(0, 78, 5, "cap", f'<p>{e(so["ko"])}. 글자를 밤 사진으로 채웠다 — 낱말이 곧 장면이다.</p>'),
         "", "stop", [ns], "stop")
    mf = spec["manifesto"]
    side = side_of()
    page(f'<div class="a mani" lang="en" data-col="1" data-mirror="{side}" data-technique="experimental_type" style="left:{X(1, side)}cqw;bottom:{round(BOTTOM + 4, 3)}cqw;height:100cqw">'
         + "".join(f"<div>{e(l)}<sup>{i}</sup></div>" for i, l in enumerate(mf["lines"], 1)) + "</div>"
         + at(8, round(TOP, 3), 4, "", f'<p class="kicker" lang="en">Manifesto</p><p class="cap" style="margin-top:.8em">{e(credit_name)}, philosophy.md</p>'),
         "text", "manifesto", [], "manifesto")
    # ===== 16 duotone | 17 pair =================================================================================
    du = spec["duotone"]
    page(f'<div class="a duo" style="inset:0" data-bleed data-technique="duotone">{img(du)}<div class="grain"></div><div class="scrim-b"></div></div>'
         + at(0, None, 6, "on-photo", caption(du, f'{spec["photos"][_k(du)]} — 듀오톤', light=True), bottom=round(BOTTOM + 2.5, 3)),
         "night", "photo", [du], "manifesto")
    p1, p2 = L_["pair"]
    ph = round(SPAN(12) / aspect, 3)
    page(fig(p1, 0, round(TOP, 3), 12) + fig(p2, 0, round(TOP + ph + 10, 3), 12), "", "pair", [p1, p2], "manifesto")
    # ===== 18 | 19 why pictures (article) ========================================================================
    wp = L_["why_photo"]
    page(at(0, round(TOP + 4, 3), 11, "pull", f'<p class="ko" lang="ko" style="font-size:{pt(26)}cqw;line-height:1.45" data-technique="pull_quote">'
            f'“{e(L_["pull_quotes"]["why"])}”</p>')
         + fig(wp, 0, 66, 12), "", "photo", [wp], "why")
    wy = story["why"]
    qa_cols = [[], []]
    for i, b in enumerate(spec["qa_text"]):
        paras, cur = [], []
        for a_ in b["a"]:
            if a_.startswith(("첫째", "둘째")) and cur:
                paras.append(cur); cur = []
            cur.append(a_)
        paras.append(cur)
        body = "".join(f'<p class="ko" lang="ko" style="font-size:{pt(10)}cqw;line-height:1.85;margin-bottom:1em">' + " ".join(
            (f'<span style="color:var(--accent-text)">{e(x)}</span>' if x.startswith(("첫째", "둘째")) else e(x)) for x in p_) + "</p>" for p_ in paras)
        qa_cols[0 if i < 2 else 1].append(
            f'<div style="margin-bottom:{pt(34)}cqw"><p class="num-l" style="font-size:{pt(30)}cqw;color:var(--accent-text);line-height:1">Q{i + 1}</p>'
            f'<p class="ko" lang="ko" style="font-size:{pt(15)}cqw;line-height:1.5;margin:{pt(8)}cqw 0 {pt(10)}cqw">{e(b["q"])}</p>{body}</div>')
    page(section(wy["en"], "Interview with the photographs")
         + at(0, round(TOP + 9, 3), 12, "", f'<p class="byline" lang="en">Questions &amp; answers — {e(credit_name)}</p>')
         + at(0, 25, 6, "", "".join(qa_cols[0]), tech="text_columns") + at(6, 25, 6, "", "".join(qa_cols[1])),
         "text", "qa", [], "why")
    # ===== 20 | 21 looking closer ===============================================================================
    z = spec["zoom"]
    zk = _k(z["photo"])
    cl = story["closer"]
    zh = round(SPAN(8) / aspect, 3)
    frames = ""
    sd = side_of()
    for i, sc in enumerate(z["scales"]):
        top = 24 + i * (zh + 5.6)
        w = sc * 100
        lx = max(min(50 - z["focus"][0] * w, 0), 100 - w)
        ty = max(min(50 - z["focus"][1] * w * (258 / 468) * (SPAN(8) / zh), 0), 100 - w * (258 / 468) * (SPAN(8) / zh))
        frames += (at(0, top, 3, "num-l", f'<p style="font-size:{pt(30)}cqw;line-height:1" lang="en">×{sc:g}</p>')
                   + at(4, top, 8, "", f'<div class="zoom" style="height:{zh}cqw"><img src="{e(src_of(zk))}" alt="{e(spec["photos"][zk])} (×{sc:g})" '
                        f'data-photo="{zk}" data-srcpx="{assets[zk]["source_pixels"][0] if zk in assets else 0}" style="width:{w:.1f}%;left:{lx:.1f}%;top:{ty:.1f}%"></div>',
                        tech="closeup"))
    page(section(cl["en"], "One photograph, three times") + frames
         + at(4, None, 8, "cap", f'<p><b>{zk}</b>{e(spec["photos"][zk])} — 같은 사진을 ×1 · ×2.2 · ×4.4로 당겼다. 확대할수록 사진의 낱알이 드러난다.</p>',
              bottom=round(BOTTOM + 2, 3)),
         "", "zoom", [z["photo"]], "closer")
    ks = sorted(k for k in spec["photos"] if k in assets)
    order = sorted(ks, key=lambda k: -meas[k]["brightness"])
    sd = side_of()
    bw = (SPAN(12) - (len(order) - 1) * 0.5) / len(order)
    bands = ""
    for i, k in enumerate(order):
        pal = meas[k].get("palette", [])
        tot = sum(sh for _, sh in pal) or 1
        stack = "".join(f'<div style="height:{sh / tot * 100:.2f}%;background:{hx}"></div>' for hx, sh in pal)
        x = X(0, sd) + i * (bw + 0.5)
        bands += (f'<div class="a" style="left:{x:.3f}cqw;top:26cqw;width:{bw:.3f}cqw;height:80cqw;display:flex;flex-direction:column">{stack}</div>'
                  f'<div class="a cap" style="left:{x:.3f}cqw;top:107.6cqw;width:{bw:.3f}cqw;text-align:center;color:var(--ink)">{k}</div>')
    page(section("Colour of the Day", "Measured palettes, bright → dark") + f'<div data-technique="chromatic_timeline">{bands}</div>'
         + at(0, None, 8, "cap", '<p>열다섯 장에서 잰 색 — 사진마다 여섯 색과 그 비율을, 잰 밝기 순서로 놓았다(왼쪽이 가장 밝다). '
              '지면의 사진은 채도를 낮췄지만 이 띠는 원본에서 잰 색이다.</p>', bottom=round(BOTTOM + 2, 3)),
         "", "timeline", [], "closer")
    # ===== 22 lens | 23 index ====================================================================================
    Lz = spec["lens"]
    cw = round(SPAN(3) / aspect, 3)
    cands = "".join(at(i * 3, 26, 3, "", f'<div style="height:{cw}cqw">{img(n, pos="50% 50%")}</div>'
                       f'<p class="cap" style="margin-top:{pt(4)}cqw{";color:var(--accent-text)" if n == Lz["chosen"] else ""}"><b'
                       f'{" style=" + chr(34) + "color:var(--accent-text)" + chr(34) if n == Lz["chosen"] else ""}>{_k(n)}</b>'
                       f'{"표지" if n == Lz["chosen"] else ""}</p>') for i, n in enumerate(Lz["candidates"]))
    paras = "".join(f'<p class="ko" lang="ko" style="margin-bottom:.95em">{e(r["text"])}{cite(r["claims"])}</p>' for r in Lz["reading"])
    others = "".join(f'<p style="margin-bottom:.6em"><b>{k}</b>{e(t)}</p>' for k, t in Lz["others"].items())
    page(section(Lz["title"], "The Gentle Monster lens", lang="ko")
         + at(0, round(TOP + 9, 3), 12, "", '<p class="byline" lang="en">Column — the editor</p>')
         + cands + at(0, 26 + cw + 7, 12, "cols2", paras, tech="text_columns")
         + at(0, None, 12, "cap cols2", f'{others}<p style="margin-bottom:.6em">{e(Lz["note"])}</p><ol class="refs">REFS</ol>', bottom=round(BOTTOM + 3, 3)),
         "text", "lens", Lz["candidates"], "lens")
    ix = story["index"]
    rows = "".join(
        f'<div class="irow"><div style="height:{pt(20)}cqw;overflow:hidden">{img(k)}</div><span class="cap" style="color:var(--ink)">{k}</span>'
        f'<span class="cap" style="color:var(--ink)">{e(spec["photos"][k])}<br><span class="pill" data-technique="pill_tags">{e(moods.get(k, ""))}</span></span><span class="cap">{e(meas[k]["light"])}</span>'
        f'<span class="cap">{meas[k]["brightness"]:.2f}</span><span class="cap">{meas[k]["saturation"]:.2f}</span><span>'
        + "".join(f'<i class="sw" style="background:{hx}"></i>' for hx, _ in meas[k].get("palette", [])[:5]) + "</span></div>" for k in ks)
    page(section(ix["en"], "Seen · measured")
         + at(0, 22, 12, "", '<div class="irow h furn"><span></span><span>No.</span><span>보이는 것</span><span>빛</span><span>밝기</span><span>채도</span>'
              f'<span>색 (잰 값)</span></div>{rows}', tech="contact_sheet")
         + at(0, None, 12, "cap", f'<p>{e(spec["photos_note"])} 빛 · 밝기 · 채도 · 색은 원본 사진에서 잰 값이다(밝기 · 채도 0–1). '
              f'무드 낱말은 {e(spec["moods"]["note"])}</p>', bottom=round(BOTTOM + 2, 3)),
         "text", "index", ks, "index")
    # ===== 24 notes | 25 last page ===============================================================================
    page(section(story["notes"]["en"], "Techniques · sources · colophon")
         + at(0, 22, 12, "cap tlist", "TECHS")
         + at(0, None, 6, "cap", "NOTUSED", bottom=round(BOTTOM + 2, 3))
         + at(6, None, 6, "cap", f'<p class="kicker" lang="en" style="margin-bottom:.6em">Mood reference</p><p>{e(spec["mood_reference"]["name"])}</p>'
              f'<p style="margin-top:.4em">{e(spec["mood_reference"]["substitutions"])}</p>', bottom=round(BOTTOM + 2, 3)),
         "text", "notes", [], "notes")
    lp = L_["last_photo"]
    page(fig(lp, 0, round(TOP + 4, 3), 12)
         + at(0, 80, 12, "", f'<p class="title" lang="en" style="font-size:{pt(40)}cqw">“{e(c["question"])}”</p>'
              f'<p class="ko lead" lang="ko" style="margin-top:{pt(10)}cqw;color:var(--grey)">{e(spec["last_question_ko"])}</p>', tech="white_space"),
         "", "last", [lp], "last")
    # ===== 26 back cover =========================================================================================
    b = spec["back"]
    page(f'<div class="a" style="inset:0" data-bleed data-technique="full_bleed">{img(b["photo"])}<div class="grain"></div></div>'
         + at(1, 12, 10, "box", f'<div style="padding:3.2cqw 3.4cqw"><p class="ko" lang="ko" style="font-size:{T["lead"]}cqw;line-height:1.66;margin-bottom:1em">{e(b["ko"])}</p>'
              f'<p class="body" lang="en" style="margin-bottom:1.4em;font-family:var(--serif);line-height:1.5">{e(b["en"])}</p>'
              f'<p class="title" lang="en" style="font-size:{pt(22)}cqw">“{e(c["question"])}”</p></div>')
         + f'<div class="a band furn" lang="en" data-technique="footer_band" style="color:{PAPER}"><span>{e(spec["masthead"])} 00 — {e(spec["credit"])}</span>'
           f'<span lang="ko">독립 콘셉트 매거진 · 젠틀몬스터가 발행 · 승인하지 않았습니다</span></div>',
         "text", "back", [b["photo"]], "back")

    # ---- fill-ins that need every page first
    first = {}
    for p in pages:
        first.setdefault(p["label"], p["n"])
    toc = "".join(f'<a href="#p{first[s_["id"]]:02d}" class="toc"><span class="num-l" style="font-size:{pt(19)}cqw;line-height:1">{first[s_["id"]]:02d}</span>'
                  f'<span><span lang="en" style="display:block;font-size:{T["lead"]}cqw;line-height:1.2">{e(s_["en"])}</span>'
                  f'<span class="cap" style="display:block;margin-top:.2em">{e(s_["ko"])}</span></span>'
                  f'<span class="furn" lang="en" style="text-align:right">{"Feature" if s_["id"] in ("opener", "why") else ("Column" if s_["id"] == "lens" else "")}</span></a>'
                  for s_ in spec["story"] if s_["id"] != "contents" and first.get(s_["id"]))
    pages[2]["html"] = pages[2]["html"].replace("TOC", toc, 1)
    clines = "".join(f'<div class="cline"><span class="num-l" style="font-size:{pt(9)}cqw;color:#f6f3ec">{first[k]:02d}</span><span>'
                     f'<span lang="en" style="font-size:{pt(15)}cqw;line-height:1.1;display:block">{e(t)}</span>'
                     f'<span class="cap" style="color:#e4e0d6">{e(ko_)}</span></span></div>' for t, ko_, k in lines if first.get(k))
    pages[0]["html"] = pages[0]["html"].replace("CLINES", clines, 1)
    used = {}
    for p in pages:
        for t in re.findall(r'data-technique="([a-z_]+)"', p["html"]):
            used.setdefault(t, [])
            if p["n"] not in used[t]:
                used[t].append(p["n"])
    # structural, not a tag: every inner page is laid on the mirrored grid (QA measures each block against X(col, side))
    used["mirrored_margins"] = [p["n"] for p in pages if p["kind"] not in ("cover", "back")]
    techs = "".join(f'<p><span style="color:var(--ink)">{e(TECHNIQUES[t][0])}<br><span style="color:var(--grey)">{e(TECHNIQUES[t][1])}</span></span>'
                    f'<span style="white-space:nowrap">{", ".join(f"{n:02d}" for n in used.get(t, [])[:6])}</span></p>' for t in TECHNIQUES)
    notused = "".join(f'<p style="margin-bottom:.4em"><b>{e(k)}</b>{e(v)}</p>' for k, v in NOT_USED.items())
    tp = next(p for p in pages if p["label"] == "notes")
    tp["html"] = tp["html"].replace("TECHS", techs, 1).replace("NOTUSED", f'<p class="kicker" lang="en" style="margin-bottom:.6em">Not used</p>{notused}', 1)
    ref_html = "".join(f'<li id="lref-{n}" value="{n}"><span lang="en">{e(src[s_]["title"])}</span> — {e(src[s_]["url"])} (검색 결과의 조각만 확인)</li>'
                       for s_, n in sorted(refs.items(), key=lambda kv: kv[1]))
    body = "".join(p["html"] for p in pages).replace('<ol class="refs">REFS</ol>', f'<ol class="refs">{ref_html}</ol>')
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(spec["title"])}</title><style>{css()}</style></head><body>{duotone_svg()}<main>{body}</main><script>{R.QA_JS}</script></body></html>')
    (out / "fonts").mkdir(exist_ok=True)
    for _, _, fn, _ in FACES:
        if (FONT_DIR / fn).is_file() and not (out / "fonts" / fn).is_file():
            (out / "fonts" / fn).write_bytes((FONT_DIR / fn).read_bytes())
    for lic in ("LICENSE-Pretendard.txt", "LICENSE-NotoSerifCJK.txt"):
        if (FONT_DIR / lic).is_file():
            (out / "fonts" / lic).write_bytes((FONT_DIR / lic).read_bytes())
    hp = out / "index.html"
    hp.write_text(doc, encoding="utf-8")
    pres = PDF.render(hp, out / "magazine.pdf") if pdf else None
    checks = qa(spec, pages, hp, pres, meas, assets, bad_text, missing, pdf, first, used, measured_accent)
    QA.save(checks, out, spec["title"])
    (out / "photos.json").write_text(json.dumps(meas, ensure_ascii=False, indent=1), encoding="utf-8")
    A.save(list(assets.values()), out / "assets.json")
    (out / "techniques.json").write_text(json.dumps({t: {"name": TECHNIQUES[t][0], "source": TECHNIQUES[t][1], "pages": used.get(t, [])}
                                                     for t in TECHNIQUES}, ensure_ascii=False, indent=1), encoding="utf-8")
    ranking = sorted((k for k in meas if not meas[k].get("missing")), key=lambda k: -meas[k]["strength"])
    return {"dir": str(out), "html": str(hp), "pdf": (pres or {}).get("path"), "pdf_result": pres, "pages": len(pages),
            "verdict": QA.verdict(checks), "checks": checks, "measured_cover_rank": ranking[:5], "measures": meas,
            "accent": {"catalogue": ACCENT_RAW, "text": ACCENT_TEXT, "measured_cover": measured_accent}, "techniques": used}


KO_SPACING = re.compile(r"[A-Za-z0-9’”')\]] (은|는|이|가|을|를|의|에|에서|에는|도|로|으로|와|과)(?=[\s.,·])")
MIN_TECHNIQUES = 20


def qa(spec, pages, html_path, pres, meas, assets, bad_text, missing, want_pdf, first, used, measured_accent) -> list:
    C = QA._c
    out = [C("content", "user texts are verbatim from docs/portfolio", "FAIL" if bad_text else "PASS", "; ".join(bad_text[:4]) or "cover · intro · manifesto · Q&A · back"),
           C("content", "every photo in the spec is on disk", "FAIL" if missing else "PASS", ", ".join(missing) or f"{len(assets)} photos"),
           C("content", "every photo is printed with the user's rights", "PASS" if all(A.publishable(a) for a in assets.values()) else "FAIL",
             f"rights '{spec['rights']}', credit '{spec['credit']}'")]
    shown = {k for p in pages for k in p["photos"]}
    out.append(C("content", "every photo appears", "PASS" if shown >= set(assets) else "FAIL", f"{len(shown)} of {len(assets)}"))
    from gentle_monster.magazine import drift as D
    try:
        D.guard_text(" ".join(r["text"] for r in spec["lens"]["reading"]))
        out.append(C("content", "the lens page states no fiction as brand fact", "PASS"))
    except D.ContradictionError as ex:
        out.append(C("content", "the lens page states no fiction as brand fact", "FAIL", str(ex)))
    out.append(C("content", "brand claims on the lens page read in full", "WARNING", "all cited claims are search snippets"))
    # mood: the catalogue's tokens are the page's tokens
    html_text = Path(html_path).read_text(encoding="utf-8")
    toks = spec.get("mood_reference", {}).get("tokens", {})
    miss = [f"{k} {v}" for k, v in toks.items() if v.lower() not in html_text.lower()]
    out.append(C("mood", "VISUAL INDEX tokens are the page's tokens", "FAIL" if miss or not toks else "PASS",
                 ", ".join(miss) or ", ".join(f"{k} {v}" for k, v in toks.items())))
    import numpy as np
    ratios = []
    for k, a in assets.items():                         # measured on the files as printed, against the source
        sv = lambda pth: float(np.asarray(PH._load(pth, 300).convert("HSV"))[..., 1].mean())
        s0 = sv(meas[k]["path"])
        if s0 > 8:                                       # a grey photo has nothing to desaturate
            ratios.append(sv(a["local_path"]) / s0)
    mr = sum(ratios) / len(ratios) if ratios else 0
    out.append(C("mood", "photos at the catalogue's saturate(.78) (measured on the files)", "PASS" if 0.72 <= mr <= 0.86 else "FAIL",
                 f"mean saturation ratio {mr:.2f} over {len(ratios)} colour photos"))
    import colorsys
    hue = lambda hx: colorsys.rgb_to_hls(*(int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)))[0]
    dh = abs(hue(ACCENT_RAW) - hue(measured_accent["raw"])) * 360
    out.append(C("mood", "catalogue red agrees with the cover photo's measured red", "PASS" if min(dh, 360 - dh) <= 15 else "WARNING",
                 f"{ACCENT_RAW} vs measured {measured_accent['raw']}: hue apart {min(dh, 360 - dh):.1f}°"))
    # techniques
    absent = [t for t in TECHNIQUES if t not in used]
    out.append(C("techniques", "every registered technique is on a page", "FAIL" if absent else "PASS", ", ".join(absent) or f"{len(used)} techniques"))
    out.append(C("techniques", f"at least {MIN_TECHNIQUES} techniques in use", "PASS" if len(used) >= MIN_TECHNIQUES else "FAIL", str(len(used))))
    # structure
    order = [p["label"] for p in pages]
    story_ok = all(first.get(s["id"]) for s in spec["story"]) and [first[s["id"]] for s in spec["story"]] == sorted(first[s["id"]] for s in spec["story"])
    out.append(C("structure", "story sections appear in the spec's order", "PASS" if story_ok else "FAIL", " → ".join(dict.fromkeys(order))))
    day_end, night_at = max((p["n"] for p in pages if p["label"] == "day"), default=0), first.get("night", 0)
    out.append(C("structure", "the night stop comes after the day", "PASS" if 0 < day_end < night_at else "FAIL", f"day ends p{day_end}, night p{night_at}"))
    toc_bad = [n for n in re.findall(r'href="#p(\d\d)"', html_text.split("</section>", 2)[1]) if f'id="p{n}"' not in html_text]
    out.append(C("structure", "contents page numbers point at real pages", "FAIL" if toc_bad else "PASS", ", ".join(toc_bad)))
    out.append(C("structure", "even page count (spreads close)", "PASS" if len(pages) % 2 == 0 else "FAIL", str(len(pages))))
    # typography (text level)
    vis = re.sub(r"<[^>]+>", " ", html_text.split("<main>", 1)[-1].split("<script>", 1)[0])
    sp = sorted(set(m.group(0) for m in KO_SPACING.finditer(html.unescape(vis))))
    out.append(C("typography", "no space between a Latin word and its Korean particle", "FAIL" if sp else "PASS", ", ".join(sp[:6])))
    out.append(C("typography", "curly quotes, no straight quotes in Korean text", "FAIL" if re.search(r"[가-힣][^<]{0,40}'[^<]{0,40}'", html.unescape(vis)) else "PASS"))
    out.append(C("production", "independence line", "PASS" if "독립 콘셉트 매거진" in html_text else "FAIL"))
    from gentle_monster.magazine import design as DS
    cr = {"ink/paper": DS.contrast(INK, PAPER), "grey/paper": DS.contrast(GREY, PAPER), "accent-text/paper": DS.contrast(ACCENT_TEXT, PAPER),
          "night-ink/night": DS.contrast(NIGHT_INK, NIGHT)}
    out.append(C("colour", "text contrast", "PASS" if min(cr.values()) >= 4.5 else "FAIL", ", ".join(f"{k} {v}" for k, v in cr.items())))
    acc_uses = html_text.count("var(--accent-text)") + html_text.count('class="eyebrow"')
    out.append(C("colour", "the red is used sparingly", "PASS" if acc_uses <= 14 else "WARNING", f"{acc_uses} uses"))
    if not PDF.available():
        out.append(C("production", "browser measurements", "NOT_CHECKED", "Chromium not available"))
    else:
        pr = PDF.measure(html_path, 869, 1134, "qa-print")
        mob = PDF.measure(html_path, 375, 800, "qa")
        if not pr.get("ok"):
            out.append(C("production", "HTML renders in a browser", "FAIL", pr.get("error")))
        else:
            P = pr["pages"]
            out.append(C("production", "HTML renders in a browser", "PASS", f"{len(P)} pages"))
            clash = [f"p{p['i']}: {c_}" for p in P for c_ in p.get("clash", [])]
            out.append(C("layout", "no text block overlaps another (print size)", "FAIL" if clash else "PASS", "; ".join(clash[:4]) or "none"))
            over = [f"p{p['i']}" for p in P if p["overflow"] or p["self_scroll"]]
            out.append(C("layout", "text overflow at print size", "FAIL" if over else "PASS", ", ".join(over) or "none"))
            off = [f"p{p['i']}:c{c_['col']:g}{c_['mirror']}{c_['x'] - X(c_['col'], c_['mirror'] or 'r'):+.2f}" for p in P for c_ in p.get("cols", [])
                   if abs(c_["x"] - X(c_["col"], c_["mirror"] or "r")) > 0.3]
            wrong_side = [f"p{p['i']}" for p in P for c_ in p.get("cols", []) if c_["mirror"] and c_["mirror"] != ("l" if p["i"] % 2 == 0 else "r")]
            out.append(C("layout", "every block uses its own page side's margins (mirrored)", "FAIL" if wrong_side else "PASS",
                         ", ".join(sorted(set(wrong_side))[:6]) or f"inner {INNER * 2.3:.0f} mm · outer {OUTER * 2.3:.0f} mm"))
            n_cols = sum(len(p.get("cols", [])) for p in P)
            out.append(C("layout", "blocks sit on the mirrored 12-column grid (±0.3 cqw)", "FAIL" if off else "PASS", ", ".join(off[:6]) or f"{n_cols} blocks"))
            faux = []
            for p in P:
                for f in p.get("faux", []):
                    w_, fam, txt = (f.split("|", 2) + ["", ""])[:3]
                    fam_ko = next((k for k in KO_WEIGHTS if k in (fam or "")), None)
                    # Hangul falls through Latin-first stacks to the Korean face: judge the Korean face the stack reaches
                    if fam_ko is None:
                        fam_ko = "Noto Serif KR" if fam in ("Caladea",) else "Pretendard"
                    if int(w_ or 0) not in KO_WEIGHTS[fam_ko]:
                        faux.append(f"p{p['i']}:{fam_ko} {w_} {txt}")
            out.append(C("typography", "Korean weights all have a real face (no faux bold)", "FAIL" if faux else "PASS",
                         ", ".join(faux[:4]) or "Pretendard 300–700 · Noto Serif KR 400/600"))
            loaded = set(pr.get("fonts", []))
            need = {f"{fam} {w}" for fam, w, _, _ in FACES}
            used_faces = {x for x in loaded if x.split(" ")[0] in ("Pretendard", "Noto")}
            out.append(C("typography", "vendored Korean fonts load in the browser", "PASS" if used_faces else "FAIL",
                         ", ".join(sorted(used_faces)) or f"none of {len(need)} faces loaded"))
            mins = min(p.get("minfs", 99) for p in P)
            out.append(C("typography", "smallest text at print size ≥ 6.5 pt", "PASS" if mins * 0.75 >= 6.5 else "FAIL", f"{mins * 0.75:.1f} pt"))
            broken = [i["src"] for p in P for i in p["images"] if not i["ok"]]
            out.append(C("image", "images load", "FAIL" if broken else "PASS", ", ".join(broken[:4]) or f"{sum(len(p['images']) for p in P)} placements"))
            dpis, crops = [], []
            for p in P:
                for i in p["images"]:
                    if i.get("nw") and i.get("rw"):
                        s = max(i["rw"] / i["nw"], i["rh"] / i["nh"]) if i["fit"] == "cover" else i["rw"] / i["nw"]
                        if i["fit"] == "cover":                         # share of the frame kept, on the file as placed
                            crops.append((round(i["rw"] * i["rh"] / (i["nw"] * s * i["nh"] * s), 2), p["i"]))
                        k_ = i.get("srcpx") or i["nw"]                  # dpi: judge the source, not the smoothed copy
                        s_src = s * i["nw"] / k_
                        dpis.append((round(96 / s_src), p["i"], round(k_ * PRINT_DPI_MIN * s_src / 96)))
            low = sorted(d for d in dpis if d[0] < PRINT_DPI_MIN)
            out.append(C("image", f"print resolution >= {PRINT_DPI_MIN} dpi", "FAIL" if low else "PASS",
                         (f"{len(low)} of {len(dpis)} placements below; lowest {low[0][0]} dpi (p{low[0][1]}). Source photos are "
                          f"{min(a['source_pixels'][0] for a in assets.values())} px wide -- print needs at least {max(d[2] for d in low)} px "
                          f"on the long edge. The web version is unaffected") if low else f"lowest {min(dpis)[0] if dpis else '—'} dpi"))
            heavy = sorted(c_ for c_ in crops if c_[0] < 0.4 and pages[c_[1] - 1]["kind"] not in ("spread",))
            out.append(C("image", "no photo cropped to less than 40% of its frame (spreads excepted)", "WARNING" if heavy else "PASS",
                         ", ".join(f"p{p_} keeps {f:.0%}" for f, p_ in heavy[:5]) or (f"smallest kept {min(crops)[0]:.0%}" if crops else "—")))
            han = [p for p in P if p["hangul"]]
            out.append(C("typography", "Hangul has a font", "PASS" if (used_faces or not han) else "FAIL",
                         "Pretendard + Noto Serif KR (vendored)" if used_faces else "only system fallback"))
        if mob.get("ok"):
            if mob["viewport"][0] != 375:
                out.append(C("layout", "phone width 375 px", "NOT_CHECKED", f"viewport {mob['viewport'][0]}"))
            else:
                out.append(C("layout", "phone width 375 px: no sideways scroll", "PASS" if mob["doc_scroll_w"] <= 375 else "FAIL",
                             f"document {mob['doc_scroll_w']}px"))
                mclash = [f"p{p['i']}: {c_}" for p in mob["pages"] for c_ in p.get("clash", [])]
                out.append(C("layout", "no text block overlaps another (375 px)", "FAIL" if mclash else "PASS", "; ".join(mclash[:4]) or "none"))
    if want_pdf:
        ok = pres and pres.get("ok") and pres["pages"] == len(pages)
        out.append(C("production", "PDF output", "PASS" if ok else "FAIL",
                     f"{(pres or {}).get('pages')} PDF pages for {len(pages)}" if pres and pres.get("ok") else (pres or {}).get("error", "not built")))
    return out
