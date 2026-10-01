"""python3 -m gentle_monster <command>

    make "<brief>" [--brand B] [--name N] [--photo P ...] [--ref R ...] [--image I ...] [--blueprint] [--full]
                              synopsis (Gemini) -> layout PDF + magazine moodboard PDF.
                              --photo: photos · --ref: reference layout image(s) · --image: unsorted (measured: photo or reference)
                              --blueprint adds the blueprint; --full adds blueprint + MP4 (tens of minutes).
    example <gm|tb|ac|ae> [--name N] [same image flags] [--blueprint] [--full]
                              same, from a bundled synopsis (no model call)
    layout <name> [same image flags]   rebuild the layout + moodboard of an existing job (alias: moodboard)
    blueprint <name> [--then-video] photoreal stills + A3 drawing sheet PDF (on request)
    video <name>                    30 s walkthrough MP4 (on request; run it in the background)
    status <name> · list · check <job.json>
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from gentle_monster import paths, pipeline, spec


def _imgs(a) -> None:
    a.add_argument("--photo", action="append", default=[]); a.add_argument("--ref", action="append", default=[])
    a.add_argument("--image", action="append", default=[]); a.add_argument("--text", default="", help="the user's words (reference hints)")
    a.add_argument("--no-llm", action="store_true", help="measure the reference only; no Gemini vision read")


def _layout(name, a):
    return pipeline.layout(name, photos=[str(paths.resolve_photo(p)) for p in a.photo], refs=[str(paths.resolve_photo(p)) for p in a.ref],
                           images=[str(paths.resolve_photo(p)) for p in a.image], text=a.text, use_llm=not a.no_llm)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gentle_monster")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("make", "example"):
        a = sub.add_parser(c)
        a.add_argument("what", help="brief" if c == "make" else "bundled example id")
        a.add_argument("--brand", default=""); a.add_argument("--name", default="")
        a.add_argument("--full", action="store_true"); a.add_argument("--blueprint", action="store_true")
        _imgs(a)
    for c in ("layout", "moodboard"):
        a = sub.add_parser(c); a.add_argument("name"); _imgs(a)
    for c in ("blueprint", "video", "status"):
        sub.add_parser(c).add_argument("name")
    sub.choices["blueprint"].add_argument("--then-video", action="store_true", help="render the MP4 right after")
    sub.add_parser("list")
    sub.add_parser("check").add_argument("file")
    a = ap.parse_args(argv)
    try:
        if a.cmd in ("make", "example"):
            name = a.name or (a.what if a.cmd == "example" else time.strftime("gm_%Y%m%d_%H%M%S"))
            if a.cmd == "make":
                pipeline.synopsis(name, brief=a.what, brand=a.brand)
            else:
                pipeline.synopsis(name, example=a.what)
            _layout(name, a)
            if a.full or a.blueprint:
                pipeline.blueprint(name)
            if a.full:
                pipeline.video(name)
            print(f"=== 보고 ===\n작업 {name}: 시놉시스 · 레이아웃 PDF · 무드보드 PDF" + (" · 청사진" if a.full or a.blueprint else "") + (" · MP4" if a.full else "") +
                  (f"\n청사진·영상이 필요하면: python3 -m gentle_monster blueprint {name} · video {name}" if not a.full else ""))
        elif a.cmd in ("layout", "moodboard"):
            _layout(a.name, a)
        elif a.cmd == "blueprint":
            pipeline.blueprint(a.name)
            if a.then_video:
                pipeline.video(a.name)
        elif a.cmd == "video":
            pipeline.video(a.name)
        elif a.cmd == "status":
            print(json.dumps(pipeline.status(a.name), ensure_ascii=False))
        elif a.cmd == "list":
            for d in sorted(p for p in paths.OUT.glob("*") if (p / "job.json").is_file()):
                print(d.name, json.dumps(pipeline.status(d.name)))
        elif a.cmd == "check":
            bad = spec.check(spec.load(a.file))
            print("ok" if not bad else "\n".join(bad))
            return 0 if not bad else 1
        return 0
    except Exception as e:                                  # noqa: BLE001 -- say what failed, in one block
        print(f"[gentle_monster {a.cmd} 실패] {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
