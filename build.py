#!/usr/bin/env python3
"""Mustafa Ünal kişisel sitesi (test sürümü) üreticisi.

data/ ve static/ klasörlerinden docs/ altına statik site üretir:  python3 build.py
"""
import html
import json
import os
import re
import shutil

import books
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
D = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
ORIGIN = "https://mustafaunal.tr"
# SITE_MODE=canli: mustafaunal.tr için (arama motorlarına açık, test notu yok). Varsayılan: test.
CANLI = os.environ.get("SITE_MODE", "test") == "canli"
READER = "https://acipayam.com"
ASSET_V = "31"
E = lambda s: html.escape(str(s or ""), quote=True)  # noqa: E731

SERIES = [
    {"slug": "icimde-kalan-cocuk", "no": "I", "title": "İçimde Kalan Çocuk", "path": "/kitaplar/icimde-kalan-cocuk/",
     "line": "Çocukluğun saf pusulasından vicdana uzanan ilk on dört yıl."},
    {"slug": "karanlik-odada-yedi-ay", "no": "II", "title": "Karanlık Odada Yedi Ay", "path": "/kitaplar/karanlik-odada-yedi-ay/",
     "line": "1990’da Ankara-Akyurt’ta geçen yedi ay ve otuz beş yıl sonra yeniden açılan bir hayat."},
    {"slug": "uslu-dusler", "no": "III", "tag": "Bonus", "title": "US’lu Düşler", "path": "/kitaplar/uslu-dusler/",
     "line": "Kırk sayfa civarında; aç, oku, bitir. Zihni dürtmeyi sürdüren küçük bir beyin jimnastiği."},
    {"slug": "adi-konmamis-islere-don-bicen-adam", "no": "IV", "soon": True,
     "title": "Adı Konmamış İşlere Don Biçen Adam", "path": "/kitaplar/adi-konmamis-islere-don-bicen-adam/",
     "line": "GAMEKS, işler, fikirler ve internet: adı konmamış işlerle geçen bir çalışma hayatı."},
    {"slug": "gonul-dostu", "no": "V", "soon": True, "title": "Gönül Dostu", "path": "/kitaplar/gonul-dostu/",
     "line": "Sabit Kızılhan ile yol yürümek: dostluğun ve hak mücadelesinin tanıklığı."},
    {"slug": "uslu-dimag", "no": "VI", "tag": "Final", "soon": True, "title": "US’lu Dimağ", "path": "/kitaplar/uslu-dimag/",
     "line": "Doksan öğretide ölçüsü oturmuş bir zihin."},
]
OTHERS = [
    {"slug": "bana-koyunu-anlat", "title": "Bana Köyünü Anlat", "role": "Sözlü tarih", "who": [("Yazar", "Sabit Kızılhan"), ("Editör", "Mustafa Ünal")], "path": "/kitaplar/bana-koyunu-anlat/",
     "line": "Acıpayam köylerinin anlatıcılarıyla hazırlanan sözlü tarih çalışması."},
    {"slug": "kelekcide-yasamak", "title": "Kelekçi’de Yaşamak", "role": "Hatıra kitabı", "who": [("Yazar", "Dr. Oktar Öner"), ("Yayına hazırlayan", "Mustafa Ünal")],
     "path": "/kitaplar/kelekcide-yasamak/", "line": "El yazmaları, mektuplar ve radyo kayıtlarıyla bir Kelekçi hafızası."},
]

SALONS = [("kitaplar", "Kitaplar"), ("fotograflar", "Fotoğraflar"), ("mazi", "Mazi"), ("doga", "Doğa"),
          ("calismalar", "Çalışmalar"), ("basin", "Basın"), ("hakkimda", "Hakkımda")]
NAV = [(f"#{a}", t) for a, t in SALONS[:4]] + [("/gameks/", "GAMEKS"), ("#hakkimda", "Hakkımda")]


TEST_NOTE = ('<p class="foot-note">Bu adres, mustafaunal.tr içeriğiyle hazırlanmış yeni tasarımın test sürümüdür. '
             f'Asıl site: <a href="{ORIGIN}/">mustafaunal.tr</a></p>')


def og_slug(path):
    """Paylaşım kartı: /kitaplar/<kitap>/ altındaki sayfalar o kitabın kartı."""
    m = path.split("/")
    if len(m) > 2 and m[1] == "kitaplar" and (ROOT / "static/img/paylas" / f"{m[2]}.jpg").exists():
        return m[2]
    return ""


