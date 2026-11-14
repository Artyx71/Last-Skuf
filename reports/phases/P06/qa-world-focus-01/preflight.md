# P06 Timka WORLD — QA source preflight диагностики фокуса

Изменение fixture допускает новый отдельный frozen native прогон. Оно не ослабляет существующие проверки и не принимает неудачный native01. Полная P06, поведение фокуса и native02 пока не приняты.

Проверен before-файл с SHA из native01 source inventory и точный diff к current fixture. Все четыре изменения — вставки. Весь PreviewActor (physics/velocity/анимация), функции key/frames/record, все grid/continuous сценарии, distance/phasecoverage assertions и failure/shutdown логика совпадают побайтно. Добавлены только записи фактического Engine Input/Shift и Window focus, а также запрос FLAG_NO_FOCUS исключительно для native MovieMaker до отправки scripted key events. Live-ветка флаг не запрашивает. Новых повторных keypress/input reassertions, исключений из FAIL или подавления ошибок нет.

Оба авторских headless прогона70/70 прочитаны вместе с artifactSHA. У каждого672/672 samples соответствуют ожидаемому Inputvector/Shift. Это реальный Godot Input.parse_input_event, не физическая OS-клавиатура. В headless ветке native-флаг не исполняется: первый прогон содержит только диагностику, второй movie_window_no_focus_requested=false. Поэтому эти прогоны не подтверждают работу no-focus на X11; это проверит только новый frozen native02.

Неудача01 сохранена: live110/110 и40PNG; MovieMaker67/70, FAIL movement:walk_down и две недостающие фазы. В первых36walk samples —6walk_down и30idle_down, physics ticks58–93; с tick64 velocity0. Реальный AVI независимо проверен ffprobe:750/750 кадров,60FPS,12.5s. Receipt/logSHA корректны, exit1; validation passed=false. В Godot log нет пароля/auth ошибки. Источник внешнего отпускания Input неизвестен, связь с закрытым владельцем неизвестным passwordwindow не доказана.

Существующий порог movement>50 и phasecoverage остались прежними; новая диагностика сама по себе не является новым gate «ни одного потерянного sample». Дляnative02 QA проверит фактические Input samples, фокус, неизменность failed01 и все прежние assertions. Никаких выводов о gameplay/manual focus, ART, аудио, exports, FPS производительности или PASS P06.
