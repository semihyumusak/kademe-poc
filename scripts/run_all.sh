#!/usr/bin/env bash
# KADEME PoC uçtan uca: fetch -> parse -> graph -> eval
#
# Kullanım:
#   scripts/run_all.sh              # tam çalıştırma (bge-m3 yoğun gömme dahil)
#   scripts/run_all.sh --no-dense   # yalnızca BM25 (GPU/model indirmesi olmadan, hızlı)
#   SKIP_FETCH=1 scripts/run_all.sh # data/raw zaten doluysa indirmeyi atla
set -euo pipefail
cd "$(dirname "$0")/.."

DENSE_FLAG=""
EXTRAS="dev,dense"
if [[ "${1:-}" == "--no-dense" ]]; then
  DENSE_FLAG="--no-dense"
  EXTRAS="dev"
fi

command -v pdftotext >/dev/null || { echo "pdftotext (poppler) gerekli: brew install poppler | apt install poppler-utils"; exit 1; }

if [[ ! -x .venv/bin/python ]]; then
  if command -v uv >/dev/null; then
    uv venv --python 3.11 .venv
    uv pip install --python .venv/bin/python -e ".[${EXTRAS}]"
  else
    python3.11 -m venv .venv
    .venv/bin/pip install -e ".[${EXTRAS}]"
  fi
fi
PY=.venv/bin/python

echo "== 1/6 fetch (1 istek/sn; Wayback anlık görüntüleri dahil)"
if [[ -z "${SKIP_FETCH:-}" ]]; then $PY -m kademe.fetch; fi

echo "== 2/6 parse -> data/graph/*.jsonl"
$PY -m kademe.parse

echo "== 3/6 graph -> istatistik, SQLite, RDF/Turtle"
$PY -m kademe.graph

echo "== 4/6 testler"
$PY -m pytest -q

echo "== 5/6 değerlendirme seti + elle kontrol örneklemi"
$PY -m kademe.eval.adaylar
$PY -m kademe.eval.soru_seti
$PY -m kademe.eval.ornekle

echo "== 6/6 değerlendirme -> eval/results.json"
$PY -m kademe.eval.run $DENSE_FLAG --ablation
$PY -m kademe.eval.rapor
