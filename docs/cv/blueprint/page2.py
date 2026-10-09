"""CV 2/2 — cover-letter page, three layouts that put the reading first.

    python3 docs/cv/blueprint/page2.py    # -> types/D-00.svg (A3 overview), page2_P2-A/B/C.svg (A4), page2_options.pdf

Q2 (본인 소개 · 강점) is set in full from the applicant's text. Q1 (지원 이유 · 왜 젠틀몬스터) is still being
written (cover_letter.md: 1000자 이내, 퇴고 대기), so it is reserved as grey line bars for 1000 characters.
Line breaks are measured with the real Noto Sans CJK KR metrics (Pillow), so the fit numbers are real.
"""
import math
import subprocess
from pathlib import Path

from PIL import ImageFont

from bp import *  # noqa: F401,F403
import bp

HERE = Path(__file__).parent
FONT = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 1000, index=1)  # KR

# ------------------------------------------------------------------ text (verbatim from the applicant)
Q1 = ("01", "WHY GENTLE MONSTER", "지원한 이유, 왜 젠틀몬스터여야 하는가?")
Q2 = ("02", "ABOUT ME · STRENGTHS", "본인을 소개하시오. 자신의 강점은 무엇입니까?")
Q2_TITLE = "〈틀을 배우고, 그 안을 채우는 건축학도〉"
Q2_BODY = [
    ("sub", "① 본인 소개", None),
    ("p", "건물을 설계하던 감각으로 매장을 설계하려는 건축학도입니다. 5년제 건축학과의 설계 수업에서 다룬 건축은 대지와 주변 건물과의 관계 속에서 '틀'을 정하는 일이었습니다. 그 틀 안의 실내 공간을 다룰 때 더 큰 흥미를 느껴, 4학년 2학기에 휴학하고 공간 디자인으로 전향해 젠틀몬스터에 지원했습니다.", None),
    ("sub", "② 강점", None),
    ("p", "첫째, 기획입니다. 1학년부터 매 학기, 7학기 동안 설계 수업에서 리서치와 분석으로 컨셉을 세우고 그 컨셉을 건물로 발전시켰습니다. 하나의 생각을 끝까지 형태로 밀고 가는 이 과정을 공간 기획에 가져가겠습니다.", "01 PLANNING"),
    ("p", "둘째, 구현과 소통입니다. 수업에서는 컨셉을 다이어그램과 이미지로 옮겨 발표했습니다. 건축사사무소 인턴으로는 현장을 실측해 모델링하고, 주변 대지와 프로젝트 건물을 구현했습니다. 2D부터 3D 모델링, 시각화, 후보정까지 다룹니다. 오토캐드, 라이노, 엔스케이프, 포토샵, 일러스트, 인디자인을 씁니다. 매장 컨셉도 같은 방식으로 모델과 이미지로 옮겨 전하겠습니다.", "02 MAKING · TELLING"),
    ("p", "셋째, 디자인적 감각입니다. 건축가도 디자이너라는 생각으로 시야를 넓혀 왔습니다. 학부 과정에서는 건물의 비례, 이미지 표현, 색채를 다듬는 작업을 지향했고, 다양한 건축물을 다니며 실내 공간을 이루는 마감재와 가구, 조명을 살폈습니다.", "03 SENSE"),
    ("p", "원색 대신 채도를 낮춘 색으로 포인트를 주고 주변과 어우러지게 해, 가구와 조명 같은 오브제가 공간 속에서 하나의 장면이 되게 하는 방식에 관심이 많습니다. 이 감각을 아트 오브제와 가구, 마감재를 기획하는 데 쓰겠습니다.", None),
    ("p", "절제된 비례와 색 조합에는 익숙합니다. 학부 시절 건축을 통해 절제된 디자인을 배워 왔기 때문입니다. 반면 과감한 디자인은 아직 익숙하지 않아, 그쪽으로 폭을 넓혀 가려 합니다. 젠틀몬스터의 공간은 과감한 형태와 색의 디자인 언어를 쓰기에, 그 언어 앞에서는 채워야 할 부분입니다. 그 일환으로서 스타일부터 변화하고 있습니다. 무채색 기반의 패션을 컬러 포인트와 개성 있는 아이템으로 바꿔나가고 있습니다. 옷에서 시작한 이 변화를 실무까지 이어 가고 싶습니다. 건축에서 익힌 절제 위에 과감을 더해, 절제와 과감을 한 공간에서 함께 다루고자 합니다.", "04 RESTRAINT + BOLD"),
    ("sub", "③ 포부", None),
    ("p", "틀을 배운 건축학도에서, 스토어와 팝업 공간의 그 안을 채우는 젠틀몬스터의 공간 설계 디자이너가 되겠습니다.", "VISION"),
]
Q1_CHARS = 1000
Q2_CHARS = len(Q2_TITLE) + sum(len(s) for k, s, _ in Q2_BODY) + sum(1 for k, *_ in Q2_BODY if k == "p")


