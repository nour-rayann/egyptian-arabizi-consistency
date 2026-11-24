"""Other models: compare each extra model with Qwen3-4B on the same 85 in-scope requests.

Uses data/more_models_scored.csv (hand-checked scores of the extra models) against
data/results_400.csv (English, Arabizi + English) and data/q1_script_test_results.csv
(Arabizi rewritten in Arabic script). Same settings as the main benchmark, no system prompt.
Usage: python scripts/model_stats.py      Needs: pip install pandas numpy scipy
"""
from pathlib import Path
import re
import sys
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
rng = np.random.default_rng(0)
SCORES = ["intent_score", "action_score"]
CONDS = ["English", "Arabizi + English", "Arabizi, Arabic script"]

main = pd.read_csv(ROOT / "data" / "results_400.csv")
q1 = pd.read_csv(ROOT / "data" / "q1_script_test_results.csv")
base = {c: main[main.condition == c].set_index("example_id") for c in CONDS[:2]}
base[CONDS[2]] = q1[q1.scope == "in_scope"].set_index("arabizi_example_id")
other = pd.read_csv(ROOT / "data" / "more_models_scored.csv")


def ci(x):
    x = np.asarray(x, float)
    m = x[rng.integers(0, len(x), (10_000, len(x)))].mean(1)
    return f"{x.mean():.2f} [{np.percentile(m, 2.5):.2f}, {np.percentile(m, 97.5):.2f}]"


def holm(p):
    p = np.asarray(p); out = np.empty(len(p)); run = 0
    for r, i in enumerate(np.argsort(p)):
        run = max(run, (len(p) - r) * p[i]); out[i] = min(1, run)
    return out


for model, g in other.groupby("model"):
    print(f"\n{model} vs Qwen/Qwen3-4B-Instruct-2507 (85 in-scope requests per condition)")
    rows = []
    for c in CONDS:
        x = g[g.condition == c].set_index("row_id")
        b = base[c].loc[x.index]
        for m in SCORES:
            d = x[m] - b[m]
            p = wilcoxon(x[m], b[m]).pvalue if (d != 0).any() else 1.0
            rows.append([c, m, ci(x[m]), ci(b[m]), (d > 0).sum(), (d < 0).sum(), p])
    for r, pa in zip(rows, holm([r[-1] for r in rows])):
        print(f"  {r[0]:24s} {r[1]:12s} {model.split('/')[-1]} {r[2]}  4B {r[3]}  higher {r[4]}, lower {r[5]}, p = {pa:.2g} (Holm over 6)")
    print("  Unsupported actions:", g.groupby("condition").unsupported_action.sum().to_dict())
    saudi = g.model_response.str.contains(r"سعود|saudi", flags=re.I, regex=True)
    print("  Answers that bring in Saudi Arabia:", g[saudi].groupby("condition").size().to_dict())
    print("  What it did:")
    print(pd.crosstab(g.response_type, g.condition)[CONDS].to_string())
