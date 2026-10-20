# TÜBİTAK 1002-A Hızlı Destek Modülü — Proje Önerisi Taslağı

> **Başvuru notları (metne girmez).**
> - Bu taslak, ARDEB-PBS'deki 1002-A başvuru adımlarına göre bölümlenmiştir
>   (bilgi notu 1002BF-01, Mart 2026 sürümü). Kelime sınırları: Bilimsel
>   Nitelik 1.000–3.500, Amaç ve Hedefler 100–1.000, Yöntem 750–3.000, Çıktı/
>   Etki/Kazanımlar 100–400, Diğer Konular ≤ 250. Her bölümün sonunda taslağın
>   kelime sayısı verilmiştir.
> - Destek üst limiti 1 Şubat 2026'dan itibaren yıllık 150.000 TL (burs dahil);
>   süre en fazla 12 ay. Bütçe (EK-2) buna göre kurgulandı; burs tutarları ve
>   bursiyer nitelikleri başvuru sırasında güncel üst sınırlarla kontrol edilmeli.
> - Bilgi notuna göre proje içeriğinin web sayfası ya da dosya paylaşım
>   bağlantısıyla dışarıda sunulması durumunda öneri değerlendirmeye alınmadan
>   iade ediliyor. Bu nedenle ön çalışma sonuçları metnin içine alındı; depo
>   yalnızca EK-1'de yazılım atfı olarak geçiyor.
> - Sosyal ve Beşeri Bilimler dışındaki önerilerde THS adımı zorunlu; öneri
>   Bilgi ve İletişim Teknolojileri alanından (EEEAG / bilgisayar bilimleri)
>   sunulacağı varsayımıyla THS 3 → 4 olarak yazıldı.
> - `[...]` içindeki alanlar (unvan, bölüm, bursiyer sayısı, hesaplama altyapısı)
>   başvuru sahibince doldurulacak.
> - EK-1'deki künyeler başvurudan önce DOI'leriyle birlikte doğrulanmalı;
>   belirsiz olanlar arXiv numarasıyla verildi.

---

**Proje Başlığı:** KADEME: Yükseköğretim Mevzuatı için Hiyerarşi ve Sürüm Farkında Graf Temelli Erişim ve Doğrulanabilir Soru Yanıtlama

**Proje Yürütücüsü:** [Unvan] Semih Yumuşak, TOBB Ekonomi ve Teknoloji Üniversitesi, [Bölüm]

**Projenin Yürütüleceği Kuruluş:** TOBB Ekonomi ve Teknoloji Üniversitesi

**Önerilen Süre:** 12 ay

**Anahtar Kelimeler:** mevzuat bilgi grafı, zamansal sürümleme, erişim destekli üretim (RAG), hukuki doğal dil işleme, Türkçe, yükseköğretim mevzuatı, Akoma Ntoso, ELI

**Keywords:** legislative knowledge graph, temporal versioning, retrieval-augmented generation, legal NLP, Turkish, higher education legislation, Akoma Ntoso, ELI

---

## Özet

Yükseköğretim mevzuatı dört katmanlı bir hiyerarşi oluşturur: 2547 sayılı Yükseköğretim Kanunu, Yükseköğretim Kurulu yönetmelikleri, üniversite yönetmelikleri ve senato yönergeleri. Her katman bir üst katmana dayanır, maddeler sık sık değişir ve geçici maddeler aynı kuralı öğrencinin giriş dönemine göre farklı uygular. Büyük dil modelleriyle kurulan soru-yanıt sistemleri bu yapıyı görmez: metni düz parçalara bölüp benzerlikle arar, yürürlükten kalkmış bir sürümü yürürlükteki gibi sunar ve yönergeyi, dayandığı yönetmelikten kopuk okur. Hukuk alanında yapılan ölçümler, bu tür sistemlerin yanıtlarında önemli oranda var olmayan ya da yanlış atıf ürettiğini göstermektedir.

Bu proje, mevzuatın hiyerarşi ve sürüm yapısını deterministik olarak bir bilgi grafına çıkaran ve erişimi bu graf üzerinden yürüten KADEME yaklaşımını geliştirmeyi ve ölçmeyi amaçlamaktadır. Yürütücünün tamamladığı kavram kanıtı çalışmasında 12 normdan 3.215 birim ve 969 madde-sürüm içeren bir graf üretilmiş; 42 kayıtlık bir soru seti üzerinde graf temelli erişim, düz erişime göre zamansal sorularda duyarlılık@5'i 0,69'dan 1,00'e, hiyerarşi kapsamasını 0,62'den 0,75'e çıkarmış, düz erişimin zamansal sorularda getirdiği sürümlerin yalnızca %47'sinin sorgu tarihinde yürürlükte olduğu görülmüştür. Proje bu kanıtı dört yönde ileri taşıyacaktır: (1) külliyatın YÖK yönetmeliklerinin tamamına ve üç üniversiteye genişletilmesi ve sürümlemenin fıkra düzeyine indirilmesi; (2) sorudaki tarih ve kohort ifadelerini anlayan, çok atlamalı graf genişletmesi ve öğrenilmiş yeniden sıralama kullanan erişim; (3) her atıfı grafta ve yürürlükte doğrulayan cevap üretimi; (4) çift etiketlenmiş, ayrı geliştirme ve test bölmeleri olan 300 soruluk açık bir değerlendirme seti (YÖKSC) ile istatistiksel karşılaştırma. Çıktılar açık lisanslı graf, ontoloji, kod ve veri seti olarak paylaşılacak; teknoloji hazırlık seviyesi 3'ten 4'e taşınacaktır.

## Abstract

Turkish higher-education legislation forms a four-layer hierarchy: the Higher Education Law No. 2547, Council of Higher Education regulations, university regulations and senate directives. Each layer derives its authority from the one above, articles are amended frequently, and transitional provisions apply the same rule differently depending on a student's enrolment cohort. Question-answering systems built on large language models ignore this structure: they split texts into flat chunks, retrieve by similarity, present repealed versions as current and read a directive in isolation from the regulation it depends on. Empirical audits of legal AI tools report substantial rates of fabricated or incorrect citations.

This project develops and evaluates KADEME, an approach that deterministically extracts the hierarchy and version structure of legislation into a knowledge graph and routes retrieval through it. In a completed proof of concept, a graph of 3,215 units and 969 article-versions was built from 12 norms; on a 42-record question set, graph-based retrieval raised recall@5 on temporal questions from 0.69 to 1.00 and hierarchy coverage from 0.62 to 0.75, while only 47% of the versions returned by flat retrieval for temporal questions were in force on the query date. The project advances this evidence in four directions: (1) extending the corpus to all CHE regulations and three universities, and versioning at paragraph level; (2) retrieval that interprets date and cohort expressions in the question, with multi-hop graph expansion and learned re-ranking; (3) answer generation in which every citation is verified against the graph and its validity period; (4) a 300-question open benchmark (YÖKSC) with double annotation and separate development and test splits, enabling statistical comparison. Outputs will be released as an openly licensed graph, ontology, code and dataset; the technology readiness level will advance from 3 to 4.

---

## 1. BİLİMSEL NİTELİK

### 1.1 Konunun Önemi ve Projenin Bilimsel Niteliği

