# Независимый Lead — Тега, компонент окружения, review01

**FAIL_COMPONENT: TEGA-L01, MEDIUM, must-fix.** При синхронном foot-audio callback, который переносит тот же зарегистрированный предмет либо героя за допустимую дальность, старый job ещё выполняет движение в том же physics tick. Требуется повторная проверка фактической геометрии после внешних callbacks. Это локальное замечание компонента; полная P06 не рассматривалась и её attempt не сбрасывается.

Рассмотрен runtime/art `6a0224e016e53e13ddb1e6fde747b66e7f75447b`, связанный с `084026895f2ffb1b51b438cbf87e8a97440d7b77` ровно тремя тестовыми/export изменениями. Последующее исправление `c8f465840ec970e6abdcb9d41e1f0cbed8fc38bd` данным решением не принято: ему нужен отдельный review02 с новыми доказательствами. Старые ART/Gameplay PASS сохраняются как заключения по проверенному ими набору сценариев.

## TEGA-L01: проверка близости устаревает внутри tick

Место: frozen `game/scripts/systems/environment_kick_runtime.gd`, `tick()`, участок от первой `_near_foot` до `_wall_contact`/`make_noise` и последующего motion. `_valid_job` проверяет epoch, живые экземпляры, registry identity, enabled и полномочия, но не текущие range/facing/foot-overlap/LOS. `_near_foot` вызывается до внешнего audio-event; после callback остаётся только `_valid_job`. Поэтому перенос того же действующего предмета не отменяет сохранённый первый шаг.

Это уже не предположение по коду. Независимый QA добавил отдельный сценарий `qa_tega_callback_geometry.gd` и выполнил его на unfixed084/runtime6a, в изолированной ROOT-копии. Observer с `process_physics_priority=1000` фиксирует состояние после Core в том же физическом тике. Lead самостоятельно прочитал script, result, command и log и пересчитал разности координат.

| Callback | Состояние сразу после callback | После Core того же tick |
|---|---|---|
| same_object_transform_far, tick19 | actor `[280,240]`, prop `[408,240]`, range128px | оба ещё сдвинулись на `0.70001220703125px`; jobs1 |
| source_transform_far, tick48 | actor `[180,240]`, prop `[308,240]`, range128px | оба ещё сдвинулись на `0.70001220703125px`; jobs1 |

В обоих случаях предмет тот же, enabled и зарегистрирован; pose1/clock≈.183333. Это недопустимое движение после потери foot-contact, а не повреждение masks/exceptions. **Damage и receipts равны0: удалённый урон не воспроизведён и не заявляется.** Actual результат —6 passed/2 failed из8 assertions, exit1 с двумя ожидаемыми assertion errors. Физический движок и baseline pose/control checks не заменены фиктивными координатами; мгновенный перенос — явно объявленный callback-триггер, а stale дополнительный шаг измерен отдельно после него.

Минимальный remedy и acceptance:

1. После каждого внешнего foot-audio/noise callback и непосредственно перед последующим motion/contact сохранить instance/registry/epoch/authority проверки и повторно вычислить реальный foot range/facing/overlap/LOS. Проверять валидность экземпляров до typed access, как в прежнем freed-object fix.
2. При потере геометрии удалить старый job до первого нового шага. Отменять только то прежнее действие, которому принадлежат прежние attackID/authority; callback не должен отменить уже новое действие. Не делать refund, reset или возврат перемещённого callback-ом чужого transform частью исправления.
3. Неизменный независимый geometry reproducer должен показать нулевые postcallback actor/prop deltas, jobs0 и отсутствие новых damage/receipts в обоих случаях. Проверить также геометрию после второго callback и перед contact; прежние cancel/free/revoke/replace/reset варианты и custom masks/exceptions должны остаться рабочими.
4. Новый frozen source должен получить свежие положительные/отрицательные engine proofs и actual native/movie evidence. Прежняя запись6a остаётся историческим baseline, а не новым render исправленного SHA. Не ослаблять пороги и не перезаписывать старые решения.

## Что проверено и следует сохранить

Реализация использует существующий CharacterPlayer/CombatSystem с отдельными `environment_kick.gd` и `environment_kick_runtime.gd`, без переписывания основной боёвки. Source diff показывает ограниченные hooks: создание/tick/reset resolver, dispatch стратегии, cleanup при cancel, HUD-подсказка. Объект действительно зарегистрированный collider, а не VFX или ranged shockwave. Данные .18/.18/.32, cooldown2.4, скорость210px/s и максимум37.8px не являются самостоятельной приёмкой ощущений.

Lead независимо пересчитал все три actual JSON: headless04, native01 live и movie. Каждый содержит4631 actor observations,4570 object observations,66 Core contacts и12 clothing overlays. В восьми Full/Reduced object-hit маршрутах собственные special0→1→2 идут по порядку, actor/object сохраняют относительное смещение с ошибкой<.02px, tick displacement≤3.501px. Contact один, environmental damage1, собственная pose1, score0; Full/Reduced displacement совпадает. Потолок37.8px не назван измеренной свободной дистанцией: реальные столкновения ограничивают положительные маршруты раньше.

