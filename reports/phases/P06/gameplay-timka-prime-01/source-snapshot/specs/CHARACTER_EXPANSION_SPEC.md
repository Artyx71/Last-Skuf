# P06 Character expansion — обязательный контракт

См. planning/P06_TASKS.md и независимый reports/phases/P06/scope-review-initial/contract.json. Все критерии ниже обязательны; план и наличие PNG не являются приёмкой.

- Character definition: actor_id/display_name/portrait expressions/frames/move/equipment/ability/context и finisher profile. Unknown ID/emotion/context отвергаются. Existing Yakuza path/CH01 сохраняются.
- Input→windup→contact→recovery единым physics clock; графика отображает фазу, не начисляет damage. Каждый action имеет eligibility, target/range/facing/LOS/environment, cooldown/cost/cancel/reaction/audio IDs. Повтор callbacks/reset/reload не повторяет damage/kill/reward.
- Базовая раскладка остальных героев: action8/direction (melee windup/contact/recovery, interact, hurt, down, death, ranged contact), finisher8/direction (shared windup, пять category contacts, shared recovery, signature contact). Для Тимки действует утверждённое ниже исключение84. Shared poses явно указаны; additional movement requires actual drawn frames. Death hold и static portrait не называются многофреймовой анимацией.
- Данные не дают всем героям любое оружие. Timka peaceful_present не выполняет prime grapple; context хранится в доверенной scene definition. Новый sandbox context означает reset fixture. Unknown save cannot authorize prime.
- Девять NPC portrait sets: neutral/angry/surprise/hurt/catchphrase, 160×160, технический alpha/palette/native inspection. Каждая фотография сверяется со своим hash; сырьё не включается в Git/export/reports. World 48×64, pivot24,58, 4 directions; every source cell accounted, bounded palette/alpha/coverage.
- Sandbox dialogue использует отдельное persistent viewing-state и не меняет StoryState, event ledger, campaign unlock/reward или сохранённый resource/line CH01. Проверка вход/выход/process restart обязательна. Audio reuses accepted fictional bleeps without voice identity claims.
- ART принимает likeness/согласованность/реальные анимации; GAMEPLAY — Input, contact timing/readability/cancel; QA — negative cases, settings invariance, effect lifetime/caps, regressions/performance/builds; Lead самостоятельно связывает frozen source и evidence SHA. Никакого author self-PASS.

## P06 sandbox equipment policy (не campaign unlock)

Разрешённые категории ниже задают верхнюю границу. Фактическая категория также требует выданного инструмента, состояния противника, facing/range/LOS и зарегистрированного объекта для environmental. Наличие пяти нарисованных finisher contacts не выдаёт пять инструментов.

| Герой / контекст | Категории |
|---|---|
| Gabar / training | unarmed, blunt, firearm |
| Olezhka / training | unarmed, blunt, sharp |
| Timka / peaceful_present | никаких добиваний |
| Timka / athletic_prime | unarmed, blunt, environmental |
| Ryzhik / training | unarmed, blunt, environmental |
| Tega / training | unarmed, blunt, environmental; cannon отсутствует |
| Pasha / training | unarmed, blunt, sharp, firearm, environmental |
| Existing Yakuza | training как прежде; campaign escape не получает training finishers |

Новый actor resolver обязан реализовать live `can_use_finisher(category)` и `finisher_authority(category)`. Authority содержит actor_id/context/fixture_id/generation/category, берётся из scene fixture, копируется в job и сверяется до contact. При смене actor/context/fixture/generation старый job отменяется даже при разрешённой новой категории. Definition/timing фиксируются один раз; повторная авторизация не меняет contact clock. Resolver без обязательной policy безопасно отвергается. Изменение authority во время cancel_action не оставляет частичную reservation.

Тестовая `tests/fixtures/character_policy_lab.gd` использует прежний визуальный actor только для проверки production CombatSystem hook. Она не входит в playable character factory и не доказывает готовность новых способностей, арта или доверенных production scenes.

`CharacterScenePolicy` читает только registered keys из res://resources/characters/sandbox_scenes.json; API не принимает saved actor/context dictionary. Seven fixtures: six героев + отдельные Timka present/prime. Копии definitions/authority не мутируют scene owner. Reopen даже того же key меняет generation; замена policy instance добавляет отличимый scene_instance. Host CharacterLab всё ещё должен reset CombatSystem перед сменой fixture и не вызывать open из произвольных сохранённых context полей. Наличие компонента и unit fixtures не означает готовность playable factory.

`PixelPresentation` выравнивает только visual child по canvas grid. Body position/collision/action clocks остаются дробными. Native QA обязана подтвердить отсутствие растрового дрожания на half-pixel coordinates и непрерывный Input маршрут без fixture teleport; кадры из отдельных reset poses не доказывают переходы.

Production actor construction must prepare the complete registered context's required frames, validated per-frame clothing annotations and actual implemented ability before removing the current actor. Only after successful preparation: reset CombatSystem → invalidate old scene owner → open the same registered fixture → bind the exact prepared actor/context/ability. Resource absence rejects selection; no Yakuza substitution or assert-only state mutation. Timka peaceful_present requires WORLD/ACTION/disengage, never prime FINISHER; athletic_prime additionally requires its complete FINISHER/clinch.

