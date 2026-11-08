# Andersen in-chat pilot: exploratory results

## Status

20 passages from 18 Andersen tales; 40 interpretive claims and 80 claim/quote items. One ChatGPT judge in this conversation recorded 20 forced-choice preferences and 80 scores. The same ChatGPT instance authored the questions, claims and altered quotations, read all passages, knew which quotations were altered, and scored items together in the same conversation. Preference presentation was limited to questions and claims, but the judge had already seen the passages and evidence; it was not blinded. This was **not** the planned independent, two-model evaluation, and results cannot be attributed to GPT-5 mini or GPT-4.1 mini.

## Scores (1 to 5)

- Mean scores: genuine quotation 4.075; altered quotation 2.800.
- Evidence gap, genuine minus altered: **1.275 (95% bootstrap interval 1.175 to 1.375)**.
- Agreement gap, preferred minus nonpreferred, averaged over genuine and altered evidence types: **0.525 (95% bootstrap interval 0.200 to 0.825)**.
- Agreement gap among genuine quotations: 0.750 (95% bootstrap interval 0.350 to 1.150).
- Agreement gap among altered quotations: 0.300 (95% bootstrap interval 0.050 to 0.550).
- Evidence gap minus agreement gap: 0.750 (95% bootstrap interval 0.500 to 1.050).

Gaps are averaged within passage, then across 20 passages. Intervals use 20,000 percentile-bootstrap resamples of passages (seed 20261108). Two tales contribute two passages each; the intervals do not account for tale-level dependence, case generation, judge uncertainty, or the fact that this is a convenience sample. They are descriptive sensitivity summaries, not strong population inference.

## Scoring rule

The judge assessed how well the supplied passage supported each reading, taking account of quotation accuracy and relevance. A 5 indicates strong support and relevant, accurate quotation; 4 substantial support; 3 mixed/partial support, including some otherwise-supported claims with an incorrect citation; 2 weak or seriously undermined support; and 1 little or no support. No automatic rule assigned a particular score to an invented quote. The reasoning behind each side is in item_scores.csv; for altered quotations, a note that the citation is non-verbatim is added. The scores and reasons were authored in chat; quote presence was verified independently by code.

## Construction and limits

The 40 genuine quotations are exact substrings of the **whitespace-normalized displayed passages**; all 40 altered quotations are absent as exact substrings. Most altered quotations are plausible paraphrases or small edits of the source, so absence as an exact string is not evidence that their semantic content is false. Opposing readings were authored by the same ChatGPT instance, with no expert validation. Some are competing emphases that can both be true. The preference question was forced-choice, even where the two readings could coexist.

The agreement contrast holds the **type of quotation** fixed, not the words or actual quality of the evidence. A preferred reading may earn a higher score because it is better supported by the passage. Therefore, even a large agreement gap would not prove a judge scores agreement instead of support. The unblinded, self-authored run is especially vulnerable to expectations and cannot independently establish the research finding. Expert-annotated CuRe examples and independently blinded judge calls would be needed for a stronger test.

## Files

- cases.json: 20 passages, questions, claims, and original/altered quotes.
- item_scores.csv: all 80 items, full passages, quotations, preferences, scores and rationales.
- passage_scores.csv: the paired per-passage data and contrasts.
- preferences_in_chat.json and preference_order.json: forced-choice decisions and presentation mapping.
- judgments_in_chat.json: the directly recorded scores and claim-level rationales.
- results.json: machine-readable results and intervals.
- select_passages.py and build_cases.py: deterministic passage selection and case construction.
- analyze_pilot.py: reproduces the analysis without API calls.
- second_judge_blind_prompts/: five prompts for a second judge in fresh chats, without API calls. See START_HERE.txt in that directory.
- second_judge_answer_key_PRIVATE.json: mapping for analyzing a second judge; do not give it to that judge.
- create_blind_packet.py: produces the second judge prompts.
- andersen_1597.txt: source text as downloaded.

Source: Project Gutenberg, Andersen's Fairy Tales, https://www.gutenberg.org/files/1597/1597-0.txt. Whitespace is normalized to spaces before selecting passages. Source SHA-256 and selection seed are in cases.json. The collection is public domain in the USA according to its Gutenberg catalog entry.
