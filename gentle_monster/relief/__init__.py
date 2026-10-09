"""RELIEF 0.1 — a page engine: a flat A4 layout raised into a 3D set, rendered in Blender Cycles and printed in a
vintage six-ink dither with sharp type on top. Every element keeps its page position at any depth:
printed on the wall (2D), mounted off it (2.5D), standing in the room (3D) — a relief.

Handle for other sessions: RELIEF, package gentle_monster/relief, repo cogito5170/gentleMonster, branch claude/hyeokju-cv.
Input: a layout SVG in page millimetres (group ids like T1_03_HERO) or a sheet function in pages.py.
Output: <sheet>_final.png per sheet, one PDF per job.

    pip install bpy==5.1.2 fonttools pillow       # Blender as a Python module (Python 3.13)
    python -m gentle_monster.relief assets          # fonts, HDRIs, head scan -> $RELIEF_ASSETS (default ~/.cache/gm_relief)
    python -m gentle_monster.relief home            # CV 1/2, homepage card grid  -> out/relief/CV_HOME.pdf
    python -m gentle_monster.relief book            # SPA magazine, five sheets   -> out/relief/SPA_BOOK.pdf
    python -m gentle_monster.relief sheet object    # one sheet                   -> out/relief/object_final.png

--draft renders small and fast; --layout my.svg feeds the homepage another TYPE 1 layout.
Modules: engine (page <-> 3D projection, materials, props), pages (the sheets), objects (four-axis specs),
svgpage (flat layout reader), post (vintage print), drawings (plans hung in the sets).
"""
