# Runtime bundle B2e220 — independent Lead: FAIL_COMPONENT

Frozen candidate2e22039a49b843f4f0959d18941aeba654fd2ada. **No actual ROOT B execution is approved.** Actual A remains installed/verified; its immutable receipt147c691e… must not be edited to accommodate this candidate. Source/tests/seven payloads and the genuine receipt are preserved in13-source snapshot. ROOT Game remains cold, stopP06 unchanged; P06 PASS/MERGED is not reopened.

Actual author runa95ad28763104c81ab34ae79fc9255f9 receipt0/log/argv verified; validation reports229/229. Source has useful safeguards: exactly7 target hashes, dependencies before runner, reverse rollback, immutable same-buffer intent parsing, repeated load checks before copies/commit/cleanup, post-A runner rollback requirement and retained B-start ledger. Tests genuinely cover18 child os._exit scenarios across9 copy/commit boundaries and pending CLI/failure cases in fake roots. Positive results are retained, but they do not cover the two concrete failures below.

Independent `probe_B_entry.py` executed only in auto-deleted TEST_ONLY fake roots. No actual RootController, engine, network, Git or production mutation occurred. Raw facts are in B-entry-results.json.

## B-L01 — HIGH: real installed-A receipt is rejected

`verify_a()` requires a truthy reviewer field. The genuine installed-A decision has typed role `INDEPENDENT_LEAD_ACTUAL_INSTALL_VERIFIER`, scope, actual_A_verified and installed_runner_sha256, but no reviewer property. Its exact bytes/SHA147c691e86b13050ce3929816e53230198190c5d74fa02bab1d7f565a1a82308 were copied without modification into the fake root. Verification rejects it with “A component/execution GO is not installed-A verification”. Existing test receipt invents reviewer=INDEPENDENT_TEST_ONLY and hides this wire mismatch.

Minimum fix: define/validate the actual immutable installed-A contract, including role/scope/actual verified fields and its hash-bound post-A baseline, rather than requiring a property absent from the published artifact. Use a genuine byte-exact147c wire control. Do not rewrite147c or treat an arbitrary component/execution GO as installed verification. The helper must accept the real verified prerequisite before an actual B plan can be useful.

## B-L02 — HIGH: durable prepare can become unrecoverable and does not stop a second begin

Fault injection denies only the HANDOFF_PENDING write, after immutable intent, PREPARED journal and B-start ledger were successfully written. Runtime and protected data remain exactly post-A; no mixed-code or authority damage is claimed. The old transaction is durably PREPARED, ledger includes its ID, but marker is absent.

Both normal resume and rollback call load_bundle and refuse with “Pending bundle marker missing”. However begin_bundle checks only current pending markers; it permits a second new transaction while the first PREPARED entry remains unresolved, appending a second ledger ID. Existing os._exit tests begin after marker creation has already succeeded, so before_first_replace does not cover this preparation failure.

Minimum fix: make the preparation/marker bootstrap recoverable under the same lease, and prevent new begin while a durable ledger-owned transaction is unresolved. For the demonstrated no-copy state, an explicit verified repair/abort may check all before/protected/immutable ownership and reconstruct its marker or record a complete owned rollback; it must not bless unknown partial mutations or delete B history. Preserve the B-start ledger after verified abort/rollback so A cannot be silently unfenced. Test failure/exit around journal/ledger/marker preparation, not only target replacement. No new engine, game or full C02 scope is needed.

## Scope and continuation

These are actual fake-root code/contract counterexamples, not a claim that ROOT B started. Only code-only B, its eleven previously required compatibility/interruption/lease/state conditions are reviewed here. Actual RootGame/tools sync, FULL readiness and P07 are separate. The old post-A baseline remains the correct future rollback baseline.

Next: fix on a new frozen source, keep the current229 evidence and this FAIL immutable, repeat the genuine-receipt and marker-preparation controls, then obtain independent QA/Lead component and exact-plan execution review. A component PASS alone cannot authorize actual B. On unexpected source/state/ownership changes, preserve journal/ledger and require independent recovery; do not reset/stash/clean or roll back authority/history. No workaround deleting the ledger or changing signed A evidence is accepted.
