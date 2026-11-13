# P03 — runtime handoff (implementation, not independent gate)

Статус: реализован ограниченный диалоговый/аудио полигон; независимый review и человеческое прослушивание обязательны отдельно. Новая миссия, кампания, полное озвучивание, новые лица и gore-пак не заявлены.

## Реализация

- `game/resources/dialogue/yakuza_phone.json`: пять оригинальных коротких русских реплик только Якудзы, neutral/angry, телефонная подпись «ЖИНЬКА», стабильные scene/event/line/speaker/emotion/localization IDs, один реальный persistent flag. Выборов с фиктивными последствиями нет.
- `DialogueDirector`: внешняя проверяемая JSON-сцена; посимвольное раскрытие с паузами на пунктуации, Space раскрывает/продвигает, Shift ускоряет в пять раз, instant text, журнал H, разрешённый только после просмотра skip K. Автосохранение/восстановление строки, прогресса, истории, seen-state и once-only event ledger. Атомарная замена save-файла через `.tmp`; ошибка записи откатывает завершение/последствия. Повторный запуск/skip не повторяет exit action.
- `res://scenes/world/dialogue_audio_lab.tscn`: существующий native combat world остаётся видимым, его физика приостановлена для постановки диалога. Большой original pixel portrait; реальный `portrait_motion.png` используется как 3×2-sheet, mouth/rest и blink берутся из разных клеток. FPS/интервал/длительность blink читаются из atlas metadata. Сниженное движение показывает rest-frame. Отсутствие motion asset отражается как false и не выдаётся за готовую анимацию.
- VHS ограничен линиями с малой opacity над областью мира. Caption/textbox находятся выше него; текст не искажается. Опции VHS/reduced motion работают независимо.
- `OptionsStore`: schema1 с атомарным сохранением Master/Music/SFX/Voice-UI, text speed, instant text, text scale, VHS, reduced motion, reduced impact, optional sound captions. Базовая реплика всегда видна: bleep-only речь не заменяет её смысл. «Подписи звуков» скрывают только дополнительную подпись телефона/вызова.
- `AudioDirector`: actual manifest/stems/SFX, `AudioStreamSynchronized` из четырёх stems с единым mixer timeline; OGG loop включён явно, музыкальный контейнер не пересоздаётся при смерти/повторе. Реальный clock берётся из playback_position + time_since_last_mix с учётом wrap. COMBAT назначается на следующий beat; менее интенсивные изменения — на bar. Gain ramps, dialogue duck, pause/cutscene duck, death/retry lifecycle. Бусы Master, Music, Music_Ambience→Music, SFX, SFX_UI, Speech_Cues; Voice-UI управляет двумя последними. На Master установлен limiter.
- Типизированный сигнал `combat_lab.audio_event(event_id: StringName, at: Vector2)` соединён с AudioDirector; hooks только в точках шагов, оружия, попадания, AI alert/telegraph, смерти/retry/exit. Музыкальные состояния не опрашивают игровой RNG. Шаги различают concrete/metal; round-robin двух вариантов принадлежит AudioDirector. Пространственные SFX имеют attenuation, UI/bleeps не пространственные. Общая граница 12 голосов, throttling; при перегрузке новый cue пропускается, уже звучащий tail не обрезается. Reduced impact уменьшает SFX на 5 dB.
- `runtime_shutdown.gd`: общий shutdown/unset-streams + 50 ms startup + 150 ms mixer drain перед quit. Исправляет воспроизводимые асинхронные AudioStreamPlayback leaks при быстром завершении Dummy/native driver; после shutdown поздние события игнорируются. В старых `*_test.gd` изменён только terminal teardown; assertions и fixtures сохранены.

## API и воспроизведение

Autoloads `/root/OptionsStore`, `/root/AudioDirector`, `/root/DialogueDirector`.

