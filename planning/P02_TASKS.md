# P02 — боевой прототип

Prerequisite: независимый P01 PASS attempt 2; handoff в reports/phases/P01/reviewer-attempt2/P02_HANDOFF.md. Не миссия P04 и не расширение кампании.

| ID / requirement | Атомарный результат | Проверка |
|---|---|---|
| P02-01 / GP-01 | Данные attack/damage/cooldown, collision layers, native melee/projectile | T-CMB-001: hit/miss, один damage на атаку, стены, реальные physics queries |
| P02-02 / GP-02 | Слабый Якудза, ограниченный импровизированный приём/отвлечение; отдельный учебный набор оружия | T-CMB-002: input + aim, kit restrictions; никакой случайной обязательной неудачи |
| P02-03 / GP-03 | FSM patrol/rusher/shooter; видимость и предупреждение перед атакой | T-AI-001: обнаружение, LOS, pursuit, telegraph, projectile collision |
| P02-04 / GP-01 | Lethal encounter и полный deterministic restart | T-RST-001: минимум 10 смертей/возвратов, сброс snapshot/seed/state, измерение cached latency <1 с |
| P02-05 / GP-02 | Настоящий путь ухода без убийств в технической арене | T-ESC-001: native input replay от старта до выхода, enemies active, kills=0; failure/retry replay |
| P02-06 / VIS-01 | Оригинальные пиксельные охранники, читаемые атаки/телеграфы | Actual PNG/source/provenance, screenshot + animation recording; не цветные коробки вместо персонажей |
| P02-07 / TEC-01, OPS-01 | Регрессии, Linux/Windows exports, actual CI, независимый gate | Logs/exit codes/hashes; Linux runtime/render, Windows runtime только при наличии среды |

Параметры оружия и AI — контракт прототипа, не финальный баланс. Персонаж по умолчанию остаётся слабым и ориентированным на уход; учебный kit явно отделён от его сюжетного инвентаря. Геометрия полигона — технический стенд, не финальный level art. Новые охранники вымышлены и не используют фотографии друзей. P00/P01 доказательства и сборки не перезаписывать. Диалоги, soundtrack/VHS — P03; законченная миссия — P04.

Владельцем уже разрешены private repo/push без raw фото и image_gen с фото всех; одобрены показанные P01 portraits/world. Public release, реальные голоса, merge, расходы и изменение платежей не разрешены. Постоянного runner нет.