def mw(s, pt):
    return FONT.getlength(s) / 1000 * pt * PT


def kwrap(s, maxw, pt):
    out, cur = [], ""
    for word in s.split(" "):
        trial = (cur + " " + word).strip()
        if cur and mw(trial, pt) > maxw:
            out.append(cur); cur = word
        else:
            cur = trial
    return out + ([cur] if cur else [])


def bars(x, y, maxw, pt, lh, n_chars):
    """grey line bars standing in for n_chars of Korean text; returns (lines, height)."""
    per = int(maxw / (pt * PT * 0.86))          # measured: this text averages 0.86 em per character
    n = math.ceil(n_chars / per)
    L = pt * PT * lh
    for i in range(n):
        wd = maxw if i < n - 1 else maxw * 0.42
        r(x, y + i * L - pt * PT * 0.62, wd, pt * PT * 0.5, "sub", rx=0.3)
    return n, n * L


def nav(page_label="PAGE 2 / 2"):
    M = 7
    t(M + 1, 12.6, "JEONG HYEOKJU", 7, "text", 600, ls=0.35)
    x = 203
    for i, p in enumerate(["CONTACT", "COVER LETTER", "SKILLS", "EXPERIENCE", "EDUCATION", "ABOUT"]):
        pw = len(p) * 1.55 + 4.4
        x -= pw
        if i == 0:
            hatch_pill(x, 8.8, pw, 4.6, p)
        else:
            r(x, 8.8, pw, 4.6, "text" if p == "COVER LETTER" else "card", rx=0.8)
            t(x + pw / 2, 11.9, p, 4.6, "bg" if p == "COVER LETTER" else "text", 600, "middle", ls=0.2)
        x -= 1.4
    t(x - 2, 12.2, page_label, 4.8, "sub", 500, "end", ls=0.3)


def footer(y=285.5):
    ln(7, y - 3, 203, y - 3, "line", 0.25)
    arrow(9.5, y + 0.6, "PAGE 1 · CV", 1.7)
    t(203, y + 1.3, "T ____   ·   E ____   ·   PORTFOLIO ____", 4.8, "sub", 400, "end", fam=KR)


# ------------------------------------------------------------------ flow typesetter
def flow(items, cols, y0, y1, pt, lh=1.72, draw=True, label_cb=None):
    """Set items into columns [(x, width)] from y0 to y1. Returns (fits, end_y, n_lines)."""
    L = pt * PT * lh
    ci, y, nlines = 0, y0, 0

    def room(h):
        nonlocal ci, y
        if y + h > y1:
            ci += 1
            y = y0
        return ci < len(cols)
    for it in items:
        kind = it[0]
        if ci >= len(cols):
            return False, y, nlines
        x, cw = cols[ci]
        if kind == "qhead":
            _, num, en, ko, note = it
            if not room(17):
                return False, y, nlines
            x, cw = cols[ci]
            if y > y0:
                y += 3
            if draw:
                ln(x, y, x + cw, y, "text", 0.35)
                t(x, y + 6.2, num, 15, "text", 200)
                t(x + 11, y + 3.6, en, 5.2, "sub", 600, ls=0.3)
                t(x + 11, y + 7.6, ko, 7.4, "text", 700, fam=KR)
                if note:
                    t(x + cw, y + 3.6, note, 4.8, "sub", 400, "end", fam=KR)
            y += 13
        elif kind == "title":
            if not room(9):
                return False, y, nlines
            x, cw = cols[ci]
            if draw:
                t(x, y + 4.6, it[1], 10.5, "text", 400, fam=KR)
            y += 10
        elif kind == "sub":
            if not room(L * 2.2):
                return False, y, nlines
            x, cw = cols[ci]
            y += L * 0.35
            if draw:
                t(x, y + pt * PT, it[1], pt * 0.92, "text", 700, fam=KR)
            y += L * 1.25
        elif kind == "p":
            text, label = it[1], it[2]
            ls_ = kwrap(text, cw, pt)
            first = True
            for s in ls_:
                if not room(L):
                    return False, y, nlines
                x, cw2 = cols[ci]
                if draw:
                    t(x, y + pt * PT, s, pt, "text", 400, fam=KR, op=0.92)
                    if first and label and label_cb:
                        label_cb(label, y)
                first = False
                y += L; nlines += 1
            y += L * 0.55
        elif kind == "ph":
            per = int(cw / (pt * PT * 0.86))
            n = math.ceil(it[1] / per)
            done = 0
            while done < n:
                if not room(L):
                    return False, y, nlines
                x, cw = cols[ci]
                k = min(n - done, int((y1 - y) / L))
                if k <= 0:
                    ci += 1; y = y0
                    continue
                for i in range(k):
                    last = done + i == n - 1
                    if draw:
                        r(x, y + i * L + pt * PT * 0.32, cw * (0.42 if last else 1), pt * PT * 0.52, "line", rx=0.3)
                y += k * L; done += k; nlines += k
            y += L * 0.55
    return True, y, nlines


