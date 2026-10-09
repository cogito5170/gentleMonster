"""HTML magazine from the plan -- in Korean. Quotes from sources stay in their original language (English), marked as such.

Facts carry their citation, kind and reading depth; experiments carry the 실험 tag. Front (cover, contents), body
(features), appendix (directions not taken, images, critique, references, colophon) -- apparatus at the back.

Pictures: only publishable assets (assets.publishable) are printed. A reference whose rights are unknown is shown
as a '보류' slot with its title and URL. Generated plates say they are drawings.
The page embeds a measuring script (QA_JS) that runs only when the URL has #qa: overflow, image ratios, grid
offsets, visible Hangul, elements past the viewport -> <script id="qa-result">, read back by qa.py.
"""
from __future__ import annotations

import html
import os
from pathlib import Path

from gentle_monster.magazine import assets as A, catalogue as CAT, design as DS, drift as D

e = lambda s: html.escape(str(s if s is not None else ""))
J = CAT.josa
REFS_PER_PAGE = 34
KIND_LABEL = {"official_statement": "공식 입장", "reported_fact": "보도", "interpretation": "해석"}
READ_LABEL = {"fulltext": "원문 열람", "snippet": "검색 조각만 봄", "none": "출처 없음"}
SUBJ_KO = {"gentle_monster": "젠틀몬스터", "haus_dosan": "하우스 도산", "skp_s": "SKP-S", "haus_nowhere": "하우스 노웨어",
           "mykita": "MYKITA", "jacques_marie_mage": "Jacques Marie Mage", "kuboraum": "Kuboraum",
           "retrosuperfuture": "RETROSUPERFUTURE", "tamburins": "탬버린즈", "nudake": "누데이크", "032c": "032c",
           "dazed": "Dazed", "the_face": "The Face", "a_magazine_curated_by": "A Magazine Curated By", "purple": "Purple",
           "document_journal": "Document Journal", "kaleidoscope": "Kaleidoscope", "system": "System",
           "apartamento": "Apartamento", "pin_up": "PIN–UP", "drift_studio": "DRIFT (스튜디오)"}
INDEPENDENCE = ("이 책은 연구 도구가 만든 독립 콘셉트 매거진입니다. 젠틀몬스터를 비롯해 이 책에 나오는 어떤 브랜드나 매거진도 "
                "이 책을 발행 · 의뢰 · 승인 · 후원하지 않았습니다. 이름은 연구 대상을 가리키기 위해서만 씁니다. "
                "로고 · 캠페인 이미지 · 캠페인 문구는 싣지 않았습니다.")
