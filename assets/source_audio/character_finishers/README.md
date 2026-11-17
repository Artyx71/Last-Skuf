# Собственные finisher SFX — кандидаты P06

20реальных исходныхPCM16/mono/44100WAV и math-only recipe. Новый звук использует отдельные temporal/cloth profiles для шести героев и category resonators. Это не запись/клон голоса и не переработанный стороннийsample. TimkaPresent не имеет finisher звуков; prime получает только unarmed/blunt/environmental. Пять первоначальных Yakuza finish_* файлов сохраняются в combat_polish.

Signal-only приёмка c69fe500… основана на независимом decode/truepeak/300checks/38pairs/byte-exact rerender. Она не оценивает качество звучания и не заменяет реальный engine mix либо прослушивание. Слуховая и runtime приёмки пока не завершены. Близкие Oleg/Pasha огибающие требуют отдельного внимания слушателя; это не установленный дефект.

Воспроизведение source: python3 assets/source_audio/character_finishers/render.py --catalog game/resources/characters/catalog.json --output <новый-каталог>. Recipe не заменяет Game автоматически и запрещает перезапись предыдущего output.
