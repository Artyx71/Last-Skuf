# Tega WORLD — независимый actual native ART review v1

**ACCEPTABLE_CAPTURED_CONFIGURATION_ART_COMPONENT_ONLY.** В предоставленном реальном X11-прогоне приняты четыре направления WORLD idle/walk/run Теги: все32 исходные позы,12 циклов и семь непрерывных переходов. Action/боёвка/способность Теги, production CharacterPlayer и полная P06 этим не принимаются. Критических/обязательных ART исправлений в данном bounded evidence нет.

Reviewer `/root/art_olezhka_recovery` независим от автора/билдера. WORK прочитан, записаны только файлы ROOT с префиксом `reports/phases/P06/art-preflight/tega-world-native-review-v1`. Godot/native builder, Git/controller, генераторы и сеть не запускались; исходные AVI/MP4 не менялись. Использованы собственные диагностические scripts для SHA/PNG/source reconstruction/trace анализа и фактического декодирования существующего AVI. Субъективная игра, прослушивание, новая photo-likeness приёмка и FPS benchmark не выполнялись.

## Привязка к действительным артефактам

- Frozen declared source head: `00298c2406243d7ef9cde20d10645ebfb8d1a648`. Все **1036 записанных входов** из `source_hashes.json` побайтно сверены по SHA256 при начале и завершении review; несовпадений нет. Это проверка конкретных recorded keys, а не обещание заморозки всех будущих/новых файлов дерева.
- Durable operation `19acf1ed4aea41a7b9bc00cb0c732705`: receipt exit0, input argv/task/actor/output paths и argv hash совпали; output.log SHA проверен. Controller consumption/lease это ART review не изменяет и отдельно не принимает.
- Native `reports/phases/P06/attempt1/tega-world-native-01`: независимо пересчитаны реальные check entries live110/110 и movie70/70. Все51 перечисленные native report artifacts сверены; дополнительно зафиксированы SHA validation.json и обоих настоящих видео.
- Runtime atlas SHA `3a34b5233d76ea0fe18f39061a9d1ed0e6b8bdfd139fae3848bfcf7cf5f5048f` byte-exact accepted source v5d. Source review decision SHA `34fcdd4a1eec004e98b15113a01631cada1240e684e69ce71a00bf620040582b`; все50 его source inputs и24 diagnostic/report artifacts сверены. Это привязка к прежней независимой source-приёмке, не ретроактивный PASS старых отвергнутых рисунков.

## Что независимо проверено технически

Source master1536×1024 →32 whole192×256 cells → NN48×64, alpha128/canonical43palette и сохранённые rowDY воспроизведены без вызова production packer. Все32 native RGBA совпали с PNG/manifest, opaque pixels не потеряны. Native atlas384×256: alpha только0/255,36 используемых opaque цветов, transparentRGB0, минимальный прозрачный native gutter4px. Никакого per-frame sole58 выравнивания reviewer не делал.

Каждая из32 отдельных lossless phase PNG плюс8 непрерывных endpoint PNG сопоставлена с нужной native позой в её записанной экранной позиции. **Все40 PNG имеют0 несовпадений opaque RGB.** На собственных NN-диагностиках просмотрены все32 целые фигуры и реальный фон; чёрных opaque прямоугольников, обрезания головы/обуви, переноса чужого персонажа или неверной source колонки нет.

Фактически ffprobe определил в обоих AVI/MP4 **751 кадр /12.516667s**,1280×720/60fps. AVI MJPEG действительно декодирован целиком:751 RGB frame hashes сохранены в extraction.json. Первоначальное ожидание750 опровергнуто actual evidence; ничего не обрезалось и не подгонялось. Оба оригинала сохранены. PCM stream AVI не прослушивался; fixture по коду muted, MP4 создавался без audio; никакой аудиоприёмки нет.

Alignment определён независимо21 probes с offset−3…+3. Лучшее соответствие: video index=physics_tick−1, MAE13.28965 против26.74524/27.26420 у ближайших смещений. Все **672 размеченные actual movie позы** классифицировались лучше всего как ожидаемая фаза своего направления/state; ошибок0. Lossy MJPEG RGB не выдаётся за lossless PNG, для точных цветов использованы отдельные40 PNG.

## Действительный temporal ART просмотр

Из actual декодированных кадров созданы и просмотрены20 chronological onset boards:12 grid groups и8 continuous groups, всего98 смен фаз. Дополнительно просмотрены семь join boards с **каждым соседним video frame**, включая два setup ticks без trace sample (в boards помечены `*`; crop привязан к ближайшему recorded root, точная физическая позиция этим промежуточным кадрам не приписывается). Четыре20-frame strips дают80 последовательных actual run кадров. Всего просмотрены36 сохранённых диагностических PNG.

