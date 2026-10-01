"""<Step 1> Spatial synopsis: a brief -> a job spec (story + layout + walkthrough stops), written by
Gemini (gentle_monster.llm; with no key we say we cannot run -- we do not substitute another model).

The model writes; code judges. Every draft goes through spec.check(). A failed draft goes back with
**facts about its own layout** ("the circulation passes 0.1 m inside candle2 (x 3.4-5.0 ...)"), never
with rule names, for at most `rounds` rounds. If it still fails we stop and say what is wrong -- a
layout that walks through a sculpture is not handed on to the PDF.
"""
from __future__ import annotations

import json
import re

from gentle_monster import spec


def _gemini(prompt: str) -> str:
    from gentle_monster import llm
    if not llm.key():
        raise RuntimeError("no Gemini key (GEMINI_API_KEY) -- the synopsis step cannot run here")
    return llm.ask(prompt)


def _example() -> str:
    ex = spec.examples().get("gm") or next(iter(spec.examples().values()))
    return json.dumps(ex, ensure_ascii=False, separators=(",", ":"))


def prompt(brief: str, brand: str = "") -> str:
    shapes = "\n".join(f"  {k}: {v}" for k, v in spec.SHAPES.items())
    return f"""You are the spatial design director of an experimental flagship store. Write ONE spatial synopsis
for the brief below and lay it out as a real, walkable room.

Brief: {brief}
Brand: {brand or "take it from the brief; if none is named use Gentle Monster"}

Write in English only. Return ONLY a JSON object with exactly the fields of the example at the end:
brand, title, subtitle, line (one sentence), synopsis (3-5 sentences, second person, concrete materials,
light, motion and what the visitor does), keywords (3), quote (the philosophy in one line), why (4 design
reasons {{t, d}} that tie a layout decision to the synopsis), palette (5 {{hex, name}}), materials
(4 {{name, where, preset}}), accent (#rrggbb), room, layout, stops.

Layout rules (metres; origin = street-side left corner; x to the right, y into the store; the door is on y = 0):
- layout: {{name, W, D, H, columns, items, flows, entry, exit}}; W and D 10-24 m, H 3.5-7 m.
- items: {{id, type, x0, y0, x1, y1, h, label, zone, shape, material}}; exactly one door item on y = 0.
  `type` is the plan symbol: {", ".join(sorted(spec.TYPES))}.
  `shape` is what gets built in 3D:
{shapes}
  `material` (and room.floor/wall/ceiling, materials[].preset): {", ".join(sorted(spec.MATERIALS))}.
  room: {{floor, wall, ceiling, light}}, light one of {", ".join(sorted(spec.LIGHTS))}; optional beams, fog, dome.
- Solid items must not overlap each other. Zones, shards, light_ceiling and floor_patch are not solid.
- flows[0].pts is the visitor's circulation from the door, 6-12 points. Every point of it must stay at least
  {spec.CLEAR} m from every solid item and from the outer walls. Make the hero object the centre of the walk.
- stops: exactly 3 moments of the synopsis on the circulation: {{at:[x,y] on the path, d seconds (2.4-3.6),
  look:[x, height, y] what the visitor looks at, h eye height 1.1-1.62, cap (first person, one line),
  sub (one line)}}. Total hold at most 11 s.

Example (a finished job; write a different space, do not copy it):
{_example()}
"""


def _parse(txt: str) -> dict:
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", (txt or "").strip())
    a, b = t.find("{"), t.rfind("}")
    if a < 0 or b <= a:
        raise ValueError("the reply contains no JSON object")
    return json.loads(t[a:b + 1])


def generate(brief: str, brand: str = "", ask=None, rounds: int = 3, log=None) -> dict:
    """Returns {'job': dict | None, 'problems': [...], 'rounds': n, 'drafts': [...]}. ask(prompt) -> text (default Gemini)."""
    ask = ask or _gemini
    p = prompt(brief, brand)
    drafts, problems = [], []
    for r in range(1, rounds + 1):
        txt = ask(p)
        try:
            job = _parse(txt)
        except (ValueError, json.JSONDecodeError) as e:
            problems = [f"your reply was not a parseable JSON object ({e})"]
            job = None
        else:
            problems = spec.check(job)
        drafts.append({"round": r, "problems": problems})
        if log:
            log(f"[synopsis] round {r}: {len(problems)} problem(s)")
        if job is not None and not problems:
            return {"job": job, "problems": [], "rounds": r, "drafts": drafts}
        prev = json.dumps(job, ensure_ascii=False, separators=(",", ":")) if job is not None else (txt or "")[:6000]
        p = (prompt(brief, brand) + "\n\nYour previous answer:\n" + prev +
             "\n\nThese things are true about that answer and must change:\n- " + "\n- ".join(problems) +
             "\n\nReturn the corrected full JSON object only.")
    return {"job": None, "problems": problems, "rounds": rounds, "drafts": drafts}
