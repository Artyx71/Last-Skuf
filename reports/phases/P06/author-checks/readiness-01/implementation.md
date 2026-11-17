# P06: готовность зарегистрированного боевого контекста

Наличие полных листов и clothing sockets теперь недостаточно для выбора героя. `CharacterPlayer.prepare_fixture` сначала проверяет зарегистрированный scene key и реализованный обработчик способности; сейчас разрешены только Gabar/training/lunge и Oleg/training/counter. После проверки загружается прежний полный арт. При bind повторно сверяются точное определение сцены, actor, context и ability. Сохранённый/произвольный словарь не принимается как ScenePolicy.

`CharacterLab.select_fixture` вызывает эту подготовку до закрытия options, Core.reset, смены authority и удаления текущего игрока. Отказ сохраняет текущий бой. Новые герои, способности, компактная раскладка Тимки и исключение из SDD не добавлены; предложение владельцу остаётся pending.

Реальные проверки автора: readiness56/56; production Gabar124/124; Oleg164/164; изоляция CH01 25/25 плюс actual fresh-process reload; Godot import без ошибок. Логи и JSON лежат здесь и в соседнем readiness-regression-01. Негативный CompleteArtProbe намеренно симулирует доступность полного арта через тестовый Gabar sheet, чтобы отказ нельзя было объяснить отсутствующими PNG. Он не является production identity или доказательством готовности Паши/Теги/Тимки/Рыжика. Живой lifecycle тест использует настоящие Gabar/Oleg тела; прямые Core contact/projectile вызовы служат только созданию pending jobs/receipt, не являются доказательством Input/анимации нового оружия.

Независимый QA ещё требуется. Phase approval / merge approval: false.
