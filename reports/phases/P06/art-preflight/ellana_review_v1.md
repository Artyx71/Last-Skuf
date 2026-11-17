# P06 — независимый ART preflight: Ellana v1

**ACCEPTABLE_STATIC_CANDIDATE**, frames0–4. Нет must-fix likeness/alpha/crop findings. Это ранний review actual source/native и собственного приватного фото, не PASS P06, не runtime approval и не final frozen-SHA приёмка.

Проверенный native SHA `519a1a3cccfeb5c34accd608be5179c46aa92b3f6556994d356792bd7e77c803`. Master `003a1577d50f14ee32ff341c7d36f3dbf9f50e86353d91ff3f138d9f798ca3f8`. Проверено именно собственное `ellana_ref01.png`, SHA `0f35d82fb6b8e4b5877c9e0f29a49163550b1d0f3390218b15e6bcadc3a4c89c`, не фотография Elya. Generation reference/prompt/master hashes совпали с фактическими файлами.

## Likeness и выражения

Длинные очень тёмные волнистые волосы, почти центральный пробор, вытянутый светлый овал лица в левом3quarter повороте, длинный заметный нос, естественно полные розоватые губы и ivory loose collared blouse соответствуют собственному фото. Нос сохранён выраженным/слегка подчеркнутым, как требует brief; нет extreme deformity. Волосы несколько объёмнее и jaw/brow shadows угловатее фотографии, в рамках общей карикатурной pixel language. Сохраняются женственные пропорции собственного лица; нет переноса мужской челюсти/телосложения Yakuza, фото-обломков или произвольной pinup позы. Не найдены выдуманные украшения/пирсинг/татуировки/читаемые бренды.

Frame0 neutral — внимательный взгляд/закрытые губы;1 angry — явное сведение бровей/напряжённые губы;2 surprise — поднятые брови, раскрытые глаза и небольшой открытый рот;3 hurt — болезненный взгляд и cheekbruise без видимой крови;4 catchphrase — calling с большим открытым ртом/напряжёнными бровями. Все5 различимы в actual native160×160. Calling image не доказывает narrative blame/control; роли/диалог ещё требуют runtime/narrative review.

## Alpha fringe и pixel clarity

Master действительно имеет заметный красно-белый низкоальфовый мусор под ровным срезом blouse. Проверка только master дала бы ошибочное заключение о production contamination. Ниже alpha128 bbox у source base5 максимум alpha соответственно21/25/25/18/17 из255. Эти пиксели полностью отбрасываются техническим threshold128 и не входят в production native.

Осмотр actual native на обычном тёмном фоне и отдельно на белом/чёрном (`ellana_native_contrast_v1.png`) подтверждает отсутствие цветного halo/белых полос под shirtbottom. Native rows158–159 во всех9 клетках полностью прозрачны. У каждой base-клетки одна8connected alpha-компонента, без оторванных фоновых островков; размеры0–4:16887/16880/17174/16976/17063 пикселей. На белом фоне видны отдельные attached1px hair contour hooks; они соединены с волосами и читаются как rough flyaway outline, не чужой фон. Нет основания требовать anatomical/procedural repair или новую генерацию по этим краям. Ровный нижний bustcrop — ожидаемое завершение портрета, без случайного среза головы/плеч.

Master1254×1254, actual atlas1440×160; alpha0/255,35 непрозрачных цветов,9 уникальных RGBA рисунков. Hard square pixels, без bilinear blur/photographic remnants/checkerboard/panels. Реальные partitions x`[0,428,829,1254]`, y`[0,421,839,1254]`; все9 `source_rect` подтверждены как целые threshold alpha-bbox, все9 frame hashes/bounds совпали. Общий NN scale0.390745501285347, baseline158, без реконструкции лица. Base top6 и bottom158; ширина/смещение1–2px приемлемы для статичных эмоций.

Metadata честно содержит5 static expressions, пустой motion mapping, unused5–8; jitter animation не заявлен и не одобрен. Остаются actual dialogue captures5expressions, speaker/filtering/intendedscreen size, правильная supporting роль Ellana/Yakuza, final frozen-source gates. Godot/controller/Git/source изменения или generation ревьюер не выполнял. Фото локально просмотрено, не копировалось/не загружалось; записаны только разрешённые отчёты и derived игровые strips.

Полная SHA256-инвентаризация/проверки: `ellana_metrics_v1.json`; игровые strips `ellana_static5_v1_native.png`, `ellana_static5_v1_2x.png`; white/black diagnostic `ellana_native_contrast_v1.png`.
