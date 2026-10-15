"""python3 -m gentle_monster <command>

    make "<brief>" [--brand B] [--name N] [--photo P ...] [--ref R ...] [--image I ...] [--blueprint] [--full]
                              synopsis (Gemini) -> layout PDF + magazine moodboard PDF.
                              --photo: photos · --ref: reference layout image(s) · --image: unsorted (measured: photo or reference)
                              --blueprint adds the blueprint; --full adds blueprint + MP4 (tens of minutes).
    example <gm|tb|ac|ae> [--name N] [same image flags] [--blueprint] [--full]
                              same, from a bundled synopsis (no model call)
    layout <name> [same image flags]   rebuild the layout + moodboard of an existing job (alias: moodboard)
    revise <name> "<instruction>" [same image flags] [--no-verify]
                              a follow-up on an existing job ("벽은 콘크리트 말고 나무로"): memory -> selected context
                              -> Gemini -> code checks -> layout + moodboard rebuilt. An unclear correction is asked back.
    memory <name> [--all]           what the job's memory holds (active records; --all: superseded and retracted too)
    blueprint <name> [--then-video] photoreal stills + A3 drawing sheet PDF (on request)
    cover <name|gm|tb|ac|ae> [--attach PATH] [--print]
                                    the blueprint's Codex cover: the three.js scene + sheet data as an image spec in
                                    .relay/tasks/ (push it; the VM inbox runs Codex). --attach <task folder|png> makes it
                                    the job's cover.png, which the next blueprint puts in front of the sheet
    video <name>                    30 s walkthrough MP4 (on request; run it in the background)
    site <name> [--rounds N]        frontend engine: the room as a web page, browser-judged, evolved
                                    under the se_new policy (ACCEPT only if V holds and J rose)
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
        a.add_argument("--site", action="store_true", help="also build the web page (frontend engine)")
        _imgs(a)
    for c in ("layout", "moodboard"):
        a = sub.add_parser(c); a.add_argument("name"); _imgs(a)
    a = sub.add_parser("revise"); a.add_argument("name"); a.add_argument("instruction")
    a.add_argument("--no-verify", action="store_true", help="skip the separate model call that checks the instruction"); _imgs(a)
    a = sub.add_parser("memory"); a.add_argument("name"); a.add_argument("--all", action="store_true")
    for c in ("blueprint", "video", "status"):
        sub.add_parser(c).add_argument("name")
    sub.choices["blueprint"].add_argument("--then-video", action="store_true", help="render the MP4 right after")
    a = sub.add_parser("cover"); a.add_argument("name"); a.add_argument("--attach", default="")
    a.add_argument("--print", action="store_true", help="print the image spec only")
    a = sub.add_parser("site"); a.add_argument("name"); a.add_argument("--rounds", type=int, default=6)
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
            if a.site:
                pipeline.site(name)
            if a.full:
                pipeline.video(name)
            print(f"=== 보고 ===\n작업 {name}: 시놉시스 · 레이아웃 PDF · 무드보드 PDF" + (" · 청사진" if a.full or a.blueprint else "") + (" · MP4" if a.full else "") + (" · 웹 페이지" if a.site else "") +
                  (f"\n청사진·영상이 필요하면: python3 -m gentle_monster blueprint {name} · video {name}" if not a.full else ""))
        elif a.cmd == "revise":
            r = pipeline.revise(a.name, a.instruction, verify_ask=False if a.no_verify else None)
            if r["asked"]:
                print("=== 보고 ===\n" + r["asked"])
                return 0
            _layout(a.name, a)
            bad = [c for c in r["checks"] if c["verdict"] not in ("supported",)]
            print(f"=== 보고 ===\n작업 {a.name}: 수정본 시놉시스 · 레이아웃 PDF · 무드보드 PDF (이전 판은 job.v*.json 에 남았다)"
                  + "".join(f"\n- {'확인됨' if c['verdict'] == 'supported' else '확인 안 됨: ' + c['verdict']} ({c['by']}) {c['what']}" for c in r["checks"])
                  + "".join(f"\n- {x}" for x in r["notes"]))
            return 0 if not [c for c in bad if c["verdict"] in ("violated", "contradicted")] else 1
        elif a.cmd == "memory":
            from gentle_monster import memory
            st = memory.open_job(a.name)
            for r in st.all():
                if a.all or r["status"] == "active":
                    print(f"{r['id']:>4} {r['status']:<10} {r['kind']:<15} {r['turn'] or r['source'].get('ref', ''):<8} "
                          f"{(r['key'] or ''):<12} {r['content'][:90]}" + (f"  -> {r['superseded_by']}" if r['superseded_by'] else ""))
        elif a.cmd in ("layout", "moodboard"):
            _layout(a.name, a)
        elif a.cmd == "blueprint":
            pipeline.blueprint(a.name)
            if a.then_video:
                pipeline.video(a.name)
        elif a.cmd == "cover":
            from gentle_monster import cover
            if a.attach:
                print(f"=== 보고 ===\n작업 {a.name}: Codex 커버 → {cover.attach(a.name, a.attach)} (다음 blueprint 의 첫 장)")
                return 0
            job = pipeline.load_job(a.name) if pipeline.job_path(a.name).is_file() or a.name not in spec.examples() else spec.examples()[a.name]
            if a.print:
                print(json.dumps(cover.spec(job), ensure_ascii=False, indent=2))
                return 0
            d = cover.request(a.name, job)
            t = d.relative_to(paths.REPO)
            print(f"=== 보고 ===\n작업 {a.name}: Codex 커버 요청 {t}\n"
                  f"git add {t} && git commit -m 'relay request {d.name}: image' && git push  (claude/* 브랜치)\n"
                  f"VM 이 image.png 를 올리면: python3 -m gentle_monster cover {a.name} --attach {t}")
        elif a.cmd == "video":
            pipeline.video(a.name)
        elif a.cmd == "site":
            r = pipeline.site(a.name, rounds=a.rounds)
            return 0 if r["ships"] else 1
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
