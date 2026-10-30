"""블루엘리펀트 Creative Intern — 포트폴리오 1 시안 (저해상도 사진, 이야기 · 배치 확인용).

  python3 tools/be_layout/p1_draft.py   ->  docs/blue_elephant_creative_intern/layout/p1_draft.pdf

뼈대: 안 A 터널 · 구조 · 장면 + 안 C 의 KEEP 한 쪽 (docs/blue_elephant_creative_intern/storyline_options.md, 사용자 "권하는 방향으로 진행").
재료: 매장 거울 셀카 ME-01–05(사용자 제공) · 인스타그램 캡처를 자른 IG-xx(저해상도, 원본 받으면 교체) · JAJU 때 받은 사진 PH · 건축 AR.
지면 문법(블루엘리펀트 화면 언어에서): 본문 쪽 = 연회색 바탕 · 장식 없는 격자(커머스), 파트 표지 = 전면 사진 + 큰 글자(캠페인).
제품 컷은 만들지 않는다 — 산 안경을 직접 찍기 전까지 빈 칸. 브랜드 형식을 빌린 쪽에는 '지원용 시안 (비공식)'.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../..'))
BE = os.path.join(REPO, 'docs/blue_elephant_creative_intern')
JA = os.path.join(REPO, 'docs/jaju_rounding_vmd/assets')
FONTS = os.path.join(REPO, 'tools/p1_layout/fonts')
PRINT = os.path.join(REPO, 'tools/p1_layout/print_pdf.mjs')
OUT = os.path.join(BE, 'layout')
TMP = '/tmp/be_layout'

SRC = {'ME': f'{BE}/assets/me', 'IG': f'{BE}/assets/ig', 'PH': f'{JA}/photo', 'AR': f'{JA}/arch'}
GREY, INK, MUTE, BLUE = '#E6E6E3', '#121212', '#77756F', '#2B47D6'


def src(pid):
    return 'file://' + os.path.join(SRC[pid[:2]], pid + '.jpg')


def box(x, y, w, h, inner='', cls='', style=''):
    return f"<div class='b {cls}' style='left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm;{style}'>{inner}</div>"


def img(pid, x, y, w, h, pos='50% 50%', cls=''):
    low = " <span class='low'>LOW-RES</span>" if pid.startswith('IG') else ''
    return box(x, y, w, h, f"<img src='{src(pid)}' style='object-position:{pos}'>{low}", 'ph ' + cls)


def slot(x, y, w, h, label):
    return box(x, y, w, h, f"<span>{label}</span>", 'slot')


def t(x, y, w, h, html, cls):
    return box(x, y, w, h, html, 't ' + cls)


def foot(n, part):
    return t(14, 197, 140, 5, f'JEONG HYEOKJU — {part}', 'ft') + t(243, 197, 40, 5, f'{n:02d}', 'ft r')


def mock():
    return t(213, 8, 70, 5, '지원용 시안 (비공식)', 'mock r')


# ── 쪽 ───────────────────────────────────────────────────────────────────────────────
def p_cover():
    return ''.join([
        img('ME-02', 0, 0, 160, 210, '50% 45%'),
        t(172, 20, 112, 6, 'PORTFOLIO 01 — 2026', 'mono'),
        t(172, 70, 115, 44, 'Where the eye stops.', 'hero'),
        t(172, 118, 112, 10, '시선이 멈추는 곳을, 화면으로 만든다.', 'kl'),
        t(172, 168, 112, 18, '<p>JEONG HYEOKJU · 디자인_건축학과</p><p>BLUE ELEPHANT Creative Intern 지원</p>', 'mono'),
        t(172, 186, 112, 6, 'TUNNEL · STRUCTURE · SCENE', 'mono blue'),
    ])


def p_prologue():
    ko = ('<p>블루엘리펀트 매장에 들어섰을 때, 먼저 보인 것은 안경이 아니라 공간이었다. H빔 골조가 드러난 천장과 노출콘크리트 벽, '
          '그 사이사이 오브제처럼 놓인 매대. 공간을 보는 재미에 오래 머물렀다. 거울이 곳곳에 있어 안경을 쓰자마자 내 얼굴을 볼 수 있었고, '
          '그 편함이 결국 구매로 이어졌다.</p>'
          '<p>돌아보면 그날의 순서는 분명했다. 공간이 시선을 끌어들이고, 구조가 그 시선을 정리하고, 거울 앞의 한 장면이 마음을 정했다. '
          '이 포트폴리오는 그 세 단계로 나의 작업을 보여 준다.</p>')
    en = ('In the store, I noticed the space before the glasses — exposed steel beams, bare concrete, counters set like objects. '
          'Mirrors everywhere let me see myself the moment I tried a pair on, and I ended up buying one. '
          'The space drew my eye, the structure ordered it, and a scene in the mirror made the decision.')
    steps = ''.join(f"<div class='st'><b>{a}</b><span>{b}</span></div>" for a, b in
                    [('/01 TUNNEL', '끌어들이다'), ('/02 STRUCTURE', '정리하다'), ('/03 SCENE', '멈추게 하다')])
    return ''.join([
        t(14, 16, 120, 12, 'Prologue.', 'h1'),
        t(14, 40, 128, 80, ko, 'body'),
        t(14, 124, 128, 30, en, 'en'),
        t(14, 160, 128, 24, steps, 'steps'),
        img('ME-01', 156, 16, 62, 82, '50% 40%'), img('ME-04', 222, 16, 62, 82, '50% 45%'),
        img('ME-05', 156, 102, 62, 82, '50% 40%'), img('ME-03', 222, 102, 62, 82, '50% 40%'),
        t(156, 186, 128, 5, '매장 거울 앞에서 — 직접 촬영 ME-01–05', 'cap'),
        foot(1, 'PROLOGUE'),
    ])


def opener(pid, pos, num, word, ko, en, n, dark=False):
    return ''.join([
        img(pid, 0, 0, 297, 210, pos),
        box(0, 0, 297, 210, '', 'shade'),
        t(16, 118, 60, 10, num, 'num'),
        t(14, 128, 270, 40, word, 'giant'),
        t(16, 170, 250, 8, ko, 'okl'),
        t(16, 180, 250, 6, en, 'oen'),
        t(243, 197, 40, 5, f'{n:02d}', 'ft r lt'),
    ])


def p_tunnel_ways():
    ways = [('IG-03', 'FRAME', '격자 창 너머, 불꽃 앞의 요리사.'), ('IG-11', 'DIAGONAL', '매장을 덮은 사선 그림자.'),
            ('PH-12', 'LINE', '한 점으로 모이는 곡선 도로.'), ('IG-04', 'LIGHT', '채광창 아래 붉은 띠 하나.')]
    o = [t(14, 16, 120, 12, 'Four ways in.', 'h1'),
         t(14, 38, 84, 30, '<p>사진을 찍을 때 나는</p><p>네 가지로 시선을 끌어들인다.</p>', 'lead'),
         t(14, 64, 84, 20, 'Frame, diagonal, line and light — four ways I pull the eye into a picture.', 'en'),
         t(14, 170, 84, 16, '<p>내 인스타그램 게시물 15장 가운데.</p><p>저해상도 캡처 — 원본을 받으면 바꾼다.</p>', 'cap')]
    for i, (pid, k, cap) in enumerate(ways):
        x, y = 104 + (i % 2) * 91, 16 + (i // 2) * 88
        o += [img(pid, x, y, 87, 72), t(x, y + 74, 87, 10, f'<b>{k}</b> — {cap}', 'cap2')]
    return ''.join(o) + foot(3, '01 TUNNEL')


def p_tunnel_frames():
    fr = [(1, 1, '1080 × 1080', 'FEED'), (4, 5, '1080 × 1350', 'FEED 4:5'), (9, 16, '1080 × 1920', 'STORY'), (3, 1, '1920 × 640', 'BANNER')]
    o = [t(14, 16, 160, 12, 'One photo, four frames.', 'h1'),
         t(14, 38, 120, 20, '<p>같은 사진도 놓일 화면에 따라 다시 자른다.</p><p>시선이 모이는 점은 그대로 두고, 틀만 바꾼다.</p>', 'lead'),
         t(14, 58, 120, 10, 'Same picture, re-cut for each screen — the point of focus stays, only the frame changes.', 'en')]
    H, x = 70, 14
    for a, b, px, name in fr[:3]:
        w = H * a / b
        o += [img('PH-17', x, 74, w, H, '36% 62%'), t(x, 74 + H + 2, max(w, 30), 8, f'<b>{name}</b><br>{px}', 'cap2')]
        x += w + 6
    o += [img('PH-17', 14, 158, 102, 34, '36% 62%'), t(120, 176, 60, 8, '<b>BANNER</b><br>1920 × 640', 'cap2'),
          t(204, 74, 80, 40, '<p>원본: PH-17 — 접힌 파라솔 셋 옆 돌 벤치에 앉은 사람.</p><p>사람(시선이 모이는 점)이 어느 틀에서도 같은 자리에 오도록 잘랐다.</p>', 'cap')]
    return ''.join(o) + foot(4, '01 TUNNEL')


def p_structure_grid():
    rules = [('BACKGROUND', '연회색 하나'), ('ANGLE', '정면 · 측면 · 3/4 — 같은 순서'), ('MARGIN', '네 변 같은 여백'), ('CENTER', '렌즈 중심을 가운데 선에')]
    o = [t(14, 16, 150, 12, 'Same angle, same grey.', 'h1'),
         t(14, 38, 112, 30, '<p>격자 골조 모형에서 기둥과 보는 같은 간격으로 칸을 나눴다.</p>'
                            '<p>썸네일도 같은 각도, 같은 배경, 같은 여백의 칸 안에서 상품만 바뀌어야 한다.</p>', 'lead'),
         img('AR-03', 14, 78, 56, 42), img('AR-04', 74, 78, 52, 42, '50% 50%'),
         t(14, 122, 112, 6, 'AR-03 격자 골조 모형 · AR-04 반복되는 루버', 'cap'),
         t(14, 140, 112, 40, ''.join(f"<div class='rule'><b>{a}</b><span>{b}</span></div>" for a, b in rules), 'rules'),
         mock()]
    for i in range(6):
        x, y = 140 + (i % 3) * 48, 18 + (i // 3) * 82
        o += [box(x, y, 45, 60, "<div class='cl'></div><div class='cv'></div><span>제품 컷<br>직접 촬영 예정</span>", 'thumb'),
              t(x, y + 62, 45, 12, f"<b>MODEL-{'ABCDEF'[i]}</b><br>{['FRONT', 'SIDE', '3/4'][i % 3]}", 'cap2')]
    return ''.join(o) + foot(6, '02 STRUCTURE')


def glasses_svg():
    return ("<svg viewBox='0 0 120 50' class='gl'><rect x='8' y='14' width='42' height='26' rx='9'/><rect x='70' y='14' width='42' height='26' rx='9'/>"
            "<path d='M50 22 Q60 16 70 22'/><path d='M8 18 L1 16'/><path d='M112 18 L119 16'/>"
            "<path class='d' d='M8 46 H50'/><text x='29' y='50'>A</text><path class='d' d='M50 8 H70'/><text x='60' y='6'>B</text>"
            "<path class='d' d='M3 14 V40'/><text x='0' y='29'>C</text></svg>")


def p_structure_detail():
    blocks = [('01', '어떻게 생겼나', 'FRONT · SIDE · 3/4', None), ('02', '쓰면 어떤가', '착용 컷', 'ME-01'),
              ('03', '무엇으로 만들었나', 'LENS · FRAME', None), ('04', '나에게 맞나', 'SIZE A–E', 'svg'),
              ('05', '무엇이 함께 오나', 'PACKAGE', None), ('06', '받기 전에', 'INFORMATION', None)]
    o = [t(14, 16, 150, 12, 'A detail page, in order.', 'h1'),
         t(14, 38, 104, 36, '<p>상세페이지는 손님이 묻는 순서대로 놓는다.</p>'
                            '<p>어떻게 생겼나, 쓰면 어떤가, 무엇으로 만들었나, 나에게 맞나.</p>', 'lead'),
         t(14, 74, 104, 14, 'A detail page follows the order of a customer\'s questions.', 'en'),
         t(14, 100, 104, 70, ''.join(f"<div class='q'><b>{n}</b><span>{q}</span><i>{k}</i></div>" for n, q, k, _ in blocks), 'qs'),
         mock()]
    x0, w = 150, 70
    y = 16
    hs = [34, 40, 22, 26, 20, 12]
    for (n, q, k, what), h in zip(blocks, hs):
        if what == 'ME-01':
            o.append(img('ME-01', x0, y, w, h, '50% 45%'))
        elif what == 'svg':
            o.append(box(x0, y, w, h, glasses_svg(), 'blk'))
        else:
            o.append(box(x0, y, w, h, f'<span>{k}</span>', 'blk'))
        o.append(t(x0 + w + 4, y + 1, 50, 8, f'<b>{n}</b> {k}', 'cap2'))
        y += h + 2
    return ''.join(o) + foot(7, '02 STRUCTURE')


def p_keep():
    tree = ('BE_SS26/\n'
            '├ 01_RAW/        260301_CAMPAIGN_STUDIO/\n'
            '├ 02_SELECT/\n'
            '├ 03_RETOUCH/    MODEL-A_BLK_FRONT_v02.psd\n'
            '├ 04_EXPORT/\n'
            '│   ├ THUMB_1080x1080/\n'
            '│   ├ DETAIL_860w/\n'
            '│   ├ FEED_1080x1350/\n'
            '│   └ STORY_1080x1920/\n'
            '└ 05_ARCHIVE/')
    return ''.join([
        t(14, 16, 150, 12, 'Keep.', 'h1'),
        t(14, 38, 118, 60, '<p>카페 창고를 정리할 때, 선반을 칸으로 나눠 품목마다 자리를 정했다. 남은 수량이 한눈에 보였고, 찾는 시간이 줄었다.</p>'
                            '<p>촬영 이미지와 디자인 파일도 같다. 자리가 정해져 있어야 찾는 시간이 줄고, 마감이 지켜진다.</p>', 'body'),
        t(14, 100, 118, 16, 'Shelves for stock, folders for files — a fixed place for everything keeps the deadline.', 'en'),
        t(14, 140, 118, 30, '<p><b>이름 규칙</b> 날짜_시즌_모델_색_각도_버전</p><p class=mono>260301_SS26_MODEL-A_BLK_FRONT_v02.jpg</p>'
                             '<p class=cap>예시 — 실제 모델명 · 일정이 아님</p>', 'body sm'),
        box(146, 16, 138, 168, f'<pre>{tree}</pre>', 'tree'),
        mock(),
        foot(8, '02 STRUCTURE — KEEP'),
    ])


def p_mirror():
    shots = [('ME-02', '50% 45%'), ('ME-04', '50% 45%'), ('ME-05', '50% 40%')]
    o = [t(14, 16, 150, 12, 'In the mirror.', 'h1'),
         t(14, 38, 100, 36, '<p>매장 거울 앞에서 나는 몇 번이고 사진을 찍었다.</p><p>손님이 스스로 찍는 이 장면이 가장 자연스러운 콘텐츠다.</p>', 'lead'),
         t(14, 74, 100, 14, 'I kept taking pictures in the store mirrors. The scene customers make themselves is the most natural content.', 'en'),
         t(14, 150, 100, 30, '<p><b>제안</b> — 거울 앞 사진을 모으는 피드 시리즈 <b>IN THE MIRROR</b>. 매장마다 다른 거울과 빛을 번호로 묶는다(0001, 0002 …).</p>', 'body sm'),
         mock()]
    for i, (pid, pos) in enumerate(shots):
        x = 122 + i * 55
        o += [img(pid, x, 30, 51, 64 * 1.25 / 1.0 * 0.85 + 0, pos), t(x, 30 + 69 + 2, 51, 8, f'<b>{i + 1:04d}</b> IN THE MIRROR', 'cap2')]
    o.append(t(122, 120, 161, 6, 'FEED 4:5 · 1080 × 1350 — 직접 촬영 사진으로 만든 피드 시안', 'cap'))
    return ''.join(o) + foot(10, '03 SCENE')


def p_ai():
    steps = [('01 MOOD', '내 사진에서 장면을 고른다', 'img', ['IG-09', 'PH-15', 'IG-05']),
             ('02 DIRECTION', '방향을 한 문장으로', 'txt', '바다 앞 빈 의자 둘, 그 위에 놓인 안경 하나 — 익숙한 장면에 낯선 한 점.'),
             ('03 AI', '시안을 만든다', 'slot', 'AI 시안 — 3_이미지 생성 세션에서 (제품 위조 없이)'),
             ('04 LAYOUT', '화면마다 다시 짠다', 'slot', 'FEED · BANNER · POP')]
    o = [t(14, 16, 200, 12, 'From a photo to a campaign.', 'h1'),
         t(14, 38, 260, 12, '<p>내 사진에서 장면을 고르고, 방향을 문장으로 정하고, AI 로 시안을 만든 뒤, 화면마다 다시 짠다.</p>', 'lead'),
         t(14, 48, 260, 8, 'Pick a scene from my photos, write the direction, make drafts with AI, then rebuild them for each screen.', 'en'),
         mock()]
    for i, (k, d, kind, v) in enumerate(steps):
        x = 14 + i * 68
        o.append(t(x, 64, 64, 12, f'<b>{k}</b><br>{d}', 'cap2'))
        if kind == 'img':
            o += [img(v[0], x, 80, 64, 46), img(v[1], x, 128, 31, 40), img(v[2], x + 33, 128, 31, 40)]
        elif kind == 'txt':
            o.append(box(x, 80, 64, 88, f'<p>{v}</p>', 'dir'))
        else:
            o.append(slot(x, 80, 64, 88, v))
        if i < 3:
            o.append(t(x + 64.5, 118, 4, 6, '→', 'arrow'))
    return ''.join(o) + foot(11, '03 SCENE')


def p_close():
    th = [('PH-13', 'TUNNEL'), ('AR-03', 'STRUCTURE'), ('ME-04', 'SCENE')]
    o = [t(14, 40, 270, 40, 'Where does your eye stop?', 'hero2'),
         t(16, 86, 200, 10, '다음 장면은, 블루엘리펀트의 화면 위에서.', 'kl'),
         t(16, 176, 200, 12, '<p>JEONG HYEOKJU · ____ · ____@____</p>', 'mono')]
    for i, (pid, k) in enumerate(th):
        x = 16 + i * 46
        o += [img(pid, x, 112, 42, 52), t(x, 166, 42, 5, k, 'cap2')]
    return ''.join(o) + foot(12, 'END')


PAGES = [
    (p_cover, 'w'), (p_prologue, 'g'),
    (lambda: opener('PH-13', '50% 40%', '/01', 'TUNNEL.', '내 사진은 시선을 한 점으로 끌어들인다.', 'My photographs pull the eye to a single point.', 2), 'k'),
    (p_tunnel_ways, 'g'), (p_tunnel_frames, 'g'),
    (lambda: opener('AR-03', '50% 50%', '/02', 'STRUCTURE.', '건축에서 배운 구조로, 화면을 정리한다.', 'I order a screen with the structure I learned in architecture.', 5), 'k'),
    (p_structure_grid, 'g'), (p_structure_detail, 'g'), (p_keep, 'g'),
    (lambda: opener('ME-04', '50% 40%', '/03', 'SCENE.', '사람이 멈춰 사진을 찍는 장면을, 화면으로 만든다.', 'I turn the moment people stop for a photo into screens.', 9), 'k'),
    (p_mirror, 'g'), (p_ai, 'g'), (p_close, 'w'),
]


def css():
    f = lambda n: 'file://' + os.path.join(FONTS, n)
    return f"""
