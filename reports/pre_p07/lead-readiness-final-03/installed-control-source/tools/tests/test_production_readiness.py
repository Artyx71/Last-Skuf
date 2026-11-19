"""Temporary Git fixtures only. These approvals never touch production state."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'autopilot'))
from readiness import (ReadinessBlocked, require_p07_production, require_p07_review_acceptance,
                       CAPABILITIES, OBLIGATIONS, ACCEPTANCE_STAGE)
from github import validate_review, guarded_merge
from runner import Blocked, Controller, DEFAULT_PHASES, load


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


class ProductionReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.registry = self.root / 'game/resources/story/registry.json'
        write(self.registry, {'chapters': [{'id': f'CH{i:02}'} for i in range(1, 22)]})
        self.source = self.root / 'game/combat.gd'
        self.source.write_text('# isolated TEST fixture, no production approval\n')
        for argv in [['git', 'init', '-q'], ['git', 'add', 'game'],
                     ['git', '-c', 'user.name=Test Fixture', '-c', 'user.email=fixture@invalid', 'commit', '-qm', 'test-only source']]:
            subprocess.run(argv, cwd=self.root, check=True, capture_output=True)
        self.head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.root, text=True).strip()
        inventory = {str(p.relative_to(self.root)): sha(p) for p in (self.root / 'game').rglob('*') if p.is_file()}
        self.ready = self.decision('PRE_P07_PRODUCTION_READINESS', inventory)
        self.ready['ready_for_p07'] = True
        capabilities = {}
        for capability in sorted(CAPABILITIES):
            p = self.root / f'reports/pre_p07/TEST_ONLY/{capability}.txt'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('TEST ONLY capability evidence: ' + capability)
            relative = str(p.relative_to(self.root))
            inventory[relative] = sha(p)
            capabilities[capability] = {'status': 'PASS', 'evidence': [{'path': relative, 'sha256': sha(p)}]}
        self.ready['preproduction_capabilities'] = capabilities
        self.ready['future_acceptance_obligations'] = {k: {'severity': 'HIGH', 'status': 'OPEN',
            'enforce_at': ACCEPTANCE_STAGE, 'requirement': 'TEST ONLY future ' + k,
            'source_findings': ['TEST_ONLY_REQUIREMENT_' + k]} for k in OBLIGATIONS}
        specs = {}
        for i in range(1, 22):
            p = self.root / f'planning/CH{i:02}.md'
            p.parent.mkdir(exist_ok=True)
            p.write_text(f'TEST ONLY distinct fixture chapter {i}; not a real MDS.')
            specs[f'CH{i:02}'] = {'path': str(p.relative_to(self.root)), 'sha256': sha(p)}
        self.designs = self.decision('P07_MISSION_DESIGN_APPROVAL', {e['path']: e['sha256'] for e in specs.values()})
        self.designs.update(approved_for_mass_production=True, mission_specs=specs)
        self.state = {'autopilot': {'phases': {p: {'status': 'PASS', 'merge': {
            'status': 'MERGED', 'reviewed_head': self.head, 'merge_sha': self.head}}
            for p in DEFAULT_PHASES}, 'production_gates': {}}}
        self.publish()

    def tearDown(self):
        self.temp.cleanup()

    def decision(self, scope, inventory):
        return {'schema': 1, 'status': 'PASS', 'scope': scope, 'acceptance_level': 'FULL', 'role': 'LEAD_REVIEWER',
                'reviewer': 'independent-test-fixture-only', 'independent_of_author': True,
                'p06_base_head': self.head, 'must_fix': [], 'findings': [],
                'source_inventory_sha256': inventory}

    def publish(self):
        for name, data in [('readiness', self.ready), ('mission_designs', self.designs)]:
            relative = f'reports/pre_p07/TEST_ONLY/{name}.json'
            p = self.root / relative
            write(p, data)
            self.state['autopilot']['production_gates'][name] = {'decision': relative, 'sha256': sha(p)}

    def blocked(self):
        with self.assertRaises(ReadinessBlocked):
            require_p07_production(self.root, self.state)

    def test_full_frozen_fixture_passes_without_mutation(self):
        before = copy.deepcopy(self.state)
        self.assertEqual(require_p07_production(self.root, self.state)['mission_specs'], 21)
        self.assertEqual(self.state, before)

    def test_missing_records_block(self):
        for name in ['readiness', 'mission_designs']:
            with self.subTest(name=name):
                self.publish()
                del self.state['autopilot']['production_gates'][name]
                self.blocked()

    def test_fail_blocked_component_and_concept_are_not_production_pass(self):
        for data in [self.ready, self.designs]:
            for status in ['FAIL', 'BLOCKED', 'PASS_COMPONENT', 'CONCEPT_ONLY']:
                with self.subTest(scope=data['scope'], status=status):
                    data['status'] = status; self.publish(); self.blocked()
            data['status'] = 'PASS'

    def test_concept_only_pass_cannot_use_full_scope(self):
        self.designs['acceptance_level'] = 'CONCEPT_ONLY'
        self.publish(); self.blocked()

    def test_component_level_pass_with_full_scope_still_blocks(self):
        self.ready['acceptance_level'] = 'COMPONENT_ONLY'
        self.publish(); self.blocked()

    def test_independence_and_explicit_permissions_required(self):
        for data, key, bad in [(self.ready, 'independent_of_author', False),
                               (self.ready, 'role', 'AUTHOR'), (self.ready, 'reviewer', ''),
                               (self.ready, 'ready_for_p07', False),
                               (self.designs, 'approved_for_mass_production', False)]:
            old = data[key]; data[key] = bad
            self.publish(); self.blocked()
            data[key] = old

    def test_open_critical_high_and_mandatory_findings_block(self):
        for data in [self.ready, self.designs]:
            data['must_fix'] = ['fixture issue']; self.publish(); self.blocked(); data['must_fix'] = []
            for severity in ['CRITICAL', 'HIGH']:
                data['findings'] = [{'severity': severity, 'status': 'OPEN'}]
                self.publish(); self.blocked()
            data['findings'] = []

    def test_resolved_findings_and_nonblocking_medium_allowed(self):
        self.ready['findings'] = [{'severity': 'HIGH', 'status': 'VERIFIED'}, {'severity': 'MEDIUM', 'status': 'OPEN'}]
        self.publish()
        require_p07_production(self.root, self.state)

    def test_exact_decision_digest_required(self):
        p = self.root / self.state['autopilot']['production_gates']['readiness']['decision']
        p.write_text(p.read_text() + '\n'); self.blocked()

    def test_changed_game_and_rehashed_claim_still_rejected_by_git(self):
        self.source.write_text('unreviewed replacement\n')
        self.blocked()
        self.ready['source_inventory_sha256']['game/combat.gd'] = sha(self.source)
        self.publish(); self.blocked()

    def test_whole_game_inventory_required(self):
        del self.ready['source_inventory_sha256']['game/combat.gd']
        self.publish(); self.blocked()

    def test_untracked_game_file_blocks(self):
        (self.root / 'game/new.gd').write_text('unreviewed\n'); self.blocked()

    def test_generated_import_cache_excluded(self):
        p = self.root / 'game/.godot/imported/cache'; p.parent.mkdir(parents=True); p.write_text('cache')
        require_p07_production(self.root, self.state)

    def test_untracked_directory_symlink_cannot_hide_unreviewed_source(self):
        with tempfile.TemporaryDirectory() as external:
            p = Path(external); (p / 'unreviewed.gd').write_text('outside production commit')
            (self.root / 'game/hidden').symlink_to(p, target_is_directory=True)
            self.blocked()

    def test_internal_directory_symlink_also_requires_reconciliation(self):
        p = self.root / 'elsewhere'; p.mkdir(); (p / 'unreviewed.gd').write_text('unreviewed')
        (self.root / 'game/hidden').symlink_to(p, target_is_directory=True)
        self.blocked()

    def test_game_file_symlink_rejected_even_if_bytes_match(self):
        p = self.root / 'copy.gd'; p.write_bytes(self.source.read_bytes())
        self.source.unlink(); self.source.symlink_to(p)
        self.blocked()

    def test_dangling_production_symlink_rejected(self):
        (self.root / 'game/dangling').symlink_to(self.root / 'missing')
        self.blocked()

    def test_report_prefix_symlink_cannot_move_approvals_outside_repository(self):
        import shutil
        with tempfile.TemporaryDirectory() as external:
            p = Path(external) / 'approvals'
            original = self.root / 'reports/pre_p07'
            shutil.move(str(original), str(p)); original.symlink_to(p, target_is_directory=True)
            self.blocked()

    def test_mds_parent_symlink_cannot_move_files_outside_repository(self):
        import shutil
        with tempfile.TemporaryDirectory() as external:
            p = Path(external) / 'specs'; original = self.root / 'planning'
            shutil.move(str(original), str(p)); original.symlink_to(p, target_is_directory=True)
            self.blocked()

    def test_boolean_schema_is_not_schema_one(self):
        self.ready['schema'] = True
        self.publish(); self.blocked()

    def test_unknown_or_malformed_severities_never_silently_skip_gate(self):
        for severity in [None, {'priority': 'HIGH'}, '', 'HIG H', 1]:
            with self.subTest(severity=severity):
                self.ready['findings'] = [{'severity': severity, 'status': 'OPEN'}]
                self.publish(); self.blocked()

    def test_whitespace_high_still_blocks(self):
        self.ready['findings'] = [{'severity': 'HIGH ', 'status': 'OPEN'}]
        self.publish(); self.blocked()

    def test_unknown_resolution_status_rejected(self):
        self.ready['findings'] = [{'severity': 'LOW', 'status': None}]
        self.publish(); self.blocked()

    def test_wrong_frozen_head_blocks(self):
        self.ready['p06_base_head'] = 'f' * 40
        self.publish(); self.blocked()

    def test_p06_merge_and_phase_status_required(self):
        phase = self.state['autopilot']['phases']['P06']
        for key, value in [('status', 'BLOCKED'), ('status', 'PASS_COMPONENT')]:
            old = phase[key]; phase[key] = value; self.blocked(); phase[key] = old
        phase['merge']['status'] = 'PENDING'; self.blocked()

    def test_all_21_individual_specifications_required(self):
        del self.designs['mission_specs']['CH21']
        self.publish(); self.blocked()

    def test_duplicate_specification_rejected(self):
        self.designs['mission_specs']['CH21'] = self.designs['mission_specs']['CH20']
        self.publish(); self.blocked()

    def test_duplicate_contents_rejected(self):
        source = self.root / 'planning/CH20.md'; target = self.root / 'planning/CH21.md'
        target.write_bytes(source.read_bytes())
        self.designs['mission_specs']['CH21']['sha256'] = sha(target)
        self.designs['source_inventory_sha256']['planning/CH21.md'] = sha(target)
        self.publish(); self.blocked()

    def test_changed_mds_rejected(self):
        (self.root / 'planning/CH21.md').write_text('unreviewed replacement'); self.blocked()

    def test_mds_without_review_inventory_rejected(self):
        del self.designs['source_inventory_sha256']['planning/CH21.md']
        self.publish(); self.blocked()

    def test_empty_mds_rejected_even_with_updated_hashes(self):
        p = self.root / 'planning/CH21.md'; p.write_text(' \n')
        self.designs['mission_specs']['CH21']['sha256'] = sha(p)
        self.designs['source_inventory_sha256']['planning/CH21.md'] = sha(p)
        self.publish(); self.blocked()

    def test_decision_cannot_escape_report_directory(self):
        self.state['autopilot']['production_gates']['readiness']['decision'] = 'game/combat.gd'
        self.blocked()

    def test_malformed_state_blocks(self):
        for value in [None, {}, {'autopilot': []}, {'autopilot': {'phases': []}}]:
            with self.assertRaises(ReadinessBlocked): require_p07_production(self.root, value)
        self.state['autopilot']['production_gates'] = []
        self.blocked()

    def test_controller_calls_production_gate(self):
        controller = object.__new__(Controller)
        controller.root = self.root; controller.phases = DEFAULT_PHASES
        controller.state = lambda: self.state
        controller.prerequisite('P07')
        del self.state['autopilot']['production_gates']['readiness']
        with self.assertRaises(Blocked): controller.prerequisite('P07')

    def test_missing_actual_capability_blocks_production(self):
        del self.ready['preproduction_capabilities']['navigation_pilot']
        self.publish(); self.blocked()

    def test_capability_needs_accepted_actual_hash_bound_evidence(self):
        entry = self.ready['preproduction_capabilities']['audio_playback_pipeline']
        entry['status'] = 'PLANNED'; self.publish(); self.blocked()
        entry['status'] = 'PASS'; entry['evidence'] = []; self.publish(); self.blocked()

    def test_missing_future_contract_blocks_production(self):
        del self.ready['future_acceptance_obligations']
        self.publish(); self.blocked()

    def test_future_requirements_cannot_be_downgraded_closed_or_unknown_stage(self):
        entry = self.ready['future_acceptance_obligations']['campaign_pacing_actual']
        for key, value in [('severity', 'MEDIUM'), ('status', 'CLOSED'), ('enforce_at', 'AFTER_MERGE'),
                           ('requirement', ''), ('source_findings', [])]:
            old = entry[key]; entry[key] = value
            self.publish(); self.blocked(); entry[key] = old

    def acceptance_review(self):
        write(self.root / 'automation/phase_state.json', self.state)
        proof = self.root / 'reports/P07/TEST_ONLY_CONTENT_EVIDENCE.txt'
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_text('TEST ONLY evidence, not actual game content acceptance')
        item = {'path': str(proof.relative_to(self.root)), 'sha256': sha(proof)}
        return {'phase': 'P07', 'status': 'PASS', 'reviewed_commit': self.head,
                'independent_review': True, 'reviewer': 'independent-test-fixture-only',
                'evidence': [item], 'findings': [], 'production_acceptance': {
                    'schema': 1, 'scope': 'P07_CONTENT_ACCEPTANCE', 'reviewed_commit': self.head,
                    'readiness_sha256': self.state['autopilot']['production_gates']['readiness']['sha256'],
                    'closed_obligations': {k: {'status': 'PASS', 'evidence': [item]} for k in OBLIGATIONS}}}

    def test_future_open_obligations_allow_mass_entry_but_not_automatic_phase_pass(self):
        require_p07_production(self.root, self.state)
        review = self.acceptance_review(); del review['production_acceptance']
        self.assertTrue(validate_review(self.root, review, self.head, 'P07'))

    def test_independent_actual_content_closure_allows_p07_pass(self):
        review = self.acceptance_review()
        self.assertEqual(validate_review(self.root, review, self.head, 'P07'), [])

    def test_missing_obligation_closure_blocks_phase_pass(self):
        review = self.acceptance_review()
        del review['production_acceptance']['closed_obligations']['new_audio_acceptance']
        self.assertTrue(validate_review(self.root, review, self.head, 'P07'))

    def test_stale_readiness_or_p07_sha_blocks_closure(self):
        for key in ['readiness_sha256', 'reviewed_commit']:
            review = self.acceptance_review()
            review['production_acceptance'][key] = 'f' * 64
            self.assertTrue(validate_review(self.root, review, self.head, 'P07'))

    def test_future_evidence_must_be_in_actual_review_inventory(self):
        review = self.acceptance_review()
        review['production_acceptance']['closed_obligations']['new_audio_acceptance']['evidence'] = [
            {'path': 'reports/MISSING.txt', 'sha256': 'f' * 64}]
        self.assertTrue(validate_review(self.root, review, self.head, 'P07'))

    def test_future_evidence_tamper_blocks_closure(self):
        review = self.acceptance_review()
        (self.root / review['evidence'][0]['path']).write_text('unreviewed replacement')
        self.assertTrue(validate_review(self.root, review, self.head, 'P07'))

    def test_canonical_state_is_used_in_linked_worktree_not_historical_copy(self):
        review = self.acceptance_review()
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / 'P07'
            subprocess.run(['git', 'worktree', 'add', '--detach', str(work), self.head],
                           cwd=self.root, check=True, capture_output=True)
            try:
                import shutil
                shutil.copytree(self.root / 'reports', work / 'reports')
                write(work / 'automation/phase_state.json', {'STALE_WORKTREE_COPY': True})
                self.assertTrue(require_p07_review_acceptance(work, review, self.head))
                self.state['autopilot']['production_gates'].pop('readiness')
                write(self.root / 'automation/phase_state.json', self.state)
                self.assertTrue(validate_review(work, review, self.head, 'P07'))
            finally:
                subprocess.run(['git', 'worktree', 'remove', '--force', str(work)],
                               cwd=self.root, check=True, capture_output=True)

    def merge_view(self):
        return {'number': 4, 'repository': 'Artyx71/Last-Skuf', 'head_repo': 'Artyx71/Last-Skuf',
                'head_sha': self.head, 'base': 'main', 'base_sha': 'b' * 40, 'state': 'open',
                'draft': False, 'squash_allowed': True, 'permissions': {'push': True},
                'protection_inspected': True, 'mergeable': True, 'merge_state': 'CLEAN',
                'threads_complete': True, 'unresolved_threads': 0, 'review_decision': 'APPROVED',
                'approvals_required': 1, 'queue_required': False, 'required_checks': ['bootstrap'],
                'integration_ids': {}, 'checks': {'bootstrap': {'status': 'completed',
                    'conclusion': 'success', 'head_sha': self.head, 'app_id': 1, 'app_slug': 'github-actions'}}}

    def test_merge_rechecks_canonical_contract_before_network_write(self):
        review = self.acceptance_review(); review.update(base_branch='main', base_sha='b' * 40)
        calls = []; sent = []
        def snapshot(*_):
            calls.append(1)
            if len(calls) == 2:
                del self.state['autopilot']['production_gates']['readiness']
                write(self.root / 'automation/phase_state.json', self.state)
            return self.merge_view()
        result = guarded_merge(self.root, 4, {}, review, 'P07', snapshot, lambda *a: sent.append(a))
        self.assertEqual(result['status'], 'BLOCKED'); self.assertEqual(len(calls), 2); self.assertFalse(sent)

    def test_merge_without_closure_never_sends_request(self):
        review = self.acceptance_review(); review.update(base_branch='main', base_sha='b' * 40)
        del review['production_acceptance']; sent = []
        result = guarded_merge(self.root, 4, {}, review, 'P07', lambda *_: self.merge_view(), lambda *a: sent.append(a))
        self.assertEqual(result['status'], 'BLOCKED'); self.assertFalse(sent)

    def test_fail_and_blocked_review_need_not_fabricate_content_closure(self):
        review = self.acceptance_review(); del review['production_acceptance']
        for status in ['FAIL', 'BLOCKED']:
            review['status'] = status
            self.assertEqual(validate_review(self.root, review, self.head, 'P07'), [])

    def test_malformed_or_open_high_phase_finding_blocks_even_with_content_closure(self):
        for severity in ['HIGH ', 'critical', None, {'priority': 'HIGH'}, 'UNKNOWN']:
            review = self.acceptance_review()
            review['findings'] = [{'severity': severity, 'status': 'OPEN'}]
            self.assertTrue(validate_review(self.root, review, self.head, 'P07'))

    def test_cli_strict_schema_requires_all_object_fields_and_nullable_other_phases(self):
        schema = json.loads((ROOT / 'autopilot/review_schema.json').read_text())
        def check(node):
            if isinstance(node, dict):
                if node.get('type') == 'object':
                    self.assertEqual(set(node.get('required', [])), set(node.get('properties', {})))
                    self.assertIs(node.get('additionalProperties'), False)
                for value in node.values(): check(value)
            elif isinstance(node, list):
                for value in node: check(value)
        check(schema)
        self.assertIn({'type': 'null'}, schema['properties']['production_acceptance']['anyOf'])

    def test_duplicate_raw_closure_id_is_rejected_by_actual_runner_loader(self):
        review = self.acceptance_review()
        raw = json.dumps(review)
        needle = '"new_audio_acceptance":'
        self.assertEqual(raw.count(needle), 1)
        raw = raw.replace(needle, '"new_audio_acceptance":{"status":"FAIL","evidence":[]},' + needle)
        p = self.root / 'ambiguous-verdict.json'; p.write_text(raw)
        with self.assertRaises(Blocked): load(p)

    def test_duplicate_top_level_verdict_status_is_rejected_before_merge(self):
        review = self.acceptance_review()
        raw = json.dumps(review)
        raw = raw.replace('"status": "PASS"', '"status":"FAIL","status":"PASS"', 1)
        p = self.root / 'ambiguous-verdict.json'; p.write_text(raw)
        sent = []
        with self.assertRaises(Blocked):
            verdict = load(p)
            guarded_merge(self.root, 4, {}, verdict, 'P07', lambda *_: self.merge_view(), lambda *a: sent.append(a))
        self.assertFalse(sent)

    def test_duplicate_capability_keys_in_hash_bound_readiness_are_rejected(self):
        record = self.state['autopilot']['production_gates']['readiness']
        p = self.root / record['decision']; raw = p.read_text()
        needle = '"navigation_pilot":'
        raw = raw.replace(needle, '"navigation_pilot":{"status":"FAIL"},' + needle)
        p.write_text(raw); record['sha256'] = sha(p)
        self.blocked()

    def test_nonfinite_json_is_not_accepted_as_a_controller_record(self):
        p = self.root / 'nonfinite.json'; p.write_text('{"value":NaN}')
        with self.assertRaises(Blocked): load(p)

    def test_malformed_phase_findings_container_never_passes(self):
        for value in [{}, {'severity': 'HIGH', 'status': 'OPEN'}, None, '']:
            review = self.acceptance_review(); review['findings'] = value
            self.assertTrue(validate_review(self.root, review, self.head, 'P07'))


if __name__ == '__main__':
    unittest.main()
