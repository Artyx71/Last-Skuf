# PR association recovery fix

Observed while delivering P03: the new independent phase decision lacked the previous pull_request URL. The controller lost the PR number and created draftPR5 instead of reusing existingPR4. No merge occurred. Draft5 was closed unmerged; canonical history records this, and real branch discovery restoredPR4 and retargeted it to main.

Fix0c7f751: prepare queries open PRs for the exact branch/repository before creating anything; ambiguous/truncated matches block. A registered implementation workspace also publishes repair commits to its matching open PR before CI; mismatched branches block. No force/admin/protection changes. Four regression cases added: existing-number recovery, ambiguous matches, publish repairs, wrong-branch rejection. Actual local41/41PASS in unit_tests_41.log. Game/assets/audio unchanged.

Ordinary predecessor merge dbb8d2b87fbdf6e41f55f92938267764a3f44ed8 preserves the complete0c7f751tree; before resolving predecessor conflicts, currentmain tree equalled original acceptedP02tree3194671. PR4 now targets main e8eaf5c89d372e988fa351267f00d4034856faf9. FreshCI43417181910SUCCESS, requires independent review of actual current head/base before ready/merge. Prior P03attempt2 phasePASS remains historical and is not this new merge receipt. No quality/music assertion or P04 implementation claim.
