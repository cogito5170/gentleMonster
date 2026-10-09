"""cv3d: the CV as pages laid out inside a 3D set (Blender Cycles), printed in a vintage six-ink dither
with sharp type on top.

    pip install bpy==5.1.2 fonttools pillow       # Blender as a Python module (Python 3.13)
    python -m gentle_monster.cv3d assets          # fonts, HDRIs, head scan -> $GM_CV3D_ASSETS (default ~/.cache/gm_cv3d)
    python -m gentle_monster.cv3d home            # CV 1/2, homepage card grid  -> out/cv3d/CV_HOME.pdf
    python -m gentle_monster.cv3d book            # SPA magazine, five sheets   -> out/cv3d/SPA_BOOK.pdf
    python -m gentle_monster.cv3d sheet object    # one sheet                   -> out/cv3d/object_final.png

--draft renders small and fast; --layout my.svg feeds the homepage another TYPE 1 layout.
Modules: engine (page <-> 3D projection, materials, props), pages (the sheets), objects (four-axis specs),
svgpage (flat layout reader), post (vintage print), drawings (plans hung in the sets).
"""
