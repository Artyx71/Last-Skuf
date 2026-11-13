# P06 — Gabar world source preflight v1

**FAIL_SOURCE_MOVEMENT_SEMANTICS.** Не принимать этот atlas как idle2/walk4/run2 animation и не распространять текущий шаблон на остальных героев. Static identity/pixel structure в основном пригодны; основные blockers — gait phases и handedness часов. Это review одного source-кандидата, не runtime или phase decision.

Ревьюер `/root/art_review_p06` независимо осмотрел actual master, native atlas48×64, inspection3x, собственные diagnostic4xfilmstrips всех32 клеток, принятые портреты Gabar и accepted Yakuza worldcamera. Собственный referenceGabar ранее сверен локально в portrait review; его hash повторно проверен. Godot/controller/Git/generator не запускались, source не менялся; записаны только разрешённые art-preflight artifacts.

Точный native SHA256 `166827e8c90cbd6e88118f330368178c165efee5419c2a2fdbd5ea98c7983c1a`; master `5358aca97b2f30f2f0727f4cccd10f84c9cc93f5d36624d936ac627532ae8361`. Далее индексы columns **0-based**: idle0–1, walk2–5, run6–7; rows down/left/right/up.

## Обязательные исправления

### GABAR-WORLD-01 / HIGH — отсутствует читаемый четырёхфазный walk

В left и right строках **все walk cols2,3,4,5 держат одну и ту же широко вытянутую contactstance**: ближняя нога вытянута вперёд, дальняя отнесена назад, руки остаются в одной фазе. Меняются мелкие контуры/складки/расстояния, но нет убедительной смены ведущей ноги, прохода стоп под тазом и переноса веса. Цикл будет читаться как slide/shuffle/textureboil, а не четыре последовательных шага.

В down и up cols2–5 видны две противоположные contactfamilies, повторённые A/B/A/B. Это лучше sideview, но самостоятельные passingposes не читаются: четыре разных изображения не дают четыре разных фазы. Требуется явно авторский цикл contactA → passingA → contactB → passingB во всех4 направлениях. Passing должен иметь реальный knee/foot movement под тазом и reciprocal armphase; contactB должен ясно менять ближнюю/дальнюю ведущую ногу. Можно сохранять годные настоящие contactdrawings, но недостающие фазы должны быть новыми целыми авторскими позами.

### GABAR-WORLD-02 / HIGH — run2 не меняет ведущую ногу

Cols6 и7 во всех4 направлениях показывают одну и ту же leadleg/armfamily с небольшими вариациями. В sideviews особенно ясно: передняя вытянутая стопа и согнутая задняя нога не меняются ролями. Down/up также не дают ясного противоположного leg/armswing; широкие fists/lean остаются в одной фазе. Нужны две реально различные противоположные беговые позы с обменом ведущей ноги и рук. Два кадра допустимы по контракту, но они должны составлять читаемую A/B пару. Более быстрый playback, перестановка frames или32unique hashes этого не исправляют.

### GABAR-WORLD-03 / MEDIUM — часы меняют анатомическую руку в east/right

Фото/prompt задают часы на **левой** руке. Down/front watch справа на изображении и up/back watch слева — согласованы. В left/west view часы допустимо видны на ближней нижней руке, которая является anatomicalleft. Но в right/east row часы также нарисованы на ближней нижней руке; в этом направлении она anatomicalright. Это типичная handedness ошибка зеркалоподобного бокового рисунка. Correct east cells должны держать watch на дальней anatomicalleft руке, с допустимым естественным occlusion; часы не нужно насильно показывать на ближнем запястье. Новый рисунок не должен менять руку только ради видимости аксессуара. Требуется корректная авторская rightrow, не procedural accessory/limb swap.

## Дополнительная проблема движения/anchor

Packing прибивает exclusive bottom к58 и сохраняет X; no opaque clipping проверено. Но общий soleanchor сам по себе не удерживает head/torso. В leftwalk headtops native `[10,10,8,9]`, leftrun `[10,7]`; при одинаковой семантической contactstance это даёт до3px вертикального pogo. Sourceheadtop почти одинаковый, а verticalalignment transforms `[+3,0]` для run усиливают разрыв. При новой авторской походке согласовать ground-contact и pelvis/head height, оставляя только осмысленный ограниченный bob. Не скрывать это отдельным склеиванием головы/ног; новые wholepose drawings должны иметь согласованные anchors. Независимый runtime replay понадобится после исправления gaitsemantics. Idle0–1 можно оценивать только как subtle/static candidate; breathingmotion этим sourcepreflight не одобрена.

## Что пригодно

Gabar узнаваем по brown swept hair, rectangularblackglasses, burgundy short-sleeved shirt и robust athleticshoulders при сравнительно узкой талии, без переноса obese Yakuza body/phone. Darkpants/trainers и отсутствие оружия/надписей согласованы. Hair/garment palette совпадают с портретом; часы по цвету читаемы. Down/left/right/up orientation корректны, up не показывает лицо. Visible headtop/укороченные ноги и боковыеprofile близки принятому Yakuza chibi/topdown language; явного нового isometricdiagonal направления нет. Camera/gameplayreadability на actualfloor ещё не проверена, это не автоматическое camera runtimeapproval.

Master1536×1024, atlas384×256,32cells48×64, pivot24,58. Native alpha строго0/255,37 непрозрачных цветов,32уникальных RGBA hashes. Все sourcecells полностью содержат тела с clear margins; все source bounds/framehashes/native bounds совпали с manifest. Generation reference/prompt/master/inputroles hashes сверены с фактическими файлами. Source использовал собственные generatedportrait/styleinputs, metadata утверждает rawphoto notuploadedforthiscall; ревьюер никаких referenceuploads не выполнял.

Pixel edges hard, нет production photo remnants/checkerboard/фонов между клетками. Technicalpackaging в основном корректен и не делает anatomical reconstruction. **32unique hashes являются только техническим фактом**, не32семантически различных движений. Уникальная фактура/антиалиас threshold variation не заменяет authored phases.

## Повторный review

Сначала новый Gabar gaitsource с ясно обозначенными phasepositions и правильным watchwrist, затем native phasefilmstrip/contactsheet и реальный worldplayback. До его проверки не выдавать walk4/run2/idlebreathing animation approval и не генерировать остальных по этому неработающему posepattern. Runtime controls, floor/collision alignment, gameplaycontacts/actions/finishers остаются вне текущего sourcepreflight. Новая попытка должна сохранить v1master/hash/report как историю.

Evidence: `gabar_world_preflight_v1_metrics.json`, `gabar_world_down_v1_4x.png`, `gabar_world_left_v1_4x.png`, `gabar_world_right_v1_4x.png`, `gabar_world_up_v1_4x.png`. Диагностические filmstrips используют неизменённые реальные native cells, только NN4x и подписи.
