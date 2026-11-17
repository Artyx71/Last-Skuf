# Lead: исправление cast replay и запуск remaining5

**PASS_COMPONENT_EXECUTION_ONLY** для source263e888afc9875ebf887267c0dd734b70897f344 и contract02 e5ef81ddc24fc12420cc602c403deefe5cb8891961b2e985d85c64e53515a343. Разрешён один последовательный canonical ROOT job: проверка синтаксиса текущего Pasha fixture, затем пять оставшихся native stages. Новые native результаты и полный P06 этим решением не приняты.

## Исправление протокола

Исторический cast FAIL fd0bfb43 / operation d56af6d9cc6b4b13be4a0436e4a13a21 сохраняется: 191/193 проверки, 45 PNG, две лично просмотренные картинки показывают следующую реплику вместо ожидаемой. Source/HEAD/proof bindings оставались стабильными, current Pasha check-only прошёл; четыре последующих этапа не запускались.

Director.advance корректно раскрывает неполный текст либо переходит дальше, если строка уже раскрыта. Старый driver всегда нажимал Space после 16 frames. Начальная причина преждевременного раскрытия или лишнего перехода остаётся UNKNOWN: старой телеметрии для вывода об ОС, Shift или production UI нет.

Лично прочитан новый diff. Изменён только QA driver: он проверяет active/index/expected line ID/emotion, раскрывает через настоящий Input только неполный текст, проверяет сохранение строки, затем делает один Input advance. Старые expression/text-fit/capture/history/campaign predicates и ожидание 16 frames сохранены. Добавлены 135 assertions и 180 снимков состояния; прямой установки строки, портрета или visible_count нет. Production Director, Viewer, session, тексты и портреты не менялись.

## Реальные проверки обеих ветвей

Самостоятельно прочитаны normal и large headless результаты: по 283 проверки и 180 snapshots, по 45 actor/expression groups. Line IDs/index/emotion/active сохраняются до capture, текст полностью раскрыт, после одного advance достигается следующая строка либо finish. Separate-process reload и source_unchanged прошли. Во всех этих 90 случаях до reveal текст ещё был неполным.

Поэтому выполнен один отдельный контроль существующей настройки Instant Text, без изменения Game: schema2 instant_text=true в новом изолированном profile. Canonical operation 5ed9fb4693ae43d4ae26dc0dade69ee1 действительно завершился exit0; receipt, argv и log SHA проверены. Результат: 283 проверки, 180 snapshots, 45 уже полностью раскрытых строк ДО условного reveal. Их IDs/index/active сохраняются, один Input advance переводит на next/finish; reload/source_unchanged=true. Data SHA: 1b62fce941f730bd9b1e2a2e4f00f5febc29739174b32cb3139e9a6bf7e22cb3.

Итого проверены движком обе ветви: 90 partial и 45 already-visible cases, 540 snapshots / 135 groups. Это headless evidence, а не новые rendered PNG или typography acceptance. Старую причину сбоя эти результаты задним числом не устанавливают.

## Связь исходников и доказательств

Лично перехешированы 905 реальных contract artifacts; все 845 прежних digest сохранены. Закреплены old full FAIL, семь успешных stages, targeted Pasha и failed tail01. Текущий source delta соответствует ровно четырём разрешённым путям: Pasha QA, cast QA, coordinator и его unit file. Остальные production Actor/Core/AI/audio/render/assets не изменены.

У coordinator изменена только константа allowlist, добавляющая конкретный cast QA path. Все шесть функций совпадают с проверенным 63a, включая same-bytes SHA/parse, проверки binding перед parse/каждым child/после tail и сохранение исходных digest. Pipeline и process containment также неизменны: enable_subreaper вызывается внутри run_command до Popen. Прежние pure drift/process proofs применимы по точному коду; новые engine/process repro reviewer не запускал.

Независимый QA c0c4e4ca64f83da47f560bf5298e17acd6373e703c198e608761ae3571a1bf00 прочитан вместе с review и typed proofs. Все 48 portable files лично SHA-сверены. QA отдельно проверил 905 artifacts, source delta, четыре pure unit-функции, старые predicates, 540 snapshots и три настоящих headless receipts. Его вывод согласуется с самостоятельной проверкой.

Privacy operation ec5ba675f3ef410ca34c7e910a56a285: actual receipt exit0/log SHA и validation 10239d47… прочитаны. Проверены 35 checks, 11 current private files и 17156 shared objects; дополнительных WORK index raw matches нет. Это point-in-time проверка путей и точной SHA-идентичности private11 на source263/mainbe4, с phase/publication=false. Она не доказывает отсутствие всех transforms, неучтённых inputs или PCK contents и не даёт коммерческие права. Старые privacy01/02 early FAIL сохранены. Reviewer скан не запускал.

## Условия запуска

Один canonical ROOT worker после author release и завершения/consumption предыдущих privacy и Instant Text jobs; никаких overlap, source/Git writers или изменения HEAD во время job. Нужны fresh report/build paths и точный SHA этого внешнего независимого approval.

Сначала текущий Pasha --headless --check-only; ошибка прекращает продолжение. Затем только cast → cast_large_text → finisher_audio → npc_baseline → combat_baseline. P04G получает --exports --movie, C01 сохраняет native headroom/replay scope. Budget7200; автоматического whole13 retry и replay consumed jobs нет.

Для каждого native cast ожидаются 328 checks / 45 PNG — пока это прогноз, NOT_RUN. После actual receipt проверять все 180 states на mode, IDs/emotions до и после capture, реальные PNG, text-fit/reload; далее fresh PCM, NPC cases, real non-Movie wallframes с flags/hardware и actual Linux/PE Wine builds. Одних counters недостаточно. Любой child/report/source/HEAD/proof drift запрещает приёмку.

First7 и targeted Pasha не переснимаются. Composed ledger честно различает 7 reused + targeted Pasha + 5 fresh и сохраняет original FAIL. GO относится только к exact reviewed source/contract.

Full P06, phase advance, current PR/CI/protected merge, readiness, P07, ROOT installation, release, listening, native Windows и FPS этим review не одобрены. Formal P06 attempt1 и last full P05/PR10 сохранены. Reviewer engine/Git/state/source mutations=0; написаны только собственные ROOT reports.
