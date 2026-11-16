# Независимый preflight742: FAIL_COMPONENT

Scope только нового coordinator tools/continue_p06_native.py на742e9dc79bb97568a929b01ab39b398cb0536473, moduleSHA8100208ff8e3fba1010c0461cc1c1bddf2aee59b30e8428b3be82bb8bb354ddf; oldcontract86ddfcf1efb3ec1bfcab725586058d32eb013032c070f2c8bd30c50e7d1ac9da. Реальные tail stages не запускались. Это не пересмотр Пашиного runtime/ART и не fullP06 phase attempt.

## CONT-L01 — MEDIUM, блокирует execution до исправления

Код в начале хеширует/read-parses approval и проверяет её contract digest. После tail он перепроверяет845artifact inputs, но contract/approval сами не входят в этот набор и повторно не сверяются. Summary вычисляет CURRENT contract SHA, хотя использовал старый parsed object. Изменение proof во время прогона может дать passed=true с неодобренным digest либо уже FAIL approval.

Фактически исполнен неизменённый coordinator.main на трёх чистых TEST_ONLY fixtures. Mock только HEAD/inventory/plan/child execution; настоящий main, strict JSON, path confinement, artifact/approval binding, held_data и valid_report исполняются. Ни Game/engine/Git/network subprocess не запускался.

- Positive control: unchanged approved proofs → exit0/composed13 passed=true.
- Contract заменён mock child последнего tailstage после начала прогона: exit0/passed=true/13stage, summary берёт НОВЫЙ digest, которого approval не разрешала.
- Approval заменён на statusFAIL_COMPONENT последним mock child: exit0/passed=true/13stage со старым approval digest.

Это actual pure orchestration counterexample, а не настоящий13-stage run. Копии исходного module/contract, воспроизводимый source script и raw outcomes приложены. Script читает frozen742 snapshot; новый WORK coordinator не подменяет старый reproducer.

Минимальное исправление: читать contract/approval единожды bytes→hash→parse, хранить исходные approved digests, сравнивать их перед parse/каждым новым child и в конце; missing/changed означает fail/следующий child не запускать. Summary сохраняет начальные digests и final hash diagnostics, не перепривязывает старое разрешение к новой записи. Требуются pure controls final mutation/missing и midstage-stop, positive control; no renderer для этой проверки.

Положительные свойства742: hard3sourcepath allowlist, exact approved source delta,7reused +targetedPasha +fresh5 provenance, all original FAIL preserved, same existing process cleanup/typed parser. Проверено: enable_subreaper() уже находится внутри approvedrun_command передPopen. Моё прежнее предположение о необходимости отдельного вызова уточнено реальным кодом. Эти положительные свойства не закрывают CONT-L01.

Новый63a8-кандидат рассматривается отдельно; данный FAIL immutable. FullP06/native acceptance/readiness/merge/Rootinstall/exports/phase advance не разрешены. Формальный attempt1 не меняется.
