"""Tables, intervals and paired tests for the follow-up experiments
(system prompt, Arabizi hint, transliterate-first), plus figures/followup_arabizi.png.

The hint and transliterate-first runs both use the same support-assistant system prompt,
so each is compared with the system-prompt Arabizi run. The hand rewrite was run without
a system prompt (main benchmark settings).

Usage: python scripts/followup_stats.py      (run from the repository root)
Needs: pip install pandas numpy scipy matplotlib
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
ORDER = ["English", "Egyptian Arabic", "Egyptian Arabic + English", "Arabizi + English"]
N_BOOT = 10_000
rng = np.random.default_rng(0)

base = pd.read_csv(ROOT / "data" / "results_400.csv")
q1 = pd.read_csv(ROOT / "data" / "q1_script_test_results.csv")
fu = pd.read_csv(ROOT / "data" / "followup_experiments_scored.csv")
base, q1, fu = (d[d.scope == "in_scope"] for d in (base, q1, fu))


def ci(x):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), (N_BOOT, len(x)))
    lo, hi = np.percentile(x[idx].mean(1), [2.5, 97.5])
    return x.mean(), lo, hi


def holm(p):
    p = np.asarray(p); order = np.argsort(p); adj = np.empty(len(p)); running = 0
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i]); adj[i] = min(1, running)
    return adj


def series(metric):
    """One column per setting, indexed by scenario."""
    s = {f"none | {c}": base[base.condition == c].set_index("scenario_id")[metric] for c in ORDER}
    sp = fu[fu.experiment == "sysprompt_400"]
    s.update({f"system prompt | {c}": sp[sp.condition == c].set_index("scenario_id")[metric] for c in ORDER})
    s["hint | Arabizi + English"] = fu[fu.experiment == "hint_arabizi_100"].set_index("scenario_id")[metric]
    s["transliterate first | Arabizi + English"] = fu[fu.experiment == "translit_first_100"].set_index("scenario_id")[metric]
    s["hand rewrite | Arabizi in Arabic script"] = q1.set_index("scenario_id")[metric]
    return pd.DataFrame(s).dropna()


PAIRS = [("none | Arabizi + English", "system prompt | Arabizi + English"),
         ("none | Egyptian Arabic", "system prompt | Egyptian Arabic"),
         ("none | Egyptian Arabic + English", "system prompt | Egyptian Arabic + English"),
         ("none | English", "system prompt | English"),
         ("system prompt | Arabizi + English", "system prompt | English"),
         ("system prompt | Arabizi + English", "system prompt | Egyptian Arabic + English"),
         ("system prompt | Egyptian Arabic", "system prompt | Egyptian Arabic + English"),
         ("system prompt | Arabizi + English", "hint | Arabizi + English"),
         ("hint | Arabizi + English", "hand rewrite | Arabizi in Arabic script"),
         ("system prompt | Arabizi + English", "transliterate first | Arabizi + English"),
         ("transliterate first | Arabizi + English", "hand rewrite | Arabizi in Arabic script")]

for metric in ["intent_score", "action_score"]:
    w = series(metric)
    print(f"\n=== {metric} (in-scope, {len(w)} scenarios) ===")
    for col in w.columns:
        m, lo, hi = ci(w[col]); print(f"  {col:45s} {m:.2f} [{lo:.2f}, {hi:.2f}]")
    rows = []
    for a, b in PAIRS:
        d = w[b] - w[a]
        p = wilcoxon(w[a], w[b]).pvalue if (d != 0).any() else 1.0
        rows.append((a, b, *ci(d), int((d > 0).sum()), int((d < 0).sum()), p))
    adj = holm([r[-1] for r in rows])
    print("  Paired differences (B minus A), Wilcoxon signed-rank, Holm-corrected over these 11 tests:")
    for r, pa in zip(rows, adj):
        a, b, m, lo, hi, up, down, _ = r
        print(f"  {a}  ->  {b}: {m:+.2f} [{lo:+.2f}, {hi:+.2f}]  higher {up}, lower {down}, p = {pa:.2g}")

print("\n=== Unsupported actions on in-scope requests ===")
print(f"  no system prompt, all four forms: {int(base.unsupported_action.sum())}")
for exp, g in fu.groupby("experiment"):
    print(f"  {exp}: {int(g.unsupported_action.sum())}", {k: int(v) for k, v in g.groupby("condition").unsupported_action.sum().items()} if exp == "sysprompt_400" else "")

print("\n=== Arabizi response types, in-scope ===")
t = pd.concat({"no prompt": base[base.condition == "Arabizi + English"].response_type.value_counts(),
               "system prompt": fu[(fu.experiment == "sysprompt_400") & (fu.condition == "Arabizi + English")].response_type.value_counts(),
               "hint": fu[fu.experiment == "hint_arabizi_100"].response_type.value_counts(),
               "transliterate first": fu[fu.experiment == "translit_first_100"].response_type.value_counts()}, axis=1).fillna(0).astype(int)
print(t.to_string())

try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    w_i, w_a = series("intent_score"), series("action_score")
    cols = ["none | Arabizi + English", "system prompt | Arabizi + English", "transliterate first | Arabizi + English",
            "hint | Arabizi + English", "hand rewrite | Arabizi in Arabic script", "system prompt | English"]
    labels = ["Arabizi,\nno prompt", "Arabizi +\nsystem prompt", "+ model\ntransliterates\nfirst", "+ Arabizi\nhint", "Hand rewrite\nin Arabic script\n(no prompt)", "English +\nsystem prompt"]
    x = np.arange(len(cols)); fig, ax = plt.subplots(figsize=(9, 4.2))
    for k, (w, name, color, off) in enumerate([(w_i, "Intent", "#2b7bd6", -0.2), (w_a, "Action", "#e2612c", 0.2)]):
        stats = [ci(w[c]) for c in cols]
        ax.bar(x + off, [s[0] for s in stats], 0.38, color=color, label=name,
               yerr=[[s[0] - s[1] for s in stats], [s[2] - s[0] for s in stats]], capsize=3)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9); ax.set_ylim(0, 2.1); ax.set_ylabel("Mean score (0 to 2), 85 in-scope requests")
    ax.set_title("Arabizi under different fixes (Qwen3-4B), with 95% bootstrap intervals"); ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False); fig.tight_layout()
    fig.savefig(ROOT / "figures" / "followup_arabizi.png", dpi=160); print("\nSaved figures/followup_arabizi.png")
except ImportError:
    print("\n(matplotlib not installed: figure skipped)")
