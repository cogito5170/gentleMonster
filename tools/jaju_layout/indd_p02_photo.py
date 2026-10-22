"""JAJU 포트폴리오 2쪽 — 사진 위 메시지 1안(Galatasaray) · 3안(Desjobert) InDesign 파일.

  python3 tools/jaju_layout/indd_p02_photo.py

  docs/jaju_rounding_vmd/indesign/p02_photo_galatasaray/   (+ .zip)
  docs/jaju_rounding_vmd/indesign/p02_photo_desjobert/     (+ .zip)
    <이름>.idml   InDesign 문서 (파일 > 열기 → .indd 로 저장)
    <이름>.jsx    같은 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 열리지 않을 때)
    <이름>.pdf    기준 시안 (비교용 '안' 표시를 뺀 한 쪽)
    Links/opening_book_dark.jpg     사진 (사용자 제공)
    Document Fonts/                 Lora · IBM Plex Mono (3안, OFL)

값은 p02_photo_text_options.py 의 opt1() · opt3() 과 같다(mm). 빌더는 indd_p03.py.
사진 틀은 재단 여유 3mm 까지 넓혔다(시안은 쪽 안). 1안의 검정 녹임은 검정 사각형 + 그레이디언트 페더(위 30% 투명 → 58% 75% → 72% 96%),
3안의 글 상자는 검정 사각형 불투명도 72%. 한글 글꼴 Pretendard 는 따로 설치.
"""
import os
import shutil
import subprocess
import sys
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import indd_p03 as base  # noqa: E402
import p02_photo_text_options as opt  # noqa: E402

W, H, BL = base.W, base.H, base.BLEED
IMG = opt.IMG
FILE = os.path.basename(IMG)
PX = Image.open(IMG).size
P, LO, MO = 'Pretendard', 'Lora', 'IBM Plex Mono'
KO, HEAD, EN = opt.KO, opt.HEAD, opt.EN
T = base.T
PHOTO = dict(kind='image', x=-BL, y=-BL, w=W + 2 * BL, h=H + 2 * BL, file=FILE, px=PX, focus=(0.5, 0.5), name='photo')
BLACK = dict(kind='rect', x=-BL, y=-BL, w=W + 2 * BL, h=H + 2 * BL, fill='Black', name='background (black)')


def white_tail(path_idml, path_jsx, body, tail):
    """본문 끝 문장만 흰색 — IDML 은 글자 범위를 둘로 나누고, JSX 는 글자 범위에 색."""
    tmp = path_idml + '.tmp'
    with zipfile.ZipFile(path_idml) as zin, zipfile.ZipFile(tmp, 'w') as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            old = f'<Content>{base.q(body)}</Content>'.encode()
            if item.filename.startswith('Stories/') and old in data:
                new = (f'<Content>{base.q(body[:-len(tail)])}</Content></CharacterStyleRange>'
                       f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FillColor="Color/White">'
                       f'<Content>{base.q(tail)}</Content>').encode()
                data = data.replace(old, new)
            zout.writestr(item, data, compress_type=item.compress_type)
    os.replace(tmp, path_idml)
    with open(path_jsx, encoding='utf-8') as f:
        s = f.read()
    s = s.replace('})();', f'var b = pg.textFrames.itemByName("body"); b.parentStory.characters.itemByRange({len(body) - len(tail)}, {len(body) - 1}).fillColor = C["White"];\n}})();')
    with open(path_jsx, 'w', encoding='utf-8') as f:
        f.write(s)


def setup_1():
    base.COLORS = {'Black': (10, 10, 10), 'White': (242, 242, 242), 'Gray': (154, 154, 154)}
    base.STYLES = {
        'Title': dict(font=P, style='Bold', size=19, lead=24, color='White', align='left'),
        'Body':  dict(font=P, style='Regular', size=10, lead=17, color='Gray', align='left'),
    }
    body = ' '.join(KO)
    base.ITEMS = [BLACK, PHOTO,
                  dict(kind='rect', x=-BL, y=-BL, w=W + 2 * BL, h=H + 2 * BL, fill='Black', name='fade to black',
                       feather=[(30, 0), (58, 75), (72, 96), (100, 96)]),
                  T(62, 140, 220, 12, [('Title', HEAD)], 'title'),
                  T(62, 156, 180, 40, [('Body', body)], 'body')]
    return body, KO[-1], [], opt.opt1, '1안 · GALATASARAY'


