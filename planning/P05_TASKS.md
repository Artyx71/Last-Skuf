# P05 — атомарный план, статус PREPARED

Основание: независимый P04G PASS и подтверждённый squashPR9 `756054674383f92f67c7f5f4944c1a5ee8c384f1`, новое «давай дальше». Один автор, без сброса прогресса; следующий checkpoint P05. Полная кампания не реализуется.

1. Реестр событий/хронологии/POV и валидируемый граф21плановых slots с честной доступностью CH01.
2. StoryStore: атомарные события/сохранения, миграция ChapterProgress/DialogueDirector, idempotence/replay isolation.
3. D01–D06 и branch resolver: три основных маршрута + REAL_PRIME secret overlay, осмысленные downstream conditions.
4. Игровой журнал/выбор доступной главы, реальная привязка CH01; никаких фиктивных сцен будущих глав.
5. Тесты графа, условий/доступности, save/migration/failure, canonical/replay; native Input evidence и Linux/Wine exports по доступности.
6. Frozen source → CI → независимые Story/QA/Lead → защищённый squash только PASS.

Архитектура/полные контракты — P05_EXECUTION_BRIEF.md, STORY_SPEC.md. План не является реализованной системой.
