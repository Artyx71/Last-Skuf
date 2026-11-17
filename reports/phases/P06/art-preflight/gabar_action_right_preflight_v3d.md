# Gabar RIGHT ACTION v3d — independent source ART preflight

Verdict: **ACCEPTABLE_RIGHT_ACTION_DIRECTION_SOURCE_CANDIDATE** for native SHA256 `124fbbdcf15097347e878e298a0fa2946cb4ecdb341f75dde54c105ae4724a4b`. The previous death6 wrist-readability defect is resolved. No additional source correction is required for these eight poses. Acceptance is limited to this exact assembled master/native pair.

Read-only independent ART review of source candidates. Inspected assembled masters, exact native pixels enlarged with nearest-neighbor sampling, light/dark composites, and standing world/action comparisons. Independently checked source provenance, alpha components, cell margins, shared transforms and complete native reconstruction. No Godot, controller, Git commands, generation, source edits or subagents. All review derivatives are under this report directory. No runtime action atlas/metadata exists at game/assets/art/characters/gabar/action_sheet.png or action.json at review time. Pose drawings do not prove runtime timing, contact/cancel windows, transitions, damage, projectile origin, abilities or combat readiness. No full P06 approval.

## Complete-pose extraction and provenance

Independently flood-filled all alpha >=128 components in the raw v3b lower row with 8-connectivity. Four components were found: 69,621 pixels at [1194,554,1502,951], 74,216 at [49,557,320,960], 63,352 at [422,614,688,950], and death6 with **52,174 pixels at [754,746,1108,939]**. The whole 384×512 rectangle [738,512,1122,1024] contains exactly the death component's opaque pixels: no neighboring opaque pixel and no lost death pixel. Its full raw RGBA bytes equal assembled cell6, including transparent samples. The 30px source translation is of one complete pose; there is no body-part correction, resize, mirroring or pixel repaint in this assembly. Death's source margins within the selected rectangle are left16/right14/top234/bottom85px. Neighbor5 ends at x688, neighbor7 starts at1194, outside the selected window.

All seven other cells equal their original v3 source rectangles byte for byte; source-file, whole-cell RGBA and assembly hashes match. New generation prompt/input/output hashes match metadata. The nominal-cell v3c strict-bound failure remains preserved, with no native v3c created; this review does not reinterpret that failure as a successful pack. V3d succeeds through a different, explicit complete-pose rectangle.

## All eight poses

| Index | Actual drawing / finding |
| --- | --- |
| 0 | Cocked melee windup; visible raised near RIGHT arm bare; far LEFT guard watch coherent. |
| 1 | Full rightward punch; near RIGHT wrist bare; far arm mostly occluded. Complete fist inside cell. |
| 2 | Retracted recovery guard; near RIGHT bare, far LEFT guard watch coherent. |
| 3 | Open rightward reaching hand; near RIGHT wrist bare; fingers and full arm intact. |
| 4 | Hurt curl/guard, recognizable glasses; visible LEFT guard watch belongs to the far/turned arm. |
| 5 | Low kneel/palm-supported knockdown; grounded near RIGHT forearm bare, far LEFT guard watch present. |
| 6 | Static curled death hold; exposed near RIGHT sleeve-to-forearm path reads bare, far LEFT wrist hidden. No duplicate band. Hair/head cover most glasses naturally. |
| 7 | Rightward pistol; visible near RIGHT trigger wrist bare; far support wrist occluded. Muzzle and plausible overlapping grip intact. |

The correction in6 changes the exposed forearm contour as one authored pose. Bare near-arm reading is now supported by the visible sleeve/forearm connection rather than guessing handedness from screen position alone. This is an honest static death drawing; no extra fall/death animation is implied.

## Native contours, camera and root

Reconstructed all eight 48×64 outputs independently from full 384×512 cells: NN48×64, common DX0/DY+2, fixed standing reference0 bottom58, alpha128 and palette43, no dither. Output RGBA is byte-exact; zero opaque placement loss. All source cell bounds are strictly internal. Native has37 opaque colors and alpha only0/255. Light/dark views show clean outlined contours without the cloudy master preview background becoming opaque.

Standing0 bounds [6,7,40,58], height51px, match accepted world RIGHT idle height51 and camera/proportions. Glasses, swept reddish hair, burgundy shirt, dark trousers and light shoe trim preserve Gabar identity. Death6 bounds [2,31,46,55], so both horizontal margins are2px and last opaque row54. Its bent silhouette sits three pixels above standing bottom58; this is authored spatial extent under the same transform, not a per-pose floor snap or detected crop. Ground/shadow and knockdown→death/world→action joins must be judged in the forthcoming native presentation; this source review does not certify those joins.

Supporting diagnostics: gabar_action_right_v3d_light_dark_4x.png; gabar_action_right_v3d_world_standing_fire_6x.png; gabar_action_right_v3d_death6_whole_source.png. Full bounds/provenance/component results and file hashes are in the accompanying metrics/decision JSON. Earlier raw-v1, RIGHT-v3 and strict v3c failures remain unchanged.
