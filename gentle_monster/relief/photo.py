"""RELIEF photo: photographs of real-looking people, made by Gemini's image model from written prompts.

Each prompt is written by Claude Code in print mode (`claude -p`) from a brief; the image comes from Gemini.
The grammar comes from the motion references: a crowd streaks past on a slow shutter, one person stands still
and sharp in the middle. It is the CV's question made visible: Where did you last stop?

    python -m gentle_monster.relief photo all              # four scenes -> out/relief/photos/<scene>.png (+ .prompt.txt)
    python -m gentle_monster.relief photo all --print      # only write the prompts (claude -p), no image call
    python -m gentle_monster.relief photo A --fixed        # skip claude -p, use the fixed prompt
    python -m gentle_monster.relief photo C --face me.jpg  # keep the face of a reference photo (the applicant's own)

Key: GEMINI_API_KEY (or GOOGLE_API_KEY). Model: GEMINI_IMAGE_MODEL, default gemini-2.5-flash-image.
The people in the output are generated, not the applicant, unless --face gives his photograph.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# the still person: the applicant's own SECTOR A style (docs/portfolio/01_style.md), not his likeness
SUBJECT = (
    "a Korean man in his mid twenties, short neat black hair with natural texture, black horn-rimmed glasses, "
    "an oversized black wool long coat over a grey knit, wide grey trousers, grey New Balance sneakers, a small vintage steel watch, "
    "standing completely still, calm neutral expression, looking straight into the lens"
)
CAMERA = (
    "Real photograph, not an illustration, not CGI, not a painting. Shot on 35mm film, 50mm lens, slow shutter around 1/4 second on a tripod: "
    "the still man is tack sharp, every moving person is a long-exposure motion blur streak. Natural skin texture with visible pores, "
    "real wool and cotton texture, accurate hands, true human proportions. Muted, faded, nearly monochrome grey palette with fine film grain, "
    "soft diffuse light. Vertical 4:5 frame. No text, no logo, no watermark."
)
SCENES = {
    "A": "A pale seamless white studio like a gallery. The man sits upright on a plain white plinth in the exact centre, knees apart, hands loosely joined. "
         "Around him six people walk past fast in long coats, blurred into ghost streaks; two of them wear deep red, the rest ivory and grey.",
    "B": "A vast pale grey exhibition hall with a concrete floor. The man stands in the middle in profile-three-quarter view while a dense crowd in black and charcoal coats "
         "sweeps around him in every direction, smeared by motion. Seen slightly from above.",
    "C": "A wide city crosswalk at dusk after rain, seen from a high angle. Wet asphalt, white zebra stripes, the faint red glow of a traffic light reflected in a puddle. "
         "The man stands still on the stripes holding nothing, while commuters rush across in blurred streaks of black, grey and beige.",
    "D": "A close, crowded street, telephoto 85mm. The man stands still in the centre, framed from the chest up, sharp; the people in front of and behind him pass as "
         "soft warm-grey motion blur, overlapping his edges.",
}


def prompt(scene: str) -> str:
    """The fixed prompt (fallback when `claude -p` is not available)."""
    return f"{SCENES[scene]} The still person is {SUBJECT}. {CAMERA}"


BRIEF = """You write prompts for a photographic image model. Write ONE prompt, in English, 120-170 words, plain prose,
no headings, no quotes, no lists, nothing before or after it.

What the image must be: a real photograph of real people, never an illustration, 3D render or painting.
Grammar (from four fashion-editorial references): a crowd moves past on a slow shutter and blurs into streaks;
exactly one person stands still, tack sharp, in the middle of the frame, looking into the lens. Muted, faded,
near-monochrome grey palette, fine film grain, soft diffuse light, vertical 4:5. Skin pores, fabric weave and
hands must read as real. No text, logos or watermarks.

The still person (a generated model wearing the applicant's own style, not a portrait of a real individual):
a Korean man in his mid twenties, short neat textured black hair, black horn-rimmed glasses, oversized black
wool long coat over a grey knit, wide grey trousers, grey New Balance sneakers, small vintage steel watch.

Scene: {scene}
Camera to state: 35mm film, lens and shutter you choose to fit the scene, tripod, eye level unless the scene says otherwise.
"""


def write_prompt(scene: str, timeout: float = 240) -> str:
    """Ask Claude Code in print mode (`claude -p`) to write the image prompt; fall back to the fixed one."""
    import shutil
    import subprocess
    if not shutil.which("claude"):
        return prompt(scene)
    try:
        r = subprocess.run(["claude", "-p", BRIEF.format(scene=SCENES[scene]), "--output-format", "text"],
                           capture_output=True, text=True, timeout=timeout)
        text = r.stdout.strip()
        return text if r.returncode == 0 and 60 < len(text.split()) < 260 else prompt(scene)
    except (subprocess.TimeoutExpired, OSError):
        return prompt(scene)


def generate(scene: str, out: Path, face: Path | None = None, model: str = "", timeout: float = 180, text: str | None = None) -> Path:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set: add it to the environment, then run again.")
    parts = [{"text": (text or prompt(scene)) + (" Keep the exact face and identity of the person in the attached photograph." if face else "")}]
    if face:
        mime = "image/png" if face.suffix.lower() == ".png" else "image/jpeg"
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(face.read_bytes()).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "4:5"}}}
    url = API.format(model=model or os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image"))
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        res = json.loads(r.read())
    for c in res.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            data = p.get("inline_data") or p.get("inlineData")
            if data:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(base64.b64decode(data["data"]))
                return out
    raise RuntimeError("no image in the response: " + json.dumps(res)[:400])


def main(argv):
    scenes = list(SCENES) if not argv or argv[0] == "all" else [argv[0]]
    face = Path(argv[argv.index("--face") + 1]) if "--face" in argv else None
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else Path("out/relief/photos")
    out.mkdir(parents=True, exist_ok=True)
    for s in scenes:
        text = prompt(s) if "--fixed" in argv else write_prompt(s)      # written by `claude -p` unless --fixed
        (out / f"{s}.prompt.txt").write_text(text + "\n", encoding="utf-8")
        print(f"[{s}] {text}\n")
        if "--print" not in argv:
            print(generate(s, out / f"{s}.png", face, text=text))


if __name__ == "__main__":
    main(sys.argv[1:])
