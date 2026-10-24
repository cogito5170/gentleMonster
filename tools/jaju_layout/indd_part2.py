"""JAJU 포트폴리오 파트 2 /02 Match. 8–11쪽 — InDesign 파일.

  python3 tools/jaju_layout/indd_part2.py

  docs/jaju_rounding_vmd/indesign/part2_match/   (+ .zip)
    part2_match.idml   네 쪽 문서 (쪽 번호 8–11). 8쪽은 글만 — 사용자 표지 이미지를 맨 아래에 놓는다
    part2_match.pdf    기준 시안 (8쪽은 자리 표시 위 미리 보기)
    Links/ · Document Fonts/
순서: part2_match.py 로 HTML → html2idml_extract.mjs → html2idml.py.
"""
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '../..'))
NAME = 'part2_match'
DIR = os.path.join(REPO, 'docs/jaju_rounding_vmd/indesign', NAME)
FIRST = 8


def main():
    import part2_match as p2
    import html2idml
    p2.main()
    # InDesign 용: 8쪽 자리 표시(색 면 · 인물 점선)는 빼고 글만, 한국어 표지 글은 210 타임라인
    p2.p08 = lambda: p2.cm.text().replace("class='t ko'", "data-font='210 타임라인|Regular' class='t ko'")
    html = os.path.join(p2.TMP, 'part2_match_indd.html')
    with open(html, 'w', encoding='utf-8') as f:
        f.write(p2.html_doc([(8, p2.p08)] + p2.PAGES[1:]))
    items = os.path.join(p2.TMP, 'part2_match_items.json')
    subprocess.run(['node', os.path.join(HERE, 'html2idml_extract.mjs'), html, items], check=True)
    if os.path.isdir(DIR):
        shutil.rmtree(DIR)
    os.makedirs(os.path.join(DIR, 'Document Fonts'))
    out = os.path.join(DIR, NAME + '.idml')
    doc = html2idml.build(items, out, 1, 4, p2.W, p2.H)
    z_in = zipfile.ZipFile(out)
    parts = {n: z_in.read(n) for n in z_in.namelist()}
    z_in.close()
    parts['designmap.xml'] = parts['designmap.xml'].replace(b'PageNumberStart="1"', f'PageNumberStart="{FIRST}"'.encode())
    for n in parts:
        if n.startswith('Spreads/'):
            for k in range(1, 5):
                parts[n] = parts[n].replace(f'Name="{k}" AppliedMaster'.encode(), f'Name="{FIRST + k - 1}" AppliedMaster'.encode())
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), parts.pop('mimetype'), compress_type=zipfile.ZIP_STORED)
        for n, b in parts.items():
            z.writestr(n, b, compress_type=zipfile.ZIP_DEFLATED)
    print(len(doc.stories), 'text frames ·', len(doc.links), 'links ·', len(doc.pstyles), 'paragraph styles')
    fonts = os.path.join(REPO, 'tools/p1_layout/fonts')
    for f in ('InstrumentSans-Bold.ttf', 'InstrumentSans-Regular.ttf', 'InstrumentSans-OFL.txt', 'IBMPlexMono-Regular.ttf', 'IBMPlexMono-OFL.txt'):
        shutil.copyfile(os.path.join(fonts, f), os.path.join(DIR, 'Document Fonts', f))
    shutil.copyfile(os.path.join(p2.OUT, 'part2_match.pdf'), os.path.join(DIR, NAME + '.pdf'))
    with zipfile.ZipFile(DIR + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
