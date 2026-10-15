# KADEME PoC

**Ön çalışma, araştırma prototipi.** Bu depo, yükseköğretim mevzuatı için
hiyerarşi ve sürüm farkında, graf temelli erişim yaklaşımının (KADEME) küçük
ama uçtan uca ölçülebilir bir kavram kanıtıdır. Hukuki görüş ya da danışmanlık
niteliği taşımaz; metinler resmî kaynakların yerine geçmez.

Tanım belgesi: [SPEC.md](SPEC.md) · Algoritmalar: [docs/algoritma.md](docs/algoritma.md)

## Amaç

Yöntemin tamamını değil, iki kritik iddiayı göstermek:

1. Mevzuatın **hiyerarşi ve sürüm yapısı deterministik olarak grafa
   çıkarılabilir**: kanun → YÖK yönetmeliği → üniversite yönetmeliği → senato
   yönergesi dayanak zinciri; madde düzeyinde yürürlük aralıklı sürüm zinciri;
   değişiklik olayları; geçici/intibak maddelerinden giriş dönemine bağlı
   uygulama kuralları.
2. **Graf temelli genişletme ve sürüm filtresi**, düz RAG'e göre atıf ve
   yürürlük doğruluğunu artırır.

## Kapsam

| Katman | Norm | Kaynak |
|---:|---|---|
| 1 | 2547 sayılı Yükseköğretim Kanunu | mevzuat.gov.tr + 40 Wayback anlık görüntüsü (2012–2025) |
| 2 | Lisansüstü Eğitim ve Öğretim Yönetmeliği (RG 20/4/2016-29690) | mevzuat.gov.tr + arşiv |
| 2 | Önlisans ve Lisans Düzeyindeki Programlar Arasında Geçiş, Çift Anadal, Yan Dal ile Kurumlar Arası Kredi Transferi Yapılması Esaslarına İlişkin Yönetmelik (RG 24/4/2010-27561) | mevzuat.gov.tr + arşiv |
| 2 | Öğretim Üyeliğine Yükseltilme ve Atanma Yönetmeliği (RG 12/6/2018-30449) | mevzuat.gov.tr |
| 2 | Yükseköğretim Kurumlarında Yabancı Dil Öğretimi ve Yabancı Dille Öğretim Yapılmasında Uyulacak Esaslara İlişkin Yönetmelik (RG 23/3/2016-29662) | mevzuat.gov.tr + arşiv |
| 3 | TOBB ETÜ Lisans Eğitim-Öğretim ve Sınav Yönetmeliği (RG 12/9/2011-28052) | mevzuat.gov.tr |
| 3 | TOBB ETÜ Lisansüstü Eğitim-Öğretim Yönetmeliği (RG 21/12/2025-33114) | mevzuat.gov.tr |
| 4 | TOBB ETÜ Çift Anadal Programı Yönergesi | etu.edu.tr (PDF) |
| 4 | TOBB ETÜ Yandal Programı Yönergesi | etu.edu.tr (PDF) |
| 4 | TOBB ETÜ Yatay Geçiş Esasları | etu.edu.tr (PDF) |
| 4 | TOBB ETÜ Ortak Eğitim Yönergesi | etu.edu.tr (DOCX) |
| 4 | TOBB ETÜ İngilizce Hazırlık Programı Eğitim-Öğretim Esaslarına İlişkin Yönerge | etu.edu.tr (DOCX) |

