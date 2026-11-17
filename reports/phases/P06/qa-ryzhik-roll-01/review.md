# Независимый QA: Ryzhik roll, исходный кандидат407f9

**FAIL_COMPONENT** для frozen `407f9a1df6c3d8ed110ab908b234fad4750b622d`. Два must-fix замечания: TPR-R01 — отсутствует обязательный Reduced FIN coverage; TPR-R02 — native report predicate принимает пустой renderer. Это coverage/guard gaps, не доказанные ошибки физики переката или Reduced-режима. Будущий author fix/ART candidate в этот verdict не входит. Полная P06/readiness/merge не принимаются.

Независимо скопированы1182 game/tools/source-art inputs без links и отдельный pinned Godot. Полная snapshot-map совпала с actual native source map407. Девятнадцать критических implementation/test/tool файлов сохранены отдельно. QA дождался явной остановки canonical builder и запускал engines исключительно последовательно в собственной ROOT-копии, с новыми XDG/save profiles. Fresh import прошёл.

| Реальный независимый прогон | Результат |
|---|---:|
| Ryzhik Input replay |202/202|
| Strict Roll resource/layout |33/33|
| Current readiness/atomic refusal |70/70|
| Gabar |124/124|
| Oleg |164/164|
| Counter HUD |57/57|
| Timka present |104/104|
| Timka prime |214/214|
| Timka compact layout |102/102|
| Собственные adversaries |18/18|

Все эти процессы завершились0 без engine errors/leaks. Source-only layout-test выдаёт предупреждение, что `Image.load_from_file(res://...roll_sheet.png)` не подходит для export: оно сохранено в логе. Это способ проверки исходного PNG в unit-test; production loader использует imported Texture2D/get_image. Runtime export этим source-only тестом не объявляется проверенным. Прежний author807/pre-registry прогон не выдан за текущую регрессию. После последнего engine QA немедленно сообщил Root об освобождении; новых engines не запускал.

GroundRoll — отдельная стратегия на общем CharacterPlayer/Core, а не новая боевая система. Clock0.08/0.32/0.16, cooldown1.2, активный swept move180px/s ограничен57.6px. Направление фиксируется при старте. Standard movement подавляется на roll, source policy/instance/generation reauthorised, collision masks не меняются и immunity не добавляется. Landing-control — настоящий Core overlap с damage0/stun0.45 только на видимой pose6. CharacterFrames допускает strict ROLL32 только Ryzhik, проверяет32 RGBA cells/identity/dimensions/columns/anchors. Runtime60 clips — ссылки на собственные128 sheet drawings; это не128 отдельных animations. Sharp/fire drawings не дают equipment/ranged grant.

Повторный анализ actual independent202/native286/movie202 data проверил все четыре направления, упорядоченные poses0..7, sprite frame==action frame, конечный57.6px путь по actor clock и единственный landing-contact наpose6. Для значений JSON-clock в пределах1e-6 от phase edge учтена потеря точности сериализации; ordered frames и actual sprite/action equality остаются обязательны. В каждой записи36 уникальных Core contact tokens:4 обычных landing contacts,6 реальных incoming melee (три фазы×hurt/fatal),12 earned FIN contacts вместе с12 ordinary Space contacts и2 settings-roll contacts. FIN проходит через реальные Input-earned stun/active NPC clock, собственную pose1 наdamage tick, NPC contact1→corpse2 и once reward. Это Full evidence; Reduced FIN из этих данных не выводится.

Собственные18 проверок добавляют реальные отрицательные пути: missing/wrong-identity Roll metadata или stale Roll socket отказывают factory атомарно, сохраняя pending Gabar body/context/jobs/options. Все изменённые файлы ROOT-копии восстановлены byte-exact. Чужой strategy instance не начинает действие/не тратит cost; latent sharp/fire tools отказываются. Два реально перекрывающихся landing targets проверяют reentrancy: отзыв authority после первого настоящего Core callback предотвращает второй recipient/receipt; потраченный cooldown не возвращается. Повторный callback на всё ещё живом target с уже зарезервированным token отклонён, урон/score не повторяются. Cancel не оставляет движения/contact, чужая scene policy не даёт действий/обычного движения, atomic host reselection восстанавливает правильное тело. Эти прямые metadata/API adversaries не обозначены как обычный player flow.

Actual producer receipt015037e2… exit0, argv/output-log SHA проверены. Native286/286,84PNG, movie202/202; все92 перечисленных artifacts и1182 source keys совпали с фактическими файлами. Три настоящих PNG просмотрены и скопированы. MP4 существует, полный SHA/streams/container прочитаны ffprobe; это не full-film artistic review, listening или host-FPS measurement. ART-оценка UP26/29 остаётся отдельной задачей; QA не придумывает визуальное заключение по ней.

Actual common verifier main выполнен с полностью mocked subprocesses: Roll wrapper назначается один раз/headless/fresh output, Roll layout назначается, success/control, nonzero и error-log/exit0 распространяются в итоговый FAIL правильно. Три export-helper mock cases подтверждают intersection пяти fixture claims, исключение Ryzhik при отсутствующем Windows success check и пустую availability при failed smoke. Это не GitHub CI, реальные exports или Windows runtime. JSON predicate отдельно проверен на копиях actual native result:8/9 ожидаемых исходов совпали; пустой renderer ошибочно принят — точный repro TPR-R02 сохранён. Ни actual JSON, ни WORK при этом не менялись.

TPR-R01: конечная `Full_Reduced_same_combat_logic` сравнивает только roll/control. Двенадцать FIN routes находятся раньше и в новом clean profile работают в Full; Reduced FIN/NPC/once matrix отсутствует. Нужны реальные12 Reduced routes и сравнение результатов/реакций/once, source и native evidence. Ранее пройденный общий P04G и Full FIN не заменяют этот критерий.

TPR-R02: `valid_replay` проверяет string type и отличие от literal headless, поэтому `renderer=""` считается native. Нужна непустая допустимая backend identity и negative tests для blank/whitespace/unknown/mode/type. Actual native407 остаётся валидным X11 corpus; это не allegation о его провале.

После probes все1182 исходных файлов изолированной копии hash-exact; лишний script — только собственный QA probe. WORK/Game/Controller/Git/canonical state/queue/network QA не изменял. Позднейшие author WIP fixes не смешаны с407 snapshot. Полные игры/движок/source-art/cache/save profiles/mock export artifacts исключены из portable manifest. Нет full P06, ART/feel, новых audio/listening, native Windows, реального FPS или hardware latency claims. Отчёт предназначен для FAIL→FIX→нового независимого review; текущие настоящие green results сохраняются.
