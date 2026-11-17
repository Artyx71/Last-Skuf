# P07 production guard — независимый bounded QA v2

**PASS_COMPONENT.** PG-C01..PG-C04 закрыты для сохранённого кандидата readiness.py SHA f82db9f1fa54caca6ce78ce6fb0aad5d92c5f92202b947f3054458c6445c5304 и runner SHA e3ca71276d3ca97a2c06f3977039b94ca5c337230dc46ad25a2b96b72ffc4626. Реально выполнены isolated34/34 новых tests,47/47 regressions, исходные10/10 independent repro cases и15/15 дополнительных probes. Нерешённых дефектов в этом ограниченном scope не выявлено. Это не full Production Readiness, установка ROOT runner, старт P07, phase или merge approval.

## Подтверждение исправлений

Использован побайтно тот же adversarial.py, который воспроизводил v1 обходы, но он импортирует v2 из нового isolated-source. Все6 прежних неожиданных принятия теперь отвергнуты: untracked game directory symlink, external reports/pre_p07 symlink prefix, severity HIGH с trailing whitespace, severity null/object и schema boolean. Каждый случай сохраняет state без изменений. Exact HIGH/OPEN, дубликат MDS через symlink и ../ inventory escape также блокируются. Valid P07 worktree resume остаётся разрешённым при неизменном frozen ROOT source.

PG-C01: production_files использует no-follow os.walk и явно отказывает на file/directory/dangling symlinks в production tree до сравнения с frozen Git. Больше нет невидимого untracked directory source. Генерируемые .godot/__pycache__ по прежнему исключены согласно протоколу: это source guard, не проверка импортного cache.

PG-C02: file_under отвергает .. и любой symlink component relative path; отдельно проверяет resolved boundary и file containment внутри canonical root. Prefix, указывающий наружу, больше не расширяет доверенную область. Штатные34 tests включают reports и planning parent escapes; independent additional same-byte internal decision-leaf и inventory-file symlinks также отвергнуты.

PG-C03: severity должен быть строкой с известным enum после strip/upper, status — известным resolution enum. Malformed значения не превращаются в незначимые findings. В обоих approval scopes отдельно проверены whitespace/lowercase HIGH+OPEN и отсутствие LOW status — отказ; normalized HIGH+VERIFIED принят как валидный контроль.

PG-C04: schema требует exact int1. Independent tests по обоим scopes отвергают float1.0; исходный boolean schema repro также отвергнут. Отдельно проверены blank reviewer и numeric independence1 вместо true — отказ в обоих scopes. Это machine validation объявленных role/identity/independence fields; настоящий отдельный Lead context остаётся обязательством workflow, а не доказывается синтетическим reviewer string.

## Resume и прежние gates

Исходный valid resume fixture содержит P07 status IMPLEMENTING/checkpoint validation/attempt1 и отдельный worktree с продолжающимися изменениями game. Guard проходит и state не меняется. Дополнительный негативный resume удаляет readiness record: prerequisite отказывает, но сохраняет attempts/checkpoint/state и existing workspace marker. Это проверка обоих направлений без сброса прогресса, а не end-to-end production resume.

Existing47 tests проходят, включая durable worker finish/adopt-once, lease exclusion, receipt tamper, SHA-bound protected merge и запрет unverified merged-parent progress. Все реальные Controller/worker/Git actions относятся только к TemporaryDirectory fixtures; GitHub calls mocked. Ни одна production Controller lease, canonical state/queue, WORK Git или engine не использовались.

Новые34 tests сохраняют whole game Git-blob validation даже после согласованного обновления claimed inventory, strict P06 PASS/MERGED/head requirements, missing/FAIL/BLOCKED/component/concept refusal, high/critical closure policy и21 distinct MDS bindings. MDS contents/дизайн/сюжет по прежнему принимает настоящий Lead/Narrative/Gameplay: фиктивные документы тестов не являются настоящими21 MDS.

## Замороженные доказательства и дальнейший handoff

Все4 frozen input SHA совпадают с guard-author-02 до/после QA, исходники и зависимости сохранены в isolated-source. V1 FAIL decision SHA03bc98cacbb1aa5478cd866deb80513a31cb82228af4c5b1732474a02f107881 и все22 его artifacts проверены неизменными. Новый отчёт не переписывает v1.

Read-only наблюдение только дисковых ROOT файлов подтверждает: новый hook в ROOT runner отсутствует, stop_after_phase=P06. Это не инспекция живого процесса и не установка. Безопасный точный ROOT/WORK handoff, реальные P06 full PASS/CI/protected merge, свежие независимые full readiness и21 MDS decisions остаются отдельными обязательными gates. Их фактическое наличие этим review не заявляется; старые readiness FAIL/concept-only решения не заменялись.

Портативные scripts/modules/config/tests/logs/results перечислены относительными путями в artifacts.json. Для повторения в новом ROOT report directory нужно скопировать эти paths, создать пустой tmp/, затем запускать run-isolated.py production, run-isolated.py regression, adversarial.py и additional.py с TMPDIR=<new-report>/tmp и PYTHONDONTWRITEBYTECODE=1. Повторять поверх immutable evidence нельзя; используйте новый каталог. Temporary Git repos, production state, caches и неиспользуемая queue в manifest не входят.

Никаких WORK/ROOT production mutations, engine/network/GitHub actions reviewer не выполнял. PASS относится только к exact candidate code и ограниченным tests, не к готовности самой игры или разрешению производства.
