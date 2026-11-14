# Egyptian Arabic, Code-Switching and Arabizi Consistency Benchmark

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nour-rayann/egyptian-arabizi-consistency/blob/main/notebooks/qwen3_4b_egyptian_arabic_evaluation.ipynb)

![Intent and action scores by condition](figures/results_by_condition.png)

A 400-example benchmark that writes the same 100 customer-support requests in four forms of everyday Egyptian communication, used to test whether a language model keeps the same understanding of a request when only its written form changes. It comes with the responses of [Qwen/Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507), their scores, and a follow-up test that rewrites the Arabizi requests in Arabic script.

**Author:** Nouran Mohamed El-Sayed (Ain Shams University, Cairo) · **Created:** October 2026 · **Results last revised:** 15 November 2026

> **Update (15 November 2026).** Fourteen "Egyptian Arabic" prompts had English words in Latin letters (for example "refund", "sync", "tracking"), so that condition was not purely in Arabic script. They were rewritten with the same English words in Arabic letters (ريفاند، سينك، التراكر), run again with the same model and settings, and scored again. The earlier prompts, answers and scores are kept in the `_v1` columns of `data/results_400.csv`. Egyptian Arabic scores fell (in-scope intent from 1.52 to 1.44, action from 1.26 to 1.15); no other condition changed. The difficulty of scenarios S046 and S050 was corrected from `high` to `medium`, and a missing urgency label (E020) in `data/benchmark_400_prompts.csv` was restored.

> **Correction (18 October 2026).** An earlier version of this repository reported results from a spreadsheet in which most model responses could not be traced to the prompts they sat next to: 219 of the 400 responses were exact copies of another row's response, and many belonged to a different prompt. Those results, including an Arabizi intent score of 0.34 and a failure breakdown dominated by "Welsh or Portuguese" and "AWS App Mesh" readings, are withdrawn. All 400 prompts were run again with the same model and settings, and every response was scored again. The tables below come from that run.

## Why this benchmark

Egyptians often mix Egyptian Arabic and English in one sentence, write Arabic in Latin letters and numbers (Arabizi), and adapt English words into Arabic ("اكنسل" for "cancel"). Standard benchmarks tend to test languages separately with clean, formal text, so they do not show whether a model's understanding of a task survives these changes. In customer support, a small shift in interpretation can lead to the wrong action, an unnecessary question or an unsupported assumption.

