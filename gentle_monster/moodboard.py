"""Magazine moodboard: multi-spread A3 PDF built from the job, the user's photos and (optionally)
a reference layout image.

How a board is decided -- nothing here is a fixed page:
  1. Style. The reference layout is *measured* (photos.reference_style): paper colour, white-space
     share, image share, accent -> paper, margins, density. With a Gemini key the reference is also
     *read* (vision) for the spread order and masthead; the answer is accepted only if it names
     spreads from CATALOG. Without a reference the default grammar is the exhibition-catalogue one
     (cover · contents · rotated manifesto · image pair · full bleed · board · collage · sequence).
  2. Photos. Every photo is measured (photos.measure). The strongest (saturation x contrast x edges)
     takes the cover, the darkest/monochrome takes the full bleed, the rest fill pairs and the collage.
  3. Gaps. When photos run out, slots fall back to photoreal renders (if a blueprint was made),
     then the plan, then generated material textures -- each labelled as generated, never passed
     off as a photograph.
The page says which of these happened (closing spread, "How this board was made").
"""
from __future__ import annotations

import base64
import html
import json
import re
from pathlib import Path

from gentle_monster import paths, photos as PH

CATALOG = ("cover", "contents", "manifesto", "pair", "bleed", "board", "collage", "sequence")
DEFAULT = list(CATALOG)
FONT = '"Archivo","Liberation Sans","Helvetica Neue",Arial,sans-serif'
e = lambda s: html.escape(str(s))


# ---------------------------------------------------------------- style
def _llm_read(ref: str, ask_vision=None) -> "dict | None":
    """Gemini vision reads the reference for spread order + masthead. Returns None on any failure (no key, bad JSON)."""
    prompt = ("This image is a reference layout (a magazine or catalogue spread board). Describe its layout grammar as JSON only: "
              '{"sequence": [spread types in the order this reference suggests, chosen only from ' + json.dumps(list(CATALOG)) + '], '
              '"masthead": "stencil|solid|outline", "type": "grotesk|serif", "mood": [three English words]}. '
              "Always start with cover and include board.")
    try:
        if ask_vision is None:
            from gentle_monster import llm
            if not llm.key():
                return None
            data = Path(ref).read_bytes()
            mime = "image/png" if ref.lower().endswith(".png") else ("image/webp" if ref.lower().endswith(".webp") else "image/jpeg")
            txt = llm.ask(prompt, images=[(mime, data)])
        else:
            txt = ask_vision(prompt, ref)
        a, b = txt.find("{"), txt.rfind("}")
        d = json.loads(txt[a:b + 1])
        seq = [s for s in d.get("sequence", []) if s in CATALOG]
        if not seq or seq[0] != "cover" or "board" not in seq:
            return None
        return {"sequence": list(dict.fromkeys(seq)), "masthead": d.get("masthead") if d.get("masthead") in ("stencil", "solid", "outline") else "stencil",
                "type": d.get("type") if d.get("type") in ("grotesk", "serif") else "grotesk", "mood": [str(m)[:20] for m in d.get("mood", [])][:3]}
    except Exception:                                        # noqa: BLE001 -- the measured style still stands
        return None


def style(refs, ask_vision=None, use_llm: bool = True) -> dict:
    st = {"paper": "#fbfbf9", "ink": "#111111", "sub": "#66665f", "pad": 6.0, "density": "balanced", "sequence": DEFAULT,
          "masthead": "stencil", "type": "grotesk", "mood": [], "source": "default exhibition-catalogue grammar", "measured": None}
    if not refs:
        return st
    m = PH.reference_style(refs[0])
    st["measured"] = m
    if m["dark_paper"]:
        st.update(paper=m["paper"], ink="#f1f1ec", sub="#a9a9a2")
    elif m["paper"] != "#ffffff":
        st["paper"] = m["paper"]
    st["density"] = m["density"]
    st["pad"] = {"airy": 7.5, "balanced": 6.0, "dense": 4.5}[m["density"]]
    st["source"] = f"reference measured: paper {m['paper']}, white space {m['whitespace']:.0%}, image share {m['image_share']:.0%} -> {m['density']}"
    if use_llm:
        r = _llm_read(refs[0], ask_vision)
        if r:
            st.update(sequence=r["sequence"], masthead=r["masthead"], type=r["type"], mood=r["mood"])
            st["source"] += "; spread order read from the reference by Gemini vision"
    return st


