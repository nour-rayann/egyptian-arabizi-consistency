"""Recompute every number in the README from the scored data files.

Usage: python scripts/summarize.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["English", "Egyptian Arabic", "Egyptian Arabic + English", "Arabizi + English"]

df = pd.read_csv(ROOT / "data" / "results_400.csv")
q1 = pd.read_csv(ROOT / "data" / "q1_script_test_results.csv")


def table(d):
    t = (d.groupby("condition")
          .agg(examples=("example_id", "count"),
               intent=("intent_score", "mean"),
               action=("action_score", "mean"),
               unsupported=("unsupported_action", "sum"))
          .reindex(ORDER))
    return t.round(2)


inscope = df[df.scope == "in_scope"]
print("In-scope requests (85 per condition), 0 to 2 scale\n")
print(table(inscope).to_string(), "\n")
q1_in = q1[q1.scope == "in_scope"]
print(f"Arabizi rewritten in Arabic script (85): intent {q1_in.intent_score.mean():.2f}, "
      f"action {q1_in.action_score.mean():.2f}\n")

print("All 100 requests per condition\n")
print(table(df).to_string(), "\n")
print(f"Arabizi rewritten in Arabic script (100): intent {q1.intent_score.mean():.2f}, "
      f"action {q1.action_score.mean():.2f}\n")

a = df[df.condition == "Arabizi + English"].set_index("scenario_id")
s = q1.set_index("scenario_id")
better = (s.intent_score > a.intent_score).sum()
worse = (s.intent_score < a.intent_score).sum()
print(f"Script test: intent higher in Arabic script for {better} scenarios, lower for {worse}")
print(f"Mean tokens: Arabizi {q1.tokens_arabizi.mean():.1f}, Arabic script {q1.tokens_arabic_script.mean():.1f}\n")

print("Response types for the 100 Arabizi + English requests\n")
print(df[df.condition == "Arabizi + English"].response_type.value_counts().to_string())
