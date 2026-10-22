"""JAJU 포트폴리오 — 2쪽(표지 다음) 메시지 쪽 세 안: 검정 바탕 + 글.

  python3 tools/jaju_layout/p02_message_options.py   ->  docs/jaju_rounding_vmd/layout/p02_message_options.pdf

사용자: 사례 1(Galatasaray S.K.) · 2(NEA Magazine)처럼 첫 쪽은 사진으로 인상을, 둘째 쪽은 검정 바탕에 글로 메시지를.
조건: 검정 바탕 · '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.' 포함 · 프롤로그 일곱 문장(한국어 필수, 영어는 필요하면) ·
문단 바꿈 허용 · 글 · 배치 · 글꼴을 안마다 다르게.
  1안  Galatasaray — 왼쪽 1/5 에서 시작하는 굵은 고딕 제목 한 줄 + 회색 문단 하나. 나머지는 비운다.
  2안  NEA — 가운데 정렬. 가는 명조 제목, 한국어 세 덩어리, 그 아래 영어 한 덩어리.
  3안  유리 — 가운데 세로선이 유리. 왼쪽(밖)은 제목 앞 절반을 거울 글자로, 오른쪽(안)은 뒤 절반을 바로. 아래 두 단에 문장.
PDF 는 표지(흑백 사진) 다음에 세 안을 차례로 — 쪽마다 오른쪽 위 작은 '안' 표시는 비교용이라 최종본에서 지운다.
한글 글꼴: 이 환경에는 문천역정흑 하나뿐이라 시안은 모두 그 글꼴이다. 최종 글꼴은 안마다 아래 FONT 에 적었다(InDesign 단계).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import plan_b14 as b14  # noqa: E402  (COVER-BW 경로)

pe = b14.pe
pc, t, div, photo = pe.pc, pe.t, pe.div, pe.photo
OUT, TMP, PRINT, FONTS = pe.OUT, pe.TMP, pe.PRINT, pe.FONTS

HEAD = '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.'
KO = pc.LEAD_KO  # 일곱 문장 (마지막 = 그래서 나는 안에서 밖을 보는 VMD가 되려 한다.)
EN = pc.LEAD_EN
EN_HEAD = 'From the street you see the products. From inside, you see the people.'
FONT = {
    '1안': '제목 Pretendard Bold · 본문 Pretendard Regular (Galatasaray 의 굵은 산세리프 + 회색 본문)',
    '2안': '제목 · 본문 국문 명조(KoPub바탕 Light 또는 Noto Serif KR Light) · 영문 Instrument Sans (NEA 의 명조 제목 + 산세리프 본문)',
    '3안': '제목 Pretendard SemiBold · 본문 Pretendard Regular · 영문 Lora Italic · 표지 글 IBM Plex Mono',
}


def cover():
    return photo('COVER-BW', 0, 0, 297, 210, focus=(0.5, 0.5))


def tag(s):
    return t(250, 6, 40, 4, s, 'tag r')


# ── 1안 · Galatasaray ────────────────────────────────────────────────────────────────
def opt1():
    body = ' '.join(KO[:-1]) + f" <span class='w'>{KO[-1]}</span>"
    return ''.join([
        t(62, 62, 220, 12, HEAD, 'g-head'),
        t(62, 80, 172, 60, f'<p>{body}</p>', 'g-body wrap'),
        tag('1안 · GALATASARAY'),
    ])


# ── 2안 · NEA ───────────────────────────────────────────────────────────────────────
def opt2():
    ko = (f'<p>{KO[0]}</p><p>{KO[1]}</p><p>{KO[2]}</p><p class="gap"></p>'
          f'<p>{KO[3]}</p><p>{KO[4]}</p><p>{KO[5]}</p><p class="gap"></p><p class="w">{KO[6]}</p>')
    return ''.join([
        t(20, 34, 257, 10, HEAD, 'n-head c'),
        t(20, 46, 257, 6, EN_HEAD.upper(), 'n-sub c'),
        t(48.5, 66, 200, 70, ko, 'n-ko c'),
        t(63.5, 134, 170, 30, f'<p>{EN}</p>', 'n-en c wrap'),
        tag('2안 · NEA'),
    ])


# ── 3안 · 유리 ──────────────────────────────────────────────────────────────────────
def opt3():
    a, b = HEAD.split(', ')
    left = ''.join(f'<p>{s}</p>' for s in KO[:3])
    right = ''.join(f'<p>{s}</p>' for s in KO[3:6]) + f'<p class="w">{KO[6]}</p>'
    return ''.join([
        div(148.4, 26, .2, 90, '', 'glass'),
        t(14, 50, 126, 14, f'{a},', 'm-head mirror r'),
        t(157, 50, 126, 14, b, 'm-head'),
        t(14, 66, 126, 5, 'OUTSIDE — 밖에서 읽으면 거꾸로', 'm-lab r'),
        t(157, 66, 126, 5, 'INSIDE — 안에서 보면 사람', 'm-lab'),
        t(14, 128, 126, 30, left, 'm-ko r'),
        t(157, 128, 126, 40, right, 'm-ko'),
        t(157, 168, 126, 22, f'<p>{EN}</p>', 'm-en wrap'),
        t(14, 192, 126, 5, 'FROM THE INSIDE', 'm-lab r'),
        tag('3안 · GLASS'),
    ])


KOF = "'WenQuanYi Zen Hei',sans-serif"
CSS = pe.CSS + f"""
@font-face{{font-family:Inst;src:url('file://{FONTS}/InstrumentSans-Regular.ttf')}}
@font-face{{font-family:Crimson;src:url('file://{FONTS}/CrimsonPro-Regular.ttf')}}
.sheet.blk{{background:#0A0A0A}}
.tag{{font-family:Mono,monospace;font-size:5pt;letter-spacing:.1em;color:#5a5a5a;white-space:nowrap}}
.w{{color:#F2F2F2}}
/* 1안 */
.g-head{{font-family:{KOF};font-weight:700;font-size:19pt;line-height:24pt;color:#F2F2F2;white-space:nowrap;-webkit-text-stroke:.35pt #F2F2F2}}
.g-body{{font-family:{KOF};font-size:11pt;line-height:19pt;color:#8C8C8C;word-break:keep-all}}.g-body p{{white-space:normal}}
/* 2안 */
.n-head{{font-family:{KOF};font-size:17pt;line-height:22pt;color:#CFCFCF;white-space:nowrap;letter-spacing:.02em}}
.n-sub{{font-family:Crimson,serif;font-size:9pt;letter-spacing:.14em;color:#8C8C8C;white-space:nowrap}}
.n-ko{{font-family:{KOF};font-size:9.6pt;line-height:17pt;color:#BDBDBD}}.n-ko .gap{{height:8pt}}
.n-en{{font-family:Inst,sans-serif;font-size:8pt;line-height:13pt;color:#8C8C8C}}.n-en p{{white-space:normal}}
/* 3안 */
.glass{{background:linear-gradient(to bottom,rgba(242,242,242,0),rgba(242,242,242,.5) 20%,rgba(242,242,242,.5) 80%,rgba(242,242,242,0))}}
.m-head{{font-family:{KOF};font-weight:700;font-size:24pt;line-height:30pt;color:#F2F2F2;white-space:nowrap;-webkit-text-stroke:.3pt #F2F2F2}}
.m-head.mirror{{transform:scaleX(-1);color:#4A4A4A;-webkit-text-stroke:.3pt #4A4A4A;text-align:left}}
.m-lab{{font-family:Mono,monospace;font-size:5.6pt;letter-spacing:.12em;color:#6E6E6E;white-space:nowrap}}
.m-ko{{font-family:{KOF};font-size:9.4pt;line-height:17pt;color:#A6A6A6}}
.m-en{{font-family:Lora,serif;font-style:italic;font-size:7.4pt;line-height:11.5pt;color:#6E6E6E}}.m-en p{{white-space:normal}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    pages = [cover(), opt1(), opt2(), opt3()]
    body = ''.join(f"<div class='sheet{'' if i == 0 else ' blk'}'>{p}</div>" for i, p in enumerate(pages))
    h = os.path.join(TMP, 'p02_message_options.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p02 message options</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p02_message_options.pdf'), os.path.join(TMP, 'p02_msg')], check=True)


if __name__ == '__main__':
    main()
