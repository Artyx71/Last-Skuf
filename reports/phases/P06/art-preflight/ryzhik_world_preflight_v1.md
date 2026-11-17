# Ryzhik WORLD v1 — independent source ART review

**FAIL_SIDE_GAIT_OWNERSHIP.** Все32 source/native клетки просмотрены заново, техническая реконструкция точна, но SIDE walking/running не дают требуемой читаемой смены анатомической ведущей ноги. Кандидат не принят для runtime adoption. Исправление требуется целыми позами; source-only review не разрешает phase progression.

Reviewer `/root/art_olezhka_recovery` читал ART/CHARACTER_BIBLE, CharacterExpansion contract, собственный Ryzhik portrait/master/provenance, WORLD prompt/master/native/manifest и whole-cell light/dark comparisons. Source/runtime предыдущих персонажей использовались только как явно подписанные camera/gait comparisons. Godot/controller/Git/network/generator не запускались; WORK и исходный арт не менялись. Raw photo не открывалась и не копировалась: own previously accepted portrait достаточен для текущей проверки continuity, не объявляется новым human likeness signoff.

Облик в целом согласован с собственным портретом: тёмные side-swept волосы, более узкое лицо, тёмные брови и короткая stubble shading; отсутствуют ginger/Timka blond/очевидные Oleg clean-crop accessories. Oversized dark teal/charcoal crewneck без капюшона, длинные рукава до небольших кистей, свободные брюки и серые кроссовки сохранены. Новых татуировок, часов, очков, цепочки или lettering нет. Видимая crown/верх плеч и foreshortened ноги соответствуют overhead family; общего platformer camera drift не обнаружено. Это положительные наблюдения по облику, не принятие полного листа.

В DOWN и UP контакты2/4 и stride6/7 визуально меняют стороны ведущей/отстающей стопы, руки и сгиб коленей. UP остаётся задним видом без front face. Idle0/1 — действительно очень близкие rest poses; head/crown/wardrobe family сохраняется. Passing3/5 отличаются от широких contacts и друг от друга, но cadence/loop closure ещё не проверялись в движении.

**RYZHIK-WORLD-SOURCE-GAIT-01 / HIGH:**

| Целая клетка | Индекс | Наблюдение и минимальное исправление |
|---|---:|---|
| LEFT4 | 12 | В сравнении с собственным LEFT2 foreground brighter lower-leg/seam по-прежнему читается ведущим. Смена near/far hip→knee→shoe не установлена достаточно чётко, хотя передняя рука меняет позу. Нужен однозначный far-leading walking contact с near leg, уходящей назад screenRIGHT. |
| LEFT7 | 15 | Run6/7 сохраняют ту же leading foreground near-leg / trailing far-leg family; различаются ширина шага, наклон и руки, но не противоположная опорная нога. Нарисовать противоположный runB: darker far leg вперёд screenLEFT, ясно связанная с near hip near leg назад screenRIGHT. |
| RIGHT4 | 20 | Walk2/4 сохраняют крупную foreground near-leg, ведущую screenRIGHT, при изменённых руках/раскрытии стойки. Для B4 нужна near leg назад screenLEFT и far leg вперёд screenRIGHT с читаемым пересечением/разделением у таза. |
| RIGHT7 | 23 | Run6/7 вновь показывают foreground near-leg вперёд screenRIGHT и far leg позади. B7 должна менять именно анатомическую ведущую ногу, а не только fists/contour. |

Whole-source и native full-cell panels показывают этот issue независимо от labels в prompt и32unique hashes. Проблема не в номере кадра или технике упаковки. Минимальный путь — сохранить own near-leading A2/A6 и остальные28 клеток; сгенерировать четыре исправленные целые B4/B7 позы в собственной одежде/камере/пропорциях, с непрерывными hip→thigh→knee→shoe связями и opposing arms. Допустима целая independently generated figure/cell с документированной uniform normalization; недопустимы зеркалирование, перестановка/перерисовка частей ног Python или объявление same-leg silhouettes полноценным opposing cycle. После assembly нужен новый full32 source review, затем настоящая Godot animation QA.

Независимая техническая проверка: canvas1536×1024, native384×256, клетки48×64/pivot24,58,4directions×8. Все32 RGBA клетки byte-exact реконструированы через whole-cell NEAREST, manifest palette/alpha128 и fixed row translations DOWN0/LEFT0/RIGHT−1/UP−1; post-sampling opaque placement loss0. Проверены frame RGBA hashes, source/master/prompt/reference SHA и generation metadata. Native alpha binary,32unique рисунка. Light/dark просмотр не выявил широких matte panels/halo, соседних фигур или пропавших конечностей. Уникальность и alpha не доказывают gait.

Idle projected heights DOWN51–52/LEFT52/RIGHT51–52/UP52–53px вписываются в принятую family. Некоторые stride soles выходят глубже nominal pivot58 (точные bounds в metrics); это открытая runtime floor/cadence reservation, а не автоматическое sole recentering. Пропорции головы и torso в reviewed source достаточно связны, чтобы не требовать отдельной camera/identity регенерации всех32. Повторный reviewer обязан проверить, что исправленные клетки не вносят чужие короткие рукава/голову/камеру.

Actual Input, idle/walk/run playback, loop seams, foot glide, head bob, pixel-grid/fractional physics, ability choreography, audio, performance, export и полный P06 не проверялись и не одобрены. Старые completed Timka/Oleg source verdicts не переносятся на этот лист. Четыре исправления и точные исходные hashes закреплены в companion decision; raw private фотографии отсутствуют в diagnostic artifacts.
