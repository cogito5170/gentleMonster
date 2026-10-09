"""cv3d: the CV as a magazine whose 2D pages are laid out inside a 3D set (Blender Cycles), then printed in a
vintage six-ink dither with sharp type on top.

    pip install bpy==5.1.2            # Blender as a Python module (Python 3.13)
    export GM_CV3D_ASSETS=<dir>       # fonts/, hdri/, LeePerrySmith.glb + its maps (three.js examples, CC BY 3.0)
    python -m gentle_monster.cv3d.drawings out/
    python -m gentle_monster.cv3d.render photo_puddle out/   (photo_sprout, photo_bulb first: the picture sheet uses them)
    python -m gentle_monster.cv3d.render cover out/          (plan, picture, object, experience)
    python -m gentle_monster.cv3d.post cover out/            -> out/cover_final.png

Assets are not committed (size and licences); see engine.py for what each file is.
"""