WA_URL = "https://wa.me/mustafaunal_tr"
WA_IC = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z"/><path d="M9 8.5c0 3.5 3 6.5 6.5 6.5l1-1.6-2-1-1 1c-1.2-.5-2.4-1.7-2.9-2.9l1-1-1-2z"/></svg>'


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
<meta property="og:title" content="{E(title)}">
<meta property="og:locale" content="tr_TR">
<meta property="og:type" content="{'book' if og_slug(path) else 'website'}">
<meta property="og:site_name" content="Mustafa Ünal">
<meta property="og:url" content="{ORIGIN}{path}">
<meta property="og:description" content="{E(desc or D['hero']['text'])}">
<meta property="og:image" content="{ORIGIN}/img/paylas/{og_slug(path) or 'mustafaunal-v2'}.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{"" if CANLI else chr(60) + "meta name=" + chr(34) + "robots" + chr(34) + " content=" + chr(34) + "noindex" + chr(34) + ">"}
<link rel="canonical" href="{ORIGIN}{path}">
<meta name="theme-color" content="#16231d">
<script>(function(){{var t;try{{t=localStorage.getItem("tema")}}catch(e){{}}document.documentElement.setAttribute("data-theme",t==="light"?"light":"dark")}})()</script>
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
  <a class="tema ara-btn" href="/ara/" aria-label="Sitede ara" title="Sitede ara"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg></a>
  <button type="button" class="tema" id="tema" aria-label="Açık ya da koyu görünüme geç" title="Açık / koyu görünüm">
    <svg class="gunes" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
    <svg class="ay" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
  </button>
  <details class="menu"><summary>Salonlar</summary><nav aria-label="Ana menü">{nav}</nav></details>
</header>
<main id="icerik">
{body}
{books.share_bar()}
</main>
<footer class="foot" id="iletisim">
  <div class="foot-in">
    <p class="foot-name">Mustafa Ünal</p>
    <p class="foot-line">Bir ömür, birçok iz. Sergi her zaman açık.</p>
    <p class="foot-wa-row"><a class="foot-wa" href="{WA_URL}" target="_blank" rel="noopener">{WA_IC}<span><b>WhatsApp’tan yazın</b>@mustafaunal_tr</span></a></p>
    <nav aria-label="İletişim">{contact}<a href="{READER}/">ACIPAYAM.com</a><a href="https://eskidenizli.com">Eski Denizli</a></nav>
  </div>
  {"" if CANLI else TEST_NOTE}
