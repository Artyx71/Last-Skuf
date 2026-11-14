# Gabar native render remediation — independent ART review v2

Verdict: **ACCEPTABLE_GABAR_CONTROLLER_RENDER_FOR_CAPTURED_CONFIGURATION**. Close **GABAR-ART-DEPTH-01** against frozen native02 HEAD8f30222dd054ef7b605ecc654500aa2eb1a1ef3a. Actual UP contact hand/tool silhouettes now remain visible in the correct depth order across all six contact ticks and release. No remaining must-fix ART finding was observed in this bounded replay. This is component ART acceptance only: no full P06, full character/gameplay, real-time feel, audio quality or other hero approval.

Native01's major finding/report remain unchanged. Closure is based on new actual images and decoded movie, not only new tests, source intent or unchanged bitmap hashes.

## Direct defect closure

Viewed the new68PNG contact sheets/selected originals, all18 UP contact-hold movie frames, contact→recovery/release strips for all12 allowed category/direction combinations, and four continuous run→special→run strips. UP shows Gabar's crown, exposed RIGHT fist/club/pistol in front of the target according to floor depth. The enemy still overlaps where physically behind/above, and debug impact/query rings remain, but they no longer erase the category-defining hand/tool silhouette throughout contact. No held-to-live release depth reversal, ghost duplicate or unexpected frame remap was observed in the viewed transitions.

| Actual UP capture weapon/hand ROI[31,4,46,25] | Native01 exact source RGB visible | Native02 exact source RGB visible |
| --- | --- | --- |
| Unarmed | 40/84 | **84/84** |
| Blunt | 5/74 | **74/74** |
| Firearm | 32/79 | **79/79** |

These are opaque source pixels in the same anatomical region, including hand/skin/crown as well as weapon; no semantic weapon-segmentation claim is made. New PNG hashes: unarmed e4abca1725254c53393c3436be81e71f460c67544c1930d218179c1e357f6787; blunt2a2b9dd9d801e4ab9839d8726c58221f5c0f476686701558a8bdfa0c2876599d; firearmc26da9bc1d6a3f9b3f8452dec35210e152c5b21bb70fbc6bf8c47d7a0a66c8f0. The aligned source/native01/native02 diagnostic visibly corroborates these counts.

New movie independently confirms UP contact physics1038–1043/video1037–1042 for unarmed,1278–1283/video1277–1282 blunt,1518–1523/video1517–1522 firearm, then recovery at1044/1284/1524. Each complete six-frame hold was inspected, not just the convenient PNG. Hand/tool shape remains readable after first impact and through target motion, and release into the recovered stance keeps the intended depth. JPEG ROI errors improve across all18 samples, but movie is not claimed pixel-exact; lossless viewport PNG source matching is the exact-pixel evidence.

Required change is appropriately bounded: CharacterLab opts into y_sort before actor construction; CombatImpact snapshots each actor's floor-root sort_y and sorts a copied held-render array only when its host enables y_sort. The lifetime/physics array is not reordered. Hosts without y_sort keep their existing path. No source-art regeneration, watch/hand repair or procedural duplicate weapon is involved.

## Independent integrity and render-only comparison

Verified all **666** frozen source inventory entries and **79** listed native02 artifacts by SHA256: zero initial mismatches; completion mismatches `[]`. Compared prior652 inventory entries: only game/scripts/core/character_lab.gd and game/scripts/systems/combat_impact.gd changed. The14 added inventory entries include new unrelated source files; they are not retrospectively part of native01 and grant no Olezhka body/action quality approval. Current operationc788ed6782ef4e5cbccc00cbff99523f/exit0 is supplied task context; the reviewer did not operate the controller. Validation records194/194 checks,68actual PNG and source_unchanged=true.

All96 atlas-frame RGBA hashes again match their original directional source-native cells. World/action/finisher bitmap and socket metadata hashes are unchanged from native01. World `1fe0754e2d974d205ed21b02bd1bf2c712725263b9b87506f028f3e7f9419bdd`, action `f7974642a6efe5461a97d6fe786836498912545392503c8af196b466c9ae753d`, finisher `760d20224ff01be63ed225d2a8fe919a595bae717483193ae2e29d515391250b`. The manual finisher19 torso socket override[20,32] is retained; no palette-centroid/hair rollback occurred. Native01 report/decision/derivative hashes also remain intact: checked all its declared review artifacts, mismatches `[]`.

