"""Reproduce the Claude judge analysis from the preserved inputs; no API calls."""
from __future__ import annotations

import csv
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

root = Path(__file__).resolve().parent
cases_document = json.loads((root / 'source_data' / 'cases.json').read_text(encoding='utf-8'))
cases = cases_document['cases']
key = json.loads((root / 'source_data' / 'second_judge_answer_key_PRIVATE.json').read_text(encoding='utf-8'))

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

preferences = read_csv(root / 'inputs' / 'Claude_Preferences_20.csv')
assert len(preferences) == 20 and len({x['case_id'] for x in preferences}) == 20
assert {x['case_id'] for x in preferences} == set(key['preference'])
preferred = {}
for record in preferences:
    assert record['choice'] in ('A', 'B')
    mapping = key['preference'][record['case_id']]
    preferred[mapping['passage_id']] = mapping[record['choice']]

scores = {}
for batch in range(1, 5):
    path = root / 'inputs' / f'Claude_Scores_Batch_{batch}.csv'
    records = read_csv(path)
    assert len(records) == 20
    assert len({r['item_id'] for r in records}) == 20
    expected = {k for k, v in key['items'].items() if v['batch'] == batch}
    assert {r['item_id'] for r in records} == expected
    for record in records:
        assert record['item_id'] not in scores
        score = int(record['score'])
        assert 1 <= score <= 5 and record['rationale'].strip()
        scores[record['item_id']] = {'score': score, 'rationale': record['rationale']}
assert len(scores) == 80 and set(scores) == set(key['items'])

case_by_id = {c['id']: c for c in cases}
assert len(case_by_id) == 20 and set(case_by_id) == set(preferred)
by_case = defaultdict(dict)
items = []
for item_id, mapping in sorted(key['items'].items()):
    pid, side, kind, batch = (mapping[k] for k in ('passage_id', 'reading', 'quote_status', 'batch'))
    case = case_by_id[pid]
    quote = case[side][kind + '_quote']
    match = quote in case['passage']
    assert match == (kind == 'real')
    record = scores[item_id]
    rationale = record['rationale'].lower()
    # The judge was not separately asked for a binary label. Extract its
    # explicit statements about each quotation from the supplied rationales.
    nonverbatim_markers = ('not verbatim', 'not in the passage', 'inaccurate',
                           'invented', 'does not appear in the passage',
                           'a paraphrase', 'quotation paraphrases')
    if any(marker in rationale for marker in nonverbatim_markers):
        reported_status = 'nonverbatim'
    elif 'verbatim' in rationale or 'accurate' in rationale:
        reported_status = 'verbatim'
    else:
        reported_status = 'unclear'
    assert (side, kind) not in by_case[pid]
    by_case[pid][side, kind] = record['score']
    items.append({
        'item_id': item_id, 'batch': batch, 'passage_id': pid,
        'tale': case['title'], 'question': case['question'], 'passage': case['passage'],
        'preferred_reading': preferred[pid], 'reading': side, 'claim': case[side]['claim'],
        'quote_status': kind, 'quote': quote, 'quote_exactly_in_passage': match,
        'score': record['score'], 'rationale': record['rationale'],
        'rationale_reported_quote_status': reported_status,
    })

contrasts = []
for case in cases:
    pid = case['id']
    data = by_case[pid]
    assert set(data) == {('A', 'real'), ('A', 'fake'), ('B', 'real'), ('B', 'fake')}
    p = preferred[pid]
    other = 'B' if p == 'A' else 'A'
    mean_real = (data['A', 'real'] + data['B', 'real']) / 2
    mean_fake = (data['A', 'fake'] + data['B', 'fake']) / 2
    agreement_real = data[p, 'real'] - data[other, 'real']
    agreement_fake = data[p, 'fake'] - data[other, 'fake']
    contrasts.append({
        'passage_id': pid, 'tale': case['title'], 'preferred_reading': p,
        'A_real': data['A', 'real'], 'A_fake': data['A', 'fake'],
        'B_real': data['B', 'real'], 'B_fake': data['B', 'fake'],
        'real_mean': mean_real, 'fake_mean': mean_fake,
        'evidence_gap': mean_real - mean_fake,
        'agreement_real': agreement_real, 'agreement_fake': agreement_fake,
        'agreement_gap': (agreement_real + agreement_fake) / 2,
    })