# ---------------------------------------------------------------- images
class Pool:
    """Photos ranked by measured strength, then photoreal renders. When both run out, an image already used
    comes back as a detail crop (magazines do this); a generated texture only when there is no image at all."""

    def __init__(self, photo_paths, renders=()):
        self.meta = [PH.measure(p) for p in photo_paths]
        self.left = sorted(self.meta, key=lambda m: -m["strength"])
        self.left += [{"path": r, "generated": "photoreal render"} for r in renders if r and Path(r).is_file()]
        self.used, self.k = [], 0

    def reserve(self, prefer: str) -> "dict | None":
        """Take the best match for a role now, before the generic slots empty the pool."""
        cand = [m for m in self.left if "generated" not in m]
        if not cand:
            return None
        key = {"dark": lambda m: m["dark"] + (1 if m["mono"] else 0), "bright": lambda m: m["brightness"]}[prefer]
        m = max(cand, key=key)
        self.left.remove(m); self.used.append(m)
        return m

    def take(self) -> dict:
        if self.left:
            m = self.left.pop(0); self.used.append(m)
            return m
        imgs = [m for m in self.used if not m.get("texture") and not m.get("detail")]
        if imgs:
            m = dict(imgs[self.k % len(imgs)], detail=True, pos=["30% 35%", "70% 60%", "50% 75%", "25% 70%"][self.k % 4]); self.k += 1
            self.used.append(m)
            return m
        m = {"texture": True}; self.used.append(m)
        return m

    def all(self):
        return [m for m in self.used if not m.get("texture") and not m.get("detail")]


def _uri(p) -> str:
    return Path(p).resolve().as_uri()


def _img(m: dict, cls: str = "", pos: str = "50% 50%", tex: str = "concrete", alt: str = "") -> str:
    if m.get("texture"):
        return f'<canvas class="{cls}" data-tex="{e(tex)}" width="600" height="600" aria-label="generated texture"></canvas>'
    if m.get("detail"):                                   # a detail crop of an image already on the board
        return f'<div class="{cls} crop"><img src="{_uri(m["path"])}" alt="{e(alt)}" style="object-position:{m["pos"]};transform:scale(1.6);transform-origin:{m["pos"]}"></div>'
    return f'<img class="{cls}" src="{_uri(m["path"])}" alt="{e(alt)}" style="object-position:{pos}">'


def _short(t: str, n: int = 28) -> str:
    """First clause, cut at a word boundary -- never mid-word."""
    t = t.split(",")[0].split(".")[0].strip()
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(" ,;:-")


def _cap(m: dict) -> str:
    if m.get("texture"):
        return "generated material texture"
    if m.get("generated"):
        return m["generated"] + (" · detail" if m.get("detail") else "") + " (generated)"
    if m.get("detail"):
        return f"{Path(m['path']).stem} · detail crop"
    return f"{Path(m['path']).stem} · brightness {m['brightness']:.2f} · saturation {m['saturation']:.2f} · warmth {m['warmth']:+.2f}"