Audio API: `request_state(StringName)`, `dialogue_active(bool)`, `on_gameplay_audio(StringName,Vector2)`, `play_cue`, `variant`, `bleep`, `reset_for_retry`, `diagnostics`, `begin_capture`, `end_capture(path)`, `shutdown`.

Lab CLI: `--capture-dialogue`, `--p03-replay`; дополнительные capture fixtures `--capture-options` и `--capture-large-text` используются вместе с `--capture-dialogue`. Root bootstrap предоставляет переход `--open-dialogue`/F3.

Переменные:

- `AYAY_OPTIONS_PATH`, `AYAY_DIALOGUE_SAVE_PATH`: отдельные пути preferences/save для tests/captures.
- `AYAY_CAPTURE_PATH`: PNG framebuffer.
- `AYAY_P03_RESULT_PATH`: JSON replay result.
- `AYAY_P03_AUDIO_PATH`: WAV с фактического Master bus через AudioEffectRecord.

Для штатного завершения других runtime capture/replay fixtures: `preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), code)`; в SceneTree-test передать `self`.

## Проверка исполнителя

Pinned engine `.tools/godot/Godot_v4.7.2-stable_linux.x86_64`. Новые checks:

| Script | Passed | Failed |
|---|---:|---:|
| `game/tests/options_test.gd` | 26 | 0 |
| `game/tests/dialogue_test.gd` | 44 | 0 |
| `game/tests/audio_test.gd` | 45 | 0 |

Всего 115 assertions; exit0; финальные logs `.tools/p03-runtime/{options,dialogue,audio}-final.log` без WARNING/ERROR. Dialogue tests включают native InputEventAction Space/H/O, actual slider, ошибку записи и rollback, once-only restore/replay, caption accessibility и размеры всех пяти реплик при 1.25. Audio scheduler unit test использует явный test clock; реальная проверка mixer clock — отдельный native replay. Audio tests проверяют неизменность полного combat snapshot/RNG от audio events и десять lethal damage/retry lifecycle.

Native desktop captures просмотрены исполнителем на framebuffer 640×360:

- `.tools/p03-runtime/dialogue-native.png`: readable first line, original portrait, world behind.
- `.tools/p03-runtime/options-native.png`: все sliders/checks внутри viewport.
- `.tools/p03-runtime/dialogue-large-native.png`: самая длинная реплика при 1.25 в двух строках без обрезки; angry portrait; native quit без warnings/errors. Это последняя accessibility capture.

Нативный PulseAudio replay `.tools/p03-runtime/engine-replay.{json,wav,png,log}`: finished, exit_actions1, actual_deaths10, audio/capture codes0, one synchronized music player / stem_starts1 / active voices0 в конце. Actual mixer clock≈20.37s; SUSPICION bar28, COMBAT beat32≈13.338s, EXPLORE bar40, CLEAR bar44≈18.338s. Log без WARNING/ERROR. Воспроизведение произошло до финальных чисто accessibility/atlas-metadata/cleanup уточнений; Root делает финальные build/capture/regression evidence на frozen source.

## Ограничения gate

WAV/метрики и исполнение PulseAudio подтверждают фактическое формирование звука, но не являются прослушиванием. Возможность аудиовосприятия инструментом эмпирически отсутствует (`audio content omitted because you do not support audio input`, проверено Root). Художественный баланс, loop/transition/death-tail слуховой QA остаётся scoped human listening BLOCKED. Независимый Lead/Art review и полная старая regression suite/exports принадлежат Root; этот handoff не присваивает P03 PASS.

## Root integration correction

Final shutdown is scheduled without suspending caller coroutines. A short test could stop before the first mix and leak AudioStreamSynchronized/PlaybackSynchronized; verbose reproduction confirmed this. The helper now pauses gameplay, lets queued audio startup run for 50 ms, calls shutdown, and quits at 200 ms. Fresh verbose art test is clean. Source a2c09cb; final root regression/capture evidence is under reports/phases/P03.
