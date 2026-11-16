#!/usr/bin/env python3
"""Actual P04G PCM signal QA. Numerical results never constitute listening."""
from array import array
import argparse
import json
from pathlib import Path
import subprocess
import sys
import wave

from audio_qa import basic_checks, decode, loudness, metrics, sha

ROOT = Path(__file__).resolve().parents[1]
BASE_RUNTIME_NAMES = ('full_replay', 'reduced_replay')
EXPORT_RUNTIME_NAMES = ('linux_export_replay', 'wine_export_replay')
FULL_RUNTIME_NAMES = BASE_RUNTIME_NAMES + ('movie_replay',) + EXPORT_RUNTIME_NAMES


def runtime_capture_plan(runtime_dir, names=None):
    # Default remains the complete exported/MovieMaker P04G evidence contract.
    expected = tuple(FULL_RUNTIME_NAMES if names is None else names)
    selected = set(expected)
    if len(expected) != len(selected) or not set(BASE_RUNTIME_NAMES) <= selected:
        raise ValueError('Runtime scope requires unique Full and Reduced names')
    if not selected <= set(FULL_RUNTIME_NAMES):
        raise ValueError('Unknown runtime capture name')
    exports = selected & set(EXPORT_RUNTIME_NAMES)
    if exports and exports != set(EXPORT_RUNTIME_NAMES):
        raise ValueError('Linux and Wine export captures must be requested together')
    captures = sorted(runtime_dir.glob('*_replay.wav'))
    exact = {p.stem for p in captures} == selected
    return expected, captures, exact



def analyze_asset(path):
    """Decode actual samples; short cues use RMS, not a gated LUFS target."""
    with wave.open(str(path), 'rb') as source:
        header = {'channels': source.getnchannels(), 'sample_width': source.getsampwidth(),
                  'rate': source.getframerate(), 'frames': source.getnframes()}
        if header['sample_width'] != 2:
            raise ValueError('P04G dry source must be lossless PCM16')
        pcm = array('h', source.readframes(source.getnframes()))
    if sys.byteorder != 'little':
        pcm.byteswap()
    signal, rate = decode(path, mono_to_stereo=header['channels'] == 1)
    stats = metrics(signal, rate)
    levels = loudness(path)
    # Positive PCM16 full scale is 32767/32768, below float1. Check both rails.
    stats['pcm_full_scale_samples'] = sum(abs(value) >= 32767 for value in pcm)
    stats['endpoint_peak'] = max(abs(value) for value in (*signal[:2], *signal[-2:]))
    checks = basic_checks(stats)
    checks.update(pcm16_44100=header['rate'] == 44100,
                  mono_source=header['channels'] == 1,
                  no_pcm_rails=stats['pcm_full_scale_samples'] == 0,
                  bounded_duration=.025 <= stats['duration_seconds'] <= 2,
                  quiet_endpoints=stats['endpoint_peak'] < .01,
                  no_internal_dropout=stats['max_internal_silence_seconds'] <= .15,
                  true_peak_headroom=levels['true_peak_dbfs'] is not None and levels['true_peak_dbfs'] < 0)
    return {'sha256': sha(path), 'header': header, 'signal': stats, 'loudness': levels,
            'checks': checks, 'passed': all(checks.values()),
            'scope': 'Single-shot SFX; loop join is not applicable. Short-cue LUFS is informational; RMS is measured.'}


