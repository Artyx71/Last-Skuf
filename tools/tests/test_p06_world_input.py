"""Regression protection against partial key loss masked by coarse movement gates.

The positive inputs are immutable, real Godot traces, not copies of the validator's
route implementation. Negative cases keep original engine PASS/displacement
checks intact while corrupting the sampled signals a new gate must reject.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from p06_world_input import validate_world_input


class WorldInputGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = ROOT / 'reports/phases/P06/attempt1/timka-world-native-02'
        cls.recordings = {}
        for mode, digest in [('live', 'be390655f9a4eebfcfe9af8187b53fff53ebd79f4917a11929394e05eaa85684'),
                             ('movie', '78d27436513572122176c999647634249d6278c11ae9f9611d50fb4ff49ad48d')]:
            data = (folder / mode / 'result.json').read_bytes()
            assert hashlib.sha256(data).hexdigest() == digest
            cls.recordings[mode] = json.loads(data)

    def setUp(self):
        self.result = copy.deepcopy(self.recordings['live'])

    def verify(self):
        return validate_world_input(self.result, 'timka', 84)

    def rejected(self):
        self.assertFalse(self.verify()['passed'])

    def test_real_live_and_movie_all1344_samples_and_no_mutation(self):
        before = copy.deepcopy(self.recordings)
        for result in self.recordings.values():
            gate = validate_world_input(result, 'timka', 84)
            self.assertTrue(gate['passed'], gate)
            self.assertEqual(gate['matched_samples'], 672)
            self.assertFalse(gate['phase_approval'])
        self.assertEqual(before, self.recordings)

    def test_single_dropped_walk_key_even_when_original_checks_pass(self):
        self.assertTrue(self.result['passed'])
        self.result['trace'][50]['input_vector'] = [0, 0]
        self.rejected()

    def test_single_lost_shift(self):
        self.result['trace'][85]['run_pressed'] = False
        self.rejected()

    def test_velocity_wrong_despite_correct_input_and_animation(self):
        self.result['trace'][50]['velocity'] = [0, 0]
        self.rejected()

    def test_continuous_route_key_loss(self):
        self.result['trace'][510]['input_vector'] = [0, 0]
        self.rejected()

    def test_swapped_direction(self):
        self.result['trace'][170]['input_vector'] = [1, 0]
        self.rejected()

    def test_missing_input_observation_is_not_approved_by_animation(self):
        del self.result['trace'][50]['input_vector']
        self.rejected()

    def test_incomplete_or_extra_trace(self):
        for count in [0, 671, 673]:
            with self.subTest(count=count):
                self.result = copy.deepcopy(self.recordings['live'])
                self.result['trace'] = (self.result['trace'] + [self.result['trace'][-1]])[:count]
                self.rejected()

    def test_wrong_actor_or_missing_actual_input(self):
        for key, value in [('actor_id', 'gabar'), ('actual_input', False),
                           ('continuous_trace_start', 479), ('scope', 'unknown')]:
            with self.subTest(key=key):
                self.result = copy.deepcopy(self.recordings['live'])
                self.result[key] = value
                self.rejected()

    def test_invalid_signal_types_and_nonfinite_values(self):
        for key, value in [('input_vector', [True, 1]), ('input_vector', [0, float('nan')]),
                           ('velocity', [0, float('inf')]), ('velocity', '84'),
                           ('run_pressed', 0), ('frame', True), ('frame', 4),
                           ('physics_tick', True), ('input_vector', [0, 10**1000])]:
            with self.subTest(key=key, value=value):
                self.result = copy.deepcopy(self.recordings['live'])
                self.result['trace'][50][key] = value
                self.rejected()

    def test_reversed_physics_tick(self):
        self.result['trace'][50]['physics_tick'] = 1
        self.rejected()

    def test_wrong_phase_or_route(self):
        for key, value in [('animation', 'walk_right'), ('sequence', 'continuous')]:
            self.result = copy.deepcopy(self.recordings['live'])
            self.result['trace'][50][key] = value
            self.rejected()

    def test_focus_observation_does_not_claim_focus_efficacy(self):
        for point in self.result['trace']:
            point['window_focused'] = False
        gate = self.verify()
        self.assertTrue(gate['passed'])
        self.assertFalse(gate['focus_efficacy_approval'])
        self.assertFalse(gate['manual_keyboard_approval'])

    def test_invalid_speed_or_report_fails_closed(self):
        for speed in [None, 0, -1, True, float('nan'), float('inf'), 10**1000]:
            self.assertFalse(validate_world_input(self.result, 'timka', speed)['passed'])
        for result in [None, [], {}, {'trace': [None]}]:
            self.assertFalse(validate_world_input(result, 'timka', 84)['passed'])


if __name__ == '__main__':
    unittest.main()
