"""Draft alternative spellings of the Arabizi prompts, for the spelling-variation test.

Arabizi has no standard spelling. This script respells each Arabizi prompt two ways with simple rules:
  no_digits    3ayza -> ayza, 7elw -> helw, 5ales -> khales, 8eer -> gheer, te2oly -> te'oly
  more_digits  mokhtalef -> mo5talef, yeshtaghal -> yeshta8al
English terms (taken from the Arabic + English version of the same scenario) are left alone.

The rules are rough. EVERY ROW MUST BE READ AND FIXED BY A NATIVE WRITER before it is used:
set `checked` to 1 once a row looks like something a real person would type.

Usage: python scripts/make_spelling_variants.py
"""
from pathlib import Path
import re
import sys
import pandas as pd

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data"

df = pd.read_csv(ROOT / "data" / "results_400.csv")
arabizi = df[df.condition == "Arabizi + English"].set_index("scenario_id")
mixed = df[df.condition == "Egyptian Arabic + English"].set_index("scenario_id")
VOWELS = "aeiouy"


def no_digits(w):
    w = re.sub(r"3(?=[%s])" % VOWELS, "", w)     # 3ayza -> ayza, a3raf -> araf
    w = w.replace("3", "a")                       # ba3d -> baad, ma3 -> maa
    w = w.replace("7", "h").replace("5", "kh").replace("8", "gh")
    w = re.sub(r"^2", "", w)                      # 2olily -> olily
    w = w.replace("2", "'")                       # te2oly -> te'oly
    return w


def more_digits(w):
    return w.replace("kh", "5").replace("gh", "8")


def respell(prompt, english, rule):
    out = []
    for tok in re.split(r"(\s+)", prompt):
        core = re.sub(r"[^\w']", "", tok).lower()
        latin = bool(re.fullmatch(r"[a-z0-9']+", core))
        is_number = bool(re.fullmatch(r"\d+x?", core))        # 2x, 500
        out.append(rule(tok) if latin and not is_number and core not in english else tok)
    return "".join(out)


rows = []
for sid, r in arabizi.iterrows():
    english = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", mixed.loc[sid, "prompt"])}
    english |= {p for w in english for p in w.split("-")}
    for name, rule in [("no_digits", no_digits), ("more_digits", more_digits)]:
        v = respell(r.prompt, english, rule)
        if v != r.prompt:
            rows.append(dict(scenario_id=sid, arabizi_example_id=r.example_id, scope=r["scope"],
                             original=r.prompt, variant_type=name, variant=v, checked=0))
out = pd.DataFrame(rows)
out.to_csv(OUT / "arabizi_spelling_variants_draft.csv", index=False, encoding="utf-8-sig")
print(len(out), "variants;", out.variant_type.value_counts().to_dict(), ";", out.scenario_id.nunique(), "scenarios")
