# Tega WORLD v5d — независимый свежий ART SOURCE review всех32 поз

**PASS_SOURCE — ACCEPTABLE_FOUR_DIRECTION_SOURCE_CANDIDATE.** Независимо просмотрены все32 целые фигуры в итоговом source master и native atlas. Приняты исходные рисунки idle/walk/run для четырёх направлений. Это разрешает только последующую точную source adoption и runtime-проверку; Godot animation, боёвка, P06 и merge не приняты.

## Что проверено визуально

Просмотрены actual source1536×1024, native384×256, все32 wholefigure sourcecells на NN2 strips, все32 nativecells на light/dark NN4 boards, новые raw LEFT7/RIGHT4/RIGHT7 и собственный принятый portrait atlas Теги. Новый просмотр не наследовал решение одной LEFT4. Набор сохраняет короткую тёмную стрижку, тяжёлые брови/мешки под глазами, щетину, короткую стройную взрослую фигуру, серый hoodie с опущенным капюшоном, длинные рукава с манжетами, тёмные брюки и серые кроссовки. Ошибки переноса чужого swept-hair/Oleg-образа, оружие, аксессуары или голые предплечья не обнаружены. Свежие личные фото не открывались и не отправлялись; новая фото-likeness приёмка не заявлена.

Во всех направлениях видимая crown/плоскость плеч поддерживает собственный вид сверху. У боковых B-поз лицо/шея/ворот/chest сохраняют компактную семью принятой LEFT4 v4a. Новые кадры не дают прежнего узкого вытянутого v2 профиля или отдельного увеличенного портретного head/body языка. Разная видимость chest, кистей и рукавов соответствует смене swing/перекрытия, а не смене костюма. На intended native сетке обе кисти связаны с рукавами, лишняя конечность не установлена. Небольшая тёплая деталь у шнурка RIGHT6 сама по себе не объявлена третьей кистью; полный рисунок не подтверждает отдельную лишнюю руку.

| Направление | Walk2→4 | Run6→7 |
| --- | --- | --- |
| DOWN | Длинная continuous trouser→shoe цепь меняется с screen-left на screen-right; противоположная нога уходит назад, swing меняется. | Ведущие left/right цепи и поднятые противоположные стопы реально чередуются. |
| LEFT | A2 ведёт крупной ближней ногой от нижнего таза влево; B4 ведёт более тёмной дальней ногой от высокого таза влево, ближняя уходит назад вправо. | A6 продолжает near-leading контакт; новая B7 ведёт far-leg влево с отдельной bent near-knee/heel цепью назад вправо. |
| RIGHT | A2 ведёт крупной ближней ногой вправо; новая B4 ведёт дальней от высокого таза вправо, ближняя уходит назад влево. | A6 near-leading; новая B7 far-leading вправо с отдельным поднятым ближним heel назад влево. |
| UP | Непрерывная длинная screen-left цепь A2 меняется на screen-right B4; руки/поднятая противоположная стопа меняются. | A6/B7 чередуют видимую подошву ведущей стороны и согнутую другую ногу. |

Leg ownership оценивалась по целым hip→thigh→knee→shoe цепям и их перекрытию, а не только по цвету брюк, положению кистей, подписям или уникальности hash. Все32 индивидуальные наблюдения записаны в metrics.visual_cells. Новые LEFT7/RIGHT4/RIGHT7 просмотрены самостоятельно: исходная CELL12-приёмка на них автоматически не переносилась. RIGHT-позы показывают собственный right-profile рисунок; никакая из8 RIGHT клеток не является точным bitmap mirror соответствующей LEFT даже после tight-support выравнивания. Проверена provenance новых reference-файлов/сырых рисунков/prompts; имена/метки генератора не считались доказательством правильной анатомии.

Источник задаёт idle[0,1], walk[2,3,4,5], run[6,7]. Изучены целые фигуры в этом порядке;12 diagnostic GIF созданы из actual native кадров, декодированы и побайтно сверены с правильными source columns. GIF/strips являются source-order diagnostics. Они не доказывают cadence, root/floor устойчивость, input-driven переходы или качество actual Godot animation. Полноценного engine playback в этом review не было.

## Независимая техническая реконструкция

Final master SHA3fb8b578… и native SHA3a34b523… совпали с заявленными. Независимо воспроизведена вся цепочка четырёх generated complete figures: v4a CELL12 и v5a/b/c CELLS15/20/23. Для каждой подтверждены raw alpha128 support bbox, uniform wholefigure NEAREST scale/placement, resizedRGBA, итоговая sourcecell и exact assembled master; остальные31 клетки на каждом шаге неизменны. Python-сборка не меняет/не зеркалит отдельно голову, туловище или конечности. До gutter-сдвигов остальные28 клеток byte-exact v1; принятая CELL12 v4a сохранена в final v5d точно.

v5d отличается от v5c только минимальными целыми вертикальными сдвигами ради source gutter16: D2−5px, D4−10px, D6−7px, D7−10px, U2-4px, U4-7px, U7-7px. Все32 entries recipe проверены по actual pixels, точным supportRGBA/opaque counts и формуле минимального сдвига. Нового resize/рисования или per-frame sole58 выравнивания нет. Alpha128-support каждой фигуры имеет не менее16px прозрачного отступа; supportRGBA и число opaque pixels сохранены. Полный final master восстановлен byte-exact. Точная копия прочитанного helper сохранена как report artifact; production helper не вызывался.

Каждая целая sourcecell независимо NN преобразована192×256→48×64, quantized в canonical43 palette и alpha128, затем сдвинута одним неизменным column0 reference для всей строки: rowDY[0,0,0,−1]. Все32 reconstructed native RGBA совпали с actual PNG и manifest. Есть32 уникальных cellRGBA,36 использованных opaque цветов, только alpha0/255, transparentRGB0. Потерь opaque при source placement, gutter translations или native row alignment нет. Все32 source/native RGBA hashes присутствуют в metrics и decision.

## Что остаётся обязательным

Source finding TEGA-WORLD-SIDE-GAIT-01 устранён на уровне итоговых рисунков12/15/20/23; предыдущие v1/v2/v3 FAIL и v4 CELL12 decision сохраняются неизменными. Это не ретроактивное принятие отклонённых версий и не runtime closure.

Actual Godot gate должен независимо проверить все directions/idle/walk/run, root/floor/grid/camera consistency, переходы и реальные input-driven cadence/движение. Сохранённые exclusive native bottoms: DOWN[58,58,60,57,60,60,60,60], LEFT[58,57,58,57,58,58,59,59], RIGHT[58,58,58,58,58,58,58,58], UP[58,58,59,58,59,58,59,59]. Эти реальные различия не скрыты принудительным per-frame anchor и не названы runtime floor PASS; следующий review обязан оценить их в игре. Если там выявится jump/slide/нечитаемое чередование, требуются исправление и новое review, независимо от source PASS.

В этом bounded task созданы только ROOT reports с данным префиксом. WORK/source/art/implementation не изменялись; Git, Controller, native/build, imagegen и network не вызывались. Автор production assets и этот независимый ART reviewer — разные контексты. Никакого phase, gameplay, export или merge approval не выдано.
