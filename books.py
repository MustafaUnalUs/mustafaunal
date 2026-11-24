"""Kitap sayfaları ve okuma sayfaları (Mustafa Ünal sitesi, müze tasarımı).

Veriler data/kitap/ altında: düzenlenmiş PDF'lerden çıkarılmış bölümler (kitaplar/*.json) ve tanıtımlar.
"""
import html
import json
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
K = ROOT / "data" / "kitap"
MEDIA_BASE = os.environ.get("MEDIA_BASE", "https://acipayam.com/")
MEDIA_RE = re.compile(r"https://acipayam\.com/([^\"\s<>]*?(?:\.mp3|/bolumler/))")
E = lambda s: html.escape(str(s or ""), quote=True)  # noqa: E731


def J(name):
    return json.loads((K / name).read_text(encoding="utf-8"))


def plain(s):
    return re.sub(r"<[^>]+>", "", html.unescape(s or ""))


def slugify(s):
    tr = str.maketrans("çğıöşüâîûÇĞİÖŞÜÂÎÛ", "cgiosuaiuCGIOSUAIU")
    return re.sub(r"[^a-z0-9]+", "-", plain(s).translate(tr).lower()).strip("-")[:60]


def minutes(words):
    return max(1, math.ceil(words / 200))


def tr_title(s):
    s = plain(s)
    if s.upper() != s:
        return s
    small = {"VE", "İLE", "DE", "DA", "Mİ", "MI", "MU", "MÜ", "Kİ", "YA"}
    keep = {"GAMEKS", "US", "PTT", "TRT", "ADB", "AI", "ADEBİR", "ACİBİR"}
    out = []
    for i, w in enumerate(s.split(" ")):
        low = w.replace("I", "ı").replace("İ", "i").lower()
        if i and w in small:
            out.append(low)
        elif re.sub(r"[’'].*$", "", w) in keep:
            out.append(w)
        else:
            out.append(low[:1].replace("i", "İ").upper() + low[1:] if low else low)
    return " ".join(out)


def mb(n):
    return f"{n / 1_048_576:.0f} MB" if n > 1_048_576 else f"{n / 1024:.0f} KB"


HOME, PAGES, USLU, SABIT = J("home.json"), J("book-pages.json"), J("uslu-dusler.json"), J("sabit.json")
SOON_SRC = next(u for u in HOME["upcoming"] if u["title"].startswith("Adı Konmamış"))

BOOKS = [
    {"slug": "icimde-kalan-cocuk", "title": "İçimde Kalan Çocuk", "author": "Mustafa Ünal", "seri": "Kitap I",
     "intro": PAGES["icimde-kalan-cocuk"]["intro"], "audio": PAGES["icimde-kalan-cocuk"]["audio_full"],
     "tracks": PAGES["icimde-kalan-cocuk"].get("tracks"), "tracks_base": PAGES["icimde-kalan-cocuk"]["chapters_audio_base"]},
    {"slug": "karanlik-odada-yedi-ay", "title": "Karanlık Odada Yedi Ay", "author": "Mustafa Ünal", "seri": "Kitap II",
     "intro": PAGES["karanlik-odada-yedi-ay"]["intro"], "audio": PAGES["karanlik-odada-yedi-ay"]["audio_full"]},
    {"slug": "uslu-dusler", "title": "US’lu Düşler", "subtitle": "Olmuş Zekâ", "author": "Mustafa Ünal", "seri": "Kitap III · Bonus",
     "intro": USLU["intro"], "overview": USLU["overview"], "audio": USLU["audio_full"], "audio_len": USLU["listen"]["duration"]},
    {"slug": "adi-konmamis-islere-don-bicen-adam", "title": "Adı Konmamış İşlere Don Biçen Adam", "author": "Mustafa Ünal",
     "seri": "Kitap IV · Hazırlanıyor", "soon": True, "status": SOON_SRC["status"],
     "intro": SOON_SRC["tagline"] + " " + " ".join(SOON_SRC["paragraphs"])},
    {"slug": "uslu-dimag", "title": "US’lu Dimağ", "author": "Mustafa Ünal", "seri": "Kitap V · Final",
     "intro": "Bu kitap öğretmek ya da ikna etmek için yazılmadı. Bir insanın hayatın içinde düşe kalka, zamanla oluşmuş us izlerinin kaydı; davranıştan zamana, güvenden vedaya doksan kısa öğreti."},
    {"slug": "gonul-dostu", "title": "Gönül Dostu", "subtitle": "Sabit Kızılhan ile Yol Yürümek", "author": "Mustafa Ünal",
     "role": "Bağımsız eser", "intro": next(u for u in HOME["upcoming"] if u["title"].startswith("Gönül"))["paragraphs"][0]},
    {"slug": "bana-koyunu-anlat", "title": "Bana Köyünü Anlat", "author": "Sabit Kızılhan", "editor": "Mustafa Ünal",
     "role": "Sözlü tarih · Editörlük", "intro": SABIT["lead"], "audio": SABIT["audio_full"]},
    {"slug": "kelekcide-yasamak", "title": "Kelekçi’de Yaşamak", "author": "Dr. Oktar Öner", "editor": "Mustafa Ünal",
     "role": "Yayına hazırlık", "intro": PAGES["kelekcide-yasamak"]["intro"], "audio": PAGES["kelekcide-yasamak"]["audio_full"],
     "quote": PAGES["kelekcide-yasamak"]["quote"]},
]
SERIES = [b for b in BOOKS if b.get("seri")]
for b in BOOKS:
    b["base"] = f"/kitaplar/{b['slug']}/"
    b["cover"] = f"/img/kapak/{b['slug']}.webp"
    if not b.get("soon"):
        b["data"] = J(f"kitaplar/{b['slug']}.json")
        b["pdf"] = f"/indir/{b['slug']}.pdf"
        b["pdf_size"] = (ROOT / "static" / "indir" / f"{b['slug']}.pdf").stat().st_size
        b["words"] = sum(c["words"] for c in b["data"]["chapters"])

