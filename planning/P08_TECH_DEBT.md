# P08: явно отложенная дополнительная полировка

Статус всех пунктов ниже DEFERRED_NOT_IMPLEMENTED_NOT_ACCEPTED. P08 не запущена; текущий stop-limit P06 сохранён. Новое прямое решение владельца automation/decisions/P06_NPC_VISUAL_POLISH_TO_P08.json разрешает узкий перенос оставшейся визуальной NPC C09 в P08-NPC-STYLE-01. Собственные player-механики/анимации/звук/HUD и базовые NPC реакции/correctness остаются обязательными в P06.

| ID | Дополнительная работа | Критерии закрытия |
|---|---|---|
| P08-VAR-01 | Больше декоративных вариантов уже принятых blood/decal эффектов | Реальные новые оригинальные source/PNG/hash/license; native Full/Reduced/decals-off сравнение; неизменные hitboxes/damage/score/story; lifetime/caps и wall-frame performance; independent ART/QA. Пока новых вариантов нет. |
| P08-VAR-02 | Необязательные дополнительные версии уже работающих персонажных добиваний | Только после принятого базового набора всех7 в P06; собственные дополнительные рисунки/переходы, ясный отдельный счёт shared refs; реальные contact/reaction/audio/timing/cancel/settings проверки и independent ART/GAMEPLAY/QA. Одну анимацию с новой скоростью не считать вариантом. |
| P08-VHS-01 | Дополнительная декоративная VHS стилизация | Читаемые hit telegraphs/HUD/диалоги на native разрешениях; off/reduced options; боевые state/receipt трассы совпадают; отдельное wall-frame измерение и independent ART/QA. Текущие доступные toggles сохраняются. |
| P08-NPC-STYLE-01 | Оставшаяся hero-linked визуальная индивидуализация NPC C09: contact/release/grip artwork, presentation routing/role maps | HIGH, до итоговой P08/release приёмки. Точные исходники, scope, зависимости и независимые критерии ниже. Owner deferral не принимает ранее отклонённый арт. |

Обязательные Timka present/prime стойки/действия, Ryzhik roll transitions, Pasha resources HUD, собственный sound design, player FIN и базовые NPC реакции остаются P06. Только дополнительные hero-linked визуальные NPC styles перенесены прямым решением владельца; это не приёмка их реализации. Все debt items открыты.


## P08-NPC-STYLE-01 — прямой перенос владельца, не выполненная работа

Решение: automation/decisions/P06_NPC_VISUAL_POLISH_TO_P08.json. Причина: владелец считает прототип достаточным для завершения P06 после обязательной общей проверки и просит перенести оставшуюся визуальную детализацию NPC в P08. Игровая реализация не меняется этим документом. Начать P08 сейчас или автоматически принять P06/P07/релиз не разрешено.

**Объём.** Новые hero/context/style/action-variant связанные contact/release/grip рисунки NPC, обслуживающий их presentation descriptor/clip/role routing и новые clip-specific source/native reviews. Собственные player FIN/способности/звуки/HUD не переносились. В P06 остаются принятые category NPC sprites/FSM и обязательные реальные проверки контакта/стан-падение-смерть/приоритеты/once/настройки.

**Сохранённый незавершённый материал.** assets/source_art/npc_styles/gabar/partial-source-ledger.json:19retainable новых wholeposes+1eligible existing P04 release ref+4missing shooter contact drawings. Это не20новых рисунков и не полный source пакет. Source ART FAIL985592e6/073430cd, feasibility ART_BLOCKED18dfe9a8 и actual generator moderation request09e29275 сохранены без правок. Other hero-linked NPC sets также не произведены. План156wholeposes был стартовой оценкой, не доказательством объёма или фиксированным числом для PASS. Исторический подробный план: planning/P06_C09_TASKS.md.

**Зависимости и ограничения.** P08 может исполняться только после своих обычных phase gates/разрешений; P07 production/readiness/21MDS guards сохраняются. Для новых GPU/sprites сначала нужен доступный допустимый art workflow и свежий независимый source ART PASS. Тот же отклонённый generator request не повторять автоматически; rawphotos/расходы/публикация — по прежним разрешениям. Целые существующие рисунки можно переиспользовать только с явным ledger и положительной оценкой совместимости; не переклеивать кисти/оружие и не выдавать refs за новые poses.

**Критерии закрытия.**

1. Настоящие новые исходники/runtime sheets со всеми source/prompt/hash/license, realunique/shared ref ledger, читаемым оружием и постоянной ведущей рукой, правильными4проекциями/пиксельной сеткой/pivots/clothing anchors. ART подтверждает реальную совместимость contact/release/grip с парой player/NPC, не только число PNG.
2. Descriptor закреплён за actor/context/style/actionvariant/category/archetype/facing и exactepoch/action/target. Старый Core остаётся единственным владельцем damage/score/cost. Не добавлять способности/силу presentTimka и не расширять Timka84/excludedequipment; Якудза остаётся слабым.
3. Health/dead/layer0/score наступают на прежнем contacttick; новый release/terminal role map не задерживает смерть/не воскрешает NPC. Reentrant presentation callbacks не повреждают новый encounter, free/reset/cancel/revoke безопасны. Legacy0/1/2 и исходные targeted regressions сохраняются.
4. Реальная матрица новых clips:25allowedhero/category×3NPC×4dir×FullReduced, дополнительно signature variants (counter/roll/clinch/prop/projectile), контроль паузы/death/retry/once/settings. Planned600new-style cases не являются уже выполненными. Визуальная опция не меняет damage/hitboxes/score/story/RNG.
5. Ограниченные native paired captures/видео с actual contact receipts и source/target roles, directional geometry/depth/оружием/clothing. Lifetime/caps и реальные wall-frame performance; current Windows/Linux exports/runtime насколько доступны с явным Wine/nativeWindows разграничением.
6. Независимые ART/Gameplay/QA затем Lead на frozen bytes. До такого решения status остаётся DEFERRED/FAIL/BLOCKED; source-only/component reports не закрывают полный P08/release gate.
