"""Külliyat tanımı: dört katmandan PoC'ye alınan normlar ve kaynakları.

Kapsam bilinçli olarak dardır (bkz. SPEC.md §1). Her norm için güncel metnin
kaynağı ve (varsa) tarihsel anlık görüntülerin aranacağı URL kalıpları verilir.
"""
from __future__ import annotations

from dataclasses import dataclass, field

MEVZUAT = "https://www.mevzuat.gov.tr"
ETU = "https://www.etu.edu.tr"


@dataclass(frozen=True)
class NormSpec:
    id: str
    ad: str
    tur: str  # kanun | yonetmelik | yonerge | usul_esas
    katman: int  # 1-4
    kurum: str
    rg_tarih: str | None  # ISO tarih (ilk yayım)
    rg_sayi: str | None
    uygulanabilirlik: str  # devlet | vakif | hepsi
    kaynak: str  # mevzuat | etu
    url: str  # güncel metin
    mevzuat_kod: str | None = None  # "tur.tertip.no" (mevzuat.gov.tr)
    dosya_turu: str = "html"  # html | pdf | docx
    notlar: str = ""
    wayback_kaliplari: tuple[str, ...] = field(default_factory=tuple)

    @property
    def raw_name(self) -> str:
        return self.id.replace(":", "_")


def _mevzuat(tur: int, no: int) -> str:
    return f"{MEVZUAT}/anasayfa/MevzuatFihristDetayIframe?MevzuatTur={tur}&MevzuatNo={no}&MevzuatTertip=5"


def _wb(tur: int, no: int) -> tuple[str, ...]:
    # Eski ikili .doc kopyaları taşınabilir biçimde okunamadığından yalnızca PDF ve HTML alınır.
    kod = f"{tur}.5.{no}"
    pdf = f"www.mevzuat.gov.tr/MevzuatMetin/{kod}.pdf" if tur == 1 else f"www.mevzuat.gov.tr/MevzuatMetin/yonetmelik/{kod}.pdf"
    return (pdf, f"www.mevzuat.gov.tr/Metin.Aspx?MevzuatKod={kod}*")


