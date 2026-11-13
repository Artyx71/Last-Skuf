# P03 / AU-01 — авторская поставка audio candidate

Статус: реальные оригинальные audio assets и техническая проверка готовы; perceptual listening **SCOPED BLOCKED**, независимый PASS этим документом не заявляется. AudioDirector/native capture/10 deaths/restarts проверяет integration/runtime, этот отчёт не заменяет их evidence.

## Композиция и источники

Создан `LAST_SKUF_DEMO`: 144 BPM, 4/4, 8 тактов, 48 kHz, ровно 640000 стереофреймов (13⅓ s). D minor, A-dominant turnaround; форма AABA по два такта. Тяжёлый смещённый басовый рисунок, настоящий моносаб и затухающий гармонический корпус; Dm/B♭ → Gm/A7 → Dm/A7, answering lead, стереотекстура, swing hats, kick pickups и tom fills. Ноты/ритм/гармония редактируются в `assets/source_audio/last_skuf_demo/composition.json`; локальный синтез полностью воспроизводится `render.py`. Это описание авторского замысла, а не оценка услышанного качества.

Доставлены 4 отдельных 24-bit PCM WAV stem, unity master WAV, 4 runtime Vorbis OGG; 18 самостоятельных synthesized SFX с WAV source/OGG runtime. Manifest `game/assets/audio/manifest.json` имеет `schema:1`, заданные 4 профиля, все canonical minimum IDs и согласованные runtime aliases. Два distinct `speech_yakuza_*` — короткие низкие непроизносимые синтезаторные сигналы, без реальных голосов и speech model. Синхронность 4 stems сохраняется; эффекты delay переносят хвост через границу цикла.

Внешние звуки, recordings, sample packs, мелодии Hotline Miami, модели реальных голосов, приватные фото и paid APIs не использованы. Python/NumPy/FFmpeg служат инструментами, внешние медиа не копируются. Dependencies установлены только в temporary user-local venv, без sudo/покупок. Строки для основного licensing CSV подготовлены в `audio_license_rows.csv`; автор не редактировал общий CSV. Публичная публикация этим asset delivery не выполняется.

## Доказательства технической проверки

Команды: `/tmp/ayay-p03-audio/bin/python assets/source_audio/last_skuf_demo/render.py` и затем `verify.py`; оба exit 0. FFmpeg n9.0.1, Python 3.14.7, NumPy 2.3.5. `verify.py` проверяет metadata FFprobe до декодирования и отдельно анализирует фактические runtime OGG, а не только исходники.

| Проверка | Измеренный результат |
|---|---|
| Все 4 source WAV и декодированные runtime OGG | stereo / 48000 Hz / ровно 640000 frames |
| Sample clipping | 0 в источниках, runtime, state mixes |
| Runtime EXPLORE / SUSPICION peak | −13.9943 / −8.1962 dBFS |
| Runtime COMBAT / CLEAR peak | −4.2443 / −15.8564 dBFS |
| Runtime all stems unity peak | −4.2598 dBFS |
| 101 interpolation positions для каждой пары состояний | max −4.2443 dBFS, clipping 0 |
| Decoded seam step bass / texture | −70.4747 / −55.8029 dBFS |
| Decoded seam step drums / lead | −60.7256 / −55.2523 dBFS |
| COMBAT PCM FFmpeg EBU R128 | −16.6 LUFS integrated, −4.4 dBTP |

Величины seam step ниже максимального внутреннего sample step каждого stem. Это численный индикатор, **не** заявление «стык не слышен». Дополнительный headroom предусмотрен для SFX; сумма нескольких runtime voices требует ограничения полифонии/выходного headroom в AudioDirector. OGG может слегка увеличить sample peak относительно WAV, что учтено измерениями. One-shot Vorbis может иметь decoder padding; длительности всех коротких runtime cues измерены и остаются меньше 2 s.

Подробности: `audio_metrics.json`, `audio_inventory.json` с SHA-256, `audio_loudness_ffmpeg.log`. Не утверждается native Windows listening или перцептивная оценка микса.

## Файлы для listening

`audio_preview_combat.mp3` (13.33 s), `audio_preview_explore.mp3`, `audio_preview_suspicion.mp3`, `audio_preview_clear.mp3` — полные профили, рядом 24-bit WAV. `audio_preview_combat_runtime_twice.wav` (26.67 s) — именно два повторения декодированных runtime OGG, граница на 13⅓ s. `audio_preview_adaptive_8states.mp3` (26.67 s) — последовательность EXPLORE→SUSPICION→COMBAT→CLEAR→COMBAT→EXPLORE→COMBAT→CLEAR, смена каждые два такта с 120 ms interpolation. Это авторская production demonstration, не Godot capture. `audio_preview_sfx.mp3` (11.3 s) содержит по одному cue с шагом 0.6 s, IDs/таймкоды в `audio_preview_sfx_cues.json`.

## Конкретное ограничение listening

Root действительно передал `audio_preview_combat.mp3` через audio input. Ответ инструмента: `audio content omitted because you do not support audio input`. В контексте audio author также нет exposed listening/perception tool. Наличие ffplay/paplay, exit 0, waveform и LUFS не являются прослушиванием. Никто из авторов не выдаёт их за слуховую проверку.

`audio_listening_capability.json` сохраняет этот эксперимент. Требуется человеческая проверка реальных previews и native Godot capture: характер/развитие музыки, стык двух циклов, ясность SFX и bleeps, crossfades/ducking и серия death/retry. До этого AU-01 listening остаётся scoped BLOCKED. Интеграция и объективные проверки продолжаются независимо.