**Kapsam ve sınırlar.** Türkiye'de yükseköğretim, 2547 sayılı Yükseköğretim Kanunu'nun çizdiği çerçeve içinde Yükseköğretim Kurulu (YÖK) yönetmelikleri, her üniversitenin Resmî Gazete'de yayımlanan eğitim-öğretim yönetmelikleri ve senatoların çıkardığı yönerge ve usul-esaslarla düzenlenir. Bu dört katman arasında açık bir dayanak ilişkisi vardır: bir senato yönergesi, "Dayanak" maddesinde hangi yönetmeliğe ve o yönetmelik hangi kanun maddesine dayandığını belirtir. Katmanlar yalnızca hiyerarşik değil, zamansal olarak da katmanlıdır. 2547 sayılı Kanun'un bazı maddelerinin on altı ayrı sürümü vardır; YÖK'ün Önlisans ve Lisans Düzeyindeki Programlar Arasında Geçiş Yönetmeliği 2010'dan bu yana onlarca değişiklik geçirmiştir. Geçici maddeler ise aynı kuralı, öğrencinin kayıt yaptırdığı eğitim-öğretim yılına göre farklı uygular: 2023 değişikliğinden önce yurt dışından yatay geçiş için kayıt yaptıran öğrenciye değişiklik öncesi hüküm uygulanır. Dolayısıyla "bu konuda kural nedir?" sorusunun doğru yanıtı üç değişkene bağlıdır: hangi katman, hangi tarih, hangi kohort.

Proje, bu üç değişkeni açıkça modelleyen bir erişim ve soru-yanıt yaklaşımı geliştirmeyi hedefler. Kapsam yükseköğretim mevzuatı ile sınırlıdır; cevap üretiminde amaç hukuki yorum değil, ilgili ve yürürlükteki hükümleri doğru atıfla getirmektir. Yöntem alan bağımsızdır; ancak doğrulama yükseköğretim külliyatı üzerinde yapılacaktır.

**Sorunun önemi.** Üniversitelerde öğrenci işleri, enstitüler, hukuk müşavirlikleri ve öğrencilerin kendileri her gün bu soruları sorar; YÖK'e ve üniversitelere gelen bilgi edinme başvurularının önemli bir bölümü mevzuatın hangi sürümünün kime uygulanacağına ilişkindir. Büyük dil modelleri (BDM) bu ihtiyaca cevap vermek için yaygın biçimde kullanılmaya başlanmıştır; ancak mevzuat metni üzerinde düz "erişim destekli üretim" (retrieval-augmented generation, RAG; Lewis ve diğerleri, 2020) kuran sistemlerin üç yapısal zaafı vardır. Birincisi, metin parçalara bölünüp gömme benzerliğiyle arandığından aynı maddenin farklı tarihli sürümleri birbirinden ayırt edilmez; yürürlükten kalkmış bir hüküm yürürlükteymiş gibi getirilir. İkincisi, yönerge ile dayandığı yönetmelik arasındaki ilişki metinde değil yapıda olduğundan hiyerarşik tamamlama yapılamaz; bir yönerge hükmü, onu sınırlayan üst kural olmadan sunulur. Üçüncüsü, model yanıtına koyduğu atıfların varlığı ve yürürlüğü denetlenmez. Dahl ve diğerleri (2024), genel amaçlı BDM'lerin hukuki sorularda %58 ile %88 arasında halüsinasyon oranı gösterdiğini; Magesh ve diğerleri (2025) ise erişim destekli ticari hukuk araştırma araçlarının bile yanıtlarının %17 ile %33'ünde halüsinasyon (yanlış ya da uydurma bilgi veya atıf) ürettiğini ölçmüştür. Türkçe için bu ölçümler henüz yapılmamıştır; ancak zaafların dilden bağımsız olduğu, yapısal olduğu açıktır.

**Literatürdeki durum.** Üç araştırma çizgisi bu projeyle doğrudan ilgilidir.

*Mevzuatın yapısal ve zamansal modellenmesi.* Akoma Ntoso (Palmirani ve Vitali, 2011) ve Avrupa Mevzuat Tanımlayıcısı ELI (Avrupa Birliği Konseyi, 2012) mevzuatı eser, ifade ve sürüm düzeylerinde tanımlayan standartlardır. Bu standartlar belge merkezlidir: belirli bir tarihteki durum, konsolide bir belge olarak saklanır; madde ya da fıkra düzeyinde bağımsız sürüm zinciri ve bir değişikliğin hangi birimi nasıl etkilediği açıkça modellenmez. de Martim (2025a) bu boşluğu LRMoo tabanlı, olay merkezli bir graf modeliyle kapatmayı önermiş ve Brezilya Anayasası üzerinde kavramsal bir mimari sunmuştur; aynı yazar (2025b) bu grafa deterministik erişim ilkelleri tanımlamıştır. Her iki çalışma da uygulama ve ölçüm içermez. Colombo ve diğerleri (2025) İtalyan mevzuatından, Akoma Ntoso XML'den yola çıkarak BDM destekli bir özellik grafı kurmuştur. Akarajaradwong ve diğerleri (2026), Tayland mevzuatı için 4.118 kanunun 6.561 sürümünü hiyerarşi, zaman ve çapraz atıf kenarlarıyla birleştiren bir üretim grafı sunmuş ve graf temelli erişimin atıf F1'ini düz vektör erişimine göre 0,685'ten 0,812'ye çıkardığını bildirmiştir. Bu çalışmaların ortak sonucu açıktır: hukuk metninde yapıyı açıkça modellemek erişim doğruluğunu artırır. Ortak eksikleri de açıktır: hiçbiri Türkçe için yapılmamıştır; hiçbiri kanun, düzenleyici kurum, üniversite ve senato biçiminde dört katmanlı bir hiyerarşiyi ele almamıştır; hiçbiri geçici maddelerin kohort bağımlı uygulanabilirliğini modellememiştir. Tayland çalışması yapısal XML'i olmayan, HTML ve PDF olarak yayımlanan kaynaklardan graf çıkarmanın mümkün olduğunu gösterir; Türkiye'de mevzuat.gov.tr de yapısal biçim sunmaz ve yalnızca güncel konsolide metni verir, bu nedenle tarihsel sürümlerin yeniden oluşturulması ayrı bir problemdir.

*Graf destekli erişim.* GraphRAG (Edge ve diğerleri, 2024) ve ardından gelen çalışmalar (Peng ve diğerleri, 2024) metinden BDM ile çıkarılan varlık graflarını erişimde kullanır. Mevzuat için bu yaklaşımın iki sakıncası vardır: graf olasılıksal çıkarıldığından denetlenemez ve hukuki yapıda zaten açıkça var olan ilişkiler (dayanak, atıf, değişiklik) yeniden "keşfedilmeye" çalışılır. Projenin yaklaşımı tersidir: graf, metindeki kalıplardan (madde başlıkları, değişiklik notları, dayanak maddeleri, atıf ifadeleri) deterministik kurallarla çıkarılır; BDM yalnızca sorgu anlama ve son cevap aşamasında kullanılır. Bu, de Martim'in (2025b) "belirsizlik yalnızca niyet çevirisi ve anlatımda kalmalı" ilkesiyle örtüşür, ancak o çalışmanın aksine uçtan uca uygulanıp ölçülecektir.

*Hukuki RAG değerlendirmesi ve Türkçe kaynaklar.* LegalBench (Guha ve diğerleri, 2023) ve LegalBench-RAG (Pipitone ve Alami, 2024) İngilizce için hukuki akıl yürütme ve erişim ölçütleri sunar; LEXTREME (Niklaus ve diğerleri, 2023) çok dilli bir settir. Bu setlerin hiçbirinde "belirli bir tarih itibarıyla yürürlükteki hüküm" sorusu yoktur; zamansal doğruluk, hukuki RAG değerlendirmesinde ölçülmeyen bir boyuttur. Türkçe hukuk NLP'si yüksek mahkeme kararlarının sınıflandırılmasıyla başlamış (Mumcuoğlu ve diğerleri, 2021), son dönemde Türkçe hukuk alanına özgü kodlayıcı ve üretken modeller (Uğur ve diğerleri, 2026) ve topluluk kaynaklı mevzuat RAG denemeleri ortaya çıkmıştır. Ancak Türkçe mevzuat için (i) sürüm ve hiyerarşi bilgisi taşıyan açık bir graf, (ii) zamansal ve hiyerarşik soruları içeren çift etiketli bir değerlendirme seti ve (iii) atıf doğruluğunun ölçüldüğü bir karşılaştırma bulunmamaktadır.

