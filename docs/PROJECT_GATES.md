# PROJECT GATES — evidence-based acceptance

## Policy
Every phase has PASS/FAIL/BLOCKED status, decided by `Lead Reviewer` in independent context. Review must compare `specs/` to built artifacts, not trust author claims. Only PASS advances; FAIL loops with finite attempts; BLOCKED escalates only for missing permission, missing platform/software, unresolved creative likeness dispute or inaccessible external tooling. Reports stay in repository; user is not required to ferry them between assistants.

## Definition of done for every phase
- Scope traceable to requirement IDs and test cases, with clear boundary to next phase.
- Relevant code committed, tests run with exit codes and logs, screenshots/audio reviews named, no fake success.
- New generated assets individually inventoried with hashes, source provenance, licensing and whether privacy/likeness cleared.
- Playable build for major milestones: Linux and Windows as declared, or mark platform-specific test BLOCKED without false PASS.
- In-game language/plot/Ossetian phrase checks, user preferences respected.
- Independent lead reviewer `reports/phases/Pxx/decision.json` PASS + signed reasoning + evidence links. Avoid unreviewable green checkmarks.

## Reviewer scoring matrix
| Domain | Must show |
|---|---|
| Gameplay | video/replay and tests prove lethal/readable combat, unique abilities, weak-yet-playable Yakudza, instant reset |
| Story | event ledger, reachable endings, six decisions, POV consistency, complete scenes for committed milestone |
| Art | source dimensions, screenshot in Godot, visual comparison to correct private photo, readable pixel clusters, no generic AI portraits |
| Audio | actual WAV/OGG, listening report, no clipping, loop/transition analysis, licensing provenance |
| Engineering | Godot smoke, lint/tests, exports, save/load migration, performance capture |
| Privacy | raw photos absent from committed/public files, no unapproved upload or publication, fiction disclaimer |

## Exit/stop conditions
- Never mark successful audio generation because a prompt or MIDI plan exists.
- Never mark likeness passed without independent visual examination. Programmatic check is only structural.
- Never mark a Windows runtime test done if only Windows export files were built on Linux.
- Never advance to next phase based on self-generated author approval or if hard-blocking CRITICAL/HIGH issues remain.
- If the current session ends, persist next step in `reports/STATUS.md`; a later Codex run may continue. No promises of background execution.