NORMS: tuple[NormSpec, ...] = (
    # Katman 1
    NormSpec(
        id="kanun:2547", ad="Yükseköğretim Kanunu", tur="kanun", katman=1, kurum="TBMM",
        rg_tarih="1981-11-06", rg_sayi="17506", uygulanabilirlik="hepsi", kaynak="mevzuat",
        url=_mevzuat(1, 2547), mevzuat_kod="1.5.2547", wayback_kaliplari=_wb(1, 2547),
    ),
    # Katman 2: YÖK yönetmelikleri
    NormSpec(
        id="yonetmelik:21510", ad="Lisansüstü Eğitim ve Öğretim Yönetmeliği", tur="yonetmelik", katman=2,
        kurum="YÖK", rg_tarih="2016-04-20", rg_sayi="29690", uygulanabilirlik="hepsi", kaynak="mevzuat",
        url=_mevzuat(7, 21510), mevzuat_kod="7.5.21510", wayback_kaliplari=_wb(7, 21510),
    ),
    NormSpec(
        id="yonetmelik:13948",
        ad="Yükseköğretim Kurumlarında Önlisans ve Lisans Düzeyindeki Programlar Arasında Geçiş, Çift Anadal, "
           "Yan Dal ile Kurumlar Arası Kredi Transferi Yapılması Esaslarına İlişkin Yönetmelik",
        tur="yonetmelik", katman=2, kurum="YÖK", rg_tarih="2010-04-24", rg_sayi="27561", uygulanabilirlik="hepsi",
        kaynak="mevzuat", url=_mevzuat(7, 13948), mevzuat_kod="7.5.13948", wayback_kaliplari=_wb(7, 13948),
    ),
    NormSpec(
        id="yonetmelik:24672", ad="Öğretim Üyeliğine Yükseltilme ve Atanma Yönetmeliği", tur="yonetmelik", katman=2,
        kurum="YÖK", rg_tarih="2018-06-12", rg_sayi="30449", uygulanabilirlik="hepsi", kaynak="mevzuat",
        url=_mevzuat(7, 24672), mevzuat_kod="7.5.24672", wayback_kaliplari=_wb(7, 24672),
    ),
    NormSpec(
        id="yonetmelik:21475",
        ad="Yükseköğretim Kurumlarında Yabancı Dil Öğretimi ve Yabancı Dille Öğretim Yapılmasında "
           "Uyulacak Esaslara İlişkin Yönetmelik",
        tur="yonetmelik", katman=2, kurum="YÖK", rg_tarih="2016-03-23", rg_sayi="29662", uygulanabilirlik="hepsi",
        kaynak="mevzuat", url=_mevzuat(7, 21475), mevzuat_kod="7.5.21475", wayback_kaliplari=_wb(7, 21475),
        notlar="SPEC'teki Öğrenci Disiplin Yönetmeliği mevzuat.gov.tr yürürlükteki mevzuat aramasında bulunamadı "
               "(disiplin hükümleri 7437 s. Kanunla 2547 m.54'e alındı); yerine katman 4'teki hazırlık yönergesinin "
               "dayanağı olan bu yönetmelik alındı.",
    ),
    # Katman 3: TOBB ETÜ yönetmelikleri
    NormSpec(
        id="yonetmelik:15287", ad="TOBB Ekonomi ve Teknoloji Üniversitesi Lisans Eğitim-Öğretim ve Sınav Yönetmeliği",
        tur="yonetmelik", katman=3, kurum="TOBB ETÜ", rg_tarih="2011-09-12", rg_sayi="28052",
        uygulanabilirlik="vakif", kaynak="mevzuat", url=_mevzuat(8, 15287), mevzuat_kod="8.5.15287",
        wayback_kaliplari=_wb(8, 15287),
    ),
    NormSpec(
        id="yonetmelik:42791", ad="TOBB Ekonomi ve Teknoloji Üniversitesi Lisansüstü Eğitim-Öğretim Yönetmeliği",
        tur="yonetmelik", katman=3, kurum="TOBB ETÜ", rg_tarih="2025-12-21", rg_sayi="33114",
        uygulanabilirlik="vakif", kaynak="mevzuat", url=_mevzuat(8, 42791), mevzuat_kod="8.5.42791",
        wayback_kaliplari=_wb(8, 42791),
    ),
    # Katman 4: TOBB ETÜ senato yönergeleri ve esasları
    NormSpec(
        id="yonerge:etu-cap", ad="TOBB ETÜ Çift Anadal Programı Yönergesi", tur="yonerge", katman=4,
        kurum="TOBB ETÜ Senatosu", rg_tarih=None, rg_sayi=None, uygulanabilirlik="vakif", kaynak="etu",
        url=f"{ETU}/files/dosyalar/2024/01/29/eb43dcd9a0d834026a02e9da7ecf1539.pdf", dosya_turu="pdf",
    ),
    NormSpec(
        id="yonerge:etu-yandal", ad="TOBB ETÜ Yandal Programı Yönergesi", tur="yonerge", katman=4,
        kurum="TOBB ETÜ Senatosu", rg_tarih=None, rg_sayi=None, uygulanabilirlik="vakif", kaynak="etu",
        url=f"{ETU}/files/dosyalar/2017/07/13/ab1a55e4a6eb099986f4834fc8bb7e3a.pdf", dosya_turu="pdf",
    ),
    NormSpec(
        id="usul_esas:etu-yatay-gecis", ad="TOBB ETÜ Yatay Geçiş Esasları", tur="usul_esas", katman=4,
        kurum="TOBB ETÜ Senatosu", rg_tarih=None, rg_sayi=None, uygulanabilirlik="vakif", kaynak="etu",
        url=f"{ETU}/files/dosyalar/2024/01/29/558f2c5efbd7a6c311e1452fab5624c7.pdf", dosya_turu="pdf",
    ),
    NormSpec(
        id="yonerge:etu-ortak-egitim", ad="TOBB ETÜ Ortak Eğitim Yönergesi", tur="yonerge", katman=4,
        kurum="TOBB ETÜ Senatosu", rg_tarih=None, rg_sayi=None, uygulanabilirlik="vakif", kaynak="etu",
        url=f"{ETU}/files/dosyalar/2026/04/10/e472b6276fe3c0cb3c126a74a668b4a2.docx", dosya_turu="docx",
    ),
    NormSpec(
        id="yonerge:etu-hazirlik", ad="TOBB ETÜ İngilizce Hazırlık Programı Eğitim-Öğretim Esaslarına İlişkin Yönerge",
        tur="yonerge", katman=4, kurum="TOBB ETÜ Senatosu", rg_tarih=None, rg_sayi=None, uygulanabilirlik="vakif",
        kaynak="etu", url=f"{ETU}/files/dosyalar/2026/07/21/ffa917c0d1363d027fb323dfb3c8c47e.docx",
        dosya_turu="docx",
    ),
)

NORM_BY_ID = {n.id: n for n in NORMS}
