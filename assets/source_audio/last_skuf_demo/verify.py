#!/usr/bin/env python3
"""Measure delivered PCM AND decoded runtime media; this is not listening QA."""
from pathlib import Path
import csv, hashlib, itertools, json, math, subprocess, wave
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REPORT=ROOT/"reports/phases/P03"
MANIFEST=ROOT/"game/assets/audio/manifest.json"
M=json.loads(MANIFEST.read_text())
SR=M["music"]["sample_rate"]; N=M["music"]["loop_frames"]
def decode(path):
    probe=subprocess.run(["ffprobe","-v","error","-select_streams","a:0","-show_entries","stream=sample_rate,channels","-of","json",str(path)],check=True,stdout=subprocess.PIPE,text=True)
    stream=json.loads(probe.stdout)["streams"][0]
    assert int(stream["sample_rate"])==SR and stream["channels"]==2,(str(path),stream)
    p=subprocess.run(["ffmpeg","-v","error","-i",str(path),"-f","f32le","-ac","2","-ar",str(SR),"pipe:1"],check=True,stdout=subprocess.PIPE)
    return np.frombuffer(p.stdout,dtype="<f4").reshape(-1,2)
def db(a): return round(float(20*np.log10(max(1e-12,a))),4)
def measure(x):
    d=np.abs(np.diff(x,axis=0)); seam=float(np.max(np.abs(x[0]-x[-1])))
    return {"frames":len(x),"sample_rate":SR,"channels":2,"sample_peak_dbfs":db(np.max(np.abs(x))),"rms_dbfs":db(np.sqrt(np.mean(x.astype(np.float64)**2))),"clipped_samples":int(np.count_nonzero(np.abs(x)>=1)),"seam_step":seam,"seam_step_dbfs":db(seam),"internal_max_step":float(np.max(d)),"internal_p999_step":float(np.quantile(d,.999)),"seam_below_internal_max":bool(seam<=np.max(d))}
def path_from_res(path): return ROOT/"game"/path.removeprefix("res://")
def write_wav(path,x):
    a=np.round(np.clip(x,-1,1-1/8388608)*8388608).astype(np.int32).ravel()
    packed=np.column_stack((a&255,(a>>8)&255,(a>>16)&255)).astype(np.uint8)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(packed.tobytes())
