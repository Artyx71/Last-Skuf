# P06 — Gabar UP world preflight v6 / technical v6a

**FAIL_ANATOMICAL_WATCH_HANDEDNESS.** Actual master и оба native показывают часы RunA6 на screenRIGHT/anatomicalRIGHT. Это реальная ошибка самого source, не metadata label. V6 и перепакованный v6a не принимаются; целая поза RunA требует authored correction.

Master SHA `10a8cc94b35e9b43b3908894190775cb6fe781fca685115f84e451d14140be9f`. Native v6 SHA `f37eddea20d0d208440206a5c1876debe0cd713194a2d615c26042b81ebc2d2d`; v6a SHA `080f0bcb47f67c4383713856f85ed97b98a7e30d6f68e48e3e8b7b4698860087`. Ревьюер просмотрел actual full master и v6a native8/inspection, а v6 technical packing проверил RGBA reconstruction. В остальных позах часы на видимой LEFT/screenLEFT либо occluded; новое несоответствие identity/camera не выявлено.

Сам gait читается: вA2/6 anatomicalRIGHT/screenRIGHT колено и передняя поднятая стопа уходят вверх, LEFT/screenLEFT trailing sole виден ниже; вB4/7 роли противоположны. Passing3/5 уже, меняют опору/колено. Нельзя трактовать нижний trailing shoe в backview как ведущую ногу: движение направлено вверх от зрителя.

V6 per-frame sole locking также создаёт walk headtop9/11/9/11 и idle12, меньший native idle46px относительно sides51–52. Общая whole-pose упаковка v6a исправляет scale/anchor: headtops `[5,5,5,5,6,6,6,6]`, idle53px, bottoms `[58,58,61,58,61,58,59,61]`. Однако эта техническая коррекция не исправляет wrongwatch RunA, поэтому её статус также FAIL. Нужна отдельная целая authored pose correction, а не процедурная дорисовка часов.

Для обоих native независимо сверены palette/alpha/NN/whole-cell placement, hashes/framebounds/no opaque loss и generation prompt/master/input roles. V6 alpha0/255,32 colors; V6a34 colors;8 unique каждая версия. Unique count не доказывает animation.

Evidence: `gabar_world_up_preflight_v6_metrics.json`, `gabar_world_up_preflight_v6a_metrics.json`, historical `gabar_world_down_v5a_up_v6a_idle_continuity_8x.png`. Только source preflight, без runtime/phase approval. Записи только разрешённый reportdir; author/runtime/source не затрагивались.
