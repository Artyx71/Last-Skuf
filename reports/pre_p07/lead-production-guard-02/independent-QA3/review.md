# P07 staged production guard — independent bounded QA v3 / final03b

**FAIL_COMPONENT.** Разделение фактической готовности и будущей контентной приёмки в основном работает, но два malformed-verdict случая ещё допускаются до merge guard. Фактически запущены final03b50/50 tests и47/47 regressions; исходные10 v1 adversarial cases также дают ожидаемые результаты. Из25 дополнительных staged cases23 соответствуют контракту, два — нет. Это новый отдельный QA для exact frozen03b; предыдущие QA1 FAIL/QA2 PASS и Lead semantic FAIL не переписываются.

## Открытые дефекты

**PG-C05 / HIGH — duplicate raw closure ID silently overwrites FAIL and reaches PUT.** Actual runner.load использует обычный json.loads. В полностью синтетическом JSON verdict присутствуют два new_audio_acceptance keys внутри closed_obligations: первый statusFAIL/evidence[], второй statusPASS с валидным fake proof. Parser сохраняет только последний. Actual validate_review возвращает errors[], guarded_merge проходит оба snapshot gates и вызывает request spy с PUT squash. Spy не выполняет сеть и возвращает merged:false, поэтому итоговый BLOCKED — только его заглушенный ответ после запроса, не отказ validation. mock_PUT_count=1, actual_network_requests=0.

Это прямое нарушение acceptance требования Lead: missing/extra/duplicate closure IDs deny. Dict set equality и JSON schema уже не видят дубликат после last-wins parse. QA не утверждает, что реальный Codex CLI сгенерировал такой output; проверяется настоящий cache/verdict loader и повторная merge validation. Сырой конфликтный JSON сохранён в duplicate-raw-verdict.TEST_ONLY.txt; отдельный duplicate-proof.py повторяет фактическую цепочку load→validate→оба snapshots→request spy. Все Git/state/proofs только во временном тестовом repo.

Исправление: strict duplicate-key JSON decoding на реальных ingress/cache/receipt/state boundaries, включая загрузку независимого verdict и readiness receipts; неоднозначные записи должны отвергаться до создания обычного dict. Не заменять это авторским no_duplicates flag или тестом заранее построенного dict. Добавить actual raw JSON regression с противоречивыми closure statuses и подтверждением0 PUT. Поведение старых корректных исторических receipts сохранять; malformed данные не переписывать молча.

**PG-C06 / MEDIUM — malformed phase findings object accepted.** При остальных валидных P07 closure полях findings={} принимается с validate_review errors[]. Внешняя schema требует array, но runtime PASS validator перебирает review.get('findings',[]) без проверки типа контейнера; пустой dict просто даёт ноль iterations. Это существующая runtime schema-validation щель, теперь подтверждённая на новом full P07 gate, а не регрессия самого staged concept. Исправление: явная typed list validation до итерации, корректные структурные отказы для malformed phase records; не полагаться только на output schema производителя. Добавить отрицательные cache/validate/merge tests для object/null/других неверных containers.

Автор уведомлён, v4 исправление отдельно. Этот immutable v3 отчёт опирается на сохранённые исходники final03b и не требует, чтобы последующий WORK v4 оставался побайтно равным v3.

## Что реально подтверждено

Прочитан actual Lead corrective stage contract SHA d349be21d7c7678b75b2e2c7bc85387e460fc79ea04f67970a9399631c94c0ad и полный semantic FAIL PG-L05. Generic P07 остаётся массовым executor: полные21 MDS и actual six-capability matrix нужны до входа. Future obligations имеют ровно четыре известных ID, HIGH/OPEN, фиксированный enforce_at=P07_LEAD_PASS_AND_MERGE, requirement и source_findings trace. Они больше не требуют ложного преждевременного CLOSED.

Independent probes показывают: правильные future OPEN obligations допускают synthetic mass entry; отсутствие каждой из6 capabilities блокирует; строка DESIGN_ONLY не обходит missing capability; неизвестный stage и missing/extra obligation блокируют. P07 full PASS требует inline production_acceptance: unknown scope, boolean schema, missing/extra closure ID, stale P07 head, stale readiness SHA, FAIL closure и empty evidence отвергаются. Положительный control с четырьмя closure entries и actual hashed temporary evidence проходит; это только machine-contract test, не настоящая контентная приёмка.

Два independent second-snapshot tests действительно проходят первую проверку, затем меняют canonical Readiness SHA или actual proof file перед вторым snapshot. Повторная gate validation возвращает BLOCKED с snapshot_count2/request_count0. SHA/CI/protection/manual approval guards не удалялись; existing47 также проходят. Не было реальных HTTP/API/GitHub действий.

Canonical ROOT проверен настоящим linked temporary Git worktree: создан новый P07 commit с новым content source, отличный от P06; WORK historical state заведомо неверен. Валидный canonical ROOT receipt позволяет closure при exact new P07 HEAD; удаление ROOT readiness затем блокирует, хотя stale WORK copy остаётся. Это подтверждает фактический Git common-dir resolution и отсутствие self-commit-SHA cycle для inline verdict; full production resume/merge на реальном репозитории не запускались.

Исходные symlink/path/schema/severity repro из QA1 остаются закрыты. Valid P07 workspace progress/resume не сбрасывается. Все тесты и state/Git mutations существуют только в ROOT TemporaryDirectory fixtures. Сам reviewer не вызывал WORK/real ROOT Controller, GitHub, engine, авторский executor или каноническую очередь.

## Версия схемы, границы и handoff

До исполнения сохранён final guard-author-03b freeze, включающий required nullable production_acceptance для остальных фаз и strict object required-field schema contract. Ранняя49-test версия была только прочитана; она не использована как executed QA freeze. Фактический запуск —50 tests. Проанализированы exact frozen readiness/runner/github/schema/prompt/protocol/tests; копии и hashes публикуются в manifest.

ROOT дисковые файлы по read-only observation не содержат нового hook, stop_after_phase=P06. Это не проверка живого процесса и не разрешение установки. Full verify_p06/safe handoff, реальные fullP06/CI/protected merge/readiness/21MDS, настоящие возможности/содержимое/listening, полный P07 Lead и P08/release не принимаются этим отчётом. Actual future evidence оценивает независимый Lead; количество фиктивных proof files не подменяет игру.

Portable artifacts включают исходники, schema/prompt/protocol, воспроизводимые probes, raw TEST_ONLY verdict, logs/results и inventory; temporary repos/канонический state/queue исключены. Для повторения копировать manifest в новый ROOT report directory, создать tmp, использовать TMPDIR и PYTHONDONTWRITEBYTECODE; не перезапускать поверх immutable evidence. Нужны отдельные v4 fixes→freeze→QA→Lead, без изменения старых решений.
