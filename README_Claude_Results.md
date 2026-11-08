# Andersen pilot: Claude in-chat judge

## What was run

One judge, Claude Opus 5.5 medium as shown in the chat, made 20 forced-choice preferences and scored 80 items. The model version and separate-chat setup are self-reported and cannot be independently verified from the pasted text. The experiment used 20 selected passages from 18 Andersen tales, two readings per passage and one exact and one altered quote per reading. The cases were authored by ChatGPT in an earlier conversation. The preference prompt contained only questions and two claims, with no passage or quotations. The four score prompts each showed 20 passages, with one condition per passage in each prompt. I used a separate new chat for each batch. I ran the experiment entirely in chat.

Code verifies that all 40 real quotations occur as exact substrings of the whitespace-normalized displayed passages, and all 40 altered quotations do not. Altered quotations are mostly paraphrases or small wording changes; a non-verbatim quote is not necessarily a false claim about the story.

In its written rationales, Claude described 40/40 exact quotes as verbatim or accurate and 40/40 altered quotes as non-verbatim or inaccurate. These statuses were extracted from explicit words in its rationales; the prompt did not ask for a separate binary classification. This is a result for this synthetic set, not a general accuracy claim.

## Results (1 to 5)

- Mean score, exact quote: **3.725**; altered quote: **2.600**.
- Evidence gap (exact minus altered, within the same reading): **1.125 (95% passage-bootstrap interval 0.975 to 1.275)**.
- Preference gap (preferred minus nonpreferred, averaged across quote types): **0.875 (95% passage-bootstrap interval 0.375 to 1.325)**.
- Preference gap for exact quotations: 1.250 (95% passage-bootstrap interval 0.550 to 1.850).
- Preference gap for altered quotations: 0.500 (95% passage-bootstrap interval 0.150 to 0.850).
- Evidence gap minus preference gap: 0.250 (95% passage-bootstrap interval -0.200 to 0.750).
- Preference gap by passage: positive 16, zero 1, negative 3.

The default intervals resample the 20 passages as clusters (20,000 percentile-bootstrap draws, seed 20261108). Because two tales contribute two passages each, the results.json also includes a sensitivity analysis resampling the 18 tales (seed 20261109). Both analyses are descriptive for this small convenience sample; they do not measure variability across repeated calls, models, or dataset creation, and they are not a guarantee of generalization.

## Interpretation and limitations

The scoring prompt explicitly asked the judge to consider whether the quotation was accurate, and the scale linked the highest score to an accurate relevant quotation. A real-versus-altered difference is therefore not a pure test of interpreting literary evidence; it partly measures response to a known citation defect under the scoring rubric.

The preference comparison holds quote **type**, not actual quotation or evidence quality, constant. A preferred reading may really be better supported. Thus a preference gap is descriptive association, not proof that the judge substitutes agreement for evidence. The preference task required choosing between claims without a passage and forced a choice even when both readings were reasonable; this may reflect differences in wording or general plausibility. The preference options were presented in one randomized order only; stability after swapping the options was not measured. Some paired claims are competing emphases rather than logically incompatible interpretations. There was no human expert validation of whether both readings were equally defensible or whether altered claims were semantically unsupported. One in-chat model's results do not establish behavior across models or versions. The confidence interval for the difference between gaps includes zero, but this does not prove the gaps equivalent.

The earlier ChatGPT self-judgment was not blinded and must not be described as a second independent judge. It is excluded from this report. A stronger next step is to use another blinded model, genuinely matched evidence, and literary-expert judgments.

## Reproducibility

- `claude_80_items_full.csv`: all 80 passages, claims, quotes, condition labels, scores and rationales.
- `claude_20_passage_contrasts.csv`: paired ratings and per-passage contrasts.
- `inputs/`: the preference and score CSVs I pasted from the chats, along with the five prompts.
- `source_data/cases.json`: original 20 cases and selection metadata.
- `source_data/second_judge_answer_key_PRIVATE.json`: mapping from blind IDs to conditions. Do not disclose to any further blinded judge.
- `source_data/andersen_1597.txt`: Project Gutenberg source, https://www.gutenberg.org/files/1597/1597-0.txt. Text was whitespace-normalized before selecting passages; the source SHA-256 is in cases.json.
- Run `python analyze_claude.py` to recreate the tables and results, using only the Python standard library.
