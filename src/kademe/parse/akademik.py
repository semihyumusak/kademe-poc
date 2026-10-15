"""Akademik takvim ifadelerini tarihe çevirme.

Uzlaşım (SPEC dışı, PoC kararı): eğitim-öğretim yılı/güz dönemi 1 Eylül,
bahar dönemi 1 Şubat, yaz dönemi 15 Haziran'da başlar kabul edilir.
"""
from __future__ import annotations

import re
from datetime import date

AY_RE = re.compile(
    r"(?P<y1>\d{4})\s*[-–]\s*(?P<y2>\d{4})\s+(?:eğitim|öğretim)[\s-]*(?:öğretim\s+)?(?:yılı|dönemi)?"
    r"(?P<tail>[^.;]{0,40})",
    re.I,
)


def akademik_tarih(text: str) -> date | None:
    m = AY_RE.search(text)
    if not m:
        return None
    y1 = int(m.group("y1"))
    tail = m.group("tail").lower()
    if "bahar" in tail:
        return date(y1 + 1, 2, 1)
    if "yaz" in tail:
        return date(y1 + 1, 6, 15)
    return date(y1, 9, 1)


def donem_tarihi(giris_donemi: str) -> date:
    """"2019-2020 güz" -> 2019-09-01 (değerlendirme setindeki giriş dönemi alanı)."""
    d = akademik_tarih(giris_donemi.replace("güz", "eğitim-öğretim yılı güz").replace(
        "bahar", "eğitim-öğretim yılı bahar"))
    if d is None:
        raise ValueError(f"giriş dönemi çözümlenemedi: {giris_donemi}")
    return d
