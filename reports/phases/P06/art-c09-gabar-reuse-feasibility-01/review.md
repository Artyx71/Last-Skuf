# C09 Gabar — existing shooter wholepose reuse feasibility01

**ART_BLOCKED: четыре contact остаются без совместимого wholepose. Один DOWN release пригоден как explicit existing ref.** Это feasibility audit, не review03 нового готового пакета, не source package/runtime/C09/P06 PASS. Два прежних FAIL сохраняются. Запрещённый moderation_blocked imagegen request не повторялся; reviewer не вызывал генератор, Godot, runner, Git/Controller и не менял Game/WORK. Причину toolblock здесь не переоцениваем.

Лично через actual view_image осмотрены **все96 shooter reaction wholecells**:8states×3frames×4directions. Четыре диагностических3x board содержат каждую фигуру; дополнительный5x board показывает четыре unused hurt2 и ближайшие DOWN release. Это реальный осмотр poses, а не поиск по именам состояний. Все96 RGBA hashes совпадают с atlas metadata,96 уникальны. Exact equality с shooter FIN определяет20 reaction cells, уже используемых как legacy category contacts; это не новые Gabar drawings. Прочитаны pack_generated mapping/исторический source README; принятый P04 baseline не переоткрывается.22 frozen inputs/snapshots после audit неизменны.

## Пригодный existing ref — только R6C1 DOWN release

`game/assets/art/combat_polish/shooter_reactions.png`, **state=knockdown, direction=down, frame=1**, rect **[768,0,48,64]**, bounds **[6,22,44,58]**, exact RGBA SHA **cd63f61ba646433b1a42b157e700bbb8444601af38ce795f68f0507736c466d1**.

Это целиком уже нарисованный NPC, с опущенным корпусом/головой, согнутой опорной ногой и компактным боковым оседанием; он ещё не лежит terminal corpse. Читается настоящий короткий handgun с slide/muzzle и offset grip. Оружие остаётся в анатомической правой / screen-left руке, опущенной к полу; другая сторона тела/колено поддерживают buckle. Он не повторяет ни одного legacy category contact по RGBA. Отличие от текущей v3 release — опора распределена между низкой оружейной рукой и коленом, вместо явно раскрытой пустой ладони у пола. Эта уже полноценная grounded поза физически допустима как shared промежуточный release; требовать совпадения каждой кисти с v3 шаблоном не нужно.

Разрешён лишь **source preparation с целым exact ref**, без вырезания пистолета, перехвата руки, зеркала/вращения или pixel paint. Это не новый рисунок и не новый Gabar contact. Shared release не должен выдавать standalone style uniqueness: новые compatible contact ещё отсутствуют. Будущий полный source пакет обязан явно записать этот ref, а actual paired runtime подтвердить переход из собственного Gabar contact к этому buckle и далее совместимому held corpse, alignment/depth/cloth в Full/Reduced. Сам fallback не меняет death/AI/score clock.

## Почему четыре contact не закрываются existing pool

**R5C1 DOWN, R5C2 LEFT, R5C3 RIGHT, R5C4 UP — ART_BLOCKED.** Нет предложенного разрешённого replacement_ref. Причины по всему пулу закреплены в reuse-assessment.json.

- Telegraph/attack/recovery (36poses) показывают готовность, выстрел с muzzle flash или выход из собственного прицеливания. Это outgoing enemy action, а не полученная Gabar chest/shoulder compression. Переназвать recovery в victim contact означало бы вернуть исправленный defect01.
- Hurt0/1 (8poses), death0 (4), finisher_reaction1 (4), knockdown0 (4) — **ровно20 прежних category contacts**: firearm/unarmed/blunt/sharp/environmental. Копирование/ретайм в новый style slot не даёт нового характерного Gabar contact. Shared ordinary reactions допустимы при честном ledger, но ими нельзя объявить закрытым этот конкретный отсутствующий style brief.
- **Unused hurt2** — ближайшие реальные кандидаты. DOWN [528,0,48,64], SHA96bd1a2b…: корпус собран вперёд, руки и gun близко перед животом, это короткий обычный flinch, не новый chest-back power recoil. LEFT [528,64,48,64], SHA16ee17d3… и RIGHT [528,128,48,64], SHAd03aa06d…: голова немного отклонена, но pistol всё ещё представлен вперёд и руки сохраняют aimed silhouette; отличия от legacy hurt1 слишком малы для требуемого собственного контакта. UP [528,192,48,64], SHAa34c0666…: почти вертикальная спина и собранные плечи, нет читаемой displaced noncombat arm/recoil формы. Наличие иных SHA не устраняет эти наблюдения.
- Stun0..2 (12poses) — standing/hunched neutral loss of readiness, а не короткий grounded chest impact; они не заменяют recoil и в DOWN не дают requested supported release.
- Knockdown1 (4poses) — уже falling intermediates, тело значительно ниже/впереди contact. Только DOWN релевантен открытому release slot; три остальных не следует ставить в contact ради gun identity. Death1 (4poses) уже почти лежит, а knockdown2/death2/finisher_reaction2 (12poses) — лежащие terminal figures. Они не могут быть контактной грудной компрессией или компактным промежуточным buckle.
- Finisher_reaction0 (4poses) — прежний restrained hold; он не изображает силовой hit. Перенос его в contact не добавляет необходимого движения.

Недостаточность source-пары не исправляется сменой speed, role label, category routing, montage или hitbox. Воспроизводимость baseline и читаемый pistol сами по себе не доказывают характерную реакцию на стиль. Category unarmed/blunt/firearm Габара имеет разные fist/tool/muzzle trajectories; здесь не найден даже полный four-way source contact набор, который был бы готов к такой paired проверке.

## Точный итог и ledger

Из пяти defect03 cells **один имеет легитимный existing wholepose release ref**, четыре contact остаются отсутствующими. Нельзя собирать ledger19new+5existing как завершённый пакет: подтверждено только **19 сохранённых C09 source cells +1 existing P04 release ref +4 missing contact cells**. Existing ref не увеличивает unique new drawing count. Source03 формального prepared package review **NOT_STARTED**.19 retainable cells из immutable review02 сохраняются побайтно; новый source master/atlas этим audit не создавался.

Полный source ART gate остаётся BLOCKED до фактических совместимых wholefigure contact drawings. Toolblock не основание ослаблять критерии или подставлять placeholder. Source adoption текущего v3, actual paired runtime, C09/fullP06/P07/merge этим отчётом не разрешены. Все output bytes после decision immutable.
