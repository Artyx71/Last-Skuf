# P06 original character art — candidates

Built-in `image_gen`, one own authorized private reference per identity, own accepted Yakuza portrait art as medium reference. Raw photographs are never copied here. Each selected generated master is preserved with its actual prompt, reference SHA (not photo), generated-file SHA and metadata. Final likeness/runtime/phase acceptance remains independent.

`pack_portraits.py` only finds clear grid gutters, extracts **whole** generated portraits, applies one shared nearest-neighbor scale/anchor per master, thresholds alpha and maps to a fixed43-color pixel palette. It does not read photographs or draw/reconstruct anatomy. Output cells160×160; manifest records every source box/native frame hash. Run `.tools/art-venv/bin/python assets/source_art/characters/pack_portraits.py <actor...>`.

Only five base expressions0–4 are used for new-character dialogue. Generated extras5–8 are explicitly unused: early independent Gabar review identified pose-wide jitter, so no animated speech/blinking is claimed. Existing accepted Yakuza P03 animation stays in its original path. New static portraits do not count as world animation or gameplay implementation.

World/actions/finishers and controls are subsequent tasks in planning/P06_TASKS.md. Current portrait assets do not make P06 PASS.
