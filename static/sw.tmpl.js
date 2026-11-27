/* Çevrimdışı okuma: açılan sayfalar ve site dosyaları cihazda saklanır. */
const SURUM = "__V__";
const ON = ["/", "/assets/site.css?v=__A__", "/assets/site.js?v=__A__", "/img/favicon.svg", "/cevrimdisi.html"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(SURUM).then((c) => c.addAll(ON)).then(() => self.skipWaiting())); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== SURUM).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== location.origin || r.headers.has("range") || /\.(mp3|m4a|pdf)$/i.test(u.pathname)) return;
  if (r.mode === "navigate") {
    e.respondWith(fetch(r).then((res) => { const k = res.clone(); caches.open(SURUM).then((c) => c.put(r, k)); return res; })
      .catch(() => caches.match(r).then((x) => x || caches.match("/cevrimdisi.html"))));
    return;
  }
  e.respondWith(caches.match(r).then((x) => x || fetch(r).then((res) => {
    if (res.ok && /\.(css|js|webp|png|jpg|svg|woff2?|json)$/i.test(u.pathname)) { const k = res.clone(); caches.open(SURUM).then((c) => c.put(r, k)); }
    return res;
  })));
});
