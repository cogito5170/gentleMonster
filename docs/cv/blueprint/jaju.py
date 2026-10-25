"""CV 1/2 (TYPE 1, card grid) re-toned for JAJU — three tone options, same layout and copy.

    python3 docs/cv/blueprint/jaju.py   # -> types/E-00.svg, jaju_options.pdf, ../ai/CV_JAJU_TYPE1_J*.ai

Colour source: press coverage of the JAJU rebranding (Dec 2024) — it dropped the achromatic image and took
colour and pattern from Korean nature and tradition: patterns of bean pods, charcoal and dried chilli,
packaging with hemp, ceramic and wood textures. The hex values below are picked from those materials;
they are NOT JAJU's official brand colours.
"""
import subprocess
from pathlib import Path

from bp import *  # noqa: F401,F403
import bp
from cv_types import type1

HERE = Path(__file__).parent
AI = HERE.parent / "ai"

TONES = [
    dict(code="J1", en="HEMP", ko="삼베", note="바탕 삼베 · 글자 숯 · 강조 말린 고추",
         th=dict(bg="#E7DFD0", card="#DCD2C0", side="#DCD2C0", photo="#CBBFA9", px="#B7AA92",
                 text="#24221F", sub="#625C52", line="#C2B7A2", grid="#D2C8B5", accent="#9C3A26", on_accent="#F4EEE4")),
    dict(code="J2", en="PORCELAIN", ko="백자", note="바탕 백자 · 글자 숯 · 강조 콩깍지",
         th=dict(bg="#F1EEE7", card="#E5E0D5", side="#E5E0D5", photo="#D3CDC0", px="#BDB6A7",
                 text="#1F1E1C", sub="#5F5B54", line="#CFC9BD", grid="#DDD7CB", accent="#6F7148", on_accent="#F4F1EA")),
    dict(code="J3", en="CHARCOAL", ko="숯", note="바탕 숯 · 글자 한지 · 강조 말린 고추",
         th=dict(bg="#1F1D1B", card="#2B2825", side="#2B2825", photo="#393531", px="#4A4540",
                 text="#EDE6DA", sub="#A39C91", line="#3C3833", grid="#2B2825", accent="#B4482F", on_accent="#F6EFE6")),
]


def a4(tone, path):
    bp.OUT.clear()
    w('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">')
    w(f'<title>CV 1/2 · JAJU · {tone["code"]} {tone["en"]} · JEONG HYEOKJU</title>')
    theme(tone["th"])
    type1()
    zone_end()
    w('</svg>')
    path.write_text("\n".join(bp.OUT), encoding="utf-8")


def overview(path):
    sheet_open()
    t(16, 17, "E-00   CV 1/2 · TYPE 1 FOR JAJU  ·  3 TONES", 10, INK, 700, ls=0.3)
    t(16, 22.5, "젠틀몬스터 CV 1페이지(TYPE 1)를 같은 구성 · 같은 글로 두고, 색만 자주(JAJU)에 맞춘 세 안. "
                "색은 자주 리브랜딩 보도에 나온 재료(삼베 · 백자 · 숯 · 말린 고추 · 콩깍지)에서 고름 — 공식 브랜드 색 아님.",
      6.0, INK2, 400, fam=KR)
    s, gx, gy, gap = 0.6, 16, 30, 7
    pw, ph = 210 * s, 297 * s
    for i, tone in enumerate(TONES):
        x = gx + i * (pw + gap)
        drawing(type1, x, gy, s, tone["th"])
        bp.zone_end()
        r(x, gy, pw, ph, stroke=INK, sw=0.25)
        cy = gy + ph + 5.5
        t(x, cy, f"{tone['code']}  {tone['en']}", 8, INK, 700, ls=0.3)
        t(x + pw, cy, tone["ko"], 6, INK2, 500, "end", fam=KR)
        t(x, cy + 4.4, tone["note"], 5.4, INK, 400, fam=KR)
        keys = [("bg", "바탕"), ("card", "카드"), ("text", "글자"), ("sub", "본문"), ("accent", "강조")]
        for k, (key, lab) in enumerate(keys):
            sx = x + k * 25
            r(sx, cy + 7, 23, 5, tone["th"][key], INK, 0.15)
            t(sx, cy + 15, lab, 4.8, INK, 500, fam=KR)
            t(sx, cy + 17.6, tone["th"][key], 4.4, INK2, 400)
    yb = 262
    ln(16, yb - 4, 404, yb - 4, RULE, 0.3)
    notes = ["· 바뀐 것: 바탕 · 카드 · 글자 · 강조색. 강조색이 정해져 메뉴 오른쪽 CONTACT 버튼이 빗금에서 단색으로 바뀜.",
             "· 그대로인 것: 구성 · 헤드라인 FRAME & INTERIOR · 강점 카드 · 학력 · 경력 · 스킬 · 글 전부 (젠틀몬스터를 가리키는 말은 1페이지에 없음).",
             "· 첫 화면 작은 줄의 직무 SPATIAL DESIGNER · 공간 설계 디자이너 는 자주 지원 직무가 정해지면 그 이름으로 바꿈.",
             "· 근거: 자주는 2024년 12월 리브랜딩에서 무채색을 버리고 한국의 자연 · 전통에서 색과 문양을 가져옴 (한경 매거진 · 머니투데이 보도)."]
    lines(16, yb, notes, 5.8, 1.55, fill=INK, fam=KR)
    sheet_close(path)


def main():
    out = HERE / "types"
    pdfs = []
    ov = out / "E-00.svg"
    overview(ov)
    svgs = [ov]
    for tone in TONES:
        p = out / f"jaju_{tone['code']}.svg"
        a4(tone, p)
        svgs.append(p)
    for svg in svgs:
        pdf = svg.with_suffix(".pdf")
        subprocess.run(["inkscape", str(svg), "--export-type=pdf", f"--export-filename={pdf}"], check=True, capture_output=True)
        pdfs.append(str(pdf))
    subprocess.run(["pdfunite", *pdfs, str(HERE / "jaju_options.pdf")], check=True)
    for tone in TONES:          # Illustrator copies
        stem = f"CV_JAJU_TYPE1_{tone['code']}_{tone['en']}"
        svg = AI / f"{stem}.svg"
        a4(tone, svg)
        pdf = AI / f"{stem}.pdf"
        subprocess.run(["inkscape", str(svg), "--export-type=pdf", "--export-pdf-version=1.5", f"--export-filename={pdf}"],
                       check=True, capture_output=True)
        pdf.replace(AI / f"{stem}.ai")
        print(AI / f"{stem}.ai")
    print(HERE / "jaju_options.pdf")


if __name__ == "__main__":
    main()
