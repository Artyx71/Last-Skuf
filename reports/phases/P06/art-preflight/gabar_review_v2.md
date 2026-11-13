# P06 — независимый ART preflight: Gabar, pack v2

**ACCEPTABLE_STATIC_CANDIDATE**, только frames0–4. Это проверка кандидата по исходнику/приватному фото/native160×160, не PASS P06 и не runtime approval. Предыдущие `gabar_review.md`, `gabar_metrics.json` и их SHA остаются историей другого native atlas, не перезаписаны.

Точный проверенный native: `9f7ce3e913a8550d82cdda32463c3d94496c4044d49cb6a4388d4a059e89c44d`. Master прежний: `59ee2c4ce1500ddf81f77b590a6fe6ca869ec4502085744e4a95676af7156cf6`. Собственный локальный reference: `a363744ee1e505d72c8bf1afb7840e271ff250f8c3aee8d81404139e4c502da5`.

В новом atlas головы/плечи немного крупнее, чем в v1, остаются целыми. Все9 bounds `[4,8,156,158]`, alpha0/255,40 непрозрачных цветов. Pixel edges жёсткие; нейтральное лицо, очки и рот/брови остальных4 выражений читаются в native размере. Нет must-fix likeness, wardrobe или expression-ID проблемы. Предыдущее замечание о мелкой stipple-текстуре остаётся minor polish observation; новый технический масштаб не превращает её в blur. Пять базовых статичных выражений по-прежнему приемлемы для продолжения интеграции.

Прочитан revised `pack_portraits.py`, SHA `5c40e3266a6d7946eb39102b08ecef165618d21ee7e4fa5ba7606d1f20ca71aa`. Он находит реальные прозрачные gutters, берёт целый alpha-bbox каждого портрета, использует один общий масштаб0.3948051948051948 для всех9, nearest sampling и общую baseline158. Это техническая упаковка целых рисунков без реконструкции лица. Независимый расчёт bbox внутри фактических partitions совпал с каждым `source_rect`; все9 RGBA hash/bounds совпали с manifest. `shared_animation_references` теперь пуст; `static_expressions` содержит все5 IDs, `[5,6,7,8]` явно unused. Ранее запрещённый motion mapping в metadata снят корректно. Не заявляется, что источник теперь подходит для анимации.

Новый packer проверен на этих реальных9 клетках; произвольный будущий master потребует такого же осмотра, алгоритм gutters сам по себе не доказывает соответствие IDs. Runtime filtering/размер в диалоге/world consistency/frozen-SHA final gates ещё не проверены. Никакие исходники, Git или процессы Godot/controller не менялись. Записаны только отчёты и derived игровые filmstrips в разрешённом каталоге. Приватное фото не копировалось и не загружалось.

Инвентаризация и проверки: `gabar_timka_v2_metrics.json`; native strip: `gabar_static5_v2_native.png`; NN2x: `gabar_static5_v2_2x.png`.
