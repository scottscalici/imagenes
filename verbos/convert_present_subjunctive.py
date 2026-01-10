#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from copy import deepcopy

# ---------------- CONFIG ----------------

SOURCE_TENSE = "presente"                 # change if your present file uses a different label
TARGET_TENSE = "subjuntivo presente"

KEY_INFINITIVE = "infinitivo"
KEY_TENSE = "tiempo"
KEY_SUBJECT = "sujeto"
KEY_PERSONA_BASE = "persona_base"
KEY_FORM = "forma"
KEY_TRANSLATION = "traducción"

TRANSLATION_PREFIX = "SUBJUNCTIVE CONTEXT: "

# Persona keys we will generate/lookup
BOOT = {"yo", "tú", "él/ella/Ud.", "ellos/ellas/Uds."}

# Normalize persona_base variants you might have
PERSONA_MAP = {
  "yo": "yo",
  "tú": "tú",
  "tu": "tú",
  "nosotros": "nosotros",
  "vosotros": "vosotros",

  # common 3rd-sing labels
  "él": "él/ella/Ud.",
  "ella": "él/ella/Ud.",
  "usted": "él/ella/Ud.",
  "él/ella/ud.": "él/ella/Ud.",
  "él/ella/ud": "él/ella/Ud.",
  "él/ella/usted": "él/ella/Ud.",
  "él/ella/Ud.": "él/ella/Ud.",
  "él/ella/Ud": "él/ella/Ud.",

  # common 3rd-pl labels
  "ellos": "ellos/ellas/Uds.",
  "ellas": "ellos/ellas/Uds.",
  "ustedes": "ellos/ellas/Uds.",
  "ellos/ellas/uds.": "ellos/ellas/Uds.",
  "ellos/ellas/uds": "ellos/ellas/Uds.",
  "ellos/ellas/Uds.": "ellos/ellas/Uds.",
  "ellos/ellas/Uds": "ellos/ellas/Uds.",
}

# 6 “super irregulars” (full present subjunctive)
IRREGULAR_FULL = {
  "ser":     {"yo":"sea","tú":"seas","él/ella/Ud.":"sea","nosotros":"seamos","vosotros":"seáis","ellos/ellas/Uds.":"sean"},
  "ir":      {"yo":"vaya","tú":"vayas","él/ella/Ud.":"vaya","nosotros":"vayamos","vosotros":"vayáis","ellos/ellas/Uds.":"vayan"},
  "dar":     {"yo":"dé","tú":"des","él/ella/Ud.":"dé","nosotros":"demos","vosotros":"deis","ellos/ellas/Uds.":"den"},
  "estar":   {"yo":"esté","tú":"estés","él/ella/Ud.":"esté","nosotros":"estemos","vosotros":"estéis","ellos/ellas/Uds.":"estén"},
  "saber":   {"yo":"sepa","tú":"sepas","él/ella/Ud.":"sepa","nosotros":"sepamos","vosotros":"sepáis","ellos/ellas/Uds.":"sepan"},
  "haber":   {"yo":"haya","tú":"hayas","él/ella/Ud.":"haya","nosotros":"hayamos","vosotros":"hayáis","ellos/ellas/Uds.":"hayan"},
}

# Subjunctive endings
ENDINGS_AR = {"yo":"e","tú":"es","él/ella/Ud.":"e","nosotros":"emos","vosotros":"éis","ellos/ellas/Uds.":"en"}
ENDINGS_ER_IR = {"yo":"a","tú":"as","él/ella/Ud.":"a","nosotros":"amos","vosotros":"áis","ellos/ellas/Uds.":"an"}

# ---------------- HELPERS ----------------

def norm_persona(p: str) -> str:
    p0 = (p or "").strip()
    return PERSONA_MAP.get(p0, p0)

def verb_class(inf: str) -> str:
    inf = (inf or "").strip().lower()
    if inf.endswith("ar"): return "ar"
    if inf.endswith("er"): return "er"
    if inf.endswith("ir"): return "ir"
    return ""

def safe_strip_suffix(s: str, suffix: str) -> str:
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s

def derive_base_stem_from_present(rows_by_persona: dict, cls: str) -> str | None:
    """
    For AR/ER boot-changers, nosotros/vosotros should use non-boot stem.
    We derive that from the present indicative nosotros form, if available.
    """
    nos = rows_by_persona.get("nosotros")
    if not nos:
        return None
    form = (nos.get(KEY_FORM) or "").strip()
    if cls == "ar":
        return safe_strip_suffix(form, "amos")
    if cls == "er":
        return safe_strip_suffix(form, "emos")
    if cls == "ir":
        return safe_strip_suffix(form, "imos")
    return None

def yo_stem_from_yo_form(yo_form: str) -> str:
    yo_form = (yo_form or "").strip()
    # regular: hablo -> habl ; tengo -> teng ; conozco -> conozc
    if yo_form.endswith("o") and len(yo_form) > 1:
        return yo_form[:-1]
    # fallback (for weird data); better than crashing
    return yo_form

