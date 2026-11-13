# AUTO-PR-OWN-01 remediation candidate

Independent Lead reproduced a registered-workspace/no-number/no-existing-PR path that could publish/create before checking record.branch. The ownership check now runs at the start of prepare, before discovery or any publish/create; unregistered branch discovery also requires the requested phase prefix. Existing known historical PRs without an authoring workspace can still be retargeted from the root controller without publishing its branch.

Two additional meaningful regressions ensure zero GitHub API calls and zero publish on registered ownership mismatch or unregistered wrong-phase request. Local43/43tests PASS, including the real SIGKILL fixture. Game/audio/source assets unchanged. This fix requires fresh exact-head CI and independent handoff review before merge and before starting P04. No self-PASS for the fix.
