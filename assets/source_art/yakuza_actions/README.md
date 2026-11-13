# P02 — ограниченный action pack Якудзы

Статус: **DRAFT_REQUIRES_INDEPENDENT_ACTION_REVIEW**. Реальные оригинальные pixel-art shove/hit/fall poses для P02; не P03 и не phase PASS.

## Происхождение

Использованы только утверждённые собственные `game/assets/art/yakuza/world_sheet.png` и `portraits.png` как style/identity/scale references. Raw фото повторно не использовались. Сохранены узнаваемые чёрные волосы, вымышленное короткое широкое тяжёлое тело, чёрная футболка, тёмные брюки/обувь и телефон. Shove короткий и неуклюжий: одна правая ладонь, телефон остаётся в левой, без героического удара или нового оружия.

`actions_master_v1.png` — первый реальный встроенный image_gen результат 1536×1024 RGBA, 8×4 cells по 192×256. Автор обнаружил касание границ у LEFT-row fall cells: край руки/волос мог быть обрезан генератором. Этот вариант не передан как финальный runtime.

`actions_master_v2.png` — targeted built-in edit того же собственного master. LEFT-row последние три позы авторски переработаны компактнее: согнуты локти/колени, сохранены голова/руки/телефон. Ни один opaque source contour теперь не касается границы своей ячейки. Остальные позы/стиль сохранены. Обе generated versions оставлены для provenance.

Точные prompts: `action_prompt.txt`, `cleanup_prompt.txt`. Возвращённые output_hint и имена полей результата без base64: `generation_metadata.json`, `cleanup_metadata.json`. Original generated files оставлены в CODEX_HOME. Использован встроенный image_gen, всего два вызова; paid CLI/API fallback и sudo не применялись.

## Packing и runtime

`build_assets.py` выполняет только техническую нарезку generated pixel drawings: crop, alpha threshold128, NN sample 192×256→48×64, существующая approved31-color palette без dithering и anchor placement. Он читает старый `atlas.json` только ради палитры и не меняет его. Утверждённые P01 source/PNG/evidence не перезаписываются. `actions_native_source.png` — фактический pixel-grid raster source. Layered Aseprite project не создавался.

Запуск: `.tools/art-venv/bin/python assets/source_art/yakuza_actions/build_assets.py`. Уже доступная локальная Pillow13.0.0, без новой системной установки.

Экспорт: `game/assets/art/yakuza/action_sheet.png`, 384×256, frame48×64, 8columns×4rows down/left/right/up. Pivot=(24,58), нижняя граница подошвы/позы каждого кадра58, тело полностью внутри frame.

- Col0–2: melee, wind-up / короткий shove ладонью / тяжёлая recovery. Runtime12FPS, contactcol1, nonloop.
- Col3–4: hit/flinch, runtime12FPS, nonloop.
- Col5–7: death/fall, runtime12FPS, nonloop; последний кадр hold. Col7 — явно лежачая согнутая поза, не сидящий или стоящий персонаж. При всех4направлениях голова/руки/ноги/живот целиком сохранены.

`actions_atlas.json` — отдельный manifest с rectangles/origins/bounds/hashes/FPS/source и индивидуальными offsets. FPS согласованы с фактической конфигурацией combat_player.gd: 12FPS для всех трёх sequences, чтобы три fall poses помещались до automatic retry250ms. Nonloop, финальный лежачий кадр удерживается до reset. Gameplay contact timing остаётся ответственностью combat state.

## Проверки и ограничения

Автор открыл оба master и native checkerboard preview. На финальном master проверенные углы имеют alpha0, нет видимой непрозрачной matte или фотофрагментов. Production PNG: alpha0/255, transparentRGB=(0,0,0),29используемых цветов из approved31palette. Все32позы непустые/уникальные, source edges чистые, при packing не потерян ни один opaque pixel. Bounds x2..46 и y7..58. Неизменность трёх approved P01PNG отдельно сверена по SHA256.

Небольшое изменение объёма/формы волос и тела между generated poses остаётся. В right-facing shove телефон частично скрыт ближней рукой/торсом; он не должен считаться брошенным предметом. LEFT fall poses компактнее исходной версии ради цельного силуэта. Только три key poses падения; root должен удерживать лежачий финал. Это авторские наблюдения, не fake animation QA: реальный Godot replay и независимый reviewer ещё проверяют движение, контакт и чтение hit/death.

Evidence: `reports/phases/P02/yakuza_action_preview_3x.png`, `yakuza_action_structural_check.json`, `yakuza_action_inventory.json`, `yakuza_action_author_review.md`. Никаких commit/push/public release или самостоятельного PASS не было.
