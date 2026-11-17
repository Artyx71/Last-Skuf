"""Adopter adversarial tests. ALL fake review documents/targets live in TempDir.

These tests do not constitute ART review or approval of the actual FIN candidate.
Run with the project art venv (Pillow), not the dependency-free game test runner.
"""
import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import adopt_timka_supported as adopter
import compact_timka as compact

PROJECT = compact.ROOT


class AdopterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ayay-timka-adopter-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'isolated-test-project'
        self.root.mkdir()
        self.patcher = patch.object(adopter, 'ROOT', self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def fixture(self, kind='action'):
        self.kind = kind
        self.source = self.root / 'assets/source_art/characters/timka'
        self.source.mkdir(parents=True)
        self.native = self.source / f'{kind}_native_supported_v1.png'
        self.metadata = self.source / f'{kind}_manifest_supported_v1.json'
        actual = PROJECT / self.metadata.relative_to(self.root)
        self.manifest = json.loads(actual.read_text())
        provenance = self.manifest['source_compaction']
        files = [self.native.relative_to(self.root), self.metadata.relative_to(self.root),
                 Path(self.manifest['master'])] + [Path(provenance[k]) for k in ['input_native', 'input_manifest', 'script', 'owner_decision']]
        for relative in set(files):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PROJECT / relative, target)
        destination = self.root / 'game/assets/art/characters/timka'
        destination.mkdir(parents=True)
        self.target = destination / (kind + '_sheet.png')
        self.target_meta = destination / (kind + '.json')
        if kind != 'finisher':
            old = json.loads((self.root / provenance['input_manifest']).read_text())
            shutil.copyfile(self.root / provenance['input_native'], self.target)
            self.target_meta.write_text(json.dumps(old))
        self.review_path = self.root / 'reports/phases/P06/art-preflight/TEST_ONLY_FAKE_REVIEW.json'
        self.review_path.parent.mkdir(parents=True)
        report = self.review_path.with_suffix('.md')
        report.write_text('TEST DOUBLE ONLY. No visual inspection/ART approval has occurred here.\n')
        metrics = self.review_path.with_name(self.review_path.stem + '_metrics.json')
        metrics.write_text('{"TEST_ONLY":true}\n')
        count = self.manifest['source_cells']
        self.review = {'schema': 2, 'layout_profile': compact.PROFILE, 'actor_id': 'timka', 'kind': kind,
            'status': 'ACCEPTABLE_SUPPORTED_LAYOUT_SOURCE_CANDIDATE',
            'reviewer': 'TEST_DOUBLE_IN_TEMP_NOT_REAL_ART_REVIEW', 'independent_of_author': True,
            'source_only_acceptance': True, 'all_required_cells_freshly_reviewed': True,
            'reviewed_cell_indices': list(range(count)), 'source_cells': count, 'must_fix': [],
            'runtime_approval': False, 'phase_approval': False, 'full_phase_approval': False,
            'native_sha256': compact.sha(self.native), 'manifest_sha256': compact.sha(self.metadata),
            'master_sha256': self.manifest['master_sha256'],
            'report_sha256': compact.sha(report), 'metrics_sha256': compact.sha(metrics),
            'source_inventory_sha256': {str(p): compact.sha(self.root / p) for p in set(files)},
            'review_artifacts_sha256': {report.name: compact.sha(report), metrics.name: compact.sha(metrics)}}
        self.write_review()

    def write_review(self):
        self.review_path.write_text(json.dumps(self.review))

    def runtime_snapshot(self):
        folder = self.root / 'game'
        return {str(p.relative_to(folder)): p.read_bytes() for p in folder.rglob('*') if p.is_file()}

    def reject(self):
        before = self.runtime_snapshot()
        with self.assertRaises((ValueError, KeyError, TypeError, FileNotFoundError)):
            adopter.adopt(self.kind, 'supported_v1', str(self.review_path.relative_to(self.root)))
        self.assertEqual(before, self.runtime_snapshot(), 'Failed adoption mutated runtime')

    def rebind_modified_candidate_for_test(self):
        # An adversary also changes claimed review hashes. Whole-cell provenance
        # must still reject edited art, even with these consistent fake claims.
        self.manifest['sha256'] = compact.sha(self.native)
        self.metadata.write_text(json.dumps(self.manifest))
        self.review['native_sha256'] = compact.sha(self.native)
        self.review['manifest_sha256'] = compact.sha(self.metadata)
        for relative in self.review['source_inventory_sha256']:
            self.review['source_inventory_sha256'][relative] = compact.sha(self.root / relative)
        self.write_review()

    def test_supported_action_positive_and_legacy_snapshot(self):
        self.fixture()
        before = self.runtime_snapshot()
        adopter.adopt('action', 'supported_v1', str(self.review_path.relative_to(self.root)))
        metadata = json.loads(self.target_meta.read_text())
        self.assertEqual(metadata['source_cells'], 28)
        self.assertNotIn('fire', metadata['animations_source_columns'])
        self.assertEqual(self.target.read_bytes(), self.native.read_bytes())
        self.assertEqual((self.source / 'runtime_before_supported_v1/action_sheet.png').read_bytes(), before['assets/art/characters/timka/action_sheet.png'])

    def test_world_preserves_exact_png_bytes(self):
        self.fixture('world')
        original = self.target.read_bytes()
        adopter.adopt('world', 'supported_v1', str(self.review_path.relative_to(self.root)))
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual(json.loads(self.target_meta.read_text())['schema'], 2)

    def test_finisher_24_technical_path_only_in_temp(self):
        self.fixture('finisher')
        adopter.adopt('finisher', 'supported_v1', str(self.review_path.relative_to(self.root)))
        metadata = json.loads(self.target_meta.read_text())
        self.assertEqual(metadata['source_cells'], 24)
        self.assertEqual(metadata['source_column_mapping'], [0, 1, 2, 5, 6, 7])
        self.assertNotIn('finish_firearm', metadata['animations_source_columns'])
        self.assertNotIn('finish_sharp', metadata['animations_source_columns'])

    def test_partial_cell_review_rejected(self):
        self.fixture(); self.review['reviewed_cell_indices'].pop(); self.write_review(); self.reject()

    def test_legacy_all32_review_rejected(self):
        self.fixture(); self.review['all32_freshly_reviewed'] = True; self.write_review(); self.reject()

    def test_wrong_count_rejected(self):
        self.fixture(); self.review['source_cells'] = 32; self.write_review(); self.reject()

    def test_boolean_index_rejected(self):
        self.fixture(); self.review['reviewed_cell_indices'][0] = False; self.write_review(); self.reject()

    def test_critical_art_finding_rejected(self):
        self.fixture(); self.review['must_fix'] = ['environment remains unreadable']; self.write_review(); self.reject()

    def test_runtime_approval_cannot_replace_source_review(self):
        self.fixture(); self.review['runtime_approval'] = True; self.write_review(); self.reject()

    def test_explicit_independence_required(self):
        self.fixture(); self.review['independent_of_author'] = False; self.write_review(); self.reject()

    def test_changed_inventory_input_rejected(self):
        self.fixture(); self.native.write_bytes(self.native.read_bytes() + b'tamper'); self.reject()

    def test_changed_report_rejected(self):
        self.fixture(); self.review_path.with_suffix('.md').write_text('changed'); self.reject()

    def test_absolute_inventory_path_rejected(self):
        self.fixture(); self.review['source_inventory_sha256'][str(self.native)] = compact.sha(self.native); self.write_review(); self.reject()

    def test_required_master_binding_cannot_be_omitted(self):
        self.fixture(); del self.review['source_inventory_sha256'][self.manifest['master']]; self.write_review(); self.reject()

    def test_changed_cell_rejected_even_if_fake_review_hashes_updated(self):
        self.fixture()
        image = Image.open(self.native).convert('RGBA')
        image.putpixel((0, 0), (255, 0, 255, 255)); image.save(self.native)
        self.manifest['frames'][0]['rgba_sha256'] = hashlib.sha256(image.crop((0, 0, 48, 64)).tobytes()).hexdigest()
        self.rebind_modified_candidate_for_test(); self.reject()

    def test_world_reencoding_rejected_even_if_same_RGBA(self):
        self.fixture('world')
        before = self.native.read_bytes()
        image = Image.open(self.native).convert('RGBA'); image.save(self.native, compress_level=0)
        self.assertNotEqual(before, self.native.read_bytes())
        self.rebind_modified_candidate_for_test(); self.reject()

    def test_migration_cannot_be_replayed_over_schema2(self):
        self.fixture(); adopter.adopt(self.kind, 'supported_v1', str(self.review_path.relative_to(self.root))); self.reject()

    def test_stale_sockets_prevent_migration(self):
        self.fixture(); (self.target.parent / 'action.sockets.json').write_text('{"schema":1,"frames":[]}'); self.reject()

    def test_invalid_profile_rejected_by_validator(self):
        self.fixture(); bad = copy.deepcopy(self.manifest); bad['layout_profile'] = 'untrusted'
        with self.assertRaises(ValueError): compact.validate(bad, Image.open(self.native).convert('RGBA'))


if __name__ == '__main__':
    unittest.main()
