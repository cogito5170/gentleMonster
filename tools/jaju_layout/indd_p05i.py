"""JAJU 포트폴리오 5쪽 일정표 격자 꼴(315 × 195) — InDesign 파일.

  python3 tools/jaju_layout/indd_p05i.py

  docs/jaju_rounding_vmd/indesign/p05_itinerary/   (+ .zip)
    p05_itinerary.idml   한 쪽 문서 (쪽 번호 5)
    p05_itinerary.pdf    기준 시안
    Links/ · Document Fonts/
순서: p05_itinerary.py 로 HTML → html2idml_extract.mjs → html2idml.py.
"""
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '../..'))
NAME = 'p05_itinerary'
DIR = os.path.join(REPO, 'docs/jaju_rounding_vmd/indesign', NAME)


def main():
    import p05_itinerary as d6
    import html2idml
    d6.main()
    html = os.path.join(d6.TMP, 'p05_itinerary.html')
    items = os.path.join(d6.TMP, 'p05_itinerary_items.json')
    subprocess.run(['node', os.path.join(HERE, 'html2idml_extract.mjs'), html, items], check=True)
    if os.path.isdir(DIR):
        shutil.rmtree(DIR)
    os.makedirs(os.path.join(DIR, 'Document Fonts'))
    doc = html2idml.build(items, os.path.join(DIR, NAME + '.idml'), 1, 1, d6.W, d6.H)
    # 쪽 번호를 5 으로 (한 쪽 문서라 build 의 첫 쪽 = 1)
    tmp = os.path.join(DIR, NAME + '.idml')
    z_in = zipfile.ZipFile(tmp)
    parts = {n: z_in.read(n) for n in z_in.namelist()}
    z_in.close()
    parts['designmap.xml'] = parts['designmap.xml'].replace(b'PageNumberStart="1"', b'PageNumberStart="5"')
    parts['Spreads/Spread_uSp0.xml'] = parts['Spreads/Spread_uSp0.xml'].replace(b'Name="1" AppliedMaster', b'Name="5" AppliedMaster')
    with zipfile.ZipFile(tmp, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), parts.pop('mimetype'), compress_type=zipfile.ZIP_STORED)
        for n, b in parts.items():
            z.writestr(n, b, compress_type=zipfile.ZIP_DEFLATED)
    print(len(doc.stories), 'text frames ·', len(doc.links), 'links ·', len(doc.pstyles), 'paragraph styles')
    fonts = os.path.join(REPO, 'tools/p1_layout/fonts')
    for f in ('CrimsonPro-Regular.ttf', 'CrimsonPro-Italic.ttf', 'CrimsonPro-OFL.txt', 'Lora-Italic.ttf', 'Lora-OFL.txt',
              'IBMPlexMono-Regular.ttf', 'IBMPlexMono-OFL.txt', 'InstrumentSans-Regular.ttf', 'InstrumentSans-OFL.txt'):
        shutil.copyfile(os.path.join(fonts, f), os.path.join(DIR, 'Document Fonts', f))
    shutil.copyfile(os.path.join(d6.OUT, 'p05_itinerary.pdf'), os.path.join(DIR, NAME + '.pdf'))
    with zipfile.ZipFile(DIR + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
