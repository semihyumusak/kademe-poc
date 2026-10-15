"""Ham belgelerden graf JSONL dosyalarını üretir: python -m kademe.parse

Çıktılar (data/graph/):
  normlar.jsonl              Norm düğümleri
  birimler.jsonl             Birim düğümleri (madde, fıkra, bent, alt bent)
  surumler.jsonl             Sürüm düğümleri (madde düzeyinde zincir)
  degisiklik_olaylari.jsonl  DegisiklikOlayi düğümleri
  uygulanabilirlik.jsonl     UygulanabilirlikKurali düğümleri
  kenarlar.jsonl             DAYANAK, ATIF, DEGISTIRIR, UYGULANIR, PARCASI kenarları
  parse_raporu.json          sayımlar ve sorunlar
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

from kademe.corpus import NORMS, NormSpec
from kademe.parse import akademik, notes as notes_mod, refs as refs_mod, yururluk
from kademe.parse.structure import Bent, Madde, ParsedDoc, parse_paragraphs
from kademe.parse.text import paragraphs, tr_lower
from kademe.parse.versions import _TAIL_CUT, Gozlem, SurumTaslak, build_chain, temizle
from kademe.paths import GRAPH, RAW

# Atıf çözümlemesi için ayırt edici ad parçaları (tr_lower).
ALIASES = [
    refs_mod.NormAlias("kanun:2547", "2547", ("yükseköğretim kanunu",)),
    refs_mod.NormAlias("yonetmelik:21510", None, ("lisansüstü eğitim ve öğretim yönetmeliğ", "20/4/2016 tarihli ve 29690")),
    refs_mod.NormAlias("yonetmelik:13948", None, ("programlar arasında geçiş, çift anadal, yan dal", "24/4/2010 tarihli ve 27561")),
    refs_mod.NormAlias("yonetmelik:24672", None, ("öğretim üyeliğine yükseltilme ve atanma yönetmeliğ",)),
    refs_mod.NormAlias("yonetmelik:21475", None, ("yabancı dil öğretimi ve yabancı dille öğretim", "29662 sayılı")),
    refs_mod.NormAlias("yonetmelik:15287", None, ("lisans eğitim-öğretim ve sınav yönetmeliğ", "lisans eğitim öğretim ve sınav yönetmeliğ", "28052 sayılı")),
    refs_mod.NormAlias("yonetmelik:42791", None, ("lisansüstü eğitim-öğretim yönetmeliğ", "33114 sayılı")),
    refs_mod.NormAlias("yonerge:etu-cap", None, ("çift anadal programı yönergesi",)),
    refs_mod.NormAlias("yonerge:etu-yandal", None, ("yandal programı yönergesi",)),
    refs_mod.NormAlias("usul_esas:etu-yatay-gecis", None, ("yatay geçiş esasları",)),
    refs_mod.NormAlias("yonerge:etu-ortak-egitim", None, ("ortak eğitim yönergesi",)),
    refs_mod.NormAlias("yonerge:etu-hazirlik", None, ("hazırlık programı eğitim-öğretim esaslarına ilişkin yönerge",)),
]

SENATO_RE = re.compile(r"(\d{1,2}[./]\d{1,2}[./]\d{4})\s*tarih\w*\s*(?:ve\s*)?(S-?\d{4}-[\d/]+|\d+/\d+)?\s*sayılı\s*Senato", re.I)


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _fetch_date(spec: NormSpec) -> date:
    man = RAW / "manifest.jsonl"
    rel = f"{spec.raw_name}/current."
    found = None
    if man.exists():
        for line in man.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["path"].startswith(rel):
                found = datetime.fromisoformat(row["fetched_at"]).date()
    return found or date.today()


def _snapshots(spec: NormSpec) -> list[tuple[date, Path]]:
    d = RAW / spec.raw_name / "wayback"
    out = []
    if d.exists():
        for f in sorted(d.iterdir()):
            if f.suffix.lower() in (".pdf", ".html", ".docx") and re.match(r"\d{14}", f.stem):
                out.append((date(int(f.stem[:4]), int(f.stem[4:6]), int(f.stem[6:8])), f))
    return out


def norm_yururluk(spec: NormSpec, doc: ParsedDoc) -> tuple[date | None, str]:
    """Normun ilk yürürlük tarihi ve dayanağı."""
    yur = next((m for m in doc.maddeler if m.baslik and "yürürlük" == tr_lower(m.baslik).strip()), None)
    if yur is not None:
        t = yur.metin
        ak = akademik.akademik_tarih(t)
        if ak and "yürürlüğe" in t and not (spec.rg_tarih and "yayımı tarihinde" in t):
            return ak, "yururluk_maddesi_akademik"
        if "Senato" in t or "senato" in t:
            m = SENATO_RE.search(t) or SENATO_RE.search(" ".join(doc.onsoz))
            if m:
                return notes_mod.parse_date(m.group(1)), "senato_karari"
    if spec.rg_tarih:
        return date.fromisoformat(spec.rg_tarih), "resmi_gazete"
    m = SENATO_RE.search(" ".join(doc.onsoz))
    if m:
        return notes_mod.parse_date(m.group(1)), "senato_karari"
    return None, "bilinmiyor"


def son_not_isaretleri(text: str, son_notlar: dict[str, str]) -> list[tuple[Not_, date]]:
    """Notu izleyen "(n)" işaretini sondaki "Bu değişiklik ... yürürlüğe girer" notuna bağlar."""
    out = []
    # İşaret notla aynı satırda olmalı; satır başındaki "(1)" fıkra numarasıdır.
    for m in re.finditer(rf"({notes_mod.NOTE_RE.pattern})[ \t]*\((\d)[ \t]*\)", text):
        n_no = m.groups()[-1]
        if n_no in son_notlar:
            ns = notes_mod.parse_notes(m.group(1))
            d = akademik.akademik_tarih(son_notlar[n_no])
            # Yürürlük, değişikliğin yayımından önce olamaz (en fazla bir aylık takvim yuvarlaması).
            if ns and d and (ns[0].tarih is None or d.toordinal() >= ns[0].tarih.toordinal() - 31):
                out.append((ns[0], d))
    return out


Not_ = notes_mod.Not


def birim_records(norm_id: str, md: Madde, sira: int) -> list[dict]:
    mid = f"{norm_id}/{md.key}"
    recs = [{"id": mid, "norm_id": norm_id, "tip": "madde", "numara": md.no, "anahtar": md.key,
             "baslik": md.baslik, "ust": norm_id, "sira": sira}]

    seen: set[str] = {mid}

    def uniq(x: str) -> str:
        y, k = x, 2
        while y in seen:
            y, k = f"{x}_{k}", k + 1
        seen.add(y)
        return y

    def bent(parent: str, b: Bent, tip: str, j: int):
        bid = uniq(f"{parent}/{'b' if tip == 'bent' else 'a'}{b.no}")
        recs.append({"id": bid, "norm_id": norm_id, "tip": tip, "numara": b.no, "ust": parent, "sira": j,
                     "metin": b.metin})
        for k, a in enumerate(b.alt):
            bent(bid, a, "alt_bent", k)

    for i, f in enumerate(md.fikralar):
        fid = uniq(f"{mid}/f{f.no}")
        recs.append({"id": fid, "norm_id": norm_id, "tip": "fikra", "numara": str(f.no), "ust": mid, "sira": i,
                     "metin": f.metin})
        for j, b in enumerate(f.bentler):
            bent(fid, b, "bent", j)
    return recs


KURAL_KOSUL_RE = [
    # "2011-2012 eğitim-öğretim yılı öncesinde kayıt yaptırmış öğrenciler"
    (re.compile(r"(\d{4})\s*-\s*\d{4}\s+eğitim[\s-]*öğretim\s+yılı\w*\s+(öncesinde|önce|başından önce)\s+[^.]{0,60}?(kayıt\s+yaptır\w*|kaydol\w*|kayıtlı|kayıt\s+olan)", re.I), "giris_once_yil"),
    (re.compile(r"(\d{4})\s*-\s*\d{4}\s+eğitim[\s-]*öğretim\s+yılı\w*\s+(?:ve sonrasında|itibaren|sonra)\s+[^.]{0,60}?(kayıt\s+yaptır\w*|kaydol\w*|kayıt\s+olan)", re.I), "giris_sonra_yil"),
    # "yürürlüğe girdiği / yayımı tarihinden önce ... kayıt yaptıran"
    (re.compile(r"(yürürlüğe\s+girdiği|yayımı)\s+tarih\w*\s+önce\s+[^.]{0,120}?(kayıt\s+yaptır\w*|kaydol\w*|kayıtlı|kayıt\s+olan|başlayan)", re.I), "giris_once_yururluk"),
]


def uygulanabilirlik_kurallari(norm_id: str, md: Madde, gecerli_tarih: date | None, son_notlar: dict) -> list[dict]:
    """Geçici/intibak maddelerinden giriş dönemine bağlı uygulama kurallarını çıkarır."""
    if not md.key.startswith("gm") and not (md.baslik and re.search(r"intibak|geçiş", tr_lower(md.baslik))):
        return []
    out = []
    for fi, f in enumerate(md.fikralar or []):
        t = f.metin + " " + " ".join(b.metin for b in f.bentler)
        for rx, tip in KURAL_KOSUL_RE:
            m = rx.search(t)
            if not m:
                continue
            if tip == "giris_once_yil":
                esik, op = date(int(m.group(1)), 9, 1), "once"
            elif tip == "giris_sonra_yil":
                esik, op = date(int(m.group(1)), 9, 1), "sonra"
            else:
                notlar = notes_mod.parse_notes(md.metin)
                esik = next((n.tarih for n in notlar if n.tur == "ekleme"), None) or gecerli_tarih
                op = "once"
            if esik is None:
                continue
            hedefler = sorted({r.madde for r in refs_mod.extract_refs(t, self_norm=norm_id, self_tur="", aliases=[])
                               if r.hedef_norm == norm_id and r.madde != md.key})
            if re.search(r"uygulanmaz|önceki hükümler|eski hükümler|kayıt\w* oldukları tarihte|tabi oldukları|"
                         r"mevcut hükümler", t):
                etki = "onceki_surum"
            elif re.search(r"uygulanmaya başlanır|uygulanır", t):
                etki = "baslangic_ertele"
            else:
                etki = "onceki_surum"
            ertele = akademik.akademik_tarih(t[m.end():]) if etki == "baslangic_ertele" else None
            out.append({
                "id": f"{norm_id}/{md.key}/kural{len(out) + 1}",
                "kaynak_birim": f"{norm_id}/{md.key}",
                "norm_id": norm_id,
                "hedef_maddeler": [f"{norm_id}/{h}" for h in hedefler] or [norm_id],
                "kosul": {"giris": op, "esik": esik.isoformat()},
                "etki": etki,
                "ertele_tarihi": _iso(ertele),
                "metin": t[:600],
            })
            break
    return out


def build(only: list[str] | None = None) -> dict:
    normlar, birimler, surumler, olaylar, kurallar, kenarlar = [], [], [], [], [], []
    rapor: dict = {"normlar": {}, "sorunlar": []}
    docs: dict[str, ParsedDoc] = {}
    for spec in NORMS:
        if only and spec.id not in only:
            continue
        cur_path = next((RAW / spec.raw_name).glob("current.*"), None)
        if cur_path is None:
            rapor["sorunlar"].append(f"{spec.id}: ham dosya yok (önce fetch çalıştırın)")
            continue
        doc = parse_paragraphs(paragraphs(cur_path))
        if not doc.maddeler:
            rapor["sorunlar"].append(f"{spec.id}: madde bulunamadı; kapsam dışı bırakıldı")
            continue
        docs[spec.id] = doc
        fetch_d = _fetch_date(spec)
        yur, yur_kaynak = norm_yururluk(spec, doc)
        tablo = yururluk.parse_table(cur_path) if spec.tur == "kanun" and cur_path.suffix == ".html" else {}

        # tarihsel gözlemler
        hist: list[tuple[date, str, ParsedDoc]] = []
        for d, f in _snapshots(spec):
            try:
                hdoc = parse_paragraphs(paragraphs(f))
            except Exception as exc:  # pragma: no cover - bozuk arşiv dosyası
                rapor["sorunlar"].append(f"{spec.id}: {f.name} okunamadı ({type(exc).__name__}; bozuk ya da PDF olmayan arşiv kopyası)")
                continue
            if len(hdoc.maddeler) < max(3, len(doc.maddeler) // 4):
                rapor["sorunlar"].append(f"{spec.id}: {f.name} yetersiz ayrıştırıldı ({len(hdoc.maddeler)} madde); atlandı")
                continue
            hist.append((d, f"wayback:{f.stem}", hdoc))

        dip_olay = {k: notes_mod.footnote_event(v) for k, v in doc.dipnotlar.items()}
        normlar.append({
            "id": spec.id, "ad": spec.ad, "tur": spec.tur, "katman": spec.katman, "kurum": spec.kurum,
            "resmi_gazete_tarih": spec.rg_tarih, "resmi_gazete_sayi": spec.rg_sayi,
            "uygulanabilirlik": spec.uygulanabilirlik, "yururluk_baslangic": _iso(yur),
            "yururluk_kaynagi": yur_kaynak, "kaynak_url": spec.url, "mevzuat_kod": spec.mevzuat_kod,
            "erisim_tarihi": fetch_d.isoformat(), "tarihsel_gozlem_sayisi": len(hist), "notlar": spec.notlar,
        })
        kenar_parcasi = []
        n_surum = 0
        zincir_uzunluk = []
        for sira, md in enumerate(doc.maddeler):
            brs = birim_records(spec.id, md, sira)
            birimler.extend(brs)
            for b in brs:
                kenar_parcasi.append({"tip": "PARCASI", "kaynak": b["id"], "hedef": b["ust"]})
            # gözlemler
            ek = [dip_olay[n] for n in notes_mod.FOOTNOTE_REF_RE.findall(md.metin) if dip_olay.get(n)]
            gz = [Gozlem(tarih=fetch_d, metin=_TAIL_CUT.sub("", md.metin).strip(), kaynak="guncel", baslik=md.baslik, ek_notlar=ek)]
            for d, src, hdoc in hist:
                hm = next((x for x in hdoc.maddeler if x.key == md.key), None)
                if hm is not None:
                    gz.append(Gozlem(tarih=d, metin=temizle(hm.metin), kaynak=src))
            akad = {n.ham: d for n, d in son_not_isaretleri(md.metin, doc.son_notlar)}

            def etkin(n: Not_, _key=md.key) -> tuple[date | None, str]:
                if n.ham in akad:
                    return akad[n.ham], "dipnot"
                if tablo:
                    d, from_tab = yururluk.yururluk_tarihi(tablo, n.kaynak_no, _key, n.tarih)
                    if n.aynen_kabul is None or from_tab:
                        return d, "tablo" if from_tab else "not"
                return n.tarih, "not"

            chain = build_chain(gz, dogum=yur, etkin_tarih=etkin, aday_olaylar=ek)
            zincir_uzunluk.append(len(chain))
            mid = f"{spec.id}/{md.key}"
            for k, s in enumerate(chain):
                sid = f"{mid}@{_iso(s.baslangic) or 'bilinmiyor'}"
                if any(x["id"] == sid for x in surumler[-len(chain):]):
                    sid = f"{sid}#{k}"
                surumler.append({
                    "id": sid, "birim_id": mid, "norm_id": spec.id, "sira": k,
                    "metin": s.metin, "metin_mevcut": s.metin_mevcut, "baslik": md.baslik,
                    "yururluk_baslangic": _iso(s.baslangic), "yururluk_bitis": _iso(s.bitis),
                    "baslangic_kaynagi": s.baslangic_kaynagi, "durum": s.durum,
                    "baslangic_belirsizlik": [_iso(x) for x in s.belirsizlik] if s.belirsizlik else None,
                    "gozlemler": s.gozlemler,
                    "kaynak_notu": "; ".join(n.ham for n in s.notlar if not n.kapsam.startswith("ibare (dipnot)"))[:800] or None,
                })
                n_surum += 1
                # değişiklik olayları: sürümü başlatan notlar
                for n in s.notlar:
                    d, src = etkin(n)
                    if d != s.baslangic:
                        continue
                    oid = f"{mid}!{n.tur}@{_iso(n.tarih)}#{len(olaylar)}"
                    olaylar.append({
                        "id": oid, "tur": n.tur, "kapsam": n.kapsam or "madde", "tarih": _iso(n.tarih),
                        "yururluk_tarihi": _iso(d), "yururluk_kaynagi": src, "kaynak": n.kaynak,
                        "kaynak_norm_no": n.kaynak_no, "aynen_kabul": n.aynen_kabul, "hedef_birim": mid,
                        "ham": n.ham,
                    })
                    kenarlar.append({"tip": "DEGISTIRIR", "kaynak": oid, "hedef": sid})
            for kural in uygulanabilirlik_kurallari(spec.id, md, yur, doc.son_notlar):
                kurallar.append(kural)
        kenarlar.extend(kenar_parcasi)
        rapor["normlar"][spec.id] = {
            "madde": len(doc.maddeler), "surum": n_surum, "tarihsel_gozlem": len(hist),
            "zincir_uzunlugu": dict(sorted(Counter(zincir_uzunluk).items())),
            "dipnot": len(doc.dipnotlar), "yururluk": _iso(yur), "yururluk_kaynagi": yur_kaynak,
        }

    # ---------------------------------------------------------------- atıf ve dayanak
    birim_ids = {b["id"] for b in birimler}
    norm_tur = {n["id"]: n["tur"] for n in normlar}
    dayanak_kanun: dict[str, str] = {}
    dis_atif = Counter()
    for nid, doc in docs.items():
        for md in doc.maddeler:
            if not refs_mod.is_dayanak_madde(md.baslik, md.metin):
                continue
            rs = refs_mod.extract_refs(md.metin, self_norm=nid, self_tur=norm_tur[nid], aliases=ALIASES)
            hedef_normlar = set()
            for r in rs:
                if r.hedef_norm and r.hedef_norm != nid:
                    tid = f"{r.hedef_norm}/{r.madde}"
                    if tid not in birim_ids:
                        rapor["sorunlar"].append(f"DAYANAK hedefi bulunamadı: {nid} -> {tid}")
                        continue
                    kenarlar.append({"tip": "DAYANAK", "kaynak": nid, "hedef": tid, "fikra": r.fikra,
                                     "bent": r.bent, "metin": r.metin, "kaynak_madde": f"{nid}/{md.key}"})
                    hedef_normlar.add(r.hedef_norm)
                    if norm_tur.get(r.hedef_norm) == "kanun":
                        dayanak_kanun.setdefault(nid, r.hedef_norm)
            for t in refs_mod.dayanak_norm_mentions(md.metin, ALIASES, nid):
                if t not in hedef_normlar and t in norm_tur:
                    kenarlar.append({"tip": "DAYANAK", "kaynak": nid, "hedef": t, "fikra": None, "bent": None,
                                     "metin": None, "kaynak_madde": f"{nid}/{md.key}"})
            break
    # Dayanak zincirinden kanunu devral (yönerge -> yönetmelik -> kanun)
    for nid in docs:
        if nid not in dayanak_kanun and norm_tur[nid] != "kanun":
            dayanak_kanun[nid] = "kanun:2547"

    atif_seen = set()
    for s in surumler:
        if not s["metin"]:
            continue
        nid = s["norm_id"]
        rs = refs_mod.extract_refs(s["metin"], self_norm=nid, self_tur=norm_tur[nid], aliases=ALIASES,
                                   varsayilan_kanun=dayanak_kanun.get(nid))
        for r in rs:
            if r.dis_kanun:
                dis_atif[r.dis_kanun] += 1
                continue
            if not r.hedef_norm:
                continue
            tid = f"{r.hedef_norm}/{r.madde}"
            if tid not in birim_ids:
                continue
            if tid == s["birim_id"]:
                continue
            fid = f"{tid}/f{r.fikra}" if r.fikra else None
            if fid and fid in birim_ids:
                tid = fid
            key = (s["birim_id"], tid)
            if key in atif_seen:
                for e in reversed(kenarlar):
                    if e["tip"] == "ATIF" and (e["kaynak"], e["hedef"]) == key:
                        if s["id"] not in e["surumler"]:
                            e["surumler"].append(s["id"])
                        break
                continue
            atif_seen.add(key)
            kenarlar.append({"tip": "ATIF", "kaynak": s["birim_id"], "hedef": tid, "metin": r.metin,
                             "cozum": r.cozum, "surumler": [s["id"]]})

    # UYGULANIR: kural -> hedef maddenin kural eşiğinden önce yürürlükte olan sürümü
    for k in kurallar:
        esik = k["kosul"]["esik"]
        for h in k["hedef_maddeler"]:
            hedef_s = [s for s in surumler if s["birim_id"] == h and s["metin_mevcut"]]
            if not hedef_s:
                continue
            if k["etki"] == "onceki_surum":
                aday = [s for s in hedef_s if (s["yururluk_baslangic"] or "") < esik]
                sec = aday[-1] if aday else None
            else:
                sec = hedef_s[-1]
            if sec:
                kenarlar.append({"tip": "UYGULANIR", "kaynak": k["id"], "hedef": sec["id"], "kosul": k["kosul"],
                                 "etki": k["etki"]})

    rapor["sayimlar"] = {
        "Norm": len(normlar), "Birim": len(birimler),
        "Birim_tip": dict(Counter(b["tip"] for b in birimler)),
        "Surum": len(surumler), "Surum_metinli": sum(1 for s in surumler if s["metin_mevcut"]),
        "Surum_mulga": sum(1 for s in surumler if s["durum"] == "mulga"),
        "DegisiklikOlayi": len(olaylar), "UygulanabilirlikKurali": len(kurallar),
        "kenarlar": dict(Counter(e["tip"] for e in kenarlar)),
        "baslangic_kaynagi": dict(Counter(s["baslangic_kaynagi"] for s in surumler)),
        "atif_cozum": dict(Counter(e["cozum"] for e in kenarlar if e["tip"] == "ATIF")),
        "korpus_disi_kanun_atiflari": dict(dis_atif.most_common(15)),
    }
    zl = Counter()
    by_birim = defaultdict(int)
    for s in surumler:
        by_birim[s["birim_id"]] += 1
    for v in by_birim.values():
        zl[v] += 1
    rapor["sayimlar"]["surum_zinciri_uzunluk_dagilimi"] = dict(sorted(zl.items()))
    out = {
        "normlar": normlar, "birimler": birimler, "surumler": surumler,
        "degisiklik_olaylari": olaylar, "uygulanabilirlik": kurallar, "kenarlar": kenarlar,
    }
    return out, rapor


def write(out: dict, rapor: dict) -> None:
    for name, rows in out.items():
        with (GRAPH / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (GRAPH / "parse_raporu.json").write_text(json.dumps(rapor, ensure_ascii=False, indent=1), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kademe.parse", description=__doc__)
    ap.add_argument("--only", action="append")
    args = ap.parse_args(argv)
    out, rapor = build(args.only)
    write(out, rapor)
    print(json.dumps(rapor["sayimlar"], ensure_ascii=False, indent=1))
    for s in rapor["sorunlar"][:30]:
        print("  !", s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