В grid присутствуют полноценные idle[0,1],walk[2,3,4,5],run[6,7] циклы всех четырёх направлений с возвратами фаз. Отдельный uninterrupted путь: idle_up →walk_right →run_right →idle_right →walk_down →run_left →walk_up →idle_up. Он не выдаётся за grid reset-позы: source fixture код отдельно сбрасывает старт только перед continuous block; дальнейшие семь переходов идут через held engine Input/physics без fixture teleport.

| Направление | Реальная читаемость и согласованность |
| --- | --- |
| DOWN | Короткая тёмная макушка, тяжёлые брови/усталое лицо и серый hood/torso сохраняются. Leading hip→trouser→shoe цепи screen-left/right действительно чередуются; противоположная стопа поднимается. Passing фазы сжатые и читаемые. |
| LEFT | Ближняя leading leg в walk2/run6 сменяется дальней от более высокого таза в walk4/run7; ближнее колено/heel уходит назад вправо. Это реальная смена ownership, а не та же нога под другим цветом. Head/crown/neck/hood остаются компактной собственной top-down семьёй. |
| RIGHT | Собственный right-profile. Walk4/run7 выводят дальнюю ногу вправо, ближняя отведена назад влево; A2/A6 ведут ближней. Нет возврата к узкому вытянутому боковому персонажу или чрезмерно крупной портретной голове при смене A/B. |
| UP | Видимая crown и dropped hood держат собственную камеру. Левые/правые длинные leg chains и подошвы меняются в walk/run, руки counter-swing связаны с длинными серыми рукавами. Не установлены лишняя кисть/оборванная конечность/пропавшая поза. |

Полные индивидуальные наблюдения по всем32 клеткам записаны в metrics.independent_visual_cells. Short dark hair/eyebags/stubble/grey hoodie/charcoal trousers/trainers остаются одной собственной фигурой; рисунок другой генеративной версии не мигает при contact/pass фазах. Историческая source находка TEGA-WORLD-SIDE-GAIT-01 в финальном принятом наборе не воспроизводится и в данном captured runtime; прежние FAIL сохранены.

## Стопы, root, grid и cadence

Сохранены реальные exclusive native bottoms — они не нормализованы скрыто:

| Направление | Колонки0…7 |
| --- | --- |
| DOWN |58,58,60,57,60,60,60,60|
| LEFT |58,57,58,57,58,58,59,59|
| RIGHT |58,58,58,58,58,58,58,58|
| UP |58,58,59,58,59,58,59,59|

При pivot24,58 это изменения нарисованной обуви/стойки относительно physics-root: DOWN до+2/−1px, LEFT idle1−1px/run+1px, UP stride+1px. В actual циклах LEFT idle1 меняет локальный контур подошвы на1px; голова и торс не перемещаются целиком как отдельный скачок. Видимая небольшая drawn bob в DOWN/UP согласуется с проходящей/ведущей ногой. На данном масштабе/скорости это не превращается в лишнее renderer pogo/скольжение или floor snap между source frames. В семи joins не обнаружен дополнительный whole-sprite jump/смена масштаба головы/камеры. Такая приёмка ограничена captured fixture, не доказывает поведение на будущих ступенях/стенах/боевых поверхностях.

В каждом trace визуальный origin строго на pixel grid (max error0). При этом **392/672 physics positions каждого прогона остаются дробными**; max per-axis visual rounding0.49609375px, max2D0.541579px. Same-segment velocity integration error≤0.000008139px. Continuous192 samples каждого прогона укладываются в92px/s и run×1.44, включая setup gaps; max recorded step6.624023px, teleport не установлен. Pixel alignment не округляет body/collision trajectory.

Полные interior phase holds в physics ticks: movie idle20/walk7–8/run5; live idle20/walk7–8/run5–6. Порядок всех onset фаз последовательный, выпадение кадров/неверная обратная смена не установлены. Это actual recorded cadence, **не wall-frame FPS/performance измерение** и не субъективное управление игроком.

## Границы приёмки

Оба сохранённых strict input gates:672/672/errors0; дополнительно независимо сопоставлены все672 samples каждого trace с ожидаемыми segment/state/direction/Input vector/run/velocity. Это engine Input replay, не физическая клавиатура. Все window_focused samples=true, поэтому FLAG_NO_FOCUS efficacy/устойчивость к реальной потере фокуса этим не доказаны. Превью имеет собственный простой PreviewActor: production combat actor/ability/equipment/garment sockets/gore/settings/gameplay feel не принимаются. Поздний UP run подходит к техническим надписям fixture; появление glyphs рядом в crop — ограничение кадрирования полигона, не sprite clipping или opacity дефект.

Не проверены новые способности/боевая ART, настоящие finisher reactions, новое аудио/прослушивание, FPS, exports/Linux/Wine/Windows, full CharacterLab/кампания/P06. Никакого phase approval, attempt reset, next phase или merge permission. Автор может продолжать уже разрешённые задачи текущей P06, сохраняя отдельные Quality Gates. Если будущая production интеграция меняет эти рисунки/scale/clock/transforms, требуется новое соответствующее runtime evidence.
