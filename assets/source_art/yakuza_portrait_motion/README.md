# P03 — feature-only portrait motion Якудзы

Статус: **DRAFT_REQUIRES_INDEPENDENT_FEATURE_MOTION_REVIEW**. Это отдельный настоящий mouth/blink pack; существующие approved present/past/world PNG и P01 atlas не менялись. Личность/лицо вне описанных feature masks остаются approved базой. Новый human likeness gate не вводится.

## Происхождение

Один встроенный `image_gen` precise edit использовал `feature_reference_board.png`: точную RGBA-копию approved neutral/angry portraits, дважды повторённых в2×2 layout и увеличенных2×nearest. Raw фото/реальные голоса/чужие assets не использовались. Показанные прежде approved черты, чёрная футболка, широкое вымышленное тело и телефон сохраняются.

Точный prompt: `feature_prompt.txt`. Фактические возвращённые ключи и output_hint: `generation_metadata.json`, без base64. `feature_master_v1.png` — настоящий generated RGBA результат1254×1254,2×2cells627×627. Вверхneutral, внизangry; слеваmouth-open, справаblink. Генератор изменяет некоторые пиксели и за пределами лица, поэтому такой master НЕ используется целиком как новая копия approved portrait.

`neutral_approved_reference.png`, `angry_approved_reference.png` — private-project собственные approved raster crops, не raw фотографии. `feature_reference_board.png` — единственный image_gen input. Original generated file оставлен в CODEX_HOME согласно skill. Внешний paid CLI/API, sudo и новые программы не использовались; локальная Pillow13 уже доступна.

## Native source и сохранение лица

`feature_masks.json` — явные native polygon ROI для губ/рта и внутренних век двух эмоций. `*_mask.png` — фактические бинарные160×160masks. Всё снаружи каждой маски в соответствующем runtime frame побайтно равно approved base. Место/масса головы, волосы, нос, подбородок, родинки, брови вне eye-interior ROI, одежда, руки и телефон не анимируются.

`build_assets.py` берёт реальные generated feature cells, выбирает их nearest-neighbor на160×160, приводит к существующей31-color approved palette безdither и вставляет только через сохранённуюbinarymask в точную approved базу. Alpha берётся из базы без изменений. Rest frames — прямые RGBA-копии approved neutral0 и angry1, вообще без quantization. Никаких face-swap plates, автоматического downscale фотографии, bob/scale/head translation вместо речи нет. Mouth visibly opens и оба глаза закрываются реальными изменениями рисунка.

`portrait_motion_native_source.png` — actual final pixel-grid source480×320. Слоистый Aseprite source не создавался. Запуск из корня: `.tools/art-venv/bin/python assets/source_art/yakuza_portrait_motion/build_assets.py`. Recipe пишет только новые portrait_motion PNG/atlas/source и новые P03 portrait evidence. Approved P01 files read-only.

## Runtime контракт

`game/assets/art/yakuza/portrait_motion.png`:480×320,160×160cells. Rows0neutral/1angry; cols0rest/1talk/2blink. Отдельный `portrait_motion_atlas.json` хранит rectangles/origins, RGBA/file/mask hashes, source/masks и timing suggestions. Origin(80,160) согласован с прежним portrait atlas.

Talk: alternating rest/talk при8FPS во время reveal. Blink: отдельный closed-eyes frame примерно0.125s, suggested interval4s; затем вернуть соответствующий silent/talk state. Rows не следует трактовать как два состояния одного speaking loop. Actual DialogueDirector задаёт runtime schedule; artist timing здесь предложен и должен быть согласован с runtime интеграцией.

## Авторская проверка и пределы

Автор открыл approved reference board, настоящий generated master и exported native sheet на checkerboard2×. Рот neutral/angry явно открыт с тёмной полостью/малым tongue/teeth акцентом; blink закрывает оба глаза, сохраняя характерные спокойные/нахмуренные brows. Feature rendering ограничен масками; местами меняется локальная lip/eyelid shading, что является частью рисунка речи/мигания. При этом никакой whole-head motion нет.

Структурно rest exact, outside masks0changed, alpha exact, palette31, canvas480×320. Talk меняет226/232pixels, blink223/204pixels. Это не самостоятельное доказательство визуального качества: root/runtime/reviewer оценивают реальное dialogue video с world/text/effects. Author не объявляет independent PASS или fake human signoff. Если при повторном просмотре обнаружится неудачный feature transition, исправляется только mask/feature source, approved face не подменяется.

CSV не редактировался: `reports/phases/P03/portrait_license_row.csv` — только предложение для root, который объединяет его с audio provenance. Public release/merge/voice rights не выводятся из approved likeness. Commit/push не выполнялись.
