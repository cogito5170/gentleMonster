"""Gentle Monster editorial system: research catalogue -> Drift -> design hypotheses -> editorial plan
-> assets (rights-gated) -> HTML + PDF -> QA.

    python3 -m gentle_monster magazine "<brief in any words>"

Modules
    catalogue   research sources + claims (evidence, kind, verification), comparison matrix, coverage
    drift       the SE_NEW DRIFT rules carried over from prose to editorial concepts (see research/drift/)
    planner     brief -> >= 3 directions -> one chosen -> page-by-page plan
    assets      asset catalogue; only cleared assets are published, the rest stay research references
    plates      generated (own) SVG plates -- labelled as generated, never as photographs
    design      tokens, type scale, grid, page types -> CSS (screen and print kept apart)
    render      HTML magazine; pdf: Chromium print; qa: research / creative / production checks
"""
