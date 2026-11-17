# Независимое архитектурное ревью предложения по Тимке

**PROPOSAL_NEEDS_FIXES; OWNER_DECISION_REQUIRED.** Предложенное исключение согласуется с каноном и действующей equipment policy, но меняет обязательный художественный контракт P06. Ответ владельца ожидается. Этот документ не принимает исключение, не разрешает его реализацию и не является фазовым FAIL/PASS, source/art-приёмкой, разрешением следующей фазы или merge.

Reviewer `/root/art_olezhka_recovery` независим от единственного автора. Проверены текст предложения и существующие production loader/controller/policy/adopter/packer, тестовые инварианты и gates. WORK только прочитан; запись ограничена тремя файлами этого каталога. Godot, тесты, native capture, builds, Git, сеть и генераторы не запускались; фото не читались. Это анализ проекта изменения по исходному коду, без заявления о реально работающем новом формате.

Предложение: `reports/phases/P06/TIMKA_SUPPORTED_ANIMATIONS_PROPOSAL.md`, SHA256 `a27870889b2a7e93890cab096cdd1cfabb16e81f254f3f2effa98c320c685ed1` (WORK). Полная привязка прочитанных входов — `artifacts.json`.

## Что обосновано

`CHARACTER_EXPANSION_SPEC.md:7` требует action8/finisher8, а `planning/P06_TASKS.md:7` и исходный scope contract считают 96 клеток. Поэтому разрешённые категории и обязательные нарисованные категории сейчас различаются: equipment policy не является уже выданным освобождением от рисунков. После явного согласия владельца можно оформить узкое исключение Тимки, не менять прочих героев и не выдавать ему нож/пистолет. WORLD32 + ACTION28 + FIN24 действительно равно84. Компактные атласы без фиктивных клеток честнее отражают такую поправку.

Текущие зарегистрированные `timka_present`/`timka_prime` и catalog уже ограничивают present: no finishers, ability `disengage`, speed84; prime: unarmed/blunt/environmental, ability `clinch`, speed118. Предложение сохраняет эти границы. Общие пять категорий FIN-02/P04G и путь слабого Yakuza остаются обязательными независимо от числа категорий Тимки.

Запись отказа подтверждает HTTP400/input `moderation_blocked`, request `2f18a694-ee56-482f-888a-361ee16f492d`, без возвращённого изображения, `retried_after_moderation=false`. Это проверка сохранённого артефакта, не независимое наблюдение истории запросов. Отказ сохраняется; новых запросов/обходов это ревью не назначает.

## Уточнения до реализации исключения

### TIMKA-PROPOSAL-01 — HIGH: как выглядит мирный disengage

В компактном FIN предложены `[prep0,unarmed1,blunt2,environment3,recover4,primeclinch5]`, но обещаны две контекстные способности. Схема не определяет презентацию `disengage`. Сегодня `CharacterPlayer.use_ability` реализует только Gabar/Olezhka и отвергает Тимку; общий `special` проигрывает три фазы. Удаление оружейных клеток само по себе не реализует ни одну способность.

Добавить точную таблицу context → ability → движение/target/cancel/cooldown → реальные directional clip/source columns. Для present допустимо осмысленно использовать уже принятые WORLD/ACTION кадры, если они действительно показывают мирное уклонение/отход и shared presentation честно описана. Нельзя незаметно показывать primeclinch, выдавать prime hit/finisher или называть неподвижную позу полноценным новым движением. Если требуются дополнительные рисунки, бюджет84 перестаёт быть окончательным: это надо раскрыть до утверждения, а не скрыть дубликатами. Точные параметры приёма могут уточняться в отдельной реализации, но факт и способ презентации обеих способностей должен быть определён.

### TIMKA-PROPOSAL-02 — MEDIUM: нужен строгий, замкнутый контракт компактной миграции

Фраза «строгая раскладка по actor/kind» верна по направлению, но недостаточна для reviewable migration. Сейчас `character_frames.gd` проверяет schema1/32/384×256, использует глобальные maps и `row*8+column` для sockets; `_valid_sockets` требует32. Packer требует1536×1024 source и32cells; adopter требует `all32_freshly_reviewed`,32nativecells и глобальные MAPS. `_configure_action_frames` комментирует56clips; tests явно проверяют Gabar56 и32socket requirements. Простая смена размеров сломает загрузку; разрешение произвольного count из недоверенного manifest ослабит проверки всех героев.

До кодирования зафиксировать версионированную actor/kind allowlist: WORLD8/384×256/32, Timka ACTION7/336×256/28, Timka FIN6/288×256/24; frame48×64/pivot24,58/four directions неизменны. Остальные actor/kind сохраняют8/32 и прежние требования. Для текущей предложенной раскладки ACTION: shove[0,1,2], interact[3], hit[4], fall[5,6], без fire; FIN: finish_unarmed[0,1,4], finish_blunt[0,2,4], finish_environmental[0,3,4], prime special[0,5,4]. Последний mapping надо согласовать с решением по disengage из01.

