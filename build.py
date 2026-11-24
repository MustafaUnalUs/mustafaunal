#!/usr/bin/env python3
"""Mustafa Ünal kişisel sitesi (test sürümü) üreticisi.

data/ ve static/ klasörlerinden docs/ altına statik site üretir:  python3 build.py
"""
import html
import json
import os
import shutil

import books
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
D = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
ORIGIN = "https://mustafaunal.tr"
# SITE_MODE=canli: mustafaunal.tr için (arama motorlarına açık, test notu yok). Varsayılan: test.
CANLI = os.environ.get("SITE_MODE", "test") == "canli"
READER = "https://acipayam.gunerunal.com.tr"   # kitapların okunduğu site
ASSET_V = "5"
E = lambda s: html.escape(str(s or ""), quote=True)  # noqa: E731

SERIES = [
    {"slug": "icimde-kalan-cocuk", "no": "I", "title": "İçimde Kalan Çocuk", "path": "/kitaplar/icimde-kalan-cocuk/",
     "line": "Çocukluğun saf pusulasından vicdana uzanan ilk on dört yıl."},
    {"slug": "karanlik-odada-yedi-ay", "no": "II", "title": "Karanlık Odada Yedi Ay", "path": "/kitaplar/karanlik-odada-yedi-ay/",
     "line": "1990’da Ankara-Akyurt’ta geçen yedi ay ve otuz beş yıl sonra yeniden açılan bir hayat."},
    {"slug": "uslu-dusler", "no": "III", "tag": "Bonus", "title": "US’lu Düşler", "path": "/kitaplar/uslu-dusler/",
     "line": "Kırk sayfa civarında; aç, oku, bitir. Zihni dürtmeyi sürdüren küçük bir beyin jimnastiği."},
    {"slug": "adi-konmamis-islere-don-bicen-adam", "no": "IV", "tag": "Hazırlanıyor", "soon": True,
     "title": "Adı Konmamış İşlere Don Biçen Adam", "path": "/kitaplar/adi-konmamis-islere-don-bicen-adam/",
     "line": "GAMEKS, işler, fikirler ve internet. 2027’de yayımlanması planlanıyor."},
    {"slug": "uslu-dimag", "no": "V", "tag": "Final · Hazırlanıyor", "soon": True, "title": "US’lu Dimağ", "path": "/kitaplar/uslu-dimag/",
     "line": "Doksan öğretide ölçüsü oturmuş bir zihin. 2027’de yayımlanması planlanıyor."},
]
OTHERS = [
    {"slug": "gonul-dostu", "title": "Gönül Dostu", "role": "Yazar · Hazırlanıyor", "soon": True, "path": "/kitaplar/gonul-dostu/",
     "line": "Sabit Kızılhan ile yol yürümek: 2005–2026 arasından dostluğun ve hak mücadelesinin tanıklığı. 2027’de yayımlanması planlanıyor."},
    {"slug": "bana-koyunu-anlat", "title": "Bana Köyünü Anlat", "role": "Editör · Sabit Kızılhan’ın derlemesi", "path": "/kitaplar/bana-koyunu-anlat/",
     "line": "Acıpayam köylerinin anlatıcılarıyla hazırlanan sözlü tarih çalışması."},
    {"slug": "kelekcide-yasamak", "title": "Kelekçi’de Yaşamak", "role": "Yayına hazırlayan · Dr. Oktar Öner’in kitabı",
     "path": "/kitaplar/kelekcide-yasamak/", "line": "El yazmaları, mektuplar ve radyo kayıtlarıyla bir Kelekçi hafızası."},
]

SALONS = [("kitaplar", "Kitaplar"), ("fotograflar", "Fotoğraflar"), ("mazi", "Mazi"), ("doga", "Doğa"),
          ("calismalar", "Çalışmalar"), ("basin", "Basın"), ("hakkimda", "Hakkımda")]
NAV = [(f"#{a}", t) for a, t in SALONS[:4]] + [("/gameks/", "GAMEKS"), ("#hakkimda", "Hakkımda")]


TEST_NOTE = ('<p class="foot-note">Bu adres, mustafaunal.tr içeriğiyle hazırlanmış yeni tasarımın test sürümüdür. '
             f'Asıl site: <a href="{ORIGIN}/">mustafaunal.tr</a></p>')


