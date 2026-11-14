# Timka WORLD32 supported v2 — technical rebind

**ACCEPTABLE_SUPPORTED_LAYOUT_SOURCE_CANDIDATE**, schema2/profile`timka_supported_v1`. Это отдельная техническая привязка неизменного SOURCE ART к исправленному adopter. V1 не изменён. Новых рисунков, нового визуального осмотра или нового runtime-теста в этом rebind нет; приёмка всех32 поз обоснована полным независимым визуальным reviewv1 и повторной точной проверкой тех же байтов сейчас.

Reviewer `/root/art_timka_recovery`, independent_of_author=true. WORK только прочитан. Результаты записаны только ROOT `reports/phases/P06/art-preflight/timka_world_supported_v2*`. Godot/Git/controller/генераторы/сеть/productionmigration не запускались и не изменялись. Пиксели, исходники, ownerdecision,compact_timka и v1диагностики не менялись.

## Неизменное художественное основание

V1decision `timka_world_supported_v1.json` SHA `fd723fe18121bc12e445625ecef7ccad61faaee29e0460f521f51d27e236411b`; report SHA `555d1aa8ad24a283eb65a00345acce3ae07775b303fea488b8333f1af03d14fb`; metrics SHA `1f8cfae2f137d43c532352e7f0ac9ab9573eed88a01beee83188c058933b5203`. Визуальный осмотр выполнен вv1: `2026-11-14T21:33:27.981731+00:00`. Все v1review artifacts заново сверены и связаны с v2inventory. Текущий record не выдаёт эту старую дату/работу за новый просмотр.

Повторно сверены ВСЕ v1sourceinventory paths. Единственное отличие — adopter: `84380b0e67d23eb1cfb562d76973fbe87d94f7de695d53f7ce51f73a6a45987e` → `b1b8d3d72536947715234c99003c047c3bc8d368c97d5fd652b67a5ac7842b8c`. Остальные21 sourceinputs совпали с v1. Native SHA `8e505380e88fb538988310a364c6b16a135cb69b94d136fe00307c8a49a99cea`, manifest SHA `fed2f79ac370ce44eefd873cfa2af3452a067d805a70da61976de2095d91a72e`, master SHA `79ab1a0ebd2e06e4793d83c8ed1d2f336f502d37228f3df1e8fb590ff8c114c0` неизменны. Все32клетки заново декодированы, их RGBA совпали с визуально рассмотреннымиv1 и целымиoriginalcells. Source→native NN/палитра/alpha128/исходный rowDY также повторно восстановлены без opaquealignmentloss. Это integrity-проверка, не новые runtime кадры.

Наблюдение WORLD о9старых source-полях6–14px (при nativeclear>=3) сохранено без изменения классификации и списка. V2 не заявляет source>=16, не пересматривает это visualfinding и не отменяет hardgate. Исходный PNG WORLD остаётся byte-exact.

## Исправленный технический binding

Прочитан именно`adopt_timka_supported.py` SHA `b1b8d3d72536947715234c99003c047c3bc8d368c97d5fd652b67a5ac7842b8c`. Код теперь требует canonicalcompact_timka path и совпадение фактического scriptSHA с записанным compaction.script_sha256. Проверены canonicalownerdecision path, scopedkind/P06/Timka/profile, бюджет32/28/24 и total84 с inttypes, excludedclips/requiredcontexts и phase/mergefalse; фактическое immutablepermission этим условиям соответствует.

Это ограниченная code/sourcebindingпроверка, относящаяся к QA_TC-C01/02. Adopter не исполнялся, productionmigration и mutationnegativeprobes не проводились. V2 **не выдаёт независимый QA2PASS**: отдельное QA/code решение должно быть завершено по своему протоколу перед зависимыми действиями. Закрытие QAfindings не утверждается одним ARTsourceapproval.

V1 содержит старый adopterSHA и не должен использоваться для текущей миграции. V2 supersedes его только как актуальная техническая SOURCEпривязка; прежние report/metrics/decision/изображения сохраняются как неизменное основание. В v2sourceinventory изменён только SHAadopter; currentloader/tests/character_frames.gd не frozen.

## Границы

Те же reviewed_cell_indices0..31, source_cells=32, all_required_cells_freshly_reviewed=true и source_only_acceptance=true означают сохранённый полный v1осмотр неизменных поз, не повторное рассматривание картинок в этом rebind. `visual_inspection_performed_in_this_rebind=false` записан явно. Must-fix и visualfindings перенесены без изменения. Runtime/full_phase/phase=false. Не использован legacyуниверсальный all32flag.

FIN24/environmental, новые sockets, distinctpresent/prime/disengage/clinch, actualschema2native, audio/gameplayfeel/FPS/exports/CI/Lead/P06/merge этим не принимаются. Сырые фото не читались/не копировались/не передавались. Никакого source/runtime gate не отменено.
