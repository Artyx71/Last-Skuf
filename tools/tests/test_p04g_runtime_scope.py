"""Prevent partial or mislabelled PCM inventories from passing the selected scope."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_p04g_audio import BASE_RUNTIME_NAMES, FULL_RUNTIME_NAMES, runtime_capture_plan


class RuntimeScopeTest(unittest.TestCase):
    def test_default_still_requires_all_five(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in BASE_RUNTIME_NAMES:
                (root / (name + '.wav')).touch()
            self.assertFalse(runtime_capture_plan(root)[2])
            self.assertTrue(runtime_capture_plan(root, BASE_RUNTIME_NAMES)[2])
            for name in FULL_RUNTIME_NAMES:
                (root / (name + '.wav')).touch()
            self.assertTrue(runtime_capture_plan(root)[2])
            self.assertFalse(runtime_capture_plan(root, BASE_RUNTIME_NAMES)[2])

    def test_same_count_wrong_names_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ['full_replay', 'unrelated_replay']:
                (root / (name + '.wav')).touch()
            self.assertFalse(runtime_capture_plan(root, BASE_RUNTIME_NAMES)[2])

    def test_invalid_scopes_are_rejected(self):
        for names in [(), ('full_replay',), BASE_RUNTIME_NAMES + ('full_replay',),
                      BASE_RUNTIME_NAMES + ('../escape',),
                      BASE_RUNTIME_NAMES + ('linux_export_replay',),
                      BASE_RUNTIME_NAMES + ('wine_export_replay',)]:
            with self.subTest(names=names), self.assertRaises(ValueError):
                runtime_capture_plan(Path('/unused'), names)


if __name__ == '__main__':
    unittest.main()