def analyze(runtime_dir=None, runtime_names=None):
    manifest_path = ROOT/'game/assets/audio/combat_polish.json'
    provenance_path = ROOT/'assets/source_audio/combat_polish/provenance.json'
    manifest = json.loads(manifest_path.read_text())
    provenance = json.loads(provenance_path.read_text())
    result = {'schema': 1, 'phase': 'P04G', 'checks': [], 'assets': {}, 'runtime': {},
              'artistic_acceptance': {'status': 'NOT_ASSESSED', 'method': 'Signal analysis is not listening'},
              'loop_transition_scope': 'P03/P04 music is reused; existing loop/transition QA remains mandatory. New dry effects are single shots.',
              'producer_files': {str(p.relative_to(ROOT)): sha(p) for p in
                  [Path(__file__), ROOT/'tools/audio_qa.py', manifest_path, provenance_path]}}

    def check(name, passed, details=None):
        result['checks'].append({'name': name, 'passed': bool(passed), 'details': details})

    expected = {f'impact_{kind}_{surface}' for kind in ['unarmed', 'blunt', 'sharp', 'firearm', 'environmental']
                for surface in ['body', 'concrete', 'metal']}
    expected.update('finish_'+kind for kind in ['unarmed', 'blunt', 'sharp', 'firearm', 'environmental'])
    check('complete_twenty_cue_manifest', set(manifest['sfx']) == expected)
    paths = set()
    for cue, entry in manifest['sfx'].items():
        relative = entry['path']
        if not relative.startswith('res://assets/audio/combat_polish/'):
            raise ValueError('Unsafe cue path')
        path = (ROOT/'game'/relative[6:]).resolve()
        if not path.is_relative_to((ROOT/'game/assets/audio/combat_polish').resolve()):
            raise ValueError('Cue escapes production audio root')
        paths.add(path)
        item = analyze_asset(path)
        item['path'] = str(path.relative_to(ROOT))
        item['checks']['provenance_matches'] = item['sha256'] == provenance['assets'][cue]['sha256']
        item['passed'] = all(item['checks'].values())
        result['assets'][cue] = item
        check(cue, item['passed'], item['checks'])
    check('twenty_distinct_files', len(paths) == 20)
    check('dsp_recipe_matches', sha(ROOT/'assets/source_audio/combat_polish/render.py') == provenance['recipe_sha256'])
    if runtime_dir is not None:
        expected_names, captures, exact = runtime_capture_plan(runtime_dir, runtime_names)
        result['runtime_expected_names'] = list(expected_names)
        result['runtime_capture_scope'] = 'FULL_EXPORT_MOVIE' if set(expected_names) == set(FULL_RUNTIME_NAMES) else 'SELECTED_NATIVE_CAPTURE_SCOPE_ONLY'
        result['phase_approval'] = False
        check('exact_requested_runtime_captures', exact,
              {'expected': list(expected_names), 'actual': [p.stem for p in captures]})
        for path in captures:
            signal, rate = decode(path)
            stats = metrics(signal, rate)
            levels = loudness(path)
            trace_path = path.with_suffix('.json')
            trace = json.loads(trace_path.read_text())
            checks = basic_checks(stats)
            checks.update(long_mix=stats['duration_seconds'] > 10,
                          no_internal_dropout=stats['max_internal_silence_seconds'] <= .25,
                          true_peak_headroom=levels['true_peak_dbfs'] is not None and levels['true_peak_dbfs'] < 0,
                          actual_replay=trace.get('passed') is True,
                          one_music_player=trace.get('audio', {}).get('music_players') == 1)
            result['runtime'][path.name] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                'trace_sha256': sha(trace_path), 'signal': stats, 'loudness': levels,
                'driver': trace.get('audio', {}).get('audio_driver'), 'checks': checks,
                'scope': 'Actual mixer PCM; waveform analysis does not establish sound quality or exact acoustic contact alignment.'}
            check(path.name, all(checks.values()), checks)
    result['status'] = ('PASS_SIGNAL_AND_RETAINED_RUNTIME' if runtime_dir else 'PASS_SIGNAL_ONLY') if all(x['passed'] for x in result['checks']) else 'FAIL'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-dir', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runtime-name', action='append', choices=FULL_RUNTIME_NAMES,
                        help='Explicit native scope; default requires all five exported/MovieMaker captures')
    args = parser.parse_args()
    if args.runtime_name and not args.runtime_dir:
        parser.error('--runtime-name requires --runtime-dir')
    try:
        report = analyze(args.runtime_dir.resolve() if args.runtime_dir else None, args.runtime_name)
    except (OSError, ValueError, KeyError, wave.Error, subprocess.SubprocessError) as error:
        report = {'phase': 'P04G', 'status': 'FAIL', 'error': str(error),
                  'artistic_acceptance': {'status': 'NOT_ASSESSED', 'method': 'Signal analysis is not listening'}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(report['status'], 'checks', len(report.get('checks', [])))
    return 1 if report['status'] == 'FAIL' else 0


if __name__ == '__main__':
    sys.exit(main())
