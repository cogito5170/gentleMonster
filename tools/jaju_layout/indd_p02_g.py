"""JAJU 포트폴리오 2쪽 메시지 — 1안(Galatasaray 방식) InDesign 파일.

  python3 tools/jaju_layout/indd_p02_g.py

  docs/jaju_rounding_vmd/indesign/p02_message_galatasaray/
    p02_message_galatasaray.idml   InDesign 문서 (파일 > 열기 → .indd 로 저장)
    p02_message_galatasaray.jsx    같은 쪽을 InDesign 안에서 짓는 스크립트 (IDML 이 열리지 않을 때)
    p02_message_galatasaray.pdf    기준 시안 (비교용 '안' 표시를 뺀 1안)
  docs/jaju_rounding_vmd/indesign/p02_message_galatasaray.zip

값은 p02_message_options.py 의 opt1() 과 같다(mm). 빌더는 indd_p03.py 의 것을 쓴다.
글꼴은 Pretendard 하나(Bold 제목 · Regular 본문) — 따로 설치. 본문은 한 문단, 마지막 문장만 흰색(글자 단위 색).
"""
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import indd_p03 as base  # noqa: E402
import p02_message_options as opt  # noqa: E402

NAME = 'p02_message_galatasaray'
DIR = os.path.join(base.REPO, 'docs/jaju_rounding_vmd/indesign', NAME)
W, H, BL = base.W, base.H, base.BLEED

base.PAGE_NO = 2
base.COLORS = {'Black': (10, 10, 10), 'White': (242, 242, 242), 'Gray': (140, 140, 140)}
P = 'Pretendard'
base.STYLES = {
    'Title': dict(font=P, style='Bold', size=19, lead=24, color='White', align='left'),
    'Body':  dict(font=P, style='Regular', size=11, lead=19, color='Gray', align='left'),
}
KO = opt.KO
LAST = KO[-1]
BODY = ' '.join(KO[:-1]) + ' ' + LAST
T = base.T
base.ITEMS = [
    dict(kind='rect', x=-BL, y=-BL, w=W + 2 * BL, h=H + 2 * BL, fill='Black', name='background'),
    T(62, 62, 220, 12, [('Title', opt.HEAD)], 'title'),
    T(62, 80, 172, 60, [('Body', BODY)], 'body'),
]

# 마지막 문장만 흰색: 빌더가 만든 글에 글자 단위 색을 덧입힌다
_idml, _jsx = base.build_idml, base.build_jsx


def build_idml(path_out):
    _idml(path_out)
    tmp = path_out + '.tmp'
    with zipfile.ZipFile(path_out) as zin, zipfile.ZipFile(tmp, 'w') as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith('Stories/') and base.q(BODY).encode() in data:
                head = base.q(' '.join(KO[:-1]) + ' ')
                old = f'<Content>{base.q(BODY)}</Content>'
                new = (f'<Content>{head}</Content></CharacterStyleRange>'
                       f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" FillColor="Color/White">'
                       f'<Content>{base.q(LAST)}</Content>')
                data = data.decode().replace(old, new).encode()
            zout.writestr(item, data, compress_type=item.compress_type)
    os.replace(tmp, path_out)


def build_jsx(path_out):
    _jsx(path_out)
    with open(path_out, encoding='utf-8') as f:
        s = f.read()
    start = len(BODY) - len(LAST)
    s = s.replace('})();', f'var b = pg.textFrames.itemByName("body"); b.parentStory.characters.itemByRange({start}, {len(BODY) - 1}).fillColor = C["White"];\n}})();')
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write(s)


def reference_pdf(path_out):
    html = opt.opt1().replace(opt.tag('1안 · GALATASARAY'), '')
    h = os.path.join(opt.TMP, NAME + '.html')
    with open(h, 'w', encoding='utf-8') as f:
        f.write(f"<!doctype html><html lang=ko><head><meta charset=utf-8><title>{NAME}</title><style>{opt.CSS}</style></head>"
                f"<body><div class='sheet blk'>{html}</div></body></html>")
    subprocess.run(['node', opt.PRINT, h, path_out, os.path.join(opt.TMP, NAME)], check=True)


def main():
    os.makedirs(DIR, exist_ok=True)
    build_idml(os.path.join(DIR, NAME + '.idml'))
    build_jsx(os.path.join(DIR, NAME + '.jsx'))
    reference_pdf(os.path.join(DIR, NAME + '.pdf'))
    with zipfile.ZipFile(os.path.join(os.path.dirname(DIR), NAME + '.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
