# Bootstrap A — independent Lead: FAIL_COMPONENT

Candidate WORK HEAD `6c4f030e28afa7b561a218c44fd240311f0ee2bd`, generated guarded-legacy runner target `d1c347d43877f79c276e606fcd55f2f6c58b62aace8ba4904d32fa2bd31585d5`. **Actual ROOT installation is not approved.** The separate A→B design remains feasible; these findings concern the concrete A installer, not a reopening of accepted RF-Q01 or P06.

Actual source inspected: pinned generator, `cold_bootstrap.py`, exact old02b fixture, reviewed d700 fence, both test modules. Six exact inputs are preserved in source-snapshot/source-freeze.json. The generator verifies both source SHA, inserts the accepted guard and precisely three admission call sites, and requires legacy AST equivalence after removing those additions. Pause controls now cover missing/existing PAUSE and late pending after import. Those are useful implementations of the earlier design conditions.

Actual author run96738d6091444ff2bcb51e9f5526ba35 completed exit0/11.612s; argv/log SHA independently verified. Its saved validation reports217/217, source unchanged, no actual ROOT installation. These positive tests are retained, but they omit the concrete boundary mutations below. They are not a reason to accept false commit/intent ownership.

## Independent reproduction

`python3 -B reports/pre_p07/lead-bootstrap-A-01/probe_boundaries.py` uses the frozen concrete helper against newly created, auto-deleted **TEST_ONLY fake canonical roots**. No Controller, worker, engine, network, real authority or Git calls occur. The helper does perform real filesystem/flock/atomic operations only inside those fixtures. Raw `boundary-results.json` records all results.

| Case | Expected | Actual |
|---|---|---|
| Unchanged valid control | VERIFIED, original state/mode/inode | Correct |
| Change protected state; edit journal protected={} only | Refuse, retain intent | VERIFIED; marker removed; state differs |
| Edit journal target.mode0755→0700 only | Refuse corrupted immutable intent | VERIFIED; installed mode0700 |
| Replace canonical lock inode in before_commit hook | Refuse lost canonical lease | VERIFIED; marker removed; replacement flock acquirable while old fd held |
| Change protected state in after_commit hook | Block completion; retain recovery marker | VERIFIED; marker removed; state differs |

Thus one positive control passes and four contract negatives fail. The generated runner bytes are legitimate; the problem is installer acceptance/recovery semantics.

## BA-L01 — HIGH: journal is its own mutable source of authority

Frozen `cold_bootstrap.py:163` stores `journal_sha256_at_prepare` in BOOTSTRAP_PENDING, but `load()` never compares it. Instead it trusts journal fields such as `protected`, before/target metadata and status afresh. Checking current values against an edited expected map cannot detect the edit. With unchanged marker and correct old/new byte hashes, removing `protected` allows unknown state changes; changing target.mode makes the installer itself violate preservation. Both return VERIFIED and remove intent.

Minimum remedy: separate/pin immutable transaction intent and its complete typed fields from mutable outcome status. Bind the bytes actually parsed to the originally prepared/approved digest on every recovery and commit. Do not simply hash the now-edited journal and accept its own value. Validate old/target metadata relation, protected paths/map and terminal states. A completed retry must not gain permission to reapply using newly edited preconditions merely because status remains VERIFIED. Keep original negative fixtures byte-identical and verify they refuse without untracking/deleting intent or overwriting protected data.

## BA-L02 — HIGH: canonical lease identity is not checked at commit

The helper checks lock before/after replacement, then calls `before_commit`. After that it checks runner/protected bytes, writes terminal journal and removes marker without another lock identity check. The concrete hook unlinks/recreates the lock path: the original fd still holds the old inode, while another maintenance actor could lock the new canonical inode. An independently acquired nonblocking flock succeeds on that replacement during the old lease; nevertheless finish returns VERIFIED.

Minimum remedy: revalidate the same canonical path/fd/device/inode/single-link lease after each mutation-capable boundary and immediately before terminal/marker actions. Lost or substituted lock is BLOCKED, never a successful commit; do not delete the new lock or pretend the old fd controls it. Test the unchanged before_commit replacement case and corresponding final-removal boundaries. The existing test named symlink_and_changed_lock currently exercises runner symlink only; its name does not prove this lock path case.

## BA-L03 — MEDIUM: post-commit mutation can be reported as completed preservation

After `after_commit`, finish only checks marker ID before unlink. A hook writing unknown protected state at that boundary produces VERIFIED and clears recovery intent. It must not silently certify the unchanged protected snapshot after observing this scenario. Recheck the bound immutable intent, runner, protected values, canonical lease and marker ownership before release/completion. If the durable outcome was already written but an unknown mutation now exists, preserve recovery evidence and report BLOCKED; do not restore stale authority/history to manufacture equality.

## Required next step and limits

Fix the helper and add narrow deterministic controls for these four actual counterexamples plus the existing valid control; retain all previous217 results and current FAIL. Re-review the new frozen helper independently. The generated target runner may remain byte-identical if the admission guard is unchanged; no new art/engine/native/gameplay work is needed for this installer fix.

Execution GO additionally requires the actual planned quiescence, exact protected input allowlist, ownership/modes, source hashes, same lock inode, verified backup and cold/no-launcher conditions. This review does not replace them. Bootstrap marker is intentionally not a retroactive old-entrypoint barrier; full B remains a separate transaction, using post-A guarded baseline for rollback and all eleven previous C02 installation cases. Root Game/tools synchronization is separate. stopP06, authority/history/counters, staged four debug-key deletions/local files, P06 PASS/MERGED and readiness/MDS gates remain unchanged.

No production files were changed by this reviewer. Actual ROOT runner is still02b59b6d… . C02, actual bootstrap/install, FULL Production Readiness and P07 remain unapproved. The report is immutable after completion; any new candidate receives a separate review.
