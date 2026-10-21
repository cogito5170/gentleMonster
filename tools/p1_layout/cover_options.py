"""P1 표지 + 1쪽 재수정 — 두 안을 PDF 한 벌로.

  python3 tools/p1_layout/cover_options.py   ->  docs/shinsegae_vmd/p1_layout/cover_options.pdf

  0쪽  안내 (두 안 축소본 · 무엇을 어디서 가져왔나)
  1–2  안 A · ETÉREO   — 표지: 잡지 표지(종이 테두리 안의 사진 + 머리말). 1쪽: R1 Women of the mountain 을 그대로 따른다
  3–4  안 B · Galatasaray — 표지: 사진 띠 + 검정 바탕의 제목과 메시지 한 문장. 1쪽: 검정 바탕, 좁은 단의 글 + 검정으로 녹아드는 대표 이미지
단위 mm, A4 가로. 그림은 사용자 이미지(Links/cover.jpg)만 쓴다(자르기 · 배치만).
"""
import html
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
OUT = os.path.join(REPO, 'docs/shinsegae_vmd/p1_layout')
TMP = os.path.join(REPO, 'out/p1_layout')
IMG = os.path.join(OUT, 'Links/cover.jpg')
IPX = (1296, 912)

LEAD_KO = [
    '사람들은 쇼윈도를 밖에서 본다. 나는 안에서 본다.',
    '안에서 보면 가게 이름은 거꾸로 읽히고, 진열은 등을 보인다.',
    '대신 유리 너머로 사람들의 얼굴이 보인다.',
    '대부분은 그냥 지나간다.',
    '가끔 누군가 걸음을 멈추고, 들여다보고, 웃는다.',
    '나는 그 사람이 무엇을 보고 웃었는지 본다.',
    '진열의 답은 상품이 아니라 그 표정에 있기 때문이다.',
    '그래서 나는 안에서 밖을 보는 VMD가 되려 한다.',
]
EN = ('People look at a shop window from outside. I look from inside. From inside, the shop’s name reads backwards '
      'and the display shows its back. Instead, I see faces through the glass. Most people walk past. Now and then someone '
      'stops, looks in, and smiles. I watch what made them smile. The answer to a display is in that face, not in the '
      'product. So I want to be a VMD who looks out from the inside.')
ONE_KO = '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.'
ONE_EN = 'From the street you see the products. From inside, you see the people.'
e = html.escape


def box(x, y, w, h, inner='', cls='', style=''):
    return f"<div class='{cls}' style='left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm;{style}'>{inner}</div>"


def photo(x, y, w, h, crop=None, cls='', style=''):
    """틀(x,y,w,h)을 사진으로 가득 채운다. crop=(cx, cy): 원본에서 틀 가운데에 올 점(0–1)."""
    s = max(w / IPX[0], h / IPX[1])
    iw, ih = IPX[0] * s, IPX[1] * s
    cx, cy = crop or (0.5, 0.5)
    ox = min(0, max(w - iw, w / 2 - cx * iw))
    oy = min(0, max(h - ih, h / 2 - cy * ih))
    return box(x, y, w, h, f"<img src='file://{IMG}' style='left:{ox:.3f}mm;top:{oy:.3f}mm;width:{iw:.3f}mm;height:{ih:.3f}mm'>", 'ph ' + cls, style)


def t(x, y, w, h, inner, cls, style=''):
    return box(x, y, w, h, inner, 't ' + cls, style)


# ── 안 A · ETÉREO ─────────────────────────────────────────────────────────────────────
def a_cover():
    pw = 182 * IPX[0] / IPX[1]            # 사진 높이 182 → 폭
    px = (297 - pw) / 2
    return ''.join([
        box(0, 0, 297, 210, '', 'paper'),
        t(px, 7.5, 60, 6, '2026', 'hdb'),
        t(297 - px - 80, 7.5, 80, 6, 'FROM THE INSIDE', 'hdb r'),
        photo(px, 17, pw, 182),
        t(px, 201.5, 150, 5, "<b>JEONG HYEOKJU</b>&nbsp;&nbsp;Visual Merchandiser Portfolio", 'small'),
        t(297 - px - 60, 201.5, 60, 5, 'Shinsegae VMD', 'small r'),
    ])