</footer>
<a class="wa-yuzen" href="{WA_URL}" target="_blank" rel="noopener" aria-label="WhatsApp’tan bana yazın">{WA_IC}<span>Bana yazın</span></a>
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
            f'<span class="spot">{ph("/img/kapak/" + b["slug"] + ".webp?v=" + ASSET_V, b["title"] + " kapağı", "cover", 400, 620)}'
            + ('<span class="rozet">Hazırlanıyor</span>' if soon else "") + '</span>'
            f'<span class="book-meta">{E(sub)}</span><span class="book-title">{E(b["title"])}</span>'
            + "".join(f'<span class="book-who"><small>{E(r)}</small> {E(n)}</span>' for r, n in b.get("who", []))
            + f'<span class="book-line">{E(b["line"])}</span><span class="book-act">{act}</span></a></li>')


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
    from urllib.parse import quote
    alinti = "".join(
        f'<li><button type="button" class="photo alinti-k" data-full="{q["img"]}" data-label="{E(q["title"])} · {E(q["author"])}" aria-label="Alıntı kartını büyüt">'
        f'<img src="{q["img"]}" alt="“{E(q["text"])}” · {E(q["title"])}, {E(q["author"])}" width="1080" height="1080" loading="lazy"></button>'
        f'<p class="alinti-act"><a href="https://wa.me/?text={quote("“" + q["text"] + "” " + q["title"] + ", " + q["author"] + " · " + ORIGIN + q["url"])}" target="_blank" rel="noopener">WhatsApp’ta paylaş</a>'
        f'<a href="{q["url"]}">Bölümü oku →</a></p></li>'
        for q in json.loads((ROOT / "data" / "alintilar.json").read_text(encoding="utf-8")))
    body = f"""
<section class="hero">
  <div class="hero-text">
    <p class="hero-roles">Yazar · Fotoğrafçı · Yerel hafıza</p>
    <h1>Mustafa<br>Ünal</h1>
    <p class="hero-motto">Bir ömür, birçok iz.</p>
    <p class="hero-lead">1969’da Balkıca’da başlayan bir hayat. Kitaplar, yaklaşık 250 bin fotoğraf, Acıpayam.com ve Eski Denizli ile yaşananları kaybolmadan görmek, unutmadan aktarmak için.</p>
    <p class="hero-actions"><a class="btn" href="#kitaplar">Kitaplarım</a><a class="btn btn-line" href="#fotograflar">Fotoğraflarım</a></p>
    {books.share_mini()}
  </div>
  <figure class="hero-portrait">
    <span class="halo" aria-hidden="true"></span>
    <img src="{h["portrait"]}" alt="Mustafa Ünal" width="700" height="700">
  </figure>
</section>

<section class="salon" id="kitaplar" aria-labelledby="kitaplar-baslik">
  {salon_head(1, "kitaplar", "Kitaplar", "Hepsi ücretsiz; internette okunur, PDF olarak indirilir. Bir kitaba dokunun, sayfası açılsın.")}
  <h3 class="row-title">US’lu Anlatılar <span>Altı kitaplık seri · <a href="/uslu-anlatilar/">Okuma sırası ve seri hakkında</a></span></h3>
  <ol class="shelf is-series">{series}</ol>
  <h3 class="row-title">Editörlüğünü yaptığım kitaplar <span>Başka yazarların eserleri</span></h3>
  <ul class="shelf">{others}</ul>
  <h3 class="row-title" id="alintilar">Kitaplardan <span>Bir cümle, bir kitap. Kartı paylaşın; okuyan bölüme ulaşsın.</span></h3>
  <ul class="alinti-list">{alinti}</ul>
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




def build_seri():
    """US’lu Anlatılar: altı kitaplık serinin okuma sırası."""
    us = "/kitaplar/icimde-kalan-cocuk/bolum/03/"
    rows = ""
    for i, b in enumerate(SERIES):
        soon = b.get("soon")
        durum = "Hazırlanıyor" if soon else "Yayında"
        etiket = f"Kitap {b['no']}" + (f" · {b['tag']}" if b.get("tag") else "")
        acts = (f'<a class="btn btn-line" href="{b["path"]}">Kitabın sayfası</a>' if soon else
                f'<a class="btn" href="{b["path"]}bolum/01/">Okumaya başla</a><a class="btn btn-line" href="{b["path"]}">Kitabın sayfası</a>')
        rows += (f'<li class="seri-k{" is-soon" if soon else ""}"><span class="seri-adim" aria-hidden="true">{b["no"]}</span>'
                 f'<a class="seri-kapak" href="{b["path"]}">{ph("/img/kapak/" + b["slug"] + ".webp?v=" + ASSET_V, b["title"] + " kapağı", "", 400, 620)}</a>'
                 f'<div class="seri-yazi"><p class="seri-et">{E(etiket)} <span class="seri-durum">{durum}</span></p><h2>{E(b["title"])}</h2>'
                 f'<p>{E(b["line"])}</p><p class="seri-act">{acts}</p></div></li>')
    yayinda = sum(1 for b in SERIES if not b.get("soon"))
    body = f"""
<section class="lobby seri-lobi">
  <div class="lobby-text"><p class="salon-no">Altı kitaplık seri</p><h1>US’lu Anlatılar</h1>
    <p class="lobby-lead">Çocukluktan bugüne bir ömrün anlatısı. Her kitap tek başına okunabilir; sırayla okuyan, bir hayatın nasıl bir düşünme biçimine dönüştüğünü izler. Şu an {yayinda} kitap yayında, {len(SERIES) - yayinda} kitap hazırlanıyor.</p>
    <blockquote class="seri-soz"><p>Us, akıldır. Ama benim için yalnızca düşünmek değildir. Sorgulamaktır, merak etmektir, bilmediğini kabul edebilmektir.</p>
      <p>“Us” kelimesini seçmemin bir başka nedeni de ismimle ilgili: Mustafa Ünal. U ve S…</p>
      <cite>İçimde Kalan Çocuk, “US Nedir?” · <a href="{us}">Bölümün tamamını okuyun</a></cite></blockquote>
    {books.share_mini()}</div>
</section>
<section class="salon seri-salon" aria-label="Okuma sırası">
  <p class="salon-no">Okuma sırası</p>
  <ol class="seri-yol">{rows}</ol>
  <p class="more-link"><a href="/#kitaplar">Bütün kitaplar</a></p>
