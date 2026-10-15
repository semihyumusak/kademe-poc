"""Mini değerlendirme seti: eval/yoksc_mini.jsonl (SPEC §4).

Sorular eval/adaylar.jsonl'deki şablon adaylarından seçilip elle doğal dile
yazılmıştır. Her soru için altın MADDELER ve sorgu tarihi elle belirlenir;
madde-sürüm kimlikleri bu maddelerin o tarihte (ve varsa giriş dönemine göre)
uygulanan sürümü olarak graftan çözülür ve dosyaya sabitlenir.

Uyarı (README'de de belirtilir): altın sürüm kimlikleri, B yapılandırmasının da
kullandığı sürüm zincirinden çözülür. Bu nedenle zamansal sorulardaki ölçüm,
"zincir doğruysa erişim onu kullanabiliyor mu?" sorusunu yanıtlar; zincirin
kendi doğruluğu 50 madde-sürümlük elle kontrol örneklemiyle ayrıca ölçülür.

  python -m kademe.eval.soru_seti
"""
from __future__ import annotations

import json
from datetime import date

from kademe.graph.model import KademeGraph
from kademe.parse.akademik import donem_tarihi
from kademe.paths import EVAL

BUGUN = "2026-10-01"
K = "kanun:2547"
LU = "yonetmelik:21510"
GC = "yonetmelik:13948"
AT = "yonetmelik:24672"
YD = "yonetmelik:21475"
EL = "yonetmelik:15287"
ELU = "yonetmelik:42791"
CAP, YAN, OE, HZ = "yonerge:etu-cap", "yonerge:etu-yandal", "yonerge:etu-ortak-egitim", "yonerge:etu-hazirlik"

