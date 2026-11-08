# Literary evidence and LLM judging: an exploratory pilot

How does an LLM judge score a literary reading when the cited words are changed, and how do those scores relate to the reading it initially prefers? This repository contains the passages, constructed readings, blinded prompts, manually relayed judge responses, and code for a small pilot.

**Status:** 20 passages, 80 scored items, and one blinded model judge. The cases and altered quotations are synthetic. The data do not establish that a preference gap is caused by agreement bias.

## Results

| Paired comparison | Mean difference on a 1-5 scale | 95% passage-bootstrap interval |
| --- | ---: | ---: |
| Exact quotation minus altered quotation, for the same reading | 1.125 | [0.975, 1.275] |
| Initially preferred minus nonpreferred reading, within quote type | 0.875 | [0.375, 1.325] |

The mean score was 3.725 for exact quotations and 2.600 for altered quotations. In its rationales, the judge described all 40 altered quotations as non-verbatim or inaccurate and all 40 exact quotations as verbatim or accurate. The prompt explicitly asked it to consider quote accuracy. These findings apply to this constructed dataset and judge, not to literary interpretation in general.

## Design

1. Select 20 passages from 18 tales in the English Project Gutenberg edition of Andersen's fairy tales.
2. Construct one question and two competing readings for each passage. Each reading has an exact quotation and an altered quotation: 20 x 2 x 2 = 80 items.
3. Ask the judge which reading it prefers using **only the question and two claims**, without the passage or quotations. The choice is forced.
4. In four scoring batches, present each passage once per batch, with one reading and one quotation. I collected the responses in separate new chats. The model version comes from the label shown in the chat.
5. Calculate the two paired gaps above. Bootstrap over the 20 passages; the analysis also reports a sensitivity interval clustered by tale.

The altered quotations are mostly paraphrases or small wording changes. Failure to match word-for-word does **not** mean that the altered quotation expresses a factually false claim.

## Important interpretation

- The evidence gap partly measures response to a citation defect: the scoring rubric explicitly asked for quotation accuracy and linked the top score to an accurate quotation.
- The preference gap holds **quotation type** constant, not the actual text or quality of the evidence. A preferred reading can genuinely be better supported.
- Preference was selected without the passage and cannot be assumed to represent an informed literary interpretation. No expert assessed whether the two readings are equally defensible.
- This is one model, one set of model-generated cases, 20 passages, and chat output that I pasted in. The model shown in the chat was **Claude Opus 5.5 medium**. I did not have a model snapshot, generation settings, response IDs, or raw provider logs.
- The archived preliminary ChatGPT scores were produced by the same conversation that created the cases and saw their labels. They are **not** a second blinded judge and are excluded from the main results.

See [the analysis report](README_Claude_Results.md) and [the protocol and limitations](docs/protocol.md).

## Reproduce the analysis

Requires Python 3; no packages, API key, network access, or model calls are needed.

```bash
python analyze_claude.py
python -m unittest discover -s tests -v
```

The analysis checks the identifiers, four conditions per passage, scores, and exact quotation matches. It recreates `results.json`, `claude_20_passage_contrasts.csv`, `claude_80_items_full.csv`, and `README_Claude_Results.md` from the saved inputs. Confidence intervals use 20,000 bootstrap resamples with recorded seeds.

## Repository contents

| Path | Contents |
| --- | --- |
| `inputs/` | The 20 preference choices, four batches of 20 scores and rationales, and the blinded prompts. |
| `source_data/cases.json` | The 20 normalized passages, questions, readings, and exact/altered quotations. |
| `source_data/second_judge_answer_key_PRIVATE.json` | Mapping from blind IDs to readings and quote conditions; do not provide this file to a new judge. |
| `source_data/andersen_1597.txt` | The archived story text with the Project Gutenberg notice and full license. |
| `analyze_claude.py` | Standard-library analysis and bootstrap code. |
| `claude_80_items_full.csv` | All items with passages, scores, rationales, and decoded conditions. |
| `claude_20_passage_contrasts.csv` | Paired scores and contrasts for each passage. |
| `generation/` | Preserved passage selection, case construction, and blind-prompt generation scripts and inputs. |
| `provenance/unblinded_chatgpt/` | The preliminary, non-independent in-chat scoring, retained for transparency only. |

For another blinded judge, use the files in `inputs/blind_prompts/` and follow `START_HERE.txt`. Keep the answer key, this README, and previous scores out of the judge's context. These are batch judgments, not separate API calls for every item.

The word `PRIVATE` in the answer-key filename means **withhold it from the judge**. The file itself is included in this repository for reproducibility and is not a secret.

## Sources and reuse

Passages come from [Andersen's Fairy Tales, Project Gutenberg eBook 1597](https://www.gutenberg.org/ebooks/1597), source text [`1597-0.txt`](https://www.gutenberg.org/files/1597/1597-0.txt), retrieved on 8 November 2026. The SHA-256 of the original archive, from the start marker through the end marker and its final newline, is `b68136f61260d1b865c45ba7c27a0ec616eb319d8339dbcb7564fcaae0ef1470`. Project Gutenberg identifies this edition as public domain in the United States. Both bundled copies include the notice and full license outside the archived text.

Questions and readings were created with ChatGPT during the pilot. I pasted the scoring output from the chat. No license for the repository's original code or constructed data has been specified.
