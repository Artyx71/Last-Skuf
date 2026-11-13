# Завершение интеграции и P04

Исторические принятые фазы доставлены по порядку P00→P03, каждый раз с текущими CI и отдельным exact-head/base reviewer receipt. Все четыре confirmed squash сохраняются в canonical state. Source/reference данные не сбрасывались. После основной P03приёмки найденный duplicate draftPR5 закрыт без merge; PR4 восстановлен по ветке. Потеря номера PR не создаёт новый PR автоматически при существующем совпадении.

Перед любым discovery/publish/create зарегистрированный worktree обязан совпадать с record.branch и requestedphase. Для незарегистрированной ветки тоже проверяется phase prefix. Multiple/truncated discovery, wrongbranch, closedPR не публикуются; исправления existingworkspace отправляются обычным privacy-checked push доCI. AUTO-PR-OWN-01 должен пройти новый CI/independent review до P04; следующий handoffPR применяет code+tests+resume state вместе.

43local unit cases включают SIGKILL/lease/adoptiononce, SHA/base/CI/manualapproval/mergeintent/state regression и PR recovery/early ownership. Это проверка инфраструктуры; игровые785 assertions и actualPulseAudio71checks имеют отдельные отчёты. Full power-loss durability не проверялась; artificial forcedquit audio-reference warnings сохранены. Нет обещания always-on runner или agent audio listening.

P04 readiness PREPARED означает доступные зависимости и priorphasePASS+confirmedmerge. Mission/арты/finishers не объявлены созданными. Порядок P04→P04G, P07 требует P04G PASS; будущая referenceработа Тимки блокируется только локальным manifest drift. Resume отчёты не заменяют independent quality gates.