Проверены24 FIN segments (3разрешённых категории×4направления×2режима): настоящий Space-earned stun, один shove0 и один lethal finisher1, contact pose1, score100/two damage_events без повторов,12 Full/Reduced равенств. NPC reaction1→corpse2 подтверждён actual assertions и соседними визуальными доказательствами; raw trace не выдан за независимый полный NPC health/kill counter. Шесть входящих Core hurt/fatal контактов и ещё четыре nonfatal clothing-case контакта наблюдаются в данных. Первоначальные deny/interruption/eight-callback сценарии не дают Core contacts. Они не покрывали найденный same-instance transform случай.

Независимо восстановлены96 complete-cell RGBA из master в native (WORLD/ACTION/FIN по32), все96 socket SHA/opaque pixels и56 clip maps. Художественная семантика отдельно проверена изображениями и независимым ART, не выведена из непрозрачности точки. Source FIN11 sharp x0 остаётся раскрытым latent border-risk, не blanket border-free acceptance; sharp/firearm abilities запрещены.

Lead самостоятельно декодировал и просмотрел66 настоящих whole video frames через явно помеченные диагностические crops:24 object0/1/2,24 Full/Reduced FIN contacts,12 кровяных special-поз и6 incoming contacts. Также просмотрены исходные native wall-stop и UP-contact PNG. Видны собственный серый худи, направленная стопа, физический верстак, NPC impact и восстановление; новая внешняя генерация/фотореференсы не использовались. Для blood frame map учтён `video n=tick−1`, не следующий setup. Положительный TTL и garment tracking сохраняются, actual follow lag≤3px раскрыт.

Movie SHA `5546870556a6500ec9c45b8ada00f3ef4fda717e2a46965ec5917695d22c1cb7`; независимый полный decode-count —4649 frames,1280×720,60/1,77.483333s. Это fixed MovieMaker cadence, не host FPS. Native01 даёт424/424 и128PNG, movie296/296, headless04 —296/296. Все136 producer artifact hashes проверены; actual producer `fc1f65eaa2e747a2b762eb92b70e613a`, exit0, argv/log/receipt SHA совпали.

Все1242 native recorded inputs проверены до начала исправления:1239 current084 byte-exact, три отличия — только `owner_preview_smoke.gd`, Oleg stale-selection KEY6→KEY7 и export fixture mapping. Их прежние6a байты проверены `git show` против recorded SHA; точные diff и critical source snapshots сохранены. Это не утверждение о неизменности всего будущего WORK после начала исправления.

ART `75e2a6fcc0f3fa3cc833c28c4c3a0ba4a8d6e972b94e24d2a32a52b9f0afe4db` и Gameplay `052c1cf3b4331d3f6d8bb4831f5c497139b75e32853f16638234d8e544bb2846` прочитаны с исходными proofs. Проверены54 ART portable entries и500 Gameplay entries, без дублирования всего decoded-cache. Они дают положительную оценку прежним eight-callback маршрутам и кадрам, но не отменяют новый QA05 defect. Нового Tega DEV export нет: исходный source-preview smoke29/29 и historical DEV05 не называются Tega exported-build acceptance. Counter57/57 после stale fixture correction тоже тестовая коррекция, не новая способность.

Формальный независимый QA01 завершился **FAIL_COMPONENT**, decision `3cbcc64ebe2ac771182a82eb76b986dcb3cbc4098fb0093367a5dbfa228d0224`; TEG-Q03 ссылается на TEGA-L01. Прочитаны итоговые review/findings/metrics, проверены188 portable entries и FINAL_HASHES. До нового контрпримера реально прошли14 suites/2297 assertions, включая Tega296, старые combat/contact/P04G/Yakuza/restart/Gabar/Oleg/Timka/Ryzhik/readiness/layout. Дополнительные23 negative,3 custom-mask/exclusion,4 actor-wall и57 fixed-counter/29 source-preview сохранены отдельно. Первые QA20/23 и28/29 не скрыты: пропущенное подключение audio и ошибочное требование zero-total-travel до стены были ошибками fixtures, исправленными до фактической квалификации нового product gap. Source/render/CI mock assertions не подменяют QA05 failure.

Все882 уникальные внешние reference bindings повторно сверены. Собственные critical runtime snapshots совпадают с recorded6a SHA; три084 test/export snapshots восстановлены из точного Git commit и совпадают с записанными hash. Начавшийся c8 fix не выдаётся за исходники, на которых снят старый фильм.

Все11 текущих приватных reference hashes совпали, raw references/ZIP не tracked, ignore подтверждён read-only Git query. Generation metadata новых ACTION/FIN использует собственный project art; review не копировал и не загружал личные фото. License rows сохраняют owner-controlled original art и отдельное коммерческое ограничение; public release clearance не выдана.

Ревью независимо от автора; reviewer Godot/native/export engines не запускал, WORK/source/Git refs/controller/state/очередь не менял. Разрешено исправление TEGA-L01 внутри текущей P06 с новым review02. Общая sevenhero audio/NPC matrix, Тега после fix, Паша, полный verifier/ROOT safe handoff и полный phase Lead review ещё требуются. Last full PASS=P05; P06 attempt1 остаётся IMPLEMENTING. Full P06/readiness/P07/merge/release, listening, hardware latency/FPS и native Windows этим решением не принимаются.
