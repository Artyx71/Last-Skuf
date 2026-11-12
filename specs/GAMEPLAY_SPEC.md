# АЫАЫ: ПОСЛЕДНИЙ СКУФ — GAMEPLAY SPEC v0.1

Status: Approved direction, implementation details proposed; not yet prototyped.

## Approved requirements
- Desktop top-down 2D action in Godot 4 with a fast, lethal, instant-retry loop and original art/audio/code.
- Playable protagonists have distinct movement, melee/ranged tools and abilities; no single universal combat kit.
- Yakuza is genuinely weak and clumsy; his missions favor escaping, improvised tools, distractions, lucky accidents and route planning. This is not a power fantasy.
- Personalized weapon/ability styles.
- Graphic pixel violence with an option to reduce gore, dismemberment, wounded portraits and violent effects; toggle must not affect mechanics, difficulty, scoring, or hitboxes.
- Enemy variety: patrols, guards, rushers, ranged, specialists and unique bosses.
- Author-controlled nonlinear chapter order and multi-perspective retellings, similar as a structural influence to Hotline Miami 2 (all content original).
- Hardcore default: lethal encounters, fast death and instant reload, minimal handholding.
- Rich metagame: secrets, combo and grade scoring, achievements, interactive cutscenes, bosses.

## Design consistency / constraints
1. **Weak Yakuza vs hardcore:** all Yakuza stages require at least one viable no-conventional-combat path and fair telegraphed threats. His movement must be responsive to inputs even when animation portrays clumsiness; avoid random unavoidable failures.
2. **Personal equipment vs encounter balance:** maintain per-character level validation and a matrix of threats, counters and available equipment. Never assume access to another character's weapon.
3. **Nonlinear story vs clarity:** all missions have a canonical timeline timestamp, played-order index, protagonist, POV, reveal, prerequisites, and a recap on replay. Reveal gating prevents spoilers.
4. **Gore options vs readability:** reduced gore retains hit confirmation and enemy state via non-graphic effects. No gameplay information hidden by gore setting.
5. **Frequent death vs cinematic pacing:** checkpoints only at clear sequence boundaries, instant retry restores deterministic enemy placements and encounter RNG seed. Seen dialogue can be fast-forwarded; story moments do not replay unskippably on every death.
6. **7 protagonists vs scope:** implement one vertical slice first; extend mechanics using data-driven ability definitions and state machines, not branches by character in central controllers.
7. **Scoring:** separate grade/combo scores from canonical story outcomes and death counters. Avoid rewarding violence when objective is evasion; score each mission's intended style.
8. **Controls:** configurable keyboard/mouse, controller support planned; pause and accessibility settings; hit feedback remains legible with VHS disabled.

## Proposed character identities (not yet final-approved)
- Yakuza: survival, improvised distractions, low endurance, inept attacks; call interruptions; escape-first objective.
- Gabar: fast accurate close combat, environment/technology interactions, planned execution.
- Pasha: high mobility, chaotic risky ranged play; no automatic guaranteed self-destruction.
- Ryzhik: breakdance-based evasive movement, close-range crowd control.
- Timka: in present avoids conflict, in flashbacks powerful physical style; Jack companion in select levels.
- Tega: traps, tactical positioning, loud stun/taunt mechanic; sleep-deprivation visuals do not obstruct mandatory cues.
- Olezhka: straightforward balanced skillset with gradual progression and brother-centric missions.

## Proposed first vertical slice
One Yakuza level with original pixel art assets, top-down navigation, interactable doors/props, 2-3 enemy archetypes, stealth/escape route, failure and instant retry, one animated portrait dialogue, phone interruption, score and accessibility gore toggle, music and adaptive SFX. Not a full mission from the 21-chapter plan until story and art lock.

## Acceptance tests (initial)
- Death-to-control retry target < 1 s on development hardware after assets cached (performance target, verify empirically).
- Both gore modes preserve identical enemy behavior, damage, hitboxes and victory conditions.
- Yakuza slice can be completed without defeating every enemy.
- No required random event makes completion impossible after an otherwise correct input.
- Dialogue skip/fast-forward works after first viewing and does not corrupt story flags.
- Replaying a chapter cannot modify previously locked canonical events unexpectedly.
- Each unique character's moveset covered by automated or scripted smoke checks when implemented.
- Hit effects and enemy outlines remain readable with VHS enabled or disabled.

## Out of scope for this stage
- Exact frame data, combat damage, weapon lists, AI parameters, scores and chapter difficulty curves. Define after prototype playtests.
- Final rating targets or guaranteed asset quality prior to art review.
