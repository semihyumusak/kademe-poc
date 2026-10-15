"""SQLite deposu ve RDF/Turtle dışa aktarımı."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

from kademe.graph.model import DOSYALAR, read_jsonl
from kademe.paths import GRAPH

KADEME = Namespace("https://w3id.org/kademe/ontology#")
KD = Namespace("https://w3id.org/kademe/id/")
ELI = Namespace("http://data.europa.eu/eli/ontology#")


def to_sqlite(directory: Path = GRAPH, db_path: Path | None = None) -> Path:
    db_path = db_path or directory / "kademe.sqlite"
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for name in list(DOSYALAR) + ["kenarlar"]:
        rows = read_jsonl(directory / f"{name}.jsonl")
        cols = sorted({k for r in rows for k in r}) if rows else ["id"]
        cur.execute(f'CREATE TABLE "{name}" ({", ".join(f"{c!r} TEXT" for c in cols)})')
        for r in rows:
            vals = [json.dumps(r[c], ensure_ascii=False) if isinstance(r.get(c), (list, dict)) else r.get(c)
                    for c in cols]
            cur.execute(f'INSERT INTO "{name}" VALUES ({", ".join("?" * len(cols))})', vals)
    cur.execute('CREATE INDEX ix_surum_birim ON surumler(birim_id)')
    cur.execute('CREATE INDEX ix_kenar_kaynak ON kenarlar(kaynak)')
    cur.execute('CREATE INDEX ix_kenar_hedef ON kenarlar(hedef)')
    con.commit()
    con.close()
    return db_path


def _uri(nid: str) -> URIRef:
    safe = nid.replace(":", "/").replace("@", "/surum/").replace("!", "/olay/").replace("#", "-")
    return KD[safe]


def to_turtle(directory: Path = GRAPH, out: Path | None = None) -> Path:
    out = out or directory / "kademe.ttl"
    g = Graph()
    g.bind("kademe", KADEME)
    g.bind("kd", KD)
    g.bind("eli", ELI)
    for n in read_jsonl(directory / "normlar.jsonl"):
        u = _uri(n["id"])
        g.add((u, RDF.type, KADEME.Norm))
        g.add((u, RDFS.label, Literal(n["ad"], lang="tr")))
        g.add((u, KADEME.tur, Literal(n["tur"])))
        g.add((u, KADEME.katman, Literal(n["katman"], datatype=XSD.integer)))
        g.add((u, KADEME.cikaranKurum, Literal(n["kurum"])))
        g.add((u, KADEME.uygulanabilirlik, Literal(n["uygulanabilirlik"])))
        if n.get("resmi_gazete_tarih"):
            g.add((u, ELI.date_publication, Literal(n["resmi_gazete_tarih"], datatype=XSD.date)))
        if n.get("resmi_gazete_sayi"):
            g.add((u, KADEME.resmiGazeteSayi, Literal(n["resmi_gazete_sayi"])))
        if n.get("yururluk_baslangic"):
            g.add((u, ELI.first_date_entry_in_force, Literal(n["yururluk_baslangic"], datatype=XSD.date)))
    for b in read_jsonl(directory / "birimler.jsonl"):
        u = _uri(b["id"])
        g.add((u, RDF.type, KADEME.Birim))
        g.add((u, KADEME.birimTipi, Literal(b["tip"])))
        g.add((u, KADEME.numara, Literal(b["numara"])))
        g.add((u, ELI.is_part_of, _uri(b["ust"])))
        if b.get("baslik"):
            g.add((u, RDFS.label, Literal(b["baslik"], lang="tr")))
    for s in read_jsonl(directory / "surumler.jsonl"):
        u = _uri(s["id"])
        g.add((u, RDF.type, KADEME.Surum))
        g.add((u, KADEME.surumu, _uri(s["birim_id"])))
        if s.get("yururluk_baslangic"):
            g.add((u, KADEME.yururlukBaslangic, Literal(s["yururluk_baslangic"], datatype=XSD.date)))
        if s.get("yururluk_bitis"):
            g.add((u, KADEME.yururlukBitis, Literal(s["yururluk_bitis"], datatype=XSD.date)))
        g.add((u, KADEME.durum, Literal(s["durum"])))
        g.add((u, KADEME.baslangicKaynagi, Literal(s["baslangic_kaynagi"])))
        if s.get("metin"):
            g.add((u, KADEME.metin, Literal(s["metin"], lang="tr")))
    for o in read_jsonl(directory / "degisiklik_olaylari.jsonl"):
        u = _uri(o["id"])
        g.add((u, RDF.type, KADEME.DegisiklikOlayi))
        g.add((u, KADEME.olayTuru, Literal(o["tur"])))
        if o.get("tarih"):
            g.add((u, KADEME.tarih, Literal(o["tarih"], datatype=XSD.date)))
        if o.get("yururluk_tarihi"):
            g.add((u, KADEME.yururlukTarihi, Literal(o["yururluk_tarihi"], datatype=XSD.date)))
        g.add((u, KADEME.kaynak, Literal(o.get("kaynak") or "")))
    for k in read_jsonl(directory / "uygulanabilirlik.jsonl"):
        u = _uri(k["id"])
        g.add((u, RDF.type, KADEME.UygulanabilirlikKurali))
        g.add((u, KADEME.kosul, Literal(json.dumps(k["kosul"], ensure_ascii=False))))
        g.add((u, KADEME.etki, Literal(k["etki"])))
    pred = {"DAYANAK": KADEME.dayanak, "ATIF": KADEME.atif, "DEGISTIRIR": KADEME.degistirir,
            "UYGULANIR": KADEME.uygulanir}
    for e in read_jsonl(directory / "kenarlar.jsonl"):
        if e["tip"] in pred:
            g.add((_uri(e["kaynak"]), pred[e["tip"]], _uri(e["hedef"])))
    g.serialize(destination=str(out), format="turtle")
    return out
