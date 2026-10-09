"""HTML magazine from the plan. Facts carry their citation and kind; experiments carry an EXPERIMENT tag.

Pictures: only publishable assets (assets.publishable) are printed. A reference whose rights are unknown is
shown as a 'withheld' slot with its title and URL -- the gap is visible. Generated plates say they are drawings.
The page embeds a measuring script (QA_JS) that runs only when the URL has #qa: it reports overflow, image
ratios, grid offsets and visible Hangul (no CJK font here) into <script id="qa-result">, read back by qa.py.
"""
from __future__ import annotations

import html
import json
import math
import os
from pathlib import Path

from gentle_monster.magazine import assets as A, catalogue as CAT, design as DS, drift as D

e = lambda s: html.escape(str(s if s is not None else ""))
REFS_PER_PAGE = 30
KIND_LABEL = {"official_statement": "Official statement", "reported_fact": "Reported", "interpretation": "Interpretation"}
INDEPENDENCE = ("An independent concept magazine produced by a research tool. It is not published, commissioned, "
                "approved or endorsed by Gentle Monster or any brand or magazine named in it. Names identify the subjects "
                "of the research. No logos, campaign images or campaign copy are reproduced.")

QA_JS = r"""
(function(){
 if(location.hash.indexOf('qa')<0) return;
 if(location.hash.indexOf('print')>=0) document.documentElement.classList.add('print-sim');
 function run(){
  var out={viewport:[innerWidth,innerHeight],doc_scroll_w:document.documentElement.scrollWidth,pages:[]};
  var hangul=/[ㄱ-ㆎ가-힣]/;
  document.querySelectorAll('.page').forEach(function(p,i){
   var r=p.getBoundingClientRect(), over=[], imgs=[], off=[];
   p.querySelectorAll(':scope > *, .entries > *, .cols-2 > *, .cols-3 > *, figure, table, .refs').forEach(function(el){
     var b=el.getBoundingClientRect();
     if(getComputedStyle(el).position==='absolute' && el.tagName==='FIGURE') return;
     if(b.width>0 && (b.bottom>r.bottom+1 || b.right>r.right+1)) over.push((el.className||el.tagName)+'');
   });
   p.querySelectorAll('img').forEach(function(im){
     var b=im.getBoundingClientRect();
     imgs.push({src:im.getAttribute('src'),ok:im.complete&&im.naturalWidth>0,nat:im.naturalWidth?im.naturalWidth/im.naturalHeight:0,
                shown:b.height?b.width/b.height:0,fit:getComputedStyle(im).objectFit});
   });
   var cs=getComputedStyle(p), pl=parseFloat(cs.paddingLeft), pr=parseFloat(cs.paddingRight), gap=parseFloat(cs.columnGap)||0;
   var inner=r.width-pl-pr, col=(inner-gap*11)/12, lines=[];
   for(var k=0;k<=12;k++){lines.push(r.left+pl+k*(col+gap)); if(k>0) lines.push(r.left+pl+k*(col+gap)-gap);}
   if(cs.display==='grid') p.querySelectorAll(':scope > [class*="span-"], :scope > figure, :scope > .entries').forEach(function(el){
     var x=el.getBoundingClientRect().left, d=Math.min.apply(null,lines.map(function(L){return Math.abs(L-x)}));
     if(d>1.5) off.push({el:el.className||el.tagName,dx:Math.round(d*10)/10});
   });
   var txt=p.innerText||'';
   out.pages.push({i:i+1,id:p.id,type:p.dataset.type,overflow:over,images:imgs,grid_off:off,hangul:hangul.test(txt),chars:txt.length,
                   self_scroll:p.scrollHeight>p.clientHeight+2});
  });
  var wide=[]; document.querySelectorAll('body *').forEach(function(el){var b=el.getBoundingClientRect();
    if(b.right>innerWidth+1 && wide.length<6 && !el.closest('.nav')) wide.push((el.tagName+'.'+(el.className||'')).slice(0,40)+':'+Math.round(b.right));});
  out.too_wide=wide;
  var s=document.createElement('script'); s.type='application/json'; s.id='qa-result'; s.textContent=JSON.stringify(out);
  document.body.appendChild(s);
 }
 if(document.readyState==='complete') run(); else addEventListener('load',run);
})();
"""


