"""Madde düzeyinde sürüm zinciri çıkarımı.

Girdi: bir maddenin farklı tarihlerdeki gözlemleri (güncel metin + Wayback
anlık görüntüleri) ve her gözlemdeki değişiklik notları.

Algoritma (ayrıntı: docs/algoritma.md):
 1. Gözlemler tarih sırasına dizilir; biçimden bağımsız parmak izi aynı (ya da
    benzerliği >= ESIK) olan ardışık gözlemler tek "gözlenen sürüm"de birleşir.
 2. Her gözlenen sürümün başlangıcı, metnindeki notların (Değişik/Ek/İptal...)
    yürürlük tarihlerinden önceki sürümün başlangıcından sonra gelen en
    büyüğüdür. Not yoksa: ilk sürüm için normun/maddenin doğumu, sonrakiler için
    ilk gözlem tarihi (yaklaşık; "gozlem" kaynağıyla işaretlenir).
 3. Notlarda geçen ama hiçbir gözlemde metni bulunmayan ara tarihler için metni
    bilinmeyen yer tutucu sürümler eklenir; böylece yürürlük aralıkları
    kesintisiz kalır.
 4. Madde düzeyinde Mülga/İptal notu taşıyan ve gövdesi boş sürümler "mulga"
    durumuyla işaretlenir.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from difflib import SequenceMatcher
from typing import Callable

from kademe.parse.notes import FOOTNOTE_REF_RE, Not, parse_notes, strip_notes
from kademe.parse.structure import MADDE_RE, NOTE_ONLY_RE, split_leading_notes
from kademe.parse.text import fingerprint

ESIK = 0.985


@dataclass
class Gozlem:
    tarih: date
    metin: str
    kaynak: str  # "guncel" | "wayback:<timestamp>"
    baslik: str | None = None
    ek_notlar: list[Not] = field(default_factory=list)  # dipnotlardan gelen olaylar


@dataclass
class SurumTaslak:
    metin: str | None
    baslangic: date | None
    bitis: date | None
    baslangic_kaynagi: str  # not | tablo | dipnot | yayim | gozlem | dogum
    gozlemler: list[str]
    notlar: list[Not]
    durum: str = "yururlukte"  # yururlukte | mulga
    ilk_gozlem: date | None = None
    son_gozlem: date | None = None
    belirsizlik: tuple[date, date] | None = None  # başlangıç bu aralıkta (gözleme dayalı)

    @property
    def metin_mevcut(self) -> bool:
        return self.metin is not None


_PDF_NOISE = [
    # Satır içine düşmüş dipnot cümleleri: "22/2/2018 tarihli ve 7100 sayılı Kanunun 11 inci maddesiyle, ... değiştirilmiştir."
    re.compile(r"\d{1,2}/\d{1,2}/\d{4}\s+tarih\w*\s+ve\s+\d+\s+sayılı\s+[\w']+(?:\s+[\w']+){0,6}?\s+\d+\s*\w*\s+maddesiyle"
               r"(?:[^.]{0,400}?(?:değiştirilmiş|eklenmiş|çıkarılmış|kaldırılmış|kanunlaşmış)\w*\.)?"),
    re.compile(r"Madde başlığı[^.]{0,200}?(?:değiştirilmiş|eklenmiş)\w*\."),
    re.compile(r"Sözkonusu İptal Kararı[^.]{0,200}\."),
    re.compile(r"\b\d{4}-\d{1,2}\b"),  # Düstur sayfa/cilt numaraları
    re.compile(r"(?:\(\d{1,2}\)){2,}"),  # art arda dipnot işaretleri
]
_TAIL_CUT = re.compile(r"(?:Yönetmeliğin|Yönergenin) Yayımlandığı Resm[îi] Gazete.*$", re.S)


def temizle(text: str) -> str:
    """Arşiv (PDF) metinlerindeki norm dışı gürültüyü ayıklar."""
    text = _TAIL_CUT.sub("", text)
    for rx in _PDF_NOISE:
        text = rx.sub(" ", text)
    return re.sub(r"[ \t]{2,}", " ", text).strip()


def _fp(text: str) -> str:
    return fingerprint(FOOTNOTE_REF_RE.sub("", temizle(text)))


def _ratio(a: str, b: str, esik: float) -> bool:
    sm = SequenceMatcher(None, a, b, autojunk=False)
    if sm.real_quick_ratio() < esik or sm.quick_ratio() < esik:
        return False
    return sm.ratio() >= esik


def _not_imzasi(text: str) -> frozenset:
    return frozenset((n.tur, n.tarih) for n in parse_notes(text))


def _same(a: str, b: str, na: frozenset | None = None, nb: frozenset | None = None) -> bool:
    """İki gözlem aynı sürüm mü?

    Ya parmak izleri >= ESIK benzerdir ya da değişiklik notu kümeleri aynıdır ve
    rakamlar atıldığında metinler >= 0.95 benzerdir (PDF'teki sayfa/dipnot
    numarası gürültüsü gerçek bir değişiklik sayılmaz).
    """
    if a == b:
        return True
    if not a or not b:
        return False
    if _ratio(a, b, ESIK):
        return True
    if na is not None and na == nb:
        return _ratio(re.sub(r"\d", "", a), re.sub(r"\d", "", b), 0.95)
    return False


def baslik_notlari(text: str) -> list[Not]:
    """Madde başlık satırında ("Madde 5 – (Mülga: ...)") madde numarasının hemen ardından gelen,
    yani tüm maddeye ilişkin notlar."""
    first = text.split("\n", 1)[0]
    m = MADDE_RE.match(first)
    if not m:
        return []
    rest = m.group("rest").strip()
    lead, core = split_leading_notes(rest)
    if not lead and NOTE_ONLY_RE.match(rest):
        lead = rest  # gövdesi olmayan başlık: "(Mülga: ...)"
    # Yönetmeliklerde "(1)" fıkra numarası notun önüne gelirse not fıkraya aittir.
    return parse_notes(lead) if lead else []


def _govde_bos(text: str) -> bool:
    body = text
    m = MADDE_RE.match(body.split("\n", 1)[0])
    if m:
        body = m.group("rest") + ("\n" + body.split("\n", 1)[1] if "\n" in body else "")
    body = re.sub(r"\[\d+\]", "", strip_notes(body))
    return len(re.sub(r"[\W_]", "", body)) < 3


def build_chain(
    gozlemler: list[Gozlem],
    *,
    dogum: date | None,
    etkin_tarih: Callable[[Not], tuple[date | None, str]],
    aday_olaylar: list[Not] | None = None,
) -> list[SurumTaslak]:
    """Bir maddenin gözlemlerinden sürüm zincirini kurar.

    dogum: maddenin ilk yürürlük tarihi (normun yürürlüğü). Madde düzeyinde "Ek"
    notu varsa o tarih kullanılır.
    etkin_tarih: nottan (yürürlük tarihi, kaynak etiketi) üretir.
    """
    gozlemler = sorted(gozlemler, key=lambda g: g.tarih)
    # 1. gruplama
    gruplar: list[list[Gozlem]] = []
    fps: list[str] = []
    imzalar: list[frozenset] = []
    for g in gozlemler:
        fp = _fp(g.metin)
        im = _not_imzasi(g.metin)
        if gruplar and _same(fps[-1], fp, imzalar[-1], im):
            gruplar[-1].append(g)
            fps[-1] = fp if g.kaynak == "guncel" else fps[-1]
            continue
        # Daha eski bir sürüme geri dönüş (ör. bozuk anlık görüntü) varsa onu da aynı gruba kat.
        back = next((i for i in range(len(gruplar) - 2, -1, -1) if _same(fps[i], fp, imzalar[i], im)), None)
        if back is not None and g.kaynak != "guncel":
            continue  # tutarsız gözlem: zinciri bozmamak için yok sayılır
        gruplar.append([g])
        fps.append(fp)
        imzalar.append(im)

    def notlar(grup: list[Gozlem]) -> list[Not]:
        rep = grup[-1]
        return parse_notes(rep.metin) + list(rep.ek_notlar)

    def tarihler(ns: list[Not]) -> list[tuple[date, str, Not]]:
        out = []
        for n in ns:
            d, src = etkin_tarih(n)
            if d is not None:
                out.append((d, src, n))
        return sorted(out, key=lambda x: x[0])

    # Madde düzeyinde "Ek" notu maddenin doğumudur.
    for grup in gruplar:
        for n in baslik_notlari(grup[-1].metin):
            if n.tur == "ekleme":
                d, _ = etkin_tarih(n)
                if d and (dogum is None or d > dogum):
                    dogum = d
                break
        break

    surumler: list[SurumTaslak] = []
    onceki_bas: date | None = None
    for i, grup in enumerate(gruplar):
        ns = notlar(grup)
        ts = [t for t in tarihler(ns) if onceki_bas is None or t[0] > onceki_bas]
        ilk, son = grup[0].tarih, grup[-1].tarih
        if ts:
            # Konsolide metin, değişikliğin yürürlük tarihinden önce yayımlanmış olabilir;
            # sürümün başlangıcı yine de yürürlük tarihidir.
            bas, kaynak = ts[-1][0], ts[-1][1]
        elif i == 0:
            bas, kaynak = dogum, "dogum"
        else:
            onceki_son = gruplar[i - 1][-1].tarih
            pencere = sorted(
                (d, src) for d, src, _ in tarihler(list(aday_olaylar or []))
                if onceki_son < d <= ilk and (onceki_bas is None or d > onceki_bas)
            )
            if pencere:
                bas, kaynak = pencere[-1][0], "dipnot"
            else:
                bas, kaynak = ilk, "gozlem"
        # 3. araya yer tutucu sürümler
        alt_sinir = onceki_bas if onceki_bas is not None else dogum
        ara = sorted({t[0] for t in ts if t[0] < (bas or date.max) and (alt_sinir is None or t[0] > alt_sinir)})
        if i == 0 and dogum is not None and bas is not None and dogum < bas:
            ara = sorted(set(ara) | {dogum})
        for d in ara:
            src = next((t[1] for t in ts if t[0] == d), "dogum")
            surumler.append(SurumTaslak(metin=None, baslangic=d, bitis=None, baslangic_kaynagi=src,
                                        gozlemler=[], notlar=[t[2] for t in ts if t[0] == d]))
        rep = grup[-1]
        madde_mulga = any(n.tur in ("mulga", "iptal") for n in baslik_notlari(rep.metin)) and _govde_bos(rep.metin)
        s = SurumTaslak(
            metin=None if madde_mulga else rep.metin,
            baslangic=bas,
            bitis=None,
            baslangic_kaynagi=kaynak,
            gozlemler=[g.kaynak for g in grup],
            notlar=ns,
            durum="mulga" if madde_mulga else "yururlukte",
            ilk_gozlem=ilk,
            son_gozlem=son,
        )
        if kaynak == "gozlem" and i > 0:
            s.belirsizlik = (gruplar[i - 1][-1].tarih, ilk)
        surumler.append(s)
        onceki_bas = bas if bas is not None else onceki_bas
    # bitişler
    for a, b in zip(surumler, surumler[1:]):
        a.bitis = b.baslangic
    # Tarihi bilinmeyen başlangıçlar yalnızca ilk sürümde olabilir; tutarsız sıralamayı düzelt.
    for a, b in zip(surumler, surumler[1:]):
        if a.baslangic and b.baslangic and b.baslangic < a.baslangic:
            b.baslangic = a.baslangic
            a.bitis = b.baslangic
    return [s for s in surumler if not (s.baslangic and s.bitis and s.baslangic >= s.bitis and s.metin is None)]