**Projenin bilimsel niteliği ve özgün katkısı.** Proje üç özgün katkı hedefler.

1. *Dört katmanlı, kohort farkında mevzuat grafı.* Kanun, YÖK yönetmeliği, üniversite yönetmeliği ve senato yönergesi katmanlarını DAYANAK kenarlarıyla; madde ve fıkra düzeyinde sürümleri yürürlük aralıklarıyla; değişiklikleri olay düğümleriyle; geçici maddeleri giriş dönemine bağlı uygulanabilirlik kuralları olarak modelleyen, Akoma Ntoso ve ELI ile hizalı bir ontoloji ve bu ontolojiyi dolduran deterministik, test edilebilir bir ayrıştırıcı. Literatürde kohort bağımlı uygulanabilirlik kuralı modellenmemiştir.

2. *Yalnızca güncel metin yayımlayan bir kaynaktan tarihsel sürümlerin yeniden oluşturulması.* Değişiklik notları, kanun sonundaki yürürlük tabloları, akademik takvim dipnotları, Resmî Gazete'deki değiştirici mevzuat metinleri ve İnternet arşivi gözlemlerinin birlikte kullanıldığı, her sürüm başlangıcının dayanağını ve belirsizliğini kayıt altına alan bir yöntem. Bu problem, yapısal arşivi olmayan her ulusal mevzuat sistemi için geçerlidir.

3. *Zamansal ve hiyerarşik doğruluğu ölçen açık bir Türkçe değerlendirme seti (YÖKSC) ve doğrulanabilir cevap üretimi.* Sorudaki tarih ve kohort ifadelerini çözen, graf üzerinde çok atlamalı genişletme yapan ve her atıfı grafta ve yürürlükte doğrulayan bir erişim-üretim hattı; düz RAG ile istatistiksel olarak karşılaştırılması.

**Ön çalışma.** Yürütücü, bu önerinin iki temel iddiasını sınamak için küçük ölçekli, uçtan uca bir kavram kanıtı (KADEME PoC; Yumuşak, 2026) tamamlamıştır. Külliyat dört katmanı temsil eden 12 normdan oluşmuştur: 2547 sayılı Kanun; dört YÖK yönetmeliği; TOBB ETÜ'nün lisans ve lisansüstü yönetmelikleri; beş TOBB ETÜ yönergesi/usul-esası. Deterministik ayrıştırıcı 3.215 birim (572 madde, 1.664 fıkra, 814 bent, 165 alt bent), 969 madde-sürüm (709'u metinli), 684 değişiklik olayı, 17 DAYANAK ve 180 ATIF kenarı ile 4 uygulanabilirlik kuralı üretmiştir. Tarihsel metinler, mevzuat.gov.tr'nin İnternet arşivindeki 40 kopyasından elde edilmiş; sürüm başlangıçlarının %97'si değişiklik notu, yürürlük tablosu, dipnot ya da normun yürürlüğü gibi belgesel dayanağa bağlanmış, yalnızca %3'ü arşiv gözlemine dayalı "yaklaşık" olarak işaretlenmiştir. Ayrıştırıcı için 14 birim testi yazılmıştır.

Erişim karşılaştırması 42 kayıtlık bir soru seti (10 tek madde, 16 zamansal sürüm, 8 hiyerarşi, 4 intibak, 4 cevaplanamaz) üzerinde, BM25 ve bge-m3 (Chen ve diğerleri, 2024) hibrit erişimini kullanan iki yapılandırmayla yapılmıştır: A düz RAG; B aynı hibrit erişim + yürürlük ve kohort filtresi + DAYANAK/ATIF üzerinden tek atlamalı genişletme + katman önceliği. Sonuçlar Tablo 1'dedir.

**Tablo 1.** Ön çalışma sonuçları (k = 5; madde-sürüm düzeyinde).

| Soru türü (n) | Ölçüt | A: düz RAG | B: KADEME-lite |
|---|---|---:|---:|
| Tek madde (10) | Duyarlılık@5 | 0,90 | 1,00 |
| Zamansal sürüm (16) | Duyarlılık@5 | 0,69 | 1,00 |
| Zamansal sürüm (16) | Yürürlük doğruluğu | 0,47 | 1,00 |
| Hiyerarşi (8) | Hiyerarşi kapsaması | 0,62 | 0,75 |
| İntibak (4) | Duyarlılık@5 | 0,88 | 0,88 |
| Tüm cevaplanabilir (38) | Duyarlılık@5 | 0,79 | 0,96 |
| Tüm cevaplanabilir (38) | Yürürlük doğruluğu | 0,67 | 1,00 |
| Cevaplanamaz (4) | Reddetme | 0,25 | 0,25 |

Bileşen ayrıştırması, hiyerarşi kazancının graf genişletmesinden geldiğini (genişletmesiz B: 0,62), zamansal kazancın ise yürürlük filtresinden geldiğini göstermiştir. Ön çalışma, aynı zamanda projede giderilecek sınırları da ortaya koymuştur: set küçüktür ve ayrı bir geliştirme bölmesi yoktur; sürümleme madde düzeyindedir; sorgu tarihi soruyla birlikte verilmektedir, sorudan çıkarılmamaktadır; cevap üretimi yoktur; intibak sorularında her iki yapılandırma da geçici maddeyi kaçırmıştır; iki norm arasında DAYANAK kenarı bulunmadığında genişletme çalışmamaktadır; reddetme eşiği kalibre edilmemiştir.

**Araştırma sorusu ve hipotezler.** Ana soru şudur: *Mevzuatın hiyerarşi, sürüm ve kohort yapısı deterministik olarak bir grafa çıkarılıp erişim ve cevap üretimi bu graf üzerinden yürütüldüğünde, düz RAG'e göre atıf, yürürlük ve hiyerarşi doğruluğu ne ölçüde artar?* Sınanacak hipotezler:

- **H1 (çıkarılabilirlik).** Dört katmanlı yükseköğretim mevzuatının madde ve fıkra düzeyindeki sürüm zinciri, deterministik kurallarla, rastgele örneklemde ≥ %90 metin doğruluğu ve ≥ %85 yürürlük aralığı doğruluğuyla çıkarılabilir.
- **H2 (zamansal doğruluk).** Graf temelli erişim, zamansal sorularda düz RAG'e göre duyarlılık@5'i en az 0,20 mutlak puan artırır ve getirilen hükümlerin yürürlük doğruluğunu ≥ 0,95'e taşır (düz RAG'de < 0,70 beklenir).
- **H3 (hiyerarşik tamamlama).** Çok atlamalı DAYANAK/ATIF genişletmesi, hiyerarşi sorularında iki katmandan da hüküm getirme oranını ≥ 0,85'e çıkarır.
- **H4 (atıf doğrulama).** Graf doğrulamalı cevap üretimi, cevaplardaki var olmayan ya da yürürlükte olmayan atıf oranını düz RAG tabanlı üretime göre en az yarıya indirir.

Hipotezler, ≥ 300 soruluk, çift etiketli ve ayrı test bölmesi olan YÖKSC seti üzerinde eşleştirilmiş yeniden örnekleme testleriyle sınanacaktır.

*(Kelime sayısı: yaklaşık 1.490)*

### 1.2 Amaç ve Hedefler

**Amaç.** Yükseköğretim mevzuatının hiyerarşi, sürüm ve kohort yapısını açık, deterministik ve denetlenebilir bir bilgi grafına çıkaran; erişimi ve cevap üretimini bu graf üzerinden yürüterek yürürlükte olmayan ya da hiyerarşik bağlamından kopuk hükümlerin getirilmesini önleyen KADEME yaklaşımını geliştirmek ve açık bir değerlendirme seti üzerinde düz RAG'e göre kazancını ölçmek.

**Hedefler.**

