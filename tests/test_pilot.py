"""Integrity and end-to-end checks for the preserved pilot artifacts."""
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PilotDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / 'source_data' / 'cases.json').read_text(encoding='utf-8'))
        cls.key = json.loads((ROOT / 'source_data' / 'second_judge_answer_key_PRIVATE.json').read_text(encoding='utf-8'))

    def test_source_and_quotation_integrity(self):
        source = (ROOT / 'source_data' / 'andersen_1597.txt').read_bytes()
        self.assertEqual(source, (ROOT / 'generation' / 'andersen_1597.txt').read_bytes())
        start = source.index(b'*** START OF THE PROJECT GUTENBERG EBOOK 1597 ***')
        end_marker = b'*** END OF THE PROJECT GUTENBERG EBOOK 1597 ***\n'
        end = source.index(end_marker, start) + len(end_marker)
        self.assertIn(b'https://www.gutenberg.org/policy/license.html', source[:start])
        self.assertIn(b'START: FULL LICENSE', source[end:])
        self.assertEqual(hashlib.sha256(source[start:end]).hexdigest(), self.cases['source_sha256'])
        cases = self.cases['cases']
        self.assertEqual(len(cases), 20)
        self.assertEqual(len({case['id'] for case in cases}), 20)
        self.assertEqual(len({case['title'] for case in cases}), 18)
        for case in cases:
            with self.subTest(passage=case['id']):
                self.assertEqual(len(case['passage'].split()), case['word_count'])
                for side in ('A', 'B'):
                    self.assertIn(case[side]['real_quote'], case['passage'])
                    self.assertNotIn(case[side]['fake_quote'], case['passage'])

    def test_scoring_batches_do_not_repeat_a_passage(self):
        records = self.key['items']
        self.assertEqual(len(records), 80)
        for batch in range(1, 5):
            with self.subTest(batch=batch):
                subset = {k: v for k, v in records.items() if v['batch'] == batch}
                self.assertEqual(len(subset), 20)
                self.assertEqual(len({v['passage_id'] for v in subset.values()}), 20)
                prompt = (ROOT / 'inputs' / 'blind_prompts' / f'0{batch}_scores.txt').read_text(encoding='utf-8')
                self.assertEqual(set(re.findall(r'^ITEM (I\d{4})$', prompt, re.M)), set(subset))
                self.assertNotIn('quote_status', prompt)
                self.assertNotIn('answer key', prompt.lower())
        for case in self.cases['cases']:
            condition_set = {(v['reading'], v['quote_status']) for v in records.values() if v['passage_id'] == case['id']}
            self.assertEqual(condition_set, {('A', 'real'), ('A', 'fake'), ('B', 'real'), ('B', 'fake')})

    def test_preference_prompt_omits_passages_and_quotes(self):
        prompt = (ROOT / 'inputs' / 'blind_prompts' / '00_preferences.txt').read_text(encoding='utf-8')
        self.assertEqual(set(re.findall(r'^C\d{3}$', prompt, re.M)), set(self.key['preference']))
        self.assertNotIn('PASSAGE:', prompt)
        self.assertNotIn('CITED QUOTATION:', prompt)
        for case in self.cases['cases']:
            self.assertNotIn(case['passage'], prompt)

    def test_saved_judgments_cover_every_blind_id(self):
        observations = []
        for batch in range(1, 5):
            with (ROOT / 'inputs' / f'Claude_Scores_Batch_{batch}.csv').open(encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f))
            expected = {k for k, v in self.key['items'].items() if v['batch'] == batch}
            self.assertEqual({r['item_id'] for r in rows}, expected)
            self.assertEqual(len(rows), 20)
            self.assertTrue(all(r['score'] in ('1', '2', '3', '4', '5') and r['rationale'] for r in rows))
            observations.extend(rows)
        self.assertEqual(len(observations), 80)
        self.assertEqual(len({x['item_id'] for x in observations}), 80)

    def test_clean_analysis_reproduces_recorded_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            shutil.copy2(ROOT / 'analyze_claude.py', target)
            shutil.copytree(ROOT / 'inputs', target / 'inputs')
            shutil.copytree(ROOT / 'source_data', target / 'source_data')
            result = subprocess.run([sys.executable, 'analyze_claude.py'], cwd=target, capture_output=True, text=True, check=True)
            output = json.loads(result.stdout)
            self.assertEqual(output['n_preferences'], 20)
            self.assertEqual(output['n_judged_items'], 80)
            self.assertEqual(output['evidence_gap']['estimate'], 1.125)
            self.assertEqual(output['agreement_gap']['estimate'], 0.875)
            self.assertEqual(output['rationales_recognizing_exact'], 40)
            self.assertEqual(output['rationales_recognizing_altered'], 40)
            for filename in ('results.json', 'README_Claude_Results.md', 'claude_20_passage_contrasts.csv', 'claude_80_items_full.csv'):
                self.assertTrue((target / filename).is_file(), filename)

    def test_case_construction_reproduces_saved_data(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ('andersen_1597.txt', 'select_passages.py', 'build_cases.py'):
                shutil.copy2(ROOT / 'generation' / name, target / name)
            subprocess.run([sys.executable, 'select_passages.py'], cwd=target, capture_output=True, text=True, check=True)
            subprocess.run([sys.executable, 'build_cases.py'], cwd=target, capture_output=True, text=True, check=True)
            regenerated = json.loads((target / 'cases.json').read_text(encoding='utf-8'))
            self.assertEqual(regenerated, self.cases)

    def test_blind_prompt_generation_reproduces_saved_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ('cases.json', 'preference_order.json', 'create_blind_packet.py'):
                shutil.copy2(ROOT / 'generation' / name, target / name)
            subprocess.run([sys.executable, 'create_blind_packet.py'], cwd=target, capture_output=True, text=True, check=True)
            regenerated_key = json.loads((target / 'second_judge_answer_key_PRIVATE.json').read_text(encoding='utf-8'))
            self.assertEqual(regenerated_key, self.key)
            for name in ('00_preferences.txt', '01_scores.txt', '02_scores.txt', '03_scores.txt', '04_scores.txt'):
                self.assertEqual((target / 'second_judge_blind_prompts' / name).read_text(encoding='utf-8'),
                                 (ROOT / 'inputs' / 'blind_prompts' / name).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
