"""Ayrıştırıcı birim testleri: sürüm zinciri, dayanak, atıf ve yardımcılar.

Testler ağ erişimi ya da ham veri gerektirmez; gerçek mevzuat metinlerinden
kısaltılmış örnekler kullanır.
"""
from datetime import date

from kademe.parse.akademik import akademik_tarih, donem_tarihi
from kademe.parse.notes import footnote_event, parse_notes, strip_notes
from kademe.parse.refs import NormAlias, dayanak_norm_mentions, extract_refs, is_dayanak_madde
from kademe.parse.structure import parse_paragraphs
from kademe.parse.text import fingerprint
from kademe.parse.versions import Gozlem, baslik_notlari, build_chain, temizle
from kademe.parse.yururluk import parse_madde_listesi, yururluk_tarihi

ALIASES = [
    NormAlias("kanun:2547", "2547", ("yükseköğretim kanunu",)),
    NormAlias("yonetmelik:13948", None, ("programlar arasında geçiş, çift anadal, yan dal",)),
    NormAlias("yonetmelik:15287", None, ("lisans eğitim-öğretim ve sınav yönetmeliğ",)),
]


def _etkin(n):
    return n.tarih, "not"


# ------------------------------------------------------------------ değişiklik notları

def test_kanun_notu_tarih_ve_kaynak():
    ns = parse_notes("Madde 44 – (Değişik: 13/2/2011-6111/171 md.) a. Yükseköğretim kurumlarının ...")
    assert len(ns) == 1
    n = ns[0]
    assert (n.tur, n.tarih, n.kaynak, n.kaynak_no) == ("degistirme", date(2011, 2, 13), "6111/171", "6111")


def test_khk_aynen_kabul_ve_kapsam():
    n = parse_notes("(Değişik ikinci fıkra: 15/8/2017-KHK-694/44 md.; Aynen kabul: 1/2/2018-7078/41 md.) Milli")[0]
    assert n.kapsam == "ikinci fıkra"
    assert n.kaynak == "KHK-694/44" and n.kaynak_no == "694"
    assert n.aynen_kabul == "7078/41"


def test_yonetmelik_rg_notu_ve_aym_iptali():
    n = parse_notes("(1) (Değişik:RG-9/6/2017- 30091) Aynı yükseköğretim kurumunda")[0]
    assert n.tarih == date(2017, 6, 9) and n.kaynak == "RG-30091"
    iptal = parse_notes("3) (İptal alt bent: Anayasa Mahkemesinin 22/2/2024 tarihli ve E: 2023/78, K: 2024/55 "
                        "sayılı Kararı ile)")[0]
    assert iptal.tur == "iptal" and iptal.kapsam == "alt bent"
    assert iptal.kaynak == "AYM E:2023/78 K:2024/55"
    assert strip_notes("a) (Mülga: 22/2/2018-7100/2 md.) metin") == "a) metin"


def test_dipnot_ibare_degisikligi():
    n = footnote_event("25/8/2016 tarihli ve 671 sayılı KHK'nin 27 nci maddesiyle, bu maddenin ikinci fıkrasında "
                       "yer alan \"yetmişiki\" ibaresi \"yetmişbeş\" şeklinde değiştirilmiştir.")
    assert n is not None and n.tarih == date(2016, 8, 25) and n.kaynak == "KHK-671/27"


# ------------------------------------------------------------------ yapı

def test_madde_fikra_bent_yonetmelik():
    paras = [
        "LİSANSÜSTÜ EĞİTİM VE ÖĞRETİM YÖNETMELİĞİ",
        "Amaç ve kapsam",
        "MADDE 1 – (1) Bu Yönetmeliğin amacı; lisansüstü eğitimi düzenlemektir.",
        "Dayanak",
        "MADDE 2 – (1) Bu Yönetmelik 2547 sayılı Yükseköğretim Kanununun 44 üncü maddesine dayanılarak hazırlanmıştır.",
        "Tanımlar",
        "MADDE 3 – (1) Bu Yönetmelikte geçen;",
        "a) ALES: Akademik Personel ve Lisansüstü Eğitimi Giriş Sınavını,",
        "b) Senato: Yükseköğretim kurumunun senatosunu,",
        "(2) İkinci fıkra.",
        "GEÇİCİ MADDE 1 – (1) Geçiş hükmü.",
    ]
    d = parse_paragraphs(paras)
    assert [m.key for m in d.maddeler] == ["m1", "m2", "m3", "gm1"]
    m3 = d.maddeler[2]
    assert m3.baslik == "Tanımlar"
    assert [f.no for f in m3.fikralar] == [1, 2]
    assert [b.no for b in m3.fikralar[0].bentler] == ["a", "b"]
    assert d.maddeler[1].baslik == "Dayanak"


