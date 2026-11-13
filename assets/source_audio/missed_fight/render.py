#!/usr/bin/env python3
"""Original local synthesis. Python 3.14 + numpy 2.3.5 + FFmpeg (libvorbis).

Run from any directory; no external audio inputs. Writes only P04 mission audio ownership. DSP derived from project-owned P03 render.py.
All temporal effects wrap around the loop so reverb/delay tails survive the seam.
"""
from pathlib import Path
import csv, hashlib, json, math, subprocess, wave
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = json.loads((HERE / "composition.json").read_text())
SR = DATA["sample_rate"]
N = DATA["loop_frames"]
B = 60 / DATA["bpm"]
RNG = np.random.default_rng(DATA["seed"])
RUNTIME = ROOT / "game/assets/audio"
REPORT = ROOT / "reports/phases/P04/attempt1"
for d in [HERE / "masters", HERE / "sfx", RUNTIME / "music", RUNTIME / "sfx", REPORT]:
    d.mkdir(parents=True, exist_ok=True)

def midi(n): return 440 * 2 ** ((n - 69) / 12)
def timeline(seconds): return np.arange(round(seconds * SR)) / SR
def envelope(t, duration, attack=.004, release=.04, decay=0):
    e = np.minimum(1., t / attack) * np.minimum(1., np.maximum(0, duration-t) / release)
    return e * np.exp(-decay * t)
def band_noise(n, low, high):
    a = RNG.standard_normal(n)
    spec = np.fft.rfft(a)
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.minimum(1, f / max(1,low)) ** 4 / np.sqrt(1+(f/high)**8)
    a = np.fft.irfft(spec, n)
    return a / max(.001, np.std(a))
def stereo(x, pan=0):
    if x.ndim == 2: return x
    return np.column_stack((x * math.sqrt((1-pan)/2), x * math.sqrt((1+pan)/2)))
def add(buf, x, when, gain=1, pan=0):
    s = round(when * SR)
    x = stereo(x, pan) * gain
    for offset in range(0, len(x), N):
        z = x[offset:offset+N]
        indices = (s + offset + np.arange(len(z))) % N
        buf[indices] += z
def delay_loop(x, seconds, amount=.2, repeats=3, cross=True):
    out = x.copy()
    for k in range(1, repeats+1):
        y = np.roll(x, round(seconds*SR*k), axis=0)
        if cross and k % 2: y = y[:, ::-1]
        out += y * amount**k
    return out
def write_wav(path, x):
    # 24-bit PCM source avoids destructive per-stem loudness normalisation.
    a = np.round(np.clip(x, -1, 1-1/8388608) * 8388608).astype(np.int32).ravel()
    packed = np.column_stack((a & 255,(a >> 8) & 255,(a >> 16) & 255)).astype(np.uint8)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(packed.tobytes())
def ogg(wav, target):
    subprocess.run(["ffmpeg","-v","error","-y","-i",str(wav),"-c:a","libvorbis","-q:a","6","-ar",str(SR),str(target)],check=True)
def peak(x): return float(np.max(np.abs(x)))
def db(x): return round(20*math.log10(max(x,1e-12)),3)

def bass_note(note, duration, velocity=1, accent=False):
    t = timeline(duration); f = midi(note)
    # Stable sub + detuned saturated upper harmonics, brightness decays on each note.
    phase = 2*np.pi*f*t
    sub = .72*np.sin(phase)
    body = np.zeros(len(t))
    for h in range(1,18):
        bright = np.exp(-h*(.13+1.25*t))
        body += np.sin(h*phase + .035*np.sin(2*np.pi*.7*t)) * bright / h
    body = np.tanh(2.4*body) / 2.4
    bite = .13*np.sin(2*np.pi*(f*1.005)*t+1.4*np.exp(-18*t)*np.sin(phase*2))
    y = (sub + body*.9 + bite) * envelope(t,duration,.003,.035,1.4)
    y *= velocity * (1.08 if accent else 1)
    return stereo(y)