def layout(path, title, body, desc="", cls=""):
    nav = "".join(f'<a href="{("/" + h) if h.startswith("#") and path != "/" else h}">{t}</a>' for h, t in NAV)
    contact = "".join(f'<a href="{E(c["href"])}">{E(c["label"])}</a>' for c in D["contact"])
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc or D['hero']['text'])}">
{"" if CANLI else chr(60) + "meta name=" + chr(34) + "robots" + chr(34) + " content=" + chr(34) + "noindex" + chr(34) + ">"}
<link rel="canonical" href="{ORIGIN}{path}">
<meta name="theme-color" content="#16231d">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Instrument+Sans:wght@400..700&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={ASSET_V}">
</head>
<body class="{cls}">
<div class="torch" aria-hidden="true"></div>
<a class="skip" href="#icerik">İçeriğe geç</a>
<header class="bar">
  <a class="name" href="/"><span class="name-dot" aria-hidden="true"></span>Mustafa Ünal</a>
  <details class="menu"><summary>Salonlar</summary><nav aria-label="Ana menü">{nav}</nav></details>
</header>
<main id="icerik">
{body}
</main>
<footer class="foot" id="iletisim">
  <div class="foot-in">
    <p class="foot-name">Mustafa Ünal</p>
    <p class="foot-line">Bir ömür, birçok iz. Sergi her zaman açık.</p>
    <nav aria-label="İletişim">{contact}<a href="{READER}/">ACIPAYAM.com</a><a href="https://eskidenizli.com">Eski Denizli</a></nav>
  </div>
  {"" if CANLI else TEST_NOTE}
</footer>
<script src="/assets/site.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


def ph(src, alt, cls="", w=None, h=None, lazy=True):
    dims = f' width="{w}" height="{h}"' if w and h else ""
    return f'<img class="{cls}" src="{src}" alt="{E(alt)}"{dims}{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""}>'


def label(title, lines, extra=""):
    """Müze duvar etiketi."""
    rows = "".join(f"<span>{E(x)}</span>" for x in lines if x)
    return f'<div class="label"><b>{E(title)}</b>{rows}{extra}</div>'


def salon_head(no, anchor, title, text):
    return (f'<header class="salon-head"><p class="salon-no">Salon {no}</p><h2 id="{anchor}-baslik">{E(title)}</h2>'
            f'<p class="salon-text">{E(text)}</p></header>')


def book(b, series=False):
    soon = b.get("soon")
    sub = (f"Kitap {b['no']}" + (f" · {b['tag']}" if b.get("tag") else "")) if series else b["role"]
    act = "Kitabın sayfası" if soon else "Kitabı aç"
    return (f'<li class="book{" is-soon" if soon else ""}"><a class="book-link" href="{b["path"]}">'
            f'<span class="spot">{ph("/img/kapak/" + b["slug"] + ".webp", b["title"] + " kapağı", "cover", 400, 620)}</span>'
            f'<span class="book-meta">{E(sub)}</span><span class="book-title">{E(b["title"])}</span>'
            f'<span class="book-line">{E(b["line"])}</span><span class="book-act">{act}</span></a></li>')


def card(img, kicker, title, text, href, btn, alt=""):
    pic = f'<span class="card-pic">{ph(img, alt or title)}</span>' if img else ""
    return (f'<li class="card"><a href="{E(href)}">{pic}<span class="card-body"><span class="card-kicker">{E(kicker)}</span>'
            f'<b>{E(title)}</b><span class="card-text">{E(text)}</span><span class="btn">{E(btn)}</span></span></a></li>')


