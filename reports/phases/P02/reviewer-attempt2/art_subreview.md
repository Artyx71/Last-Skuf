# P02 — independent art re-review, attempt 2

Reviewer `/root/lead_reviewer/p01_art_subreview`, отдельно от авторов root/gameplay_p02/art_production. Проверяемый source `4202a74f82498b1656de9a7b24bef765c606659c`, art change `1d91be2`, база diff `021c126`. Дата 2026-11-13. Только review/inspection artifacts в этой папке; source/production PNG не менялись, генерация/commit/push/upload фото не выполнялись.

**Art verdict: исправления ART-P02-02/03/04 приняты; ART-P02-01 частично исправлен и остаётся OPEN MEDIUM для wind-up/recovery sockets. Открытых HIGH/CRITICAL в данном art scope нет.** Это не утверждение «все4 tickets закрыты» и не финальное решение фазы: parent Lead определяет общий gate по QA/CI/artifacts и политике MEDIUM findings. Нового human likeness gate нет: принятый P01 сохранён, guards вымышленные.

## Evidence и независимые проверки

Прочитаны relevant source diff, `weapon_visuals.json`, combat/player/enemy presentation code, shooter attempt2 README/prompt/recipe/inventory, author report, transition probe source/metadata. Авторские assertions не использованы как единственное доказательство.

Через локальный `view_image` открыты:

- Actual восемь `attempt2/weapon/melee_{down,left,right,up}.png` и `ranged_{down,left,right,up}.png`, а также `gameplay_weapon_hand_sheet.png`.
- Actual `defeat_fade.png`, `defeat_cue.png`, `defeat_cleared.png`, `hud_upper_edge.png` и свежие parent reviewer captures этих состояний/всех восьми wind-up/recovery phases в `reviewer-attempt2/phases/`.
- Production `game/assets/art/enemies/shooter_sheet.png`, новый source `shooter_master_v2.png`, `shooter_before_after_4x.png`, actual transition contact sheet.
- Собственные frame extractions из реальных MP4: `weapon_phase_replay_11p20.png` и `shooter_{first,second,third}_cycle_8fps.png`. Также `actual_windup_recovery_4x.png` — NEAREST crops свежих parent native captures, и `hand_socket_phase_inspection.png` — actual immutable action-sheet crops с зелёными crosshairs на authored socket coordinates.

Независимо посчитано: новый shooter SHA256 `c56e165d27bb923770d107e12959c6c2575d9414171e3be309c639cfd38b50ec`; изменены **ровно4 frames** `(row,col)=(0,0),(0,1),(3,0),(3,1)`, остальные28 RGBA frames точно совпадают с Git base. Patrol/rusher PNG и их atlas entries, global atlas fields, action PNG/atlas неизменны. Все28 файлов нового shooter inventory совпадают с указанными SHA256. P01 world/present/past PNG и atlas совпадают с accepted P01 decision hashes.

Native shooter: 384×256, alpha только0/255, transparentRGB(0,0,0),25 opaque colors, clean hard pixel edges. Рецепт выбирает только4 cells нового generated master и документированно удаляет3 избыточные shin rows у up-idle; uniform figure resize отсутствует. Осмотр поз не выявил оторванных коленей/ботинок, clipping или чужого фона.

## Решения по tickets

### ART-P02-01 — OPEN MEDIUM: контакт/стрельба исправлены, knife wind-up/recovery ещё на phone-hand

Прежнее оружие у стоп устранено. Все4 melee contact captures используют sprite frame1, все4 ranged — `fire` frame0, который отображает source contact pose; нож/пистолет начинаются у видимой кисти. Up weapon рисуется сзади корпуса и выше floor, остальные — перед кистью. Телефон остаётся в левой руке. В actual ranged captures вспышка и tracer выходят вдоль ствола; source хранит начальный hand-to-ground visual offset для всей траектории, без привязки летящей пули к последующему движению руки. В dense actual replay пистолет и летящий tracer также находятся на согласованной высоте. Эта часть старого ticket закрыта.

Однако fresh parent native captures воспроизвели недостаток остальных фаз:

