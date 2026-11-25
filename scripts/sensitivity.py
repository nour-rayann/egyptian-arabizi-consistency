"""Sensitivity check: do the main results hold without the seven flagged Arabizi prompts?

Seven Arabizi prompts contain Arabic-script words that were not intended (see the
data_note column of data/results_400.csv). This script drops those scenarios in every
condition, so comparisons stay paired, and repeats the main table and the key tests.

Usage: python scripts/sensitivity.py            (run from the repository root)
Needs: pip install pandas numpy scipy
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
ORDER = ["English", "Egyptian Arabic", "Egyptian Arabic + English", "Arabizi + English"]
REWRITE = "Arabizi in Arabic script"
N_BOOT = 10_000
rng = np.random.default_rng(0)

df = pd.read_csv(ROOT / "data" / "results_400.csv")
q1 = pd.read_csv(ROOT / "data" / "q1_script_test_results.csv")
flagged = df[df.data_note.notna() & (df.condition == "Arabizi + English")]
FLAGGED = set(flagged.scenario_id)
print("Flagged Arabizi prompts:", ", ".join(flagged.example_id),
      f"({flagged[flagged.scope == 'in_scope'].shape[0]} in scope)")
df = df[df.scope == "in_scope"]
q1 = q1[q1.scope == "in_scope"]


def wide(metric, drop):
    w = df.pivot(index="scenario_id", columns="condition", values=metric)[ORDER]
    w[REWRITE] = q1.set_index("scenario_id")[metric]
    return w[~w.index.isin(FLAGGED)] if drop else w


def ci(x):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), (N_BOOT, len(x)))
    lo, hi = np.percentile(x[idx].mean(1), [2.5, 97.5])
    return x.mean(), lo, hi


def holm(p):
    p = np.asarray(p)
    adj, running = np.empty(len(p)), 0
    for rank, i in enumerate(np.argsort(p)):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(1, running)
    return adj


PAIRS = [("English", "Arabizi + English"),
         (REWRITE, "Arabizi + English"),
         ("Egyptian Arabic + English", REWRITE),
         ("Egyptian Arabic + English", "Egyptian Arabic")]

for metric in ["intent_score", "action_score"]:
    print(f"\n=== {metric} ===")
    for drop in (False, True):
        w = wide(metric, drop)
        label = f"without flagged ({len(w)} scenarios)" if drop else f"all in-scope ({len(w)} scenarios)"
        print(f"\n{label}")
        for c in w.columns:
            m, lo, hi = ci(w[c])
            print(f"  {c:28s} {m:.2f} [{lo:.2f}, {hi:.2f}]")
        rows = []
        for a, b in PAIRS:
            d = w[a] - w[b]
            m, lo, hi = ci(d)
            p = wilcoxon(d).pvalue if (d != 0).any() else 1.0
            rows.append((a, b, m, lo, hi, p))
        for (a, b, m, lo, hi, _), pa in zip(rows, holm([r[-1] for r in rows])):
            print(f"  {a} minus {b}: {m:+.2f} [{lo:+.2f}, {hi:+.2f}], p = {pa:.2g}")
