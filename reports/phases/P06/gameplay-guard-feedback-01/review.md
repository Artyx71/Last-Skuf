# Независимый Gameplay Review: окно парирования Олежки

Решение: **PASS_COMPONENT** для читаемости существующей контратаки Олежки в training sandbox. Проверенный frozen HEAD: `f844e4d3cb2c5a7d851337fdf49a00bf51c67b6c`. Автор реализации и reviewer — разные агенты; reviewer не изменял игровой код, WORK, controller, очередь или каноническое состояние.

Область: читаемое окно/направление/результат блока и его согласованность с уже существующим pre-damage melee parry, в пределах P06-CBT-02 и раздела «Ограниченная контратака Олежки». Это не full P06, seven-hero combat, readiness, P07, merge, export, native Windows, FPS или художественная аудиоприёмка.

## Код и неизменность механики

Непосредственно прочитаны production actor/Core/HUD/CharacterLab, replay helpers, новый replay и verifier. Сравнение с `git show ec6d470:game/scripts/actors/character_player.gd` сохранено вместе с diff. Предикат вынесен без изменения границ: action clock 0,06–0,26 с включительно; action frame0, живой Олежка, действующая authority, один расходуемый блок. 0,28 windup / 0,10 active / 0,34 recovery / cooldown2 с сохранены. Успешное парирование по-прежнему переводит action clock в authored contact; оно не ждёт остаток windup.

Защита остаётся только для настоящего enemy melee unarmed/blunt/sharp, distance1–40, frontal dot>=0,65 и LOS. Core резервирует incoming once-token до hook; defended event возвращается до damage/score/blood path. Ответ идёт отдельной Core melee job с damage1/stun0,45/reach21/radius14 и повторной authority-проверкой. Пули, finisher/legacy direct contacts, задние/боковые и внеоконные удары не получают иммунитет.

`counter_feedback()` возвращает свежий read-only snapshot; UI не принимает Input и не меняет clocks, cooldown, damage или receipts. Process priority100 отображает текущий результат физики, observer1000 читает уже обработанный HUD. HUD скрывается у Габара; сброс очищает stale selection warning. Все записанные source hashes сверены с файлами WORK: расхождений нет. От regression01 изменены только CharacterLab, HUD и новый feedback replay; actor/Core/config/assets с того прогона неизменны.

## Фактические игровые материалы

Проверены фактические result/контакты/наблюдения, логи и code paths, а не только author summary. В report помещены переносимые копии evidence и исходников. Повторных engine-прогонов reviewer не выполнял. Независимая обработка данных и 33 artifact hash-проверки сохранены в `factual-proofs.json`; 0 расхождений.

- headless03:57/57,269 наблюдений; native03 live:78/78,274 наблюдения и21 viewport PNG; MovieMaker:57/57,269 наблюдений.
- Во всех812 наблюдениях displayed snapshot равен текущей модели. Независимая проверка каждого зелёного guard требует живого игрока, special/frame0, blocks0, actual window и clock внутри0,06–0,26. Ошибочных зелёных состояний нет.
- Native miss: подготовка tick19/clock0; guard tick23/0,0667; последний guard clock0,25; closed tick35/0,2667; recovery tick42/0,3833; cooldown tick63; ready tick140. Зелёное окно занимает12 физических тиков (200 мс). Границы0,06/0,26 не совпадают с сеткой60Hz: включительность доказана кодом, дискретные adjacent-boundary проверки164-case replay сохранены отдельно.
- Настоящие frontal parry в down/left/right/up: native defense ticks148/162/176/190, отдельные counter contacts149/163/177/191. На defense tick HUD уже «БЛОК! · ОТВЕТНЫЙ УДАР», health1/blocks1/damage0. На следующем tick ровно damage1 по NPC при authored contact frame1/clock0,2967. Score не начисляется. Это не прямой damage callback.
- Native early fatal contact tick210: health0,blocks0; только incoming lethal receipt, ответ отсутствует. R возвращает ready и чистое состояние. C немедленно убирает guard и сохраняет cooldown. Пауза держит clock0,0667/cooldown1,9333 и показывает «ПАУЗА»; продолжение возвращает то же окно. Revocation даёт unavailable, reselect восстанавливает ready. Неготовый выбор сохраняет Олежку с предупреждением; R очищает предупреждение.
- Full/Reduced и flash/shake/VHS варианты сохраняют информацию и одинаковые механические результаты. 100 чтений/мутаций возвращённых snapshots не меняют gameplay state; reset оставляет одну панель, scene exit её освобождает.

Прочитаны результаты и фактические receipts прежнего regression01: Олежка164/164, Габар124/124; все11 команд завершились успешно. Олежка покрывает miss/early/late/rear/side/projectile/wrong-category/range/friendly/wall, cancel/revoke/reopen/reset, once-token, второй одновременный incoming contact и revoke после parry. Второй удар может убить и отменить pending ответ — ложной общей неуязвимости нет. Эти old regression результаты относятся к неизменному combat body, а не к финальной геометрии HUD. Последняя геометрия проверена03; финальные restart68/readiness56/isolation25+fresh process reload также представлены и прочитаны.

## Визуальная читаемость и временная связь

Непосредственно осмотрены все21 native03 PNG и старый native01 guard. Фазы обозначены русским текстом и различимым цветом: подготовка, открытый frontal block, успешный блок/ответ, закрытие, восстановление, численный cooldown, пауза, смерть, unavailable. Подсказка F объясняет блок спереди; текст не требует угадывать значение цвета. Цветная полоса убывает по тому же clock, отдельного UI-таймера нет. Панель наверху справа не закрывает бой; actual bar rect во всех видимых наблюдениях [350,50,274,5], низ55 выше playarena y62. Текст помещается в отведённую ширину.

Native01 действительно имел27px theme-minimum полосу, перекрывавшую арену; его прежний зелёный test summary не является приёмкой этой геометрии. Исторический screenshot/result сохранён. В03 визуально подтверждена тонкая5px полоса, и тест проверяет уже actual rect.

Скопирован настоящий MP41280×720,60fps,286 кадров/4,7667 с. FFmpeg извлёк13 немодифицированных кадров с указанными frame index/PTS; непосредственно осмотрены кадры20 (guard),26 (closed),165 (counter) и214 (pause). Вместе с непрерывными269 movie observations и actual contact ticks это подтверждает temporal presentation; отдельные reset screenshots сами по себе переходами не считаются.

## Границы вывода

Fixture задаёт placements/aim/health и приостанавливает AI; атаки запускаются через production Core с реальным collision dispatch, F/C/R/O/выбор — через scripted Input. Это доказательство объективного окна, контактов и HUD; аппаратная keyboard latency, субъективная реакция человека, естественная сложность боя и художественное звучание не измерялись. Fixed60 MovieMaker не доказывает live FPS. Новые аудио/растры/clips этим изменением не принимаются. Открытых gameplay-дефектов внутри проверенного компонента нет; remediation tickets не требуются.
