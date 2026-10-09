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
# Mood: the VISUAL INDEX catalogue (spec "mood_reference") -- warm paper, green-black ink, serif display over sans
#   metadata in tracked capitals, ink rules over captions, photographs at saturate(.78), one red.
# ① Layout: 230 x 300 mm, 12 columns, 8 cqw margins, 2 cqw gutters; blocks sit on column lines (QA measures).
# ② Type: serif display (Georgia in the catalogue; Liberation Serif here), sans metadata, Korean in WenQuanYi
#    (one weight -- never bold). Sizes from one scale.
# ③ Image: native aspect unless a technique says otherwise; focal points for crops; print dpi and crop share measured.
# ④ Colour: catalogue tokens; small text in the catalogue's #555850 and a darkened accent, both >= 4.5:1.
# ⑤ Structure: spec "story". Every technique is tagged data-technique and listed, with its source, on the
#    techniques page -- QA checks each registered technique is really on a page.
MARGIN, GUTTER, COLS = 8.0, 2.0, 12
COL = (100 - 2 * MARGIN - (COLS - 1) * GUTTER) / COLS            # 5.1667 cqw
PAGE_H = 100 * H_MM / W_MM                                       # 130.43 cqw
TYPE = {"cap": 1.15, "body": 1.6, "lead": 2.3, "title": 4.2, "display": 9.0, "word": 12.0}
PAPER, INK, MUTE_RAW, LINE, ACCENT_RAW, GREY = "#f3f0e8", "#1e211e", "#73766e", "#c9c7bd", "#c64c32", "#555850"
NIGHT, NIGHT_INK = "#141614", "#ece8de"
INK_TEXT = GREY            # small grey text: the catalogue's own body grey (6.4:1), not #73766e (4.06:1)

# technique id -> (name, where it comes from)
TECHNIQUES = {
    "masthead_overlap": ("마스트헤드 오버랩 — 제호가 사진 위에 놓인다", "매거진 URL 카탈로그 · 레이아웃"),
    "masthead_top": ("마스트헤드 상단 배치", "매거진 URL 카탈로그 · 레이아웃 (12/29)"),
    "coverlines": ("커버라인", "매거진 URL 카탈로그 · 레이아웃 (7/29)"),
    "full_bleed": ("풀블리드", "매거진 URL 카탈로그 · 레이아웃 (14/29)"),
    "white_space": ("화이트 스페이스 · 넓은 마진", "매거진 URL 카탈로그 · 레이아웃"),
    "text_page": ("텍스트 중심 지면", "매거진 URL 카탈로그 · 레이아웃"),
    "asymmetric": ("비대칭 레이아웃 — 7/5 · 5/7 단", "매거진 URL 카탈로그 + VISUAL INDEX 격자"),
    "grotesk_caps": ("그로테스크 올캡스 · 넓은 트래킹", "매거진 URL 카탈로그 · 타이포그래피 + VISUAL INDEX 메타데이터"),
    "serif_display": ("세리프 디스플레이 + 산세리프 메타데이터", "VISUAL INDEX · Typography"),
    "experimental_type": ("실험적 타이포그래피 — 세운 글줄", "매거진 URL 카탈로그 · 타이포그래피"),
    "image_in_type": ("글자 속 이미지 — 사진으로 채운 낱말", "편집자 추가 (고전 기법)"),
    "closeup": ("클로즈업 — 한 장을 세 번 당겨 보기", "매거진 URL 카탈로그 · 이미지 (3/29)"),
    "contact_sheet": ("밀착 인화 · 갤러리 벽", "MCA 레퍼런스 보드"),
    "caption_line": ("캡션 라인 — 위에 괘선, 양 끝 정렬, Fig. 번호", "VISUAL INDEX · Image treatment"),
    "desaturate": ("채도 낮추기 saturate(.78)", "VISUAL INDEX · hero/이미지"),
    "pill_tags": ("태그 칩", "VISUAL INDEX · tags (낱말은 무드보드 색인의 분위기 8개)"),
    "section_head": ("섹션 머리 — 잉크 괘선 + 세리프 제목 + 작은 대문자 라벨", "VISUAL INDEX · section-head"),
    "split_spread": ("두 쪽에 걸친 한 장", "MCA 레퍼런스 보드"),
    "show_through": ("비침 — 뒷장 단어를 좌우 반전해 10%", "docs/portfolio/02_picture.md (사용자 지시)"),
    "duotone": ("듀오톤 — 잉크와 시그니처 레드", "매거진 URL 카탈로그 · 색상 ‘시그니처 레드’ + 편집자 추가"),
    "chromatic_timeline": ("색의 연대기 — 잰 팔레트를 밝기 순서로", "편집자 추가 (측정 데이터의 시각화)"),
    "pull_quote": ("풀쿼트", "편집자 추가 (고전 기법)"),
    "drop_cap": ("드롭캡", "편집자 추가 (고전 기법)"),
    "specs_grid": ("사양 격자 — 빨간 라벨", "VISUAL INDEX · manifesto/specs"),
    "footer_band": ("어두운 하단 띠", "VISUAL INDEX · footer"),
    "data_table": ("측정 색인 표", "편집자 추가"),
    "grain": ("필름 그레인 — 사진 위의 고운 입자", "편집자 추가 (무드)"),
    "newsstand": ("가판대 표지 — 커버라인과 쪽 번호, 호수 · 계절, 바코드 칸", "매거진 URL 카탈로그 · 커버라인 + 판매 잡지의 관례"),
    "scrim": ("스크림 — 사진 위 글자를 위한 그라데이션", "편집자 추가 (가독성)"),
}
NOT_USED = {"디돈 세리프 · 고대비 획": "이 환경에 디돈 글꼴이 없다 — 가짜로 흉내 내지 않는다",
            "셀러브리티 커버 · 스튜디오 · 포트레이트": "사진의 성격(거리 · 바다 · 밤의 스냅숏)과 다르다",
            "모노그램 마스트헤드 · 핸드레터링": "제호 SPA는 사용자가 확정한 글자다(cover.md)"}


