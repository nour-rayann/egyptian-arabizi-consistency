"""Agreement between the author's scores and a second annotator.

Usage: python scripts/agreement.py
Needs the filled annotation/second_annotator_sheet.csv. pip install pandas scikit-learn
"""
from pathlib import Path
import sys
import pandas as pd
from sklearn.metrics import cohen_kappa_score

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
ANN = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "annotation"

mine = pd.read_csv(ROOT / "data" / "results_400.csv").set_index("example_id")
key = pd.read_csv(ANN / "second_annotator_key.csv")
theirs = pd.read_csv(ANN / "second_annotator_sheet.csv").merge(key, on="row_id")
theirs = theirs.dropna(subset=["intent_score", "action_score"])
print(f"{len(theirs)} responses scored by both annotators\n")


def report(rows, label):
    for col in ["intent_score", "action_score"]:
        a = mine.loc[rows.example_id, col].astype(int).values
        b = rows[col].astype(int).values
        exact = (a == b).mean()
        if len(set(a) | set(b)) < 2:
            print(f"  {label:28s} {col:13s} exact agreement {exact:.0%} (kappa undefined: only one score used)")
            continue
        k = cohen_kappa_score(a, b, labels=[0, 1, 2])
        kw = cohen_kappa_score(a, b, labels=[0, 1, 2], weights="quadratic")
        print(f"  {label:28s} {col:13s} exact agreement {exact:.0%}   kappa {k:.2f}   weighted kappa {kw:.2f}")


report(theirs, "All")
for cond, rows in theirs.groupby("condition"):
    report(rows, cond)

if theirs.unsupported_action.notna().any():
    a = mine.loc[theirs.example_id, "unsupported_action"].astype(int).values
    b = theirs.unsupported_action.fillna(0).astype(int).values
    print(f"\n  Unsupported-action flag: exact agreement {(a == b).mean():.0%}")
