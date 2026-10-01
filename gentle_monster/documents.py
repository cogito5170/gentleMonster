"""Printed outputs: the plan (render3d), the one-page magazine layout PDF (default) and the A3
blueprint sheet PDF (on request). English only, small type -- the user's standing request for
these pages. Printing runs offline: every non-file request is aborted, so a missing font can
never hang a render (it fell back to local fonts in the build container)."""
from __future__ import annotations

import html
import json
from pathlib import Path

from gentle_monster import paths

AREA_EN = {"통로(잔여)": "Circulation", "코어(계단·EV)": "Core", "BOH": "Back of house", "카페": "Cafe", "결제·서비스": "Pay + service",
           "판매 집기": "Retail fixtures", "O2O": "O2O", "체험·포토": "Experience"}
FONT = '"Archivo","Liberation Sans","Helvetica Neue",Arial,sans-serif'
e = lambda s: html.escape(str(s))


def plan(job: dict, out_png) -> "tuple[str, dict]":
    """render3d plan (grid, dimensions, entrance, circulation) + area programme in English. Sum == W x D is asserted."""
    from render3d import layout as LY, plan as PL
    L = job["layout"]
    sc = LY.to_scene(dict(L, name=f"{job['brand']} — {job['title']}"))
    png = PL.render(sc, out_png, scale="approx. 1:100")
    a = {AREA_EN.get(k, k): v for k, v in LY.area_program(sc).items() if v > 0}
    tot = sum(a.values())
    assert abs(tot - L["W"] * L["D"]) < .5, f"area programme {tot} != W x D {L['W'] * L['D']}"
    return png, a


def palette_from_photos(photos, n: int = 3) -> "list[dict]":
    """Dominant colours of the applicant's photos (6-colour median cut per photo, largest share first)."""
    from PIL import Image
    out = []
    for p in photos:
        im = Image.open(p).convert("RGB"); im.thumbnail((200, 200))
        q = im.quantize(colors=6, method=Image.Quantize.MEDIANCUT); pal = q.getpalette()
        for cnt, idx in sorted(q.getcolors(), reverse=True)[:2]:
            r, g, b = pal[idx * 3:idx * 3 + 3]
            out.append({"hex": "#%02x%02x%02x" % (r, g, b), "name": f"from {Path(p).name}"})
    return out[:n]


def _print(html_path: Path, pdf_path: Path, width: str, height: str, shot=None) -> str:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = paths.launch(p, gl=False)
        ctx = b.new_context(viewport={"width": 1200, "height": 1600})
        ctx.route(lambda u: not u.startswith("file:"), lambda r: r.abort())
        pg = ctx.new_page()
        pg.goto(html_path.as_uri(), wait_until="load")
        pg.wait_for_timeout(300)
        pg.pdf(path=str(pdf_path), print_background=True, width=width, height=height, prefer_css_page_size=True)
        if shot:
            pg.screenshot(path=str(shot), full_page=True)
        b.close()
    return str(pdf_path)


