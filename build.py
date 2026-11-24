#!/usr/bin/env python3
"""Mustafa Ünal kişisel sitesi (test sürümü) üreticisi.

data/ ve static/ klasörlerinden docs/ altına statik site üretir:  python3 build.py
"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
D = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
ORIGIN = "https://mustafaunal.tr"
READER = "https://acipayam.gunerunal.com.tr"   # kitapların okunduğu site
ASSET_V = "1"
E = lambda s: html.escape(str(s or ""), quote=True)  # noqa: E731

SERIES = [
    {"slug": "icimde-kalan-cocuk", "no": "I", "title": "İçimde Kalan Çocuk", "path": "/icimde-kalan-cocuk/",
     "line": "Çocukluğun saf pusulasından vicdana uzanan ilk on dört yıl."},
    {"slug": "karanlik-odada-yedi-ay", "no": "II", "title": "Karanlık Odada Yedi Ay", "path": "/karanlik-odada-yedi-ay/",
     "line": "1990’da Ankara-Akyurt’ta geçen yedi ay ve otuz beş yıl sonra yeniden açılan bir hayat."},
    {"slug": "uslu-dusler", "no": "III", "tag": "Bonus", "title": "US’lu Düşler", "path": "/uslu-dusler/",
     "line": "Kırk sayfa civarında; aç, oku, bitir. Zihni dürtmeyi sürdüren küçük bir beyin jimnastiği."},
    {"slug": "adi-konmamis-islere-don-bicen-adam", "no": "IV", "tag": "Hazırlanıyor", "soon": True,
     "title": "Adı Konmamış İşlere Don Biçen Adam", "path": "/adi-konmamis-islere-don-bicen-adam/",
     "line": "GAMEKS, işler, fikirler ve internet. 2027’de yayımlanması planlanıyor."},
    {"slug": "uslu-dimag", "no": "V", "tag": "Final", "title": "US’lu Dimağ", "path": "/uslu-dimag/",
     "line": "Doksan öğretide ölçüsü oturmuş bir zihin."},
]
OTHERS = [
    {"slug": "gonul-dostu", "title": "Gönül Dostu", "role": "Yazar", "path": "/gonul-dostu/",
     "line": "Sabit Kızılhan ile yol yürümek: 2005–2026 arasından dostluğun ve hak mücadelesinin tanıklığı."},
    {"slug": "bana-koyunu-anlat", "title": "Bana Köyünü Anlat", "role": "Editör · Sabit Kızılhan’ın derlemesi", "path": "/sabit/",
     "line": "Acıpayam köylerinin anlatıcılarıyla hazırlanan sözlü tarih çalışması."},
    {"slug": "kelekcide-yasamak", "title": "Kelekçi’de Yaşamak", "role": "Yayına hazırlayan · Dr. Oktar Öner’in kitabı",
     "path": "/kelekcide-yasamak/", "line": "El yazmaları, mektuplar ve radyo kayıtlarıyla bir Kelekçi hafızası."},
]

NAV = [("#kitaplar", "Kitaplar"), ("#fotograflar", "Fotoğraflar"), ("#mazi", "Mazi"), ("#doga", "Doğa"),
       ("/gameks/", "GAMEKS"), ("#hakkimda", "Hakkımda")]


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
<meta name="robots" content="noindex">
<link rel="canonical" href="{ORIGIN}{path}">
<meta name="theme-color" content="#f4f4f1">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={ASSET_V}">
</head>
<body class="{cls}">
<a class="skip" href="#icerik">İçeriğe geç</a>
<header class="bar">
  <a class="name" href="/">Mustafa Ünal</a>
  <details class="menu"><summary>Menü</summary><nav aria-label="Ana menü">{nav}</nav></details>
</header>
<main id="icerik">
{body}
</main>
<footer class="foot" id="iletisim">
  <div class="foot-in">
    <p class="foot-name">Mustafa Ünal</p>
    <p class="foot-line">Bir ömür, birçok iz. Kitaplar, fotoğraflar ve yerel hafıza.</p>
    <nav aria-label="İletişim">{contact}<a href="{READER}/">ACIPAYAM.com</a><a href="https://eskidenizli.com">Eski Denizli</a></nav>
  </div>
  <p class="foot-note">Bu adres, mustafaunal.tr içeriğiyle hazırlanmış yeni tasarımın test sürümüdür. Asıl site: <a href="{ORIGIN}/">mustafaunal.tr</a></p>
</footer>
<script src="/assets/site.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


def ph(src, alt, cls="", w=None, h=None, lazy=True):
    dims = f' width="{w}" height="{h}"' if w and h else ""
    return f'<img class="{cls}" src="{src}" alt="{E(alt)}"{dims}{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""}>'


def book_card(b, series=False):
    cover = f"/img/kapak/{b['slug']}.webp"
    label = (f"Kitap {b['no']}" + (f" · {b['tag']}" if b.get("tag") else "")) if series else b["role"]
    soon = b.get("soon")
    action = ('<span class="book-soon">Henüz yayında değil</span>' if soon else
              f'<a class="book-read" href="{READER}{b["path"]}">Oku</a>')
    zoom = (f'<button type="button" class="zoom" data-full="/img/kapak/{b["slug"]}-buyuk.webp" data-back="/img/kapak/{b["slug"]}-arka-buyuk.webp" '
            f'data-label="{E(b["title"])}" aria-label="{E(b["title"])} kapağını büyüt">{ph(cover, b["title"] + " kapağı", "cover", 400, 620)}</button>')
    return (f'<li class="book{" is-soon" if soon else ""}">{zoom}<p class="book-label">{E(label)}</p>'
            f'<h3>{E(b["title"])}</h3><p class="book-line">{E(b["line"])}</p>{action}</li>')


def contact_sheet():
    """Ana sayfadaki kontakt baskı: fotoğraflardan seçilmiş kareler, biri kırmızı kalemle işaretli."""
    order = [3, 0, 1, 6, 9, 4, 2, 7]   # seçki sırası
    pics = [D["photos"][i] for i in order if i < len(D["photos"])]
    cells = []
    for n, p in enumerate(pics, 1):
        mark = ""
        if n == 1:
            mark = ('<svg class="grease" viewBox="0 0 200 140" aria-hidden="true"><path d="M30 78 C 24 30, 120 6, 172 40 C 204 62, 186 120, 108 128 '
                    'C 44 134, 14 104, 34 64 C 46 40, 90 22, 140 26" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/></svg>')
        cells.append(f'<figure class="frame">{ph(p["img"], p.get("alt") or "Mustafa Ünal fotoğrafı", "", p.get("w"), p.get("h"), lazy=n > 4)}'
                     f'<figcaption>{n:02d}{"A" if n % 2 else ""}</figcaption>{mark}</figure>')
    return '<div class="sheet" aria-label="Fotoğraf arşivinden seçki">' + "".join(cells) + "</div>"


def build_home():
    h = D["hero"]
    roles = "".join(f"<li>{E(r)}</li>" for r in h["roles"])
    series = "".join(book_card(b, True) for b in SERIES)
    others = "".join(book_card(b) for b in OTHERS)
    tl = ""
    for t in D["timeline"]:
        links = "".join(f'<a href="{E(l["href"])}">{E(l["label"])}</a>' for l in t["links"])
        links = links.replace('href="#gameks"', 'href="/gameks/"').replace(ORIGIN + "/", "/")
        pic = ""
        if t["img"]:
            pic = ph(t["img"], t["title"], "tl-logo" if t["logo"] else "tl-img")
        tl += (f'<li class="tl"><p class="tl-time">{"<br>".join(E(x) for x in t["time"])}</p>'
               f'<div class="tl-body"><h3>{E(t["title"])}</h3><p>{E(t["text"])}</p>'
               f'{f"<p class=links>{links}</p>" if links else ""}</div>{pic}</li>')
    life = "".join(f'<figure>{ph(p["img"], p["cap"], "", p.get("w"), p.get("h"))}<figcaption>{E(p["cap"])}</figcaption></figure>'
                   for p in D["life"]["photos"])
    photos = "".join(
        f'<li class="{E(p["shape"])}"><button type="button" class="photo" data-full="{p["img"]}" data-label="Fotoğraf {i:02d}" '
        f'aria-label="Fotoğraf {i:02d} büyüt">{ph(p["img"], p.get("alt") or "Mustafa Ünal fotoğrafı", "", p.get("w"), p.get("h"))}'
        f'<span class="frame-no">{i:02d}</span></button></li>'
        for i, p in enumerate(D["photos"], 1))
    n = D["nature"]
    nature_links = "".join(f'<li><a href="{E(l["href"])}">{E(l["label"])}</a></li>' for l in n["links"])
    works = "".join(
        f'<li>{ph(w["img"], w["title"], "", w.get("w"), w.get("h"))}<div><p class="kicker">{E(w["kicker"])}</p><h3>{E(w["title"])}</h3>'
        f'<p>{E(w["text"])}</p><a href="{E("/gameks/" if w["link"]["href"] == "#gameks" else w["link"]["href"])}">{E(w["link"]["label"])}</a></div></li>'
        for w in D["works"])
    press = "".join(
        f'<div><h3>{E(g["title"])}</h3><ul>' + "".join(f'<li><a href="{E(l["href"])}">{E(l["label"])}</a></li>' for l in g["links"]) + "</ul></div>"
        for g in D["press"]["groups"])
    a = D["about"]
    about_text = "".join(f"<p>{E(p)}</p>" for p in a["text"])
    g = D["gameks"]
    body = f"""
