# Timka compact schema2 — независимый bounded QA v2

**PASS_COMPONENT.** TC-C01 и TC-C02 закрыты для точной v2 реализации adopter SHA b1b8d3d72536947715234c99003c047c3bc8d368c97d5fd652b67a5ac7842b8c. Независимо выполнены actual Godot96/96, Pillow25/25 и10 дополнительных TempDir отрицательных сценариев. Это проверка структурного пайплайна и допуска к миграции, не ART/source принятие, настоящая migration approval, способность/готовность Тимки, P06 или merge.

Исходный v1 FAIL сохранён: decision SHA e01f4a6249b73e5091ab71b27a8a9c1a67fed1bd2b72daddd74c80b3604bc511 и все26 публикуемых v1 artifacts повторно совпали с их manifest. Ни один файл qa-timka-compact-01 не изменялся. Семь v2 implementation keys совпадают с timka-compact-code-freeze-02.json до/после запуска и сохранены отдельными точными code snapshots. Diff содержит только расширение adopter scope/provenance checks, шесть targeted unit cases и регистрацию несвязанного CH01 теста в common verify. Поведение CH01/Core/CombatLab этим review не принимается.

## Закрытие исходных дефектов

TC-C01: adopter теперь требует канонический owner decision path; exact status/kind/phase/actor/profile; integer counts32/28/24 и integer total84; точные excluded actions и required contexts; phase/merge false. Оригинальный v1 сценарий с APPROVED, но UNAPPROVED_OTHER_LAYOUT, и согласованно обновлёнными manifest/review hashes теперь действительно получает ValueError до любых записей. Это проверено нашим отдельным скриптом, а не только добавленным автором unit test. SHA-снимок всех файлов временного fixture до/после отказа совпадает.

TC-C02: путь упаковщика канонический, recorded script_sha256 сравнивается с actual script SHA, а required review inventory по-прежнему связывает этот же файл. Оригинальный сценарий64 нулей при actual c1a034… теперь действительно отвергается до записей. Дополнительно точная копия скрипта под другим именем/путём отвергается, даже если все прочие hashes согласованы. Эти пробы импортировали сохранённые v2 snapshots; actual tested implementation digest записан в adversarial-results.json.

Независимые10 probes также проверили owner kind/phase, float84 и float budget28.0 вместо integers, неподходящие exclusions и недопустимые phase/merge approval. Все10 получили конкретный ValueError и сохранили полный SHA snapshot каждого temporary project. Авторские25 unit tests отдельно закрывают wrong budget/actor/context/canonical owner path и прежние pixel/inventory/review/backup/socket проверки. Fake reviews и положительные FIN adoption в unit tests существуют только в TempDir; они не являются настоящим ART evidence или переносом FIN в WORK.

## Проверенный неизменный контракт

compact_timka.py SHA c1a034a4247898f345aa1f9d05d0646fbeb4bd2488ea6d83e00c557cdb5d1f96 и все6 supported PNG/manifest bytes совпадают с v1. Поэтому исправление adopter не пересобирало рисунки и не меняло 32/28/24 mapping. В v1 actual wholecell roundtrips32/28/24 уже проверяли transform и exact WORLD PNG; в v2 этот неизменный transform повторно не запускался. Свежие96 source-contract checks проверяют actual candidate PNG decoded RGBA и metadata/maps/rects, changed pixels, отказ legacy Timka/schema/profile, asymmetric socket counts/stride/column mapping и запреты unsupported clips.

Godot открывал только ROOT isolated-project/game без editor/native/display.418 скопированных input-файлов остались byte-exact, все XDG config/data/cache/state/runtime, TMPDIR и save overrides направлены в собственные ROOT каталоги. Pillow использовал только временные проекты. Реальные9 Timka runtime файлов WORK после QA совпадают с исходной копией; FIN runtime отсутствует. Никакой production migration не выполнялось. В WORK reviewer ничего не записывал; Git/Controller/network/generator не вызывались.

## Обязательные дальнейшие gates

Вся v1 оценка прерываний остаётся актуальна: замена PNG+JSON не транзакционна как пара. При остановке между replace сохраняются exact legacy backups и pending JSON, повтор отказывает без перезаписи; автоматического rollback/resume нет, нужен явный reconciliation. Эта механика v2 не менялась и повторно не запускалась; её новый PASS или улучшенный recovery не заявляется.

Настоящий перенос остаётся отдельным действием автора после свежего независимого ART technical rebind на точный исправленный adopter SHA. Если предыдущий ART inventory включал старый adopter, QAv2 не исправляет его автоматически и не заменяет ART erratum. FIN source finding, authored sockets и context abilities этим QA не закрываются. Текущая legacy Timka runtime намеренно отвергается новым loader; полный character_frames/common CI до migration нельзя называть прошедшим на основании этих96/25. После переноса обязательны actual frames, Gabar/Oleg/isolation regressions и дальнейшие native/runtime ART/gameplay/Lead gates. Результаты параллельных авторских регрессий и CH01 проверки здесь не присваиваются.

Нерешённых замечаний в исправленном bounded compact/adopter scope не найдено. Публикуемые code snapshots/diffs/scripts/probes/logs/results/inventories перечислены в artifacts.json; isolated game/.godot/cache/raster copies остаются локальным evidence.
