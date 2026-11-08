"""Analyze the pre-recorded, unblinded, one-chat pilot; no API calls."""
from collections import Counter
from pathlib import Path
import csv, json, random, statistics

root=Path(__file__).resolve().parent
cases=json.loads((root/'cases.json').read_text(encoding='utf-8'))['cases']
orders=json.loads((root/'preference_order.json').read_text(encoding='utf-8'))
prefs=json.loads((root/'preferences_in_chat.json').read_text(encoding='utf-8'))
ratings=json.loads((root/'judgments_in_chat.json').read_text(encoding='utf-8'))
assert len(cases)==20 and len(ratings)==len(prefs)==20
assert set(orders)==set(prefs)==set(ratings)=={c['id'] for c in cases}
fields=['passage_id','title','word_count','question','passage','preferred_reading','reading','quote_status','claim','quote','quote_exactly_in_passage','score','rationale']
rows=[]
unit=[]
for c in cases:
    pid=c['id']; preferred=orders[pid][prefs[pid]]; other='B' if preferred=='A' else 'A'
    vals=ratings[pid]
    for side in ('A','B'):
        for qtype in ('real','fake'):
            quote=c[side][qtype+'_quote']; exact=quote in c['passage']; score=vals[side][qtype]
            assert exact == (qtype=='real') and isinstance(score,int) and 1<=score<=5
            reason=vals[side]['reason']
            if qtype=='fake': reason='The displayed quote is not verbatim. '+reason
            rows.append({'passage_id':pid,'title':c['title'],'word_count':c['word_count'],'question':c['question'],'passage':c['passage'],'preferred_reading':preferred,'reading':side,'quote_status':qtype,'claim':c[side]['claim'],'quote':quote,'quote_exactly_in_passage':exact,'score':score,'rationale':reason})
    real=(vals['A']['real']+vals['B']['real'])/2
    fake=(vals['A']['fake']+vals['B']['fake'])/2
    agreement_real=vals[preferred]['real']-vals[other]['real']
    agreement_fake=vals[preferred]['fake']-vals[other]['fake']
    unit.append({'id':pid,'preferred':preferred,'real_mean':real,'fake_mean':fake,'evidence_gap':real-fake,'agreement_real':agreement_real,'agreement_fake':agreement_fake,'agreement_gap':(agreement_real+agreement_fake)/2})
assert len(rows)==80
with (root/'item_scores.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
with (root/'passage_scores.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(unit[0])); writer.writeheader(); writer.writerows(unit)

def mean(field): return statistics.mean(x[field] for x in unit)
def quantile(sorted_vals, q):
    position=(len(sorted_vals)-1)*q
    lo=int(position); hi=min(lo+1,len(sorted_vals)-1); f=position-lo
    return sorted_vals[lo]*(1-f)+sorted_vals[hi]*f

rng=random.Random(20261108)
boots={'evidence_gap':[],'agreement_gap':[],'agreement_real':[],'agreement_fake':[],'difference':[]}
for _ in range(20000):
    sample=[rng.choice(unit) for _ in unit]
    for name in ('evidence_gap','agreement_gap','agreement_real','agreement_fake'):
        boots[name].append(statistics.mean(x[name] for x in sample))
    boots['difference'].append(statistics.mean(x['evidence_gap']-x['agreement_gap'] for x in sample))
summary={
 'judge':'One ChatGPT in this conversation; same judge authored the cases and knew condition labels',
 'independence':'Not blinded; sequential comparisons in same context; preference choices contaminated by prior access to passages and quote labels',
 'n_passages':len(unit),'n_readings':len(unit)*2,'n_items':len(rows),'n_judges':1,
 'real_mean':mean('real_mean'),'fake_mean':mean('fake_mean'),
 'preference_counts':dict(Counter(x['preferred'] for x in unit)),
 'score_counts':dict(sorted(Counter(x['score'] for x in rows).items())),
 'bootstrap':{'unit':'passage','resamples':20000,'seed':20261108,'method':'percentile'},
}
for key in ('evidence_gap','agreement_gap','agreement_real','agreement_fake'):
    v=sorted(boots[key]); summary[key]={'estimate':mean(key),'ci_95':[quantile(v,.025),quantile(v,.975)]}
v=sorted(boots['difference']);summary['evidence_minus_agreement']={'estimate':mean('evidence_gap')-mean('agreement_gap'),'ci_95':[quantile(v,.025),quantile(v,.975)]}
(root/'results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
def fmt(x): return f"{x['estimate']:.3f} (95% bootstrap interval {x['ci_95'][0]:.3f} to {x['ci_95'][1]:.3f})"
report=f'''# Andersen in-chat pilot: exploratory results

## Status

20 passages from 18 Andersen tales; 40 interpretive claims and 80 claim/quote items. One ChatGPT judge in this conversation recorded 20 forced-choice preferences and 80 scores. The same ChatGPT instance authored the questions, claims and altered quotations, read all passages, knew which quotations were altered, and scored items together in the same conversation. Preference presentation was limited to questions and claims, but the judge had already seen the passages and evidence; it was not blinded. This was **not** the planned independent, two-model evaluation, and results cannot be attributed to GPT-5 mini or GPT-4.1 mini.

## Scores (1 to 5)

- Mean scores: genuine quotation {summary['real_mean']:.3f}; altered quotation {summary['fake_mean']:.3f}.
- Evidence gap, genuine minus altered: **{fmt(summary['evidence_gap'])}**.
- Agreement gap, preferred minus nonpreferred, averaged over genuine and altered evidence types: **{fmt(summary['agreement_gap'])}**.
- Agreement gap among genuine quotations: {fmt(summary['agreement_real'])}.
- Agreement gap among altered quotations: {fmt(summary['agreement_fake'])}.
- Evidence gap minus agreement gap: {fmt(summary['evidence_minus_agreement'])}.

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
'''
(root/'README_results.md').write_text(report,encoding='utf-8')
print(json.dumps(summary,indent=2))
