# C01 — индивидуальные звуки добиваний, принятый прототип

**Независимый Lead031cc8c1 и QA02eed5a827: PASS_COMPONENT на0dd1cc4.** 20новых cues+5legacy, реальный source/Input/voice/PCM/DEV08 proof; owner prototype listening сохранён отдельно. FullP06/C09/readiness/merge не приняты. Дальше — сохранённая история реализации и исправлений, а не текущие открытые аудиоблокеры.

20 новых оригинальных math/DSP monoPCM WAV воспроизводимы из render.py; независимый offline signal audit c69fe500 PASS_SIGNAL_ONLY. Все файлы source/runtime byte-exact; прежние5 Якудзы не изменены. Габар3/Олег3/ТимкаPrime3/Рыжик3/Тега3/Паша5; present/sharp-firearmTimka не получают grant. Приёмка звучания новых cues не выполнена.

Изменяется только cue в копии принятого combat profile; все damage/equipment/timing поля сохраняются. CharacterFinisherAudio проверяет маршруты и отказывает при повреждении пакета. AudioDirector загружает реальные WAV, проверяет loop/duration и отклоняет collision нового cue с прежними registry. Последнее исправляет независимый static finding C01-P01 из preflight29a002f0; до исполнения probe closure не заявляется.

Добавлены strict source/recipe/registry SHA bindings к immutable independent decision/freeze, импортированные stream tests и actual Input replay20новых×Full/Reduced+5legacy. Replay должен снять native mixer PCM gameplay/solo/stress, привязать stream/voice/bus/gain/pose/physics tick и cancellation/reset/death/revoke к настоящему Core. Это пока код кандидата, не выполненные тесты. Headless не объявляется mixer evidence.

DEV06 не изменена; owner «протестил все окей» сохранён в owner-preview-20261115-06/owner-feedback.json, это не приёмка новых SFX. C09NPCmatrix/fullP06/realperformance/export/Lead/CI/readiness/P07 остаются отдельными gates.

## Доказанный C01-Q03, обязательный headroom fix

Независимый actual PCM audit обнаружил stress truepeak+0.1dBTP при samplepeak−1dBFS/0PCMrails; normal−9.4/solo−5.9 прошли. Старый WAV56cce2cb и FAIL сохранены. Это настоящий signal finding, не утверждение о слышимом качестве.

Master limiter threshold/ceiling сдвинуты вместе на−2dB (−5/−3 вместо−3/−1), сохраняя прежний makeup+2dB; источники, cue gain, music profiles и clocks не меняются. Обоснование параметров: [Godot limiter implementation](https://raw.githubusercontent.com/godotengine/godot/4.7-stable/servers/audio/effects/audio_effect_limiter.cpp), [официальный класс](https://docs.godotengine.org/en/stable/classes/class_audioeffectlimiter.html). Предел sample peaks не доказывает truepeak headroom: нужна свежая реальная PCM запись и независимый анализ.

Targeted native replay нового Master:3реальныхInput FIN (Габар/ТимкаPrime/Паша),20solo cues,8stress12voicebursts. Это целевой повтор изменённого mixer graph, не замена прежнего45route regression и не новое утверждение о пройденных тестах до запуска. Owner artistic acceptance привязана к предыдущим услышанным solo/gameplay файлам; новый stress им явно не прослушивался.

Итог headroom: реальная fresh stress запись−1.7dBTP/0rails,199PCM+49export проверок.20 aligned old/new solo stereo segments byte-exact; perceived/artistic оценка — только фактически заявленное прослушивание владельца старых solo/gameplay для прототипа. Все независимые FAIL и source-equivalence сохранены. DEV08 Linux81/Wine72; нативная Windows/FPS/input hardware latency не проверены.