INTERVIEWS = {int(i["no"]): i for i in SABIT["interviews"]}
for c in next(b for b in BOOKS if b["slug"] == "bana-koyunu-anlat")["data"]["chapters"]:
    m = re.match(r"(\d+)\.\s", c["title"])
    if m and int(m.group(1)) in INTERVIEWS:
        c["interview"] = INTERVIEWS[int(m.group(1))]


def chapter_url(book, i):
    return f"{book['base']}bolum/{i + 1:02d}/"


def yt(vid, title="Video"):
    return (f'<div class="yt" data-id="{E(vid)}"><button type="button" aria-label="{E(title)} videosunu oynat">'
            f'<img src="https://i.ytimg.com/vi/{E(vid)}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">'
            f'<span class="yt-play" aria-hidden="true"></span><span class="yt-title">{E(title)}</span></button></div>')


def fix_yt(htm):
    return re.sub(r'<div class="yt" data-id="([\w-]+)" data-title="([^"]*)"></div>',
                  lambda m: yt(m.group(1), html.unescape(m.group(2))), htm)


def render_blocks(blocks, slug):
    out, first = [], True
    for b in blocks:
        k, h = b["k"], b.get("h", "")
        t = plain(h).strip()
        if k == "img":
            cap = b.get("cap", "")
            out.append(f'<figure class="r-photo"><img src="{b["src"]}" alt="{E(plain(cap) or "Kitaptan fotoğraf")}" '
                       f'width="{b["w"]}" height="{b["ht"]}" loading="lazy">' + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")
        elif k == "orn":
            out.append('<p class="orn" aria-hidden="true">◆</p>')
        elif k == "h3":
            out.append(f'<h2 class="sub" id="{slugify(t)}">{h}</h2>')
        elif k == "verse":
            out.append(f'<p class="verse">{h}</p>')
        elif k == "small":
            out.append(f'<p class="note">{h}</p>')
        else:
            c = ["alt"] if k == "alt" else []
            if t.startswith("✧"):
                c = ["bro"]
                h = re.sub(r"^\s*✧\s*", "", h)
            if first and k == "p" and not c and len(t) > 120:
                c.append("lead-p")
                first = False
            out.append(f'<p{" class=" + chr(34) + " ".join(c) + chr(34) if c else ""}>{h}</p>')
    return "\n".join(out)


def covers(b):
    items = ""
    for side, label in (("", "Ön kapak"), ("-arka", "Arka kapak")):
        items += (f'<button type="button" class="zoom" data-full="/img/kapak/{b["slug"]}{side}-buyuk.webp" '
                  f'data-back="/img/kapak/{b["slug"]}{"-arka" if not side else ""}-buyuk.webp" data-label="{E(b["title"])} · {label}" '
                  f'aria-label="{E(b["title"])}, {label.lower()}: büyüt"><img src="/img/kapak/{b["slug"]}{side}.webp" '
                  f'alt="{E(b["title"])} {label.lower()}" width="400" height="620"><span>{label}</span></button>')
    return f'<figure class="bk-covers">{items}<figcaption>Büyütmek ve okumak için kapağa dokunun</figcaption></figure>'


def series_strip(book):
    if not book.get("seri"):
        return ""
    li = "".join(
        f'<li><a href="{b["base"]}"{" aria-current=" + chr(34) + "page" + chr(34) if b is book else ""}>'
        f'<img src="{b["cover"]}" alt="" width="400" height="620" loading="lazy"><span class="s-no">{E(b["seri"])}</span>'
        f'<span class="s-t">{E(b["title"])}</span></a></li>' for b in SERIES)
    return (f'<section class="bk-series"><h2>US’lu Anlatılar</h2><p>Beş kitaplık seri. Her kitap tek başına da okunabilir.</p>'
            f'<ol>{li}</ol></section>')


def toc(book):
    rows, part = [], object()
    for i, c in enumerate(book["data"]["chapters"]):
        if c["part"] != part:
            part = c["part"]
            if rows:
                rows.append("</ol>")
            rows.append((f'<h3 class="toc-part">{E(tr_title(part))}</h3>' if part else "") + '<ol class="toc">')
        title = c["interview"]["title"] + " · " + c["interview"]["subtitle"] if c.get("interview") else tr_title(c["title"])
        rows.append(f'<li><a href="{chapter_url(book, i)}"><span class="toc-n">{i + 1:02d}</span>'
                    f'<span class="toc-t">{E(title)}</span><span class="toc-m">{minutes(c["words"])} dk</span></a></li>')
    rows.append("</ol>")
    return "\n".join(rows)


def build_book(b, layout):
    by = E(b["author"]) + (f" · Editör: {E(b['editor'])}" if b.get("editor") else "")
    kicker = f"US’lu Anlatılar · {b['seri']}" if b.get("seri") else b.get("role", "")
    sub = f'<p class="bk-sub">{E(b["subtitle"])}</p>' if b.get("subtitle") else ""
    if b.get("soon"):
        facts = ""
        actions = f'<p class="bk-status"><b>Henüz yayında değil.</b> {E(b["status"])}. Yayımlandığında burada okunabilecek, PDF olarak indirilebilecek.</p>'
        body_main = ""
    else:
        hours = b["words"] / 200 / 60
        read = f"yaklaşık {format(hours, '.1f').replace('.', ',')} saat" if hours >= 1 else f"{minutes(b['words'])} dakika"
        facts = (f'<dl class="bk-facts"><div><dt>Bölüm</dt><dd>{len(b["data"]["chapters"])}</dd></div>'
                 f'<div><dt>Okuma</dt><dd>{read}</dd></div><div><dt>PDF</dt><dd>{mb(b["pdf_size"])}</dd></div></dl>')
        acts = [f'<a class="btn" href="{chapter_url(b, 0)}">Okumaya başla</a>',
                f'<a class="btn btn-line" href="{b["pdf"]}" download>PDF indir</a>']
        if b.get("audio"):
            acts.append('<a class="btn btn-line" href="#dinle">Sesli kitap</a>')
        actions = '<p class="bk-actions">' + "".join(acts) + "</p>"
        side = []
        if b.get("overview"):
            side.append('<section class="bk-panel"><h2>Kitabın içinden</h2>' + "".join(f"<p>{E(p)}</p>" for p in b["overview"]) + "</section>")
        if b.get("quote"):
            side.append(f'<blockquote class="bk-quote">{E(b["quote"])}</blockquote>')
        if b.get("audio"):
            tracks = ""
            if b.get("tracks"):
                tracks = '<h3 class="toc-part">Bölüm bölüm dinle</h3><ol class="toc">' + "".join(
                    f'<li><a href="{E(b["tracks_base"] + t["file"])}"><span class="toc-n">{t["track"]:02d}</span>'
                    f'<span class="toc-t">{E(tr_title(t["title"]))}</span><span class="toc-m">{int(t["planned_duration_seconds"]) // 60}:'
                    f'{int(t["planned_duration_seconds"]) % 60:02d}</span></a></li>' for t in b["tracks"]) + "</ol>"
            side.append(f'<section class="bk-panel" id="dinle"><h2>Sesli kitap</h2>'
                        f'<p class="muted">Kayıt kitabın ilk yayımlanan sürümünden hazırlandı; metindeki son düzeltmeler kayda yansımamış olabilir.</p>'
                        f'<audio controls preload="none" src="{E(b["audio"])}"></audio>{tracks}</section>')
        body_main = (f'<div class="bk-body"><section class="bk-toc" id="icindekiler"><h2>İçindekiler</h2>{toc(b)}</section>'
                     f'<aside class="bk-side">{"".join(side)}</aside></div>')
    body = f"""<section class="bk-hero">
  {covers(b)}
  <div class="bk-copy">
    <p class="salon-no">{E(kicker)}</p>
    <h1>{E(b['title'])}</h1>{sub}
    <p class="bk-by">{by}</p>
    <p class="bk-intro">{E(b['intro'])}</p>
    {facts}{actions}
  </div>
</section>
{series_strip(b)}
{body_main}
<p class="bk-back"><a href="/#kitaplar">Bütün kitaplar</a></p>"""
    return layout(b["base"], f"{b['title']} · Mustafa Ünal", body, desc=b["intro"][:160], cls="page-book")


def build_chapter(b, i, layout):
    ch = b["data"]["chapters"]
    c = ch[i]
    iv = c.get("interview")
    title = iv["title"] if iv else tr_title(c["title"])
    lead = f'<p class="r-lead">{E(iv["subtitle"])}</p>' if iv else ""
    video = yt(iv["video"], f'{iv["title"]} — {iv["subtitle"]}') if iv and iv.get("video") else ""
    extra = ('<section class="r-extra">' + "".join(fix_yt(x) for x in iv["extra"]) + "</section>") if iv and iv.get("extra") else ""
    part = f'<p class="r-part">{E(tr_title(c["part"]))}</p>' if c.get("part") else ""
    prev_ = (chapter_url(b, i - 1), tr_title(ch[i - 1]["title"])) if i else None
    next_ = (chapter_url(b, i + 1), tr_title(ch[i + 1]["title"])) if i + 1 < len(ch) else None
    pager = ('<nav class="r-pager" aria-label="Bölümler">'
             + (f'<a href="{prev_[0]}"><small>Önceki bölüm</small>{E(prev_[1])}</a>' if prev_ else "<span></span>")
             + (f'<a class="nx" href="{next_[0]}"><small>Sonraki bölüm</small>{E(next_[1])}</a>' if next_ else
                f'<a class="nx" href="{b["base"]}"><small>Kitabın sonu</small>Kitabın sayfasına dön</a>') + "</nav>")
    body = f"""<div class="progress" aria-hidden="true"><span></span></div>
<nav class="r-band" aria-label="Kitap"><a href="{b['base']}"><img src="{b['cover']}" alt="" width="40" height="62">{E(b['title'])}</a><span>Bölüm {i + 1} / {len(ch)}</span></nav>
<article class="reader">
  <header class="r-head">
    <p class="r-num" aria-hidden="true">{i + 1:02d}</p>{part}
    <h1>{E(title)}</h1>{lead}
    <div class="r-tools" role="group" aria-label="Okuma ayarları"><span>{minutes(c['words'])} dakikalık okuma</span>
      <button type="button" data-size="-1" aria-label="Yazıyı küçült">A−</button><button type="button" data-size="1" aria-label="Yazıyı büyüt">A+</button>
      <a href="{b['base']}#icindekiler">İçindekiler</a></div>
  </header>
  {video}
  <div class="r-text">
{render_blocks(c["blocks"], b["slug"])}
  </div>
  {extra}
  {pager}
</article>"""
    return layout(chapter_url(b, i), f"{title} · {b['title']}", body, desc=f"{b['title']} — {title}", cls="page-reader")


def build_all(write_raw, layout):
    def write(path, content):
        write_raw(path, MEDIA_RE.sub(lambda m: MEDIA_BASE + m.group(1), content))
    n = 0
    for b in BOOKS:
        write(b["base"], build_book(b, layout))
        n += 1
        if b.get("soon"):
            continue
        for i in range(len(b["data"]["chapters"])):
            write(chapter_url(b, i), build_chapter(b, i, layout))
            n += 1
    # eski mustafaunal.tr adresleri
    redirects = {"/karanlik-odada-yedi-ay/": "/kitaplar/karanlik-odada-yedi-ay/",
                 "/kitaplar/uslu-dusler/dinle/": "/kitaplar/uslu-dusler/#dinle",
                 "/kitaplar/uslu-dusler/giris/": "/kitaplar/uslu-dusler/bolum/01/"}
    for src, dst in redirects.items():
        write(src, f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={dst}">'
                   f'<link rel="canonical" href="{dst}"><title>Yönlendiriliyor</title><a href="{dst}">Devam etmek için tıklayın</a>')
    return n