Source manifest/review/adopter/packing, runtime metadata/texture rects и sockets должны использовать одну принятую схему, фиксированные ожидаемые размеры/число клеток и sheet SHA. Все84 garment annotations обязательны; кадры источника и animation references считать отдельно. Для такой карты получилось бы44clips/108references, но число зависит от окончательной presentation-карты обеих способностей. Это вычисление по предложению, не результат запуска.

Не выставлять `all32_freshly_reviewed=true` для28/24 и не превращать старый FAIL в допустимую source acceptance. Нужен новый честный count-aware review contract с hash binding и свежей полной приёмкой каждого оставшегося листа. Старые версии/adoptions/reviews сохранить; runtime migration явная, целые клетки без перерисовки анатомии. Новые source rects и provenance должны связываться со старыми целыми клетками. Не распаковывать компактные данные как384wide и не заполнять отсутствующие клипы foreign/default/idle fallback.

`prepare_art(id)` сейчас выполняется ДО bind_policy и до разрушения старого actor. Уточнить: либо он готовит весь строгий Timka84-набор для обоих контекстов, либо новый context-aware API получает только зарегистрированное определение и проверяет свой полный capability contract до switch. Мирный контекст не должен стать способом принять незавершённый P06 набор или пропущенные hurt/fall/death/sockets.

## Что остаётся обязательным после реального owner approval

1. Сохранить ответ владельца с конкретной версией предложения; согласованно обновить SDD, P06 tasks/scope amendment/traceability, asset inventory и критерии CI. Исторический контракт96 не переписывать как будто исключение существовало всегда. До ответа действует прежний контракт; продолжать можно независимые разрешённые задачи текущей фазы.
2. Отказанные sharp/firearm/fire требования отметить как снятые только из нового scope Тимки после утверждения, а не как исправленные рисунки. Остальные findings открыты. В частности независимый `timka_finisher_up5_preflight_v3a` остаётся FAIL: исходная cell29 environmental при переносе станет UP3 компактного листа (index21), но смена индекса не исправляет crown/head/body/hoodie/leg family. Нужна настоящая целая согласованная поза и свежий ART review. Данное ревью не повторяло визуальную приёмку и не назначает генерацию.
3. Реализовать обе способности и три разрешённых prime finisher категории через существующий CombatSystem. Trusted context/fixture/generation/scene_instance/action ability pins, target/range/facing/LOS/registered prop, finite timings/cost/recovery/cancel остаются. Один physics action clock, отдельный contact event и once damage/kill/reward; graphics не наносят урон. Смена present/prime/reset/death/owner до контакта отзывает старый job и оставшихся same-tick recipients.
4. Отсутствующие fire/finish_sharp/finish_firearm отклонять ДО action mutation/reservation/ammo/damage; не надеяться лишь на отсутствие клипа. `_present_action` сейчас не защищает отсутствующий animation/count от отрицательного индекса и заданных phase indices0/1/2; callers должны гарантировать доступность полного клипа. Present не получает prime special даже если он есть в actor atlas. Прямые API/повторный Input/save text/unknown metadata не авторизуют возможности.
5. Обязательны count-aware positive/negative packing/adoption/loader/socket tests, wrong actor/schema/dimensions/count/rect/hash/column cases; полная регрессия прежних8col героев и пяти глобальных категорий. Gameplay tests обеих Timka fixtures: отсутствие запрещённых действий/побочных эффектов, реальные disengage/clinch, cancellation/authority swap, once ledger, environmental target. Не заменять эти проверки меньшим числом зелёных generic tests.
6. Новые native Input/все направления/continuous transitions/contact/recovery/hurt/fall/death/settings/clothing/depth, ART/GAMEPLAY/QA, wall-frame performance, фактические Linux/Wine exports с честным native-Windows статусом и неизменность CH01/StoryState остаются фазовыми gates. Counts/static source review не доказывают их. Formal independent Lead на frozen SHA/base, mandatory CI и GitHub rules/current SHA нужны отдельно. Это ревью не расходует/обнуляет фазовый attempt budget, не меняет AUTOPILOT и не разрешает P07.

## Передача автору

Сначала уточнить01 и02 и дождаться отдельного действительного owner decision. Исправленный proposal можно повторно оценить в этом же bounded scope. При отказе владельца исходный8/8 контракт сохраняется, оружейная source-позиция остаётся со scoped blocker; обход отказа генератора не разрешён. При согласии всё равно нужны реализация и новые независимые проверки. Ни одна текущая source/runtime/phase находка этим документом не закрыта.

Проверки этой сессии: read-only статический анализ и SHA256 входов. Тесты/прослушивание/нативная игра не выполнялись; phase approval=false.
