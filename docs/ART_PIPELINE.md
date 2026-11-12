# ART_PIPELINE v0.1

## Source → production asset
1. Immutable source photo in `assets/references/characters` (restricted).
2. Artist-created original concept portrait and palette swatches in `assets/concepts` (future).
3. Art-direction approval for recognition, anatomy, pixel density and tone.
4. Production transparent PNG portrait + expression variants and top-down sprite directions.
5. Pack spritesheets + machine-readable frame atlas; verify frame grid, alpha, pivot, silhouette, collision bounds.
6. Import Godot resources/AnimatedSprite2D; snapshot and in-engine runtime tests.

## Initial technical targets (proposals; validate in prototype)
- Logical canvas 640×360, nearest-neighbor scaling, letterboxing.
- World tiles 32×32 px; player sprites 32×48 to 48×64 px depending on silhouette, with fixed foot anchors; no indiscriminate stretching to equal height.
- Dialogue portraits ~192×192 logical pixels, palette-limited pixel art, transparent; shared eye-level and framing.
- Animations: idle, walk in 4 directions, attack, hurt, down, interact, signature action; 6–10 FPS initially where pixel readability works.
- Portrait emotions: neutral, talk (2–3 frames), angry, surprised, smirk/laugh, character signature.
- Formats: editable source when available (Aseprite or layered project), exported PNG sprite sheets, atlas JSON, Godot `.tres` resources.
- Music: original licensed-for-project stems/loops, looping metadata, per-scene intensity layers and mixing rules.

## Acceptance checks
- Portrait recognizability confirmed against the user's corresponding reference.
- All sprite directions and frames use same coherent pixel grid and color/shading style.
- No baked photo backgrounds; no unwanted extra limbs; clean transparent alpha and consistent anchors.
- Gameplay animations respond to controls; portraits animate with dialogues.
- Avoid copyrighted imagery/sounds/sprites from Hotline Miami, and avoid public distribution of private photos without permission.

## First asset milestone
Produce Yakudza (old + stylized present) front-facing dialogue portrait with 5 expressions, plus idle and walk sprites in 4 directions. Verify inside a Godot prototype before scaling output.