- **Hedef 1 — Graf.** 2547 sayılı Kanun, YÖK'ün eğitim-öğretim ve öğretim elemanlarına ilişkin yürürlükteki tüm yönetmelikleri ile biri vakıf (TOBB ETÜ), ikisi devlet olmak üzere üç üniversitenin yönetmelik ve senato yönergelerinden oluşan, en az 60 norm, 20.000 birim ve 6.000 madde-sürüm içeren; fıkra düzeyinde sürümlenmiş; ELI ve Akoma Ntoso ile hizalı ontolojiyle RDF olarak dışa aktarılabilen bir mevzuat grafı. Ölçüt: 100 rastgele sürümün elle kontrolünde metin doğruluğu ≥ %90, yürürlük aralığı doğruluğu ≥ %85 (H1).
- **Hedef 2 — Değerlendirme seti.** En az 300 soruluk, altı türde (tek madde, zamansal sürüm, hiyerarşi, intibak/kohort, çok atlamalı, cevaplanamaz) ve 100/200 geliştirme/test bölmeli, iki bağımsız etiketleyici tarafından doğrulanmış açık Türkçe set (YÖKSC). Ölçüt: etiketleyiciler arası Cohen kappa ≥ 0,80; set CC BY 4.0 ile yayımlanmış.
- **Hedef 3 — Erişim.** Sorudaki tarih ve kohort ifadelerini çözen, graf üzerinde çok atlamalı genişletme ve öğrenilmiş yeniden sıralama kullanan erişim hattı. Ölçüt: test bölmesinde zamansal duyarlılık@5'te düz RAG'e göre ≥ 0,20 mutlak artış ve yürürlük doğruluğu ≥ 0,95 (H2); hiyerarşi kapsaması ≥ 0,85 (H3); farklar %95 güven düzeyinde anlamlı.
- **Hedef 4 — Doğrulanabilir cevap.** Açık ağırlıklı bir BDM ile cevap üreten ve her atıfı grafta varlık ve yürürlük yönünden denetleyen hat. Ölçüt: var olmayan ya da yürürlükte olmayan atıf oranının düz RAG'e göre ≥ %50 azalması (H4); cevaplanamaz sorularda reddetme ≥ 0,90, cevaplanabilir sorularda yanlış reddetme ≤ 0,05.
- **Hedef 5 — Açık çıktılar ve THS 4.** Kod (Apache-2.0), graf ve set (CC BY 4.0), ontoloji ve uçtan uca yeniden üretilebilir çalıştırma betiği; bileşenlerin bütünleştirilmiş sistemde ve temsili külliyat üzerinde doğrulanmasıyla THS 4.

*(Kelime sayısı: yaklaşık 310)*

---

## 2. YÖNTEM

**Araştırma tasarımı.** Proje, yapı çıkarma (Hedef 1), ölçüm aracı geliştirme (Hedef 2) ve karşılaştırmalı deney (Hedef 3–4) adımlarından oluşan, deneysel bir bilgisayar bilimi çalışmasıdır. Deneylerde *bağımsız değişkenler* erişim yapılandırması (düz RAG; graf filtreli; graf filtreli + genişletme; + yeniden sıralama; + doğrulamalı üretim), soru türü ve külliyat katmanıdır. *Bağımlı değişkenler* madde-sürüm düzeyinde kesinlik ve duyarlılık@k, yürürlük doğruluğu, hiyerarşi kapsaması, reddetme ve yanlış reddetme oranları ile cevaplardaki geçersiz atıf oranıdır. *Kontrol edilen değişkenler* aynı gömme modeli, aynı BM25 ayarları, aynı aday kümesi ve aynı BDM'dir; yapılandırmalar yalnızca graf bileşenlerinde farklılaşır. Tüm parametreler geliştirme bölmesinde seçilir ve test bölmesinde bir kez ölçülür. Ön çalışmanın kodu ve veri modeli (Yumuşak, 2026) başlangıç noktasıdır.

### 2.1 Külliyat ve edinim (İP1)

Kaynaklar mevzuat.gov.tr (kanun ve yönetmeliklerin güncel konsolide metinleri), Resmî Gazete (değiştirici mevzuat metinleri), üniversitelerin web siteleri (yönerge ve usul-esaslar; yalnızca metin katmanı olan PDF/DOCX) ve İnternet Arşivi'nin CDX API'si (mevzuat.gov.tr sayfalarının tarihli kopyaları) olacaktır. Edinim, saniyede bir istekle sınırlı, her dosyanın URL, SHA-256 özeti ve zaman damgasını kaydeden bir manifest ile yapılır; ham dosyalar dağıtılmaz, yalnızca türetilmiş yapısal veri yayımlanır (5846 sayılı FSEK m.31 kapsamındaki resmî metinler için de bu ilke korunur). Külliyat: 2547 ve 2914 sayılı Kanunlar; YÖK'ün eğitim-öğretim, öğrenci ve öğretim elemanı konularındaki yürürlükteki yönetmelikleri (mevzuat.gov.tr sayımına göre tahminen 40–60); TOBB ETÜ ile biri büyük, biri orta ölçekli iki devlet üniversitesinin (seçim: Resmî Gazete'de yayımlanmış yönetmelik sayısı ve yönergelerinin web'de metin olarak erişilebilirliği ölçütleriyle) yönetmelik ve yönergeleri.

### 2.2 Deterministik ayrıştırma ve sürümleme (İP1, İP2)

Ayrıştırıcı, ön çalışmada geliştirilen kural tabanını genelleştirir. *Yapı:* madde, ek madde, geçici madde, fıkra, bent ve alt bent kalıpları; kanun sonundaki yürürlük tabloları ve "işlenemeyen hükümler" blokları; yönetmelik sonundaki Resmî Gazete tabloları. *Değişiklik notları:* "(Değişik/Ek/Mülga/İptal/Yeniden düzenlenen …: tarih-kanun/madde)" kalıplarından değiştiren norm, madde, tarih, Resmî Gazete sayısı ve Anayasa Mahkemesi kararları çıkarılır; notlardaki kabul tarihi, kanunların yürürlük tablosu ve yönetmeliklerin "(n) Bu değişiklik … döneminden itibaren yürürlüğe girer" dipnotları ile yürürlük tarihine çevrilir.

Projede iki yenilik eklenecektir. (i) *Fıkra düzeyi sürümleme:* değişiklik notları fıkra ve bent kapsamını zaten belirtmektedir; sürüm zinciri bu kapsam bilgisiyle fıkra düzeyine indirilecek, madde sürümü fıkra sürümlerinin birleşimi olarak türetilecektir. (ii) *Resmî Gazete'den yeniden oluşturma:* ön çalışmada tarihsel metinler yalnızca arşiv gözlemlerinden alınmıştı. Projede değiştirici mevzuatın Resmî Gazete metnindeki "… maddesi aşağıdaki şekilde değiştirilmiştir" kalıpları ayrıştırılarak önceki sürüm metni geriye doğru yeniden oluşturulacak, arşiv gözlemleri bu yeniden oluşturmayı doğrulamak için kullanılacaktır. Her sürüm başlangıcı dayanağıyla (tablo, not, dipnot, Resmî Gazete, arşiv gözlemi) ve varsa belirsizlik aralığıyla kaydedilir. Kısmi yürürlük hükümleri (madde bazlı farklı yürürlük tarihleri) modellenecektir.

*Dayanak ve atıf:* "Dayanak" maddelerindeki ve metin içindeki "… Kanununun 44 üncü maddesinin (c) fıkrası" türü ifadeler, niteleyici devralma kurallarıyla çözümlenir; korpus dışı normlara atıflar sayılır ama kenar üretmez. *Uygulanabilirlik kuralları:* geçici ve intibak maddelerindeki "… eğitim-öğretim yılından önce kayıt yaptıran öğrencilere … uygulanmaz/önceki hükümler uygulanır" kalıpları, hedef madde ve giriş dönemi koşulu taşıyan kurallara çevrilir. Ön çalışmada dört kural bulunmuştur; genişleyen külliyatta kalıp envanteri çıkarılıp kapsama oranı raporlanacaktır.

