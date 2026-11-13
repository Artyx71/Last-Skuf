# P02 — боевой прототип

Авторы: `/root` интеграция/verification/toolchain, `/root/gameplay_p02` combat/AI/restart, `/root/art_production` real image_gen art. Prerequisite: independent P01 PASS attempt2. Source implementation1786633. Это технический полигон, не законченная миссия P04.

## Реализация и управление

Enter открывает полигон, F1 лабораторию P01. WASD/стрелки, Space/ЛКМ melee, мышь aim (keyboard fallback по facing), E finite distraction, R полный restart, F2 явно обозначенный учебный kit, Esc меню. Сюжетный default escape kit:82px/s,health1,nonlethal shove/stun без gun. Training kit отдельно даёт нож/пистолет. Gameplay data JSON включён в оба exports.

Melee — native intersect_shape + wall LOS + once-per-attack target set. Projectiles — continuous segment ray, включая origin→muzzle и hit_from_inside; проходят tests pointblank/thin-wall/muzzle adjacency/high-speed sweep. Collision layers walls1/player2/enemies4. Patrol/rusher/shooter: patrol→alert→pursue→locked-aim telegraph→recover; noise/stun/dead отдельные состояния. AI предупреждает до actual hitbox/projectile; из locked aim можно уйти.

Cached reset очищает health/position/velocity, kit/cooldowns/aim/action-animation, AI timers/intent/stuns/layers/transitions, bullets/hitboxes/damage/noise/score, seed/rng. Death-to-control nominal250ms; ten actual lethal physics hits дают10/10 exact snapshot restoration, measured max269.057ms. Это локальная cached latency, не универсальный performance benchmark.

## Реальный арт

Три разных masked fictional guards (patrol cyan heavy, rusher orange, shooter crimson) имеют native48×64 frames,384×256 sheets,2idle+6walk по4directions,hard alpha и source recipes/prompts/masters. Новый отдельный Yakuza action sheet:3shove/2hit/3fall на4directions,12FPSnonloop; последний кадр явно лежит. Metadata/provenance и inventories сохранены. Approved P01 portraits/world PNG и atlas не менялись. Структурные тесты не утверждают художественное качество. Minor guard pose jitter существует; независимая визуальная оценка обязательна. Raw фото не входят в Git/game; publicrelease/voice rights не выданы.

## Проверка

`python3 tools/verify_p02.py --references`:21 recorded acceptance commands/results PASS (точный список validation.json). Native assertions555/555: bootstrap6,art90,movement34,combat-art300,combat35,AI32,restart58. Reference hashes/privacy PASS. Movie Maker записал actual scene/input,773frames60FPS12.883333s; MP4 silent, аудио P03 ещё не создано. Escape386physicsframes6.43s,0kills,0shots,3detections,2pursuing; E меняет intent, player движется от58до584px без teleport. Затем настоящая AI death, R restart (max477.168ms при MJPEG recording), отдельный training bench:1melee-hit+1projectile-hit. Bench специально ставит targets для testing; escape идёт в неизменённой арене с activeAI. Replay JSON содержит initial/end/death/reset snapshots и acceptance checks.

Автор осмотрел actual screenshots Linux/Wine и извлечённые movie frames combat_fall.png/combat_melee.png, сравнил action sheet: падение и нож видны, UI training явно отличается. Contact sheet взят из MP4 с fps2. Не выдаём тестовые annotations/geometry за level art или SFX.

Linux и Windows builds в build/P02, прежние P00/P01 не перезаписаны. Linux smoke/renderPASS; Windows PE smoke/renderPASS **под Wine11.17 на Linux**, native Windows NOT_TESTED. Реальный Windows Godot выводит OpenGL/NVIDIA, capture сохранён из Windows process. Wine MESA-EGL/SDR warnings сохраняются в logs, exit0; ничего не скрыто. Hashes exports.json.

## CI и gate

GitHub CI43387775768 SUCCESS на source1786633: свежие555assertions, оба exports и artifact download. Ephemeral runner удалён автоматически; API runners0/variables0, local credentials отсутствуют. Archive cache verifiedSHA512, fresh imports/builds. Exported Linux и Windows/Wine также прошли полный actual replay; maxreset283.249/283.251ms (export_replay_acceptance.json). Independent Lead Review финализируется отдельно; до actual decision PASS P03 не начинается. Платежи/hostconfig не менялись, sudo не применялся. Repo private, phase PR stacked без merge. Постоянного runner нет; session CI только single-job ephemeral с последующим cleanup.
