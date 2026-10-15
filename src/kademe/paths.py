"""Depo içi yollar. KADEME_ROOT ortam değişkeniyle değiştirilebilir."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("KADEME_ROOT", Path(__file__).resolve().parents[2]))
DATA = ROOT / "data"
RAW = DATA / "raw"
GRAPH = DATA / "graph"
CACHE = DATA / "cache"
EVAL = ROOT / "eval"
ONTOLOGY = ROOT / "ontology"

for _p in (RAW, GRAPH, CACHE):
    _p.mkdir(parents=True, exist_ok=True)
