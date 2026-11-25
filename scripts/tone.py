"""How the models talk to customers: reply language, refusals, apologies, lecturing, tone.

Counts wording patterns in every model's answers to the 85 in-scope requests in English,
Arabizi and the Arabic-script rewrite. These are counts of how an answer is worded, not scores:
an answer can apologise or mention being an AI and still be right.

Uses data/more_models_scored.csv, data/results_400.csv and data/q1_script_test_results.csv.
Usage: python scripts/tone.py      Needs: pip install pandas
"""
from pathlib import Path
import re
import sys
import pandas as pd

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
D = ROOT / "data"
CONDS = ["English", "Arabizi + English", "Arabizi, Arabic script"]

m = pd.read_csv(D / "more_models_scored.csv")
r = pd.read_csv(D / "results_400.csv")
r = r[(r.scope == "in_scope") & r.condition.isin(CONDS[:2])].assign(row_id=r.example_id)
q = pd.read_csv(D / "q1_script_test_results.csv")
q = q[q.scope == "in_scope"].assign(row_id=q.arabizi_example_id, model_response=q.response_arabic_script)
qwen = pd.concat([r, q]).assign(model="Qwen/Qwen3-4B-Instruct-2507")
cols = ["model", "condition", "row_id", "scenario_id", "model_response", "intent_score", "action_score", "response_type"]
d = pd.concat([m[cols], qwen[cols]], ignore_index=True)
d["model"] = d.model.str.split("/").str[-1].str.replace("-Instruct-preview", "", regex=False).str.replace("-Instruct-2507", "", regex=False)
d["model_response"] = d.model_response.fillna("")

SORRY = r"\basef\b|آسف|\bاسف\b|معلش|\bsorry\b|apologi|عذرًا|عذرا|أعتذر|نعتذر"
CANT = r"mesh ha2dar|ma3andish|mesh 3andy|مش هقدر|مش هينفع|معنديش|مش عندي|can'?t|cannot|unable|don'?t have|do not have|لا يمكنني|لا أستطيع|ليس لدي"
AI = r"\bka AI\b|كـ ?AI|AI language model|AI model|AI assistant|مجرد AI|مجرد برنامج|ذكاء اصطناعي|\bas an AI\b|I'?m (?:just )?an AI|\bana AI\b|نموذج لغوي"
PATTERNS = {
    "apologises": SORRY,
    "sorry_but_cant": rf"(?:{SORRY})[^.\n]{{0,30}}(?:\bbas\b|\bbs\b|بس|but|لكن)[^.\n]{{0,25}}(?:{CANT})",
    "says_cant_help": r"mesh ha2dar (?:asa3d|a2olak|ashoof)|مش هقدر|مش هينفع (?:أ|ا)ساعد|can'?t (?:help|assist)|cannot (?:help|assist)|unable to (?:help|assist)|لا (?:يمكنني|أستطيع) (?:مساعدتك|تقديم المساعدة|المساعدة)",
    "mentions_being_ai": AI,
    "as_an_ai_i_cant": rf"(?:{AI})[^.\n]{{0,60}}(?:{CANT})",
    "lectures": r"be7teram|ne7terem|محترمة|نحترم|lazem net3amel|لازم نتعامل|لازم تفتكر|stay calm|remain calm|calm down|be respectful|please be patient|اهدأ",
    "casual_address": r"يا سيدي|يا صاحبي|ya sa7by|يا باشا|ya basha|يا حبيبي|يا معلم",
}
for k, p in PATTERNS.items():
    d[k] = d.model_response.str.contains(p, case=False, regex=True)
d["flat_refusal"] = d.response_type.isin(["refused", "safety_refusal"])


def reply_language(t):
    latin, arabic = len(re.findall(r"[A-Za-z]", t)), len(re.findall(r"[؀-ۿ]", t))
    if arabic > latin:
        return "Arabic script"
    words = r"\b(?:ana|mesh|bas|3ashan|momken|beta3\w*|asef|ezay|keda|elly|3ayez|3ayza)\b"
    return "Arabizi" if len(re.findall(words, t, re.I)) >= 2 else "English"


d["reply_language"] = d.model_response.map(reply_language)
d["condition"] = pd.Categorical(d.condition, CONDS)
g = d.groupby(["model", "condition"], observed=True)
table = g[list(PATTERNS) + ["flat_refusal"]].sum()
table.insert(0, "n", g.size())
print("Answers containing each pattern (85 in-scope requests per row)\n")
print(table.to_string())

print("\nLanguage of the reply, by the form of the request\n")
print(pd.crosstab([d.condition, d.model], d.reply_language).to_string())

print("\nScores of answers that open a refusal with an apology ('sorry, but I can't'), against the rest\n")
print(d.groupby(["model", "condition", "sorry_but_cant"], observed=True)[["intent_score", "action_score"]]
      .agg(["mean", "count"]).round(2).to_string())

angry = d[d.scenario_id.isin(["S075", "S076"])]
print("\nAngry-customer scenarios S075 and S076: answers that lecture the customer")
print(angry.groupby("model").lectures.agg(["sum", "size"]).rename(columns={"sum": "lectures", "size": "answers"}).to_string())
