"""JAJU 포트폴리오 맨 끝 두 쪽(카페 · 창고 / 봉사) — InDesign 파일.

  python3 tools/jaju_layout/indd_outside.py

  docs/jaju_rounding_vmd/indesign/outside_pages/   (+ .zip)
    outside_pages.idml   두 쪽 문서. 봉사 사진 자리는 점선 틀(빈 그래픽 틀 아님 — 지우고 사진을 넣는다)
    outside_pages.pdf    기준 시안
    Links/ · Document Fonts/
순서: outside_pages.py 로 HTML → html2idml_extract.mjs → html2idml.py. 쪽 번호는 책에 넣을 때 정한다.
"""
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '../..'))
NAME = 'outside_pages'
DIR = os.path.join(REPO, 'docs/jaju_rounding_vmd/indesign', NAME)


def main():
    import outside_pages as op
    import html2idml
    op.main()
    html = os.path.join(op.TMP, 'outside_pages.html')
    items = os.path.join(op.TMP, 'outside_pages_items.json')
    subprocess.run(['node', os.path.join(HERE, 'html2idml_extract.mjs'), html, items], check=True)
    if os.path.isdir(DIR):
        shutil.rmtree(DIR)
    os.makedirs(os.path.join(DIR, 'Document Fonts'))
    doc = html2idml.build(items, os.path.join(DIR, NAME + '.idml'), 1, 2, op.W, op.H)
    print(len(doc.stories), 'text frames ·', len(doc.links), 'links ·', len(doc.pstyles), 'paragraph styles')
    fonts = os.path.join(REPO, 'tools/p1_layout/fonts')
    for f in ('InstrumentSans-Regular.ttf', 'InstrumentSans-Bold.ttf', 'InstrumentSans-OFL.txt', 'IBMPlexMono-Regular.ttf',
              'IBMPlexMono-OFL.txt', 'Lora-Italic.ttf', 'Lora-OFL.txt'):
        shutil.copyfile(os.path.join(fonts, f), os.path.join(DIR, 'Document Fonts', f))
    shutil.copyfile(os.path.join(op.OUT, 'outside_pages.pdf'), os.path.join(DIR, NAME + '.pdf'))
    with zipfile.ZipFile(DIR + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
