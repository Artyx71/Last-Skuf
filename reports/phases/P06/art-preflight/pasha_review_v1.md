# P06 — независимый ART preflight: Pasha v1

**ACCEPTABLE_STATIC_CANDIDATE**, frames0–4. Must-fix likeness/invented-features findings отсутствуют. Проверены реальные master/native изображения и собственное фото; это не PASS P06, не runtime approval и не окончательная frozen-SHA приёмка.

Проверенный native SHA `a50abd0d060c2d01118697e1e8bf3ec69f301bd02f3adde4cba125a435932cf7`. Master `1343cc89610d813366876ddb80a894117572849cb620d3f023a14a3950ad3ad5`. Собственный локальный `pasha_ref01.png`, SHA `8d63afa1a7c598de854b68d07afc25c82a5e0d69afef2caac181ce0d7d5d19fa`, сопоставлен визуально. Generation reference/prompt/master hashes совпали с фактическими файлами.

## Likeness и базовые5

Высокая растрёпанная объёмная lightbrown/darkblond причёска, взъерошенная вверх/наружу, тёмные стороны, сильные брови, стройное молодое взрослое лицо, прямой сравнительно узкий нос и короткая борода/усы с небольшим pointedchin/goatee соответствуют собственному фото. Hair clusters сильнее взбиты и имеют тёплые copper/plum highlights в общей palette; коричневая масса/характерный силуэт остаются узнаваемыми. Это minor caricature observation, не подмена на чёрноволосого Yakuza/Ryzhik. От Timka отличается высокой беспокойной причёской и более узким лицом. Физический рост персонажа из bust не доказывается.

Одежда — тёмный простой casual sweatshirt с малой приглушённой blue-grey деталью воротника; нет скопированного photo crest, читаемых брендов/надписей или выдуманных татуировок. Нет добавленных очков, постоянных шрамов/родинок или чужих facial anchors.

Frame0 neutral: закрытые губы, нетерпеливый взгляд. Frame1 angry: сведённые брови и оскал. Frame2 surprise: широко раскрытые глаза и небольшой открытый рот. Frame3 hurt: прищур/опухший глаз, фиолетовый bruise и напряжённые губы, без видимой крови. Frame4 catchphrase: большой энергичный laugh/shout с подъёмом головы, соответствует гиперактивной подаче. Все5 отличимы в actual native160×160. Catchphrase больше меняет head/neck angle, чем базовый neutral, но это честный отдельный static expression; motion continuity этим не одобряется.

## Native/pack/provenance

Master1254×1254; actual atlas1440×160; alpha только0/255;39 непрозрачных цветов;9 уникальных RGBA рисунков. Hard square pixels, нет фотофрагментов, встроенного bilinear blur, checkerboard/panels, загрязнения соседними клетками. Лицо/брови/рот читаемы при native размере; волосы целиком помещаются. Основные base bounds0–3 top10, catchphrase top7 с общей baseline158; head tilt/static pose объясняет3px, не является случайным clipping.

Фактические partitions x`[0,426,817,1254]`, y`[0,413,820,1254]`. Все9 `source_rect` равны независимо измеренным полным alpha-bbox в собственных partitions; все9 frame hashes/bounds совпали. Один общий NN scale0.39378238341968913 и centered-x/baseline158, без face reconstruction/compositing. Metadata честно содержит5 static expressions, пустой motion mapping, unused5–8. Девять unique drawings не объявляются девятью runtime выражениями/анимацией.

Остались native dialogue captures5expressions, speaker/filtering/intended screen size, world/portrait consistency, controls и final frozen-source review. Godot/controller/Git/source изменения и генерация ревьюером не выполнялись. Фото только локально просмотрено, не копировалось/не загружалось; записаны только разрешённые отчёты и derived игровые strips.

Полные hashes/проверки: `pasha_metrics_v1.json`; игровые strips: `pasha_static5_v1_native.png`, `pasha_static5_v1_2x.png`.
