# ASSET_PIPELINE — self-produced art, sounds and music

## Rule: no stock replacements as final
The assistant/Codex should **actively create** original assets, not just suggest the user source them. However if image/audio rendering tools or skilled human retouching are missing, output work orders and mark assets BLOCKED rather than labeling placeholders as production-ready.

## Pixel portraits and sprites
1. Read private character photo by ID from `assets/references/manifest.json` without uploading externally by default. Generate a draft concept using authorized image tooling if actually available (not guaranteed in a Codex shell).
2. Convert to deliberate pixel-art **by artistic redraw**, not automatic photo downscale/posterisation; palette, cluster edges, transparent layers. Tools to consider: **LibreSprite/Aseprite** (check availability/license), Krita, ImageMagick/Pillow, optional **Blender** for mockups/3D reference renders only; Blender is NOT required for normal 2D sprites.
3. Export individual PNG sprites (not cropped poster collage), JSON/.tres metadata: frame dimensions, origins, animations, fps, pivot points, palettes, asset-version, author/provenance. Multiple poses and expressive portraits validated for likeness.
4. Run structural check (dimensions, alpha, orientation, nearest filtering, sheet count); assemble in Godot and render test scene with screenshot. Art-reviewer examines resemblance and design; cannot infer likeness automatically from filename.
5. Repeat and approve a single Yakudza character pack before expanding to the entire cast. Beware Ellana/Elya and Timka/Olezhka photo mix-ups.

## Music/SFX
- Music for each hero: Yakudza heavy slightly ridiculous sub-bass; Gabar fast techno; Tega harsh industrial; Ryzhik breakbeat; Pasha frantic electro/acid break; Timka warm melancholy/athletic synth contrasted with absurd dog-walk theme; Olezhka driving disciplined electro; Kaban low ominous distorted drone. Original compositions preferred, third party only with documented compatible license.
- Adaptive stems: EXPLORATION, SUSPICION, COMBAT, CLEAR, plus transitions. Plan coherent tempo/key and seamless bar boundaries, no audio dropouts when restarting or entering another state.
- Author original music through available **licensed tools**: DAW (REAPER needs license evaluation, Ardour/LMMS free workflows), synth plugins with licenses, procedural synthesis via Python/scipy if appropriate. Command-line synthesis can produce genuine original loops, but inspect by listening and refine with music production skill; a waveform technically exists ≠ finished driving track.
- SFX: original recordings/synthesis for footsteps by material, impacts, weapons, wounds, ambient Vladikavkaz, engines, keypad, cybercafe, voice bleeps. Pure synthesized dialogue chirps can be made locally. Memey voice clips must be recordings from authorized speakers or licensed/generated material; avoid impersonating real friends without consent.
- No copyrighted Hotline Miami recordings/tracks/art; document external music author/license, allowed platforms, attribution, redistribution, AI-generated content conditions, file hashes in `licenses/ASSET_LICENSES.csv`.

## Software installation process
1. Inspect `godot --version`, `which blender libresprite aseprite krita ffmpeg python3`, package manager, headless/audio capabilities.
2. Present reproducible `tools/install_deps.sh` **proposal** or approved container actions, preferably user-local and pinned; tools can install automatically only when permitted by environment and owner, **never silently use sudo**, don't buy assets or incur API costs.
3. Install minimum tools justified by work: Godot, Python Pillow/audio packages, ffmpeg; LibreSprite/Krita for pixel polish; LMMS/Ardour for soundtrack, Blender only if a 3D task truly requires it.
4. If tools not available: record precise BLOCKED reason and proceed with unaffected tasks, no pretending completion.

## Private vs public
Keep `assets/references/` and bundled ZIP off public Git history unless explicit consent. Use private copy for artist agent, exclude from exports. Only ship original approved production assets with signed-off privacy/license manifests.
