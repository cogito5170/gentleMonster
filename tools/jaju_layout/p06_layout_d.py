"""JAJU 포트폴리오 6쪽 What made me stop. — 안 D: 왼쪽 위 큰 사진 하나 + 오른쪽 아래 작은 사진 둘 (315 × 195).

  python3 tools/jaju_layout/p06_layout_d.py   ->  docs/jaju_rounding_vmd/layout/p06_layout_d.pdf

사용자: "좌측 상단의 큰 이미지 1개, 우측 하단의 작은 이미지 2개의 레이아웃을 작성한다. 비례, 배치, 텍스트 위치 등은 포트폴리오 사례를 참고하라."
사례: 1 ETÉREO R4(Architecture · Music · Art — 크기가 다른 사진 셋을 엇갈려, 큰 사진 옆에 이탤릭 캡션 제목),
      6 Desjobert(제목 + 2–4줄), 참고 사이트(머리 줄 · 필름 모서리 · 타임코드).
비례: 내용 폭 287mm 를 큰 사진 172 : 오른쪽 단 105 (약 0.6 : 0.4, 사이 10). 큰 사진 높이 95(사진 비 1.8),
      작은 사진은 오른쪽 단 폭을 둘로(50.5 × 28.4) — 큰 사진 넓이의 약 1/11 씩. 대각선(왼쪽 위 크게 → 오른쪽 아래 작게)으로 읽힌다.
사진 셋: a) 빨간 의자(PH-05) · b) 빨간 신호(PH-08) · c) 초록 싹(PH-10) — '다른 하나'의 세 종류(색 · 빛 · 살아 있음).
         분홍 수영복(PH-01)은 a) 와 같은 '색 하나'라 뺐다. 글은 2-2 세션 rev4.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import p06_options as po  # noqa: E402

po.circles = lambda active=None: ''.join(f"<span class='cc{' on' if k == active else ''}'>{k}</span>" for k in 'abc')  # 사진 셋

raw_t = po.raw_t
OUT, TMP, PRINT = po.OUT, po.TMP, po.PRINT

ROWS = [('a)', '빨간 의자', '바닷가의 의자', '색 하나', 'PH-05'), ('b)', '빨간 신호', '밤거리의 불빛', '빛 하나', 'PH-08'),
        ('c)', '초록 싹', '마른 잎 사이의 식물', '살아 있는 하나', 'PH-10')]

END3 = ['진열도 같다.', '먼저 전체를 하나로 맞추고,', '그 안에 하나를 구분되게 둔다.']  # 좁은 단이라 세 줄로 끊음


def opt_d():
    """rev5 — rev4 의 작은 사진(74 × 41.6) 그대로, 큰 사진 오른쪽 끝을 첫 작은 사진(b 빨간 신호)의 빨간 점 세로선까지 키움.
    ETÉREO R4: 큰 사진 옆 단에 글 · 목록, 사진 바닥에 이탤릭 캡션. 왼쪽 아래 = 서술 | 맺음 두 단."""
    SG, SW = 6, 74
    SH = round(SW / 1.78, 2)
    SY = 180.5 - 9 - SH
    SX = 301 - 2 * SW - SG                    # x 147 · 227
    L, BY = 14, 22
    RED_X = 182.42                            # PH-08 빨간 신호 초점의 쪽 위 x (원본 880 px, focus 0.6 · zoom 1.6 으로 잰 값)
    BW = RED_X - L                            # 168.4
    BH = round(BW / 1.78, 2)                  # 94.6
    RX = L + BW + 10                          # 오른쪽 단 x 192.4
    RW = 301 - RX                             # 108.6
    rows = ''.join(f"<div class='r3'><span class='n'>{a}</span><b>{pt}</b><span class='s'>{fit} — {dif}</span></div>" for a, pt, fit, dif, _ in ROWS)
    o = [
        po.card('PH-05', L, BY, BW, BH, 'a)&nbsp;&nbsp;PH-05', '포인트 — 빨간 의자', 'a', '1 / 3', '0.59% OF THE FRAME'),
        # 오른쪽 단: 제목 · 첫 문단 · 질문 · 답 · 영문 · 표
        raw_t(RX, 17, RW, 4, 'PART 1 OBSERVE&nbsp;&nbsp;/&nbsp;&nbsp;06', 'mono'),
        raw_t(RX, 22, RW + 10, 14, po.TITLE, 'jt'),
        raw_t(RX, 39, RW, 8, po.FIRST, 'kb6 wrap'),
        raw_t(RX, 48, RW, 7, po.Q, 'q6'),
        raw_t(RX, 56.5, RW, 14, po.ANS, 'ans wrap'),
        raw_t(RX, 71, RW - 4, 9, po.ANS_EN, 'en6 wrap'),
        raw_t(RX, 81, RW, 4, '포인트 — 어울림 — 다름', 'lab6'),
        raw_t(RX, 85, RW, 18, rows, 'rows3'),
        # 큰 사진 바닥에 맞춘 이탤릭 캡션 (ETÉREO R4)
        raw_t(RX, BY + BH - 13.5, RW, 9, '<i>A</i> red chair.', 'jt2 s'),
        raw_t(RX, BY + BH - 5, RW, 9, po.MEASURE, 'cap6 xs wrap'),
        # 왼쪽 아래: 서술 | 맺음
        raw_t(L, BY + BH + 10, 66, 52, ''.join(f'<p>{s}</p>' for s in po.DESC), 'desc xs wrap'),
        raw_t(L + 74, BY + BH + 10, SX - 8 - L - 74, 22, ''.join(f'<p>{s}</p>' for s in END3), 'end6 s'),
        raw_t(L + 74, BY + BH + 26, SX - 8 - L - 74, 14, po.END_EN, 'en6 wrap'),
    ]
    for i, (a, pt, fit, dif, pid) in enumerate(ROWS[1:]):
        x = SX + i * (SW + SG)
        o.append(po.card(pid, x, SY, SW, SH, f'{a}&nbsp;&nbsp;{pt}', dif, a[0], f'{i + 2} / 3', ''))
    return ''.join(o)


CSS = po.CSS + """
.lab6{font-family:Mono,monospace;font-size:6.4pt;letter-spacing:.1em;color:#9A8F82;white-space:nowrap}
.rows4 .r4{position:static;display:flex;align-items:baseline;gap:2mm;padding:.8mm 0;border-top:.15mm solid #3a332c}
.rows4 .r4:last-child{border-bottom:.15mm solid #3a332c}
.rows4 .n{font-family:Mono,monospace;font-size:7pt;color:#D9773A;width:5mm;flex:none}
.rows4 .t2{position:static}.rows4 b{display:block;font-family:'WenQuanYi Zen Hei',sans-serif;font-weight:700;font-size:9pt;line-height:13pt;color:#EFE3CB}
.rows4 .s{display:block;font-family:'WenQuanYi Zen Hei',sans-serif;font-size:7pt;line-height:10pt;color:#A99F92;white-space:nowrap}
.desc.xs{font-size:7pt;line-height:10.6pt}
.rows3 .r3{padding:.8mm 0}.rows3 b{width:17mm;font-size:8.6pt}.rows3 .s{font-size:7.4pt}
.jt2.s{font-size:19pt;line-height:21pt}.cap6.xs{font-size:7pt;line-height:10pt}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    html, g = po.page(opt_d)
    h = os.path.join(TMP, 'p06_layout_d.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>JAJU p06 D</title><style>{CSS}</style></head>"
                f"<body><div class='sheet {g}'>{html}</div></body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p06_layout_d.pdf'), os.path.join(TMP, 'p06d')], check=True)


if __name__ == '__main__':
    main()