def apply_car_gar_zar(inf: str, stem: str, next_vowel: str) -> str:
    """
    Only needed when the ending begins with 'e' (subjunctive of -AR verbs).
    buscar -> busqu- ; llegar -> llegu- ; empezar -> empiec-
    """
    inf = (inf or "").lower().strip()
    if next_vowel != "e":
        return stem
    if inf.endswith("car") and stem.endswith("c"):
        return stem[:-1] + "qu"
    if inf.endswith("gar") and stem.endswith("g"):
        return stem[:-1] + "gu"
    if inf.endswith("zar") and stem.endswith("z"):
        return stem[:-1] + "c"
    return stem

def last_replace(s: str, old: str, new: str) -> str:
    i = s.rfind(old)
    if i == -1:
        return s
    return s[:i] + new + s[i+len(old):]

def detect_ir_nosvos_shift(base_stem: str, yo_stem: str) -> str | None:
    """
    Heuristic:
    - if base has 'o' and yo has 'ue' => o->u for nos/vos
    - if base has 'e' and yo has 'ie' => e->i for nos/vos
    - if base has 'e' and yo has 'i'  => e->i (pedir: pido)
    """
    b = base_stem
    y = yo_stem
    if "o" in b and "ue" in y:
        return "o->u"
    if "e" in b and "ie" in y:
        return "e->i"
    if "e" in b and "i" in y:
        # covers pedir-type and other e->i
        return "e->i"
    return None

def build_present_subj_form(inf: str, cls: str, persona: str, yo_stem: str, base_stem: str | None) -> str:
    # irregular full set
    inf_l = inf.lower()
    if inf_l in IRREGULAR_FULL:
        return IRREGULAR_FULL[inf_l][persona]

    endings = ENDINGS_AR if cls == "ar" else ENDINGS_ER_IR
    ending = endings[persona]
    next_vowel = ending[0]  # 'e' or 'a'

    # choose stem
    if persona in BOOT:
        stem = yo_stem
    else:
        # nosotros/vosotros
        if cls in ("ar", "er"):
            stem = base_stem or yo_stem
        else:
            # IR: nosotros/vosotros use preterite-style shift if it’s a boot stem-changer
            base = base_stem or (inf[:-2] if len(inf) > 2 else yo_stem)
            shift = detect_ir_nosvos_shift(base, yo_stem)
            if shift == "o->u":
                stem = last_replace(base, "o", "u")
            elif shift == "e->i":
                stem = last_replace(base, "e", "i")
            else:
                stem = base

    # spelling changes for -car/-gar/-zar when next vowel is 'e'
    stem = apply_car_gar_zar(inf, stem, next_vowel)

    return stem + ending

# ---------------- MAIN ----------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_present_subjunctive.py input_present.json output_subj.json")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        data = [r for r in data if isinstance(r, dict)]

    # filter source tense
    source_rows = [r for r in data if r.get(KEY_TENSE) == SOURCE_TENSE]

    # group by infinitive
    by_inf = {}
    for r in source_rows:
        inf = r.get(KEY_INFINITIVE)
        if not inf:
            continue
        by_inf.setdefault(inf, []).append(r)

    output = []
    skipped = []

    for inf, rows in by_inf.items():
        cls = verb_class(inf)
        if cls not in ("ar", "er", "ir"):
            skipped.append((inf, "unknown verb class"))
            continue

        # map first row for each persona_base (we only need yo + nosotros stems; extra subject variants remain in rows)
        rows_by_persona = {}
        for r in rows:
            p = norm_persona(r.get(KEY_PERSONA_BASE))
            rows_by_persona.setdefault(p, r)

        yo_row = rows_by_persona.get("yo")
        if not yo_row and inf.lower() not in IRREGULAR_FULL:
            skipped.append((inf, "missing yo row"))
            continue

        yo_stem = yo_stem_from_yo_form(yo_row.get(KEY_FORM)) if yo_row else ""
        base_stem = derive_base_stem_from_present(rows_by_persona, cls)

        # convert every existing row (preserves your subject variety)
        for r in rows:
            new_r = deepcopy(r)
            persona = norm_persona(r.get(KEY_PERSONA_BASE))

            if persona not in ENDINGS_AR and persona not in ENDINGS_ER_IR:
                # unknown persona label; skip this row
                continue

            new_r[KEY_PERSONA_BASE] = persona
            new_r[KEY_TENSE] = TARGET_TENSE
            new_r[KEY_FORM] = build_present_subj_form(inf, cls, persona, yo_stem, base_stem)

            old_tr = str(new_r.get(KEY_TRANSLATION, "")).strip()
            new_r[KEY_TRANSLATION] = (TRANSLATION_PREFIX + old_tr) if old_tr else TRANSLATION_PREFIX.rstrip()

            output.append(new_r)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Done. Wrote {len(output)} rows to {out_path}")
    if skipped:
        print(f"⚠️ Skipped {len(skipped)} verbs (first 20 shown):")
        for inf, reason in skipped[:20]:
            print(" -", inf, ":", reason)

if __name__ == "__main__":
    main()