Ayrıştırıcı birim testleriyle (hedef ≥ 60 test) korunur. Doğruluk, graftan rastgele seçilen 100 madde/fıkra-sürümünün yürütücü ve bir hukuk müşavirliği uzmanı tarafından kaynak metinle karşılaştırılmasıyla ölçülür (H1).

### 2.3 Veri modeli ve graf (İP2)

Düğümler: Norm (tür, katman, kurum, Resmî Gazete bilgisi, uygulanabilirlik: devlet/vakıf/hepsi), Birim (madde/fıkra/bent), Sürüm (metin, yürürlük başlangıç/bitiş, dayanak, durum), DeğişiklikOlayı, UygulanabilirlikKuralı. Kenarlar: DAYANAK, ATIF, DEĞİŞTİRİR, UYGULANIR, PARÇASI, SÜRÜMÜ. Ontoloji, ELI'nin LegalResource/LegalExpression ve Akoma Ntoso'nun yapısal sınıflarıyla `closeMatch` eşlemeleri taşır. Graf NetworkX ile bellekte tutulur, SQLite ve RDF/Turtle olarak dışa aktarılır; `point_in_time(birim, tarih)` ve `applicable(birim, tarih, kohort)` sorguları ikili arama ve kural uygulamayla deterministik olarak yanıtlanır. Graf istatistikleri (düğüm/kenar sayıları, sürüm zinciri uzunluk dağılımı, başlangıç dayanağı dağılımı) otomatik raporlanır.

### 2.4 Değerlendirme seti YÖKSC (İP3)

En az 300 soru, altı türde dengelenir: tek madde (60), zamansal sürüm çifti (80; aynı soru iki tarihte, farklı doğru sürüm), hiyerarşi (60; iki katmandan hüküm gerektirir), intibak/kohort (40; giriş dönemiyle), çok atlamalı (20; yönerge → yönetmelik → kanun) ve cevaplanamaz (40; mevzuatta karşılığı olmayan ya da sorgu tarihinde henüz düzenlenmemiş konular). Sorular graftan şablonla aday olarak üretilir (değişiklik notu olan maddeler, DAYANAK zincirleri, kurallar), sonra doğal dile elle yazılır; sorgu tarihi ve kohort bilgisi soru metnine gömülür ("2019 güzünde kayıt yaptıran bir öğrenci 2023'te …"). Altın hükümler madde/fıkra düzeyinde, tarih elle; sürüm kimlikleri graftan çözülür ve sabitlenir. Etiketler, aynı kılavuzla eğitilmiş iki lisans bursiyeri tarafından birbirinden bağımsız doğrulanır; anlaşma Cohen kappa (Cohen, 1960) ile raporlanır, uyuşmazlıklar yürütücü tarafından, gerektiğinde hukuk müşavirliğine danışılarak çözülür. Set 100 geliştirme / 200 test olarak bölünür; test bölmesi parametre seçiminde kullanılmaz.

### 2.5 Erişim (İP4)

*Taban:* madde/fıkra-sürüm metinleri üzerinde BM25 (Robertson ve Zaragoza, 2009; Türkçe küçük harf ve kök kısaltma) ve bge-m3 yoğun gömmeleri (Chen ve diğerleri, 2024), karşılıklı sıra füzyonu ile birleştirilir (Cormack ve diğerleri, 2009). Türkçe hukuk alanına özgü gömme modelleri (Uğur ve diğerleri, 2026) geliştirme bölmesinde karşılaştırılır.

*Zamansal sorgu anlama:* sorudaki mutlak tarih, akademik dönem ("2019-2020 güz") ve kohort ifadeleri kural tabanlı çözücü ile tarih ve giriş dönemine çevrilir; çözülemeyen durumlarda küçük bir BDM yapılandırılmış çıkarım için kullanılır ve çıkarım kayıt altına alınır. Tarih yoksa sorgu tarihi "bugün" kabul edilir.

*Graf filtresi ve genişletme:* aday hükümler sorgu tarihinde ve kohorta göre uygulanan sürümlerle sınırlanır; ilk k tohumdan DAYANAK (yukarı/aşağı) ve ATIF kenarları üzerinden iki atlamaya kadar genişletme yapılır; komşular kendi hibrit skorlarıyla, kenar türüne göre ağırlıklanarak aday olur. Katman önceliği, temsil edilmeyen katmanların en iyi adayını listeye alır. DAYANAK kenarı eksik norm çiftleri için (ön çalışmada gözlenen sorun) ad tabanlı norm çözümleme eklenir.

*Yeniden sıralama:* ilk 20 aday, çapraz kodlayıcı (bge-reranker-v2-m3) ile yeniden sıralanır; graf özellikleri (katman, DAYANAK uzaklığı, sürüm yaşı) ile sıralama skorunun doğrusal birleşimi geliştirme bölmesinde ayarlanır.

*Reddetme:* en yüksek benzerlik ve yeniden sıralama skoru eşiği, geliştirme bölmesinde yanlış reddetme ≤ 0,05 koşuluyla seçilir; eşik taraması raporlanır.

### 2.6 Doğrulanabilir cevap üretimi (İP5)

Açık ağırlıklı, Türkçe destekli bir BDM (8–14 milyar parametre aralığında; seçim geliştirme bölmesinde) yalnızca erişilen hükümlerle, her cümleye atıf koyacak biçimde yönlendirilir. Üretilen her atıf, ön çalışmadaki `cite_check` mantığıyla grafta varlık, sorgu tarihinde yürürlük ve kohorta uygulanabilirlik yönünden denetlenir; geçersiz atıf taşıyan cümleler işaretlenir ve yeniden üretim ya da reddetme tetiklenir. Ölçüm: geçersiz atıf oranı, atıf duyarlılığı (altın hükümlerin cevapta anılma oranı) ve 50 soruluk alt kümede iki uzmanın (hukuk müşavirliği ve öğrenci işleri) 1–5 ölçeğinde doğruluk ve yeterlilik puanı. Düz RAG tabanlı üretimle aynı BDM ve aynı yönlendirme kullanılarak karşılaştırılır (H4).

### 2.7 İstatistiksel analiz

Yapılandırmalar aynı sorular üzerinde ölçüldüğünden farklar eşleştirilmiş olarak sınanır: soru düzeyi ölçütler için eşleştirilmiş önyükleme (bootstrap, 10.000 yeniden örnekleme) ile %95 güven aralıkları ve Wilcoxon işaretli sıra testi; oranlar için McNemar testi. Çoklu karşılaştırmalarda Holm düzeltmesi uygulanır. Soru türü başına ve tüm set için sonuçlar raporlanır; etki büyüklüğü mutlak fark olarak verilir. Bileşen ayrıştırması (her graf bileşeni ayrı ayrı çıkarılarak) ön çalışmadaki gibi yapılır.

### 2.8 Yeniden üretilebilirlik ve THS doğrulaması

Tüm hat tek bir betikle (edinim → ayrıştırma → graf → test → değerlendirme → rapor) temiz bir makinede, GPU ve ücretli API gerektirmeden çalışır; yoğun gömme ve BDM adımları ayrı seçeneklerle etkinleşir. THS 4 doğrulaması, bileşenlerin bütünleştirilmiş sistemde temsili külliyat ve YÖKSC üzerinde çalıştırılması, çıktıların bağımsız bir makinede yeniden üretilmesi ve sonuçların bu başlıkların altındaki ölçütlerle belgelenmesiyle yapılır.

*(Kelime sayısı: yaklaşık 1.160)*

---

## 3. PROJE YÖNETİMİ

### 3.1 İş Paketleri ve İş-Zaman Çizelgesi

