#!/usr/bin/env python3
"""Native pacing calibration/acceptance, using the existing second-pilot setup."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

from p07_second_pilot import prepare_project
from p07_room_pilot import ROOT, digest, inventory, write
sys.path.insert(0, str(ROOT / 'autopilot'))
from readiness import strict_json

CONTEXTS = ['yakuza', 'gabar_training', 'olezhka_training', 'timka_present', 'timka_prime',
            'ryzhik_training', 'tega_training', 'pasha_training']


def percentile(values, q):
    if not values or not all(math.isfinite(x) and x >= 0 for x in values):
        raise ValueError('Finite nonnegative samples required')
    return sorted(values)[max(0, math.ceil(q * len(values)) - 1)]


def load_contract(path, review_path, current):
    if review_path is None:
        raise ValueError('Independent calibration review required before acceptance')
    contract_blob, review_blob = path.read_bytes(), review_path.read_bytes()
    contract = strict_json(contract_blob.decode())
    review = strict_json(review_blob.decode())
    pins = {str(path.resolve()): hashlib.sha256(contract_blob).hexdigest(),
            str(review_path.resolve()): hashlib.sha256(review_blob).hexdigest()}
    if (type(review.get('schema')) is not int or review['schema'] != 1
            or review.get('status') != 'PASS_COMPONENT' or review.get('scope') != 'H04_CALIBRATION_CONTRACT'
            or review.get('role') != 'LEAD_REVIEWER' or review.get('independent_of_author') is not True
            or not isinstance(review.get('reviewer'), str) or review['reviewer'].strip() in ['', '/root']
            or review.get('must_fix') != [] or review.get('contract_sha256') != hashlib.sha256(contract_blob).hexdigest()):
        raise ValueError('Missing, unreviewed or changed calibration contract')
    if (type(contract.get('schema')) is not int or contract['schema'] != 1
            or contract.get('scope') != 'H04_PILOT_ACCEPTANCE' or contract.get('source_inventory_sha256') != current):
        raise ValueError('Stale calibrated source inventory')
    if set(contract.get('limits', {})) != {'accept_p95_ms', 'render_p95_ms', 'frame_p95_ms', 'frame_p99_ms', 'restart_max_ms'}:
        raise ValueError('All five calibrated limits required')
    limits = contract['limits']
    if (not all(type(x) in [int, float] and math.isfinite(x) and x > 0 for x in limits.values())
            or limits['restart_max_ms'] > 1000 or limits['accept_p95_ms'] > 50
            or limits['render_p95_ms'] > 83.334 or limits['frame_p95_ms'] > 25 or limits['frame_p99_ms'] > 33.334):
        raise ValueError('Calibration cannot weaken absolute safety ceilings')
    return contract, pins


def validate_pins(pins):
    for path, expected in pins.items():
        if digest(Path(path)) != expected:
            raise ValueError('Pinned calibration contract/review changed: ' + path)


def visual_key(state):
    for key in ['position', 'draw_position']:
        if (not isinstance(state.get(key), list) or len(state[key]) != 2
                or not all(type(x) in [int, float] and math.isfinite(x) for x in state[key])):
            raise ValueError('Finite actual actor coordinates required')
    if (not isinstance(state.get('animation'), str) or type(state.get('frame')) is not int
            or type(state.get('action_frame')) is not int
            or type(state.get('health')) is not int or not isinstance(state.get('context'), str)):
        raise ValueError('Actual rendered actor pose required')
    return tuple(state['draw_position']), state['animation'], state['frame']


def integer_fields(row, keys):
    if any(type(row.get(key)) is not int or row[key] < 0 for key in keys):
        raise ValueError('Integer, not boolean, observation IDs/timestamps required')


def analyze(raw):
    if type(raw.get('schema')) is not int or raw['schema'] != 1 or type(raw.get('failed')) is not int or raw['failed'] != 0:
        raise ValueError('Complete functional native run required')
    checks = raw.get('checks', [])
    if (not checks or type(raw.get('passed')) is not int or any(type(c.get('passed')) is not bool for c in checks)
            or len({c.get('check') for c in checks}) != len(checks)
            or raw['passed'] != sum(c['passed'] for c in checks)
            or raw['failed'] != sum(not c['passed'] for c in checks)):
        raise ValueError('Functional summary must match actual typed unique checks')
    draws = raw['draws']
    for row in draws:
        integer_fields(row, ['usec', 'draw', 'tick'])
        if 'state' in row: visual_key(row['state'])
    if len(draws) < 120 or any(b['usec'] <= a['usec'] for a, b in zip(draws, draws[1:])):
        raise ValueError('Ordered monotonic rendered frames required')
    intervals = [(b['usec'] - a['usec']) / 1000 for a, b in zip(draws, draws[1:])
                 if a['segment'] == b['segment'] and b['segment'] in ['controlled_movement', 'controlled_melee', 'controlled_restart']]
    idle = [(b['usec'] - a['usec']) / 1000 for a, b in zip(draws, draws[1:])
            if a['segment'] == b['segment'] == 'idle_calibration']
    physics = raw['physics']
    for row in physics:
        integer_fields(row, ['usec', 'tick'])
        visual_key(row['state'])
    if not physics or any(b['usec'] <= a['usec'] for a, b in zip(physics, physics[1:])):
        raise ValueError('Ordered monotonic physics observations required')
    requests = raw['requests']
    for row in requests:
        integer_fields(row, ['id', 'input_usec', 'input_tick', 'accepted_usec', 'accepted_tick', 'render_usec', 'render_draw'])
        for key in ['before_state', 'accepted_state', 'render_state']: visual_key(row[key])
        if row['kind'] == 'melee': integer_fields(row, ['contact_usec'])
        if row['kind'] == 'restart': integer_fields(row, ['death_usec'])
    for row in raw['contacts']: integer_fields(row, ['usec', 'tick', 'id', 'epoch', 'target', 'player_id', 'damage', 'action_frame'])
    for row in raw['activity']:
        integer_fields(row, ['usec', 'tick'])
        if 'request' in row['details']: integer_fields(row['details'], ['request'])
    expected = [(context, kind) for context in CONTEXTS for kind in ['move']*4+['melee', 'restart']]
    if len(requests) != 48 or [(r['context'], r['kind']) for r in requests] != expected or [r['id'] for r in requests] != list(range(1, 49)):
        raise ValueError('All eight contexts / 48 unique observed requests required')
    if any(b['input_usec'] <= a['input_usec'] for a, b in zip(requests, requests[1:])):
        raise ValueError('Ordered actual input requests required')
    if len(raw['contacts']) != 16:
        raise ValueError('Eight outgoing and eight lethal Core contacts required')
    def predicate(state, row, index):
        if state['context'] != row['context']: return False
        if state['health'] <= 0 or state['host_state'] != 'playing': return False
        if row['kind'] == 'move':
            delta = [b-a for a, b in zip(row['before_state']['position'], state['position'])]
            axis, sign = [(0, 1), (1, 1), (0, -1), (1, -1)][index % 6]
            return delta[axis]*sign > .01 and abs(delta[1-axis]) < .01
        if row['kind'] == 'melee': return state['action'] == 'shove'
        return state['position'][0] > 80.01 and abs(state['position'][1]-280) < .01
    accepted, rendered, retries, windups = [], [], [], []
    for index, row in enumerate(requests):
        if not row['input_usec'] <= row['accepted_usec'] <= row['render_usec']:
            raise ValueError('Invalid input/accept/render timestamp order')
        before_state = row['before_state']
        old_visual = visual_key(before_state)
        if before_state['context'] != row['context'] or before_state['health'] != (0 if row['kind']=='restart' else 1):
            raise ValueError('Input does not match its actual context/precondition')
        end = requests[index+1]['input_usec'] if index+1 < len(requests) else raw['ended_usec']
        candidates = [p for p in physics if row['input_usec'] <= p['usec'] < end and predicate(p['state'], row, index)]
        if (not candidates or candidates[0]['usec'] != row['accepted_usec'] or candidates[0]['tick'] != row['accepted_tick']
                or candidates[0]['state'] != row['accepted_state']):
            raise ValueError('Acceptance must be the first causal actor/context physics observation')
        changed = [p for p in draws if row['accepted_usec'] <= p['usec'] < end and 'state' in p
                   and p['state']['context'] == row['context'] and visual_key(p['state']) != old_visual]
        if (not changed or changed[0]['usec'] != row['render_usec'] or changed[0]['draw'] != row['render_draw']
                or changed[0]['state'] != row['render_state']):
            raise ValueError('Render must be the first changed draw of the same actor/context')
        for kind, start in [('accepted', row['accepted_usec']), ('rendered_actor_change', row['render_usec'])]:
            markers = [e for e in raw['activity'] if e['kind']==kind and e['details'].get('request')==row['id']]
            if len(markers)!=1 or markers[0]['context']!=row['context'] or not start <= markers[0]['usec'] < end:
                raise ValueError('Missing causal activity marker')
        accepted.append((row['accepted_usec'] - row['input_usec']) / 1000)
        rendered.append((row['render_usec'] - row['input_usec']) / 1000)
        if row['kind'] == 'restart':
            lethal = [c for c in raw['contacts'] if c['context']==row['context'] and c['usec']==row['death_usec']
                      and c['target']==c['player_id'] and c['lethal'] is True and c['damage']>0]
            markers = [e for e in raw['activity'] if e['kind']=='death' and e['context']==row['context']]
            if (len(lethal)!=1 or len(markers)!=1 or not row['death_usec'] <= markers[0]['usec'] <= row['input_usec']
                    or markers[0]['details']['attack_id']!=lethal[0]['id'] or markers[0]['details']['cue']!=lethal[0]['cue']
                    or not any(p['state']['context']==row['context'] and p['state']['health']==0 and p['state']['host_state']=='dead'
                               and row['death_usec'] <= p['usec'] <= row['input_usec'] for p in physics)):
                raise ValueError('Restart must follow the same real lethal Core contact/dead state')
            retries.append((row['accepted_usec'] - row['death_usec']) / 1000)
        if row['kind'] == 'melee':
            outgoing = [c for c in raw['contacts'] if c['context']==row['context'] and c['usec']==row['contact_usec']
                        and c['target']!=c['player_id'] and c['action']=='shove' and c['action_frame']==1]
            if len(outgoing)!=1 or not row['accepted_usec'] < row['contact_usec'] < end:
                raise ValueError('Contact must be the same actual Core action/contact pose')
            windups.append((row['contact_usec'] - row['accepted_usec']) / 1000)
    if len(retries) != 8 or len(windups) != 8 or len(idle) < 120:
        raise ValueError('Missing calibration, deaths or contact samples')
    # Derive progress from actual physics positions, keeping intentional waits explicit.
    previous = {}
    progress = []
    for row in raw['physics']:
        state = row['state']
        key = state['context']
        point = state['position']
        old = previous.get(key)
        if old is None or math.dist(old['position'], point) >= 4 or state['action'] != old['action']:
            progress.append({'usec': row['usec'], 'context': key, 'segment': row['segment'], 'position': point})
            previous[key] = {'position': point, 'action': state['action']}
    gaps = [(b['usec'] - a['usec']) / 1000 for a, b in zip(progress, progress[1:])
            if a['context'] == b['context'] and a['segment'] == b['segment'] == 'controlled_movement']
    deaths = [row for row in raw['activity'] if row['kind'] == 'death']
    if len(deaths) != 8:
        raise ValueError('Eight actual attributed deaths required')
    def stats(values):
        return {'samples': len(values), 'p50': percentile(values, .5), 'p95': percentile(values, .95),
                'p99': percentile(values, .99), 'max': max(values)}
    return {'input_accept_ms': stats(accepted), 'input_render_ms': stats(rendered),
            'death_to_control_ms': stats(retries), 'accepted_to_contact_ms': stats(windups),
            'movement_frame_ms': stats(intervals), 'idle_frame_ms': stats(idle),
            'meaningful_movement_gaps_ms': stats(gaps), 'progress_events': progress, 'death_causes': deaths,
            'physical_keyboard_or_photon_latency': 'NOT_MEASURED',
            'campaign_duration_or_full_Readiness_approval': False}


def encode_clip(out, raw):
    if any(row['error'] != 0 for row in raw['clip_frames']):
        raise ValueError('Native clip capture failed')
    clip = raw['clip_frames']
    if len(clip) < 60 or any(b['usec'] <= a['usec'] for a, b in zip(clip, clip[1:])):
        raise ValueError('Continuous timestamped native clip required')
    lines = ['ffconcat version 1.0']
    for i, row in enumerate(clip):
        escaped = row['path'].replace("'", "'\\''")
        lines.extend([f"file '{escaped}'", 'option framerate 1000'])
        if i + 1 < len(clip): lines.append('duration %.6f' % ((clip[i + 1]['usec'] - row['usec']) / 1000000))
    concat = out / 'clip.ffconcat'
    concat.write_text('\n'.join(lines) + '\n')
    argv = ['ffmpeg', '-nostdin', '-n', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
            '-i', str(concat), '-fps_mode', 'vfr', '-enc_time_base', '1:1000', '-video_track_timescale', '1000',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(out / 'native-camera.mp4')]
    encoded = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    (out / 'encode.log').write_text(encoded.stdout + encoded.stderr)
    write(out / 'encode.json', {'argv': argv, 'exit_code': encoded.returncode})
    if encoded.returncode != 0: raise ValueError('Native clip encoding failed')


def propose_contract(raw, metrics, source, raw_sha256, metrics_sha256):
    idle95 = metrics['idle_frame_ms']['p95']
    return {'schema': 1, 'scope': 'H04_PILOT_ACCEPTANCE', 'status': 'PROPOSED_NOT_APPROVED',
            'hardware': raw['hardware'], 'source_inventory_sha256': source,
            'baseline_raw_sha256': raw_sha256, 'baseline_metrics_sha256': metrics_sha256,
            'limits': {'accept_p95_ms': min(50, math.ceil(idle95 * 2)),
                       'render_p95_ms': min(83.334, math.ceil(idle95 * 3.5)),
                       'frame_p95_ms': min(25, math.ceil(idle95 * 1.4)),
                       'frame_p99_ms': min(33.334, math.ceil(idle95 * 1.9)), 'restart_max_ms': 1000},
            'excluded_frame_segments': ['setup', 'idle_calibration', 'attack_probe_setup', 'death_probe_setup',
                                        'staged_AI_death_wait', 'authored_setup', 'visual_clip_readback', 'intentional_idle'],
            'requires_independent_review_before_acceptance': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--contract', type=Path, help='Frozen independently reviewed contract; omit for calibration only')
    parser.add_argument('--review', type=Path, help='Independent exact-contract calibration decision')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise SystemExit('Fresh evidence directory required')
    before = inventory()
    contract, pins = load_contract(args.contract, args.review, before) if args.contract else (None, {})
    out.mkdir(parents=True)
    write(out / 'source_before.json', before)
    project = prepare_project(out)
    shutil.copy2(ROOT / 'tools/fixtures/p07_pacing.gd', project / 'tests/p07_pacing.gd')
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert digest(engine) == lock['linux_binary_sha256']
    capture = out / 'native_captures'
    capture.mkdir()
    isolate = out / 'isolated_saves'
    env = dict(os.environ, XDG_DATA_HOME=str(isolate / 'data'), XDG_CONFIG_HOME=str(isolate / 'config'),
               XDG_CACHE_HOME=str(isolate / 'cache'), AYAY_P07_SECOND_RESULT=str(out / 'raw.json'),
               AYAY_P07_SECOND_CAPTURE=str(capture), GODOT_SILENCE_ROOT_WARNING='1')
    runs = []
    for name, flags in [('import', ['--headless', '--editor', '--quit']),
                        ('native', ['--disable-vsync', '--max-fps', '60', '--script', 'res://tests/p07_pacing.gd'])]:
        validate_pins(pins)
        argv = [str(engine), '--path', str(project), *flags]
        run = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=360)
        log = run.stdout + run.stderr
        (out / f'{name}.log').write_text(log + f'\nexit_code={run.returncode}\n')
        ok = run.returncode == 0 and not any(s in log for s in ['SCRIPT ERROR:', 'Parse Error:'])
        runs.append({'name': name, 'argv': argv, 'exit_code': run.returncode, 'passed': ok})
        write(out / 'runs.json', runs)
        if not ok:
            write(out / 'validation.json', {'passed': False, 'stage': name, 'runs': runs})
            return 1
    validate_pins(pins)
    raw = strict_json((out / 'raw.json').read_text())
    metrics = analyze(raw)
    write(out / 'metrics.json', metrics)
    encode_clip(out, raw)
    after = inventory()
    write(out / 'source_after.json', after)
    passed = before == after
    if contract:
        passed = passed and raw['hardware'] == contract['hardware']
        measured = {'accept_p95_ms': metrics['input_accept_ms']['p95'],
                    'render_p95_ms': metrics['input_render_ms']['p95'],
                    'frame_p95_ms': metrics['movement_frame_ms']['p95'],
                    'frame_p99_ms': metrics['movement_frame_ms']['p99'],
                    'restart_max_ms': metrics['death_to_control_ms']['max']}
        checks = {key: {'actual': measured[key], 'limit': value, 'passed': measured[key] < value}
                  for key, value in contract['limits'].items()}
        passed = passed and all(c['passed'] for c in checks.values())
        write(out / 'threshold_checks.json', checks)
    else:
        proposal = propose_contract(raw, metrics, before, digest(out / 'raw.json'), digest(out / 'metrics.json'))
        write(out / 'contract.PROPOSED.json', proposal)
    validate_pins(pins)
    result = {'schema': 1, 'passed': passed, 'mode': 'acceptance' if contract else 'calibration_only',
              'raw_sha256': digest(out / 'raw.json'), 'contract_sha256': pins.get(str(args.contract.resolve())) if contract else None,
              'review_sha256': pins.get(str(args.review.resolve())) if contract else None,
              'source_unchanged': before == after, 'new_exports_listening_or_full_Readiness': False}
    write(out / 'validation.json', result)
    print(json.dumps(result), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
