#!/usr/bin/env python3
"""Serialize through the project Controller. Actual runtime/mixer QA, no listening claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from verify_p06_cast import ROOT, GODOT, ERRORS, sha, sources, write
from verify_character_finisher_audio import verify


def source_hashes():
    result = sources()
    for folder in ['assets/source_audio/character_finishers', 'reports/phases/P06/audio-c01-signal-review-01']:
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file(): result[str(path.relative_to(ROOT))] = sha(path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--import-assets', action='store_true')
    parser.add_argument('--replay-only', action='store_true', help='Keep earlier unchanged-source regressions; run actual contact replay only')
    parser.add_argument('--headroom-only', action='store_true', help='Native targeted three contacts plus all twenty solo cues and eight twelve-voice bursts')
    args = parser.parse_args()
    if args.headroom_only and (args.headless or not args.replay_only): parser.error('Headroom check requires native --replay-only')
    output = (ROOT / args.output).resolve()
    if output.exists(): parser.error('Use a fresh output; consumed jobs are never blindly repeated')
    output.mkdir(parents=True)
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    assert sha(GODOT) == lock['linux_binary_sha256']
    profile = ROOT / '.tools/p06-c01-qa' / hashlib.sha256(str(output).encode()).hexdigest()[:16]
    profile.mkdir(parents=True)
    env = dict(os.environ, AYAY_C01_OUTPUT=str(output / 'replay'), XDG_CONFIG_HOME=str(profile/'config'), XDG_DATA_HOME=str(profile/'data'))
    for key, name in [('AYAY_OPTIONS_PATH','options'),('AYAY_STORY_SAVE_PATH','story'),('AYAY_CHAPTER_SAVE_PATH','chapter'),('AYAY_DIALOGUE_SAVE_PATH','dialogue')]:
        env[key] = str(profile / (name + '.json'))
    env['AYAY_TIMING_RESULT'] = str(output / 'contact_timing.json')
    before = source_hashes();write(output/'source_hashes_before.json', before)
    bindings = verify();write(output/'source_binding.json', bindings)
    commands = []
    def run(name, argv, timeout=100):
        start = time.monotonic()
        try:
            result = subprocess.run(list(map(str,argv)), cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
            code, log = result.returncode, result.stdout+result.stderr
        except subprocess.TimeoutExpired as error:
            code, log = 124, 'TIMEOUT\n'+str(error.stdout)+str(error.stderr)
        (output/(name+'.log')).write_text(log+'\nexit_code='+str(code)+'\n')
        item = {'name':name,'argv':list(map(str,argv)),'exit_code':code,'passed':code==0 and not ERRORS.search(log),'seconds':round(time.monotonic()-start,3)}
        commands.append(item);write(output/'commands.json',commands);print(name,'PASS' if item['passed'] else 'FAIL',flush=True)
        return item['passed']
    ok = bool(bindings) and all(c['passed'] for c in bindings)
    base = [GODOT, '--headless', '--path', ROOT/'game']
    if ok and args.import_assets: ok = run('import',base+['--editor','--quit'])
    imported = source_hashes()
    changed = [key for key in set(before)|set(imported) if before.get(key)!=imported.get(key)]
    allowed = {f'game/assets/audio/character_finishers/{p.name}.import' for p in (ROOT/'game/assets/audio/character_finishers').glob('*.wav')}
    allowed |= {'game/scripts/systems/character_finisher_audio.gd.uid','game/tests/character_finisher_audio_test.gd.uid','game/tests/character_finisher_audio_replay.gd.uid'}
    write(output/'import_source_delta.json',{'changed':sorted(changed),'allowed':sorted(allowed),'unexpected':sorted(set(changed)-allowed)})
    ok = ok and (not changed or args.import_assets and set(changed)<=allowed)
    if ok and not args.replay_only:
        for test in ['character_finisher_audio','character_combat_profile','audio','contact_timing','p04g','yakuza_finisher_authority','restart']:
            # The legacy contact test counts render observations of fixed physics
            # poses. Lock one physics step per frame, preserving its full-window
            # oracle even during the first cold asset/cache load.
            timing = ['--fixed-fps','60'] if test=='contact_timing' else []
            if not run(test,base+timing+['--script',f'res://tests/{test}_test.gd']): ok=False;break
    replay = {}
    if ok:
        (output/'replay').mkdir()
        argv = [GODOT,'--path',ROOT/'game','--disable-vsync','--max-fps','60']
        if args.headless: argv += ['--headless','--fixed-fps','60']
        argv += ['--script','res://tests/character_finisher_audio_replay.gd']
        if args.headroom_only: argv += ['--','--c01-headroom-only']
        ok = run('contact_replay',argv,420)
        path = output/'replay/result.json'
        if path.exists(): replay=json.loads(path.read_text())
        ok = ok and replay.get('passed') is True and replay.get('actual_input') is True and len(replay.get('route_results',[]))==(3 if args.headroom_only else 45)
    unchanged = source_hashes()==imported
    summary = {'schema':1,'scope':'C01_HEADROOM_TARGETED_ONLY' if args.headroom_only else 'C01_RUNTIME_SIGNAL_ONLY','passed':bool(ok and unchanged),'headless':args.headless,
               'phase_approval':False,'artistic_approval':False,'listening_performed':False,'source_unchanged_after_import':unchanged,
               'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
               'source_binding_checks':len(bindings),'runtime_checks':len(replay.get('checks',[])),
               'commands':commands,'mixer_signal_analysis':'PENDING' if not args.headless else 'NOT_TESTED_HEADLESS',
               'native_windows':'NOT_TESTED','hardware_latency':'NOT_MEASURED'}
    write(output/'source_hashes_after.json',source_hashes())
    write(output/'validation.json',summary)
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    return 0 if summary['passed'] else 1


if __name__=='__main__': sys.exit(main())
