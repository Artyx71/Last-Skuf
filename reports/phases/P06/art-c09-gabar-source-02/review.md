# C09 Gabar source repair v3 — независимый ART review02

**FAIL_SOURCE_ART / FIVE_SHOOTER_WHOLEPOSE_REPAIRS_REQUIRED.** Review01 `985592e6…` остаётся immutable. Результат02 ограничен новым v3 source/packing; исторические baseline tests, generator или Godot не запускались. Производственные Game, SourceAudio, Git/Controller не менялись. Только новые owned outputs в этой папке.

Осмотрены actual raw-edit, assembled master, native PNG и inspection3x, затем собственные NN wholecell boards рядом с принятым shooter handgun и rusher knife. Дополнительно лично осмотрены прежние shooter WORLD и Gabar FIN для identity/category сверки. Это8 PNG views, не runtime captures. Прочитаны новые prompt/generation/assembly и оба recipe; предыдущие gate criteria и review01 действуют. Все31 frozen inputs и snapshot copies совпадают при after-check. Старое decision01 по-прежнему SHA `985592e6d599a9c1abc13703f4c7f71bd5385e5441e2dca688f821b4b4d7376e`.

## Что исправлено

**ART-C09-GAB-01 закрыт на source уровне:** все12 contact теперь дают читаемый recoil — голова/грудь отведены относительно согнутых опирающихся ног, руки раскрыты/ослаблены, две готовые атакующие кисти и прежний aimed-pistol силуэт устранены. UP остаётся настоящей задней проекцией; руки асимметричны, корпус/ноги показывают off-balance. Новые формы отличаются от старого enemy idle/attack. Не требуется снова переделывать эти позы ради большей театральности.

**ART-C09-GAB-02 закрыт по handedness:** rusher R4C1 и shooter R6C1 сохраняют оружие в исходной анатомической правой / screen-left руке, пустая левая / screen-right кисть поддерживает падение. Они целые supported knee-buckles. Исправление shooter ownership само по себе не доказывает правильность типа оружия.

Все24 фигуры целые, четыре проекции читаются, UP без front face, не найдено обрезанных рук/пальцев/оружия, новых конечностей или fake corpse. Release остаётся промежуточным оседанием; окончательное тело должно быть отдельной явно связанной совместимой corpse role. Архетипные цвета/hood/armor сохраняются. Дополнительный wardrobe/baseline redraw не запрашивается.

## Единственный открытый defect: ART-C09-GAB-03

**Пять новых shooter wholefigures теряют читаемость компактного пистолета.** Это observable identity defect исходника, а не предположение по названию manifest и не требование поменять стрелковую механику. Индексы 1-based; C1 DOWN,C2 LEFT,C3 RIGHT,C4 UP; R5 shooter contact,R6 shooter release.

| Cell | Source rect xyxy | Наблюдение |
|---|---|---|
| R5C1 DOWN contact | [0,1024,256,1280] | Длинная узкая светлая полоса с зауженным концом под кулаком; не читаются короткий slide и поперечная рукоять. Почти тот же ножевой силуэт, что у rusher. |
| R5C2 LEFT contact | [256,1024,512,1280] | Свисающий pointed strip, кулак на верхнем конце; компактная геометрия handgun исчезла. |
| R5C3 RIGHT contact | [512,1024,768,1280] | Конец более округлый, чем у остальных; предмет читается узким rod/capsule, без различимой offset рукояти и short slide. Это не основание называть его ножом с уверенностью, но собственный пистолет всё равно не узнаётся. |
| R5C4 UP contact | [768,1024,1024,1280] | У правого бедра длинный светлый taper, читающийся blade; отдельная handgun геометрия отсутствует. |
| R6C1 DOWN release | [0,1280,256,1536] | Рука уже правильная, но предмет под ней — узкий прямой blade/rod, не компактный pistol. |

