# Тега FIN v1a — независимый SOURCE ART review

**ACCEPTABLE_SOURCE_CANDIDATE.** Все32 native48×64 целые позы просмотрены свежо при1×/NNувеличении, на светлом/тёмном фоне и с собственными WORLD idle/walk/run/портретами. Рассмотрены24SOURCE ONLY схемы0→contact1..5→6 и0→special7→6 по4DIR. Новых существенных source must-fix не обнаружено. Это не игровая запись и не принятие runtime добиваний.

Тега сохраняет buzzdarkhair, тяжёлые глаза/брови, щетину, крупную карикатурную голову и короткий компактный корпус, greyziphoodie/полные длинные рукава до кистей, тёмные брюки и серо-белые кроссовки. Стойки/оружейные позы и recovery принадлежат тому же ownWORLD семейству, без выданных чужих черт или фронтального UPлица. Руки, плечи, ноги и стопы целы. Shove/palm, lowbaton, knife/pistol refs, двухручный environmental press и kick различимы.

Signature7 читает простой пинок перед собой с опорной ногой: DOWN подошва вперёд/вниз, LEFT стопа SCREENLEFT, RIGHT SCREENRIGHT, UP затылок/капюшон и стопа SCREEN TOP. В source нет flips/breakdance/магии; позы подходят заданному непретенциозному стилю. Точная высота низкого контакта с floorobject, исход и поддержка ноги во времени остаются runtime gate: одиночный рисунок не доказывает hitbox/опору. Пропорции головы не уменьшены ради огромного legspan.

## Сборка и пиксели

Raw26f5d713… и первый pack_failure сохранены. Reviewer независимо пересчитал32компоненты alpha≥128: весь raw support учтён. Все32 bbox-прямоугольника включают полную собственную фигуру и0соседнего support. LEFTrawcell1 содержал носок соседней2, но две фигуры не маскировались и не делились анатомически. Только9/10 переуложены ЦЕЛИКОМ прямоугольными RGBAcrop и translation; uniformNN scale1.0, размеры159×194/179×207, без потери альфы. Остальные30rawcells RGBA exact. Новый master восстановлен exact из исходника, все32native самостоятельно repack exact. Никакой генерации новой части тела или переноса донорских конечностей не было. У authorassembler есть неиспользованная переменная/комментарий от ACTION-шаблона; она не читает другую картинку и не участвует в независимо восстановленной FINцепочке.

Native188acc9f…384×256/8×4, pivot24/58,32уникальные клетки,36непрозрачных цветов общей палитры, binaryalpha/transparentRGB0, rowtranslation без opaque loss. Source bounds внутри клеток.

Раскрытое ограничение:18sourcegutter<16px (полный списокmetrics), минимум1px в LEFTsharp11. При NNpack один чёрный пиксель кончика ножа попадает в nativex0,y35. Полная исходная фигура/нож внутри sourcecell, фактического срезания острия или соседнего фрагмента не видно. Не заявляется all-native-free-border либо16px PASS. Это bounded source padding/sampling риск латентного sharp reference; runtime sharp не принят. При будущей активации этого reference нужен реальный region/nearest sampling review или целиковый padding fit; запрещено скрыть риск обходом gate. Текущие knife/firearm картинки не дают способностей и обычного ranged kit.

## Границы

Принимается только точный hash-bound source candidate для последующего авторского импорта/интеграции. Нужны независимые actualInput прогоны разрешённыхFIN, NPC contact/reaction/corpse, timing/once outcomes, objectkick/worldtarget collision, hurt/death/restart, clothing anchors/actualeffects и Full/Reduced. Не приняты весь Тега/body/ability, новый photo-likeness, audio/listening, FPS/Windows, P06/P07/readiness/merge. ACTIONv2a решениеef71ab4c… сохранено неизменным и не переоценено этим FINreview.

Reviewer не запускал Godot/controller/Git/generation и не менял Game/sourceassets. Privatephotos не открывались/не передавались; raw generation использовала только ownWORLD+ownportraits. Portable packet содержит whole-cell diagnostics и hash bindings оригиналов, без fullsource/engine/moviecache.
