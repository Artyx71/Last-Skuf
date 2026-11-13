# P06 Character expansion — обязательный контракт

См. planning/P06_TASKS.md и независимый reports/phases/P06/scope-review-initial/contract.json. Все критерии ниже обязательны; план и наличие PNG не являются приёмкой.

- Character definition: actor_id/display_name/portrait expressions/frames/move/equipment/ability/context и finisher profile. Unknown ID/emotion/context отвергаются. Existing Yakuza path/CH01 сохраняются.
- Input→windup→contact→recovery единым physics clock; графика отображает фазу, не начисляет damage. Каждый action имеет eligibility, target/range/facing/LOS/environment, cooldown/cost/cancel/reaction/audio IDs. Повтор callbacks/reset/reload не повторяет damage/kill/reward.
- action8/direction: melee windup/contact/recovery, interact, hurt, down, death, ranged contact. finisher8/direction: shared windup, пять разных category contacts, shared recovery, signature contact. Shared poses явно указаны; additional movement requires actual drawn frames. Death hold и static portrait не называются многофреймовой анимацией.
- Данные не дают всем героям любое оружие. Timka peaceful_present не выполняет prime grapple; context хранится в доверенной scene definition. Новый sandbox context означает reset fixture. Unknown save cannot authorize prime.
- Девять NPC portrait sets: neutral/angry/surprise/hurt/catchphrase, 160×160, технический alpha/palette/native inspection. Каждая фотография сверяется со своим hash; сырьё не включается в Git/export/reports. World 48×64, pivot24,58, 4 directions; every source cell accounted, bounded palette/alpha/coverage.
- Sandbox dialogue использует отдельное persistent viewing-state и не меняет StoryState, event ledger, campaign unlock/reward или сохранённый resource/line CH01. Проверка вход/выход/process restart обязательна. Audio reuses accepted fictional bleeps without voice identity claims.
- ART принимает likeness/согласованность/реальные анимации; GAMEPLAY — Input, contact timing/readability/cancel; QA — negative cases, settings invariance, effect lifetime/caps, regressions/performance/builds; Lead самостоятельно связывает frozen source и evidence SHA. Никакого author self-PASS.
