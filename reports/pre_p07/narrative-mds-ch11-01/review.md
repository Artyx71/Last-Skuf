# CH11 — независимый Narrative / paper-contract review01

**PASS_COMPONENT — только текущий Narrative draft CH11.** Обязательных исправлений канона/причинности/бумажного контракта не найдено. Это не Gameplay/ART/runtime/Lead/Readiness или all21MDS approval.

Проверены фактическая CH11 SHA `be372f97ae68a2f9b082ae760b24ca21d34c9dc733188b967c56413eba4462ab`, STORY/GAMEPLAY/AUDIO/DIALOGUE/CHARACTER contracts, canonical registry/routes, Timka catalog и actual character_player/scene-policy code. Заявленный WORK HEAD `5dcacdf6633871c56e0401deea2fb2fb0393291c`; Git не вызывался, authority — exact bytes/SHA. Автор — ROOT, reviewer MDS не реализовывал. CH01/CH09/CH12/CH16 совпали с ранее принятыми Narrative hashes.

## Канон и ограничения знания

CH11/EV_CH11_COMPLETE,11/11,present,TIMKA,EV_CH10_COMPLETE и пустая production_pending дата совпадают с registry.19:30–20:30 — каноническое окно привычной прогулки, без придуманной точной даты/минуты и без зависимости от системных часов. Тимка хочет вернуться к Эле; она не смешивается с Ellana/Zhinka и не назначается виновницей/контролёром. Кабан/организатор и Gabar Engine преждевременно не раскрываются.

EV_WITNESS_TRANSFER действительно выдаёт только flags.witness_transfer. Поздний EV_VERIFIED_OPERATIONS в CH20 требует ещё founding_records; эта глава не подменяет независимые источники и не выдаёт illegal_operations/open_source_origin/founding_records. D01–D06 не изменены. Canonical optional EV_SECRET_JACK_REVENGE существует именно в CH11 и выдаёт только одноимённый secret; завершённая безопасная сцена/seen-skip, не простой proximity, записывает его once. Основной выход от секрета не зависит. Ending predicates/безусловная доступность WIFE_CALLING сохранены; secret — лишь один из существующих REAL_PRIME условий.

## Present Timka и Джек

Catalog подтверждает peaceful_present speed84/lethal=false/finishers=false/equipment[]. Actual disengage в character_player имеет0.12/0.24/0.18/1.8, speed140 и до33.6px при свободном движении. Код двигает назад от action_aim через move_and_collide только active-интервалом, не даёт damage/teleport/invulnerability. Draft не подключает prime FIN/clinch/оружие и прямо требует жизнеспособный обычный отход при cooldown. Последнее — ещё требование будущему actual route test, не уже доказанная игровая проходимость.

Jack companion допустим утверждённым scope и направлением GAMEPLAY_SPEC, но draft честно говорит, что runtime/арт ещё отсутствуют. Ограничены world collision/footprint/follow distance, отсутствуют attack/combat target/actor blocking/щит; нет нового leash-QTE/animal-combat sandbox. Выход требует локально присутствующего Джека, допускает возврат за отставшим и не запирает пару по разные стороны. CP/reload использует проверяемую пару позиций, не поздний target/телепорт. Реализация/кадры/двойной clearance остаются объявленным HIGH до производства; этот review их не закрывает.

## Бумажная карта, постановка и устойчивость

Заданы связные пути DW0→DW1→наблюдение→DW3 и альтернативный DW1→DW2→DW3. Препятствие в DW1 имеет обходы; оба маршрута сохраняются, условием не становятся kills/FIN/frame-perfect ability. Отличие от остальных четырёх MDS содержательно: мирная прогулка/наблюдение, короткий evade с небоевым спутником; CH01 ключ/звонок, CH09 объект/телефон, CH12 архив/два POV, CH16 D02 reclaim не повторяются. Уникальность всех21 этим не оценена.

Указанный LOS от688,576 к848,288 пересекает границу y512 при x≈723.56, внутри portal640..736. Fixed cover и названная ограда не дают очевидного бумажного перекрытия этого отрезка. Но при стандартном центрировании camera640×360 target y288 выше top396: readable transfer потребует постановочного смещения/кадра. Документ уже требует привлечения камеры и actual LOS/readability proof до art lock; это открытая production обязанность, не основание заявить, что неподвижный игровой кадр уже всё показывает. Толщина стен/кадр/изображение не проверены engine.

Два guard — участники передачи; их появление связано с завершением сцены, закрытием багажника/шагами/подходами и предупреждением. До E2 угрозы неактивны, нет shooter/rusher/спавна у героя. CP1 задаёт safe pair688,576/656,592 до охраны, фиксированные stage/seed, затем resume-lock и предупреждённый E3. Durable witness предшествует CP, не откатывается смертью; ошибки записи не выдают ложный флаг. CH01 ChapterProgress не объявлен готовой общей схемой: chapter snapshot validation/atomic tests отдельно HIGH. Complete требует witness+пару у exit+HOME once; CH12 только eligible, не falsely playable.

## Статус ассетов и граница решения

Новая Jack-walk аранжировка FALLEN TITAN соответствует AUDIO_SPEC тёплого present, а не Prime retime. Music/SFX/сцены/мир/Джек/позы передачи REQUIRED_NOT_CREATED; signal/listening/native/frame/placement gates сохранены. Полноценного follower/runtime capture/audio/gameplay review не было.5–10min — NOT_MEASURED hypothesis без таймеров/пустых кругов; secret/AFK/пауза отдельно.

PASS_COMPONENT поддерживает NARRATIVE_REVIEWED только этой exact CH11 MDS. Reviewer не изменял registry/status/source. Declared HIGH зависимости не закрыты: до производства нужны Jack/checkpoint/route/host/door/camera/music и actual ordinary-escape-at-cooldown tests. Нет all21/Gameplay/ART/Audio/QA/Lead/Readiness/runtime/production/phase/merge/release PASS. Параллельный CH01 production pilot вне scope.

Engine/generator/network/Controller/Git не вызывались, код/ассеты/состояние не менялись; новый owned report — единственные записи. Source snapshots, fact checks, paper traces, before/end verification и FINAL_HASHES фиксируют самостоятельный вывод. После verdict packet immutable.