def items(q1_note="원고 보류 중 · 1000자 이내 자리"):
    return ([("qhead", *Q1, q1_note), ("ph", Q1_CHARS), ("qhead", *Q2, f"{Q2_CHARS}자"), ("title", Q2_TITLE)] +
            [(k, s, lab) for k, s, lab in Q2_BODY])


def fit_pt(its, cols, y0, y1, hi=8.2, lo=6.6):
    pt = hi
    while pt >= lo:
        ok, _, _ = flow(its, cols, y0, y1, pt, draw=False)
        if ok:
            return pt
        pt = round(pt - 0.1, 2)
    return lo


SPEC = {}


# ================================================================== P2-A · ARTICLE, two columns
def p2a():
    r(0, 0, 210, 297, "bg")
    nav()
    t(12, 32, "COVER LETTER", 30, "text", 100, ls=0.6)
    t(12, 39, "자기소개서  ·  문항 1 지원 이유  ·  문항 2 본인 소개와 강점", 6, "sub", 400, fam=KR)
    t(198, 39, "FRAME & INTERIOR", 6, "text", 500, "end", ls=0.4)
    cols = [(12, 88), (110, 88)]
    its = items()
    pt = fit_pt(its, cols, 46, 279)
    flow(its, cols, 46, 279, pt)
    footer()
    SPEC["P2-A"] = dict(pt=pt, cols=cols, cpl=int(88 / (pt * PT * 0.86)))


# ================================================================== P2-B · SIDENOTE, one reading column (light)
def p2b():
    r(0, 0, 210, 297, "bg")
    nav()
    LX, LW, X, W = 12, 44, 66, 132
    t(LX, 25, "COVER", 16, "text", 200, ls=0.4)
    t(LX, 31.5, "LETTER", 16, "text", 200, ls=0.4)
    t(X, 25, "왼쪽 여백의 표시 01–04 = 1페이지 강점 카드와 같은 이름", 5.4, "sub", 400, fam=KR)

    def lab(label, y):
        t(LX, y + 2.4, label, 5.2, "text", 700, ls=0.3)
    its = items()
    # question numbers in the margin, text in the column
    marg = []

    def flow_b(draw, pt):
        y = 34
        Lh = pt * PT * 1.72
        ok = True
        for it in its:
            k = it[0]
            if k == "qhead":
                _, num, en, ko, note = it
                y += 2
                if draw:
                    ln(LX, y, X + W, y, "text", 0.35)
                    t(LX, y + 9, num, 22, "text", 200)
                    t(LX + 13, y + 4.4, en, 4.8, "sub", 600, ls=0.25)
                    para(LX, y + 14, ko, LW - 2, 6.4, 1.4, fill="text", fam=KR, weight=700)
                    if note:
                        t(X + W, y + 4.4, note, 4.8, "sub", 400, "end", fam=KR)
                y += 6
            elif k == "title":
                if draw:
                    t(X, y + 4.4, it[1], 10.5, "text", 400, fam=KR)
                y += 9
            elif k == "sub":
                y += Lh * 0.3
                if draw:
                    t(X, y + pt * PT, it[1], pt * 0.92, "text", 700, fam=KR)
                y += Lh * 1.2
            elif k == "p":
                ls_ = kwrap(it[1], W, pt)
                if draw and it[2]:
                    lab(it[2], y)
                for s in ls_:
                    if draw:
                        t(X, y + pt * PT, s, pt, "text", 400, fam=KR)
                    y += Lh
                y += Lh * 0.5
            elif k == "ph":
                per = int(W / (pt * PT * 0.86))
                n = math.ceil(it[1] / per)
                for i in range(n):
                    if draw:
                        r(X, y + pt * PT * 0.32, W * (0.42 if i == n - 1 else 1), pt * PT * 0.52, "line", rx=0.3)
                    y += Lh
                y += Lh * 0.5
            ok = ok and y <= 279
        return ok, y
    pt = 8.2
    while pt > 6.6 and not flow_b(False, pt)[0]:
        pt = round(pt - 0.1, 2)
    flow_b(True, pt)
    footer()
    SPEC["P2-B"] = dict(pt=pt, cols=[(X, W)], cpl=int(W / (pt * PT * 0.86)))


