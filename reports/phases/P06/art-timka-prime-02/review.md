# ART02: Тимка present/prime и FIN runtime

**PASS_COMPONENT** для фактической визуальной сборки двух контекстов на frozen source `db84b39711181bb93b6ce58ac4bb7a244dee032b`. Три ART01 coverage finding закрыты новым evidence. Исторический FAIL01 `de0499f73d4c2c0acdf24feedd90283ff3852b31e714af0bed5bfc941d8549e1` сохранён без изменений.

Reviewer `/root/art_timka_fin_v4` независим от автора. WORK только прочитан. Reviewer не запускал Godot/builders/controller/Git mutations/network/generation, не читал и не передавал личные фотографии. Собственные диагностические файлы созданы только в ROOT `reports/phases/P06/art-timka-prime-02`. Единственные engine runs — отдельные разрешённые controller jobs автора; ниже приведены их фактические данные и независимая проверка ART.

## Корпус и независимая проверка

Native02 завершён: actual Input,304/304,90 PNG,source_unchanged=true,source db84. Проверены94 сохранённых artifact digests; для всех40 locomotion captures независимо сверены actual animation/direction/frame, а не их названия. Source/runtime PNG/metadata/sockets и production GDScript/NPC/Core совпадают с прежним3a9 corpus. WORLD32/ACTION28/FIN24 bitmaps не менялись. Исправления source snapshot01→02 затрагивают replay, Python QA wrapper/recovery tests и verify wiring; новый рисунок не выдаётся за созданный.

Movie02 отдельно завершён:214/214,source db84/unchanged, явно переиспользует complete identical-source native02 validation SHA `442e43fdb4019b413835c181c5e1644473ed8b26b6766e6c6f1eb41dc142eaca`. Два сохранённых source inventories равны. Все movie artifact digests проверены. Реальный MP41280×720/60fps содержит3600кадров,60.000s. Reviewer самостоятельно декодировал174 выбранных реальных кадра и просмотрел32 упорядоченные movie strips:8двухцикловых походок,4силовых Space,4F,12V,2incoming interruptions,Full/Reduced. Это проверка реальных временных последовательностей, не ручной просмотр всех3600 кадров/аудиопрослушивание.

Соответствие video n=physics tick−1 проверено заново по8 directional samples: средняя opaque source RGB error11.851, для других offsets30.565–36.093. Source использован только как шаблон диагностического сравнения; ни один sprite не вклеен поверх actual recording. H264 даёт ненулевую цветовую ошибку. Файлы `*_MOVIE_ALIGNED.png` состоят из целых реально отрисованных фигур с окружением.

## Закрытие ART01

- **ART-TIMKA-CTX-STANCE-COVERAGE-01 — CLOSED для db84.** Реальный WASD/release устанавливает нужное направление. Все16 captures показывают idle0/1 обоих контекстов во всех4 направлениях. Эти фактические позы просмотрены при одинаковом масштабе. Неправильно подписанные восемь idle_right в старом corpus не переименованы.
- **ART-TIMKA-CTX-STRIDE-COVERAGE-02 — CLOSED для db84.** Present показывает0,1,2,3; prime0,1. Из longest contiguous real walk trace независимо пересчитаны2wraps на каждом из8 маршрутов, и в live, и в movie. Просмотрены фактические два цикла, направление тела, движение относительно пола и возврат к стойке. Наличие source columns само по себе не использовалось как приёмка.
- **ART-TIMKA-RECORDING-EVIDENCE-03 — CLOSED для новых native02/movie02.** Complete movie result/probe/validation и native-source binding присутствуют. Старый exit130 и partial AVI сохранены; причина старого прерывания не объявлена установленной. Новые jobs используют отдельные пути. Old native01 movie не использован как успешный.

## Визуальный результат

Настоящий Тимка стоит спокойно, руки опущены, обычный шаг имеет четыре собственных рисунка. Prime использует широкую готовую к захвату стойку с поднятыми руками и две другие собственные длинные шаговые позы. Во всех направлениях читаются одна личность/одежда и два разных состояния. FIN0+ACTION0 idle и WORLD6/7 stride prime, WORLD0/1 idle и WORLD2..5 stride present явно учтены как reuse внутри собственного набора; общий run6/7 сохранён. Это не новый бюджет рисунков. При фактически просмотренных циклах существующих рисунков достаточно для базового различия контекстов; новых обязательных context drawings не назначаю.

Space prime имеет собственную FIN contact-позу и видимый силовой акцент, восстановление и реакцию противника. F показывает другую собственную хватательную позу FIN original7. V unarmed/blunt/environmental отображает свои distinct contact cells, тупой предмет и environmental brace, включая исправленную UP v4a. Все16 F/V направленных клипов просмотрены в трёх фазах на native PNG и actual movie. NPC показывают удерживаемую начальную реакцию, контактную реакцию и отдельное падение/death hold; урон не выдан за визуальный эффект без тела. Все47 исходящих actual contact records movie относятся к player action_frame1, что согласуется с видимыми contact snapshots; 16 native NPC contact assertions отмечают frame1. Проверка once-only damage/reward и eligibility остаётся у Gameplay/QA.

Входящий Core контакт прерывает F и заменяет его собственным hurt/fall; последующий R показывает собственную стойку. В death interruption пользовательский быстрый R не даёт оснований утверждать, что именно эта короткая запись полностью выдерживает оба fall кадра игрока: общий ACTION fall уже проверен прежним present component, его байты неизменны. NPC finishers действительно показывают свой отдельный corpse кадр после контакта.

Просмотрены Full/Reduced actual F sequence справа. Reduced сохраняет фигуры/фазы/реакцию с уменьшенным кровавым оформлением; Full показывает соответствующие кровь/следы. Исходы данных одинаковы по existing check, независимая полная settings/balance/performance приёмка этим не подменяется. Полные viewport показывают раздельные подписи present/prime и действия F/V, без обрезки HUD/героя в рассмотренном корпусе.

## Одежда, неизменность и пределы

FIN24 clothing annotations приняты в ART01 после свежего whole-frame просмотра всех24: hashes/точки/колонки сейчас совпадают. WORLD/ACTION60 ранее приняты, также неизменны. Все84 annotations переносятся на те же source frames; новые clip aliases сохраняют metadata этих texture references. Не заявляю повторную новую визуальную оценку всех84 или новое фотографическое сходство. Native transition strips подтверждают собственные читаемые тела без пропавших кадров и скрытого чужого actor.

На момент финального metadata probe позже db84 изменены только `tools/verify_p06_timka_prime.py` и `tools/tests/test_p06_prime_recovery.py`. Их новые guard/recovery semantics не являются предметом ART02. Production art/body/harness и hash-bound native02/movie02 corpus остаются точными. Новый текущий HEAD, новые helper tests/03 runs, свежие builds и CI должен отдельно связать Lead; ART02 не объявляет их проверенными.

ART must-fix по указанному компоненту отсутствуют. Принимаются фактическое visual distinction present/prime, собственная FIN runtime appearance и bound clothing overlays для этого корпуса. Полные способности/управление/баланс, собственные7hero sounds, художественное аудиослушание, FPS/physical input latency, native Windows, owner build/release, вся P06, readiness/P07/merge не приняты этим решением. Переносимый packet перечислен в `transfer_manifest.json`; original movie/source/native PNG не дублируются, сохраняются hashes и собственные выбранные actual-frame diagnostics.
