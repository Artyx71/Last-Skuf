# P06 — Gabar DOWN world preflight v5a

**ACCEPTABLE_DOWN_DIRECTION_SOURCE_CANDIDATE.** Техническая упаковка целых поз устраняет finding v5, сохраняя читаемый противоположный шаг/бег и overhead identity. Новый source blocker не найден. Это пригодность к дальнейшему native preview, не runtime/fullworld/P06 approval.

Ревьюер `/root/art_review_p06` просмотрел actual unchanged master v5, native8/inspection4x, contact/run pairs8x, walk4 и четыре direction-idle рядом. Source master SHA `055d15039aa525779c0f4efd3c60cbadfdd31bf48c8da4ec8bb2685f6024f726`; native SHA `dab7e3f2fd1d2451211d2a7536e6ebc20fc5ae657449ccf3def083a49efce060`.

У contacts2/4 и run6/7 нижняя ведущая стопа явно меняет screenLEFT/anatomicalRIGHT ↔ screenRIGHT/anatomicalLEFT. Руки дают взаимный обмен; часы остаются screenRIGHT/anatomicalLEFT в переднем и заднем положениях. Passing3/5 показывают разные опорные/поднятые колени, контактные и проходные силуэты различимы. Нет прежней ошибки «одна ведущая нога при смене только рук».

Визуально сохраняются crown/shouldertop и короткие ноги overhead family, прямоугольные очки, поднятые волосы, бордовая футболка. Frontal idle шире side idle по ожидаемой проекции; высота теперь50px, рядом с LEFT52/RIGHT51, без прежнего провала на6–7px. Headtops `[8,8,8,8,8,8,9,9]`: walk0px bob, run0px; переход к run имеет1px authored variation.

Packing — whole384×512→54×72 NN, единый масштаб9/64 по обеим осям, fixed dx−3/dy−1 во всех8 позах. Ни anatomical reconstruction, ни component warp/mirror нет. Независимая реконструкция всех8 из master с palette43/alpha128 дала точное RGBA совпадение; подсчитанная сумма opaque alpha до/после совпала. Crop отсутствует, alpha0/255,35 opaque colors; hashes/bounds/metadata/input roles verified.

Standing pivot остаётся24,58; exclusive bottom `[58,58,62,59,63,61,64,63]` — стопы контактов выступают ниже стоячего origin. RunA6 доходит до последней строки y63 без потери opaque pixels. Это не выдаётся за проверенный floor contact: actual runtime должен оценить foot slide, perceived root/floor position, loop cut, idle↔walk↔run и direction transitions, особенно DOWN против side rows с sole58. При необходимости исправляется documented whole-pose anchor/integration, не перерисовкой частей тела. По static source признаков обрезки или недопустимой походки нет.

Evidence: `gabar_world_down_preflight_v5a_metrics.json`, `gabar_world_down_v5a_phase_pairs_8x.png`, `gabar_world_down_v5a_walk4_4x.png`, `gabar_world_final_direction_idle_comparison_8x.png`. Manifest CANDIDATE_NOT_IN_PRODUCTION. Production world_sheet на момент inventory отсутствует. V5 FAIL сохранён. Godot/controller/Git/generation/source edits reviewer не выполнял; только разрешённые reports/diagnostics.