def a_page1():
    lead = ''.join(f'<p>{e(l)}</p>' for l in LEAD_KO)
    return ''.join([
        box(0, 0, 297, 210, '', 'paper'),
        t(10, 7.5, 80, 6, 'FROM THE INSIDE', 'hdb'), t(90.5, 7.5, 50, 6, 'PROLOGUE', 'hd r'),
        t(156.5, 7.5, 60, 6, '2026', 'hdb'), t(217, 7.5, 70, 6, 'JEONG HYEOKJU', 'hdb r'),
        t(10, 23, 125, 48, lead, 'leadko'),
        t(80, 76, 60.5, 32, f'<p><b>From the inside–</b>{e(EN)}</p>', 'capen'),
        t(8.5, 108, 136, 92, '<p>Inside,</p><p><i>looking</i></p><p>out</p>', 'title bottom'),
        photo(156.5, 23, 130.5, 171, crop=(0.0, 0.5)),
        t(5.4, 116, 20, 3.4, '<i>page</i>&nbsp;&nbsp;1', 'folio', 'transform:rotate(-90deg);transform-origin:0 0'),
        t(291.6, 96, 20, 3.4, '<i>page</i>&nbsp;&nbsp;1', 'folio', 'transform:rotate(90deg);transform-origin:0 0'),
    ])


# ── 안 B · Galatasaray ────────────────────────────────────────────────────────────────
def b_cover():
    return ''.join([
        box(0, 0, 297, 210, '', 'ink'),
        photo(0, 0, 297, 142, crop=(0.5, 0.39)),
        t(8, 5.5, 80, 4, 'FROM THE INSIDE', 'tiny w'), t(209, 5.5, 80, 4, '2026', 'tiny w r'),
        t(62, 155, 170, 9, 'From the inside', 'gtitle'),
        t(62, 166, 170, 6, e(ONE_KO), 'gko'),
        t(62, 173, 170, 5, e(ONE_EN), 'gen'),
        t(207, 193, 80, 5, '<b>JEONG HYEOKJU</b>', 'gname r'),
        t(187, 198, 100, 5, 'Visual Merchandiser Portfolio', 'gen r'),
    ])


def b_page1():
    ko = ''.join(f'<p>{e(l)}</p>' for l in LEAD_KO)
    return ''.join([
        box(0, 0, 297, 210, '', 'ink'),
        photo(170, 0, 127, 210, crop=(0.0, 0.5), cls='fade'),
        t(8, 5.5, 80, 4, 'FROM THE INSIDE', 'tiny'), t(209, 5.5, 80, 4, '01', 'tiny r'),
        t(30, 62, 130, 6, 'Prologue', 'ghead'),
        t(30, 71, 130, 52, ko, 'gbody'),
        t(30, 128, 112, 32, f'<p>{e(EN)}</p>', 'genp'),
    ])


# ── 안내 쪽 ───────────────────────────────────────────────────────────────────────────
def index(pages):
    mini = lambda x, y, inner, cap: (box(x, y, 89.1, 63, f"<div class='sheet'>{inner}</div>", 'mini')
                                     + t(x, y + 64.5, 89.1, 8, cap, 'mcap'))
    rows = [
        ('안 A · ETÉREO', '잡지처럼 — 종이 위의 사진과 세리프 제목',
         '표지: ETÉREO 의 실제 표지처럼 미색 종이 테두리 안에 사진, 위에 작은 머리말 두 개(해 · 책 이름). 제목을 사진 위에 얹지 않아 사진 속 거꾸로 읽히는 글자와 빨간 스카프가 그대로 보인다.<br>'
         '1쪽: R1 Women of the mountain 을 그대로 — 위 리드 문단(국문 8줄) · 가운데 오른쪽 영문 캡션(굵은 첫머리 + 줄표) · 아래 절반을 채우는 대형 세리프 제목 · 오른쪽 면 여백 안의 사진(표지 왼쪽, 진열의 등).'),
        ('안 B · Galatasaray', '사례 연구처럼 — 검정 바탕, 메시지 한 문장',
         '표지: 사진 띠(Galatasaray 의 여는 사진) 아래 검정 바탕에 제목 + 메시지 한 문장(국문 · 영문). 위 구석에 작은 표기 둘.<br>'
         '1쪽: The Heritage 처럼 짧은 굵은 머리 + 좁은 단의 회색 글. 오른쪽은 대표 이미지(진열의 등 · 빨간 스카프)가 검정으로 녹아든다 — 대표 숫자 10 이 검정으로 사라지던 방식.'),
    ]
    tx = ''.join(f"<div class='row'><h3>{a}</h3><h4>{b}</h4><p>{c}</p></div>" for a, b, c in rows)
    return ''.join([
        box(0, 0, 297, 210, '', 'sheetbg'),
        t(12, 9, 270, 8, 'P1 표지 + 1쪽 — 재수정 두 안', 'ih1'),
        t(12, 17.5, 270, 6, '사례: ETÉREO(에디토리얼 진) · Galatasaray(서체 사례 연구). 이미지는 받은 표지 한 장만 — 자르기 · 배치만 했다. 글은 p1_text.md 편집본.', 'ih2'),
        mini(12, 28, pages[0], '안 A · 표지  (2쪽)'), mini(106, 28, pages[1], '안 A · 1쪽  (3쪽)'),
        mini(12, 104, pages[2], '안 B · 표지  (4쪽)'), mini(106, 104, pages[3], '안 B · 1쪽  (5쪽)'),
        t(206, 28, 80, 160, tx, 'itext'),
        t(12, 182, 190, 20, '공통: 이미지 1296 × 912 px — 화면용으로는 충분, A4 인쇄에는 가로 3500 px 이상 원본이 필요하다. '
                            'PDF 의 한글은 이 환경의 글꼴(문천역정흑)이라 최종(Pretendard · 본명조)과 모양이 다르다.', 'note'),
    ])


