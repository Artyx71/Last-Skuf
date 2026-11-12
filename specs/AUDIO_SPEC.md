# AUDIO_SPEC.md — АЫАЫ: Последний скуф

Version: 0.1 (approved creative direction; implementation parameters provisional)
Status: audio design decisions approved by project owner, production assets pending.

## 1. Approved requirements

- Music: distinct energetic electronic compositions chosen per mission, with the momentum and intensity expected of a fast top-down action game. All music must be original or demonstrably licensed for this project's distribution.
- Adaptive score: transitions across EXPLORE → SUSPICION → COMBAT → CLEAR / AFTERMATH, with musical continuity and no audible stutters.
- Dialogue: text-first; individual character-specific short nonverbal speech bleeps/vocal cues, **no full voice acting**. Real recordings are optional later and require permission.
- Soundscape: high-density, responsive SFX covering weapons, impacts, gore, footsteps by material, doors, broken glass, interactions, machinery, weather, cars, club ambience and street noise.
- Ossetian influence: selective, intentional use in certain tracks, locations and cutscenes, with knowledgeable review of musical/linguistic authenticity. No blanket ethnic musical clichés.
- Combat tone: soundtrack is serious and hard-hitting; humour comes primarily from characters and context rather than novelty music.

## 2. Character music direction

| Character | Theme concept | Arrangement & feel |
|---|---|---|
| Якудза | THE LAST SKUF | Heavy, slightly clumsy bass motif; low synth ostinato, lumbering pulse and sudden urgent accelerations when Жинька calls; still engaging rather than irritating |
| Габар | OPERATOR OVERDRIVE | Fast techno/electro, rhythmic precision, driving kick and machine-like arpeggios, clean build-ups |
| Тега | ANCIENT RAGE | Abrasive industrial electronics, distorted percussion, unstable syncopation, fatigue/anger tension |
| Рыжик | BREAK THE ROUTE | Strong breakbeat/big beat, swinging drum breaks and dance-battle movement |
| Паша | CAFFEINE RUNAWAY | Frantic electro/breakcore-adjacent bursts, energetic breaks, unexpected stop-start edits; readable beat for play |
| Тимка | FALLEN TITAN | Two connected arrangements: grand forceful retro workout motif in flashbacks, warmer relaxed synth motif in present; Jack-walk variation |
| Олежка | NEXT REP | Taut progressive electronic pulse that grows in layers as abilities develop; fragments from Gabar and family motifs |
| Кабан | FAMILY BUSINESS | Slow threatening sub-bass, minimal percussion, sparse cold motif; can mask connection to PRIME early |
| Эля | HOME AT 19:30 | Gentle intimate minimal synth texture, not an antagonist cue |
| Жинька / Эллана | INCOMING CALL | Short recognisable ringtone motif that can interrupt other tracks; avoid presenting her as responsible for criminal actions |

Character tracks are creative briefs only: no audio masters exist yet.

## 3. Adaptive music state machine

States: `EXPLORE`, `SUSPICION`, `COMBAT`, `CLEAR`, `CUTSCENE`, `PAUSE`. Music can employ synchronized stems (drums/bass/lead/ambience) or bar-aligned variants. Enter COMBAT at the next musically appropriate beat/bar when feasible; expose immediate danger cues without waiting for music. Cool down to SUSPICION/EXPLORE after threat-resolution delay, tuned in playtests. On death use a short stinger followed by rapid restart and beat-aligned return. Pause ducks/filters according to UI state. Cutscenes may override, but transitions must be intentional.

Prototype acceptance criteria:
1. At least one original licensed-for-use demo cue exists with a stem/variant for EXPLORE and COMBAT.
2. Repeated transitions and ten rapid deaths/restarts cause no clipped tails, stacked tracks or audible pops.
3. SFX stay intelligible over music: ducking/sidechain or selective frequency shaping when needed.
4. Dialogue UI lowers background music without silencing spatial cues essential for comprehension.
5. Volume controls: Master, Music, SFX, Voice/UI; persist settings.
6. Optional reduced-impact controls for harsh transients and tinnitus-like effects; avoid excessively loud sustained audio.

## 4. Event taxonomy and engine integration

Godot Audio Buses: `Master`, `Music`, `Music_Ambience`, `SFX`, `SFX_UI`, `Speech_Cues` (exact routing to be validated). `AudioDirector` listens to typed gameplay events and chapter data rather than hard-coded scene logic. Audio asset IDs and attribution live in an audio manifest. Spatial sound follows the 2D camera and attenuation; UI cues are nonspatial. Configure voice stealing/polyphony limits for repeated impacts, footsteps and gunshots. No uncontrolled per-frame sound triggering.

## 5. Dialogue cues and location sound

Use a bounded pool of short character-specific text bleeps/grunts, with rate limits and variation in pitch/timbre. Distinct recognizable motifs for Якудза's «АЫАЫ», Тега's anger, Паша's «ГАБАР КИПИТ», etc.; textual lines remain fully readable without sound. Avoid synthesizing real people's voices from photos. Use real spoken recordings only when voluntarily provided and consented to.

Location cues: CyberX (fans, keyboard/mouse clicks, chatter), Vladiкавказ streets (cars, footfalls, exterior ambience), hookah lounge (low rumble, ventilation, clinking), gym (plates, racks), stairwells (reverb, doors), PRIME facility (industrial humming). Distinct footwear and floor-surface footsteps where worthwhile.

## 6. Music asset & licensing policy

- First choice: original tracks composed/produced for game.
- Third-party tracks permitted only with written evidence granting needed use: downloadable desktop-game synchronization, reproduction, redistribution, commercial use if applicable, territory, term, derivative edits and distribution via storefronts. Check attribution, sublicensing and Content ID risks; keep source/license text, purchase receipt or permission attached to manifest.
- Do not use Hotline Miami soundtrack or other commercial tracks without appropriate license.
- Prefer editable master and loop-ready stems; distribute runtime-optimized audio (e.g. OGG), retain production originals outside game build.
- Review samples, packs and generated audio for usage rights, platform terms and possible infringement.

## 7. Delivery requirements

Per cue: `audio_id`, `chapter_id`, `character_id`, BPM, musical key if known, loop boundaries, state/stem mappings, runtime file, source/master path, license provenance, loudness target, priority and implemented status. Music should have loop points checked by ear. Avoid promising specific LUFS without a listening/mixing pass; set technical targets at first real audio milestone. Quality gates: listening QA with headphones/speakers, game capture, transition testing and platform export tests on Windows/Linux.

## 8. Roadmap and dependencies

P0: build AudioDirector and one demo track, transitions, bus sliders, footsteps/impacts and death/restart.
P1: per-character motifs and cutscene support; one distinct score for each vertical-slice sequence.
P2: original full soundtrack, location ambience, sound-effect variants, localization/Ossetian cultural review, final mix.

## 9. Open implementation decisions

Final track count, composers/tools, exact BPM, budget, desired licensed catalog, supported sample rates, save format, voice-bleep design and SFX asset sources must be resolved during production planning. Approved direction does not imply any music or SFX have been generated or licensed yet.
