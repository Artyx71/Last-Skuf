# P02 — independent art subreview, attempt 1

Reviewer `/root/lead_reviewer/p01_art_subreview`, не автор root/gameplay_p02/art_production. Source HEAD `1786633e2d4f366a267ae884e1b2cf6029fbc546`, 2026-11-13. Исходники, PNG, code, Git не изменялись; только inspection artifacts рядом с этим отчётом. Raw фотографии не открывались и не отправлялись; новые guards вымышленные.

**Art verdict: FAIL по интеграции action/contact (ART-P02-04 HIGH), плюс три MEDIUM findings. Технические PNG и базовые дизайны пригодны для P02.** Это независимый AI art review, не финальное решение фазы. Parent Lead определяет окончательный gate после QA/CI/artifacts. Новый человеческий likeness gate не придумывается: P01 уже утверждён, guards анонимные вымышленные, действия Якудзы сопоставлены с accepted P01.

## Что проверено

Прочитаны AGENTS, `planning/P02_TASKS.md`, ART_BIBLE, P01 PASS/owner approval scope, enemy/action inventories, author reviews, оба source README, common/design/exact prompts, cleanup prompt, новые atlases и связанный animation/combat code. Точные enemy prompts равны прочитанным common+blank-line+role-design. Оба inventory независимо проверены: **33/33 файлов совпадают с записанными SHA256**.

Локально через `view_image` открыты все три enemy masters; action master v1 и финальный v2; actual `patrol_sheet.png`, `rusher_sheet.png`, `shooter_sheet.png`, `action_sheet.png`; accepted P01 `world_sheet.png`; реальные `combat_lab.png`, `combat_melee.png`, `combat_fall.png`, `export_linux_combat.png`, `export_windows_wine_combat.png`, `combat_contact_sheet.png`. Дополнительно открыты собственные ×4 NEAREST sheets и crops реального replay в этой папке. Crops не содержат фото и не исправляют artwork.

P01 `world_sheet.png`, `portraits.png`, `portraits_past.png` **и atlas.json** точно совпадают с hashes в accepted P01 decision (reviewed commit `6ccf4afbc5e81972596529ccc1d5e8f9f367f5b0`). Утверждённый комплект не регрессировал.

## Независимая визуальная оценка

**Дизайн/силуэты.** Patrol — широкие квадратные плечи, каска, жилет и поясная сумка, cyan fasteners/visor, дубинка. Rusher — узкие плечи, мягкий капюшон, короткая orange куртка и лёгкие ноги. Shooter — угловатый шлем/наплечники, crimson chest/back plates, читаемый двухручный пистолет в side views. Это отдельные полноценные рисунки, не цветные boxes или перекраска одного base. Наблюдаемой подмены персонажами P01, реальных символов, photo remnants нет. Независимая проверка авторства чужих библиотек по одним изображениям невозможна; source/provenance согласованы с заявленным original AI-assisted workflow.

**Камера/пиксели/фон.** Видны верх шлема/капюшона, плечи и короткие ноги; side views остаются oblique overhead. Guards компактнее и менее широкие, чем гротескный Якудза, на actual lab они читаются в одном игровом масштабе. Native clusters жёсткие, без baked bilinear blur; фон чистый. Независимый pixel inspection всех четырёх новых PNG: 384×256, 48×64×8×4; alpha только 0/255, transparent RGB=(0,0,0); opaque palette patrol25/rusher16/shooter25/actions29. У всех32 frames каждого atlas origin(24,58) и alpha bottom bound58 exclusive. Fixed foot pivot подтверждён; это не доказывает стабильность корпуса.

**Action identity/readability.** Black tee, большая тяжёлая фигура, волосы, skin ramps и телефон согласованы с P01. Shove читается коротким palm push, а не героическим punch; hit — recoil/crumple; во всех четырёх col7 лежачая согнутая поза. Телефон удерживается слева; в right-facing shove contact он закрыт ближней рукой/корпусом, а не показан брошенным. Final v2 left fall cells компактны и целиком помещаются; source v1 оставлен как история, а не финальный asset. На actual `combat_fall.png` Якудза действительно лежит; падение не сведено к tint стоячего героя.

**Actual lab/platform captures.** Linux и Wine captures визуально согласованы с native lab. На тёмном фоне cyan/orange/crimson отличимы, matte/светлой каймы не видно. Красная line и кольцо над головой сообщают shooter telegraph, даже когда down-view нарисованный пистолет диагонален. Contact sheet показывает движение/escape/смерть/retry/training, но редкая выборка сама по себе не доказывает timing. Dense crop реального MP4 11.30–11.85 дополнительно просмотрен: здесь patrol вбегает в reach, и kills1 впервые виден вместе с contact-позой. Этот replay **не является доказательством раннего damage**; отдельный code-derived timing риск ниже.

## Findings / минимальные tickets

### ART-P02-01 — MEDIUM: учебное оружие отделено от руки

Место: `game/scripts/actors/combat_player.gd:187` (gun overlay) и `:191` (knife overlay), `combat_melee.png` t=11.60; `combat_melee_inspection.png`, dense timing crop рядом.

