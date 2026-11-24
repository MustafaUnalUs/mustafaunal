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
ASSET_V = "2"
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

SALONS = [("kitaplar", "Kitaplar"), ("fotograflar", "Fotoğraflar"), ("mazi", "Mazi"), ("doga", "Doğa"),
          ("calismalar", "Çalışmalar"), ("hakkimda", "Hakkımda")]
NAV = [(f"#{a}", t) for a, t in SALONS[:4]] + [("/gameks/", "GAMEKS"), ("#hakkimda", "Hakkımda")]


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
  <p class="foot-note">Bu adres, mustafaunal.tr içeriğiyle hazırlanmış yeni tasarımın test sürümüdür. Asıl site: <a href="{ORIGIN}/">mustafaunal.tr</a></p>
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
    sub = (f"US’lu Anlatılar · Kitap {b['no']}" + (f" · {b['tag']}" if b.get("tag") else "")) if series else b["role"]
    action = ('<span class="soon">Henüz yayında değil</span>' if soon else
              f'<a class="read" href="{READER}{b["path"]}">Kitabı oku</a>')
    zoom = (f'<button type="button" class="zoom" data-full="/img/kapak/{b["slug"]}-buyuk.webp" data-back="/img/kapak/{b["slug"]}-arka-buyuk.webp" '
            f'data-label="{E(b["title"])}" aria-label="{E(b["title"])} kapağını büyüt">'
            f'{ph("/img/kapak/" + b["slug"] + ".webp", b["title"] + " kapağı", "cover", 400, 620)}</button>')
    return f'<li class="book{" is-soon" if soon else ""}"><div class="spot">{zoom}</div>{label(b["title"], [sub, b["line"]], action)}</li>'