def lead_note(note, duration, velocity=1):
    t = timeline(duration); f=midi(note)
    env=envelope(t,duration,.006,.065,3.7)
    carrier = np.sin(2*np.pi*f*t + (1.8*np.exp(-8*t)+.2)*np.sin(2*np.pi*f*2*t))
    fifth = .24*np.sin(2*np.pi*f*2*t)
    x=(carrier+fifth)*env*velocity
    # Width comes from a quiet pitched counterpart, never from low-frequency phase.
    return np.column_stack((x+.10*np.sin(2*np.pi*f*.998*t)*env,x+.10*np.sin(2*np.pi*f*1.002*t)*env))*.71

def kick():
    t=timeline(.39)
    phase=2*np.pi*(48*t+85*.021*(1-np.exp(-t/.021)))
    x=np.sin(phase)*np.exp(-11*t)+.12*band_noise(len(t),1800,8500)*np.exp(-250*t)
    return np.tanh(x*1.5)*envelope(t,.39,.0007,.018)
def snare():
    t=timeline(.24)
    x=.52*band_noise(len(t),900,10000)*np.exp(-23*t)
    x+=(.36*np.sin(2*np.pi*185*t)+.12*np.sin(2*np.pi*311*t))*np.exp(-30*t)
    return np.tanh(x*1.3)*envelope(t,.24,.001,.025)
def hat(opened=False):
    dur=.18 if opened else .059; t=timeline(dur)
    x=band_noise(len(t),6500,14500)
    x+=.17*(np.sin(2*np.pi*7131*t)+np.sin(2*np.pi*9269*t))
    return x*np.exp(-t*(20 if opened else 73))*envelope(t,dur,.0008,.014)
def tom(pitch=100):
    t=timeline(.18)
    return (np.sin(2*np.pi*(pitch*t+20*.03*(1-np.exp(-t/.03))))+.08*band_noise(len(t),300,2500))*np.exp(-24*t)*envelope(t,.18,.001,.025)

stems={k:np.zeros((N,2)) for k in ["bass","texture","drums","lead"]}
k,s=kick(),snare()
for bar in range(8):
    start=bar*4*B
    pattern=DATA["bass_B_rhythm_beats"] if bar in [4,5] else DATA["bass_rhythm_beats"]
    for i,(beat,interval,length) in enumerate(pattern):
        # Bar seven turns upward into the first D; octave/fifth walk is intentional.
        if bar==7 and i>=4: interval=[7,11][i-4]
        add(stems["bass"],bass_note(DATA["root_midi"][bar]+interval,length*B,.88 if i else 1.0,i==0),start+beat*B,.25)
    kicks=[0,.75,2,3.5] if bar not in [4,5] else [0,1.5,2.25,3.25]
    if bar in [3,7]: kicks=[0,1.75,2,2.75,3.5]
    for beat in kicks: add(stems["drums"],k,start+beat*B,.47 if beat in [0,2] else .37)
    for beat in [1,3]: add(stems["drums"],s,start+beat*B,.37)
    for h in range(8):
        beat=h*.5+(.035 if h%2 else 0)
        add(stems["drums"],hat(h==5),start+beat*B,.051 if h%2 else .075,(-.36 if h%2 else .31))
    if bar in [1,3,5,7]:
        for h in range(4):
            add(stems["drums"],hat(),start+(3.25+h*.1875)*B,.034+h*.004,(-1 if h%2 else 1)*.45)
        for j in range(3 if bar in [3,7] else 1):
            add(stems["drums"],tom(130-j*23),start+(3.25+j*.25)*B,.16+j*.015,(j-1)*.32)
    for j,note in enumerate(DATA["lead_midi_by_bar"][bar]):
        add(stems["lead"],lead_note(note,(.38 if j!=2 else .62)*B,.8 if j==1 else 1),start+DATA["lead_onsets_beats"][j]*B,.088,(-.16 if j%2 else .16))
    if bar in [3,7]:
        for j,note in enumerate([69,72,73] if bar==7 else [69,70,72]):
            add(stems["lead"],lead_note(note,.12*B,.66),start+(3.5+j*.1666667)*B,.067)
    # Padded harmonic bed and quiet offbeat sequencer create harmonic development.
    dur=4*B+.45; t=timeline(dur); pad=np.zeros((len(t),2))
    for ci,note in enumerate(DATA["chords_midi"][bar]):
        f=midi(note)
        for channel,detune in [(0,.9988),(1,1.0012)]:
            pad[:,channel]+=(np.sin(2*np.pi*f*detune*t)+.19*np.sin(2*np.pi*f*2*t))*.25
    pad*=envelope(t,dur,.13,.48)[:,None]
    add(stems["texture"],pad,start,.035)
    for j in range(8):
        note=DATA["chords_midi"][bar][j%4]+12
        tt=timeline(.18)
        arp=np.sin(2*np.pi*midi(note)*tt)*envelope(tt,.18,.004,.05,17)
        add(stems["texture"],arp,start+(j*.5+.25)*B,.027,math.sin(j*1.8)*.7)

