"""Confidence intervals and paired tests for the benchmark results.

Usage: python scripts/stats.py            (run from the repository root)
Needs: pip install pandas numpy scipy
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
ORDER = ["English", "Egyptian Arabic", "Egyptian Arabic + English", "Arabizi + English"]
REWRITE = "Arabizi rewritten in Arabic script"
N_BOOT = 10_000
rng = np.random.default_rng(0)

df = pd.read_csv(ROOT / "data" / "results_400.csv")
q1 = pd.read_csv(ROOT / "data" / "q1_script_test_results.csv")
df = df[df.scope == "in_scope"]
q1 = q1[q1.scope == "in_scope"]


def wide(metric):
    w = df.pivot(index="scenario_id", columns="condition", values=metric)[ORDER]
    w[REWRITE] = q1.set_index("scenario_id")[metric]
    missing = w.isna().any(axis=1)
    if missing.any():
        print(f"  note: {missing.sum()} scenarios skipped because some scores are still empty")
    return w[~missing]


def ci(x):
    """Mean and 95% bootstrap interval, resampling scenarios."""
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), (N_BOOT, len(x)))
    lo, hi = np.percentile(x[idx].mean(1), [2.5, 97.5])
    return x.mean(), lo, hi


def holm(p):
    p = np.asarray(p)
    order = np.argsort(p)
    adj = np.empty(len(p))
    running = 0
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(1, running)
    return adj


PAIRS = [("English", "Egyptian Arabic"),
         ("English", "Egyptian Arabic + English"),
         ("English", "Arabizi + English"),
         ("Egyptian Arabic", "Egyptian Arabic + English"),
         ("Egyptian Arabic + English", "Arabizi + English"),
         (REWRITE, "Arabizi + English"),
         ("Egyptian Arabic + English", REWRITE)]

for metric in ["intent_score", "action_score"]:
    w = wide(metric)
    print(f"\n=== {metric} ({len(w)} in-scope scenarios) ===\n")
    print("Mean with 95% bootstrap interval, and share of fully correct answers (score 2)")
    for c in w.columns:
        m, lo, hi = ci(w[c])
        print(f"  {c:38s} {m:.2f}  [{lo:.2f}, {hi:.2f}]   fully correct: {(w[c] == 2).mean():.0%}")

    print("\nPaired comparisons (A minus B): mean difference, 95% interval, Wilcoxon signed-rank p (Holm-adjusted)")
    rows = []
    for a, b in PAIRS:
        d = w[a] - w[b]
        m, lo, hi = ci(d)
        p = wilcoxon(d).pvalue if (d != 0).any() else 1.0
        rows.append((a, b, m, lo, hi, (d > 0).sum(), (d < 0).sum(), p))
    adj = holm([r[-1] for r in rows])
    for (a, b, m, lo, hi, up, down, p), pa in zip(rows, adj):
        print(f"  {a} vs {b}\n      diff {m:+.2f} [{lo:+.2f}, {hi:+.2f}]   A higher in {up}, lower in {down}   p = {pa:.2g}")

# Script test on the scenarios where the rewrite is NOT identical to the Arabic + English prompt
sub = q1[~q1.identical_to_arabic_english_prompt.astype(bool)].scenario_id
print(f"\n=== Script test on the {len(sub)} in-scope scenarios where the rewrite differs from the Arabic + English prompt ===")
for metric in ["intent_score", "action_score"]:
    w = wide(metric)
    w = w.loc[w.index.intersection(sub)]
    d = w[REWRITE] - w["Arabizi + English"]
    m, lo, hi = ci(d)
    print(f"  {metric}: Arabizi {w['Arabizi + English'].mean():.2f}, Arabic script {w[REWRITE].mean():.2f}, "
          f"diff {m:+.2f} [{lo:+.2f}, {hi:+.2f}], Wilcoxon p = {wilcoxon(d).pvalue:.2g}")

print("\n=== Arabizi intent by difficulty (in-scope) ===")
a = df[df.condition == "Arabizi + English"]
print(a.groupby("difficulty").intent_score.agg(["count", "mean"]).round(2).to_string())