**SPEC'ten sapma.** SPEC'te katman 2 için öngörülen *Yükseköğretim Kurumları
Öğrenci Disiplin Yönetmeliği*, mevzuat.gov.tr'nin yürürlükteki mevzuat
aramasında bulunamadı (öğrenci disiplin hükümleri 7437 sayılı Kanunla 2547
m.54'e alınmıştır). Yerine, katman 4'teki hazırlık yönergesinin dayanağı olan
yabancı dil yönetmeliği alındı. Disiplin konusu 2547 m.53–54 üzerinden
kapsamdadır.

**Tarihsel metinler.** mevzuat.gov.tr yalnızca güncel konsolide metni sunar.
Eski sürüm metinleri, sitenin Internet Archive'daki PDF/HTML kopyalarından
elde edildi; değişiklik notları, kanunun yürürlük tablosu ve dipnotlar
sürümlerin yürürlük tarihlerini belirlemekte kullanıldı (ayrıntı:
[docs/algoritma.md](docs/algoritma.md) §2.4). Arşiv kopyası bulunmayan
dönemler için sürüm düğümü vardır ama metni yoktur (`metin_mevcut: false`).

Kapsam dışı: cevap üretimi kalitesi, arayüz, hukuki yorum, çoklu üniversite.

## Sonuçlar

<!-- RAPOR:sonuc -->
| Soru türü (n) | Ölçüt | A: düz RAG | B: KADEME-lite |
|---|---|---:|---:|
| Tek madde (10) | Kesinlik@5 / Duyarlılık@5 | 0.18 / 0.90 | 0.20 / 1.00 |
| | Yürürlük doğruluğu | 0.78 | 1.00 |
| Zamansal sürüm (16) | Kesinlik@5 / Duyarlılık@5 | 0.14 / 0.69 | 0.20 / 1.00 |
| | Yürürlük doğruluğu | 0.47 | 1.00 |
| Hiyerarşi (8) | Kesinlik@5 / Duyarlılık@5 | 0.33 / 0.81 | 0.35 / 0.88 |
| | Yürürlük doğruluğu | 0.97 | 1.00 |
| İntibak/geçici madde (4) | Kesinlik@5 / Duyarlılık@5 | 0.25 / 0.88 | 0.25 / 0.88 |
| | Yürürlük doğruluğu | 0.60 | 1.00 |
| Tüm cevaplanabilir (38) | Kesinlik@5 / Duyarlılık@5 | 0.20 / 0.79 | 0.24 / 0.96 |
| | Yürürlük doğruluğu | 0.67 | 1.00 |
| Hiyerarşi (8) | Hiyerarşi kapsaması | 0.62 | 0.75 |
| Cevaplanamaz (4) | Reddetme | 0.25 | 0.25 |

_Ayarlar: k=5, yoğun model: `BAAI/bge-m3`, reddetme eşiği (kosinüs): 0.5, rank_bm25.BM25Okapi, Türkçe küçük harf + F5 kök, füzyon: RRF k=60, dizindeki madde-sürüm: 709. Üretim: 2026-10-15T13:55:12+00:00, macOS-26.5.2-arm64-arm-64bit._

Bileşen ayrıştırması (tüm cevaplanabilir sorular; hiyerarşi kapsaması yalnız hiyerarşi soruları):

| Yapılandırma | Kesinlik@5 | Duyarlılık@5 | Yürürlük doğruluğu | Hiyerarşi kapsaması | Reddetme |
|---|---:|---:|---:|---:|---:|
| A_duz_rag | 0.20 | 0.79 | 0.67 | 0.62 | 0.25 |
| B_kademe_lite | 0.24 | 0.96 | 1.00 | 0.75 | 0.25 |
| B-yalniz_tarih_filtresi | 0.22 | 0.90 | 1.00 | 0.62 | 0.25 |
| B-genisletme_yok | 0.22 | 0.90 | 1.00 | 0.62 | 0.25 |
| B-katman_onceligi_yok | 0.24 | 0.96 | 1.00 | 0.75 | 0.25 |

Reddetme eşiği taraması (aday listesindeki en yüksek kosinüse göre; `yanlış red` = cevaplanabilir sorunun boş dönme oranı):

| Eşik | A reddetme | A yanlış red | B reddetme | B yanlış red |
|---:|---:|---:|---:|---:|
| 0.400 | 0.00 | 0.00 | 0.00 | 0.00 |
| 0.425 | 0.00 | 0.00 | 0.00 | 0.00 |
| 0.450 | 0.00 | 0.00 | 0.00 | 0.00 |
| 0.475 | 0.00 | 0.00 | 0.00 | 0.00 |
| 0.500 | 0.25 | 0.00 | 0.25 | 0.00 |
| 0.525 | 0.25 | 0.00 | 0.25 | 0.00 |
| 0.550 | 0.25 | 0.00 | 0.25 | 0.00 |
| 0.575 | 0.75 | 0.00 | 0.75 | 0.00 |
| 0.600 | 1.00 | 0.00 | 1.00 | 0.00 |
| 0.625 | 1.00 | 0.00 | 1.00 | 0.00 |
| 0.650 | 1.00 | 0.05 | 1.00 | 0.05 |
<!-- /RAPOR:sonuc -->

**Bulgular (2026-10-15 çalıştırması).**
- *Tek madde*: fark küçük (duyarlılık@5 0,90 → 1,00), SPEC'teki beklentiyle uyumlu.
- *Zamansal*: B'nin duyarlılığı 0,69 → 1,00. A'nın bu sorularda getirdiği
  sürümlerin yalnızca %47'si sorgu tarihinde yürürlükteydi; A, aynı maddenin
  yanlış sürümünü getiriyor ya da birkaç sürümüyle ilk-5'i dolduruyor (ör.
  T07'de 2547 m.6'nın dört sürümü doğru maddeyi, m.7'yi dışarıda bırakıyor).
- *Hiyerarşi*: kapsama 0,62 → 0,75. Bileşen ayrıştırmasına göre kazanç graf
  genişletmesinden geliyor (genişletmesiz B 0,62); katman önceliği bu sette
  ek katkı sağlamadı. H08'de (ETÜ lisansüstü yönetmeliği ↔ YÖK lisansüstü
  yönetmeliği) iki norm arasında DAYANAK kenarı olmadığı için genişletme işe
  yaramıyor.