# ---------------------------------------------------------------- spreads
def _spreads(job, st, pool, pal, mats, plan):
    brand, title = job["brand"], job["title"]
    L = job["layout"]
    out = {}
    # the darkest / monochrome photo belongs to the full bleed -- claimed first when there are enough photos,
    # because noise in near-black pixels reads as saturation and can make a dark shot the "strongest"
    if sum(1 for m in pool.left if "generated" not in m) >= 3:
        bl = pool.reserve("dark"); hero = pool.take()
    else:
        hero = pool.take(); bl = pool.reserve("dark") or pool.take()
    back = pool.reserve("bright") or pool.take()
    out["cover"] = f"""<div class="page l"><div class="bleed">{_img(back, 'fill', tex=mats[0][2])}</div>
  <div class="box" style="left:9cqw;top:54cqw;width:64cqw"><p class="k">{e(brand)} · mood issue</p><p class="s">{e(job['line'])}</p></div>
  <span class="cap" style="left:9cqw;bottom:6cqw">BACK COVER · {e(_cap(back))}</span></div>
 <div class="page r"><div class="pad col">
  <h1 class="mast {st['masthead']}" style="font-size:{min(19.0, 84 / (max(len(w) for w in brand.split()) * .72)):.2f}cqw">{e(brand)}</h1>
  <div class="hero">{_img(hero, 'fill', tex=mats[1][2])}</div>
  <div class="colo s"><div>{e(title).upper()}<br><span class="sub">{e(job.get('subtitle', ''))}</span></div><div><b>{e(job['quote'])}</b></div></div></div></div>"""
    toc = [("01", "Introduction", job["line"]), ("02", title, job.get("subtitle", "")), ("03", "Palette · materials", " · ".join(m[0] for m in mats)),
           ("04", "The walk", " · ".join(s["cap"] for s in job["stops"])), ("05", "Notes", "how this board was made")]
    out["contents"] = f"""<div class="page l"><div class="pad"><div class="toc">{''.join(f'<div><span>{n}</span><span>{e(t).upper()}<br><i>{e(d)}</i></span></div>' for n, t, d in toc)}</div></div><span class="folio">1</span></div>
 <div class="page r"><div class="pad col" style="justify-content:space-between"><p class="k" style="text-align:center">Introduction</p>
  <div class="s intro"><p>{e(job['synopsis'])}</p><p class="hr">{''.join(f'<b>{e(w["t"])}.</b> {e(w["d"])} ' for w in job['why'][:2])}</p></div></div><span class="folio">2</span></div>"""
    lines = [s["cap"].rstrip(".") for s in job["stops"]] + [job["keywords"][0]]
    fs = max(3.2, min(8.0, 125 / (max(len(x) for x in lines) * .56)))
    mp = pool.take()
    out["manifesto"] = f"""<div class="page l"><div class="rot" style="font-size:{fs:.2f}cqw">{''.join(f'<p>{e(x)}<sup>{i + 1}</sup></p>' for i, x in enumerate(lines))}</div>
  <p class="k" style="position:absolute;right:{st['pad']}cqw;top:{st['pad']}cqw;text-align:right">{e(title)}<br>{e(brand)}</p><span class="folio">3</span></div>
 <div class="page r"><div class="bleed">{_img(mp, 'fill', tex=mats[2][2])}</div><span class="cap" style="right:6cqw;bottom:6cqw">{e(_cap(mp))}</span></div>"""
    a, b = pool.take(), pool.take()
    w1, w2 = (job["keywords"] + ["", ""])[:2]
    out["pair"] = f"""<div class="page l"><div class="pad pair"><p class="k">{e(title)} — {e(brand)}</p><div class="frame">{_img(a, 'fill', tex=mats[1][2])}</div><p class="word">{e(w1)}</p></div><span class="folio">4</span></div>
 <div class="page r"><div class="pad pair"><p></p><div class="frame">{_img(b, 'fill', tex=mats[2][2])}</div><p class="word">{e(w2)}</p></div><span class="folio">5</span></div>"""
    out["bleed"] = f"""<div class="page l"><div class="bleed">{_img(bl, 'half left', tex=mats[3][2])}</div><span class="cap" style="left:6cqw;bottom:6cqw">{e(title).upper()} — {e(brand).upper()}</span></div>
 <div class="page r"><div class="bleed">{_img(bl, 'half right', tex=mats[3][2])}</div><span class="cap" style="right:6cqw;bottom:6cqw">{e(_cap(bl))}</span></div>"""
    sw = "".join(f'<div><i style="background:{e(h)}"></i><b>{e(h.upper())}</b><span>{e(n)}</span></div>' for h, n in pal)
    mt = "".join(f'<div><canvas data-tex="{e(k)}" width="240" height="240"></canvas><b>{e(n)}</b><span>{e(w)}</span></div>' for n, w, k in mats)
    why = "".join(f'<div><b>{e(w["t"])}</b><p>{e(w["d"])}</p></div>' for w in job["why"])
    out["board"] = f"""<div class="page l"><div class="pad col"><div><h2 class="ttl">{e(title)}</h2><p class="sub2">{e(job.get('subtitle', ''))}</p></div>
  <p class="syn">{e(job['synopsis'])}</p><div class="kw s">{''.join(f'<span>{e(k)}</span>' for k in job['keywords'])}</div>
  <div style="margin-top:auto"><p class="k hr">Palette</p><div class="sw s">{sw}</div></div></div><span class="folio">6</span></div>
 <div class="page r"><div class="pad col"><div class="mats s">{mt}</div><div class="why s">{why}</div>
  {f'<div class="plan"><img src="{_uri(plan)}" alt="plan"></div>' if plan else ''}</div><span class="folio">7</span></div>"""
    cl = [pool.take() for _ in range(3)]
    walk = "".join(f'<div><b>{e(s["cap"])}</b><p>{e(s["sub"])}</p></div>' for s in job["stops"])
    out["collage"] = f"""<div class="page l"><div class="coll">{_img(cl[0], 'fill wide', tex=mats[0][2])}<canvas data-tex="{e(mats[1][2])}" width="400" height="400"></canvas><canvas data-tex="{e(mats[2][2])}" width="400" height="400"></canvas>{_img(cl[1], 'fill', tex=mats[3][2])}{_img(cl[2], 'fill', tex=mats[0][2])}</div></div>
 <div class="page r"><div class="pad col"><p class="k">The walk · three moments</p><h2 class="ttl">{e(title)}</h2><div class="why s">{walk}</div>
  <p class="q" style="margin-top:auto">{e(job['quote'])}</p></div><span class="folio">9</span></div>"""
    seq = pool.all()[:6] or [{"texture": True}] * 3
    words = [_short(s["cap"]) for s in job["stops"]] + job["keywords"]
    cols = 3 if len(seq) >= 5 else 2
    tiles = "".join(f'<figure>{_img(m, "sq", tex=mats[i % 4][2])}<figcaption class="word2">{e(words[i % len(words)])}</figcaption></figure>' for i, m in enumerate(seq))
    notes = [st["source"] + ".", f"{len(pool.meta)} photo(s) placed by measured strength; " + ("photoreal renders (generated) filled slots; " if any("generated" in x for x in pool.used) else "") + ("repeated images appear as detail crops." if any(x.get("detail") for x in pool.used) else "no image is repeated."),
             f"Layout {L['W']} x {L['D']} m, ceiling {L['H']} m. Concept; dimensions assumed, not surveyed. Circulation checked by code (>= 0.3 m clear)."]
    out["sequence"] = f"""<div class="page l"><div class="pad"><p class="k">Sequence</p><div class="seq" style="grid-template-columns:repeat({cols},1fr)">{tiles}</div></div><span class="folio">10</span></div>
 <div class="page r"><div class="pad col"><p class="thesis">{e(job['quote'])}</p>
  <div class="notes xs hr" style="margin-top:auto"><p class="k">How this board was made</p>{''.join(f'<p>{e(n)}</p>' for n in notes)}</div></div><span class="folio">11</span></div>"""
    return out


