# Scoring rubric

How every model answer in this benchmark is scored. It applies to the main run, the follow-up runs, the spelling variants and the other models.

Each answer gets three scores and one label:

| Field | Values | Question it answers |
|---|---|---|
| `intent_score` | 0, 1, 2 | Did the model identify the customer's underlying issue? |
| `action_score` | 0, 1, 2 | Did it propose an appropriate next step for that issue? |
| `unsupported_action` | 0, 1 | Did it make the scenario's forbidden assumption? |
| `response_type` | a label (see below) | What did the model actually do? It does not change the score, only the failure counts. |

Each answer is scored against its scenario's gold labels in `data/benchmark_400_prompts.csv`: `gold_intent`, `expected_action` and `forbidden_assumption`.

## 1. Intent (0–2)

| Score | Meaning |
|---|---|
| **2** | The model correctly identified the issue. |
| **1** | It understood part of the issue, or it restated the meaning correctly but treated the message as text to translate or analyze rather than as a request. |
| **0** | It got the issue wrong: it misread the message, took it for another language or domain, said it didn't understand a clear request, or refused for no reason. |

## 2. Action (0–2)

| Score | Meaning |
|---|---|
| **2** | Appropriate next step, for example asking for the order number, giving the right troubleshooting steps, or pointing to the right place (the store's website, customer support). |
| **1** | Partly right or incomplete: vague, generic, or a reasonable step wrapped in a refusal. |
| **0** | Wrong step or no step at all. |

**Out-of-scope requests** (15 scenarios, for example legal, medical or creative requests): the right action is to decline and redirect. Carrying out the request scores action 0, with `unsupported_action` = 1.

## 3. Unsupported action (0/1)

**1** when the answer makes the scenario's forbidden assumption. Typical cases:

- inventing a store policy ("we don't accept cash on delivery", "a 30-day return window")
- inventing a status, date or reason ("the promotion ends on December 31")
- a flat "yes" or "no" to a policy question with no hedge ("Yes, you can pause for a month")
- claiming an action was done (refund issued, address changed)
- asking for the customer's OTP or verification code
- fulfilling an out-of-scope request (acting as a travel planner)

Hedged general knowledge is **not** unsupported: "many stores allow it, check the policy", or "it depends on the company", followed by a pointer to where to check.

## 4. Conventions for borderline answers

These follow how earlier answers were scored, so that scores stay comparable across runs and models.

| Situation | Intent / Action | Unsupported | `response_type` |
|---|---|---|---|
| Flat refusal: "Sorry, I can't help with this request" | 0 / 0 | 0 | `refused` |
| Opens by refusing, then points to the right place ("I can't help, contact the company") | 2 / 1 | 0 | `partial` |
| Points to the right place with no refusal ("I have no access; check the website / contact support") | 2 / 2 | 0 | `success` |
| "I have no access to your information", with no next step | 2 / 0 | 0 | `partial` |
| Restates the issue with no next step ("Your delivery is late.") | 2 / 0 | 0 | `partial` |
| Repeats the prompt back, word for word or almost | 0 / 0 | 0 | `garbled_output` |
| Translates the request into another language or script instead of helping | 1 / 0 | 0 | `language_task` |
| Only rephrases the request, correctly, as if it were the customer (for example Nile-Chat E089: "ana et7asabt marteen 3ala nafs el talab"). The rephrase shows it understood, but it gives no help | 2 / 0 | 0 | `language_task` |
| Asks a sensible clarifying question (which order, which product) | 2 / 2 | 0 | `success` |
| "Information not enough, please clarify" on a clear request | 0 / 0 | 0 | `unclear` |
| Flat unverified claim on a policy question ("Yes, you can pay cash") | 2 / 1 | 1 | `success_unsupported` |
| Right issue, wrong domain ("return" as a tax return or an HTTP status) | 0–1 / 0 | 0 | `wrong_domain` |
| Useful start, then repetitive looping | 2 / 1 | 0 | `partial` |
| Answer cut off at 300 tokens but useful so far | scored on what is there | | |

Special scenarios:

- **S074** ("cant get in"): any clarifying question that recognises an access problem scores 2/2.
- **S085** (an incomplete message): the right action is a short clarifying question, which scores 2/2. Guessing the issue does not.

**Reply language is not scored.** An answer in a different language or script from the request is scored on its content. Taking the request *for* another language is different: that is `other_language` and intent 0. (Example: Nile-Chat-4B answered English requests in Arabizi.)

## 5. Response types

| Label | Meaning |
|---|---|
| `success` | Understood and gave the right next step |
| `partial` | Understood, but the next step was incomplete or vague |
| `success_unsupported` | Understood, but invented something (e.g. a store policy) |
| `misread_word` | Read an Egyptian (or loan) word as something else, e.g. "ma weselsh" as Welsh |
| `mesh` | Read "mesh" (Egyptian for "not") as AWS App Mesh, a 3D mesh or a mesh network |
| `language_task` | Translated, explained or analyzed the message instead of helping |
| `other_language` | Took it for another language, and often answered in it |
| `unclear` | Said it didn't understand and asked for a rephrase |
| `wrong_domain` | Read a support word in another domain (`return` as Python, a tax return, an HTTP status) |
| `other_task` | Did something unrelated to the request |
| `garbled_output` | Broken or repetitive text, or just repeats the prompt |
| `refused` | Refused for no reason, including on made-up safety grounds |
| `oos_complied` | Out-of-scope request, and it just carried it out |
| `oos_partial` | Out-of-scope request, half-declined but still did some of it |
| `bad_rewrite` | Transliterate-first run only: its own Arabic-script rewrite got the message wrong |

Before version 1.8, the main run and the script test labelled refusals `safety_refusal`. They are now `refused` everywhere.

**Condition names** used in the data files:

- `English`
- `Egyptian Arabic`
- `Egyptian Arabic + English`
- `Arabizi + English`
- `Arabizi, Arabic script`: the hand-written Arabic-script rewrite of the Arabizi requests

## 6. Scoring process

1. **First pass.** An LLM judge scores every answer with this rubric, sets `response_type`, and flags borderline answers to check first.
2. **Hand check.** The author checks every score on a score-check page, flagged answers first, and either confirms or changes it. Only the hand-checked scores are reported. For example, 120 of the 600 follow-up first-pass scores were changed.
3. **Headline numbers** use the 85 in-scope scenarios. There is no system prompt in the main run, so out-of-scope requests are fulfilled in every condition. All-100 tables are given separately.

## 7. Reliability so far

- **Blind self re-score:** 100 answers re-scored six days later from this rubric alone. Intent: 93% exact agreement, Cohen's kappa 0.85. Action: 85%, kappa 0.74. Unsupported: 94%, kappa 0.77. Agreement is lowest on Arabizi (intent kappa 0.73).
- **LLM judge against the hand check:**
  - 600 follow-up answers: intent 92% (kappa 0.86), action 92% (kappa 0.88).
  - Qwen3-1.7B: intent 89% (kappa 0.83), action 92% (kappa 0.87).
  - ALLaM-7B: intent 95% (kappa 0.91), action 95% (kappa 0.92).
  - Nile-Chat-4B: intent 98% (kappa 0.95), action 95% (kappa 0.92).
  - Qwen3-8B: not computed, because its first-pass scores were not kept. The hand check changed 34 of its 255 answers.
- **Not yet measured:** agreement with a second annotator. Use `scripts/make_annotation_sheet.py` and `scripts/agreement.py`.

To reproduce: `python scripts/self_agreement.py`.
