# Mustafa Ünal — yeni tasarım (test sürümü)

mustafaunal.tr içeriğiyle sıfırdan tasarlanmış kişisel site. Test adresi:
**https://mustafaunal.gunerunal.com.tr**

- `data/site.json`: mustafaunal.tr'den çıkarılan içerik (Mazi, fotoğraflar, çalışmalar, GAMEKS tarihçesi…)
- `static/`: görseller ve kitap kapakları
- `assets/`: tasarım (`site.css`) ve etkileşim (`site.js`)
- `build.py`: siteyi `docs/` klasörüne üretir (`python3 build.py`, ek paket gerekmez)
- `tools/extract.py`: içeriği mustafaunal.tr'nin yerel kopyasından yeniden çıkarır

Kitaplar acipayam.gunerunal.com.tr'deki okuyucuda okunur; burada kapakları ve tanıtımları yer alır.
`main` dalına her gönderimde GitHub Actions siteyi üretip GitHub Pages'e yayınlar.
Test sürümü arama motorlarına kapalıdır.