def test_kanun_numarasiz_fikra_ve_ek_madde():
    paras = [
        "Kapsam:",
        "Madde 2 – Bu kanun; yükseköğretim üst kuruluşlarını kapsar.",
        "(Değişik ikinci fıkra: 15/8/2017-KHK-694/44 md.) Özel kanun hükümleri saklıdır.",
        "Ek Madde 18 – (Ek: 26/6/2001 - 4702/9 md.) Vakıf yükseköğretim kurumları ...",
        "Madde 53/A – (Ek: 2/12/2016 - 6764/27 md.) Disiplin soruşturmasında uyulacak esaslar:",
    ]
    d = parse_paragraphs(paras)
    assert [m.key for m in d.maddeler] == ["m2", "em18", "m53A"]
    assert d.maddeler[0].baslik == "Kapsam"
    assert len(d.maddeler[0].fikralar) == 2


# ------------------------------------------------------------------ atıf ve dayanak

def test_atif_kanun_sayili_ve_liste():
    rs = extract_refs("Bu Yönetmelik, 2547 sayılı Yükseköğretim Kanununun 7 nci maddesinin birinci fıkrasının (e) "
                      "bendine ve 44 üncü maddesinin (c) fıkrasına dayanılarak hazırlanmıştır.",
                      self_norm="yonetmelik:13948", self_tur="yonetmelik", aliases=ALIASES)
    assert [(r.hedef_norm, r.madde) for r in rs] == [("kanun:2547", "m7"), ("kanun:2547", "m44")]
    assert rs[0].fikra == 1 and rs[0].bent == "e"


def test_atif_oz_ek_gecici_ve_dis_kanun():
    rs = extract_refs("bu Kanunun 36 ncı maddesinde belirtilen; ek 18 inci madde ile geçici 2 nci maddede; "
                      "2914 sayılı Kanunun 11 inci maddesindeki", self_norm="kanun:2547", self_tur="kanun",
                      aliases=ALIASES)
    got = {(r.hedef_norm, r.madde, r.cozum) for r in rs}
    assert ("kanun:2547", "m36", "oz") in got
    assert ("kanun:2547", "em18", "oz") in got
    assert ("kanun:2547", "gm2", "oz") in got
    assert any(r.dis_kanun == "2914" and r.hedef_norm is None for r in rs)


def test_dayanak_ad_ile_ve_kesme_isareti():
    metin = ("Bu Yönerge, Yükseköğretim Kurulunun, Yükseköğretim Kurumlarında Önlisans ve Lisans Düzeyindeki "
             "Programlar Arasında Geçiş, Çift Anadal, Yan Dal ile Kurumlar Arası Kredi Transferi Yapılması "
             "Esaslarına İlişkin Yönetmeliği ile TOBB Ekonomi ve Teknoloji Üniversitesi Lisans Eğitim-Öğretim ve "
             "Sınav Yönetmeliğine dayanılarak hazırlanmıştır.")
    assert is_dayanak_madde(None, metin)
    assert set(dayanak_norm_mentions(metin, ALIASES, "yonerge:etu-cap")) == {"yonetmelik:13948", "yonetmelik:15287"}
    rs = extract_refs("2547 sayılı Yükseköğretim Kanunu'nun Ek 23 üncü maddesine", self_norm="yonerge:x",
                      self_tur="yonerge", aliases=ALIASES)
    assert [(r.hedef_norm, r.madde) for r in rs] == [("kanun:2547", "em23")]


