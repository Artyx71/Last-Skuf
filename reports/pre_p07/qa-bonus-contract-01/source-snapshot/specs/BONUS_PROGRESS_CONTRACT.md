# Бонусные эпизоды: контракт прогресса и интеграции

DRAFT_FOR_INDEPENDENT_REVIEW / NOT_IMPLEMENTED. READINESS-H05 / NS01-INTEGRATION. Это проект отдельной совместимости, а не миграция, уже выполненная в игре. Реальные тесты из §6 ещё не запускались. Основной frozen24 planning и runtime registry не изменены.

## 1. Граница канона

Пять `registry.data.secrets` и overlay condition в `routes.json` остаются прежними. `SECRET_OFFLINE_BUILD` и `SECRET_COUNTER_LESSON` — одобренные CONCEPT_ONLY исходные предложения; технические ID новых эпизодов — `BONUS_OFFLINE_BUILD` и `BONUS_COUNTER_LESSON`. Они не входят в StoryState.ledger/history/secrets/flags/evidence/relationships/endings/completion_rewards, D01–D06 или 21chapter_complete. REAL_PRIME продолжает проверять прежние пять секретов, WIFE_CALLING доступна на прежних условиях. В журнале отдельная секция «Бонусы · вне основной истории»; completion не называется шестым/седьмым условием концовки.

Unlock derive-only: первый бонус после durable CH14_AGENT_SWARM, второй после durable CH10_THE_KIMONO. Факты берутся только из успешно проверенного campaign Store, не scenario/fork/session payload. Состояние unlock не сохраняется в sidecar. Completed само по себе не открывает запуск без текущего prerequisite. Принятые5секретов+2отдельныхбонуса дают реестр7эпизодов, не изменение основной сюжетной схемы.

## 2. Единственный новый файл

Сохранить существующий `story_v2.json`, его VERSION=2, validate/_apply/миграцию из legacy и старые файлы побайтно. Вместо расширения exact-derived-state схемы добавить отдельный `user://bonus_progress_v1.json` **в том же изолированном профиле**, что активный campaign save. Для тестового override путь задаёт единый доверенный профиль/host, не значение внутри save. Автоматическая запись рядом с реальным профилем из replay/test запрещена.

Предлагаемая точная форма:

```json
{"schema":1,"domain":"bonus_profile","history":[],"completed":{"BONUS_OFFLINE_BUILD":false,"BONUS_COUNTER_LESSON":false}}
```

History содержит только уникальные ID завершённых бонусов (максимум2); completed строго bool и точно восстанавливается из history. Не хранить счёт, награду, произвольные flags, scene/actor/context/path. Неизвестный ID/ключ/версия, частичное состояние, duplicate JSON key, повтор history, не-bool, противоречивые производные поля и повреждённый JSON отклоняются, исходные bytes сохраняются, запись в sidecar блокируется. Неподдерживаемая новая версия не превращается в пустой файл.

Sidecar принадлежит профилю, а не очередной кампании. New Game/replay основных глав его не обнуляет и не получает из него сюжетных фактов. Даже completed=true требует заново доступный current campaign prerequisite для запуска; чистая установка/отдельный профиль получает оба false. Новое требование «сбросить все бонусы» не добавляется.

## 3. Совместимость и публикация

Отсутствующий sidecar означает оба false в памяти, status NEW; само открытие журнала ничего не пишет. Первое успешное реальное завершение создаёт sidecar. Это миграция добавлением отдельного optional namespace: старый story_v2 и legacy не переписываются, заполненный старый secret не переносится в bonus, failure sidecar не ломает доступ к основной истории. Невалидный campaign запрещает новые unlock/launch/completion, но не портит существующий sidecar. Изолированная ошибка bonus даёт сообщение в секции бонусов; основной журнал сохраняет текущую политику ошибок StoryService.

Write protocol использует действующий publish-after-rename pattern: candidate duplicate→validate→same-directory .tmp write/flush/error/close→rename→только затем заменить in-memory state и показать completion. Open/write/rename failure сохраняет прежние main+bonus bytes, in-memory state и отсутствие награды. Повтор одного completion возвращает успех без новой записи/истории/очков; crash до publish не выдаёт ложного completed. Оставшийся .tmp не считается commit и не восстанавливается как факт автоматически. Два параллельных writer запрещены текущим единственным profile/StoryService owner; дополнительные универсальные storage/lock frameworks не нужны.

## 4. Реальный запуск и завершение

