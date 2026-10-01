"use strict";
/* World Trip — 화면. 엔진의 판정을 그대로 보여 준다. 수를 여기서 만들지 않는다. */
(function () {
  const $ = (s, r) => (r || document).querySelector(s);
  const NS = "http://www.w3.org/2000/svg";
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 없어도 돈다 */ } },
  };
  const TAG_KO = { history: "역사", art: "예술", culture: "문화", architecture: "건축", nature: "자연", food: "음식",
    nightlife: "밤", shopping: "쇼핑", family: "가족", views: "전망", religion: "종교" };
  const MODE_KO = { flight: "항공", train: "열차", night_train: "야간열차", bus: "버스", ferry: "페리" };
  const CAT_KO = { transport: "이동", airport: "공항 이동", lodging: "숙소", food: "식비", local_transit: "시내교통",
    attractions: "입장료", activities: "활동" };
  let WORLD = null;
  let LAST = null;
  const REDUCED = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  // 엔진 주소: ?api= > 저장한 값 > <meta name="worldtrip-api"> > 같은 출처("")
  const API = (() => {
    const q = new URLSearchParams(location.search).get("api");
    if (q !== null) store.set("worldtrip.api", q);
    const meta = document.querySelector('meta[name="worldtrip-api"]');
    return ((q !== null ? q : store.get("worldtrip.api")) || (meta && meta.content) || "").replace(/\/+$/, "");
  })();

  function el(tag, attrs, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") n.className = v;
      else if (k === "style") Object.assign(n.style, v);
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? "" : v);
    }
    for (const c of kids.flat(Infinity)) {
      if (c === null || c === undefined || c === false) continue;
      n.append(c instanceof Node ? c : document.createTextNode(String(c)));
    }
    return n;
  }
  function s(tag, attrs, ...kids) {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) if (v !== null && v !== undefined) n.setAttribute(k, v);
    for (const c of kids.flat()) if (c) n.append(c instanceof Node ? c : document.createTextNode(String(c)));
    return n;
  }
  const won = (n) => (n === null || n === undefined) ? "—" : Math.round(n).toLocaleString("ko-KR") + "원";
  const man = (n) => (n === null || n === undefined) ? "—" : (n >= 1e8 ? (n / 1e8).toFixed(2) + "억" : Math.round(n / 1e4).toLocaleString("ko-KR") + "만");
  const range = (a, b) => a === b ? man(a) : `${man(a)}–${man(b)}`;
  const lvl = (l) => el("span", { class: "lvl" + (l === "user" ? " user" : "") }, l === "snippet" ? "조각" : l === "user" ? "사용자" : l === "full" ? "원문" : l);
  const src = (so) => so && so.url ? el("a", { class: "src", href: so.url, target: "_blank", rel: "noopener noreferrer" },
    new URL(so.url).hostname.replace(/^www\./, "")) : null;

  async function api(path, body) {
    const headers = { "Content-Type": "application/json" };
    const tok = store.get("worldtrip.token");
    if (tok) headers.Authorization = "Bearer " + tok;
    const r = await fetch(API + path, body === undefined ? { headers } : { method: "POST", headers, body: JSON.stringify(body) });
    const d = await r.json().catch(() => ({ error: "응답이 JSON 이 아니다" }));
    if (!r.ok) throw new Error(d.error || "HTTP " + r.status);
    return d;
  }

  /* ---------------- map (등장방형 투영, 경계에 맞춤) ---------------- */
  function routeMap(box, opts) {
    const { coords, names, edges, route, highlight } = opts;
    const ids = (route && route.length ? route : Object.keys(coords)).filter((c) => coords[c]);
    const pts = ids.map((c) => coords[c]);
    let la0 = Math.min(...pts.map((p) => p[0])), la1 = Math.max(...pts.map((p) => p[0]));
    let lo0 = Math.min(...pts.map((p) => p[1])), lo1 = Math.max(...pts.map((p) => p[1]));
    const padLa = Math.max(3, (la1 - la0) * .18), padLo = Math.max(5, (lo1 - lo0) * .12);
    la0 -= padLa; la1 += padLa; lo0 -= padLo; lo1 += padLo;
    const W = 1600, H = 900;
    // 종횡비를 지킨다 -- 지도가 늘어나 보이면 거리를 잘못 읽는다
    const sx = W / (lo1 - lo0), sy = H / (la1 - la0), k = Math.min(sx, sy);
    const ox = (W - (lo1 - lo0) * k) / 2, oy = (H - (la1 - la0) * k) / 2;
    const P = (c) => [ox + (coords[c][1] - lo0) * k, oy + (la1 - coords[c][0]) * k];
    const g = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "도시와 연결" });
    for (let x = Math.ceil(lo0 / 10) * 10; x <= lo1; x += 10) {
      const X = ox + (x - lo0) * k;
      g.append(s("line", { x1: X, y1: 0, x2: X, y2: H, stroke: "currentColor", "stroke-opacity": .08, "stroke-width": 1 }));
    }
    for (let y = Math.ceil(la0 / 10) * 10; y <= la1; y += 10) {
      const Y = oy + (la1 - y) * k;
      g.append(s("line", { x1: 0, y1: Y, x2: W, y2: Y, stroke: "currentColor", "stroke-opacity": .08, "stroke-width": 1 }));
    }
    const inView = new Set(ids);
    for (const e of edges || []) {
      if (!coords[e.from] || !coords[e.to]) continue;
      if (route && route.length && !(inView.has(e.from) && inView.has(e.to))) continue;
      const [x1, y1] = P(e.from), [x2, y2] = P(e.to);
      g.append(s("line", { x1, y1, x2, y2, stroke: "currentColor", "stroke-opacity": .22, "stroke-width": 1.2,
        "stroke-dasharray": e.mode === "flight" ? "6 6" : null }));
    }
    if (route && route.length > 1) {
      for (let i = 0; i < route.length - 1; i++) {
        const [x1, y1] = P(route[i]), [x2, y2] = P(route[i + 1]);
        const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - Math.min(140, Math.hypot(x2 - x1, y2 - y1) * .18);
        g.append(s("path", { d: `M${x1},${y1} Q${mx},${my} ${x2},${y2}`, fill: "none", stroke: "var(--accent)", "stroke-width": 3.2 }));
      }
    }
    const order = {};
    (route || []).forEach((c, i) => { if (!(c in order)) order[c] = i; });
    for (const c of ids) {
      const [x, y] = P(c);
      const on = c in order || (highlight && highlight.has(c));
      g.append(s("circle", { cx: x, cy: y, r: on ? 9 : 5, fill: on ? "var(--accent)" : "currentColor", "fill-opacity": on ? 1 : .55 }));
      const t = s("text", { x: x + 13, y: y + 5, "font-size": on ? 26 : 20, "font-weight": on ? 700 : 500,
        fill: "currentColor", "font-family": "Archivo, Arial, sans-serif" }, (c in order && route ? String(order[c]).padStart(2, "0") + " " : "") + (names[c] || c));
      g.append(t);
    }
    box.replaceChildren(g);
  }

  /* ---------------- brief ---------------- */
  function chip(name, value, label, opts) {
    const o = opts || {};
    return el("label", { class: "chip" + (o.na ? " na" : ""), title: o.title || null },
      el("input", { type: o.radio ? "radio" : "checkbox", name, value, checked: !!o.checked }), label);
  }
  function buildBrief() {
    const f = $("#brief");
    const d = new Date(Date.now() + 30 * 864e5);
    f.start_date.value = d.toISOString().slice(0, 10);
    const ints = $("#interests");
    for (const [k, v] of Object.entries(TAG_KO)) ints.append(chip("interests", k, v, { checked: k === "art" || k === "history" }));
    const regs = $("#regions");
    for (const r of WORLD.regions) regs.append(chip("regions", r.id, r.name_ko, { checked: r.id.includes("europe") }));
    const must = $("#must");
    for (const r of WORLD.regions) for (const k of r.countries) for (const c of k.cities) {
      if (c.id === "seoul") continue;
      const na = !c.plannable_tiers.length;
      must.append(chip("must", c.id, c.name_ko, { na, title: na ? "원장에 비용이 비어 있다 — 고르면 '모름' 으로 거절될 수 있다" : null }));
    }
    f.addEventListener("submit", (ev) => { ev.preventDefault(); runPlan(); });
  }
  function readBrief() {
    const f = $("#brief");
    const all = (n) => [...f.querySelectorAll(`input[name="${n}"]:checked`)].map((x) => x.value);
    const num = (n) => f[n].value === "" ? null : Number(f[n].value);
    return {
      origin: "seoul", start_date: f.start_date.value, nights: num("nights"), travelers: num("travelers"),
      budget_krw: num("budget_krw") || null, style: all("style")[0], budget_basis: all("budget_basis")[0],
      interests: all("interests"), must: all("must"), regions: all("regions").length ? all("regions") : null,
      max_cities: num("max_cities"), default_min_nights: num("default_min_nights"),
    };
  }
  async function runPlan() {
    const btn = $(".go");
    btn.disabled = true;
    $("#result").replaceChildren(el("p", { class: "loading" }, "조합을 전수하고, 심판이 다시 더하는 중…"));
    try {
      const req = readBrief();
      const r = await api("/api/plan", { request: req });
      LAST = { r, req };
      renderPlan(r, req);
      $("#result").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "start" });
    } catch (e) {
      $("#result").replaceChildren(el("p", { class: "v" }, "오류: " + e.message));
    } finally { btn.disabled = false; }
  }

  /* ---------------- result ---------------- */
  function renderPlan(r, req) {
    const out = $("#result");
    out.replaceChildren();
    const ok = r.verdict === "ACCEPT";
    const head = el("section", { class: "spread" },
      el("div", { class: "verdict" },
        el("p", { class: "stamp " + (ok ? "ok" : "bad") }, ok ? "Accept" : "Reject"),
        el("div", {}, el("p", { class: "cap" }, "Verdict · 심판"), el("p", { class: "h-l" }, r.reason || ""),
          r.evidence ? el("p", { class: "banner" }, r.evidence.banner) : null)));
    out.append(head);
    if (r.input_errors) { head.append(el("ul", { class: "small v" }, r.input_errors.map((e) => el("li", {}, e)))); return; }
    if (r.diagnostics && r.diagnostics.length) head.append(el("div", { class: "box", style: { marginTop: "16px" } },
      el("p", { class: "cap" }, "왜"), el("ul", { class: "small" }, r.diagnostics.map((d) => el("li", {}, d)))));
    if (!r.itinerary) return;
    const it = r.itinerary, b = r.budget;
    head.append(el("div", { class: "kv" },
      el("div", {}, el("span", {}, "Route"), el("b", {}, it.route_ko.join(" → "))),
      el("div", {}, el("span", {}, "Total · 범위"), el("b", { class: "num" }, range(b.min, b.max))),
      el("div", {}, el("span", {}, "1인당"), el("b", { class: "num" }, range(b.per_person[0], b.per_person[1]))),
      el("div", {}, el("span", {}, b.budget_krw ? (b.basis === "mid" ? "예산 · 가운데값 판정" : "예산 · 최대가 판정") : "예산 없음"),
        el("b", { class: "num" }, b.budget_krw ? man(b.budget_krw) : "—"))));
    head.append(el("div", { class: "actions" },
      el("button", { class: "btn", type: "button", onclick: () => showBlueprint(r, req) }, "청사진 보기 · A3"),
      el("a", { class: "btn", href: "#ledger" }, "원장 #" + (r.ledger ? r.ledger.seq : "—"))));

    // Route
    const map = el("div", { class: "mapbox" });
    const legs = el("ol", { class: "legs" }, it.legs.map((l) => el("li", {},
      el("div", {}, el("b", {}, `${l.from_ko} → ${l.to_ko}`), el("span", { class: "mode" }, MODE_KO[l.mode] || l.mode),
        el("div", { class: "xs muted" }, (l.hours ? `${l.hours}시간` : "시간 모름") + (l.notes_ko ? " · " + l.notes_ko : ""))),
      el("div", { class: "num small" }, range(l.price_krw[0], l.price_krw[1]), lvl(l.price.source.level), el("br"), src(l.price.source)))));
    out.append(el("section", { class: "spread" },
      el("div", { class: "sect-head" }, el("div", {}, el("p", { class: "cap" }, "02 · The route"), el("h2", { class: "h-xl" }, "경로")),
        el("p", { class: "small muted" }, `이동 ${it.transit_hours}시간 · 관심사 점수 ${it.value}`)),
      el("div", { class: "two" }, map, el("div", {}, legs))));
    routeMap(map, { coords: WORLD.coords, names: WORLD.names_ko, edges: WORLD.edges, route: it.route });

    // Days
    out.append(el("section", { class: "spread" },
      el("div", { class: "sect-head" }, el("div", {}, el("p", { class: "cap" }, "03 · The days"), el("h2", { class: "h-xl" }, `${it.days.length}일`)),
        el("p", { class: "small muted" }, "도착일 4시간 · 다른 날 8시간. 시간을 모르는 명소는 2시간으로 잡았다.")),
      el("div", { class: "days" }, it.days.map((d) => el("div", { class: "day" + (d.free ? " free" : "") },
        el("div", { class: "d" }, d.date.slice(5).replace("-", ".") + " · " + new Date(d.date + "T00:00").toLocaleDateString("ko-KR", { weekday: "short" })),
        el("div", { class: "c" }, d.city_ko),
        d.attraction_names.length ? el("ul", {}, d.attraction_names.map((n) => el("li", {}, n))) : el("div", { class: "small muted" }, "자유일"),
        d.suggest && d.suggest.length ? el("div", { class: "sug" }, "제안 · " + d.suggest.join(", ") + " (예산 미포함)") : null,
        el("div", { class: "meter" }, el("i", { style: { width: Math.min(100, 100 * d.hours / d.capacity_h) + "%" } })))))));

    // Budget
    const maxv = Math.max(b.max, b.budget_krw || 0) || 1;
    const bars = el("div", { class: "bars" }, Object.entries(b.by_category).sort((x, y) => y[1].max - x[1].max).map(([k, v]) =>
      el("div", { class: "barrow" }, el("span", {}, CAT_KO[k] || k),
        el("div", { class: "track" }, el("i", { class: "lo", style: { width: (100 * v.min / maxv) + "%" } }),
          el("i", { class: "hi", style: { left: (100 * v.min / maxv) + "%", width: (100 * (v.max - v.min) / maxv) + "%" } })),
        el("span", { class: "num small" }, range(v.min, v.max)))));
    const total = el("div", { class: "barrow" }, el("b", {}, "합계"),
      el("div", { class: "track" }, el("i", { class: "lo", style: { width: (100 * b.min / maxv) + "%" } }),
        el("i", { class: "hi", style: { left: (100 * b.min / maxv) + "%", width: (100 * (b.max - b.min) / maxv) + "%" } }),
        b.budget_krw ? el("i", { style: { position: "absolute", top: "-4px", bottom: "-4px", width: "2px", background: "var(--accent)", left: (100 * b.budget_krw / maxv) + "%" }, title: "예산" }) : null),
      el("b", { class: "num small" }, range(b.min, b.max)));
    const table = el("div", { class: "tblwrap" }, el("table", {},
      el("thead", {}, el("tr", {}, el("th", {}, "항목"), el("th", {}, "근거"), el("th", { class: "r" }, "최소"), el("th", { class: "r" }, "최대"))),
      el("tbody", {}, b.lines.map((ln) => el("tr", {}, el("td", {}, ln.label), el("td", {}, lvl(ln.level)),
        el("td", { class: "r num" }, won(ln.min)), el("td", { class: "r num" }, won(ln.max)))))));
    out.append(el("section", { class: "spread" },
      el("div", { class: "sect-head" }, el("div", {}, el("p", { class: "cap" }, "04 · The budget"), el("h2", { class: "h-xl" }, "예산 보드")),
        el("p", { class: "small muted" }, "막대: 진한 부분 = 최소, 빗금 = 최대까지의 폭, 붉은 선 = 예산")),
      el("div", { class: "two" }, el("div", {}, bars, el("div", { style: { height: "14px" } }), total,
        b.unknown.length ? el("p", { class: "small v" }, "모름(0 이 아니다): " + b.unknown.join(", ")) : null,
        b.excluded.length ? el("p", { class: "small muted" }, "포함 안 함: " + b.excluded.join(", ")) : null), table)));

    // Cities
    for (const c of it.cities) out.append(citySpread(c, req));

    // Alternatives
    if (r.alternatives && r.alternatives.length) out.append(el("section", { class: "spread" },
      el("p", { class: "cap" }, "06 · Alternatives"), el("h2", { class: "h-l" }, "다른 안"),
      el("ul", { class: "alts" }, r.alternatives.map((a) => el("li", {},
        el("div", {}, el("b", {}, a.route_ko.join(" → ")), el("div", { class: "xs muted" },
          Object.entries(a.nights).map(([k, n]) => `${WORLD.names_ko[k] || k} ${n}박`).join(" · ") + ` · 점수 ${a.value} · 이동 ${a.transit_hours}h`
          + (a.unknown.length ? " · 모름: " + a.unknown.join(", ") : ""))),
        el("div", { class: "num small" + (a.fits_budget ? "" : " v") }, range(a.min, a.max), a.fits_budget ? "" : " · 예산 밖"))))));

    // fine print
    out.append(el("section", { class: "spread" }, el("p", { class: "cap" }, "Colophon · 이 판정의 조건"),
      el("div", { class: "fine" },
        el("div", {}, el("p", { class: "cap" }, "무효가 되는 조건"), el("ul", {}, r.invalidated_if.map((x) => el("li", {}, x)))),
        el("div", {}, el("p", { class: "cap" }, "재지 않은 것"), el("ul", {}, r.not_checked.map((x) => el("li", {}, x)))),
        el("div", {}, el("p", { class: "cap" }, "심판"), el("ul", {}, r.judge.checks_run.map((x) => el("li", {}, x))),
          r.judge.violations.length ? el("ul", { class: "v" }, r.judge.violations.map((v) => el("li", {}, `[${v.check}] ${v.message}`))) : null,
          el("p", { class: "xs muted" }, r.search.method + " · 조합 " + r.search.combinations + "개")))));
  }

  function citySpread(c, req) {
    const att = el("ul", { class: "items" }, c.attraction_detail.map((a) => el("li", {},
      el("b", {}, a.name_ko || a.name), a.reservation ? el("span", { class: "res" }, "예약") : null,
      el("span", { class: "num small" }, " · " + (a.price_krw[1] === 0 ? "무료" : range(a.price_krw[0], a.price_krw[1])), lvl(a.price.source.level)),
      el("span", { class: "tip" }, (a.hours_known ? `${a.hours}시간 · ` : "시간 모름(2시간으로 잡음) · ") + (a.tip_ko || "")), src(a.price.source))));
    const rest = el("ul", { class: "items" }, c.restaurants.length ? c.restaurants.map((x) => el("li", {},
      el("span", { class: "tag" }, x.kind || ""), el("b", {}, x.name), el("span", { class: "num small" }, " · " + won(x.price.min) + (x.price.max !== x.price.min ? "~" : "")),
      el("span", { class: "tip" }, x.tip_ko || ""), src(x.price.source))) : el("li", { class: "muted" }, "원장에 식당이 없다 — 지어내지 않는다"));
    const acts = el("ul", { class: "items" }, c.activities.length ? c.activities.map((x) => el("li", {},
      el("b", {}, x.name_ko || x.name), el("span", { class: "num small" }, " · " + won(x.price.min) + (x.price.max !== x.price.min ? "~" : "")), src(x.price.source))) :
      el("li", { class: "muted" }, "원장에 활동이 없다"));
    const conc = c.concerns.length ? el("ol", { class: "concerns" }, c.concerns.map((x) => el("li", {},
      el("span", { class: "tag" }, x.topic), x.text_ko, " ", src(x.source)))) : el("p", { class: "small muted" }, "원장에 고민이 없다");
    const revs = c.reviews.length ? c.reviews.map((x) => el("div", { class: "rev" },
      el("span", { class: "sent " + x.sentiment, title: x.sentiment }), el("b", {}, x.about), el("div", {}, x.summary_ko), src(x.source))) :
      [el("p", { class: "small muted" }, "원장에 후기가 없다 — 지어내지 않는다")];
    return el("section", { class: "city" },
      el("div", {}, el("p", { class: "cap" }, `05 · ${c.country_ko} · ${c.nights}박`), el("h2", { class: "cityname" }, c.name),
        el("p", { class: "cityko" }, c.name_ko), el("p", { class: "small muted" }, `${c.arrive} → ${c.depart} · ${c.tz}`),
        c.season_note ? el("p", { class: "small v" }, c.season_note) : null,
        c.transit && c.transit.pass ? el("div", { class: "box", style: { marginTop: "16px" } }, el("p", { class: "cap" }, "교통 패스"),
          el("p", { class: "small" }, el("b", {}, c.transit.pass.name), " · " + won(c.transit.pass.price.min) + "~", el("br"), el("span", { class: "muted" }, c.transit.pass.covers || ""))) : null,
        c.transit && c.transit.airport ? el("div", { class: "box", style: { marginTop: "12px" } }, el("p", { class: "cap" }, "공항"),
          el("p", { class: "small" }, el("b", {}, c.transit.airport.name), " · " + won(c.transit.airport.price.min) + "~" + (c.transit.airport.minutes ? ` · ${c.transit.airport.minutes}분` : ""))) : null),
      el("div", {},
        el("div", { class: "grid3" },
          el("div", { class: "box" }, el("p", { class: "cap" }, "보는 것"), att),
          el("div", { class: "box" }, el("p", { class: "cap" }, "먹는 곳 · " + req.style), rest, el("p", { class: "cap", style: { marginTop: "18px" } }, "할 것"), acts),
          el("div", { class: "box" }, el("p", { class: "cap" }, "여행자의 고민"), conc)),
        el("div", { class: "box", style: { marginTop: "22px" } }, el("p", { class: "cap" }, "후기 · 원문을 바꿔 쓴 요약"), revs)));
  }

  /* ---------------- 청사진 (A3 가로) ---------------- */
  function showBlueprint(r, req) {
    const it = r.itinerary, b = r.budget;
    const bp = $("#blueprint");
    const plan = el("div", { class: "mapbox", style: { flex: "1", minHeight: "0", border: "0", background: "#fff", color: "#15191b", aspectRatio: "auto" } });
    const cats = Object.entries(b.by_category);
    const sheet = el("div", { class: "sheet" },
      el("div", { class: "pl" }, el("p", { class: "cap", style: { margin: 0 } }, "Sheet A-01 · Route plan"), plan,
        el("p", { class: "cap2", style: { padding: 0 } }, "등장방형 투영, 축척 없음. 붉은 선 = 경로, 점선 = 원장의 다른 항공 연결, 실선 = 지상 연결.")),
      el("div", { class: "mid" },
        el("div", { class: "cap2" }, "Sequence · " + it.days.length + " days"),
        el("div", { class: "daygrid" }, it.days.map((d, i) => el("div", { class: "dg" },
          el("span", {}, String(i + 1).padStart(2, "0") + " · " + d.date.slice(5)), el("b", {}, d.city_ko),
          el("span", {}, d.attraction_names.join(" · ") || (d.suggest && d.suggest.length ? "자유 — " + d.suggest[0] : "자유"))))),
        el("div", { class: "cap2" }, "Legs · " + it.legs.map((l) => `${l.from_ko}→${l.to_ko} ${MODE_KO[l.mode]}${l.hours ? " " + l.hours + "h" : ""}`).join("  /  "))),
      el("div", { class: "sd" },
        el("div", {}, el("div", { class: "no" }, "WORLD TRIP"), el("h2", {}, it.route_ko.slice(1, it.route_ko.length - (req.return_to === null ? 0 : 1)).join(" · ")),
          el("p", { class: "subt" }, `${req.start_date} 출발 · ${req.nights}박 · ${req.travelers}인 · ${req.style}`),
          el("dl", {}, el("dt", {}, "Verdict"), el("dd", {}, r.verdict + " — " + r.reason),
            el("dt", {}, "Budget"), el("dd", {}, b.budget_krw ? won(b.budget_krw) + (b.basis === "mid" ? " (가운데값 판정)" : " (최대가 판정)") : "없음"),
            el("dt", {}, "Total"), el("dd", {}, won(b.min) + " – " + won(b.max)),
            el("dt", {}, "Evidence"), el("dd", {}, r.evidence.banner),
            el("dt", {}, "Ledger"), el("dd", {}, r.ledger ? `#${r.ledger.seq} · ${r.ledger.hash.slice(0, 16)}…` : "—"),
            el("dt", {}, "Tools"), el("dd", {}, "worldtrip · tree × graph · Held-Karp · deterministic judge"))),
        el("div", {}, el("h3", {}, "Design intent"), el("ol", { style: { margin: 0, paddingLeft: "16px", color: "#5b656b" } },
          el("li", {}, el("b", { style: { color: "#15191b" } }, "도시는 그래프로. "), "직접 연결이 원장에 있는 순서만 만든다."),
          el("li", {}, el("b", { style: { color: "#15191b" } }, "나라는 트리로. "), "같은 나라는 한 번에, 나라 하한으로 예산 밖 조합을 자른다."),
          el("li", {}, el("b", { style: { color: "#15191b" } }, "모르는 값은 0 이 아니다. "), "핵심 비용이 비면 거절한다."),
          el("li", {}, el("b", { style: { color: "#15191b" } }, "심판은 따로 센다. "), "날짜별로 다시 더해 생성자와 맞춘다."))),
        el("div", {}, el("h3", {}, "Budget programme (KRW)"), el("table", {}, cats.map(([k, v]) => el("tr", {},
          el("td", {}, CAT_KO[k] || k), el("td", { class: "r" }, man(v.min) + "–" + man(v.max)),
          el("td", { style: { width: "34%" } }, el("i", { style: { width: (100 * v.max / (b.max || 1)).toFixed(1) + "%" } })))))),
        el("div", { class: "xs", style: { color: "#5b656b" } }, "Status: 계획. 값은 2026-10-01 검색 조각 — 예약 전 출처 확인. " + r.not_checked[0])));
    const bar = el("div", { class: "bp-bar" },
      el("button", { class: "btn", type: "button", onclick: () => { document.body.classList.add("print-blueprint"); window.print(); } }, "인쇄 · PDF"),
      el("button", { class: "btn", type: "button", onclick: () => { bp.hidden = true; document.body.classList.remove("print-blueprint"); } }, "닫기"));
    bp.replaceChildren(bar, sheet);
    bp.hidden = false;
    routeMap(plan, { coords: WORLD.coords, names: WORLD.names_ko, edges: WORLD.edges, route: it.route });
    const fit = () => { const k = Math.min(1, (window.innerWidth - 48) / 1587); sheet.style.transform = `scale(${k})`; sheet.style.marginBottom = `${-1123 * (1 - k)}px`; };
    fit();
    window.addEventListener("resize", fit, { once: true });
  }
  window.addEventListener("afterprint", () => document.body.classList.remove("print-blueprint"));

  /* ---------------- explore ---------------- */
  function covDots(c) {
    const k = c.known;
    const bits = [["숙소", k.lodging.length], ["식비", k.food.length], ["교통", k.transit_day], ["명소", k.attractions], ["고민", k.concerns], ["후기", k.reviews]];
    return el("span", { class: "cov", title: bits.map(([n, v]) => `${n} ${v ? "있음" : "모름"}`).join(" · ") },
      bits.map(([, v]) => el("i", { class: v ? "y" : "" })));
  }
  function renderExplore() {
    const tree = $("#tree");
    tree.replaceChildren();
    for (const r of WORLD.regions) {
      tree.append(el("h3", {}, r.name_ko));
      for (const k of r.countries) {
        const bnd = k.bounds.min_night_plus_food_krw;
        tree.append(el("h4", {}, k.name_ko + " ", el("span", { class: "xs muted" },
          Object.keys(bnd).length ? "1박+식비 하한 " + Object.entries(bnd).map(([t, v]) => `${t} ${man(v)}`).join(" · ") : "하한 모름")));
        for (const c of k.cities) tree.append(el("button", { class: "cityrow", type: "button", "aria-pressed": "false",
          onclick: (ev) => { tree.querySelectorAll(".cityrow").forEach((b) => b.setAttribute("aria-pressed", "false")); ev.currentTarget.setAttribute("aria-pressed", "true"); openCity(c.id); } },
          el("span", {}, c.name_ko + " ", el("span", { class: "xs muted" }, c.name)), covDots(c)));
      }
    }
    routeMap($("#explore-map"), { coords: WORLD.coords, names: WORLD.names_ko, edges: WORLD.edges, route: null });
  }
  async function openCity(id) {
    const g = $("#guide");
    g.replaceChildren(el("p", { class: "loading" }, "불러오는 중…"));
    const d = await api("/api/city", { city: id, style: "mid" });
    const cost = (p) => p ? range(p[0], p[1]) : "모름";
    g.replaceChildren(...[
      el("p", { class: "cap" }, d.city.country_ko + " · " + d.city.tz), el("h2", { class: "cityname" }, d.city.name), el("p", { class: "cityko" }, d.city.name_ko),
      el("div", { class: "kv" },
        el("div", {}, el("span", {}, "호스텔/박"), el("b", { class: "num" }, cost(d.costs_krw.lodging.hostel))),
        el("div", {}, el("span", {}, "중급/박"), el("b", { class: "num" }, cost(d.costs_krw.lodging.mid))),
        el("div", {}, el("span", {}, "식비 mid/일"), el("b", { class: "num" }, cost(d.costs_krw.food_per_day.mid))),
        el("div", {}, el("span", {}, "시내교통/일"), el("b", { class: "num" }, cost(d.costs_krw.transit_day)))),
      d.missing_for_style.length ? el("p", { class: "small v" }, "mid 등급 계획에 모자란 것: " + d.missing_for_style.join(", ")) : null,
      el("div", { class: "grid3", style: { marginTop: "18px" } },
        el("div", { class: "box" }, el("p", { class: "cap" }, "명소"), el("ul", { class: "items" }, d.attractions.map((a) => el("li", {},
          el("b", {}, a.name_ko || a.name), el("span", { class: "num small" }, " · " + (a.price_krw[1] === 0 ? "무료" : range(a.price_krw[0], a.price_krw[1]))),
          el("span", { class: "tip" }, a.tip_ko || ""), src(a.price.source))))),
        el("div", { class: "box" }, el("p", { class: "cap" }, "식당 · 활동"), el("ul", { class: "items" },
          d.restaurants.concat(d.activities).map((x) => el("li", {}, el("b", {}, x.name_ko || x.name), el("span", { class: "num small" }, " · " + cost(x.price_krw)), src(x.price.source))),
          (!d.restaurants.length && !d.activities.length) ? el("li", { class: "muted" }, "없음") : null)),
        el("div", { class: "box" }, el("p", { class: "cap" }, "여행자의 고민"), d.concerns.length ? el("ol", { class: "concerns" },
          d.concerns.map((x) => el("li", {}, x.text_ko, " ", src(x.source)))) : el("p", { class: "small muted" }, "없음"))),
      d.reviews.length ? el("div", { class: "box", style: { marginTop: "18px" } }, el("p", { class: "cap" }, "후기"), d.reviews.map((x) =>
        el("div", { class: "rev" }, el("span", { class: "sent " + x.sentiment }), el("b", {}, x.about), el("div", {}, x.summary_ko), src(x.source)))) : null,
      d.gaps.length ? el("div", { class: "box", style: { marginTop: "18px" } }, el("p", { class: "cap" }, "조사의 빈칸"), el("ul", { class: "small muted" }, d.gaps.map((x) => el("li", {}, x)))) : null,
      el("p", { class: "xs muted" }, d.note)].filter(Boolean));
  }

  /* ---------------- ledger ---------------- */
  async function renderLedger() {
    const box = $("#ledger-body");
    box.replaceChildren(el("p", { class: "loading" }, "불러오는 중…"));
    const [lg, st] = await Promise.all([api("/api/ledger"), api("/api/status")]);
    const S = st.stats;
    box.replaceChildren(
      el("div", { class: "kv" },
        el("div", {}, el("span", {}, "판정 원장"), el("b", { class: lg.chain.ok ? "" : "v" }, lg.chain.ok ? "사슬 성함" : "끊김")),
        el("div", {}, el("span", {}, "판정 수"), el("b", {}, lg.chain.entries)),
        el("div", {}, el("span", {}, "도시 · 연결"), el("b", {}, `${S.cities} · ${S.edges}`)),
        el("div", {}, el("span", {}, "원문 확인 수"), el("b", { class: "v" }, `${S.prices_by_level.full || 0} / ${Object.values(S.prices_by_level).reduce((a, b) => a + b, 0)}`))),
      el("p", { class: "banner" }, st.honest_note),
      el("div", { class: "two", style: { marginTop: "20px" } },
        el("div", {}, el("p", { class: "cap" }, "최근 판정"), el("ul", { class: "items" }, lg.recent.slice().reverse().map((x) => el("li", {},
          el("b", {}, `#${x.seq} ${x.body.verdict}`), " ", el("span", { class: "small muted" }, `${x.time} · ${x.kind} · ${(x.body.route || []).join("→")}`),
          el("span", { class: "tip" }, x.hash.slice(0, 24) + "…"))))),
        el("div", {}, el("p", { class: "cap" }, "환율 (원장 날짜)"), el("table", {}, el("tbody", {}, Object.entries(S.fx).filter(([k]) => k !== "KRW").map(([k, v]) =>
          el("tr", {}, el("td", {}, k), el("td", { class: "r num" }, v.krw.toLocaleString("ko-KR") + "원"), el("td", { class: "muted" }, v.date))))),
          el("p", { class: "cap", style: { marginTop: "18px" } }, "연결이 끊긴 도시"),
          el("p", { class: "small" }, S.components.slice(1).map((c) => c.map((x) => WORLD.names_ko[x] || x).join(", ")).join(" / ") || "없음"),
          el("p", { class: "cap", style: { marginTop: "18px" } }, "엔진"),
          el("p", { class: "small" }, (API || location.origin) + " · ", el("button", { class: "btn", type: "button", onclick: () => { store.set("worldtrip.api", ""); location.reload(); } }, "같은 출처로")),
          el("p", { class: "cap", style: { marginTop: "18px" } }, "토큰(서버가 요구할 때만)"),
          el("input", { type: "text", value: store.get("worldtrip.token") || "", placeholder: "WORLDTRIP_TOKEN", onchange: (e) => store.set("worldtrip.token", e.target.value) }))));
  }

  /* ---------------- 엔진에 못 닿았을 때 ---------------- */
  function offline(e) {
    const input = el("input", { type: "text", value: API, placeholder: "https://엔진주소 (비우면 같은 출처)", "aria-label": "엔진 주소" });
    $("#result").replaceChildren(el("section", { class: "spread" },
      el("p", { class: "stamp bad" }, "No engine"),
      el("p", { class: "h-l" }, "엔진에 닿지 못했다"),
      el("p", { class: "small muted" }, (API || location.origin) + " · " + e.message),
      el("p", { class: "small" }, "이 화면은 worldtrip 엔진이 있어야 돈다. 엔진에서 ", el("code", {}, "worldtrip app"),
        " 으로 띄우면 같은 출처라 설정이 필요 없다. 다른 곳에 띄운 엔진이면 주소를 넣어라(그 엔진의 WORLDTRIP_ALLOWED_ORIGINS 에 이 화면의 출처가 있어야 한다)."),
      el("label", {}, "엔진 주소", input),
      el("button", { class: "go", type: "button", onclick: () => { store.set("worldtrip.api", input.value.trim()); location.search = ""; location.reload(); } }, "연결")));
    $("#brief").hidden = true;
  }

  /* ---------------- tabs ---------------- */
  function route() {
    const t = (location.hash || "#plan").slice(1);
    const tab = ["plan", "explore", "ledger"].includes(t) ? t : "plan";
    for (const v of ["plan", "explore", "ledger"]) $("#view-" + v).hidden = v !== tab;
    document.querySelectorAll(".tabs a").forEach((a) => {
      if (a.dataset.tab === tab) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    if (tab === "explore" && WORLD) renderExplore();
    if (tab === "ledger") renderLedger().catch((e) => $("#ledger-body").replaceChildren(el("p", { class: "v" }, e.message)));
  }

  document.addEventListener("DOMContentLoaded", async () => {
    if ("serviceWorker" in navigator && location.protocol !== "file:") navigator.serviceWorker.register("sw.js").catch(() => {});
    try { WORLD = await api("/api/explore"); }
    catch (e) { offline(e); return; }
    buildBrief();
    window.addEventListener("hashchange", route);
    route();
  });
})();
