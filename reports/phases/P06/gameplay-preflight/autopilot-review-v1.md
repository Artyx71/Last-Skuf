# P06 — bounded AUTOPILOT native publication gate review v1

Статус: **COMPONENT_GATE_CHANGE_VERIFIED_P06_PENDING**. HEAD прочитан непосредственно из Git metadata files без Git command: `ced53eeedaa71b4fe7532b2063f83f98138fa225`. Reviewer `/root/gameplay_review_p06` выполнял только read-only source/log/hash inspection. Controller, Git commands, Godot, tests, generation/build не запускались; repo authority/attempts/leases не изменялись. Единственные записи — этот versioned md/json в корневой gameplay-preflight. Полный P06, native gameplay и subjective feel не оценивались.

## Проверенный diff

Файловое сравнение ROOT с WORK через Python difflib показывает одну строку production change: `autopilot/runner.py:294` добавляет P06 в список фаз с mandatory native-validation после обычной validation. В `tools/tests/test_autopilot.py:298–337` добавлены helper fixture и два теста. Worker/github исходники совпадают с ROOT побайтно. Reviewer не выполнял Git diff по запрету Git commands; граница сравнения подтверждена содержимым файлов и hashes evidence.

## Поведение gate

- Обычный P06 checkpoint validation после успеха идёт в native-validation (`runner.py:288–295`), затем запускает **tools/verify_p06.py --exports --movie** с head/attempt-specific output/build paths и **safe_retry=False** (`:296–301`). Partial verify_p06_cast.py/verify_p06_world.py не подставляются.
- Nonzero code переводит phase в **recovery-review / BLOCKED** и бросает Blocked до publication (`:302–304`). Это включает failure, timeout и interruption codes: worker возвращает124/130, а отсутствие receipt в stage даёт130 (`worker.py:43–59`, `runner.py:197–205`). Attempts здесь не увеличиваются/не сбрасываются; implementation повторно не стартует. Повтор run_phase при BLOCKED отказывает (`:269`). При завершении controller без receipt shared stage с unsafe retry требует recovery review (`:157–169`) вместо слепого повтора.
- Resume непосредственно с native-validation идёт через ту же полную команду и safe_retry=False, обходя author implementation и обычную validation. Только code0 переводит checkpoint в publication, затем manage prepare (`:305–308`). Это routing proof, а не факт успешного native run.
- `tools/verify_p06.py` фактически **отсутствует**. Реальный Python subprocess на этой команде не сможет открыть script и даст nonzero; controller остановится на recovery-review BLOCKED. Нет success stub и нет замены частичными cast/world previews. Полная harness остаётся необходимой работой в IMPLEMENTING; этим review никакой phase status не меняется.

## Проверки и ограничения доказательства

Первый новый тест моделирует validation success и native failure; проверяет full harness/flags/safe_retryFalse, отсутствие manage calls, event order validation→native, attempts1 и recovery-review BLOCKED. Второй моделирует resume native success, проверяет native→prepare без author replay и сохранение attempts1. Native stages и GitHub prepare в этих тестах mocked; реальный subprocess missing-script failure специально не запускался reviewer.

Прочитан реальный `reports/phases/P06/author-checks/autopilot-gate-01.log`: **Ran47 tests, OK**. JSON сообщает exit0 и scope UNIT_ONLY; reviewer независимо пересчитал четыре source hashes runner/worker/github/tests и log SHA256: все совпадают. Tests временные fixtures используют TemporaryDirectory, не production authority. Reviewer suites не перезапускал и не выдаёт авторские47 checks за независимый runtime/native прогон.

## Сохранённые merge ограничения

Unchanged `autopilot/github.py` по-прежнему проверяет independent exact head/phase и evidence hashes (`:34–70`), current main base, branch protection/approvals/threads/current-head CI (`:128–159`), повторный fresh snapshot и head/base перед SHA-bound squash request (`:162–181`). Runner publication→CI→independent review→merge порядок остаётся прежним (`runner.py:306–336`). Эти условия не проверялись против live GitHub; publication/merge permissions этим отчётом не выдаются.

Новых actionable findings в рассмотренном component diff не найдено. Требуются реальная full verify_p06.py, весь production P06 content и свежие native/platform evidence с независимыми ART/GAMEPLAY/QA/Lead gates. Частичные previews и этот47-test routing report не могут заменить их.
