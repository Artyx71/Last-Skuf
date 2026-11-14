# P07: независимые разрешения на производство

Кандидат `runner.py` вызывает `readiness.require_p07_production` перед общим P07 mass-production executor. ROOT runner пока не заменён: безопасный handoff остаётся отдельной задачей, действующий stop_after_phase=P06 сохраняется. Поднятие stop limit без handoff/полных gates запрещено. Это дополнение не заменяет существующие GitHub SHA/CI/protection/merge guards.

В каноническом `automation/phase_state.json` после фактического независимого review контроллер сохраняет `autopilot.production_gates` с двумя записями `readiness` и `mission_designs`. Каждая содержит `decision` (относительный путь под `reports/pre_p07/`) и точный `sha256`. Автор не создаёт себе PASS и не вставляет тестовые разрешения в рабочее состояние.

Обе отдельные decision JSON имеют schema=1, status=PASS, acceptance_level=FULL, role=LEAD_REVIEWER, независимого `reviewer`, independent_of_author=true, `p06_base_head` равный подтверждённому reviewed_head или merge_sha P06, пустой must_fix и `source_inventory_sha256` всех рассмотренных файлов. Для фактических предпроизводственных Critical/High findings допустимы только CLOSED/RESOLVED/VERIFIED. Будущая приёмка ещё не созданного контента задаётся отдельными обязательствами ниже; её нельзя ложно закрывать до производства. Нет разрешения по CONCEPT_ONLY/PASS_COMPONENT или по отсутствующему полю.

- Readiness: scope=PRE_P07_PRODUCTION_READINESS, ready_for_p07=true. Inventory включает всё дерево game подтверждённого коммита P06. При входе реальные файлы сверяются также с Git blobs, а не только с заявленными JSON-хешами. Новые/исчезнувшие файлы game блокируют вход; локальные `.godot`/`__pycache__` исключены из сравнения.
- Все21 MDS: scope=P07_MISSION_DESIGN_APPROVAL, approved_for_mass_production=true. `mission_specs` сопоставляет ровно21 ID из канонического registry объектам `{path, sha256}`. Файлы под planning, отдельные, непустые, с разным содержимым, входят в review inventory. Содержательность, уникальность дизайна и соответствие сюжету оценивает независимый Lead с Narrative/Gameplay, а не проверка количества документов.

Чтобы избежать циклической зависимости, полные MDS допускается готовить как неконфликтную PRE-P07 работу при сохранённой P06, до открытия массового производства. Тесты используют только временные Git repositories и фиктивные решения с TEST_ONLY. Они не доказывают готовность игры и не меняют рабочий phase_state.

Действующий readiness FAIL и concept-only PASS сохранены как исторические независимые решения; ни один из них не подходит для открытия этого guard. После исправлений требуется новый полный независимый review, без переписывания старых отчётов.

## Фактическая готовность и будущая приёмка — разные gates

Общий `run_phase(P07)` остаётся массовым исполнителем. Все21 MDS обязательны до его запуска. Неконфликтную design/pilot подготовку можно выполнять ранее в PRE-P07 без смены фазы и без сброса существующего P07 workspace. Отдельного незащищённого design-stage string нет.

Независимый FULL readiness receipt содержит `preproduction_capabilities`: ровно full_p06, safe_handoff, navigation_pilot, audio_playback_pipeline, pacing_instrumentation, secret_integration_contract. Каждая запись — status=PASS и непустой evidence[{path,sha256}], входящий в source_inventory_sha256. Это реальные, уже проверенные способности pipeline: полный P06/merge; full verifier и безопасный ROOT handoff; representative навигационные fixtures; actual mixer/retry/loops и слушание нового P06/pilot audio; instrumentation/current calibrated pilot; полные отдельные bonus MDS и проверенный namespace/once/save migration contract до соответствующей интеграции. Название файла не доказывает содержание; независимый Lead проверяет сами evidence.

Ещё не созданный контент не требует преждевременного playthrough и не объявляется CLOSED. Тот же независимый readiness receipt задаёт `future_acceptance_obligations` ровно с четырьмя ID:

| ID | Что реально проверяется после создания контента |
|---|---|
| chapter_delivery_21 | Все21 реальные главы: карта/проходимость/особенности героя/постановка/ветки/save/ART и реальный Gameplay/QA |
| campaign_pacing_actual | Реальные chapter/route/death/retry/idle/input/wallframe данные, темп и осмысленность уровней; целевые7–9h проверяются по прохождениям, не по расчёту |
| new_audio_acceptance | Настоящие per-chapter/newhero files, signal/runtime/mixer/loop/transition/retry и фактическое слушание нового материала |
| secret_delivery_7 | Пять canonical +два отдельных бонуса: полные MDS/Narrative/Lead до производства, integration contract до интеграции, затем actual levels/once/save/old-save/ending/playthrough evidence |

Каждая obligation имеет неизменённую severity=HIGH, status=OPEN, enforce_at=P07_LEAD_PASS_AND_MERGE, содержательный requirement и непустой source_findings[] для трассировки исходного замечания/требования. Missing/unknown stage/понижение severity/ложный CLOSED блокируют вход. Разделение этих обязанностей с фактическими предпроизводственными findings делает только независимый Lead в новом hash-bound решении, автор не редактирует старый FAIL.

## Закрытие после реализации

Существующий независимый full P07 reviewer заполняет inline `production_acceptance` в своём verdict: integer schema=1, scope=P07_CONTENT_ACCEPTANCE, reviewed_commit=currentP07head, readiness_sha256=каноническое решение, closed_obligations=ровно те же четыре ID, каждый status=PASS и непустые evidence[{path,sha256}]. Все nested evidence также входят в общий review.evidence и реально проверяются по хешам. Judgement находится в независимом verdict вне WORK, поэтому не возникает невозможного committed proof с собственным финальным commitSHA. Отдельный авторский checklist PASS не принимается.

`github.validate_review` запрещает запись full P07 PASS без этого closure. `guarded_merge` вызывает ту же проверку по актуальному canonical ROOT state и обоим fresh GitHub snapshots, включая непосредственно перед squash; SHA/CI/protection/manual approvals остаются обязательными. Canonical ROOT определяется через Git common-dir, stale phase_state внутри WORK не используется. Missing/stale contract/head/evidence/обязательство блокирует merge без PUT. FAIL/BLOCKED не обязаны выдумывать готовую closure и не разрешают merge. Прежние phase gates сохраняются.

Readiness PASS разрешает производство; full P07 PASS и merge принимают уже сделанный контент. Ни один из этих уровней не подменяет другой и не разрешает P08/release. ROOT installation/safe handoff всё ещё отдельная задача: module/component QA не ставит себе actual readiness PASS.
