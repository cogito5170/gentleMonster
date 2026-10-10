"""RELIEF photo: photographs of real-looking people, made by Gemini's image model from written prompts.

The grammar comes from the motion references: a crowd streaks past on a slow shutter, one person stands still
and sharp in the middle. It is the CV's question made visible: Where did you last stop?

    python -m gentle_monster.relief photo all              # four scenes -> out/relief/photos/<scene>.png
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
    return f"{SCENES[scene]} The still person is {SUBJECT}. {CAMERA}"


def generate(scene: str, out: Path, face: Path | None = None, model: str = "", timeout: float = 180) -> Path:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set: add it to the environment, then run again.")
    parts = [{"text": prompt(scene) + (" Keep the exact face and identity of the person in the attached photograph." if face else "")}]
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
    if "--print" in argv:
        for s in scenes:
            print(f"[{s}] {prompt(s)}\n")
        return
    for s in scenes:
        print(generate(s, out / f"{s}.png", face))


if __name__ == "__main__":
    main(sys.argv[1:])
