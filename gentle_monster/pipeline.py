"""gentle_monster pipeline.

    <synopsis>  ->  <layout PDF + moodboard PDF>   default: every request gets these
                ->  <blueprint PDF + MP4>   only when the user asks for it
                ->  <site>                  on request: the frontend engine (engine/) -- a web page of the room,
                                            judged in a browser and evolved under the se_new policy

A job lives in one folder (paths.OUT/<name>/): job.json is the single source every step reads,
so the blueprint and the video always show the room the layout PDF described.
Every produced file is printed as `산출물: <path relative to the repo>` -- a host bot can attach those
to its reply.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from gentle_monster import paths, spec


def _rel(p) -> str:
    try:
        return str(Path(p).resolve().relative_to(paths.REPO))
    except ValueError:
        return str(p)


def _out(p, log=print) -> str:
    log("산출물: " + _rel(p))
    return str(p)


def job_path(name: str) -> Path:
    return paths.job_dir(name) / "job.json"


def load_job(name: str) -> dict:
    p = job_path(name)
    if not p.is_file():
        raise FileNotFoundError(f"no job named {name!r} -- run the synopsis step first (python3 -m gentle_monster make ...)")
    return spec.load(p)


def save_job(name: str, job: dict) -> Path:
    p = job_path(name)
    p.write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
    md = [f"# {job['brand']} — {job['title']}", f"*{job.get('subtitle', '')}*", "", job["synopsis"], "",
          "**Keywords:** " + " · ".join(job["keywords"]), f"**Philosophy:** {job['quote']}", "", "## Design intent"]
    md += [f"- **{w['t']}** {w['d']}" for w in job["why"]] + ["", "## The walk"] + [f"- **{s['cap']}** {s['sub']}" for s in job["stops"]]
    (p.parent / "synopsis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return p


def synopsis(name: str, brief: str = "", brand: str = "", example: str = "", ask=None, log=print) -> dict:
    """Step 1. `example` uses a bundled, already-checked synopsis (no model call)."""
    if example:
        ex = spec.examples()
        if example not in ex:
            raise KeyError(f"no bundled example {example!r}; have: {', '.join(ex)}")
        job = ex[example]
    else:
        from gentle_monster import synopsis as SY
        r = SY.generate(brief, brand=brand, ask=ask, log=log)
        if not r["job"]:
            raise RuntimeError("the synopsis did not pass the layout check after %d rounds:\n- " % r["rounds"] + "\n- ".join(r["problems"][:12]))
        job = r["job"]
    p = save_job(name, job)
    _out(p.parent / "synopsis.md", log)
    d, where, _ = spec.clearance(job["layout"])
    log(f"[synopsis] {job['brand']} — {job['title']} · {job['layout']['W']} x {job['layout']['D']} m · path clearance {d:.2f} m (nearest: {where})")
    return job


def _keep(name: str, files, sub: str, log=print) -> "list[str]":
    """Copy the user's images into the job folder, so a later rebuild (or the blueprint step) still has them."""
    import shutil
    d = paths.job_dir(name) / sub
    kept, missing = [], []
    for f in files or ():
        f = Path(f)
        if not f.is_file():
            missing.append(str(f)); continue
        d.mkdir(parents=True, exist_ok=True)
        t = d / f.name
        if f.resolve() != t.resolve():
            shutil.copy2(f, t)
        kept.append(str(t))
    if missing:
        log(f"[{sub}] not found, left out: " + ", ".join(missing))
    return kept


