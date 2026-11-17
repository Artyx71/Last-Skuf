# PROJECT GATES — evidence-based acceptance

## Policy
Every phase has PASS/FAIL/BLOCKED status, decided by `Lead Reviewer` in independent context. Review must compare `specs/` to built artifacts, not trust author claims. Only PASS advances; FAIL loops with finite attempts; BLOCKED escalates only for missing permission, missing platform/software, unresolved creative likeness dispute or inaccessible external tooling. Reports stay in repository; user is not required to ferry them between assistants.

## Definition of done for every phase
- Scope traceable to requirement IDs and test cases, with clear boundary to next phase.
- Relevant code committed, tests run with exit codes and logs, screenshots/audio reviews named, no fake success.
- New generated assets individually inventoried with hashes, source provenance, licensing and whether privacy/likeness cleared.
- Playable build for major milestones: Linux and Windows as declared, or mark platform-specific test BLOCKED without false PASS.
- In-game language/plot/Ossetian phrase checks, user preferences respected.
- Independent lead reviewer `reports/phases/Pxx/decision.json` PASS + signed reasoning + evidence links. Avoid unreviewable green checkmarks.

## Reviewer scoring matrix
| Domain | Must show |
|---|---|
| Gameplay | video/replay and tests prove lethal/readable combat, unique abilities, weak-yet-playable Yakudza, instant reset |
| Story | event ledger, reachable endings, six decisions, POV consistency, complete scenes for committed milestone |
| Art | source dimensions, screenshot in Godot, visual comparison to correct private photo, readable pixel clusters, no generic AI portraits |
| Audio | actual WAV/OGG, listening report, no clipping, loop/transition analysis, licensing provenance |
| Engineering | Godot smoke, lint/tests, exports, save/load migration, performance capture |
| Privacy | raw photos absent from committed/public files, no unapproved upload or publication, fiction disclaimer |

## Exit/stop conditions
- Never mark successful audio generation because a prompt or MIDI plan exists.
- Never mark likeness passed without independent visual examination. Programmatic check is only structural.
- Never mark a Windows runtime test done if only Windows export files were built on Linux.
- Never advance to next phase based on self-generated author approval or if hard-blocking CRITICAL/HIGH issues remain.
- If the current session ends, persist next step in `reports/STATUS.md`; a later Codex run may continue. No promises of background execution.

## P06 combat acceptance before P07

Все P06-CBT-01..10 из specs/P06_COMBAT_ACCEPTANCE.md обязательны. Независимые Gameplay и ART смотрят реальные покадровые анимации/взаимодействия, QA и Lead сверяют полный frozen source/evidence. Старые bounded component PASS не равны новому полному gate. Решение владельца automation/decisions/P06_NPC_VISUAL_POLISH_TO_P08.json переносит оставшуюся визуальную hero-style индивидуализацию NPC C09 в P08-NPC-STYLE-01. Принятые shared category NPC clips допустимы для P06; базовые реакции/AI/контакт/once/settings/смерть/restart остаются обязательными. Собственные player-анимации/механики/звук/HUD не переносятся. Source FAIL не превращается в ART PASS; полная P06 всё ещё требует общей верификации и независимой приёмки.

## PRE-P07 production readiness и MDS

После полного P06 PASS/обязательного CI/подтверждённого защищённого merge нужен отдельный независимый Lead Production Readiness PASS по восьми системам. Аудит фиксирует реализованное, actual tests, partial, Critical/High зависимости и конкретный допустимый P08 debt; текущий readiness FAIL не изменяет старые phase PASS. Неконфликтная подготовка разрешена во время P06.

Перед массовым производством Lead с Narrative/Gameplay принимает все21 отдельную содержательную MDS по planning/MISSION_DESIGN_TEMPLATE.md и canonical IDs из planning/CAMPAIGN_PRODUCTION_REGISTRY.json. Требуются различные планировки/цели/боевые сценарии, возможности героя, навигация/проходимость/тупики/retry, постановка/сохранение/ветки/music, assets и измеримые критерии. CyberX/PRIME многоэтапны; одинаковая арена с переименованием или увеличение HP не разнообразие. Пять исходных секретов канонические; два новых бонуса имеют только отдельный CONCEPT_ONLY PASS и требуют своих полных MDS/integration gates.

Технический протокол разрешений: autopilot/PRODUCTION_GATES.md. Отсутствующий/FAIL/BLOCKED/component/concept-only/stale report или изменённые reviewed source/MDS запрещают производство. Установка candidate guard в ROOT и изменение stop limit требуют отдельного безопасного handoff без второго исполнителя и потери истории.

## P07 и P08 Gameplay Pacing Review

Независимый Gameplay Reviewer проверяет actual input responsiveness, читаемость/контакт/баланс, разнообразие encounters, predictable-on-retry события, быстрый restart/seen-skip и музыку Exploration→Tension→Combat→Aftermath. Нужны software Input→accepted/first-visible отдельно от windup, restart walltime, meaningful-action intervals, deaths/causes, chapter/route duration и monotonic wall-frame FPS с условиями; аппаратную задержку не заявлять по injected Input.

Сначала instrumentation и calibrated representative pilot baseline, затем acceptance runs с заранее зафиксированными порогами. Target7–9h первого прохождения с реальными смертями/повторами — NOT_MEASURED до готового контента и реальных прогонов; не складывать взаимоисключающие маршруты/AFK и не растягивать ожиданиями/пустыми переходами. Новая музыка требует signal/runtime QA и фактического слушателя; metadata/waveform не подтверждают художественное качество. Полные требования: planning/PRE_P07_REQUIREMENTS.md. P08 review записан как будущий gate, без разрешения начать P08/релиз.
