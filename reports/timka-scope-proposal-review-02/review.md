# Независимое bounded review — предложение Тимки V2

**OWNER_DECISION_REQUIRED.** Два замечания первого proposal review закрыты **только на уровне уточнения предложения**. Новых блокирующих архитектурных ошибок в V2 не обнаружено. Исключение не утверждено и не применено: действительный ответ владельца по-прежнему необходим. Это не фазовый PASS/FAIL, не source/runtime приёмка, не разрешение изменить контракт, merge или перейти в P07.

Reviewer `/root/art_olezhka_recovery` независим от единственного автора. Проверены V2 и привязка к фактическим исходникам первого review. Все29 входов первого review, включая неизменённый V1, имеют прежние SHA256. Текст V2 сопоставлен с Frames/CharacterPlayer/ScenePolicy/CharacterLab/adopter/packer, текущим SDD и gates, рассмотренными в первом review. Рабочая копия не изменялась. Тесты/Godot/native/build/Git/controller/генераторы/сеть не запускались; raw photos не читались. В этом каталоге записаны только review.md, decision.json и artifacts.json.

V2: `reports/phases/P06/TIMKA_SUPPORTED_ANIMATIONS_PROPOSAL_V2.md`, SHA256 `d20a236d5c93d0186f83fcda98950aa9334a692923a0e275ddadcb295705c024`. Полный input inventory и SHA предыдущего review находятся в artifacts.json.

## TIMKA-PROPOSAL-01 — CLOSED_FOR_PROPOSAL_ONLY

V2 явно отделяет present `disengage` от prime `clinch`. Для мирного контекста предложена проверяемая цепочка ACTION0 guard → четыре собственные WORLD walk-фазы в обратном временном порядке → ACTION2 recovery, без damage/неуязвимости/добиваний. Ограниченное движение назад проходит collision, authority/cancel/cooldown сохраняются. Текст честно называет это повторными ссылками на существующие рисунки, а не новыми уникальными клетками. Если реальные переходы неприемлемы, V2 требует дополнительные настоящие рисунки, отдельный учёт их количества и новый review; prime fallback запрещён.

Это достаточно конкретный план для будущей реализации и проверки; возможность художественно убедительно показать такой отход пока НЕ доказана. Утверждение владельцем исключения трёх оружейных категорий само по себе не утверждает качество этой хореографии. Полная P06 требует обе реализованные способности и оба контекста, даже если present разрешено отдельно осматривать раньше.

## TIMKA-PROPOSAL-02 — CLOSED_FOR_PROPOSAL_ONLY

V2 ограничивает schema2/profile только Тимкой; остальные actor/kind сохраняют прежнюю строгую schema1 8×4. Заданы фиксированные WORLD384×256/32, ACTION336×256/28 и FIN288×256/24 при48×64/pivot24,58/four directions. Явно определены whole-cell source mappings: ACTION old0–6, FIN old0,1,2,5,6,7; weapon clips отсутствуют и не имеют fallback. Source/native/frame RGBA/hash/count, новая truthful all-required-cells независимая source acceptance и garment sockets связаны с профилем и реальным числом клеток.

Фабрика теперь описана как preparation по зарегистрированному scene key, с проверкой полного набора данного контекста, clothing sockets и реализованного handler ДО reset/invalidate/removal. Bind повторно сверяет actor/context/ability. При preflight отказе старое состояние сохраняется; после начала commit-перехода несовпадение блокируется fail-closed. Непринятый prime-набор нельзя считать готовой фазой из-за доступности отдельного present-набора.

Это закрывает отсутствие строгого миграционного контракта в V1. Ни существующие loaders/adopter, ни код актёра не стали автоматически совместимыми: сейчас они всё ещё имеют32/8-column инварианты и требуют отдельной согласованной реализации/тестов.

## Реализационные ограничения, не новые блокеры предложения

- Предложенный disengage имеет шесть последовательных texture references на направление, тогда как нынешний `_present_action` для `special` жёстко выбирает кадры0/1/2. Нужен собственный phase-aware presentation mapping с четырьмя walk-позами в средней фазе, под одним physics clock и без animation-callback damage. Простое добавление шести кадров в прежний `special` не реализует предложенную цепочку. Prime special остаётся отдельным разрешённым маршрутом. Четыре дополнительных directional disengage clips, если оформлены отдельно, увеличивают reference/clip counts, но не число уникальных source cells.
- При byte-exact WORLD PNG его действительный SHA остаётся прежним. «Новый sheetSHA» для sockets означает SHA фактического соответствующего PNG, а не искусственно отличающееся значение ради metadata migration. Старые source/adoption/review версии сохраняются, новый schema/profile/source mapping проверяется отдельно; socket points при whole-cell remap могут остаться теми же локальными integer coordinates, но должны быть заново корректно сопоставлены и проверены.
- Atomic preparation не является обещанием отката после уже выполненного reset. Нужна проверка отказов ДО разрушения старого состояния и безопасно заблокированное состояние при неожиданной смене key/context/ability на commit/bind; никаких частично авторизованных действий.
- Источник обязательных counts/maps — allowlist production contract, не произвольный manifest/save. Нельзя ослабить отрицательные проверки unknown actors/schema/dimensions/count/rect/SHA/socket/unsupported clips для остальных героев. Новый source review должен реально осмотреть все необходимые32/28/24 клетки и не наследовать старый FAIL как acceptance.

## Что остаётся обязательным

1. Получить и сохранить отдельный явный owner decision с конкретной версией исключения. До него V2 остаётся PROPOSED; прежний8/8 SDD не изменён. После согласия оформить узкую поправку SDD/planning/scope/traceability/asset inventory/CI; исторические96 и отказы сохранить.
2. Исправить и независимо принять оставшиеся обязательные рисунки. Environmental `TIMKA-FINISHER-SOURCE-UP5-FAMILY-03` по source29 остаётся OPEN: compact UP3/index21 наследует рисунок, не исправление. Weapon-source находка/HTTP400 request2f18a694-ee56-482f-888a-361ee16f492d сохраняются в истории; исключение, если утверждено, снимает requirement из нового Timka scope, а не объявляет рисунок исправленным. Новых запросов/повторов/обходов review не назначает.
3. Реально реализовать и проверить both-context abilities, три prime categories с собственной читаемой постановкой, eligibility/facing/range/LOS/environment/finite timing/cost/cancel. Только CombatSystem начисляет damage/kill/reward; once receipts, один action clock, pinned live authority и отмена при reset/death/смене сцены неизменны. Present не получает prime ability/finishers/weapon fire; forbidden direct APIs отвергаются до любых side effects.
4. Пройти обязательные negative/positive schema/packing/adoption/socket и atomic-context tests, реальный Input/native art/timings/continuous joins/garment overlays, settings invariance/performance, Linux/Wine exports с честным native-Windows статусом, регрессии Gabar/Oleg/Yakuza/CH01/StoryState. Общие пять категорий FIN-02/P04G не сокращаются исключением Тимки.
5. Отдельные ART/GAMEPLAY/QA и formal Lead на frozen source/base, mandatory CI/current SHA и GitHub protections сохраняются. Этот документ не изменяет phase attempt budget, AUTOPILOT, source FAIL или полномочия merge/next phase. Независимые уже разрешённые задачи внутри P06 могут продолжаться.

Рекомендация автору: техническое предложение достаточно уточнено для решения владельца. Ожидать ответ по исключению; не применять его по этому документу. После разрешения реализовывать контракт с новыми evidence и review; при отказе оставить исходные требования и scoped blocker.
