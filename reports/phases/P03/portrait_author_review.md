# P03 — авторский осмотр portrait motion

**DRAFT_REQUIRES_INDEPENDENT_FEATURE_MOTION_REVIEW**. Реальный generated mouth/blink pack готов к runtime; этот отчёт не independent art/phase PASS.

Утверждённые present neutral/angry использованы как immutable RGBA bases. Один built-in precise edit создал четыре реальные feature variants из собственного reference board, без raw фотографий. Master/prompts/metadata и explicit source masks сохранены. Высокий generated master не заменяет approved лицо: runtime копирует из него только mouth/eyelid ROI, сохраняя прочие пиксели базы.

Автор открыл reference/master/native2×checkerboard preview. В двухtalk frames рот явно открыт, в двухblink frames оба глаза закрыты. Black hair, calm/angry brows, лицо/телефон/чёрная футболка согласованы с approved base. Никакого bob/scale/head movement вместо речи нет. Статические rest frames служат частью настоящего rest↔mouth-open animation, а не объявляются talk сами по себе.

`portrait_structure.json` подтверждает480×320/160×160,31opaque colors, alpha0/255, transparentRGB0, rest RGBA exact и0changes outside binary feature masks. Mouth changes226/232pixels, blink223/204pixels; frame alpha идентична базе. Эти проверки не означают independent perceptual QA. Реальное dialogue/reveal/blink schedule, world visibility и VHS/reducedmotion проверяют runtime/root и reviewer по actual video отдельно.

Отдельные portrait_motion.png/portrait_motion_atlas.json переданы root для интеграции. Suggested talk8FPS, blink0.125s/interval4s. Approved P01 PNG/source/atlas не менялись; weapon carryfix, audio, tests и gameplay автор арта не трогал. CSV не менялся, root получает новый row proposal. Нового human likeness gate не создано: вне feature masks лицо буквально неизменно. Commit/push/publication не выполнялись.
