# P06 — индекс раннего независимого portrait preflight

**9 static source candidates reviewed. Не PASS P06, не runtime approval.**

Локально сверены собственные9 фото и actualnative:45 базовых статичных эмоций. Дополнительные36 source drawings учитываются как unused, motion не одобрен. Все81 native RGBAклетки различны также между актёрами. Все текущие native hashes по-прежнему совпадают с проверенными кандидатами; provenance reference/prompt/master hashes во всех9 generation metadata совпадают с фактическими файлами.

| Actor | Native SHA256 | Report |
|---|---|---|
| gabar | `9f7ce3e913a8550d82cdda32463c3d94496c4044d49cb6a4388d4a059e89c44d` | [gabar_review_v2.md](gabar_review_v2.md) |
| olezhka | `6dc278dd2cc6c2956e5878e65a638bf9c7516fa594c7c29a70200fd047c1e29c` | [olezhka_review_v1.md](olezhka_review_v1.md) |
| timka | `c1647b81e9005c270260587841007255e2092c2db2cef0720854a6e332c81606` | [timka_review_v1.md](timka_review_v1.md) |
| ryzhik | `37f2aaa4bb2654b6290770b7a1e66dafc9f0d17c3c65319c65ed2e98bcde5320` | [ryzhik_review_v1.md](ryzhik_review_v1.md) |
| tega | `5295e29d8ef86ea830a4ffe8855fdde566c7e53b79ad5483e1014bdea5d3a1e6` | [tega_review_v1.md](tega_review_v1.md) |
| pasha | `a50abd0d060c2d01118697e1e8bf3ec69f301bd02f3adde4cba125a435932cf7` | [pasha_review_v1.md](pasha_review_v1.md) |
| kaban | `522fdb3196b4e8c62632479b0344a18a69eb69181ec383584155465cf66c933c` | [kaban_review_v1.md](kaban_review_v1.md) |
| ellana | `519a1a3cccfeb5c34accd608be5179c46aa92b3f6556994d356792bd7e77c803` | [ellana_review_v1.md](ellana_review_v1.md) |
| elya | `2243af0f10e5fbbd61cd9cf3e6019e53178e5f6f779552c1122082f17ad244b2` | [elya_review_v1.md](elya_review_v1.md) |

Kaban: LOW_MARGIN_NEUTRAL_ANGRY_SEPARATION. При native160px различие бровей видно, но pair0↔1 нужно отдельно проверить в actual dialogue UI; при потере различия нужны новые целые expression drawings и review.

Ellana master low-alpha hem fringe и Elya master low-alpha greybackground не сохраняются в проверенном production native; отдельные white/black diagnostics и измерения в отчётах. Старые Gabarv1 hashes/report сохранены как история.

Остаются runtime five-expression captures, filtering/screen-size/speaker bindings, world/portrait consistency и movement/action/finisher art, actual controls и frozen-source final independent gates. Фаза P06 не заморожена и не принималась этим индексом.

Machine-readable exact inventory: `portrait_candidates_index_v1.json`. Rawphotos не включены в этот каталог/derived strips. Ревьюер не запускал Godot/controller/generation, не менял Git или source.
