# KADEME PoC: Algoritmaların ana hatları

Bu belge, `SPEC.md`'de tanımlanan boru hattının her adımında kullanılan
algoritmaları özetler. Kod referansları `src/kademe/` altındadır.

## 1. Edinim (`fetch/`)

- **Güncel metin.** mevzuat.gov.tr'deki iç çerçeve sayfası
  (`/anasayfa/MevzuatFihristDetayIframe?MevzuatTur=..&MevzuatNo=..&MevzuatTertip=5`)
  konsolide metni paragraf (`<p>`) düzeyinde verir. TOBB ETÜ yönergeleri
  üniversitenin sitesinden PDF/DOCX olarak alınır.
- **Tarihsel gözlemler.** mevzuat.gov.tr eski konsolide metinleri sunmaz. Bu
  nedenle Internet Archive CDX API'si ile sitenin PDF ve eski HTML kopyalarının
  arşiv anlık görüntüleri listelenir; aynı içerik özetine (digest) sahip
  kopyalar tekilleştirilir, en fazla 40 tanesi zamana yayılarak seçilir ve özgün
  baytlar (`.../web/<zaman>id_/<url>`) indirilir. Her anlık görüntü, arşivlendiği
  tarih itibarıyla konsolide metnin bir **gözlemidir**.
- Bütün istekler 1 istek/sn ile sınırlıdır; indirilen her dosya
  `data/raw/manifest.jsonl`'e URL, SHA-256 ve zaman damgasıyla yazılır. Ham
  dosyalar depoya alınmaz.

## 2. Ayrıştırma (`parse/`)

### 2.1 Metin çıkarma (`text.py`)
HTML'de yaprak blok öğeleri (p, td, li), PDF'de `pdftotext` çıktısı, DOCX'te
paragraflar ve tablo hücreleri kullanılır. PDF'de satırlar paragraflara
birleştirilir (madde/fıkra/bent başlangıcı ya da noktalama + büyük harf yeni
paragraf sayılır); sayfa üst/alt bilgileri tekrar sıklığından, sayfa dipnotları
ayırıcı çizgiden sonra gelen satırlar olarak ayıklanır.

### 2.2 Yapı (`structure.py`)
- Madde başlığı: `(Geçici|Ek)? Madde N(/Harf)? –`. Anahtarlar `m44`, `m53A`,
  `em18` (ek madde), `gm1` (geçici madde); kanun sonundaki "ana kanuna
  işlenemeyen hükümler" bloğundaki maddeler `ih<kanun no>-gm1` biçimindedir.
- Madde başlığı (ör. "Amaç", "Dayanak") madde satırından önceki kısa satırdır.
- Fıkra: yönetmelik ve yönergelerde `(1)`, `(2)`; kanunda numarasız paragraf.
  Bent `a)`/`a.`, alt bent `1)` ya da (kanunda bent içinde) `(1)`. Yalnızca
  not içeren paragraflar sonraki paragrafa eklenir.
- Kuyruk: kanun sonundaki yürürlük tabloları, dipnotlar (`[n] ...`),
  yönetmelik sonundaki "Yönetmeliğin Yayımlandığı Resmî Gazete" tablosu ve
  "(n) Bu değişiklik ... yürürlüğe girer" notları madde gövdesine katılmaz.
- Madde içermeyen belgeler (ör. Yatay Geçiş Esasları) için numaralı bölüm
  başlıkları ("6. YURT İÇİNDEN ...") madde yerine kullanılır.

### 2.3 Değişiklik notları (`notes.py`, `yururluk.py`, `akademik.py`)
- Not kalıbı: `(Değişik|Ek|Mülga|İptal|Yeniden düzenlenen <kapsam>: <gövde>)`.
  Gövdeden tarih, değiştiren kanun/KHK numarası ve maddesi (`6764/27`),
  Resmî Gazete sayısı (`RG-30091`), AYM esas/karar numaraları ve "Aynen kabul"
  bilgisi çıkarılır.
- Notlardaki tarih değiştiren kanunun **kabul** tarihidir. Kanun metninin
  sonundaki "... YÜRÜRLÜĞE GİRİŞ TARİHİNİ GÖSTERİR LİSTE" tablosu
  (kanun no, etkilenen maddeler) → yürürlük tarihi eşlemesine çevrilir ve
  varsa yürürlük tarihi olarak bu kullanılır.
