# P03 — dialogue/audio prototype

Prerequisite independent P02 PASSattempt2; source4202a74, evidence6dc34ad, decision325hashes. Не P04миссия/не21главы. Branch phase/p03-dialogue-audio, stackedPRпосле реализации. Owner approvals уже действуют: privatepush безrawphotos, image_gen всехфото; likenessP01approved; public/realvoices/merge/billing/sudo не разрешены.

| Task | Atomic result | Acceptance |
|---|---|---|
| P03-00 ART-P02-01 | Correct free-right-hand sockets vs phonehand, perphasevisibility/layer for occluded left0 | Actual3phases×4directions+fire4captures, unchangedP01PNGs, contact48regressions; independentartreview |
| P03-01 DL-01 | Short original Russian externalYakuza scene, stable speaker/emotion/localization/eventIDs; typewriter/reveal/next/history/seen-skip/autosave | Realinput tests inclhold/instant/no duplicate exit/action; native dialoguecapture visibleworld |
| P03-02 VIS-02 | Realneutral/angry mouth-open+blink pixelart (separate6frame sheet, approvedbaseimmutable), portraitswap, boundedVHS/reducedmotion | Actualfacefeaturechanges/sourceprovenance, nativevideo, readabilityon/off; staticPNGswapnotcalledtalk |
| P03-03 AU-01 | Original LAST_SKUF_DEMO,4synchronizedstemsbass/texture/drums/lead, BPM144/4beats/8bars/48000Hz; WAVsource+runtimeOGG+metadata | Actual13.333sloops, peak/seam/mixanalysis, realaudition/refinement; nooutside samples |
| P03-04 AU-01 | AudioDirector typed gameplayevents,4stateadaptiveprofiles, beat/bartransition, dialogue duck, pause/death/retry; synthesizedSFX+2nonverbalYakuza bleeps | Actualenginecapture,10rapiddeath/restarts no stackedvoices/pops; listening required, waveformnotlistening; mechanics/RNGnoninterference |
| P03-05 options | Versionedpersisted Master/Music/SFX/VoiceUI volumes; textspeed/instant, VHS/reducedmotion/reducedimpact; boundedpolyphony | Save/loadroundtrip, actualbusgains/UIcontrols, essentialsignalsreadable, nofakegoreclaims |
| P03-06 OPS/TEC | RegressionP00–P02+P03tests, actualreplay/audioevidence, separateLinux/Windowsbuilds andactualCI | Logs/hashes/executables, Linuxruntime+Wine label, independentLeadgate; missingperceptuallistening→scopedBLOCKED |

## Shared asset/API contract

Audio production owns game/assets/audio, assets/source_audio, licenses/audio provenance, reports/P03/audio*. Runtime owns new AudioDirector/DialogueDirector/options/VHS/lab/scripts/tests and explicit audioevent hooks in existing combat code; root owns socketdata/draw layer helper+phasecapturefixture, bootstrap/F3, verification/export/CI/state. Art owns separate portraitmotionPNG/metadata/source and reports/P03/portrait*; approvedP01files unchanged.

Audio manifest game/assets/audio/manifest.json schema1: music{id,bpm,beats_per_bar,bars,sample_rate,loop_frames,loop_seconds,key,stems:[{id,path}],profiles:{EXPLORE:{stem:gain},SUSPICION,COMBAT,CLEAR}}, sfx:{id:{path,bus,gain_db}}, bleeps:{YAKUZA:{variants:[paths]}}. Stems bass/texture/drums/lead share640000frames. Bus names Master,Music,Music_Ambience,SFX,SFX_UI,Speech_Cues; VoiceUI setting controls lasttwo, ambient→Music. Relativeassetpaths res://assets/audio/... . Purebleeps no friend'svoice model.

Portraitmotion game/assets/art/yakuza/portrait_motion.png480×320,160×160cells,rowsneutral/angry,columnsrest/talk/blink; portrait_motion_atlas.json withfps/masks/hash/source. Restmatchesapprovedpresent0/1exactly; sourceROI edits retainidentity. Runtime references actualfiles, never invisiblefallbackasfinishedasset.

Listening capability must be determined empirically; ffmpeg/Pythoncanrenderoriginalsound, filename/waveformexistence alone is not auditoryQA. Persistent runner absent; per-sessionephemeralCI cleanup mandatory. Newbuilds/reportsP03, preserveallP00–P02artifacts.
