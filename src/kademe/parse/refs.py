"""Atıf ve dayanak kalıplarının deterministik (regex) çıkarımı.

Desteklenen biçimler (örnekler):
  "2547 sayılı Yükseköğretim Kanununun 44 üncü maddesi"
  "Kanunun 7 nci, 14 üncü ve 44 üncü maddelerine"
  "bu Yönetmeliğin 12 nci maddesinin ikinci fıkrası"
  "Lisansüstü Eğitim ve Öğretim Yönetmeliğinin 9 uncu maddesi"
  "geçici 2 nci madde", "ek 18 inci maddesi"
  "44 üncü maddede belirtilen" (niteleyicisiz: aynı norm)
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from kademe.parse.text import tr_lower

SUFFIX = r"(?:\s*'?\s*(?:inci|ıncı|üncü|uncu|nci|ncı|ncü|ncu|ünci|uncü))"
NUM = rf"(?:(?:[Ee]k|[Gg]eçici)\s+)?\d+(?:\s*/\s*[A-ZÇĞİÖŞÜ])?{SUFFIX}?"
LIST = rf"{NUM}(?:\s*(?:,|\bve\b|\bile\b|\bila\b)\s*{NUM})*"
MADDE_W = r"madde(?:si|leri|sine|lerine|sinde|lerinde|sinin|lerinin|siyle|leriyle|sindeki|lerindeki|ye|de|den|deki|nin|ler)?\b"
QUAL = (
    r"(?P<q>(?:[Bb]u|[İi]şbu)\s+(?:Kanun|Yönetmeli|Yönerge|Esas|Usul)\w*"
    r"|(?P<sayi>\d{3,4})\s+sayılı\s+(?:[A-ZÇĞİÖŞÜ][\w-]*\s+){0,8}?(?:Kanun|KHK|Kararname)\w*(?:'\w+)?"
    r"|(?:Kanun|Yönetmeli|Yönerge|Esaslar)\w*(?:'\w+)?)\s+"
)
REF_RE = re.compile(
    rf"(?:{QUAL})?(?P<list>{LIST})\s+{MADDE_W}"
    rf"(?:\s*(?:nin|in)?\s*(?P<fikra>birinci|ikinci|üçüncü|dördüncü|beşinci|altıncı|yedinci|sekizinci|dokuzuncu|onuncu"
    rf"|\(\d+\)\s*numaralı)\s+fıkra\w*)?"
    rf"(?:\s*(?:nın|nin)?\s*\((?P<bent>[a-zçğıöşü])\)\s*bend\w*)?"
)
ITEM_RE = re.compile(rf"(?P<pre>[Ee]k|[Gg]eçici)?\s*(?P<no>\d+)(?:\s*/\s*(?P<harf>[A-ZÇĞİÖŞÜ]))?")
ORDINALS = {"birinci": 1, "ikinci": 2, "üçüncü": 3, "dördüncü": 4, "beşinci": 5, "altıncı": 6, "yedinci": 7,
            "sekizinci": 8, "dokuzuncu": 9, "onuncu": 10}
DAYANAK_RE = re.compile(r"dayanılarak|dayanak", re.I)


@dataclass(frozen=True)
class Ref:
    hedef_norm: str | None  # korpus norm id'si; çözülemezse None
    madde: str  # madde anahtarı (m44, em18, gm2)
    fikra: int | None
    bent: str | None
    metin: str
    cozum: str  # oz | acik | ad | cikarim | dis
    dis_kanun: str | None = None  # korpus dışı kanun numarası


@dataclass(frozen=True)
class NormAlias:
    norm_id: str
    kanun_no: str | None
    adlar: tuple[str, ...]  # tr_lower biçiminde ayırt edici ad parçaları


def _items(list_text: str) -> list[str]:
    keys = []
    prefix = ""
    for m in ITEM_RE.finditer(list_text):
        if m.group("pre"):
            prefix = "gm" if m.group("pre").lower().startswith("g") else "em"
        keys.append(f"{prefix or 'm'}{m.group('no')}{m.group('harf') or ''}")
    return keys


def _fikra_no(s: str | None) -> int | None:
    if not s:
        return None
    m = re.search(r"\((\d+)\)", s)
    return int(m.group(1)) if m else ORDINALS.get(s.split()[0])


def resolve_alias(context: str, aliases: list[NormAlias]) -> str | None:
    ctx = tr_lower(context)
    best, pos = None, -1
    for a in aliases:
        for ad in a.adlar:
            i = ctx.rfind(ad)
            if i > pos:
                best, pos = a.norm_id, i
    return best


def extract_refs(
    text: str,
    *,
    self_norm: str,
    self_tur: str,
    aliases: list[NormAlias],
    varsayilan_kanun: str | None = None,
) -> list[Ref]:
    """Bir madde metnindeki atıfları çıkarır.

    varsayilan_kanun: yönetmelik/yönergelerde niteleyicisiz "Kanunun N inci maddesi"
    ifadesinin bağlanacağı kanun (dayanak zincirinden çıkarılır).
    """
    by_no = {a.kanun_no: a.norm_id for a in aliases if a.kanun_no}
    out: list[Ref] = []
    onceki: tuple[int, str | None, str, str | None] | None = None  # (bitiş, hedef, çözüm, dış)
    for m in REF_RE.finditer(text):
        q = m.group("q")
        # "Kanununun 7 nci maddesinin (e) bendine ve 44 üncü maddesinin ..." : niteleyici devralınır.
        if q is None and onceki is not None:
            ara = text[onceki[0]:m.start()]
            if len(ara) <= 80 and re.fullmatch(r"[\w\s(),'-]*?(?:,|\bve\b|\bile\b)\s*", ara) \
                    and not re.search(r"\b(?:bu|işbu)\b", ara, re.I):
                keys = _items(m.group("list"))
                fikra = _fikra_no(m.group("fikra")) if len(keys) == 1 else None
                bent = m.group("bent") if len(keys) == 1 else None
                for k in keys:
                    out.append(Ref(hedef_norm=onceki[1], madde=k, fikra=fikra, bent=bent, metin=m.group(0).strip(),
                                   cozum=onceki[2], dis_kanun=onceki[3]))
                onceki = (m.end(), onceki[1], onceki[2], onceki[3])
                continue
        keys = _items(m.group("list"))
        if not keys:
            continue
        # Sayı tek başına ve sıra eki yoksa ("5 madde") gerçek atıf değildir.
        if not re.search(SUFFIX, m.group("list")) and not q:
            continue
        hedef, cozum, dis = None, "", None
        if q is None:
            hedef, cozum = self_norm, "oz"
        elif re.match(r"(?:[Bb]u|[İi]şbu)\s", q):
            hedef, cozum = self_norm, "oz"
        elif m.group("sayi"):
            no = m.group("sayi")
            if no in by_no:
                hedef, cozum = by_no[no], "acik"
            else:
                cozum, dis = "dis", no
        elif q.lower().startswith("kanun"):
            if self_tur == "kanun":
                # "Kanunun" önünde bir kanun adı yoksa çoğunlukla aynı kanundur; en yakın sayıyı ara.
                prev = re.findall(r"(\d{3,4})\s+sayılı", text[max(0, m.start() - 200):m.start()])
                if prev:
                    no = prev[-1]
                    hedef, cozum, dis = (by_no[no], "acik", None) if no in by_no else (None, "dis", no)
                else:
                    hedef, cozum = self_norm, "cikarim"
            else:
                prev = re.findall(r"(\d{3,4})\s+sayılı", text[:m.start()])
                if prev:
                    no = prev[-1]
                    hedef, cozum, dis = (by_no[no], "acik", None) if no in by_no else (None, "dis", no)
                elif varsayilan_kanun:
                    hedef, cozum = varsayilan_kanun, "cikarim"
        else:
            hedef = resolve_alias(text[max(0, m.start() - 250):m.end()], aliases)
            cozum = "ad" if hedef else ""
        if not cozum:
            continue
        fikra = _fikra_no(m.group("fikra")) if len(keys) == 1 else None
        bent = m.group("bent") if len(keys) == 1 else None
        for k in keys:
            out.append(Ref(hedef_norm=hedef, madde=k, fikra=fikra, bent=bent, metin=m.group(0).strip(),
                           cozum=cozum, dis_kanun=dis))
        onceki = (m.end(), hedef, cozum, dis) if cozum != "oz" else None
    return out


def is_dayanak_madde(baslik: str | None, metin: str) -> bool:
    if baslik and "dayanak" in tr_lower(baslik):
        return True
    return bool(re.search(r"dayanılarak\s+hazırlan", metin))


def dayanak_norm_mentions(text: str, aliases: list[NormAlias], self_norm: str) -> list[str]:
    """Madde numarası verilmeden dayanak gösterilen normlar (ör. "... Yönetmeliğine dayanılarak")."""
    ctx = tr_lower(text)
    found = []
    for a in aliases:
        if a.norm_id == self_norm:
            continue
        if any(ad in ctx for ad in a.adlar) or (a.kanun_no and re.search(rf"\b{a.kanun_no}\s+sayılı", text)):
            found.append(a.norm_id)
    return found
