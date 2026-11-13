# P05 attempt1 — авторская передача

P05 реализован как кандидат инфраструктуры. Phase acceptance не решалась автором; независимые Narrative/QA/Lead, exact-head CI, native renderer/audio/exports/Wine — HOST_PENDING. Единственный автор, без subagents/runner/PR/push/merge/release. P06/P07 не начинались.

## Реализовано

- GDScript `story_registry.gd` + data registry21slots/43events, отдельные presentation/relative chronology/POVs/prerequisites/availability. CH01 сохраняет accepted ID/timestamp/scene и слабого Якудзу;20future slots честно planned без scene/timestamp. Проверяются duplicates/unknowns/DAG/reachability/backwards causality/simultaneous POV conflicts; подробные conservative defaults — design.md.
- `story_state.gd`/`story_service.gd`: authoritative schema2 event ledger, persistent derived flags/evidence/relationships/secrets/unlocks/endings, typed choices и first-choice lock, finite/type/range/version validation, atomic rename с rollback. Newer/corrupt/partial saves сохраняются; write disabled. Legacy P04 completion/dialogue мигрируют в новый файл без изменения legacy bytes; лабораторный P03 сюжет не выдаётся за CH01.
- D01–D06 и их immediate/downstream effects заданы ресурсами. Absent отличается от explicit refusal. D05 secure09/decode14 раздельны; decoder требует evidence. Out-of-order/unavailable/unknown events отклоняются без mutation. Conditions композиционные по declared fields.
- Три primary route gates и отдельный post-story REAL_PRIME overlay. WIFE_CALLING всегда default. BROTHERHOOD — exact три утверждённых факта; FAMILY_BUSINESS — repeated explicit concealment и отсутствие key evidence. План маршрута содержит encounter/entry/escape, permanent relationship, dialogue и два epilogues; `content_available=false`. Будущие cinematics/maps не реализованы.
- Русский journal на J/F4 с доступной/пройденной CH01 и честно недоступными20главами, normal Enter/F1–F3/mission/lab controls. DialogueDirector.finished и реальный outro передают canonical ID ровно однажды. Replay sandbox не пишет canonical facts/rewards; P04 checkpoint/deaths/bestscore работают как прежде. CombatSystem/contact clocks/accepted art/audio/options не менялись.
- `verify_p05.py` готовит actual Input journal/CH01/retry/skip/replay/checkpoint/resume, fresh-process reload, Full/Reduced comparison, rendered screenshots/MovieMaker и Linux/Wine экспортные процедуры. Native ветви подготовлены, автором не запускались. CI добавлен P05 headless suite; старым verify/verify_p04/verify_p04g добавлена изоляция StoryState save.

## Реальные проверки

Все пути ниже относительно worktree. Raw commands/exits/stdout находятся в соответствующих logs/validation.json. Godot pinned4.7.2 SHA проверен harness.

| Команда | exit | Реальный результат |
|---|---:|---|
| `python3 tools/verify_p05.py --headless --output reports/phases/P05/attempt1/technical-final --build-output build/P05/technical-final` |0|14/14 checks; story_registry13, story_state40, story_integration11, graph662778 assertions —0failures; input33, process_reload34, reduced_input33 checks; Full/Reduced canonical state одинаков; hashes неизменны |
| `python3 tools/verify_p04g.py --headless --output reports/phases/P05/attempt1/p04g-regression-01 --build-output build/P05/p04g-regression-01` |0|7/7 checks; Full и Reduced:20finisher/category-direction cases,12AI cases,600measured stress frames; одинаковые outcomes, hashes unchanged; только headless technical |
| `python3 tools/verify.py --output reports/phases/P05/attempt1/regression-01` |1|24/25commands успешно; **import не засчитан**, хотя child exit0: editor log содержит socket FAILED/ERR_CANT_CREATE в sandbox. Все остальные child exit0 и clean logs, включая P04 normal/accelerated Input, 3689 assertions в RESULT-based legacy suites, mission+story suites |
| `python3 -m unittest discover -s tools/tests -v` |0|73tests,0failures; log python-tests.log |
| `python3 -m py_compile tools/verify_p05.py tools/verify.py tools/verify_p04.py tools/verify_p04g.py` |0|Python syntax check |
| `git add planning/P05_TASKS.md` через linked Git |128|index.lock read-only; переход к авторизованному alternate git-dir без reset/замены.git |

Graph exploration: **6344paths**, **171366successful observed transitions**, **177710state visits** (включают initial states), **22828unique observed states**. Первая partition:729ternary D01–D06 combinations ×8optional acquisition toggles; отдельно512secret-record subsets при положительных choices/evidence. WIFE_CALLING eligible5832, BROTHERHOOD189, FAMILY_BUSINESS714 в первой partition; REAL_PRIME1/512 во второй. Reproducible histories/code/masks — technical-final/graph_exploration.json. Это exhaustive внутри указанных partitions; не все interleavings и не готовая кампания. Overlay дополнительно проверен поверх BROTHERHOOD с сохранением primary classification.