def _kept(name: str, sub: str) -> "list[str]":
    d = paths.job_dir(name) / sub
    return sorted(str(p) for p in d.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")) if d.is_dir() else []


MOOD_VIEWS = ("eye", "cut", "stop0", "stop2")


def layout(name: str, photos=(), refs=(), images=(), text: str = "", moodboard: bool = True, use_llm: bool = True, log=print) -> dict:
    """Step 2 (default). One A3 layout page + the magazine moodboard (multi-spread A3).

    images: unsorted attachments -- photos.split() measures which are reference layouts.
    With fewer than 3 photos the moodboard is filled with photoreal renders of the job (labelled generated)."""
    from gentle_monster import documents
    job = load_job(name)
    if images:
        from gentle_monster import photos as PH
        ph, rf = PH.split(images, text)
        photos, refs = list(photos) + ph, list(refs) + rf
        log(f"[images] {len(ph)} photo(s), {len(rf)} reference layout(s) (measured flat-block share >= {PH.REF_THRESHOLD})")
    photos = _keep(name, photos, "photos", log) or _kept(name, "photos")
    refs = _keep(name, refs, "refs", log) or _kept(name, "refs")
    d = paths.job_dir(name)
    r = documents.layout_pdf(job, d, photos=photos)
    _out(r["pdf"], log); _out(r["preview"], log)
    if not moodboard:
        return r
    from gentle_monster import moodboard as MB
    renders = []
    if len(photos) < 3:
        have = {v: d / f"render_{v}.png" for v in MOOD_VIEWS}
        if not all(p.is_file() for p in have.values()):
            from gentle_monster import render
            t = time.time()
            render.stills(job, d, views=[v for v, p in have.items() if not p.is_file()], w=1400, h=900)
            log(f"[moodboard] {len(photos)} photo(s) -> photoreal renders of the room fill the rest ({time.time() - t:.0f} s)")
        renders = [str(p) for p in have.values()]
    m = MB.build(job, d, photos, refs, renders=renders, plan=r["plan"], use_llm=use_llm)
    log(f"[moodboard] {len(m['spreads'])} spreads · {m['style']['source']} · generated fills {m['generated_fills']} · detail crops {m['detail_crops']}")
    _out(m["pdf"], log)
    return dict(r, moodboard=m["pdf"], moodboard_info=m)


def blueprint(name: str, log=print) -> dict:
    """Step 3a (on request). Photoreal stills + A3 drawing sheet."""
    from gentle_monster import documents, render
    job = load_job(name)
    t = time.time()
    rs = render.stills(job, paths.job_dir(name))
    r = documents.blueprint_pdf(job, paths.job_dir(name), rs)
    for f in (r["pdf"], rs["eye"], rs["cut"]):
        _out(f, log)
    log(f"[blueprint] {time.time() - t:.0f} s")
    return dict(r, renders=rs)


def video(name: str, workers: int = 0, crf: int = 26, log=print) -> str:
    """Step 3b (on request). 30 s first-person walkthrough along the drawn circulation. Tens of minutes."""
    from gentle_monster import render
    job = load_job(name)
    t = time.time()
    safe = "".join(c if c.isalnum() else "_" for c in f"{job['brand']}_{job['title']}")[:60]
    mp4 = render.video(job_path(name), paths.job_dir(name) / f"{safe}.mp4", workers=workers, crf=crf)
    _out(mp4, log)
    log(f"[video] 30 s · 1280x720 · 24 fps · {Path(mp4).stat().st_size / 1e6:.1f} MB · {time.time() - t:.0f} s")
    return mp4


def site(name: str, rounds: int = 6, log=print) -> dict:
    """On request. The job as a web page: tokens -> page -> browser judge -> se_new policy, `rounds` operators tried."""
    from gentle_monster import engine
    job = load_job(name)
    t = time.time()
    r = engine.build(job, paths.job_dir(name) / "site", rounds=rounds, log=log)
    for f in (r["html"], r["tokens"], r["report"]):
        _out(f, log)
    bad = [k for k, ok in r["V"].items() if not ok]
    log(f"[site] {r['accepted']} accepted · {r['rejected']} rejected · J {r['score']:.4f} · "
        + ("every invariant holds" if not bad else "DOES NOT SHIP -- invariant failed: " + ", ".join(bad)) + f" · {time.time() - t:.0f} s")
    return r


def status(name: str) -> dict:
    d = paths.job_dir(name)
    return {k: (d / f).is_file() for k, f in (("synopsis", "job.json"), ("layout", "layout.pdf"), ("moodboard", "moodboard.pdf"), ("blueprint", "blueprint.pdf"), ("site", "site/index.html"))} | {"video": bool(list(d.glob("*.mp4")))}