# ================================================================== P2-C · CARDS, continued from page 1
def p2c():
    M, CW, G = 7, 196, 2.5
    hw = (CW - G) / 2
    r(0, 0, 210, 297, "bg")
    nav()
    pt = 8.2
    for attempt in range(20):
        L = pt * PT * 1.66
        heights = {}
        # Q1 card: two columns of bars
        per = int((hw - 10) / (pt * PT * 0.86))
        q1_lines = math.ceil(math.ceil(Q1_CHARS / per) / 2)
        heights["q1"] = 15 + q1_lines * L + 5
        intro = Q2_BODY[1][1]
        heights["intro"] = 0
        strengths = [Q2_BODY[3], Q2_BODY[4], (None, Q2_BODY[5][1] + "\n" + Q2_BODY[6][1], "03 SENSE"), Q2_BODY[7]]
        tw = hw - 10

        def ph(text):
            return sum(len(kwrap(s, tw, pt)) for s in text.split("\n")) * L + (text.count("\n")) * L * 0.5
        h_intro = 13 + max(len(kwrap(intro, CW - 10 - 54, pt)), 1) * L + 4
        row1 = 12 + max(ph(strengths[0][1]), ph(strengths[1][1])) + 4
        row2 = 12 + max(ph(strengths[2][1]), ph(strengths[3][1])) + 4
        total = 17 + heights["q1"] + G + 15 + h_intro + G + row1 + G + row2 + G + 16
        if total <= 281:
            break
        pt = round(pt - 0.1, 2)
    y = 17
    # Q1
    r(M, y, CW, heights["q1"], "card", rx=1.6)
    t(M + 5, y + 6, "Q1  ·  WHY GENTLE MONSTER", 5.4, "sub", 600, ls=0.3)
    t(M + 5, y + 11, Q1[2], 7.4, "text", 700, fam=KR)
    t(M + CW - 5, y + 6, "원고 보류 중 · 1000자 이내 자리", 4.8, "sub", 400, "end", fam=KR)
    for c in range(2):
        for i in range(q1_lines):
            last = c == 1 and i == q1_lines - 1
            r(M + 5 + c * (hw + G), y + 15 + i * L + pt * PT * 0.32, tw * (0.42 if last else 1), pt * PT * 0.52, "line", rx=0.3)
    y += heights["q1"] + G
    # Q2 title band
    t(M + 1, y + 6.5, "Q2  ·  ABOUT ME · STRENGTHS", 5.4, "sub", 600, ls=0.3)
    t(M + 1, y + 12.6, Q2_TITLE, 11, "text", 400, fam=KR)
    t(M + CW, y + 6.5, f"{Q2_CHARS}자", 4.8, "sub", 400, "end", fam=KR)
    y += 15
    # 1 intro: wide card, label column + text
    r(M, y, CW, h_intro, "card", rx=1.6)
    t(M + 5, y + 6, "① 본인 소개", 6.4, "text", 700, fam=KR)
    t(M + 5, y + 10, "ABOUT", 5, "sub", 600, ls=0.3)
    for i, s in enumerate(kwrap(intro, CW - 10 - 54, pt)):
        t(M + 59, y + 6 + i * L, s, pt, "text", 400, fam=KR)
    y += h_intro + G
    # 2 strengths: 2 x 2 cards, numbered like page 1
    names = [("01  PLANNING", "첫째 · 기획"), ("02  MAKING · TELLING", "둘째 · 구현과 소통"),
             ("03  SENSE", "셋째 · 디자인적 감각"), ("04  RESTRAINT + BOLD", "절제와 과감")]
    for k in range(4):
        cx = M + (k % 2) * (hw + G)
        cy = y if k < 2 else y + row1 + G
        ch = row1 if k < 2 else row2
        r(cx, cy, hw, ch, "card", rx=1.6)
        t(cx + 5, cy + 6, names[k][0], 5.6, "text", 600, ls=0.25)
        t(cx + 5, cy + 9.8, "② 강점  ·  " + names[k][1], 5.2, "sub", 500, fam=KR)
        yy = cy + 15
        for j, part in enumerate(strengths[k][1].split("\n")):
            for s in kwrap(part, tw, pt):
                t(cx + 5, yy, s, pt, "text", 400, fam=KR)
                yy += L
            yy += L * 0.5
    y += row1 + G + row2 + G
    # 3 vision band (hatched accent edge)
    r(M, y, CW, 14, "card", rx=1.6)
    r(M, y, 3, 14, "url(#hatch)", rx=0)
    t(M + 8, y + 5.6, "③ 포부  ·  VISION", 5.4, "sub", 600, ls=0.25, fam=KR)
    t(M + 8, y + 10.8, Q2_BODY[9][1], 8.2, "text", 400, fam=KR)
    footer()
    SPEC["P2-C"] = dict(pt=pt, cols=[(M + 5, tw)], cpl=int(tw / (pt * PT * 0.86)), bottom=y + 14)