- *İntibak*: fark yok (0,88). I02'de iki yapılandırma da geçici maddeyi
  (13948 geçici m.2) kaçırıyor; A hedef maddenin (m.14) üç sürümünü birlikte
  getirirken B yalnızca kohorta uygulanan değişiklik öncesi sürümü getiriyor.
- *Reddetme*: önceden seçilen 0,50 eşiğiyle her iki yapılandırma da 4
  cevaplanamaz sorudan yalnızca 1'ini reddediyor. Taramada 0,60 eşiği bu sette
  hiçbir cevaplanabilir soruyu boşaltmadan tümünü reddediyor; ancak eşiği aynı
  küçük sette seçmek aşırı uyum olacağından tablo 0,50 ile raporlandı.

**Okuma notları.**
- Kesinlik@5, getirilen beş öğe üzerinden hesaplanır; tek altın öğeli bir
  soruda üst sınırı 0,20, iki öğelide 0,40'tır.
- B'nin yürürlük doğruluğu tasarım gereği 1'e yakındır: B yalnızca sorgu
  tarihinde (ve giriş dönemine göre) uygulanan sürümleri aday yapar. Asıl
  bulgu, A'nın aynı sorularda ne oranda yürürlükte olmayan sürüm getirdiğidir.
- Zamansal soruların altın sürüm kimlikleri, B'nin de kullandığı sürüm
  zincirinden çözülür (`src/kademe/eval/soru_seti.py`). Dolayısıyla bu ölçüm
  "zincir doğruysa erişim onu kullanabiliyor mu?" sorusunu yanıtlar; zincirin
  kendi doğruluğu aşağıdaki elle kontrolle ayrıca ölçülmelidir.
- Set küçüktür (34 tekil soru, 42 kayıt); farklar yön gösterir, istatistiksel
  anlamlılık iddia edilmez.
- Ayrı bir geliştirme seti yoktur. B'nin parametreleri (tohum 8, genişletme
  3, DAYANAK önceliği ×1,25, korunan doğrudan isabet 2, katman oranı 0,5)
  geliştirme sırasında yalnızca BM25 ile bu set üzerinde bir kez gözden
  geçirildi (ilk sürümde ATIF komşuları da öncelik alıyor ve doğrudan
  isabetleri dışarı itiyordu); bge-m3 ile ölçümden önce donduruldu.
  Reddetme eşiği (0,50) önceden seçildi; etkisi eşik taramasında gösterilir.

