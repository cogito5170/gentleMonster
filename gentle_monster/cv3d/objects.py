"""Installation grammar: every object is specified on four axes before it is modelled.

  1 FORM        geometry (sphere, cylinder, cone, polyhedron) or organic (root, cell, coral, bone, liquid),
                deformation (stretch, compress, twist, crush), silhouette (pointed, round, asymmetric, fragmented)
  2 CURVATURE   gentle <-> sharp, surface type (plane, cylinder, sphere, free-form), curvature change
                (constant <-> tightening / opening), continuity (smooth <-> creased)
  3 MATERIAL    name plus the measured properties: roughness, gloss, transparency, density, weight, flexibility
                (0 = none, 1 = full; weight is visual weight)
  4 COMPOSITION aggregate, cluster, repetition, proliferation, radial, vertical / horizontal, asymmetric balance

REFERENCES records the Gentle Monster installations from the [A to Z] article on the same four axes; OBJECTS
records the five objects of the CV. The object sheet prints the OBJECTS table; pages.py builds each object
from its entry (deformations, counts and growth factors are read from here, not hard-coded twice).
"""

REFERENCES = {
    "haus_dosan_pods": dict(
        form=dict(type="polyhedron", deform=["stretch"], silhouette=["pointed", "asymmetric"]),
        curvature=dict(gentle_sharp="sharp", surface="plane facets", change="tightening to the tip", continuity="creased (folded)"),
        material=dict(name="black woven metal mesh", roughness=0.45, gloss=0.3, transparency=0.05, density=0.8, weight=0.9, flexibility=0.1),
        composition=["cluster", "vertical", "asymmetric balance", "orthogonal steel truss as counter-frame"],
    ),
    "coral_cluster": dict(
        form=dict(type="organic: cell, coral", deform=["compress"], silhouette=["round", "fragmented"]),
        curvature=dict(gentle_sharp="gentle", surface="sphere", change="constant per body, many radii", continuity="smooth body, creased joints"),
        material=dict(name="plaster / foam, porous", roughness=0.85, gloss=0.05, transparency=0.0, density=0.4, weight=0.5, flexibility=0.0),
        composition=["aggregate", "repetition", "proliferation (size gradient)"],
    ),
    "roots_on_stilts": dict(
        form=dict(type="organic: root, mushroom", deform=["stretch"], silhouette=["pointed", "asymmetric"]),
        curvature=dict(gentle_sharp="gentle", surface="tapering cylinders", change="tightening toward the tips", continuity="branching joints"),
        material=dict(name="driftwood, fungus foam, black gravel", roughness=0.9, gloss=0.05, transparency=0.0, density=0.6, weight=0.4, flexibility=0.2),
        composition=["cluster of three", "radial from the base", "vertical", "size variation"],
    ),
    "cast_tray": dict(
        form=dict(type="organic: liquid", deform=["compress"], silhouette=["round"]),
        curvature=dict(gentle_sharp="gentle", surface="free-form", change="opening outward", continuity="smooth (G2)"),
        material=dict(name="cast aluminium, satin", roughness=0.35, gloss=0.5, transparency=0.0, density=0.9, weight=0.7, flexibility=0.0),
        composition=["beaded rim: repetition", "contents in a row: horizontal"],
    ),
}

OBJECTS = {
    "probe": dict(
        title="The Probe", where="cover",
        form=dict(type="polyhedron", deform=["stretch", "twist"], silhouette=["pointed", "asymmetric"]),
        curvature=dict(gentle_sharp="sharp", surface="plane facets", change="tightening to the tip", continuity="creased"),
        material=dict(name="black woven mesh / chrome truss / graphite arm", roughness=0.42, gloss=0.35, transparency=0.0, density=0.8, weight=0.9, flexibility=0.1),
        composition=["cluster of 3", "vertical", "asymmetric balance", "arm presents one frame"],
        params=dict(pods=[(-0.48, 0.12, 1.35, 0.30), (0.0, -0.05, 1.55, 0.34), (0.46, 0.15, 1.25, 0.28)], twist=0.25),
    ),
    "titan": dict(
        title="The Synthetic Titan", where="object",
        form=dict(type="polyhedron from a head scan", deform=["stretch", "twist"], silhouette=["pointed", "fragmented"]),
        curvature=dict(gentle_sharp="sharp", surface="plane facets", change="twisting upward", continuity="creased"),
        material=dict(name="black mesh facets / acrylic lens shards / chrome cage", roughness=0.4, gloss=0.4, transparency=0.35, density=0.7, weight=0.8, flexibility=0.0),
        composition=["one body", "proliferation of shards around it", "vertical"],
        params=dict(stretch=0.9, twist_deg=38, facets=0.012, shards=14),
    ),
    "scent": dict(
        title="Residue of Scent", where="object",
        form=dict(type="organic: cell, coral", deform=["compress"], silhouette=["round", "fragmented"]),
        curvature=dict(gentle_sharp="gentle", surface="sphere + bumps", change="constant per cell", continuity="smooth body, creased joints"),
        material=dict(name="bone-white porous plaster / red wax, liquid", roughness=0.82, gloss=0.08, transparency=0.0, density=0.4, weight=0.5, flexibility=0.0),
        composition=["aggregate", "repetition", "proliferation (radius x0.78 per step)"],
        params=dict(cells=11, growth=0.78, r0=0.09, bumps=0.012),
    ),
    "monolith": dict(
        title="Monolithic Fusion", where="object",
        form=dict(type="sphere", deform=["crush"], silhouette=["round"]),
        curvature=dict(gentle_sharp="gentle", surface="sphere, broken by grain", change="constant", continuity="rough"),
        material=dict(name="granite / stainless slats / black cables", roughness=0.85, gloss=0.1, transparency=0.0, density=1.0, weight=1.0, flexibility=0.0),
        composition=["one body on a repeated ramp", "vertical cables: repetition", "horizontal slats"],
        params=dict(slats=7, cables=5),
    ),
    "apothecary": dict(
        title="The Stratified Apothecary", where="object",
        form=dict(type="cylinder strata over a liquid basin", deform=["compress"], silhouette=["round"]),
        curvature=dict(gentle_sharp="gentle", surface="cylinder strata / free-form basin", change="opening outward", continuity="smooth basin, stepped strata"),
        material=dict(name="red clay, matte / cast aluminium, satin / water", roughness=0.6, gloss=0.4, transparency=0.1, density=0.8, weight=0.7, flexibility=0.0),
        composition=["vertical stack: repetition", "beaded rim: repetition", "three stilts"],
        params=dict(layers=8, beads=36),
    ),
}


def spec_lines(key):
    """Four short lines for the sheet, in the architect's shorthand."""
    o = OBJECTS[key]; f, c, m = o["form"], o["curvature"], o["material"]
    return [
        f"FORM  {f['type']} · {' + '.join(f['deform'])} · {' / '.join(f['silhouette'])}",
        f"CURV  {c['gentle_sharp']} · {c['surface']} · {c['continuity']}",
        f"MAT   R{m['roughness']:.1f} G{m['gloss']:.1f} T{m['transparency']:.1f} D{m['density']:.1f} W{m['weight']:.1f} F{m['flexibility']:.1f}",
        f"COMP  {' · '.join(o['composition'][:2])}",
    ]
