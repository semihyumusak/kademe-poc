"""Paragraf listesinden madde, fıkra ve bent yapısının çıkarılması.

Kanunlarda fıkralar numarasızdır (her paragraf bir fıkra), yönetmelik ve
yönergelerde "(1)", "(2)" ile numaralanır. Bentler "a)", "b)"; alt bentler
"1)", "2)" biçimindedir.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

MADDE_RE = re.compile(
    r"^(?P<pre>(?:GEÇİCİ|Geçici|GEÇICI|EK|Ek)\s+)?(?:MADDE|Madde|madde)\s+(?P<no>\d+)"
    r"(?:\s*/\s*(?P<harf>[A-ZÇĞİÖŞÜ])\b)?\s*(?:[-–—]+|:|\.(?!\d))\s*(?P<rest>.*)$"
)
FIKRA_RE = re.compile(r"^\((?P<no>\d+)\)\s*(?P<rest>.*)$")
BENT_RE = re.compile(r"^(?P<no>[a-zçğıöşü]{1,2})(?:\)|\.(?=\s+[A-ZÇĞİÖŞÜ(]))\s*(?P<rest>.*)$")
NOTE_ONLY_RE = re.compile(
    r"^(?:\((?:[^()]|\([^()]*\))*(?:Değişik|Ek|Mülga|İptal|Yeniden)(?:[^()]|\([^()]*\))*\)\s*)+$"
)
ALTBENT_RE = re.compile(r"^(?P<no>\d{1,2})\)\s*(?P<rest>.*)$")
BOLUM_RE = re.compile(r"^(?:[A-ZÇĞİÖŞÜ]+(?:\s+[A-ZÇĞİÖŞÜ]+)?\s+)?(?:BÖLÜM|KISIM)\b|^(?:BÖLÜM|KISIM)\s")
FOOTNOTE_RE = re.compile(r"^\[(?P<no>\d+)\]\s*(?P<rest>.+)$")
# Kanun sonundaki yürürlük tablosu ve benzeri ekler madde gövdesine katılmaz.
TAIL_RE = re.compile(
    r"SAYILI (?:KANUNA|KANUNUN|KANUNDA) EK VE DEĞİŞİKLİK (?:GETİREN|YAPAN)|YÜRÜRLÜĞE GİRİŞ TARİHİNİ GÖSTERİR"
    r"|YÜRÜRLÜKTEN KALDIRDIĞI KANUN"
    r"|^_{5,}$|^(?:Yönetmeliğin|Yönergenin) Yayımlandığı Resm[îi] Gazete", re.I
)
# Yönetmelik/yönerge sonundaki "(1) Bu değişiklik 2019-2020 eğitim-öğretim yılı ... yürürlüğe girer." dipnotları
TAIL_NOTE_RE = re.compile(r"^\((?P<no>\d+)\s*\)\s*(?P<rest>Bu (?:değişiklik|madde|hüküm).+)$")
# Kanunun sonundaki "ANA KANUNA İŞLENEMEYEN HÜKÜMLER": değiştiren kanunların kendi geçici maddeleri
ISLENEMEYEN_RE = re.compile(r"İŞLENEMEYEN HÜKÜMLER", re.I)
ISLENEMEYEN_BLOK_RE = re.compile(r"^\d+\)\s*\d{1,2}/\d{1,2}/\d{4}.*?(?P<no>\d{3,4})\s+[Ss]ayılı")
# Madde içermeyen belgeler (ör. "esaslar") için numaralı bölüm başlıkları: "6. YURT İÇİNDEN ..."
SECTION_RE = re.compile(r"^(?P<no>\d+)\.\s+(?P<rest>[A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜ ,'/-]{3,}.*)$")


@dataclass
class Bent:
    no: str
    metin: str
    alt: list["Bent"] = field(default_factory=list)


@dataclass
class Fikra:
    no: int
    metin: str
    bentler: list[Bent] = field(default_factory=list)


@dataclass
class Madde:
    key: str  # m44, m5A, em18, gm1
    no: str  # görüntülenen numara: "44", "Ek 18", "Geçici 1"
    baslik: str | None
    paragraflar: list[str]
    fikralar: list[Fikra] = field(default_factory=list)

    @property
    def metin(self) -> str:
        return "\n".join(self.paragraflar)


@dataclass
class ParsedDoc:
    baslik: str | None
    maddeler: list[Madde]
    dipnotlar: dict[str, str]
    onsoz: list[str]  # ilk maddeden önceki paragraflar (künye vb.)
    son_notlar: dict[str, str] = field(default_factory=dict)  # "(n) Bu değişiklik ..." notları


def madde_key(pre: str | None, no: str, harf: str | None = None) -> tuple[str, str]:
    pre = (pre or "").strip().lower()
    harf = (harf or "").upper()
    if pre.startswith("ge"):
        return f"gm{no}{harf}", f"Geçici {no}{('/' + harf) if harf else ''}"
    if pre.startswith("ek"):
        return f"em{no}{harf}", f"Ek {no}{('/' + harf) if harf else ''}"
    return f"m{no}{harf}", f"{no}{('/' + harf) if harf else ''}"


def _looks_like_title(p: str) -> bool:
    if len(p) > (200 if p.endswith(":") else 90) or MADDE_RE.match(p) or FIKRA_RE.match(p) or BENT_RE.match(p):
        return False
    if p.endswith((".", ";", ",")):
        return False
    return p[:1].isupper()


def _clean_title(p: str) -> str:
    # "İKİNCİ BÖLÜM Genel Hükümler Amaç:" gibi birleşik başlıklarda son öğeyi al.
    p = re.sub(r"\s*\[\d+\]", "", p).rstrip(":").strip()
    m = re.search(r"(?:BÖLÜM|KISIM)\s+(.*)$", p)
    if m:
        rest = m.group(1)
        # Bölüm adı + madde başlığı: büyük harfle başlayan son sözcük grubunu al.
        parts = re.split(r"\s+(?=[A-ZÇĞİÖŞÜ][a-zçğıöşü])", rest)
        p = parts[-1] if len(parts) > 1 else rest
    return p.strip()


def parse_paragraphs(paras: list[str], *, numarali_fikra: bool | None = None) -> ParsedDoc:
    maddeler: list[Madde] = []
    dipnotlar: dict[str, str] = {}
    onsoz: list[str] = []
    cur: Madde | None = None
    seen: dict[str, int] = {}
    in_tail = False
    prev: str | None = None
    son_notlar: dict[str, str] = {}
    madde_re = MADDE_RE if any(MADDE_RE.match(p) for p in paras) else SECTION_RE
    ih_prefix: str | None = None  # işlenemeyen hüküm bloğu: "ih4702-"
    for p in paras:
        if ISLENEMEYEN_RE.search(p) and not MADDE_RE.match(p):
            ih_prefix = "ih?-"
            prev = p
            continue
        if ih_prefix is not None:
            bm_ = ISLENEMEYEN_BLOK_RE.match(p)
            if bm_:
                ih_prefix = f"ih{bm_.group('no')}-"
                prev = p
                continue
        tn = TAIL_NOTE_RE.match(p)
        if tn and (in_tail or "eğitim" in p and "yürürlüğe" in p):
            son_notlar[tn.group("no")] = tn.group("rest")
            in_tail = True
            continue
        fn = FOOTNOTE_RE.match(p)
        if fn and (in_tail or cur is not None):
            dipnotlar[fn.group("no")] = fn.group("rest")
            in_tail = True
            continue
        if TAIL_RE.search(p):
            in_tail = True
        if in_tail:
            prev = p
            continue
        m = madde_re.match(p)
        if m:
            gd = m.groupdict()
            key, no = madde_key(gd.get("pre"), gd["no"], gd.get("harf"))
            if ih_prefix:
                key, no = ih_prefix + key, f"{no} ({ih_prefix[2:-1]} s. Kanun)"
            if key in seen:  # aynı numaralı ikinci madde (ör. farklı kanunlarla eklenen geçici maddeler)
                seen[key] += 1
                key = f"{key}-{seen[key]}"
            else:
                seen[key] = 1
            title = None
            if madde_re is SECTION_RE:
                title = _clean_title(_tr_capitalize(re.split(r"\s+\d+\.\d+\.", m.group("rest"))[0]))
            elif prev is not None and _looks_like_title(prev):
                title = _clean_title(prev)
                if cur is not None and cur.paragraflar and cur.paragraflar[-1] == prev:
                    cur.paragraflar.pop()
            cur = Madde(key=key, no=no, baslik=title, paragraflar=[p])
            maddeler.append(cur)
        elif cur is None:
            onsoz.append(p)
        elif BOLUM_RE.match(p):
            pass
        else:
            cur.paragraflar.append(p)
        prev = p
    # Bölüm başlıkları ve sonraki maddenin başlığı önceki maddenin sonuna yapışmış olabilir.
    for md in maddeler:
        while len(md.paragraflar) > 1 and _looks_like_title(md.paragraflar[-1]) and len(md.paragraflar[-1]) < 60 \
                and not md.paragraflar[-1].endswith(":"):
            md.paragraflar.pop()
    if numarali_fikra is None:
        numarali_fikra = sum(1 for md in maddeler for p in md.paragraflar[:1] if re.search(r"[-–—]\s*\(1\)", p)) \
            > len(maddeler) / 3
    for md in maddeler:
        md.fikralar = split_fikralar(md, numarali=numarali_fikra)
    baslik = onsoz[0] if onsoz else None
    return ParsedDoc(baslik=baslik, maddeler=maddeler, dipnotlar=dipnotlar, onsoz=onsoz, son_notlar=son_notlar)


def _strip_header(p: str) -> str:
    m = MADDE_RE.match(p)
    return m.group("rest").strip() if m else p


def split_fikralar(md: Madde, *, numarali: bool) -> list[Fikra]:
    paras = [_strip_header(md.paragraflar[0])] + md.paragraflar[1:]
    paras = _merge_note_only([p for p in paras if p])
    fikralar: list[Fikra] = []
    cur_f: Fikra | None = None
    cur_b: Bent | None = None
    for p in paras:
        lead, core = split_leading_notes(p)
        fm = FIKRA_RE.match(core)
        bm = BENT_RE.match(core)
        am = ALTBENT_RE.match(core)
        if lead:  # notu, eşleşen öğenin metnine geri ekle
            fm, bm, am = (_Relead(x, lead) if x else None for x in (fm, bm, am))
        new_f = False
        if numarali:
            # "(1)" yönetmelikte fıkradır; ancak bent içinde "(1)" alt bent olarak da kullanılabilir.
            if fm and (cur_f is None or int(fm.group("no")) == cur_f.no + 1):
                new_f = True
            elif fm and cur_b is not None:
                cur_b.alt.append(Bent(no=fm.group("no"), metin=fm.group("rest")))
                continue
        else:
            # Kanun: bent ya da alt bent değilse her paragraf yeni fıkra.
            if fm and cur_b is not None:  # kanunda "(1)" alt bent
                cur_b.alt.append(Bent(no=fm.group("no"), metin=fm.group("rest")))
                continue
            bent_bekliyor = cur_b is not None and bool(NOTE_ONLY_RE.match(cur_b.metin))
            new_f = not bm and not (am and cur_b is not None) and not bent_bekliyor
        if new_f or cur_f is None:
            no = int(fm.group("no")) if (numarali and fm) else len(fikralar) + 1
            text = fm.group("rest") if (numarali and fm) else p
            cur_f = Fikra(no=no, metin=text)
            fikralar.append(cur_f)
            cur_b = None
            if bm and not (numarali and fm):
                cur_b = Bent(no=bm.group("no"), metin=bm.group("rest"))
                cur_f.bentler.append(cur_b)
            continue
        if bm:
            cur_b = Bent(no=bm.group("no"), metin=bm.group("rest"))
            cur_f.bentler.append(cur_b)
        elif am and cur_b is not None:
            cur_b.alt.append(Bent(no=am.group("no"), metin=am.group("rest")))
        elif cur_b is not None and (not numarali or NOTE_ONLY_RE.match(cur_b.metin)):
            cur_b.metin += " " + p
        else:
            cur_f.metin += " " + p
    return fikralar


def _merge_note_only(paras: list[str]) -> list[str]:
    """Yalnızca değişiklik notundan oluşan paragrafı izleyen paragrafla birleştirir."""
    out: list[str] = []
    carry = ""
    for p in paras:
        if NOTE_ONLY_RE.match(p) and "Mülga" not in p and "İptal" not in p:
            carry = f"{carry} {p}".strip()
            continue
        out.append(f"{carry} {p}".strip() if carry else p)
        carry = ""
    if carry:
        out.append(carry)
    return out


LEADING_NOTE_RE = re.compile(r"^((?:\((?:[^()]|\([^()]*\))*(?:Değişik|Ek|Mülga|İptal|Yeniden)(?:[^()]|\([^()]*\))*\)\s*)+)(.*)$")


def split_leading_notes(p: str) -> tuple[str, str]:
    m = LEADING_NOTE_RE.match(p)
    if not m or not m.group(2):
        return "", p
    return m.group(1).strip(), m.group(2)


class _Relead:
    """re.Match benzeri sarmalayıcı: 'rest' grubunun başına baştaki notu ekler."""

    def __init__(self, m: re.Match, lead: str):
        self._m, self._lead = m, lead

    def group(self, name: str) -> str:
        v = self._m.group(name)
        return f"{self._lead} {v}".strip() if name == "rest" else v


def _tr_capitalize(s: str) -> str:
    from kademe.parse.text import tr_lower

    s = tr_lower(s.strip())
    return (s[:1].replace("i", "İ").upper() + s[1:]) if s else s
