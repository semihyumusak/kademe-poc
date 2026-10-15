"""İki erişim yapılandırması.

A) duz_rag     : hibrit (BM25 + bge-m3, RRF) ilk-k; yürürlük filtresi yok.
B) kademe_lite : aynı hibrit erişim
                 + sorgu tarihi (ve varsa giriş dönemi) ile yürürlük filtresi
                 + DAYANAK/ATIF üzerinden 1 atlamalı graf genişletmesi
                 + katman önceliğiyle yeniden sıralama.

Her iki yapılandırma aynı reddetme eşiğini kullanır: ilk-k içindeki en yüksek
yoğun kosinüs benzerliği RED_ESIGI'nin altındaysa sonuç boş döner.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache

import numpy as np

from kademe.graph.model import KademeGraph
from kademe.retrieve.index import HybridIndex

RED_ESIGI = 0.50  # a priori seçildi; eval/results.json'da eşik taraması ayrıca raporlanır


@dataclass
class Hit:
    surum_id: str
    birim_id: str
    norm_id: str
    katman: int
    skor: float
    kosinus: float | None
    yol: str  # "erisim" | "graf:ATIF" | "graf:DAYANAK_yukari" | "graf:DAYANAK_asagi"


@dataclass
class Sonuc:
    hits: list[Hit]
    reddedildi: bool
    max_kosinus: float | None
    aday: list[Hit] = field(default_factory=list)  # reddetmeden önceki ilk-k

    @property
    def ids(self) -> list[str]:
        return [h.surum_id for h in self.hits]


def _reddet(hits: list[Hit], esik: float | None) -> tuple[list[Hit], bool, float | None]:
    cs = [h.kosinus for h in hits if h.kosinus is not None]
    mx = max(cs) if cs else None
    if esik is not None and mx is not None and mx < esik:
        return [], True, mx
    return hits, False, mx


class DuzRAG:
    ad = "A_duz_rag"

    def __init__(self, idx: HybridIndex, *, k: int = 5, red_esigi: float | None = RED_ESIGI):
        self.idx, self.k, self.red_esigi = idx, k, red_esigi

    def search(self, soru: str, tarih: date | None = None, giris: date | None = None) -> Sonuc:
        fused, _bm, cos = self.idx.hybrid(soru)
        order = np.argsort(-fused, kind="stable")[: self.k]
        hits = [self._hit(i, fused, cos, "erisim") for i in order]
        kept, red, mx = _reddet(hits, self.red_esigi)
        return Sonuc(kept, red, mx, aday=hits)

    def _hit(self, i: int, fused, cos, yol: str) -> Hit:
        d = self.idx.docs[i]
        return Hit(d.id, d.birim_id, d.norm_id, d.katman, float(fused[i]),
                   float(cos[i]) if cos is not None else None, yol)


class KademeLite(DuzRAG):
    ad = "B_kademe_lite"

    def __init__(self, idx: HybridIndex, kg: KademeGraph, *, k: int = 5, tohum: int = 8, genislet: int = 3,
                 graf_bonus: float = 0.25, alt_norm_ilk: int = 2, katman_orani: float = 0.5, koru: int = 2,
                 red_esigi: float | None = RED_ESIGI, genisletme: bool = True, katman_onceligi: bool = True):
        super().__init__(idx, k=k, red_esigi=red_esigi)
        self.kg = kg
        self.tohum, self.genislet, self.graf_bonus = tohum, genislet, graf_bonus
        self.alt_norm_ilk, self.katman_orani, self.koru = alt_norm_ilk, katman_orani, koru
        self.genisletme, self.katman_onceligi = genisletme, katman_onceligi

    @lru_cache(maxsize=256)
    def _uygulanan(self, tarih: date, giris: date | None) -> dict[str, str]:
        """birim_id -> o tarihte (kohort dikkate alınarak) uygulanan sürüm id'si."""
        out = {}
        for bid in self.kg._surumler:
            s = self.kg.applicable(bid, tarih, giris)
            if s is not None and s.get("metin_mevcut"):
                out[bid] = s["id"]
        return out

    def search(self, soru: str, tarih: date | None = None, giris: date | None = None) -> Sonuc:
        tarih = tarih or date.today()
        fused, _bm, cos = self.idx.hybrid(soru)
        uyg = self._uygulanan(tarih, giris)
        izinli = set(uyg.values())
        order = [i for i in np.argsort(-fused, kind="stable") if self.idx.docs[i].id in izinli]
        aday: dict[str, Hit] = {}
        for i in order[: self.tohum]:
            h = self._hit(i, fused, cos, "erisim")
            aday[h.surum_id] = h
        if self.genisletme:
            for i in order[: self.genislet]:
                self._genislet(self.idx.docs[i].birim_id, uyg, fused, cos, aday)
        hits = sorted(aday.values(), key=lambda h: -h.skor)
        if self.katman_onceligi:
            hits = self._katman_sirala(hits)
        else:
            dogrudan = [h for h in hits if h.yol == "erisim"][: self.koru]
            hits = (dogrudan + [h for h in hits if h not in dogrudan])[: self.k]
        kept, red, mx = _reddet(hits, self.red_esigi)
        return Sonuc(kept, red, mx, aday=hits)

    def _ekle(self, birim_id: str, uyg, fused, cos, aday, yol: str) -> None:
        sid = uyg.get(birim_id)
        if sid is None or sid not in self.idx.pos:
            return
        i = self.idx.pos[sid]
        h = self._hit(i, fused, cos, yol)
        # Katmanlar arası (DAYANAK) komşular küçük bir öncelik alır; aynı norm içi ATIF
        # komşuları yalnızca aday havuzuna eklenir.
        h.skor = float(fused[i]) * (1 + (self.graf_bonus if yol.startswith("graf:DAYANAK") else 0.0))
        if sid not in aday or aday[sid].skor < h.skor:
            aday[sid] = h

    def _genislet(self, birim_id: str, uyg, fused, cos, aday) -> None:
        kg = self.kg
        for nb in kg.atif_komsulari(birim_id):
            self._ekle(nb, uyg, fused, cos, aday, "graf:ATIF")
        yukari, asagi = kg.dayanak_komsulari(birim_id)
        for h in yukari:
            targets = [h] if "/" in h else kg.maddeler(h)
            self._en_iyi(targets, uyg, fused, cos, aday, "graf:DAYANAK_yukari")
        for alt in asagi:
            self._en_iyi(kg.maddeler(alt), uyg, fused, cos, aday, "graf:DAYANAK_asagi")

    def _en_iyi(self, maddeler: list[str], uyg, fused, cos, aday, yol: str) -> None:
        """Bir normun maddelerinden sorguyla en ilgili alt_norm_ilk tanesini ekler."""
        scored = []
        for m in maddeler:
            sid = uyg.get(m)
            if sid in self.idx.pos:
                scored.append((float(fused[self.idx.pos[sid]]), m))
        for _, m in sorted(scored, reverse=True)[: self.alt_norm_ilk]:
            self._ekle(m, uyg, fused, cos, aday, yol)

    def _katman_sirala(self, hits: list[Hit]) -> list[Hit]:
        """En güçlü `koru` doğrudan isabeti tut; sonra en iyi skorun katman_orani katından yüksek
        adaylar arasında henüz temsil edilmeyen her katmanın en iyisini ekle (hiyerarşi
        kapsaması); kalan yerleri skora göre doldur. Sonuç üst katmandan alta sıralanır."""
        if not hits:
            return hits
        top = hits[0].skor
        # En güçlü doğrudan erişim isabetleri her zaman korunur.
        secilen: list[Hit] = [h for h in hits if h.yol == "erisim"][: self.koru]
        gorulen_katman = {h.katman for h in secilen}
        for h in hits:
            if h.skor < self.katman_orani * top or len(secilen) >= self.k:
                break
            if h.katman not in gorulen_katman and h not in secilen:
                gorulen_katman.add(h.katman)
                secilen.append(h)
        for h in hits:
            if len(secilen) >= self.k:
                break
            if h not in secilen:
                secilen.append(h)
        return sorted(secilen, key=lambda h: (h.katman, -h.skor))
