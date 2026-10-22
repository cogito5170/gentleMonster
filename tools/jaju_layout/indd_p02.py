"""JAJU 포트폴리오 2쪽 메시지 — 2안(NEA 방식) InDesign 파일.

  python3 tools/jaju_layout/indd_p02.py

  docs/jaju_rounding_vmd/indesign/p02_message_nea/
    p02_message_nea.idml   InDesign 문서 (파일 > 열기 → .indd 로 저장)
    p02_message_nea.jsx    같은 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 열리지 않을 때)
    p02_message_nea.pdf    기준 시안 (비교용 '안' 표시를 뺀 2안)
    Document Fonts/        Crimson Pro · Instrument Sans (OFL). 국문 명조 Noto Serif KR 는 따로 설치
  docs/jaju_rounding_vmd/indesign/p02_message_nea.zip

값은 p02_message_options.py 의 opt2() 와 같다(mm). 빌더는 indd_p03.py 의 것을 쓴다.
한글은 시안에서 문천역정흑(이 환경의 유일한 한글 글꼴)이지만, 2안의 최종 글꼴인 명조(Noto Serif KR)로 지정한다.
"""
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import indd_p03 as base  # noqa: E402
import p02_message_options as opt  # noqa: E402

NAME = 'p02_message_nea'
DIR = os.path.join(base.REPO, 'docs/jaju_rounding_vmd/indesign', NAME)
W, H, BL = base.W, base.H, base.BLEED

base.PAGE_NO = 2
base.COLORS = {'Black': (10, 10, 10), 'Title': (207, 207, 207), 'Body': (189, 189, 189), 'Mute': (140, 140, 140), 'White': (242, 242, 242)}
SERIF, CR, IS = 'Noto Serif KR', 'Crimson Pro', 'Instrument Sans'
base.STYLES = {
    'Title':        dict(font=SERIF, style='Regular', size=17, lead=22, color='Title', align='center', track=20),
    'Subtitle':     dict(font=CR, style='Regular', size=9, lead=11, color='Mute', align='center', track=140),
    'Body KO':      dict(font=SERIF, style='Light', size=9.6, lead=17, color='Body', align='center'),
    'Body KO Next': dict(font=SERIF, style='Light', size=9.6, lead=17, color='Body', align='center', before=8),
    'Body KO Last': dict(font=SERIF, style='Regular', size=9.6, lead=17, color='White', align='center', before=8),
    'Body EN':      dict(font=IS, style='Regular', size=8, lead=13, color='Mute', align='center'),
}
KO = opt.KO
T = base.T
base.ITEMS = [
    dict(kind='rect', x=-BL, y=-BL, w=W + 2 * BL, h=H + 2 * BL, fill='Black', name='background'),
    T(20, 34, 257, 10, [('Title', opt.HEAD)], 'title'),
    T(20, 46, 257, 6, [('Subtitle', opt.EN_HEAD.upper())], 'subtitle'),
    T(48.5, 66, 200, 64, [('Body KO', KO[0]), ('Body KO', KO[1]), ('Body KO', KO[2]),
                          ('Body KO Next', KO[3]), ('Body KO', KO[4]), ('Body KO', KO[5]), ('Body KO Last', KO[6])], 'body ko'),
    T(63.5, 134, 170, 30, [('Body EN', opt.EN)], 'body en'),
]


def reference_pdf(path_out):
    """비교용 '안' 표시를 뺀 2안 한 쪽."""
    html = opt.opt2().replace(opt.tag('2안 · NEA'), '')
    h = os.path.join(opt.TMP, NAME + '.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>{NAME}</title><style>{opt.CSS}</style></head>"
                f"<body><div class='sheet blk'>{html}</div></body></html>")
    subprocess.run(['node', opt.PRINT, h, path_out, os.path.join(opt.TMP, NAME)], check=True)


def main():
    os.makedirs(os.path.join(DIR, 'Document Fonts'), exist_ok=True)
    base.build_idml(os.path.join(DIR, NAME + '.idml'))
    base.build_jsx(os.path.join(DIR, NAME + '.jsx'))
    for f in ('CrimsonPro-Regular.ttf', 'CrimsonPro-OFL.txt', 'InstrumentSans-Regular.ttf', 'InstrumentSans-OFL.txt'):
        shutil.copyfile(os.path.join(base.FONTS, f), os.path.join(DIR, 'Document Fonts', f))
    reference_pdf(os.path.join(DIR, NAME + '.pdf'))
    with zipfile.ZipFile(os.path.join(os.path.dirname(DIR), NAME + '.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