## Graf istatistikleri

<!-- RAPOR:graf -->
| Düğüm | Sayı | | Kenar | Sayı |
|---|---:|---|---|---:|
| Norm | 12 | | DAYANAK | 17 |
| Birim (madde/fıkra/bent/alt bent) | 3215 | | ATIF | 180 |
| Sürüm (madde düzeyi) | 969 | | DEGISTIRIR | 684 |
|   └ metni olan | 709 | | UYGULANIR | 2 |
| DegisiklikOlayi | 684 | | PARCASI | 3215 |
| UygulanabilirlikKurali | 4 | | SURUMU | 969 |

Birim tipleri: madde 572, fıkra 1664, bent 814, alt bent 165.

Sürüm zinciri uzunluk dağılımı (madde başına sürüm sayısı → madde sayısı):

| Uzunluk | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 12 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Madde | 393 | 92 | 37 | 20 | 12 | 6 | 4 | 5 | 1 | 1 | 1 |

Sürüm başlangıç tarihlerinin dayanağı:

- normun ya da ek maddenin yürürlüğü: 445 (%46)
- kanun yürürlük tablosu: 284 (%29)
- değişiklik notu tarihi: 190 (%20)
- yalnızca arşiv gözlemi (yaklaşık): 29 (%3)
- dipnot / akademik takvim notu: 21 (%2)

Norm başına:

| Norm | Katman | Madde | Sürüm | Arşiv gözlemi | Yürürlük |
|---|---:|---:|---:|---:|---|
| Yükseköğretim Kanunu (`kanun:2547`) | 1 | 229 | 482 | 36 | 1981-11-06 (resmi_gazete) |
| Lisansüstü Eğitim ve Öğretim Yönetmeliği (`yonetmelik:21510`) | 2 | 40 | 65 | 1 | 2016-04-20 (resmi_gazete) |
| Yükseköğretim Kurumlarında Önlisans ve Lisans Düzeyindeki Programlar Arasında Geçiş, Çift Anadal, Yan Dal ile Kurumlar Arası Kredi Transferi Yapılması Esaslarına İlişkin Yönetmelik (`yonetmelik:13948`) | 2 | 33 | 87 | 3 | 2010-04-24 (resmi_gazete) |
| Öğretim Üyeliğine Yükseltilme ve Atanma Yönetmeliği (`yonetmelik:24672`) | 2 | 20 | 24 | 0 | 2018-06-12 (resmi_gazete) |
| Yükseköğretim Kurumlarında Yabancı Dil Öğretimi ve Yabancı Dille Öğretim Yapılmasında Uyulacak Esaslara İlişkin Yönetmelik (`yonetmelik:21475`) | 2 | 14 | 17 | 1 | 2016-03-23 (resmi_gazete) |
| TOBB Ekonomi ve Teknoloji Üniversitesi Lisans Eğitim-Öğretim ve Sınav Yönetmeliği (`yonetmelik:15287`) | 3 | 58 | 58 | 0 | 2011-09-01 (yururluk_maddesi_akademik) |
| TOBB Ekonomi ve Teknoloji Üniversitesi Lisansüstü Eğitim-Öğretim Yönetmeliği (`yonetmelik:42791`) | 3 | 45 | 45 | 0 | 2025-12-21 (resmi_gazete) |
| TOBB ETÜ Çift Anadal Programı Yönergesi (`yonerge:etu-cap`) | 4 | 15 | 16 | 0 | 2017-09-01 (yururluk_maddesi_akademik) |
| TOBB ETÜ Yandal Programı Yönergesi (`yonerge:etu-yandal`) | 4 | 11 | 11 | 0 | 2017-09-01 (yururluk_maddesi_akademik) |
| TOBB ETÜ Yatay Geçiş Esasları (`usul_esas:etu-yatay-gecis`) | 4 | 11 | 19 | 0 | 2015-08-07 (senato_karari) |
| TOBB ETÜ Ortak Eğitim Yönergesi (`yonerge:etu-ortak-egitim`) | 4 | 62 | 78 | 0 | 2016-02-11 (senato_karari) |
| TOBB ETÜ İngilizce Hazırlık Programı Eğitim-Öğretim Esaslarına İlişkin Yönerge (`yonerge:etu-hazirlik`) | 4 | 34 | 67 | 0 | 2015-08-07 (senato_karari) |

