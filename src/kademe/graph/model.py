"""JSONL'den NetworkX grafı ve zamansal sorgular.

Düğüm etiketleri: Norm, Birim, Surum, DegisiklikOlayi, UygulanabilirlikKurali
Kenar tipleri : DAYANAK, ATIF, DEGISTIRIR, UYGULANIR, PARCASI, SURUMU
"""
from __future__ import annotations

import json
from bisect import bisect_right
from collections import defaultdict
from datetime import date
from functools import cached_property
from pathlib import Path

import networkx as nx

from kademe.paths import GRAPH

DOSYALAR = {
    "normlar": "Norm",
    "birimler": "Birim",
    "surumler": "Surum",
    "degisiklik_olaylari": "DegisiklikOlayi",
    "uygulanabilirlik": "UygulanabilirlikKurali",
}


def _d(s: str | date | None) -> date | None:
    if s is None or isinstance(s, date):
        return s
    return date.fromisoformat(s)


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


class KademeGraph:
    def __init__(self, g: nx.MultiDiGraph):
        self.g = g
        self._surumler: dict[str, list[dict]] = defaultdict(list)
        for n, a in g.nodes(data=True):
            if a.get("etiket") == "Surum":
                self._surumler[a["birim_id"]].append(a)
        for lst in self._surumler.values():
            lst.sort(key=lambda s: (s.get("yururluk_baslangic") or "0000", s.get("sira", 0)))

    # ------------------------------------------------------------------ yükleme
    @classmethod
    def load(cls, directory: Path = GRAPH) -> "KademeGraph":
        g = nx.MultiDiGraph()
        for name, etiket in DOSYALAR.items():
            for row in read_jsonl(directory / f"{name}.jsonl"):
                g.add_node(row["id"], etiket=etiket, **row)
        for e in read_jsonl(directory / "kenarlar.jsonl"):
            attrs = {k: v for k, v in e.items() if k not in ("kaynak", "hedef", "tip")}
            g.add_edge(e["kaynak"], e["hedef"], key=e["tip"], tip=e["tip"], **attrs)
        for n, a in list(g.nodes(data=True)):
            if a.get("etiket") == "Surum":
                g.add_edge(n, a["birim_id"], key="SURUMU", tip="SURUMU")
        return cls(g)

    # ------------------------------------------------------------------ erişim
    def node(self, nid: str) -> dict:
        return self.g.nodes[nid]

    def norm(self, nid: str) -> dict:
        return self.g.nodes[nid]

    @cached_property
    def normlar(self) -> list[dict]:
        return [a for _, a in self.g.nodes(data=True) if a.get("etiket") == "Norm"]

    @cached_property
    def surum_listesi(self) -> list[dict]:
        return [s for lst in self._surumler.values() for s in lst]

    def surumler(self, birim_id: str) -> list[dict]:
        return self._surumler.get(birim_id, [])

    def madde_of(self, birim_id: str) -> str:
        """Fıkra/bent kimliğinden madde kimliğini döndürür."""
        parts = birim_id.split("/")
        return "/".join(parts[:2])

    def norm_of(self, nid: str) -> str:
        return nid.split("/")[0]

    def katman(self, nid: str) -> int:
        return self.g.nodes[self.norm_of(nid)]["katman"]

    # ------------------------------------------------------------------ zaman
    @staticmethod
    def yururlukte(s: dict, t: date) -> bool:
        if s.get("durum") != "yururlukte":
            return False
        b, e = _d(s.get("yururluk_baslangic")), _d(s.get("yururluk_bitis"))
        return (b is None or b <= t) and (e is None or t < e)

    def norm_yururlukte(self, norm_id: str, t: date) -> bool:
        n = self.g.nodes[norm_id]
        b, e = _d(n.get("yururluk_baslangic")), _d(n.get("yururluk_bitis"))
        return (b is None or b <= t) and (e is None or t < e)

    def point_in_time(self, birim_id: str, t: date | str) -> dict | None:
        """birim_id (madde) için t tarihinde yürürlükte olan sürüm; yoksa None."""
        t = _d(t)
        if not self.norm_yururlukte(self.norm_of(birim_id), t):
            return None
        lst = self.surumler(self.madde_of(birim_id))
        starts = [_d(s.get("yururluk_baslangic")) or date.min for s in lst]
        i = bisect_right(starts, t) - 1
        while i >= 0:
            s = lst[i]
            if self.yururlukte(s, t):
                return s
            if s.get("durum") == "mulga" and (_d(s.get("yururluk_baslangic")) or date.min) <= t:
                return None
            i -= 1
        return None

    def snapshot(self, t: date | str, *, metinli: bool = True) -> list[dict]:
        """t tarihinde yürürlükte olan tüm madde sürümleri (graf üzerinde nokta-zaman kesiti)."""
        t = _d(t)
        out = []
        for bid in self._surumler:
            s = self.point_in_time(bid, t)
            if s is not None and (s.get("metin_mevcut") or not metinli):
                out.append(s)
        return out

    def kurallar(self, birim_id: str) -> list[dict]:
        mid = self.madde_of(birim_id)
        norm = self.norm_of(mid)
        out = []
        for n, a in self.g.nodes(data=True):
            if a.get("etiket") == "UygulanabilirlikKurali" and (mid in a["hedef_maddeler"] or norm in a["hedef_maddeler"]):
                out.append(a)
        return out

    def applicable(self, birim_id: str, t: date | str, giris: date | str | None = None) -> dict | None:
        """Giriş dönemi (kohort) dikkate alınarak t tarihinde öğrenciye uygulanacak sürüm.

        Kural "onceki_surum": eşikten önce kayıt yaptıranlara, eşik tarihinden önce
        yürürlükte olan sürüm uygulanmaya devam eder. Kural "baslangic_ertele":
        eşikten önce kayıt yaptıranlar için yeni sürüm ertele_tarihi'ne kadar uygulanmaz.
        """
        t = _d(t)
        s = self.point_in_time(birim_id, t)
        if giris is None or s is None:
            return s
        giris = _d(giris)
        for k in self.kurallar(birim_id):
            esik = _d(k["kosul"]["esik"])
            uyar = giris < esik if k["kosul"]["giris"] == "once" else giris >= esik
            if not uyar:
                continue
            bas = _d(s.get("yururluk_baslangic")) or date.min
            if k["etki"] == "onceki_surum" and bas >= esik:
                eski = self.point_in_time(birim_id, date.fromordinal(esik.toordinal() - 1))
                if eski is not None:
                    return eski
            if k["etki"] == "baslangic_ertele" and k.get("ertele_tarihi") and t < _d(k["ertele_tarihi"]):
                eski = self.point_in_time(birim_id, date.fromordinal(bas.toordinal() - 1))
                return eski
        return s

    # ------------------------------------------------------------------ hiyerarşi
    def dayanak_hedefleri(self, norm_id: str) -> list[str]:
        """norm_id'nin DAYANAK kenarıyla bağlandığı üst birim/norm kimlikleri."""
        return [v for _, v, k in self.g.out_edges(norm_id, keys=True) if k == "DAYANAK"]

    def dayanak_zinciri_yukari(self, norm_id: str) -> list[str]:
        """Dayanak zincirini yukarı yürür: [alt norm, üst norm, en üst norm ...]."""
        out, frontier, seen = [norm_id], [norm_id], {norm_id}
        while frontier:
            nxt = []
            for n in frontier:
                for h in self.dayanak_hedefleri(n):
                    up = self.norm_of(h)
                    if up not in seen:
                        seen.add(up)
                        out.append(up)
                        nxt.append(up)
            frontier = nxt
        return out

    def dayanak_zinciri_asagi(self, hedef: str) -> list[str]:
        """hedef (norm ya da madde) üzerine dayanan alt normları (özyinelemeli) döndürür."""
        out, frontier = [], [hedef]
        seen = {hedef}
        while frontier:
            nxt = []
            for h in frontier:
                targets = [h] if "/" in h else [h] + [b for b in self.g.predecessors(h)
                                                      if self.g.nodes[b].get("tip") == "madde"]
                for t in targets:
                    for u, _, k in self.g.in_edges(t, keys=True):
                        if k == "DAYANAK" and u not in seen:
                            seen.add(u)
                            out.append(u)
                            nxt.append(u)
            frontier = nxt
        return out

    def atif_komsulari(self, birim_id: str) -> set[str]:
        """ATIF kenarlarıyla (iki yönde) 1 atlamalı madde komşuları."""
        mid = self.madde_of(birim_id)
        out = set()
        nodes = [mid] + [n for n in self.g.predecessors(mid) if self.g.nodes[n].get("etiket") == "Birim"]
        for n in nodes:
            for _, v, k in self.g.out_edges(n, keys=True):
                if k == "ATIF":
                    out.add(self.madde_of(v))
            for u, _, k in self.g.in_edges(n, keys=True):
                if k == "ATIF":
                    out.add(self.madde_of(u))
        out.discard(mid)
        return out

    def dayanak_komsulari(self, birim_id: str) -> tuple[set[str], set[str]]:
        """(yukarı, aşağı): maddenin normunun dayandığı üst maddeler / üst normlar ve
        bu maddeye ya da normuna dayanan alt normlar."""
        mid = self.madde_of(birim_id)
        norm = self.norm_of(mid)
        yukari = set(self.dayanak_hedefleri(norm))
        asagi = set()
        for t in (mid, norm):
            for u, _, k in self.g.in_edges(t, keys=True):
                if k == "DAYANAK":
                    asagi.add(u)
        return yukari, asagi

    def maddeler(self, norm_id: str) -> list[str]:
        return [n for n in self.g.predecessors(norm_id) if self.g.nodes[n].get("tip") == "madde"]
