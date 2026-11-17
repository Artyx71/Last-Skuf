C01 — контракт исходных finisher cue candidates, не приёмка игрового аудио

Текущий пакет содержит двадцать реальных dry single-shot WAV. Source topology должна соответствовать фактическому catalog: Gabar3/Oleg3/TimkaPrime3/Ryzhik3/Tega3/Pasha5. TimkaPresent не получает cue или prime capability; TimkaPrime не получает sharp/firearm. Пять существующих finish_* Yakuza остаются теми же файлами и маршрутами. Число различных SHA служит проверкой идентичности файлов, а не доказательством двадцати воспринимаемо различных звуков.

Offline source acceptance проверяет actual PCM decode и независимое FFmpeg float decode, 44100/mono/PCM16, длину, энергию/RMS/DC, оба PCM rails, тишину/dropout, quiet endpoints/release, sample peak, собственную 8× windowed-sinc true-peak estimate и FFmpeg true peak. Short-cue integrated LUFS записывается только информационно; music loudness target не применяется к импульсам 0.21–0.31s. Signal pass не гарантирует отсутствие клиппинга суммарного микса.

Для сравнения профилей сохраняются реальные STFT/log-band spectra, absolute/time-normalized RMS envelopes, energy-time quantiles и все same-category crosshero distances. Recipe проверяется на разные temporal/cloth profiles, а не лишь label/seed/gain/pitch. Близкие descriptors — приоритет фактического прослушивания, а не автоматическое доказательство одинакового либо качественного звучания. Любая оценка приятности, узнаваемости оружия/героя, характера/музыкального качества требует реального listening evidence. Текущий инструментальный контекст не содержит инструмента прослушивания; статус ARTISTIC_NOT_LISTENED остаётся честным ограничением.

До runtime acceptance обязательны фактическая Godot integration и отдельный serialized engine/mixer QA:

1. Для каждого из20 разрешённых actor/context/category routes реальный input→earned vulnerability→finisher contact выбирает правильный новый stream. Логировать pinned actor/context/category, cue/path/stream SHA, epoch/id, contact tick и фактический AudioStream playback; не ограничиваться названиями файлов.
2. Связать запуск cue с тем же настоящим contact event/pose, который зарегистрировал урон. Отмена до contact, смерть/revoke/reset/замена source не дают поздний старый cue; одно добивание не запускает повторный voice и не меняет once-damage/score/cost.
3. TimkaPresent V остаётся denied с0новыхfinisher cues; исключённые категории/контексты также denied. Базовые5Yakuza finish cues проигрывают прежние streams/SHA. Новые routed cues не должны глобально переназначить legacy names.
4. Проверить реальные Godot imported stream parameters: ожидаемые samples/channels/rate/duration, loop disabled, нужный SFX bus/gain; recipe manifest gain не считается уже применённым engine gain.
5. Снять действительный mixer PCM для solo cues и предусмотренного игрового стресса с музыкой/одновременными SFX. Повторить decoded RMS/DC/rails/true-peak/silence checks, проверить слышимость cue инструментально по event windows и stream binding. Wave-source pass не гарантирует безопасную сумму voices.
6. Проверить export filtering и фактическое наличие/загрузку всех новых streams в Linux и Windows-PE там, где доступны реальные проверки; Wine не объявлять native Windows. Нативные playback/mixer проверки не подменять offline metadata.

Новые cues — single shots: loop join и music-state transition для них N/A. Прежние music loop/adaptive transition gates сохраняются; этот source audit их не переоценивает и не закрывает. Hardware latency/FPS, художественный listening и полная P06/P07/readiness/merge остаются отдельными gates.

Исполнитель source audit не меняет Game/candidates/recipe/Git/Controller. Для воспроизводимости допускается только byte-exact копия проверенного чистого math recipe и повторный вывод20WAV в новую QA-папку; это проверка происхождения, не новая production-итерация. Кандидаты, каталог, рецепт и legacy5 должны сохранить исходные hashes после job.
