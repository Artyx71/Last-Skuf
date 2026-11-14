# P07: независимые разрешения на производство

Кандидат `runner.py` вызывает `readiness.require_p07_production` перед входом в P07. ROOT runner пока не заменён: безопасный handoff остаётся отдельной задачей, действующий stop_after_phase=P06 сохраняется. Поднятие stop limit без handoff/полных gates запрещено. Это дополнение не заменяет существующие GitHub SHA/CI/protection/merge guards.

В каноническом `automation/phase_state.json` после фактического независимого review контроллер сохраняет `autopilot.production_gates` с двумя записями `readiness` и `mission_designs`. Каждая содержит `decision` (относительный путь под `reports/pre_p07/`) и точный `sha256`. Автор не создаёт себе PASS и не вставляет тестовые разрешения в рабочее состояние.

Обе отдельные decision JSON имеют schema=1, status=PASS, acceptance_level=FULL, role=LEAD_REVIEWER, независимого `reviewer`, independent_of_author=true, `p06_base_head` равный подтверждённому reviewed_head или merge_sha P06, пустой must_fix и `source_inventory_sha256` всех рассмотренных файлов. Для Critical/High finding допустимы только CLOSED/RESOLVED/VERIFIED. Нет разрешения по CONCEPT_ONLY/PASS_COMPONENT или по отсутствующему полю.

- Readiness: scope=PRE_P07_PRODUCTION_READINESS, ready_for_p07=true. Inventory включает всё дерево game подтверждённого коммита P06. При входе реальные файлы сверяются также с Git blobs, а не только с заявленными JSON-хешами. Новые/исчезнувшие файлы game блокируют вход; локальные `.godot`/`__pycache__` исключены из сравнения.
- Все21 MDS: scope=P07_MISSION_DESIGN_APPROVAL, approved_for_mass_production=true. `mission_specs` сопоставляет ровно21 ID из канонического registry объектам `{path, sha256}`. Файлы под planning, отдельные, непустые, с разным содержимым, входят в review inventory. Содержательность, уникальность дизайна и соответствие сюжету оценивает независимый Lead с Narrative/Gameplay, а не проверка количества документов.

Чтобы избежать циклической зависимости, полные MDS допускается готовить как неконфликтную PRE-P07 работу при сохранённой P06, до открытия массового производства. Тесты используют только временные Git repositories и фиктивные решения с TEST_ONLY. Они не доказывают готовность игры и не меняют рабочий phase_state.

Действующий readiness FAIL и concept-only PASS сохранены как исторические независимые решения; ни один из них не подходит для открытия этого guard. После исправлений требуется новый полный независимый review, без переписывания старых отчётов.
