(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // Menü: geniş ekranda hep açık; bağlantıya basınca kapanır
  const menu = $(".menu");
  const mq = matchMedia("(min-width: 900px)");
  const sync = () => { if (menu) menu.open = mq.matches; };
  sync(); mq.addEventListener?.("change", sync);
  $$(".menu nav a").forEach((a) => a.addEventListener("click", () => { if (!mq.matches) menu.open = false; }));

  // Büyütme penceresi: kapaklar (ön/arka) ve fotoğraflar
  const dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.innerHTML = '<div class="lb-top"><span></span><button type="button" class="lb-close" aria-label="Kapat">×</button></div>' +
    '<div class="lb-stage"><img alt=""></div><div class="lb-bottom"></div>';
  document.body.append(dlg);
  const img = $(".lb-stage img", dlg), title = $(".lb-top span", dlg), bottom = $(".lb-bottom", dlg);
  let items = [], idx = 0;
  const show = (i) => {
    idx = (i + items.length) % items.length;
    dlg.classList.remove("zoomed");
    img.src = items[idx].src; img.alt = items[idx].label; title.textContent = items[idx].label;
    $$("[data-i]", bottom).forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.i) === idx)));
  };
  const open = (list, i, buttons) => {
    items = list;
    bottom.innerHTML = buttons
      ? buttons.map((t, j) => `<button type="button" data-i="${j}">${t}</button>`).join("") + '<button type="button" data-zoom>Yakınlaştır</button>'
      : '<button type="button" data-step="-1">‹ Önceki</button><button type="button" data-step="1">Sonraki ›</button><button type="button" data-zoom>Yakınlaştır</button>';
    $$("[data-i]", bottom).forEach((b) => b.addEventListener("click", () => show(Number(b.dataset.i))));
    $$("[data-step]", bottom).forEach((b) => b.addEventListener("click", () => show(idx + Number(b.dataset.step))));
    $("[data-zoom]", bottom).addEventListener("click", (e) => {
      dlg.classList.toggle("zoomed"); e.target.textContent = dlg.classList.contains("zoomed") ? "Sığdır" : "Yakınlaştır";
    });
    show(i); dlg.showModal();
  };
  $$(".bk-covers").forEach((fig) => {
    const btns = $$(".zoom", fig);
    const list = btns.map((b) => ({ src: b.dataset.full, label: b.dataset.label }));
    btns.forEach((b, i) => b.addEventListener("click", () => open(list, i, ["Ön kapak", "Arka kapak"])));
  });
  const photos = $$(".photo");
  photos.forEach((b, i) => b.addEventListener("click", () => open(
    photos.map((p) => ({ src: p.dataset.full, label: p.dataset.label })), i, null)));
  dlg.addEventListener("keydown", (e) => { if (e.key === "ArrowRight") show(idx + 1); if (e.key === "ArrowLeft") show(idx - 1); });
  img.addEventListener("click", () => {
    dlg.classList.toggle("zoomed");
    const z = $("[data-zoom]", bottom); if (z) z.textContent = dlg.classList.contains("zoomed") ? "Sığdır" : "Yakınlaştır";
  });
  $(".lb-close", dlg).addEventListener("click", () => dlg.close());
  dlg.addEventListener("click", (e) => { if (e.target === dlg || e.target.classList.contains("lb-stage")) dlg.close(); });
})();

// El feneri: imleç duvarı aydınlatır
(() => {
  const root = document.documentElement;
  if (matchMedia("(hover: none), (prefers-reduced-motion: reduce)").matches) return;
  let raf = 0;
  addEventListener("pointermove", (e) => {
    if (raf) return;
    raf = requestAnimationFrame(() => {
      root.style.setProperty("--mx", e.clientX + "px");
      root.style.setProperty("--my", e.clientY + "px");
      raf = 0;
    });
  }, { passive: true });
})();

