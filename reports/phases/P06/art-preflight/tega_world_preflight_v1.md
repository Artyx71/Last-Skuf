# Tega WORLD v1 — независимый ART SOURCE review

FAIL: четыре SIDE B-позы не устанавливают противоположную ведущую ногу. Это SOURCE_CORRECTION_REQUIRED; v1 не принимать в runtime. Проверены все32wholeposes, а не только число уникальных файлов. Runtime/Godot animation/phase approval не выданы.

Облик согласован с собственным ранее принятым портретом Теги: очень короткая тёмная стрижка, щетина, тяжёлые брови и усталые глаза/мешки; серый длиннорукавный hoodie с опущенным капюшоном, тёмные брюки/серые кроссовки, компактная стройная фигура. Нет Olegface/длинной чёлки/очков/оружия/татуировок. Это проверка continuity к собственному принятому арту, не новое photo-likeness signoff; rawphotos не открывались/не отправлялись. Во всех4направлениях видна макушка, плечи показаны сверху, профиль не превращается в плоский sidescroller; общий camera/pixel язык согласован с собственным Oleg guide. LEFT/RIGHT не являются точными растровыми зеркалами.

Все32позы просмотрены отдельно на светлом и тёмном фоне, whole-source SIDE2/4/6/7 и native6x дополнительно сопоставлены. DOWN/UP крупные walk2/4 и run6/7 визуально меняют левую/правую вынесенную стопу; passing/idle позы различимы. Боковые руки меняют windup/swing семью, но обязательный near/far leg lead в B-позах не меняется достаточно ясно.

## Обязательное исправление TEGA-WORLD-SIDE-GAIT-01

| Направление | B column | Index | Source wholecell XYXY | Native XYWH |
|---|---:|---:|---|---|
| LEFT |4|12|768,256,960,512|192,64,48,64|
| LEFT |7|15|1344,256,1536,512|336,64,48,64|
| RIGHT |4|20|768,512,960,768|192,128,48,64|
| RIGHT |7|23|1344,512,1536,768|336,128,48,64|

Severity major/source-blocking. Прослеженная lower nearhip→thigh→shoe цепь в A2/A6 уходит к крупной передней нижней стопе. В B4/B7 она остаётся той же ведущей цепью: дляLEFT передняя нижняя стопа остаётсяLEFT, задняя более высокаяRIGHT; дляRIGHT — наоборот. Изменены кулаки/локти, ширина stance и контуры, но не читается требуемая FARleg-leading фаза. Одной смены цвета/теней или контура недостаточно. Это дефект обещанных source phase poses; скольжение реальной Godot анимации этим review не заявляется, поскольку replay ещё не было.

Минимальная правка — новые целые B4/B7 позы в обеих SIDE строках: nearleg уверенно уходитназад, farleg ведётвперёд с двумя связными hip→thigh→knee→shoe цепями и читаемым разделением; neararm идётвперёд, fararm назад. ВLEFT B nearleg trailsRIGHT/farleg leadsLEFT, вRIGHT B nearleg trailsLEFT/farleg leadsRIGHT. A2/A6 и identity/camera/greyhoodie сохранять как anchors; по возможности сохранить прочие28полных cells byte-exact. Только whole-pose authored correction через разрешённый генератор/packing, не кодовое дорисовывание/сшивание конечностей или зеркалирование анатомии. v1master/native/report сохранить, затем свежий all32source review исправленной сборки.

## Техническая проверка

Независимо восстановлены все32native cells из1536×1024master: whole192×256 NN→48×64, alpha128, canonical43palette, фиксированный col0reference DY по строке (DOWN0/LEFT0/RIGHT0/UP−1). Все32RGBA совпали побайтно с native и manifest hashes; unique32, реально37opaque colors, binaryalpha0/255, alignment opaque loss0. Ни один тул, палец или ботинок не потерян при упаковке. Технический успех не закрывает SIDE gait finding.

Границы для будущего runtime review: fixedpivot24,58 не означает одинаковую нижнюю грань каждой движущейся стопы. DOWN bottom58..62, UP58..61; минимальные sourcegutters в частиDOWN/UP всего6–12px, ниже requested16target24, но все силуэты целые, с nativepadding и нулевой opaque loss. LEFTidle0/1 bottoms58/57: actual idle loop/floor join ещё проверить. Не обрезать стопы ради косметического root alignment. Эти полевые границы и возможная читаемость малых деталей hoodie остаются runtime reservations, не PASS анимации. Static diagnostic boards не являются Godot playback.

Reviewer path incident: один собственный диагностический .py ошибочно создан под WORK/reports из-за cwd; команда ссылалась на ROOT и не выполнила его. Только этот собственный untracked reportfile был перемещён byte-exact в разрешённый ROOT path, stray WORK file удалён. Поэтому не утверждается «WORK вообще не затрагивался»: были report-only creation/removal, implementation/source/art не менялись. Master/native SHA и17relevant inputs подтверждены; инцидент отдельно сохранён в reviewer-path-correction.txt. Исходный арт автором этого review не создавался/не исправлялся, независимость source-review сохранена.

Нет runtime adoption, nativebuild/Controller/Git/network/generator действий этого reviewer. Следующий шаг — source correction указанных4wholeposes и независимый re-review; не следующий этап проекта.
