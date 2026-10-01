"""The judge. Code, not a model -- the generator (compose) never grades itself.

It opens the page in headless Chromium and **measures the rendered page**, not the source text
(se_new: a check that reads characters cannot see what the browser does). Two kinds of result:

V -- invariants. Every one must hold or the page is not acceptable at all. Unknown counts as fail.
    overflow-375 / overflow-1440   no horizontal scroll at phone and desktop width, and no text box outside
                                   the viewport (a clipping container hides overflow from scrollWidth --
                                   measured: the first version of this check passed a 900 px line on a phone)
    contrast-rendered              every visible text element, computed colour over its composited
                                   background: >= 4.5 (>= 3 for large text). A text element whose
                                   background is an image/gradient cannot be measured -> fail
    contrast-tokens                the same quantity by a second route: from the token pairs, by math
    min-font-375                   no text under 12 px on a phone
    offline                        0 requests leave file:/data: (fonts, CDNs, trackers)
    js-errors                      0 page errors
    names                          every img has alt; every svg[role=img]/canvas has an accessible name
    headings                       lang set, exactly one h1, no skipped heading level
    reduced-motion                 with prefers-reduced-motion: reduce, no animation is running
    weight                         the page is <= 1.5 MB

J -- quality, each 0..1, higher is better. The taste is declared here, not hidden:
    drama      scale contrast: largest font / running-text font at 1440 px in 6-14 (Gentle Monster's
               masthead against the body). Running text = the size carrying most <p> characters
    hierarchy  4-8 distinct type sizes reads as a system; fewer is flat, more is noise
    measure    share of paragraphs whose measured characters-per-line fall in 40-80 (desktop)
               and 30-80 (phone) -- counted from real line boxes, not estimated
    air        share of the desktop page that is background, scored against 0.6 (the void)
    accent     share of accent pixels in 0.3%-4% -- one hot colour, used sparingly
    rhythm     distinct grid signatures across sections / sections

J components are kept at 0.01. Measured on gm: the air share alone moved 0.733 -> 0.795 when only the
screenshot's downscale changed (180 -> 1440 px wide), while a genome step moved it 0.0015-0.003. A
difference below 0.01 is not resolved by this judge, so it is not counted as an improvement (nor as a
regression) -- the first run of this loop ACCEPTed exactly such a sub-resolution gain.

Also returned: `content`, a hash of all visible text outside [data-meta]. Two pages with different
content are not two tellings of one room; the policy refuses to compare them.
"""
from __future__ import annotations

import hashlib
import io
import math
from pathlib import Path

from gentle_monster import paths
from gentle_monster.engine import color as C

WIDTHS = (375, 1440)
MAX_BYTES = 1_500_000

