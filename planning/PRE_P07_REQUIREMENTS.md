# PRE-P07 / P07: новые требования владельца

Статус: INDEPENDENT_READINESS_FAIL_REMEDIATION_QUEUED. Источники — прямые поручения MISSION PACING & LEVEL DESIGN QUALITY GATE, HIGH-INTENSITY GAMEPLAY & PACING, PRODUCTION READINESS AUDIT. Утверждённый сюжет и выполненные фазы сохраняются. P06 не перезапускается. Это не21 готовая MDS, не28 готовых миссий и не доказательство готовности P07.

## Условия продолжения

Владелец разрешил автоматический P07 после полного P06 PASS/CI/защищённого merge и независимого Lead Production Readiness PASS. До массового производства Lead должен принять21 отдельную MDS. Nonconflicting audit/шаблон/реестр допустимы во время P06. Запуск контента P07 до gates запрещён. Текущий технический stop-limit P06 остаётся до тестируемого добавления readiness guard и безопасного ROOT/WORK runner handoff; новая авторизация сама не снимает gate. P08/release не авторизованы этим решением.

## Продолжительность и MDS

Цель —420–540мин первого прохождения, включая реальные смерти/повторные попытки. Это оценочная цель, NOT_MEASURED. Не суммировать все взаимоисключающие ветки, повторный просмотр, AFK или100% secrets как обязательную длительность одного маршрута. Для каждой канонической/доступной альтернативной ветки нужны реальные игровые прогоны, wall-clock и разложение combat/traversal/story/deaths/retry; сохранять число игроков/первых прохождений, разброс и условия. Короткие мемные эпизоды могут занимать5–10мин; не растягивать их ради суммы.

Нужны единый шаблон и отдельные содержательные21MDS: хронология/event_id/POV; герой/механики; карта связанных зон и порядок помещений; цели/победа/поражение; позиции/archetypes врагов; инструменты/взаимодействия; уникальные encounters; boss phases если сюжет предусматривает босса; диалоги/cutscenes/transitions; adaptive music/SFX; secrets/альтернативы; story flags; assets; тестовые сценарии/критерии. Каждая глава имеет вступление→развитие→кульминацию→завершение, свою идею и критерии отличия от остальных. CyberX и финальный PRIME — многоэтапные. Не добавлять боссов или менять сюжет ради checklist; предусмотренные боссы имеют уникальные читаемые механики.

Обязателен реестр21main+7secret production slots. Фактический утверждённый specs/STORY_SPEC.md §6 и game/resources/story/registry.json содержат21main+5definedsecrets. Владелец разрешил два необязательных предложения: SECRET_OFFLINE_BUILD и SECRET_COUNTER_LESSON. Они получили отдельный Narrative/Lead CONCEPT_ONLY PASS; полные MDS, канонизация и runtime ещё не приняты. См. planning/missions/OPTIONAL_CONCEPT_REVIEW_FOLLOWUPS.md. Это не блокирует P06/build.

## Динамика и отзывчивость

Переиспользовать работающие clock/contact/hitstop/knockback/restart/music/save systems. Измерять software Input→accepted action/первый видимый отклик отдельно от намеренного windup/contact. Отдельно фиксировать OS/hardware latency, если реально доступна; injected Engine.Input не называть физическим замером клавиатуры. Быстрые читаемые атаки/смена оружия/короткий hitstop/направленное отбрасывание требуют native Gameplay review. Не ускорять анимации только численно. Input buffering вводить лишь по доказанной необходимости: ограниченная длительность/одна заявка, истечение/очистка на death/reset/pause/context change, без дублей damage/score.

Slow Yakuza ≠ медленные миссии: преследование, ограничения, события, пути побега/отвлечения/окружение; семь героев меняют игровой ритм, не только скорости. Combat encounters чередуют открытые/тесные зоны, разные enemy combinations, интерактивное окружение и оправданные обходы; исключить пустой бег. Сложность не наращивается только HP/числом врагов. Проверять layout similarity и реальные сценарии; переименование арены/врага не уникальность.

События lights/reinforcements/routes/POV/objective/story должны быть сценарно обусловлены и воспроизводимо предсказуемы при retry, если влияют на выживание. Нет случайных неизбежных смертей. Сохранять быстрые scene transitions, skip уже просмотренного и короткий retry, выразительные chapter cards, естественные диалоги и спокойные сцены без удаления важных сюжетных моментов.

Music: Exploration→Tension→Combat→Aftermath как смысловые состояния, с явным mapping на текущие API; transition/bar alignment/volume/no abrupt cuts. Смерть не обязана перезапускать композицию; проверить actual playback position/retry/duck/reload без наложения слоёв. Новую музыку принимать по реальным файлам/signalQA/listening, не именам states.

## Production Readiness и измерения

Аудит8 направлений: combat/finishers; player/NPC animations; AI/navigation; dialogue direction; music transitions; storyflags/save; UI/VHS/scene transitions; performance/effects. Для каждого: реальный код/assets/evidence/существующие tests, partial parts, блокерыP07 и допустимыйP08 debt. Critical блокируетP07; High исправить до массового соответствующего контента; Medium P07–P08 с конкретным ticket/gate; Low косметика. Не объявлять старую фазу FAIL без новых доказательств и не принимать авторский отчёт за independent verdict.

Gameplay Pacing Review обязателен в P07 и финальном P08: Input-to-action latency, time-to-restart, интервалы без значимого действия, уникальные encounter scenarios, причины/частота смертей, длительность каждой главы/маршрута, actual wall-frame FPS/frame-time distribution, real music transitions. Отделять AFK/pause/целенаправленное исследование/важную режиссуру от пустого ожидания; не вырезать их для искусственной метрики. Численные пороги после baseline calibration фиксируются до acceptance run; исходный retry gate<1000ms сохраняется. Headless fixed-fps/physics delta/расчётные бюджеты не доказывают renderFPS, input hardware latency или7–9часов.

Readiness/полныеMDS/пилоты/производство/послепроизводственные реальные прогоны имеют отдельные independent Gameplay/Narrative/Art/QA/Lead gates и конечные FAIL→FIX→REVIEW tickets. Сам шаблон/реестр/план не результат readiness. P06 полностью PASS/MERGED, PR11 squash f832 подтверждён. Полный readiness PASS отсутствует.

Независимый аудит: reports/pre_p07/lead-readiness-01/decision.json — FAIL только по readiness, без изменения P06/прежних PASS. Девять конкретных замечаний сохранены в findings.json и очереди. Защита перехода фактически установлена в ROOT A/B/C и отдельно принята в technical safe_handoff review; stopP06 сохраняется до всех полных gates. Навигационный пилот и оставшиеся ограничения: planning/PRE_P07_NAVIGATION_PILOT.md.
