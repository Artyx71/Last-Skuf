# P06 — Olezhka world source preflight v2a / alpha208

**FAIL_NATIVE_CONTOUR_FRINGE.** Authored RIGHT B gait correction читается, но threshold208 сохраняет broad brown/olive matte в actualnative контурах. Clean cell gutters и32unique hashes не дают чистый foreground. Кандидат не принимается. Нужен ограниченный technical alpha review, не procedural anatomy или новая endless generation.

Native SHA `9f1275cacf184776148fcd4f02375fb8df5862cf66f15b469aa51cb40b733d06`; original unchanged master v2 SHA `b3d0decc7ef9b80445097a7515409a1cffb912a33355c7b4c2655bb352e8f3b1`. Reviewer `/root/art_review_p06` осмотрел actual fullmaster/native32, light/dark fullatlas, four direction phase pairs8x и side walk4strips. Only reportdir writes; no Godot/controller/Git commands/generation/source edits/subagents. Runtime Olezhka world atlas отсутствует.

## Конкретный contour finding

Коричневые непрозрачные полосы идут вокруг crown, bare arms, hands и hips в нескольких направлениях; на тёмном фоне создают широкую тёплую кайму вместо чистого тёмного outline. LEFT idle0 имеет flat brown bar над волосами, заметный на светлом фоне. Первоначальное quick-message слово «detached» уточнено: компонентный анализ показывает бар соединённым с crown несколькими пикселями; это extraneous contour, не отдельный floating component. Все32 native cells остаются one8connected, что не отменяет видимый matte.

Evidence: `olezhka_world_v2a_light_dark_2x.png`, `olezhka_world_v2a_left_phase_pairs_8x.png`, `olezhka_world_v1_v2a_v2b_contour_r1_c0_8x.png`. Actual source/native сравнение не позволяет объявить brownfringe intentional outline только потому, что shared palette включает brown RGB.

## Alpha/integrity

Один global alpha>=208 действительно даёт clear source margins во всех32. Независимая проверка source thresholds:128 touches20cells,160 touches12,192 touches3,208 touches0; поэтому preserved strict128 failure относится к residual matte, а не доказывает anatomical clipping. Исторический `world_v2_pack_failure.json` сохранён; updatedauthor `world_v2_alpha_analysis.json` уточняет интерпретацию.

Все32 exact RGBA reconstructed: whole192×256→48×64 NN, shared43palette, oneglobal208threshold, fixed idleY perrow; никаких bodypart masks/warps/repaints/mirror. Все hashes/bounds/sourceRects/metadata/inputroles совпали. «No opaque loss» здесь означает только отсутствие placement crop ПОСЛЕ выбранного threshold; threshold сам намеренно удаляет raw alpha samples. Raw master alpha максимум252, cores в основном248–251, поэтому blindly raising threshold до248/250 повреждает части фигуры. Три целых diagnostic cells при240 выглядят лучше, но их недостаточно для full32 approval.

Native alpha0/255,34opaque colors,32unique. Все32 frame pixels изменились относительно v1, поэтому проверены заново. LEFT headtops walk7/4/7/4 включают fringe и дают3pxrange; это не переносится как достоверный authored headbob без очистки contour. Nativev2a непригоден по указанному broadmatte finding даже при правильных hashes.

## Gait/identity

RIGHT corrected contactB4/runB7 теперь даёт dark FARLEFT leg leading screenRIGHT, bright NEARRIGHT leg trailing screenLEFT; A2/6 обратный. PassingB5 согласует опору/колено; первоначальный v1 same-near-leading finding устранён sourcewholepose edit. DOWN/UP opposite phases и LEFT более тёмная leadingB leg сохраняются. Собственное молодое cleanface/stocky build/shortcrop/darktrainingwear без glasses/watch/jewelry сохранено; нового likeness mustfix нет. Все32 просмотрены, не assumed unchanged29.

Следующий bounded technical candidate v2b/240 оценивается отдельным report; v2a FAIL не стирается. Никаких runtime/world/P06 approval. Metrics: `olezhka_world_preflight_v2a_metrics.json`; threshold diagnostics208/224/240/248/250 — лишь review evidence, не productionassets.
