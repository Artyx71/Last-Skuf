# ART: Тимка present / disengage, компонент

**PASS_COMPONENT** для визуальной сборки present/disengage на frozen source `69ffc58c7ff2dedd773bd58b137553c3666ad1da`. Это ART-приёмка ограниченного компонента, не Gameplay/QA/Lead gate и не полная P06.

Reviewer `/root/art_timka_fin_v4` независим от автора. WORK только прочитан. Проверены исходные PNG/метаданные, authored clothing annotations, реальный native Input replay и кадры настоящей записи. Godot/builders/controller/Git mutations/network/generation не запускались. Записаны только reviewer-диагностики под ROOT `reports/phases/P06/art-timka-present-01`.

## Реально проверенные материалы

Native01 `validation.json` имеет passed/source_unchanged=true и frozen head69ffc; live98/98, movie72/72, 26 actual viewport PNG. Reviewer проверил34 artifact digests и все1108 сохранённых source digests против WORK до последующей авторской смены harness. Полный source snapshot не выдаётся за актуальный после этой смены. Production-art/controller bindings ниже остаются точными; новая coverage требует отдельного ART addendum.

Просмотрены WORLD32/ACTION28 authored v2 annotation boards; дополнительно целые оригинальные кадры с кольцом вокруг anchor без закраски центрального пикселя, включая исправленные WORLD6/7, ACTION8/15 и спорные тёмные точки WORLD8/ACTION21/22. Для всех60 независимо проверены actor/profile/count, исходная/компактная колонка, direction/index, sheet SHA, individual original frame RGBA SHA, целочисленные координаты и непрозрачность точки. Точки визуально находятся на худи/его швах и деталях, не на коже, лице, волосах или пустом фоне. Изначальная шестицветная `garment_palette` относится к сохранённому palette candidate; ручная точка может принадлежать другому цвету того же реального худи. Цвет сам по себе не использовался как доказательство одежды. FIN sockets не проверялись и не принимаются.

Просмотрены все24 actual native pose captures (6 фаз ×4направления), wall stop и ready after restart; представлены также полные viewport PNG с HUD. Независимо декодирован неизменённый MP4 SHA `75081d76a020d45b7605c9d7bc6cb676f21749afe059defc09e1422affb5f38c`: 904 кадров1280×720/60fps. Оценивались выбранные реальные кадры и упорядоченные filmstrips, а не все904 вручную. Финальные `*_ALIGNED.png` показывают6 фаз каждого направления, hurt и fall/restart. Ни один source sprite не подставлен поверх записи.

Для подписей отдельно проверено соответствие physics/video: 24 samples по opaque RGB своего sprite при saved visual origin дают video n=tick−1 (mean RGB difference12.067; другие проверенные offsets25.4–31.979). Lossy H264 не обязан давать нулевую ошибку. Первоначальные приблизительные boards без суффикса `_ALIGNED` сохранены как рабочие preview и не являются финальным acceptance evidence. Два начальных ffmpeg diagnostic decode failures сохранены; они не запускали игру и не меняли её файлы.

## Наблюдаемое поведение и границы

Собственное лицо/макушка/чёрный худи/обувь Тимки сохраняются. Защитная поза → четыре собственных walk drawings в обратном порядке → возврат читается как короткое отступление спиной с сохранением направления взгляда. Ступни действительно меняют опору, целая фигура отходит от противника; ни пропавшей фигуры, ни чужого тела, ни зеркальной подмены/обрезанных конечностей в просмотренных фазах нет. Выбранный короткий шаг допускает существующие рисунки: новых disengage source drawings этот пакет не заявляет и для данного bounded компонента не требует. Это не новое уникальное добивание и не доказательство различия с ещё отсутствующим prime.

На wall capture игрок остаётся перед препятствием и возвращается к собственной стойке. В просмотренных movie interruption-последовательностях текущая поза сменяется собственным hurt и двумя fall кадрами, затем виден восстановленный Timka после R. Эти native01 hurt/death cases происходят через явный тестовый `receive_hit`; данный пакет не выдаёт их за доказательство вражеского Core contact в каждом guard/active/recovery окне. Дополнительные входящие Core/projectile scenarios и новый harness относятся к следующему native02/addendum и Gameplay review.

HUD показывает «Тимка / настоящее», явно сообщает отсутствие оружия/добиваний, действие F и остаток cooldown. Верхний текст остаётся над игровой областью, нижние строки — в viewport640×360 без обрезки; в просмотренных кадрах окно защиты Олега не появляется. После рестарта виден тот же собственный персонаж; незавершённый prime не выдан за готовый. Числа cooldown рассматриваются как отображение текущего состояния, не как ART-доказательство баланса или input latency.

## Решение

Source/native ART must-fix для этого компонента отсутствуют. Принимаются WORLD/ACTION clothing sockets и визуальная сборка present/disengage на указанном69ffc art/controller корпусе. Native02 на новом harness требует свежего addendum, даже при неизменных art hashes.

Не принимаются prime/context distinctness, FIN sockets, собственные добивания Тимки, новая музыка/аудиослушание, субъективное управление реальным игроком, физическая input latency, производительность, Windows native, полная P06/readiness/P07/merge. Приёмку настоящих контактов, отмены, отсутствия invulnerability/урона и баланс должен дать независимый Gameplay/QA/Lead по требуемой coverage.
