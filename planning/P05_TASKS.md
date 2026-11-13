# P05 — атомарный план, статус IMPLEMENTING (автор, без phase decision)

Основание: независимый P04G PASS и подтверждённый squashPR9 `756054674383f92f67c7f5f4944c1a5ee8c384f1`, новое «давай дальше». Один автор, без сброса прогресса; следующий checkpoint P05. Полная кампания не реализуется.

1. Реестр событий/хронологии/POV и валидируемый граф21плановых slots с честной доступностью CH01.
2. StoryStore: атомарные события/сохранения, миграция ChapterProgress/DialogueDirector, idempotence/replay isolation.
3. D01–D06 и branch resolver: три основных маршрута + REAL_PRIME secret overlay, осмысленные downstream conditions.
4. Игровой журнал/выбор доступной главы, реальная привязка CH01; никаких фиктивных сцен будущих глав.
5. Тесты графа, условий/доступности, save/migration/failure, canonical/replay; native Input evidence и Linux/Wine exports по доступности.
6. Frozen source → CI → независимые Story/QA/Lead → защищённый squash только PASS.

Архитектура/полные контракты — P05_EXECUTION_BRIEF.md, STORY_SPEC.md. План не является реализованной системой.

## Границы реализации attempt1

- [x] Data registry: 21 slot, 43 event definitions; CH01 timestamp locked, будущие timestamps production_pending; относительная chronology предварительна.
- [x] StoryState schema2, event-sourced validation, atomic rename, first-choice lock, replay fork и read-only legacy migration.
- [x] Подключение CH01 и русский журнал, сохранение Enter/F1–F4.
- [x] Исчерпывающие ternary D01–D06 + optional evidence/secret exploration, реальные Input fixtures.
- [x] verify_p05/CI и P04G Full/Reduced regression.
- [ ] Финальный неизменный hash run, source freeze/inventory/bundle.
- [ ] Native host renderer/audio/Linux/Wine и отдельные Lead/Narrative/QA (после автора).

Общий index недоступен (read-only index.lock); коммиты создаются в ignored `.tools/p05-author-git`, base `b774a1abfc18ef41f263259dc5c99cd4f26bc4c9`. ROOT controller не изменяется. Никаких runner/subagents/push/merge.
