# Последовательное исполнение фазы

Читай AGENTS.md, specs/, planning/PHASES.md, текущие решения и automation/REVIEW_LOOP.md. Основной контроллер хранит единственное authoritative состояние automation/phase_state.json; snapshot в worktree не начинает историю заново. Не сбрасывай старые PASS/attempts/артефакты. Не запускай subagents, параллельный Codex или рекурсивный runner.

Работай только в назначенной фазе/изолированной phase/* ветке. Используй существующий CombatSystem/action clock/AI/AudioDirector. Оригинальные sprites/animations/audio должны быть реальными файлами с provenance; placeholders не считаются выполненной задачей. Осмысленные regression и actual engine captures обязательны. Audio signal analysis отдельно от фактического listening. Сохраняй source/evidence/commits и отчёт reports/phases/<PHASE>/implementation.md, не переписывая старые attempts.

Учитывай findings предыдущего FAIL. После конкретного исправления проведи затронутые проверки. Не подделывай review/CI/выводы слушателя. Коммить готовую реализацию/доказательства; PR/push/merge управляет единственный контроллер после privacy check, отдельного read-only Lead и CI текущего SHA. Автор не утверждает свою фазу.

Владелец разрешил публичный Artyx71/Last-Skuf и conditional squash merge в main; точные разрешения automation/AUTHORIZATIONS.json. Rawphotos, private secrets, real voice cloning, расходы, force push/admin bypass и отдельный release не разрешены. Не менять visibility/protection/billing в обычном phase run.

P04G обязательна до P07; character styles зависят от соответствующих P06 ability/art gates. Не начинай21главу до настоящего vertical slice и finisher/reaction/impact baseline PASS.
