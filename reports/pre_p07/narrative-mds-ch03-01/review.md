# CH03 — независимый Narrative / paper-contract review01

**PASS_COMPONENT — только текущий Narrative draft CH03.** Обязательных исправлений канона/сцен/бумажной цепочки исходов не найдено. Новый tabletop interaction поддержан как уместное Narrative предложение, **не** как принятая Gameplay/Lead механика или работающая мини-игра.

Привязка: CH03 SHA `b11d8493f07cee7658234edc38d66213de0eba1d4423b099b0b9dd58159c56ac`, заявленный HEAD prefix `d00435ce`. Git не вызывался; authority — actual exact bytes/SHA. Автор — ROOT, reviewer draft не реализовывал. Проверены STORY/GAMEPLAY/AUDIO/DIALOGUE/CHARACTER/template, canonical registry/routes/StoryState и declaration доступного P06 controller. Принятые CH02/CH09/CH11 сопоставлены по неизменённым SHA.

## Канон и необходимость предложения

CH03/EV_CH03_COMPLETE,3/3,past,TEGA,EV_CH02_COMPLETE с пустой production_pending датой совпадают с registry. Прошлая сила армрестлера соответствует CHARACTER_BIBLE и chapter slot. Один анонимный взрослый спортсмен, местный roundloss, небоевые зрители и отсутствие смерти/перелома логичнее раскрывают этот слот, чем ещё одна CH02 арена. Тега узнаваем короткой раздражённой речью, не постоянным криком. Нет PRIME/Макса/Кабана/телефона/кода, жестокости к Ахшару, permanent прокачки или выдуманных D/evidence/отношений.

Автор честно обосновал **один** узкий сценовый interaction необходимостью спортивного эпизода и отличием от CH02/CH09/CH11. Но этот аргумент не заменяет Gameplay/Lead paper approval и actual prototype. Спортивный стол не переименовывается в P06 finisher/HP/kill mode. Новые poses/input driver/UI/checkpoint — High/NOT_CREATED; free-roam factory/policy ещё должны быть определены. Права боевого training контекста не выдаются по произвольному save, стол не регистрируется finisher_enabled/trainbench. Seated ownership явно отзывает movement/ability и очищает Core jobs; обратно управление возвращается один раз послеrelease/resume-lock.

## Paper игра и локальные состояния

Таблица задаёт читаемые ready/load/window/regrip/outcome, fixed циклические load timings,0.25s окно, advantage±1 до±2, settled transaction и отсутствие выгоды от spam. Демонстрация не даёт очков; local loss не равен смерти. Pause/history/held input/scene change обязаны сохранять честный outcome. Это спецификация поведения: доступность0.25s, синхронизация двух рук/позы/HUD/SFX, удовольствие/качество спорта и потоки input ещё **не** проверены. Считать их принятыми нельзя.

CP0/match_ready не восстанавливает pendingrelease или остаток окна: midmatch reload начинаетready0/attempt0. Победа сначала durable win_pending+match_won=true, затем сценаAW03_WIN, только после неё durable exit_ready; глава завершается фактическим выходом, не локальной победой. Первая failed write оставляет безопасное ожидание победного результата без ложного CP1/complete, вторая сохраняет win_pending и допускает повтор safe диалога/записи. Схема допускает только перечисленные stage/boolean пары, invalid save сохраняется/отвергается. Это достаточно ясный paper once-контракт; его typed schema/ресурсные poses/восстановление input ownership/atomicity ещё High и требуют implementation QA.

Карта связана AW0→AW1→AW3 с необязательной AW2→AW3. Место предмета и выход доступны без ключевой fetch-цепочки; перед выигрышем выход честно сообщает незавершённость, не запирает комнату. Стол и seated anchors разнесены как authored closeup, а не как невозможное растягивание WORLD рук. Новые footprints/подходы/кадр/позы надо проверить actual ART/Gameplay, геометрическая таблица не доказательство их реализации.

## Optional запись и готовность

EV_MEMORABILIA_1 действительно относится кCH03 и даёт только flags.memorabilia_1. MEM2 остаётсяCH09, MEM3 —CH14. Существующий EV_SECRET_SUPPOSITORY_CANNON вCH14 требует все три; эта глава не выдаёт сон/пушку/secret. Законченный optional item beat/once ledger и separate local match outcome не превращают skip/replay в farm. Основное завершение не требует медали и даёт только EV_CH03_COMPLETE, CH04 eligible/ещё planned. Реальные endings predicates сохранены.

ANCIENT RAGE past variation и COMBAT как музыкальное напряжение спорта совместимы с AUDIO direction, не означают боевой урон. Арт обеих рук/стол/соперник/медаль/музыка/новые poses NOT_CREATED.5–10min — NOT_MEASURED hypothesis, успешный матч короче; нет обязательных пятиминутных ожиданий/серий противников ради KPI.

PASS_COMPONENT поддерживает NARRATIVE_REVIEWED только этой exact MDS. Не выдано одобрение нового interaction от Gameplay/Lead, actual sport quality/window/calibration, art/audio/runtime, all21/Readiness/production/phase/merge/release. Существующий P06 и другие MDS не переоткрыты. Engine/Controller/generator/network/Git не запускались, source/registry/status не редактировались. Записи только в owned report; source-before/end, snapshots, fact checks/paper traces и FINAL_HASHES сохраняют bounded evidence. После verdict packet immutable.
