# Независимый ART source preflight: Рыжик ACTION32 v1a

**ACCEPTABLE_SOURCE_CANDIDATE**, только нормализованный v1a и его точный native preview. Raw v1 и его прежний pack failure сохранены. Runtime/ability/полная P06 не принимаются.

Reviewer `/root/art_timka_fin_v4` независим от генерации/normalizer/packer автора. WORK и ignored pending source только прочитаны; свои файлы — только ROOT `reports/phases/P06/art-preflight/ryzhik_action_v1a_*`. Godot/builders/controller/Git mutations/generation/network не запускались, фотографии не читались/не копировались/не передавались. Использованы собственные WORLD/portrait references Рыжика.

## Фактический просмотр всех32

Просмотрены raw/normalized sheet, native1x, все32 целые native клетки на тёмном фоне, четыре светлых whole-cell сравнения WORLD0/WORLD2/ACTION0..7 и упорядоченные source-only shove0→1→2 и hurt4→fall5→down6 во всех4 направлениях. Идентичность сохраняется: тёмные side-swept волосы/короткая щетина, свободная navy/charcoal одежда, светлые детали обуви, собственная chibi голова и камера. Рыжий цвет/чужая светлая макушка не введены. L/R показывают соответствующие разные профильные ракурсы.

Стадии подготовки, направленного толчка открытой ладонью и возврата различимы, включая UP с рукой вперёд к screenTOP. Interact3 показывает отдельное протягивание руки; hurt4 закрывает корпус и меняет баланс; fall5 снижает тело с опорой, down6 — полноценная лежащая фигура с головой, обеими ногами и обувью. Падение отличается от компактного вращения ранее рассмотренного ROLL. Лежащие фигуры не растянуты до высоты стоящего персонажа. UP fall/down остаются rear-view с уходом головы вперёд/в сторону; невидимое лицо не заменено фронтальным. Fire7 имеет читаемую направленную стойку/небольшой предмет, UP barrel направлен к TOP; это reference pose, не выдача игрового оружия.

Исходные пальцы/локти/обувь и corpse silhouette видны целиком, matte/чужих фигур в native нет. Это source покадровое сравнение: фактическая синхронизация контакта, скорость падения, hitbox/смерть и restart ещё не проверены в движке.

## Независимая проверка whole-figure normalization

Raw SHA `a5522f8958eb24fc3c350577079e19794692d51edc4ba42d003e520e53930243`; v1a SHA `75caa95feb4974e99bbc4ef567a860cd4e612ddcbe6d2151ab25f4f71fb8e693`. Независимо заново найдены разделители, crop bounds, коэффициенты/placement и восстановлены RGBA четырёх целых фигур13/14/29/30, затем всего v1a master. Совпали source-whole/resized hashes, итоговое изображение и recipe/script digests. Остальные28 полных192×256 исходных клеток byte-exact raw v1.

LEFT corpse14 уменьшен единым NN коэффициентом `0.9633507853403142` до184×122, без отдельной обработки головы/конечностей. Другие три фигуры не масштабировались. Полнота двух соседних исходных фигур проверена подсчётом всех support alpha>=128 до resampling; после размещения непрозрачные края не обрезаны. Потеря отдельных образцов при заявленном NN уменьшении не выдана за побайтную сохранность уменьшенного тела.

**Разделитель прозрачен по support alpha128, не по alpha0.** Максимальный raw alpha в найденной полосе LEFT=125, UP=23. Subthreshold fringe вне support rectangle отбрасывается в согласии с конечным alpha128 packer, а не объявляется отсутствующим. Никакие части тела не вырезались/не соединялись, не рисовались, не отражались/не вращались. Raw file/failed raw generation metadata не переписаны.

## Native/grid/padding

Native SHA `4605ae8dc1f7d5eb0f361cc3fe6d83685d43c970e3eba4922dcbc27eff64aa90`,384×256,32unique48×64,pivot24,58. Независимо восстановлен весь native RGBA: canonical whole-cell NN, alpha128, общая палитра35used colors, zeroRGB при alpha0, fixed row DY `[−2,0,0,−1]`. Проверены32 frame hashes/направления/колонки/rects/bounds. Все32 native фигуры внутри свободной границы, baseline placement не срезает opaque pixels.

Generation target16sourcepx не достигнут в12 клетках: индексы6=2,9=7,11=7,13=10,14=4,15=6,19=9,21=6,22=3,23=8,29=6,30=9px. Это **bounded source-only deviation для точных текущих bytes**, не «16px PASS»: полного body clipping не видно, native border остаётся свободным, включая широкие corpse. Реальное atlas sampling/падение у стен/края viewport всё ещё требуют runtime review. Автоматического разрешения такого padding для изменённых будущих клеток нет.

## Решение и пределы

Все32 source клетки свежо просмотрены, source must-fix отсутствуют. Принимаются v1a raw normalization provenance и native preview как source-кандидат. Game assets/loader/annotations/механики не изменялись reviewer. Латентный fire reference не создаёт ability grant. ROLL source приёмка `3678206e…` сохранена, её UP2..5 actual runtime trajectory gate остаётся открытым.

До actor/runtime PASS нужны реальные Input/native shove contact/recovery по направлениям, hurt/fall/death hold/restart, clothing annotations и фактическое отсутствие обрезки при edge sampling; отдельно Gameplay/QA проверяют hitboxes/прерывания/коллизии/логику. FIN source рассматривается отдельным пакетом. `source_only_acceptance=true`, `runtime_approval=false`, `phase_approval=false`, `full_phase_approval=false`; художественное аудио, новая фото-оценка, полная P06/readiness/merge не приняты.
