"""README'deki otomatik bölümleri günceller.

README.md içinde şu işaretler arasındaki metin yeniden üretilir:
  <!-- RAPOR:sonuc -->      ...  <!-- /RAPOR:sonuc -->
  <!-- RAPOR:graf -->       ...  <!-- /RAPOR:graf -->
  <!-- RAPOR:kontrol -->    ...  <!-- /RAPOR:kontrol -->
  <!-- RAPOR:anlasma -->    ...  <!-- /RAPOR:anlasma -->

  python -m kademe.eval.rapor
"""
from __future__ import annotations

import json
import re

from kademe.paths import EVAL, GRAPH, ROOT


def _replace(text: str, key: str, body: str) -> str:
    pat = re.compile(rf"(<!-- RAPOR:{key} -->)(.*?)(<!-- /RAPOR:{key} -->)", re.S)
    return pat.sub(lambda m: f"{m.group(1)}\n{body.strip()}\n{m.group(3)}", text)


def sonuc_bolumu() -> str:
    p = EVAL / "results.json"
    if not p.exists():
        return "_Henüz çalıştırılmadı: `scripts/run_all.sh`._"
    r = json.loads(p.read_text(encoding="utf-8"))
    ay = r["ayarlar"]
    lines = [(EVAL / "results_table.md").read_text(encoding="utf-8").strip(), ""]
    lines.append(f"_Ayarlar: k={ay['k']}, yoğun model: `{ay['yogun_model']}`, reddetme eşiği (kosinüs): "
                 f"{ay['reddetme_esigi']}, {ay['bm25']}, füzyon: {ay['fuzyon']}, dizindeki madde-sürüm: "
                 f"{ay['dokuman_sayisi']}. Üretim: {r['uretim_zamani']}, {r['ortam']['platform']}._")
    abl = {k: v for k, v in r["sonuclar"].items() if k.startswith("B-")}
    if abl:
        lines += ["", "Bileşen ayrıştırması (tüm cevaplanabilir sorular; hiyerarşi kapsaması yalnız hiyerarşi soruları):", "",
                  "| Yapılandırma | Kesinlik@5 | Duyarlılık@5 | Yürürlük doğruluğu | Hiyerarşi kapsaması | Reddetme |",
                  "|---|---:|---:|---:|---:|---:|"]
        for ad in ["A_duz_rag", "B_kademe_lite", *abl]:
            o = r["sonuclar"][ad]["ozet"]
            c = o["cevaplanabilir"]
            lines.append(f"| {ad} | {c['kesinlik@5']:.2f} | {c['duyarlilik@5']:.2f} | {c['yururluk_dogrulugu']:.2f} | "
                         f"{o['hiyerarsi']['hiyerarsi_kapsamasi']:.2f} | {o['cevaplanamaz']['reddetme']:.2f} |")
    if r.get("esik_taramasi"):
        lines += ["", "Reddetme eşiği taraması (aday listesindeki en yüksek kosinüse göre; "
                      "`yanlış red` = cevaplanabilir sorunun boş dönme oranı):", "",
                  "| Eşik | A reddetme | A yanlış red | B reddetme | B yanlış red |", "|---:|---:|---:|---:|---:|"]
        for row in r["esik_taramasi"]:
            lines.append(f"| {row['esik']:.3f} | {row['A_reddetme']:.2f} | {row['A_yanlis_red']:.2f} | "
                         f"{row['B_reddetme']:.2f} | {row['B_yanlis_red']:.2f} |")
    return "\n".join(lines)


