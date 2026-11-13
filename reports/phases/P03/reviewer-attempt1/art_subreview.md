# P03 — независимый art subreview, attempt 1

Reviewer: `/root/lead_reviewer_p03/art_review`; separate context от исполнителей root/runtime/art. Исходники read-only. Проверенный implementation commit: `a2c09cbf41c55330e4eed0e0cad16d7ffd9f9af1`; test/verification commit `92c8e96912f4db1731dbe3da46c3f99f097e59de`. На момент завершения проверенные art/runtime/socket paths не имеют diff от implementation commit. Полный phase/platform/audio gate принимает Lead.

**Рекомендация по art scope: PASS. ART-P02-01 закрыт.** Новых visual CRITICAL/HIGH/MEDIUM/LOW findings в проверенном scope нет. Это не новый human likeness approval: ранее утверждённое сходство P01 остаётся действующим, проверялись только ограниченные mouth/blink изменения и отсутствие изменений остального комплекта. Исторические ART-P01-01 idle jitter и META-P01-01 atlas-note discrepancy остаются прежним backlog.

## Проверенные источники и provenance

Прочитаны AGENTS, LEAD_REVIEWER, P03_TASKS, P02 PASS attempt2 и P03_HANDOFF, README, PHASES, PROJECT_GATES, DIALOGUE_SPEC, ART_BIBLE, SECURITY_AND_RIGHTS; runtime atlas/recipe/masks/prompt/generation metadata/license row и фактические изображения. Авторский report не принимался как доказательство качества.

Локально открыты actual `feature_master_v1.png`, six-frame runtime PNG и native captures. `feature_reference_board.png`640×640 состоит из четырёх точных nearest×2 копий approved neutral/angry160×160: собственная RGBA-проверка всех четырёх cells дала true. Metadata original image_gen output `/home/artyx/.codex/generated_images/01a1d1d2-7706-7642-ac55-8c4c7dda699b/exec-b4f5a317-be51-45d2-acb1-cd44b96973d1.png` существует и побайтно совпадает с сохранённым master. Recipe использует generated master1254×1254, nearest sampling/palette31 и сохранённые feature masks, без замены всей головы. Source-native и runtime motion PNG совпадают. В manifest есть отдельная P03 license/provenance row; public-release clearance не утверждается. Это согласованный проверяемый provenance, не экспертиза всей обучающей базы генератора.

## Пиксели и ограничение изменений

Собственная Pillow RGBA-проверка исходных PNG, без запуска author recipe:

| Cell | Changed pixels vs approved base | Outside saved ROI | Alpha |
|---|---:|---:|---|
| neutral rest | 0 | 0 | exact |
| neutral talk | 226 | 0 | exact |
| neutral blink | 223 | 0 | exact |
| angry rest | 0 | 0 | exact |
| angry talk | 232 | 0 | exact |
| angry blink | 204 | 0 | exact |

Runtime sheet480×320, cells160×160, alpha только0/255, palette31 opaque colors. Rest совпадает полностью, включая transparent RGBA. Отдельное сравнение `git show 4202a74:<path>` с текущими bytes подтверждает unchanged `portraits.png`, `portraits_past.png`, `world_sheet.png`, `atlas.json`, `action_sheet.png`.

Визуально оба mouth кадра действительно открывают небольшой рот: видна тёмная полость и сдержанный светлый/розовый акцент. Blink закрывает оба глаза; характерные брови neutral/angry сохраняются. Голова, волосы, нос, подбородок, одежда, телефон и silhouette неподвижны; нет масштабирования/bob вместо речи или новой photo plate. Hard clusters согласованы с approved base. Новой оценки private photo likeness не делалось и не требуется для неизменённой базы.

## Реальная runtime presentation

Просмотрены `native_dialogue.png`, `native_large_text.png`, `native_options.png`, `native_reduced_motion_vhs_off.png`, actual native MovieMaker AVI и соответствующие MP4 через плотную временную выборку actual frames. Это frame-based visual inspection реальной записи, без заявления непрерывного realtime просмотра. Собственная evidence `motion_video_samples.png` получена из финальных AVI: portrait crop320×320 на(40,364), nearest→160×160; сравниваются default и reduced/off.

Default: в0.000/0.125/0.250/0.375s neutral rest/talk действительно чередуется; в1.250/1.375/1.500/1.625s чередуется angry rest/talk. В11.750/11.875/12.000s neutral даёт rest/blink/rest. Head registration остаётся стабильной, движение читается как ограниченная речь и короткое мигание. Angry blink source валиден визуально; именно angry blink не был достигнут в этом быстром replay, поскольку clock сбрасывается каждой репликой до4s. Это предел выборки, не найденный runtime дефект.

Reduced-motion/VHS-off: actual second AVI показывает только neutral/angry rest во всех открытых временных выборках, включая моменты default talk/blink. Меняется нужное выражение, mouth/blink отключены. Независимая автоматическая классификация ROI по source templates на8FPS, исключая закрывающий лицо history panel interval2.8–3.5s, нашла только rest states во второй записи; глазами проверены representative pairs. В обычной записи встречаются оба talk и blink. Textbox/имя/подсказки не искажаются VHS, эффект ограничен миром ниже UI; native максимальный текст помещается в две строки. World и top-down actor остаются видимыми. Options controls помещаются в viewport. Временное перекрытие портрета открытым history panel ожидаемо.