# (id, tür, soru, tarih, giriş dönemi, altın maddeler, kaynak notu, çift id)
SORULAR: list[tuple] = [
    # ---------------------------------------------------------------- tek madde (10)
    ("T01", "tek_madde", "YÖK Lisansüstü Eğitim ve Öğretim Yönetmeliğine göre tezli yüksek lisans programının azami süresi ne kadardır?",
     BUGUN, None, [f"{LU}/m7"], "21510 m.7 Süre", None),
    ("T02", "tek_madde", "Yükseköğretim Kanununa göre devlet ve vakıf üniversitelerine rektör nasıl atanır?",
     BUGUN, None, [f"{K}/m13"], "2547 m.13 Rektör", None),
    ("T03", "tek_madde", "TOBB ETÜ'de son sınıf lisans öğrencilerine mezuniyet ek sınavı hakkı hangi koşullarda tanınır?",
     BUGUN, None, [f"{EL}/m33"], "15287 m.33", None),
    ("T04", "tek_madde", "TOBB ETÜ'de ortak eğitim toplam kaç dönemden oluşur ve her dönem kaç haftadır?",
     BUGUN, None, [f"{OE}/m5"], "Ortak Eğitim Yönergesi m.5", None),
    ("T05", "tek_madde", "Profesör kadrolarına atanabilmek için hangi şartlar aranır?",
     BUGUN, None, [f"{AT}/m12"], "24672 m.12", None),
    ("T06", "tek_madde", "TOBB ETÜ İngilizce hazırlık programında derslere devam zorunluluğu yüzde kaçtır?",
     BUGUN, None, [f"{HZ}/m7"], "Hazırlık Yönergesi m.7", None),
    ("T07", "tek_madde", "Yükseköğretim Kurulunun kanunda sayılan görevleri nelerdir?",
     BUGUN, None, [f"{K}/m7"], "2547 m.7", None),
    ("T08", "tek_madde", "TOBB ETÜ lisansüstü programlarında doktora yeterlik sınavı nasıl yapılır ve kaç kez girilebilir?",
     BUGUN, None, [f"{ELU}/m27"], "42791 m.27", None),
    ("T09", "tek_madde", "TOBB ETÜ'de yandal programına başvuru hangi dönemlerde ve hangi belgelerle yapılır?",
     BUGUN, None, [f"{YAN}/m5"], "Yandal Yönergesi m.5", None),
    ("T10", "tek_madde", "Yabancı uyruklu öğrencilerin yatay geçiş kontenjanı YÖK yönetmeliğinde nasıl düzenlenmiştir?",
     BUGUN, None, [f"{GC}/m15"], "13948 m.15", None),
    # ---------------------------------------------------------------- zamansal çiftler (8 çift = 16 kayıt)
    ("Z01a", "zamansal", "Yükseköğretim Kanununa göre öğretim üyeleri hangi unvanlardan oluşur?",
     "2017-03-01", None, [f"{K}/m3"], "2547 m.3; 7100 s. Kanunla (2018) yardımcı doçent yerine doktor öğretim üyesi", "Z01"),
    ("Z01b", "zamansal", "Yükseköğretim Kanununa göre öğretim üyeleri hangi unvanlardan oluşur?",
     "2022-06-01", None, [f"{K}/m3"], "2547 m.3", "Z01"),
    ("Z02a", "zamansal", "Doçentlik unvanı almak için hangi şartlar ve süreç öngörülmüştür?",
     "2013-05-01", None, [f"{K}/m24"], "2547 m.24; 7100 s. Kanunla (2018) değişti", "Z02"),
    ("Z02b", "zamansal", "Doçentlik unvanı almak için hangi şartlar ve süreç öngörülmüştür?",
     "2019-08-01", None, [f"{K}/m24"], "2547 m.24", "Z02"),
    ("Z03a", "zamansal", "Yükseköğretim kurumlarında öğrencilere verilebilecek disiplin cezaları ve bunları gerektiren eylemler nelerdir?",
     "2017-03-01", None, [f"{K}/m54"], "2547 m.54; 7437 s. Kanunla (2023) yeniden düzenlendi", "Z03"),
    ("Z03b", "zamansal", "Yükseköğretim kurumlarında öğrencilere verilebilecek disiplin cezaları ve bunları gerektiren eylemler nelerdir?",
     "2023-08-01", None, [f"{K}/m54"], "2547 m.54", "Z03"),
    ("Z04a", "zamansal", "Öğrencilerin azami öğrenim süreleri nedir ve bu süreler sonunda hangi haklar tanınır?",
     "2017-12-01", None, [f"{K}/m44"], "2547 m.44; 7243 s. Kanun değişikliği", "Z04"),
    ("Z04b", "zamansal", "Öğrencilerin azami öğrenim süreleri nedir ve bu süreler sonunda hangi haklar tanınır?",
     "2023-10-01", None, [f"{K}/m44"], "2547 m.44", "Z04"),
    ("Z05a", "zamansal", "Yurt dışındaki bir yükseköğretim kurumundan Türkiye'deki bir üniversiteye yatay geçiş şartları nelerdir?",
     "2022-05-01", None, [f"{GC}/m14"], "13948 m.14; RG 16/7/2023-32250 değişikliği", "Z05"),
    ("Z05b", "zamansal", "Yurt dışındaki bir yükseköğretim kurumundan Türkiye'deki bir üniversiteye yatay geçiş şartları nelerdir?",
     "2024-11-01", None, [f"{GC}/m14"], "13948 m.14", "Z05"),
    ("Z06a", "zamansal", "YÖK Lisansüstü Eğitim ve Öğretim Yönetmeliğine göre doktora programına başvuru ve kabul koşulları nelerdir?",
     "2023-03-01", None, [f"{LU}/m16"], "21510 m.16; RG 6/3/2026-33188 değişikliği", "Z06"),
    ("Z06b", "zamansal", "YÖK Lisansüstü Eğitim ve Öğretim Yönetmeliğine göre doktora programına başvuru ve kabul koşulları nelerdir?",
     "2026-06-01", None, [f"{LU}/m16"], "21510 m.16", "Z06"),
    ("Z07a", "zamansal", "Yükseköğretim kurumlarında araştırma görevlisi kadrolarına istihdam hangi esaslara göre yapılır?",
     "2021-10-01", None, [f"{K}/em38"], "2547 ek m.38; 7417 s. Kanunla (2022) değişti", "Z07"),
    ("Z07b", "zamansal", "Yükseköğretim kurumlarında araştırma görevlisi kadrolarına istihdam hangi esaslara göre yapılır?",
     "2024-08-01", None, [f"{K}/em38"], "2547 ek m.38", "Z07"),
    ("Z08a", "zamansal", "Yükseköğretim kurumlarında yabancı uyruklu öğretim elemanları hangi usulle çalıştırılır?",
     "2012-06-01", None, [f"{K}/m34"], "2547 m.34; 2016 KHK ve 2018 değişiklikleri", "Z08"),
    ("Z08b", "zamansal", "Yükseköğretim kurumlarında yabancı uyruklu öğretim elemanları hangi usulle çalıştırılır?",
     "2020-06-01", None, [f"{K}/m34"], "2547 m.34", "Z08"),
    # ---------------------------------------------------------------- hiyerarşi (8)
    ("H01", "hiyerarsi", "TOBB ETÜ'de çift anadal programına başvuru ve kabul koşulları nelerdir ve YÖK'ün çerçeve yönetmeliği çift anadal için hangi asgari şartları koyar?",
     BUGUN, None, [f"{CAP}/m5", f"{GC}/m16"], "ÇAP Yönergesi m.5 (katman 4) + 13948 m.16 (katman 2)", None),
    ("H02", "hiyerarsi", "TOBB ETÜ'de yandal programını tamamlayan öğrenciye ne verilir ve YÖK yönetmeliği yandal programlarını nasıl düzenler?",
     BUGUN, None, [f"{YAN}/m7", f"{GC}/m18"], "Yandal Yönergesi m.7 + 13948 m.18", None),
    ("H03", "hiyerarsi", "TOBB ETÜ İngilizce hazırlık programından kimler muaf olabilir ve YÖK'ün yabancı dil yönetmeliği yabancı dil yeterlilik ve seviye tespit sınavlarını nasıl düzenler?",
     BUGUN, None, [f"{HZ}/m6", f"{YD}/m6"], "Hazırlık Yönergesi m.6 + 21475 m.6", None),
    ("H04", "hiyerarsi", "TOBB ETÜ lisans programlarında azami öğrenim süresi nedir ve Yükseköğretim Kanunu azami süreleri nasıl belirler?",
     BUGUN, None, [f"{EL}/m9", f"{K}/m44"], "15287 m.9 (katman 3) + 2547 m.44 (katman 1)", None),
    ("H05", "hiyerarsi", "TOBB ETÜ'de ortak eğitim programı mezuniyet için zorunlu mudur ve lisans yönetmeliği ortak eğitim dönemlerini nasıl düzenler?",
     BUGUN, None, [f"{OE}/m9", f"{EL}/m38"], "Ortak Eğitim Yönergesi m.9 + 15287 m.38", None),
    ("H06", "hiyerarsi", "Doçent kadrolarına atanma şartı nedir ve Yükseköğretim Kanununda doçentlik unvanının alınması nasıl düzenlenmiştir?",
     BUGUN, None, [f"{AT}/m8", f"{K}/m24"], "24672 m.8 + 2547 m.24", None),
    ("H07", "hiyerarsi", "Öğretim dili Türkçe olan programlarda zorunlu yabancı dil dersleri nasıl verilir ve Kanun yabancı dil hazırlık eğitimini nasıl düzenler?",
     BUGUN, None, [f"{YD}/m7", f"{K}/m49"], "21475 m.7 + 2547 m.49", None),
    ("H08", "hiyerarsi", "TOBB ETÜ'de tezli yüksek lisans programının süresi nedir ve YÖK Lisansüstü Eğitim ve Öğretim Yönetmeliği bu süreyi nasıl belirler?",
     BUGUN, None, [f"{ELU}/m15", f"{LU}/m7"], "42791 m.15 + 21510 m.7 (aralarında DAYANAK kenarı yok)", None),
    # ---------------------------------------------------------------- intibak / geçici madde (4)
    ("I01", "intibak", "2011-2012 eğitim-öğretim yılından önce TOBB ETÜ'ye kayıt yaptırmış bir öğrenci için sınamalı ve başarısız öğrencilere ilişkin hükümler ne zaman uygulanmaya başlar?",
     "2012-03-01", "2010-2011 güz", [f"{EL}/gm1", f"{EL}/m32"], "15287 geçici m.1", None),
    ("I02", "intibak", "2022'de yurt dışındaki bir üniversiteye kayıt yaptırmış bir öğrenci 2024'te Türkiye'deki bir üniversiteye yatay geçiş yapmak isterse hangi hükümler uygulanır?",
     "2024-03-01", "2022-2023 güz", [f"{GC}/gm2", f"{GC}/m14"], "13948 geçici m.2 + m.14 (değişiklik öncesi sürüm)", None),
    ("I03", "intibak", "YÖK Lisansüstü Eğitim ve Öğretim Yönetmeliğinin 2019 değişikliğinden önce aynı anda birden fazla lisansüstü programa kayıtlı olan öğrenciler hakkında hangi hüküm uygulanır?",
     "2020-01-01", "2018-2019 güz", [f"{LU}/gm1", f"{LU}/m35"], "21510 geçici m.1", None),
    ("I04", "intibak", "Ortak Eğitim Yönergesi yürürlüğe girmeden önce çift anadal programına kayıtlı TOBB ETÜ öğrencileri üç ortak eğitim dönemini nasıl tamamlar?",
     "2017-01-01", "2015-2016 güz", [f"{OE}/gm1", f"{OE}/m10"], "Ortak Eğitim Yönergesi geçici m.1 + m.10", None),
    # ---------------------------------------------------------------- cevaplanamaz (4)
    ("C01", "cevaplanamaz", "TOBB ETÜ kampüsünde öğrenci otoparkı ücretleri nasıl belirlenir?", BUGUN, None, [], "korpusta karşılığı yok", None),
    ("C02", "cevaplanamaz", "Üniversite yemekhanesinde öğle yemeği fiyatı ne kadardır?", BUGUN, None, [], "korpusta karşılığı yok", None),
    ("C03", "cevaplanamaz", "Bir öğrenci kulübü kurmak için en az kaç üye gerekir?", BUGUN, None, [], "korpusta karşılığı yok (Öğrenci Konseyi/Etkinlikleri yönergeleri kapsam dışı)", None),
    ("C04", "cevaplanamaz", "Akademisyenlerin sosyal medya hesaplarında kurumsal logo kullanımına ilişkin kurallar nelerdir?", BUGUN, None, [], "korpusta karşılığı yok", None),
]


