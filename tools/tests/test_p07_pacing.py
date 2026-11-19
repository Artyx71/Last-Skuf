import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from p07_pacing import analyze, load_contract, percentile


class PacingValidation(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.contract = Path(self.directory.name) / 'contract.json'
        self.review = Path(self.directory.name) / 'review.json'
        self.data = {'scope': 'H04_PILOT_ACCEPTANCE', 'source_inventory_sha256': {'TEST_ONLY': 'a'},
                     'limits': {'accept_p95_ms': 34, 'render_p95_ms': 60, 'frame_p95_ms': 24,
                                'frame_p99_ms': 32, 'restart_max_ms': 1000}}
        self.verdict = {'status': 'PASS_COMPONENT', 'scope': 'H04_CALIBRATION_CONTRACT',
                        'independent_of_author': True, 'reviewer': 'TEST_ONLY_REVIEWER', 'must_fix': []}
        self.save()

    def save(self):
        self.contract.write_text(json.dumps(self.data))
        self.verdict['contract_sha256'] = hashlib.sha256(self.contract.read_bytes()).hexdigest()
        self.review.write_text(json.dumps(self.verdict))

    def test_percentile_and_bad_samples(self):
        self.assertEqual(percentile([30, 10, 20], .95), 30)
        for samples in [[], [float('nan')], [-1]]:
            with self.assertRaises(ValueError): percentile(samples, .5)

    def test_exact_independent_contract(self):
        self.assertEqual(load_contract(self.contract, self.review, {'TEST_ONLY': 'a'}), self.data)

    def test_no_review_cannot_start_acceptance(self):
        with self.assertRaises(ValueError): load_contract(self.contract, None, {'TEST_ONLY': 'a'})

    def test_changed_contract_cannot_start_acceptance(self):
        self.contract.write_text(self.contract.read_text() + '\n')
        with self.assertRaises(ValueError): load_contract(self.contract, self.review, {'TEST_ONLY': 'a'})

    def test_unresolved_or_self_approval_cannot_start_acceptance(self):
        for key, value in [('status', 'BLOCKED'), ('independent_of_author', False), ('reviewer', '/root'), ('must_fix', ['TEST_ONLY'])]:
            with self.subTest(key=key):
                before = dict(self.verdict)
                self.verdict[key] = value
                self.save()
                with self.assertRaises(ValueError): load_contract(self.contract, self.review, {'TEST_ONLY': 'a'})
                self.verdict = before

    def test_missing_or_weakened_limit_cannot_start_acceptance(self):
        for weakened in [True, False]:
            self.data['limits']['restart_max_ms'] = 1001
            if not weakened: self.data['limits'].pop('restart_max_ms')
            self.save()
            with self.assertRaises(ValueError): load_contract(self.contract, self.review, {'TEST_ONLY': 'a'})

    def test_changed_source_cannot_start_acceptance(self):
        with self.assertRaises(ValueError): load_contract(self.contract, self.review, {'TEST_ONLY': 'changed'})

    def test_non_monotonic_raw_observations_rejected(self):
        raw = {'schema': 1, 'failed': 0, 'draws': [{'usec': 100}] * 120}
        with self.assertRaises(ValueError): analyze(raw)

    def test_reversed_action_timestamps_rejected(self):
        raw = {'schema': 1, 'failed': 0,
               'draws': [{'usec': i + 1, 'segment': 'idle_calibration'} for i in range(120)],
               'requests': [{'id': i, 'context': str(i % 8), 'input_usec': 20,
                             'accepted_usec': 10, 'render_usec': 30} for i in range(48)]}
        with self.assertRaises(ValueError): analyze(raw)


if __name__ == '__main__':
    unittest.main()