// Okuma: yazı boyutu ve ilerleme çubuğu; YouTube tıklayınca yüklenir
(() => {
  const q = (s, r = document) => r.querySelector(s);
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".yt button");
    if (!btn) return;
    const box = btn.parentElement, f = document.createElement("iframe");
    f.src = `https://www.youtube-nocookie.com/embed/${box.dataset.id}?autoplay=1&rel=0`;
    f.title = btn.getAttribute("aria-label") || "Video";
    f.allow = "autoplay; encrypted-media; picture-in-picture";
    f.allowFullscreen = true;
    box.replaceChildren(f);
  });
  if (!q(".reader")) return;
  const root = document.documentElement;
  let size = 0;
  try { size = Number(localStorage.getItem("mu:size")) || 0; } catch { /* yok say */ }
  const apply = () => root.style.setProperty("--read", `${1.2 + size * 0.0625}rem`);
  apply();
  document.querySelectorAll("[data-size]").forEach((b) => b.addEventListener("click", () => {
    size = Math.max(-2, Math.min(5, size + Number(b.dataset.size)));
    try { localStorage.setItem("mu:size", size); } catch { /* yok say */ }
    apply();
  }));
  const bar = q(".progress span");
  const on = () => {
    const h = root.scrollHeight - innerHeight;
    if (bar) bar.style.width = `${h > 0 ? Math.min(100, (scrollY / h) * 100) : 0}%`;
  };
  addEventListener("scroll", on, { passive: true });
  on();
})();

/* paylaş: bulunduğu adresi kullan */
document.querySelectorAll("[data-share]").forEach((a) => {
  const u = encodeURIComponent(location.href.split("#")[0]), t = encodeURIComponent(document.title);
  a.href = { wa: `https://wa.me/?text=${t}%20${u}`, fb: `https://www.facebook.com/sharer/sharer.php?u=${u}`,
             x: `https://x.com/intent/post?text=${t}&url=${u}` }[a.dataset.share];
});

/* açık / koyu görünüm düğmesi */
(() => {
  const b = document.getElementById("tema");
  if (!b) return;
  const root = document.documentElement;
  const meta = document.querySelector('meta[name="theme-color"]');
  const paint = () => { if (meta) meta.content = root.getAttribute("data-theme") === "light" ? "#f4efe4" : "#16231d"; };
  paint();
  b.addEventListener("click", () => {
    const t = root.getAttribute("data-theme") === "light" ? "dark" : "light";
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("tema", t); } catch { /* yok say */ }
    paint();
  });
})();