def font(f):
    return 'file://' + os.path.join(HERE, 'fonts', f)


CSS = f"""
@font-face{{font-family:Crimson;src:url('{font('CrimsonPro-Regular.ttf')}')}}
@font-face{{font-family:Crimson;font-style:italic;src:url('{font('CrimsonPro-Italic.ttf')}')}}
@font-face{{font-family:Inst;src:url('{font('InstrumentSans-Regular.ttf')}')}}
@font-face{{font-family:Inst;font-weight:700;src:url('{font('InstrumentSans-Bold.ttf')}')}}
@page{{size:297mm 210mm;margin:0}}*{{box-sizing:border-box;margin:0;padding:0}}html,body{{background:#777}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;font-family:Inst,'WenQuanYi Zen Hei',sans-serif;color:#1B1A18}}
.sheet{{position:relative;width:297mm;height:210mm;overflow:hidden;page-break-after:always;background:#000}}
.sheet div{{position:absolute}}.t p{{white-space:nowrap}}
.paper{{background:#E6E1DA}}.ink{{background:#0B0B0B}}.sheetbg{{background:#F4F2EE}}
.ph{{overflow:hidden}}.ph img{{position:absolute;display:block}}
.fade{{-webkit-mask-image:linear-gradient(to right,transparent 0,#000 38%);mask-image:linear-gradient(to right,transparent 0,#000 38%)}}
.r{{text-align:right}}
.hd,.hdb{{font-size:9.5pt;line-height:12pt;letter-spacing:.02em;white-space:nowrap}}.hdb{{font-weight:700}}
.small{{font-size:7.5pt;line-height:10pt;white-space:nowrap}}
.leadko{{font-size:9.5pt;line-height:16.5pt}}
.capen{{font-size:6.6pt;line-height:9pt;text-align:justify}}.capen p{{white-space:normal}}
.title{{font-family:Crimson,serif;font-size:94pt;line-height:80pt;letter-spacing:-.012em;display:flex;flex-direction:column;justify-content:flex-end}}
.folio{{font-family:Crimson,serif;font-size:7pt;line-height:8pt;color:#4a463f;white-space:nowrap}}
.tiny{{font-size:6pt;line-height:8pt;letter-spacing:.06em;color:#8a8a8a;white-space:nowrap}}.tiny.w{{color:#f2f2f2}}
.gtitle{{font-size:20pt;line-height:24pt;font-weight:700;color:#fff;white-space:nowrap}}
.gko{{font-size:10pt;line-height:15pt;color:#c9c9c9;white-space:nowrap}}
.gen{{font-size:7.6pt;line-height:11pt;color:#8a8a8a;white-space:nowrap}}
.gname{{font-size:8pt;line-height:11pt;color:#fff;white-space:nowrap}}
.ghead{{font-size:9pt;line-height:12pt;font-weight:700;color:#fff}}
.gbody{{font-size:10pt;line-height:17pt;color:#cfcfcf}}
.genp{{font-size:7pt;line-height:10.5pt;color:#8c8c8c}}.genp p{{white-space:normal}}
.ih1{{font-size:14pt;font-weight:700}}.ih2{{font-size:7.5pt;color:#5d574e}}
.mini{{outline:.2mm solid #999;overflow:hidden}}.mini .sheet{{transform:scale(.3);transform-origin:0 0;position:absolute;left:0;top:0}}
.mcap{{font-size:7pt;font-weight:700}}
.itext{{font-size:7.2pt;line-height:1.5}}.itext .row{{position:static;margin-bottom:5mm}}.itext h3{{font-size:10pt}}.itext h4{{font-size:7.6pt;font-weight:400;color:#5d574e;margin-bottom:1.5mm}}
.itext p{{white-space:normal}}.note{{font-size:6.8pt;color:#5d574e;line-height:1.5}}
"""


def main():
    pages = [a_cover(), a_page1(), b_cover(), b_page1()]
    body = ''.join(f"<div class='sheet'>{p}</div>" for p in [index(pages)] + pages)
    os.makedirs(TMP, exist_ok=True)
    h = os.path.join(TMP, 'cover_options.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>P1 cover options</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(['node', os.path.join(HERE, 'print_pdf.mjs'), h, os.path.join(OUT, 'cover_options.pdf'), os.path.join(TMP, 'cover_options')], check=True)


if __name__ == '__main__':
    main()