| İP | İş paketinin adı ve hedefleri | Kim | Aylar | Başarı ölçütü | Önem (%) |
|---|---|---|---|---|---:|
| 1 | **Külliyat genişletme ve ayrıştırıcının genelleştirilmesi.** Edinim, manifest, yapı ayrıştırma; YÖK yönetmelikleri ve üç üniversite için kural tabanının genişletilmesi. | Yürütücü, YL bursiyeri, lisans bursiyeri A | 1–4 | ≥ 60 norm, ≥ 20.000 birim edinilip ayrıştırılmış; ≥ 60 birim testi geçiyor; atlanan belge oranı ≤ %5 ve gerekçeli raporlanmış. | 20 |
| 2 | **Fıkra düzeyi sürümleme, Resmî Gazete'den yeniden oluşturma, ontoloji ve graf.** Değişiklik olayları, uygulanabilirlik kuralları, ELI/AKN hizalı RDF dışa aktarımı. | Yürütücü, YL bursiyeri, lisans bursiyeri A | 2–6 | ≥ 6.000 madde-sürüm; 100 rastgele sürümün elle kontrolünde metin doğruluğu ≥ %90, yürürlük aralığı doğruluğu ≥ %85 (H1); RDF çıktısı SPARQL ile sorgulanabilir. | 20 |
| 3 | **YÖKSC değerlendirme seti.** Şablon adayları, doğal dile yazım, çift etiketleme, uyuşmazlık çözümü, bölme. | Yürütücü, lisans bursiyerleri B ve C, YL bursiyeri | 3–8 | ≥ 300 soru, altı tür; Cohen kappa ≥ 0,80; 100/200 bölme; CC BY 4.0 ile yayım hazır. | 15 |
| 4 | **Graf temelli erişim ve deneyler.** Zamansal sorgu anlama, çok atlamalı genişletme, yeniden sıralama, reddetme kalibrasyonu; bileşen ayrıştırması; istatistiksel analiz. | Yürütücü, YL bursiyeri | 5–10 | Test bölmesinde zamansal duyarlılık@5 artışı ≥ 0,20 ve yürürlük doğruluğu ≥ 0,95 (H2); hiyerarşi kapsaması ≥ 0,85 (H3); farklar %95 düzeyinde anlamlı; sonuç tabloları otomatik üretiliyor. | 25 |
| 5 | **Doğrulanabilir cevap üretimi, uzman değerlendirmesi ve THS 4 doğrulaması.** Atıf denetimli üretim, 50 soruluk uzman puanlaması, uçtan uca yeniden üretilebilir çalıştırma. | Yürütücü, YL bursiyeri, lisans bursiyeri C | 8–12 | Geçersiz atıf oranı düz RAG'e göre ≥ %50 düşük (H4); reddetme ≥ 0,90, yanlış reddetme ≤ 0,05; hat bağımsız makinede baştan sona çalışıp aynı tabloları üretiyor; kod, graf, set ve ontoloji açık lisansla yayımlanmış. | 20 |

İş paketlerinin toplam süresi 12 aydır; İP1–İP2 ve İP3–İP4 kısmen örtüşür (veri hazırlığı ile set geliştirme paralel yürür).

### 3.2 Risk Yönetimi

| İP | En önemli riskler | Risk yönetimi (B planı) |
|---|---|---|
| 1 | mevzuat.gov.tr ya da üniversite sitelerinin HTML/PDF yapısı değişir veya bazı belgeler metin katmanı olmadan (taranmış) yayımlanmıştır; ayrıştırıcı bu belgelerde düşük kapsama verir. | Ayrıştırıcı belge başına kapsama oranı raporlar; eşik altı belgeler kapsam dışı bırakılıp gerekçesiyle listelenir. Taranmış PDF'ler için OCR yapılmaz; aynı normun Resmî Gazete metni kullanılır. Külliyat hedefi (≥ 60 norm) devlet üniversitesi seçimi değiştirilerek korunur. |
| 2 | Resmî Gazete değiştirici metinlerinden geriye doğru yeniden oluşturma bazı değişiklik türlerinde (ibare değişikliği, fıkra ekleme sırası) belirsiz kalır; arşiv gözlemi bulunmayan dönemler için metin elde edilemez. | Yeniden oluşturulamayan sürümler metinsiz yer tutucu olarak kalır ve `metin_mevcut = false` ile işaretlenir; başlangıç dayanağı ve belirsizlik aralığı kaydedilir. H1 ölçümü metinli sürümler üzerinden, yer tutucu oranı ayrıca raporlanarak yapılır. |
| 3 | Çift etiketlemede anlaşma hedefin (kappa ≥ 0,80) altında kalır; soru türlerinden biri için yeterli aday bulunamaz. | Etiketleme kılavuzu pilot 30 soruda revize edilir; uyuşmazlıklar üçüncü kişiyle çözülür ve kappa tekrar ölçülür. Aday bulunamayan tür için hedef sayı diğer türlere dağıtılır; set en az 300 soruda tutulur. |
| 4 | Graf genişletmesi doğrudan isabetleri dışarı iterek kesinliği düşürür (ön çalışmada gözlendi); yeniden sıralayıcı Türkçe mevzuat metninde yeterince ayırt edici değildir. | Geliştirme bölmesinde doğrudan isabetlerin korunma sayısı ve kenar ağırlıkları ayarlanır; yeniden sıralayıcı kazanç sağlamazsa graf özellikli doğrusal sıralama ile devam edilir. Hipotez testleri her durumda test bölmesinde bir kez yapılır; olumsuz sonuç da raporlanır. |
| 5 | Açık ağırlıklı BDM'ler Türkçe hukuk metninde tutarlı atıf üretmez; uzman değerlendiricilere zamanında ulaşılamaz. | Atıf denetimi üretimden bağımsız olduğundan, üretim kalitesi düşük olsa da geçersiz atıf oranı ölçülebilir; iki BDM karşılaştırılır. Uzman puanlaması 50 sorudan 30'a indirilebilir; yürütücü kurumun hukuk müşavirliği ve öğrenci işleriyle ön görüşme proje başında yapılır. |

### 3.3 Araştırma Olanakları

