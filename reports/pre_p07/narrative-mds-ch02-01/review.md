# CH02 — независимый Narrative / paper-contract review01

**PASS_COMPONENT — только текущий Narrative draft CH02.** Обязательных текстовых исправлений не найдено. Вымышленная потасовка заполняет утверждённый Timka flashback slot; канон, исходы, prime-контекст и описанные ограничения соответствуют inspected источникам. Это самостоятельный reviewer, автор — ROOT.

Привязка: CH02 SHA `5f5279ce433a748de439b9332aa4e3910deddc5dc89e25b7876bcccb93a44d8e`, заявленный WORK HEAD `7d97af62ebd42b20cf9aa598ee38ed450d54ef53`. Git не вызывался; authority — actual exact bytes/SHA. Проверены STORY/GAMEPLAY/AUDIO/DIALOGUE/CHARACTER/template, actual registry/routes/catalog/profile/finisher definitions и CharacterPlayer/CombatSystem/scene-policy code. Источники snapshots и before/end hashes сохранены. CH01 и принятая present-CH11 неизменны; их Narrative решения не переоткрыты.

## Канон и драматургия

CH02/EV_CH02_COMPLETE,2/2,past,TIMKA,EV_CH01_SERVICE_ESCAPE и пустая production_pending дата точно совпадают с registry. Год/синхронность с CH01/окно прогулки19:30–20:30 не придуманы. Prime — период физической формы, не организация PRIME. Нет раннего раскрытия Макса/Кабана/кода/документов/15k или будущей передачи.

Герой сначала даёт людям уйти, не хвастается и не ищет повод избить слабого. Летальный Core разрешён, но добровольное добивание и вымышленная опасная потасовка не маскируются под безвредный спортивный спарринг. Можно контролировать/оглушить и пройти. Это совместимо с добродушным Тимкой и его добровольно мирным present, без обвинения Эли и без permanent upgrade. Все дополнительные сценические факты названы proposal, не реальными событиями/новыми именованными боссами. У гражданских только до-боевой staged departure, не новая escort/animal system.

Единственный обязательный canonical outcome — существующая chapter completion. Новые decisions/evidence/отношения/secrets/XP не выдаются; flashback не переписывает present save. StoryState.complete_chapter реально существует и фиксирует event через ledger; CH03 остаётся planned/scene-empty и получает eligibility, не готовый runtime launch.

## Возможности и пределы P06

Actual catalog athletic_prime: speed118/lethal=true/finishers=true, unarmed/blunt/environmental. CharacterPlayer prime strike действительно damage0/stun1.25/strong,0.20/0.12/0.28/cooldown0.9: базового NPC не приходится искусственно усиливать ради earned захвата. F clinch выбирает один eligible unarmed target с пустыми руками; Core требует stunned/knockdown,8..35px,dot≥0.72,LOS/live authority и повторную проверку уязвимости. Profile задаёт0.48/0.12/0.38, successful ability start —2.4s cooldown. Нет дистанционного авто-grab/неуязвимости/дополнительного animation damage.

Environmental definition реально использует ID training_bench, source-target≤36 и target-object≤43; обязательны enabled registered object, alignment и LOS. Пример1728,496→1728,472→1728,448 даёт24/24px иdot1. Это разумная paper-постановка, не доказанный collider/native contact. Авторский bench20×12, его визуальный footprint/LOS/контакт ещё должны быть проверены. ENV_TITAN_BENCH как сценовый объект с регистрацией под exact Core ID не превращает любую стену в finisher. Env требует собственного category/authority; F clinch не переключается автоматически.

Optional blunt не выдаёт firearm/sharp/обычную lethal knife attack. Его pickup/save ещё отсутствует. Draft прямо признаёт, что sandbox timka_prime не является campaign grant: нужны trusted CH02 definition и расширение текущей factory/ability whitelist. Эта HIGH интеграция не принята и не объявлена готовой по actor/context строке из save.

## Карта, угрозы и сохранение

Paper graph связан: TT0→TT1→TT2→TT3→TT4. TT1→TT4 не обходит всю главу до открытия обратной задвижки изTT4. F-двери после ухода гражданских не зависят от kill/key drop. E1 один контролируемый melee contact; E2 поворот partition/LOS; E3 разнесённые две роли и два обхода cover через2112,192 или1792,544. Состав конечный, E3 предупреждён/детерминирован, нет HP padding/босса/подкреплений. Оба дворовых подхода существуют геометрически; actual AI/разрыв дистанции/footprints/доступность на cooldown ещё не доказаны.

CP1 не объявляется безопасным по названию. Текст требует отсутствие threat/projectile/attack, воспроизводимую позицию/уязвимость оставшегося NPC, иначе оставляет CP0. Не требуется обязательное убийство E2. Схема stage/director/checkpoint/atomic write честно HIGH, а не переименованный готовый ChapterProgress; pickup при restore либо в inventory, либо доступен в мире без копии. Остаточные stun/cooldown/positions требуют explicit policy/tests. Durable completion после живого exit/final scene once, failed write не даёт ложного сохранения. Это достаточный Narrative paper контракт; actual retry safety/state tests отдельно.

## Статус и граница PASS

Новые сцены/зал/двор/bench/инструмент/силуэты и retro-workout FALLEN TITAN/stems NOT_CREATED. P06 frames/category reactions/cues честно reuse, C09 style debt остаётся P08. Новый score не принят прежним audio PASS.12–20min — NOT_MEASURED hypothesis; нет обязательных упражнений/пустого ожидания/HP для диапазона.

PASS_COMPONENT поддерживает NARRATIVE_REVIEWED только этой exact CH02 MDS. Reviewer не менял registry/status/source. Campaign factory, checkpoint/pickup, real contact/art/music и проходимость остаются declared HIGH до производства. Нет Gameplay/ART/Audio/QA/Lead/all21/Readiness/implementation/runtime/phase/merge/release PASS. Личное управление, ощущения ударов, native контакты и длительность не тестировались.

Engine/Controller/generator/network/Git не запускались; код/ассеты/состояние/MDS не менялись. Новые файлы только в owned report. FINAL_HASHES фиксирует packet после verdict; frozen файлы не переписываются.