def graf_bolumu() -> str:
    st = json.loads((GRAPH / "graf_istatistikleri.json").read_text(encoding="utf-8"))
    pr = json.loads((GRAPH / "parse_raporu.json").read_text(encoding="utf-8"))
    s = pr["sayimlar"]
    de = st["dugum_etiket"]
    ke = st["kenar_tip"]
    lines = [
        "| Düğüm | Sayı | | Kenar | Sayı |",
        "|---|---:|---|---|---:|",
    ]
    dug = [("Norm", de.get("Norm", 0)), ("Birim (madde/fıkra/bent/alt bent)", de.get("Birim", 0)),
           ("Sürüm (madde düzeyi)", de.get("Surum", 0)), ("  └ metni olan", st["madde_surum_metinli"]),
           ("DegisiklikOlayi", de.get("DegisiklikOlayi", 0)),
           ("UygulanabilirlikKurali", de.get("UygulanabilirlikKurali", 0))]
    ken = [(k, ke.get(k, 0)) for k in ("DAYANAK", "ATIF", "DEGISTIRIR", "UYGULANIR", "PARCASI", "SURUMU")]
    for i in range(max(len(dug), len(ken))):
        a = dug[i] if i < len(dug) else ("", "")
        b = ken[i] if i < len(ken) else ("", "")
        lines.append(f"| {a[0]} | {a[1]} | | {b[0]} | {b[1]} |")
    bt = s["Birim_tip"]
    lines += ["", f"Birim tipleri: madde {bt.get('madde', 0)}, fıkra {bt.get('fikra', 0)}, bent {bt.get('bent', 0)}, "
                  f"alt bent {bt.get('alt_bent', 0)}.", ""]
    dz = st["surum_zinciri_uzunluk_dagilimi"]
    lines += ["Sürüm zinciri uzunluk dağılımı (madde başına sürüm sayısı → madde sayısı):", "",
              "| Uzunluk | " + " | ".join(dz) + " |", "|---|" + "---:|" * len(dz),
              "| Madde | " + " | ".join(str(v) for v in dz.values()) + " |", ""]
    bk = s["baslangic_kaynagi"]
    toplam = sum(bk.values())
    ad = {"tablo": "kanun yürürlük tablosu", "not": "değişiklik notu tarihi", "dipnot": "dipnot / akademik takvim notu",
          "dogum": "normun ya da ek maddenin yürürlüğü", "gozlem": "yalnızca arşiv gözlemi (yaklaşık)"}
    lines += ["Sürüm başlangıç tarihlerinin dayanağı:", ""]
    lines += [f"- {ad.get(k, k)}: {v} (%{100 * v / toplam:.0f})" for k, v in sorted(bk.items(), key=lambda x: -x[1])]
    lines += ["", "Norm başına:", "", "| Norm | Katman | Madde | Sürüm | Arşiv gözlemi | Yürürlük |",
              "|---|---:|---:|---:|---:|---|"]
    katman = {}
    for line in (GRAPH / "normlar.jsonl").read_text(encoding="utf-8").splitlines():
        n = json.loads(line)
        katman[n["id"]] = (n["katman"], n["ad"])
    for nid, v in pr["normlar"].items():
        k, ad_ = katman[nid]
        lines.append(f"| {ad_} (`{nid}`) | {k} | {v['madde']} | {v['surum']} | {v['tarihsel_gozlem']} | "
                     f"{v['yururluk']} ({v['yururluk_kaynagi']}) |")
    if pr.get("sorunlar"):
        lines += ["", "Ayrıştırma sırasında atlanan/sorunlu kaynaklar:", ""]
        lines += [f"- {x}" for x in pr["sorunlar"]]
    return "\n".join(lines)


def kontrol_bolumu() -> str:
    p = EVAL / "elle_kontrol.jsonl"
    if not p.exists():
        return "_Örneklem henüz üretilmedi: `python -m kademe.eval.ornekle`._"
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    done = [r for r in rows if r.get("kontrol")]
    if not done:
        return (f"**Durum: bekliyor.** `eval/elle_kontrol.jsonl` dosyasında {len(rows)} rastgele madde-sürüm "
                "(tohum 2026) kontrol için hazır; her satırın `kontrol` alanı yürütücü tarafından doldurulacak. "
                "Doldurulduktan sonra `python -m kademe.eval.rapor` bu bölümü oranlarla günceller.")
    metin = sum(1 for r in done if r["kontrol"].get("metin_dogru"))
    aralik = sum(1 for r in done if r["kontrol"].get("aralik_dogru"))
    return (f"{len(done)}/{len(rows)} sürüm kontrol edildi. Metin doğruluğu: {metin}/{len(done)} "
            f"(%{100 * metin / len(done):.0f}); yürürlük aralığı doğruluğu: {aralik}/{len(done)} "
            f"(%{100 * aralik / len(done):.0f}).")


def anlasma_bolumu() -> str:
    rows = [json.loads(l) for l in (EVAL / "yoksc_mini.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    both = [r for r in rows if r["dogrulama"].get("yurutucu") is not None and r["dogrulama"].get("ogrenci") is not None]
    if not both:
        return (f"**Durum: bekliyor.** {len(rows)} kaydın altın etiketleri yürütücü ve bir öğrenci tarafından "
                "bağımsız doğrulanacak (`dogrulama.yurutucu`, `dogrulama.ogrenci`: `true`/`false`). Doldurulunca "
                "anlaşma oranı ve Cohen kappa burada raporlanır.")
    a = [bool(r["dogrulama"]["yurutucu"]) for r in both]
    b = [bool(r["dogrulama"]["ogrenci"]) for r in both]
    po = sum(x == y for x, y in zip(a, b)) / len(both)
    pa, pb = sum(a) / len(a), sum(b) / len(b)
    pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    return f"{len(both)} kayıtta anlaşma oranı %{100 * po:.0f}, Cohen kappa {kappa:.2f}."


def main() -> int:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    for key, fn in (("sonuc", sonuc_bolumu), ("graf", graf_bolumu), ("kontrol", kontrol_bolumu),
                    ("anlasma", anlasma_bolumu)):
        text = _replace(text, key, fn())
    path.write_text(text, encoding="utf-8")
    print("README güncellendi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
