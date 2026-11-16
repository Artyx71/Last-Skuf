"""Unsafe source reuse and tampered proof inputs must fail before an engine starts."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from continue_p06_native import check_changes, checked_path, verify_artifacts
from verify_p06 import sha


class ContinuationSafetyTest(unittest.TestCase):
    def test_production_change_cannot_be_approved_by_manifest(self):
        path = 'game/scripts/actors/character_player.gd'
        with self.assertRaises(ValueError):
            check_changes({path: 'old'}, {path: 'new'}, {path: {'before': 'old', 'after': 'new'}})
        fixture = 'game/tests/pasha_moving_shot_replay.gd'
        check_changes({fixture: 'old'}, {fixture: 'new'}, {fixture: {'before': 'old', 'after': 'new'}})
        with self.assertRaises(ValueError):
            check_changes({fixture: 'old'}, {fixture: 'unreviewed'}, {fixture: {'before': 'old', 'after': 'new'}})

    def test_escaped_proof_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for path in ['../outside', '/outside', None]:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    checked_path(root, path)

    def test_missing_duplicate_or_modified_proof_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'proof.json'
            path.write_text('original')
            item = {'path': 'proof.json', 'sha256': sha(path)}
            verify_artifacts(root, [item])
            for inventory in [[], [item, item], [{'path': 'missing', 'sha256': '0' * 64}]]:
                with self.assertRaises(ValueError):
                    verify_artifacts(root, inventory)
            path.write_text('changed')
            with self.assertRaises(ValueError):
                verify_artifacts(root, [item])


if __name__ == '__main__':
    unittest.main()
