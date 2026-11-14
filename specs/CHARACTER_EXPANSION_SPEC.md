# P06 Character expansion — обязательный контракт

См. planning/P06_TASKS.md и независимый reports/phases/P06/scope-review-initial/contract.json. Все критерии ниже обязательны; план и наличие PNG не являются приёмкой.

- Character definition: actor_id/display_name/portrait expressions/frames/move/equipment/ability/context и finisher profile. Unknown ID/emotion/context отвергаются. Existing Yakuza path/CH01 сохраняются.
- Input→windup→contact→recovery единым physics clock; графика отображает фазу, не начисляет damage. Каждый action имеет eligibility, target/range/facing/LOS/environment, cooldown/cost/cancel/reaction/audio IDs. Повтор callbacks/reset/reload не повторяет damage/kill/reward.
- action8/direction: melee windup/contact/recovery, interact, hurt, down, death, ranged contact. finisher8/direction: shared windup, пять разных category contacts, shared recovery, signature contact. Shared poses явно указаны; additional movement requires actual drawn frames. Death hold и static portrait не называются многофреймовой анимацией.
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

Production actor construction must prepare the complete world/action/finisher frames and validated per-frame clothing annotations before removing the current actor. Only after successful preparation: reset CombatSystem → invalidate old scene owner → open registered fixture → bind prepared actor. Resource absence rejects selection; no Yakuza substitution or assert-only state mutation.

Ordinary melee/signature attacks must pin the live scene action authority (actor/context/fixture/generation/scene instance) and signature ability identity at start. Revoke pending motion/contact after invalidate/reopen/owner replacement, including active-window remaining targets. CombatSystem rechecks the optional source authorization before EACH melee recipient; no later same-tick target receives revoked damage. Finisher authority remains separately pinned and checked by the existing core.

## Ограниченная контратака Олежки (training sandbox)

F открывает видимый guard с windup0.28s, active0.10s, recovery0.34s и cooldown2s. Защита допустима только в интервале единого action clock0.06–0.26s, перед персонажем (dot>=0.65), на расстоянии1–40px, с LOS и действующей scene authority. Только один настоящий hostile melee contact категорий unarmed/blunt/sharp может быть отражён. Пули, добивания, legacy direct contacts, удары сзади/сбоку/вне окна проходят обычным путём. Промах не планирует урон; отмена, смерть, reset и смена authority отзывают pending counter.

CombatSystem резервирует прежний once-token incoming contact ДО opt-in defense hook. Успешная защита не создаёт damage/score/blood event; отдельный bounded defended event не является попаданием. Контакт переводит тот же physics action clock в authored signature contact и ставит отдельный Core melee counter (damage1, stun0.45, reach21/radius14). Урон ответа проверяется per-recipient следующим physics turn; это не прямой callback damage. Второй одновременный incoming contact уже не защищён и может прервать queued ответ. Тест длинного удара использует явно объявленный QA reach34 вместо базового enemy18 для фактического collision вне defense range; он не выдаёт противнику новый сюжетный набор.
