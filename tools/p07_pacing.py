#!/usr/bin/env python3
"""Native pacing calibration/acceptance, using the existing second-pilot setup."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess

from p07_second_pilot import prepare_project
from p07_room_pilot import ROOT, digest, inventory, write


def percentile(values, q):
    if not values or not all(math.isfinite(x) and x >= 0 for x in values):
        raise ValueError('Finite nonnegative samples required')
    return sorted(values)[max(0, math.ceil(q * len(values)) - 1)]


def load_contract(path, review_path, current):
    if review_path is None:
        raise ValueError('Independent calibration review required before acceptance')
    contract = json.loads(path.read_text())
    review = json.loads(review_path.read_text())
    if (review.get('status') != 'PASS_COMPONENT' or review.get('scope') != 'H04_CALIBRATION_CONTRACT'
            or review.get('independent_of_author') is not True or review.get('reviewer') in [None, '', '/root']
            or review.get('must_fix') != [] or review.get('contract_sha256') != digest(path)):
        raise ValueError('Missing, unreviewed or changed calibration contract')
    if contract.get('scope') != 'H04_PILOT_ACCEPTANCE' or contract.get('source_inventory_sha256') != current:
        raise ValueError('Stale calibrated source inventory')
    if set(contract.get('limits', {})) != {'accept_p95_ms', 'render_p95_ms', 'frame_p95_ms', 'frame_p99_ms', 'restart_max_ms'}:
        raise ValueError('All five calibrated limits required')
    limits = contract['limits']
    if (not all(type(x) in [int, float] and math.isfinite(x) and x > 0 for x in limits.values())
            or limits['restart_max_ms'] > 1000 or limits['accept_p95_ms'] > 50
            or limits['render_p95_ms'] > 83.334 or limits['frame_p95_ms'] > 25 or limits['frame_p99_ms'] > 33.334):
        raise ValueError('Calibration cannot weaken absolute safety ceilings')
    return contract


def analyze(raw):
    if raw.get('schema') != 1 or raw.get('failed') != 0:
        raise ValueError('Complete functional native run required')
    draws = raw['draws']
    if len(draws) < 120 or any(b['usec'] <= a['usec'] for a, b in zip(draws, draws[1:])):
        raise ValueError('Ordered monotonic rendered frames required')
    intervals = [(b['usec'] - a['usec']) / 1000 for a, b in zip(draws, draws[1:])
                 if a['segment'] == b['segment'] and b['segment'] in ['idle_calibration', 'controlled_movement', 'controlled_melee', 'controlled_restart']]
    idle = [(b['usec'] - a['usec']) / 1000 for a, b in zip(draws, draws[1:])
            if a['segment'] == b['segment'] == 'idle_calibration']
    requests = raw['requests']
    if len(requests) != 48 or len({r['context'] for r in requests}) != 8 or len({r['id'] for r in requests}) != 48:
        raise ValueError('All eight contexts / 48 unique observed requests required')
    accepted, rendered, retries, windups = [], [], [], []
    for row in requests:
        if not row['input_usec'] <= row['accepted_usec'] <= row['render_usec']:
            raise ValueError('Invalid input/accept/render timestamp order')
        if not any(p['usec'] == row['accepted_usec'] and p['tick'] == row['accepted_tick'] for p in raw['physics']):
            raise ValueError('Acceptance is not bound to raw physics observation')
        if not any(p['usec'] == row['render_usec'] and p['draw'] == row['render_draw'] for p in draws):
            raise ValueError('Render observation is not in raw draw series')
        accepted.append((row['accepted_usec'] - row['input_usec']) / 1000)
        rendered.append((row['render_usec'] - row['input_usec']) / 1000)
        if row['kind'] == 'restart':
            if row['death_usec'] > row['input_usec']:
                raise ValueError('Restart precedes real death')
            retries.append((row['accepted_usec'] - row['death_usec']) / 1000)
        if row['kind'] == 'melee':
            if row['contact_usec'] <= row['accepted_usec']:
                raise ValueError('Intentional contact must remain separate from acceptance')
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
    contract = load_contract(args.contract, args.review, before) if args.contract else None
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
    raw = json.loads((out / 'raw.json').read_text())
    metrics = analyze(raw)
    write(out / 'metrics.json', metrics)
    if any(row['error'] != 0 for row in raw['clip_frames']):
        raise ValueError('Native clip capture failed')
    clip = raw['clip_frames']
    if len(clip) < 60 or any(b['usec'] <= a['usec'] for a, b in zip(clip, clip[1:])):
        raise ValueError('Continuous timestamped native clip required')
    lines = ['ffconcat version 1.0']
    for i, row in enumerate(clip):
        escaped = row['path'].replace("'", "'\\''")
        lines.append(f"file '{escaped}'")
        if i + 1 < len(clip): lines.append('duration %.6f' % ((clip[i + 1]['usec'] - row['usec']) / 1000000))
    concat = out / 'clip.ffconcat'
    concat.write_text('\n'.join(lines) + '\n')
    argv = ['ffmpeg', '-nostdin', '-n', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
            '-i', str(concat), '-fps_mode', 'vfr', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(out / 'native-camera.mp4')]
    encoded = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    (out / 'encode.log').write_text(encoded.stdout + encoded.stderr)
    write(out / 'encode.json', {'argv': argv, 'exit_code': encoded.returncode})
    if encoded.returncode != 0: raise ValueError('Native clip encoding failed')
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
        idle95 = metrics['idle_frame_ms']['p95']
        proposal = {'schema': 1, 'scope': 'H04_PILOT_ACCEPTANCE', 'status': 'PROPOSED_NOT_APPROVED',
                    'hardware': raw['hardware'], 'source_inventory_sha256': before,
                    'baseline_raw_sha256': digest(out / 'raw.json'),
                    'baseline_metrics_sha256': digest(out / 'metrics.json'),
                    'limits': {'accept_p95_ms': min(50, math.ceil(idle95 * 2)),
                               'render_p95_ms': min(83.334, math.ceil(idle95 * 3.5)),
                               'frame_p95_ms': min(25, math.ceil(idle95 * 1.4)),
                               'frame_p99_ms': min(33.334, math.ceil(idle95 * 1.9)), 'restart_max_ms': 1000},
                    'excluded_frame_segments': ['setup', 'attack_probe_setup', 'death_probe_setup', 'staged_AI_death_wait', 'authored_setup', 'visual_clip_readback', 'intentional_idle'],
                    'requires_independent_review_before_acceptance': True}
        write(out / 'contract.PROPOSED.json', proposal)
    result = {'schema': 1, 'passed': passed, 'mode': 'acceptance' if contract else 'calibration_only',
              'raw_sha256': digest(out / 'raw.json'), 'contract_sha256': digest(args.contract) if contract else None,
              'source_unchanged': before == after, 'new_exports_listening_or_full_Readiness': False}
    write(out / 'validation.json', result)
    print(json.dumps(result), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
