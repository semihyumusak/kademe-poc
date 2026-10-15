"""Internet Archive (Wayback Machine) üzerinden tarihsel anlık görüntüler.

mevzuat.gov.tr yalnızca güncel (konsolide) metni sunar. Eski sürüm metinleri
için sitenin Wayback'teki arşivlenmiş PDF/DOC/HTML kopyaları kullanılır. Her
anlık görüntü, arşivlendiği tarih itibarıyla konsolide metnin bir gözlemidir.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from kademe.fetch import http

CDX = "https://web.archive.org/cdx/search/cdx"


@dataclass(frozen=True)
class Snapshot:
    timestamp: str  # YYYYMMDDhhmmss
    original: str
    mimetype: str
    digest: str

    @property
    def date(self) -> str:
        t = self.timestamp
        return f"{t[0:4]}-{t[4:6]}-{t[6:8]}"

    @property
    def raw_url(self) -> str:
        # "id_" eki arşivin yeniden yazdığı değil, özgün baytları döndürür.
        return f"https://web.archive.org/web/{self.timestamp}id_/{self.original}"

    @property
    def ext(self) -> str:
        o = self.original.lower().split("?")[0]
        for e in ("pdf", "docx", "doc"):
            if o.endswith("." + e):
                return e
        return "html"


def list_snapshots(pattern: str) -> list[Snapshot]:
    params = {
        "url": pattern,
        "output": "json",
        "fl": "timestamp,original,mimetype,digest",
        "collapse": "digest",
        "filter": "statuscode:200",
    }
    r = http.get(CDX, params=params, timeout=120)
    text = r.text.strip()
    if not text:
        return []
    rows = json.loads(text)[1:]
    return [Snapshot(*row) for row in rows]


def select(snapshots: list[Snapshot], *, max_n: int = 40) -> list[Snapshot]:
    """Aynı içerik (digest) tekrarlarını atar; çok sayıda varsa zamana yayılmış alt küme seçer."""
    seen: set[str] = set()
    uniq = []
    for s in sorted(snapshots, key=lambda s: s.timestamp):
        if s.digest in seen:
            continue
        seen.add(s.digest)
        uniq.append(s)
    if len(uniq) <= max_n:
        return uniq
    step = (len(uniq) - 1) / (max_n - 1)
    return [uniq[round(i * step)] for i in range(max_n)]
