# Безопасное продолжение P04

Это подготовка по прямому поручению владельца; фаза не начата и playable mission не объявлена. Gate: независимый P03 PASS + подтверждённый squash merge его актуального проверенного SHA в main. При блокировке GitHub продолжать только разрешённые независимые задачи текущей фазы. Не считать художественную приёмку заменённой Audio QA.

| Шаг | Атомарный результат | Evidence |
|---|---|---|
| 0 | Reconcile automation/phase_state, decision и confirmed main merge | AUTOPILOT status/PR snapshot; ни одного сброшенного PASS |
| 1 | Authored scene flow первой миссии с canonical event ID | STORY_SPEC chapter01 THE MISSED FIGHT: flashback/непобедимый конфликт объяснён постановкой, а не ломающимся combat |
| 2 | Оригинальная карта и tiles/props с реальной collision/nav/readability | Source PNG/atlas/licenses/native screenshots; техническая арена P02 не выдаётся за миссию |
| 3 | Внешние authored dialogue/intro/exit, взаимодействия и checkpoint | Реальные flags/scene transition/save/load; не добавлять фиктивные consequential choices |
| 4 | Интеграция существующей слабой Якудзы/combat/AI/retry/audio | Contact48 regression, actual Input mission replay, оригинальная музыка, реальные captures |
| 5 | Linux/Windows builds, regression, independent review | Билды исполняются где доступно, native/Wine точно подписаны; human visual/audio gate |
| 6 | PASS+CI+current-SHA squash main; очередь P04G | Без merge при FAIL/BLOCKED/manual approval/unknown protection |

После P04 — P04G по specs/COMBAT_GORE_POLISH_SPEC.md: impact, оригинальная кровь, enemy reactions и пять категорий finishers, затем варианты персонажей по P06. P07 заблокирован без P04G PASS. Существующая combat physics архитектура и принятые исходники сохраняются. Арт, сюжет и новые механики требуют собственной реализации и доказательств; этот документ их не заменяет.