/* bölümler arası kolay geçiş: klavye okları, telefonda kaydırma, alttaki küçük çubuk */
(() => {
  const prevA = document.querySelector(".pager-prev, .r-pager a:not(.nx)");
  const nextA = document.querySelector(".pager-next, .r-pager a.nx");
  if (!prevA && !nextA) return;
  const go = (a) => { if (a && a.href) location.href = a.href; };
  const label = (a) => (a ? [...a.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join("").trim() : "");

  // 1) Bilgisayar: ← → tuşları
  addEventListener("keydown", (e) => {
    if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    const t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (document.querySelector("dialog[open]")) return;
    if (e.key === "ArrowRight") go(nextA);
    else if (e.key === "ArrowLeft") go(prevA);
  });

  // 2) Alttaki küçük geçiş çubuğu
  const pos = document.querySelector(".chap-band-in span, .r-band span");
  const bar = document.createElement("nav");
  bar.className = "gecis";
  bar.setAttribute("aria-label", "Bölüm geçişi");
  const mk = (a, cls, arrow, txt) => {
    const el = document.createElement(a ? "a" : "span");
    el.className = cls + (a ? "" : " is-off");
    if (a) { el.href = a.href; el.title = label(a); }
    el.innerHTML = cls === "g-prev" ? `<b aria-hidden="true">${arrow}</b><span>${txt}</span>` : `<span>${txt}</span><b aria-hidden="true">${arrow}</b>`;
    return el;
  };
  const mid = document.createElement("span");
  mid.className = "g-mid";
  mid.textContent = pos ? pos.textContent.replace(/^Bölüm\s*/, "") : "";
  bar.append(mk(prevA, "g-prev", "‹", "Önceki"), mid, mk(nextA, "g-next", "›", nextA && /sonu|sayfasına/i.test(nextA.textContent) ? "Kitaba dön" : "Sonraki"));
  document.body.append(bar);
  document.body.classList.add("has-gecis");

  // aşağı okurken gizlen, yukarı kaydırınca ya da sona gelince görün
  let lastY = scrollY;
  const onScroll = () => {
    const y = scrollY;
    const nearEnd = y + innerHeight > document.documentElement.scrollHeight - 600;
    bar.classList.toggle("is-hidden", y > lastY + 4 && y > 300 && !nearEnd);
    if (y < lastY - 4 || nearEnd) bar.classList.remove("is-hidden");
    lastY = y;
  };
  addEventListener("scroll", onScroll, { passive: true });

  // 3) Telefon: metni sağa/sola kaydırarak geç
  const area = document.querySelector(".reader") || document.body;
  let sx = 0, sy = 0, st = 0, ok = false;
  area.addEventListener("touchstart", (e) => {
    if (e.touches.length !== 1) { ok = false; return; }
    sx = e.touches[0].clientX; sy = e.touches[0].clientY; st = Date.now(); ok = true;
  }, { passive: true });
  area.addEventListener("touchend", (e) => {
    if (!ok || getSelection().toString()) return;
    const t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
    if (Date.now() - st < 700 && Math.abs(dx) > 90 && Math.abs(dx) > Math.abs(dy) * 2.2) {
      bar.classList.add(dx < 0 ? "go-next" : "go-prev");
      go(dx < 0 ? nextA : prevA);
    }
  }, { passive: true });
})();

/* okuma alanının iki yanında oklar + telefonda kaydırma ipucu */
(() => {
  const reader = document.querySelector(".reader");
  const prevA = document.querySelector(".pager-prev, .r-pager a:not(.nx)");
  const nextA = document.querySelector(".pager-next, .r-pager a.nx");
  if (!reader || (!prevA && !nextA)) return;
  const mk = (a, cls, ch, lab) => {
    const el = document.createElement(a ? "a" : "span");
    el.className = "yan-ok " + cls + (a ? "" : " is-off");
    if (a) { el.href = a.href; el.setAttribute("aria-label", lab); el.title = lab; }
    el.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ch}"/></svg>`;
    document.body.append(el);
    return el;
  };
  const L = mk(prevA, "yan-sol", "M15 5l-7 7 7 7", "Önceki bölüm");
  const R = mk(nextA, "yan-sag", "M9 5l7 7-7 7", nextA && /sonu|sayfasına/i.test(nextA.textContent) ? "Kitaba dön" : "Sonraki bölüm");
  const place = () => {
    const r = reader.getBoundingClientRect();
    L.style.left = Math.max(8, r.left - 64) + "px";
    R.style.left = Math.min(innerWidth - 56, r.right + 16) + "px";
    const room = r.left > 80;
    L.hidden = R.hidden = !room;
  };
  place();
  addEventListener("resize", place);
  const hint = document.createElement("p");
  hint.className = "kaydir-ipucu";
  hint.innerHTML = "<span aria-hidden=\"true\">←</span> Bölüm değiştirmek için yazıyı sağa ya da sola kaydırın <span aria-hidden=\"true\">→</span>";
  const pager = document.querySelector(".pager, .r-pager");
  (pager ? pager.parentNode : reader).insertBefore(hint, pager || null);
})();

/* kaldığın yerden devam et */
(() => {
  const K = (base) => "devam:" + base;
  const get = (k) => { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch { return null; } };
  const set = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* yok say */ } };
  const band = document.querySelector(".chap-band-in > a, .r-band > a");
  const reader = document.querySelector(".reader");
  if (band && reader) {
    const base = band.getAttribute("href");
    const num = (document.querySelector(".chap-num, .r-num") || {}).textContent || "";
    const title = (reader.querySelector("h1") || {}).textContent || "";
    const frac = () => { const h = document.documentElement.scrollHeight - innerHeight; return h > 0 ? scrollY / h : 0; };
    const save = () => {
      const f = frac();
      if (Number(num) > 1 || f > .08) set(K(base), { u: location.pathname, n: num.trim(), t: title.trim(), f: Math.round(f * 1000) / 1000 });
    };
    if (location.hash === "#devam") {
      const s = get(K(base));
      if (s && s.u === location.pathname && s.f > .02) {
        addEventListener("load", () => scrollTo(0, s.f * (document.documentElement.scrollHeight - innerHeight)));
      }
    }
    let t;
    addEventListener("scroll", () => { clearTimeout(t); t = setTimeout(save, 400); }, { passive: true });
    addEventListener("pagehide", save);
    if (Number(num) > 1) setTimeout(save, 1500);
    return;
  }
  const acts = document.querySelector(".bk-actions");
  if (!acts) return;
  const s = get(K(location.pathname));
  if (!s || !s.u) return;
  const a = document.createElement("a");
  a.className = "devam";
  a.href = s.u + "#devam";
  const pct = s.f ? ` · %${Math.max(1, Math.round(s.f * 100))}` : "";
  a.innerHTML = `<span class="devam-k">Kaldığınız yer${pct}</span><b></b><span class="devam-go">Devam et <span aria-hidden="true">→</span></span>`;
  a.querySelector("b").textContent = (s.n ? s.n + " · " : "") + s.t;
  acts.parentNode.insertBefore(a, acts);
  const main = acts.querySelector(".ba-main span");
  if (main) main.textContent = "Baştan başla";
})();