EXP_TAG = ('<span class="tag exp">실험 — 인용한 연구 위에 지은 표류의 허구입니다. 실제 캠페인 · 제품 · 사건이 아닙니다</span>')

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
     if(el.closest('[data-bleed]')) return;   // bleeds past the trim on purpose (a spread split over two pages)
     if(b.width>0 && (b.bottom>r.bottom+1 || b.right>r.right+1)) over.push((el.className||el.tagName)+'');
   });
   p.querySelectorAll('img').forEach(function(im){
     var b=im.getBoundingClientRect();
     imgs.push({src:im.getAttribute('src'),ok:im.complete&&im.naturalWidth>0,nat:im.naturalWidth?im.naturalWidth/im.naturalHeight:0,
                shown:b.height?b.width/b.height:0,fit:getComputedStyle(im).objectFit,
                nw:im.naturalWidth,nh:im.naturalHeight,rw:b.width,rh:b.height,
                pw:p.getBoundingClientRect().width,ph:p.getBoundingClientRect().height});
   });
   var cs=getComputedStyle(p), pl=parseFloat(cs.paddingLeft), pr=parseFloat(cs.paddingRight), gap=parseFloat(cs.columnGap)||0;
   var inner=r.width-pl-pr, col=(inner-gap*11)/12, lines=[];
   for(var k=0;k<=12;k++){lines.push(r.left+pl+k*(col+gap)); if(k>0) lines.push(r.left+pl+k*(col+gap)-gap);}
   if(cs.display==='grid') p.querySelectorAll(':scope > [class*="span-"], :scope > figure, :scope > .entries').forEach(function(el){
     var x=el.getBoundingClientRect().left, d=Math.min.apply(null,lines.map(function(L){return Math.abs(L-x)}));
     if(d>1.5) off.push({el:el.className||el.tagName,dx:Math.round(d*10)/10});
   });
   var faux=[], minfs=99, cols=[];
   p.querySelectorAll('*').forEach(function(el){
     var own=''; el.childNodes.forEach(function(n){ if(n.nodeType===3) own+=n.textContent; });
     if(!own.trim()) return;
     var cs2=getComputedStyle(el), fs=parseFloat(cs2.fontSize);
     if(cs2.display!=='none' && cs2.visibility!=='hidden' && cs2.opacity>0.2 && fs<minfs) minfs=fs;
     if(hangul.test(own) && parseInt(cs2.fontWeight)>=600) faux.push(own.trim().slice(0,20));
   });
   p.querySelectorAll('[data-col]').forEach(function(el){
     var b=el.getBoundingClientRect(); cols.push({col:parseFloat(el.dataset.col),x:(b.left-r.left)/r.width*100,mirror:el.dataset.mirror||''});
   });
   var blocks=[], clash=[];
   p.querySelectorAll(':scope > *').forEach(function(el){
     if(el.closest('[data-bleed]')||el.classList.contains('ghost')||el.classList.contains('folio')) return;
     if(!(el.innerText||'').trim()) return;
     var b=el.getBoundingClientRect(); if(b.width>0&&b.height>0) blocks.push([el,b]);
   });
   for(var a1=0;a1<blocks.length;a1++) for(var a2=a1+1;a2<blocks.length;a2++){
     var A1=blocks[a1][1], A2=blocks[a2][1];
     var w=Math.min(A1.right,A2.right)-Math.max(A1.left,A2.left), h=Math.min(A1.bottom,A2.bottom)-Math.max(A1.top,A2.top);
     if(w>2&&h>2) clash.push(((blocks[a1][0].innerText||'').trim().slice(0,14))+' / '+((blocks[a2][0].innerText||'').trim().slice(0,14)));
   }
   var txt=p.innerText||'';
   out.pages.push({i:i+1,id:p.id,type:p.dataset.type,overflow:over,images:imgs,grid_off:off,hangul:hangul.test(txt),chars:txt.length,
                   faux:faux,minfs:minfs,cols:cols,clash:clash,
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


def subj(s: str) -> str:
    return SUBJ_KO.get(s, s.replace("_", " "))


def _clip(text, n):
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " …"


def _claim(c, refs, cat, short=False) -> str:
    read = CAT.claim_verification(cat, c)
    ev = _clip(c["evidence"], 250) if short else c["evidence"]
    conf = (f'<p class="small note">출처마다 다르다: <span lang="en">{e(_clip(c["conflicts"], 200))}</span></p>'
            if c.get("conflicts") and not short else "")
    return (f'<div class="claim"><div class="kind">{KIND_LABEL[c["kind"]]} · {e(subj(c["subject"]))} · {READ_LABEL[read]}</div>'
            f'<p class="quote" lang="en">{e(ev)}{refs.cite(c.get("source_ids", []))}</p>{conf}</div>')


def _fig(asset, caption, cls="", rel=None) -> str:
    if asset and A.publishable(asset):
        src = os.path.relpath(asset["local_path"], rel) if rel else asset["local_path"]
        gen = asset["asset_type"] == "generated_plate"
        alt = ("생성한 도면: " if gen else "") + (asset.get("source_title") or "")
        credit = "이 도구가 그린 도면 — 사진이 아닙니다" if gen else (asset.get("attribution") or "")
        return (f'<figure class="{cls}" data-asset="{e(asset["asset_id"])}"><img src="{e(src)}" alt="{e(alt)}">'
                f'<figcaption><b>{e(caption)}</b> {e(credit)}.</figcaption></figure>')
    if asset:
        return (f'<figure class="{cls}" data-asset="{e(asset["asset_id"])}"><div class="withheld">이미지 보류 — 사용 권리 미확인<br>'
                f'<span lang="en">{e(asset.get("source_title") or "")}</span></div><figcaption><b>{e(caption)}</b> 출처로만 싣는다: '
                f'{e(asset.get("source_url") or "")}</figcaption></figure>')
    return ""


def _rh(left, right) -> str:
    return f'<div class="rh"><span>{e(left)}</span><span>{e(right)}</span></div>'


def _short(text, n=90):
    t = text.split(";")[0].split(". ")[0]
    return _clip(t, n)


def build(plan: dict, cat: dict, assets: list, plates: dict, tokens: dict, out_dir, title: str) -> dict:
    """plates: section -> asset (generated). Returns {'html': path, 'pages': [...rendered page records]}."""
    out_dir = Path(out_dir)
    refs = Refs(cat)
    claims = {c["id"]: c for c in cat["claims"]}
    hyps = {h["hypothesis_id"]: h for h in plan["hypotheses"]}
    chosen = hyps[plan["chosen"]]
    ko = chosen["ko"]
    brief = plan["brief"]
    rendered, body = [], []
    issue = f"필드 노트 00호 · {ko['title']}"
    # folios are known before rendering (references may run to several pages) -- the contents page needs them
    n_refs = -(-len(cat["sources"]) // REFS_PER_PAGE)
    folio, toc = 1, []
    for p in plan["pages"]:
        toc.append((folio, p))
        folio += n_refs if p["type"] == "references" else 1

    def page(p, inner, extra_cls="", title_ko=None):
        n = len(rendered) + 1
        side = "l" if n % 2 == 0 else "r"
        pid = f"p{n:02d}"
        rendered.append({"folio": n, "section": p["section"], "title_ko": title_ko or p.get("title_ko"), "type": p["type"],
                         "kind": p["kind"], "part": p.get("part"), "id": pid, "hypothesis": p.get("hypothesis"),
                         "device": p.get("device"), "assets": [], "claims": p.get("claims", [])})
        fol = f'<div class="folio {side}">{n:02d}</div>' if p["type"] != "cover" else ""
        body.append(f'<section class="page pt-{p["type"]} {extra_cls}" id="{pid}" data-type="{p["type"]}" '
                    f'data-kind="{p["kind"]}" data-section="{e(p["section"])}">{inner}{fol}</section>')
        return rendered[-1]

    for p in plan["pages"]:
        sec, typ, tk = p["section"], p["type"], p.get("title_ko") or p["section"]
        pl = plates.get(sec)
        exp_tag = EXP_TAG if p["kind"] == "experiment" else ""
        if typ == "cover":
            obj_ko = {"eyewear": "안경", "fragrance": "향", "dessert": "디저트"}.get(brief["object"], brief["object"])
            q = f"{J(obj_ko, '이/가')} {J(ko['reads_as'], '이/가')} 된다면?"
            inner = (f'<div class="rh" style="border:0"><span>{e(issue)}</span><span>독립 콘셉트 매거진</span></div>'
                     f'<div class="mast" lang="en">Field<br>Notes</div>'
                     f'<div class="sub">젠틀몬스터를 읽는 독립 연구지 — 00호</div>'
                     f'{_fig(pl, "표지 도판.", rel=out_dir)}'
                     f'<div class="q">{e(q)}</div>'
                     f'<div class="disclaimer">{e(INDEPENDENCE)}</div>')
            rec = page(p, inner)
        elif typ == "contents":
            rows = []
            last = None
            for f, q in toc:
                if q["type"] in ("cover", "contents"):
                    continue
                if q.get("part") != last:
                    rows.append(f'<li class="part">{e(q.get("part"))}</li>')
                    last = q.get("part")
                rows.append(f'<li><a href="#p{f:02d}"><span class="no">{f:02d}</span> {e(q.get("title_ko"))}</a>'
                            f'{"<span class=kind> 실험</span>" if q["kind"] == "experiment" else ""}</li>')
            inner = (_rh(tk, issue) + f'<div class="span-5"><h2>차례</h2><p class="lede">{e(J(ko["title"], "은/는"))} 이번 호가 '
                     f'표류해 닿은 자리입니다. 앞쪽은 사실, 가운데는 실험, 뒤쪽은 그 실험을 검산하는 자료입니다.</p></div>'
                     f'<ol class="toc start-6">{"".join(rows)}</ol>')
            rec = page(p, inner)
        elif sec == "Editor's Letter":
            n_off = sum(c["kind"] == "official_statement" for c in cat["claims"])
            themes = ", ".join(brief.get("themes_ko") or []) or ", ".join(brief["terms"][:6])
            others = [h for h in plan["hypotheses"] if h is not chosen]
            inner = (_rh(tk, issue) + f'<div class="span-7"><h2>편집자의 글</h2>'
                     f'<p class="lede">이번 호는 한 문장의 주문에서 시작했습니다. 거기서 읽어 낸 낱말은 <b>{e(themes)}</b>입니다.</p>'
                     f'<p>제품을 칭찬하려고 만든 책이 아닙니다. 젠틀몬스터와 그 주변의 브랜드 · 매거진에 관한 출처 {len(cat["sources"])}개와 '
                     f'주장 {len(cat["claims"])}개를 모았고, 그중 {n_off}개만이 브랜드가 스스로에 대해 한 말입니다. 나머지는 다른 이들이 '
                     f'보도하거나 해석한 것입니다. 사실을 말하는 문장에는 모두 출처 번호가 붙고, 그 출처를 얼마나 읽었는지도 함께 적습니다.</p>'
                     f'<p>그다음 재료를 표류시켰습니다. 한 걸음에 연산 하나 — 떼어내기, 세분, 잇기, 뒤집기, 다시 부르기, 접기, 드물게 도약 — 를 '
                     f'걸고, {D.EVERY}걸음마다 바깥의 무언가가 끼어들었습니다. 방향 {len(plan["hypotheses"])}개가 나왔고 그중 '
                     f'<b>{e(ko["title"])}</b>을 골랐습니다. {e(", ".join(h["ko"]["title"] for h in others[:3]))}은 부록에 남겼습니다.</p>'
                     f'<p><span class="kind">실험</span> 표시가 붙은 쪽은 그 표류에서 나왔습니다. 인용한 사실 위에 지은 허구이며, '
                     f'브랜드의 작업으로 내놓지 않습니다. 확인하지 못한 것은 숨기지 않고 비평 쪽에 적었습니다.</p></div>'
                     f'<div class="span-5 small aside"><h3>읽는 법</h3><p><span class="kind">공식 입장</span> 브랜드가 스스로에 대해 한 말</p>'
                     f'<p><span class="kind">보도</span> 다른 이가 사실로 전한 것</p><p><span class="kind">해석</span> 누군가의 읽기</p>'
                     f'<p><span class="kind">검색 조각만 봄</span> 검색 결과의 조각만 보았고 원문 쪽은 열지 못함</p>'
                     f'<p>영어로 된 인용은 출처의 원래 말입니다. 옮기지 않았습니다.</p></div>')
            rec = page(p, inner)
        elif p["kind"] == "fact":
            cs = [claims[c] for c in p.get("claims", []) if c in claims]
            n_off = sum(c["kind"] == "official_statement" for c in cs)
            subs = ", ".join(dict.fromkeys(subj(c["subject"]) for c in cs))
            intro = {"Brand and Culture": f"브랜드가 스스로 한 말 {n_off}건과 남이 전한 말 {len(cs) - n_off}건을 나란히 놓습니다. 둘은 섞지 않습니다.",
                     "Spatial Experiments": "매장은 물건을 파는 곳이기 전에 무대였습니다. 층마다 다른 세계, 움직이는 기계, 상품이 없는 층.",
                     "Eyewear as Object": "안경을 만들어진 사물로 봅니다. 출처가 그 사물에 대해 말하는 것만 적습니다.",
                     "Cross-disciplinary Research": "다른 브랜드와 매거진에서 찾은 것을 원리로만 가져옵니다. 겉모습을 베끼지 않습니다."}.get(sec, "")
            head = f'<div class="span-12"><h2>{e(tk)}</h2><p class="lede small">{e(intro)} <span class="kind">{e(subs)}</span></p></div>'
            many = len(cs) > 7
            if typ == "asymmetric":
                inner = _rh(tk, issue) + head + _fig(pl, f"{tk} — 격자 평면.", "span-5", rel=out_dir) + (
                    '<div class="start-6 small">' + "".join(_claim(c, refs, cat, True) for c in cs) + "</div>")
            elif typ == "product_study":
                inner = _rh(tk, issue) + head + _fig(pl, "분해도, 부품 번호.", "span-7", rel=out_dir) + (
                    '<div class="span-5 small">' + "".join(_claim(c, refs, cat, True) for c in cs) + "</div>")
            else:
                inner = _rh(tk, issue) + head + (f'<div class="span-12 {"cols-3" if many else "cols-2"} small">'
                                                 + "".join(_claim(c, refs, cat, many) for c in cs) + "</div>")
            rec = page(p, inner)
        elif typ == "intrusion":
            x = p["intrusion"]
            inner = (_rh(tk, issue) + f'<div class="span-12">{exp_tag}</div><div class="who">{e(J(x["who_ko"], "이/가"))} '
                     f'{e(x["how_ko"])}.</div><div class="mark">남은 것: {e(x["mark_ko"])}.<br>이 쪽의 무엇도 그것에 답하지 않는다.</div>')
            rec = page(p, inner, "dark")
        elif p["kind"] == "experiment":
            inner = _rh(tk, ko["title"]) + _experiment(p, chosen, cat, claims, refs, pl, out_dir, exp_tag)
            rec = page(p, inner, "dark" if D.DEVICES.get(p.get("device"), ("", "", ""))[2] == "orbit" else "")
        elif sec == "Directions Not Taken":
            crit = {"source_traceability": "출처 추적", "conceptual_distance": "개념 거리", "editorial_coherence": "편집 일관성",
                    "visual_originality": "시각 독창성", "brand_relevance": "브랜드 관련성", "feasibility": "실현 가능성",
                    "rights_compliance": "권리 준수"}
            rows = "".join(
                f'<tr><td class="n">{e(h["hypothesis_id"])}{" ✓" if h is chosen else ""}</td><td>{e(h["ko"]["title"])}<br>'
                f'<span class="kind">{"채택" if h is chosen else ("남김" if h["status"] == "kept" else "제외 — " + e(h.get("excluded_because")))}</span></td>'
                f'<td class="n">{h["total"]}</td><td>{e(crit[h["strength"]])}</td><td>{e(crit[h["weakness"]])}</td></tr>'
                for h in plan["hypotheses"])
            sc = "".join(f'<tr><td>{e(crit[k])}</td>' + "".join(f'<td class="n">{"—" if h["scores"].get(k) is None else h["scores"][k]}</td>'
                                                              for h in plan["hypotheses"]) + "</tr>" for k in chosen["scores"])
            paths = "".join(f'<li><b>{e(h["ko"]["title"])}</b>: ' + " → ".join(e(D.OP_KO.get(s["op"], s["op"])) for s in h["path"][1:]) + "</li>"
                            for h in plan["hypotheses"])
            inner = (_rh(tk, issue) + f'<div class="span-12"><h2>{e(tk)}</h2><p class="small">표류가 낸 방향 전부와, 같은 일곱 기준. '
                     f'점수는 원장에서 계산한 어림값이지 취향의 판정이 아닙니다(정의는 판권 쪽).</p>'
                     f'<table><tr><th>번호</th><th>방향</th><th>합</th><th>강점</th><th>약점</th></tr>{rows}</table>'
                     f'<h3 class="mt">기준별</h3><table><tr><th></th>' + "".join(f'<th>{e(h["hypothesis_id"])}</th>' for h in plan["hypotheses"])
                     + f'</tr>{sc}</table><h3 class="mt">걸음의 순서</h3><ol class="small chain">{paths}</ol></div>')
            rec = page(p, inner)
        elif sec == "Image Catalogue":
            gen = [a for a in assets if a["asset_type"] == "generated_plate"]
            user = [a for a in assets if a["asset_type"] == "user_photo"]
            off = [a for a in assets if a["asset_type"] == "official_campaign"][:max(0, 12 - len(gen) - len(user))]
            rest = len(assets) - len(gen) - len(user) - len(off)
            ent = "".join(f'<div class="entry">{_fig(a, a["source_title"], rel=out_dir)}<div class="kind">'
                          f'권리 {e(a["rights_status"])} · 수집 {e(a["retrieval_status"])}</div></div>' for a in user + gen + off)
            inner = (_rh(tk, issue) + f'<div class="span-12"><h2>{e(tk)}</h2><p class="small">실은 것: 생성 도면 {len(gen)}장'
                     f'{f", 제공받은 사진 {len(user)}장" if user else ""}. 보류한 것: 이미지를 받지 못했고(접속 차단) 사용 권리도 모르는 '
                     f'공식 페이지들 — 출처로만 적습니다. 나머지 {rest}개 출처는 참고 문헌에 있습니다. 이미지를 찾은 것과 실어도 되는 것은 '
                     f'다른 일입니다.</p></div><div class="entries four">{ent}</div>')
            rec = page(p, inner)
        elif sec == "Critical Review":
            snippet = sum(1 for c in cat["claims"] if CAT.claim_verification(cat, c) != "fulltext")
            nc = "".join(f'<li lang="en">{e(x)}</li>' for x in cat.get("not_checked", [])[:8])
            risks = []
            if snippet:
                risks.append(f"연구 원리 대부분이 검색 조각에 기대고 있습니다(주장 {len(cat['claims'])}개 중 {snippet}개).")
            if chosen["scores"]["brand_relevance"] < 0.5:
                risks.append("브랜드 관련성이 얇습니다 — 연구의 낱말이 끝까지 많이 살아남지 못했습니다.")
            if any(s["op"] == "leap" for s in chosen["path"]):
                risks.append("도약이 들어 있습니다 — 일부러 먼 연결이라 자의적으로 읽힐 수 있습니다.")
            risks.append("실제 캠페인 이미지는 권리를 확인하지 못해 싣지 않았습니다. 지면의 그림은 모두 생성 도면입니다.")
            inner = (_rh(tk, issue) + f'<div class="span-12"><h2>{e(tk)}</h2></div><div class="span-6 small">'
                     f'<h3>이 책이 기대고 있는 것</h3><p>주장 {len(cat["claims"])}개 중 {snippet}개가 검색 결과의 조각에 기댑니다. 브랜드와 '
                     f'매거진 사이트에 직접 접속하는 길이 막혀 원문 쪽을 하나도 열지 못했습니다. 여기 인용한 문구는 원문과 다를 수 있습니다.</p>'
                     f'<h3>고른 방향의 위험</h3><ul>{"".join(f"<li>{e(r)}</li>" for r in risks)}</ul></div>'
                     f'<div class="span-6 small"><h3>확인하지 못한 것 (조사 원장 그대로)</h3><ul>{nc}</ul></div>')
            rec = page(p, inner)
        elif typ == "references":
            ordered = refs.ordered()
            src = CAT.by_id(cat)
            chunks = [ordered[i:i + REFS_PER_PAGE] for i in range(0, len(ordered), REFS_PER_PAGE)]
            kind_ko = {"official": "공식", "press": "언론", "secondary": "2차", "blog": "블로그", "retailer": "판매처", "repository": "저장소"}
            for k, ch in enumerate(chunks):
                lis = "".join(f'<li id="ref-{n}" value="{n}"><span lang="en">{e(src[s]["title"])} — {e(src[s].get("publisher") or "")}.</span> '
                              f'<a href="{e(src[s]["url"])}">{e(src[s]["url"])}</a> <span class="kind">{kind_ko.get(src[s]["kind"], src[s]["kind"])} · '
                              f'{READ_LABEL.get(src[s]["verification"], src[s]["verification"])} · {e(src[s].get("accessed", ""))}</span></li>'
                              for s, n in ch)
                q = dict(p)
                t2 = tk if k == 0 else f"{tk} (이어서)"
                rec = page(q, _rh(t2, issue) + (f'<div class="span-12"><h2>{e(tk)}</h2></div>' if k == 0 else "")
                           + f'<ol class="refs">{lis}</ol>', title_ko=t2)
                rec["sources"] = [s for s, _ in ch]
            continue
        elif typ == "colophon":
            t = tokens
            inner = (_rh(tk, issue) + f'<div class="span-7"><h2>{e(tk)}</h2><p>{e(INDEPENDENCE)}</p>'
                     f'<p class="small">만든 길: <code>python3 -m gentle_monster magazine</code> — 연구 원장 → 표류(SE_NEW DRIFT 규칙: 원장, '
                     f'한 걸음에 연산 하나, 물려받은 낱말을 잰다, 식은 것을 다시 부른다, {D.EVERY}걸음마다 끼어들기, 하드 게이트 둘) → 방향 '
                     f'{len(plan["hypotheses"])}개 → 편집 계획 → HTML → Chromium PDF → QA. 언어 모델은 한 줄도 쓰지 않았습니다. 지면의 글은 '
                     f'연구 원장과 고정된 문장 틀에서 조립했습니다.</p>'
                     f'<p class="small">점수: 출처 추적 = 출처가 있는 원리의 몫 · 개념 거리 = 1 − 출발과 끝의 낱말 겹침 · 브랜드 관련성 = 끝까지 '
                     f'살아남은 반복 연구 낱말 ÷ 4(상한 1) · 편집 일관성과 실현 가능성 = 쪽 유형 / 그릴 수 있는 도판에 대응하는 장치의 몫 · '
                     f'시각 독창성 = 다른 방향이 안 쓰는 장치의 몫.</p></div>'
                     f'<div class="span-5 small"><h3>활자와 격자</h3><p>Liberation Sans · Serif · Mono, 한글은 WenQuanYi Zen Hei. 비율 '
                     f'{DS.RATIO}, 기준선 {DS.BASELINE} pt, {DS.COLS}단, 거터 {DS.GUTTER} mm, 판형 {DS.PAGE_W} × {DS.PAGE_H} mm.</p>'
                     f'<p>종이 {t["color"]["paper"]} · 잉크 {t["color"]["ink"]} · 강조 {t["color"]["accent"]} (고른 분야 — '
                     f'{e(ko["domains"][-1] if ko["domains"] else "")} — 에서). 잉크/종이 대비 {t["contrast"]["ink/paper"]}:1.</p></div>')
            rec = page(p, inner)
        else:
            rec = page(p, _rh(tk, issue) + f'<div class="span-12"><h2>{e(tk)}</h2></div>')
        if pl:
            rec["assets"].append(pl["asset_id"])

    nav = "".join(f'<a href="#{r["id"]}">{r["folio"]:02d} {e(r["title_ko"])}</a>' for r in rendered)
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{e(title)}</title><meta name="description" content="{e(INDEPENDENCE)}">'
           f'<meta name="brief" content="{e(brief["text"])}"><style>{DS.css(tokens)}</style></head><body>'
           f'<nav class="nav" aria-label="쪽">{nav}</nav><main>{"".join(body)}</main>'
           f'<script>{QA_JS}</script></body></html>')
    path = out_dir / "index.html"
    path.write_text(doc, encoding="utf-8")
    return {"html": str(path), "pages": rendered, "cited": dict(refs.num)}


def _experiment(p, h, cat, claims, refs, pl, out_dir, tag) -> str:
    dev = p.get("device")
    label, ptype, _plate = D.DEVICES[dev]
    lab = D.DEVICE_KO[dev]
    ko = h["ko"]
    head = f'<div class="span-12">{tag}<h2>{e(ko["title"])}</h2><p class="small"><b>규칙.</b> {e(ko["rule"])}</p></div>'
    gm = [claims[c["claim"]] for c in h["observed_principles"] if c["claim"] in claims][:6]
    gm += [c for c in cat["claims"] if c["subject"] in CAT.GM_SUBJECTS and c not in gm][:6 - len(gm)]
    if ptype == "catalogue":
        prefix = {"lot_entry": "출품", "find_number": "출토", "tag_entry": "꼬리표", "specimen_plate": "표본"}.get(dev, "번호")
        ent = "".join(f'<div class="entry"><div class="no">{prefix} {i + 1:02d}</div><p class="quote" lang="en">{e(_short(c["evidence"]))}'
                      f'{refs.cite(c["source_ids"])}</p><div class="kind">출처: {e(subj(c["subject"]))} · {KIND_LABEL[c["kind"]]}</div></div>'
                      for i, c in enumerate(gm))
        return head + _fig(pl, f"도판 — {lab}.", "span-12", rel=out_dir) + f'<div class="entries">{ent}</div>'
    if ptype == "multi_column":
        rows = "".join(f'<tr><td class="n">{i:02d}</td><td>{e(D.OP_KO.get(s["op"], s["op"]))}</td><td lang="en">{e(s["label"][:80])}</td>'
                       f'<td class="n">{"" if not s.get("measure") else str(s["measure"].get("new")) + " / " + str(s["measure"].get("kept"))}</td></tr>'
                       for i, s in enumerate(h["path"]))
        return head + (f'<div class="span-12"><p class="small">{e(lab)}: 표류 그 자체를 일지로 적는다. 새것 / 이어받음 = 앞 걸음에 더한 낱말 / '
                       f'가져온 낱말(2개 이상이어야 물려받은 것으로 친다).</p><table><tr><th>걸음</th><th>연산</th><th>항목</th><th>새것 / 이어받음</th>'
                       f'</tr>{rows}</table></div>')
    if ptype == "single_column":
        items = "".join(f'<li><b>{e(D.OP_KO.get(s["op"], s["op"]))}</b> — <span lang="en">{e(s["label"][:110])}</span></li>' for s in h["path"])
        src = "".join(f'<li class="quote" lang="en">{e(_short(c["evidence"], 120))}{refs.cite(c["source_ids"])}</li>' for c in gm[:4])
        return head + (f'<div class="span-7"><h3>{e(lab)}</h3><ol class="chain small">{items}</ol></div>'
                       f'<div class="span-5 small"><h3>출발한 자리</h3><ul>{src}</ul></div>')
    if ptype == "typographic":
        kept = ko["rule"].split("이어받은 낱말: ")[-1].rstrip(".").split(", ") if "이어받은 낱말" in ko["rule"] else []
        words = (kept + ["다시", "가까이", "보기"])[:7]
        size, lines = 4.2, []
        for w in words:
            lines.append(f'<div style="font-size:{size:.2f}em">{e(w.upper())}</div>')
            size *= 0.72
        return head + f'<div class="chart">{"".join(lines)}</div>' + _fig(pl, f"도판 — {lab}.", "start-5", rel=out_dir)
    if ptype == "full_bleed":
        return (_fig(pl, f"{lab}.", rel=out_dir) + f'<div class="over">{tag}<h3>{e(ko["title"])}</h3>'
                f'<p class="small">{e(ko["experience"])}.</p></div>')
    if ptype == "image_essay":
        return head + _fig(pl, f"도판 — {lab}.", "span-8", rel=out_dir) + (
            f'<div class="span-4 small"><p>{e(ko["image"])}.</p><p>{e(ko["content"])}.</p></div>')
    if ptype == "asymmetric":
        cues = "".join(f'<li><b>Q{i}</b> {e(D.OP_KO.get(s["op"], s["op"]))} — <span lang="en">{e(s["label"][:60])}</span></li>'
                       for i, s in enumerate(h["path"][1:], 1))
        return head + _fig(pl, f"도판 — {lab}.", "span-7", rel=out_dir) + f'<div class="span-5 small"><ol class="chain">{cues}</ol></div>'
    notes = "".join(f'<p><b>{i + 1}.</b> <span class="quote" lang="en">{e(_short(c["evidence"], 140))}</span>{refs.cite(c["source_ids"])}</p>'
                    for i, c in enumerate(gm[:4]))
    return head + _fig(pl, f"도판 — {lab}. 그린 것이지 잰 것이 아닙니다.", "span-8", rel=out_dir) + f'<div class="span-4 small">{notes}</div>'
