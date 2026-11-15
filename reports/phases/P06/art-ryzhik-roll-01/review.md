# Независимый ART runtime review — Рыжик, 407f9

**FAIL_COMPONENT.** Два открытых замечания: RYZHIK-ROLL-UP-READABILITY-01 (HIGH, фактический визуальный дефект) и RYZHIK-FIN-REDUCED-COVERAGE-02 (HIGH, недостающее обязательное evidence). Источники не исправлялись reviewer. Прежние SOURCE ONLY решения сохранены: они явно оставляли UP runtime gate открытым.

Проверены реальные завершённые X11 native286/286,84PNG, movie202/202,36 контактов на прогон; MP4 hash59336490… содержит2215 кадров1280×720/60fps,36.916667s. Свежо проверены все validation/source/evidence hashes, frozen head407f9a1df6c3d8ed110ab908b234fad4750b622d. Offline ffmpeg декодировал364 выбранных РЕАЛЬНЫХ видеокадра; просмотрены непрерывные route strips через2 кадра,12FIN contact/reaction strips,6 incoming-contact/fall sequences и обзор всей записи через2s. Сохранённые decode viewports уменьшены ровно1/2 посредством NN, исходный полный MP4 связан хешем и не дублируется. Не заявляется просмотр каждого из2215 кадров в реальном времени или аудиопрослушивание. Статические SOURCE_ONLY схемы не использованы вместо игровой записи.

## RYZHIK-ROLL-UP-READABILITY-01

Actual TOP-путь непрерывен: y272→214.4,8поз0..7; это не teleport. Однако native UP2/source26 и movie n335..338 наклоняют голову/ладони к SCREENBOTTOM, против forward-away входа. UP5/source29, movie n347..350 возвращает похожую опору к камере. На actual TOP path последовательность воспринимается как движение вверх с обратным наклоном/посадкой. Жест переднего кувырка вверх недостаточно читается. Средние3/4 допустимы как turnover сами по себе: необходимость их перерисовки отдельно не доказана.

Минимальное исправление: новые ЦЕЛЫЕ собственные UP2/UP5 с направленным от камеры входом и согласованным выходом/приземлением, затем свежая проверка полной UP0..7→WORLD на фактическом TOP path. Не менять направление движения ради совпадения с неверным жестом; не зеркалить/вращать donor, не собирать анатомию из частей. DOWN/LEFT/RIGHT в actual sequence читаются как перекат; их движение/позы не получили ART must-fix. Короткий palm/foot support на этой пиксельной частоте не даёт оснований обещать физически точный foot-lock.

## RYZHIK-FIN-REDUCED-COVERAGE-02

Двенадцать разрешённых FIN unarmed/blunt/environmental×4DIR реально дают Input-shove→stun→windup0→contact1→NPCdead/contact1→corpse2 и видимый once score100. Контактные рисунки, реакции, общий костюм и альфа читаются. LEFT environmental source13 (native x=0) при реальном nearest-region проигрывании не показал отрезанной кисти или соседнего кадра. Историческое ограничение исходного отступа не исчезает и не объявляется free-border PASS.

Но все FIN сняты в Full, а Reduced включается позже только в damage0roll. Равенство результата такого ролла не подтверждает Reduced corpse/finishers. Нужен actual12FIN×Full/Reduced с контактами/трупами и равенством исходов. Это исправление replay/evidence, без необходимости переписывать работающую боёвку.

## Что подтверждено и границы

Все128 authored source-frame hashes/anchors проверены, центры на непрозрачных пикселях собственной одежды. Все128 целые позы осмотрены с крестами и точным текущим effect6 overlay. Эти overlay — маркированная offline диагностика, не screenshot Godot. Реальное incoming hurt/fall показывает, что эффект следует одежде; нет нового существенного socket ART замечания. Не заявляется engine capture всех128 латентных поз: sharp/firearm не предоставляют способности. Точные WORLD/ACTION/FIN/ROLL bitmaps совпадают с SOURCE approvals.

Native84 captures просмотрены по40WORLD/roll,36FIN,6incoming,wall,restart. Входящие реальные Core удары в трёх фазах прерывают перекат в собственные hit/fall; movie показывает дальнейшее падение. Стена прерывает путь без видимого tunnel; возврат WORLD и restart читаются. HUD помещается в640×360 и на записи1280×720; VHS отключён по сценарному setup. Наблюдаемая пиксельная стабильность не является измерением host FPS или аппаратной latency. Протокол trace отдельно подтверждает максимум3px на tick без fixture reset внутри измеренной route.

Это runtime ART только данного компонента. Не приняты субъективный feel, аудио, оригинальные уникальные саундпрофили, character-specific NPC/audio matrix всей P06, реальные FPS/Windows, campaign readiness, P06/P07 либо merge. Reviewer не запускал Godot/controller, не менял Game/Git/исходные растры, не открывал и не передавал приватные фото. После исправлений нужен новый freeze и новая native/movie evidence;407/native01 и этот FAIL остаются неизменными.
