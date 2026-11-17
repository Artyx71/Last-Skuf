#!/usr/bin/env python3
"""Decoded signal and real Godot mixer QA; never a perceptual/music-quality verdict."""
from __future__ import annotations
import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = {
    'schema': 1, 'silence_dbfs': -70.0, 'dc_limit': 0.025,
    'loop_join_limit': 0.025, 'mix_peak_limit': 0.95,
    'mix_internal_silence_limit_seconds': 0.2,
    'music_loudness_guard_lufs': [-50, -5],
    'note': 'Broad technical guards, not artistic loudness targets or proof of inaudibility.'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def command(argv, timeout=60):
    proc = subprocess.run(list(map(str, argv)), capture_output=True, timeout=timeout)
    if proc.returncode:
        raise ValueError(f'{argv[0]} exit {proc.returncode}: {proc.stderr.decode(errors="replace")[-900:]}')
    return proc


def decode(path, *, mono_to_stereo=False):
    # Decode to float WAV at the source's native rate/channels; parse the actual
    # output stream, eliminating a separate ffprobe dependency.
    # Duplicate a mono cue at unity; the default rematrix would attenuate it.
    conversion = ['-af', 'pan=stereo|c0=c0|c1=c0'] if mono_to_stereo else []
    decoded = command(['ffmpeg', '-v', 'error', '-i', path, '-map', '0:a:0',
                       *conversion, '-acodec', 'pcm_f32le', '-f', 'wav', 'pipe:1']).stdout
    if decoded[:4] != b'RIFF' or decoded[8:12] != b'WAVE':
        raise ValueError('Decoder did not produce WAV')
    offset=12; rate=None; channels=None; raw=None
    while offset+8 <= len(decoded):
        kind=decoded[offset:offset+4]; size=struct.unpack_from('<I',decoded,offset+4)[0]; offset+=8
        if kind==b'fmt ':
            tag,channels,rate=struct.unpack_from('<HHI',decoded,offset)
            bits=struct.unpack_from('<H',decoded,offset+14)[0]
            subtype=struct.unpack_from('<H',decoded,offset+24)[0] if tag==65534 and size>=40 else tag
            if bits!=32 or subtype!=3:raise ValueError('Expected actual IEEEfloat32 decoded samples')
        if kind==b'data':
            raw=decoded[offset:offset+size] if size!=0xffffffff else decoded[offset:]
            break
        offset+=size+(size%2)
    if channels!=2 or rate is None or raw is None:
        raise ValueError(f'Expected complete stereo decoded stream: {path}')
    signal = array('f')
    signal.frombytes(raw)
    if sys.byteorder != 'little':
        signal.byteswap()
    if not signal or len(signal) % channels or not all(math.isfinite(x) for x in signal):
        raise ValueError(f'Empty, incomplete or nonfinite decoded signal: {path}')
    return signal, rate


def db(value):
    return 20 * math.log10(max(value, 1e-12))


def metrics(signal, rate):
    if len(signal) < 4 or len(signal) % 2:
        raise ValueError('Need complete stereo frames')
    peak = max(abs(x) for x in signal)
    energy = sum(x*x for x in signal)
    frames = len(signal) // 2
    block = max(1, rate // 100) * 2
    quiet = 10 ** (POLICY['silence_dbfs'] / 20)
    runs, start = [], None
    rms_blocks = []
    for offset in range(0, len(signal), block):
        chunk = signal[offset:offset+block]
        rms = math.sqrt(sum(x*x for x in chunk)/len(chunk))
        rms_blocks.append(rms)
        if rms <= quiet and start is None:
            start = offset // 2
        elif rms > quiet and start is not None:
            runs.append([start/rate, offset/2/rate]); start = None
    if start is not None:
        runs.append([start/rate, frames/rate])
    internal = [b-a for a,b in runs if a > 0 and b < frames/rate]
    derivatives = [abs(signal[i]-signal[i-2]) for i in range(2,len(signal))]
    derivatives.sort()
    return {
        'frames': frames, 'sample_rate': rate, 'channels': 2, 'duration_seconds': frames/rate,
        'sample_peak': peak, 'sample_peak_dbfs': db(peak), 'rms_dbfs': db(math.sqrt(energy/len(signal))),
        'clipped_samples': sum(abs(x) >= 1.0 for x in signal),
        'dc_channels': [sum(signal[channel::2])/frames for channel in range(2)],
        'silence_threshold_dbfs': POLICY['silence_dbfs'], 'silence_runs_seconds': runs,
        'max_internal_silence_seconds': max(internal, default=0),
        'boundary_step': max(abs(signal[c]-signal[-2+c]) for c in range(2)),
        'max_sample_step': derivatives[-1],
        'sample_step_p9999': derivatives[min(len(derivatives)-1, int(len(derivatives)*.9999))],
    }


def basic_checks(stats):
    return {'nonempty_signal_energy': stats['rms_dbfs'] > -60,
            'no_full_scale_clipping': stats['clipped_samples'] == 0,
            'bounded_dc': max(abs(x) for x in stats['dc_channels']) < POLICY['dc_limit']}


def loudness(path):
    proc = command(['ffmpeg', '-hide_banner', '-nostats', '-i', path,
                    '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    text = proc.stderr.decode(errors='replace')
    integrated = re.findall(r'I:\s+(-?[\d.]+) LUFS', text)
    truepeak = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', text)
    return {'integrated_lufs': float(integrated[-1]) if integrated else None,
            'true_peak_dbfs': float(truepeak[-1]) if truepeak else None,
            'short_cue_gating_warning': 'Integrated LUFS is not reliable for very short cues.'}


def mix(stems, gains):
    names = list(stems)
    return array('f', (sum(float(stems[name][i])*gains.get(name,0) for name in names)
                       for i in range(len(stems[names[0]]))))


def event_windows(signal, rate, times, radius=.04):
    result = []
    for event in times:
        t = event['sample_time_seconds']
        center = int(t*rate)*2
        lo, hi = max(0,center-int(radius*rate)*2), min(len(signal),center+int(radius*rate)*2)
        if hi-lo < 4:
            result.append({**event,'in_capture':False}); continue
        segment = signal[lo:hi]
        result.append({**event,'in_capture':True,'peak':max(abs(x) for x in segment),
                       'max_step':max(abs(segment[i]-segment[i-2]) for i in range(2,len(segment))),
                       'rms_dbfs':db(math.sqrt(sum(x*x for x in segment)/len(segment)))})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='reports/autopilot/P03/audio_qa')
    parser.add_argument('--capture-engine', action='store_true')
    parser.add_argument('--analysis-only', action='store_true', help='CI signal checks only; never a full runtime gate')
    args = parser.parse_args()
    if args.capture_engine == args.analysis_only:
        parser.error('Choose exactly one of --capture-engine or --analysis-only')
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT) or output.is_relative_to(ROOT/'assets/references'):
        raise SystemExit('Output must be inside project and outside private references')
    output.mkdir(parents=True,exist_ok=True)
    result = {'schema':1,'policy':POLICY,'checks':[], 'assets':[], 'mixes':{}, 'transitions':[],
              'artistic_acceptance':{'status':'NOT_ASSESSED','method':'Decoded signal analysis is not listening'}}
    result['producer_files']={str(path.relative_to(ROOT)):sha(path) for path in [
        Path(__file__).resolve(), ROOT/'tools/fixtures/audio_qa_capture.gd',ROOT/'game/assets/audio/manifest.json']}
    def check(name, condition, details=None):
        result['checks'].append({'name':name,'passed':bool(condition),'details':details})
    try:
        manifest = json.loads((ROOT/'game/assets/audio/manifest.json').read_text())
        music = manifest['music']; stems = {}; asset_paths = {}
        for entry in music['stems']:
            asset_paths[entry['path']] = 'stem'
        for entry in manifest['sfx'].values():
            asset_paths[entry['path']] = 'sfx'
        for relative,kind in asset_paths.items():
            if not relative.startswith('res://assets/audio/'):
                raise ValueError('Unsafe audio resource path')
            path = (ROOT/'game'/relative[6:]).resolve()
            if not path.is_relative_to(ROOT/'game/assets/audio'):
                raise ValueError('Audio escapes asset root')
            signal,rate = decode(path); stats = metrics(signal,rate); levels = loudness(path)
            tests = basic_checks(stats)
            tests['source_stereo_48k'] = rate == music['sample_rate']
            tests['true_peak_below_full_scale'] = levels['true_peak_dbfs'] is not None and levels['true_peak_dbfs'] < 0
            if kind == 'stem':
                lower,upper=POLICY['music_loudness_guard_lufs']
                tests['broad_loudness_guard']=levels['integrated_lufs'] is not None and lower<levels['integrated_lufs']<upper
                tests.update(exact_loop_frames=stats['frames']==music['loop_frames'],
                             bounded_loop_join=stats['boundary_step'] < POLICY['loop_join_limit'])
                name = next(s['id'] for s in music['stems'] if s['path']==relative)
                stems[name] = signal
            else:
                tests['bounded_cue_duration'] = .025 <= stats['duration_seconds'] <= 2
            check(relative,all(tests.values()),tests)
            result['assets'].append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),
                                     'kind':kind,'signal':stats,'loudness':levels})
        # Decode retained production masters too: corrupt/silent source cannot hide behind a valid OGG.
        for path in sorted((ROOT/'assets/source_audio/last_skuf_demo').rglob('*.wav')):
            signal,rate = decode(path); stats = metrics(signal,rate)
            tests = basic_checks(stats)
            if path.parent.name == 'masters': tests['exact_master_frames'] = stats['frames']==music['loop_frames']
            check(str(path.relative_to(ROOT)),all(tests.values()),tests)
            result['assets'].append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'kind':'source','signal':stats})
        for state,gains in music['profiles'].items():
            signal = mix(stems,gains); stats = metrics(signal,music['sample_rate'])
            tests = basic_checks(stats)
            tests.update(headroom=stats['sample_peak'] < POLICY['mix_peak_limit'],
                         bounded_join=stats['boundary_step'] < POLICY['loop_join_limit'],
                         no_internal_dropout=stats['max_internal_silence_seconds'] <= POLICY['mix_internal_silence_limit_seconds'])
            check('decoded_profile_'+state,all(tests.values()),tests)
            result['mixes'][state] = stats
        # Probe every directed profile transition at three different rhythmic offsets.
        # Continuous gain ramps + coherent stem phase; these are synthetic probes, not engine captures.
        sr = music['sample_rate']; count = music['loop_frames']
        profiles = music['profiles']
        for before,a in profiles.items():
            for after,b in profiles.items():
                if before == after: continue
                probes = []
                for beat in [0,7,16]:
                    offset = int(beat*60/music['bpm']*sr)
                    last = [sum(stems[n][((offset-1)%count)*2+c]*a[n] for n in stems) for c in range(2)]
                    peak=0.; step=0.
                    for frame in range(int(sr*.55)):
                        elapsed=frame/sr
                        gains={n:a[n]+max(-elapsed*1.9,min(elapsed*1.9,b[n]-a[n])) for n in stems}
                        values=[sum(stems[n][((offset+frame)%count)*2+c]*gains[n] for n in stems) for c in range(2)]
                        peak=max(peak,*map(abs,values)); step=max(step,*(abs(values[c]-last[c]) for c in range(2))); last=values
                    probes.append({'beat_offset':beat,'peak':peak,'max_step':step})
                check('profile_transition_'+before+'_'+after, all(p['peak']<.98 for p in probes),probes)
                result['transitions'].append({'from':before,'to':after,'signal_probes':probes,'scope':'offline numerical probes'})
        # Historical real gameplay capture: retained immutable P03 evidence includes ten actual deaths.
        replay=ROOT/'reports/phases/P03/native_replay.json'
        capture=ROOT/'reports/phases/P03/native_replay.wav'
        data=json.loads(replay.read_text()); sig,rate=decode(capture); stats=metrics(sig,rate)
        check('actual_gameplay_replay',data['passed'] and data['actual_deaths']==10 and data['audio']['music_players']==1 and data['audio']['stem_starts']==1 and stats['clipped_samples']==0)
        result['historical_gameplay']={'json':str(replay.relative_to(ROOT)),'json_sha256':sha(replay),'wav':str(capture.relative_to(ROOT)),'wav_sha256':sha(capture),'signal':stats,'provenance':'retained P03 native replay; not a fresh run'}
        if args.capture_engine:
            lock=json.loads((ROOT/'tools/toolchain.lock.json').read_text())
            binary=ROOT/'.tools/godot'/f'Godot_v{lock["release"]}_linux.x86_64'
            check('pinned_engine',sha(binary)==lock['linux_binary_sha256'])
            engine_json=output/'engine.json'; engine_wav=output/'engine.wav'
            env=dict(os.environ,AYAY_AUDIO_QA_JSON=str(engine_json),AYAY_AUDIO_QA_WAV=str(engine_wav),
                     AYAY_OPTIONS_PATH=str(output/'isolated-options.json'),AYAY_DIALOGUE_SAVE_PATH=str(output/'isolated-dialogue.json'))
            for p in [engine_json,engine_wav,output/'isolated-options.json',output/'isolated-dialogue.json']: p.unlink(missing_ok=True)
            argv=[str(binary),'--path',str(ROOT/'game'),'--script',str(ROOT/'tools/fixtures/audio_qa_capture.gd')]
            proc=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=55)
            text=proc.stdout+proc.stderr
            (output/'engine.log').write_text(text+f'\nexit_code={proc.returncode}\n')
            check('fresh_godot_execution',proc.returncode==0 and not any(t in text for t in ['SCRIPT ERROR:','ERROR:','FAIL','ObjectDB instances were leaked']))
            engine=json.loads(engine_json.read_text()); audio=engine['audio']; sig,rate=decode(engine_wav); stats=metrics(sig,rate)
            start=engine['capture_start_clock']; end=engine['capture_end_clock']
            # Account for mixer-buffer latency. Store the estimate and a conservative window uncertainty.
            origin=end-stats['duration_seconds']
            events=[e for e in audio['events'] if e.get('kind')=='commit' and start<=e['clock']<=end]
            windows=event_windows(sig,rate,[{'state':e['state'],'clock':e['clock'],'sample_time_seconds':e['clock']-origin} for e in events])
            wrap_times=[]; loop=float(music['loop_seconds']); boundary=math.ceil(origin/loop)*loop
            while boundary<end:
                wrap_times.append({'clock':boundary,'sample_time_seconds':boundary-origin}); boundary+=loop
            wrap_windows=event_windows(sig,rate,wrap_times)
            check('real_mixer_driver',audio['audio_driver'] not in ['Dummy',''] and audio['mixer_clock'])
            check('fresh_mix_signal',all(basic_checks(stats).values()) and stats['duration_seconds']>=28 and stats['max_internal_silence_seconds']<=.2)
            check('fresh_all_profiles',set(e['state'] for e in events)==set(profiles))
            check('fresh_no_stacking',audio['music_players']==1 and audio['stem_starts']==1)
            check('fresh_loop_wraps',len(wrap_windows)>=2 and all(w.get('in_capture') for w in wrap_windows))
            # Numeric discontinuity guard only. Expected percussion transients share this limit.
            limit=max(.12,stats['sample_step_p9999']*4)
            check('fresh_transition_windows',bool(windows) and all(w['in_capture'] and w['max_step']<=limit for w in windows),{'step_limit':limit})
            check('fresh_loop_windows',all(w['max_step']<=limit for w in wrap_windows),{'step_limit':limit})
            result['engine']={'driver':audio['audio_driver'],'json':str(engine_json.relative_to(ROOT)),'json_sha256':sha(engine_json),
                'wav':str(engine_wav.relative_to(ROOT)),'wav_sha256':sha(engine_wav),'signal':stats,'loudness':loudness(engine_wav),
                'capture_start_clock':start,'estimated_first_sample_clock':origin,'alignment_uncertainty_seconds':.04,
                'transition_windows':windows,'loop_windows':wrap_windows,
                'warning':'No listening/inaudibility claim. Window alignment is bounded by mixer latency, not sample-exact.'}
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as exc:
        check('qa_execution',False,str(exc))
    result['technical_status']='PASS' if result['checks'] and all(c['passed'] for c in result['checks']) else 'FAIL'
    if result['technical_status']=='PASS' and args.analysis_only:
        result['technical_status']='PASS_SIGNAL_ONLY'
    result['technical_scope']='signal_and_fresh_mixer' if args.capture_engine else 'signal_only_runtime_not_rerun'
    result['passed_checks']=sum(c['passed'] for c in result['checks'])
    result['failed_checks']=sum(not c['passed'] for c in result['checks'])
    (output/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['technical_status','passed_checks','failed_checks']}))
    return 0 if result['technical_status'] in ['PASS','PASS_SIGNAL_ONLY'] else 1

if __name__=='__main__':
    sys.exit(main())