The idea grew out of a mentorship with Prof. Ahmed Hassan Yousef (https://scholar.google.com/citations?hl=en&user=OVwUxWQAAAAJ&view_op=list_works&is_public_preview=1) and his work on Arabic sentiment analysis and summarization.

## Design

100 scenarios, each written in four conditions, so that the meaning stays fixed and only the form changes:

| Condition | Example (scenario S001) |
|---|---|
| English | Can you check why this order is stuck? |
| Egyptian Arabic | ممكن تبصلي ليه الأوردر واقف؟ |
| Egyptian Arabic + English terms | ممكن تبصلي ليه الـ order stuck؟ |
| Arabizi + English terms | momken tebosly leh el order stuck? |

- **Scripts:** the Egyptian Arabic condition uses Arabic script only; English loanwords are written in Arabic letters, as Egyptians often write them (الأوردر، ريفاند). The other two Egyptian conditions keep English terms in Latin letters.
- **Scope:** 85 in-scope operational scenarios (orders, delivery, returns, refunds, payments, promotions, pricing, accounts, account security, subscriptions, app sync, rewards and more) and 15 out-of-scope requests (for example legal, medical or creative requests) that a support assistant should not try to fulfil.
- **Difficulty:** easy, medium and hard, plus edge cases such as typos, missing punctuation, abbreviations, sarcasm, emotional tone, several issues in one message, letter elongation and mixed script.
- **Gold labels per scenario:** intended issue (`gold_intent`), urgency, the expected next action, and a forbidden assumption the model must not make (for example "Never request the customer's OTP").

## Repository layout

```
data/
  benchmark_400_prompts.csv       the 400 prompts and gold labels
  results_400.csv                 prompts + model responses + scores + response type
                                  (_v1 columns: earlier versions of the 14 rewritten prompts)
  q1_transliteration_sheet.csv    the 100 Arabizi requests rewritten word for word in Arabic script
  q1_script_test_results.csv      the model's answers to those rewritten requests, with scores
  arabizi_spelling_variants_draft.csv   alternative Arabizi spellings for a planned test (not yet checked)
notebooks/
  qwen3_4b_egyptian_arabic_evaluation.ipynb   builds the benchmark, runs the model, summarizes scores
  extensions.ipynb                code for the planned follow-up experiments (see Next steps)
scripts/
  summarize.py                    recomputes every table in this README
  stats.py                        confidence intervals and paired significance tests
  make_annotation_sheet.py        builds a blinded sheet for re-scoring a sample
  agreement.py                    agreement between two sets of scores (Cohen's kappa)
  make_spelling_variants.py       builds the spelling-variants draft
figures/
  results_by_condition.png
```

To reproduce the tables: `pip install pandas` then `python scripts/summarize.py`. For the intervals and tests: `pip install pandas numpy scipy` then `python scripts/stats.py`.

## Evaluation setup

- **Model:** Qwen/Qwen3-4B-Instruct-2507, loaded with `transformers`.
- **Prompting:** each prompt sent on its own as a single user message, with no system prompt.
- **Decoding:** greedy (`do_sample=False`), up to 300 new tokens.
- **Scoring:** each response gets two scores on a 0 to 2 scale (0 = incorrect, 1 = partly correct or incomplete, 2 = correct) and an unsupported-action flag.
  - **Intent:** did the model identify the user's underlying issue? Restating the meaning correctly but treating the message as text to translate, rather than as a request, scores 1.
  - **Action:** did it propose an appropriate next step for that issue (asking for the order number, giving the right troubleshooting steps, or, for out-of-scope requests, declining and redirecting)?
  - **Unsupported action:** did it make the scenario's forbidden assumption (for example inventing a store policy, or acting as a travel planner)?
- **Who scored:** first-pass scores were assigned by an LLM judge following the rubric above, and every score was then checked by hand by the author. Each response also has a `response_type` label describing what the model did.

Because there is no system prompt, the model has no way of knowing that it is meant to be a support assistant. On the 15 out-of-scope requests it therefore usually just fulfils the request (recommending restaurants, planning a trip), in every condition. The main table uses the 85 in-scope requests for that reason; the all-100 table is given below it.

## Results

### Main table: 85 in-scope requests per condition

| Condition | Intent | Action | Unsupported actions |
|---|---|---|---|
| English | 1.96 | 1.87 | 1 |
| Egyptian Arabic | 1.44 | 1.15 | 1 |
| Egyptian Arabic + English | 1.71 | 1.54 | 0 |
| Arabizi + English | 0.74 | 0.54 | 0 |
| *Arabizi + English, rewritten in Arabic script* | *1.62* | *1.47* | *0* |

In English the model almost always understood the request. In Egyptian Arabic written fully in Arabic script it dropped, and keeping the English terms in Latin letters helped: intent rose from 1.44 to 1.71. In Arabizi it understood far fewer requests: it got the intent fully right for 15 of the 85, and for 37 it got it completely wrong.

### How sure are these numbers?

Each scenario appears in every condition, so conditions can be compared scenario by scenario. Intervals are 95% bootstrap intervals over the 85 in-scope scenarios; p-values are Wilcoxon signed-rank tests, Holm-corrected within each score.

| Condition | Intent | Action | Intent fully correct |
|---|---|---|---|
| English | 1.96 [1.92, 2.00] | 1.87 [1.78, 1.94] | 96% |
| Egyptian Arabic | 1.44 [1.27, 1.59] | 1.15 [0.96, 1.33] | 60% |
| Egyptian Arabic + English | 1.71 [1.58, 1.82] | 1.54 [1.39, 1.68] | 76% |
| Arabizi + English | 0.74 [0.59, 0.91] | 0.54 [0.39, 0.71] | 18% |
| *Arabizi + English, rewritten in Arabic script* | *1.62 [1.48, 1.75]* | *1.47 [1.31, 1.62]* | *73%* |

- **Arabizi against its Arabic-script rewrite:** intent +0.88 [+0.71, +1.06], higher in 54 scenarios and lower in 2 (p < 0.001); action +0.93 [+0.74, +1.13] (p < 0.001).
- **The rewrite against the Egyptian Arabic + English condition:** intent differs by 0.08 [−0.01, +0.19] (p = 0.10), so the remaining gap cannot be told apart from zero.
- **English against Arabizi:** intent +1.22 [+1.06, +1.38] (p < 0.001). English never scored lower than Arabizi on intent.
- **Egyptian Arabic against Egyptian Arabic + English:** keeping English terms in Latin letters helped, intent +0.27 [+0.12, +0.44] (p = 0.003), action +0.39 [+0.21, +0.56] (p < 0.001).

### Is the gap about script or dialect?

Each Arabizi request was rewritten word for word in Arabic script, keeping the English words in Latin letters (`data/q1_transliteration_sheet.csv`), and the model was run again with the same settings. The words and the dialect stayed the same; only the script changed.

- Intent rose from 0.74 to 1.62, and action from 0.54 to 1.47. That closes about 90% of the gap to the Egyptian Arabic + English condition (1.71 and 1.54).
- The rewritten version scored higher on intent in 62 of the 100 scenarios and lower in 2.
- For 65 scenarios the rewritten request turned out to be identical to the existing "Egyptian Arabic + English" prompt, and with greedy decoding the model gave exactly the same answer to both. On the other 35, where the wording differs slightly, the result holds: intent 0.80 in Arabizi against 1.46 in Arabic script. On the 27 of these that are in scope, intent rose from 0.63 to 1.33 (p = 0.001).
- Token counts are almost the same (13.8 tokens on average for Arabizi, 13.4 for Arabic script), so Arabizi is not simply split into more pieces.

In this benchmark, then, most of the Arabizi gap comes from the Latin script rather than from the dialect. Reading the answers suggests why: the model often reads Latin-spelled Egyptian words as words of another language.

### English words written in Arabic letters

The 14 rewritten Egyptian Arabic prompts (see the update above) give a small test in the opposite direction: the same English loanwords, first in Latin letters and then in Arabic letters, with the rest of the sentence unchanged. On the 12 in-scope prompts, intent fell from 1.58 to 1.00 and action from 1.33 to 0.58; intent was lower in 6 prompts and higher in 1.

The model read ريفاند (refund) as a replacement, a product or "Re-Validation" (E082, E086, E286), or could not make sense of it (E114). It read فيتشر (feature) as an app called "Vitshir" (E262), التراكر (tracking) as a GPS tracker (E026) and, in an out-of-scope request, السي في (CV) as a legal document (E362). ريسيت (reset) and سينك (sync) were understood (E166, E242).

With 12 prompts this is an observation rather than a measured effect, but it points the same way as the Arabizi result: each kind of word was understood best in the script it is usually written in, Egyptian words in Arabic letters and English words in Latin letters.

### What the model did with the 100 Arabizi requests

| Response type | Count | Examples |
|---|---|---|
| Answered correctly | 12 | |
| Misread an Egyptian word | 21 | "ma weselsh" (did not arrive) read as Welsh (E168); "8alat" (wrong) read as the number 80 (E308); "bet2abloha" read as a betting site (E104) |
| Treated the request as a language task, translating or analyzing it instead of helping | 15 | E008, E012, E088 |
| Took it for another language and often answered in it (Spanish, Portuguese, Indonesian, Filipino, French) | 14 | Portuguese (E016), Spanish (E060), Indonesian (E240), Filipino (E360) |
| Said the message was unclear and asked for a rephrase | 9 | E004, E036 |
| Read "mesh" (Egyptian for "not") as AWS App Mesh, a 3D mesh or a mesh network | 7 | App Mesh (E244, E328), 3D mesh (E028) |
| Read a support word in a technical sense | 5 | `return` as the Python statement (E048, E052) |
| Understood the request but gave an incomplete next step | 5 | |
| Refused for no reason ("If this is a question involving false or bad content...") | 4 | E180, E296, E340 |
| Produced repetitive, broken output | 2 | E064, E300 |
| Fulfilled an out-of-scope request (as in the other conditions) | 6 | |

Arabic script had problems of its own, and some of them appear in every Arabic condition. "الأوردر واقف" (the order is stuck) was read as a stock-trading order (E002, E003), "return" as the Python statement (E050, E051), "اتخصم مني" (I was charged) as a discount (E090), and "بطل يشتغل" (stopped working) as a product called "Batal" (E070).

### All 100 requests per condition

| Condition | Intent | Action | Unsupported actions |
|---|---|---|---|
| English | 1.97 | 1.68 | 11 |
| Egyptian Arabic | 1.46 | 1.03 | 10 |
| Egyptian Arabic + English | 1.74 | 1.38 | 10 |
| Arabizi + English | 0.82 | 0.47 | 11 |
| *Arabizi + English, rewritten in Arabic script* | *1.66* | *1.30* | *11* |

Almost all unsupported actions here are out-of-scope requests that the model fulfilled. On in-scope requests there were two: inventing an order-limit policy (E073) and stating flatly that two promo codes cannot be combined (E146).

## Known issues and limitations

- **One model, one domain, one annotator.** The scores are evidence from this benchmark only, not a general measure of the model's Arabic ability. The first pass was done by an LLM judge, the hand check is by one person, and no inter-annotator agreement has been measured.
- **No system prompt.** The model was not told it was a support assistant, which mainly affects the out-of-scope requests (see above).
- **Synthetic requests.** All scenarios were written by the author, not collected from real users.
- **Seven Arabizi prompts contain Arabic-script words** that were not intended (E080, E096, E244, E248, E264, E356, E396). E328 is mixed script on purpose (`edge_case = mixed_script`).

These rows are flagged in the `data_note` column and were not changed, so the scores match the prompts the model saw.

## Next steps

The code for steps 1 and 2, and for the system-prompt and fix experiments below, is in `notebooks/extensions.ipynb`. No results from it are reported yet.

1. **Scale:** run the same benchmark across model sizes and families, to see whether the script gap shrinks with size.
2. **Where in the model does the gap appear?** Compare how the model represents the Arabizi and Arabic-script versions of the same request.
3. **System prompt:** run the benchmark again with the model told it is a support assistant, to see whether the Arabizi gap remains.
4. **Simple fixes:** test a one-sentence hint about Arabizi, and asking the model to rewrite Arabizi in Arabic script before answering.
5. **Consistency training:** build paired data in which one request appears in many realistic forms and test whether consistency-based training narrows the gap.
6. **Scoring reliability:** re-score a blinded sample and measure agreement with the original scores, and with the LLM judge's first pass.

## Citation

```bibtex
@misc{elsayed2026arabizi,
  author = {El-Sayed, Nouran Mohamed},
  title  = {Egyptian Arabic, Code-Switching and Arabizi Consistency Benchmark},
  year   = {2026},
  howpublished = {\url{https://github.com/nour-rayann/egyptian-arabizi-consistency}}
}
```

## License

Data (`data/`, `figures/`) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code (`notebooks/`, `scripts/`) is released under the MIT License (see `LICENSE`).
