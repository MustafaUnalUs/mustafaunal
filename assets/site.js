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