Ayrıştırma sırasında atlanan/sorunlu kaynaklar:

- kanun:2547: 20130831162609.pdf yetersiz ayrıştırıldı (42 madde); atlandı
- kanun:2547: 20190819022638.html yetersiz ayrıştırıldı (0 madde); atlandı
- kanun:2547: 20230324193006.pdf okunamadı (RuntimeError; bozuk ya da PDF olmayan arşiv kopyası)
- kanun:2547: 20231128163422.pdf okunamadı (RuntimeError; bozuk ya da PDF olmayan arşiv kopyası)
- yonetmelik:21510: 20190917142325.html yetersiz ayrıştırıldı (0 madde); atlandı
<!-- /RAPOR:graf -->

## Elle kontrol (50 rastgele madde-sürüm)

<!-- RAPOR:kontrol -->
**Durum: bekliyor.** `eval/elle_kontrol.jsonl` dosyasında 50 rastgele madde-sürüm (tohum 2026) kontrol için hazır; her satırın `kontrol` alanı yürütücü tarafından doldurulacak. Doldurulduktan sonra `python -m kademe.eval.rapor` bu bölümü oranlarla günceller.
<!-- /RAPOR:kontrol -->

## Etiket doğrulama ve anlaşma

<!-- RAPOR:anlasma -->
**Durum: bekliyor.** 42 kaydın altın etiketleri yürütücü ve bir öğrenci tarafından bağımsız doğrulanacak (`dogrulama.yurutucu`, `dogrulama.ogrenci`: `true`/`false`). Doldurulunca anlaşma oranı ve Cohen kappa burada raporlanır.
<!-- /RAPOR:anlasma -->

## Nasıl çalıştırılır

Gereksinimler: Python 3.11, `pdftotext` (poppler), internet erişimi
(mevzuat.gov.tr, etu.edu.tr, web.archive.org). GPU ve ücretli API gerekmez.

```bash
git clone https://github.com/semihyumusak/kademe-poc.git && cd kademe-poc
scripts/run_all.sh            # fetch -> parse -> graph -> test -> eval (bge-m3 ile)
scripts/run_all.sh --no-dense # yalnızca BM25; model indirmeden hızlı deneme
```

Adımlar ayrı ayrı da çalıştırılabilir:

```bash
python -m kademe.fetch          # data/raw/ (depoya alınmaz)
python -m kademe.parse          # data/graph/*.jsonl
python -m kademe.graph          # istatistik, data/graph/kademe.sqlite, data/graph/kademe.ttl
python -m kademe.eval.soru_seti # eval/yoksc_mini.jsonl
python -m kademe.eval.run --ablation
python -m kademe.eval.rapor     # README'deki tabloları günceller
python -m kademe.verify 2015-01-01 "2547 sayılı Yükseköğretim Kanununun 44 üncü maddesi"
```

Graf Python'dan:

```python
from kademe.graph.model import KademeGraph
kg = KademeGraph.load()
kg.point_in_time("kanun:2547/m3", "2017-03-01")["id"]          # 'kanun:2547/m3@2016-02-26'
kg.applicable("yonetmelik:13948/m14", "2024-03-01", "2022-09-01")["id"]  # geçici m.2: değişiklik öncesi sürüm
kg.dayanak_zinciri_yukari("yonerge:etu-cap")
```

## Veri modeli

Akoma Ntoso / ELI ile hizalı, sade bir model (`ontology/kademe.ttl`).