## ART-P02-01 — закрытие carryforward

Фактически просмотрены все16 native PNG из `weapon_poses`:3 melee phases×4directions плюс4ranged. Для независимого увеличения actual rendered pixels создан `weapon_pixels_independent.png`: crop(270,198,350,274), exact nearest×4, строки down/left/right/up; колонки phase0/phase1/phase2/fire. Никакой ретуши или изменения gameplay art.

- Down: knife следует отдельной правой кисти на всех трёх фазах; телефон остаётся слева. Pistol начинается у вытянутой свободной кисти.
- Right: ошибочные windup0/recovery2 исправлены — knife теперь у ближней свободной кисти, телефон отдельно у груди; contact1 и fire также у правильной кисти.
- Left: windup0 не рисует knife через phone-hand, так как правая кисть скрыта; contact1/recovery2 показывают оружие у свободной кисти. Fire держится той же видимой свободной кистью. Это разрешённое phase visibility решение, не утверждение pixel-confirmed hidden wrist.
- Up: knife в0/1/2 и pistol находятся у правой кисти с rear layer; телефон остаётся отдельно в левой. Weapon не исчезает под полом: actor_body z1 и relative weapon layer−1 дают допустимую плоскость над ареной.

Нет прежнего weapon у стоп или привязки к телефону; all-phase motion и phone separation убедительны. Fixture действительно использует actual Input actions/actual player action frames/RenderingServer draw; `weapon_captures.json` содержит16unique phase_verified/saved rows. Source `combat_player.gd`, `combat_weapon_visual.gd`, `weapon_visuals.json` согласован с пикселями и visibility/layer. Contact timing не выводится только из этих stills: regression log показывает48/0, а Lead отдельно повторил48/0. Art subreview engine tests самостоятельно не перезапускал.

## Ограничения

Это art recommendation, не финальный P03 PASS. Аудиопрослушивание, final export/CI verification и общая decision принадлежат Lead. Native Windows human/runtime certification этим отчётом не создаётся. Public/merge/release/real-voice permissions не расширяются. Наблюдаемых art blockers не осталось.

## Hashes просмотренного evidence

| Path | SHA-256 |
|---|---|
| `game/assets/art/yakuza/portrait_motion.png` | `d4f63deecbc575249b29fa6c2d2c004b9f12dfcece87ab78becd21305c099217` |
| `game/assets/art/yakuza/portrait_motion_atlas.json` | `9989e5d52723aab3058bfde4824213a0193dcf1a1fe3fba97746f919b9b0bf72` |
| `assets/source_art/yakuza_portrait_motion/feature_master_v1.png` | `2739b12e03095a070eeb9cf923f9ce715d50454308590aaf24a8c2a5c8b9d1f3` |
| `game/resources/combat/weapon_visuals.json` | `8a22bd923c6151788329fc6991ebed258be318cdcd8f550ff9eb18cb9aa680d7` |
| `game/scripts/actors/combat_player.gd` | `bdd0810bd50a31820ccf80ad2190da5ae46551e65f97d970783ab4f412f6102a` |
| `game/scripts/actors/combat_weapon_visual.gd` | `9f02a8f3ddf83e8d97ce33bfa84217df7b320cc6be88d7a71ac5e0281d1c48b3` |
| `game/scripts/core/dialogue_audio_lab.gd` | `1c3561345f744625bf9bf5b82a724f8723dfe0be7f45ef66f305081ebee92bbd` |
| `game/scripts/ui/vhs_overlay.gd` | `3318264a1d724b3cd854cf5fe5e605b074b7896e27cb4d20f59871cc60c7d1f9` |
| `reports/phases/P03/native_dialogue.png` | `2c6a241ab84a79fd3463f40b9529363b5972e185e0d109e912209fa0766e893b` |
| `reports/phases/P03/native_large_text.png` | `4e896f6492ba614109cc00b80c6991dcfc3edbb154e8eb3f27844085db6913d4` |
| `reports/phases/P03/native_options.png` | `9cb720d6a6bf4650d6d26727f3a0fcc350aeab4002e9fdb5119a959a5663bbca` |
| `reports/phases/P03/native_reduced_motion_vhs_off.png` | `1d729e1b7495fdb2c1fcb77b344803a41959cca876bea06ecf8c89dbe0c93789` |
| `reports/phases/P03/dialogue_audio_replay.mp4` | `a5909a3ffeb8e1230402112b82f39f016d0c5b0a4f144a9b1c1bf0eb5ad0367e` |
| `reports/phases/P03/dialogue_audio_replay_reduced_motion_vhs_off.mp4` | `35d7f3711ddd4f2d834c4d148032bc4d58326801d226130606fa14129642dcf9` |
| `reports/phases/P03/weapon_poses/weapon_captures.json` | `b1f8f276ad6474e90f590d161f10098afe40d8d6ec10c1d627e10f5c6e3dbec1` |
| `reports/phases/P03/reviewer-attempt1/weapon_pixels_independent.png` | `88bd254dcab41de9645aca714842557029d1dacd9cb8da55df7d48496c459421` |
| `reports/phases/P03/reviewer-attempt1/motion_video_samples.png` | `98720ca377b43a00562a2436f1909d47e6c97b9e7dac45d89cf07e4518a555b8` |
