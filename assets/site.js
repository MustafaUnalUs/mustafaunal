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
