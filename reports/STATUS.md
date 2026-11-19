# Статус проекта

Независимые QA и Lead приняли H04 как **PASS_COMPONENT**: измерение программной реакции на ввод, времени кадра и восстановления после смерти плюс короткий маршрут CH01 с движением/камерой. Lead: [решение](pre_p07/lead-pacing-acceptance-01/decision.json), SHA `ba6c5f22…`. Это компонент подготовки, общий Production Readiness ещё не принят; массовое производство P07 закрыто.

Свежий native Linux прогон `a75a4330de35414ab87b8a143a28cce0`: 74 проверки, 48 запросов в восьми контекстах, восемь настоящих смертей от Core. По заранее утверждённому контракту: ввод→наблюдаемое принятие p95 17.914мс (<34); ввод→изменённое post-draw состояние p95 18.876мс (<60); контролируемые кадры p95 17.093 / p99 17.567мс (<24/33); смерть→скриптовое восстановление управления максимум 16.722мс (<1000). Это программные наблюдения, не измерение клавиатура→пиксель/фотон. Контакт удара измерен отдельно от начала действия. Hardware Ryzen5 3600/GTX1050Ti/X11/Godot4.7.2/60Hz physics/max60.

Сырые ряды, контракт, исходники до/после, логи и 105 свежих кадров/видео сохранены в `reports/pre_p07/pacing-acceptance-01`. Lead просмотрел все105 выборочных кадров и четыре исходных640×360 кадра; независимый Gameplay дал ограниченный PASS читаемости маршрута. Это не интерактивная оценка combat feel и не полная запись каждого draw. NPC в клипе активируются после диалога; ошибочное прежнее описание «отключены» исправлено отдельными erratum без переписывания старых отчётов. Capture/readback/setup/idle/death-wait исключены из performance budget согласно контракту. Все пять порогов зафиксированы до свежего acceptance, исходные FAIL и исправления валидаторов сохранены.

Последняя полная принятая и слитая фаза — P06: [PR11](https://github.com/Artyx71/Last-Skuf/pull/11), squash `f8325212381d67a469b5d9a6dffbf3d244bc9933`. Все21 основные MDS получили FULL independent Lead DESIGN PASS `c8123ab2…`; canonical mission_designs gate записан, frozen24 planning не менялись. Это проекты глав, а не готовая кампания; цель7–9часов **TARGET_NOT_MEASURED**.

H02 second pilot/routerfix приняты как компонент Lead `70aa8ad1…` и QA `433c0132…`, source `c3ea57f5`, router `f9f23f82…`. Проверки121headless/102nativeLinux/70legacycontract/18room/28mission/58CH01native,10death/retry;12PNG. Исторический native05 FAIL сохранён, причинаUNKNOWN; пороги не ослаблены. FullH02 и реальные chapter-specific geometry/followers/doors/checkpoints остаются отдельными обязательствами.

Audio pipeline audit PASS_COMPONENT `9ffd7b3d…` поддерживает принятую P06 prototypeспособность:233файла совпали с принятымиP06SHA,13historicalmedia сохранилиSHA; прежнее ownerlistening сохранено. Нового прослушивания/музыки/миксов не было. Dedicated scene-reload acoustic continuity ещё требует проверки; разныхscore crossfade нет.

Два отдельных полных бумажных MDS бонусов и контракт сохранений приняты независимым Lead `a04b0a71…` на `947045bd`, после исправлений Gameplay/QA. Старые FAIL сохранены. Габар — сервисная петля/узлы/lunge; Олег — радиальные секторы/оглушение/отход/физическая изоляция без обязательного убийства. Это DESIGN_ONLY: сцен/миграции/ассетов/новых тестов бонуса ещё нет.

Далее: реальный изолированный compatibility pilot BP01–09 (namespace/defaultfalse/once/old-save/replay/profile/crash) и независимая приёмка; только затем отдельная FULL Readiness-приёмка всех направлений. BP10 — будущие реальные уровни/ART/audio/native acceptance, HIGH OPEN. Будущие ART/audio/пейсинг/геометрия принимаются по фактическому контенту. P07 PENDING/formal0, stop_after_phase=P06, global2; компоненты не разрешают phase/merge. НовогоPR/push/CI нет. Один ROOT executor, постоянныйdaemon не настроен.

Candidatefix/H04helpers находятся в WorkP07; RootGame остаётсяP06. A/B/C technicalhandoff и21MDS не повторять. ФотоAKIMBO69 приватное; CH03анимация/QTE ещё NOT_IMPLEMENTED,12private references, новыхгенераций/публикаций нет.

Прежняя сборка: `build/PRE_P07_DEV_20261117_10/PLAY_LINUX.sh` и `PLAY_WINDOWS.cmd`, EnterCH01/F5герои/F6портреты. Новый navfix/H04helpers не экспортированы. Linux/Wine проверки сборки исторические; nativeWindows **NOT_TESTED**.

Resume: `reports/phases/P07/resume/decision.json`; authority `automation/phase_state.json`, mirror `.autopilot/STATE.json`. Последняя операция a75 завершена/consumed/exit0; не перезапускать её автоматически после прерывания.
