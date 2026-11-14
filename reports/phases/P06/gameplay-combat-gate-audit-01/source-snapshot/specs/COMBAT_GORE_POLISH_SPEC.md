# Combat & Gore Polish — зависимая подфаза P04G

Источник: прямое поручение владельца. Статус: P04G PASS после независимого Lead attempt3 и human prototype acceptance; сохранённый decision reviewed `9128605a6e4a715b3abd71df0124e12a860bead6`, squash PR9 `756054674383f92f67c7f5f4944c1a5ee8c384f1`. Evidence/history в reports/phases/P04G/ сохранены. Это принятие прототипа, не финальный release; character-specific расширения остальных героев требуют P06. Контракты ниже сохраняются для регрессии.

## Контракты и атомарная очередь

| ID | Работа | Зависит от | Проверяемый результат |
|---|---|---|---|
| IMP-01 | Hitstop сильного попадания, направленное отбрасывание, hurt-поза, ограниченные flash/shake | P04, CMB-P02-01 | Событие контакта и визуальная реакция на одном physics tick; лимиты длительности/интенсивности |
| IMP-02 | Звуки по оружию/поверхности, синхронные combat events | IMP-01, AU-01 | Actual capture контакта и зарегистрированного damage, отдельные audio IDs, mixer QA |
| ART-G01 | Оригинальные pixel blood spray:4направления, particles, floor/wall/clothing/decal variants | Art Bible, IMP-01 | Реальные PNG/atlas/source/palette/hash/лицензия и native кадры; случайные фигуры не считаются art |
| ART-G02 | Повреждённые портреты/реакции без изменения принятых исходников | ART-G01 | Отдельные sheets, правильные character/reference, независимый ART review |
| AI-G01 | Telegraph,attack,recovery,hurt,stun,knockdown,death,finisher reaction для patrol/rusher/shooter | P02, ART-G01 | Настоящие authored frames; native видео каждого архетипа, damage без attack-frame запрещён |
| FIN-01 | Расширяемые finisher definitions и resolver | IMP-01, AI-G01 | Eligibility: состояние/оружие/направление/дистанция/окружение; explicit enter/contact/exit/cancel |
| FIN-02 | Unarmed,blunt,sharp,firearm,environmental базовые категории | FIN-01, ART-G01 | Каждая категория имеет отдельную action/reaction анимацию, contact event, звук и результат |
| FIN-03 | Якудза: большая задержка, риск и прерываемость | FIN-02 | Не супербоец: enemy attack/потеря цели/движение/невалидное окружение отменяют разрешённые стадии |
| OPT-G01 | Full/Reduced gore,decals on/off,shake0–100%,flashes on/off,VHS on/off | IMP-01, ART-G01 | Versioned options migration; hitboxes/damage/score/story одинаковы для всех визуальных режимов |
| QA-G01 | Exactly-once damage/score,state transitions,effect lifetime/caps,frame coverage | FIN-03, OPT-G01 | Исполняемые тесты, interrupted/repeated contact/reset проверены |
| PERF-G01 | Массовые попадания/декали, повторные рестарты и native frame timings | QA-G01 | Заданный fixture workload, hardware/backend/длительность/frame percentiles; без неподтверждённых FPS заявлений |
| REV-G01 | Независимые ART/GAMEPLAY/QA и Lead | всё выше | Actual screenshots/video/assets/tests/exports/diff; PASS/FAIL/BLOCKED, immutable evidence |

## Использовать существующую архитектуру

`CombatSystem` уже владеет physics hit queries, attack IDs, active windows и projectile sweep; `CombatPlayer` — action phase/lifecycle; `EnemyActor` — AI FSM/receive_hit; `combat_lab` — encounter reset/score/audio_event; `AudioDirector` — typed cues/получение mixer evidence; `OptionsStore` — schema/persist. Расширять эти интерфейсы точечными событиями и компонентами, не создавать второй независимый damage/score engine. Authoritative contact clock из CMB-P02-01 сохраняется. Render/audio callbacks не наносят урон.

Finisher controller: `eligible → windup → contact → recovery → finished`, либо `cancelled` до контакта. Один action/attack ID, contact token и kill/score ledger исключают повтор при нескольких hitboxes, repeated animation callback, resume/load или отмене. После commit нельзя второй раз уронить/убить/начислить очки. AI-действие, hurt/stun/knockdown/death имеют явный приоритет; dead не возвращается в attack/recovery без encounter reset. Eligibility повторно проверяется в contact, environmental target — реальный зарегистрированный объект/поверхность.

Hitstop не должен пропускать или повторять physics contacts; его механизм и временной бюджет уточняются в реализации с тестами времени. Cosmetic RNG отделён от gameplay RNG. Knockback сохраняет коллизию со стенами. Camera shake ограничен суммой/клампом, уважает slider0/reduced-motion. Gore Reduced меняет только рисунок; настройки не меняют hitbox/damage/score/story. Для всей временной графики есть bounded pools и TTL, все ссылки/таймеры очищаются reset; точные caps фиксируются в resource и тестируются на максимуме.

## Стили персонажей (не выдавать за реализованные)

| Герой | Стиль и граница канона |
|---|---|
| Габар | Быстрые силовые удары; не сверхчеловеческая неуязвимость |
| Рыжик | Акробатические приёмы с читаемыми contact/recovery |
| Паша | Хаотичные импровизации, но корректный resolver и hit timing |
| Тимка | Мощные захваты только в сценах прайма; современный не получает прежнюю силу автоматически |
| Олежка | Приёмы, объяснённые реальными тренировочными сценами/flags |
| Тега | Импровизация с доступными объектами окружения |
| Якудза | Неуклюжий/медленный/рискованный, длительный windup и окно прерывания |

FIN-02 базовый набор обязателен до P07, character-specific расширения — после соответствующих P06 abilities/portraits. Если нового генератора/рендерера или художественного review нет, ART portion BLOCKED, не замена реальных эффектов геометрией.

## Evidence и release gate

Сохранить в `reports/phases/P04G/`: перечень новых PNG/atlas/source/audio с SHA256 и лицензиями, full-direction phase captures, короткое native видео каждой категории/архетипа, reduced/full сравнение, actual тесты и performance fixture, свежие Windows/Linux builds с точной маркировкой runtime/Wine/native. Раздельные независимые ART/GAMEPLAY/QA заключения и итоговый Lead decision. Работа выполняется последовательно одним исполнителем; review контексты не редактируют код. Нет claim полного gore/finishers до реализации и PASS.
