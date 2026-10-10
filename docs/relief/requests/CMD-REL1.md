```ga
{"schema": "directive/2", "id": "CMD-REL1", "rev": 1, "to": "LOCAL", "from": "gentleMonster", "after": [],
 "goal": "Generate four photographic images (scenes A-D) from the prompts in cogito5170/gentleMonster@claude/hyeokju-cv docs/cv/photos/{A,B,C,D}.prompt.txt with an open-weight image model running on the VM, and push them with their sidecars to gentleMonster branch claude/relief-photos under docs/cv/photos/.",
 "why": "The CV hero (PHOTO 01) needs a real-looking person standing still in a motion-blurred crowd. The cloud sessions cannot make it: their network policy blocks huggingface.co and download.pytorch.org, and the Gemini key in the GEMINI_API_KEY environment has image quota 0 (HTTP 429 on gemini-2.5-flash-image and five gemini-3.x image models, 2026-10-10 01:39 UTC, session_017EVHBofkdPhvYSUBCeRAH4). The RELIEF engine (Blender) renders the set but not a photographic person.",
 "scope": [
  {"id": "S1", "text": "Probe the VM first: reach huggingface.co, free RAM, GPU, free disk. Pick FLUX.1-schnell (Apache-2.0) if RAM >= 24 GB, else Z-Image-Turbo (Apache-2.0), else SDXL-Turbo (research licence: note it in the report). Use diffusers on CPU (or GPU if present) in a fresh venv; do not touch running services."},
  {"id": "S2", "text": "One image per prompt file, 4:5 portrait (1024x1280, or 832x1040 if memory is short), the prompt text verbatim, a fixed seed per scene (A 11, B 22, C 33, D 44), the model's recommended steps and guidance."},
  {"id": "S3", "text": "Save <scene>.png and <scene>.json (model id and revision, seed, steps, guidance, size, seconds) in docs/cv/photos/. Look at each image; regenerate a failed scene once with seed+1. Do not retouch or composite."},
  {"id": "S4", "text": "Commit on a new branch claude/relief-photos from claude/hyeokju-cv and push it (no force, no PR, no other branch). photos/ is in .gitignore: add these files with git add -f. If VM policy does not allow pushing to cogito5170/gentleMonster, put the files in ga-mailbox to/session_01EwZvjiXu5ppJiaJniHRYoT/ instead and say so."},
  {"id": "S5", "text": "No paid model API. No keys or tokens in files, commits or the report. The people are generated, not a real individual; no face reference is supplied."}
 ],
 "done_when": [
  {"id": "D1", "text": "docs/cv/photos/A-D.png and A-D.json exist on claude/relief-photos (or the mailbox fallback), listed with the commit sha."},
  {"id": "D2", "text": "Each image: the centre person reads as a photograph (skin, fabric, hands intact), the crowd is motion blur, no text or watermark. State per scene pass/fail after viewing."},
  {"id": "D3", "text": "report/2 back to baseline with model, seconds per image, RAM/GPU seen, and the commit sha."}
 ],
 "budget": "VM CPU time <= 2 h; no model API cost.",
 "model": "gemini-3.7-flash-medium"}
```

## Request from gentleMonster (RELIEF) to baseline

This is a **draft directive for LOCAL**, proposed by the gentleMonster session (`session_01EwZvjiXu5ppJiaJniHRYoT`, user 정혁주).
The user asked (10-10 KST) to pass the image job to the VM through baseline. baseline decides whether to send it, renumbers it if
needed, and writes it to `ga-mailbox` `to/LOCAL/`.

- Prompts: written by `claude -p` from the RELIEF brief (`gentle_monster/relief/photo.py`, `BRIEF`), saved verbatim in
  `docs/cv/photos/*.prompt.txt`. Grammar: one person still and sharp at the centre, a crowd streaking past on a slow shutter,
  muted grey film palette, 4:5. The still person wears the applicant's SECTOR A style (black long coat, horn-rimmed glasses).
- What happens next on our side: RELIEF grades the photo to its six grey inks and mounts it in the CV hero window
  (`python -m gentle_monster.relief home`).
- Checked with `python3 ops/flow/mailcheck.py` from baseline `claude/gracious-meitner-vp49xe` before sending.
