# Прослушивание новых звуков добиваний C01

Это реальные записи AudioDirector/PulseAudio на source f615b2e, не синтетическая склейка. Отдельный source signal PASS не подтверждает художественное качество. Новые SFX отсутствуют в ранее принятой DEV06.

[20 звуков отдельно (~12 секунд)](native-01/replay/solo_cues.wav) · [Игровые добивания с музыкой (~111 секунд)](native-01/replay/runtime_mix.wav) · [Нагрузочный микс (~6 секунд)](native-01/replay/stress_mix.wav)

Для прототипа требуется оценить разборчивость контакта и характер героя/оружия, отсутствие неприятных резкостей и уместность громкости. Намеренная тишина между одиночными cues не является dropout. Тимка present не получает ударные акценты прайма. Ни агент, ни signal checker не заявляют, что прослушали эти записи.

| Начало в записи, с* | Герой | Категория | Cue |
|---:|---|---|---|
| 0.10 | Габар | unarmed | `finish_gabar_unarmed` |
| 0.70 | Габар | blunt | `finish_gabar_blunt` |
| 1.30 | Габар | firearm | `finish_gabar_firearm` |
| 1.90 | Олежка | unarmed | `finish_olezhka_unarmed` |
| 2.50 | Олежка | blunt | `finish_olezhka_blunt` |
| 3.10 | Олежка | sharp | `finish_olezhka_sharp` |
| 3.70 | Тимка в прайме | unarmed | `finish_timka_prime_unarmed` |
| 4.30 | Тимка в прайме | blunt | `finish_timka_prime_blunt` |
| 4.90 | Тимка в прайме | environmental | `finish_timka_prime_environmental` |
| 5.50 | Рыжик | unarmed | `finish_ryzhik_unarmed` |
| 6.10 | Рыжик | blunt | `finish_ryzhik_blunt` |
| 6.70 | Рыжик | environmental | `finish_ryzhik_environmental` |
| 7.30 | Тега | unarmed | `finish_tega_unarmed` |
| 7.90 | Тега | blunt | `finish_tega_blunt` |
| 8.50 | Тега | environmental | `finish_tega_environmental` |
| 9.10 | Паша | unarmed | `finish_pasha_unarmed` |
| 9.70 | Паша | blunt | `finish_pasha_blunt` |
| 10.30 | Паша | sharp | `finish_pasha_sharp` |
| 10.90 | Паша | firearm | `finish_pasha_firearm` |
| 11.50 | Паша | environmental | `finish_pasha_environmental` |

*Время вызова playback относительно начала capture; есть неопределённость одного блока микшера. Это не измерение аппаратной input latency.

Статус: ARTISTIC_NOT_LISTENED. Новые 20 cues ещё требуют независимой технической приёмки реального PCM/exports и художественной приёмки. Полная P06/P07 этим отчётом не принимаются.
