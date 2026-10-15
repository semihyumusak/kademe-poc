"""Değişiklik notlarının (Değişik / Ek / Mülga / İptal) ve dipnotların ayrıştırılması.

Örnek kalıplar:
  (Değişik: 17/8/1983 - 2880/1 md.)
  (Değişik ikinci fıkra: 15/8/2017-KHK-694/44 md.; Aynen kabul: 1/2/2018-7078/41 md.)
  (Ek: 2/12/2016 - 6764/27 md.)
  (Mülga: 22/2/2018-7100/2 md.)
  (İptal alt bent: Anayasa Mahkemesinin 22/2/2024 tarihli ve E: 2023/78, K: 2024/55 sayılı Kararı ile)
  (Değişik:RG-12/10/2017-30208)        yönetmelik
  (Değişik ibare:RG-6/5/2020-31119)    yönetmelik
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

NOTE_RE = re.compile(
    r"\((?P<tur>Değişik|Ek|Mülga|İptal|Yeniden [Dd]üzenle\w*)(?P<kapsam>[^:()]{0,60}?)\s*:\s*"
    r"(?P<govde>(?:[^()]|\([^()]*\))*?)\)"
)
DATE_RE = re.compile(r"(?P<g>\d{1,2})\s*[/.]\s*(?P<a>\d{1,2})\s*[/.]\s*(?P<y>\d{4})")
KANUN_KAYNAK_RE = re.compile(
    r"\d{4}\s*[-–]\s*(?P<khk>KHK\s*[-/]?\s*)?(?P<no>\d{2,4})\s*/\s*(?P<md>\d+)\s*md"
)
RG_KAYNAK_RE = re.compile(r"RG\s*[-–]\s*\d{1,2}/\d{1,2}/\d{4}\s*[-–]\s*(?P<sayi>\d{4,5})")
FOOTNOTE_EVENT_RE = re.compile(
    r"^(?P<tarih>\d{1,2}/\d{1,2}/\d{4})\s+tarihli\s+ve\s+(?P<no>\d+)\s+sayılı\s+(?P<tip>Kanun|KHK|Cumhurbaşkanlığı)"
)

TUR_MAP = {"Değişik": "degistirme", "Ek": "ekleme", "Mülga": "mulga", "İptal": "iptal",
           "Yeniden düzenleme": "degistirme"}


@dataclass(frozen=True)
class Not:
    tur: str  # ekleme | degistirme | mulga | iptal
    kapsam: str  # "", "ikinci fıkra", "ibare" ...
    tarih: date | None
    kaynak: str  # "6764/27", "KHK-694/44", "RG-30208", "AYM E:2023/78 K:2024/55"
    kaynak_no: str | None  # değiştiren kanun/KHK numarası ya da RG sayısı
    ham: str
    aynen_kabul: str | None = None  # KHK'nin kanunlaşması (ör. "7078/41")

    @property
    def madde_duzeyi(self) -> bool:
        """Not tüm maddeye mi ilişkin (kapsam belirtilmemiş)?"""
        return not self.kapsam


def parse_date(s: str) -> date | None:
    m = DATE_RE.search(s)
    if not m:
        return None
    try:
        return date(int(m.group("y")), int(m.group("a")), int(m.group("g")))
    except ValueError:
        return None


def parse_notes(text: str) -> list[Not]:
    out = []
    for m in NOTE_RE.finditer(text):
        govde = m.group("govde")
        tur = TUR_MAP.get(m.group("tur"), "degistirme")
        kapsam = m.group("kapsam").strip()
        tarih = parse_date(govde)
        kaynak, kaynak_no, aynen = "", None, None
        parts = re.split(r";\s*Aynen kabul\s*:", govde)
        if len(parts) > 1:
            km = KANUN_KAYNAK_RE.search(parts[1])
            aynen = f"{km.group('no')}/{km.group('md')}" if km else parts[1].strip()
        km = KANUN_KAYNAK_RE.search(parts[0])
        rm = RG_KAYNAK_RE.search(parts[0])
        if tur == "iptal" or "Anayasa Mahkemesi" in govde:
            e = re.search(r"E\s*[.:]\s*(\d{4}/\d+)", govde)
            k = re.search(r"K\s*[.:]\s*(\d{4}/\d+)", govde)
            kaynak = "AYM" + (f" E:{e.group(1)}" if e else "") + (f" K:{k.group(1)}" if k else "")
        elif km:
            kaynak_no = km.group("no")
            kaynak = f"{'KHK-' if km.group('khk') else ''}{km.group('no')}/{km.group('md')}"
        elif rm:
            kaynak_no = rm.group("sayi")
            kaynak = f"RG-{rm.group('sayi')}"
        out.append(Not(tur=tur, kapsam=kapsam, tarih=tarih, kaynak=kaynak, kaynak_no=kaynak_no,
                       ham=m.group(0), aynen_kabul=aynen))
    return out


def strip_notes(text: str) -> str:
    return re.sub(r"\s{2,}", " ", NOTE_RE.sub(" ", text)).strip()


FOOTNOTE_REF_RE = re.compile(r"\[(\d{1,3})\]")


def footnote_event(text: str) -> Not | None:
    """Dipnotu (ör. "[104] 25/8/2016 tarihli ve 671 sayılı KHK'nin 27 nci maddesiyle ... değiştirilmiştir.")
    ibare düzeyinde bir değişiklik olayına çevirir."""
    m = FOOTNOTE_EVENT_RE.match(text)
    if not m:
        return None
    if not re.search(r"değiştirilmiş|eklenmiş|yürürlükten kaldırılmış|madde metninden çıkarılmış|iptal", text):
        return None
    tur = "degistirme"
    if "eklenmiş" in text and "değiştirilmiş" not in text:
        tur = "ekleme"
    elif "yürürlükten kaldırılmış" in text or "çıkarılmış" in text:
        tur = "mulga"
    md = re.search(r"(\d+)\s*(?:'?\s*(?:inci|ıncı|üncü|uncu|nci|ncı|ncü|ncu))\s+maddesiyle", text)
    no = m.group("no")
    pre = "KHK-" if m.group("tip") == "KHK" else ""
    return Not(tur=tur, kapsam="ibare (dipnot)", tarih=parse_date(m.group("tarih")),
               kaynak=f"{pre}{no}/{md.group(1) if md else '?'}", kaynak_no=no, ham=text[:300])