<section class="hero">
  <div class="hero-text">
    <h1 class="sr-only">Mustafa Ünal</h1>
    <p class="hero-big" aria-hidden="true">Mustafa<br>Ünal</p>
    <p class="hero-motto">{E(" ".join(h["title"]))}</p>
    <p class="hero-lead">{E(h["text"])}</p>
    <ul class="roles">{roles}</ul>
    <p class="hero-links"><a class="btn" href="#kitaplar">Kitaplar</a><a class="btn btn-line" href="#fotograflar">Fotoğraflar</a></p>
  </div>
  {contact_sheet()}
</section>

<section class="sec" id="kitaplar">
  <header class="sec-head"><h2>Kitaplar</h2><p>Şimdi kitaplarımı yazıyorum. Hepsi ücretsiz; internette okunabilir, PDF olarak indirilebilir. Kapağa dokunursanız büyür, arka kapağı da okunur.</p></header>
  <div class="series">
    <div class="series-head"><h3>US’lu Anlatılar</h3><p>Beş kitaplık seri: çocukluktan bugüne bir hayatın hatıraları ve süzgeçten geçmiş düşünceleri.</p></div>
    <ol class="books">{series}</ol>
  </div>
  <div class="series">
    <div class="series-head"><h3>Yazarlık, editörlük, yayına hazırlık</h3><p>Dostluğun, köylerin ve bir ömrün son durağının kitapları.</p></div>
    <ul class="books">{others}</ul>
  </div>
