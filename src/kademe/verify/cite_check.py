"""Atıf denetimi: bir cevapta geçen her atıf grafta var mı ve sorgu tarihinde yürürlükte mi?

PoC'de cevap üretimi yoktur; bu modül (a) erişim çıktısındaki sürüm kimliklerini,
(b) serbest metindeki "2547 sayılı Kanunun 44 üncü maddesi" gibi atıfları
denetler. Bir dil modeli eklenirse çıktısı doğrudan check_text()'e verilebilir.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date

from kademe.graph.model import KademeGraph
from kademe.parse.refs import extract_refs


@dataclass
class Denetim:
    atif: str
    birim_id: str | None
    grafta_var: bool
    yururlukte: bool
    yururlukteki_surum: str | None
    not_: str = ""


def check_ids(kg: KademeGraph, ids: list[str], tarih: date, giris: date | None = None) -> list[Denetim]:
    out = []
    for sid in ids:
        if sid not in kg.g:
            out.append(Denetim(sid, None, False, False, None, "grafta yok"))
            continue
        a = kg.node(sid)
        bid = a.get("birim_id", sid)
        guncel = kg.applicable(bid, tarih, giris)
        ok = guncel is not None and (guncel["id"] == sid or a.get("etiket") == "Birim")
        out.append(Denetim(sid, bid, True, ok, guncel["id"] if guncel else None,
                           "" if ok else "sorgu tarihinde yürürlükte değil ya da farklı sürüm uygulanıyor"))
    return out


def check_text(kg: KademeGraph, text: str, tarih: date, *, varsayilan_norm: str | None = None,
               giris: date | None = None) -> list[Denetim]:
    from kademe.parse.__main__ import ALIASES

    out = []
    for r in extract_refs(text, self_norm=varsayilan_norm or "", self_tur="", aliases=ALIASES,
                          varsayilan_kanun="kanun:2547"):
        if not r.hedef_norm:
            out.append(Denetim(r.metin, None, False, False, None,
                               f"korpus dışı norm ({r.dis_kanun} sayılı)" if r.dis_kanun else "norm çözülemedi"))
            continue
        bid = f"{r.hedef_norm}/{r.madde}"
        if bid not in kg.g:
            out.append(Denetim(r.metin, bid, False, False, None, "madde grafta yok"))
            continue
        s = kg.applicable(bid, tarih, giris)
        out.append(Denetim(r.metin, bid, True, s is not None, s["id"] if s else None,
                           "" if s else "madde sorgu tarihinde yürürlükte değil"))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kademe.verify", description=__doc__)
    ap.add_argument("tarih", help="YYYY-MM-DD")
    ap.add_argument("metin_ya_da_id", nargs="+")
    args = ap.parse_args(argv)
    kg = KademeGraph.load()
    t = date.fromisoformat(args.tarih)
    ids = [x for x in args.metin_ya_da_id if x in kg.g]
    res = check_ids(kg, ids, t) if ids else check_text(kg, " ".join(args.metin_ya_da_id), t)
    print(json.dumps([asdict(r) for r in res], ensure_ascii=False, indent=1))
    return 0
