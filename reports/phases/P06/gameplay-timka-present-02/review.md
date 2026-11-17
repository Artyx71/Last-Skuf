# Независимое Gameplay closure: Timka present / disengage

**PASS_COMPONENT** на исходниках `2780e9e2a8e177e88b892d6abe91d9e141bf04de`. GP-TIM-PRES-01 закрыт новым actual-contact evidence. Первоначальный FAIL на69ffc58 не изменён и сохранён в `gameplay-timka-present-01`; его decision SHA256: `020140176a1b0c558443052d417e671662c3172058ad3d76502c3e71a2c9f554`.

Область — существующий present/disengage компонент: backward motion, фазы, отмена, ограничения действий и отсутствие иммунитета в проверенных настоящих incoming contacts. Это не приёмка prime, полной present/prime художественной разницы, всех7 героев, full P06, readiness, P07, merge, CI, exports или релиза. Gameplay reviewer работал независимо от автора, не запускал Godot/builders/controller и не изменял WORK/код/state/queue/Git/network. Записаны только review-артефакты ROOT.

## Точная привязка исходников

Непосредственно прочитаны новый replay, Core start_melee/collision/receipt/damage path, enemy bind_melee/contact presentation, player body/hit/impulse logic и изменения common verifier. Production handler, frame loader, Core, art и sockets с предыдущего69ffc58 не изменены; fix добавляет реальные incoming scenarios и регистрацию wrapper в `tools/verify.py`.

Native02/headless03 записаны на2780e9e. Текущий WORK HEAD при инспекции — f66995892c8fdf8782e389a76c8ff05d628714d0: единственное game-source отличие — `game/scripts/qa/owner_preview_smoke.gd`. Его новая проверка KEY3/F-step/no-finisher и KEY4 atomic prime denial не меняет gameplay. Snapshot этого файла взят через `git show 2780e9e:...`, а не из более нового HEAD. Все1108 hashes записанного runtime/tooling inventory сверены:1107 совпадают с текущими файлами, оставшийся owner-preview smoke совпадает с exact2780 source. Все45 listed artifact hashes native/headless также совпадают. Полный inventory и оба diff находятся рядом с отчётом. Решение не перепривязано кf669958 и не принимает его packaged export.

## Что изменилось после FAIL

В старом evidence `contacts=[]`; прямой receive_hit доказывал только нижележащую реакцию. Новый replay дополнительно ставит противника до измеряемого F-input, явно отключает AI, затем вызывает production `CombatSystem.start_melee` с обычной `enemy_melee` definition. Core вызывает настоящий enemy bind_melee, формирует attack pose и выполняет actual spatial query/LOS → incoming once-token → defense hook → receive_hit. Для новых случаев нет прямого receive_hit/_apply_hit или телепорта игрока во время шага. Старые direct reaction cases остаются отдельными и не используются как доказательство Core delivery.

В каждом новом прогоне7 настоящих incoming receipts: guard hurt/fatal, active hurt/fatal, recovery hurt/fatal и projectile during active. Headless03:104/104; native02 live:137/137 с33 PNG; movie:104/104. Каждый содержит1098 непрерывных trace samples. Reviewer самостоятельно пересчитал контакты/фазы/геометрию и baseline motion:3294 samples,21 incoming event в трёх actual запусках. Это независимый анализ сохранённых прогонов автора, не собственный запуск движка.

| Случай | Предыдущий live clock/frame | Live contact tick | Результат |
|---|---|---|---|
| guard hurt / fatal |0,033333 /0|774 /795|hit /fall|
| active hurt / fatal |0,2 /2|825 /855|hit /fall|
| recovery hurt / fatal |0,4 /5|897 /939|hit /fall|
| projectile active |0,2 /2|967|hit|

Предыдущая запись для каждого контакта ровно на один physics tick раньше. До receive_hit clock ещё увеличивается на1/60с:0,05 остаётся guard,0,216667 active,0,416667 recovery. Сам contact event уже содержит заменённый action clock0/hit/fall; его нельзя ошибочно объявлять pre-contact clock. Зафиксированный фазовый переход согласуется с настоящим tick order.

