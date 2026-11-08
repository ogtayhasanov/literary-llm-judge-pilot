import json
from pathlib import Path

# Each row: passage ID, question, A claim, A real quote, A invented quote,
# B claim, B real quote, B invented quote. Quotes are exact single substrings.
rows = [
('P01','What chiefly motivates the officer to praise the imaginary cloth?',
 'The officer is chiefly afraid of being exposed as personally incompetent.', 'no one shall know anything about it', 'no one must learn that I cannot see it',
 'The officer is chiefly protecting the material benefits of his office.', 'my good, profitable office', 'my comfortable and profitable position'),
('P02','How should the princess\'s demand on her attendants be understood?',
 'The princess uses her rank to make her attendants bear a burden they reject.', 'Remember that you owe everything to me', 'Do not forget that you all depend on me',
 'The princess treats the bargain as a shared sacrifice she is also willing to make.', 'If I can kiss him, surely you can', 'If I am willing to kiss him, you can do the same'),
('P03','What does the queen\'s test of the visitor mainly reveal?',
 'The queen is trying to establish whether the visitor truly belongs to the royal family.', 'Ah! we shall soon see that!', 'We shall soon discover if she is a princess',
 'The test exposes the physical cruelty behind royal gatekeeping.', 'am all over black and blue', 'my whole body is bruised and aching'),
('P04','What is the narrator primarily mocking in the discussion of the moon?',
 'The narrator mocks the inhabitants\' self-centered certainty about their place in the universe.', 'the real heart of the universe', 'the true center of the entire universe',
 'The narrator mocks political deference to a supposedly powerful foreign realm.', 'not run counter to the moon', 'be careful not to offend the moon'),
('P05','What matters most to the tree during the celebration?',
 'The tree is chiefly anxious that its decorated appearance will be damaged.', 'he should lose something of his splendor', 'he might be robbed of his shining beauty',
 'The tree is chiefly distressed at being excluded from the children\'s enjoyment.', 'Am I to do nothing whatever?', 'Must I stand here and take no part?'),
('P06','Where does Gerda\'s power principally come from?',
 'Gerda\'s strength is portrayed as an inward quality grounded in her innocence.', 'that power lies in her heart', 'her greatest strength is hidden inside her heart',
 'Gerda\'s strength is demonstrated through the help of the beings she encounters.', 'how men and animals are forced to serve her', 'how people and animals come to her aid'),
('P07','How does the scene present aristocratic status?',
 'The scene treats noble birth as a serious reason to regard a contestant as suitable.', 'for he had noble blood', 'because he was descended from noble blood',
 'The scene ridicules the shallow and absurd claims used to establish noble status.', 'a green uniform, which he had by right of birth', 'his green coat, which he inherited at birth'),
('P08','What does the preserved flower chiefly sustain?',
 'The flower sustains the traveler\'s personal bond with the maiden.', 'the little maiden, peeping forth with her bright blue eyes', 'the maiden looking at him with her bright blue eyes',
 'The flower sustains the traveler\'s attachment to his Danish homeland.', 'the fragrance of the Danish groves', 'the remembered scent of the Danish woods'),
('P09','What does the focus on the king\'s son chiefly communicate?',
 'The focus celebrates the prince\'s personal resolution in pursuing the bell.', 'he was an excellent and resolute youth', 'he was an admirable and determined young man',
 'The focus exposes the preference given to a privileged traveler over the poor boy.', 'it is him that we will follow', 'we shall follow the king\'s son instead'),
('P10','What is the main effect of the old house\'s animated details?',
 'The house seems to welcome the boy as if it were a living host.', 'The little boy comes!', 'The young visitor has arrived!',
 'The animation draws attention to the neglected house\'s dilapidation and overgrowth.', 'with large holes and long crevices', 'with gaping holes and cracks in its walls'),
('P11','How should the snails\' inheritance speech be read?',
 'The speech primarily expresses the parents\' affection and concern for their children.', 'as a dowry and inheritance, the whole forest of burdocks', 'the whole burdock forest as a gift for their children',
 'The speech satirizes the family\'s failure to recognize the danger in its ideal future.', 'be boiled black, and laid on silver dishes', 'be cooked dark and served on silver plates'),
('P12','How should Night\'s demand that the mother sing be understood?',
 'Night cruelly delays the mother while her child is being taken away.', 'But Night stood still and mute', 'But Night would not let the mother pass',
 'Night makes the mother revisit the loving bond with her child before continuing.', 'I saw thy tears whilst thou sang\'st them', 'I heard the love in every song thou sangest'),
('P13','What is the main target of the scene\'s criticism of the collar?',
 'The scene criticizes the collar for ignoring the garter\'s refusal and personal boundaries.', 'I will thank you not to speak to me', 'I ask you to leave me alone',
 'The scene criticizes the collar chiefly for its false claims of social standing.', 'it was his master who had them: but he boasted', 'they belonged to his master, though he claimed them as his own'),
('P14','Why does the princess accept the shadow\'s explanation?',
 'Flattery about her eyesight makes the princess trust the shadow\'s explanation.', 'you see too clearly, but it has decreased, you are cured', 'your clear sight has weakened, and now you are cured',
 'Her attraction to the stranger makes her willing to believe his explanation.', 'I am extremely fond of that stranger', 'I have grown very fond of this stranger'),
('P15','How do the girl\'s visions function in this passage?',
 'The visions offer the girl a brief source of comfort in the cold.', 'It was a warm, bright flame, like a candle', 'It was a bright and comforting little flame',
 'The visions emphasize how fragile and temporary her comfort is.', 'the small flame went out, the stove vanished', 'the flame died away and the warm stove disappeared'),
('P16','What view of Denmark does the sequence chiefly emphasize?',
 'The sequence celebrates modern development and the improvement of towns.', 'a town that is just rising into importance', 'a town that is becoming prosperous and important',
 'The sequence celebrates national history and the continuity of the monarchy.', 'all the kings and queens of Denmark, hand in hand', 'the kings and queens of Denmark walked hand in hand'),
('P17','What kind of danger does Cupid represent?',
 'Cupid represents the danger of trusting someone whom one has welcomed and helped.', 'he who had taken him into his warm room', 'the poet who had given the boy warmth and shelter',
 'Cupid represents a danger that can strike people without their deliberately welcoming it.', 'unperceived, he thrusts an arrow to their bosom', 'unnoticed, he sends an arrow into their hearts'),
('P18','What chiefly shapes Karen\'s desire for the red shoes?',
 'Karen\'s desire is shaped by imitating the princess and aristocratic fashion.', 'just like those the princess had worn', 'exactly like the princess\'s splendid shoes',
 'Karen is drawn chiefly to the shoes\' immediate visual beauty.', 'How beautiful they were!', 'How wonderfully beautiful the shoes appeared!'),
('P19','What chiefly motivates the watchman\'s wish to visit the heavens?',
 'The wish expresses dissatisfaction with bodily earthly life.', 'my body might stay here on the steps for what I care', 'I would gladly leave my body behind on these steps',
 'The wish expresses curiosity about celestial objects.', 'examining the little glimmering things somewhat nearer', 'looking more closely at the little shining stars'),
('P20','How should the tame Raven\'s help to Gerda be understood?',
 'The Raven helps Gerda out of sympathy for her distress.', 'Your tale is very affecting', 'Your sad story has moved me deeply',
 'The Raven\'s help is conditioned by an expectation of future gratitude.', 'when you enjoy honor and distinction, that you possess a grateful heart', 'when you are rich and honored, remember to thank me')
]