class Refs:
    """Reference numbers in order of first citation; uncited sources follow."""

    def __init__(self, cat):
        self.cat, self.src, self.num = cat, CAT.by_id(cat), {}

    def cite(self, sids) -> str:
        out = []
        for s in sids:
            if s not in self.src:
                continue
            n = self.num.setdefault(s, len(self.num) + 1)
            out.append(f'<a href="#ref-{n}">{n}</a>')
        return f"<sup>[{','.join(out)}]</sup>" if out else ""

    def ordered(self):
        for s in self.cat["sources"]:
            self.num.setdefault(s["id"], len(self.num) + 1)
        return sorted(self.num.items(), key=lambda kv: kv[1])


def _claim(c, refs, cat, short=False) -> str:
    read = CAT.claim_verification(cat, c)
    ev = c["evidence"] if not short or len(c["evidence"]) < 260 else c["evidence"][:250].rsplit(" ", 1)[0] + " ..."
    conf = f'<p class="small"><i>Sources differ:</i> {e(c["conflicts"][:220])}</p>' if c.get("conflicts") and not short else ""
    return (f'<div class="claim"><div class="kind">{KIND_LABEL[c["kind"]]} · {e(c["subject"]).replace("_", " ")} · read: {read}</div>'
            f'<p>{e(ev)}{refs.cite(c.get("source_ids", []))}</p>{conf}</div>')


def _fig(asset, caption, cls="", rel=None) -> str:
    if asset and A.publishable(asset):
        src = os.path.relpath(asset["local_path"], rel) if rel else asset["local_path"]
        gen = asset["asset_type"] == "generated_plate"
        alt = ("Generated drawing: " if gen else "") + (asset.get("source_title") or "")
        credit = asset.get("attribution") or ""
        return (f'<figure class="{cls}" data-asset="{e(asset["asset_id"])}"><img src="{e(src)}" alt="{e(alt)}">'
                f'<figcaption><b>{e(caption)}</b> {e(credit)}.</figcaption></figure>')
    if asset:
        return (f'<figure class="{cls}" data-asset="{e(asset["asset_id"])}"><div class="withheld">Image withheld -- rights not '
                f'cleared<br>{e(asset.get("source_title") or "")}</div><figcaption><b>{e(caption)}</b> Reference only: '
                f'{e(asset.get("source_url") or "")}</figcaption></figure>')
    return ""


def _rh(left, right) -> str:
    return f'<div class="rh"><span>{e(left)}</span><span>{e(right)}</span></div>'


def _short(text, n=90):
    t = text.split(";")[0].split(". ")[0]
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + " ..."


