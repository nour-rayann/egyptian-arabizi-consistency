# Changelog

Version numbers follow `CITATION.cff`. Unless an entry says otherwise, the main tables did not change.

## 1.10 (27 November 2026)

Added a fifth model, Qwen3-8B, with every score checked by hand. The main tables did not change.

- **Doubling the size does not close the Arabizi gap.** Qwen3-8B matches Qwen3-4B on English (intent 1.96 for both). On Arabizi it is a little higher, but not significantly (intent 0.94 against 0.74, p = 0.24).
- **Across the three Qwen3 sizes,** English intent stays at 1.93 to 1.96 while Arabizi intent goes from 0.27 (1.7B) to 0.74 (4B) to 0.94 (8B).
- **The Arabic-script rewrite still helps most** (intent 0.94 to 1.55). On the rewrite Qwen3-8B is level with Qwen3-4B on intent and somewhat lower on action (1.26 against 1.47, p = 0.07).
- **No refusals.** Qwen3-8B gave no flat refusals in any form.
- **Data:**
  - `data/more_models_scored.csv` gains Qwen3-8B's 255 answers. The hand check changed 34 of them; 31 of those were among the 97 the LLM judge had flagged to check first.
  - `data/more_models_llm_first_pass.csv` gains the LLM judge's first-pass scores for Qwen3-8B. Judge agreement with the hand check: intent 96% (kappa 0.92), action 95% (kappa 0.91).
- **README:** "Other models" and "How Nile-Chat talks to customers" gain a Qwen3-8B column. The evaluation setup now says Qwen3-8B was also run with `enable_thinking=False`.
- **README:** corrected the gloss of Nile-Chat's "بص يا سيدي" from "look, sir" to "look, man".

## 1.9 (25 November 2026)

Added a fourth model, Nile-Chat-4B (Gemma 3 4B trained on Egyptian Arabic), with every score checked by hand. The main tables did not change.

- **Arabizi gap closed.** Nile-Chat understood Arabizi as well as the Arabic-script rewrite (intent 1.71 against 1.65, p = 0.48), almost a point above Qwen3-4B on Arabizi.
- **But English got worse.** Nile-Chat is the weakest model in English (intent 1.36), mostly because of refusals.
- **New section, "How Nile-Chat talks to customers"**, with a new script, `scripts/tone.py`. It covers:
  - answering English customers in Arabizi (78 of 85)
  - bare refusals (19 English answers)
  - apologies that open refusals
  - repeated "as an AI, I can't"
  - lecturing angry customers
- **Nile-Chat was disappointing outside Arabizi.** It gave vague next steps: of the English requests it understood, the next step was fully right in 69%, against 93% for Qwen3-4B. But it was the only model, without a system prompt, to get the misspelt "brosh" request (E333) fully right.
- **Data:**
  - `data/more_models_scored.csv` and `data/more_models_llm_first_pass.csv` gain Nile-Chat's 255 answers.
  - The hand check changed 22 of the first-pass scores.
- **`RUBRIC.md`** records one more convention: an answer that only rephrases the request correctly, as if it were the customer, scores 2/0.
- **`scripts/model_stats.py`** now gives each model its own fixed random seed for the bootstrap intervals, so adding a model no longer shifts another model's intervals. Qwen3-1.7B's intervals move by at most 0.02; its means, counts and p-values are unchanged.

## 1.8 (25 November 2026)

Housekeeping. No scores changed.

- **One refusal label.** The 5 answers labelled `safety_refusal` (4 in `data/results_400.csv`, 1 in `data/q1_script_test_results.csv`) are now `refused`, the label the later files use.
- **One condition name** for the hand-written Arabic-script rewrite: `Arabizi, Arabic script`, as in `data/more_models_scored.csv`.
  - `data/q1_script_test_results.csv` gains a `condition` column with this value.
  - The analysis cell in `notebooks/extensions.ipynb` uses it too.
- **No blank conditions.** The 200 hint and transliterate-first rows in `data/followup_experiments_scored.csv` now say `Arabizi + English` instead of being blank.
- **No hidden character.** `data/q1_transliteration_sheet.csv` no longer starts with a UTF-8 byte-order mark.
- **Added:**
  - `RUBRIC.md`: the full scoring rubric and the conventions for borderline answers.
  - `scripts/sensitivity.py`: the main results without the seven flagged Arabizi prompts. They hold.
  - `requirements.txt`: the versions the analysis scripts were tested with.
- **The hand-check record is now kept for the other models too.**
  - Added `data/more_models_llm_first_pass.csv`: the LLM judge's first-pass scores for Qwen3-1.7B and ALLaM-7B.
  - `data/more_models_scored.csv` gains a `changed_in_hand_check` column: 60 and 36 answers changed.
  - `scripts/self_agreement.py` reports judge agreement for these models.
- **Notebooks** now print the Python, `transformers` and `torch` versions and the GPU when they load a model.
- **README:** "Evaluation setup" records the hardware (Colab, T4) and the library versions recovered for the main run.
- **README:**
  - The model settings for every run are in "Evaluation setup".
  - New limitations: the scorer could see the condition, and the hand-check record exists only for Qwen3-4B.
  - Link to the Hugging Face copy of the data.
  - The update notes moved here.

## 1.7 (24 November 2026)

Added a third model, the Arabic-focused ALLaM-7B, with every score checked by hand ("Other models: size and Arabic training" in the README).

## 1.6 (22 November 2026)

Added a second model: Qwen3-1.7B on the 85 in-scope requests in English, Arabizi and the Arabic-script rewrite, with every score checked by hand.

## 1.5 (21 November 2026)

- Added a spelling-variation test. Respelled Arabizi did not do better; it did slightly worse.
- Added two checks of scoring reliability:
  - a blind self re-score of 100 answers
  - agreement between the LLM judge's first pass and the hand-checked scores

## 1.4 (20 November 2026)

Added three follow-up runs on Qwen3-4B, all hand-checked:

- a support-assistant system prompt
- an Arabizi hint
- asking the model to rewrite Arabizi in Arabic script before answering

## 1.3 (17 November 2026)

Added a hidden-state analysis comparing how the model represents the same request in different forms, with a control comparison against pure Egyptian Arabic. No scores changed.

## 1.2 (15 November 2026)

- **Fourteen Egyptian Arabic prompts rewritten.** They had English words in Latin letters (for example "refund", "sync", "tracking"), so that condition was not purely in Arabic script. They were rewritten with the same English words in Arabic letters (ريفاند، سينك، التراكر), run again with the same model and settings, and scored again.
  - The earlier prompts, answers and scores are kept in the `_v1` columns of `data/results_400.csv`.
  - Egyptian Arabic scores fell: in-scope intent from 1.52 to 1.44, action from 1.26 to 1.15. No other condition changed.
- **Labels corrected.** The difficulty of scenarios S046 and S050 changed from `high` to `medium`. A missing urgency label (E020) in `data/benchmark_400_prompts.csv` was restored.
- **Statistics added:** confidence intervals and paired tests.

## 1.1 (18 October 2026)

**Correction.** An earlier version reported results from a spreadsheet in which most model responses could not be traced to the prompts they sat next to. 219 of the 400 responses were exact copies of another row's response, and many belonged to a different prompt.

Those results are withdrawn, including:

- an Arabizi intent score of 0.34
- a failure breakdown dominated by "Welsh or Portuguese" and "AWS App Mesh" readings

All 400 prompts were run again with the same model and settings, and every response was scored again.

## 1.0 (16 October 2026)

First release: 400 prompts, Qwen3-4B responses and scores.
