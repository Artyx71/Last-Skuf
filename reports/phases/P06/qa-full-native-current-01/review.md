# Independent QA — полный native01 остановлен с FAIL

**FAIL_COMPONENT** для actual попытки `8e8ab4a27ccd47ebacf5a66dd3b6780c`, source HEAD `beb30f319b2cf86a1799672ed24837c4640a9bee` / reviewed pipeline8e. Семь этапов прошли; восьмой остановил pipeline из-за четырёх проверок Pasha MovieMaker. Cast, large-text cast, C01 capture, NPC supplement и P04G combat/export/performance **в этой попытке не запускались**. Полного P06 PASS, native acceptance, readiness, публикации, merge или P07 это ревью не даёт.

## Реальное завершение и fail-closed поведение

Самостоятельно прочитаны actual job input/started/receipt/output.log, canonical completion history и phase.native_full_validation. Receipt содержит integer exit1 и совпадающие operation/argv/log SHA; actual duration1171.527s. Созданный input.json закономерно хранит первоначальный consumed=false. Helper сначала сохраняет consumed=true вместе с completion event/phase binding; последующая canonical operation уже другая. Это происхождение отражено отдельно, creation-time input не выдан за текущее состояние.

Actual commands — точный префикс13-plan, первые7exit0 и восьмойexit1. Все8 cleanup events без unexpected/remaining children; собственные identity проверки показывают, что первоначальные worker/aggregator PID+start_ticks+boot_id закончились. Никаких сигналов от QA не посылалось. Source before=after, HEAD before=after. Независимо перечитаны **1454 frozen source files**; на момент проверки после receipt все physical SHA совпадали. Проверены **806 child artifact hashes** и raw wrapper/child logs. Источники и исходные результаты не исправлялись мной. Последующий author candidate рассматривается отдельно от этого frozen FAIL.

Отдельный предшествующий local unit suite действительно выполнил175tests, записал OK и footer exit_code=0, при source before=after на том же HEAD. Это локальные тесты, не remote GitHub CI. В моём первом диагностическом matcher было неверное ожидание, что OK — последняя строка; correct raw log имеет exit footer после OK. Оригинальный diagnostic и corrected-v2 сохранены, это не падение unit suite.

## Что подтвердилось в завершённых этапах

Coverage-matrix.json содержит точные native/movie assertion counts и738actual native PNG. Часть native assertions — успешное сохранение кадра, поэтому это не738новых gameplay cases. Raw Core events пересчитаны отдельно: уникальность(epoch,id,target), outgoing FIN contact на player pose1, численные Full/Reduced outcome pairs совпадают. Incoming synthetic/real negative finisher по игроку не смешивался с outgoing FIN. HUD counter: actual display/model parity,5pxrect выше арены, открытое окно на нужном clock/frame/health и конечный progress подтверждены по сохранённым observations. Эти узкие пересчёты прошли и у Паши; они не отменяют провал движения.

Все сохранённые capture records существуют с успешным code и корректным PNG header/integer-scaled viewport. Gabar был1920×1080, остальные имеют собственный integer scale. Мой первый probe ошибочно требовал универсальные640×360: initial diagnostic сохранён и исправлен как **ошибка QA ожидания**, не product failure. Самостоятельно просмотрен один целый actual Gabar finisher screenshot; это не ART review всех738кадров.

После завершения engine job независимо перечитаны7actual MP4 containers: H264/AAC, ненулевые frame counts1792/1896/285/1113/3599/3500/4810. Собственные ffprobe commands и SHA сохранены. Это container metadata query, не полный decode или новая субъективная оценка анимаций. У Паши сохранён failed raw AVI400255102bytes/5662frames; успешного encode/MP4 для этой попытки нет. Формат60FPS MovieMaker не выдан за измеренную производительность. Новый realwallframe benchmark и exports не достигнуты.

Полные533Game-path/hash dictionaries совпадают с independently accepted native0dd C01 baseline; actual current533files также перечитаны при postreceipt integrity audit. Это явное scoped source-equivalence evidence для прежних компонентных тестов/DEV08, а не утверждение, что старые экспорты или другие недостигнутые этапы выполнены заново. New C09 NPC styles остаются owner-deferred; они не добавлялись как новое условие этого ревью.

## FULL-Q01 — обязательная квалификация четырёх падений Паши

Native Паши581/581,188PNG. Movie389/393. Обе ошибки `all8_ordered_poses_then_held_run` не означают пропавшие poses: raw trace действительно содержит0..7по порядку. Не выполнен held-run в конце. Вторые проверки physical_run_no_teleport_or_immunity также проваливают >70distance независимо от других конъюнктов.

Reduced down: tick208/pose5 velocity180→0, position фиксируется[380,236], последние14samples idle_down; исходная declared позиция[380,200], displacement36. Reduced left: tick237/pose3−180→−125, затем tick253→0, финал[245.6665802,240] против начальных[300,240], displacement54.3334; последние9samples idle_left.32samples на каждый route. Максимальные шаги не превышают исходный bound. Bullet/ammo/one-damage/score assertions проходят; нельзя использовать их, чтобы игнорировать провал движения.

Принятый b359 movie04e6bc7a и текущий native имеют те же32samples и180на протяжении этих маршрутов, заканчиваясьrun. Девять критических Pasha actor/base/movement strategy/Core/replay/wrapper исходников побайтно равны b359.125совпадает с обычной скоростью walk, но реальный Input vector/Shift/focus/event source не записан. Поэтому **причинность не установлена**: нельзя утверждать ни внешнюю клавиатуру/focus, ни новый gameplay bug только по этим данным.

Минимальный следующий шаг — отдельный canonical serial targeted Pasha job с actual Engine Input/vector/character_run/pressed-key и focus/window telemetry, строгим per-sample held contract и прежними predicates без ослабления. Можно отдельно проверить MovieMaker-only NO_FOCUS как явно отмеченную harness настройку; это не разрешение менять manual gameplay/focus поведение. Нельзя reassert keys каждый tick, принудительно двигать actor, понижать distance, принимать только список8poses или слепо повторять completed failure. Если при правильном Input движение снова падает, нужен фактический collision/health/policy reproducer и product fix. Первые7не требуется слепо повторять ради диагностики; как завершить remaining5/current full evidence после fix — отдельное согласованное source/receipt решение Lead, исходная попытка остаётся FAIL.

## FULL-Q02 и ограничения

LOW: Gabar validation наследует устаревшую строку «five other hero bodies/abilities pending». Она не описывает актуальную13-stage матрицу. Сохранить immutable output, добавить erratum и исправить будущий текст отдельно; не перезаписывать старый запуск.

Фактического listening инструмента в ALL_TOOLS не обнаружено; agent listening/quality не заявлены. Прежнее owner prototype C01 listening — отдельный scoped record, не новая прослушка. Native Windows, remote CI, fullphase/merge, ROOT handoff, новое художественное NPC-производство и новая реальная FPS приёмка в этой попытке не подтверждены. Все собственные действия — read-only анализ и файлы данного ROOT report; Godot/Controller/runner/реализация не запускались и не редактировались.
