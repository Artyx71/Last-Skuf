# Якудза — исходники P01

Статус всего набора: **DRAFT_REQUIRES_LIKENESS_REVIEW**. Это реальная генерация оригинального рисованного pixel-art через встроенный `image_gen`; ниже нет разрешения на публичное распространение портрета частного человека. Никакой PASS художником не присваивался.

## Происхождение

В текущей сессии владелец проекта явно разрешил встроенный image_gen с фотографиями всех персонажей. Для P01 использована только правильная фотография `assets/references/characters/yakuza_ref01.png`, предварительно открытая локально через view_image. Вызовы не использовали платный CLI/API fallback. Второй вызов дополнительно получил наш `portraits_master_v1.png` для согласованности собственного дизайна. Сырые фотографии сюда не копируются.

- `portraits_master_v1.png` — реальный RGBA результат встроенного генератора, 1536×1024; 3×2 ячейки 512×512, пять выражений и пустая последняя ячейка.
- `world_master_v1.png` — реальный RGBA результат встроенного генератора, 1536×1024; 8×4 ячейки 192×256.
- `*_prompt.txt` — точный текст соответствующего вызова.
- `*_generation_metadata.json` — возвращённые имена полей и output_hint, без base64 payload. Original generated files оставлены на месте в CODEX_HOME согласно imagegen skill.
- `portraits_native_source.png`, `world_native_source.png` — экспортированные исходники на фактической фиксированной сетке160/48×64. Layered Aseprite/LibreSprite source не создавался; редактируемый растровый source — PNG и воспроизводимый packing recipe.
- `build_assets.py` — техническая нарезка собственных сгенерированных рисунков, НЕ автоматическое превращение фотографии в pixel-art. Никаких raw photos он не читает. Технические операции: crop, alpha threshold128, NN sampling, вставка в фиксированный foot anchor, зеркалирование up-row ради постоянной левой руки с телефоном, намеренно выбранная31-цветная палитра и экспорт. Все изображения на выходе прозрачные RGBA с alpha0/255, transparentRGB=(0,0,0).

## Воспроизведение

Из корня проекта: `.tools/art-venv/bin/python assets/source_art/yakuza/build_assets.py`. Установлена локальная Pillow13.0.0 через существующий uv0.13.7, безsudo. Каталог `.tools/` игнорируется. Скрипт обновляет PNG/atlas и структурные evidence. Он не меняет scenes/scripts, не публикует файлы и не утверждает likeness.

## Контракт

Runtime: `game/assets/art/yakuza/portraits.png`800×160, 5 столбцов160×160; neutral, angry, surprised, hurt, catchphrase. Размер160 выбран из разрешённого диапазона: сохраняются узнаваемый объём волос, соотношения глаз/носа/губ/подбородка и родинки, остаётся место для текста в640×360 UI. Insets2px защищают контур от случайного соседнего кадра. Optional talk отсутствует.

Runtime: `game/assets/art/yakuza/world_sheet.png`384×256, 48×64×8×4; down,left,right,up; col0–1idle3FPS, col2–7walk8FPS. Pivot=(24,58), нижняя граница подошвы каждого кадра58. Согласованные blacktee/густыеblackhair/широкое короткое вымышленное тело/phone. Подробные rect/origin/bounds/hash/fps/source в `atlas.json`.

## Честные ограничения

Автор открыл исходные и native экспортированные sheets, сравнил с правильным фото. Наблюдение художника: узнаются объёмные асимметричные волосы, спокойный прищур neutral, геометрия лица и родинки; чёрная футболка и телефон согласованы. Это НЕ человеческий signoff или независимая оценка сходства.

Original masters содержат мягкие alpha fringes и градиентные RGB в полностью/почти прозрачных областях; numeric corner alpha0/1 и compositing на зелёный фон показали, что это не непрозрачная фоновая matte. Художник визуально не обнаружил фотографических фрагментов: изображения полностью рисованные. Native export порогомalpha128 удаляет прозрачный шум; это не утверждение, что любой future master можно так очищать.

Генератор не выдержал идеально однородную сетку крупного master; настоящая единичная pixel-grid и hard alpha зафиксированы в native production export. Поэтому highres master не следует использовать напрямую в игре. Это разрешённая техническая обработка сгенерированных pixel drawings, не photo downscale/posterization.

Остался небольшой межкадровый jitter объёма волос/тела и высоты idle2. При зафиксированных подошвах верх головы гуляет на2–4nativepx; независимый reviewer должен оценить его в анимации. Верхняя часть волос темнее фона некоторых локаций — проверять силуэт в Godot. Выражения intentionally гротескные; пользователь должен подтвердить, что это нужная узнаваемость. Созданы отдельные past/flashback-портреты: менее тяжёлая молодая вымышленная версия, согласованная с исходной фотографией. World sheet изображает только тяжёлую present-версию. Разрешение на public distribution и human likeness approval пока не получены.


## Дополнение: past / flashback

Требование `ART_PIPELINE.md` о прежней и стилизованной современной версиях выполнено отдельным atlas `portraits_past.png`, 800×160, в том же порядке пяти эмоций. Это прежний период, не пожилой возраст. Face/hair/phone/black tee остаются согласованными; шея и щёки менее раздуты. Размер глаз/головы и рамка сохраняют совместимость с present-портретами.

- `portraits_past_master_v1.png` — первый реальный generated past master. Автор обнаружил белёсую кайму вокруг волос и не принял этот вариант как финальный экспорт.
- `portraits_past_master_v2.png` — результат отдельного targeted built-in background-extraction edit; удалена светлая matte/кайма, сохранены лица и оригинальный рисунок. При проверке углы имеют alpha 0, native checkerboard preview показывает чистые края.
- `past_portrait_prompt.txt`, `past_cleanup_prompt.txt` и соответствующие `*_generation_metadata.json` сохраняют оба вызова.
- `build_past_assets.py` — отдельный воспроизводимый packing, читающий shared palette из atlas. Он не перезаписывает present/world PNG. Запускать после основного `build_assets.py`; основной скрипт сохраняет уже существующий `portraits_past` entry.
- `portraits_past_native_source.png` — фактическая native pixel-grid версия для ручной растровой правки.

Автор открыл master v1, master v2 и native preview. Сходство и выбор между era-версиями по-прежнему требуют человеческого signoff; отдельного old-world moveset в P01 не требуется. Всего выполнены четыре встроенных image_gen вызова: present portraits, world sheet, past portraits, past alpha cleanup.