def build_home():
    h = D["hero"]
    hero_photo = next((p for p in D["photos"] if "photo-18" in p["img"]), D["photos"][0])   # şimşek
    guide = "".join(f'<li><a href="#{a}"><span>{i}</span>{E(t)}</a></li>' for i, (a, t) in enumerate(SALONS, 1))
    series = "".join(book(b, True) for b in SERIES)
    others = "".join(book(b) for b in OTHERS)
    photos = "".join(
        f'<li><button type="button" class="photo" data-full="{p["img"]}" data-label="Fotoğraf {i:02d}" aria-label="Fotoğraf {i:02d}: büyüt">'
        f'<span class="mat">{ph(p["img"], p.get("alt") or "Mustafa Ünal fotoğrafı")}</span></button><p class="tag">No. {i:02d}</p></li>'
        for i, p in enumerate(D["photos"], 1))
    life = "".join(
        f'<li><button type="button" class="photo" data-full="{p["img"]}" data-label="{E(p["cap"])}" aria-label="{E(p["cap"])}: büyüt">'
        f'<span class="mat">{ph(p["img"], p["cap"])}</span></button><p class="tag">{E(p["cap"])}</p></li>'
        for p in D["life"]["photos"])
    tl = ""
    for t in D["timeline"]:
        links = "".join(f'<a href="{E("/gameks/" if l["href"] == "#gameks" else l["href"])}">{E(l["label"])}</a>' for l in t["links"])
        pic = f'<span class="tl-pic{" is-logo" if t["logo"] else ""}">{ph(t["img"], t["title"])}</span>' if t["img"] else '<span class="tl-pic is-empty"></span>'
        tl += (f'<li><p class="tl-year">{" ".join(E(x) for x in t["time"])}</p><div class="tl-text"><h3>{E(t["title"])}</h3><p>{E(t["text"])}</p>'
               f'{f"<p class=links>{links}</p>" if links else ""}</div>{pic}</li>')
    n = D["nature"]
    nature_links = "".join(f'<li><a href="{E(l["href"])}">{E(l["label"])}</a></li>' for l in n["links"])
    g = D["gameks"]
    works = "".join(
        card(w["img"], w["kicker"], w["title"].replace("GAMEKS — Bilişimden Üretime", "GAMEKS"), w["text"],
             "/gameks/" if w["link"]["href"] == "#gameks" else w["link"]["href"],
             "Tarihçeyi oku" if w["link"]["href"] == "#gameks" else w["link"]["label"])
        for w in D["works"])
    press = "".join(
        f'<div class="press-col"><h3>{E(gr["title"])}</h3><ul>' + "".join(f'<li><a href="{E(l["href"])}">{E(l["label"])}</a></li>' for l in gr["links"]) + "</ul></div>"
        for gr in D["press"]["groups"])
    a = D["about"]
    body = f"""
<section class="hero">
  <div class="hero-text">
    <p class="hero-roles">Yazar · Fotoğrafçı · Yerel hafıza</p>
    <h1>Mustafa<br>Ünal</h1>
    <p class="hero-motto">Bir ömür, birçok iz.</p>
    <p class="hero-lead">1969’da Balkıca’da başlayan bir hayat. Kitaplar, yaklaşık 250 bin fotoğraf, Acıpayam.com ve Eski Denizli ile yaşananları kaybolmadan görmek, unutmadan aktarmak için.</p>
    <p class="hero-actions"><a class="btn" href="#kitaplar">Kitaplarım</a><a class="btn btn-line" href="#fotograflar">Fotoğraflarım</a></p>
  </div>
  <figure class="hero-portrait">
    <span class="halo" aria-hidden="true"></span>
    <img src="{h["portrait"]}" alt="Mustafa Ünal" width="700" height="700">
  </figure>
</section>

<section class="salon" id="kitaplar" aria-labelledby="kitaplar-baslik">
  {salon_head(1, "kitaplar", "Kitaplar", "Hepsi ücretsiz; internette okunur, PDF olarak indirilir. Bir kitaba dokunun, sayfası açılsın.")}
  <h3 class="row-title">US’lu Anlatılar <span>Beş kitaplık seri</span></h3>
  <ol class="shelf">{series}</ol>
  <h3 class="row-title">Yazarlık, editörlük, yayına hazırlık</h3>
  <ul class="shelf">{others}</ul>
</section>

<section class="salon" id="fotograflar" aria-labelledby="fotograflar-baslik">
  {salon_head(2, "fotograflar", "Fotoğraflar", "Yaklaşık 250 bin kareden küçük bir seçki. Bir kareye dokunun; büyür, oklarla gezilir.")}
  <ul class="grid3">{photos}</ul>
  <h3 class="row-title">{E(D['life']['title'])} <span>{E(D['life']['text'])}</span></h3>
  <ul class="grid4">{life}</ul>
  <p class="more-link"><a class="btn btn-line" href="{E(D['photos_link']['href'])}">{E(D['photos_link']['label'])}</a></p>
</section>

<section class="salon" id="mazi" aria-labelledby="mazi-baslik">
  {salon_head(3, "mazi", "Mazi", "Bugünden geriye: 2026’dan Balkıca’ya uzanan yol.")}
  <ol class="years">{tl}</ol>
</section>

<section class="salon" id="doga" aria-labelledby="doga-baslik">
  {salon_head(4, "doga", "Doğa", "Fotoğraf bazen itirazın kaydıdır.")}
  <div class="split">
    <figure class="framed"><span class="mat">{ph(n["img"], n["cap"], lazy=False)}</span>
      <figcaption><span class="label"><b>Dalaman Çayı, Saimin Köprüsü</b><span>2016 · Fotoğraf: çeken kişi bilinmiyor</span></span></figcaption></figure>
    <div><p class="body-text">{E(n["text"])}</p><h3 class="list-title">Basında</h3><ul class="link-list">{nature_links}</ul></div>
  </div>
</section>

<section class="salon" id="calismalar" aria-labelledby="calismalar-baslik">
  {salon_head(5, "calismalar", "Çalışmalar", "Ayrı projeler değil, ortak bir emek.")}
  <ul class="cards">{works}</ul>
</section>

<section class="salon" id="basin" aria-labelledby="basin-baslik">
  {salon_head(6, "basin", "Basın ve arşiv", D["press"]["text"])}
  <div class="press">{press}</div>
</section>

<section class="salon" id="hakkimda" aria-labelledby="hakkimda-baslik">
  {salon_head(7, "hakkimda", "Hakkımda", "")}
  <div class="split about">
    <figure class="framed oval"><span class="mat">{ph(a["img"], "Fotoğraf makinesiyle Mustafa Ünal")}</span></figure>
    <div>{"".join(f'<p class="body-text">{E(p)}</p>' for p in a["text"])}
      <p class="now"><b>Şu sıralar</b> {E(a["now"])}</p>
      <blockquote>{E(a["quote"])}</blockquote></div>
  </div>
</section>
"""
    return layout("/", "Mustafa Ünal — Bir ömür, birçok iz.", body, cls="home")


