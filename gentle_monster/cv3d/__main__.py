"""cv3d command line.

    python -m gentle_monster.cv3d assets                 fetch fonts, HDRIs and the head scan into $GM_CV3D_ASSETS
    python -m gentle_monster.cv3d list                   the sheets the engine knows
    python -m gentle_monster.cv3d sheet home             render + vintage print one sheet  -> out/home_final.png
    python -m gentle_monster.cv3d home --layout my.svg   the homepage CV from any TYPE 1 layout SVG -> out/CV_HOME.pdf
    python -m gentle_monster.cv3d book                   cover, plan, picture, object, experience -> out/SPA_BOOK.pdf

Options: --out DIR (default out/cv3d), --width PX (1240 = A4 at 150 dpi), --samples N (96), --draft (520 px, 24 samples).
Rendering needs Blender as a Python module: run with the interpreter that has `bpy` (pip install bpy==5.1.2, Python 3.13).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
BOOK = ["cover", "plan", "picture", "object", "experience"]

GF = "https://raw.githubusercontent.com/google/fonts/main/ofl"
THREE = "https://raw.githubusercontent.com/mrdoob/three.js/r170/examples"
FONTS = {
    "Archivo[wdth,wght].ttf": f"{GF}/archivo/Archivo%5Bwdth,wght%5D.ttf",
    "InstrumentSerif-Regular.ttf": f"{GF}/instrumentserif/InstrumentSerif-Regular.ttf",
    "InstrumentSerif-Italic.ttf": f"{GF}/instrumentserif/InstrumentSerif-Italic.ttf",
    "NotoSerifKR[wght].ttf": f"{GF}/notoserifkr/NotoSerifKR%5Bwght%5D.ttf",
    "NotoSansKR[wght].ttf": f"{GF}/notosanskr/NotoSansKR%5Bwght%5D.ttf",
}
INSTANCES = [  # (source, axes, file the pages ask for)
    ("Archivo[wdth,wght].ttf", {"wdth": 125, "wght": 250}, "ArchivoExp-Thin.ttf"),
    ("Archivo[wdth,wght].ttf", {"wdth": 125, "wght": 400}, "ArchivoExp-Reg.ttf"),
    ("Archivo[wdth,wght].ttf", {"wdth": 125, "wght": 600}, "ArchivoExp-Semi.ttf"),
    ("Archivo[wdth,wght].ttf", {"wdth": 100, "wght": 100}, "Archivo-Thin.ttf"),
    ("Archivo[wdth,wght].ttf", {"wdth": 100, "wght": 500}, "Archivo-Med.ttf"),
    ("Archivo[wdth,wght].ttf", {"wdth": 100, "wght": 600}, "Archivo-Semi.ttf"),
    ("Archivo[wdth,wght].ttf", {"wdth": 100, "wght": 700}, "Archivo-Bold.ttf"),
    ("NotoSerifKR[wght].ttf", {"wght": 400}, "NotoSerifKR-Reg.ttf"),
    ("NotoSerifKR[wght].ttf", {"wght": 700}, "NotoSerifKR-Bold.ttf"),
    ("NotoSansKR[wght].ttf", {"wght": 400}, "NotoSansKR-Reg.ttf"),
    ("NotoSansKR[wght].ttf", {"wght": 500}, "NotoSansKR-Med.ttf"),
    ("NotoSansKR[wght].ttf", {"wght": 700}, "NotoSansKR-Bold.ttf"),
]
HDRIS = ["royal_esplanade_1k.hdr", "venice_sunset_1k.hdr", "moonless_golf_1k.hdr", "blouberg_sunrise_2_1k.hdr"]
SCAN = ["LeePerrySmith.glb", "Map-COL.jpg", "Map-SPEC.jpg", "Infinite-Level_02_Tangent_SmoothUV.jpg"]  # CC BY 3.0, Lee Perry-Smith / Infinite-Realities


def assets_dir():
    return Path(os.environ.get("GM_CV3D_ASSETS", Path.home() / ".cache" / "gm_cv3d"))


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print("  get", dest.name)
    with urllib.request.urlopen(url, timeout=300) as r, open(dest, "wb") as f:
        f.write(r.read())


def cmd_assets(a):
    d = assets_dir(); print("assets ->", d)
    for name, url in FONTS.items():
        fetch(url, d / "fonts" / name)
    for h in HDRIS:
        fetch(f"{THREE}/textures/equirectangular/{h}", d / "hdri" / h)
    for f in SCAN:
        fetch(f"{THREE}/models/gltf/LeePerrySmith/{f}", d / f)
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for src, axes, out in INSTANCES:
        o = d / "fonts" / out
        if not o.exists():
            f = TTFont(d / "fonts" / src); instancer.instantiateVariableFont(f, axes, inplace=True, updateFontNames=False); f.save(o)
            print("  font", out)
    print("ok")


def _run(module, *args):
    env = dict(os.environ, GM_CV3D_ASSETS=str(assets_dir()))
    subprocess.run([sys.executable, "-m", f"gentle_monster.cv3d.{module}", *map(str, args)], check=True, env=env)


def sheet(name, out, width, samples):
    if name == "plan":
        _run("drawings", out)
    _run("render", name, out, width, samples)
    _run("post", name, out)
    return out / f"{name}_final.png"


def pdf(pngs, path, title):
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in pngs]
    ims[0].save(path, save_all=True, append_images=ims[1:], resolution=150 * ims[0].width / 1240, quality=92, title=title)
    print("pdf", path)


def main():
    ap = argparse.ArgumentParser(prog="python -m gentle_monster.cv3d", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["assets", "list", "sheet", "home", "book"])
    ap.add_argument("name", nargs="?")
    ap.add_argument("--out", default="out/cv3d"); ap.add_argument("--width", type=int, default=1240); ap.add_argument("--samples", type=int, default=96)
    ap.add_argument("--draft", action="store_true"); ap.add_argument("--layout")
    a = ap.parse_args()
    out = Path(a.out); w, s = (520, 24) if a.draft else (a.width, a.samples)
    if a.cmd == "assets":
        return cmd_assets(a)
    if a.cmd == "list":
        from gentle_monster.cv3d.pages import PAGES
        print("\n".join(PAGES)); return
    if a.layout:
        os.environ["GM_CV3D_LAYOUT"] = str(Path(a.layout).resolve())
    out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "sheet":
        print(sheet(a.name, out, w, s))
    elif a.cmd == "home":
        pdf([sheet("home", out, w, s)], out / "CV_HOME.pdf", "CV — Jeong Hyeokju")
    elif a.cmd == "book":
        pdf([sheet(n, out, w, s) for n in BOOK], out / "SPA_BOOK.pdf", "SPA — Jeong Hyeokju")


if __name__ == "__main__":
    main()
