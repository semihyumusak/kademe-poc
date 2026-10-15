# KADEME PoC: Ön Çalışma Tanımı

Amaç: 1002-A başvurusuna "ön çalışma" kanıtı ve THS 3 dayanağı sağlayacak, küçük ama uçtan uca ölçülebilir bir deneysel kanıt (proof-of-concept). Yöntemin tamamını değil, iki kritik iddiayı gösterir: (1) mevzuatın hiyerarşi ve sürüm yapısı deterministik olarak grafa çıkarılabilir, (2) graf temelli genişletme ve sürüm filtresi, düz RAG'e göre atıf ve yürürlük doğruluğunu artırır.

Önerilen depo adı: `kademe-poc`. Lisans: Apache-2.0 (kod), CC BY 4.0 (veri). README'de açıkça "ön çalışma, araştırma prototipi" ibaresi.

## 1. Kapsam (bilinçli olarak dar)

Külliyat, dört katmanı temsil edecek en küçük küme:

- Katman 1: 2547 sayılı Yükseköğretim Kanunu (mevzuat.gov.tr, değişiklik notlarıyla).
- Katman 2: YÖK yönetmeliklerinden dört tanesi: Lisansüstü Eğitim ve Öğretim Yönetmeliği; Önlisans ve Lisans Düzeyindeki Programlar Arasında Geçiş, Çift Anadal, Yan Dal ile Kurumlar Arası Kredi Transferi Yapılması Esaslarına İlişkin Yönetmelik; Yükseköğretim Kurumları Öğrenci Disiplin Yönetmeliği; Öğretim Üyeliğine Yükseltilme ve Atanma Yönetmeliği.
- Katman 3: TOBB ETÜ Lisans Eğitim-Öğretim ve Sınav Yönetmeliği ile Lisansüstü Eğitim-Öğretim ve Sınav Yönetmeliği (Resmi Gazete).
- Katman 4: TOBB ETÜ'nün bu yönetmeliklere dayanan üç ila beş senato yönergesi (ör. çift anadal yönergesi, staj/ortak eğitim yönergesi, lisansüstü tez yazım esasları).

Hedef büyüklük: 1.000 ila 2.000 madde-sürüm düğümü. Daha fazlası PoC için gereksiz.

Kapsam dışı: cevap üretimi kalitesi, arayüz, hukuki yorum, çoklu üniversite, akademik personel alt alanı (bir iki soru dışında).

## 2. Veri modeli (Akoma Ntoso / ELI ile hizalı, sade)

Düğümler:
- `Norm` (id, tür: kanun | yönetmelik | yönerge | usul_esas, katman: 1-4, çıkaran kurum, resmi gazete tarih/sayı, uygulanabilirlik: devlet | vakıf | hepsi)
- `Birim` (madde, fıkra, bent; norm_id, numara, başlık)
- `Sürüm` (birim_id, metin, yürürlük_baslangic, yürürlük_bitis veya null, kaynak değişiklik notu)
- `DegisiklikOlayi` (tür: ekleme | değiştirme | mülga, kaynak norm ve madde, tarih)
- `UygulanabilirlikKurali` (geçici madde/intibak: hangi giriş dönemine hangi sürüm; sadece bulunanlar)

Kenarlar:
- `DAYANAK` (alt norm -> üst normun maddesi; yönetmeliklerin "Dayanak" maddesinden deterministik çıkarılır)
- `ATIF` (birim -> birim; "… Kanununun 44 üncü maddesi", "bu Yönetmeliğin 12 nci maddesi" kalıplarından regex ile)
- `DEGISTIRIR` (DegisiklikOlayi -> Sürüm)
- `UYGULANIR` (UygulanabilirlikKurali -> Sürüm, giriş dönemi koşuluyla)

Depolama: tek bir SQLite + JSON (graf için NetworkX yeterli). Neo4j PoC'de gereksiz. Dışa aktarım: RDF/Turtle (ELI ve Akoma Ntoso sınıf adlarıyla eşleştirilmiş küçük bir ontoloji dosyası `ontology/kademe.ttl`).

## 3. Boru hattı (modüller, her biri ayrı çalıştırılabilir)

1. `fetch/`: mevzuat.gov.tr ve Resmi Gazete'den HTML/PDF indirme; hız sınırı (1 istek/sn), ham dosyalar `data/raw/` altında ve `.gitignore`'da (yeniden dağıtılmaz; sadece türetilmiş yapısal veri depoda).
2. `parse/`: madde-fıkra-bent ayrıştırma; değişiklik notlarından ("Değişik: 2/12/2016-6764/…", "Mülga: …", "Ek: …") sürüm zinciri çıkarma; dayanak ve atıf kalıpları. Çıktı: `data/graph/*.jsonl`.
3. `graph/`: JSONL'den NetworkX grafı; `point_in_time(date)` ve `applicable(date, cohort)` fonksiyonları; dayanak zinciri yukarı/aşağı yürüme.
4. `retrieve/`: iki yapılandırma. (A) düz RAG: madde-sürüm metinleri üzerinde BM25 + yoğun gömme (bge-m3) hibrit, yürürlük filtresi yok. (B) KADEME-lite: aynı hibrit erişim + yürürlük tarihi filtresi + DAYANAK/ATIF üzerinden 1 atlama graf genişletmesi + katman önceliğiyle yeniden sıralama (çapraz kodlayıcı isteğe bağlı).
5. `verify/`: cevap üretimi yok ya da çok küçük (yerel bir 7B-8B model, isteğe bağlı). PoC'de ölçülen şey geri getirim ve atıf doğruluğu; cevap üretimi varsa her atıfın grafta var mı ve yürürlükte mi kontrolü (`cite_check`).
6. `eval/`: mini değerlendirme seti üzerinde ölçüm ve tablo üretimi.

