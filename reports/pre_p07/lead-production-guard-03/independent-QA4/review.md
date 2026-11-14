# P07 guard v4 — independent bounded QA, PG-C05/PG-C06 closure

**PASS_COMPONENT.** PG-C05 и PG-C06 закрыты для exact v4 freeze guard-author-04. Actual independent baselines55/55 и47/47 проходят. Отдельно выполнены16/16 ingress probes,23/23 staged controls и10/10 старых adversarial cases. Нерешённых замечаний в ограниченном исправлении не выявлено. Это не full readiness, phase, production start, установка ROOT runner или merge approval.

## PG-C05: фактический raw JSON ingress закрыт

В actual runner.load подан тот же raw TEST_ONLY verdict из QA3 побайтно, SHA4e2f2701cb4705d92840c42c70975410167bffdeecd4ca198e73367947700075. Это конфликтный firstFAIL/lastPASS new_audio_acceptance duplicate. Теперь actual loader выбрасывает Blocked с причиной ValueError: Duplicate JSON key: new_audio_acceptance. validation_calls0, snapshots0, mock requests0, actual network0. Исходные bytes файла сохранены; default{} не используется как молчаливый fallback.

Отдельно повторены current-head coherent duplicate, Unicode-escaped duplicate decoded key и дублированный top-level status. Они также останавливаются в actual load до phase validation/merge. Не использован заранее построенный dict или авторский no_duplicates flag. Wrapper содержит реальную цепь load→validate_review→guarded_merge; её ранняя остановка в loader является ожидаемым fail-closed результатом.

В hash-rebound ROOT readiness receipts отвергнуты escaped duplicate capability navigation_pilot и future obligation secret_delivery_7. Это actual load_gate path с совпадающим decision SHA, а не отказ только из-за старого hash. Actual canonical ROOT state reader также отвергает duplicate production_gates key, сохраняет плохой файл и не откатывает прогресс. NaN/Infinity/−Infinity literals отвергаются actual runner.load. Все эти данные и canonical state — только временные fixtures, не настоящий репозиторий/контроллер.

Код использует strict_json с object_pairs_hook, который сравнивает уже decoded keys, и parse_constant для запрещённых nonfinite literals. Его реальные точки применения просмотрены в runner.load, readiness receipt/canonical state/registry и GitHub JSON/listening readers. QA не запускал настоящий gh/CLI/API/engine ради проверки этих wrappers.

## PG-C06: phase findings проверяются на runtime boundary

Шесть malformed containers findings: пустой object, object с HIGH/OPEN, null, string, integer и boolean — проходят синтаксический actual JSON loader, но затем actual validate_review возвращает array-required error. guarded_merge отказывает после первого snapshot, request_count0. Это проверка всей доступной цепи для валидного JSON неверного типа, а не только JSON-schema производителя. Внешний verdict container также проверяется на dict в коде.

Новые55 tests включают raw contradictory duplicates через настоящий loader, duplicate top-level status/Readiness capability, nonfinite literal и malformed findings. Existing47 проверяют прежние recovery/lease/receipt/merge safeguards. Ни один test fixture не является действительным Lead/source/контентным approval.

## Staged contract и состояние сохранены

23 отдельные контроли сохраняют новый staged design:6 actual capabilities и21MDS нужны перед generic mass executor;4 future obligations остаются HIGH/OPEN с фиксированным stage; missing/unknown capability/obligation/stage/inline scope/schema/closure/currenthead/readinessSHA/evidence блокируют; валидные synthetic mass-entry/inline closure controls проходят. В двух настоящих second-snapshot fixture calls canonical Readiness SHA или proof file меняются после первой проверки — результат BLOCKED, snapshots2, requests0.

Actual linked temporary worktree содержит новый P07 commit, отличный от P06, и заведомо stale WORK state. Правильный canonical ROOT receipt позволяет exact-current-head closure; удаление ROOT readiness блокирует. Valid workspace resume не сбрасывает state/attempt/checkpoint; прежние10 symlink/path/severity/schema/resume probes остаются правильными. Это не end-to-end production resume/merge на рабочем репозитории.

Ранее FAIL QA3 decision SHA fa9b45113d742f234846e1c11a0ac6dbbf1aab3597cef0d7d46f4df4f46ce39c и все34 его artifacts проверены неизменными. Исправление не переписывает старый raw sample/FAIL. V3 stage/schema/prompt contract сохранён в v4; actual source8 SHA сверены с author04 и isolated snapshots до/после запусков.

## Пределы заключения и portable evidence

Все Git init/commit/worktree/Controller/worker действия происходили только в ROOT TemporaryDirectory fixtures. GitHub request functions были spies/mocks. WORK и actual canonical ROOT state/queue/phase attempts reviewer не менял; engine/actual network не запускались. Read-only дисковое наблюдение ROOT показывает старый runner без hook и stop_after_phase=P06; это не инспекция живого процесса и не установка.

Количество fake capabilities/proof files не доказывает готовность игры. Реальные fullP06, safe handoff, independent full Production Readiness/21MDS, actual content/listening/gameplay/build/CI/Lead acceptance и разрешение P08/release остаются за своими gates. PG-L05 окончательно принимает отдельный Lead; QA подтверждает ограниченные mechanics и закрытие PG-C05/06.

Относительные portable source/scripts/logs/results перечислены в artifacts.json. При повторении использовать новый ROOT report directory, скопировать эти paths, создать tmp/, задать TMPDIR и PYTHONDONTWRITEBYTECODE. Не перезапускать поверх immutable evidence. Temporary repositories/production state/queue исключены. Никакое разрешение установки или начала P07 из PASS_COMPONENT не следует.
