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
from readiness import ReadinessBlocked, require_p07_production
from runner import Blocked, Controller, DEFAULT_PHASES


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


if __name__ == '__main__':
    unittest.main()
