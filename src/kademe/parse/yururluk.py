"""Kanun metninin sonundaki "... YÜRÜRLÜĞE GİRİŞ TARİHİNİ GÖSTERİR LİSTE" tablosu.

Değişiklik notlarındaki tarih değiştiren kanunun kabul tarihidir; yürürlük
tarihi çoğunlukla birkaç gün sonradır, bazen yıllar sonradır. Bu tablo
(değiştiren kanun no, etkilenen maddeler) -> yürürlük tarihi eşlemesini verir.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

from kademe.parse.notes import parse_date
from kademe.parse.text import clean

YururlukTablosu = dict[str, list[tuple[frozenset[str] | None, date]]]


def parse_madde_listesi(s: str) -> frozenset[str] | None:
    """"3, 7, Ek Madde 2, Geçici Madde 52, 53 ve 54" -> {m3, m7, em2, gm52, gm53, gm54}."""
    s = clean(s)
    if not s or re.search(r"[Dd]iğer|[Tt]ümü|Yayımı", s):
        return None
    keys: set[str] = set()
    prefix = "m"
    for tok in re.split(r",|\bve\b|\bile\b", s):
        tok = tok.strip()
        if not tok:
            continue
        if re.search(r"Geçici", tok, re.I):
            prefix = "gm"
        elif re.search(r"\bEk\b", tok, re.I):
            prefix = "em"
        m = re.search(r"(\d+)\s*(?:/\s*([A-ZÇĞİÖŞÜ]))?", tok)
        if m:
            keys.add(f"{prefix}{m.group(1)}{m.group(2) or ''}")
    return frozenset(keys) or None


def parse_table(path: Path) -> YururlukTablosu:
    soup = BeautifulSoup(path.read_bytes().decode("utf-8", "replace"), "lxml")
    out: YururlukTablosu = {}
    for tr in soup.find_all("tr"):
        cells = [clean(td.get_text(" ")) for td in tr.find_all("td")]
        if len(cells) != 3:
            continue
        no_cell, maddeler, tarih_s = cells
        m = re.search(r"(KHK\s*/?\s*)?(\d{3,4})", no_cell)
        d = parse_date(tarih_s)
        if not m or d is None:
            continue
        out.setdefault(m.group(2), []).append((parse_madde_listesi(maddeler), d))
    return out


def yururluk_tarihi(tablo: YururlukTablosu, kaynak_no: str | None, madde_key: str, varsayilan: date | None) -> tuple[date | None, bool]:
    """(tarih, tablodan_mi) döndürür. Tabloda yoksa not tarihini (varsayılan) kullanır."""
    if not kaynak_no or kaynak_no not in tablo:
        return varsayilan, False
    base = re.sub(r"-\d+$", "", madde_key)
    rows = tablo[kaynak_no]
    for keys, d in rows:
        if keys is not None and base in keys:
            return d, True
    for keys, d in rows:
        if keys is None:
            return d, True
    # Tabloda kanun var ama bu madde listelenmemişse genellikle yayım tarihinde yürürlüğe girmiştir.
    return varsayilan, False
