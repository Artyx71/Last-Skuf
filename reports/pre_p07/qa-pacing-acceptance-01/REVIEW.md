What this change does: This fresh native run applies the previously approved H04 software-timing contract to eight registered contexts. It records actual injected requests, post-actor physics observations, changed post-draw states, Core contacts/deaths and a separate CH01 camera clip.

**Decision: PASS_COMPONENT — bounded native software-timing acceptance only.** No current must-fix finding was found in this run. Full H04/Readiness, campaign feel/duration, physical keyboard-to-photon latency and phase/P07 approval are not granted by this QA verdict.

The exact approved contract remains `4eb9b3f8a3aaa568a32c7b41ae1db80429f7f7f945a020513c206f0c1b23225a`; the original independent Lead decision remains `9966128fa846201420b9891d751e6f7da060871cdf819e5152337a488a5f5b85`. The recorded initial digests equal the unchanged final files. The actual dispatch arguments point to those files. The reviewed source checks the pins before each engine stage, after native and before final reporting. No threshold was adjusted after the result.

| Metric | Independently recomputed | Approved limit |
| --- | ---: | ---: |
| Input → accepted p95 | 17.914 ms | <34 ms |
| Input → changed render p95 | 18.876 ms | <60 ms |
| Controlled frame p95 | 17.093 ms | <24 ms |
| Controlled frame p99 | 17.567 ms | <33 ms |
| Death → control maximum | 16.722 ms | <1000 ms |

All five strict comparisons pass. I independently recomputed the nearest-rank statistics from raw timestamps, rather than accepting validation.json alone. The controlled frame series has958intervals;239idle-calibration intervals and setup/death-wait/readback segments are outside that budget. Intentional accepted→contact windup is separate (p95=199.696ms).

There are74true functional checks and48requests: four directional moves, melee and restart for each of eight contexts. All48bind to the same actor/context's first qualifying physics observation and first changed render state; eight outgoing and eight real incoming lethal Core contacts match the request/death records. Each restart starts from dead and returns to alive, playing and actual movement. No physical input device or special-ability response latency is inferred from these scripted Engine Input cases.

Canonical operation `a75a4330de35414ab87b8a143a28cce0` exited0 in54.344s and is consumed. I recomputed its argv hash and log hash, checked clean import/native logs and actual native flags (vsync disabled, max60, no fixed-fps/MovieMaker), and rehashed the pinned Godot binary. Source code is df7a6eeae8a8e1a440f8d8e35d84a17a20296290:616source hashes match before/after, the approved contract and current files. The guard/driver/house JSON helper match immutable QA02. Its17adversarial controls and13pure tests are reused by exact source hash, not claimed as newly executed here.

Recorded hardware equals the approved condition: Ryzen53600, GTX1050Ti, X11, Godot4.7.2,60Hz physics/max60, Window.size466×508. The separately captured render texture is640×360. The fresh clip has105actual PNGs (not the baseline's106),105decoded video frames and maximum PTS error0.498ms against saved capture timestamps. I viewed its first/middle/last PNGs and checked every capture path/hash. This is visual/rendering evidence; subjective continuous readability is handled by Gameplay/Lead.

**Scope correction to prior prose:** my QA01 sentence describing the authored clip as “AI disabled” was incorrect. The fixture disables NPCs before finishing dialogue; production dialogue resume subsequently re-enables enemy physics. The authored clip must not be described as NPC-frozen. The original immutable QA01 is preserved; `scope-erratum.json` records the exact source chain and correction. The separate eight technical timing contexts and excluded readback budget are unaffected. No runtime replay was requested merely to make footage match the erroneous description.

QA ran only read-only source/raw/statistical checks and ffprobe after the canonical worker drained. No QA engine/Controller, WORK/Git/state mutation, process signal, new export or audio listening occurred. This small controlled workload does not establish worst-case campaign FPS, universal input latency or full campaign playthrough.

Verdict: Ship this bounded acceptance evidence to Lead aggregation.
Not checked: physical keys/photons, subjective feel, full campaign pacing/duration, new exports/native Windows, full H04/Readiness/P07 admission.
