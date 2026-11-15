# Instructions for Codex / agent team

**Project:** АЫАЫ: Последний скуф. Always read README, specs, phases, security policy, and current review decision before changes. Russian documentation/dialogue; consistent English identifiers in code.

## Execution contract
- Preferred model: GPT-6.1 Sol **when available**; do not pretend a specific model/agent interface exists when unavailable.
- Work autonomously within a running Codex session: plan → implement → test → collect artifacts → independent review → fix until PASS → next phase. **Do not require the user to paste intermediate phase reports into another chat.** Store reports in `reports/phases/` and ideally PR descriptions/issues.
- Never interpret an agent-produced report as proof on its own. Inspect code, generated assets, screenshots, tests, audio files, build outputs and licensing manifest.
- Reviewer must be independently tasked, not identical to author. If the Codex environment cannot spawn independent agents, use a separate review context if possible; otherwise mark INDEPENDENCE_BLOCKED and do not falsely claim independent review.
- Pass phase gates according to `docs/PROJECT_GATES.md` and `automation/REVIEW_LOOP.md`. FAIL => concrete remediation tickets and rerun. Missing evidence => BLOCKED, not PASS. Review loop limited by configurable attempt budget; persistent failures => escalate in repo issue/report.
- A Codex session is **not** a guaranteed always-on daemon. When sessions end, persist full state and next-run instructions; CI can run repeatable checks, but advancing implementation requires an active authorized executor or explicitly configured runner. No unapproved silent external deployments.
- Take small commits with tests. PR by phase. Check target repo availability and credentials before pushing. Never force-push/overwrite user changes without approval.
- Start with infrastructure and playable vertical slice, NOT 21 simultaneous missions. All third-party art/music permissions documented.

## Agent roles
`agents/LEAD_REVIEWER.md` controls quality gates; other roles: gameplay, narrative, art, audio, QA, architecture. Reviewer can demand changes, not silently weaken approved criteria. Optional phase reviewer can evaluate evidence without sharing private photo files externally.

## Privacy and permission
- Raw photos are private, tracked separately from game assets. Do not `git add` raw images or ZIP by default; don't upload them to public GitHub or third-party generation services without permission from the depicted people and authorization from project owner.
- Don't publish identifiable depictions or clips of people without permissions. User's fictional satirical depiction of the father as a crime organiser does **not** establish any real allegation; include disclaimer in game and distribution plan.
- Don't install system-wide software via sudo without explicit permission. Do not purchase licenses, call paid generators or incur costs unapproved. For missing art/audio capabilities produce a precise requirement and stop gate rather than fabricate finished files.