OPTIONS = [
    dict(code="P2-A", fn=p2a, th=DARK, en="ARTICLE", ko="기사형 2단",
         how=["1페이지와 같은 어두운 홈페이지, 사진 없음", "두 단으로 문항 1 → 문항 2가 이어 흐름 (잡지 기사)",
              "문항마다 굵은 선 + 큰 번호 01 · 02 로 시작", "제목 COVER LETTER 는 1페이지 헤드라인과 같은 Thin"],
         plus=["한 장에 가장 많은 글이 들어감 — 글자가 가장 큼", "읽는 길이 위→아래, 왼→오 하나뿐"],
         minus=["어두운 바탕의 긴 글은 밝은 바탕보다 눈이 쉽게 피로함"]),
    dict(code="P2-B", fn=p2b, th=LIGHT, en="SIDENOTE", ko="여백 표시 1단 · 밝은 바탕",
         how=["밝은 회베이지 바탕 — 글 페이지만 밝게 (1페이지는 표지 역할)", "읽는 단은 하나, 왼쪽 여백에 문항 번호와 문단 표시",
              "여백 표시 01 PLANNING … 04 RESTRAINT + BOLD = 1페이지 강점 카드 이름", "1페이지 카드의 → P.2 화살표가 이 표시로 이어짐"],
         plus=["글이 한 줄로 흘러 가장 차분하게 읽힘", "여백 표시로 강점 네 개를 훑어볼 수 있음"],
         minus=["한 줄이 길어짐 (아래 표의 한 줄 글자 수)", "두 장의 바탕색이 달라짐 — 의도로 읽히게 해야 함"]),
    dict(code="P2-C", fn=p2c, th=DARK, en="CARDS", ko="카드 · 1페이지에서 이어짐",
         how=["1페이지 카드 그리드를 그대로 이어 씀", "강점 네 문단을 2 × 2 카드로 — 1페이지 카드 01–04 와 같은 번호 · 이름",
              "본인 소개는 넓은 카드, 포부는 마지막 띠", "문항 1은 맨 위 넓은 카드 (두 단)"],
         plus=["두 장이 한 웹사이트처럼 이어짐", "강점 문단을 하나씩 따로 읽을 수 있음"],
         minus=["카드 테두리와 여백만큼 글자가 작아짐", "글이 카드로 끊겨 한 편의 글로 읽히는 느낌은 약함"]),
]


