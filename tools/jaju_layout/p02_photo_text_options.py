"""JAJU 포트폴리오 2쪽 — 사진(책을 펼친 장면, 어둡게) 위에 메시지를 얹는 세 안.

  python3 tools/jaju_layout/p02_photo_text_options.py   ->  docs/jaju_rounding_vmd/layout/p02_photo_text_options.pdf

사용자: "해당 이미지 위에 해당 문구를 기입하라. 포트폴리오 사례를 참고하여 3가지의 안을 제시하라."
사진: docs/jaju_rounding_vmd/assets/cover/opening_book_dark.jpg (1736×1138, 사용자가 준 어둡게 한 흑백판). 쪽 전체에, 좌우가 조금 잘린다.
글: 제목 '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.' + 프롤로그 일곱 문장(한국어), 영어는 안에 따라.
  1안  Galatasaray S.K. — 사진이 아래로 검정에 녹고, 그 검정 위에 굵은 고딕 제목 한 줄 + 회색 문단 하나(왼쪽 1/5 에서 시작).
  2안  ETÉREO — 책 속 빈 면에 글을 '인쇄'한다: 면의 기울기(약 −7°)대로 돌린 세리프 제목 + 작은 본문, 어두운 잉크(곱하기 합성).
  3안  Desjobert — 오른쪽 면 위에 반투명 검정 글 상자(사례 6 의 'A 350-1000 full cabin.'), 위에 작은 표지 글.
사진 크기 · 바탕(사진의 밝기 80–140)이 어디서나 중간 회색이라, 1 · 3안은 사진을 어둡게 덮은 자리에만 흰 글자를 놓는다.
쪽 오른쪽 위의 작은 '안' 표시는 비교용 — 최종본에서 지운다. 한글 시안 글꼴은 문천역정흑(이 환경의 유일한 한글 글꼴), 최종 글꼴은 FONT.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import p02_message_options as opt  # noqa: E402

pe = opt.pe
pc, t, div, photo = pe.pc, pe.t, pe.div, pe.photo
OUT, TMP, PRINT = pe.OUT, pe.TMP, pe.PRINT
IMG = os.path.abspath(os.path.join(HERE, '../../docs/jaju_rounding_vmd/assets/cover/opening_book_dark.jpg'))
_path = pc.path
pc.path = lambda pid: IMG if pid == 'BOOK-DARK' else _path(pid)

HEAD, KO, EN = opt.HEAD, opt.KO, opt.EN
FONT = {
    '1안': 'Pretendard Bold(제목) · Regular(본문)',
    '2안': '국문 명조 Noto Serif KR Regular(제목) · Light(본문), 영문 Crimson Pro',
    '3안': 'Pretendard SemiBold(제목) · Regular(본문), 영문 Lora Italic, 표지 글 IBM Plex Mono',
}


def bg():
    return photo('BOOK-DARK', 0, 0, 297, 210, focus=(0.5, 0.5))


def tag(s):
    return t(250, 6, 40, 4, s, 'tag2 r')


# ── 1안 · Galatasaray ────────────────────────────────────────────────────────────────
def opt1():
    body = ' '.join(KO[:-1]) + f" <span class='w'>{KO[-1]}</span>"
    return ''.join([
        bg(), div(0, 0, 297, 210, '', 'fade'),
        t(62, 140, 220, 12, HEAD, 'g-head'),
        t(62, 156, 180, 40, f'<p>{body}</p>', 'g-body1 wrap'),
        tag('1안 · GALATASARAY'),
    ])


# ── 2안 · ETÉREO — 책의 빈 면에 인쇄 ─────────────────────────────────────────────────
def opt2():
    lines = ''.join(f'<p>{s}</p>' for s in KO[:-1]) + f"<p class='last'>{KO[-1]}</p>"
    inner = (f"<p class='e-head'>밖에서 보면 상품이 보이고,</p><p class='e-head'><i>안에서 보면</i> 사람이 보인다.</p>"
             f"<div class='e-body'>{lines}</div>")
    return ''.join([bg(), div(100, 147, 120, 50, inner, 'print'), tag('2안 · ETÉREO')])


# ── 3안 · Desjobert — 반투명 글 상자 ──────────────────────────────────────────────────
def opt3():
    a, b = HEAD.split(', ')
    body = ''.join(f'<p>{s}</p>' for s in KO[:-1]) + f"<p class='w'>{KO[-1]}</p>"
    return ''.join([
        bg(), div(203, 24, 82, 164, '', 'frost2'),
        t(210, 32, 70, 4, 'PROLOGUE', 'd-lab'),
        t(210, 41, 70, 24, f'<p>{a},</p><p>{b}</p>', 'd-head'),
        t(210, 68, 68, 90, body, 'd-body wrap'),
        t(210, 136, 68, 34, f'<p>{EN}</p>', 'd-en wrap'),
        t(210, 180, 70, 4, 'FROM THE INSIDE', 'd-lab'),
        tag('3안 · DESJOBERT'),
    ])


KOF = opt.KOF
CSS = opt.CSS + f"""
.tag2{{font-family:Mono,monospace;font-size:5pt;letter-spacing:.1em;color:rgba(242,242,242,.5);white-space:nowrap}}
/* 1안 */
.fade{{background:linear-gradient(to bottom,rgba(10,10,10,0) 30%,rgba(10,10,10,.75) 58%,rgba(10,10,10,.96) 72%)}}
.g-body1{{font-family:{KOF};font-size:10pt;line-height:17pt;color:#9A9A9A;word-break:keep-all}}.g-body1 p{{white-space:normal}}
/* 2안 */
.print{{transform:rotate(-6.8deg);transform-origin:50% 50%;mix-blend-mode:multiply;color:#141414}}
.print p{{position:static}}.print div{{position:static}}
.e-head{{font-family:{KOF};font-size:13pt;line-height:17pt;white-space:nowrap;letter-spacing:.01em}}
.e-head i{{font-style:normal;font-family:Crimson,{KOF}}}
.e-body{{margin-top:3.2mm;font-family:{KOF};font-size:6.6pt;line-height:10.4pt;color:#262626}}.e-body p{{white-space:nowrap}}
.e-body .last{{color:#0A0A0A;-webkit-text-stroke:.15pt #0A0A0A}}
/* 3안 */
.frost2{{background:rgba(10,10,10,.72);border:.15mm solid rgba(242,242,242,.14)}}
.d-lab{{font-family:Mono,monospace;font-size:5.6pt;letter-spacing:.14em;color:#8C8C8C;white-space:nowrap}}
.d-head{{font-family:{KOF};font-weight:700;font-size:13pt;line-height:18pt;color:#F2F2F2;white-space:nowrap;-webkit-text-stroke:.25pt #F2F2F2}}
.d-body{{font-family:{KOF};font-size:7.8pt;line-height:13pt;color:#B5B5B5;word-break:keep-all}}.d-body p{{white-space:normal;margin-bottom:1.4mm}}
.d-en{{font-family:Lora,serif;font-style:italic;font-size:6.4pt;line-height:9.6pt;color:#7E7E7E}}.d-en p{{white-space:normal}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    body = ''.join(f"<div class='sheet blk'>{p}</div>" for p in (opt1(), opt2(), opt3()))
    h = os.path.join(TMP, 'p02_photo_text_options.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p02 photo text</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p02_photo_text_options.pdf'), os.path.join(TMP, 'p02_pt')], check=True)


if __name__ == '__main__':
    main()
