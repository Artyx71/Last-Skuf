# Тега ACTION v2a — независимый SOURCE ART review

**ACCEPTABLE_SOURCE_CANDIDATE.** Свежо рассмотрены все32 целые native48×64 рисунка, полный native sheet1×, светлые/тёмные whole-cell boards, собственные WORLD idle/walk/run и портреты. Просмотрены4 directional shove0→1→2, hurt4, fall5→corpse6, interact3 и reference-only fire7; SOURCE ONLY схемы не являются игровым видео. Это первый формальный независимый ART review этого кандидата.

Короткая тёмная buzz-стрижка, тяжёлые брови/мешки под глазами и щетина, компактная фигура, greyziphoodie с длинными рукавами до кистей, тёмные navy/purple брюки и серо-белая обувь сохраняют семейство собственных WORLD/портретов. Головы карикатурного размера согласованы, включая новую LEFT15; новая поза сохраняет LEFT направление, crown/верх плеч и greyhood. Нет оснований для нового whole-pose source must-fix. Shove контакт раскрывает ладони в направлении строки; recovery возвращает закрытые руки. Hurt/fall/corpse различаются состоянием и целыми опорами. Руки/стопы, capюшон, лица/затылок читаются; отсутствие clip/соседних фрагментов подтверждено пикселями и whole-frame осмотром.

## Независимая проверка сборки

Исходный raw2ca4472f… сохранён. Первый canonical pack остановился на DOWN5 support bottom256; failed gutter normalizer не создал action_master_v1a. Существующие ошибки не переименованы в успешную сборку.

Reviewer сам пересчитал4-connected alpha≥128 компоненты исходника: ровно32 целые фигуры, весь support accounted. Их центры однозначно соответствуют32row/column слотам. Для31 сохранённой фигуры полный bbox-прямоугольник включает весь её support и0соседнего support. Компоненты использованы только для bboxанализа; в изображения не накладывались silhouette/component маски. Старый LEFTfire/index15 bbox действительно содержит223пикселя соседнего corpse toe. Эта поза не вырезалась по силуэту и не маскировалась: её заменил ОДИН новый целый imagegen рисунок4ddb9f99…, созданный по ownWORLD+ownrawACTION. Соседняя corpse14 сохранена целиком, включая исходную стопу.

17rawcells RGBA exact;14сохранённых полных фигур получили техническое whole-rectangle NNfit/translation; только15 — новый цельный рисунок. Четыре исходные широкие fall/corpse позы13/14/22/30 равномерно уменьшены целиком, остальные10 technicalfits не меняют scale1.0. Все операции, полный master и32native кадра независимо восстановлены exact, без импорта запускающего запись authorpacker. Никакой перестановки частей тела, mirror/rotation, anatomy edits или подрисовки не делалось.

Canonical packer SHA0abf9bbf877846c7cc7aa9af1e8392055c9f8730901baf59e312d73b4150fd11 неизменен. Candidate nativebe8bf8a1…:384×256,8×4,48×64, pivot24/58. Все32native уникальны,36непрозрачных цветов общей палитры, binaryalpha/transparentRGB0; placement и row-alignment без opaque loss. Все source support внутри клеток и native borders свободны.21source gutters меньше запрошенных16px (минимум3, полный списокmetrics): это раскрытое ограничение отступов, а не16px PASS. Нет утверждения, что сама metadata-проверка принимает художественную анимацию.

## Границы и следующий шаг

Source candidate допускается к следующему авторскому шагу только в точных hash-bound файлах. Пока не приняты реальный character body, contact/hitbox, actual runtime shove/hurt/fall/death/restart, clothing anchors/actualoverlay, gore modes, ability/дистанционный бой, звук, FPS/Windows либо P06/P07. Fire7 — только латентный reference, обычный ranged kit Теге этим рисунком не предоставлен. FIN не рассмотрен этим решением. Новая photo-likeness не утверждается; сравнение выполнено с собственными утверждёнными рисунками.

Reviewer не запускал Godot/controller, не менял Game/Git/source PNG и не использовал генератор. Privatephotos не открывал/не копировал/не передавал; генерация автора использовала только own generated refs. Raw, остановленные recipes, новая generation/prompt и master сохранены. Portable packet содержит whole-cell diagnostics и hash-ссылки на оригиналы, без полного source проекта/engine/cache.
