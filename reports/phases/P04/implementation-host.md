# P04 — актуальный кандидат после восстановления

Первая глава CH01_THE_MISSED_FIGHT: слабый Якудза забирает куртку с ключом, уходит через служебку, отвечает Жиньке/Эллане и выходит во двор без убийств. Драка остаётся за закрытой дверью. Реальные стены/двери/предметы, external dialogue, checkpoint/retry, отдельное versioned сохранение и exactly-once завершение интегрированы в прежний CombatSystem/AI/AudioDirector. Новые finishers/gore и остальные20глав здесь не заявляются: P04G остаётся обязательной следующей подфазой до P07.

Карта1152×640 и sprites tiles/props/doors/world нарисованы оригинальным целочисленным pixel recipe Pillow, ограниченная палитра32цвета; image_gen для этого набора не вызывался. Исходники/provenance в assets/source_art/missed_fight/. Портрет и движения Якудзы/три AI используются из принятых фаз. Новый оригинальный score MISSED_FIGHT_BACK_DOOR: E minor,144BPM,8тактов,4stems48k и doorSFX; настоящие WAV masters/recipe/provenance в assets/source_audio/missed_fight/. Никаких rawphotos/чужих samples/клонирования реальных голосов.

## Последние доказательства

- native-host-03/validation.json:24/24. Source engine и reduced mode, MovieMaker, Linux ELF и WindowsPE под Wine; каждый actualInput/AI replay59checks,10реальных смертей,9PNG,0kills,oncecompletion. Результаты/PCM/source hashes/видео в attempt1/native-host-03/. Обычные устройства PulseAudio/WASAPI; MovieMaker честно Dummy.
- native-host-03/audio_detailed.json:33/33.11реальных игровых/source файлов,5профилей включаяUNITY,12направленных переходов на3ритмических offsets,5actualruntimePCM. Декодирование,длительность,LUFS/truepeak,DC,клиппинг,тишина,loopjoins и переходные окна. Числа не означают оценки музыкального качества. Привязка событий к PCM приблизительная, не акустическая sample-accurate latency.
- reports/autopilot/P04/human_listening.json: фактический ответ владельца «Прослушал микс и профили, принимаю для прототипа P04», hashes67s игрового микса native-host-02 и четырёх профилей. Те же OGG и AudioDirector используются сейчас. Независимому Lead нужно проверить это свидетельство; автор не прослушивал музыку и не утверждает качество финального mastering.
- input-recovery/python-tests.log:62/62 Python. Включены реальные Git dirty/index/branch/race/zeroPOST проверки и настоящая Godot fault injection: неожиданный idleInput → немедленный FAIL после1подтверждённой смерти, без9выдуманных retry.
- Отдельный фактический PulseAudio monitor только проверенного ELF процесса: attempt1/host-recovery/pulse-godot-only.{wav,json},18s,не microphone/другие приложения; scope сигнала.
- Финальная regression suite:19/19 в attempt1/regression-host-final/;815unitassertions + два50-check normal/accelerated mission replays. Обычный headless выход теперь clean; stale failure сохранён отдельно.

## Исправления после честно сохранённых FAIL

Первые178некоммитнутых файлов сохранены и независимо проверены: recovery/decision.json разрешает только локальное продолжение attempt1, неphasePASS. Host создал атомарные commits; sandbox author теперь получает write allowance только к общему Git каталогу того же repo. Фактический probe создал/удалил безвредный ref без смены HEAD; read-only reviewer этого allowance не получает.

REC-PUB-01: publication блокирует staged changes и незафиксированные source/untracked deliverables, повторно проверяет ветку/HEAD после privacy и пушит проверенный objectID. Обычные generatedreports могут остаться unstaged. No force/admin/protection bypass.

REC-QA-01: обычный source-headless replay воспроизвёл2synchronizedAudio leaks; ускоренный replay —40Objects/14resources. RuntimeShutdown теперь ждёт монотонное реальное время, продолжая main frames для освобождения async mixer references. Игровые retry/урон/AI не менялись. Старые логи/ошибки сохранены. CI/verify запускают нормальный и accelerated full mission exit; игровые smokes используют штатный выход вместо raw--quit.

native-host-02 Windows обнаружил сорванное idle-предусловие harness: персонаж ушёл к телефону и9строк переиспользовали старую latency. Отдельный read-only QA подтвердил этот дефект доказательств; физическое нажатие/боевой дефект не доказаны. Исправлен только harness: release движения на всех выходах, completedphysics observation в idle, trace commanded/observedInput/positions/ticks, abort при нарушении, обязательна новая смерть. В native-host-03 Windows заново прошёл10отдельных циклов с trace. Никаких actorwarps/изменения AI или времени продукта.

## Пределы и следующий gate

Native Windows недоступен; PE реально запускался под Wine. Engine frame delta соответствует60Hz на GTX1050Ti/X11, это не независимый аппаратный benchmark или P04G stress-test. frame_timings.movie_maker возвращаетfalse даже в записанном --write-movie запуске; реальный AVI→MP4 и кадры/команда являются доказательством записи, поле не используется для PASS. PrivateTimka manifest drift по-прежнему отдельно блокирует P06 reference use. Постоянного daemon нет.

Это отчёт исполнителя, не независимое принятие. Публикация требует отдельного закрытия recovery publication blocker; merge — independent exacthead/base PASS и обязательный CI без обхода GitHub approvals. После confirmedsquash и сохранения delivery state — P04G через существующий контроллер, не второй runner. Исторический implementation.md/attempt1 failures остаются неизменны; текущая authoritative state — automation/phase_state.json основного checkout.
