#!/usr/bin/env python3
"""Bind actual C01 source bytes to independent signal review. No listening verdict."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SIGNAL_SHA = 'c69fe500f8374fa25430e743fb39f6f8a9c251a9a8ee5d0ac7a5cde6c572c84c'
FREEZE_SHA = '5fe77b841e8d661b86e4c468e9d5c598a83b71e758712587caa0df1635414ba9'
EXPECTED = {
    'gabar': ['unarmed', 'blunt', 'firearm'], 'olezhka': ['unarmed', 'blunt', 'sharp'],
    'timka': ['unarmed', 'blunt', 'environmental'], 'ryzhik': ['unarmed', 'blunt', 'environmental'],
    'tega': ['unarmed', 'blunt', 'environmental'],
    'pasha': ['unarmed', 'blunt', 'sharp', 'firearm', 'environmental']}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root=ROOT):
    checks = []
    def check(ok, name):
        checks.append({'name': name, 'passed': bool(ok)})
    try:
        review = root / 'reports/phases/P06/audio-c01-signal-review-01'
        decision, freeze = review / 'decision.json', review / 'input-freeze.json'
        check(sha(decision) == SIGNAL_SHA, 'immutable independent signal decision')
        check(sha(freeze) == FREEZE_SHA, 'immutable source freeze')
        if not all(c['passed'] for c in checks): return checks
        records = json.loads(freeze.read_text())['records']
        hashes = {Path(r['path']).name: r['sha256'] for r in records if r['path'].endswith('.wav')}
        snapshots = {r['snapshot']: r['sha256'] for r in records if r.get('snapshot')}
        source = root / 'assets/source_audio/character_finishers'
        runtime = root / 'game/assets/audio/character_finishers'
        manifest_path = root / 'game/assets/audio/character_finishers.json'
        manifest = json.loads(manifest_path.read_text())
        check(type(manifest.get('schema')) is int and manifest['schema'] == 1, 'manifest schema')
        check(manifest.get('source_signal_decision_sha256') == SIGNAL_SHA, 'manifest decision binding')
        check(manifest.get('source_recipe_sha256') == snapshots['inputs/render.py'], 'manifest recipe binding')
        for name, key in [('render.py', 'inputs/render.py'), ('candidate_manifest.json', 'inputs/candidate_manifest.json'), ('provenance.json', 'inputs/candidate-provenance.json')]:
            check(sha(source / name) == snapshots[key], 'reviewed source ' + name)
        check(sha(root / 'game/resources/characters/catalog.json') == snapshots['inputs/catalog.json'], 'reviewed allowed equipment catalog')
        expected = set()
        for actor, categories in EXPECTED.items():
            for category in categories:
                cue = 'finish_' + actor + ('_prime' if actor == 'timka' else '') + '_' + category
                expected.add(cue)
                entry = manifest['sfx'].get(cue, {})
                name = cue + '.wav'
                check(entry.get('path') == 'res://assets/audio/character_finishers/' + name and entry.get('actor_id') == actor and entry.get('context') == ('athletic_prime' if actor == 'timka' else 'training') and entry.get('category') == category, cue + ' route')
                check(entry.get('bus') == 'SFX' and type(entry.get('gain_db')) in (int, float) and -24 <= entry['gain_db'] <= 0, cue + ' bus/gain')
                check(entry.get('source_sha256') == hashes[name] and sha(source / name) == hashes[name] and sha(runtime / name) == hashes[name], cue + ' source/runtime/independent SHA')
        check(set(manifest['sfx']) == expected, 'exact twenty routes; no present/excluded grants')
        check({p.stem for p in runtime.glob('*.wav')} == expected and {p.stem for p in source.glob('*.wav')} == expected, 'exact production source/runtime WAV inventories')
        legacy = root / 'game/assets/audio/combat_polish.json'
        check(sha(legacy) == snapshots['inputs/legacy-combat-polish.json'], 'legacy routing unchanged')
        for name in ['unarmed', 'blunt', 'sharp', 'firearm', 'environmental']:
            filename = 'finish_' + name + '.wav'
            check(sha(root / 'game/assets/audio/combat_polish' / filename) == hashes[filename], 'legacy bytes ' + name)
        for path in [root / 'game/assets/audio/manifest.json', legacy]:
            check(not set(json.loads(path.read_text())['sfx']).intersection(expected), 'no duplicate cue registry ' + path.name)
        adoption = json.loads((source / 'adoption.json').read_text())
        check(adoption.get('source_signal_decision_sha256') == SIGNAL_SHA and adoption.get('runtime_manifest_sha256') == sha(manifest_path), 'adoption binds actual manifest and signal decision')
    except (OSError, ValueError, TypeError, KeyError) as error:
        check(False, type(error).__name__ + ': ' + str(error))
    return checks


if __name__ == '__main__':
    result = verify()
    print(json.dumps({'scope': 'C01_SOURCE_BINDING_ONLY', 'phase_approval': False,
                      'listening_performed': False, 'checks': result}, indent=2))
    sys.exit(0 if result and all(c['passed'] for c in result) else 1)
