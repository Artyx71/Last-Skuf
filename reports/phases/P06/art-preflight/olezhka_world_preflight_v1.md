# P06 — Olezhka world source preflight v1

**FAIL_RIGHT_OPPOSITE_LEG_PHASE_READABILITY.** Actual RIGHT row не даёт читаемого обмена near/far ведущих ног у contacts2↔4 и run6↔7. Это ограниченный source ART blocker; identity, DOWN/UP и большая часть LEFT пригодны для дальнейшего preview. Уникальные32 hashes не доказывают правильный цикл. Полного32pose source/world/runtime/P06 approval нет.

Ревьюер `/root/art_review_p06` просмотрел own private Olezhka photo локально, own approved portrait, actual master1536×1024, native384×256/inspection3x, четыре native contact/run pairs8x и side walk4strips4x. Raw photo не копировалась в reports. Godot/controller/Git commands/generator/source edits/subagents не запускались; записи только разрешённый art-preflight.

Native SHA `ecd7ebbfe685031b1560c51c6a5b9c225a42443f59ff5dddcc102fde5695e378`; master SHA `69b39853cfcd9f29789cb08028a0f833ce28a6e8ed59e4952414b0d439ba5ec5`. Manifest CANDIDATE_SOURCE_NOT_IN_RUNTIME; runtime Olezhka world_sheet отсутствует при inventory.

## Concrete must-fix RIGHT

В actual native RIGHT contactA2 blue/grey-highlighted NEAR leg ведёт вперёд screenRIGHT, тёмная FAR leg остаётся позади слева. ContactB4 сохраняет ту же foreground bright shin/front shoe, dark back leg. Руки взаимно меняются, но leg/value/occlusion роли не становятся противоположными. Run6/7 повторяют тот же highlighted near-leading forward-right family при изменённых руках и backknee. Master показывает вариации hips/knees, поэтому это не утверждение о byte-duplicate или одинаковом скрытом rig; именно final48px anatomical phase readability не проходит.

Bounded исправление: authored whole-pose RIGHT B contact4 и run7 с clearly dark FAR leg leading screenRIGHT, NEAR brighter leg trailing screenLEFT, сохранёнными camera/body/identity и reciprocal arms. PassingB5 должен согласовать новую опорную/проходную ногу. Это целые позы, без процедурной дорисовки частей/перекраски/automatic mirror. Сохранить текущий v1 FAIL, проверить новую версию и все затронутые нетаргетные poses. Остальные три направления не требуют перегенерации по данному finding.

Evidence: `olezhka_world_v1_right_phase_pairs_8x.png`, `olezhka_world_v1_right_walk4_4x.png`. Не переносить Gabar template approval на новые redrawn Olezhka limbs.

## Остальные gait directions

DOWN clearly меняет нижнюю leading boot screenLEFT/anatomicalRIGHT в2/6 на screenRIGHT/anatomicalLEFT в4/7, с reciprocal arms. Passing3/5 различают опорную ногу и bent knee, заметно уже contacts. UP away-view даёт противоположные lifted forward knee/trailing sole роли вA/B; нижний visible trailing shoe не считается leading leg, так как движение от зрителя вверх. Обе UP passing позы отдельные, runA/B сохраняют opposite leg phases.

LEFT A2/6 имеет светлее blue-highlighted near leg впереди screenLEFT; B4/7 показывает более тёмную forward leg с другой hip/occlusion связь и противоположными руками. Это читается как near/far exchange лучше RIGHT и не даёт самостоятельного must-fix. Контраст B ниже, поэтому future actual native playback должен подтвердить читаемость при cadence; source-only review не обещает animation feel. Passing3/5 уже contacts и меняют bent knee/weight.

## Ликость, камера, одежда

Молодое чистое roundish лицо, плотное athletic телосложение, короткая коричневая crop-причёска и тёмная training tee/pants/trainer outfit узнаваемо продолжают own approved Olezhka portrait, не Gabar. Очков, часов, jewelry/tattoo, букв/crest/weapons не найдено. Photo и portrait association правильные. Pixel crown выглядит более текстурной/объёмной, чем короткий crop на фото; это minor stylization в overhead chibi, длинного Gabar swept quiff нет, отдельный обязательный likeness fix не запрашивается.

Crown/shoulder tops и короткие foreshortened legs соответствуют принятой overhead camera family. Idle heights DOWN51/LEFT52/RIGHT53/UP54; нет прежнего disproportionate45px front shrink или platformer proportions. Headtops DOWN `[7,7,7,7,7,7,8,9]`, LEFT `[6,6,8,7,8,7,8,8]`, RIGHT `[5,5,6,5,5,4,6,6]`, UP `[4,4,4,4,4,4,4,4]`. Walk bob ≤2px, run≤1px, wholehead packing pogo не найден.

One fixedY per row: DOWN/LEFT/UP0, RIGHT−1; все клетки whole192×256→48×64 NN, palette/alpha128. Standing idle sole58; depth strides DOWNexclusivebottomдо63/UPдо61, side soles57–58. Ни одна opaque native pixel не обрезана; foot/root floor placement и state transitions требуют actual world fixture после source correction, не оцениваются по32 hashes.

## Integrity и scope

Независимая реконструкция всех32 целых cells + shared palette/alpha/fixedrowtranslation дала exact RGBA совпадение. Source rects, clear alpha128 margins, source/native bounds, perframe hashes, manifest/master/prompt/metadata/input role hashes совпали. Native alpha0/255,35 opaque colors,32 unique frames. No raw photo input in generation metadata; inputs own portrait identity + own Gabar pose/camera template. Whole-pose provenance соответствует ограничению, процедурная anatomical reconstruction packer не выполняет.

Metrics/evidence: `olezhka_world_preflight_v1_metrics.json`, четыре `olezhka_world_v1_{direction}_phase_pairs_8x.png`, четыре `olezhka_world_v1_{direction}_walk4_4x.png`. Сами32 source drawings сохранены как candidate; следующий шаг ограничен исправлением RIGHT B gait, затем source rereview и actual movement evidence. Runtime/hero combat/P06 approval не выдаётся.