def build(kg: KademeGraph) -> list[dict]:
    rows = []
    for sid, tur, soru, tarih, giris, maddeler, notu, cift in SORULAR:
        t = date.fromisoformat(tarih)
        g = donem_tarihi(giris) if giris else None
        altin, eksik = [], []
        for m in maddeler:
            s = kg.applicable(m, t, g)
            if s is None or not s.get("metin_mevcut"):
                eksik.append(m)
            else:
                altin.append(s["id"])
        rows.append({
            "id": sid,
            "soru": soru,
            "itibariyle_tarih": tarih,
            "giris_donemi": giris,
            "altin_birimler": altin,
            "altin_maddeler": maddeler,
            "katman": sorted({kg.katman(m) for m in maddeler}),
            "tur": tur,
            "cift_id": cift,
            "kaynak_notu": notu + (f"; metni olmayan/yürürlükte olmayan: {eksik}" if eksik else ""),
            "dogrulama": {"yurutucu": None, "ogrenci": None},
        })
    return rows


def main() -> int:
    kg = KademeGraph.load()
    rows = build(kg)
    with (EVAL / "yoksc_mini.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter

    print(len(rows), "kayıt,", len({r["soru"] for r in rows}), "tekil soru;", dict(Counter(r["tur"] for r in rows)))
    for r in rows:
        if r["tur"] != "cevaplanamaz":
            print(f"  {r['id']:5} {r['itibariyle_tarih']} {r['altin_birimler']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
