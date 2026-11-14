"""Build a blinded sheet for a second annotator: 25 scenarios x 4 conditions = 100 responses.

Usage: python scripts/make_annotation_sheet.py
Writes annotation/second_annotator_sheet.csv (give this to the annotator)
   and annotation/second_annotator_key.csv   (keep this; it links rows back to example_id)
"""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "annotation"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(ROOT / "data" / "results_400.csv")
scen = df.drop_duplicates("scenario_id")
# 21 in-scope + 4 out-of-scope scenarios, matching the 85/15 split
picked = pd.concat([scen[scen.scope == "in_scope"].sample(21, random_state=7),
                    scen[scen.scope == "out_of_scope"].sample(4, random_state=7)]).scenario_id
sub = df[df.scenario_id.isin(picked)].sample(frac=1, random_state=7).reset_index(drop=True)
sub.insert(0, "row_id", [f"R{i+1:03d}" for i in range(len(sub))])

sheet = sub[["row_id", "prompt", "gold_intent", "expected_action", "forbidden_assumption", "model_response"]].copy()
for c in ["intent_score", "action_score", "unsupported_action", "comment"]:
    sheet[c] = ""
sheet.to_csv(OUT / "second_annotator_sheet.csv", index=False, encoding="utf-8-sig")
sub[["row_id", "example_id", "scenario_id", "condition"]].to_csv(OUT / "second_annotator_key.csv", index=False)
print(f"{len(sheet)} rows written:", sub.condition.value_counts().to_dict())
