"""TYPE 2 sidebar with a smaller photo: S 48 x 64, XS 36 x 48 (3:4). -> docs/cv/ai/CV_TYPE2_SIDEBAR_PHOTO_*.ai"""
import sys, subprocess
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pathlib import Path
import bp, cv_types
AI = Path(__file__).resolve().parent.parent / "ai"
for tag, size in (("S", (48, 64)), ("XS", (36, 48))):
    bp.OUT.clear()
    bp.w('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">')
    bp.w(f'<title>CV 1/2 · TYPE 2 SIDEBAR · photo {size[0]}x{size[1]} · JEONG HYEOKJU</title>')
    bp.theme(bp.DARK); cv_types.type2(size); bp.zone_end(); bp.w('</svg>')
    svg = AI / f"CV_TYPE2_SIDEBAR_PHOTO_{tag}.svg"; svg.write_text("\n".join(bp.OUT), encoding="utf-8")
    pdf = svg.with_suffix(".pdf")
    subprocess.run(["inkscape", str(svg), "--export-type=pdf", "--export-pdf-version=1.5", f"--export-filename={pdf}"], check=True, capture_output=True)
    pdf.replace(svg.with_suffix(".ai")); print(svg.with_suffix(".ai"))