def write_csv(path, records):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

write_csv(root / 'claude_80_items_full.csv', items)
write_csv(root / 'claude_20_passage_contrasts.csv', contrasts)

def mean(records, key_name):
    return statistics.mean(row[key_name] for row in records)

def percentile(ordered, p):
    pos = (len(ordered) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)

def interval(values):
    ordered = sorted(values)
    return [percentile(ordered, .025), percentile(ordered, .975)]

fields = ('evidence_gap', 'agreement_gap', 'agreement_real', 'agreement_fake')
passage_boots = {k: [] for k in fields}
passage_boots['difference'] = []
rng = random.Random(20261108)
for _ in range(20000):
    sample = [rng.choice(contrasts) for _ in contrasts]
    for field in fields:
        passage_boots[field].append(mean(sample, field))
    passage_boots['difference'].append(mean(sample, 'evidence_gap') - mean(sample, 'agreement_gap'))

by_story = defaultdict(list)
for row in contrasts:
    by_story[row['tale']].append(row)
stories = sorted(by_story)
story_boots = {k: [] for k in fields}
rng = random.Random(20261109)
for _ in range(20000):
    sample = [row for _ in stories for row in by_story[rng.choice(stories)]]
    for field in fields:
        story_boots[field].append(mean(sample, field))

summary = {
    'model_label': 'Claude Opus 5.5 medium (as reported by user; not independently verified)',
    'n_judges': 1, 'n_passages': 20, 'n_tales': len(stories),
    'n_preferences': len(preferences), 'n_judged_items': len(items),
    'n_exact_quotes': sum(row['quote_exactly_in_passage'] for row in items),
    'n_altered_quotes': sum(not row['quote_exactly_in_passage'] for row in items),
    'rationales_recognizing_exact': sum(row['quote_exactly_in_passage'] and row['rationale_reported_quote_status'] == 'verbatim' for row in items),
    'rationales_recognizing_altered': sum(not row['quote_exactly_in_passage'] and row['rationale_reported_quote_status'] == 'nonverbatim' for row in items),
    'rationales_unclear_quote_status': sum(row['rationale_reported_quote_status'] == 'unclear' for row in items),
    'mean_real': mean(contrasts, 'real_mean'), 'mean_fake': mean(contrasts, 'fake_mean'),
    'preference_counts': dict(Counter(row['preferred_reading'] for row in contrasts)),
    'score_distribution': dict(sorted(Counter(row['score'] for row in items).items())),
    'preference_signs_by_passage': {
        'positive': sum(row['agreement_gap'] > 0 for row in contrasts),
        'zero': sum(row['agreement_gap'] == 0 for row in contrasts),
        'negative': sum(row['agreement_gap'] < 0 for row in contrasts),
    },
    'bootstrap': {'method': 'percentile', 'resamples': 20000, 'passage_seed': 20261108, 'story_seed': 20261109},
}
for field in fields:
    summary[field] = {'estimate': mean(contrasts, field), 'ci_95_passage': interval(passage_boots[field]), 'ci_95_story_sensitivity': interval(story_boots[field])}
summary['evidence_minus_agreement'] = {
    'estimate': mean(contrasts, 'evidence_gap') - mean(contrasts, 'agreement_gap'),
    'ci_95_passage': interval(passage_boots['difference']),
}
(root / 'results.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')

def show(effect):
    low, high = effect['ci_95_passage']
    return f"{effect['estimate']:.3f} (95% passage-bootstrap interval {low:.3f} to {high:.3f})"