Proje, ön çalışmada kullanılan altyapıyla yürütülebilir niteliktedir: geliştirme ve BM25/bge-m3 deneyleri iş istasyonu düzeyinde donanımda çalışmaktadır. Çapraz kodlayıcı ve 8–14 milyar parametreli BDM deneyleri için [TOBB ETÜ'nün mevcut GPU sunucusu — model/adet] kullanılacaktır; bütçede hesaplama hizmeti alımı yoktur. Kurumun hukuk müşavirliği ve öğrenci işleri birimleri, elle kontrol ve uzman değerlendirmesi için [ön görüşme yapıldı / yapılacak]. Ücretli API gerekmez.

**Proje ekibi.** Yürütücü (bilgi grafları, anlamsal web ve erişim üzerine [n] yayın; ön çalışmanın geliştiricisi), bir yüksek lisans bursiyeri (ayrıştırıcı, graf ve erişim kodu; tez konusu projeyle ilişkili) ve üç lisans bursiyeri: A ayrıştırıcı testleri ve elle kontrol (İP1–İP2), B ve C birbirinden bağımsız iki etiketleyici olarak YÖKSC'nin yazımı ve doğrulanması (İP3), C ayrıca uzman değerlendirmesi formları (İP5). İki bağımsız lisans etiketleyicisi, anlaşma ölçümünün yürütücünün kendi etiketlerinden bağımsız yapılmasını sağlar; yürütücü uyuşmazlıkları çözer. Uzman değerlendirmesi yürütücü kurumun hukuk müşavirliği ve öğrenci işleriyle yapılır.

---

## 4. ÇIKTI, ETKİ VE KAZANIMLAR

**Çıktılar.** (1) Açık lisanslı KADEME yazılımı (Apache-2.0): deterministik ayrıştırıcı, graf, erişim ve atıf denetimi; tek betikle yeniden üretilebilir (0–12 ay). (2) Yükseköğretim mevzuatı grafı: ≥ 60 norm, ≥ 6.000 madde-sürüm, RDF ve SQLite olarak, CC BY 4.0 (6–12 ay). (3) YÖKSC: ≥ 300 soruluk, çift etiketli, zamansal ve hiyerarşik doğruluğu ölçen ilk açık Türkçe mevzuat soru-yanıt seti (8–12 ay). (4) ELI/Akoma Ntoso hizalı, kohort farkında mevzuat ontolojisi (6 ay). (5) Bir uluslararası konferans bildirisi (JURIX, ICAIL ya da NLLP çalıştayı; 12–18 ay) ve bir SCI/SCI-E dergi makalesi (Information Processing & Management, Artificial Intelligence and Law düzeyinde; 12–24 ay). (6) Bir yüksek lisans tezi (12–24 ay). (7) 1001 ya da uluslararası (örneğin Ufuk Avrupa) başvurusu için THS 4 dayanağı (12–18 ay).

**Etkiler.** *Bilimsel:* yalnızca güncel metin yayımlayan mevzuat sistemlerinde tarihsel sürümlerin yeniden oluşturulması ve kohort bağımlı uygulanabilirlik kuralları için yeniden kullanılabilir bir yöntem; Türkçe hukuki RAG'de zamansal doğruluğun ilk ölçümü. *Toplumsal/kurumsal:* öğrenci işleri, enstitü ve hukuk müşavirliklerinin öğrencilere verdiği mevzuat bilgisinde yürürlük ve dayanak hatalarının azalması; öğrencilerin hangi kuralın kendilerine uygulandığını doğrulanabilir atıfla öğrenebilmesi. *Teknolojik/ekonomik:* yöntem diğer düzenleyici alanlara (sağlık, vergi, kamu ihale) aktarılabilir; yerli hukuk teknolojisi girişimleri için açık altyapı. 12. Kalkınma Planı'nın yapay zekâ ve dijital kamu hizmetleri, Türkçe doğal dil işleme ve yükseköğretimde kalite hedeflerine katkı sağlar.

**Kazanımlar ve yararlanıcılar.** Üniversitelerin idari birimleri (doğru sürüm ve dayanakla bilgi), öğrenciler, YÖK (mevzuatın makine okunur ve sürümlü temsili), hukuk teknolojisi araştırmacıları (açık graf ve set) ve mevzuat bilişimi standartları topluluğu (ELI/AKN uzantısı). Bursiyerler bilgi grafı, erişim ve değerlendirme tasarımı alanında yetişecektir.

*(Kelime sayısı: yaklaşık 260)*

---

## BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR

Ön çalışma (KADEME PoC) ayrıştırıcı birim testleri, graf istatistikleri, bileşen ayrıştırması ve reddetme eşiği taramasıyla birlikte açık lisansla yayımlanmıştır (Yumuşak, 2026); Tablo 1'deki sonuçlar bu depodaki betikle yeniden üretilebilir. Ön çalışmanın bilinen sınırları (küçük set, geliştirme bölmesi yokluğu, madde düzeyi sürümleme, sorgu tarihinin soruyla verilmesi, cevap üretimi yokluğu) bu önerinin İP2–İP5 hedeflerini doğrudan belirlemiştir. Proje insan katılımcı verisi toplamaz; uzman puanlaması anonim, kurum içi ve yalnızca sistem çıktısına ilişkindir; etik kurul gerekliliği başvuru öncesinde kurumun etik kuruluyla teyit edilecektir.

*(Kelime sayısı: yaklaşık 80)*

---

## TEKNOLOJİ HAZIRLIK SEVİYESİ (THS)

**Mevcut THS: 3 (konseptin deneysel kanıtlanması).** Yöntemin iki temel iddiası (yapının deterministik çıkarılabilirliği; graf temelli erişimin yürürlük ve hiyerarşi doğruluğunu artırdığı), temsili bir veri seti (12 norm, 969 madde-sürüm) üzerinde çalışan yazılımla ve ölçülebilir deneylerle gösterilmiştir: algoritmalar temsili veri setiyle gerçeklenmiş, temsili işlemcide uçtan uca çalıştırılmış, ayrıştırıcı birim testleri geçmiş ve karşılaştırma tablosu üretilmiştir. Bileşenler henüz bütünleşik bir sistem olarak değil, ayrı ayrı çalıştırılan modüller olarak doğrulanmıştır; cevap üretimi bileşeni yoktur.

**Hedeflenen THS: 4 (bileşenlerin laboratuvar ortamında bütünleştirilmesi ve doğrulanması).** Proje sonunda edinim, ayrıştırma, graf, erişim, cevap üretimi ve atıf denetimi bileşenleri tek bir hat içinde bütünleştirilmiş; sistem, gerçek külliyatın temsili bir alt kümesini (≥ 60 norm, üç üniversite) ve 300 soruluk ölçüm setini kullanarak laboratuvar ortamında doğrulanmış; performans ölçütleri (duyarlılık, yürürlük doğruluğu, hiyerarşi kapsaması, geçersiz atıf oranı) belirlenmiş ve bağımsız bir makinede yeniden üretilmiş olacaktır. THS 5 (ilgili ortamda doğrulama: bir üniversitenin öğrenci işleri biriminde gerçek sorularla pilot) bu projenin kapsamı dışındadır ve sonraki adım olarak planlanmaktadır.

---

## VERİ YÖNETİM PLANI (Açık Bilim Politikası)

**1. Veri türleri ve biçimleri.**
- *Ham kaynak kopyaları:* mevzuat.gov.tr, Resmî Gazete ve üniversite sitelerinden indirilen HTML/PDF/DOCX dosyaları ile İnternet Arşivi kopyaları (tahminen 2–5 GB). Resmî metinlerdir; yeniden dağıtılmaz, yalnızca URL, SHA-256 ve zaman damgasını içeren manifest paylaşılır.
- *Türetilmiş yapısal veri:* graf düğüm ve kenarları (JSONL, SQLite, RDF/Turtle; tahminen 100–300 MB), ayrıştırma raporları, graf istatistikleri.
- *Değerlendirme verisi:* YÖKSC soru seti (JSONL), etiketleme kılavuzu, iki etiketleyicinin bağımsız etiketleri ve uyuşmazlık kayıtları, elle kontrol örneklemleri.
- *Deney çıktıları:* yapılandırma dosyaları, sonuç tabloları (JSON/Markdown), rastgele tohumlar, gömme önbellekleri (yeniden üretilebilir; paylaşılmaz).
- *Yazılım:* Python kaynak kodu, testler, çalıştırma betikleri.

**2. Üst veri ve standartlar.** Graf, ELI ve Akoma Ntoso ile `closeMatch` eşlemeli bir OWL/Turtle ontolojisiyle tanımlanır; her norm Resmî Gazete tarih ve sayısıyla, her sürüm yürürlük aralığı ve başlangıç dayanağıyla tanımlanır. Veri setleri DataCite üst verisiyle Zenodo'ya yüklenir ve DOI alır; depo README'leri alan tanımlarını içerir.

**3. Saklama ve yedekleme.** Proje boyunca sürüm kontrollü bir Git deposu (GitHub) ve kurumun yedeklenen ağ diski; ham kopyalar yürütücünün kurumsal depolama alanında. Proje sonunda kod, graf, ontoloji ve YÖKSC Zenodo'da (en az 10 yıl) ve GitHub'da arşivlenir.

**4. Paylaşım ve erişim.** Kod Apache-2.0; graf, ontoloji ve YÖKSC CC BY 4.0 ile, proje bitiminde (en geç ilk yayınla birlikte) açık erişimle paylaşılır. Ham resmî metin kopyaları, kaynak sitelerin kullanım koşulları gözetilerek yeniden dağıtılmaz; edinim betiği ve manifest sayesinde herkes aynı kopyaları yeniden edinebilir. Yayınlar açık erişimli olarak (ön baskı ve/veya açık erişim dergi) sunulur.

**5. Kişisel veri ve etik.** Mevzuat metinleri kişisel veri içermez. Uzman değerlendirmesi anonimdir; yalnızca puanlar ve serbest yorumlar, kimlik bilgisi olmadan saklanır. İnsan katılımcı araştırması niteliği taşımadığı değerlendirilmekle birlikte etik kurul gerekliliği kurumla teyit edilecektir. Kullanılan BDM'ler açık ağırlıklıdır ve yerelde çalıştırılır; hiçbir veri üçüncü taraf API'lerine gönderilmez.

**6. Sorumluluk.** Veri yönetiminden proje yürütücüsü sorumludur; yüksek lisans bursiyeri depo ve manifest bütünlüğünü, lisans bursiyerleri elle kontrol ve etiketleme kayıtlarını tutar.

---

## EK-1: KAYNAKLAR

> Künyeler başvuru öncesinde tubitak.gov.tr/ardeb-kaynakca biçimine ve DOI'lere göre doğrulanmalıdır. DOI'si verilmeyenler için arXiv numarası yazılmıştır.

Akarajaradwong, P., Nutanong, S. ve Chaksangchaichot, C. (2026). FourCorners: A production knowledge graph unifying Thailand's legal system. *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 6: Industry Track)*, 1808–1818.

Avrupa Birliği Konseyi (2012). Council conclusions inviting the introduction of the European Legislation Identifier (ELI). *Official Journal of the European Union*, C 325, 3–11.

Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D. ve Liu, Z. (2024). BGE M3-Embedding: Multi-lingual, multi-functionality, multi-granularity text embeddings through self-knowledge distillation. arXiv:2402.03216.

Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37–46. DOI: 10.1177/001316446002000104

Colombo, A., Bernasconi, A. ve Ceri, S. (2025). An LLM-assisted ETL pipeline to build a high-quality knowledge graph of the Italian legislation. *Information Processing & Management*, 62, 104082. DOI: 10.1016/j.ipm.2025.104082

Cormack, G. V., Clarke, C. L. A. ve Buettcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. *Proceedings of the 32nd International ACM SIGIR Conference*, 758–759. DOI: 10.1145/1571941.1572114

Dahl, M., Magesh, V., Suzgun, M. ve Ho, D. E. (2024). Large legal fictions: Profiling legal hallucinations in large language models. *Journal of Legal Analysis*, 16(1), 64–93. DOI: 10.1093/jla/laae003

de Martim, H. (2025a). An ontology-driven graph RAG for legal norms: A structural, temporal, and deterministic approach. arXiv:2505.00039 (JURIX 2025).

de Martim, H. (2025b). Deterministic legal agents: A canonical primitive API for auditable reasoning over temporal knowledge graphs. arXiv:2510.06002.

Edge, D., Trinh, H., Cheng, N., Bradley, J., Chao, A., Mody, A., Truitt, S. ve Larson, J. (2024). From local to global: A graph RAG approach to query-focused summarization. arXiv:2404.16130.

Guha, N., Nyarko, J., Ho, D. E., Ré, C., Chilton, A., Narayana, A., ... Li, Z. (2023). LegalBench: A collaboratively built benchmark for measuring legal reasoning in large language models. *Advances in Neural Information Processing Systems*, 36. arXiv:2308.11462.

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474. arXiv:2005.11401.

Magesh, V., Surani, F., Dahl, M., Suzgun, M., Manning, C. D. ve Ho, D. E. (2025). Hallucination-free? Assessing the reliability of leading AI legal research tools. *Journal of Empirical Legal Studies*, 22(2). arXiv:2405.20362.

Mumcuoğlu, E., Öztürk, C. E., Ozaktas, H. M. ve Koç, A. (2021). Natural language processing in law: Prediction of outcomes in the higher courts of Turkey. *Information Processing & Management*, 58(5), 102684. DOI: 10.1016/j.ipm.2021.102684

Niklaus, J., Matoshi, V., Rani, P., Galassi, A., Stürmer, M. ve Chalkidis, I. (2023). LEXTREME: A multi-lingual and multi-task benchmark for the legal domain. *Findings of the Association for Computational Linguistics: EMNLP 2023*. arXiv:2301.13126.

Palmirani, M. ve Vitali, F. (2011). Akoma-Ntoso for legal documents. G. Sartor, M. Palmirani, E. Francesconi ve M. A. Biasiotti (Ed.), *Legislative XML for the Semantic Web* içinde (s. 75–100). Springer. DOI: 10.1007/978-94-007-1887-6_6

Peng, B., Zhu, Y., Liu, Y., Bo, X., Shi, H., Hong, C., Zhang, Y. ve Tang, S. (2024). Graph retrieval-augmented generation: A survey. arXiv:2408.08921.

Pipitone, N. ve Alami, R. H. (2024). LegalBench-RAG: A benchmark for retrieval-augmented generation in the legal domain. arXiv:2408.10343.

Robertson, S. ve Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4), 333–389. DOI: 10.1561/1500000019