</section>"""
    return layout("/uslu-anlatilar/", "US’lu Anlatılar: altı kitaplık seri · Mustafa Ünal", body,
                  desc="Mustafa Ünal’ın altı kitaplık US’lu Anlatılar serisi: okuma sırası, yayımlananlar ve hazırlananlar.", cls="page-seri")


def _strip(h):
    h = re.sub(r"<(script|style|svg|nav|aside|button)\b.*?</\1>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(h)).strip()


def write_search_index():
    """Site içi arama için dizin: /veri/ara.json"""
    items = []
    for f in sorted(OUT.rglob("index.html")):
        rel = "/" + str(f.parent.relative_to(OUT)).replace("\\", "/")
        rel = "/" if rel == "/." else rel + "/"
        t = f.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in t or rel.endswith("/pdf/") or rel == "/ara/":
            continue
        if rel == "/":
            for m in re.finditer(r'<section[^>]*\bid="([^"]+)"[^>]*>(.*?)</section>', t, re.S):
                h2 = re.search(r"<h2[^>]*>(.*?)</h2>", m.group(2), re.S)
                if h2:
                    items.append({"u": "/#" + m.group(1), "t": _strip(h2.group(1)), "k": "Ana sayfa", "b": "", "x": _strip(m.group(2))})
            continue
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
        title = _strip(h1.group(1)) if h1 else ""
        band = re.search(r'class="r-band"[^>]*><a [^>]*>.*?>([^<]+)</a>', t, re.S)
        book = band.group(1).strip() if band else ""
        art = re.search(r'<article class="reader".*?</article>', t, re.S)
        m = art or re.search(r'<main id="icerik">(.*)</main>', t, re.S)
        text = _strip(m.group(0) if art else (m.group(1) if m else ""))
        kind = "Kitap" if (book or rel.startswith("/kitaplar/")) else "Sayfa"
        if title and title in text[:len(title) + 40]:
            text = text[text.index(title) + len(title):].strip()
        items.append({"u": rel, "t": title, "k": kind, "b": book, "x": text})
    (OUT / "veri").mkdir(exist_ok=True)
    (OUT / "veri" / "ara.json").write_text(json.dumps(items, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(items)


def build_ara():
    body = """<section class="ara-sayfa">
  <p class="salon-no">Arama</p><h1>Ne arıyorsunuz?</h1>
  <p class="ara-lead">Kitapların bütün bölümlerinde ve sergideki salonlarda arayın.</p>
  <form class="ara-form" role="search" action="/ara/"><label class="sr-only" for="ara-q">Aranacak kelime</label>
    <input type="search" id="ara-q" name="q" placeholder="Bir isim, yer, kelime… (ör. Balkıca)" autocomplete="off" enterkeyhint="search">
    <button type="submit" class="btn">Ara</button></form>
  <p class="ara-durum" id="ara-durum" aria-live="polite">En az iki harf yazın.</p>
  <div id="ara-sonuc"></div>
</section>"""
    (OUT / "ara").mkdir(exist_ok=True)
    (OUT / "ara" / "index.html").write_text(layout("/ara/", "Sitede ara · Mustafa Ünal", body, desc="mustafaunal.tr içinde arama", cls="page-ara"), encoding="utf-8")

def write_sitemap():
    """Google için site haritası: yönlendirme sayfaları hariç bütün sayfalar."""
    from datetime import date
    today = date.today().isoformat()
    urls = []
    for f in sorted(OUT.rglob("index.html")):
        t = f.read_text(encoding="utf-8", errors="ignore")
        if 'http-equiv="refresh"' in t or 'name="robots" content="noindex"' in t:
            continue
        rel = "/" + str(f.parent.relative_to(OUT)).replace("\\", "/")
        rel = "/" if rel == "/." else rel + "/"
        pr = "1.0" if rel == "/" else ("0.5" if "/bolum/" in rel else "0.8")
        urls.append(f"  <url><loc>{ORIGIN}{rel}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>")
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    if CANLI:
        with open(OUT / "robots.txt", "a") as r:
            r.write(f"Sitemap: {ORIGIN}/sitemap.xml\n")
    return len(urls)

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
    write("/uslu-anlatilar/", build_seri())
    nf = layout("/404", "Sayfa bulunamadı · Mustafa Ünal",
                '<section class="lobby"><div class="lobby-text"><p class="salon-no">Kayıp eser</p><h1>Bu salon boş.</h1>'
                '<p class="lobby-lead">Aradığınız sayfa taşınmış olabilir. <a href="/">Sergi girişine dönün.</a></p></div></section>')
    (OUT / "404.html").write_text(nf, encoding="utf-8")
    build_ara()
    print("site üretildi →", OUT, "· arama dizini:", write_search_index(), "· site haritası:", write_sitemap(), "adres")


if __name__ == "__main__":
    main()