doc = f'''# Andersen pilot: Claude in-chat judge

## What was run

One judge, identified by the user as Claude Opus 5.5 medium, made 20 forced-choice preferences and scored 80 items. The model version and separate-chat setup are self-reported and cannot be independently verified from the pasted text. The experiment used 20 selected passages from {len(stories)} Andersen tales, two readings per passage and one exact and one altered quote per reading. The cases were authored by ChatGPT in an earlier conversation. The preference prompt contained only questions and two claims, with no passage or quotations. The four score prompts each showed 20 passages, with one condition per passage in each prompt. The user was instructed to use a separate new chat for each batch; no API calls were used.

Code verifies that all 40 real quotations occur as exact substrings of the whitespace-normalized displayed passages, and all 40 altered quotations do not. Altered quotations are mostly paraphrases or small wording changes; a non-verbatim quote is not necessarily a false claim about the story.

In its written rationales, Claude described {summary['rationales_recognizing_exact']}/40 exact quotes as verbatim or accurate and {summary['rationales_recognizing_altered']}/40 altered quotes as non-verbatim or inaccurate. These statuses were extracted from explicit words in its rationales; the prompt did not ask for a separate binary classification. This is a result for this synthetic set, not a general accuracy claim.

## Results (1 to 5)

- Mean score, exact quote: **{summary['mean_real']:.3f}**; altered quote: **{summary['mean_fake']:.3f}**.
- Evidence gap (exact minus altered, within the same reading): **{show(summary['evidence_gap'])}**.
- Preference gap (preferred minus nonpreferred, averaged across quote types): **{show(summary['agreement_gap'])}**.
- Preference gap for exact quotations: {show(summary['agreement_real'])}.
- Preference gap for altered quotations: {show(summary['agreement_fake'])}.
- Evidence gap minus preference gap: {show(summary['evidence_minus_agreement'])}.
- Preference gap by passage: positive {summary['preference_signs_by_passage']['positive']}, zero {summary['preference_signs_by_passage']['zero']}, negative {summary['preference_signs_by_passage']['negative']}.

The default intervals resample the 20 passages as clusters (20,000 percentile-bootstrap draws, seed 20261108). Because two tales contribute two passages each, the results.json also includes a sensitivity analysis resampling the {len(stories)} tales (seed 20261109). Both analyses are descriptive for this small convenience sample; they do not measure variability across repeated calls, models, or dataset creation, and they are not a guarantee of generalization.

## Interpretation and limitations

The scoring prompt explicitly asked the judge to consider whether the quotation was accurate, and the scale linked the highest score to an accurate relevant quotation. A real-versus-altered difference is therefore not a pure test of interpreting literary evidence; it partly measures response to a known citation defect under the scoring rubric.

The preference comparison holds quote **type**, not actual quotation or evidence quality, constant. A preferred reading may really be better supported. Thus a preference gap is descriptive association, not proof that the judge substitutes agreement for evidence. The preference task required choosing between claims without a passage and forced a choice even when both readings were reasonable; this may reflect differences in wording or general plausibility. The preference options were presented in one randomized order only; stability after swapping the options was not measured. Some paired claims are competing emphases rather than logically incompatible interpretations. There was no human expert validation of whether both readings were equally defensible or whether altered claims were semantically unsupported. One in-chat model's results do not establish behavior across models or versions. The confidence interval for the difference between gaps includes zero, but this does not prove the gaps equivalent.

The earlier ChatGPT self-judgment was not blinded and must not be described as a second independent judge. It is excluded from this report. A stronger next step is to use another blinded model, genuinely matched evidence, and literary-expert judgments.

## Reproducibility

- `claude_80_items_full.csv`: all 80 passages, claims, quotes, condition labels, scores and rationales.
- `claude_20_passage_contrasts.csv`: paired ratings and per-passage contrasts.
- `inputs/`: user-pasted preference and score CSVs and the five prompts.
- `source_data/cases.json`: original 20 cases and selection metadata.
- `source_data/second_judge_answer_key_PRIVATE.json`: mapping from blind IDs to conditions. Do not disclose to any further blinded judge.
- `source_data/andersen_1597.txt`: Project Gutenberg source, https://www.gutenberg.org/files/1597/1597-0.txt. Text was whitespace-normalized before selecting passages; the source SHA-256 is in cases.json.
- Run `python analyze_claude.py` to recreate the tables and results, using only the Python standard library.
'''
(root / 'README_Claude_Results.md').write_text(doc, encoding='utf-8')
print(json.dumps(summary, indent=2))
