"""P1 표지 + 1쪽 — B안(Galatasaray 방식, 2026-10-21 채택) InDesign 파일.

  python3 tools/p1_layout/cover_b.py

  docs/shinsegae_vmd/p1_layout/cover_b.idml        InDesign 문서 (파일 > 열기 → .indd 로 저장)
  docs/shinsegae_vmd/p1_layout/cover_b.jsx         같은 문서를 InDesign 안에서 짓는 스크립트 (그레이디언트 페더까지)
  docs/shinsegae_vmd/p1_layout/cover_b_indesign.zip  위 둘 + Links/cover.jpg 를 한 폴더로

지면은 cover_options.py 의 안 B 와 같은 값(mm)이다. 빌더(IDML · JSX)는 cover_p1.py 의 것을 쓴다.
"""
import os
import zipfile

import cover_p1 as base

W, H, BL = base.W, base.H, base.BLEED
para, text, I, B = base.para, base.text, base.I, base.B

base.COLORS = {'Night': (11, 11, 11), 'White': (255, 255, 255), 'Gray Light': (204, 204, 204), 'Gray Mid': (138, 138, 138)}
P = 'Pretendard'
base.STYLES = {
    'Tiny':             dict(font=P, style='Regular', size=6, lead=8, color='Gray Mid', align='left', track=60),
    'Tiny Right':       dict(font=P, style='Regular', size=6, lead=8, color='Gray Mid', align='right', track=60),
    'Tiny White':       dict(font=P, style='Regular', size=6, lead=8, color='White', align='left', track=60),
    'Tiny White Right': dict(font=P, style='Regular', size=6, lead=8, color='White', align='right', track=60),
    'Title':            dict(font=P, style='Bold', size=20, lead=24, color='White', align='left'),
    'Message KO':       dict(font=P, style='Regular', size=10, lead=15, color='Gray Light', align='left'),
    'Message EN':       dict(font=P, style='Regular', size=7.6, lead=11, color='Gray Mid', align='left'),
    'Name':             dict(font=P, style='Bold', size=8, lead=11, color='White', align='right'),
    'Role':             dict(font=P, style='Regular', size=7.6, lead=11, color='Gray Mid', align='right'),
    'Head':             dict(font=P, style='Bold', size=9, lead=12, color='White', align='left'),
    'Body KO':          dict(font=P, style='Regular', size=10, lead=17, color='Gray Light', align='left'),
    'Body EN':          dict(font=P, style='Regular', size=7, lead=10.5, color='Gray Mid', align='left'),
}

ONE_KO = '밖에서 보면 상품이 보이고, 안에서 보면 사람이 보인다.'
ONE_EN = 'From the street you see the products. From inside, you see the people.'
FULL = dict(x=-BL, y=-BL, w=W + 2 * BL, h=H + 2 * BL)

base.ITEMS = [
    # 표지 · 사진 띠(Galatasaray 의 여는 사진) + 검정 바탕의 제목 · 메시지 한 문장
    dict(page=0, kind='rect', fill='Night', name='background', **FULL),
    dict(page=0, kind='image', x=-BL, y=-BL, w=W + 2 * BL, h=142 + BL, fit='center', crop=(0.5, 0.39), name='cover photo band'),
    text(0, 8, 5.5, 80, 4, [para('Tiny White', 'FROM THE INSIDE')], name='mark L'),
    text(0, 209, 5.5, 80, 4, [para('Tiny White Right', '2026')], name='mark R'),
    text(0, 62, 155, 170, 11, [para('Title', 'From the inside')], name='title'),
    text(0, 62, 166, 170, 7, [para('Message KO', ONE_KO)], name='message ko'),
    text(0, 62, 173, 170, 6, [para('Message EN', ONE_EN)], name='message en'),
    text(0, 207, 193, 80, 6, [para('Name', 'JEONG HYEOKJU')], name='name'),
    text(0, 187, 198, 100, 6, [para('Role', 'Visual Merchandiser Portfolio')], name='role'),

    # 1쪽 · The Heritage 처럼 굵은 머리 + 좁은 단의 글, 오른쪽 대표 이미지가 검정으로 녹아든다
    dict(page=1, kind='rect', fill='Night', name='background', **FULL),
    dict(page=1, kind='image', x=170, y=-BL, w=W + BL - 170, h=H + 2 * BL, fit='left', crop=(0.0, 0.5), fade=0.38, name='hero (display back)'),
    text(1, 8, 5.5, 80, 4, [para('Tiny', 'FROM THE INSIDE')], name='mark L'),
    text(1, 209, 5.5, 80, 4, [para('Tiny Right', '01')], name='mark R'),
    text(1, 30, 62, 130, 6, [para('Head', 'Prologue')], name='head'),
    text(1, 30, 71, 130, 52, [para('Body KO', line) for line in base.LEAD_KO], name='body ko'),
    text(1, 30, 128, 112, 32, [para('Body EN', base.CAP_EN)], name='body en'),
]


def main():
    out = base.OUT
    idml, jsx = os.path.join(out, 'cover_b.idml'), os.path.join(out, 'cover_b.jsx')
    base.build_idml(idml)
    base.build_jsx(jsx)
    with zipfile.ZipFile(os.path.join(out, 'cover_b_indesign.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for f in (idml, jsx):
            z.write(f, 'cover_b/' + os.path.basename(f))
        z.write(os.path.join(out, 'Links/cover.jpg'), 'cover_b/Links/cover.jpg')
    print('wrote', idml, jsx)


if __name__ == '__main__':
    main()
