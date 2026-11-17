# PRE-P07 H02 — навигационный пилот

Это проверка технической способности pipeline, не готовый уровень, не полный H02 и не PASS P07. Базовая P06/DEV09 сохранена. Production host кампании ещё не подключён к адаптеру. Каноническая ROOT Game остаётся frozen P06 `f8325212381d67a469b5d9a6dffbf3d244bc9933`; изменения пилота находятся в phase/p07-implementation.

## Доказанный пробел и минимальное изменение

На исходной реальной AI/Physics P06 патрульный, rusher и shooter проходят открытый маршрут, но все три застревают внутри П-образного препятствия. Сохранённый diagnostic: `reports/pre_p07/navigation-baseline-01`, canonical operation `318035635d4f44be838802ed876d6fd1`.

Optional hook добавлен только в `_walk_to`: host с `navigation_velocity` предоставляет скорость обхода, остальные host используют прежнее прямое движение. `room_navigation.gd` выбирает маршрут по физическому прямоугольному footprint, проверяет реальные body sweeps и границы, ограничивает движение шагом speed×delta. FSM, видимость, telegraph/contact, damage/score, hitbox и collision masks не изменены. Grid/cache ограничены 8 профилями и128 actor paths; layout revision инвалидирует маршруты.

QA host в `tools/fixtures/p07_navigation_host.gd` читает настоящие прямоугольные blockers и обновляет revision при их изменении. Это диагностический host размером640×360, не универсальный импортёр будущих уровней.

## Реальные прогоны

Все команды прошли через единственный канонический ROOT executor. Каждый использовал новый изолированный проект и XDG-профиль, pinned Godot4.7.2 с editor import. Исходники до/после совпали. `--fixed-fps60` используется только для функциональных physics ticks; это не измерение FPS, физической задержки ввода или длительности главы.

| Срез | Source | Результат | Evidence / operation |
|---|---|---|---|
| Исходная AI | fafd2808 | open3/3; U0/3 | navigation-baseline-01 / 318035635d4f44be838802ed876d6fd1 |
| Первый adapter | 1e227d44 | open3/3; U3/3 | navigation-router-01 / f65e4de0bd07499ba87afae6cf297f7d |
| Boundary fix + двери | 0712e3de | 70/70 | navigation-contract-01 / 396075f54d664d929c75cfac69f2a205 |
| Fixed U + fallback | 0712e3de | open3/3; U3/3; existing actual Input72/72 | navigation-router-02 / fa351958acf243058194609c252981a8 |

Набор70 проверяет три настоящих архетипа: закрытую дверь и открытие, закрытие/открытие во время движения, непроходимый зазор10px, проходимый48px, обход стены, overlap/jump в каждом отслеживаемом physics tick, reset path cache, сохранность combat state, выход за четыре границы и invalid speed/delta. Отдельные LOS-прогоны используют живого игрока: стена запрещает обнаружение/атаку; без стены проходит telegraph→attack и настоящий damage/death. Отключён только physics игрока, его health/LOS/боевые queries не подменены.

Первый независимый QA вернул FAIL_COMPONENT: direct sweep мог обойти проверку навигационных границ. Старый отчёт `qa-navigation-router-01` сохраняется. В0712e3de проверка всего footprint до arrival/direct sweep закрывает NAV-Q01; independent `qa-navigation-router-02` принял именно70 проверок и этот source. Поздний6+72 прогон не приписывается завершённому QA02; его отдельно оценивает Lead.

Existing72 проверки используют SOURCE headless на обычном host без navigation hook. Надпись PACKAGED внутри старого test script — legacy label, здесь не новый export.

## Что остаётся до полного navigation readiness

- Подключение согласованного production room host и чтение геометрии реального пилотного уровня, включая дверь/альтернативный маршрут. Не подменять готовую главу синтетической ареной.
- Проверить планировочные размеры и доступность всех обязательных маршрутов: grid16 консервативен; clearance near minimum и shifted/nested/rotated geometry не принимаются по текущим48px fixtures. Unsupported body shape не получает выдуманный маршрут.
- Прогнать именно реальные игровые роли patrol/investigate/pursue и потерю/возврат LOS. Существующая pursue→patrol при потере видимости и2.1s investigate не изменены; патрульный U-тест не доказывает преследование через комнаты. Изменять FSM только при подтверждённом mission-specific требовании и отдельном review.
- Native визуальная читаемость движения/разворотов, несколько одновременно действующих NPC/динамических препятствий, frame-time на заявленном оборудовании. Headless counters не подтверждают ощущения или производительность.
- Проверить reset/retry/save переходы на настоящем room director. Нынешний reset проверяет реальный CombatLab, не будущие chapter checkpoints.

Итоговый navigation_pilot receipt выдаёт независимый Lead по этому и последующему фактическому evidence. Component PASS не закрывает остальные readiness capabilities,21MDS, P07 content obligations или P08.