For **each** live and movie trace, independently compared all1769 corresponding samples against native01 in segment, position, velocity, animation, frame, action kind/elapsed/frame, damage count, score and visual_origin: **zero changed samples**. All37 contact contents, including contact positions, categories, direction, displayed frame and action elapsed, also match after excluding runtime target IDs/epoch and absolute tick origin. Thus the observed remedy is a rendering-depth change, not a hidden movement/clock/contact adjustment. Wall timestamps were intentionally not required to match separate runs.

Supplemental author evidence was read and hash-checked: Gabar-depth headless124checks and legacy effect regression log `RESULT passed=695 failed=0`; their fixed-file hashes match current native02 source. The headless Gabar validation header retains pre-commit HEAD9b6ac504 while its source inventory contains the fixed files; this is not mistaken for the frozen native02 source-head proof. These are author-run regression results, not tests executed by this ART reviewer or a new native Yakuza visual review.

## Render, temporal and settings coverage

Opened every actual640×360 PNG and inspected them through three own contact sheets.49/68 captures match all opaque source RGB pixels at the independently aligned render origin. Remaining masks encounter expected target overlap, camera/effect offsets, blood or inherited death modulate; no source bitmap mutation or new half-pixel resampling defect was found. DOWN enemy foreground overlap now follows floor depth when the target is below Gabar, rather than forcing every attacking limb above every target. Other-direction contacted poses, floor circles, clothing and target reactions remain readable in the sampled frames.

Decoded the actual MJPEG AVI: **1792frames,1280×720,60fps,29.866667s** content; movie process wall53.367s/live30.792s are distinct measurements. Source PNGs remain lossless; decoded JPEG crops are inspection derivatives. Calibrated16 phase probes across four directions: video index=physics tick−1 gives mean source-mask MAE15.07, compared with27.75/50.08 at adjacent offsets. Saved1157 chronological native-scale crops across212phase onsets, all finisher action holds and contact/release windows. Extraction JSON records exact frame/tick mappings. Selected strips/contact holds and all68PNG contact sheets were visually inspected; no claim of real-time playback or watching every saved derivative.

Since all sampled trace fields match native01, observed phase timing is retained: specials11windup/7contact/18recovery ticks with finite3.5px-per-tick sweep and return to held run; finishers16windup/6contact/14action-recovery plus one displayed recovery tick before idle. Each finisher commits on displayed frame1 at elapsed0.266667s; earned shove is a separate preceding action. Four continuous joins show no fixture reset/teleport between run, special and run. Fractional physics and integer presentation remain: maximum visual grid residue0.00001526px. Deliberate fixture resets between separate scenarios are not claimed as continuous transitions.

RIGHT static death hold, Full/Reduced overlays, body/tool/wardrobe identity and existing clothing blood placement remain coherent in the actual captures. The death color change is inherited actor modulation rather than changed source pixels. Full uses effects/stains and Reduced removes them; underlying art/phase clocks retain their verified mapping. Socket metadata is unchanged and its96-point source review still applies; this replay does not claim runtime rendering of every96pose. Debug rings are unchanged, continue to mark the target/contact fixture, and are no longer the major silhouette blocker.

## Limits retained

This closes the specific ground-depth/readability defect for captured native02. It does not create extra animation poses: shared0/6 preparation/recovery and similar category contact families remain honestly counted. Blunt/firearm tools appear at contact and disappear at recovery; no intermediate source drawings prove continuous draw/stow. That remains a presentation limitation under the existing three-pose contract, not newly certified continuous weapon handling.

Gabar ordinary ranged remains unavailable; training finisher authority remains unarmed/blunt/firearm. Unused sharp/environmental source art, including UP environmental zero-left-gutter reservation, is not granted runtime eligibility. Other five bodies/abilities, new Olezhka sources, arbitrary encounters, exports/Windows and full P06 are outside this acceptance. Audio streams/files are hash-verified evidence, with no listening/hearing-quality claim. Legacy non-opt-in hosts were supported by source gating and author regressions, not independently played here.

No Godot, controller, author process, Git command, build, generation, source edit or subagent was run. Only ROOT art-preflight reports/decodes were written. Native01 historical FAIL artifacts remain immutable; this version records the new bounded closure.

Supporting derivatives: gabar-combat-native-review-v2-UP-source-native01-native02.png; gabar-combat-native-review-v2-UP-all-contact-holds.png; movie-contact-release-01/02/03.png; movie-continuous-release.png; live-captures-01/02/03.png. Exact extraction and pixel/trace comparisons are in accompanying JSON.
