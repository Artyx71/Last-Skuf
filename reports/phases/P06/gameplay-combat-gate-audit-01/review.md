# Независимый Gameplay GAP audit — P06 combat gate

**GAPS_IDENTIFIED_NOT_PHASE_VERDICT. Все7 героев ещё не готовы к новому combat gate.** Существующие Core, выпад Габара и парирование Олега следует сохранить. Основная работа — недостающие способности/представление/ресурсы, индивидуальная матрица добиваний/звуков/реакций и полное доказательство новых критериев. Дополнительно найден HIGH статический путь возможного campaign-добивания Якудзы; движком в этом аудите он не воспроизводился.

Reviewer `/root/art_olezhka_recovery` независим от автора. Это предреализационный bounded audit по P06-CBT-01..10, **не full-phase review и не расход phase attempt**. WORK только прочитан, выводы/снимки записаны в этот ROOT reports каталог. Не запускались Godot/native/display/builders, Controller/Git/network/generator. Новых engine tests0. ART/audio/listening/ability/full-phase/merge approval и разрешения генератору этот документ не выдаёт.

## Основание и действительные evidence

Сохранены точные38 text-source snapshots с SHA, включая обязательный контракт, controller/Core/HUD/policy/AI/audio/tests и CH01. Это point-in-time audit, не полный frozen phase checkout. Во время чтения в P06_COMBAT_ACCEPTANCE.md добавилась только ссылка на P08_TECH_DEBT; начальный текст сохранён, followup и debt сохранены отдельно. Боевые критерии этим дополнением не изменились. Strict Timka compact loader находится в работе и данным аудитом не принимается.

Исторические native evidence прочитаны напрямую, без повторного прогона:

| Набор | Реальные записи | Ограничение |
| --- | --- | --- |
| Gabar combat native02 | head8f30222…; live194/194, movie126/126;68PNG,37contacts;79 artifact hashes совпали | Ранее ограниченный controller/native компонент, не все7 и не текущее exact-head proof |
| Oleg combat native01 | head7a99727…; live248/248, movie166/166;82PNG,57contacts,13defenses;93 hashes совпали | Bounded guard/counter/finisher, без UX/слуховой/performance/полной фазы |
| CH01 engine replay P04 | Actual Input, route_warps0, kills0/score1000, distraction и10retry checks сохранены | Показывает достижимость слабого no-kill маршрута, но не испытывает V после stun |
| P04G technical-final04 | Сохранён actual technical replay/state coverage | В самом отчёте HEADLESS_TECHNICAL_NO_RENDER_EVIDENCE: не называю его новым native/visual proof |

Просмотрены7 выбранных оригинальных native PNG поз G/O (включая полный HUD) и две собственные contact-sequence diagnostics. Все172 перечисленных G/O artifact hashes сверены; это не означает нового визуального просмотра всех150PNG или ART приёмки. `evidence-analysis.json` содержит raw summaries/selected check details/parry→counter examples и206 hashes actual source/assets/evidence. Historical source labels не подменены текущим кодом: у Gabar изменены controller/Core/replay, у Oleg — readiness-wrapper controller; Oleg Core и replay byte-exact совпадают с historical recording. Поэтому полный current-source gate требует своих будущих evidence.

## Что сохранять и переиспользовать

**Олег уже защищается ДО receive_hit.** В snapshot `combat_system.gd:205` после epoch/once-token reservation hook `defend_melee_contact` вызывается до damage_events/receive_hit/contact_committed. Успех возвращает отдельный defended event с damage0; входящий hit не даёт blood/score. `character_player.gd:199` ограничивает защиту action guard/frame0, clock0.06–0.26, живым hostile melee unarmed/blunt/sharp, одним контактом, front dot≥0.65/range1–40/LOS и live authority. `_start_training_counter` не планирует удар при нажатии F. Только успешная защита переводит тот же clock в contact и ставит отдельный Core counter; это не hurt→counter и не бессмертие после смертельного попадания.