# ------------------------------------------------------------------ sürüm zinciri

def test_surum_zinciri_notlardan_ve_yer_tutuculardan():
    eski = "Madde 3 – (Değişik: 17/8/1983 - 2880/1 md.) m) Öğretim üyeleri: profesör, doçent ve yardımcı doçentlerdir."
    yeni = ("Madde 3 – (Değişik: 17/8/1983 - 2880/1 md.) m) (Değişik: 22/2/2018-7100/2 md.) Öğretim üyeleri: "
            "profesör, doçent ve doktor öğretim üyeleridir.")
    zincir = build_chain(
        [Gozlem(date(2012, 11, 19), eski, "wayback:1"), Gozlem(date(2026, 10, 15), yeni, "guncel")],
        dogum=date(1981, 11, 6), etkin_tarih=_etkin)
    bas = [(s.baslangic, s.metin_mevcut) for s in zincir]
    assert bas == [(date(1981, 11, 6), False), (date(1983, 8, 17), True), (date(2018, 2, 22), True)]
    assert zincir[1].bitis == date(2018, 2, 22) and zincir[-1].bitis is None


def test_surum_zinciri_pdf_gurultusunu_birlestirir():
    a = "Madde 5 – (Değişik: 3/4/1991 - 3708/2 md.) Yükseköğretim ana ilkelere göre planlanır."
    b = ("Madde 5 – (Değişik: 3/4/1991 - 3708/2 md.) Yükseköğretim ana ilkelere göre plan lanır. "
         "22/2/2018 tarihli ve 7100 sayılı Kanunun 11 inci maddesiyle")
    zincir = build_chain([Gozlem(date(2013, 1, 1), a, "wayback:1"), Gozlem(date(2014, 1, 1), temizle(b), "wayback:2")],
                         dogum=date(1981, 11, 6), etkin_tarih=_etkin)
    assert sum(1 for s in zincir if s.metin_mevcut) == 1


def test_mulga_madde_ve_ek_madde_dogumu():
    zincir = build_chain(
        [Gozlem(date(2019, 1, 1), "Ek Madde 18 – (Ek: 26/6/2001 - 4702/9 md.) Vakıf kurumları ...", "wayback:1"),
         Gozlem(date(2026, 1, 1), "Ek Madde 18 – (Ek: 26/6/2001 - 4702/9 md.) (Mülga: 15/4/2020-7243/14 md.)",
                "guncel")],
        dogum=date(1981, 11, 6), etkin_tarih=_etkin)
    assert zincir[0].baslangic == date(2001, 6, 26)  # Ek madde: norm yürürlüğünden değil, ekleniş tarihinden
    assert zincir[-1].durum == "mulga" and zincir[-1].baslangic == date(2020, 4, 15)
    assert [n.tur for n in baslik_notlari("Madde 2 – (1) (Ek:RG-1/1/2020-1) metin")] == []


# ------------------------------------------------------------------ yardımcılar

def test_yururluk_tablosu_ve_akademik_takvim():
    assert parse_madde_listesi("3, 7, Ek Madde 2, Geçici Madde 52, 53 ve 54") == frozenset(
        {"m3", "m7", "em2", "gm52", "gm53", "gm54"})
    tablo = {"6764": [(frozenset({"m53A", "m45"}), date(2016, 12, 9))]}
    assert yururluk_tarihi(tablo, "6764", "m53A", date(2016, 12, 2)) == (date(2016, 12, 9), True)
    assert yururluk_tarihi(tablo, "9999", "m1", date(2000, 1, 1)) == (date(2000, 1, 1), False)
    assert akademik_tarih("Bu değişiklik 2019-2020 eğitim-öğretim yılı bahar döneminden itibaren") == date(2020, 2, 1)
    assert donem_tarihi("2022-2023 güz") == date(2022, 9, 1)


def test_parmak_izi_bicimden_bagimsiz():
    assert fingerprint("Ön Lisa n s: Or t a ö ğr e t im") == fingerprint("Ön Lisans: Ortaöğretim")
    assert fingerprint("madde [12] metni (3)") == fingerprint("madde metni")
