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
  $$(".book .zoom").forEach((b) => b.addEventListener("click", () => open(
    [{ src: b.dataset.full, label: b.dataset.label + " · Ön kapak" }, { src: b.dataset.back, label: b.dataset.label + " · Arka kapak" }],
    0, ["Ön kapak", "Arka kapak"])));
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