Сохранённые реальные пары: parry ticks294/339/384/429 → отдельные counter hits295/340/385/430, разные attack IDs, player contact frame1. Replay проверяет early/late/rear/side/projectile/finisher/direct/wrong-category/lethal miss, один из двух одновременных контактов, revoke/reset/cancel/options и Full/Reduced. Переписывать этот механизм или переносить его после receive_hit нельзя. Остался UX-gap: HUD `character_lab.gd:93` показывает только «приём2.0с» cooldown; явного readable active-window/success/whiff/recovery состояния нет. Наличие guard-рисунка не заменяет новую Gameplay-приёмку читаемости окна.

**Габар уже имеет настоящий swept выпад.** `character_player.gd:99/167`:210px/s только в contact phase, move_and_collide, windup0.18/active0.12/recovery0.30/cooldown1.6; один stamped Core attack damage1/stun0.45/reach19/radius14. Snapshot Core проверяет LOS и authority для каждого recipient. Native saved checks показывают24.5px actual travel во всех4 направлениях и9.002px до стены/x611.990; contact poses совпадают с event frame1. Есть cancel/hurt/death/active-window и same-tick authority revoke tests. Нужна итоговая читаемость/точная current-source проверка; признаков необходимости переписывать весь выпад нет.

**Core/AI/effects пригодны для расширения.** Once receipts/encounter epoch, один source action clock, frozen definition/live authority, precontact cancellation, projectile ray sweep и actual contact presentation существуют. EnemyFSM имеет telegraph/attack/recovery/hurt/stun/knockdown/death/finisher reaction, три архетипа и dead priority; begin_finisher пока выбирает category reaction. Impact — presentation-only held poses, отдельный cosmetic RNG, caps48particles/40decals, TTL0.32/18s, shake≤3px и existing settings toggles; физические clock/hitboxes не должны зависеть от них. Реальная environmental geometry/LOS/enabled/existence регистрация уже есть в Core. Расширять эти seams, не создавать второй damage/score pipeline.

## Gap matrix обязательных требований

| ID | Состояние | Что ещё обязательно |
| --- | --- | --- |
| CBT01 | Частично G/O + baseline Yakuza | Матрица своих poses/contact/recovery/cue/NPC reaction всех7; реальные дополнительные наборы и индивидуальный sound design. Timings/style labels не являются завершением. |
| CBT02 | Parry/counter реализованы | Clock-derived readable-window/успех/промах/recovery feedback и независимая UX-приёмка; сохранить правильные negative cases. |
| CBT03 | Timka contexts не реализованы | Present disengage/prime clinch, различимые stance/movement/actions; complete compact resources/sockets/source, исправление environmental family. Shared WORLD и speed84/118 недостаточны. |
| CBT04 | Pasha ability/HUD отсутствуют | Настоящий moving aimed shot; конечные ammo/replenishment/cooldown/recovery и понятный HUD; повтор/empty/interruption/death/reset tests. |
| CBT05 | Слабый маршрут есть, static scope gap | Закрыть/проверить путь legacy V в CH01, сохранив training finishers и escape/no-kill/distraction. |
| CBT06 | Выпад преимущественно готов | Final-current native contact/LOS/wall/cancel/readability доказательства; использовать имеющийся код. |
| CBT07 | Ryzhik roll отсутствует | Реальные промежуточные drawn roll кадры, collision route и ограниченное close-range control окно, finite recovery/cooldown/cancel; без teleport/неоговорённой неуязвимости. |
| CBT08 | Tega handler отсутствует | Реальное действие с зарегистрированным объектом через существующий Core; исчезновение/disabled/LOS/authority/cancel/once. Dream cannon внеP06. |
| CBT09 | Baseline FSM есть | Связанные actual hero/category/archetype reaction/contact traces и проверка attack/fall/death для новой хореографии. Не каждый подходящий shared category reaction требует бессмысленного дубликата PNG. |
| CBT10 | Компонентные регрессии есть | Вся seven-hero/both-context матрица once/death/restart/settings/effect caps и wall-frame performance/exports/CI на финальном source. |