def X(c: float) -> float:
    return round(MARGIN + c * (COL + GUTTER), 3)


def SPAN(n: int) -> float:
    return round(n * COL + (n - 1) * GUTTER, 3)


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


def smooth_copy(src: Path, dst: Path, factor: int = 3) -> None:
    """A display copy resampled (Lanczos) so viewers that scale with nearest-neighbour do not show stair-steps.
    It adds no detail: print resolution is still judged on the source pixels (data-srcpx), never on this copy."""
    from PIL import Image, ImageFilter
    im = Image.open(src).convert("RGB")
    if im.width < 1600:
        im = im.resize((im.width * factor, im.height * factor), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))
    im.save(dst, "JPEG", quality=90, optimize=True)


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
            f'<text x="{w / 2:.0f}" y="{base}" text-anchor="middle" font-family="Liberation Serif, Georgia, serif" font-weight="700" '
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


def css() -> str:
    ko = '"WenQuanYi Zen Hei","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic"'
    T = TYPE
    return f"""
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTE_RAW};--line:{LINE};--accent:{ACCENT_RAW};--accent-text:{ACCENT_TEXT};--grey:{GREY};
  --night:{NIGHT};--night-ink:{NIGHT_INK};
  --serif:"Liberation Serif",Georgia,"Times New Roman",{ko},serif;--sans:"Liberation Sans",Arial,Helvetica,{ko},sans-serif}}
*{{box-sizing:border-box;font-synthesis:none}} html{{background:#2b2c29}}
body{{margin:0;color:var(--ink);font-family:var(--sans);word-break:keep-all;overflow-wrap:break-word;-webkit-font-smoothing:antialiased;
  font-kerning:normal;text-rendering:optimizeLegibility}}
main{{display:flex;flex-wrap:wrap;justify-content:center;padding:28px 0}}
.page{{container-type:inline-size;position:relative;overflow:hidden;background:var(--paper);width:min(46vw,560px);aspect-ratio:{W_MM}/{H_MM};margin-bottom:32px}}
.page.night{{background:var(--night);color:var(--night-ink)}}
.page.cover{{margin-right:46vw}} @media (max-width:1100px){{.page{{width:min(100vw - 32px,560px)}} .page.cover{{margin-right:0}}}}
.a{{position:absolute}} p{{margin:0}}
img{{display:block;width:100%;height:100%;object-fit:cover;filter:saturate(.78)}} img.nat{{height:auto;aspect-ratio:468/258}}
.duo img{{filter:url(#duotone)}}
/* type */
.cap{{font-size:max({T['cap']}cqw,8.5px);line-height:1.45;color:var(--grey);letter-spacing:.01em}}
.caps{{text-transform:uppercase;letter-spacing:.12em}}
.body{{font-size:max({T['body']}cqw,10.5px);line-height:1.72}} .en{{line-height:1.5}}
.lead{{font-size:{T['lead']}cqw;line-height:1.6;letter-spacing:-.01em}}
.serif{{font-family:var(--serif);font-weight:400}}
.title{{font-family:var(--serif);font-size:{T['title']}cqw;line-height:1;letter-spacing:-.04em;font-weight:400}}
.display{{font-family:var(--serif);font-size:{T['display']}cqw;line-height:.86;letter-spacing:-.06em;font-weight:400}}
.eyebrow{{color:var(--accent-text);font-size:max({T['cap']}cqw,8.5px);letter-spacing:.18em;text-transform:uppercase;font-weight:700}}
.night .cap{{color:#a9a69c}}
/* components (VISUAL INDEX) */
.rh{{top:4.6cqw;left:{X(0)}cqw;right:{MARGIN}cqw;display:flex;justify-content:space-between}}
.sh{{border-top:1px solid var(--ink);padding-top:1.5cqw;display:flex;justify-content:space-between;align-items:baseline;gap:2cqw}}
.cl{{border-top:1px solid var(--ink);margin-top:.9cqw;padding-top:.7cqw;display:flex;justify-content:space-between;gap:1cqw;
  font-size:max(1.1cqw,8.5px);letter-spacing:.09em;text-transform:uppercase;color:var(--ink)}}
.night .cl{{border-color:#5d5e58;color:var(--night-ink)}}
.pill{{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:.3cqw .75cqw;font-size:max(1.05cqw,8.5px);color:var(--grey);margin-top:.8cqw}}
.specs{{display:grid;grid-template-columns:1fr 1fr;column-gap:{GUTTER}cqw;row-gap:1.4cqw}} .specs div{{border-top:1px solid var(--line);padding-top:.8cqw}}
.specs b{{display:block;color:var(--accent-text);text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4cqw;font-weight:700}}
.band{{left:0;right:0;bottom:0;background:var(--ink);color:var(--paper);padding:2.2cqw {MARGIN}cqw;display:flex;justify-content:space-between;gap:2cqw}}
.folio{{position:absolute;bottom:4.6cqw;font-size:{T['cap']}cqw;color:var(--grey);font-variant-numeric:tabular-nums}}
.folio.l{{left:{X(0)}cqw}} .folio.r{{right:{MARGIN}cqw}}
.mast-ov{{color:#f6f3ec;font-family:var(--serif);font-weight:400;line-height:.8;letter-spacing:-.075em;white-space:nowrap}}
.itype{{font-family:var(--serif);font-weight:700;color:transparent;-webkit-background-clip:text;background-clip:text;background-size:cover;
  line-height:.8;letter-spacing:-.04em;white-space:nowrap}}
.dropcap::first-letter{{font-family:var(--serif);float:left;font-size:4.4em;line-height:.78;margin:.04em .08em 0 0;color:var(--ink)}}
sup{{font-size:.68em;line-height:0;vertical-align:.5em;margin-left:.08em}} sup a{{color:inherit;text-decoration:none}}
.refs{{margin:0;padding:0 0 0 2.4cqw}} .refs li{{margin-bottom:.5cqw}} .refs a{{color:inherit;text-decoration:none;word-break:break-all}}
.mani{{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;font-family:var(--serif);font-size:6.8cqw;line-height:1.12;letter-spacing:-.03em}}
.mani sup{{font-family:var(--sans);font-size:.3em;vertical-align:0;margin:0 0 .4em 0;color:var(--accent-text)}}
.split{{top:0;height:100%;width:200%}} .split.l{{left:0}} .split.r{{left:-100%}}
.ghost{{opacity:.1;transform:scaleX(-1)}}
.box{{border:1px solid rgba(255,255,255,.9);color:#fff;background:rgba(15,16,14,.24)}}
.row{{display:grid;grid-template-columns:{COL}cqw {SPAN(2)}cqw {SPAN(5)}cqw {SPAN(2)}cqw {COL}cqw {COL}cqw;column-gap:{GUTTER}cqw;
  align-items:baseline;border-bottom:1px solid var(--line);padding:1.2cqw 0}}
.row.h{{border-bottom:1px solid var(--ink);padding-top:0}}
.trow{{display:grid;grid-template-columns:{SPAN(5)}cqw {SPAN(5)}cqw {SPAN(2)}cqw;column-gap:{GUTTER}cqw;border-bottom:1px solid var(--line);padding:.85cqw 0;align-items:baseline}}
.tech .trow{{padding:.45cqw 0;line-height:1.3}}
.sw{{display:inline-block;width:1.5cqw;height:1.5cqw;margin-right:.35cqw;vertical-align:-.25cqw}}
.zoom{{overflow:hidden;position:relative;background:#ddd8cc}} .zoom img{{position:absolute;height:auto;max-width:none}}
.num{{font-variant-numeric:tabular-nums}}
.grain{{position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply;opacity:.22;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.1 -.2'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");background-size:22cqw 22cqw}}
.scrim-t{{position:absolute;left:0;right:0;top:0;height:46%;background:linear-gradient(rgba(10,11,10,.42),rgba(10,11,10,0))}}
.scrim-b{{position:absolute;left:0;right:0;bottom:0;height:52%;background:linear-gradient(rgba(10,11,10,0),rgba(10,11,10,.72))}}
.on-photo{{color:#f6f3ec}} .on-photo .cap{{color:#e4e0d6}}
.cline{{border-top:1px solid rgba(246,243,236,.75);padding:.8cqw 0 1.1cqw;display:grid;grid-template-columns:{SPAN(1)}cqw 1fr;column-gap:1cqw;align-items:baseline}}
.barcode{{background:#fff;padding:1.2cqw 1.4cqw .8cqw;color:#111}} .barcode svg{{display:block;width:100%;height:5.4cqw}}
@media (hover:hover){{ .hz img{{transition:transform .6s cubic-bezier(.2,.7,.2,1)}} .hz:hover img{{transform:scale(1.035)}} }}
@media (max-width:600px){{
  .page.text{{aspect-ratio:auto;padding:32px 20px 56px}} .page.text .a{{position:static;width:auto!important;transform:none;margin-bottom:18px}}
  .page.text .body{{font-size:15px}} .page.text .lead{{font-size:18px}} .page.text .title{{font-size:26px}} .page.text .display{{font-size:34px}}
  .page.text .cap,.page.text .cl{{font-size:12px}} .page.text .folio{{font-size:12px;bottom:18px}}
  .page.text .mani{{writing-mode:horizontal-tb;font-size:26px;white-space:normal}}
  .page.cover{{aspect-ratio:auto;min-height:133cqw;padding:58cqw 20px 28px}}
  .page.cover .a:not(.mast-ov):not([data-bleed]):not(.rh){{position:static;width:auto!important;margin:0 0 18px}}
  .page.text .row{{grid-template-columns:32px 1fr 64px;font-size:13px}} .page.text .row > :nth-child(2),.page.text .row > :nth-child(5),
  .page.text .row > :nth-child(6){{display:none}} .page.text .trow{{grid-template-columns:1fr 1fr;font-size:13px}} .page.text .trow > :nth-child(3){{display:none}}
 
}}
@page{{size:{W_MM}mm {H_MM}mm;margin:0}}
@media print{{ html{{background:none}} main{{display:block;padding:0}} .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;margin:0;break-after:page}}
  *{{-webkit-print-color-adjust:exact;print-color-adjust:exact}} }}
html.print-sim main{{display:block;padding:0;width:{W_MM}mm}} html.print-sim .page{{width:{W_MM}mm;height:{H_MM}mm;aspect-ratio:auto;margin:0}}
"""


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

    def img(n, pos=None):
        k = _k(n)
        if k not in assets:
            return f'<div class="cap">사진 {k} 없음</div>'
        return (f'<img src="{e(src_of(k))}" alt="{e(spec["photos"][k])}" data-photo="{k}" data-srcpx="{assets[k]["source_pixels"][0]}" '
                f'style="object-position:{pos or focus.get(k, "50% 50%")}">')

    def at(col, top, span=None, cls="", inner="", right=None, bottom=None, extra="", tech=""):
        pos = f"left:{X(col)}cqw;" + (f"top:{top}cqw;" if top is not None else "") + (f"bottom:{bottom}cqw;" if bottom is not None else "")
        pos += f"width:{SPAN(span)}cqw;" if span else ""
        pos += f"right:{right}cqw;" if right is not None else ""
        t = f' data-technique="{tech}"' if tech else ""
        return f'<div class="a {cls}" data-col="{col}"{t} style="{pos}{extra}">{inner}</div>'

    def photo(n, col, top, span, left_cap=None, right_cap=None, pill=True, h=None):
        k = _k(n)
        hh = h or round(SPAN(span) / (468 / 258), 3)
        lc = left_cap if left_cap is not None else f"Fig. {k}"
        rc = right_cap if right_cap is not None else e(meas[k]["light"])
        chip = (f'<span class="pill" data-technique="pill_tags">{e(moods[k])}</span>' if pill and k in moods else "")
        return at(col, top, span, "hz", f'<div style="height:{hh}cqw;overflow:hidden" data-technique="desaturate">{img(n)}</div>'
                  f'<div class="cl num" data-technique="caption_line"><span>{lc}</span><span>{rc}</span></div>{chip}')

    def head(title, label, top=10.5, col=0, span=12, lang="en"):
        return at(col, top, span, "", f'<div class="sh"><p class="title" lang="{lang}">{e(title)}</p><p class="cap caps" lang="en">{e(label)}</p></div>',
                  tech="section_head")

    pages, refs = [], {}

    def cite(ids):
        out_ = []
        for i in ids:
            for s_ in claims.get(i, {}).get("source_ids", [])[:1]:
                n = refs.setdefault(s_, len(refs) + 1)
                out_.append(f'<a href="#lref-{n}">{n}</a>')
        return f"<sup>{','.join(out_)}</sup>" if out_ else ""

    def page(inner, cls="", kind="photo", photos=(), label="", rh=None):
        n = len(pages) + 1
        side = "l" if n % 2 == 0 else "r"
        fol = "" if kind in ("cover", "back") else (f'<div class="folio {side} num caps" lang="en">' + (f'{n:02d}&emsp;{e(spec["masthead"])} — Autumn 2026'
              if side == "l" else f'{e(spec["masthead"])} — Autumn 2026&emsp;{n:02d}') + '</div>')
        hd = (f'<div class="a rh cap caps" lang="en"><span>{e(spec["masthead"])} 00</span><span>{e(rh)}</span></div>') if rh else ""
        pages.append({"n": n, "kind": kind, "label": label, "photos": [_k(p) for p in photos], "side": side,
                      "html": f'<section class="page {cls}" id="p{n:02d}" data-type="{kind}" data-label="{e(label)}">{hd}{inner}{fol}</section>'})

    c = spec["cover"]
    T = TYPE
    # 1 cover -- newsstand: full bleed, masthead over the photograph, cover lines with page numbers -------------------
    lines = [("15 Stops", "열다섯 번 멈춘 자리", "stops"), ("Looking Closer", "한 장을 세 번", "closer"),
             ("Night", "빨간불 앞에서 멈춘다", "night"), ("Manifesto", "사람과 공간 사이", "manifesto"),
             ("The Gentle Monster Lens", "왜 이 표지인가", "lens")]
    page(f'<div class="a" style="inset:0" data-bleed data-technique="full_bleed">{img(cov, pos=spec.get("cover_focus", "80% 55%"))}'
         f'<div class="grain" data-technique="grain"></div><div class="scrim-t" data-technique="scrim"></div><div class="scrim-b"></div></div>'
         + f'<div class="a rh cap caps on-photo" lang="en" data-technique="masthead_top" style="border-bottom:1px solid rgba(246,243,236,.75);padding-bottom:1cqw">'
           f'<span>Issue 00 — Autumn 2026</span><span>Independent concept magazine</span></div>'
         + f'<div class="a mast-ov" lang="en" data-bleed data-technique="masthead_overlap" style="left:{X(0) - 1.6}cqw;top:7cqw;font-size:46cqw">'
           f'{e(spec["masthead"])}</div>'
         + at(0, 46, 4, "cap caps on-photo", '<p lang="en" style="color:#f6f3ec;line-height:1.7">' + "<br>".join(e(x) for x in c["left"]) + "</p>",
              tech="grotesk_caps")
         + at(7, 46, 5, "on-photo", "CLINES", tech="newsstand")
         + at(0, None, 8, "on-photo", f'<p class="serif" lang="en" data-technique="serif_display" style="font-size:{T["title"] * 1.5:.2f}cqw;line-height:.98;letter-spacing:-.035em;margin-bottom:2.2cqw">'
              f'“{e(c["question"])}”</p><p class="lead serif" lang="en" style="line-height:1.32;margin-bottom:2.4cqw">' + "<br>".join(e(x) for x in c["right"])
              + f'</p><p class="cap caps" lang="en" style="color:#f6f3ec">' + " ".join(e(x) for x in c["byline"]) + "</p>", bottom=8, tech="coverlines")
         + at(9, None, 3, "barcode", f'{barcode_svg("SPA-00")}<p class="cap caps num" lang="en" style="color:#111;margin-top:.5cqw;font-size:max(1.1cqw,8.5px)">'
              f'SPA-00 · Concept issue<br>Not for sale</p>', bottom=8),
         "cover", "cover", [cov], "표지")
    # 2 contents | 3 intro -----------------------------------------------------------------------------------------
    specs = [("Format", f"인쇄 {W_MM} × {H_MM} mm · 반응형 HTML"), ("Grid", "12단 · 휴대폰에서 한 단"),
             ("Typography", "세리프 디스플레이 + 산세리프 메타데이터"), ("Image treatment", "원래 비율 · 크롭 · 캡션 · 대체 텍스트 · 채도 .78"),
             ("Mood", "VISUAL INDEX 카탈로그"), ("Words & photographs", spec["credit"].split(": ")[-1])]
    page(head("Contents", "Catalogue / 01—22") + at(0, 20, 12, "", "TOC")
         + at(0, None, 12, "cap specs", "".join(f'<div><b lang="en">{e(k)}</b>{e(v)}</div>' for k, v in specs), bottom=10, tech="specs_grid"),
         "text", "contents", [], "Contents", rh="Contents")
    it = spec["intro"]
    first_sentence = it["en"].split(". ")[0] + "."
    page(head("Introduction", "Picture / 02") +
         at(0, 22, 11, "display", f'<p lang="en">“{e(first_sentence)}”</p>', tech="pull_quote")
         + at(5, 72, 7, "lead", "".join(f'<p style="margin-bottom:.8em">{e(x)}</p>' for x in it["ko"]), tech="text_page")
         + at(5, 104, 7, "body en serif", f'<p lang="en" class="dropcap" data-technique="drop_cap" style="font-size:1.12em">{e(it["en"])}</p>')
         + at(0, 72, 4, "cap", f'<p class="eyebrow" lang="en">Introduction</p><p style="margin-top:1em">{e(spec["credit"])}</p>', tech="white_space"),
         "text", "intro", [], "Introduction", rh="Introduction")
    # 4-5 15 stops (contact sheet) -----------------------------------------------------------------------------------
    ks = sorted(k for k in spec["photos"] if k in assets)
    half = (len(ks) + 1) // 2
    st = story["stops"]
    for side, chunk in (("l", ks[:half]), ("r", ks[half:])):
        cols = (0, 6) if side == "l" else (1, 7)
        hd = head(st["en"], "Fig. 01—15") if side == "l" else head(st["ko"], "Contact sheet", col=1, span=11, lang="ko")
        th = round(SPAN(5) / (468 / 258), 3)
        cells = "".join(photo(k, cols[i % 2], 22 + (i // 2) * (th + 8.6), 5) for i, k in enumerate(chunk))
        page(f'<div data-technique="contact_sheet">{hd}{cells}</div>', "", "wall", chunk, "stops", rh=st["en"])
    # 6-7 day -> dusk (asymmetric 12 / 7 · 7 / 7 / 7, measured order) -------------------------------------------------
    seq = sorted(spec["sea_sequence"], key=lambda n: -meas[_k(n)].get("brightness", 0))
    d = story["day"]
    br = lambda n: f'밝기 {meas[_k(n)]["brightness"]:.2f}'
    page(head(d["en"], "Measured brightness ↓")
         + photo(seq[0], 0, 21, 12, right_cap=br(seq[0]))
         + at(0, 78, 4, "cap", f'<p>{e(d["ko"])}. 사진은 잰 밝기 순서로 놓였다 — 밝은 데서 어두운 데로.</p>', tech="asymmetric")
         + photo(seq[1], 5, 78, 7, right_cap=br(seq[1])),
         "", "sequence", seq[:2], "day", rh=d["en"])
    page(photo(seq[2], 0, 12, 7, right_cap=br(seq[2])) + photo(seq[3], 5, 50, 7, right_cap=br(seq[3]))
         + photo(seq[4], 0, 88, 7, right_cap=br(seq[4])),
         "", "sequence", seq[2:], "day", rh=d["en"])
    # 8 zoom | 9 chromatic timeline -----------------------------------------------------------------------------------
    z = spec["zoom"]
    zk = _k(z["photo"])
    cl = story["closer"]
    zh = round(SPAN(7) / (468 / 258), 3)
    frames = ""
    for i, sc in enumerate(z["scales"]):
        top = 22 + i * (zh + 6.4)
        w = sc * 100
        lx, ty = 50 - z["focus"][0] * w, 50 - z["focus"][1] * w * (258 / 468) * (SPAN(7) / zh)
        lx = max(min(lx, 0), 100 - w)
        ty = max(min(ty, 0), 100 - w * (258 / 468) * (SPAN(7) / zh))
        frames += (at(0, top, 4, "display num", f'<p lang="en">×{sc:g}</p>')
                   + at(5, top, 7, "", f'<div class="zoom" style="height:{zh}cqw"><img src="{e(src_of(zk))}" alt="{e(spec["photos"][zk])} (×{sc:g})" '
                        f'data-photo="{zk}" data-srcpx="{assets[zk]["source_pixels"][0]}" style="width:{w:.1f}%;left:{lx:.1f}%;top:{ty:.1f}%"></div>'
                        f'<div class="cl num"><span>Fig. {zk} × {sc:g}</span><span>{e(spec["photos"][zk]) if i == 0 else ("노 젓는 사람들" if i == 1 else "한 사람")}</span></div>',
                        tech="closeup"))
    page(head(cl["en"], "One photograph, three times") + frames, "text", "zoom", [z["photo"]], "closer", rh=cl["en"])
    order = sorted(ks, key=lambda k: -meas[k]["brightness"])
    bw = (SPAN(12) - (len(order) - 1) * 0.6) / len(order)
    bands = ""
    for i, k in enumerate(order):
        pal = meas[k].get("palette", [])
        tot = sum(sh for _, sh in pal) or 1
        stack = "".join(f'<div style="height:{sh / tot * 100:.2f}%;background:{hx}"></div>' for hx, sh in pal)
        bands += (f'<div class="a" style="left:{X(0) + i * (bw + 0.6):.3f}cqw;top:22cqw;width:{bw:.3f}cqw;height:84cqw;display:flex;flex-direction:column">{stack}</div>'
                  f'<div class="a cap num" style="left:{X(0) + i * (bw + 0.6):.3f}cqw;top:107.5cqw;width:{bw:.3f}cqw;text-align:center">{k}</div>')
    page(head("Colour of the Day", "Measured palettes, bright → dark") + f'<div data-technique="chromatic_timeline">{bands}</div>'
         + at(0, None, 8, "cap", f'<p>열다섯 장의 잰 색 — 사진마다 여섯 색과 그 비율을, 잰 밝기 순서로(왼쪽이 가장 밝다). '
              f'지면의 사진은 채도를 낮췄지만, 이 띠는 원본에서 잰 색이다.</p>', bottom=9, tech="data_table"),
         "", "timeline", [], "closer", rh=cl["en"])
    # 10-11 one to one (show-through) -----------------------------------------------------------------------------------
    ws = spec["words"]
    wh = round(SPAN(10) / (468 / 258), 3)
    for i, w in enumerate(ws):
        ghost = ws[i + 1]["word"] if i + 1 < len(ws) else ""
        page(at(1, 20, 10, "", f'<div style="height:{wh}cqw">{img(w["photo"])}</div>', tech="white_space")
             + (at(0, 76, 12, "ghost", f'<p style="font-size:{T["word"]}cqw;text-align:center;line-height:1">{e(ghost)}</p>', tech="show_through") if ghost else "")
             + at(0, 76, 12, "", f'<p style="font-size:{T["word"]}cqw;text-align:center;line-height:1;letter-spacing:-.02em">{e(w["word"])}</p>'),
             "", "word", [w["photo"]], "turn")
    # 12-13 night spread -----------------------------------------------------------------------------------------------
    ns = spec["night_spread"]
    nk = _k(ns)
    page(f'<div class="a split l" data-bleed data-technique="split_spread">{img(ns)}<div class="grain"></div></div>', "night", "spread", [ns], "night")
    page(f'<div class="a split r" data-bleed data-technique="full_bleed">{img(ns)}<div class="grain"></div></div>'
         + at(1, None, 6, "", f'<div class="cl num"><span>Fig. {nk}</span><span>{e(spec["photos"][nk])}</span></div>', bottom=8),
         "night", "spread", [ns], "night")
    # 14 stop (image in type) | 15 manifesto ------------------------------------------------------------------------------
    so = story["stop"]
    page(head(so["en"], "Fig. " + nk + " in the letters")
         + at(0, 36, 12, "", image_in_type("STOP", src_of(nk), band=(0.40, 0.86)), tech="image_in_type")
         + at(0, 74, 6, "cap", f'<p class="eyebrow" lang="en">Fig. {nk} — red light</p><p style="margin-top:.8em">{e(so["ko"])}. '
              f'글자를 밤 사진으로 채웠다 — 낱말이 곧 장면이다.</p>'),
         "", "stop", [ns], "stop", rh=so["en"])
    mf = spec["manifesto"]
    page(f'<div class="a mani" lang="en" data-col="1" data-technique="experimental_type" style="left:{X(1)}cqw;bottom:14cqw;height:102cqw">'
         + "".join(f"<div>{e(l)}<sup>{i}</sup></div>" for i, l in enumerate(mf["lines"], 1)) + "</div>"
         + at(8, 12, 4, "cap", f'<p class="eyebrow" lang="en">Manifesto</p><p style="margin-top:.8em">{e(spec["credit"])}</p>'),
         "text", "manifesto", [], "manifesto", rh=story["manifesto"]["en"])
    # 16 duotone | 17 collage -----------------------------------------------------------------------------------------------
    dk = _k(spec["duotone"])
    page(f'<div class="a duo" style="inset:0" data-bleed data-technique="duotone">{img(spec["duotone"])}<div class="grain"></div></div>'
         + at(0, None, 6, "", f'<div class="cl num" style="color:#fff;border-color:rgba(255,255,255,.7)"><span>Fig. {dk} — duotone</span>'
              f'<span>잉크 · 레드 · 종이</span></div>', bottom=7),
         "night", "photo", [spec["duotone"]], "manifesto")
    cells = "".join(f'<div style="overflow:hidden">{img(n)}</div>' for n in spec["collage"])
    page(f'<div class="a" data-bleed data-technique="full_bleed" style="inset:0;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:.4cqw;'
         f'background:var(--paper)">{cells}</div>', "", "collage", spec["collage"], "index")
    # 18 index | 19 why ---------------------------------------------------------------------------------------------------
    ix = story["index"]
    rows = "".join(
        f'<div class="row body"><span class="num">{k}</span><span>'
        + "".join(f'<i class="sw" style="background:{hx}"></i>' for hx, _ in meas[k].get("palette", [])[:5])
        + f'</span><span>{e(spec["photos"][k])}</span><span>{e(meas[k]["light"])}</span><span class="num">{meas[k]["brightness"]:.2f}</span>'
          f'<span class="num">{meas[k]["saturation"]:.2f}</span></div>' for k in ks)
    page(head(ix["en"], "Seen · measured")
         + at(0, 20, 12, "", '<div class="row h cap caps"><span>No.</span><span>색 (잰 값)</span><span>보이는 것</span><span>빛</span>'
              f'<span>밝기</span><span>채도</span></div>{rows}', tech="data_table")
         + at(0, None, 12, "cap", f'<p>{e(spec["photos_note"])} 색 · 빛 · 밝기 · 채도는 원본 사진에서 잰 값이다(밝기 · 채도 0–1).</p>', bottom=9),
         "text", "index", [], "index", rh=ix["en"])
    wy = story["why"]
    blocks = ""
    for i, b in enumerate(spec["qa_text"]):
        top = 22 + i * 33
        paras, cur = [], []
        for a_ in b["a"]:
            if a_.startswith(("첫째", "둘째")) and cur:
                paras.append(cur); cur = []
            cur.append(a_)
        paras.append(cur)
        body = "".join(f'<p style="margin-bottom:1em">' + " ".join(
            (f'<span style="color:var(--ink)">{e(x)}</span>' if x.startswith(("첫째", "둘째")) else e(x)) for x in p_) + "</p>" for p_ in paras)
        blocks += (at(0, top, 1, "display num", f'<p lang="en" style="font-size:{T["title"]}cqw">{i + 1}</p>')
                   + at(1, top, 4, "lead", f'<p>{e(b["q"])}</p>') + at(6, top + 0.4, 6, "body", body))
    page(head(wy["en"], "Three questions") + blocks + at(6, None, 6, "cap", f'<p>{e(spec["credit"])}</p>', bottom=9),
         "text", "qa", [], "why", rh=wy["en"])
    # 20 lens | 21 techniques ------------------------------------------------------------------------------------------------
    L = spec["lens"]
    cw = round(SPAN(3) / (468 / 258), 3)
    cands = "".join(at(i * 3, 22, 3, "", f'<div style="height:{cw}cqw">{img(n, pos="50% 50%")}</div>'
                       f'<div class="cl num"{" style=&quot;&quot;" if False else ""}><span{" style=" + chr(34) + "color:var(--accent-text)" + chr(34) if n == L["chosen"] else ""}>'
                       f'Fig. {_k(n)}</span><span{" style=" + chr(34) + "color:var(--accent-text)" + chr(34) if n == L["chosen"] else ""}>'
                       f'{"Cover" if n == L["chosen"] else ""}</span></div>') for i, n in enumerate(L["candidates"]))
    paras = "".join(f'<p style="margin-bottom:1.1em">{e(r["text"])}{cite(r["claims"])}</p>' for r in L["reading"])
    others = "".join(f'<p style="margin-bottom:1em"><span class="num" style="color:var(--ink)">{k}</span>  {e(t)}</p>' for k, t in L["others"].items())
    page(head(L["title"], "The Gentle Monster lens", lang="ko") + cands
         + at(0, 22 + cw + 8, 7, "body", paras)
         + at(8, 22 + cw + 8, 4, "cap", f'<p class="eyebrow" lang="en" style="margin-bottom:1em">Other candidates</p>{others}<p>{e(L["note"])}</p>')
         + at(0, None, 12, "cap", '<ol class="refs">REFS</ol>', bottom=9), "text", "lens", L["candidates"], "lens", rh="The Gentle Monster Lens")
    page(head(story["techniques"]["en"], "Found · used") + at(0, 20, 12, "tech", "TECHS")
         + at(0, None, 12, "cap", "NOTUSED", bottom=9), "text", "techniques", [], "techniques", rh="Techniques")
    # 22 back --------------------------------------------------------------------------------------------------------------
    b = spec["back"]
    page(f'<div class="a" style="inset:0" data-bleed data-technique="full_bleed">{img(b["photo"])}<div class="grain"></div></div>'
         + at(1, 12, 10, "box", f'<div style="padding:3.4cqw 3.6cqw"><p class="lead" style="margin-bottom:1.2em">{e(b["ko"])}</p>'
              f'<p class="body en serif" lang="en" style="margin-bottom:1.6em;font-size:1.15em">{e(b["en"])}</p>'
              f'<p class="serif" lang="en" style="font-size:{T["lead"] * 1.2:.2f}cqw">“{e(c["question"])}”</p></div>')
         + f'<div class="a band cap caps" lang="en" data-technique="footer_band" style="color:{PAPER}"><span>{e(spec["masthead"])} 00 — {e(spec["credit"])}</span>'
           f'<span lang="ko">독립 콘셉트 매거진 · 젠틀몬스터가 발행 · 승인하지 않았습니다</span></div>',
         "text", "back", [b["photo"]], "back")

    # fill-ins that need every page first ---------------------------------------------------------------------------------
    first = {}
    for p in pages:
        first.setdefault(p["label"], p["n"])
    toc_rows = [("Introduction", "여는 글", first.get("Introduction"))] + [
        (s_["en"], s_["ko"], first.get(s_["id"])) for s_ in spec["story"]] + [("Back Cover", "뒤표지 — 멈춘 뒤 남는 자리", first.get("back"))]
    toc = "".join(f'<a href="#p{n:02d}" class="trow" style="grid-template-columns:{COL}cqw {SPAN(6)}cqw {SPAN(5)}cqw;color:inherit;text-decoration:none">'
                  f'<span class="body num">{n:02d}</span><span class="serif" lang="en" style="font-size:{T["lead"]}cqw;line-height:1.1">{e(t)}</span>'
                  f'<span class="cap">{e(k)}</span></a>' for t, k, n in toc_rows if n)
    pages[1]["html"] = pages[1]["html"].replace("TOC", toc, 1)
    clines = "".join(f'<div class="cline"><span class="cap num" style="color:#f6f3ec">{first[k]:02d}</span><span><span class="serif" lang="en" '
                     f'style="font-size:{T["lead"] * 1.1:.2f}cqw;line-height:1.1;display:block">{e(t)}</span><span class="cap" style="color:#e4e0d6">{e(ko_)}</span></span></div>'
                     for t, ko_, k in lines if first.get(k))
    pages[0]["html"] = pages[0]["html"].replace("CLINES", clines, 1)
    used = {}
    for p in pages:
        for t in re.findall(r'data-technique="([a-z_]+)"', p["html"]):
            used.setdefault(t, [])
            if p["n"] not in used[t]:
                used[t].append(p["n"])
    techs = "".join(f'<div class="trow cap"><span style="color:var(--ink)">{e(TECHNIQUES[t][0])}</span><span>{e(TECHNIQUES[t][1])}</span>'
                    f'<span class="num">{", ".join(f"{n:02d}" for n in used.get(t, [])) or "—"}</span></div>' for t in TECHNIQUES)
    notused = "".join(f'<p style="margin-bottom:.5em"><span style="color:var(--ink)">{e(k)}</span> — {e(v)}</p>' for k, v in NOT_USED.items())
    tp = next(p for p in pages if p["label"] == "techniques")
    tp["html"] = tp["html"].replace("TECHS", '<div class="trow cap caps" style="border-bottom:1px solid var(--ink)"><span>기법</span><span>출처</span><span>쪽</span></div>'
                                    + techs, 1).replace("NOTUSED", f'<p class="eyebrow" lang="en" style="margin-bottom:.8em">Not used</p>{notused}', 1)
    ref_html = "".join(f'<li id="lref-{n}" value="{n}"><span lang="en">{e(src[s_]["title"])}</span> — {e(src[s_]["url"])} '
                       f'(검색 결과의 조각만 확인)</li>' for s_, n in sorted(refs.items(), key=lambda kv: kv[1]))
    body = "".join(p["html"] for p in pages).replace('<ol class="refs">REFS</ol>', f'<ol class="refs">{ref_html}</ol>')
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(spec["title"])}</title><style>{css()}</style></head><body>{duotone_svg()}<main>{body}</main><script>{R.QA_JS}</script></body></html>')
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
    out.append(C("mood", "photos at the catalogue's saturate(.78)", "PASS" if "saturate(.78)" in html_text else "FAIL"))
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
    br = [meas[k]["brightness"] for p in pages if p["label"] == "day" for k in p["photos"]]
    out.append(C("structure", "Day → Dusk runs bright to dark (measured)", "PASS" if br == sorted(br, reverse=True) else "FAIL",
                 " > ".join(f"{x:.2f}" for x in br)))
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
            off = [f"p{p['i']}:c{c_['col']:g}{c_['x'] - X(c_['col']):+.2f}" for p in P for c_ in p.get("cols", []) if abs(c_["x"] - X(c_["col"])) > 0.3]
            n_cols = sum(len(p.get("cols", [])) for p in P)
            out.append(C("layout", "blocks sit on the 12-column grid (±0.3 cqw)", "FAIL" if off else "PASS", ", ".join(off[:6]) or f"{n_cols} blocks"))
            faux = [f"p{p['i']}:{f}" for p in P for f in p.get("faux", [])]
            out.append(C("typography", "no faux-bold Korean (the Korean face has one weight)", "FAIL" if faux else "PASS", ", ".join(faux[:4]) or "none"))
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
            fonts = [f for f in QA.ko_fonts() if f.startswith("WenQuanYi")]
            out.append(C("typography", "Hangul has a font", "PASS" if fonts or not han else "FAIL", ", ".join(fonts[:1]) or "none"))
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