Uğur, Ö., Göksu, M., Çimen, M., Yılmaz, M., Şavirdi, E., Demir, A. T., Güllüce, R., Çetin, İ. ve Sağbaş, Ö. C. (2026). Mecellem models: Turkish models trained from scratch and continually pre-trained for the legal domain. arXiv:2601.16018.

Yumuşak, S. (2026). *KADEME PoC: Yükseköğretim mevzuatı için hiyerarşi ve sürüm farkında graf temelli erişim — ön çalışma* [Yazılım ve veri]. https://github.com/semihyumusak/kademe-poc

---

## EK-2: BÜTÇE VE GEREKÇESİ

Destek üst limiti (1 Şubat 2026 itibarıyla, burs dahil): 150.000 TL/yıl. Önerilen toplam: **149.750 TL**.

| Kalem | Açıklama ve gerekçe | Tutar (TL) |
|---|---|---:|
| Bursiyer — Yüksek lisans öğrencisi (1 kişi, 12 ay × 6.000 TL) | İP1–İP5'te ayrıştırıcı, graf, erişim ve cevap üretimi kodunun geliştirilmesi ve lisans bursiyerlerinin günlük eşgüdümü; tez konusu projeyle ilişkili. Ücret karşılığı çalışmayan YL bursiyeri üst sınırı (22.500 TL/ay) altındadır. | 72.000 |
| Bursiyer — Lisans öğrencisi A (1 kişi, 6 ay × 6.000 TL) | İP1–İP2'de ayrıştırıcı birim testlerinin yazılması, atlanan belgelerin incelenmesi ve 100 sürümlük elle kontrol kayıtlarının tutulması (aylar 2–7). | 36.000 |
| Bursiyer — Lisans öğrencisi B (1 kişi, 3 ay × 6.000 TL) | İP3'te soru yazımı ve birinci bağımsız etiketleme (aylar 4–6). | 18.000 |
| Bursiyer — Lisans öğrencisi C (1 kişi, 3 ay × 6.000 TL) | İP3'te ikinci bağımsız etiketleme (B'den bağımsız; anlaşma ölçümü için) ve uyuşmazlık kayıtları; İP5'te uzman değerlendirmesi formlarının hazırlanması (aylar 5–7). | 18.000 |
| Seyahat — Yurt içi bilimsel toplantı | Sonuçların ulusal bir konferansta sunulması (saha çalışması dışı yurt içi seyahat üst sınırı). | 5.750 |
| **Toplam** | | **149.750** |

Aynı anda en fazla üç lisans bursiyeri görev alır (üst sınır dört). Lisans bursiyerleri Türkiye'de bir yükseköğretim kurumunun lisans programında kayıtlı olmalı ve ücret karşılığı çalışmamalıdır. Çapraz kodlayıcı ve 8–14 milyar parametreli açık BDM deneyleri kurumun mevcut GPU altyapısında yürütülür; makine-teçhizat, sarf malzemesi ve hizmet alımı talebi yoktur. Ücretli API kullanılmaz. Proje Teşvik İkramiyesi 1002-A'da ödenmemektedir.
