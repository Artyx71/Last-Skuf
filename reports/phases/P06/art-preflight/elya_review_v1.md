# P06 — независимый ART preflight: Elya v1

**ACCEPTABLE_STATIC_CANDIDATE**, frames0–4. Нет must-fix likeness, invented forehead marks или nativehalo finding. Это ранний независимый source/native review по собственному фото; не PASS P06, не runtime approval и не окончательная frozen-SHA приёмка.

Проверенный native SHA `2243af0f10e5fbbd61cd9cf3e6019e53178e5f6f779552c1122082f17ad244b2`. Master `4a274f3e94ee2dd37e1e76e6ec6718d3ac9b3ea55f82d159c2a64b39e79d3a3f`. Собственное `elya_ref01.png`, SHA `21181af8b8be3493b16afe12ce803ff033426b0a24f95174a5c4d3c0f70bb6c3`, визуально сверено локально; reference/prompt/master hashes в generation metadata соответствуют файлам.

## Likeness, marks и различие с Ellana

Длинные тёмно-коричневые волосы с мягкими brown highlights/небольшими волнами и offcenter part, широкий лоб, мягкое округлое овальное лицо, тёмные глаза/плавные брови, короткий округлый нос и мягкие полные губы сохраняют собственную личность. Наклон головы и спокойный взгляд напоминают фото; рука у щеки не обязательна и корректно оставлена вне bust. Dark ribbed top с небольшим Vneck соответствует одежде. Нет придуманного пирсинга/очков/татуировок, glamour makeup или произвольной сексуализации.

Forehead marks проверены по увеличенному локальному in-memory просмотру собственного фото без сохранения отдельного reference crop. На фото видны3 небольшие отметки, одна слабее по контрасту. Рисунок сохраняет тот же характер/расположение, делает точки несколько чётче в pixelmedium; это не выдуманные шрамы/символы. Постоянные новые cheekmarks не добавлены; bruise только hurt.

Elya визуально не является перекрашенной Ellana: более мягкий округлый face, короче nose, фронтальнее наклонённая голова, brown-highlighted hair и darkVtop. Ellana имеет более длинный nose/oval, left3quarter view и ivory collaredblouse. Это различие видно в actualnative, даже без speaker name. Тем не менее runtime associations Elya/Timka и Ellana/Yakuza ещё требуют проверки.

Frames0–4: neutral — мягкий спокойный закрытый рот; angry — mild concerned frown с более резкими сведёнными бровями, без villain face; surprise — поднятые брови/раскрытые глаза и открытый рот; hurt — болезненный взгляд/фиолетовый cheekbruise без видимой крови; catchphrase — сдержанная тёплая закрытая улыбка. Все5 различимы в native160×160, включая neutral/angry и neutral/smile. Поддерживающая мирная подача сохранена; диалог/сюжетную роль сами изображения не доказывают.

## Фактический alpha/native

Masterpreview показывает серый фон/soft surround, но его нельзя принимать за production background: sampled cell corners имеют alpha4–31 из255. Threshold128 выделил реальные clear3×3 gutters и целые рисунки. Осмотр actualnative на белом и чёрном фоне (`elya_native_contrast_v1.png`) не обнаружил серого halo, panels или цветного surround. У каждой из9 nativeклеток одна8connected alpha-компонента; нет detached фоновых островков. Rows158–159 полностью прозрачны. Несколько attached1px hair contour hooks видны на белом, читаются как грубые flyaway edges, не требуют procedural face/background repair.

Master1254×1254, atlas1440×160; alpha строго0/255,36 непрозрачных цветов,9 уникальных RGBA рисунков. Pixel edges жёсткие, нет photo fragments или bilinear blur в production. Проверены actual partitions x`[0,420,826,1254]`, y`[0,419,830,1254]`; все9 `source_rect` подтверждены как полный thresholdalpha-bbox; hashes/bounds всех9 совпали. Общий NN scale0.41643835616438357 и baseline158 без anatomical reconstruction. Base top6–8, размеры головы/плеч согласованы для статичных выражений; clipping не обнаружен.

Metadata честно указывает5static expressions, пустой motion mapping, unused5–8. Extra4 не получают motion approval. Остаются runtime dialogue captures5expressions, intended screen size/filtering/speaker binding, correct supporting role и final frozen-source gates. Ревьюер не запускал Godot/controller/generation, не менял Git/source. Raw/reference files не сохранялись в reports и не загружались; записаны только разрешённые отчёты и derived игровые strips.

Все hashes/проверки: `elya_metrics_v1.json`; игровые strips `elya_static5_v1_native.png`, `elya_static5_v1_2x.png`; diagnostic `elya_native_contrast_v1.png`.
