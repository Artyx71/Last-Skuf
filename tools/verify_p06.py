#!/usr/bin/env python3
"""Serial native P06 verification using the existing production replays.

The AUTOPILOT runs tools/verify.py separately before this native stage.
--headless runs only that technical suite and never satisfies native acceptance.
--exports and --movie request real artifacts; no phase/review/merge approval is issued.
Use a fresh output. Interrupted attempts are preserved; never automatically replay them.
"""
import argparse
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ERRORS = re.compile(r'SCRIPT ERROR:|ERROR:|FAIL:|ObjectDB instances were leaked|resources still in use')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def inventory():
    return {str(p.relative_to(ROOT)): sha(p)
            for folder in ['game', 'tools', 'assets/source_audio', 'assets/source_art/characters']
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts}


def strict_report(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError('Non-finite JSON number: ' + value)
    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('Non-finite JSON number: ' + value)
        return number
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant, parse_float=finite)


def clean_command(row):
    return (isinstance(row, dict) and row.get('passed') is True
            and type(row.get('exit_code')) is int and row['exit_code'] == 0
            and isinstance(row.get('name'), str) and bool(row['name'].strip())
            and isinstance(row.get('argv'), list) and bool(row['argv'])
            and all(isinstance(x, str) and bool(x.strip()) for x in row['argv']))


def valid_report(path):
    try:
        value = strict_report(path.read_text())
    except (OSError, ValueError):
        return False
    if isinstance(value, list):
        # P04G's legacy command/check rows require an actual structured payload.
        if not value:
            return False
        for row in value:
            if (not isinstance(row, dict) or row.get('passed') is not True
                    or not isinstance(row.get('name'), str) or not row['name'].strip()):
                return False
            if 'exit_code' in row:
                if (type(row['exit_code']) is not int or row['exit_code'] != 0
                        or not isinstance(row.get('log'), str) or not row['log'].strip()):
                    return False
            elif not (isinstance(row.get('checks'), dict) and row['checks']
                      and all(x is True for x in row['checks'].values())):
                return False
        return True
    return (isinstance(value, dict) and value.get('passed') is True
            and isinstance(value.get('commands'), list) and bool(value['commands'])
            and all(clean_command(x) for x in value['commands'])
            and value.get('phase_approval') is False
            and value.get('source_unchanged', value.get('source_unchanged_after_import')) is True)


def enable_subreaper():
    # Linux PR_SET_CHILD_SUBREAPER: orphaned descendants stay owned by this
    # single serial verifier even after the wrapper itself exits.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'Cannot contain orphaned verifier descendants')


def owned_descendants(parent_pid):
    found = {parent_pid}
    identities = {}
    changed = True
    while changed:
        changed = False
        for item in Path('/proc').iterdir():
            if not item.name.isdigit():
                continue
            try:
                stat = (item / 'stat').read_text().rsplit(')', 1)[1].split()
                pid, ppid, start = int(item.name), int(stat[1]), stat[19]
            except (OSError, ValueError, IndexError):
                continue
            if pid == parent_pid or ppid in found or ppid == os.getpid():
                identities[pid] = start
                if pid not in found:
                    found.add(pid)
                    changed = True
    return identities


def live_descendants(parent_pid):
    alive = []
    for pid, start in owned_descendants(parent_pid).items():
        try:
            stat = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()
            if stat[19] == start and stat[0] != 'Z':
                alive.append(pid)
        except (OSError, IndexError):
            pass
    return alive


def stop_descendants(parent_pid):
    # No new process groups/sessions: the ROOT worker still owns the whole job.
    had_live = live_descendants(parent_pid)
    for sig in [signal.SIGTERM, signal.SIGKILL, signal.SIGKILL]:
        for pid, start in owned_descendants(parent_pid).items():
            try:
                now = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()[19]
                if now == start:
                    os.kill(pid, sig)
            except (OSError, IndexError):
                pass
        time.sleep(.1)
    # Reap adopted children, leaving Popen to reap its own direct wrapper.
    for pid in owned_descendants(parent_pid):
        if pid != parent_pid:
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass
    return {'unexpected_live_children': bool(had_live), 'remaining_live_children': live_descendants(parent_pid)}