_TEX_JS = r"""<script>
(function(){function R(s){return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296}}
function N(c,w,h,r,b,a,n,z){c.fillStyle=b;c.fillRect(0,0,w,h);for(let i=0;i<n;i++){const v=(r()-.5)*a;c.fillStyle=v>0?`rgba(255,255,255,${v})`:`rgba(0,0,0,${-v})`;const s=z*(.5+r());c.fillRect(r()*w,r()*h,s,s)}}
function Bx(c,w,h,r,b,a){c.fillStyle=b;c.fillRect(0,0,w,h);for(let y=0;y<h;y++){const v=(r()-.5)*a;c.fillStyle=v>0?`rgba(255,255,255,${v})`:`rgba(0,0,0,${-v})`;c.fillRect(0,y,w,1)}}
const T={concrete:(c,w,h,r)=>N(c,w,h,r,'#8a8d8b',.18,w*h*.18,2),polished_concrete:(c,w,h,r)=>N(c,w,h,r,'#6d6f6d',.1,w*h*.12,2),granite:(c,w,h,r)=>N(c,w,h,r,'#5a5a5a',.5,w*h*.3,2.2),
steel:(c,w,h,r)=>Bx(c,w,h,r,'#8f9ea3',.16),mirror_aluminium:(c,w,h,r)=>Bx(c,w,h,r,'#d4d8dc',.1),aluminium:(c,w,h,r)=>Bx(c,w,h,r,'#c9cdd1',.12),brass:(c,w,h,r)=>Bx(c,w,h,r,'#b08d57',.12),
red_wax:(c,w,h,r)=>N(c,w,h,r,'#6e1414',.2,w*h*.05,6),graphite_wax:(c,w,h,r)=>{N(c,w,h,r,'#2e2b28',.35,w*h*.28,1.6);for(let i=0;i<14;i++){c.fillStyle='rgba(150,25,20,.8)';c.beginPath();c.ellipse(r()*w,r()*h,3+r()*8,2+r()*4,0,0,7);c.fill()}},
mineral_white:(c,w,h,r)=>N(c,w,h,r,'#f1efea',.05,w*h*.1,2),strata_clay:(c,w,h,r)=>{let y=0;const k=['#9a4a32','#b86a4a','#7b5a40','#c89a72','#8a3f2b','#6d5237'];while(y<h){const t=3+r()*10;c.fillStyle=k[(r()*k.length)|0];c.fillRect(0,y,w,t);y+=t}},
lime_plaster:(c,w,h,r)=>N(c,w,h,r,'#e4dfd4',.07,w*h*.12,3),wood:(c,w,h,r)=>{c.fillStyle='#6b4a32';c.fillRect(0,0,w,h);for(let x=0;x<w;x+=2){c.fillStyle=`rgba(40,25,10,${.1+r()*.25})`;c.fillRect(x,0,1,h)}},
amber_glass:(c,w,h,r)=>{c.fillStyle='#2a1a0e';c.fillRect(0,0,w,h);for(let i=0;i<5;i++){const g=c.createLinearGradient(i*w/5,0,(i+1)*w/5,0);g.addColorStop(0,'#4a2a10');g.addColorStop(.3,'#a8621f');g.addColorStop(1,'#3a200c');c.fillStyle=g;c.fillRect(i*w/5+2,h*.15,w/5-4,h)}},
glass:(c,w,h,r)=>{c.fillStyle='#1d2427';c.fillRect(0,0,w,h);for(let i=0;i<16;i++){c.beginPath();const x=r()*w,y=r()*h;c.moveTo(x,y);for(let k=0;k<3;k++)c.lineTo(x+(r()-.5)*w*.3,y+(r()-.5)*h*.3);c.closePath();c.fillStyle=`rgba(200,225,255,${.12+r()*.3})`;c.fill()}},
skin:(c,w,h,r)=>N(c,w,h,r,'#cfa591',.05,w*h*.05,2),textile_light:(c,w,h,r)=>{c.fillStyle='#fff7e6';c.fillRect(0,0,w,h);for(let x=0;x<w;x+=3){c.fillStyle='rgba(190,170,130,.12)';c.fillRect(x,0,1,h)}},
black_stone:(c,w,h,r)=>N(c,w,h,r,'#161616',.08,w*h*.06,2),white_gloss:(c,w,h,r)=>N(c,w,h,r,'#f1f0ec',.03,w*h*.04,2),candle_wax:(c,w,h,r)=>N(c,w,h,r,'#efe6cf',.05,w*h*.06,3)};
document.querySelectorAll('canvas[data-tex]').forEach((cv,i)=>{const f=T[cv.dataset.tex]||T.concrete;f(cv.getContext('2d'),cv.width,cv.height,R(97+i*131))});})();
</script>"""


def _materials_for(job) -> "list[tuple[str, str, str]]":
    """(name, where, preset). The swatch is drawn from the declared preset, never guessed from the name."""
    return [(m["name"], m["where"], m.get("preset") or "concrete") for m in job["materials"]]


