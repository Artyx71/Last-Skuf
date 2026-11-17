# CH16 — независимый Narrative и paper-contract review01

**CHANGES_REQUESTED_COMPONENT_DRAFT_REVIEW_ONLY.** Новый draft в целом выполняет геометрическое обещание CH12: accept получает сервисный вход без обязательного E1, refuse — главный вход и отдельный reclaim encounter. Это реальное различие задач/комнат, а не две реплики при одинаковом пути. Но предметная причинность CH12→AM2 и точный порядок обязательного pickup/CP1/final ещё требуют двух коротких документных исправлений: один HIGH и один MEDIUM.

Источник — фактическая CH16 SHA `0e5c1998cc00bb7090f9d8c2e8c40afa80dbe86a008d229820bc39585c203575`, заявленный WORK HEAD `6693e3b62bb3999b6c4e77777a2155fdb52be627`. Git не вызывался; authority — exact bytes/SHA, snapshots и сверка в конце. CH12 SHA `16b7c1ed056cad8a424c6fddda01d94387451261a7ab1511ab62269aad5e42a2` совпадает с принятой Narrative pilot03. Старые решения не меняются. Автор — ROOT; reviewer не реализовывал draft.

## Что подтверждено

Registry содержит именно CH16_THE_AMERICAN_NIGHTMARE / EV_CH16_COMPLETE,16/16,present,PASHA,EV_CH15_COMPLETE; точная дата остаётся пустой/production_pending. Draft не выдумывает календарную привязку, не объявляет planned сцену готовой и не подменяет ложное подозрение Габара раскрытием Кабана.

D02 sealed в CH12: здесь нет нового вопроса/отношений/backup award. Ветка по flags.pasha_shared_evidence сверяется с choices.D02; существующая StoryState.validate действительно восстанавливает историю и отвергает derived-state mismatch. Отдельная scene-entry policy для будущей главы ещё должна быть реализована, а не считается доказанной по prose. Private reclaimed copy не равна surviving backup друзей. Canonical routes REAL_PRIME не становятся доступны только из-за pickup; первичный WIFE_CALLING не блокируется. Точные registry/routes SHA зафиксированы.

План даёт accept AM1→AM3→AM4→AM5, refuse AM0→AM2/E1→AM3→AM4→AM5. E1 только refuse; общий E2 не заставляет accept повторять reclaim. AM4 две противоположные128px щели соответствуют координатам. Различаются офисный обход/пересечение LOS, switchback и открытый двор; actual nav/AI/weapon range/читаемость или уникальность всех21 глав этим не доказаны. Новых боссов, HP inflation, ожидания или бесконечных волн нет.

Паша сохраняет P06 moving-shot, магазин4, обычное WASD/Shift и сценовые unarmed/firearm. Отмена/прерывание и очистка pending jobs соответствуют существующему action contract; dash immunity, hacking или чужие способности не добавлены. Габар получает только показанный фрагмент карточки и не спасает игрока новым всезнанием. Русские candidate реплики сохраняют голос; это ещё не принятые structured dialogue resources.

## N-MDS-CH16-01 — HIGH: предметный мост и причина входа

CH12 B3/refuse оставляет полную копию на рабочем ПК CyberX для сделки; accept отправляет отдельный носитель друзьям. CH16:18/30 уже требует вернуть собственный оставленный носитель со стола AM2 в административном месте. Не указано, то же ли это место/диск, кто и когда перенёс его, как Паша знает адрес/след предмета и зачем добровольно приходит на опасную встречу после тревоги CyberX. У accept помощь названа доступом, но её наблюдаемый источник/поступок союзника отсутствует. Spawn/lever по flag ещё не объясняет помощь в истории.

Минимальный fix — короткая entry/custody последовательность, которая свяжет рабочий ПК/носитель CH12 с AM2, объяснит знание/мотив Паши и конкретный способ полученного через союзника сервисного доступа accept. Можно прямо назвать тождество места/диска; если это другой объект/место, нужен понятный перенос и наблюдаемый след. Не требуется новый named villain, новая дата/decision/flag, дополнительное доказательство или новая механика. Reviewer не назначает эту отсутствующую историю вместо автора.

Это неполный причинный контракт, а не уже установленный новый неутверждённый канон. После его заполнения следует проверить, что обе ветки ссылаются на один последовательный предметный след, а возвращённый private carrier остаётся локальным objective и не выдает evidence.pashas_backup.

## N-MDS-CH16-02 — MEDIUM: missed pickup и once predicate

Строки18/20 требуют reclaim до общего выхода;31/56 дают CP1 после E2/card check и закрывают AM2→AM3. Условие carrier для постановки CP1 или обратный доступ до получения предмета не названы. «CP1 сохраняет наличие» не определяет, допустим ли false. Трасса refuse без F у носителя→AM3→E2/card→CP1 потому неоднозначна. Само закрытие двери не доказывает runtime softlock; конкретной runtime карты нет.

Минимум: явно включить local_carrier_reclaimed для refuse в CP1 predicate либо назвать гарантированно обратимый путь/открытие двери до pickup и точный момент её закрытия. Согласовать retry snapshot. Финальный EV_CH16_COMPLETE должен иметь один once-owner и predicate exit+card_checked+variant objective; описать отказ преждевременного завершения, пропущенный pickup и сохранение event/reward при skip/reload/ошибке записи. Это локальное состояние, не повтор D02 и не новый глобальный evidence grant. Проверить три paper trace: accept; refuse с pickup; refuse с пропуском и возвратом.

## Честность статуса и дальнейшие gates

Новая сцена/диалоги/score отсутствуют, названия ресурсов не выдаются за файлы. Artwork перечислен как required, reuse требует placement review; в игровую карточку не переносятся фото/личные данные. Music mapping и retry/duck/listening obligations заданы, но художественное качество/actual transitions не принимались.20–35мин явно NOT_MEASURED, взаимоисключающие варианты не суммируются, ожидание ради диапазона запрещено. Эти ограничения корректны.

Это review **одной новой MDS**, а не phase/release acceptance. CH12 Narrative03 не переоткрыт. Её будущий CH16 handoff геометрически начат содержательно, но закрывать его Narrative follow-through до HIGH причинного fix рано; real production H02/scene-policy/playtest также остаются отдельными. Отсутствие runtime evidence не использовано как причина FAIL данного draft; два findings относятся к самому тексту.

Нет Narrative_REVIEWED для текущей CH16, Lead/Gameplay/ART/Audio/QA, all21MDS, Readiness, P07 implementation, mass-production, runtime/phase/merge/P08 approval. ROOT A installation и C09→P08 не входят в замечания. Reviewer не запускал engine/Controller/generator/Git и не менял Game/code/assets/state/source. Только owned report, exact snapshots, диагностическая арифметика и read-only source inspection. После verdict packet immutable.