def a4_svg(opt, path):
    bp.OUT.clear()
    w('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">')
    w('<defs><pattern id="hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
      '<rect width="1.2" height="1.2" fill="#262626"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#8E8B86" stroke-width="0.4"/></pattern></defs>')
    theme(opt["th"])
    opt["fn"]()
    w('</svg>')
    path.write_text("\n".join(bp.OUT), encoding="utf-8")


def overview(path):
    sheet_open()
    t(16, 17, "D-00   CV 2/2 · COVER LETTER PAGE  ·  3 OPTIONS", 10, INK, 700, ls=0.3)
    t(16, 22.5, f"글이 먼저 읽히는 2페이지. 문항 2 원고({Q2_CHARS}자)는 그대로 조판, 문항 1(1000자 이내, 퇴고 대기)은 회색 줄로 자리만 잡음. "
                "줄바꿈은 Noto Sans KR 실제 글자 폭으로 계산.", 6.0, INK2, 400, fam=KR)
    s, gx, gy = 0.6, 16, 30
    pw, ph = 210 * s, 297 * s
    gap = 7
    for i, opt in enumerate(OPTIONS):
        x = gx + i * (pw + gap)
        drawing(opt["fn"], x, gy, s, opt["th"])
        r(x, gy, pw, ph, stroke=INK, sw=0.25)
        sp = SPEC[opt["code"]]
        cy = gy + ph + 5.5
        t(x, cy, f"{opt['code']}  {opt['en']}", 8, INK, 700, ls=0.3)
        t(x + pw, cy, opt["ko"], 6, INK2, 500, "end", fam=KR)
        rows = [("본문", f"Noto Sans KR {sp['pt']}pt · 행간 {1.72 if opt['code'] != 'P2-C' else 1.66}"),
                ("한 줄", f"약 {sp['cpl']}자 (단 폭 {sp['cols'][0][1]:.0f})"),
                ("단", f"{len(sp['cols'])}단" if opt["code"] != "P2-C" else "카드 2열")]
        yy = cy + 4.6
        for k, v in rows:
            t(x, yy, k, 5.4, INK2, 600, fam=KR); t(x + 12, yy, v, 5.4, INK, 400, fam=KR); yy += 3.1
        for head, lst, col in (("방식", opt["how"], INK), ("좋은 점", opt["plus"], INK), ("주의", opt["minus"], RED)):
            yy += 2.2
            t(x, yy, head, 5.6, INK, 700, fam=KR); yy += 3.2
            for s_ in lst:
                yy = para(x, yy, "· " + s_, pw, 5.3, 1.4, fill=col, fam=KR) + 0.6
    yb = 278
    ln(16, yb - 4, 404, yb - 4, RULE, 0.3)
    notes = ["글에 초점을 맞춘 장치 (세 안 공통): 사진 없음 · 본문 7–8pt 와 넉넉한 행간(1.66–1.72) · 제목 단계는 셋(문항 · 소제목 · 본문)만 · 장식은 선과 번호뿐.",
             "문항 순서는 서류 번호대로 01 지원 이유 → 02 본인 소개. 바꿔도 구조는 같음. 문항 2 글은 받은 원고 그대로, 한 글자도 고치지 않음.",
             "문항 1 은 1000자를 꽉 채운 경우로 자리를 잡음 — 글이 짧아지면 그만큼 본문이 커지거나 여백이 생김."]
    lines(16, yb, notes, 5.8, 1.55, fill=INK, fam=KR)
    sheet_close(path)


def main():
    out = HERE / "types"
    out.mkdir(exist_ok=True)
    pdfs = []
    for opt in OPTIONS:              # A4 pages first (fills SPEC)
        svg = out / f"page2_{opt['code']}.svg"
        a4_svg(opt, svg)
    ov = out / "D-00.svg"
    overview(ov)
    for svg in [ov] + [out / f"page2_{o['code']}.svg" for o in OPTIONS]:
        pdf = svg.with_suffix(".pdf")
        subprocess.run(["inkscape", str(svg), "--export-type=pdf", f"--export-filename={pdf}"], check=True, capture_output=True)
        pdfs.append(str(pdf))
    subprocess.run(["pdfunite", *pdfs, str(HERE / "page2_options.pdf")], check=True)
    for k, v in SPEC.items():
        print(k, v)
    print("Q2 chars", Q2_CHARS)


if __name__ == "__main__":
    main()
