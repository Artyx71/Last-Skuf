# P03 — техническая проверка сборок и воспроизведения

Исполнитель build QA; независимый Lead gate и художественное/слуховое утверждение этим отчётом не присваиваются.

**Результат: 57/57 технических checks PASS; 24 запусков команд.** Native и экспортированные Linux/Wine runtime выполнили реальный dialogue replay: actual InputEventAction, scene finished, exit action ровно один, 10 реальных смертей/retry, один AudioStreamSynchronized player / один start четырёх stems, ноль активных SFX в конце. Проверены actual mixer clock, четыре profile commits, beat/bar scheduling, PNG framebuffer и PCM16 AudioEffectRecord waveform. Полная regression suite выполняется Root отдельно.

Воспроизведение на замороженных `game/` source: `native_source_hashes.json` и `export_source_hashes.json` совпадают для 135 файлов; before/after checks PASS. Runtime commit `a2c09cb`, assets `d99c501`; точный tool/source inventory имеет приоритет над краткими commit labels.

| Actual replay | Driver | Clock, s | Capture Hz | WAV, s | Peak |
|---|---|---:|---:|---:|---:|
| `native_replay` | PulseAudio | 20.471 | 44100 | 20.352 | 0.5680 |
| `export_linux_replay` | PulseAudio | 20.489 | 44100 | 20.376 | 0.5915 |
| `export_windows_replay` | WASAPI | 20.484 | 48000 | 20.352 | 0.5130 |
| `native_movie_replay` | Dummy | 20.500 | 48000 | 20.427 | 0.5168 |
| `native_movie_replay_reduced_motion_vhs_off` | Dummy | 20.504 | 48000 | 20.427 | 0.5168 |

В каждой WAV capture ненулевой RMS, stereo PCM16, длительность более 18 s, full-scale clipping samples = 0. Источники имеют 48000 Hz; actual realtime Linux mix — 44100 Hz, Wine WASAPI — 48000 Hz. Показатели waveform не подтверждают слуховой баланс, отсутствие слышимых pops или художественное качество.

`dialogue_audio_replay.mp4` и `dialogue_audio_replay_reduced_motion_vhs_off.mp4`: actual native Godot MovieMaker, fixed 60 FPS, 1280×720, 20.65 s, audio AAC 48000 Hz/stereo. MovieMaker использует offline Dummy driver с фактическим mixer clock/events и отдельным AudioEffectRecord WAV; он не выдан за realtime-driver playback или прослушивание. Второе видео загружает настоящие schema1 options `reduced_motion=true`, `vhs=false` через изолированный preference path. Metadata: `movie_metadata.json`.

Native screenshots: `native_dialogue.png`, `native_options.png`, `native_large_text.png`, `native_reduced_motion_vhs_off.png`. Options/large/default сняты также из каждого свежего Linux и Windows/Wine executable (`export_*`). Все PNG — framebuffer 640×360; large capture использует самую длинную реплику на 1.25 text scale. Исполнитель визуально проверил options/large/reduced и Wine large: controls/text внутри viewport, две строки самой длинной реплики без обрезки. Независимая визуальная оценка принадлежит Art reviewer.

`weapon_poses/weapon_captures.json`: 16 actual input/draw captures, melee phases 0/1/2 × down/left/right/up + fire × четыре направления. Fixture проверил actual action_kind/action_frame/action_timer перед каждым PNG. Дополнительно сохранены defeat fade/cue/cleared и HUD upper-edge samples. P01 PNG не менялись исполнителем QA.

Свежие executables (не старые P02 builds):

- `build/P03/linux/last-skuf.x86_64` — 74705136 bytes, SHA256 `a45d188c94d01eb8c01c7486a95abff180b3e73d1e8d19f8cb4eee5a65276e5c`.
- `build/P03/windows/last-skuf.exe` — 110454208 bytes, SHA256 `5dda956143ef3f4f713e6569332fcb67228a7ba1b726a0b83f560b823f0d0702`.

Windows exe реально запущен через локальный Wine 11.17 на Linux: bootstrap, --open-dialogue, options, large и полный replay. Все Wine preferences/save/PNG/result/WAV paths имеют `Z:` форму. Native Windows host отсутствует: **NOT_TESTED_UNAVAILABLE**.

В финальных используемых runtime logs нет SCRIPT ERROR/ERROR/FAIL и ObjectDB leaks. Wine rendered startup сообщает MESA-EGL fallback warnings (`driver (null)` / DRI2) и warning об SDR white level виртуального adapter; actual framebuffer, replay clock и sound capture работают. Это ограничение совместимости Wine, не заявление о проверке native Windows HDR. Диагностические `diagnostic_abrupt_{linux,windows}_quit.log` сохранены отдельно: искусственный engine `--headless --quit` обходил app shutdown и сообщал два ObjectDB leaks. Финальный smoke заменён более содержательным actual bootstrap capture с normal runtime_shutdown и PNG check; он clean по leaks. Подробности: `technical_log_scan.json`.

Команды воспроизведения:

```sh
python tools/verify_p03.py --no-exports --movie
python tools/verify_p03.py --snapshots-only
python tools/verify_p03.py --exports-only
```

Pin/hash engine проверяется по `tools/toolchain.lock.json`. Все captures используют отдельные `AYAY_OPTIONS_PATH`/`AYAY_DIALOGUE_SAVE_PATH`; tool логирует capture environment, exit status и error scan. `technical_validation.json`, `technical_log_scan.json`, `exports.json` и `technical_artifacts.json` содержат конкретные acceptance/paths/hashes.

**Scoped BLOCKED: человеческое прослушивание.** Доступный audio input не поддерживается (empirical `audio content omitted because you do not support audio input`, evidence `audio_listening_capability.json`). WAV/video не объявлены прослушанными. Финальный P03 gate, независимый review и CI принадлежат Root/назначенным reviewer; этот отчёт их не заменяет.