def _css(st, accent) -> str:
    serif = st["type"] == "serif"
    body = '"Nanum Myeongjo","Liberation Serif",Georgia,serif' if serif else FONT
    return f"""
@page{{size:420mm 297mm;margin:0}} *{{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
html,body{{margin:0;background:{st['paper']};color:{st['ink']};font-family:{FONT}}}
.spread{{width:420mm;height:297mm;display:grid;grid-template-columns:1fr 1fr;break-after:page;--a:{accent};--p:{st['pad']}cqw}}
.page{{container-type:inline-size;position:relative;overflow:hidden;background:{st['paper']}}}
.page.l{{box-shadow:inset -14px 0 18px -16px rgba(0,0,0,.35)}} .page.r{{box-shadow:inset 14px 0 18px -16px rgba(0,0,0,.35)}}
.pad{{position:absolute;inset:{st['pad']}cqw {st['pad'] + .5}cqw {st['pad'] - 1}cqw}} .col{{display:flex;flex-direction:column;gap:3.2cqw}}
.bleed{{position:absolute;inset:0}} .fill{{width:100%;height:100%;object-fit:cover;display:block}}
.half{{position:absolute;top:0;height:100%;width:200%;max-width:none;object-fit:cover}} .half.left{{left:0}} .half.right{{left:-100%}}
canvas{{display:block;width:100%;height:100%}}
.s{{font-size:max(1.5cqw,9.5px);line-height:1.6}} .xs{{font-size:max(1.25cqw,8.5px);line-height:1.5;color:{st['sub']}}}
.k{{font-size:max(1.2cqw,8px);letter-spacing:.16em;text-transform:uppercase;margin:0}}
.sub,.sub2{{color:{st['sub']};font-style:italic}} .sub2{{font-size:2.6cqw;margin:1.2cqw 0 0}}
.mast{{position:relative;margin:0;font-weight:700;line-height:.82;letter-spacing:-.045em;text-transform:uppercase;overflow-wrap:normal;word-break:keep-all}}
.mast.stencil::after{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 11cqw,{st['paper']} 11cqw 12.2cqw),repeating-linear-gradient(0deg,transparent 0 6.4cqw,{st['paper']} 6.4cqw 7.4cqw)}}
.mast.outline{{color:transparent;-webkit-text-stroke:.35cqw {st['ink']}}}
.hero{{flex:1;min-height:0}} .colo{{display:grid;grid-template-columns:1fr 1.3fr;gap:4cqw}}
.box{{position:absolute;background:rgba(10,12,10,.55);color:#f4f4ef;padding:3cqw;border:1px solid rgba(255,255,255,.45)}}
.cap{{position:absolute;font-size:max(1.15cqw,8px);color:#f4f4ef;text-shadow:0 1px 3px rgba(0,0,0,.7);letter-spacing:.04em}}
.folio{{position:absolute;bottom:3cqw;font-size:max(1.1cqw,8px);color:{st['sub']}}} .l .folio{{left:6.5cqw}} .r .folio{{right:6.5cqw}}
.toc{{display:grid;gap:3cqw}} .toc div{{display:grid;grid-template-columns:8cqw 1fr;gap:2cqw;font-size:max(1.5cqw,9.5px)}} .toc i{{color:{st['sub']}}}
.intro{{max-width:80cqw;margin-left:auto;display:grid;gap:2.4cqw;font-family:{body}}} .hr{{border-top:1px solid {st['ink']};padding-top:1.6cqw}}
.rot{{position:absolute;left:6cqw;top:6cqw;bottom:9cqw;writing-mode:vertical-rl;text-orientation:sideways;transform:rotate(180deg);display:flex;flex-direction:column;gap:1.4cqw}}
.rot p{{margin:0;font-weight:500;line-height:1.05;letter-spacing:-.03em;white-space:nowrap}} .rot sup{{font-size:.4em;vertical-align:.9em}}
.pair{{display:grid;grid-template-rows:1fr auto 1fr;gap:4cqw}} .frame{{aspect-ratio:4/3}} .word{{font-size:9cqw;font-weight:500;letter-spacing:-.03em;text-align:center;margin:0;line-height:1}}
.ttl{{font-weight:700;font-size:7.6cqw;line-height:.95;letter-spacing:-.03em;margin:0}} .syn{{font-family:{body};font-size:max(1.8cqw,10.5px);line-height:1.8;margin:0}}
.kw{{display:flex;flex-wrap:wrap;gap:1.2cqw}} .kw span{{border:1px solid {st['ink']};border-radius:999px;padding:.3cqw 1.6cqw}}
.sw{{display:grid;grid-template-columns:repeat(5,1fr)}} .sw i{{display:block;aspect-ratio:1/1.3}} .sw b{{display:block;font-weight:500;margin-top:1cqw}} .sw span{{color:{st['sub']}}}
.mats{{display:grid;grid-template-columns:repeat(4,1fr);gap:2.4cqw}} .mats canvas{{aspect-ratio:1;height:auto}} .mats b{{display:block;margin-top:1cqw;font-weight:600}} .mats span{{color:{st['sub']}}}
.why{{display:grid;gap:2cqw;counter-reset:w}} .why div{{counter-increment:w}} .why div::before{{content:counter(w,decimal-leading-zero) " ";font-weight:700;color:var(--a)}}
.why b{{font-weight:600}} .why p{{margin:.5cqw 0 0;color:{st['sub']}}}
.plan{{margin-top:auto;min-height:0}} .plan img{{width:100%;max-height:58cqw;object-fit:contain;background:#fff}}
.coll{{position:absolute;inset:0;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1.4fr 1fr 1fr;gap:1cqw}} .coll .wide{{grid-column:1/-1}}
.q{{font-size:3.2cqw;line-height:1.25;color:var(--a);margin:0}}
.seq{{display:grid;gap:3cqw;margin-top:3cqw}} .crop{{overflow:hidden}} .crop img{{width:100%;height:100%;object-fit:cover;display:block}} .seq figure{{margin:0}} .seq .sq{{width:100%;aspect-ratio:1;object-fit:cover;display:block;height:auto}}
.word2{{font-size:3.6cqw;font-weight:500;letter-spacing:-.02em;margin-top:1cqw}}
.thesis{{font-size:6cqw;line-height:1.15;letter-spacing:-.03em;font-weight:500;margin:0;color:var(--a)}} .notes p{{margin:.6cqw 0 0}}
"""


