# ART_BIBLE — approved visual contract

## Canon
- Reference genre: early Hotline Miami — rough legible top-down pixel action, aggressive contrast, neon highlights, visual brutality, VHS transitions, punchy portraits to the side of world scenes. **Original compositions, silhouettes, layouts, UI and sprites only**.
- **Maximum likeness** to the 10 photos as achievable within pixel constraints; **all strongly caricatured** with their established features. Playable Yakudza 120 kg/170 cm in fiction; original photo may reflect a different era: no guessing from image alone.
- Vladikavkaz should be recognisable through **newly designed** districts, mountain views, yards, stairwells, CyberX-inspired game club, hookah venue; don't trace unlicensed signage/interiors or expose private addresses.
- Every production raster is true pixel-art: fixed grid, hard pixel edges, no photographic remnants, no bilinear blur baked into source; transparent backgrounds where needed. Nearest-neighbour upscale in engine. Manual QA at native resolution and intended screen size.
- Default technical proposal (must be validated in prototype): reference canvas 640×360; top-down actor nominal 32×48 or 48×64 depending on silhouette; tiles 16 or 32 px; portrait source region 160×160 (or a consistent alternative tested in dialog UI); palettes controlled per environment. **These are provisional**, not a ban on details.
- VHS, scanline, chromatic displacement, camera shake, bloom as opt-in postprocess; gameplay readability/high contrast and low-effects toggle required. Injured portraits and blood decals must remain consistent through scene state; gore toggle affects visuals only.
- Each playable character: 4-way idle/walk/running; interaction, melee, hit, down/death, and unique actions; portraits: neutral, anger, surprise, hurt, distinctive catchphrase. Directional frame counts authored in asset manifest, not guessed by importer.

## Character visual anchors
| ID | Visual identity / exaggeration | Standard wardrobe | Special animation |
|---|---|---|---|
| yakuza | thick black hair, calm gaze, broad short silhouette, absurd 'skuf' body exaggerated as **fictional** variant | black tee, phone | 'АЫАЫ', vape, breathlessness, Zhinka call |
| gabar | short dark-blond hair, rectangular glasses, robust shoulders | burgundy sweatshirt, watch | 'ЕБАТЬ ЕБАТЬ', coding, workout |
| olezhka | short hair, robust young training build, more grounded facial expression | dark training wear | adopts Gabar speech, reaction to kimono |
| timka | short swept blond/dark-blond hair, short beard, signature closed-lip smirk | black hoodie | leash/Jack, 'Я просто гасюсь', prime variant |
| ryzhik | side-swept dark hair, short stubble; baggy silhouette, tattoo references pending | baggy clothing | break spins, faceplant tooth gag |
| tega | extremely short hair, short beard, strong brows, **exaggerated** eye bags | grey hoodie | scream, tiredness, dream cannon |
| pasha | tousled volumetric dark-blond hair, stubble, lean short build, tattoos references pending | dark casual clothes | hyperactive, coffee, 'ГАБАР КИПИТ' |
| kaban | cropped hair, broad face and build, grey tee and chain | plain grey tee | disappointed stare, father scolding |
| ellana | long dark wavy hair, light outfit in original photo; caricature with **slightly enlarged nose** requested | photo-inspired light top | neutral, calling Yakudza |
| elya | long dark hair, calm soft face; preserve her actual photo features | photo-inspired dark/neutral clothing | with Timka/Jack, calm responses |

## Visual acceptance
1. Art reviewer compares each portrait to **its own** reference file, not generic archetype; reviewer flags mistaken identity.
2. Top-down view and portraits must match each other in hair, costume, colors, proportions.
3. Sheets must have consistent bounds, frame count/anchors and no inadvertent smooth pixels or background contamination.
4. No placeholders/AI look-alike portraits count as approved production assets; no photos inside production sprite sheets.
5. Pixel-level automation catches dimensions, alpha, animation export; human visual check is still mandatory for likeness and polish. If no authorized evaluator is available, BLOCKED, don't self-certify likeness.
