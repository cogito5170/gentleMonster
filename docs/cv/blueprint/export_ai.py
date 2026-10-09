"""Export single types as A4 (210 x 297 mm) artboards for Illustrator.

    python3 docs/cv/blueprint/export_ai.py 1 2      # -> docs/cv/ai/CV_TYPE1_CARD_GRID.ai / .svg ...

.ai is PDF-compatible (what Illustrator itself writes since CS): Inkscape exports a PDF 1.5 with live
text and embedded font subsets, saved under the .ai name. The .svg keeps the zone groups by id
(T1_03_HERO ...), which Illustrator shows as group names. Fonts: Inter, Noto Sans KR (both free).
"""
import shutil
import subprocess
import sys
from pathlib import Path

import bp
from cv_types import TYPES

OUT_DIR = Path(__file__).resolve().parent.parent / "ai"


def export(n):
    spec = TYPES[n - 1]
    stem = f"CV_TYPE{n}_{spec['en'].replace(' ', '_')}"
    bp.OUT.clear()
    bp.w('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">')
    bp.w(f'<title>CV 1/2 · TYPE {n} {spec["en"]} · JEONG HYEOKJU</title>')
    bp.w('<defs><pattern id="hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<rect width="1.2" height="1.2" fill="#262626"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#8E8B86" stroke-width="0.4"/></pattern></defs>')
    bp.theme(spec["th"])
    spec["fn"]()
    bp.zone_end()
    bp.w('</svg>')
    OUT_DIR.mkdir(exist_ok=True)
    svg, pdf, ai = OUT_DIR / f"{stem}.svg", OUT_DIR / f"{stem}.pdf", OUT_DIR / f"{stem}.ai"
    svg.write_text("\n".join(bp.OUT), encoding="utf-8")
    subprocess.run(["inkscape", str(svg), "--export-type=pdf", "--export-pdf-version=1.5", f"--export-filename={pdf}"],
                   check=True, capture_output=True)
    shutil.move(pdf, ai)
    print(ai); print(svg)


if __name__ == "__main__":
    for a in sys.argv[1:] or ["1", "2"]:
        export(int(a))
