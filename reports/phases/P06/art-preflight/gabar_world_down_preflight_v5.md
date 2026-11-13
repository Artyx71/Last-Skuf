# P06 — Gabar DOWN world preflight v5

**FAIL_NATIVE_ANCHOR_CONTINUITY.** Сам исходный DOWN gait читается, но native v5 не пригоден как окончательная упаковка: per-frame sole locking создаёт вертикальный сдвиг головы и слишком низкий idle относительно принятых боковых направлений. Это ограниченный packing finding; повторная генерация анатомии не требуется.

Ревьюер `/root/art_review_p06` просмотрел actual master, native8/inspection и diagnostic walk/idle comparison. Ноги contactA2/runA6: anatomicalRIGHT на screenLEFT впереди вниз; contactB4/runB7: anatomicalLEFT на screenRIGHT впереди вниз. Проходные3/5 различимы и уже contacts. Часы корректно на anatomicalLEFT/screenRIGHT; hair/glasses/burgundytee и крупные плечи сохраняют Gabar. Новый likeness/gait source blocker не найден.

Native SHA `3b680f0136e3232f8e817528c7f667224aa851052e234a99e7f917765ce8e0ca`; master `055d15039aa525779c0f4efd3c60cbadfdd31bf48c8da4ec8bb2685f6024f726`. Headtop `[13,13,10,13,10,11,9,10]`, exclusive sole58 всегда. Walk range3px превышает заданные2px; passingA3 опускает голову на3px от contact2. Idle45px от top13 до sole58 против LEFT52/RIGHT51. Сравнение actual master/pretranslation показывает authored headtop8 во всех шести idle/walk позах и9 в run; сдвиг добавляют dy `[5,5,2,5,2,3,0,1]` упаковки.

Разрешение finding: общий whole-pose scale/standing anchor, сохраняющий authored relative placement, с отдельной проверкой сохранности opaque pixels и actual floor contact. Именно такой последующий технический кандидат v5a оценён отдельным отчётом; исходный v5 FAIL сохраняется.

Alpha0/255,34 opaque colors,8 unique RGBA cells. Независимо восстановлены все8 целых source cells384×512→48×64 NN + palette/threshold/translation: результат byte-identical; bounds/framehashes/manifest/native/prompt/master/input-role hashes совпали. Уникальность не использована как доказательство походки.

Evidence: `gabar_world_down_preflight_v5_metrics.json`, `gabar_world_down_v5_idle_continuity_8x.png`, `gabar_world_down_v5_walk4_4x.png`. Только source review, без Godot/controller/Git/generation/source edits; записи только reportdir. Runtime/fullworld/P06 approval не выдаётся.
