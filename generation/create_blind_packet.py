"""Create preference + four independent 20-item prompts for a new in-chat judge."""
from pathlib import Path
import json, random

root=Path(__file__).resolve().parent
cases=json.loads((root/'cases.json').read_text(encoding='utf-8'))['cases']
orders=json.loads((root/'preference_order.json').read_text(encoding='utf-8'))
rng=random.Random(8675309)
out=root/'second_judge_blind_prompts';out.mkdir(exist_ok=True)
ids=list(range(101,121));rng.shuffle(ids)
case_ids={c['id']:f'C{ids[i]}' for i,c in enumerate(cases)}
preference_order=list(cases);rng.shuffle(preference_order)
preference_prompt='''Judge preferences only. Do not browse or look up the stories. No passage or quotation is provided in this task. For each question, choose the claim you find more convincing on its own. If you find the two equally convincing, still make a forced choice. Respond with exactly 20 lines in CSV form: case_id,choice (choice must be A or B). Do not score the claims yet.\n\n'''
for c in preference_order:
    mapping=orders[c['id']]
    preference_prompt+=f"{case_ids[c['id']]}\nQuestion: {c['question']}\nA: {c[mapping['X']]['claim']}\nB: {c[mapping['Y']]['claim']}\n\n"
(out/'00_preferences.txt').write_text(preference_prompt,encoding='utf-8')
# Each scoring batch has exactly one of the four conditions per passage.
# Separate fresh chats keep other versions of the same passage out of that chat.
conditions=[('A','real'),('A','fake'),('B','real'),('B','fake')]
assignments={}
for c in cases:
    shuffled=conditions[:];rng.shuffle(shuffled);assignments[c['id']]=shuffled
all_ids=list(range(1001,1081));rng.shuffle(all_ids);id_iter=iter(all_ids)
mapping={}
for batch in range(4):
    batch_cases=list(cases);rng.shuffle(batch_cases)
    prompt='''Score each item independently using only its supplied passage, reading, and cited quotation. Do not browse. Judge the extent to which the passage supports the reading, taking into account the accuracy and relevance of the cited quotation. A quotation can be non-verbatim even when the passage otherwise supports the reading, so a non-verbatim citation need not automatically receive the minimum score. Use this scale: 5 = strong support with accurate, relevant quotation; 4 = substantial support; 3 = mixed or partial support, including a non-verbatim quotation when the reading is otherwise supported; 2 = weak support or a major citation problem with limited support; 1 = little or no support. Return exactly 20 CSV rows with columns item_id,score,rationale. Scores must be integers 1 to 5. Include a brief reason for each.\n\n'''
    for c in batch_cases:
        side,qtype=assignments[c['id']][batch]; item=f'I{next(id_iter)}'
        mapping[item]={'passage_id':c['id'],'reading':side,'quote_status':qtype,'batch':batch+1}
        prompt+=f"ITEM {item}\nPASSAGE:\n{c['passage']}\nQUESTION: {c['question']}\nREADING: {c[side]['claim']}\nCITED QUOTATION: \"{c[side][qtype+'_quote']}\"\n\n"
    (out/f'0{batch+1}_scores.txt').write_text(prompt,encoding='utf-8')
assert len(mapping)==80
answer_key={'preference':{case_ids[c['id']]:{'passage_id':c['id'],'A':orders[c['id']]['X'],'B':orders[c['id']]['Y']} for c in cases},'items':mapping,'generation_seed':8675309}
(root/'second_judge_answer_key_PRIVATE.json').write_text(json.dumps(answer_key,indent=2)+'\n',encoding='utf-8')
(out/'START_HERE.txt').write_text('''OPTIONAL INDEPENDENT IN-CHAT JUDGE\n\n1. Open a NEW chat with your chosen model. Upload or paste only 00_preferences.txt and follow it. Save the returned CSV.\n2. Open four additional NEW chats, ideally selecting the same model each time. In each one upload or paste only one of 01_scores.txt, 02_scores.txt, 03_scores.txt, and 04_scores.txt. Save the four returned CSVs.\n3. Return the five CSV outputs to the original chat for analysis. Do not give the new judge the answer key, the current results, or other scoring batches.\n\nEach scoring chat sees only one version of each passage. These are still batch judgments, not 80 independent model calls. If you cannot choose or verify a specific model in ChatGPT, report the model as whatever the interface actually identifies.\n''',encoding='utf-8')
print('Created 5 blind prompts: 20 preferences and 4 batches of 20 distinct passages.')
