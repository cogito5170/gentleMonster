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
    site <name> [--rounds N]        frontend engine: the room as a web page, browser-judged, evolved
                                    under the se_new policy (ACCEPT only if V holds and J rose)
    status <name> · list · check <job.json>
    magazine "<brief>" [--name N] [--image PATH --credit C --rights own|licensed|...] [--no-pdf]
                              editorial system: research catalogue -> Drift -> >= 3 directions -> plan ->
                              HTML + PDF -> QA (PASS/WARNING/FAIL/NOT_CHECKED). No model call.
    research                  regenerate research/*.md from research/sources.json and print coverage
    cv <spec.json> [--name N]            a one-page CV in the SPA design (editorial/cv/*.json)
    photo-issue <spec.json> [--name N]   a magazine around your own photos (editorial/issues/*.json)
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
    for c in ("blueprint", "video", "status"):
        sub.add_parser(c).add_argument("name")
    sub.choices["blueprint"].add_argument("--then-video", action="store_true", help="render the MP4 right after")
    a = sub.add_parser("site"); a.add_argument("name"); a.add_argument("--rounds", type=int, default=6)
    sub.add_parser("list")
    sub.add_parser("check").add_argument("file")
    a = sub.add_parser("magazine"); a.add_argument("brief"); a.add_argument("--name", default="")
    a.add_argument("--image", action="append", default=[], help="a photo you may publish (repeatable)")
    a.add_argument("--credit", action="append", default=[], help="credit line per --image, same order")
    a.add_argument("--rights", action="append", default=[], help="own | licensed | public_domain | cc0 | cc-by, per --image")
    a.add_argument("--no-pdf", action="store_true"); a.add_argument("--sources", default=None, help="another research catalogue")
    sub.add_parser("research")
    a = sub.add_parser("cv"); a.add_argument("spec"); a.add_argument("--name", default=""); a.add_argument("--layout", default="rows", choices=["rows", "split", "creative", "art", "all"]); a.add_argument("--no-pdf", action="store_true")
    a = sub.add_parser("photo-issue"); a.add_argument("spec"); a.add_argument("--name", default=""); a.add_argument("--no-pdf", action="store_true")
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
        elif a.cmd in ("layout", "moodboard"):
            _layout(a.name, a)
        elif a.cmd == "blueprint":
            pipeline.blueprint(a.name)
            if a.then_video:
                pipeline.video(a.name)
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
        elif a.cmd == "magazine":
            from gentle_monster.magazine import build as MB
            imgs = [(str(paths.resolve_photo(p)), (a.credit[i] if i < len(a.credit) else ""), (a.rights[i] if i < len(a.rights) else "unknown"))
                    for i, p in enumerate(a.image)]
            r = MB.build(a.brief, name=a.name, images=imgs, pdf=False if a.no_pdf else None, cat_path=a.sources)
            print("=== 방향 ===")
            for hid, t, st, tot in r["directions"]:
                print(f"  {hid}  {st:8s} {tot:5}  {t}")
            print(f"=== 선택: {r['chosen']} · {r['pages']}쪽 ===\nHTML {r['html']}\nPDF  {r['pdf'] or '(없음: ' + str((r['pdf_result'] or {}).get('error', '요청 안 함')) + ')'}")
            print(f"QA {r['verdict']}: " + ", ".join(f"{c['status']} {c['check']}" for c in r["checks"] if c["status"] != "PASS"))
            print(f"보고서 {r['dir']}/QA_REPORT.md")
            return 0 if r["verdict"] != "FAIL" else 1
        elif a.cmd == "cv":
            from gentle_monster.magazine import cv as CV
            worst = 0
            for lay in (["rows", "split", "creative", "art"] if a.layout == "all" else [a.layout]):
                r = CV.build(a.spec, name=a.name, pdf=not a.no_pdf, layout=lay)
                print(f"[{lay}] {CV.LAYOUTS[lay]}\nHTML {r['html']}\nPDF  {r['pdf'] or (r['pdf_result'] or {}).get('error', '요청 안 함')}")
                print(f"QA {r['verdict']}: " + "; ".join(f"{c['status']} {c['check']} ({c['detail']})" for c in r["checks"] if c["status"] != "PASS"))
                print(f"보고서 {r['dir']}/QA_REPORT.md")
                worst = max(worst, r["verdict"] == "FAIL")
            return worst
        elif a.cmd == "photo-issue":
            from gentle_monster.magazine import photo_issue as PI
            r = PI.build(a.spec, name=a.name, pdf=not a.no_pdf)
            print(f"{r['pages']}쪽\nHTML {r['html']}\nPDF  {r['pdf'] or (r['pdf_result'] or {}).get('error', '요청 안 함')}")
            print("잰 표지 후보(채도 x 대비 x 윤곽):", ", ".join(r["measured_cover_rank"]))
            print(f"QA {r['verdict']}: " + "; ".join(f"{c['status']} {c['check']}" for c in r["checks"] if c["status"] != "PASS"))
            print(f"보고서 {r['dir']}/QA_REPORT.md")
            return 0 if r["verdict"] != "FAIL" else 1
        elif a.cmd == "research":
            from gentle_monster.magazine import build as MB, catalogue as CAT
            cat = CAT.load()
            bad = CAT.validate(cat)
            for f in MB.write_research_docs():
                print("wrote", f)
            print(json.dumps(CAT.coverage(cat), ensure_ascii=False, indent=1))
            print("catalogue problems:", len(bad), *bad[:10], sep="\n  ")
            return 0 if not bad else 1
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
