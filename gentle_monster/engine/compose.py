"""Tokens + job -> one self-contained page (HTML, inline CSS, no network). The page is the room:

    threshold   the door. Two jambs part as you scroll in; the brand is the masthead       (header, h1)
    synopsis    what the room is, in the job's own words                                  (section)
    the walk    scroll = walking. The plan is drawn from job.layout; the circulation line
                is drawn as you scroll (scroll-driven animation), and the three stops are
                the three scenes beside it                                                  (section)
    matter      the four material presets as procedural surfaces + the palette             (section)
    intent      why the layout is what it is                                               (section)
    colophon    how this page was made: genome, tokens, where the verdict is                (footer, data-meta)

Rules this file keeps so the judge can measure honestly:
  * text sits on solid token colours only, never on images or gradients (a text node over a picture is
    the one place the contrast judge cannot measure -- so the composer never puts one there);
  * every moving thing is inside `prefers-reduced-motion: no-preference`; `still` emits no animation CSS;
  * content (all text outside [data-meta]) does not depend on the genome -- a candidate page can only
    change how the room is told, never what is told. The judge checks this (content invariance).
"""
from __future__ import annotations

import html

from gentle_monster.engine import tokens as T

e = lambda s: html.escape(str(s))


def _span(cols: int, frac: float, tension: int) -> str:
    span = max(2, round(cols * frac))
    start = 1 + tension * max(1, cols // 6)
    start = min(start, cols - span + 1)
    return f"{start} / span {span}"


def plan_svg(job: dict) -> str:
    """The plan in metres (viewBox = the envelope). Street edge (y = 0) at the bottom, as you walk in."""
    L = job["layout"]
    W, D = L["W"], L["D"]
    Y = lambda y: D - y
    out = [f'<rect class="env" x="0" y="0" width="{W}" height="{D}"/>']
    for it in L["items"]:
        x0, x1, y0, y1 = it["x0"], it["x1"], it["y0"], it["y1"]
        s, t = it.get("shape", "box"), it.get("type")
        if t == "door" or s == "door":
            out.append(f'<rect class="p-door" x="{x0}" y="{Y(y1)}" width="{x1 - x0}" height="{max(.15, y1 - y0)}"/>')
            continue
        cls = "zone" if (t == "zone" or s in ("zone", "shards", "light_ceiling", "floor_patch")) else ("hero" if it.get("hero") else "solid")
        if s == "basin":
            r = min(x1 - x0, y1 - y0) / 2
            out.append(f'<circle class="{cls}" cx="{(x0 + x1) / 2}" cy="{Y((y0 + y1) / 2)}" r="{r}"/>')
        else:
            out.append(f'<rect class="{cls}" x="{x0}" y="{Y(y1)}" width="{x1 - x0}" height="{y1 - y0}"/>')
    for c in L.get("columns", []):
        out.append(f'<rect class="solid" x="{c[0] - .2}" y="{Y(c[1] + .2)}" width=".4" height=".4"/>')
    pts = " ".join(f"{x},{Y(y)}" for x, y in L["flows"][0]["pts"])
    out.append(f'<polyline class="route" pathLength="1" points="{pts}"/>')
    for i, s in enumerate(job["stops"]):
        x, y = s["at"]
        out.append(f'<circle class="stop-dot" cx="{x}" cy="{Y(y)}" r=".42"/><circle class="stop-ring" cx="{x}" cy="{Y(y)}" r=".8"/>')
    label = (f"Plan of {job['title']}, {W} by {D} metres. The circulation runs from the door on the street edge "
             f"past {len(job['stops'])} stops and back.")
    return (f'<svg class="plan-svg" role="img" aria-label="{e(label)}" viewBox="-0.5 -0.5 {W + 1} {D + 1}" '
            f'preserveAspectRatio="xMidYMid meet">{"".join(out)}</svg>')


def _css(t: dict) -> str:
    g, cols = t["genome"], t["grid"]["cols"]
    syn = _span(cols, .6, g["tension"])
    mast = {
        "stencil": ".mast::after{content:\"\";position:absolute;inset:0;pointer-events:none;"
                   "background:repeating-linear-gradient(90deg,transparent 0 .94em,var(--bg) .94em 1em),"
                   "repeating-linear-gradient(0deg,transparent 0 .46em,var(--bg) .46em .5em)}",
        "solid": "",
        "outline": ".mast{color:transparent;-webkit-text-stroke:max(1.5px,.012em) var(--ink)}",
        "split": ".mast .w:nth-child(even){color:var(--accent-text)}",
    }[g["mast"]]
    base = f"""{T.css_vars(t)}
*,*::before,*::after{{box-sizing:border-box}}
html{{background:var(--bg);color:var(--ink);-webkit-text-size-adjust:100%;scroll-behavior:auto}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);font-size:var(--step-0);line-height:1.6}}
a{{color:var(--accent-text)}} a:focus-visible{{outline:2px solid var(--accent-text);outline-offset:3px}}
.skip{{position:absolute;left:var(--space-2);top:-10rem;background:var(--accent);color:var(--on-accent);padding:var(--space-1) var(--space-2);z-index:9;font-family:var(--font-display)}}
.skip:focus{{top:var(--space-2)}}
.label,.kicker,.cue,.at,figcaption,.colophon{{font-family:var(--font-display);font-size:var(--step-m1);letter-spacing:.14em;text-transform:uppercase;color:var(--sub);font-weight:500}}
.label{{margin:0 0 var(--space-4)}}
h1,h2,h3{{font-family:var(--font-display);font-weight:700;letter-spacing:-.02em;line-height:1.05}}
section,footer{{padding:var(--space-6) var(--space-3)}}
.threshold{{position:relative;min-height:96svh;display:flex;flex-direction:column;justify-content:flex-end;gap:var(--space-3);padding:var(--space-5) var(--space-3) var(--space-5);overflow:clip}}
.door{{position:absolute;inset:0;pointer-events:none}}
.jamb{{position:absolute;top:0;bottom:0;width:22vw;background:var(--surface)}} .jamb.l{{left:0}} .jamb.r{{right:0}}
.jamb i{{position:absolute;inset:0;background:var(--line);opacity:.35;transform-origin:50% 100%}}
.eye{{position:absolute;left:50%;top:22%;width:var(--space-2);height:var(--space-2);margin-left:calc(var(--space-2) / -2);border-radius:50%;background:var(--accent)}}
.shard{{position:absolute;width:1.2vw;min-width:6px;aspect-ratio:1/2.6;background:var(--line);opacity:.5;clip-path:polygon(50% 0,100% 30%,70% 100%,0 70%)}}
.kicker,.mast,.meta,.cue{{position:relative}}
.kicker{{margin:0}}
.mast{{margin:0;font-family:var(--font-display);font-size:var(--mast);line-height:.8;letter-spacing:-.045em;text-transform:uppercase;font-weight:800;word-break:keep-all;overflow-wrap:normal;max-width:100%}}
.mast .w{{display:inline-block;margin-right:.18em}}
.meta{{display:grid;gap:var(--space-3)}}
.title{{margin:0;font-family:var(--font-display);font-size:var(--step-2);font-weight:700;line-height:1.1}} .title em{{display:block;font-weight:400;font-size:var(--step-0);color:var(--sub);margin-top:var(--space-1)}}
.line{{margin:0;max-width:34em;font-size:var(--step-1);line-height:1.45}}
.cue{{margin:0}}
.grid{{display:grid;grid-template-columns:minmax(0,1fr);column-gap:var(--space-3)}}
.syn{{font-size:var(--step-1);line-height:1.55;margin:0 0 var(--space-4);max-width:36em}}
.kw{{list-style:none;padding:0;margin:0 0 var(--space-4);display:flex;flex-wrap:wrap;gap:var(--space-1)}}
.kw li{{border:1px solid var(--ink);border-radius:999px;padding:.2em .9em;font-family:var(--font-display);font-size:var(--step-m1)}}
.quote{{margin:0;font-family:var(--font-display);font-size:var(--step-3);line-height:1.12;letter-spacing:-.02em;color:var(--accent-text);max-width:18em;font-weight:600}}
.walk-in{{display:grid;gap:var(--space-5)}}
.plan{{margin:0}} .plan-svg{{display:block;width:100%;height:auto;max-height:78svh}}
.plan figcaption{{margin-top:var(--space-2);letter-spacing:.06em;text-transform:none;line-height:1.5}}
.env{{fill:var(--bg);stroke:var(--ink);stroke-width:.1}} .solid{{fill:var(--plan-solid)}} .hero{{fill:var(--accent)}}
.zone{{fill:var(--plan-zone);stroke:var(--line);stroke-width:.05;stroke-dasharray:.25 .2}} .p-door{{fill:var(--accent)}}
.route{{fill:none;stroke:var(--accent);stroke-width:.14;stroke-linejoin:round;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:0}}
.stop-dot{{fill:var(--accent)}} .stop-ring{{fill:none;stroke:var(--accent);stroke-width:.06}}
.stops{{list-style:none;margin:0;padding:0;display:grid;gap:var(--space-6)}}
.stop .no{{display:block;font-family:var(--font-mono);font-size:var(--step-0);color:var(--accent-text);margin-bottom:var(--space-1)}}
.stop h3{{font-size:var(--step-3);margin:0 0 var(--space-2);max-width:14em}} .stop p{{margin:0;max-width:30em}}
.stop .at{{margin-top:var(--space-2);letter-spacing:.08em}}
.mats{{list-style:none;padding:0;margin:0 0 var(--space-5);display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--space-3)}}
.mats canvas{{display:block;width:100%;height:auto;aspect-ratio:1}} .mats h3{{font-size:var(--step-0);margin:var(--space-1) 0 0}} .mats p{{margin:0;color:var(--sub);font-size:var(--step-m1)}}
.swatches{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:var(--space-1)}}
.swatches i{{display:block;aspect-ratio:3/4;border:1px solid var(--line)}} .swatches b{{display:block;font-family:var(--font-mono);font-size:var(--step-m1);font-weight:400;margin-top:var(--space-1)}}
.swatches span{{display:block;color:var(--sub);font-size:var(--step-m1);line-height:1.35}}
.why{{list-style:none;padding:0;margin:0;display:grid;gap:var(--space-4);counter-reset:w}}
.why li{{counter-increment:w;max-width:32em}} .why h3{{font-size:var(--step-2);margin:0 0 var(--space-1)}} .why h3::before{{content:counter(w,decimal-leading-zero) "  ";color:var(--accent-text);font-family:var(--font-mono);font-weight:400}}
.why p{{margin:0;color:var(--sub)}}
.colophon{{border-top:1px solid var(--line);letter-spacing:.06em;text-transform:none;line-height:1.6}} .colophon p{{margin:0 0 var(--space-1);max-width:34em}}
@media (min-width:900px){{
 section,footer{{padding:var(--space-7) var(--space-5)}}
 .threshold{{padding:var(--space-5)}}
 .grid{{grid-template-columns:repeat({cols},minmax(0,1fr))}}
 .meta{{grid-template-columns:minmax(0,1fr) minmax(0,1.3fr);align-items:end}}
 .manifesto>*{{grid-column:{syn}}}
 .walk-in{{grid-template-columns:minmax(0,5fr) minmax(0,4fr);align-items:start}}
 .plan{{position:sticky;top:var(--space-4)}}
 .stops{{padding:20svh 0 30svh;gap:45svh}}
 .mats{{grid-template-columns:repeat(4,minmax(0,1fr))}}
 .why{{grid-template-columns:repeat(2,minmax(0,1fr));column-gap:var(--space-5)}} .why li:nth-child(even){{margin-top:var(--space-6)}}
}}
{mast}
"""
    if t["motion"]["kind"] == "still":
        return base
    drift = (".shard{animation:drift calc(var(--breath) * 1.7) ease-in-out infinite alternate}"
             ".shard:nth-child(odd){animation-duration:calc(var(--breath) * 2.3)}"
             "@keyframes drift{to{translate:0 -4vh;rotate:24deg}}") if t["motion"]["kind"] == "drift" else ""
    return base + f"""
@media (prefers-reduced-motion:no-preference){{
 .jamb i{{animation:breathe var(--breath) ease-in-out infinite alternate}}
 .jamb.r i{{animation-delay:calc(var(--breath) / -2)}}
 @keyframes breathe{{from{{scale:1 .92}}to{{scale:1 1}}}}
 {drift}
 @supports (animation-timeline:view()){{
  .jamb.l{{animation:part-l linear both;animation-timeline:scroll(root);animation-range:0 70svh}}
  .jamb.r{{animation:part-r linear both;animation-timeline:scroll(root);animation-range:0 70svh}}
  @keyframes part-l{{to{{translate:-22vw 0}}}} @keyframes part-r{{to{{translate:22vw 0}}}}
  .reveal{{animation:rise linear both;animation-timeline:view();animation-range:entry 0% cover 30%}}
  @keyframes rise{{from{{opacity:.2;translate:0 calc(var(--space-5))}}to{{opacity:1;translate:0 0}}}}
  .walk{{view-timeline-name:--walk}}
  .route{{animation:draw linear both;animation-timeline:--walk;animation-range:contain 0% contain 100%}}
  @keyframes draw{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
 }}
}}"""


def _walk(job) -> str:
    L = job["layout"]
    stops = "".join(f'<li class="stop reveal"><span class="no">{i + 1:02d}</span><h3>{e(s["cap"])}</h3><p>{e(s["sub"])}</p>'
                    f'<p class="at">x {s["at"][0]:.1f} m · y {s["at"][1]:.1f} m · eye {s.get("h", 1.6):.2f} m</p></li>'
                    for i, s in enumerate(job["stops"]))
    return (f'<section class="walk" id="walk" aria-labelledby="h-walk"><h2 id="h-walk" class="label">The walk · three moments</h2>'
            f'<div class="walk-in"><figure class="plan">{plan_svg(job)}<figcaption>Plan, {L["W"]} × {L["D"]} m, ceiling {L["H"]} m. '
            f'The line is the circulation, checked by code to keep at least 0.3 m from every object. Dimensions assumed, not surveyed.'
            f'</figcaption></figure><ol class="stops">{stops}</ol></div></section>')


def _matter(job) -> str:
    mats = "".join(f'<li><canvas data-tex="{e(m.get("preset") or "concrete")}" width="320" height="320" role="img" '
                   f'aria-label="generated texture for {e(m["name"])}"></canvas><h3>{e(m["name"])}</h3><p>{e(m["where"])}</p></li>'
                   for m in job["materials"])
    sw = "".join(f'<li><i style="background:{e(p["hex"])}"></i><b>{e(p["hex"].upper())}</b><span>{e(p.get("name", ""))}</span></li>'
                 for p in job["palette"])
    return (f'<section class="matter" aria-labelledby="h-mat"><h2 id="h-mat" class="label">Matter · four surfaces, five colours</h2>'
            f'<ul class="mats">{mats}</ul><ul class="swatches" aria-label="palette">{sw}</ul></section>')


def _intent(job) -> str:
    why = "".join(f'<li class="reveal"><h3>{e(w["t"])}</h3><p>{e(w["d"])}</p></li>' for w in job["why"])
    return f'<section class="intent" aria-labelledby="h-int"><h2 id="h-int" class="label">Design intent</h2><ol class="why">{why}</ol></section>'


ORDERS = {"walk-first": ("walk", "matter", "intent"), "matter-first": ("matter", "walk", "intent"),
          "intent-first": ("intent", "walk", "matter")}


def page(job: dict, t: dict) -> str:
    from gentle_monster import documents as D
    g = t["genome"]
    brand = job["brand"]
    words = "".join(f'<span class="w">{e(w)}</span>' for w in brand.split())
    shards = "".join(f'<span class="shard" style="left:{18 + (i * 37) % 64}%;top:{12 + (i * 23) % 60}%"></span>' for i in range(7)) if g["motion"] == "drift" else ""
    L = job["layout"]
    blocks = {"walk": _walk(job), "matter": _matter(job), "intent": _intent(job)}
    kw = "".join(f"<li>{e(k)}</li>" for k in job["keywords"])
    gen = " · ".join(f"{k} {v}" for k, v in g.items())
    return f"""<!doctype html><html lang="en" data-theme="{t['theme']}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="{'dark' if t['theme'] == 'dark' else 'light'}">
<title>{e(brand)} — {e(job['title'])}</title><meta name="description" content="{e(job['line'])}">
<style>{_css(t)}</style></head><body>
<a class="skip" href="#walk">Skip to the walk</a>
<header class="threshold">
 <div class="door" aria-hidden="true"><span class="jamb l"><i></i></span><span class="jamb r"><i></i></span><span class="eye"></span>{shards}</div>
 <p class="kicker">{e(brand)} · spatial synopsis</p>
 <h1 class="mast">{words}</h1>
 <div class="meta"><p class="title">{e(job['title'])}<em>{e(job.get('subtitle', ''))}</em></p><p class="line">{e(job['line'])}</p></div>
 <p class="cue">Scroll to walk in · {L['W']} × {L['D']} m</p>
</header>
<main>
<section class="manifesto grid" aria-labelledby="h-syn"><h2 id="h-syn" class="label">Synopsis</h2>
 <p class="syn reveal">{e(job['synopsis'])}</p><ul class="kw" aria-label="keywords">{kw}</ul><blockquote class="quote reveal">{e(job['quote'])}</blockquote></section>
{''.join(blocks[k] for k in ORDERS[g['order']])}
</main>
<footer class="colophon" data-meta>
 <p>How this page was made. gentle_monster frontend engine: the job's palette, light and materials became design tokens (tokens.json),
 the tokens became this page, and a browser judge measured it at 375 px and 1440 px before it was accepted (report.json).</p>
 <p>Genome: {e(gen)}.</p>
 <p>Material swatches are generated textures, not photographs. No fonts, images or scripts are fetched from the network.</p>
</footer>
{D._TEX_JS}</body></html>"""
