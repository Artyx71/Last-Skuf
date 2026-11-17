**FAIL_COMPONENT — независимый baseline QA Паши на `fb5ca9bdf0e82e315c08197877e1f39a2a6c4091`.** Это узкая квалификация wall-callback, UI и CI gaps, не полная игровая/фазовая приёмка. Blocking: `PQ-W01`, `PQ-HUD01`, `PQ-CI01`.

Reviewer сохранил 1314 source SHA и отдельную физическую ROOT-копию game/tools/source_art с copied pinned Godot и isolated XDG/save paths. WORK, Git, production и Controller самим reviewer не менялись. Единственный родительский Controller запускал три engine calls последовательно: fresh import и первый probe, затем отдельную исправленную версию. Source/probe inputs проверены до/после и не изменились. Два реальных завершённых receipt/log SHA проверены. Глобальная неизменность Controller state не заявляется: авторизованные stage transitions родителя происходили нормально.

Первый QA probe **не выполнил assertions**: GDScript не смог вывести тип `label`. Это ошибка моей QA fixture, не product proof. Actual parse log/entry/probe сохранены. V2 меняет только `var label:=...` на `var label:String=...`, использует новый entry/output и те же 16 assertions. Ничего не перезаписано.

V2 дал **14/16, exit 1** и фактически подтвердил `PQ-W01`. Настоящий Input F запускает moving shot; две positive controls и два reset cases различают:

| Ветка | До callback | После reset внутри callback | После Core в том же tick |
|---|---|---|---|
| Muzzle obstruction | projectiles0, epoch5 | epoch6, flash0, pos(0,0) | tick45: flash0.15, pos(315,210) |
| Travelling projectile wall | projectiles1, epoch8 | epoch9, flash0, pos(0,0) | tick106: flash0.15, pos(349,210) |

Observer priority1000 снимает состояние после Core; tick сравнивается с записью внутри callback. В новом epoch обе ветки восстанавливают старую вспышку/позицию. Ammo4, rounds0, jobs/projectiles0, damage/score0 и layer/mask2/1/exceptions0 при этом остаются сброшенными. Повторного урона/очков не наблюдалось. Positive controls реально попадают в стену, дают одну wall impact/round cost и flash0.15. Причина: после `_wall_contact` с внешним audio event обе ветки пишут `last_hit_position` и `hit_flash` без повторного epoch guard. Требуется проверка pinned definition epoch после callback **в обеих ветках**, до старых visual writes. Проба не дублирует Gameplay body-impact reset или target-free cases.

`PQ-HUD01`: actual native `empty_clip_HUD.png` просмотрен и rehashed по авторскому inventory, native source map exact1314/fb5. Meter y63..67 пересекает живого верхнего правого NPC; source подтверждает Control y27 + meter y36/height5. Playfield frame начинается y54. ART предварительно отметил то же; здесь имеется собственное подтверждение реальной PNG, а не только пересказ отчёта. Полный native/movie/media audit этим baseline не выполнялся. HUD нужно разместить читаемо за пределами игрового поля и проверить native/actual rect; это не изменение хитбоксов.

`PQ-CI01`: frozen `tools/verify.py` не регистрирует `tools/verify_p06_pasha.py`, хотя production body уже ready. Требуются headless controller registration и фактическая проверка common-main routing/nonzero/fatal-log propagation. Remote GitHub CI этот QA не запускал.

Большие legacy regressions, новая metadata/resource/HUD probe и source/export smoke на этом baseline **не выполнялись**. Отдельный `REGRESSION_REQUEST.json` требует их на исправленном frozen candidate из-за изменений shared CombatSystem/CharacterPlayer/Frames. Подготовленный `qa_pasha_metadata_resource.gd` — неисполненный draft для следующего кандидата, он исключён из portable доказательств. Авторские headless385/native573/movie385 не объявляются собственными проверками reviewer.

Все собственные engines завершены. Следующий шаг — авторские wall/HUD/CI исправления и новый независимый full component QA packet. Этот FAIL остаётся неизменным. Никакого P06/readiness/campaign/merge/release/nativeWindows/FPS/hardwarelatency/subjectiveaudio/export/ART/feel одобрения нет; raw-фото не копировались и не отправлялись.