stems["lead"]=delay_loop(stems["lead"],B*.75,.29,4)
stems["texture"]=delay_loop(stems["texture"],B*1.5,.22,3)
stems["drums"]=delay_loop(stems["drums"],.037,.045,2)
# Sidechain pump is a continuous periodic envelope shared by harmonic stems.
t=np.arange(N)/SR
duck=1-.24*np.exp(-((t/B)%1)/.19)
for name in ["bass","texture","lead"]: stems[name]*=duck[:,None]
# A common gain maintains compositional balance and prevents clipping for ANY
# convex interpolation between profiles (also tested at all stems unity).
unity=sum(stems.values())
common=.60/peak(unity)
for name in stems: stems[name]*=common

manifest={"schema":1,"music":{k:DATA[k] for k in ["bpm","beats_per_bar","bars","sample_rate","loop_frames","key"]},"sfx":{},"bleeps":{}}
manifest["music"].update({"id":"MISSED_FIGHT_BACK_DOOR","loop_seconds":N/SR,"stems":[],"profiles":DATA["profiles"],"source":"assets/source_audio/missed_fight","runtime_linear_gain":1.0})
for name,x in stems.items():
    wav=HERE / "masters" / f"missed_fight_{name}.wav"
    target=RUNTIME / "music" / f"missed_fight_{name}.ogg"
    write_wav(wav,x); ogg(wav,target)
    manifest["music"]["stems"].append({"id":name,"path":"res://"+str(target.relative_to(ROOT/"game"))})

# Mission-only door creak/clunk: band-limited synthetic noise, resonant latch and release.
t=timeline(.55)
y=(.17*band_noise(len(t),190,4200)*np.exp(-6*t)+.23*np.sin(2*np.pi*(137*t-37*t*t))*np.exp(-10*t))*envelope(t,.55,.008,.065)
source=HERE/"sfx"/"door_open.wav"
write_wav(source,stereo(y))
target=RUNTIME/"sfx"/"missed_fight_door.ogg"
ogg(source,target)
manifest["sfx"]["door_open"]={"path":"res://assets/audio/sfx/missed_fight_door.ogg","bus":"SFX","gain_db":-4}
(ROOT/"game/resources/chapters/missed_fight_music.json").write_text(json.dumps({"schema":1,"music":manifest["music"]},indent=2)+"\n")
for state,gains in DATA["profiles"].items():
 x=sum(stems[name]*gain for name,gain in gains.items())
 write_wav(REPORT/f"music_{state.lower()}.wav",x)
 subprocess.run(["ffmpeg","-v","error","-y","-i",str(REPORT/f"music_{state.lower()}.wav"),"-c:a","libmp3lame","-b:a","192k",str(REPORT/f"music_{state.lower()}.mp3")],check=True)
write_wav(HERE/"masters"/"missed_fight_unity.wav",sum(stems.values()))
# Add only the new cue; preserve every prior audio asset and manifest entry.
main_path=RUNTIME/"manifest.json"
main=json.loads(main_path.read_text());main["sfx"].update(manifest["sfx"])
main_path.write_text(json.dumps(main,indent=2)+"\n")
paths=list((HERE/"masters").glob("*.wav"))+[source]+list((RUNTIME/"music").glob("missed_fight_*.ogg"))+[target]
inventory={"schema":1,"source":"assets/source_audio/missed_fight/render.py","third_party_media":False,"real_voice":False,"listening":"PENDING; numerical analysis is not listening","files":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in paths]}
(HERE/"provenance.json").write_text(json.dumps(inventory,indent=2)+"\n")
print(json.dumps({"loop_seconds":N/SR,"unity_peak":peak(sum(stems.values())),"files":len(paths)}))