def layout_pdf(job: dict, out_dir, photos=()) -> "dict[str, str]":
    """<default step> One A3-portrait magazine page: masthead, hero, synopsis, palette, materials, intent, sequence, plan."""
    out_dir = Path(out_dir)
    plan_png, area = plan(job, out_dir / "plan.png")
    missing = [str(p) for p in photos if not Path(p).is_file()]
    photos = [str(Path(p)) for p in photos if Path(p).is_file()][:5]
    pal = job["palette"]
    if photos:
        pal = (palette_from_photos(photos, 3) + list(job["palette"]))[:5]
    rel = lambda p: Path(p).resolve().as_uri()
    sw = "".join(f'<div><i style="background:{e(p["hex"])}"></i><b>{e(p["hex"].upper())}</b><span>{e(p.get("name", ""))}</span></div>' for p in pal)
    mats = "".join(f'<div><canvas data-tex="{e(k)}" width="160" height="160"></canvas><b>{e(n)}</b><span>{e(w)}</span></div>' for n, w, k in _materials_for(job))
    why = "".join(f'<li><b>{e(w["t"])}.</b> {e(w["d"])}</li>' for w in job["why"])
    seq = "".join(f'<li><b>{e(s["cap"])}</b> {e(s["sub"])}</li>' for s in job["stops"])
    kw = "".join(f"<span>{e(k)}</span>" for k in job["keywords"])
    W, D, H = job["layout"]["W"], job["layout"]["D"], job["layout"]["H"]
    area_rows = "".join(f'<tr><td>{e(k)}</td><td>{v:.1f} m²</td></tr>' for k, v in area.items()) + f'<tr><td><b>Total</b></td><td><b>{W * D:.0f} m²</b></td></tr>'
    hero = f'<img class="hi" src="{rel(photos[0])}" alt="">' if photos else f'<img class="hi plan" src="{rel(plan_png)}" alt="plan">'
    low = (f'<div class="box"><p class="cap">Plan · circulation</p><img class="lp" src="{rel(plan_png)}" alt="plan"></div>' if photos else "")
    strip = "".join(f'<img src="{rel(p)}" alt="">' for p in photos[1:])
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(job['title'])}</title><style>
@page{{size:297mm 420mm;margin:0}}
*{{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
html,body{{margin:0;background:#fbfbf9;color:#111;font-family:{FONT}}}
.pg{{width:297mm;height:420mm;padding:11mm;display:grid;grid-template-rows:auto minmax(0,1fr) auto auto;gap:5mm;overflow:hidden;--a:{e(job['accent'])}}}
.cap{{text-transform:uppercase;letter-spacing:.14em;font-size:5.8pt;margin:0 0 2mm}} .s{{font-size:6.6pt;line-height:1.5}} .xs{{font-size:5.6pt;line-height:1.45;color:#66665f}}
.top{{display:grid;grid-template-columns:1fr 70mm;gap:6mm;align-items:end;border-bottom:.5pt solid #111;padding-bottom:3mm}}
.mast{{position:relative;margin:0;font-weight:700;font-size:{max(16, min(40, 300 // max(6, len(job['brand']))))}mm;line-height:.8;letter-spacing:-.045em;text-transform:uppercase}}
.mast::after{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 24mm,#fbfbf9 24mm 25.4mm),repeating-linear-gradient(0deg,transparent 0 12mm,#fbfbf9 12mm 13.2mm)}}
.hero{{display:grid;grid-template-columns:1fr 72mm;gap:6mm;min-height:0}}
.hi{{width:100%;height:100%;min-height:0;object-fit:cover;display:block}} .hi.plan{{object-fit:contain;background:#fff}}
.hero h1{{margin:0;font-size:17pt;line-height:1;letter-spacing:-.02em}} .hero h2{{margin:1.5mm 0 3mm;font-size:8pt;font-weight:400;font-style:italic;color:#555}}
.q{{font-size:11pt;line-height:1.2;color:var(--a);margin-top:3mm}}
.kw{{display:flex;flex-wrap:wrap;gap:1.2mm;margin-top:3mm}} .kw span{{border:.4pt solid #111;border-radius:9pt;padding:.3mm 2mm;font-size:5.8pt}}
.band{{display:grid;grid-template-columns:1fr 1fr 1.2fr 1.2fr;gap:5mm}}
.box{{border-top:.5pt solid #111;padding-top:2mm;min-width:0}}
.sw{{display:grid;grid-template-columns:repeat(5,1fr)}} .sw i{{display:block;height:14mm}} .sw b{{display:block;font-size:5pt;font-weight:500;margin-top:1mm}} .sw span{{display:block;font-size:4.8pt;color:#66665f}}
.mt{{display:grid;grid-template-columns:1fr 1fr;gap:2.5mm}} .mt canvas{{width:100%;aspect-ratio:1.6;display:block}} .mt b{{display:block;font-size:5.8pt;font-weight:600;margin-top:.8mm}} .mt span{{font-size:5.2pt;color:#66665f}}
ol{{margin:0;padding-left:3.6mm;display:grid;gap:1.6mm}} li b{{color:var(--a)}}
.foot{{display:grid;grid-template-columns:{'1.4fr 1fr' if photos else '1fr'};gap:5mm;align-items:start}}
.lp{{width:100%;display:block}} .strip{{display:grid;grid-template-columns:repeat(2,1fr);gap:2.5mm}} .strip img{{width:100%;height:30mm;object-fit:cover;display:block}}
table{{width:100%;border-collapse:collapse;font-size:5.8pt}} td{{padding:.3mm 0}} td+td{{text-align:right}}
.end{{border-top:.5pt solid #111;padding-top:2mm;display:grid;grid-template-columns:70mm 1fr;gap:6mm}}
</style></head><body><div class="pg">
<div class="top"><h1 class="mast">{e(job['brand'])}</h1><div class="s"><p class="cap">Spatial synopsis · layout</p><p>{e(job['line'])}</p></div></div>
<div class="hero">{hero}<div><h1>{e(job['title'])}</h1><h2>{e(job.get('subtitle', ''))}</h2><p class="s">{e(job['synopsis'])}</p><div class="kw">{kw}</div><p class="q">{e(job['quote'])}</p>
 {('<div class="strip" style="margin-top:5mm">' + strip + '</div>') if strip else ''}</div></div>
<div class="band"><div class="box"><p class="cap">Palette</p><div class="sw">{sw}</div></div>
 <div class="box"><p class="cap">Materials · where</p><div class="mt">{mats}</div></div>
 <div class="box s"><p class="cap">Design intent</p><ol>{why}</ol></div>
 <div class="box s"><p class="cap">The walk · three moments</p><ol>{seq}</ol></div></div>
<div class="foot">{low}<div class="end" style="{'grid-template-columns:1fr' if photos else ''}"><div><p class="cap">Area programme</p><table>{area_rows}</table></div>
 <p class="xs">{W:.1f} × {D:.1f} m, ceiling {H} m. Concept layout; dimensions assumed, not surveyed. The circulation is checked by code to keep at least 0.3 m from every object. Palette {'sampled from the photographs, completed from the synopsis' if photos else 'from the synopsis'}.</p></div></div>
</div>{_TEX_JS}</body></html>"""
    hp = out_dir / "layout.html"
    hp.write_text(doc, encoding="utf-8")
    pdf = _print(hp, out_dir / "layout.pdf", "297mm", "420mm", shot=out_dir / "layout_preview.png")
    return {"pdf": pdf, "plan": plan_png, "preview": str(out_dir / "layout_preview.png"), "missing_photos": missing}


def blueprint_pdf(job: dict, out_dir, renders: dict) -> "dict[str, str]":
    """<on request> A3-landscape drawing sheet: plan | eye-level + cutaway renders | title block, intent, area programme."""
    out_dir = Path(out_dir)
    plan_png, area = plan(job, out_dir / "plan.png")
    L = job["layout"]; W, D, H = L["W"], L["D"], L["H"]
    rel = lambda p: Path(p).resolve().as_uri()
    rows = "".join(f'<tr><td>{e(k)}</td><td>{v:.1f}</td><td>{100 * v / (W * D):.0f}%</td><td><i style="width:{100 * v / (W * D):.1f}%"></i></td></tr>' for k, v in area.items())
    why = "".join(f'<li><b>{e(w["t"])}</b> {e(w["d"])}</li>' for w in job["why"])
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(job['title'])} blueprint</title><style>
@page{{size:420mm 297mm;margin:0}} *{{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
html,body{{margin:0;background:#fff;color:#15191b;font-family:{FONT}}}
.sh{{width:420mm;height:297mm;display:grid;grid-template-columns:1.25fr .95fr .8fr;--a:{e(job['accent'])}}}
.pl{{padding:8mm;display:flex;align-items:center;justify-content:center;border-right:.6pt solid #15191b}} .pl img{{max-width:100%;max-height:100%}}
.rd{{display:grid;grid-template-rows:1fr 1fr;border-right:.6pt solid #15191b;min-width:0}} .rd figure{{margin:0;display:flex;flex-direction:column;min-height:0;border-bottom:.4pt solid #c5cdd1}}
.rd img{{flex:1;min-height:0;width:100%;object-fit:cover}} figcaption{{font-size:6pt;color:#5b656b;padding:1.4mm 3mm}}
.sd{{display:grid;grid-template-rows:auto 1fr auto;font-size:6.6pt;line-height:1.45}} .sd>*{{padding:5mm;border-bottom:.4pt solid #c5cdd1}}
.no{{font-weight:700;font-size:15pt;color:var(--a)}} h2{{font-size:14pt;margin:2mm 0 1mm;line-height:1}} .sub{{font-style:italic;color:#5b656b;margin:0 0 3mm}}
dl{{display:grid;grid-template-columns:auto 1fr;gap:.6mm 3mm;margin:0}} dt{{color:#5b656b;text-transform:uppercase;letter-spacing:.08em;font-size:5.6pt}} dd{{margin:0}}
h3{{font-size:5.8pt;letter-spacing:.16em;text-transform:uppercase;margin:0 0 2mm}} ol{{margin:0;padding-left:4mm;display:grid;gap:1.8mm;color:#5b656b}} li b{{color:#15191b;font-weight:600}}
table{{width:100%;border-collapse:collapse}} td{{padding:.4mm 1mm}} td:nth-child(2),td:nth-child(3){{text-align:right}} td i{{display:block;height:1.6mm;background:var(--a)}}
</style></head><body><div class="sh">
<div class="pl"><img src="{rel(plan_png)}" alt="plan"></div>
<div class="rd"><figure><img src="{rel(renders['eye'])}" alt=""><figcaption>Eye level on the circulation</figcaption></figure><figure><img src="{rel(renders['cut'])}" alt=""><figcaption>Cutaway, ceiling and front wall removed</figcaption></figure></div>
<div class="sd"><div><div class="no">{e(job['brand'])}</div><h2>{e(job['title'])}</h2><p class="sub">{e(job.get('subtitle', ''))}</p>
<dl><dt>Sheet</dt><dd>Ground floor plan, circulation, rendered views</dd><dt>Envelope</dt><dd>{W:.1f} × {D:.1f} m, ceiling {H} m, {W * D:.0f} m²</dd><dt>Scale</dt><dd>approx. 1:100</dd>
<dt>Tools</dt><dd>gentle_monster · render3d plan · three.js r170 PBR</dd><dt>Status</dt><dd>Concept. Dimensions assumed, not surveyed</dd></dl></div>
<div><h3>Design intent</h3><ol>{why}</ol></div>
<div><h3>Area programme (m²)</h3><table>{rows}<tr><td><b>Total (= W × D)</b></td><td><b>{W * D:.1f}</b></td><td>100%</td><td></td></tr></table></div></div>
</div></body></html>"""
    hp = out_dir / "blueprint.html"
    hp.write_text(doc, encoding="utf-8")
    pdf = _print(hp, out_dir / "blueprint.pdf", "420mm", "297mm")
    return {"pdf": pdf, "plan": plan_png}
