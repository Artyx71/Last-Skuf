# Read-only QA diagnostic received from /root/lead_autopilot_p03

Two actual Windows reports confirm failure of the harness idle precondition, not a proven combat/reset defect. Native02 drifted from reset432,544 to752,516 and entered phone dialogue; retries1–9 reused old latency/snapshot. MouseMotion was processed, but physical movement input is not proven. A physics boundary alone does not explain320px drift.

Recommended: release movement on every walk exit and before/during idle; observe completed physics ticks in idle checks, record commanded/observed input/position/state/ticks; fail immediately on unexpected input/movement/dialogue/no new death. Do not modify combat/AI/reset or warp actors. Preserve failed reports and rerun an instrumented Windows replay in fresh output. General walk/action cadence should not be changed without tick measurements. Reviewer ran no game or edits in this diagnostic.

Implementation adds that bounded QA instrumentation only; independent acceptance remains pending.