results={"schema":1,"kind":"AUTHOR_NUMERICAL_QA_NOT_PERCEPTUAL_LISTENING","music":{},"sfx":{},"mixes":{},"checks":{},"listening":{"status":"PENDING_HUMAN_OR_AUDIO_PERCEPTION_CAPABILITY","method":"No perceptual audio input/listening tool exposed to this author context. FFmpeg decode, plots, tool playback or process exit are not listening."}}
runtime={}
for stem in M["music"]["stems"]:
    name=stem["id"]; source=HERE/"masters"/f"last_skuf_demo_{name}.wav"; target=path_from_res(stem["path"])
    x=decode(source); y=decode(target); runtime[name]=y
    assert len(x)==N and len(y)==N, (name,len(x),len(y))
    source_stats=measure(x); runtime_stats=measure(y)
    results["music"][name]={"source":source_stats,"decoded_runtime":runtime_stats,"codec_error_rms_dbfs":db(np.sqrt(np.mean((x-y)**2))),"codec_correlation":float(np.corrcoef(x.ravel(),y.ravel())[0,1]),"bar_rms_dbfs":[db(np.sqrt(np.mean(y[i*N//8:(i+1)*N//8].astype(np.float64)**2))) for i in range(8)]}
    assert source_stats["clipped_samples"]==runtime_stats["clipped_samples"]==0
    assert runtime_stats["seam_below_internal_max"]
unity=sum(runtime.values()); results["mixes"]["ALL_STEMS_UNITY"]=measure(unity)
state_mixes={}
for state,gains in M["music"]["profiles"].items():
    x=sum(runtime[name]*gain for name,gain in gains.items()); state_mixes[state]=x
    results["mixes"][state]=measure(x)
    assert np.max(np.abs(x))<.8
    # Real loop repeated twice gives the reviewer a decoded-runtime seam preview.
    if state=="COMBAT":
        write_wav(REPORT/"audio_preview_combat_runtime_twice.wav",np.tile(x,(2,1)))
for name,entry in M["sfx"].items():
    x=decode(path_from_res(entry["path"])); stats=measure(x)
    stats["runtime_gain_db"]=entry["gain_db"]
    stats["first_frame_abs_max"]=float(np.max(np.abs(x[0])))
    stats["last_frame_abs_max"]=float(np.max(np.abs(x[-1])))
    results["sfx"][name]=stats
    assert 0<len(x)<=SR*2 and stats["clipped_samples"]==0
# A linear interpolation between profiles cannot exceed the larger endpoint
# absolute sample value. We also sample 101 gains to protect the implementation.
max_cross=0
for a,b in itertools.combinations(state_mixes,2):
    x,y=state_mixes[a],state_mixes[b]
    for alpha in np.linspace(0,1,101):
        max_cross=max(max_cross,float(np.max(np.abs(x*(1-alpha)+y*alpha))))
results["checks"].update({"source_and_runtime_frames_equal_640000":True,"all_stereo_48k":True,"all_runtime_sources_decode":True,"no_sample_clipping":True,"linear_profile_crossfade_peak_dbfs":db(max_cross),"max_unity_stems_peak_below_minus_4_dbfs":bool(np.max(np.abs(unity))<10**(-4/20)),"seams_no_larger_than_internal_max_step":True,"loop_duration_seconds":N/SR,"preview_warning":"Adaptive eight-state preview is a production demonstration, not a Godot engine capture. Runtime capture belongs to integration evidence."})
assert results["checks"]["max_unity_stems_peak_below_minus_4_dbfs"]
# Integrated loudness and true peaks are FFmpeg measurements, not an assertion
# about perceived quality. The production stays conservative until human audit.
loudness=subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",str(REPORT/"audio_preview_combat.wav"),"-af","ebur128=peak=true","-f","null","-"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True)
(REPORT/"audio_loudness_ffmpeg.log").write_text(loudness.stderr)
results["checks"]["loudness_log"]="reports/phases/P03/audio_loudness_ffmpeg.log"
(REPORT/"audio_metrics.json").write_text(json.dumps(results,indent=2)+"\n")
media=sorted([*HERE.rglob("*.wav"),*(ROOT/"game/assets/audio").rglob("*.ogg")])
inventory=[]
for path in media:
    inventory.append({"path":str(path.relative_to(ROOT)),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
(REPORT/"audio_inventory.json").write_text(json.dumps({"schema":1,"assets":inventory},indent=2)+"\n")
rows=[]
for path in sorted((ROOT/"game/assets/audio").rglob("*.ogg")):
    rows.append({"asset_id":path.stem,"category":"original_music_stem" if path.parent.name=="music" else "original_synthesized_sfx","creator":"Project audio author via original local synthesis code","source_uri":"local:assets/source_audio/last_skuf_demo/render.py","license":"Original project-authored synthesis; no third-party media; public release requires project-owner authorization","attribution_required":"NO_THIRD_PARTY_MEDIA","commercial_game_use":"PROJECT_OWNER_AUTHORIZATION_PENDING","redistribution_allowed":"PRIVATE_PROTOTYPE_AUTHORIZED;PUBLIC_NOT_AUTHORIZED","evidence_path":"reports/phases/P03/audio_inventory.json","status":"ORIGINAL_LOCAL_AUDIO;PERCEPTUAL_REVIEW_PENDING"})
with (REPORT/"audio_license_rows.csv").open("w",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
print(json.dumps({"checked_unique_media":len(media),"stems":list(runtime),"state_peaks_dbfs":{k:v["sample_peak_dbfs"] for k,v in results["mixes"].items()},"crossfade_peak_dbfs":db(max_cross),"listening":results["listening"]["status"]},indent=2))
