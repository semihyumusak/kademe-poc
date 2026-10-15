"""Grafı kurar, istatistikleri yazar, SQLite ve RDF/Turtle dışa aktarımını üretir: python -m kademe.graph"""
from __future__ import annotations

import argparse
import json
from collections import Counter

from kademe.graph.export import to_sqlite, to_turtle
from kademe.graph.model import KademeGraph
from kademe.paths import GRAPH


def stats(kg: KademeGraph) -> dict:
    g = kg.g
    zincir = Counter(len(v) for v in kg._surumler.values())
    return {
        "dugum": g.number_of_nodes(),
        "kenar": g.number_of_edges(),
        "dugum_etiket": dict(Counter(a.get("etiket") for _, a in g.nodes(data=True))),
        "kenar_tip": dict(Counter(k for _, _, k in g.edges(keys=True))),
        "madde_surum": len(kg.surum_listesi),
        "madde_surum_metinli": sum(1 for s in kg.surum_listesi if s.get("metin_mevcut")),
        "surum_zinciri_uzunluk_dagilimi": dict(sorted(zincir.items())),
        "katman_norm": dict(Counter(n["katman"] for n in kg.normlar)),
        "dayanak_zincirleri": {n["id"]: kg.dayanak_zinciri_yukari(n["id"]) for n in kg.normlar},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kademe.graph", description=__doc__)
    ap.add_argument("--no-rdf", action="store_true")
    args = ap.parse_args(argv)
    kg = KademeGraph.load()
    st = stats(kg)
    (GRAPH / "graf_istatistikleri.json").write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in st.items() if k != "dayanak_zincirleri"}, ensure_ascii=False, indent=1))
    print("sqlite:", to_sqlite())
    if not args.no_rdf:
        print("turtle:", to_turtle())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