Teknoloji: Python 3.11, uv veya pip, NetworkX, rank-bm25, sentence-transformers (bge-m3), isteğe bağlı Qdrant yerine düz numpy. GPU gerekmez. Ücretli API gerekmez.

## 4. Mini değerlendirme seti: `eval/yoksc_mini.jsonl` (30-40 soru)

Her kayıt: `soru`, `itibariyle_tarih`, `giris_donemi` (varsa), `altin_birimler` (madde-sürüm id listesi), `katman`, `tür`, `kaynak_notu`.

Dağılım:
- 10 tek madde (düz erişim de bulmalı; taban)
- 8 zamansal sürüm çifti (aynı madde, iki farklı tarih, farklı doğru sürüm)
- 8 hiyerarşi (yönerge ile yönetmelik ya da yönetmelik ile YÖK çerçevesi birlikte gerekir; altın küme iki katmandan madde içerir)
- 4 intibak/geçici madde (varsa)
- 4 cevaplanamaz (mevzuatta karşılığı yok; doğru davranış boş küme)

Türetme: graftan şablonla (değişiklik notu olan maddeler, dayanak zincirinde çift katmanlı konular), sonra elle doğal dile yazım. Etiketleri yürütücü ve bir öğrenci bağımsız doğrular; anlaşma oranı README'de.

## 5. Ölçütler ve rapor

- Atıf kesinliği / duyarlılığı @5 (madde-sürüm düzeyinde)
- Yürürlük doğruluğu: getirilen maddelerin sorgu tarihinde yürürlükte olma oranı
- Hiyerarşi kapsaması: hiyerarşi sorularında her iki katmandan da madde getirilme oranı
- Reddetme: cevaplanamaz sorularda boş/eşik altı sonuç oranı

Çıktı: README'de A ve B yapılandırmalarını karşılaştıran tek tablo ve `eval/results.json`. Beklenti: tek madde sorularında fark küçük; zamansal ve hiyerarşi sorularında B belirgin üstün. Fark çıkmazsa da raporlanır; PoC'nin amacı ölçebilmektir.

## 6. Depo yapısı

```
kademe-poc/
  README.md            # amaç, kapsam, sonuç tablosu, nasıl çalıştırılır
  SPEC.md              # bu dosya
  LICENSE
  pyproject.toml
  ontology/kademe.ttl
  src/kademe/{fetch,parse,graph,retrieve,verify,eval}/
  data/raw/            # .gitignore
  data/graph/          # türetilmiş JSONL, depoda
  eval/yoksc_mini.jsonl
  eval/results.json
  scripts/run_all.sh   # fetch -> parse -> graph -> eval
  tests/               # ayrıştırıcı için 10-15 birim testi (sürüm zinciri, dayanak, atıf)
```

## 7. Tamamlanma ölçütü (THS 3 sorularıyla hizalı)

- `run_all.sh` temiz bir makinede baştan sona çalışır ve tabloyu üretir (temsili işlemcide fiziki gösterim).
- Ayrıştırıcı testleri geçer; 50 rastgele madde-sürümün elle kontrolü README'de raporlanır (algoritmaların temsili veri setiyle gerçeklenmesi).
- `SPEC.md` ve kısa bir `docs/algoritma.md` algoritmaların ana hatlarını belgeler.
- Sonuç tablosu ve graf istatistikleri (düğüm/kenar sayıları, sürüm zinciri uzunluk dağılımı) README'de.

## 8. Zaman ve iş bölümü

Yaklaşık 3 hafta. Hafta 1: fetch ve parse (en riskli kısım, değişiklik notu kalıpları). Hafta 2: graf, erişim, mini set türetme. Hafta 3: etiket doğrulama, ölçüm, README. Yürütücü: veri modeli, politika kuralları, etiket doğrulama, README. Öğrenci: ayrıştırıcı, erişim kodu, testler.

## 9. Riskler

- mevzuat.gov.tr HTML yapısı değişken: ayrıştırıcıyı iki üç belgeyle başlatıp genişletin; takılan belge varsa kapsam dışı bırakıp raporlayın.
- Senato yönergeleri PDF: yalnızca metin katmanı olan PDF'ler alınır, OCR yok.
- Değişiklik notu formatı kanunda zengin, yönetmeliklerde seyrek: sürüm çifti soruları ağırlıklı olarak 2547 ve YÖK yönetmeliklerinden gelir.
