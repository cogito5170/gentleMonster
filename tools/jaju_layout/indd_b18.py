"""JAJU 포트폴리오 B18(315 × 195) 5–18쪽 — InDesign 파일 한 벌.

  python3 tools/jaju_layout/indd_b18.py

  docs/jaju_rounding_vmd/indesign/p05-18_315x195/   (+ .zip)
    p05-18_315x195.idml   14쪽 문서 (쪽 번호 5 부터)
    plan_b18_reference.pdf 기준 시안 — plan_b18.pdf 18쪽 전체 (5–18쪽을 볼 것)
    Links/                사진 · 잘라 낸 사진 (보정판)
    Document Fonts/       Young Serif · Lora · IBM Plex Mono · Instrument Sans (OFL). Pretendard · 210 타임라인 은 사용자 컴퓨터의 것

순서: plan_b18.py 로 HTML → html2idml_extract.mjs 로 쪽마다 그려진 것(mm) → html2idml.py 로 IDML.
"""
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '../..'))
NAME = 'p05-18_315x195'
DIR = os.path.join(REPO, 'docs/jaju_rounding_vmd/indesign', NAME)
FIRST, LAST = 5, 18


def main():
    import plan_b18
    import html2idml
    plan_b18.main()
    html = os.path.join(plan_b18.TMP, 'plan_b18.html')
    items = os.path.join(plan_b18.TMP, 'plan_b18_items.json')
    subprocess.run(['node', os.path.join(HERE, 'html2idml_extract.mjs'), html, items], check=True)
    if os.path.isdir(DIR):
        shutil.rmtree(DIR)
    os.makedirs(os.path.join(DIR, 'Document Fonts'))
    d = html2idml.build(items, os.path.join(DIR, NAME + '.idml'), FIRST, LAST, plan_b18.W, plan_b18.H)
    print(len(d.stories), 'text frames ·', len(d.links), 'links ·', len(d.pstyles), 'paragraph styles')
    fonts = os.path.join(REPO, 'tools/p1_layout/fonts')
    for f in ('YoungSerif-Regular.ttf', 'YoungSerif-OFL.txt', 'Lora-Regular.ttf', 'Lora-Italic.ttf', 'Lora-Bold.ttf', 'Lora-OFL.txt',
              'IBMPlexMono-Regular.ttf', 'IBMPlexMono-Bold.ttf', 'IBMPlexMono-OFL.txt', 'InstrumentSans-Regular.ttf', 'InstrumentSans-OFL.txt'):
        shutil.copyfile(os.path.join(fonts, f), os.path.join(DIR, 'Document Fonts', f))
    # 기준 시안: 18쪽 전체(쪽을 떼어 다시 묶으면 사진이 쪽마다 중복돼 커진다)
    shutil.copyfile(os.path.join(plan_b18.OUT, 'plan_b18.pdf'), os.path.join(DIR, 'plan_b18_reference.pdf'))
    with zipfile.ZipFile(DIR + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DIR):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, os.path.dirname(DIR)))
    print('wrote', DIR)


if __name__ == '__main__':
    main()
