"""Recompute the results table and the Arabizi failure breakdown from data/results_400.csv.

Usage: python scripts/summarize.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["English", "Egyptian Arabic", "Egyptian Arabic + English", "Arabizi + English"]

df = pd.read_csv(ROOT / "data" / "results_400.csv")

table = (df.groupby("condition")
           .agg(examples=("example_id", "count"),
                intent=("intent_score", "mean"),
                action=("action_score", "mean"),
                unsupported=("unsupported_action", "sum"))
           .reindex(ORDER))
table.loc["Overall"] = [len(df), df.intent_score.mean(), df.action_score.mean(), df.unsupported_action.sum()]
print("Scores by condition (0 to 2 scale)\n")
table["examples"] = table["examples"].astype(int)
table["unsupported"] = table["unsupported"].astype(int)
print(table.round(3).to_string(), "\n")


def failure_group(note: str) -> str:
    n = note.lower()
    if any(k in n for k in ("welsh", "portuguese", "garbled", "foreign language")):
        return "Decided it was another language or garbled text"
    if any(k in n for k in ("linguist", "translat", "language question")):
        return "Translated or analyzed it instead of helping"
    if "mesh" in n:
        return "Misread 'mesh' (Egyptian for 'not')"
    if "safety" in n:
        return "Unwarranted safety refusal"
    if "success" in n:
        return "Fully correct"
    return "Misread other words"


arabizi = df[df.condition == "Arabizi + English"]
print("How the 100 Arabizi responses failed (grouped from evaluator notes)\n")
print(arabizi.evaluator_notes.map(failure_group).value_counts().to_string())
