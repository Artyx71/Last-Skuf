What this change does: It adds a second technical map with real Input routes, two doors, all registered player bodies, and targeted AI checks. It changes test fixtures, not the production combat or room router. Expected load is one canonical serial diagnostic, not concurrent game servers.

## Must fix

1. **The first legacy body stops the walking suite** (`tools/fixtures/p07_second_pilot.gd:112`).
   - What this is: The body/art check reads `player.actor_id` before its conditional value comparison.
   - Problem: Legacy `CombatPlayer`/`YakuzaActor` has no such field. Actual log reports this script error at the first context. None of the eight walking contexts completes. The unfinished host is not disposed before the AI suite starts, so later path/LOS failures are not clean evidence of a router regression.
   - Fix: Check the legacy script/class separately; read actor_id only on CharacterPlayer. Cleanly stop/clean the suite on an unexpected coroutine error.
   - If we skip it: A new pilot never exercises its advertised player routes and mixes invalid test worlds.

2. **The coverage flag claims routes that never ran** (`p07_second_pilot.gd`, output dictionary).
   - What this is: JSON sets seven_heroes_eight_registered_contexts=true unconditionally.
   - Problem: Actual result has only three AI rows and zero context rows after the script error. The outer Python validation correctly reports FAIL, but this separate coverage claim is still false.
   - Fix: Derive the completed context set/count from actual rows and their outcome, and fail missing coverage.
   - If we skip it: Later reports can mistake an incomplete diagnostic for eight successful player routes.

Actual evidence: canonical8856… receipt1, argv/log hash verified. Fresh import exits0; pilot exits1 with26/36 checks and10failed AIchecks. Game/tools inventory613 records is identical before/after. The three fixture/tool hashes match frozenab7 source and saved runtime. No native renderer run occurred. Failed evidence is preserved here; newer2e035 source is a separate review.

Other source limits: Walking drive deliberately reissues Engine Input while steering; it is not physical keyboard/focus or held-key-loss evidence. The three movement probes use explicit setup positions outside walking claims. AI stun/death checks call receive_hit directly and qualify state priority, not new Core incoming-contact proof. Peer masks ignore each other as P06; no crowd avoidance claim is made. Native targeted AI uses only rusher while all three share the simultaneous route. These are honest bounded limits, not demands for a campaign or new engine run.

Verdict: fix 1 and 2 first.
Not checked: reviewer ran no Godot/Controller/process worker, no native input/FPS, art, audio, campaign or full H02/Readiness. The review used the ponytail-review skill and read connected production actors, router/host, reset flow, inherited Python inventory and actual logs.