Независимый расчёт геометрии подтверждает overlap: исходные enemy positions для guard/active/recovery x270/254/200 при y240, обычные reach18/radius14; реальный player body16×12 с offset(0,-6). Attack circle пересекает body в каждом contact case. Core-путь и actual receipts исключают ситуацию «тест прошёл, потому что атака промахнулась». Projectile создаётся через production fire/pistol и достигает движущегося body; это не переданный вручную damage.

На каждом melee contact ровно один incoming damage1, один hits_received, отсутствие defended/parry, health1 для nonfatal и0 для fatal; ответного ability hit/score нет. Actor переключается на собственный hit_right/fall_right, ability-distance больше не накапливается, после reset очищены receipts/action/cooldown/distance.10 последующих ticks не повторяют damage; здоровье NPC сохраняется3. При fatal body position остаётся постоянной. При nonfatal есть обычный Core knockback:85px/s начального impulse с затуханием700, а не продолжающийся disengage. Поэтому вывод не формулируется как полная неподвижность живого игрока после удара.

## Независимые QA наблюдения и сохранённая регрессия

Также прочитаны реальный QA2 observation-only subclass и его raw `incoming/result.json`. Subclass вызывает прежний callback и добавляет только запись состояния. Reviewer независимо проверил все7 actual reserved receipts: count1, health0/1 по lethal flag, hits_received1/damage_events1, counter_blocks0/score0, collision layer2/mask1, previous trace tick=contact tick−1. Эти raw значения подтверждают assertions автора без подмены QA summary доказательством. Копии и численная проверка включены в `independent-QA/` и `factual-proofs.json`. QA2 engine-прогоны не называются собственными прогонами Gameplay reviewer.

Полные Input F пути во всех направлениях заново удовлетворяют независимому интегралу `start - aim*140*clamp(clock-0.12,0,0.24)` с ошибкой<0,001px:33,59993–33,60013px, максимум2,33335px за tick. Все6 фаз совпадают с actual sprite/action frame. Existing wall/cancel/revoke/reopen/owner-replacement/pause/reset/cooldown/settings/finisher-equipment-ranged denial checks также проходят в fresh replay. Six source references остаются прежними собственными shove0 → reverse walk3..0 → shove2; новых рисунков и готовности prime это не означает.

QA2 отдельно проверил fresh present104 + observed104 + readiness62 и сохранил baseline layout102/Gabar124/Oleg164/negative30 по exact-input comparison с QA1. Reviewer прочитал правила reuse и diff: gameplay/assets и соответствующие baseline scripts не изменены. Новых самостоятельных Gabar/Oleg engine-прогонов в этом Gameplay review нет. CI wrapper теперь зарегистрирован; полноценную common CI/remote GitHub CI приёмку этот отчёт не выдаёт.

## Native визуальная проверка

Непосредственно осмотрены7 новых contact PNG: guard/active/recovery hurt/fatal и projectile reaction. Они показывают реальную enemy attack pose и own hit/fall, включая dead overlay; новой ложной block/counter подачи нет. Earlier component review уже осмотрел все26 baseline фазовых PNG; прежняя production presentation неизменна, fresh baseline paths повторно проверены численно. Текущий native набор содержит33 actual screenshots, но reviewer не заявляет повторный осмотр всех33.

Из настоящего MP41280×720,60fps,1113 кадров/18,55с извлечены10 немодифицированных кадров, все непосредственно осмотрены. Guard/active before-hit → hurt, три fatal fall и projectile aftermath согласованы с actual receipts и непрерывным movie trace. Frame index/PTS сохранены в `video-frame-inventory.json`; game physics tick не подменяется video frame number. Fixed60 MovieMaker не доказывает live FPS, аппаратную latency или субъективную реакцию человека.

GP-TIM-PRES-01 закрыт для этих controlled production contacts. Paused AI/declared placements не являются живым natural encounter, доказательством баланса уклонения или human gameplay feel. Full P06/prime/context-specific art, художественный audio/listening, Windows native и остальные phase gates остаются вне решения. Открытых Gameplay findings внутри принятого компонента нет; нового remediation ticket не требуется.
