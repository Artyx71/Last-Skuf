**FAIL_COMPONENT — QA исправления Теги на `c8f465840ec970e6abdcb9d41e1f0cbed8fc38bd`.** Исходный far-transform случай закрыт, но полное закрытие `TEG-Q03` / Lead `TEGA-L01` не подтверждено: осталась рассинхронизация актуального Node transform и физического query. Найден второй обязательный дефект `TEG-Q04`: отмена нового действия после reset с повторным numeric attack ID. До исправления обоих компонент не принят; разрешений на P06/readiness/merge/release нет.

Reviewer сохранил 1242 source SHA и собственную физическую копию game/tools/source_art без raw-фото, mutable links и WORK `.godot`. По сравнению с 084 изменены **только** `environment_kick_runtime.gd` и production `tega_environment_replay.gd`; остальные 1240 ключей, shared CharacterPlayer/CombatSystem и арт неизменны. Production source в ходе review не правился. Автор мог перейти к следующему исправлению после сохранения c8 snapshots; этот отчёт привязан к сохранённому c8, а не к будущему WORK HEAD.

Все девять собственных headless engine calls запускал родитель строго последовательно через канонический Controller.stage, с отдельной ROOT-копией pinned Godot, fresh import и isolated XDG/save paths. Job06 entry SHA `b2490c71efa6ae3fd7b73697fb57a6355fd0030cbf5bbad5a2ad42283b0ad13a`, manifest `f91933903330dc849e9088a9d0d9aec3b6661eea5f2ec2fbf6080e4b42b81a60` и четыре probes не менялись после PREPARED, что проверил сам job до/после исполнения. Job07 — отдельный новый script/output; старые результаты не перезаписаны. Оба completed job receipts/log SHA проверены. Нет утверждения о неизменности глобального Controller state: разрешённые stage receipts меняли его обычным образом.

Свежие результаты:

| Проверка | Результат |
|---|---:|
| Тот же byte-exact independent far-geometry probe | 8/8 |
| Extended LOS/footshape/new-shove probe | 10/12 |
| Старые independent metadata/lifetime/callback 23 + custommask/exclusions/reset 3 | 26/26 |
| Actor-only wall boundary | 4/4 |
| Production Tega replay | 300/300 |
| Oleg counter HUD | 57/57 |
| Source bootstrap headless smoke | 29/29 |
| Direct-shape/physics-cache/epoch qualification | **13/15** |

Production 300 и собственный unchanged geometry8 прошли. Listener, включающий препятствие LOS, теперь останавливает job в том же tick; listener cancelF→newshove сохраняет новое действие и реальную Core reservation. Старые free/reset/revoke/body replacement probes также прошли. Прежние 14 зелёных suites/2297 assertions на 6a **не объявляются новыми c8 запусками**. Для узкого изменения Tega resolver повторять их не требовалось; hashes общего кода и арта связаны `source-delta.json` и immutable QA01.

В extended probe смещение верстака на `(0,16)` оставило range 32.249 px и facing dot 0.868, но `_near_foot` неожиданно вернул true. Этот провал предусловия сначала был диагностикой, а не заявлением о product bug. Отдельный job07 квалифицировал его прямой независимой проверкой форм. [`Shape2D.collide`](https://docs.godotengine.org/en/stable/classes/class_shape2d.html#class-shape2d-method-collide) принимает две формы и явные transform matrices, поэтому контроль не зависит от world broadphase.

`TEG-Q03`, оставшаяся часть: непосредственно после callback Node body/shape находятся `(308,256)` / `(308,250)`, foot Circle8 — `(303,234)`. Прямой `Shape2D.collide` с **текущим CollisionShape2D.global_transform** возвращает false; прежняя форма до смещения контактировала. В тот же момент PhysicsServer body/shape ещё `(308,240)` / `(308,234)`, direct collision на server transform и DirectSpaceState возвращают true. Core использует этот старый query и двигает **Node на новой недоступной позиции** ещё на `0.70001220703125` px вместе с героем; job остаётся 1. Physics observer priority 1000 подтверждает тот же tick 19. Это не полное закрытие геометрической eligibility. В контрольном режиме QA вызывает `force_update_transform`: server переходит к y256, обе формы/query становятся false, Core оставляет нулевой delta/job0. Добавлять force только в тест было бы обходом; production должен обеспечить согласованную проверку текущей геометрии перед движением. Фактический исходный и forced контроль сохранены в `physics-qualification-07/result.json`.

`TEG-Q04`: синхронный callback использует нормальные production APIs `combat.reset()` и `player.reset(current_position)`, затем `use_ability()`. Прямого изменения cooldown нет. `CombatSystem.reset()` обнуляет `next_attack_id`, поэтому old epoch6/id1 сменяется **new epoch7/id1**, новое F реально создано, action `special`, job1. Затем старый `_stop_job` сравнивает лишь текущую авторизацию и numeric ID и отменяет новое действие: afterCore action пустой, id0, jobs0 в том же tick137. Нужна идентичность старого действия с encounter epoch и pinned authority, а не один numeric ID. Различный action kind (новый shove) был корректным позитивным контролем, но не покрывал повтор ID между epochs.

Оба отрицательных случая имеют damage/receipts 0, masks/exclusions неизменны. Удалённого урона/повторных очков не наблюдалось и не заявляется. Исходные 8 far-transform assertions и новые 15 qualification assertions не ослаблялись. Уточнение предположения world query подтверждено отдельным прямым измерением, а не переименованием провала в PASS.

Saved native02 автора независимо пересчитан: 136 artifact SHA, 1242 source SHA exact c8, 128 PNG, live428/movie300; saved ffprobe4717 кадров. MP4 SHA `5ce602d1850f328da9990be9f9172c1f0996cf8bdb97fb2b0d901145b4407984`. QA не запускал новый native renderer, не декодировал видео и в этом раунде не просматривал PNG. Numeric replay audit собственного production300, native и movie подтвердил в каждом 66 уникальных Core tokens и 24 FIN (12 Full/12 Reduced); эти зелёные корпуса не заменяют пропущенные отрицательные условия. Source bootstrap29 не является проверкой packaged export.

QA01 FAIL decision `3cbcc64ebe2ac771182a82eb76b986dcb3cbc4098fb0093367a5dbfa228d0224` и все 188 файлов его portable manifest перепроверены и не изменились. Его старые 51/57 counter FAIL, собственные диагностические FAIL и исторические author failures сохранены. Privacy/CI-mock/export-metadata proofs QA01 остаются историческими результатами на неизменных относящихся к ним файлах; свежих CI/privacy/export запусков в этом раунде нет. Выполнен только read-only GET официальной публичной документации Shape2D; проект/фото никуда не отправлялись.

Следующее действие: автор исправляет согласованность Node/physics geometry и epoch-qualified cancellation, затем новый freeze и отдельный независимый closure. Никакого phase/readiness/merge/release/export/nativeWindows/FPS/hardwarelatency/subjectiveaudio/ART/feel одобрения этот отчёт не даёт. Все собственные engines завершены.
