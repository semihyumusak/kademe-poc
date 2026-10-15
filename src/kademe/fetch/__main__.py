"""Ham belgeleri indirir: python -m kademe.fetch [--no-wayback] [--only ID]

Çıktı düzeni:
  data/raw/<norm>/current.<ext>                 güncel metin
  data/raw/<norm>/wayback/<timestamp>.<ext>     tarihsel anlık görüntüler
  data/raw/<norm>/wayback/index.json            anlık görüntü listesi
"""
from __future__ import annotations

import argparse
import json
import sys

from kademe.corpus import NORMS
from kademe.fetch import http, wayback
from kademe.paths import RAW


def fetch_norm(spec, *, with_wayback: bool = True, force: bool = False) -> dict:
    base = RAW / spec.raw_name
    cur = http.download(spec.url, base / f"current.{spec.dosya_turu}", force=force)
    report = {"id": spec.id, "current": str(cur.relative_to(RAW)), "wayback": 0}
    if not (with_wayback and spec.wayback_kaliplari):
        return report
    idx_path = base / "wayback" / "index.json"
    if idx_path.exists() and not force:
        index = json.loads(idx_path.read_text(encoding="utf-8"))
    else:
        found = []
        for pattern in spec.wayback_kaliplari:
            try:
                found += wayback.list_snapshots(pattern)
            except RuntimeError as exc:
                print(f"  ! CDX sorgusu başarısız ({pattern}): {exc}", file=sys.stderr)
        chosen = wayback.select(found)
        index = [s.__dict__ for s in chosen]
        idx_path.parent.mkdir(parents=True, exist_ok=True)
        idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = 0
    for row in index:
        s = wayback.Snapshot(**row)
        try:
            http.download(s.raw_url, base / "wayback" / f"{s.timestamp}.{s.ext}")
            ok += 1
        except RuntimeError as exc:
            print(f"  ! anlık görüntü indirilemedi {s.timestamp}: {exc}", file=sys.stderr)
    report["wayback"] = ok
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kademe.fetch", description=__doc__)
    ap.add_argument("--no-wayback", action="store_true", help="tarihsel anlık görüntüleri indirme")
    ap.add_argument("--only", action="append", help="yalnızca bu norm id(ler)i")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    for spec in NORMS:
        if args.only and spec.id not in args.only:
            continue
        print(f"[fetch] {spec.id}")
        rep = fetch_norm(spec, with_wayback=not args.no_wayback, force=args.force)
        print(f"        güncel={rep['current']} wayback={rep['wayback']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
