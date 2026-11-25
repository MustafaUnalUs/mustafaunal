/* Site içi PDF okuyucu: sayfalar ekrana geldikçe çizilir. */
(() => {
  const box = document.getElementById("pdfoku");
  if (!box || !window.pdfjsLib) return;
  pdfjsLib.GlobalWorkerOptions.workerSrc = "/assets/pdfjs/pdf.worker.min.js";
  const pagesEl = box.querySelector(".po-pages");
  const info = box.querySelector(".po-info");
  const KEY = "po:" + box.dataset.pdf;
  let zoom = 1, pdf = null, rendered = new Map(), io = null;
  try { zoom = Number(localStorage.getItem("po:zoom")) || 1; } catch { /* yok say */ }

  const width = () => Math.min(pagesEl.clientWidth - 16, 860) * zoom;

  const draw = async (n, holder) => {
    const page = await pdf.getPage(n);
    const base = page.getViewport({ scale: 1 });
    const scale = width() / base.width;
    const vp = page.getViewport({ scale: scale * (window.devicePixelRatio || 1) });
    const c = document.createElement("canvas");
    c.width = vp.width; c.height = vp.height;
    c.style.width = width() + "px";
    await page.render({ canvasContext: c.getContext("2d"), viewport: vp }).promise;
    holder.replaceChildren(c);
    rendered.set(n, true);
  };

  const layout = async () => {
    const first = await pdf.getPage(1);
    const r = first.getViewport({ scale: 1 });
    const ratio = r.height / r.width;
    pagesEl.replaceChildren();
    rendered.clear();
    if (io) io.disconnect();
    io = new IntersectionObserver((es) => es.forEach((e) => {
      const n = Number(e.target.dataset.n);
      if (e.isIntersecting && !rendered.get(n)) { rendered.set(n, "busy"); draw(n, e.target); }
    }), { rootMargin: "800px 0px" });
    const posObs = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) {
        const n = e.target.dataset.n;
        info.textContent = `Sayfa ${n} / ${pdf.numPages}`;
        try { localStorage.setItem(KEY, n); } catch { /* yok say */ }
      }
    }), { rootMargin: "-45% 0px -45% 0px" });
    for (let n = 1; n <= pdf.numPages; n++) {
      const d = document.createElement("div");
      d.className = "po-page"; d.dataset.n = n;
      d.style.width = width() + "px"; d.style.height = width() * ratio + "px";
      d.setAttribute("aria-label", `Sayfa ${n}`);
      pagesEl.append(d); io.observe(d); posObs.observe(d);
    }
  };

  const go = (n) => {
    const el = pagesEl.querySelector(`[data-n="${n}"]`);
    if (el) el.scrollIntoView({ block: "start" });
  };

  pdfjsLib.getDocument({ url: box.dataset.pdf, rangeChunkSize: 262144 }).promise.then(async (doc) => {
    pdf = doc;
    await layout();
    let last = 1;
    try { last = Number(localStorage.getItem(KEY)) || 1; } catch { /* yok say */ }
    if (last > 1) go(last);
    box.classList.add("is-ready");
  }).catch(() => {
    info.textContent = "PDF açılamadı. İndirerek okuyabilirsiniz.";
  });

  box.querySelectorAll("[data-zoom]").forEach((b) => b.addEventListener("click", async () => {
    if (!pdf) return;
    const cur = Number((info.textContent.match(/\d+/) || [1])[0]);
    zoom = Math.max(0.6, Math.min(2.5, zoom + Number(b.dataset.zoom)));
    try { localStorage.setItem("po:zoom", zoom); } catch { /* yok say */ }
    await layout(); go(cur);
  }));
  box.querySelector("[data-start]")?.addEventListener("click", () => go(1));
  let t;
  addEventListener("resize", () => { clearTimeout(t); t = setTimeout(async () => { if (pdf) { const cur = Number((info.textContent.match(/\d+/) || [1])[0]); await layout(); go(cur); } }, 300); });
})();
