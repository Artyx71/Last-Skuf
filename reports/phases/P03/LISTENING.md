# P03 — пакет для реального прослушивания

Музыка и звуки оригинальные, с editable sources в `assets/source_audio/last_skuf_demo`. Это проверка конкретных файлов, а не согласие на публикацию или реальные голоса.

1. [Реальная запись игры — диалог, adaptive transitions, десять смертей/retry](dialogue_audio_replay.mp4), около21секунды. Godot MovieMaker записал фактический mixer вместе с изображением; это offline fixed60 capture. Отдельная запись с native PulseAudio: [native_replay.wav](native_replay.wav). Должны читаться bleeps/телефон/death/retry и смены музыкальных слоёв без резких щелчков, пропаданий или дублирующегося трека.
2. [COMBAT из декодированных runtime OGG — два полных круга](audio_preview_combat_runtime_twice.wav),26.67секунды; стык на13.33секунде. Оценить ритм, напор, отсутствие раздражающего повторения и слышимого провала/щелчка на loop.
3. [Монтаж SFX и двух nonverbal bleeps](audio_preview_sfx.mp3),11.3секунды; последовательность и timestamps в [audio_preview_sfx_cues.json](audio_preview_sfx_cues.json). Оценить читаемость/резкость и приемлемость тембра. Это синтезированные сигналы, без клонирования чьего-либо голоса.

Наушники или привычные колонки, обычная комфортная громкость. Нужен человеческий результат: «прослушал эти файлы, принимаю» либо конкретные замечания с клипом/моментом. Отметить, если музыка по характеру не подходит. Факт наличия WAV, numerical peaks и запуск ffplay не являются прослушиванием.

Почему требуется этот пункт: `specs/AUDIO_SPEC.md` §3/§7 требует проверки loops/transitions/death tails на слух; `docs/PROJECT_GATES.md` требует listening report. Root и независимый Lead эмпирически получили `audio content omitted because you do not support audio input` при передаче реального MP3. До человеческого результата AU-01/P03 scoped BLOCKED; полный phase PASS выдаёт независимый Lead.