| Düğüm | Alanlar |
|---|---|
| `Norm` | id, ad, tür (kanun/yönetmelik/yönerge/usul_esas), katman 1–4, kurum, Resmî Gazete tarih/sayı, uygulanabilirlik (devlet/vakıf/hepsi), yürürlük |
| `Birim` | madde, fıkra, bent, alt bent; norm_id, numara, başlık, üst birim |
| `Sürüm` | birim_id (madde), metin, yürürlük başlangıç/bitiş, başlangıç dayanağı, durum, kaynak notu, arşiv gözlemleri |
| `DegisiklikOlayi` | tür (ekleme/değiştirme/mülga/iptal), kapsam, tarih, yürürlük tarihi, kaynak (ör. `6764/27`, `RG-30091`, `AYM E:..`) |
| `UygulanabilirlikKurali` | kaynak geçici madde, hedef maddeler, koşul (giriş dönemi < / ≥ eşik), etki |

Kenarlar: `DAYANAK` (alt norm → üst norm maddesi), `ATIF` (birim → birim),
`DEGISTIRIR` (olay → sürüm), `UYGULANIR` (kural → sürüm), `PARCASI`
(birim → üst birim/norm), `SURUMU` (sürüm → madde).

Kimlikler: `kanun:2547/m44` (madde), `kanun:2547/m44/f1/bc` (fıkra/bent),
`kanun:2547/m44@2014-11-26` (yürürlük başlangıcıyla sürüm).

## Depo yapısı

```
README.md  SPEC.md  LICENSE  pyproject.toml
docs/algoritma.md
ontology/kademe.ttl
src/kademe/{fetch,parse,graph,retrieve,verify,eval}/
data/raw/      # ham indirmeler (.gitignore)
data/graph/    # türetilmiş JSONL ve raporlar (depoda)
eval/yoksc_mini.jsonl  eval/results.json  eval/elle_kontrol.jsonl  eval/adaylar.jsonl
scripts/run_all.sh
tests/         # ayrıştırıcı birim testleri
```

## Bilinen sınırlamalar

- Sürüm zinciri madde düzeyindedir; fıkra/bent birimleri yalnızca güncel
  metinle temsil edilir.
- Değişiklik notu tarihi yürürlük tarihinden farklı olabilir; kanunda yürürlük
  tablosu kullanılır, yönetmeliklerde Resmî Gazete tarihi (ve varsa akademik
  takvim notu) esas alınır. Kısmi yürürlük hükümleri (ör. 2547 m.67'deki
  madde bazlı tarihler) modellenmemiştir.
- PDF arşiv kopyalarının metin katmanı kusurlu olabilir (harf aralıkları,
  satır içine düşmüş dipnotlar); temizleme sezgiseldir. Arşiv gözlemine dayalı
  yaklaşık başlangıçlar `baslangic_kaynagi: gozlem` ile işaretlidir.
- Aynı numaralı ikinci geçici maddeler (`gm30-2`) ve "işlenemeyen hükümler"
  (`ih4702-gm1`) arşiv kopyaları arasında her zaman doğru eşleşmeyebilir.
- Uygulanabilirlik kuralları yalnızca bulunan kalıplardan çıkarılır; kapsam
  bilinçli olarak dardır.
- TOBB ETÜ yönergelerinin geçmiş sürümleri yoktur (yalnızca güncel metin).

## Lisans

- Kod: [Apache-2.0](LICENSE).
- Türetilmiş yapısal veri (`data/graph/`, `eval/`): [CC BY 4.0](data/LICENSE.md).
  Mevzuat metinleri resmî metinlerdir (5846 sayılı FSEK m.31); ham dosyalar
  yeniden dağıtılmaz.

## Atıf

```
Yumuşak, S. (2026). KADEME PoC: Yükseköğretim mevzuatı için hiyerarşi ve sürüm
farkında graf temelli erişim — ön çalışma. https://github.com/semihyumusak/kademe-poc
```