| File / frame | Expected | Observed |
|---|---|---|
| `game/resources/combat/weapon_visuals.json` anchors.right.shove[0]=[38,29]; `phases/melee_right_phase0.png` | Нож следует правой согнутой кисти в wind-up; телефон отдельно слева. | Socket лежит на **левой phone-hand**. Правая кисть видна ниже/левее у груди, нож появляется из руки с телефоном. |
| right.shove[2]=[38,30]; `phases/melee_right_phase2.png` | В recovery нож опускается с правой кистью. | Правая рука опущена к бедру, нож остаётся на высоте телефона в другой руке. Это не допустимая occlusion, обе руки видны. |
| left.shove[0]=[12,36]; `phases/melee_left_phase0.png` | При скрытой правой кисти оружие имеет соответствующий rear socket/layer или скрыто корпусом до выхода руки. | Передний knife overlay снова прикреплён к видимой левой кисти с телефоном. |

Down/up phases0/2 и left phase2 выглядят связанными с правильной рукой. Exact source cells: `action_sheet.png` right_0 rect(0,128,48,64), right_2 rect(96,128,48,64), left_0 rect(0,64,48,64); исходный action sheet не менялся. Зелёные markers в `hand_socket_phase_inspection.png` показывают, на какие фактические native pixels попали sockets; `actual_windup_recovery_4x.png` подтверждает результат настоящим renderer.

Repro: training kit, aim right/left, melee; capture frame0 до1/12sec и frame2 после contact window. Минимальный остаточный ticket: переавторить right wind-up/recovery sockets по **правой** кисти, для left wind-up выбрать корректную скрытую правую кисть и occlusion/layer либо скрыть weapon на этой фазе. Не переносить нож в руку с телефоном ради непрерывной видимости. Снять все3 фазы×4directions, а не толькоcontact1; сохранить проверенные fire/contact sockets и physics clock. Изменение approved P01 или новый большой action pack не требуется.

### ART-P02-02 — CLOSED: shooter idle↔walk continuity

Independently measured head top down/up idle0/1 теперь6px, walk start6px; прежний скачок6/5px исчез. Изменились поза ног/таза и их иерархия, а не только bounding box. Каска/бронепластины не растянуты, силуэт остаётся тем же original shooter. Остался малый walk bob6–8px, который выглядит шагом.

Самостоятельный ffprobe реального `attempt2/shooter_transition.mp4`:640×360,60FPS,396frames,6.6sec. Read source/JSON: реальные idle3FPS/walk8FPS, три start-stop cycles с starts36/168/300; в каждом actual after animation показывает frames0–5. Лично извлечены и открыты chronological8FPS кадры **всех трёх циклов**, включая переходы до/после walk. Прежнее увеличение/сжатие корпуса при старте/стопе не наблюдается в after; очевидный before jump остаётся в левой контрольной половине. Это визуальный осмотр реальных кадров, не заявление о human continuous playback approval.

### ART-P02-03 — CLOSED: defeated presentation однозначна

Наблюдаемая последовательность в actual captures и MP4: guard получает явный cross/ring cue, быстро растворяется, cue затухает, затем место пустое. Standing armed corpse больше не остаётся. Прочитанный lifecycle code использует fade0.18sec/cue0.65sec; actual JSON согласован с изображениями: на0.05sec sprite alpha≈0.722/visible иcue visible; на0.25sec sprite hidden/alpha0, cue visible; на0.65sec обаhidden. Collision layer0 и health0 согласованы с dead state. Fade иcue — самостоятельная defeat presentation, они не выдаются за fall animation.

Свежий HUD upper-edge capture просмотрен вместе с source `_add_label` z_index10 противactor1: текст рисуется выше персонажа и остаётся читаемым; отдельный HUD regression finding не подтверждён.

### ART-P02-04 — CLOSED по supporting art evidence и независимому parent runtime probe

Source теперь управляет visual poses и melee phase одним physics clock; `weapon_visuals.json` явно описывает wind-up1/12sec, contact frame1, удерживаемый на первоначальный active window(.14/.16sec), recovery1/12sec. Nominal atlas12FPS не используется как независимый autoplay clock для melee. В actual replay contact effect появляется на contact-позе.

Лично прочитан **parent independent** `reviewer-attempt2/timing_probe.json`: при frame0 ticks0–4 hits0/health3, при frame1 tick5 hits1/health2; `passed=true`, `damage_during_windup_observed=false`. Это поддерживает закрытие прежнего HIGH; полную проверку contact/late-entry/cancel/cooldown и окончательное техническое решение выполняет parent, этот subreview не присваивает себе его test execution.

## Остаточный риск

Открытый ART-P02-01 MEDIUM касается hand consistency в коротких pre/post-contact фазах, а не старого эффекта оружия у стоп или раннего damage. Остальные три заявленных исправления визуально/структурно подтверждены в указанном scope. Публичные права и новые approvals из этого report не выводятся. Финальный phase gate и допустимость оставшегося MEDIUM — решение parent Lead.