_JS_TEXT = r"""() => {
 const P = s => { const m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return null;
   const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
 const over = (t, b) => { const a = t[3]; return [t[0]*a + b[0]*(1-a), t[1]*a + b[1]*(1-a), t[2]*a + b[2]*(1-a), 1]; };
 const lum = c => { const f = v => { v /= 255; return v <= 0.04045 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };
   return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2]); };
 const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05); };
 const out = {items: [], unmeasured: [], sizes: {}, body: {}, paras: [], content: [], cut: []};
 const meta = el => el.closest('[data-meta]');
 for (const el of document.body.querySelectorAll('*')) {
   if (['SCRIPT','STYLE','svg','SVG'].includes(el.tagName) || el.closest('svg')) continue;
   const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').replace(/\s+/g, ' ').trim();
   if (!own) continue;
   const cs = getComputedStyle(el), r = el.getBoundingClientRect();
   if (r.width === 0 || r.height === 0 || cs.visibility === 'hidden') continue;
   if (!meta(el)) out.content.push(own);
   if (r.right > innerWidth + 1 || (r.left < -1 && !el.matches('.skip'))) out.cut.push({text: own.slice(0, 40), left: Math.round(r.left), right: Math.round(r.right)});
   const fs = parseFloat(cs.fontSize), fw = parseInt(cs.fontWeight) || 400;
   out.sizes[Math.round(fs)] = (out.sizes[Math.round(fs)] || 0) + own.length;
   if (el.tagName === 'P' && !meta(el)) out.body[Math.round(fs)] = (out.body[Math.round(fs)] || 0) + own.length;
   // background: composite ancestors until opaque; an image/gradient on the way cannot be measured
   const layers = []; let bad = null;
   for (let a = el; a; a = a.parentElement) {
     const s = getComputedStyle(a);
     const bg = P(s.backgroundColor);
     if (bg && bg[3] > 0) layers.push(bg);
     if (bg && bg[3] >= 1) break;
     if (s.backgroundImage !== 'none') { bad = a.tagName.toLowerCase() + '.' + a.className; break; }
   }
   if (bad) { out.unmeasured.push({text: own.slice(0, 40), on: bad}); continue; }
   let bg = [255, 255, 255, 1];
   for (const l of layers.reverse()) bg = over(l, bg);
   let fg = P(cs.color);
   const sw = parseFloat(cs.webkitTextStrokeWidth || '0');
   if ((!fg || fg[3] === 0) && sw > 0) fg = P(cs.webkitTextStrokeColor);
   if (!fg) { out.unmeasured.push({text: own.slice(0, 40), on: 'colour ' + cs.color}); continue; }
   let op = 1; for (let a = el; a; a = a.parentElement) op *= parseFloat(getComputedStyle(a).opacity);
   fg = over([fg[0], fg[1], fg[2], fg[3] * op], bg);
   const large = fs >= 24 || (fs >= 18.66 && fw >= 700);
   out.items.push({text: own.slice(0, 40), ratio: Math.round(ratio(fg, bg) * 100) / 100, need: large ? 3 : 4.5, fs});
   if (el.tagName === 'P' && own.length >= 80) {
     const rg = document.createRange(); rg.selectNodeContents(el);
     const tops = new Set([...rg.getClientRects()].map(q => Math.round(q.top)));
     out.paras.push({chars: own.length, lines: tops.size});
   }
 }
 return out;
}"""

_JS_DOC = r"""() => {
 const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => +h.tagName[1]);
 let skip = 0; for (let i = 1; i < hs.length; i++) if (hs[i] > hs[i-1] + 1) skip++;
 const unnamed = [...document.querySelectorAll('img:not([alt]), svg[role=img]:not([aria-label]), canvas:not([aria-label]):not([aria-hidden=true])')].length;
 const sig = [...document.querySelectorAll('main > section, header, footer')].map(s => {
   const g = [s, ...s.querySelectorAll(':scope > *, :scope > * > *')].find(x => getComputedStyle(x).display === 'grid');
   return g ? getComputedStyle(g).gridTemplateColumns.split(' ').length + ':' + g.className : 'flow'; });
 return {lang: document.documentElement.lang || '', h1: document.querySelectorAll('h1').length, skip, unnamed,
         overflow: document.documentElement.scrollWidth - window.innerWidth,
         sections: sig.length, distinct: new Set(sig).size,
         running: document.getAnimations().filter(a => a.playState === 'running').length};
}"""


def _pixels(png: bytes, bg: str, accent: str) -> "tuple[float, float]":
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(float)    # full resolution: no resampling blend
    d = lambda h: np.sqrt(((a - np.array(C.rgb(h))) ** 2).sum(-1))
    return float((d(bg) < 10).mean()), float((d(accent) < 40).mean())


def static(t: dict) -> dict:
    """Contrast from the token pairs (route two). Text pairs only; the accent fill is decoration."""
    c = t["color"]
    pairs = {"ink/bg": (c["ink"], c["bg"], 7), "sub/bg": (c["sub"], c["bg"], 4.5), "accent-text/bg": (c["accent-text"], c["bg"], 4.5),
             "on-accent/accent": (c["on-accent"], c["accent"], 4.5)}
    got = {k: C.contrast(a, b) for k, (a, b, _) in pairs.items()}
    return {"pairs": got, "fail": [f"{k} {got[k]} < {n}" for k, (_, _, n) in pairs.items() if got[k] < n]}


def _band(x, lo, hi) -> float:
    if lo <= x <= hi:
        return 1.0
    return max(0.0, 1 - abs(math.log((x if x > 0 else 1e-6) / (lo if x < lo else hi))) / math.log(4))


