/* 앱 껍데기만 캐시한다. 판정(/api, /mcp)은 절대 캐시하지 않는다 -- 낡은 판정을 새 것처럼 보이면 안 된다. */
const V = "worldtrip-shell-v1";
const SHELL = ["./", "app.css", "app.js", "manifest.webmanifest", "icon.svg"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(V).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== V).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin || /\/(api\/|mcp$|healthz$)/.test(u.pathname)) return;
  // 네트워크 먼저, 끊기면 캐시 -- 새 배포가 바로 보이게
  e.respondWith(fetch(e.request).then((r) => { const c = r.clone(); caches.open(V).then((ca) => ca.put(e.request, c)); return r; })
    .catch(() => caches.match(e.request).then((r) => r || caches.match("./"))));
});