До full bonus MDS review, actual scene/policy/assets и независимой интеграционной приёмки оба элемента имеют availability=planned, scene отсутствует, launch.disabled=true. Клик/Enter/подделанный completed/пустой scene не записывают completion. Подготовка specs не регистрирует их в текущем runtime. После допуска отдельный ресурс host задаёт ID, scene path, hero/context и session generation; save не выдаёт combat policy/ability/оружие. CharacterPlayer сейчас признаёт только IMPLEMENTED_FIXTURE_ABILITIES: trusted bonus chapter factory/scene adapter ещё REQUIRED_NOT_IMPLEMENTED.

StoryService.store остаётся campaign owner. Бонус запускается только из безопасного журнала вне боя/диалога/перехода, с отзывом предыдущих action jobs/authority; возврат восстанавливает прежний основной safe scene без фиктивного chapter completion. Во время бонуса нет вызова campaign Store.record/complete_chapter/choose/finish_story/finish_overlay. Сессия реального первого прохождения после доступного prerequisite может commit один ID только по авторитетному goal/exit событию своего host, при alive/nojobs/resolved objectives; смерть/retry/cancel/skip только интро/уход из журнала такого права не дают. Чужая/отменённая generation, callback старого exit после restart и одновременные входы отклоняются. Завершённый бонус повторяется в read-only fork, не фармит completion/награды; первый неполный разрешённый запуск не считается просмотренным replay.

## 5. Обязательные точки изменений после design review

Существующие callers: `story_service.gd` (единственный owner/профиль/безопасный launch-return), `ui/story_journal.gd` (отдельные2строки, derived unlock/availability/errors), trusted bonus resource/host и chapter scene policy (реальный герой/контекст/цель/generation). Минимальный новый bonus store следует нынешнему StoryState atomic pattern, не меняет StoryRegistry.declared/valid_effects и StoryState.VERSION. Не добавлять фиктивный универсальный switch/магический grant.

Тесты/fixtures: отдельный временный профиль в существующем Controller.stage, старые story_state/story_graph/story_integration и новые bonus lifecycle/write failure tests; real Input launch/goal/cancel/restart/return, свежий процесс load. Exports: прежний DEV10 не меняется; новый Linux/Windows build после runtime integration и QA. Производственные scenes/UI/миграция/новые экспорты **ещё не созданы и не проверены**.

## 6. Проверки до runtime-интеграции и допуска контента

| ID | Проверка и обязательный результат |
|---|---|
| BP01 | Старые valid story_v2: fresh/CH01complete/все5secrets/разныеD01–D06/каждаяконцовка; main bytes+ledger+reward+eligible/overlay неизменны до/после открытия/сохранения bonus. Scenario fixtures отдельно и никогда не принимаются production unlock. |
| BP02 | Нет sidecar: оба false, unlock только из current durable canonical chapter, чтение не создаёт файл. Старые legacy проходят прежнюю миграцию; bonus не меняет её исход. |
| BP03 | Первый goal event даёт ровно1historyID/1true/0campaignreward; второй callback и freshprocess повтор не пишут bytes и не меняют награды. |
| BP04 | Crash/temp/open/write/rename failure: прежние bytes и state неизменны; следующий разрешённый retry может сохранить один результат. |
| BP05 | Повреждённый/новый/partial/extra/duplicate-key/duplicate-history/nonbool/unknownID sidecar сохраняется read-only, основной campaign остаётся проходимым. |
| BP06 | Replay/scenario/поддельный save.scene/context/старая generation/death/cancel/intro skip/сам клик не дают unlock или completion, не меняют кампанию. |
| BP07 | Locked/planned строка недоступна мышью/Enter/прямым launch; completed не обходит current prerequisite; базовый story journal/replay работает как раньше. |
| BP08 | Только два bonusID, canonical secretIDs/ending routes hashes прежние; все пути WIFE_CALLING/REAL_PRIME и решение D01 неизменны. |
| BP09 | Profile A/B и test/replay isolation; sidecar A не используется B, никакой записи в обычный user:// из sandbox; restart не оставляет authority/job. |
| BP10 | Реальный native firstlaunch→objectives→exit→return→freshprocess reload, death/retry/cancel и Full/Reduced; обе оригинальные миссии имеют Narrative/Gameplay/ART/QA/Lead actual acceptance. |

Ни один BP здесь не помечен PASS: это проверяемые критерии. Перед интеграцией нужны отдельные контракт/pilot tests и independent review; после реализации нужны фактические игровые проверки/ассеты/аудио. FULLReadiness и genericP07 остаются закрыты существующим controller, пока полный набор capability evidence не принят независимым Lead.
