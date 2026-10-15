"""Değerlendirme seti için graftan şablonla soru adayı türetme (SPEC §4).

Çıktı eval/adaylar.jsonl: her aday bir şablon türü, ilgili sürüm kimlikleri ve
sorgu tarihleri içerir. Adaylar elle doğal dile yazılarak eval/yoksc_mini.jsonl
dosyasına alınır; bu dosya yalnızca yazım için yardımcıdır.

  python -m kademe.eval.adaylar
"""
from __future__ import annotations

import json
from datetime import date

from kademe.graph.model import KademeGraph, _d
from kademe.paths import EVAL

GUVENILIR = {"not", "tablo", "dipnot"}


def orta(a: date, b: date | None) -> date:
    b = b or date(2026, 10, 1)
    return date.fromordinal((a.toordinal() + b.toordinal()) // 2)


def zamansal(kg: KademeGraph) -> list[dict]:
    out = []
    for bid, lst in kg._surumler.items():
        metinli = [s for s in lst if s.get("metin_mevcut") and s["durum"] == "yururlukte"]
        for a, b in zip(metinli, metinli[1:]):
            if b["baslangic_kaynagi"] not in GUVENILIR:
                continue
            if a["yururluk_bitis"] != b["yururluk_baslangic"]:
                continue
            ta = orta(_d(a["yururluk_baslangic"]), _d(a["yururluk_bitis"]))
            tb = orta(_d(b["yururluk_baslangic"]), _d(b["yururluk_bitis"]))
            out.append({"sablon": "zamansal_cift", "birim": bid, "baslik": a.get("baslik"),
                        "surum_eski": a["id"], "tarih_eski": ta.isoformat(),
                        "surum_yeni": b["id"], "tarih_yeni": tb.isoformat(),
                        "degisiklik": b.get("kaynak_notu", "")[-200:]})
    return out


def hiyerarsi(kg: KademeGraph) -> list[dict]:
    out = []
    for u, v, k in kg.g.edges(keys=True):
        if k != "DAYANAK":
            continue
        out.append({"sablon": "hiyerarsi", "alt_norm": u, "ust": v,
                    "alt_katman": kg.katman(u), "ust_katman": kg.katman(v)})
    return out


def intibak(kg: KademeGraph) -> list[dict]:
    return [{"sablon": "intibak", "kural": a["id"], "hedef": a["hedef_maddeler"], "kosul": a["kosul"],
             "etki": a["etki"], "metin": a["metin"][:300]}
            for _, a in kg.g.nodes(data=True) if a.get("etiket") == "UygulanabilirlikKurali"]


def main() -> int:
    kg = KademeGraph.load()
    rows = zamansal(kg) + hiyerarsi(kg) + intibak(kg)
    with (EVAL / "adaylar.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter

    print(Counter(r["sablon"] for r in rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