def measure(html_path, t: dict) -> dict:
    """V and J of one page. Opens it 3 times: 375 px reduced-motion, 1440 px reduced-motion, 1440 px with motion."""
    from playwright.sync_api import sync_playwright
    html_path = Path(html_path)
    v, raw, ext, errs = {}, {}, [], []
    with sync_playwright() as p:
        b = paths.launch(p, gl=False)
        for w, motion in ((375, "reduce"), (1440, "reduce"), (1440, "no-preference")):
            ctx = b.new_context(viewport={"width": w, "height": 900}, reduced_motion=motion)
            ctx.route(lambda u: not u.startswith(("file:", "data:")), lambda r: (ext.append(r.request.url), r.abort()))
            pg = ctx.new_page()
            pg.on("pageerror", lambda e_: errs.append(str(e_)))
            pg.goto(html_path.as_uri(), wait_until="load")
            pg.wait_for_timeout(150)
            key = f"{w}-{motion}"
            raw[key] = {"doc": pg.evaluate(_JS_DOC)}
            if motion == "reduce":
                raw[key]["text"] = pg.evaluate(_JS_TEXT)
                if w == 1440:
                    raw[key]["px"] = _pixels(pg.screenshot(full_page=True), t["color"]["bg"], t["color"]["accent"])
            ctx.close()
        b.close()
    m, d = raw["375-reduce"], raw["1440-reduce"]
    items = m["text"]["items"] + d["text"]["items"]
    low = sorted((x for x in items if x["ratio"] < x["need"]), key=lambda x: x["ratio"])
    unm = m["text"]["unmeasured"] + d["text"]["unmeasured"]
    st = static(t)
    # scrollWidth alone is blind to overflow that a container clips -- the text is still cut off. So both:
    # the document does not scroll sideways AND no text box reaches outside the viewport.
    v["overflow-375"] = m["doc"]["overflow"] <= 1 and not m["text"]["cut"]
    v["overflow-1440"] = d["doc"]["overflow"] <= 1 and not d["text"]["cut"]
    v["contrast-rendered"] = bool(items) and not low and not unm
    v["contrast-tokens"] = not st["fail"]
    v["min-font-375"] = bool(m["text"]["sizes"]) and min(float(k) for k in m["text"]["sizes"]) >= 12
    v["offline"] = not ext
    v["js-errors"] = not errs
    v["names"] = d["doc"]["unnamed"] == 0
    v["headings"] = d["doc"]["lang"] != "" and d["doc"]["h1"] == 1 and d["doc"]["skip"] == 0
    v["reduced-motion"] = m["doc"]["running"] == 0 and d["doc"]["running"] == 0
    v["weight"] = html_path.stat().st_size <= MAX_BYTES

    sizes = {int(k): n for k, n in d["text"]["sizes"].items()}
    bodies = {int(k): n for k, n in d["text"]["body"].items()}
    body = max(bodies, key=bodies.get) if bodies else 16          # running text = the size of most paragraph characters
    big = max(sizes) if sizes else 16
    cpl = lambda paras, lo: [lo <= p["chars"] / max(1, p["lines"]) <= 80 for p in paras if p["lines"] > 1]
    ms = cpl(d["text"]["paras"], 40) + cpl(m["text"]["paras"], 30)
    air, acc = d["px"]
    j = {"drama": _band(big / body, 6, 14),
         "hierarchy": _band(len(sizes), 4, 8),
         "measure": sum(ms) / len(ms) if ms else 0.0,
         "air": max(0.0, 1 - abs(air - .6) / .6),
         "accent": _band(acc, .003, .04),
         "rhythm": d["doc"]["distinct"] / max(1, d["doc"]["sections"])}
    j = {k: round(x, 2) for k, x in j.items()}                     # the judge's resolution (see above)
    content = hashlib.sha1("\n".join(sorted(d["text"]["content"])).encode()).hexdigest()[:16]
    return {"V": v, "J": j, "score": round(sum(j.values()) / len(j), 4), "content": content,
            "facts": {"min-contrast": min((x["ratio"] for x in items), default=None), "low-contrast": low[:6], "unmeasured": unm[:6],
                      "tokens": st["pairs"], "external": ext[:6], "errors": [x[:200] for x in errs[:3]],
                      "body-px": body, "largest-px": big, "sizes": sorted(sizes), "air": round(air, 3), "accent-share": round(acc, 4),
                      "overflow": {"375": m["doc"]["overflow"], "1440": d["doc"]["overflow"]}, "cut-text": (m["text"]["cut"] + d["text"]["cut"])[:6],
                      "running-with-motion": raw["1440-no-preference"]["doc"]["running"], "bytes": html_path.stat().st_size}}
