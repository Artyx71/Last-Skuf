# P05 — контракты реализации (автор)

Основание: STORY_SPEC §§3–6, GAMEPLAY_SPEC nonlinear/replay; принятый CH01 resource. Только CH01 имеет scene. Registry задаёт 21 slot, 43 известных event definitions (21 completion, 3 dialogue, 6 decisions, 13 optional records). Ending commit IDs отдельно типизированы API `finish_story`/`finish_overlay`. Это инфраструктура будущего производства, не 21 готовая карта.

## Хронология и осторожные решения

CH01 `EV_CH01_SERVICE_ESCAPE`, YAKUZA, `2023-10-14T22:18:00+03:00` неизменны. Для остальных глав спецификация прямо не закрепляет timestamps (§9): period+relative chronology заданы предварительным порядком slots; timestamp пуст и production_pending. Presentation хранится отдельно и может переставляться без смены причинности. POV-ретеллинги перечислены в одной canonical chapter/event definition, а не создают копии фактов. Валидатор запрещает неизвестные/повторные ID, циклы, недостижимость entry, backwards dependencies и совпадение actor/period/chronology в разных местах. Временной интервал прогулки Тимки остаётся требованием P07: CH11 не получает выдуманного времени. Точные минуты будущих сцен потребуют Narrative signoff.

## D01–D06 и последствия

| ID / глава | accept | refuse / absent | видимая будущая развилка |
|---|---|---|---|
| D01 /10 | kimono_truth; Olezhka bond +1 | explicit false; bond -1 / absent без изменения | Olezhka access vs independent entry в V |
| D02 /12 | pasha_shared_evidence+pashas_backup; Gabar-Pasha +1 | explicit false; -1 / absent без изменения | backup preserved + exposure risk vs sale exposure/trust lost vs no support; escape12/16 |
| D03 /6 | ryzhik_warned; bond +1 | false; -1 / absent без изменения | ally safe vs rival exposed vs unresolved в13/18 |
| D04 /14 | verified open_source_origin+gabar_exonerated | explicit refusal без proof / absent | public cleared vs questioned в18 |
| D05 /9 | secure tegas_phone | explicit refusal без device / absent | отдельный EV_PHONE_DECODED в14; independent corroboration в20 |
| D06 /17 | accepted responsibility | explicit false / absent | alternate climax eligibility21 |

Typed APIs не читают текст диалогов. Decisions допустимы во время entry своей главы, до её completion, только в scenario domain для ещё не выпущенных глав. Once first choice записан, противоположный ответ запрещён даже в replay. Повтор того же ID/value успешен без записи/награды. Три специальных concealment факта — D01=false, D03=false, D06=false; минимум два из трёх — осторожная конкретизация «repeatedly». Неустановленные choices не считаются false.

D05 двухступенчат: secure09, decode14 требует phone + verified project history (D04). Добыча illegal_operations: decode14 либо проверка transfer witness11 + founding_records19 в20. Это консервативная связка улик, не обвинение по одному переводу15000₽. Optional founding/witness records — не готовые сцены.

## Концовки — eligibility и планы

`routes.json` содержит composable all/any/not/eq over declared paths. WIFE_CALLING всегда default/eligible. Остальные primary eligibility только после CH20 (entry21): BROTHERHOOD точно kimono_truth + responsibility + illegal_operations; FAMILY_BUSINESS требует ≥2 explicit concealments и отсутствие **обеих** ключевых illegal_operations/founding_records. Отсутствие остальных улик само по себе Family не открывает. Primary completion возможен после CH21; первый маршрут блокирует другие primary commits.

REAL_PRIME не заменяет primary: только post-story overlay, пять evidence + все пять утверждённых secret records + kimono_record + decoded phone. «Secrets/side stories» не перечислены исчерпывающе в spec: выбран более строгий вариант — все пять; Narrative reviewer может потребовать уточнение. Tega dream требует три memorabilia из03/09/14; секретные истории не добавляют canonical time/place claims. Overlay может следовать любой доступной primary classification.

Планы задают разные entry/escape IDs21A/B/C, permanent relationship outcome, final dialogue ID, ≥2 character epilogue outcomes; отдельно вычисляют ally entry, supplier risk, archive escape, clearance18, proof20 и exposure vs clue rescue. `content_available=false` у всех финальных маршрутов. Никакие cinematics/bonus scenes не выданы за реализованные.

## Сохранения и интеграция

Один StoryState service владеет campaign store schema2: ordered history и строго восстановленные ledger/flags/evidence/relationships/choices/secrets/chapter_complete/unlocks/endings/reward-count. Полная replay-validation обнаруживает подмены derived fields, лишние/пропущенные поля, неверные types/ranges/versions и невозможный порядок. JSON целые читаются Godot как float; допускаются только finite whole numbers в точном диапазоне, bool не приводится к числу. Publication in memory только после flush+close+same-directory rename. Не заявляется fsync/power-loss гарантия сверх Godot FileAccess/OS rename.

Миграция читает ChapterProgress v1 и DialogueDirector v1 и пишет только новый story_v2 файл. Lab P03 ledger не объявляется canonical CH01: импортируются только три известных CH01 dialogue IDs и completion. Старые bytes/deaths/bestscore/checkpoint/seen/history/options не переписываются миграцией. Некорректный/newer/partial файл сохраняется с write disabled; неподтверждённый .tmp не принимается как готовый save. Ошибка миграции не публикует частичный state.

DialogueDirector остаётся владельцем presentation/seen, ChapterProgress — P04 checkpoint/deaths/bestscore; они не являются вторым story engine. Service слушает типизированный finished(scene_id) и синхронизирует соответствующие ledger ID, затем реальный mission outro пишет story completion. Порядок: legacy completion, затем story commit; при втором failure игрок повторяет F, а при следующем открытии resume_progress восстанавливает pending story commit из durable P04 completion. Это recoverable two-file handoff, не multi-file transaction. Нет повторных damage/score engines; CombatSystem и contact clocks неизменны.

Replay — fork памяти, first facts заблокированы, новые sandbox facts не попадают в canonical файл. P04 checkpoint/deaths/bestscore продолжают свою прежнюю работу во время replay; canonical story reward остаётся1. Russian journal показывает доступность/завершение CH01 и честное «в работе» для20slots, без технических schema/ID в обычном UI. Enter запускает CH01 как прежде; J/F4 открывает журнал; F1–F3 и mission/lab controls сохранены.

## Граница доказательств

Автоматическая exploration — две явно описанные exhaustive partitions, не все interleavings/полная кампания. UI/CH01 Input replay проходит реальные controllers/AI/collisions, содержит10actual deaths, повторный вход у checkpoint, seen-skip и отдельный process reload. Headless не является screenshot/listening/native Windows. Хост запускает rendered/movie/Linux/Wine на final hash; независимые Narrative/QA/Lead — после автора. Self PASS/decision отсутствует.
