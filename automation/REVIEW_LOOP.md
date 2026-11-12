# Automatic review and phase progression protocol

## Desired behavior (during active Codex execution)
`select phase → decomposed tasks → implement → run validation → capture evidence → reviewer → FAIL remediation loop OR PASS → next phase`. Handoffs are internal to Codex task orchestration; the user should not send reports back and forth.

## File protocol
- Executor produces `reports/phases/Pxx/implementation.md`, `artifacts.json` listing actual outputs and SHA-256, logs/screenshots/audio evidence.
- Reviewer independently produces `reports/phases/Pxx/review.md`, `decision.json`.
- Controller uses `automation/phase_state.json` to store `active_phase`, `attempts`, `blocked`, `last_commit`, `next_action`.
- After PASS only: update active phase, create tasks for successor, record phase PR/status and proceed if session and permissions available.
- After FAIL: assign precise fix requests, allow up to three repair/review cycles. After third failure stop and create BLOCKED report/issue; never infinite loop.
- BLOCKED (missing permission/license/tool/reviewer) pauses impacted work and logs actionable dependency. Unaffected work may proceed **within phase** without claiming PASS.

## Autonomous environment limitation
A markdown prompt does not create a background daemon. For true unattended continuation across sessions you must explicitly configure a persistent Codex runner / GitHub Actions with supported credentials, quotas and authority. GitHub Actions can run deterministic CI and publish check artifacts, but cannot silently substitute for an authorized code-generating agent. The workflow should surface a concise issue/PR comment to owner only when blocked or release approval required; routine details remain in repo.

## Guardrails
- Reviewer should have separate conversation/context and not be the author; if multi-agent unsupported mark external check pending.
- GitHub PR per phase, atom commits, no auto-merge without explicit authorization. No raw photo upload.
- Use structured decisions, no emoji or optimistic unverifiable completion statements.