Ordinary melee/signature attacks must pin the live scene action authority (actor/context/fixture/generation/scene instance) and signature ability identity at start. Revoke pending motion/contact after invalidate/reopen/owner replacement, including active-window remaining targets. CombatSystem rechecks the optional source authorization before EACH melee recipient; no later same-tick target receives revoked damage. Finisher authority remains separately pinned and checked by the existing core.

## Ограниченная контратака Олежки (training sandbox)

F открывает видимый guard с windup0.28s, active0.10s, recovery0.34s и cooldown2s. Защита допустима только в интервале единого action clock0.06–0.26s, перед персонажем (dot>=0.65), на расстоянии1–40px, с LOS и действующей scene authority. Только один настоящий hostile melee contact категорий unarmed/blunt/sharp может быть отражён. Пули, добивания, legacy direct contacts, удары сзади/сбоку/вне окна проходят обычным путём. Промах не планирует урон; отмена, смерть, reset и смена authority отзывают pending counter.

CombatSystem резервирует прежний once-token incoming contact ДО opt-in defense hook. Успешная защита не создаёт damage/score/blood event; отдельный bounded defended event не является попаданием. Контакт переводит тот же physics action clock в authored signature contact и ставит отдельный Core melee counter (damage1, stun0.45, reach21/radius14). Урон ответа проверяется per-recipient следующим physics turn; это не прямой callback damage. Второй одновременный incoming contact уже не защищён и может прервать queued ответ. Тест длинного удара использует явно объявленный QA reach34 вместо базового enemy18 для фактического collision вне defense range; он не выдаёт противнику новый сюжетный набор.

## Утверждённое исключение Тимки:84 исходные клетки

Решение владельца «давай да» после объяснения исключения зафиксировано в `automation/decisions/P06_TIMKA_SUPPORTED_ANIMATIONS.json`. Это изменяет только бюджет и неиспользуемые clips Тимки; остальные герои сохраняют schema1/96. Исторические предложения и FAIL/отклонённый запрос генератору не переписываются. Технический контракт V2 принят как основание реализации, не как готовый код или фазовый PASS.

| Лист / профиль timka_supported_v1, schema2 | Native размер | Клетки/ряд | Старые source columns → packed columns |
|---|---|---|---|
| WORLD | 384×256 |8|0,1,2,3,4,5,6,7 →0..7; прежний PNG byte-exact|
| ACTION |336×256|7|0,1,2,3,4,5,6 →0..6; fire отсутствует|
| FINISHER |288×256|6|0,1,2,5,6,7 →0..5|

WORLD: idle[0,1], walk[2,3,4,5], run[6,7]. ACTION: shove[0,1,2], interact[3], hit[4], fall[5,6]. FINISHER: unarmed[0,1,4], blunt[0,2,4], environmental[0,3,4], special/clinch[0,5,4]. Во всех листах48×64/pivot24,58/4directions;32+28+24=84 actual source cells. Shared references и число уникальных рисунков учитываются отдельно. Нет пустых reserved/дублированных placeholder колонок, sharp/firearm/fire clips отсутствуют.

Strict allowlist по actor/profile/schema/kind/размерам/картам/числу клеток; неизвестное отвергается без legacy fallback. Metadata содержит полный source-column mapping, PNG/master SHA и RGBA SHA всех32/28/24 клеток. Sockets строго привязаны к текущему sheetSHA/profile/числу клеток, находятся на собственной одежде и независимо проверяются статически и в реальном движении. Компактный adopter требует свежего независимого review всех необходимых клеток конкретного листа, hashes всех inputs/artifacts, must_fix[], source-only acceptance; all32-флаг не подходит24/28.

Present: настоящее ограниченное collision-движение назад, guard ACTION0 → собственные четыре WORLD walk-фазы в обратном временном порядке → ACTION2 recovery, с clock/cooldown/cancel/live scene authority, без урона/неуязвимости/добиваний. Это честное reuse, не новые уникальные рисунки; если переходы не приняты ART/GAMEPLAY, нужны дополнительные реальные рисунки. Prime: отдельный настоящий clinch, только unarmed/blunt/environmental, eligibility/once damage/score через существующий Core. Ранее непринятый environmental UP5 остаётся обязательным исправлением после переиндексации.

Factory готовит exact registered context/required clips/sockets/реальный ability до изменения живого боя. Наличие арт-листа не выдаёт способность. Полная P06 требует обоих контекстов, всех6 героев/7 fixtures, независимых ART/GAMEPLAY/QA/Lead и всех build/CI/merge gates. Утверждение84 не снимает ни одного из этих требований.

## Уточнение combat gate всех7 героев

Обязателен specs/P06_COMBAT_ACCEPTANCE.md (P06-CBT-01..10). Индивидуальные finisher animations/sounds/reactions, present/prime differences, Pasha HUD, Ryzhik roll и реальные environment mechanics не считаются выполненными по наличию timings/PNG.