def build_gameks():
    g = D["gameks"]
    items = ""
    for x in g["history"]:
        imgs = "".join(f'<span class="tl-pic{" is-logo" if i["logo"] else ""}">{ph(i["src"], x["title"])}</span>' for i in x["imgs"])
        links = "".join(f'<a href="{E(l["href"])}">{E(l["label"])}</a>' for l in x["links"])
        cap = f'<p class="note">{E(x["note"])}</p>' if x["note"] else ""
        if not imgs:
            imgs = '<span class="tl-pic is-empty"></span>'
        items += (f'<li><p class="tl-year">{" ".join(E(t) for t in x["time"])}</p><div class="tl-text"><h3>{E(x["title"])}</h3>'
                  + "".join(f"<p>{E(p)}</p>" for p in x["text"]) + cap + (f"<p class=links>{links}</p>" if links else "") + f"</div>{imgs[:imgs.find('</span>')+7] if 'tl-pic' in imgs else imgs}</li>")
    body = f"""
<section class="lobby lobby-gameks">
  <figure class="framed hero-frame logo-frame"><span class="mat">{ph(g['logo'], 'GAMEKS logosu', lazy=False)}</span>
    <figcaption>{label("GAMEKS", ["1999 sonu – bugün", "Bilişim · danışmanlık · üretim"])}</figcaption></figure>
  <div class="lobby-text"><p class="salon-no">Özel salon</p><h1>Bilişimden<br>üretime.</h1><p class="lobby-lead">{E(g['lead'])}</p>
    <p class="lobby-lead">{" ".join(E(p) for p in g['intro'])}</p></div>
</section>
<section class="salon"><ol class="years">{items}</ol>
  <p class="more-link"><a href="/">Sergiye dön</a> · <a href="/kitaplar/adi-konmamis-islere-don-bicen-adam/">Kitap: Adı Konmamış İşlere Don Biçen Adam</a></p></section>"""
    return layout("/gameks/", "GAMEKS: Bilişimden üretime · Mustafa Ünal", body, desc=g["lead"], cls="page-gameks")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if not CANLI:
        (OUT / "CNAME").write_text("mustafaunal.gunerunal.com.tr\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text("User-agent: *\n" + ("Allow: /\n" if CANLI else "Disallow: /\n"))
    (OUT / "index.html").write_text(build_home(), encoding="utf-8")
    def write(path, content):
        f = OUT / path.lstrip("/") / "index.html"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")
    print("kitap sayfası:", books.build_all(write, layout))
    (OUT / "gameks").mkdir()
    (OUT / "gameks" / "index.html").write_text(build_gameks(), encoding="utf-8")
    nf = layout("/404", "Sayfa bulunamadı · Mustafa Ünal",
                '<section class="lobby"><div class="lobby-text"><p class="salon-no">Kayıp eser</p><h1>Bu salon boş.</h1>'
                '<p class="lobby-lead">Aradığınız sayfa taşınmış olabilir. <a href="/">Sergi girişine dönün.</a></p></div></section>')
    (OUT / "404.html").write_text(nf, encoding="utf-8")
    print("site üretildi →", OUT)


if __name__ == "__main__":
    main()
