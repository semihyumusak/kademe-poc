"""50 rastgele madde-sürümün elle kontrolü için örneklem (SPEC §7).

eval/elle_kontrol.jsonl dosyasını üretir. Her satırda kontrol edilecek sürümün
metni, yürürlük aralığı, dayanağı (not/tablo/dipnot/doğum/gözlem) ve kaynak
URL'si vardır. Kontrolör "kontrol" alanını doldurur:
  {"metin_dogru": true/false, "aralik_dogru": true/false, "aciklama": "..."}
Sonuçlar `python -m kademe.eval.rapor` ile README'ye özetlenir.

Var olan bir dosyadaki doldurulmuş kontroller korunur (aynı sürüm id'si için).

  python -m kademe.eval.ornekle [--n 50] [--tohum 2026]
"""
from __future__ import annotations

import argparse
import json
import random

from kademe.graph.model import KademeGraph
from kademe.paths import EVAL


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kademe.eval.ornekle")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--tohum", type=int, default=2026)
    args = ap.parse_args(argv)
    kg = KademeGraph.load()
    path = EVAL / "elle_kontrol.jsonl"
    eski = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            eski[r["surum_id"]] = r.get("kontrol")
    havuz = sorted((s for s in kg.surum_listesi if s.get("metin_mevcut")), key=lambda s: s["id"])
    rnd = random.Random(args.tohum)
    secim = rnd.sample(havuz, min(args.n, len(havuz)))
    with path.open("w", encoding="utf-8") as f:
        for s in sorted(secim, key=lambda s: s["id"]):
            n = kg.norm(s["norm_id"])
            f.write(json.dumps({
                "surum_id": s["id"],
                "norm": n["ad"],
                "kaynak_url": n["kaynak_url"],
                "yururluk_baslangic": s["yururluk_baslangic"],
                "yururluk_bitis": s["yururluk_bitis"],
                "baslangic_kaynagi": s["baslangic_kaynagi"],
                "gozlemler": s["gozlemler"],
                "metin": s["metin"],
                "kontrol": eski.get(s["id"]),
            }, ensure_ascii=False) + "\n")
    print(f"{len(secim)} sürüm -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
