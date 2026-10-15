"""Madde-sürüm metinleri üzerinde BM25 + yoğun (bge-m3) hibrit dizin.

Her iki yapılandırma (A: düz RAG, B: KADEME-lite) aynı dizini kullanır;
farklar yalnızca filtreleme, graf genişletmesi ve yeniden sıralamadadır.
"""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi

from kademe.graph.model import KademeGraph
from kademe.parse.notes import strip_notes
from kademe.parse.text import tr_lower
from kademe.paths import CACHE

DENSE_MODEL = os.environ.get("KADEME_DENSE_MODEL", "BAAI/bge-m3")
_TOKEN = re.compile(r"[0-9a-zçğıöşüâîû]+")
STOP = set("""
ve veya ile da de bu şu o bir için olan olarak gibi ise ki mi mı mu mü ne nasıl hangi kadar daha en çok
her tüm göre ait dair üzere sonra önce ancak ayrıca yer alan ilgili tarafından halinde hâlinde edilir eder
olup olması olmak yapılır yapılması nedir midir mıdır var yok kaç ben bir
""".split())


def tokenize(text: str) -> list[str]:
    """Türkçe küçük harf + ilk 5 karakter kök kısaltması (F5 stemming)."""
    toks = _TOKEN.findall(tr_lower(text))
    return [t[:5] for t in toks if t not in STOP and len(t) > 1]


@dataclass
class Doc:
    id: str  # sürüm id
    birim_id: str
    norm_id: str
    katman: int
    text: str


def doc_text(kg: KademeGraph, s: dict) -> str:
    norm = kg.norm(s["norm_id"])
    madde = kg.node(s["birim_id"])
    head = f"{norm['ad']} Madde {madde['numara']}"
    if s.get("baslik"):
        head += f" ({s['baslik']})"
    return f"{head}\n{strip_notes(s['metin'])}"


class HybridIndex:
    def __init__(self, kg: KademeGraph, *, dense: bool = True, model_name: str = DENSE_MODEL):
        self.kg = kg
        self.docs = [
            Doc(id=s["id"], birim_id=s["birim_id"], norm_id=s["norm_id"], katman=kg.katman(s["norm_id"]),
                text=doc_text(kg, s))
            for s in kg.surum_listesi if s.get("metin_mevcut")
        ]
        self.pos = {d.id: i for i, d in enumerate(self.docs)}
        self.bm25 = BM25Okapi([tokenize(d.text) for d in self.docs])
        self.model_name = model_name
        self.model = None
        self.emb: np.ndarray | None = None
        if dense:
            self._build_dense()

    # ----------------------------------------------------------------- dense
    def _load_model(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer

            import torch

            device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
            self.model = SentenceTransformer(self.model_name, device=device)
            self.model.max_seq_length = 1024
        return self.model

    def _build_dense(self) -> None:
        h = hashlib.sha256((self.model_name + "\0" + "\0".join(d.id + d.text for d in self.docs)).encode()).hexdigest()[:16]
        path = CACHE / f"emb_{h}.npy"
        if path.exists():
            self.emb = np.load(path)
            return
        m = self._load_model()
        self.emb = m.encode([d.text for d in self.docs], batch_size=16, normalize_embeddings=True,
                            show_progress_bar=True).astype(np.float32)
        np.save(path, self.emb)

    @property
    def has_dense(self) -> bool:
        return self.emb is not None

    def encode_query(self, q: str) -> np.ndarray:
        return self._load_model().encode([q], normalize_embeddings=True)[0].astype(np.float32)

    # ----------------------------------------------------------------- skorlar
    def scores(self, query: str) -> tuple[np.ndarray, np.ndarray | None]:
        """(bm25, kosinüs) skor vektörleri (tüm dokümanlar)."""
        bm = np.asarray(self.bm25.get_scores(tokenize(query)), dtype=np.float32)
        cos = self.emb @ self.encode_query(query) if self.has_dense else None
        return bm, cos

    @staticmethod
    def rrf(*rank_lists: np.ndarray, k: int = 60) -> np.ndarray:
        """Karşılıklı sıra füzyonu: her liste skor vektörüdür (büyük = iyi)."""
        n = len(rank_lists[0])
        out = np.zeros(n, dtype=np.float32)
        for sc in rank_lists:
            order = np.argsort(-sc, kind="stable")
            ranks = np.empty(n, dtype=np.int64)
            ranks[order] = np.arange(n)
            out += 1.0 / (k + ranks + 1)
        return out

    def hybrid(self, query: str) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
        bm, cos = self.scores(query)
        fused = self.rrf(bm, cos) if cos is not None else self.rrf(bm)
        return fused, bm, cos