P04 реальные Input replay внутри P05 каждой Full/Reduced сессии проходят10actual AI deaths и cached retry, затем nonlethal escape/score1000. Повтор, skip intro/phone/outro, выход в меню и resume service-checkpoint выполняются реальными Input событиями. Отдельный fresh process проверяет disk load. Story integration fault fixtures (не walking evidence) проверяют отказ записи StoryState **после** durable P04 completion и recovery, без второй награды.

## Исправленные development failures и границы

История preliminary technical-01 сохранена:13/14checks, exit1 только из-за sources_unchanged (UID/CI/source edits во время ранней проверки); она не является freeze acceptance. В development-logs сохранены ранние editor socket errors, ошибочная attachment QA driver к busy scene root и два input defects: viewport после scene change и replay intro suppressed by seen. Исправлены deferred root driver/guard, handled-input до смены сцены и explicit replay intro; input3/resume3 и technical-final clean. Ранний JSON int/float roundtrip defect устранён строгим сравнением с whole-number normalization; final40save checks подтверждают roundtrip и disk rejection. Ранние parse/type ошибки при разработке не выдаются за успешные tests.

Авторский headless suite **не** подтверждает screenshots, визуальное качество UI, real audio device/listening, Linux exported executable, Wine или native Windows. Текущие WAV — runtime PCM из существующей музыки в Dummy mixer, без новой композиции/голоса/мастера. Новых art/music/photo/font assets нет, generators/платные services не вызывались. Raw photos не читались/не добавлялись. Future Timka drift остаётся P06-only.

Chronology будущих минут, optional route scene production и Narrative signoff conservative secret/concealment defaults остаются P07/независимому review. `flush+rename` не объявляется power-loss/fsync guarantee. Handoff между legacy chapter и story — recoverable, не multi-file atomic transaction. Подробности/defaults: design.md.

## Сохранность, Git и frozen source

Base `b774a1abfc18ef41f263259dc5c99cd4f26bc4c9`, parent `756054674383f92f67c7f5f4944c1a5ee8c384f1` — принятый P04G squash. Canonical ROOT automation/phase_state.json не изменялся автором. preservation.json проверяет **1225files** byte-for-byte с базой, включая весь old P04/P04G evidence/human chain, source assets/licenses, combat/AI/actors/contact/options и CH01 config/progress. Все совпали. reports/STATUS.md обновлён с сохранением исторического текста, P04/P04G отчёты не перезаписывались.

Коммиты линейны в `.tools/p05-author-git`, worktree=.; linked HEAD/index остаются под управлением хоста. Source commits: fa6c53a → b75763c → a09cf72 → c98387d. `source_freeze.json` содержит533source file SHA256 и aggregate; runtime/tool files совпадают с technical-final/source_hashes.json, документационный task status зафиксирован после теста. Последний evidence-only commit, его tree/полная parent chain, все tracked file hashes и bundle SHA записаны **после** commit в ignored `.tools/p05-delivery.json`, чтобы не создавать self-reference. В final response будет exact head.

`artifact_inventory.json` включает реальные generated outputs/hashes; ignored isolated_saves/PCM остаются локальными и не включены в Git. Author alternate working tree после evidence commit должен быть clean; исходный linked status будет показывать P05 diff до host adoption — это ожидаемо, не потерянные изменения. Bundle `.tools/p05-author.bundle` не публиковать автоматически. Host должен независимо проверить base/head/tree/все working-file hashes и принять linear objects/index по CAS/read-tree, не переписывая working files. Ни force/push, ни изменение ROOT state автором не выполнялись.

## Следующий шаг хоста

1. Проверить delivery sidecar/bundle/source freeze/protected hashes; принять через controller lease/CAS. Повторить clean Godot import в разрешённом host environment. Проверить рабочее дерево/UID и source hashes до/после, не менять frozen code без нового кандидата.
2. `python3 tools/verify_p05.py --exports --movie --output reports/phases/P05/attempt1/native-host-01 --build-output build/P05/native-host-01` — реальный renderer/audio/movies, Linux ELF и Windows PE под Wine; native Windows всё ещё отдельная отметка. При необходимости `verify_p04` и `verify_p04g` native regressions на этом же frozen source. Не переиспользовать старые listening claims как proof нового runtime.
3. Последовательные независимые Narrative/QA/Lead на exact head и evidence; exact-head mandatory CI. Решение/PR/условный merge — только хостом после gates. Никакого P06/P07/release в этом author stage.
