"""Render one sheet: python -m gentle_monster.relief.render <page> <out_dir> [width samples]

Writes <out_dir>/<page>.png (the 3D set), any extra exposures, and <out_dir>/<page>.json
(type runs, drawing lines and exposure boxes for post.py).
"""
import json
import sys
from pathlib import Path

from gentle_monster.relief import pages

name, out = sys.argv[1], Path(sys.argv[2])
w = int(sys.argv[3]) if len(sys.argv) > 3 else 1240
samples = int(sys.argv[4]) if len(sys.argv) > 4 else 96
out.mkdir(parents=True, exist_ok=True)
res = (w, round(w * 297 / 210))
if name.startswith("photo_"):
    res = (round(w * 0.65), round(w * 0.8125))
pg, spec = pages.build(name, res=res, samples=samples, out_dir=out)
pg.render(out / f"{name}.png")
for e in spec.get("exposures", []):
    sh = e.pop("shot", None)
    if sh:
        f = out / e["src"]
        pg.shot(f, sh["loc"], sh["target"], sh.get("lens", 50), tuple(sh.get("res", (900, 700))) if w >= 1000 else (450, 350), sh.get("samples"))
(out / f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok", out / f"{name}.png")
