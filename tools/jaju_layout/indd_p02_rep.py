"""JAJU 포트폴리오 2쪽 — 리포타주 판(p02_reportage.py) InDesign 파일.

  python3 tools/jaju_layout/indd_p02_rep.py

  docs/jaju_rounding_vmd/indesign/p02_reportage/   (+ p02_reportage.zip)
    p02_reportage.idml   InDesign 문서 (파일 > 열기 → .indd 로 저장)
    p02_reportage.jsx    같은 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 열리지 않을 때)
    p02_reportage.pdf    기준 시안
    Links/opening_book_dark.jpg
    Document Fonts/      IBM Plex Mono · Instrument Sans (OFL). Noto Serif KR · Pretendard 는 따로 설치

값은 p02_reportage.py 와 같다(mm). 사진은 재단 여유까지 덮도록 약 3% 키웠다(가운데 그대로).
어둡게 하기 = 검정 사각형 둘: 위 → 아래 그레이디언트 페더(50% → 22% → 22% → 60%), 왼쪽 → 오른쪽 페더(쪽의 46% 투명 → 54% 86% → 60% 불투명).
"""
import os
import shutil
import sys
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import indd_p03 as base  # noqa: E402
import p02_reportage as rep  # noqa: E402

NAME = 'p02_reportage'
DIR = os.path.join(base.REPO, 'docs/jaju_rounding_vmd/indesign', NAME)
W, H, BL = base.W, base.H, base.BLEED
IMG = rep.pt.IMG
FILE = os.path.basename(IMG)
KO, EN = rep.KO, rep.EN
SERIF, P, MO, IS = 'Noto Serif KR', 'Pretendard', 'IBM Plex Mono', 'Instrument Sans'

base.PAGE_NO = 2
base.COLORS = {'Ink': (13, 14, 16), 'Label': (142, 140, 136), 'Cream': (239, 227, 203), 'Sub': (228, 214, 186),
               'Body': (169, 167, 162), 'English': (124, 122, 118), 'Edge': (49, 48, 46)}
base.STYLES = {
    'Label':   dict(font=MO, style='Regular', size=6.4, lead=8, color='Label', align='left', track=60),
    'Title':   dict(font=SERIF, style='Light', size=19, lead=26, color='Cream', align='left', track=-10),
    'Sub':     dict(font=MO, style='Regular', size=7.4, lead=9, color='Sub', align='left', track=80),
    'Body':    dict(font=P, style='Regular', size=8.4, lead=14, color='Body', align='left'),
    'English': dict(font=IS, style='Regular', size=6.2, lead=9.4, color='English', align='left', track=20),
    'Edge':    dict(font=MO, style='Regular', size=3.6, lead=4.5, color='Edge', align='left'),
}


def stop(x_mm):
    return round((x_mm + BL) / (W + 2 * BL) * 100, 1)


T = base.T
FULL = dict(x=-BL, y=-BL, w=W + 2 * BL, h=H + 2 * BL)
k = (H + 2 * BL) / Image.open(IMG).size[1]
iw = Image.open(IMG).size[0] * k
cx = -64 + 160.2  # 시안의 사진 가운데
body2 = ' '.join(KO[3:])
items = [
    dict(kind='rect', fill='Ink', name='background', **FULL),
    dict(kind='image', x=-BL, y=-BL, w=cx + iw / 2 + BL, h=H + 2 * BL, file=FILE, px=Image.open(IMG).size,
         place=(cx - iw / 2, -BL, iw, H + 2 * BL), name='photo'),
    dict(kind='rect', fill='Ink', name='darken (top / bottom)', feather=[(0, 50), (22, 22), (70, 22), (100, 60)], **FULL),
    dict(kind='rect', fill='Ink', name='fade to text column', feather_dir='right',
         feather=[(stop(.46 * W), 0), (stop(.54 * W), 86), (stop(.60 * W), 100), (100, 100)], **FULL),
    T(170, 54, 110, 4, [('Label', 'PROLOGUE  /  FROM THE INSIDE')], 'label'),
    T(170, 62, 115, 30, [('Title', '밖에서 보면 상품이 보이고,'), ('Title', '안에서 보면 사람이 보인다.')], 'title'),
    T(170, 88, 115, 5, [('Sub', 'A VMD WHO LOOKS OUT FROM THE INSIDE')], 'subtitle'),
    T(170, 104, 92, 30, [('Body', ' '.join(KO[:3]))], 'body 1'),
    T(170, 126, 92, 36, [('Body', body2)], 'body'),
    T(170, 158, 92, 40, [('English', EN.upper())], 'english'),
]
for i, y in enumerate(range(14, 200, 16)):
    items.append(dict(T(2.2, y, 8, 3, [('Edge', f'{i * 4 + 2:02d}')], f'edge L {i}'), rotate=90))
    items.append(dict(T(288, y + 8, 8, 3, [('Edge', f'{i * 4 + 4:02d}')], f'edge R {i}'), rotate=90))
base.ITEMS = items


def cream_tail(path_idml, path_jsx, body, tail):
    tmp = path_idml + '.tmp'
    old = f'<Content>{base.q(body)}</Content>'.encode()
    with zipfile.ZipFile(path_idml) as zin, zipfile.ZipFile(tmp, 'w') as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith('Stories/') and old in data:
                data = data.replace(old, (f'<Content>{base.q(body[:-len(tail)])}</Content></CharacterStyleRange>'
                                          f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FillColor="Color/Cream">'
                                          f'<Content>{base.q(tail)}</Content>').encode())
            zout.writestr(item, data, compress_type=item.compress_type)
    os.replace(tmp, path_idml)
    with open(path_jsx, encoding='utf-8') as f:
        s = f.read()
    s = s.replace('})();', f'var b = pg.textFrames.itemByName("body"); b.parentStory.characters.itemByRange({len(body) - len(tail)}, {len(body) - 1}).fillColor = C["Cream"];\n}})();')
    with open(path_jsx, 'w', encoding='utf-8') as f:
        f.write(s)


def main():
    os.makedirs(os.path.join(DIR, 'Links'), exist_ok=True)
    os.makedirs(os.path.join(DIR, 'Document Fonts'), exist_ok=True)
    idml, jsx = os.path.join(DIR, NAME + '.idml'), os.path.join(DIR, NAME + '.jsx')
    base.build_idml(idml)
    base.build_jsx(jsx)
    cream_tail(idml, jsx, body2, KO[-1])
    shutil.copyfile(IMG, os.path.join(DIR, 'Links', FILE))
    for f in ('IBMPlexMono-Regular.ttf', 'IBMPlexMono-OFL.txt', 'InstrumentSans-Regular.ttf', 'InstrumentSans-OFL.txt'):
        shutil.copyfile(os.path.join(base.FONTS, f), os.path.join(DIR, 'Document Fonts', f))
    shutil.copyfile(os.path.join(rep.OUT, 'p02_reportage.pdf'), os.path.join(DIR, NAME + '.pdf'))
    with zipfile.ZipFile(DIR + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
