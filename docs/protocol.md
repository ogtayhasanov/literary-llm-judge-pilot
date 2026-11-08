# Protocol and limitations

## Selection and construction

The source is the full English Project Gutenberg eBook 1597, included with its notice and full license in `source_data/andersen_1597.txt`. Before extracting passages, all runs of whitespace within each tale were normalized to single spaces. A deterministic selection using Python's pseudorandom generator and seed `20261108` took one paragraph-starting passage from each of the 18 tales and a second passage from each of two longer tales. Passage lengths are 285-320 whitespace-separated words. There was no expert review of passage selection.

For each passage, ChatGPT constructed an open question, readings A and B, and one quotation per reading that appears exactly in the displayed passage. It also constructed one altered quote per reading. Within a reading, the claim is identical in the two quote conditions. The automated checks require the exact quote to occur and the altered quote not to occur as substrings of the normalized displayed passage. The construction scripts and original generated cases are in `generation/`.

Many altered quotes preserve much of the meaning of the originals. The manipulation therefore tests non-verbatim quotation under an explicit quotation-accuracy instruction; it is not a general test of factually invented evidence or of interpretive hallucination.

## Judge procedure

The preference prompt presents only the question and the two reading claims, in a randomized order; it does not provide the passage. It forces an A/B choice, even where the model might otherwise be indifferent. One order was used per case, so response-order sensitivity was not measured.

The 80 items were randomized into four prompts. Each prompt contains one item for each of the 20 passages, so within a scoring chat the judge does not see multiple versions of the same passage. Each item includes its passage, question, single reading, and cited quotation. The instructions ask for a 1-5 rating of support, taking both relevance and quote accuracy into account. The inputs do not label a quotation as exact or altered. The scoring rubric allows a non-verbatim quote to receive a partial score when the reading has other support in the passage.

I used Claude Opus 5.5 medium as the judge, with a fresh chat for the preference task and each scoring batch. Five responses were pasted into the conversation and recorded as CSV. The exact model identifier, sampling settings, response IDs, and separation of chat sessions cannot be independently established from the pasted outputs. The final batch outputs were separated at the repeated CSV header; scores and rationales were retained.

## Paired measures

For passage `p`, reading `a` or `b`, quote type `real` or `fake`, and 1-5 score `s`:

```text
evidence_gap(p) = ((s[a,real] - s[a,fake]) + (s[b,real] - s[b,fake])) / 2
preference_gap(p) = ((s[preferred,real] - s[other,real])
                   + (s[preferred,fake] - s[other,fake])) / 2
```

Each reported gap is the mean over 20 passages. A positive preference gap is an observed rating difference associated with the earlier choice; it is not an experimental estimate of a causal effect of preference. The two readings' actual support can differ even when their quotation types match. In addition, several pairs contrast emphases rather than mutually exclusive interpretations.

The script uses 20,000 percentile-bootstrap resamples at the passage level, seed `20261108`. A sensitivity analysis samples the 18 tales as clusters, seed `20261109`, including all selected passages within a sampled tale. These intervals condition on the particular one-model dataset; they do not account for model sampling, prompt selection, case-generation uncertainty, or expert validation.

## Primary result and scope

The exact-versus-altered gap is 1.125 points and the preferred-versus-other gap is 0.875 points. The estimated difference between them is 0.250, with a passage-bootstrap interval of [-0.200, 0.750]. The interval includes zero, which does not establish equivalence between the two gaps.

Expert-supported cases with matched evidential quality, actual/irrelevant quote controls, additional independent models and varied authors or languages would be needed for a stronger study of interpretation and evidence. The self-scoring by the ChatGPT instance that generated the cases is archived separately and excluded from the blinded Claude analysis.
