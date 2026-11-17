# P06 original character art — candidates

Built-in `image_gen`, one own authorized private reference per identity, own accepted Yakuza portrait art as medium reference. Raw photographs are never copied here. Each selected generated master is preserved with its actual prompt, reference SHA (not photo), generated-file SHA and metadata. Final likeness/runtime/phase acceptance remains independent.

`pack_portraits.py` only finds clear grid gutters, extracts **whole** generated portraits, applies one shared nearest-neighbor scale/anchor per master, thresholds alpha and maps to a fixed43-color pixel palette. It does not read photographs or draw/reconstruct anatomy. Output cells160×160; manifest records every source box/native frame hash. Run `.tools/art-venv/bin/python assets/source_art/characters/pack_portraits.py <actor...>`.

Only five base expressions0–4 are used for new-character dialogue. Generated extras5–8 are explicitly unused: early independent Gabar review identified pose-wide jitter, so no animated speech/blinking is claimed. Existing accepted Yakuza P03 animation stays in its original path. New static portraits do not count as world animation or gameplay implementation.

World/actions/finishers and controls are subsequent tasks in planning/P06_TASKS.md. Current portrait assets do not make P06 PASS.

## Gabar WORLD source and native preview

`gabar/world_assembly_v7.json` records the selected exact direction rows:
DOWN v5a, LEFT v3b, RIGHT v4b, UP v6c. Independent source reports accompany them in
reports/phases/P06/art-preflight. This is approval to inspect movement in Godot,
not complete character/combat or P06 approval. Failed versions remain archived.

Direction source masters are 1536×1024, eight whole poses in a4×2 grid. The technical
packer preserves actual whole poses, applies nearest sampling/binary alpha/the
established palette, and never reconstructs limbs. LEFT/RIGHT use whole48×64
cells with sole58. DOWN/UP use one uniform whole-cell54×72 scale, fixedX=-3, and
ONE vertical offset for all eight poses anchored to idlefeet58. The latter preserves
the original steady head while feet travel forward/back in depth; a separately
shifted longest shoe on each frame introduced artificial body bob. Every placement
asserts zero opaque pixel loss. No anatomy/perspective warping or mirrored hands.

Reproduction (write sibling outputs to preserve review evidence):

```
.tools/art-venv/bin/python assets/source_art/characters/pack_direction_source.py gabar down --version v5 --output-version repro_down --native-width 54 --anchor idle
```

The assembled runtime
sheet copies the four reviewed native rows exactly; `assemble_world.py` checks
independent source dispositions, report hashes, native hashes and all32cell hashes.
`tools/verify_p06_world.py` runs an explicitly labelled art movement fixture with
actual key Input and records the viewport. It contains no hero combat/abilities;
it must never replace the complete per-character combat/control gates.

## Olezhka WORLD v2b

`olezhka/world_master_v2.png` is retained unchanged. The v1 RIGHT gait rejection,
strict alpha128 cell-boundary failure and alpha208/v2a matte rejection are preserved.
Only this exact master was independently accepted with one global alpha240 threshold;
this is not a new default for other characters. All32 whole cells use the same
192×256→48×64 nearest sampling, fixed palette and one idle anchor per direction.
No semantic masks, limb edits or lost post-threshold opaque pixels are allowed.

```
.tools/art-venv/bin/python assets/source_art/characters/pack_actor_sheet.py olezhka world --version v2 --output-version v2b --source-only --anchor idle --alpha-threshold 240
```

`adopt_world.py` verifies the independent source disposition, report/metrics/master/
native/frame hashes and copies an accepted32cell atlas into runtime byte-for-byte.
It refuses to overwrite existing runtime art. Source acceptance permits a native
movement preview; it does not approve combat, game feel or P06. Original source-only
metadata stays unchanged, while runtime metadata records the exact adoption chain.

The action packer's `--anchor reference` uses one standing column0 offset for all
eight cells of a direction, preserving actual fall/death depth instead of separately
centering each pose. Strict source-cell bounds remain mandatory; the rejected Gabar
action v1 is not packed by cropping its extended fist.

## Gabar ACTION source assembly v6

Selected rows: DOWN v4d, LEFT v2a, RIGHT v3d, UP v5c. Each has an independent
source-only report; runtime joins/contact/floor/muzzle presentation remain pending.
`assemble_character_actions.py` verifies both preserved source-review schemas,
exact report/metrics/master/native hashes and copies32 reviewed RGBA frames without
additional pixel changes. It refuses missing/failed reviews and existing outputs.
Source approval and32 cells do not authorize a playable character.

DOWN v4d applies one uniform45×60 whole-cell NN scale (all8 poses), fixedX1 and
standing-column0 anchor58. Other action directions use48×64, fixed column0 anchor.
The DOWN variant reduces the source's55px apparent standing height to51px against
world50px; real world/action joins must still be inspected in Godot.

RIGHT v3d preserves7 original whole cells and the newly drawn complete death pose.
The generated death figure crosses a nominal cell boundary but fits wholly within
a384px-wide rectangle. Its exact source rectangle738,512,1122,1024 is copied to
cell6 with a30px whole-pose translation; all52,174 alpha128 foreground pixels survive,
with no neighboring figure. The rejected nominal-cell selection v3c and failure
record remain archived. This differs from the too-wide original punch: no limb
is cropped, resized separately or reconstructed. Per-cell assembly provenance is
retained for all direction corrections.

## Gabar FINISHER source assembly v5

`gabar/finisher_assembly_v5.json` copies the four independently accepted direction
rows exactly: DOWN v3, LEFT v1, RIGHT v2c, UP v4. Source acceptance does not accept
world/action joins, contact timing, runtime weapon draw/stow or the full phase.
Columns0/6 are shared preparation/recovery; columns1–5 are category contacts,
column7 is the signature contact. Close unarmed/blunt/sharp body families are
reported as shared choreography, not three unique complete movement cycles.
Only the registered scene's equipment policy grants a usable category.

The UP environmental palm is intact but reaches native x0; its source gutter is
only4px. The source review records this margin reservation. Source images have
not been clipped or repainted to conceal it. All original rejected candidates,
network failure and selected corrections retain their own provenance.

## Clothing anchors for the actual combat actor

`annotate_character_sockets.py` writes metadata candidates and separate diagnostic
boards; it never changes a character bitmap. Maroon-palette overlap with hair
makes automatic component selection insufficient as artistic acceptance. One
explicit manual torso-coordinate correction (finisher source index19) is recorded
alongside its original palette candidate. The first diagnostic shows that raw
candidate; actual runtime overlay placement still requires ART review.

Each socket document binds actor, kind, sheet SHA and32 source-frame hashes.
The loader rejects malformed or wrong-sheet annotations. `CharacterPlayer`
requires a clothing socket for every referenced frame before it can be installed;
world-art previews can still inspect a source-only actor without sockets. Full and
Reduced reuse the same clean character drawings; the existing effects system
controls clothing blood. No duplicate `_reduced` drawings or new voice/audio media
are claimed.