def run_command(argv, log, timeout):
    enable_subreaper()
    started = time.monotonic()
    process = subprocess.Popen(list(map(str, argv)), cwd=ROOT, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
    cleanup_events = []
    try:
        text, _ = process.communicate(timeout=timeout)
        code = process.returncode
    except subprocess.TimeoutExpired:
        cleanup_events.append(stop_descendants(process.pid))
        try:
            text, _ = process.communicate(timeout=2)
        except subprocess.TimeoutExpired as error:
            text = error.output.decode(errors='replace') if isinstance(error.output, bytes) else (error.output or '')
            log.write_text(text + '\nCONTAINMENT_FAILURE: job group must stop; no next stage\n')
            if os.getpid() == os.getpgrp():
                os.killpg(os.getpgrp(), signal.SIGKILL)
            raise RuntimeError('Containment failed; no next stage is permitted')
        text += '\nTIMEOUT: wrapper and its descendants terminated; no automatic retry\n'
        code = 124
    cleanup = stop_descendants(process.pid)
    cleanup_events.append(cleanup)
    if cleanup['unexpected_live_children']:
        text += '\nFAIL: wrapper left live descendants; cleaned before returning\n'
    if cleanup['remaining_live_children']:
        log.write_text(text + '\nCONTAINMENT_FAILURE: live descendants remain\n')
        if os.getpid() == os.getpgrp():
            os.killpg(os.getpgrp(), signal.SIGKILL)
        raise RuntimeError('Live descendants remain; no next stage is permitted')
    log.write_text(text + '\nexit_code=' + str(code) + '\n')
    return {'argv': list(map(str, argv)), 'exit_code': code,
            'passed': code == 0 and not ERRORS.search(text),
            'seconds': round(time.monotonic() - started, 3), 'log_sha256': sha(log), 'descendant_cleanup': cleanup, 'cleanup_events': cleanup_events}


def plan(output, build, exports=False, movie=False, headless=False):
    if headless:
        return [('headless_technical_only', [sys.executable, 'tools/verify.py', '--output', output / 'headless'], 600)]
    stages = []
    for name in ['gabar', 'olezhka', 'counter_feedback', 'timka_present', 'timka_prime', 'ryzhik', 'tega', 'pasha']:
        argv = [sys.executable, 'tools/verify_p06_' + name + '.py', '--output', output / name]
        if movie:
            argv += ['--movie', '--build-output', build / name]
        stages.append((name, argv, 600))
    for name, extra in [('cast', []), ('cast_large_text', ['--large-text'])]:
        stages.append((name, [sys.executable, 'tools/verify_p06_cast.py', '--output', output / name] + extra, 300))
    stages.append(('finisher_audio', [sys.executable, 'tools/verify_p06_finisher_audio.py', '--headroom-only', '--replay-only',
                                     '--output', output / 'finisher_audio'], 300))
    stages.append(('npc_baseline', [sys.executable, 'tools/verify_p06_npc_baseline.py',
                                   '--output', output / 'npc_baseline'], 420))
    argv = [sys.executable, 'tools/verify_p04g.py', '--output', output / 'combat_baseline',
            '--build-output', build / 'combat_baseline']
    if exports:
        argv.append('--exports')
    if movie:
        argv.append('--movie')
    stages.append(('combat_baseline', argv, 2400))
    return stages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--build-output', required=True)
    parser.add_argument('--exports', action='store_true')
    parser.add_argument('--movie', action='store_true')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    if args.headless and (args.exports or args.movie):
        parser.error('Headless technical scope cannot satisfy native exports/movie evidence')
    output, build = (ROOT / args.output).resolve(), (ROOT / args.build_output).resolve()
    for folder in [output, build]:
        if folder.exists() and any(folder.iterdir()):
            parser.error('Immutable attempt: inspect previous evidence and use a fresh directory')
        folder.mkdir(parents=True, exist_ok=True)
    (output / 'logs').mkdir()
    head_before = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    before = inventory()
    write(output / 'source_hashes_before.json', before)
    stages = plan(output, build, args.exports, args.movie, args.headless)
    write(output / 'plan.json', [{'name': n, 'argv': list(map(str, a)), 'timeout': t} for n, a, t in stages])
    rows = []
    for name, argv, timeout in stages:
        print('START', name, flush=True)
        item = run_command(argv, output / 'logs' / (name + '.log'), timeout)
        item['name'] = name
        item['report_passed'] = valid_report(output / ('headless' if args.headless else name) / 'validation.json')
        # P04G keeps its legacy report filename under the declared stage directory.
        if name == 'combat_baseline':
            item['report_passed'] = valid_report(output / 'combat_baseline/validation.json')
        item['passed'] = bool(item['passed'] and item['report_passed'])
        rows.append(item)
        write(output / 'commands.json', rows)
        print('END', name, 'PASS' if item['passed'] else 'FAIL', flush=True)
        if not item['passed']:
            break
    after = inventory()
    write(output / 'source_hashes_after.json', after)
    head_after = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    summary = {'schema': 1, 'scope': 'P06_HEADLESS_TECHNICAL_ONLY' if args.headless else 'P06_NATIVE_VERIFICATION_PIPELINE',
               'passed': len(rows) == len(stages) and all(x['passed'] for x in rows) and before == after and head_before == head_after,
               'phase_approval': False, 'merge_approval': False, 'native_evidence_requested': not args.headless, 'native_acceptance_approval': False,
               'source_unchanged': before == after, 'source_head': head_before, 'head_after': head_after, 'head_unchanged': head_before == head_after,
               'stages_expected': len(stages), 'stages_completed': len(rows), 'commands': rows,
               'exports_requested': args.exports, 'movies_requested': args.movie,
               'independent_review': 'REQUIRED; technical completion is not Lead PASS',
               'listening': 'NOT_CLAIMED; owner prototype acceptance is a separate scoped record',
               'native_windows': 'NOT_TESTED; Wine evidence is labelled separately',
               'hardware_input_latency': 'NOT_MEASURED', 'campaign_duration': 'NOT_MEASURED',
               'headless_regression': 'Separate mandatory tools/verify.py controller stage' if not args.headless else 'Executed here',
               'new_C09_NPC_styles': 'OWNER_DEFERRED_TO_P08_NOT_IMPLEMENTED_OR_ACCEPTED'}
    write(output / 'validation.json', summary)
    print(json.dumps({'passed': summary['passed'], 'stages_completed': len(rows), 'phase_approval': False}), flush=True)
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