Полные actionable tickets с точными путями/fix/acceptance — decision.json; per-requirement matrix — requirements.json. Все HIGH здесь блокируют готовность нового gate, но этот документ не превращается в formal phase FAIL.

## HIGH GP-P06-YAKUZA-SCOPE-01 — static path, runtime NOT CONFIRMED

Точная цепочка snapshot: `missed_fight.gd` наследует CombatLab и production CombatPlayer; `input_bindings.gd:15` всегда регистрирует V→finisher. В CombatPlayer defaults weapon/category=unarmed, `_physics_process:256` обрабатывает V, `try_finisher:273` вызывает Core.start_finisher. CombatSystem всегда загружает global finishers.json, а `eligible:291` проверяет earned stun/knockdown, geometry и equipment, но для legacy actor без resolve/can_use hook не проверяет campaign/config/kit. `_finisher_authority` возвращает пустой legacy authority как прежний путь. Default unarmed совпадает с unarmed definition. CH01 shove имеет stun1.15 и global finisher windup0.82: это достижимая статическая комбинация при правильной геометрии, не доказанный этим аудитом runtime exploit.

`CombatLab.select_equipment:445` запрещает переключение инструмента вне training config, но не запрещает уже default unarmed start. `config_path==CONFIG_PATH` в `_apply_hit:235` ограничивает только+100finisher score, а не убийство; Enemy.receive_hit всё ещё уменьшает health/увеличивает kills. `Profile.resolve_finisher(yakuza,campaign)=={}` unit test проверяет чистый resolver, которого настоящий legacy CombatPlayer не вызывает. Existing CH01 replay показывает безопасный маршрут и запрет ranged/F2, но не pressesV после earned stun.

Автору уже передано: отдельно воспроизвести реальный CH01 earned-shove-stun→V и direct Core entry; при подтверждении закрыть доверенную scope eligibility **до reservation/contact**, сохранить все5 training categories/долгие interruptible windup и слабый no-kill маршрут. Не хватит скрыть кнопку/менять текст HUD/обнулять score. Проверить no job/kill/score/late callback после отказа/reset/load. Автор подтвердил получение статического finding и назначил отдельный engine regression; результат этого будущего прогона здесь не выдуман.

## Декомпозиция следующей работы

1. Узкий scope regression/fix CH01 без усиления Якудзы; reusable parry/lunge не переписывать.
2. Завершить Timka84 compact/source/environment/readiness и обе context abilities. Для нового visible stance/motion gate дополнительные genuine drawings учитывать отдельно, если принятый base не подходит; одна скорость не заменяет различие.
3. Довести composable Pasha moving-fire/resource HUD, Ryzhik roll и Tega object action. Blanket `_movement_multiplier==0` для любого special должен расширяться по конкретной способности, сохраняя ограничения G/O. Стоимость/контакт/прерывание вести единым clock; определить судьбу уже выпущенной пули при death/reset, не дублировать ammo/contact.
4. Собрать actual authorized hero/category matrix:25 positive pairs×4directions=100 planned cases, плюс present/forbidden-category/campaign denial. Это план покрытия, **не100 выполненных тестов**, и не выдача всех5 категорий каждому. Source96/Timka84 отдельно остаётся действующим контрактом. Shared refs внутри своего набора честно учесть. Для звука возможен собственный accent поверх подходящей category основы, если он действительно отрендерен/прослушан; общий cue или pitch label сам по себе не выполняет требование.
5. Новый frozen source → фактические Input/native temporal/state/HUD/audio evidence, full settings/lifetime/caps/regressions/wall-frame performance/builds → независимые ART/Gameplay/QA/full Lead/mandatory CI. Только отдельный полный gate может разрешить дальнейшие guarded действия. При недоступности фактического слушателя artistic audio gate отдельно BLOCKED, metadata/signal QA его не заменяет.

P08 debt разрешает только дополнительные декоративные варианты поверх принятой базы. Обязательные собственные combat-анимации/звук/реакции, Timka distinction, Pasha HUD и остальные mechanics изCBT01..10 вP08 не переносятся. P07/P08/release этим аудитом не запускаются.
