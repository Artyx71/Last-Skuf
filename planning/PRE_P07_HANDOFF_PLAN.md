# READINESS-C02: безопасная передача ROOT

Техническая установка A/B/C завершена и независимо проверена17.11.2026. Исторический план ниже сохранён как описание шагов; это не разрешение массового производства.

Фактический итог: ROOT runtime runner d700e88e, schema12; Game533/tools54 из Git f832. A/B/C повторно не применять. Независимые actual receipts: `reports/pre_p07/lead-bootstrap-A-installed-01`, `lead-runtime-bundle-B-installed-01`, `lead-canonical-source-C-installed-01`. Последний содержит отдельный `handoff-capability-decision.json`: technical safe_handoff PASS, полный Readiness/21MDS/P07 не приняты. Fresh canonical SOURCE import/boot/input72/72. State/index/refs и пользовательские профили сохранены. StopP06 остаётся.
P06 полностью принята/merged; её результат не переоткрывается. Единственный автор
работает в WorkP07, reviewers проверяют реальные изменения отдельно.

1. **Admission fence.** Любой pending handoff блокирует импорт/новый вход
   `status/pr/resume/run/task`. Уже загруженный Controller проверяет pending и
   fingerprint runtime перед получением lease и после flock. Отдельный worktree
   не становится второй authority. Проверить на временных roots без настоящего GitHub.
2. **Cold runtime transaction.** Отдельный maintenance-процесс без импортированного
   Controller удерживает прежний executor.lock inode. До записи — drain автора,
   workers и старых экземпляров; durable backup/modes/intent/journal; точные
   before/target SHA и запрет symlink/path substitution. Прерывание/rollback
   восстанавливают только принадлежащие операции файлы, не authority/history/PID.
3. **Canonical tree.** Проверить всю Root Game/toolchain против подтверждённого
   P06 snapshot. Согласовать ROOT HEAD/index/dirty/untracked без reset/stash/clean,
   потери пользовательских данных или публикации raw photos. Одного Python bundle
   недостаточно: До C Root Game была P05; фактическая C установила frozen P06 и полный verifier.
4. **Fresh process.** После полного commit verification завершить старый процесс.
   Новый процесс проверяет реальные module paths/SHA, config/schema/prompt/worker
   и read-only status. Не использовать init/reconcile как проверку без записи.
5. **Независимая приёмка.** QA воспроизводит required interruption/rollback cases;
   Lead проверяет фактический journal, Root файлы, source/authority continuity.
   Только отдельный итоговый verdict закрывает C02. stopP06 сохраняется до
   полного Readiness и21 MDS, даже после успешной установки runtime.

Исходный независимый preflight сохранён в ROOT
`reports/pre_p07/qa-root-handoff-preflight-01`. Его15 проверок — совместимость
чтения, а не установка. Новые результаты пишутся отдельно, старые не редактируются.

Принятые P06 документы/исходники не переписываются. Все испытания установщика
сначала выполняются в auto-deleted временных копиях. Реальный ROOT изменяется
только после review конкретного tested bundle и проверенного механизма recovery.