def build(job: dict, out_dir, photo_paths=(), refs=(), renders=(), plan=None, ask_vision=None, use_llm: bool = True) -> dict:
    from gentle_monster import documents as D
    out_dir = Path(out_dir)
    st = style(list(refs), ask_vision=ask_vision, use_llm=use_llm)
    pool = Pool([p for p in photo_paths if Path(p).is_file()], renders=renders)
    pal = [(h, f"from {Path(p).stem}") for p in list(photo_paths)[:3] if Path(p).is_file() for h, _ in PH.palette(p)[:1]]
    pal = (pal + [(p["hex"], p.get("name", "")) for p in job["palette"]])[:5]
    mats = [(m["name"], m["where"], m.get("preset") or "concrete") for m in job["materials"]][:4]
    while len(mats) < 4:
        mats.append(("Concrete", "", "concrete"))
    sp = _spreads(job, st, pool, pal, mats, plan)
    seq = [s for s in st["sequence"] if s in sp]
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(job["title"])} moodboard</title><style>{_css(st, job["accent"])}</style></head><body>'
           + "".join(f'<section class="spread" data-kind="{k}">{sp[k]}</section>' for k in seq) + D._TEX_JS + "</body></html>")
    hp = out_dir / "moodboard.html"
    hp.write_text(doc, encoding="utf-8")
    pdf = D._print(hp, out_dir / "moodboard.pdf", "420mm", "297mm")
    return {"pdf": pdf, "spreads": seq, "style": {k: v for k, v in st.items() if k != "sequence"}, "photos": [m["path"] for m in pool.meta],
            "generated_fills": sum(1 for x in pool.used if "generated" in x or x.get("texture")), "detail_crops": sum(1 for x in pool.used if x.get("detail"))}
