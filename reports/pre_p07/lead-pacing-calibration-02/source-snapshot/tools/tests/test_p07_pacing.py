import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from p07_pacing import CONTEXTS, analyze, load_contract, percentile, validate_pins


class PacingValidation(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.contract = Path(self.directory.name) / 'contract.json'
        self.review = Path(self.directory.name) / 'review.json'
        self.data = {'schema': 1, 'scope': 'H04_PILOT_ACCEPTANCE', 'source_inventory_sha256': {'TEST_ONLY': 'a'},
                     'limits': {'accept_p95_ms': 34, 'render_p95_ms': 60, 'frame_p95_ms': 24,
                                'frame_p99_ms': 32, 'restart_max_ms': 1000}}
        self.verdict = {'schema': 1, 'status': 'PASS_COMPONENT', 'scope': 'H04_CALIBRATION_CONTRACT',
                        'role': 'LEAD_REVIEWER', 'independent_of_author': True, 'reviewer': 'TEST_ONLY_REVIEWER', 'must_fix': []}
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
        data, pins = load_contract(self.contract, self.review, {'TEST_ONLY': 'a'})
        self.assertEqual(data, self.data)
        validate_pins(pins)

    def test_loaded_approval_pinned_through_run(self):
        data, pins = load_contract(self.contract, self.review, {'TEST_ONLY': 'a'})
        self.review.write_text(self.review.read_text() + '\n')
        with self.assertRaises(ValueError): validate_pins(pins)
        self.assertEqual(data, self.data)

    def test_duplicate_contract_and_review_keys_rejected(self):
        for target in [self.contract, self.review]:
            self.save()
            original = target.read_text()
            target.write_text(original[:-1] + ',"schema":1}')
            if target == self.contract:
                self.verdict['contract_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
                self.review.write_text(json.dumps(self.verdict))
            with self.assertRaises(ValueError): load_contract(self.contract, self.review, {'TEST_ONLY': 'a'})

    def test_no_review_cannot_start_acceptance(self):
        with self.assertRaises(ValueError): load_contract(self.contract, None, {'TEST_ONLY': 'a'})

    def test_changed_contract_cannot_start_acceptance(self):
        self.contract.write_text(self.contract.read_text() + '\n')
        with self.assertRaises(ValueError): load_contract(self.contract, self.review, {'TEST_ONLY': 'a'})

    def test_unresolved_or_self_approval_cannot_start_acceptance(self):
        for key, value in [('status', 'BLOCKED'), ('role', 'QA'), ('independent_of_author', False), ('reviewer', '/root'), ('reviewer', {}), ('must_fix', ['TEST_ONLY'])]:
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
               'physics': [{'usec': 1}], 'contacts': [{}] * 16,
               'requests': [{'id': i+1, 'context': CONTEXTS[i//6], 'kind': (['move']*4+['melee','restart'])[i%6],
                             'input_usec': i*10+50, 'accepted_usec': i*10+49, 'render_usec': i*10+55} for i in range(48)]}
        with self.assertRaises(ValueError): analyze(raw)


if __name__ == '__main__':
    unittest.main()