Evidence: **weapon-identity-comparison-4x.png** показывает все четыре направления target рядом с реальным принятым P04 handgun и rusher knife; **shooter-source-native-wholecells.png** показывает целые raw и native клетки. Ошибка заметна уже в raw/master до scale. Нельзя объяснять её только квантованием/.24 export. Поза может держать pistol muzzle вниз и всё равно сохранять собственную короткую slide/barrel массу и рукоять; сейчас этих признаков недостаточно при native размере.

Минимальный fix: **только эти5 новых целых shooter figures**, с прежними recoil/grounded buckle, направлением, опорой и анатомической правой оружейной рукой. Сохранить узнаваемый собственный компактный handgun после штатного уменьшения: короткий массивный slide/barrel, раздельная offset/perpendicular рукоять/запястье и читаемый muzzle, без длинного светлого ножевого taper. Ствол опущен/отведён из боевой линии, свободная кисть не превращается обратно в aiming support. Не приклеивать отдельно пистолет или кисть к bitmap, не перерисовывать принятый P04 baseline. Новое source wholebody generation/technical assembly — root.

**Остальные19 source wholecells можно сохранить byteexact**: все patrol/rusher contact/release и shooter R6C2–C4. Это8 новых допустимых contact, новый rusher DOWN release и10 старых retained release. Их точные SHA в cell-review.json. Не требуется повторно генерировать эти19; новый fix не должен случайно их менять. Это локальное сохранение source для следующего review, не package adoption PASS.

## Техническая конверсия

Raw SHA `a7af3e81…`; assembled master `510c7869…`; native `00955ed9…`. Независимая RGBA проверка assembly подтверждает14 new whole256cells и10 exact v2 cells. Все10 retained native release также byteexact прежнему preview. Текущий atlas содержит24 уникальных RGBA cells — не38 новых финальных поз;24 текущих drawings и новый repair provenance считаются отдельно.

Независимая реконструкция export **совпала побайтно** без исполнения авторского recipe. Contact берётся целым alpha128 bbox, uniform .24 по обеим осям для всех12, NN; размер34–45px шириной /37–44px высотой, целиком вкладывается в48×64. Clamp embed сохраняет все sampled opaque pixels. Это uniform wholefigure scaling, а не изменение анатомии. Release сохраняет .25 whole256cell NN и crop8px только пустых боков. Anchor bottom58/pivot24,58, no dither, palette35+3; actual native33 RGB, alpha только0/255,21524 opaque pixels. Ни размещение, ни anchor не обрезают выбранную opaque область; все24 manifest frame SHA совпадают. Source master сам semi-transparent alpha0..254 и не должен называться уже бинарным pixel master.

Переход с .25 на .24 у contact допустим технически и не является причиной нового weapon defect. Разница масштаба с release/baseline и точный torso socket должны проверяться в реальной паре позднее. Этот source review не утверждает runtime pivot/центр массы или clothing/depth alignment.

## Категории и scope

Gabar FIN сохраняет разные contact columns1 unarmed /2 blunt /4 firearm, все четыре направления. Для patrol/rusher recoil форма source-совместима с подготовкой paired проверки этих категорий; каждый actual fist/tool/muzzle контакт обязан попасть в согласованный chest/shoulder объём. У shooter дефект собственного оружия относится ко всем трём incoming категориям, поэтому нельзя принять его лишь в unarmed или firearm route.

Матрица36 static bindings:24 patrol/rusher source shapes eligible для paired preparation,12 shooter bindings отклонены. Ни одна из36 не получила runtime physical compatibility approval: sheets не задают locked source/target positions и same-tick contact sockets. Shared contact может стать явным ref нескольких категорий только после этого доказательства. Нужны actual windup/contact/release/terminal, правильные facing, Full/Reduced, прежний authoritative Core и отдельные ART/Gameplay/QA/Lead gates. F-lunge не принят этим FIN review.

Package v3 пока **не разрешён к adoption preparation**. Следующий шаг —5 wholefigure repairs и свежий immutable source review. Pasha/Tega/C01 component решения не переоткрываются; full C09/P06/P07/merge и runtime не приняты. Report02 и все bound outputs не переписываются после verdict.
