# P06 — bounded CharacterFrames component review v1

Статус: **COMPONENT_MAPPING_VERIFIED_WITH_MEDIUM_ROBUSTNESS_FINDING**. HEAD прочитан напрямую из Git metadata files, без Git commands: `e113fc784b6fdfcd2b624195eda22f8092e2ebd0`. Reviewer `/root/gameplay_review_p06` не запускал Godot/controller/tests/build/генерацию, не менял source. Записаны только эти versioned frames-review-v1.md/json в корневой gameplay-preflight. Это не playable hero, ability, native/art/feel или P06 approval.

## Что подтверждено

`character_frames.gd:5–8` задаёт отдельные layouts: world idle0,1/walk2–5/run6,7; action shove0,1,2/interact3/hit4/fall5,6/fire7; finisher shared windup0 + category contacts1–5 + shared recovery6, special contact7. Это корректно отделяет новый hurt4/interact3/two-drawing fall5,6 от legacy Yakuza hit3,4 и fall5,6,7 (`combat_player.gd:44–46`). Новый loader не меняет старый Yakuza loader; existing Yakuza не имеет новых file keys, поэтому combat_frames("yakuza") возвращает null.

Metadata validation (`:49–65`) проверяет Dictionary/schema/actor/kind, numeric frame_size48×64/pivot24,58, точный порядок четырёх directions, точные source-column maps,32 entries, source_cells32, entry direction/column/rect и row/column order. JSON numeric arrays принимаются через числовое сравнение, без ошибочного требования Vector2 в JSON. Loaded texture должна иметь384×256. AtlasTexture несёт character_id/source_kind/source_direction/source_column metadata. Loader возвращает SpriteFrames; не пишет actions/clocks/damage/score/scene authority. Playback FPS — animation metadata; будущий production actor обязан по-прежнему показывать authoritative action phase, а не выдавать damage из animation callbacks.

`combat_frames:27–40` требует world+action+finisher одновременно и возвращает null при любой недостающей sheet. Нет fallback на Yakuza, placeholder или готовый universal hero. Runtime Gabar action_sheet SHA256 действительно **f7974642a6efe5461a97d6fe786836498912545392503c8af196b466c9ae753d**, соответствует action.json. Metadata честно помечена REVIEWED_SOURCE_CANDIDATE_RUNTIME_PENDING. Полная Gabar finisher_sheet.png на момент проверки отсутствует; constructor отказ соответствует test assertion. Source approvals четырёх directions сами по себе не являются native gameplay approval.

## FRAMES-PF-01 — MEDIUM: malformed file/resource type не гарантирует чистый отказ

В `character_frames.gd:46` JSON catalog field сразу присваивается typed String, а в `:66` load(path) сразу typed Texture2D. `CharacterCatalog.entries` не проверяет тип world_file/action_file/finisher_file. Поэтому catalog с существующим ключом неверного типа либо valid resource другого класса может дойти до typed assignment error вместо заявленного null отказа. Valid текущий PNG path не затронут; это static failure-path finding, не воспроизведённый reviewer runtime crash.

Минимальное исправление: сначала получить Variant path_value и проверить String/nonempty; затем получить untyped/Resource loaded value, проверить `is Texture2D` и только после этого использовать размер. При желании проверять expected resource type до load. Добавить ограниченные negative cases malformed path value/nontexture resource, без мутации production catalog во время обычного test run. Эти checks нужны для утверждения полного fail-closed data contract, а не для допуска неизвестных assets.

## Evidence и границы тестов

Прочитаны character-frames-01.json/log: actual авторский headless **300/300**, exit0. Независимо пересчитаны оба source hashes и log hash: совпадают. Тест проверяет valid Gabar world/action clips, counts/loop/FPS/texture source/exact rect/source metadata; unknown/supporting/Yakuza/missing-combat paths. Он пока не проверяет malformed metadata/typed resource cases, положительный finisher_frames mapping или успешный all-three merge branch, поскольку финальной finisher sheet нет. Требование всё равно вернуть null сейчас верно; будущая финальная sheet требует положительного test/capture.

Прочитаны frames-world-regression-03/validation.json, commands.json, live.log и actual result.json: **70/70**, actual Input через headless preview, exit0, no movie/native exports и actual_captures0. Четыре evidence artifact hashes совпадают. phase_captures32 здесь означает coverage recorded phases в trace, не32 rendered screenshots. World preview прямо заявляет WORLD_ART_MOVEMENT_PREVIEW_ONLY и combat_abilities NOT_IMPLEMENTED_IN_THIS_PREVIEW.

Полный regression source inventory содержит596 entries: current-file hash проверка дала **594 совпадения и2 расхождения** (`assets/source_art/characters/README.md`, `assets/source_art/characters/assemble_character_actions.py`), пока шла разрешённая параллельная source-art работа. Нельзя утверждать, что весь WORK сейчас совпадает с run inventory. Рассмотренные runtime Frames и world-preview source совпадают с inventory; current action PNG/hash проверен отдельно. Поле source_unchanged=true относится к авторскому run interval. Shared CombatPlayer/CombatLab/CombatSystem hashes совпадают с прежним registered-policy evidence и не менялись. Новых runtime tests reviewer не выполнял.

## Обязательная последующая интеграция

Исправить typed-data failure path. После настоящей complete finisher sheet проверить все category/special mappings и combined construction; static hashes не заменяют native presentation. Подключить production CharacterPlayer с явным hurt/interact/fall/special mapping и правильным death hold; нельзя просто подставить новый atlas в legacy three-frame assumptions. Fire/interact/hurt single drawings остаются одиночными poses, two-cell fall не становится трёхкадровой animation. Shared finish windup/recovery не являются дополнительными уникальными drawings.

Реальные шесть abilities/actions, contact/cancel/cost/recovery и policy integration, four-direction native Input/actor-target reactions, once-hit/score/reset/reload, Full/Reduced, performance/FPS и Linux/Windows exports остаются pending. Ни completeness PNG atlas, ни300 structural checks их не доказывают.
