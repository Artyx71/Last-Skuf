What this change does: moves the previously reviewed bonus sidecar into production Game source and connects the real StoryService, journal, and Bootstrap return path. Production bonus scene paths remain empty; future positive eligibility/scene binding is an explicit isolated double. No new bonus level is implemented.

The original frozen version 0fe3ac1d2989c02b3e81d95e53d2a7ffdcc6335d does not pass this adapter review. Canonical operation 8b5cbddd1688403a9d9a1fa568d57c69 completed with exit1 and was consumed. The independent source snapshot matches all seven recorded critical inputs; the complete 622-key source map is unchanged before/after. Receipt argv and output hashes match.

The moved core passes its actual isolated import/101 checks, crash recovery, and old story regressions. Live headless has 20/22 passing checks. Actual packed test-host commit, duplicate once, lifecycle revocations, and normal leave→Bootstrap return all pass. These are useful bounded positives, executed by the sole Root Controller worker, not a reviewer-launched engine.

MEDIUM BONUS-LIVE-Q01: keyboard row21 selection fails. Enter then changes scene and the test dereferences a freed menu. The driver must establish the real selected row before Enter and safely abort an invalid selection. Native journal, CLI-return, and old native StoryReplay stages were not reached. This failure neither proves that a disabled bonus launched nor establishes that actual keyboard/mouse UI is correct.

MEDIUM BONUS-LIVE-L01 (independent Lead cross-reference): original begin_chapter selects a replay fork, while Bootstrap/menu has no canonical-session restoration. Bonus authority rejects session!=store. The fixture manually toggles session back, so it misses real completed-main-replay→Bootstrap cleanup. Add the actual safe-menu restore boundary and a targeted real CH01 replay return with the explicitly future-only eligibility double. Do not copy replay facts into canonical progress.

Current WORK may advance under its sole author; this verdict refers only to the immutable commit and preserved actual attempt01. No implementation was modified by QA. Older core acceptance and its namespace failure/fix remain preserved.

Verdict: FAIL_COMPONENT for the original live adapter candidate. Fix the two bounded items and review fresh evidence separately.

Not checked: fresh native keyboard/mouse journal behavior, actual CLI return precedence, current old native StoryReplay regression (not reached), real positive CH10/CH14 unlock, actual bonus levels/host gameplay, production ROOT installation, packaged exports, full H05/Readiness/P07, audio quality, physical input latency, or campaign completion. No reviewer Godot/Controller/Git/state/source writes occurred; writes are report-only.