def build(plan: dict, cat: dict, assets: list, plates: dict, tokens: dict, out_dir, title: str) -> dict:
    """plates: section -> asset (generated). Returns {'html': path, 'pages': [...rendered page records]}."""
    out_dir = Path(out_dir)
    refs = Refs(cat)
    claims = {c["id"]: c for c in cat["claims"]}
    hyps = {h["hypothesis_id"]: h for h in plan["hypotheses"]}
    chosen = hyps[plan["chosen"]]
    brief = plan["brief"]
    rendered = []
    body = []
    issue = f"Issue 00 · {chosen['title']}"

    def page(p, inner, extra_cls=""):
        n = len(rendered) + 1
        side = "l" if n % 2 == 0 else "r"
        pid = f"p{n:02d}"
        rendered.append({"folio": n, "section": p["section"], "type": p["type"], "kind": p["kind"], "id": pid,
                         "hypothesis": p.get("hypothesis"), "device": p.get("device"),
                         "assets": [], "claims": p.get("claims", [])})
        fol = f'<div class="folio {side}">{n:02d}</div>' if p["type"] != "cover" else ""
        body.append(f'<section class="page pt-{p["type"]} {extra_cls}" id="{pid}" data-type="{p["type"]}" '
                    f'data-kind="{p["kind"]}" data-section="{e(p["section"])}">{inner}{fol}</section>')
        return rendered[-1]

    def plate_for(p):
        return plates.get(p["section"])

    for p in plan["pages"]:
        sec, typ = p["section"], p["type"]
        pl = plate_for(p)
        exp_tag = ('<span class="tag exp">Experiment -- a drift fiction built on the cited research; not a real '
                   'campaign, product or event</span>') if p["kind"] == "experiment" else ""
        if typ == "cover":
            inner = (f'<div class="rh" style="border:0"><span>{e(issue)}</span><span>Concept issue</span></div>'
                     f'<div class="mast">Gentle<br>Monster<br>Field<br>Notes</div>'
                     f'{_fig(pl, "Cover plate.", rel=out_dir)}'
                     f'<div class="q">What would {e(brief["object"])} look like if it were {e(chosen["title"].split(" read as ")[-1])}?</div>'
                     f'<div class="disclaimer">{e(INDEPENDENCE)}</div>')
            rec = page(p, inner)
        elif sec == "Editor's Letter":
            n_off = sum(claims[c]["kind"] == "official_statement" for c in claims)
            inner = (_rh(sec, issue) + f'<div class="span-7"><h2>Letter</h2>'
                     f'<p class="lede">This issue began as one sentence of instruction. The theme words read from it were: '
                     f'<b>{e(", ".join(brief["terms"][:10]))}</b>.</p>'
                     f'<p>It was not written to praise a product. It was assembled from {len(cat["sources"])} sources and '
                     f'{len(cat["claims"])} claims about Gentle Monster and the brands and magazines around it -- '
                     f'{n_off} of them the brand speaking about itself, the rest other people reporting or interpreting. Every '
                     f'factual sentence on the following pages carries its source number, and says how far that source was read.</p>'
                     f'<p>Then the material was allowed to drift. Starting from the research, each step applied one operation -- '
                     f'detach, refine, associate, invert, revive, fold, or a rare leap -- and every few steps something from outside '
                     f'interrupted. {len(plan["hypotheses"])} directions came out; one was chosen: <b>{e(chosen["title"])}</b>. '
                     f'Pages marked <i>Experiment</i> come from that drift. They are fiction built on cited facts and are never '
                     f'presented as the brand\'s own work.</p>'
                     f'<p>What could not be verified is listed in the Critical Review, not hidden.</p></div>'
                     f'<div class="span-5 small"><h3>How to read this issue</h3><p><span class="kind">Official statement</span> -- '
                     f'what a brand says about itself.</p><p><span class="kind">Reported</span> -- what others report as fact.</p>'
                     f'<p><span class="kind">Interpretation</span> -- a reading.</p><p><span class="kind">read: snippet</span> -- '
                     f'only a search-result fragment was seen; the page itself was not opened.</p>'
                     f'<p><span class="tag exp">Experiment</span></p></div>')
            rec = page(p, inner)
        elif p["kind"] == "fact":
            cs = [claims[c] for c in p.get("claims", []) if c in claims]
            fig = _fig(pl, f"{sec}.", "span-5", rel=out_dir) if pl else ""
            many = len(cs) > 7
            if typ == "asymmetric":
                inner = (_rh(sec, issue) + f'<div class="span-12"><h2>{e(sec)}</h2></div>{fig}'
                         f'<div class="start-6 small">' + "".join(_claim(c, refs, cat, True) for c in cs) + "</div>")
            elif typ == "product_study":
                inner = (_rh(sec, issue) + f'<div class="span-12"><h2>{e(sec)}</h2></div>'
                         + _fig(pl, "Exploded view, numbered parts.", "span-7", rel=out_dir)
                         + '<div class="span-5 small">' + "".join(_claim(c, refs, cat, True) for c in cs) + "</div>")
            else:
                inner = (_rh(sec, issue) + f'<div class="span-12"><h2>{e(sec)}</h2>'
                         f'<p class="small">{e(p["purpose"]).capitalize()}.</p></div>'
                         f'<div class="span-12 {"cols-3" if many else "cols-2"} small">' + "".join(_claim(c, refs, cat, many) for c in cs) + "</div>")
            rec = page(p, inner)
        elif typ == "intrusion":
            x = p["intrusion"]
            inner = (_rh(sec, issue) + f'<div class="span-12">{exp_tag}</div><div class="who">{e(x["who"]).capitalize()} '
                     f'{e(x["how"])}.</div><div class="mark">What remains: {e(x["mark"])}.<br>Nothing on this page answers it.</div>')
            rec = page(p, inner, "dark")
        elif p["kind"] == "experiment":
            inner = _rh(sec, chosen["title"]) + _experiment(p, chosen, cat, claims, refs, pl, out_dir, exp_tag)
            rec = page(p, inner, "dark" if typ == "full_bleed" and D.DEVICES.get(p.get("device"), ("", "", ""))[2] == "orbit" else "")
        elif sec == "Directions Not Taken":
            rows = "".join(
                f'<tr><td class="n">{e(h["hypothesis_id"])}{" ✓" if h["hypothesis_id"] == chosen["hypothesis_id"] else ""}</td>'
                f'<td>{e(h["title"])}<br><span class="kind">{e(h["status"])}{" -- " + e(h.get("excluded_because")) if h.get("excluded_because") else ""}</span></td>'
                f'<td class="n">{h["total"]}</td><td>{e(h["strength"].replace("_", " "))}</td><td>{e(h["weakness"].replace("_", " "))}</td></tr>'
                for h in plan["hypotheses"])
            sc = "".join(f'<tr><td>{e(k.replace("_", " "))}</td>' + "".join(f'<td class="n">{"--" if h["scores"].get(k) is None else h["scores"][k]}</td>' for h in plan["hypotheses"]) + "</tr>"
                         for k in chosen["scores"])
            paths = "".join(f'<li><b>{e(h["hypothesis_id"])}</b>: ' + " → ".join(e(s["op"]) for s in h["path"][1:]) + "</li>" for h in plan["hypotheses"])
            inner = (_rh(sec, issue) + f'<div class="span-12"><h2>{e(sec)}</h2><p class="small">Every direction the drift produced, '
                     f'with the same seven criteria. Scores are heuristics computed from the ledger (see Colophon), not judgements of taste. '
                     f'Rights compliance is the share of the direction\'s plates that are cleared to print.</p>'
                     f'<table><tr><th>id</th><th>direction</th><th>total</th><th>strongest</th><th>weakest</th></tr>{rows}</table>'
                     f'<h3 style="margin-top:1.4em">Criteria</h3><table><tr><th></th>' +
                     "".join(f'<th>{e(h["hypothesis_id"])}</th>' for h in plan["hypotheses"]) + f'</tr>{sc}</table>'
                     f'<h3 style="margin-top:1.4em">Operators, in order</h3><ol class="small" style="padding-left:1.2em">{paths}</ol></div>')
            rec = page(p, inner)
        elif sec == "Image Catalogue":
            gen = [a for a in assets if a["asset_type"] == "generated_plate"]
            user = [a for a in assets if a["asset_type"] == "user_photo"]
            off = [a for a in assets if a["asset_type"] == "official_campaign"][:max(0, 12 - len(gen) - len(user))]
            rest = len(assets) - len(gen) - len(user) - len(off)
            ent = "".join(f'<div class="entry">{_fig(a, a["source_title"], rel=out_dir)}<div class="kind">'
                          f'{e(a["rights_status"])} · {e(a["retrieval_status"])}</div></div>' for a in user + gen + off)
            inner = (_rh(sec, issue) + f'<div class="span-12"><h2>{e(sec)}</h2><p class="small">Printed: {len(gen)} generated '
                     f'drawings{", " + str(len(user)) + " supplied photographs" if user else ""}. Withheld: official pages whose '
                     f'images were not retrieved (blocked) and whose rights are unknown -- shown as citations only. '
                     f'{rest} further references are listed in the References. Finding an image is not permission to print it.</p></div>'
                     f'<div class="entries four">{ent}</div>')
            rec = page(p, inner)
        elif sec == "Critical Review":
            snippet = sum(1 for c in cat["claims"] if CAT.claim_verification(cat, c) != "fulltext")
            nc = "".join(f"<li>{e(x)}</li>" for x in cat.get("not_checked", [])[:9])
            risks = "".join(f"<li>{e(r)}</li>" for r in chosen["risks"])
            inner = (_rh(sec, issue) + f'<div class="span-12"><h2>{e(sec)}</h2></div><div class="span-6 small">'
                     f'<h3>What this issue rests on</h3><p>{snippet} of {len(cat["claims"])} claims rest on search-result fragments; no '
                     f'source page was opened in full, because direct access to the brand and magazine sites was blocked from the '
                     f'machine that made this issue. Wording quoted here may differ from the original pages.</p>'
                     f'<h3>Risks of the chosen direction</h3><ul>{risks}</ul></div>'
                     f'<div class="span-6 small"><h3>Not checked</h3><ul>{nc}</ul></div>')
            rec = page(p, inner)
        elif typ == "references":
            ordered = refs.ordered()
            src = CAT.by_id(cat)
            chunks = [ordered[i:i + REFS_PER_PAGE] for i in range(0, len(ordered), REFS_PER_PAGE)]
            for k, ch in enumerate(chunks):
                lis = "".join(f'<li id="ref-{n}" value="{n}">{e(src[s]["title"])} -- {e(src[s].get("publisher") or "")}. '
                              f'<a href="{e(src[s]["url"])}">{e(src[s]["url"])}</a> <span class="kind">{e(src[s]["kind"])} · '
                              f'read: {e(src[s]["verification"])} · accessed {e(src[s].get("accessed", ""))}</span></li>' for s, n in ch)
                q = dict(p, section=sec if k == 0 else f"{sec} (cont.)")
                rec = page(q, _rh(q["section"], issue) + (f'<div class="span-12"><h2>{e(sec)}</h2></div>' if k == 0 else "")
                           + f'<ol class="refs">{lis}</ol>')
                rec["sources"] = [s for s, _ in ch]
            continue
        elif typ == "colophon":
            t = tokens
            inner = (_rh(sec, issue) + f'<div class="span-7"><h2>{e(sec)}</h2><p>{e(INDEPENDENCE)}</p>'
                     f'<p class="small">Made by <code>python3 -m gentle_monster magazine</code>: research catalogue → Drift '
                     f'(the SE_NEW DRIFT rules: ledger, one operator per step, measured inheritance, cooling props revived, '
                     f'intrusions every {D.EVERY} steps, two hard gates) → {len(plan["hypotheses"])} directions → editorial plan → HTML → '
                     f'Chromium PDF → QA. No language model wrote these pages; their text is composed from the research catalogue.</p>'
                     f'<p class="small">Scores: traceability = share of principles with a source; distance = 1 − word overlap between '
                     f'start and end of the drift; relevance = recurring brand-research words that survived (÷4, capped); coherence and '
                     f'feasibility = share of devices that map to a page type / a drawable plate; originality = share of devices no '
                     f'other direction uses.</p></div>'
                     f'<div class="span-5 small"><h3>Type & grid</h3><p>Liberation Sans / Serif / Mono. Scale ratio {DS.RATIO}, '
                     f'baseline {DS.BASELINE} pt, {DS.COLS} columns, {DS.GUTTER} mm gutter, page {DS.PAGE_W} × {DS.PAGE_H} mm.</p>'
                     f'<p>Paper {t["color"]["paper"]} · ink {t["color"]["ink"]} · accent {t["color"]["accent"]} '
                     f'(from the chosen discipline). Contrast ink/paper {t["contrast"]["ink/paper"]}:1.</p></div>')
            rec = page(p, inner)
        else:
            rec = page(p, _rh(sec, issue) + f'<div class="span-12"><h2>{e(sec)}</h2><p>{e(p["purpose"])}</p></div>')
        if pl:
            rec["assets"].append(pl["asset_id"])

    nav = "".join(f'<a href="#{r["id"]}">{r["folio"]:02d} {e(r["section"])}</a>' for r in rendered)
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(title)}</title><meta name="description" content="{e(INDEPENDENCE)}">'
           f'<meta name="brief" content="{e(brief["text"])}"><style>{DS.css(tokens)}</style></head><body>'
           f'<nav class="nav" aria-label="pages">{nav}</nav><main>{"".join(body)}</main>'
           f'<script>{QA_JS}</script></body></html>')
    path = out_dir / "index.html"
    path.write_text(doc, encoding="utf-8")
    return {"html": str(path), "pages": rendered, "cited": dict(refs.num)}