def setup_3():
    base.COLORS = {'Black': (10, 10, 10), 'White': (242, 242, 242), 'Label': (140, 140, 140), 'Body': (181, 181, 181),
                   'English': (126, 126, 126), 'Edge': (90, 90, 90)}
    base.STYLES = {
        'Label':      dict(font=MO, style='Regular', size=5.6, lead=7, color='Label', align='left', track=140),
        'Title':      dict(font=P, style='SemiBold', size=13, lead=18, color='White', align='left'),
        'Body':       dict(font=P, style='Regular', size=7.8, lead=13, color='Body', align='left'),
        'Body Next':  dict(font=P, style='Regular', size=7.8, lead=13, color='Body', align='left', before=4),
        'Body Last':  dict(font=P, style='Regular', size=7.8, lead=13, color='White', align='left', before=4),
        'English':    dict(font=LO, style='Italic', size=6.4, lead=9.6, color='English', align='left'),
    }
    a, b = HEAD.split(', ')
    base.ITEMS = [BLACK, PHOTO,
                  dict(kind='rect', x=203, y=24, w=82, h=164, fill='Black', opacity=72, stroke=('Edge', .15), name='text box'),
                  T(210, 32, 70, 4, [('Label', 'PROLOGUE')], 'label top'),
                  T(210, 41, 70, 24, [('Title', a + ','), ('Title', b)], 'title'),
                  T(210, 68, 68, 66, [('Body', KO[0])] + [('Body Next', s) for s in KO[1:-1]] + [('Body Last', KO[-1])], 'body'),
                  T(210, 136, 68, 34, [('English', EN)], 'english'),
                  T(210, 180, 70, 4, [('Label', 'FROM THE INSIDE')], 'label bottom')]
    fonts = ['Lora-Italic.ttf', 'Lora-OFL.txt', 'IBMPlexMono-Regular.ttf', 'IBMPlexMono-OFL.txt']
    return None, None, fonts, opt.opt3, '3안 · DESJOBERT'


def reference_pdf(fn, label, path_out, name):
    html = fn().replace(opt.tag(label), '')
    h = os.path.join(opt.TMP, name + '.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>{name}</title><style>{opt.CSS}</style></head>"
                f"<body><div class='sheet blk'>{html}</div></body></html>")
    subprocess.run(['node', opt.PRINT, h, path_out, os.path.join(opt.TMP, name)], check=True)


def build(name, setup):
    base.PAGE_NO = 2
    body, tail, fonts, fn, label = setup()
    d = os.path.join(base.REPO, 'docs/jaju_rounding_vmd/indesign', name)
    os.makedirs(os.path.join(d, 'Links'), exist_ok=True)
    idml, jsx = os.path.join(d, name + '.idml'), os.path.join(d, name + '.jsx')
    base.build_idml(idml)
    base.build_jsx(jsx)
    if body:
        white_tail(idml, jsx, body, tail)
    shutil.copyfile(IMG, os.path.join(d, 'Links', FILE))
    if fonts:
        os.makedirs(os.path.join(d, 'Document Fonts'), exist_ok=True)
        for f in fonts:
            shutil.copyfile(os.path.join(base.FONTS, f), os.path.join(d, 'Document Fonts', f))
    reference_pdf(fn, label, os.path.join(d, name + '.pdf'), name)
    with zipfile.ZipFile(d + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(d):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(d)))
    print('wrote', d)


def main():
    build('p02_photo_galatasaray', setup_1)
    build('p02_photo_desjobert', setup_3)


if __name__ == '__main__':
    main()
