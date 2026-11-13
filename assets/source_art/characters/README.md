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
