"""Hız sınırlı, önbellekli HTTP indirici.

Ham dosyalar data/raw/ altına yazılır ve depoya alınmaz (.gitignore). Her
indirme data/raw/manifest.jsonl dosyasına url, sha256 ve zaman damgasıyla
kaydedilir; aynı dosya ikinci kez istenirse ağa çıkılmaz.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from kademe.paths import RAW

USER_AGENT = "Mozilla/5.0 (Macintosh; KADEME-PoC arastirma prototipi; +https://github.com/semihyumusak/kademe-poc)"
MIN_INTERVAL = 1.0  # saniye; SPEC §3: 1 istek/sn

_last_request = 0.0
_session: requests.Session | None = None


def session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = USER_AGENT
    return _session


def _throttle() -> None:
    global _last_request
    wait = MIN_INTERVAL - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def get(url: str, *, timeout: float = 90, retries: int = 3, **kw) -> requests.Response:
    last_exc: Exception | None = None
    for attempt in range(retries):
        _throttle()
        try:
            r = session().get(url, timeout=timeout, **kw)
            if r.status_code in (429, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
            r.raise_for_status()
            return r
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as exc:
            last_exc = exc
            time.sleep(2 ** attempt * 3)
    raise RuntimeError(f"indirilemedi: {url}: {last_exc}")


def _log(entry: dict) -> None:
    with (RAW / "manifest.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def download(url: str, dest: Path, *, force: bool = False) -> Path:
    """url'yi dest'e indirir; dest zaten varsa dokunmaz."""
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = get(url)
    dest.write_bytes(r.content)
    _log({
        "url": url,
        "path": str(dest.relative_to(RAW)),
        "sha256": hashlib.sha256(r.content).hexdigest(),
        "bytes": len(r.content),
        "content_type": r.headers.get("Content-Type"),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    return dest
