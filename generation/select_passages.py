import hashlib,json,random,re
from pathlib import Path

source=Path(__file__).resolve().parent/'andersen_1597.txt'
text=source.read_text(encoding='utf-8')
heads=["THE EMPEROR'S NEW CLOTHES","THE SWINEHERD","THE REAL PRINCESS","THE SHOES OF FORTUNE","THE FIR TREE","THE SNOW QUEEN","THE LEAP-FROG","THE ELDERBUSH","THE BELL","THE OLD HOUSE","THE HAPPY FAMILY","THE STORY OF A MOTHER","THE FALSE COLLAR","THE SHADOW","THE LITTLE MATCH GIRL","THE DREAM OF LITTLE TUK","THE NAUGHTY BOY","THE RED SHOES"]
positions=[re.search(r'^'+re.escape(h)+r'\s*$',text,re.M).start() for h in heads]
end=text.index('*** END OF THE PROJECT GUTENBERG EBOOK')
books=[]
for i,h in enumerate(heads):
    start=positions[i]+len(h)
    stop=positions[i+1] if i+1<len(heads) else end
    raw=text[start:stop]
    # The experiment presents a single space for all original line/paragraph breaks.
    normalized=re.sub(r'\s+', ' ',raw).strip()
    # Start at a paragraph boundary; for each tale, choose a reproducible location
    # away from the very end where ~300 words are available.
    paragraphs=[re.sub(r'\s+',' ',p).strip() for p in re.split(r'\n\s*\n',raw) if len(p.split())>=15]
    offsets=[]
    for p in paragraphs:
        pos=normalized.find(p)
        if pos>=0 and len(normalized[pos:].split())>=260:
            offsets.append(pos)
    books.append((h,normalized,offsets))
rng=random.Random(20261108)
selected=[]
for k in list(range(18))+[3,5]:
    title,book,offsets=books[k]
    # First 18: one passage per tale; last two: additional passages from long tales.
    eligible=[p for p in offsets if all(not (x['title']==title and abs(x['start_offset']-p)<2200) for x in selected)]
    start=rng.choice(eligible or offsets)
    tail=book[start:]
    matches=list(re.finditer(r'\S+',tail))
    cap=matches[min(319,len(matches)-1)].end()
    floor=matches[min(249,len(matches)-1)].end()
    stop=None
    for match in re.finditer(r'[.!?][”’"\']?(?=\s|$)',tail):
        if floor<=match.end()<=cap:
            stop=match.end()
    if stop is None: stop=cap
    passage=tail[:stop].strip()
    selected.append({'id':f'P{len(selected)+1:02d}','title':title.title(),'start_offset':start,'word_count':len(passage.split()),'passage':passage})
out={'source':'https://www.gutenberg.org/files/1597/1597-0.txt','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'selection_seed':20261108,'selection_note':'One reproducibly sampled paragraph-start passage per tale, plus two from long tales; original whitespace normalized to single spaces before selection. No interpretive screening.', 'passages':selected}
Path(__file__).with_name('passages.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in selected:
    print('\n###',p['id'],p['title'],p['word_count'])
    print(p['passage'])
