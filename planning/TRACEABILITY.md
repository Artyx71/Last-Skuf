# Traceability / required specifications

| Req | Origin | Acceptance |
|---|---|---|
| VIS-01 | approved art | photo-linked custom true pixel art for all ten, stylized grotesque, native pixel audit |
| VIS-02 | approved art | VHS/transitions, injured portraits, low-effects and gore toggles |
| MAP-01 | approved art | recognisable fictionalised Vladikavkaz locations drawn from own references |
| GP-01 | approved gameplay | lethal hard combat, instant restart, character-specific attacks |
| GP-02 | approved gameplay | weak Yakudza and viable non-power escape levels |
| GP-03 | approved gameplay | varied enemy AI, bosses, ranks, combos and secrets |
| ST-01 | approved story | seven POV, non-linear 21 slots, PRIME/Kaban reveal, WIFE CALLING main |
| ST-02 | approved story | persistent branching affects gameplay routes and endings |
| DL-01 | approved dialogue | natural profanity, rare verified Ossetian, distinct voices and animated portraits |
| AU-01 | approved audio | original/licensed musical tracks and adaptive stems, per-hero themes, rich SFX |
| TEC-01 | approved technical | Godot4 GDScript, Windows/Linux, tests/screenshots/reviews/atom commits |
| OPS-01 | newest request | reviewer obtains artifacts automatically, finite FAIL→FIX→REVIEW, PASS→NEXT, no user report forwarding |
| PRI-01 | safety | photos private, permission/license checks, fictional disclaimer |

At kickoff derive atomic test IDs `T-REQ-###` for each and reference them in phase reports; add failed tests to issue tracker.

## Дополнение Combat & Gore

COMBAT_GORE_POLISH_SPEC IDs IMP/ART-G/AI-G/FIN/OPT-G/QA-G/PERF-G/REV-G → AUTOPILOT queue P04G → reports/phases/P04G/ (P04G PASS и merged; исторические evidence сохранены). FIN-02/AI-G01/IMP-01 являются hard prerequisite P07; character variants связаны с P06.


P05 ST-01/ST-02/TEC-01: `story_registry_test` — IDs/DAG/POV/availability; `story_state_test` — schema/migration/rollback/replay; `story_graph_test` —6344paths/declared partitions/D01–D06/routes; `story_integration_test` —recoverable CH01 completion failure; `--p05-replay` — actual Input UI/CH01/retry/checkpoint/skip, отдельный process reload. Trace/defaults: reports/phases/P05/attempt1/design.md. Ни одна будущая scene/концовка не объявляется готовой.