- Yönetmelik/yönergelerde notu izleyen `(n)` işareti, sondaki
  "(n) Bu değişiklik 2019-2020 eğitim-öğretim yılı bahar döneminden itibaren
  yürürlüğe girer" notuna bağlanır; akademik ifade tarihe çevrilir (güz/yıl
  başı 1 Eylül, bahar 1 Şubat, yaz 15 Haziran). İşaretin değişiklikten önceki
  bir tarihe çözülmesi reddedilir.
- Kanun dipnotlarındaki ibare değişiklikleri ("... maddesiyle ... ibaresi ...
  şeklinde değiştirilmiştir") ayrı olay adaylarıdır.

### 2.4 Sürüm zinciri (`versions.py`)
Her madde için gözlemler (güncel metin + arşiv anlık görüntüleri) tarih
sırasına dizilir:

1. **Gruplama.** Biçimden bağımsız parmak izleri (küçük harf, yalnızca harf ve
   rakam; dipnot işaretleri ve PDF gürültüsü atılmış) benzerliği ≥ 0,985 ise ya
   da değişiklik notu kümeleri aynı ve rakamlar atıldığında benzerlik ≥ 0,95 ise
   ardışık gözlemler aynı sürümdür. Daha eski bir gruba geri dönen tutarsız
   arşiv gözlemi yok sayılır.
2. **Başlangıç.** Bir sürümün başlangıcı, metnindeki notların (önceki sürümün
   başlangıcından sonraki) en geç yürürlük tarihidir. Not yoksa ilk sürüm için
   maddenin doğumu (normun yürürlüğü ya da madde düzeyinde "Ek" notu), sonraki
   sürümler için önce gözlem aralığına düşen dipnot olayı, o da yoksa ilk
   gözlem tarihi (yaklaşık; `baslangic_kaynagi = gozlem`,
   `baslangic_belirsizlik` aralığıyla) kullanılır.
3. **Yer tutucular.** Notlarda geçen ama metni hiçbir gözlemde bulunmayan ara
   tarihler için metni bilinmeyen (`metin_mevcut = false`) sürümler eklenir;
   böylece yürürlük aralıkları kesintisizdir ve `point_in_time` metni
   bilinmeyen bir dönemde bile hangi sürümün yürürlükte olduğunu söyler.
4. **Mülga.** Madde başlık satırında Mülga/İptal notu bulunan ve gövdesi boş
   sürüm `durum = mulga` olur; o tarihten sonra madde yürürlükte sayılmaz.
5. Her sürümün bitişi bir sonrakinin başlangıcıdır. Sürümü başlatan her not
   bir `DegisiklikOlayi` düğümü ve `DEGISTIRIR` kenarı üretir.

### 2.5 Dayanak ve atıf (`refs.py`)
- Atıf kalıbı: isteğe bağlı niteleyici (`bu Kanunun`, `2547 sayılı ...
  Kanununun`, `Kanunu'nun`, bir yönetmeliğin adı) + madde listesi
  (`7 nci, 14 üncü ve 44 üncü`, `ek 18 inci`, `geçici 2 nci`) + `madde*`
  sözcüğü + isteğe bağlı fıkra/bent.
- Çözümleme: `bu/işbu` ve niteleyicisiz atıflar aynı norma; `NNNN sayılı`
  numarayla; yönetmelik adları ayırt edici ad parçalarıyla; yönetmelik ve
  yönergelerde niteleyicisiz "Kanunun" dayanak zincirindeki kanuna bağlanır.
  "... 7 nci maddesinin (e) bendine ve 44 üncü maddesinin ..." gibi
  zincirlerde niteleyici sonraki öğelere devredilir. Korpus dışı kanunlar
  (657, 2914 ...) sayılır ama kenar üretmez.
- `DAYANAK`: başlığı "Dayanak" olan ya da "dayanılarak hazırlanmıştır"
  içeren maddedeki üst norm atıfları alt normdan üst normun **maddesine**
  kenar olur; madde numarası verilmeden yalnızca adıyla anılan üst norm için
  norm düzeyinde kenar eklenir.
- `ATIF`: her metinli sürümdeki atıflar madde (ya da fıkra) birimleri arasında
  kenar olur; kenar, atfın geçtiği sürüm kimliklerini taşır.

### 2.6 Uygulanabilirlik kuralları
Geçici maddeler ve "intibak/geçiş" başlıklı maddelerde şu kalıplar aranır:
"YYYY-YYYY eğitim-öğretim yılı öncesinde kayıt yaptıran", "... itibaren kayıt
olan", "yürürlüğe girdiği/yayımı tarihinden önce ... kayıt yaptıran". Hedef
maddeler aynı normdaki atıflardan (yoksa normun tamamı), etki "uygulanmaz /
önceki hükümler" → `onceki_surum`, "... uygulanmaya başlanır" →
`baslangic_ertele` olarak çıkarılır. Yalnızca bulunan kurallar modellenir.

## 3. Graf (`graph/`)

JSONL dosyaları NetworkX `MultiDiGraph`'a yüklenir.

- `point_in_time(birim, t)`: normun t'de yürürlükte olduğu ve
  `başlangıç ≤ t < bitiş`, `durum = yururlukte` koşulunu sağlayan sürüm
  (ikili arama).
- `applicable(birim, t, giris)`: önce `point_in_time`; sonra birime hedeflenen
  kurallar içinde kohortu uyanlar için `onceki_surum` (eşik öncesi sürüm) ya da
  `baslangic_ertele` (erteleme tarihine kadar önceki sürüm) uygulanır.
- `dayanak_zinciri_yukari/asagi`: DAYANAK kenarları üzerinde özyinelemeli yürüme.
- Dışa aktarım: tek dosya SQLite (`data/graph/kademe.sqlite`) ve
  `ontology/kademe.ttl` sınıflarıyla RDF/Turtle (`data/graph/kademe.ttl`).

## 4. Erişim (`retrieve/`)

Dizin birimi metni olan madde-sürümdür; doküman metni = norm adı + madde
numarası + başlık + notlardan arındırılmış metin.

- **BM25**: Türkçe küçük harf (İ/ı kuralları), durak sözcükler, ilk 5 karakter
  kök kısaltması (F5).
- **Yoğun**: `BAAI/bge-m3`, normalize gömmeler, kosinüs benzerliği.
- **Hibrit**: karşılıklı sıra füzyonu (RRF, k = 60).
- **A (düz RAG)**: hibrit ilk-5; yürürlük filtresi yok.
- **B (KADEME-lite)**:
  1. sorgu tarihi ve (varsa) giriş dönemiyle `applicable` sürüm kümesi dışındaki
     dokümanlar elenir;
  2. kalan ilk 8 doküman tohum olur;
  3. ilk 3 tohumdan ATIF (iki yönde) ve DAYANAK (yukarı: üst madde/normun en
     ilgili 2 maddesi; aşağı: bu maddeye/norma dayanan alt normların en ilgili 2
     maddesi) üzerinden 1 atlamalı genişletme yapılır; komşunun yürürlükteki
     sürümü kendi hibrit skoru × 1,25 ile aday olur;
  4. katman önceliği: en iyi skorun yarısından yüksek adaylar arasında her
     katmanın en iyisi önce seçilir, kalan yerler skora göre doldurulur, sonuç
     üst katmandan alta sıralanır.
- **Reddetme** (her iki yapılandırmada aynı): ilk-5'teki en yüksek kosinüs
  0,50'nin altındaysa sonuç boştur. Eşik önceden seçilmiştir; eşik taraması
  `eval/results.json`'da ayrıca raporlanır.

## 5. Doğrulama (`verify/cite_check.py`)

Cevap üretimi yoktur. `check_ids` erişilen sürüm kimliklerinin grafta olup
olmadığını ve sorgu tarihinde uygulanan sürüm olup olmadığını; `check_text`
serbest metindeki atıfları aynı regex ile çözüp yürürlükte olup olmadığını
denetler (`python -m kademe.verify 2015-01-01 "2547 sayılı Yükseköğretim
Kanununun 44 üncü maddesi"`).

## 6. Değerlendirme (`eval/`)

- `adaylar.py`: graftan şablon adayları (zamansal çiftler: güvenilir
  başlangıçlı ardışık metinli sürümler; hiyerarşi: DAYANAK kenarları;
  intibak: kurallar).
- `soru_seti.py`: elle yazılmış sorular; altın maddeler ve tarih elle, altın
  sürüm kimlikleri `applicable` ile çözülüp `yoksc_mini.jsonl`'e sabitlenir.
- `run.py`: ölçütler @5; kesinlik getirilen 5 öğe üzerinden hesaplandığından
  tek altın öğeli soruda üst sınır 0,20'dir.