source=json.loads(Path(__file__).with_name('passages.json').read_text(encoding='utf-8'))
passages={p['id']:p for p in source['passages']}
assert len(rows)==20 and len({r[0] for r in rows})==20
cases=[]
for pid,question,ac,ar,af,bc,br,bf in rows:
    p=passages[pid]
    for side,real,fake in [('A',ar,af),('B',br,bf)]:
        if real not in p['passage']:
            raise ValueError(f'{pid} {side} real quote not present: {real!r}')
        if fake in p['passage']:
            raise ValueError(f'{pid} {side} invented quote present: {fake!r}')
        if real==fake or len(real.split())<4 or len(fake.split())<4:
            raise ValueError(f'{pid} {side} unusable quote')
    cases.append({**p,'question':question,'A':{'claim':ac,'real_quote':ar,'fake_quote':af},'B':{'claim':bc,'real_quote':br,'fake_quote':bf}})
out={'source':source['source'],'source_sha256':source['source_sha256'],'selection_seed':source['selection_seed'],'selection_note':source['selection_note'],'generation':'Questions, claims, and invented/real quote selections authored by ChatGPT in this conversation (not independently expert annotated; no external generator API used).', 'cases':cases}
Path(__file__).with_name('cases.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 20 cases, 40 exact real quotations, 40 invented quotations absent from their displayed passages.')
print('Words per passage:', min(c['word_count'] for c in cases), 'to', max(c['word_count'] for c in cases))
