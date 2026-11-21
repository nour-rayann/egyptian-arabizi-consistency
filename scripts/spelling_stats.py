"""Spelling-variation test: is the Arabizi gap tied to one spelling?

Compares each respelled Arabizi request (data/spelling_variants_scored.csv) with the
original Arabizi request in data/results_400.csv. Same model and settings, no system prompt.
Usage: python scripts/spelling_stats.py      Needs: pip install pandas numpy scipy
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
rng = np.random.default_rng(0)
base = pd.read_csv(ROOT / "data" / "results_400.csv").set_index("example_id")
v = pd.read_csv(ROOT / "data" / "spelling_variants_scored.csv")
v = v[v.scope == "in_scope"].copy()
for m in ["intent_score", "action_score"]:
    v["orig_" + m] = v.arabizi_example_id.map(base[m])
# Words changed beyond spelling in these rows (kept on purpose, as people would type them)
WORD_SWAPS = {"E084_mixed", "E124_no_digits", "E128_no_digits", "E140_no_digits"}


def ci(x):
    x = np.asarray(x, float)
    m = x[rng.integers(0, len(x), (10_000, len(x)))].mean(1)
    return f"{x.mean():.2f} [{np.percentile(m, 2.5):.2f}, {np.percentile(m, 97.5):.2f}]"


def holm(p):
    p = np.asarray(p); out = np.empty(len(p)); run = 0
    for r, i in enumerate(np.argsort(p)):
        run = max(run, (len(p) - r) * p[i]); out[i] = min(1, run)
    return out


def compare(df, label):
    rows = []
    for m in ["intent_score", "action_score"]:
        d = df[m] - df["orig_" + m]
        rows.append((m, ci(df["orig_" + m]), ci(df[m]), ci(d), (d > 0).sum(), (d < 0).sum(), (d == 0).sum(),
                     wilcoxon(df[m], df["orig_" + m]).pvalue if (d != 0).any() else 1.0))
    adj = holm([r[-1] for r in rows])
    print(f"\n{label}")
    for r, pa in zip(rows, adj):
        print(f"  {r[0]:12s} original {r[1]}  respelled {r[2]}  difference {r[3]}  higher {r[4]}, lower {r[5]}, same {r[6]}, p = {pa:.2g} (Holm over intent and action)")


# Main analysis: one row per request (variants of the same request averaged), so no request counts twice
per_request = v.groupby("arabizi_example_id")[["intent_score", "action_score", "orig_intent_score", "orig_action_score"]].mean()
compare(per_request, f"In-scope, one row per request ({len(per_request)} requests)")
compare(v, f"In-scope, every variant ({len(v)} variants)")
compare(v[~v.variant_id.isin(WORD_SWAPS)].groupby("arabizi_example_id").mean(numeric_only=True), "Without the variants that also change a word")
print("\nBy kind of respelling (small groups; descriptive only):")
for t, g in v.groupby("variant_type"):
    print(f"  {t:12s} n = {len(g):2d}  intent {g.orig_intent_score.mean():.2f} -> {g.intent_score.mean():.2f}  action {g.orig_action_score.mean():.2f} -> {g.action_score.mean():.2f}")
print("\nWhat the model did with the respelled in-scope requests:")
print(v.response_type.value_counts().to_string())
