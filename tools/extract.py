#!/usr/bin/env python3
"""mustafaunal.tr ana sayfasından içerik çıkarır → data/site.json, görseller → static/img/.

Kullanım: python3 tools/extract.py <mustafaunal.tr yerel kopyası>
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1])
OUT_IMG = ROOT / "static" / "img"


def T(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).replace(" ,", ",").replace(" .", ".").strip() if el else ""


def lines(el):
    for br in el.find_all("br"):
        br.replace_with("\n")
    return [re.sub(r"\s+", " ", x).strip() for x in el.get_text("\n").split("\n") if x.strip()]


images = {}


def img(src):
    """Görseli webp'ye çevirip yeni yolunu döndürür."""
    if not src:
        return None
    src = src.split("?")[0]
    name = re.sub(r"[^a-z0-9-]+", "-", Path(src).stem.lower()).strip("-")
    folder = Path(src).parent.name
    out = f"/img/{folder}/{name}.webp" if folder != "assets" else f"/img/{name}.webp"
    if src not in images:
        p = SRC / src
        dst = ROOT / "static" / out.lstrip("/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(p) as im:
            keep_alpha = im.mode in ("RGBA", "LA", "P")
            im = im.convert("RGBA" if keep_alpha else "RGB")
            im.thumbnail((2000, 2000))
            im.save(dst, "WEBP", quality=82, method=6)
            images[src] = {"out": out, "w": im.width, "h": im.height}
    return images[src]["out"]


def size(path):
    for v in images.values():
        if v["out"] == path:
            return v["w"], v["h"]
    return None, None


s = BeautifulSoup((SRC / "index.html").read_text(encoding="utf-8"), "html.parser")
d = {}

hero = s.select_one("#ust")
d["hero"] = {
    "eyebrow": T(hero.select_one(".eyebrow")),
    "title": lines(hero.select_one("h1")),
    "text": T(hero.select_one(".hero-copy > p:not(.eyebrow)")),
    "roles": [T(li) for li in hero.select(".hero-copy li")],
    "portrait": img(hero.select_one(".hero-portrait img")["src"]),
}
d["doors_title"] = lines(s.select_one("#kesfet h2"))
d["doors"] = [{"href": a["href"], "img": img(a.select_one("img")["src"]), "kicker": T(a.select_one("small")),
               "title": T(a.select_one("b")), "text": T(a.select_one("i")).rstrip(" →")} for a in s.select(".door")]

# Kitaplar: yalnızca bölüm başlığı ve kısa yazılar; kapaklar acıpayam testinden gelir
d["books_title"] = lines(s.select_one("#kitaplar h2"))
d["books"] = []
for art in s.select("#kitaplar .book-showcase"):
    d["books"].append({"label": T(art.select_one(".book-intro small")), "title": T(art.select_one(".book-intro h3")),
                       "lead": T(art.select_one(".book-intro p")), "detail": T(art.select_one(".book-detail p"))})

mem = s.select_one("#mazi")
d["mazi_title"] = lines(mem.select_one("h2"))
d["mazi_kicker"] = T(mem.select_one(".section-title p"))
d["timeline"] = []
for a in mem.select(".timeline article"):
    im = a.select_one("img")
    d["timeline"].append({
        "time": lines(a.select_one("time")), "title": T(a.select_one("h3")), "text": T(a.select_one("p")),
        "links": [{"label": T(x), "href": x["href"]} for x in a.select(".links a")],
        "img": img(im["src"]) if im else None, "logo": bool(im and "timeline-logo" in (im.get("class") or [])),
    })
la = mem.select_one(".life-archive")
d["life"] = {"eyebrow": T(la.select_one(".eyebrow")), "title": T(la.select_one("h3")), "text": T(la.select_one("div > p:not(.eyebrow)")),
             "photos": [{"img": img(f.select_one("img")["src"]), "cap": T(f.select_one("figcaption"))} for f in la.select("figure")]}
sa = mem.select_one(".source-archive")
d["press"] = {"title": T(sa.select_one("h3")), "text": T(sa.select_one("p")),
              "groups": [{"title": T(g.select_one("h4")), "links": [{"label": T(x), "href": x["href"]} for x in g.select("a")]}
                         for g in sa.select(".archive-groups section")]}

w = s.select_one("#calismalar")
d["works_title"] = lines(w.select_one("h2"))
d["works"] = [{"img": img(a.select_one("img")["src"]), "kicker": T(a.select_one("small")), "title": T(a.select_one("h3")),
               "text": T(a.select_one("p")), "link": {"label": T(a.select_one("a")).rstrip(" →"), "href": a.select_one("a")["href"]}}
              for a in w.select(".work-list article")]

ph = s.select_one("#fotograflar")
d["photos_title"] = lines(ph.select_one("h2"))
d["photos_link"] = {"label": T(ph.select_one(".section-title a")).rstrip(" ↗"), "href": ph.select_one(".section-title a")["href"]}
d["photos"] = []
for b in ph.select(".photo"):
    im = b.select_one("img")
    d["photos"].append({"img": img(im["src"]), "alt": im.get("alt", ""), "shape": next((c for c in b["class"] if c in ("tall", "wide")), "")})

n = s.select_one("#doga")
d["nature"] = {"img": img(n.select_one("img")["src"]), "cap": T(n.select_one("figcaption")), "eyebrow": T(n.select_one(".eyebrow")),
               "title": lines(n.select_one("h2")), "text": T(n.select_one("div > p:not(.eyebrow)")),
               "links": [{"label": T(x), "href": x["href"]} for x in n.select(".links a")]}

ab = s.select_one("#hakkimda")
d["about"] = {"img": img(ab.select_one("img")["src"]), "title": T(ab.select_one("h2")),
              "text": [T(p) for p in ab.select(".about-grid > div > p:not(.eyebrow)")],
              "now": T(ab.select_one(".current-work p")), "quote": T(ab.select_one("blockquote")).strip("“”\"")}

f = s.select_one("#iletisim")
d["contact"] = [{"label": T(a), "href": a["href"]} for a in f.select("nav a")]

# GAMEKS tarihçesi (şablon içinde)
tpl = s.select_one("#gameks-page-template")
g = BeautifulSoup(tpl.decode_contents(), "html.parser")
d["gameks"] = {
    "logo": img(g.select_one(".gameks-hero img")["src"]),
    "eyebrow": T(g.select_one(".gameks-hero .eyebrow")),
    "title": lines(g.select_one(".gameks-hero h1")),
    "lead": T(g.select_one(".gameks-hero p:not(.eyebrow)")),
    "intro_title": T(g.select_one(".gameks-intro h2")),
    "intro": [T(p) for p in g.select(".gameks-intro p:not(.eyebrow)")],
    "history": [],
}
for a in g.select(".gameks-history article"):
    ims = a.select("img")
    d["gameks"]["history"].append({
        "time": lines(a.select_one("time")), "title": T(a.select_one("h3")),
        "text": [T(p) for p in a.select("div > p") if not p.find("a")],
        "links": [{"label": T(x).rstrip(" →"), "href": x["href"]} for x in a.select("div p a") if x["href"].startswith("http")],
        "imgs": [{"src": img(i["src"]), "logo": "history-logo" in (i.get("class") or [])} for i in ims],
        "note": T(a.select_one(".image-note")),
    })

# boyutları ekle
for key in ("doors",):
    for x in d[key]:
        x["w"], x["h"] = size(x["img"])
for x in d["photos"] + d["life"]["photos"] + d["works"]:
    x["w"], x["h"] = size(x["img"])

(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "site.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("tamam:", len(images), "görsel;", len(d["timeline"]), "dönem;", len(d["gameks"]["history"]), "GAMEKS maddesi;",
      len(d["photos"]), "fotoğraf")
