"""A ve B yapılandırmalarını mini set üzerinde ölçer; eval/results.json ve tabloyu üretir.

Ölçütler (SPEC §5):
  atıf kesinliği / duyarlılığı @5   madde-sürüm düzeyinde (cevaplanabilir sorular)
  yürürlük doğruluğu                getirilen sürümlerin sorgu tarihinde (ve giriş
                                    dönemine göre) uygulanan sürüm olma oranı
  hiyerarşi kapsaması               hiyerarşi sorularında altın kümedeki her
                                    katmandan en az bir altın madde getirilme oranı
  reddetme                          cevaplanamaz sorularda boş sonuç oranı

  python -m kademe.eval.run [--no-dense] [--ablation]
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from collections import defaultdict
from datetime import date, datetime, timezone

import numpy as np

from kademe.graph.model import KademeGraph
from kademe.parse.akademik import donem_tarihi
from kademe.paths import EVAL, ROOT
from kademe.retrieve.configs import RED_ESIGI, DuzRAG, KademeLite
from kademe.retrieve.index import HybridIndex

K = 5
TURLER = ["tek_madde", "zamansal", "hiyerarsi", "intibak", "cevaplanamaz"]


def load_set() -> list[dict]:
    with (EVAL / "yoksc_mini.jsonl").open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def score_one(kg: KademeGraph, q: dict, ids: list[str]) -> dict:
    gold = set(q["altin_birimler"])
    t = date.fromisoformat(q["itibariyle_tarih"])
    g = donem_tarihi(q["giris_donemi"]) if q.get("giris_donemi") else None
    ret = ids[:K]
    hit = [i for i in ret if i in gold]
    out: dict = {"getirilen": ret, "dogru": hit}
    if q["tur"] == "cevaplanamaz":
        out["reddetti"] = len(ret) == 0
        return out
    out["kesinlik"] = len(hit) / len(ret) if ret else 0.0
    out["duyarlilik"] = len(hit) / len(gold) if gold else 0.0
    # madde düzeyi (sürümden bağımsız) duyarlılık: tanı amaçlı
    gm = {kg.node(i)["birim_id"] for i in gold}
    rm = {kg.node(i)["birim_id"] for i in ret}
    out["madde_duyarlilik"] = len(gm & rm) / len(gm) if gm else 0.0
    if ret:
        ok = 0
        for i in ret:
            s = kg.applicable(kg.node(i)["birim_id"], t, g)
            ok += int(s is not None and s["id"] == i)
        out["yururluk_dogrulugu"] = ok / len(ret)
    if q["tur"] == "hiyerarsi":
        katmanlar = {kg.katman(i) for i in gold}
        bulunan = {kg.katman(i) for i in hit}
        out["hiyerarsi_kapsama"] = katmanlar <= bulunan
    return out


def evaluate(kg: KademeGraph, retriever, sorular: list[dict]) -> dict:
    per_q = {}
    t0 = time.perf_counter()
    for q in sorular:
        t = date.fromisoformat(q["itibariyle_tarih"])
        g = donem_tarihi(q["giris_donemi"]) if q.get("giris_donemi") else None
        res = retriever.search(q["soru"], t, g)
        sc = score_one(kg, q, res.ids)
        sc["max_kosinus"] = res.max_kosinus
        sc["aday_max_kosinus"] = max((h.kosinus for h in res.aday if h.kosinus is not None), default=None)
        sc["yollar"] = [h.yol for h in res.hits]
        sc["tur"] = q["tur"]
        per_q[q["id"]] = sc
    sure = time.perf_counter() - t0
    return {"soru_basina": per_q, "ozet": summarize(per_q), "sure_sn": round(sure, 2)}


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(float(np.mean(xs)), 3) if xs else None


def summarize(per_q: dict) -> dict:
    by = defaultdict(list)
    for qid, s in per_q.items():
        by[s["tur"]].append(s)
        if s["tur"] != "cevaplanamaz":
            by["cevaplanabilir"].append(s)
    out = {}
    for tur in TURLER[:-1] + ["cevaplanabilir"]:
        rows = by.get(tur, [])
        out[tur] = {
            "n": len(rows),
            "kesinlik@5": _mean([r["kesinlik"] for r in rows]),
            "duyarlilik@5": _mean([r["duyarlilik"] for r in rows]),
            "madde_duyarlilik@5": _mean([r["madde_duyarlilik"] for r in rows]),
            "yururluk_dogrulugu": _mean([r.get("yururluk_dogrulugu") for r in rows]),
        }
    h = by.get("hiyerarsi", [])
    out["hiyerarsi"]["hiyerarsi_kapsamasi"] = _mean([float(r["hiyerarsi_kapsama"]) for r in h])
    c = by.get("cevaplanamaz", [])
    out["cevaplanamaz"] = {"n": len(c), "reddetme": _mean([float(r["reddetti"]) for r in c])}
    return out


def esik_taramasi(per_q_a: dict, per_q_b: dict) -> list[dict]:
    """Reddetme eşiğinin etkisi: her eşik için cevaplanamaz reddetme ve cevaplanabilir
    sorularda yanlışlıkla boş dönme oranı (aday listesindeki en yüksek kosinüse göre)."""
    out = []
    for esik in np.round(np.arange(0.40, 0.66, 0.025), 3):
        row = {"esik": float(esik)}
        for ad, pq in (("A", per_q_a), ("B", per_q_b)):
            red = [s for s in pq.values() if s["tur"] == "cevaplanamaz"]
            cev = [s for s in pq.values() if s["tur"] != "cevaplanamaz"]
            row[f"{ad}_reddetme"] = _mean([float((s["aday_max_kosinus"] or 0) < esik) for s in red])
            row[f"{ad}_yanlis_red"] = _mean([float((s["aday_max_kosinus"] or 0) < esik) for s in cev])
        out.append(row)
    return out


def tablo(sonuclar: dict) -> str:
    a, b = sonuclar["A_duz_rag"]["ozet"], sonuclar["B_kademe_lite"]["ozet"]

    def f(x):
        return "–" if x is None else f"{x:.2f}"

    lines = [
        "| Soru türü (n) | Ölçüt | A: düz RAG | B: KADEME-lite |",
        "|---|---|---:|---:|",
    ]
    for tur, ad in [("tek_madde", "Tek madde"), ("zamansal", "Zamansal sürüm"), ("hiyerarsi", "Hiyerarşi"),
                    ("intibak", "İntibak/geçici madde"), ("cevaplanabilir", "Tüm cevaplanabilir")]:
        n = a[tur]["n"]
        lines.append(f"| {ad} ({n}) | Kesinlik@5 / Duyarlılık@5 | {f(a[tur]['kesinlik@5'])} / {f(a[tur]['duyarlilik@5'])} "
                     f"| {f(b[tur]['kesinlik@5'])} / {f(b[tur]['duyarlilik@5'])} |")
        lines.append(f"| | Yürürlük doğruluğu | {f(a[tur]['yururluk_dogrulugu'])} | {f(b[tur]['yururluk_dogrulugu'])} |")
    lines.append(f"| Hiyerarşi ({a['hiyerarsi']['n']}) | Hiyerarşi kapsaması | {f(a['hiyerarsi']['hiyerarsi_kapsamasi'])} "
                 f"| {f(b['hiyerarsi']['hiyerarsi_kapsamasi'])} |")
    lines.append(f"| Cevaplanamaz ({a['cevaplanamaz']['n']}) | Reddetme | {f(a['cevaplanamaz']['reddetme'])} "
                 f"| {f(b['cevaplanamaz']['reddetme'])} |")
    return "\n".join(lines)


def _git_rev() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip() or None
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kademe.eval.run", description=__doc__)
    ap.add_argument("--no-dense", action="store_true", help="yalnızca BM25 (yoğun model olmadan)")
    ap.add_argument("--ablation", action="store_true", help="B bileşenlerinin ayrı katkısını da ölç")
    args = ap.parse_args(argv)
    kg = KademeGraph.load()
    sorular = load_set()
    idx = HybridIndex(kg, dense=not args.no_dense)
    esik = RED_ESIGI if idx.has_dense else None
    cfgs = {"A_duz_rag": DuzRAG(idx, red_esigi=esik), "B_kademe_lite": KademeLite(idx, kg, red_esigi=esik)}
    if args.ablation:
        cfgs["B-yalniz_tarih_filtresi"] = KademeLite(idx, kg, red_esigi=esik, genisletme=False, katman_onceligi=False)
        cfgs["B-genisletme_yok"] = KademeLite(idx, kg, red_esigi=esik, genisletme=False)
        cfgs["B-katman_onceligi_yok"] = KademeLite(idx, kg, red_esigi=esik, katman_onceligi=False)
    sonuclar = {ad: evaluate(kg, r, sorular) for ad, r in cfgs.items()}
    out = {
        "uretim_zamani": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git": _git_rev(),
        "ortam": {"python": platform.python_version(), "platform": platform.platform(),
                  "islemci": platform.processor() or platform.machine()},
        "ayarlar": {"k": K, "yogun_model": idx.model_name if idx.has_dense else None, "reddetme_esigi": esik,
                    "bm25": "rank_bm25.BM25Okapi, Türkçe küçük harf + F5 kök", "fuzyon": "RRF k=60",
                    "dokuman_sayisi": len(idx.docs)},
        "soru_sayisi": len(sorular),
        "sonuclar": sonuclar,
        "esik_taramasi": esik_taramasi(sonuclar["A_duz_rag"]["soru_basina"],
                                       sonuclar["B_kademe_lite"]["soru_basina"]) if idx.has_dense else None,
    }
    (EVAL / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    md = tablo(sonuclar)
    (EVAL / "results_table.md").write_text(md + "\n", encoding="utf-8")
    print(md)
    if args.ablation:
        for ad in cfgs:
            o = sonuclar[ad]["ozet"]
            print(f"{ad:28} P@5={o['cevaplanabilir']['kesinlik@5']} R@5={o['cevaplanabilir']['duyarlilik@5']} "
                  f"yürürlük={o['cevaplanabilir']['yururluk_dogrulugu']} hiy={o['hiyerarsi']['hiyerarsi_kapsamasi']} "
                  f"red={o['cevaplanamaz']['reddetme']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