</section>

<section class="sec sec-dark" id="fotograflar">
  <header class="sec-head"><h2>Fotoğraflar</h2><p>Yaklaşık 250 bin kareden küçük bir seçki. Büyütmek için kareye dokunun. <a href="{E(D['photos_link']['href'])}">{E(D['photos_link']['label'])}</a></p></header>
  <ul class="photos">{photos}</ul>
</section>

<section class="sec" id="mazi">
  <header class="sec-head"><h2>Mazi</h2><p>Bugünden geriye: birikenler kaybolmasın.</p></header>
  <ol class="timeline">{tl}</ol>
  <div class="life">
    <div class="life-head"><h3>{E(D['life']['title'])}</h3><p>{E(D['life']['text'])}</p></div>
    <div class="life-grid">{life}</div>
  </div>
</section>

<section class="sec nature" id="doga">
  <figure class="nature-pic">{ph(n['img'], n['cap'])}<figcaption>{E(n['cap'])}</figcaption></figure>
  <div class="nature-text">
    <p class="kicker">{E(n['eyebrow'])}</p>
    <h2>{E(" ".join(n['title']))}</h2>
    <p>{E(n['text'])}</p>
    <ul class="link-list">{nature_links}</ul>
  </div>
</section>

<section class="sec" id="calismalar">
  <header class="sec-head"><h2>Çalışmalar</h2><p>Ayrı projeler değil, ortak bir emek.</p></header>
  <ul class="works">{works}</ul>
