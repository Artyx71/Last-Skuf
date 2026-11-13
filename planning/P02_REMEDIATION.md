# P02 attempt2 — fixes after independent FAIL

Authority: reports/phases/P02/decision-attempt1.json, source1786633/evidence021c126. Reviewer-owned immutable snapshots contain66originaloutputs and65sourcehashes. No P03 until independent PASS.

| Ticket | Owner | Concrete change | Acceptance |
|---|---|---|---|
| CMB-P02-01 HIGH | gameplay | One physics pose/contact clock; frame0 wind-up,1contact,2recovery; cancel on death/reset | Native Input bothkits×4directions, damage/stun absent on0, present on1, onehit; original reviewer probe; wall/miss/restart regressions |
| ART-P02-01 MEDIUM | gameplay | Per-frame/directional real hand+visual muzzle sockets, layer ordering/projection | Actual melee/ranged screenshots all4directions, held weapon at wrist; projectile begins at visualmuzzle |
| ART-P02-02 MEDIUM | art | Reauthor shooter idle head/torso alignment, no uniformscale disguise | NativePNG/sourcehashes, actual8FPSstartstop oncommonpivot640×360; P01PNG untouched |
| ART-P02-03 MEDIUM | gameplay | Clear defeated cue/disappearance instead of tint-frozenwalk | Real killcapture, deadstate unambiguous, reset restores fullvisualstate deterministically |
| OPS attempt2 | root | Separate validation/buildpaths, fresh exports/replay/actualCI and independent rereview | tools/verify_p02.py --references --output reports/phases/P02/attempt2 --build-output build/P02/attempt2; CI + artifactdownload + ephemeralcleanup; reviewer decisionattempt2 |

Original reports/P02 files and build/P02/{linux,windows,combat.avi} are historical attempt1 and remain. New evidence goes under attempt2; latest STATUS/NEXT_ACTION/state link current attempt. Publicrelease/merge/realvoices/billing/systeminstall not authorized. Source photo inputs remain ignored. Owner P01art acceptance remains valid for unchanged approvedPNGs.