@font-face{{font-family:Inst;src:url('{f('InstrumentSans-Regular.ttf')}')}}
@font-face{{font-family:Inst;font-weight:700;src:url('{f('InstrumentSans-Bold.ttf')}')}}
@font-face{{font-family:Mono;src:url('{f('IBMPlexMono-Regular.ttf')}')}}
@page{{size:297mm 210mm;margin:0}}*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#999}}
.sheet{{position:relative;width:297mm;height:210mm;overflow:hidden;page-break-after:always;font-family:Inst,'WenQuanYi Zen Hei',sans-serif;color:{INK}}}
.sheet.g{{background:{GREY}}}.sheet.w{{background:#F7F7F5}}.sheet.k{{background:#111}}
.b{{position:absolute}}.ph{{overflow:hidden;background:#cfcfcb}}.ph img{{width:100%;height:100%;object-fit:cover;display:block}}
.low{{position:absolute;right:1mm;bottom:1mm;font:5pt Mono;color:#fff;background:rgba(0,0,0,.45);padding:.3mm .8mm}}
.shade{{background:linear-gradient(180deg,rgba(0,0,0,0) 45%,rgba(0,0,0,.6))}}
.t p+p{{margin-top:2.2mm}}
.h1{{font-weight:700;font-size:26pt;letter-spacing:-.02em;line-height:1}}
.hero{{font-weight:700;font-size:44pt;line-height:.98;letter-spacing:-.03em}}.hero2{{font-weight:700;font-size:58pt;letter-spacing:-.03em}}
.giant{{font-weight:700;font-size:92pt;line-height:1;color:#fff;letter-spacing:-.04em}}
.num{{font:20pt Mono;color:#fff}}.okl{{font-size:13pt;color:#fff;font-family:'WenQuanYi Zen Hei'}}.oen{{font:8pt Mono;color:#ddd}}
.kl{{font-size:13pt;font-family:'WenQuanYi Zen Hei'}}
.lead{{font-size:11pt;line-height:16pt;font-family:'WenQuanYi Zen Hei'}}
.body{{font-size:9.2pt;line-height:15pt;font-family:'WenQuanYi Zen Hei'}}.body.sm{{font-size:8.4pt;line-height:13pt}}
.en{{font-size:8pt;line-height:11.5pt;color:{MUTE}}}
.cap{{font-size:6.6pt;line-height:9.5pt;color:{MUTE};font-family:'WenQuanYi Zen Hei'}}.cap2{{font-size:7pt;line-height:9.5pt;font-family:'WenQuanYi Zen Hei'}}
.cap2 b,.cap b{{font-family:Inst;font-weight:700;letter-spacing:.04em}}
.mono{{font:7.5pt Mono;letter-spacing:.06em;line-height:11pt}}.blue{{color:{BLUE}}}
.ft{{font:6.5pt Mono;letter-spacing:.08em;color:{MUTE}}}.ft.r{{text-align:right}}.ft.lt{{color:#ccc}}.r{{text-align:right}}
.mock{{font:6.5pt 'WenQuanYi Zen Hei';color:{BLUE};text-align:right}}
.steps .st{{display:flex;gap:4mm;border-top:.3mm solid {INK};padding:1.6mm 0}}.steps b{{width:36mm;font-weight:700;font-size:8pt}}.steps span{{font-size:8.5pt;font-family:'WenQuanYi Zen Hei'}}
.rules .rule,.qs .q{{display:flex;gap:3mm;border-top:.25mm solid #bbb;padding:1.4mm 0;font-size:8pt;font-family:'WenQuanYi Zen Hei'}}
.rules b,.qs b{{width:26mm;font-family:Inst;font-weight:700;font-size:7.5pt;letter-spacing:.05em}}.qs i{{margin-left:auto;font:6.5pt Mono;color:{MUTE};font-style:normal}}
.thumb{{background:#DCDCD8;display:flex;align-items:center;justify-content:center;text-align:center;font:6.5pt 'WenQuanYi Zen Hei';color:{MUTE}}}
.thumb .cl{{position:absolute;left:50%;top:6%;bottom:6%;border-left:.2mm dashed {BLUE}}}.thumb .cv{{position:absolute;top:50%;left:6%;right:6%;border-top:.2mm dashed {BLUE}}}
.thumb span{{background:#DCDCD8;padding:1mm;position:relative}}
.blk{{background:#F4F4F2;display:flex;align-items:center;justify-content:center;font:6.5pt Mono;color:{MUTE};border:.2mm solid #d0d0cc}}
.gl{{width:80%;height:80%}}.gl rect,.gl path{{fill:none;stroke:{INK};stroke-width:1.2}}.gl .d{{stroke:{BLUE};stroke-width:.6}}.gl text{{font:5px Mono;fill:{BLUE}}}
.tree{{background:#F4F4F2;padding:6mm;border:.2mm solid #d0d0cc}}.tree pre{{font:8pt/13pt Mono;color:{INK}}}
.slot{{background:repeating-linear-gradient(45deg,#d9d9d5 0 2mm,#e2e2df 2mm 4mm);display:flex;align-items:center;justify-content:center;text-align:center;padding:4mm;font:7pt 'WenQuanYi Zen Hei';color:{MUTE}}}
.dir{{background:#111;color:#fff;padding:5mm;font:10pt/15pt 'WenQuanYi Zen Hei'}}
.arrow{{font-size:12pt;color:{BLUE}}}
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    body = ''.join(f"<div class='sheet {g}'>{p()}</div>" for p, g in PAGES)
    h = os.path.join(TMP, 'p1_draft.html')
    with open(h, 'w', encoding='utf-8') as fp:
        fp.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>BE p1 draft</title><style>{css()}</style></head><body>{body}</body></html>")
    subprocess.run(['node', PRINT, h, os.path.join(OUT, 'p1_draft.pdf'), os.path.join(TMP, 'p1')], check=True)


if __name__ == '__main__':
    main()
