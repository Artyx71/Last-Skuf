# P02 — handoff от независимого reviewer

Prerequisite: P01 PASS attempt2. Это следующий ограниченный combat prototype по planning/PHASES.md, не P04 mission и не campaign expansion. Исполнитель создаёт planning/P02_TASKS.md с requirement/test IDs до реализации и ведёт отдельную phase branch/PR; merge/release отдельно не разрешены.

| Атомарная задача / commit | Результат | Проверяемая evidence |
|---|---|---|
| P02-01 / combat contract | Зафиксировать минимальные damage/attack/projectile/hitbox contracts и collision layers; определить test-kit параметры, не выдавая их за утверждённый final balance. | Небольшие data definitions и tests на damage, hit/miss, повторное попадание/повторный damage, физические препятствия. |
| P02-02 / player combat kits | Нативные melee/ranged test kits с читаемым input/feedback; responsive weak Yakudza без случайного unavoidable failure или внезапной сверхсилы. | Actual engine input/replay и integration tests; world collision и направление attack согласованы. Не создавать универсальный final kit всем семи героям. |
| P02-03 / three enemy archetypes | Минимальные patrol, rusher, shooter FSM с читаемым обнаружением, угрозой/телеграфом и line-of-sight. | Детерминированные state-transition/collision tests; стены реально блокируют движение/стрельбу как задано контрактом. |
| P02-04 / death and restart | Lethal loop, сброс encounter snapshot/seed и быстрый возврат управления после смерти. | Серия actual deaths/retries с измеренным cached death-to-control target <1s на development hardware; враги, RNG и необходимые state поля восстановлены. Не обещать производительность других ПК. |
| P02-05 / weak-Yakudza route | Малый технический arena/escape маршрут на существующем оригинальном sprite, завершимый без уничтожения всех врагов; fair telegraphed threats. | Native input replay прохождения no-conventional-combat пути и failure/retry, screenshot/video; это prototype geometry, не финальная карта/арт P04. |
| P02-06 / regression and gate | P00/P01 regressions плюс combat/AI/reset suite, Linux/Windows sandbox exports и настоящий доступный CI job. | Logs с exit codes, hashes actual builds/video, Linux runtime, Windows runtime только при реально доступной проверке; independent P02 review. Сохранить P00/P01 evidence отдельно. |

Не включать в P02 adaptive music/dialogue production P03, final vertical slice P04, другие шесть героев или 21 главу. Gore/VHS/save/story tests добавлять при соответствующей реализации, без фиктивных claims. Raw photos остаются вне Git/exports; показанное одобрение P01 не расширяет public/voice права.

ART-P01-01 (MEDIUM jitter) и META-P01-01 (LOW atlas review-note reproduction) остаются nonblocking tickets. Не переписывать утверждённые hashes молча: после затрагивающей ассеты правки — новый inventory/evidence и ограниченный re-review. Для будущего CI заранее учитывать hosted billing limitation: постоянного runner нет, прошлый session runner/variable удалены.
