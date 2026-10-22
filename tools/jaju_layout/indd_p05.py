"""JAJU 포트폴리오 5쪽(Where people stop?, B19 · 315 × 195) — InDesign 파일.

  python3 tools/jaju_layout/indd_p05.py

  docs/jaju_rounding_vmd/indesign/p05_where_people_stop/   (+ .zip)
    p05_where_people_stop.idml   한 쪽 문서 (쪽 번호 5)
    p05_where_people_stop.pdf    기준 시안 — plan_b19.pdf 의 5쪽
    Links/ · Document Fonts/
순서: plan_b19.py 로 HTML → html2idml_extract.mjs → html2idml.py (5쪽만).
"""
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '../..'))
NAME = 'p05_where_people_stop'
DIR = os.path.join(REPO, 'docs/jaju_rounding_vmd/indesign', NAME)


def main():
    import plan_b19
    import html2idml
    plan_b19.main()
    html = os.path.join(plan_b19.TMP, 'plan_b19.html')
    items = os.path.join(plan_b19.TMP, 'plan_b19_items.json')
    subprocess.run(['node', os.path.join(HERE, 'html2idml_extract.mjs'), html, items], check=True)
    if os.path.isdir(DIR):
        shutil.rmtree(DIR)
    os.makedirs(os.path.join(DIR, 'Document Fonts'))
    d = html2idml.build(items, os.path.join(DIR, NAME + '.idml'), 5, 5, plan_b19.b18.W, plan_b19.b18.H)
    print(len(d.stories), 'text frames ·', len(d.links), 'links ·', len(d.pstyles), 'paragraph styles')
    fonts = os.path.join(REPO, 'tools/p1_layout/fonts')
    for f in ('YoungSerif-Regular.ttf', 'YoungSerif-OFL.txt', 'Lora-Regular.ttf', 'Lora-Italic.ttf', 'Lora-Bold.ttf', 'Lora-OFL.txt',
              'IBMPlexMono-Regular.ttf', 'IBMPlexMono-OFL.txt'):
        shutil.copyfile(os.path.join(fonts, f), os.path.join(DIR, 'Document Fonts', f))
    subprocess.run(['pdfseparate', '-f', '5', '-l', '5', os.path.join(plan_b19.OUT, 'plan_b19.pdf'), os.path.join(DIR, NAME + '.pdf')], check=True)
    with zipfile.ZipFile(DIR + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
