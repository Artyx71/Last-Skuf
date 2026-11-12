# TECH_ARCHITECTURE — Godot 4 / GDScript

## Target
- Godot 4.x stable (record exact version in lock metadata, verify Godot binaries locally). Desktop Windows + Linux with equivalent saves/input from vertical slice; no Electron/browser game.
- Core 2D top-down; recommend CanvasItem + CharacterBody2D; collision masks for actors, props, walls, attack volumes; fixed-timestep movement. Use nearest texture filter and integer scaling strategy; test screen sizes. Optional controller, remapping, graphics and gore options.
- Data-driven levels and dialogue. Resource (`.tres`) / JSON only where appropriate; strong validation and no evaluation of untrusted strings.

## Suggested project (Codex creates after init)
```
game/
  project.godot
  scenes/{bootstrap,world,actors,ui,levels,cutscenes}/
  scripts/{core,systems,actors,ai,ui}/
  resources/{characters,weapons,enemies,chapters,dialogue}/
  assets/{art,audio,fonts}/
  tests/{unit,integration,scenes}/
```
Core components/services:
- `GameSession` orchestration, `SaveService` versioned story flags, `ChapterDirector` nonlinear POV route, `DialogueDirector` portraits/emotion/typing and skip, `CombatSystem` deterministic damage rules, `EnemyBrain` readable FSM, `InteractionSystem`, `AudioDirector` adaptive music with beat-aware transitions, `VFXService` gore/VHS/accessibility, `AssetCatalog` stable IDs.
- Character definition resources: `actor_id`, display name, sprite frames, portrait expressions, move profile, attack inventory, special abilities, animation state. Keep ability implementation composable (don't fork entire controller per hero).
- Story event ID immutable across POV. Event ledger contains timestamp, prerequisites, branches and consequences. Save data includes version and rollback migration. No duplicative conflicting flags.

## Technical acceptance
- Initial headless smoke (Godot binary command checked against actual version): `godot --headless --path game --quit` (smoke only, not gameplay proof). For import check use `--editor --headless --path game --quit`; confirm command flags match installed Godot.
- Export use pinned export templates and `export_presets.cfg`; for CI Linux and Windows builds run export commands using installed templates and verify produced files execute where runner supports (Linux on Linux, Windows under authorized Windows runner or smoke evidence).
- Unit/integration test runner selected during bootstrap with pinned version (e.g. GUT if appropriate); tests include save-load roundtrip, story branching, hitbox collision, instant restart, gamepad/key input, gore toggle noninterference.
- Performance budget provisional: smooth 60 FPS target on ordinary laptop integrated graphics at 1080p integer upscale. Profile before claiming pass; no hardcoded exact hardware performance guarantees.
- Required per-phase: real build outputs, exit-code logs, scene screenshots, replay/recording where possible, checksum and artifact provenance.
