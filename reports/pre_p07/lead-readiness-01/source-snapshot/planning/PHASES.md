# Delivery phases — controlled sequential gates

**Each completed major phase includes runnable Windows+Linux builds once vertical slice exists, actual reports and screenshots/audio artifacts where applicable.** Earlier bootstrap/art design may have an executable sandbox instead of full playable level. Do not claim full builds prematurely.

| Phase | Work | Acceptance gate |
|---|---|---|
| P00 Bootstrap | private workspace, Godot init, clean Git, CI, tool detection/pinning, reference manifest, agent setup | project opens headlessly, privacy check, review workflow functional |
| P01 Art prototype | Yakudza real pixel portrait and top-down sprite, native test scene, first playable movement | independent photo-likeness QA + pixel structure + screenshot, source art included |
| P02 Combat prototype | movement, melee/ranged test kits, hit detection, AI patrol/rusher/shooter, instant restart | deterministic hitbox/integration tests + combat replay; real weak-Yakudza route viable |
| P03 Dialogue/audio prototype | portrait swapping, bleep-based dialogue, VHS options, first **original** adaptive musical loops, SFX | audible verified loops/transitions, screenshots, no copied media; skipping safe |
| P04 Vertical slice | complete original first mission with authored tiles/story/music, death/restart, progression and Windows/Linux exports | playable, phase regression suite + smoke and human visual/audio reviewer report |
| P04G Combat/Gore polish | impact, original blood/decals, enemy reaction states, five base finisher categories, settings | specs/COMBAT_GORE_POLISH_SPEC.md; independent ART/GAMEPLAY/QA + Lead PASS; required before P07 |
| P05 Story infrastructure | event ledger, persistent flags, branch resolver, unlock/replay, 4 endings gate tests | complete reachable transition graph and automated simulations; no dead ends |
| P06 Character expansion | other 6 playables + 3 photographed supporting, abilities, portraits, animation QA | per-character independent likeness/art/controls signoff |
| P07 Campaign production | implement 21 chapter **slots** with real maps/dialogue/POV reveals, secret missions and choices | mission-specific functional and narrative checks; no fake filler levels |
| P08 Polish/release candidate | accessibility, performance, diverse PC resolutions/controllers, licenses, export validation, permissions | complete content checklist, no HIGH issues, signed-off release candidates |

## Microtasks and commits
Each phase splits into bounded tasks with explicit deliverables and tests. Use task branches/PRs per phase, small conventional commits (feature, fix, test, art, audio, docs). Reviewer is not allowed to fix code in same independent review session: issues go back to implementer, with evidence. Review loops finite; max retries configurable default 3 before BLOCKED and issue escalation.

## No skipping
P04 required before P05–P07 content expansion. Do not spend months building 21 chapters with placeholder assets; author a truly playable and recognisable vertical slice first.