Expected: нож/пистолет как held equipment начинается у соответствующей кисти; визуальный muzzle/клинок не висит у стоп. Observed: нож нарисован при local y=-9 (blade x21 по aim), тогда как вытянутая кисть `action_sheet.png/right_1` находится значительно выше в frame, при pivot y58. В crop отчётливо видны рука на уровне груди и отдельный нож внизу между ногами актёров. Gun overlay после выстрела использует ту же высоту -9; dense crop показывает появление оружия/пули у стоп. Это реальный visual defect, не следствие масштаба crop.

Repro: F2, aim right, melee рядом с patrol; затем ranged; сравнить wrist и weapon origin на кадрах контакта/recovery. Минимальный ticket: ввести directional/per-action hand/muzzle sockets на native grid, привязать overlays к ним и актуальному animation frame; сохранить отдельную плоскость collision queries при необходимости. Нож должен следовать правой кисти, а не оставаться на месте все250ms. Снять close runtime evidence всех4 направлений melee/ranged.

### ART-P02-02 — MEDIUM: скачок корпуса shooter при idle→walk

Место: `game/assets/art/enemies/shooter_sheet.png`, `down_0/1` → `down_2` (rect96,0,48,64), `up_0/1` → `up_2` (rect96,192,48,64); `shooter_inspection_4x.png`.

Expected: переход idle→walk сохраняет apparent scale/посадку каски, шаговый bob не выглядит удлинением фигуры. Observed: top down12→6px, up11→6px при фиксированном bottom58. Это скачок5–6 native px (около10% высоты фигуры), сильнее обычной вариативности patrol/rusher и выше заявленного minor jitter. Walk internally меняет верх ещё на2px. Рисунок заметно вытягивается при начале шага; единый foot pivot этого не исправляет.

Repro: переключать shooter между0 и2 колонкой на общем pivot или смотреть остановку/старт AI. Минимальный ticket: согласовать torso/head placement idle/walk, нормализовать pose hierarchy с естественным bob без изменения массы каски/брони; проверить при8FPS и на640×360. Не лечить только uniform resize каждой фигуры и не менять approved P01. Обновить native source/atlas hashes/evidence.

### ART-P02-03 — MEDIUM: убитый guard сохраняет вооружённую стоячую позу

Место: `game/scripts/ai/enemy_actor.gd:112`; `combat_melee.png` — patrol справа от героя; конец `combat_contact_sheet.png`; `combat_replay.json` training snapshot (dead patrol `idle_right`, dead rusher `walk_left`).

Expected: defeated state быстро отличается формой/состоянием от живой неподвижной угрозы. Observed: death только убирает ring, затемняет sprite и pause текущего idle/walk frame. Видны стоящие вооружённые фигуры, в том числе rusher с поднятой ногой. На тёмном lab tint ослабляет уже тёмные детали; само положение не показывает поражение. У Якудзы состояние падения выражено существенно яснее.

Repro: убить patrol ножом и rusher пистолетом, отпустить input; сравнить их с idle живого guard без опоры на HUD kills. Минимальный ticket: однозначная самостоятельная defeated presentation — компактная оригинальная prone/static pose либо явный переход исчезновения с кратким defeat cue. Полный большой enemy action pack не требуется; не выдавать замороженный walk за fallen pose. Обновить capture.

### ART-P02-04 — HIGH, runtime-confirmed: damage во время wind-up до contact frame

Место: `game/assets/art/yakuza/actions_atlas.json` melee.contact_column=1/fps12; `combat_player.gd:137`; `game/scripts/systems/combat_system.gd:65`.

Expected: visual wind-up col0 ещё не наносит damage, contact col1 начинает объявленный контакт, затем recovery. Observed in code: `start_melee` добавляет active query немедленно, до `_play_action`; следующий physics tick уже проверяет damage, без ожидания col1/83.3ms. Parent Lead выполнил отдельный native runtime repro настоящим Input action с заранее поставленной inside-range целью health3. Я лично прочитал `timing_probe.json` и `logs/timing_probe.log` в этой папке: tick0 frame0 hits0/health3; **tick1 frame0 hits1/health2**; first sampled frame1 только tick6. Проверка завершилась exit1, `damage_during_windup_observed=true`. Это подтверждает рассогласование удара и показанной contact-позы, а не просто потенциальный code risk. Авторский replay попадает в contact по расположению движущейся цели; его видео само ранний damage не доказывало.

Repro: parent native probe evidence `timing_probe.json` и `logs/timing_probe.log`: заранее расположить цель внутри фактического melee hit volume, нажать Input attack_melee, записать hits/sprite.frame за каждый tick. Минимальный ticket: синхронизировать start/contact/recovery data с hit window, сохранив отзывчивое начало анимации и single-hit rules; либо явно переавторить первый кадр как действительный контакт и согласовать atlas. Повторный probe должен подтвердить отсутствие damage в wind-up и контакт в объявленной фазе, также повторить базовые hit/miss/cooldown/restart проверки.

## Ограничения и рекомендация

Новых human approvals этот subreview не требует. P01 likeness acceptance сохранён; public release/voice/merge прав из него не выводится. Полная platform/CI/runtime certification вне этого art subreview. PNG/прозрачность, базовая камера и оригинальные role designs подтверждены; интеграционные weapon/state/timing tickets и shooter transition следует передать исполнителям и проверить повторно. Принятый P01 MEDIUM idle jitter остаётся прежним отдельным замечанием, а не новым regression P02.