def _experiment(p, h, cat, claims, refs, pl, out_dir, tag) -> str:
    dev = p.get("device")
    label, ptype, _plate = D.DEVICES[dev]
    head = (f'<div class="span-12">{tag}<h2>{e(h["title"])}</h2><p class="small"><b>Rule.</b> {e(h["transformation_rule"])}</p></div>')
    gm = [claims[c["claim"]] for c in h["observed_principles"] if c["claim"] in claims][:6]
    gm += [c for c in cat["claims"] if c["subject"] in CAT.GM_SUBJECTS and c not in gm][:6 - len(gm)]
    if ptype == "catalogue":
        prefix = {"lot_entry": "Lot", "find_number": "F", "tag_entry": "Tag", "specimen_plate": "Sp."}.get(dev, "No.")
        ent = "".join(f'<div class="entry"><div class="no">{prefix} {i + 1:02d}</div><p>{e(_short(c["evidence"]))}'
                      f'{refs.cite(c["source_ids"])}</p><div class="kind">provenance: {e(c["subject"]).replace("_", " ")} · '
                      f'{KIND_LABEL[c["kind"]]}</div></div>' for i, c in enumerate(gm))
        return head + _fig(pl, f"Plate -- {label}.", "span-12", rel=out_dir) + f'<div class="entries">{ent}</div>'
    if ptype in ("multi_column",):
        rows = "".join(f'<tr><td class="n">{i:02d}</td><td>{e(s["op"])}</td><td>{e(s["label"][:80])}</td>'
                       f'<td class="n">{"" if not s.get("measure") else str(s["measure"].get("new")) + " / " + str(s["measure"].get("kept"))}</td></tr>'
                       for i, s in enumerate(h["path"]))
        return head + (f'<div class="span-12"><p class="small">{e(label).capitalize()}: the drift itself, logged. new / kept = words '
                       f'added / carried from the step before (kept ≥ 2 counts as inheritance).</p><table><tr><th>step</th><th>operation</th>'
                       f'<th>entry</th><th>new / kept</th></tr>{rows}</table></div>')
    if ptype == "single_column":
        items = "".join(f'<li><b>{e(s["op"])}</b> -- {e(s["label"][:110])}</li>' for s in h["path"])
        src = "".join(f'<li>{e(_short(c["evidence"], 120))}{refs.cite(c["source_ids"])}</li>' for c in gm[:4])
        return head + (f'<div class="span-7"><h3>{e(label).capitalize()}</h3><ol class="chain small">{items}</ol></div>'
                       f'<div class="span-5 small"><h3>Where it started</h3><ul>{src}</ul></div>')
    if ptype == "typographic":
        words = (h["transformation_rule"].split(": ")[-1].split(". Carry over from the research: ")[-1].rstrip(".").split(", ")
                 + [w for w in ("look", "closer", "again")])[:7]
        size, lines = 4.2, []
        for w in words:
            lines.append(f'<div style="font-size:{size:.2f}em">{e(w.upper())}</div>')
            size *= 0.72
        return head + f'<div class="chart">{"".join(lines)}</div>' + _fig(pl, f"Plate -- {label}.", "start-5", rel=out_dir)
    if ptype == "full_bleed":
        return (_fig(pl, f"{label}.", rel=out_dir) + f'<div class="over">{tag}<h3>{e(h["title"])}</h3>'
                f'<p class="small">{e(h["intended_reader_experience"]).capitalize()}.</p></div>')
    if ptype == "image_essay":
        return head + _fig(pl, f"Plate -- {label}.", "span-8", rel=out_dir) + (
            f'<div class="span-4 small"><p>{e(h["image_direction"]).capitalize()}.</p><p>{e(h["content_implications"]).capitalize()}.</p></div>')
    if ptype == "asymmetric":
        cues = "".join(f'<li><b>Q{i}</b> {e(s["label"][:70])}</li>' for i, s in enumerate(h["path"][1:], 1))
        return head + _fig(pl, f"Plate -- {label}.", "span-7", rel=out_dir) + f'<div class="span-5 small"><ol class="chain">{cues}</ol></div>'
    # product_study
    notes = "".join(f'<p><b>{i + 1}.</b> {e(_short(c["evidence"], 140))}{refs.cite(c["source_ids"])}</p>' for i, c in enumerate(gm[:4]))
    return head + _fig(pl, f"Plate -- {label}. Drawn, not measured.", "span-8", rel=out_dir) + f'<div class="span-4 small">{notes}</div>'
