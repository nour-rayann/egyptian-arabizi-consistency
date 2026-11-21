"""Scoring reliability.

1. Blind self re-score: 100 answers (25 scenarios x 4 conditions) re-scored by the author
   six days later without seeing the original scores (data/blind_rescore.csv).
2. LLM judge vs final scores: the judge's first pass on the 600 follow-up answers
   (data/followup_llm_first_pass.csv) against the hand-checked scores.
Usage: python scripts/self_agreement.py      Needs: pip install pandas scikit-learn
"""
from pathlib import Path
import sys
import pandas as pd
from sklearn.metrics import cohen_kappa_score

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]


def agree(a, b, label, ordinal=True):
    a, b = pd.Series(a).astype(int).values, pd.Series(b).astype(int).values
    exact = (a == b).mean()
    if min(len(set(a)), len(set(b))) < 2:
        return f"  {label:34s} exact {exact:.0%} (kappa not meaningful: one score dominates)"
    k = cohen_kappa_score(a, b)
    kw = f", weighted kappa {cohen_kappa_score(a, b, weights='quadratic'):.2f}" if ordinal else ""
    return f"  {label:34s} exact {exact:.0%}, kappa {k:.2f}{kw}"


orig = pd.read_csv(ROOT / "data" / "results_400.csv").set_index("example_id")
r = pd.read_csv(ROOT / "data" / "blind_rescore.csv")
print(f"1. Blind self re-score ({len(r)} answers)")
for col, new, ordinal in [("intent_score", "rescore_intent", True), ("action_score", "rescore_action", True),
                          ("unsupported_action", "rescore_unsupported", False)]:
    print(agree(orig.loc[r.example_id, col], r[new], col, ordinal))
print("  Intent, by condition:")
for cond, g in r.groupby("condition"):
    print(agree(orig.loc[g.example_id, "intent_score"], g.rescore_intent, cond))

fu = pd.read_csv(ROOT / "data" / "followup_experiments_scored.csv")
j = pd.read_csv(ROOT / "data" / "followup_llm_first_pass.csv")
m = fu.merge(j, on=["experiment", "row_id"])
print(f"\n2. LLM judge first pass vs hand-checked scores ({len(m)} follow-up answers)")
for col, ordinal in [("intent_score", True), ("action_score", True), ("unsupported_action", False)]:
    print(agree(m["judge_" + col], m[col], col, ordinal))
