# Mission Design Specification — единый контракт

Статус: DRAFT / NARRATIVE_REVIEWED / LEAD_APPROVED / IMPLEMENTED / PLAYTESTED. Эти стадии не взаимозаменяемы. Заполненная MDS не является готовым уровнем. Перед массовым производством Lead принимает все21 основных MDS; изменения принятых фактов требуют отдельного narrative review.

## Идентичность и сюжет

Стабильные chapter_id/event_id, presentation/chronology/period/timestamp_status и POV копируются из canonical registry. Перечислить неизменные факты/намеренное заблуждение/раскрытие, входящие prerequisites, существующие решения D01–D06 и выходящие flags. Не создавать точную дату вместо production_pending. Для optional secret отметить CANONICAL_CONCEPT или PROPOSED; proposal не регистрируется в runtime без review/migration.

## Обещание игроку и уникальность

Одна конкретная геймплейная идея, контраст с предыдущей/следующей главой, отличимая роль героя. Сравнить с минимум двумя похожими MDS: topology/цель/encounter sequence/контекст/взаимодействия. Ретайм той же арены, новые имена/HP/количество врагов не считаются уникальностью. Revisit/другой POV оправдывается новой информацией и задачей, а не повтором для длительности.

## Карта и постановка

Таблица зон: zone_id, bounds в логических пикселях/размер сетки, входы/выходы/двери, укрытия/интерактивные объекты, камеры/видимость, safe checkpoint. Отдельно граф связей и последовательность комнат/обходов с conditions. По каждой зоне — план координат enemy spawn/patrol/cover/telegraph, archetypes, player kit/context, цель/поражение. Боссы только если предусмотрены/отдельно approved: фазы, читаемые предупреждения, контрходы, окна уязвимости; не HP sponge. Расположение на бумаге помечается DESIGN_NOT_RUNTIME_TESTED.

## Ритм главы

Вступление→развитие→кульминация→завершение; для каждого этапа действия/угрозы/смысл/переход. Несколько содержательных разных encounters у основных боевых глав; короткий мем не растягивать. CyberX и PRIME-комплекс многоэтапны. Указать реальные способности героя и их prerequisites P06; медленный Якудза требует напряжённого побега/обстановки, а не пустой ходьбы.

## События и состояние

Триггер/телеграф/условие/сброс для lights/reinforcement/route/POV/goal changes; survival-critical события воспроизводимы при retry. Цели победы/поражения, условия запрета скрытого тупика, возврат после смерти, checkpoint/save/load. Canonical event ledger и временное состояние попытки раздельны; replay не повторяет reward/разблокировку. Все необходимые предметы/ключи имеют альтернативный достижимый путь или доказанный порядок.

## Диалоги, сцены и музыка

Список dialogue resource IDs, говорящие/эмоции/блокирующие действия, cutscene beats/skip-seen/переходы. Короткие естественные реплики; важную сцену не сокращать ради KPI. Exploration→Tension→Combat→Aftermath отображаются на существующие EXPLORE→SUSPICION→COMBAT→CLEAR. Нужны музыка/стемы/ambient/cues и transition/retry/duck rules; отсутствующие ассеты маркируются REQUIRED_NOT_CREATED, не объявляются готовыми по имени. Новые аудиофайлы проходят decode/signalQA и listening.

## Продолжительность и метрики

Планируемый диапазон первого прохождения — гипотеза с обоснованием содержанием, а не таймером. Отдельно actual first-play walltime, deaths/retry, бой/сюжет/перемещение/пауза/AFK, маршрут/skip-seen/secret participation, размер выборки/разброс. По кампании цель420–540мин, не сумма взаимоисключающих финалов/100%секретов. Не вводить ожидание/пустые комнаты/HP inflation для достижения диапазона.

Фиксировать Input event→accepted action/первый видимый отклик отдельно от намеренного windup; physical keyboard latency только при настоящем замере. Time-to-restart, интервалы без значимого действия, причины/частота смертей, wall-frame p50/p95/p99 и пики, реальные музыкальные переходы. Headless/fixed-fps/physics delta не renderFPS. Порог и условия измерения фиксируются после baseline до acceptance run.

## Ассеты и зависимости

Реестр требуемых original tiles/props/actor animations/NPC reactions/portrait expressions/VFX/music/SFX/UI с license/provenance/статусом. Shared refs считать честно. Source generation, art approval, runtime validation раздельны. Новые механики только при доказанной необходимости; перечислить переиспользуемые системы и конкретные пробелы.

## Проверки и независимые gates

По каждому encounter: проходимость всеми разрешёнными путями, geometry/LOS/pathfinding/collision clearance, безопасные spawn/telegraphs, отсутствие deadlocks. Save/reload/retry/skip/cancel/death и once ledger; Full/Reduced/settings invariance; route/ending reachability. Нужны real Input/native playtests и build checks, independent Narrative/Gameplay/ART/QA/Lead. Перед каждой стадией перечислить незакрытые Critical/High и precise remediation; шаблон сам ни одного PASS не выдаёт.