/* site içi arama */
(() => {
  const q = document.getElementById("ara-q");
  if (!q) return;
  const out = document.getElementById("ara-sonuc"), st = document.getElementById("ara-durum");
  const MAP = { "ı": "i", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ç": "c", "â": "a", "î": "i", "û": "u" };
  const norm = (s) => s.toLocaleLowerCase("tr").replace(/[ışğüöçâîû]/g, (c) => MAP[c]);
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  let DOC = null;
  const load = () => DOC ? Promise.resolve() : fetch("/veri/ara.json").then((r) => r.json()).then((d) => (DOC = d.map((x) => ({ ...x, n: norm(x.x), nt: norm(x.t + " " + x.b) }))));
  const snip = (x, nx, w) => {
    const i = nx.indexOf(w);
    if (i < 0) return esc(x.slice(0, 160)) + "…";
    const a = Math.max(0, i - 70), b = Math.min(x.length, i + w.length + 110);
    return (a ? "…" : "") + esc(x.slice(a, i)) + "<mark>" + esc(x.slice(i, i + w.length)) + "</mark>" + esc(x.slice(i + w.length, b)) + (b < x.length ? "…" : "");
  };
  const group = (title, rows, all) => rows.length ? `<section class="ara-grup"><h2>${title} (${all})</h2><ul class="ara-list">${rows.join("")}</ul></section>` : "";
  const run = () => {
    const raw = q.value.trim(), w = norm(raw);
    history.replaceState(null, "", raw ? "?q=" + encodeURIComponent(raw) : location.pathname);
    if (w.length < 2) { out.innerHTML = ""; st.textContent = "En az iki harf yazın."; return; }
    st.textContent = "Aranıyor…";
    load().then(() => {
      const hits = DOC.filter((d) => d.n.includes(w) || d.nt.includes(w))
        .map((d) => ({ d, s: (d.nt.includes(w) ? 50 : 0) + d.n.split(w).length - 1 })).sort((a, b) => b.s - a.s);
      const row = ({ d }) => `<li><a href="${d.u}"><b>${esc(d.t || d.b)}</b><small>${esc(d.k)}${d.b && d.b !== d.t ? " · " + esc(d.b) : ""}</small><p>${snip(d.x, d.n, w)}</p></a></li>`;
      const by = (k) => hits.filter((h) => h.d.k === k);
      const kit = by("Kitap"), ana = by("Ana sayfa"), say = by("Sayfa");
      out.innerHTML = group("Sergi salonları", ana.map(row), ana.length) + group("Kitaplar", kit.slice(0, 40).map(row), kit.length) + group("Diğer sayfalar", say.slice(0, 15).map(row), say.length);
      st.textContent = hits.length ? `“${raw}” için ${hits.length.toLocaleString("tr-TR")} sonuç` : `“${raw}” için sonuç bulunamadı. Yazımı değiştirmeyi deneyin.`;
    }).catch(() => { st.textContent = "Arama yüklenemedi. Sayfayı yenileyin."; });
  };
  let t;
  q.addEventListener("input", () => { clearTimeout(t); t = setTimeout(run, 250); });
  q.form.addEventListener("submit", (e) => { e.preventDefault(); run(); });
  const init = new URLSearchParams(location.search).get("q");
  if (init) { q.value = init; run(); } else q.focus();
})();

/* bölüm sesi: tam kaydın yalnızca bu bölüme ait kısmı */
document.querySelectorAll(".dinle-kutu audio[data-start]").forEach((au) => {
  const a = parseFloat(au.dataset.start), z = parseFloat(au.dataset.end);
  au.addEventListener("play", () => { if (au.currentTime < a - 1 || au.currentTime >= z) au.currentTime = a; });
  au.addEventListener("timeupdate", () => { if (au.currentTime >= z) { au.pause(); au.currentTime = a; } });
});

/* çevrimdışı okuma */
if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("/sw.js").catch(() => {});
