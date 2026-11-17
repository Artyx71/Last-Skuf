# P06 — Olezhka counter/controller preflight v1

Статус: **SOURCE_AND_AUTHOR_RUNTIME_VERIFIED_COMPONENT_ONLY**. Reviewer `/root/gameplay_review_p06` независимо прочитал production CharacterPlayer/Core, prepared replay, SDD contract и настоящие author artifacts. Godot/controller/tests/Git commands/build/generation не запускались; WORK source не менялся. Записи только versioned olezhka-controller-preflight-v1.* в корневой gameplay-preflight. Это bounded controller/contact-defense review, не full P06/Lead PASS, не native feel/ART/listening/FPS/export approval.

## Проверенная механика

Olezhka use_ability разрешён только actor_id=olezhka с live registered training_counter capability. F начинает guard с windup0.28/active0.10/recovery0.34 и cooldown2s; authority actor/context/fixture/generation/owner и ability_id фиксируются существующим _play_action. Miss не создаёт attack. Body movement блокируется special state; health/collision masks не заменяются и не дают неуязвимости.

Defense проверяет playing/alive, special+training_counter, live action authority, counter_spent=false, authored windup frame0, окно action_elapsed0.06–0.26, hostile CharacterBody source layer4/alive, permitted melee category unarmed/blunt/sharp, front dot>=0.65, distance1–40 и LOS. После первого block counter_spent ставится до постановки counter. Тот же action_elapsed переводится в windup boundary0.28, renderer показывает signature contact frame1. Это явный переход существующего physics action clock, не независимый animation timer.

Core _apply_hit резервирует существующий attack-target receipt **до** optional defense. Только реальный melee shape dispatch передаёт contact_kind="melee"; bullets/muzzle/projectile, finishers и legacy direct calls сохраняют default damage path. При accepted defense отсутствуют damage_events/receive_hit/contact_committed/knockback/blood/score; отдельный contact_defended event сdamage0 ограничен512 records и очищается reset. Incoming once-token не может повторно block или позднее damage тот же target.

Успешный block ставит отдельный stamped Core melee attack: damage1/stun0.45/reach21/radius14, существующий0.10 active/0.34 recovery. Это не прямой callback damage. Из-за iteration по attacks.duplicate новый counter обрабатывается следующим physics turn; per-recipient authorize_melee_contact повторяет live authority/phase. Cancel/death/reset/revoke отменяют pending counter. Второй simultaneous incoming attack проходит damage path и способен убить Olezhka/удалить queued response — single block не превращён в invulnerability. Default Gabar/Yakuza без допустимого Olezhka guard не получают бесплатной защиты.

Actual trace подтверждает очередность: counter_down incoming id1 defended tick283/action_elapsed0.28/frame1; outgoing id2 damage1 tick284/action_elapsed0.2966667/frame1. Это соответствует заявленному next-turn counter и единому physics clock.

## OLEZHKA-PF-01 — MEDIUM test finding CLOSED

При первом source inspection новый replay использовал неизвестные gore_reduced/blood_decals/hit_flashes keys, игнорируя false от OptionsStore, и shake1 вместо100. Это не давало proof Full/Reduced. Finding своевременно передан автору до первого actual Olezhka run; initial source snapshot сохранён отдельно.

Current replay использует reduced_gore/decals/flashes/shake0–100/vhs и проверяет каждый setter вместе с actual stored value. В actual **olezhka-combat-03** присутствуют и проходят все **10 setter/value checks** (5×Full/Reduced), затем сравниваются health/hits/events/defenses/score/collision state. Поэтому issue закрыт source плюс исполненным evidence, не только обещанием исправить тест.

## Actual Olezhka evidence

Прочитаны validation.json, command receipt, real live.log, result/trace/contacts/defenses. Run01 честно сохранён: Parse Error inferred expected variable, exit1,0executed checks; не считается gameplay failure/pass. После explicit bool Run02 дал152/152; его исторический source inventory отличается от subsequent test/CI edits и не подменяет текущий run.

**Run03:164/164, exit0, headless/fixed-fps60, actual Input,57 contacts/13 defenses,0 rendered captures/no movie/no exports.** Проверены реальный complete Olezhka body56clips/speed106; actual Tab equipment unarmed/blunt/sharp, firearm/environment/normal ranged denied; continuous held run→guard→run четырёх directions без fixture teleports; four-way parry/next-turn counter/recovery/cooldown; miss; receipt reentry; window boundaries; front/rear/side/range/friendly/LOS; C/cancel/revoke/reopen; actual projectile и synthetic direct/finisher bypass; simultaneous two attacks; revoke callback before outgoing contact; reset/options pause-resume;12 earned Space→finisher paths; four-way hurt/fall/death hold; real Full/Reduced store values и equal mechanics.

Boundary samples before incoming contact:0.03333 reject,0.05 accept,0.23333 accept,0.25 reject; actor clock advances ещё один fixed tick до collision. Это проверяет границы0.06–0.26, а не расширяет окно. Range negative намеренно использует QA enemy reach34 вместо base18, чтобы actual volume достиг player вне defense range; SDD это явно документирует. Wall test отдельно вызывает guard LOS predicate и проверяет actual Core obstruction. These fixture variants не выдаются за обычный AI kit или combat play-feel.

## Regression и hash boundary

Независимо проверены все4 artifact hashes Run03 и **706 recorded source entries** против current WORK: **0 mismatches**, включая повторный final check. CharacterPlayer SHA256 `60e868b7853a05a40f921628e3d2a21e1316e4aed19151fa57157870dd01f249`, Core `d7043f0121f12486b06beecfee15f74e922f1d1c2a547e60e8aea11daf7df21d` не менялись со времени первого counter source review. Actual Olezhka finisher PNG hash `e22296ad7634d339d62bb44067e8bf8c5ff3e3d9321e14ff5c8d97851273295c`; identity/provenance/native visual quality здесь не переоцениваются.

Current source/work based on Git label **64c57f75671aeff07e8b9d13a8ee91d4cb79b3ff**, прочитанный из metadata files без Git commands. Dirty candidate содержимое привязано по hashes; это не заявление, что run выполнен на committed exact-head tree64c. Авторское source_unchanged=true означает before==after во время run; current content match независимо проверен.

Предыдущий counter-core-regression-01: **32/32 commands exit0**, логи прочитаны без ERROR/WARNING; run был до новых art readiness/replay/CI edits и сохраняет именно эту границу. Fresh affected-regression-01 после них: **7/7**, all5P06units61+99+57+22+Frames1534 = **1773 unit checks**, Gabar124, CH01 isolation25 плюс настоящий fresh-process CH01 restore. All fresh logs clean; его706-entry source inventory/current совпали, все artifact hashes проверены. Gabar unready-negative теперь использует Timka, поэтому complete Olezhka не объявляется unavailable. Новые Frames tests покрывают все3 Oleg sheets; это atlas structure, не ART/native approval.

tools/verify.py теперь маршрутизирует bounded Olezhka harness наряду с Gabar/isolation. Full tools/verify_p06.py/native publication gate это не заменяет. Reviewer suites не перезапускал.

Новых actionable findings в рассмотренной counter/contact-defense integration не найдено. Открыты отдельные обязательные gates: native X11 Input/captures/actor-target readability и timing perception, ART body/portrait/sockets/finisher consistency, actual audio listening, wall-frame performance, exports/platform runtime, четыре оставшихся hero abilities и полная независимая P06 приёмка. Наличие реального164-check run позволяет принять данный component evidence в указанной области, но не всю фазу.