def build_home():
    h = D["hero"]
    hero_photo = next((p for p in D["photos"] if "photo-18" in p["img"]), D["photos"][0])   # şimşek
    guide = "".join(f'<li><a href="#{a}"><span>{i}</span>{E(t)}</a></li>' for i, (a, t) in enumerate(SALONS, 1))
    series = "".join(book(b, True) for b in SERIES)
    others = "".join(book(b) for b in OTHERS)
    caps = ["Acıpayam’dan bir yol", "Köy evi", "Denizli üzerinde şimşek", "Dalaman Çayı kirliliği", "Sohbet",
            "Kayada çiçek", "Bir ömür", "Ova ve bulutlar", "Toplu iftar", "Keşkek kazanı", "Örümcek"]
    photos = ""
    for i, p in enumerate(D["photos"], 1):
        shape = p["shape"] or ""
        photos += (f'<li class="hang {E(shape)}"><button type="button" class="photo" data-full="{p["img"]}" '
                   f'data-label="Fotoğraf {i:02d}" aria-label="Fotoğraf {i:02d}: büyüt"><span class="mat">'
                   f'{ph(p["img"], p.get("alt") or "Mustafa Ünal fotoğrafı", "", p.get("w"), p.get("h"))}</span></button>'
                   f'<p class="tag">No. {i:02d} · Mustafa Ünal</p></li>')
    tl = ""
    for t in D["timeline"]:
        links = "".join(f'<a href="{E("/gameks/" if l["href"] == "#gameks" else l["href"])}">{E(l["label"])}</a>' for l in t["links"])
        pic = ""
        if t["img"]:
            pic = f'<span class="tl-pic{" is-logo" if t["logo"] else ""}">{ph(t["img"], t["title"])}</span>'
        tl += (f'<li><p class="tl-year">{"<br>".join(E(x) for x in t["time"])}</p>'
               f'<div class="tl-card">{pic}<h3>{E(t["title"])}</h3><p>{E(t["text"])}</p>{f"<p class=links>{links}</p>" if links else ""}</div></li>')
    life = "".join(f'<figure class="framed small"><span class="mat">{ph(p["img"], p["cap"], "", p.get("w"), p.get("h"))}</span>'
                   f'<figcaption>{label(p["cap"].split(" · ")[0], [" · ".join(p["cap"].split(" · ")[1:]), "Fotoğraf: Mustafa Ünal"])}</figcaption></figure>'
                   for p in D["life"]["photos"])
    n = D["nature"]
    nature_links = "".join(f'<li><a href="{E(l["href"])}">{E(l["label"])}</a></li>' for l in n["links"])
    works = "".join(
        f'<li class="case">{ph(w["img"], w["title"], "", w.get("w"), w.get("h"))}<div>{label(w["title"], [w["kicker"], w["text"]])}'
        f'<a class="case-link" href="{E("/gameks/" if w["link"]["href"] == "#gameks" else w["link"]["href"])}">{E(w["link"]["label"])}</a></div></li>'
        for w in D["works"])
    press = "".join(
        f'<div><h3>{E(g["title"])}</h3><ul>' + "".join(f'<li><a href="{E(l["href"])}">{E(l["label"])}</a></li>' for l in g["links"]) + "</ul></div>"
        for g in D["press"]["groups"])
    a = D["about"]
    g = D["gameks"]
    body = f"""
<section class="lobby">
  <figure class="framed hero-frame">
    <span class="mat">{ph(hero_photo["img"], "Denizli üzerinde şimşek, Mustafa Ünal fotoğrafı", "", hero_photo.get("w"), hero_photo.get("h"), lazy=False)}</span>
    <figcaption>{label("Denizli’de gece", ["Fotoğraf: Mustafa Ünal", "Yaklaşık 250 bin karelik arşivden"])}</figcaption>
  </figure>
  <div class="lobby-text">
    <p class="salon-no">Giriş</p>
    <h1>Bir ömür,<br>birçok iz.</h1>
    <p class="lobby-lead">{E(h["text"])} Sergi, Mustafa Ünal’ın kitaplarını, fotoğraflarını ve yerel hafıza çalışmalarını bir araya getiriyor.</p>
    <nav class="guide" aria-label="Sergi rehberi"><p>Sergi rehberi</p><ol>{guide}</ol></nav>
  </div>
</section>

<section class="salon" id="kitaplar" aria-labelledby="kitaplar-baslik">
  {salon_head(1, "kitaplar", "Kitaplar", "Şimdi kitaplarımı yazıyorum. Hepsi ücretsiz; internette okunur, PDF olarak indirilir. Kapağa dokunun; büyür, arka kapağı da okunur.")}
  <h3 class="shelf-title">US’lu Anlatılar <span>beş kitaplık seri</span></h3>
  <ol class="shelf">{series}</ol>
  <h3 class="shelf-title">Yazarlık, editörlük, yayına hazırlık</h3>
  <ul class="shelf">{others}</ul>
</section>

<section class="salon" id="fotograflar" aria-labelledby="fotograflar-baslik">
  {salon_head(2, "fotograflar", "Fotoğraflar", "Yaklaşık 250 bin kareden küçük bir seçki. Bir kareye dokunun; büyür, oklarla gezilir.")}
  <ul class="wall">{photos}</ul>
  <p class="more-link"><a href="{E(D['photos_link']['href'])}">{E(D['photos_link']['label'])}</a></p>
  <h3 class="shelf-title">{E(D['life']['title'])} <span>{E(D['life']['text'])}</span></h3>
  <div class="wall-small">{life}</div>
</section>

<section class="salon" id="mazi" aria-labelledby="mazi-baslik">
  {salon_head(3, "mazi", "Mazi", "Bugünden geriye, 2026’dan Balkıca’ya: birikenler kaybolmasın.")}
  <ol class="corridor">{tl}</ol>
</section>

<section class="salon salon-split" id="doga" aria-labelledby="doga-baslik">
  <figure class="framed">
    <span class="mat">{ph(n["img"], n["cap"], lazy=False)}</span>
    <figcaption>{label("Dalaman Çayı, Saimin Köprüsü", ["2016", "Fotoğraf: çeken kişi bilinmiyor"])}</figcaption>
  </figure>
  <div>
    {salon_head(4, "doga", "Fotoğraf bazen itirazın kaydıdır.", n["text"])}
    <ul class="link-list">{nature_links}</ul>
  </div>
</section>

<section class="salon" id="calismalar" aria-labelledby="calismalar-baslik">
  {salon_head(5, "calismalar", "Çalışmalar", "Ayrı projeler değil, ortak bir emek.")}
  <ul class="cases">{works}</ul>
  <a class="gameks-door" href="/gameks/">
    {ph(g["logo"], "GAMEKS logosu", "gameks-logo")}
    <span><b>GAMEKS tarihçesi</b><em>{E(g["lead"])}</em></span>
  </a>
  <div class="press"><h3 class="shelf-title">{E(D['press']['title'])} <span>{E(D['press']['text'])}</span></h3><div class="press-grid">{press}</div></div>
</section>

<section class="salon salon-split about" id="hakkimda" aria-labelledby="hakkimda-baslik">
  <figure class="framed oval"><span class="mat">{ph(a["img"], "Fotoğraf makinesiyle Mustafa Ünal")}</span>
    <figcaption>{label("Mustafa Ünal", ["1969, Balkıca", "Yazar, fotoğrafçı"])}</figcaption></figure>
  <div>
    {salon_head(6, "hakkimda", "Hakkımda", "")}
    {"".join(f"<p>{E(p)}</p>" for p in a["text"])}
    <p class="now"><b>Şu sıralar</b> {E(a["now"])}</p>
    <blockquote>{E(a["quote"])}</blockquote>
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
        items += (f'<li><p class="tl-year">{"<br>".join(E(t) for t in x["time"])}</p><div class="tl-card">{imgs}{cap}<h3>{E(x["title"])}</h3>'
                  + "".join(f"<p>{E(p)}</p>" for p in x["text"]) + (f"<p class=links>{links}</p>" if links else "") + "</div></li>")
    body = f"""
<section class="lobby lobby-gameks">
  <figure class="framed hero-frame logo-frame"><span class="mat">{ph(g['logo'], 'GAMEKS logosu', lazy=False)}</span>
    <figcaption>{label("GAMEKS", ["1999 sonu – bugün", "Bilişim · danışmanlık · üretim"])}</figcaption></figure>
  <div class="lobby-text"><p class="salon-no">Özel salon</p><h1>Bilişimden<br>üretime.</h1><p class="lobby-lead">{E(g['lead'])}</p>
    <p class="lobby-lead">{" ".join(E(p) for p in g['intro'])}</p></div>
</section>
<section class="salon"><ol class="corridor">{items}</ol>
  <p class="more-link"><a href="/">Sergiye dön</a> · <a href="{READER}/adi-konmamis-islere-don-bicen-adam/">Kitap: Adı Konmamış İşlere Don Biçen Adam</a></p></section>"""
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
                '<section class="lobby"><div class="lobby-text"><p class="salon-no">Kayıp eser</p><h1>Bu salon boş.</h1>'
                '<p class="lobby-lead">Aradığınız sayfa taşınmış olabilir. <a href="/">Sergi girişine dönün.</a></p></div></section>')
    (OUT / "404.html").write_text(nf, encoding="utf-8")
    print("site üretildi →", OUT)


if __name__ == "__main__":
    main()
