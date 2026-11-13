# ART-P02-02 — shooter posture continuity, attempt2

Только исправление MEDIUM shooter idle→walk. Статус **DRAFT_REQUIRES_INDEPENDENT_REVIEW**. Frozen attempt1 source `1786633` и его author/reviewer reports/inventories не перезаписывались; исходный shooter_master_v1 сохранён.

## Реальный redraw

Встроенный image_gen precise edit создал `shooter_master_v2.png` из нашего оригинального anonymous fictional shooter masterv1. Raw фото/новая чужая графика не использовались. Точный prompt: `shooter_continuity_prompt.txt`; настоящий output_hint и keys без base64: `shooter_continuity_generation_metadata.json`. Задача — переавторить down/up idle posture с нормальной длиной ног и прежней массой каски/брони, не растянуть фигуру целиком.

Генератор изменил не только запрошенные4cells, поэтому production recipe берёт из нового master ТОЛЬКО down/up idle0/1. Остальные28native кадров сохранены byte-identical frozen FAIL source. Ни один patrol/rusher/Yakudza sprite не затронут.

Новый down idle — реально сгенерированные прямее стоящие ноги/таз/корпус. Новый up idle первоначально имел чрезмерно длинные голени; выполнена намеренная локальная native pixel правка нижней части ноги: убраны3избыточные строки46–48, целые каска/броня/торс/бедро0–45 перенесены вниз3px, ботинки/подошвы49–63 сохранены. Масштаб каски, торса и ботинок не меняется. Это документированная анатомическая сборка пиксельной позы, НЕ uniform scaling всей фигуры и НЕ утверждение о человеческой ручной оценке. Результат открыт и проверен на реальных render frames.

Рецепт `build_shooter_attempt2.py` читает сохранённый before PNG в новом attempt2 и generated masterv2; заменяет ровно4cells, применяет прежнюю35-color available palette/NEAREST/hardalpha/anchor. Записывает только shooter PNG/native source и shooter entry shared atlas, плюс новые attempt2 evidence. `shooter_pose_redraw_attempt2.png` — фактический native pixel source. Другие28frame RGBA hashes не изменились; patrol/rusher entries и глобальные atlas поля сохраняются. Оригинальный общий build_assets.py остаётся историей первого набора и не должен запускаться для этого fix: актуальный shooter recipe указан в shooter source metadata.

Запуск: `.tools/art-venv/bin/python assets/source_art/enemies/build_shooter_attempt2.py`. Не запускает внешние API, не меняет CSV, gameplay или P01.

## Actual view и пределы проверки

Head top: down idle12→walk6 заменено на6→6; up11→6 заменено на6→6. Прежние walk poses сохраняют естественный bob6–8. Это сопровождается новой иерархией ног/таза/корпуса; один bound не был единственным критерием.

`reports/phases/P02/attempt2/shooter_transition_probe.gd` создал настоящий Godot AnimatedSprite2D before/after render: три цикла idle3FPS→walk8FPS→stop, кадры анимации sampled в JSON; все6walk frames реально проигрывались в каждом цикле. Logical viewport640×360, native1× и2× evidence. MovieMaker записывает physical1280×720 из настроек проекта; MP4 приведён к logical640×360 через nearest. Runtime screenshots непосредственно640×360. Первичная попытка относительного movie пути закончилась ERR_CANT_OPEN; failed log сохранён. Исправленный absolute-path run exit0 и безERROR, AVI/MP4 реально существуют.

Автор открыл before/after4×comparison, runtime idle/start/stop screenshots и contact sheet с chronological8FPS extraction из реального MP4. Наблюдение: прежнее сильное вытягивание исчезло; контур/масса каски и бронепластины устойчивы,2px шагающий bob и небольшие различия разворота корпуса остаются. Автор не выдаёт просмотр кадров за human continuous playback signoff или independent art PASS. Root/reviewer получают сам MP4 для повторного просмотра.

Evidence/inventory только в `reports/phases/P02/attempt2/shooter_*`. Отдельный screenshot/structural check не объявлен доказательством фазового PASS. Commit/push не выполнялись.
