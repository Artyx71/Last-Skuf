# P06 — Gabar UP world preflight v6c (master v6b)

**ACCEPTABLE_UP_DIRECTION_SOURCE_CANDIDATE.** Whole-pose authored correction исправила RunA LEFTwatch, общий standing anchor сохраняет спокойную голову и читаемые opposite leg phases. Нового source blocker не найден; v6/v6a FAIL история не меняется. Решение source-only, без runtime/fullworld/P06 approval.

Native SHA `af761825286d105716b57ca0c248d51c56d4a9e88f1989e19edcd81a71138167`; corrected master v6b SHA `3f50f23277d79198ec522347f38855a6223d313e38b6b7f2f29c319f1a374d22`. Ревьюер просмотрел corrected master, actual native8/inspection4x, phase pairs8x, walk4filmstrip и4direction standing comparison.

RunA6 теперь несёт часы на поднятой вперёд anatomicalLEFT/screenLEFT руке; anatomicalRIGHT/screenRIGHT рука сзади голая. RunB7 даёт обратный обмен, часы остаются LEFT/screenLEFT. ContactA2/B4 согласуются с тем же handedness. PassingA3 wrist может скрываться shoulder/body, при этом нового watch на RIGHT нет; passingB5 LEFTwatch виден. Ошибка старого6 устранена actual pixels.

ВA contact/run впереди вверх идёт RIGHT/screenRIGHT leg, а ниже видна trailing LEFT/screenLEFT sole; вB lead/trailing меняются. Широкие контакты2/4, узкие проходные3/5 и обе run poses различимы на48×64. Крупная crown, shoulder tops, burgundytee, короткие тёмные pants/white-edged shoes сохраняют общий overhead family. Backview не обязан показывать очки, причёска/ширина плеч/wardrobe согласуются с Gabar и принятыми направлениями.

Whole384×512→54×72 NN, scale9/64 по обеим осям, фиксированные dx−3/dy−2. Headtop5 во всех8; idleheight53 рядом с LEFT52/RIGHT51/DOWN50. Exclusive feet `[58,58,61,58,61,59,59,61]`; opaque crop отсутствует. Все8 actual reconstructed RGBA совпадают с master+palette+threshold+whole translation; alpha0/255,36 opaque colors,8 unique; manifest bounds/framehash/prompt/master/input hashes verified.

Хотя edit targetedRunA, все8 native cells изменились относительно v6a (`[579,599,564,508,502,502,712,507]` changed pixels). Поэтому все8 осмотрены заново; нельзя переносить approval по обещанию неизменности других клеток. Texture boil, footslide, loop cut, direction/idle/run transitions и floor placement при выступающей ниже standing58 стопе ещё требуют actual playback.

Evidence: `gabar_world_up_preflight_v6c_metrics.json`, `gabar_world_up_v6c_phase_pairs_8x.png`, `gabar_world_up_v6c_walk4_4x.png`, `gabar_world_final_direction_idle_comparison_8x.png`. CANDIDATE_NOT_IN_PRODUCTION; production world_sheet отсутствует на момент inventory. Reviewer не запускал Godot/controller/generation/Git и не менял source; только разрешённые reports/diagnostics.