</section>

<section class="sec gameks-teaser">
  <a class="gameks-card" href="/gameks/">
    {ph(g['logo'], 'GAMEKS logosu', 'gameks-logo')}
    <div><p class="kicker">{E(g['eyebrow'])}</p><h2>GAMEKS: {E(" ".join(g['title']))}</h2><p>{E(g['lead'])}</p><span class="more">Tarihçeyi okuyun</span></div>
  </a>
</section>

<section class="sec" id="basin">
  <header class="sec-head"><h2>{E(D['press']['title'])}</h2><p>{E(D['press']['text'])}</p></header>
  <div class="press">{press}</div>
</section>

<section class="sec about" id="hakkimda">
  {ph(a['img'], 'Fotoğraf makinesiyle Mustafa Ünal', 'about-img')}
  <div>
    <h2>Hakkımda</h2>
    {about_text}
    <p class="now"><b>Şu sıralar</b>{E(a['now'])}</p>
    <blockquote>{E(a['quote'])}</blockquote>
  </div>
</section>
"""
    return layout("/", "Mustafa Ünal — Bir ömür, birçok iz.", body, cls="home")


def build_gameks():
    g = D["gameks"]
    items = ""
    for x in g["history"]:
        imgs = "".join(ph(i["src"], x["title"], "h-logo" if i["logo"] else "h-img") for i in x["imgs"])
        links = "".join(f'<a href="{E(l["href"])}">{E(l["label"])}</a>' for l in x["links"])
        cap = f'<figcaption>{E(x["note"])}</figcaption>' if x["note"] else ""
        items += (f'<li><p class="tl-time">{"<br>".join(E(t) for t in x["time"])}</p><div class="tl-body"><h3>{E(x["title"])}</h3>'
                  + "".join(f"<p>{E(p)}</p>" for p in x["text"])
                  + (f"<p class=links>{links}</p>" if links else "") + "</div>"
                  + (f"<figure>{imgs}{cap}</figure>" if imgs else "")
                  + "</li>")
    body = f"""
<section class="page-head">
  {ph(g['logo'], 'GAMEKS logosu', 'gameks-logo', lazy=False)}
  <div><p class="kicker">{E(g['eyebrow'])}</p><h1>{E(" ".join(g['title']))}</h1><p class="hero-lead">{E(g['lead'])}</p></div>
</section>
<section class="sec">
  <header class="sec-head"><h2>{E(g['intro_title'])}</h2><div>{"".join(f"<p>{E(p)}</p>" for p in g['intro'])}</div></header>
  <ol class="timeline">{items}</ol>
  <p class="back"><a href="/">Ana sayfaya dön</a> · <a href="{READER}/adi-konmamis-islere-don-bicen-adam/">Kitabı: Adı Konmamış İşlere Don Biçen Adam</a></p>
</section>"""
    return layout("/gameks/", "GAMEKS: Bilişimden üretime · Mustafa Ünal", body, desc=g["lead"], cls="page-gameks")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / "CNAME").write_text("mustafaunal.gunerunal.com.tr\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    (OUT / "index.html").write_text(build_home(), encoding="utf-8")
    (OUT / "gameks").mkdir()
    (OUT / "gameks" / "index.html").write_text(build_gameks(), encoding="utf-8")
    nf = layout("/404", "Sayfa bulunamadı · Mustafa Ünal",
                '<section class="page-head"><div><h1>Bu sayfa burada değil.</h1><p class="hero-lead">Adres değişmiş olabilir. '
                '<a href="/">Ana sayfaya dönün.</a></p></div></section>')
    (OUT / "404.html").write_text(nf, encoding="utf-8")
    print("site üretildi →", OUT)


if __name__ == "__main__":
    main()
