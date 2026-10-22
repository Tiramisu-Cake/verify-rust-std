The shared closure inventory proves committed file identities and bytes, but cannot establish that the final encoded payload/configuration fits transport caps. The existing committed-source client preflight must check those final caps.

# Registration plan — SORT4-ACTUAL-SELECT-2026-10-23-R21

This bundle is **PREPARED_NOT_REGISTERED**. It does not authorize or dispatch a Cloud Build.

- Owner/task: `select-sort4` / `select-callee-acceptance-autonomous-2026-10-23-r21`
- Branch and selected HEAD: `research/night-select-sort4-cloud-2026-10-09` / see `bundle.json`
- Baseline checkpoint: `44bfbdecdd61c96059fe76d8b8bff690e15dd5d6`
- Window: T0 `2026-10-22T19:54:55Z`, main deadline `2026-10-22T21:54:55Z`, absolute deadline `2026-10-22T22:24:55Z`
- Budget: `3600` Cloud seconds, max timeout `1200`, report reserve `240`
- Lane: `o26-select-callee-r20`
- Profile: new draft `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-SELECT-R21-PROFILE-2026-10-23.json` from `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json`

## Required branch-client registration

The selected client remains authoritative at `research/challenge-8/cloud-build/control.py`. The phase ID `SORT4-ACTUAL-SELECT-2026-10-23-R21` is absent from the selected client source. Existing client hooks found by static source inspection: `authorized_phase()` line 710, `envs()` line 250, `config()` line 469, `run_command()` line 822. Review/add exact phase-specific checks in `authorized_phase` (account/owner/lane/window/deadline and timeout), profile/environment binding in `envs`, source/recipe checks in `config` or source preparation, and final authorization before reservation in `run_command`. The branch lane entrypoint must consume the prepared ledger, the prepared profile and recipe. Add matching synthetic registration and service error-path tests.

The generated ledger's draft status intentionally fails current submission gates. The session preparer does not create permissive client hooks, alter the live coordinator, or decide trusted proof/profile semantics. Commit the reviewed generated files and client registration on the assigned branch, then run the branch's static preflight and synthetic service tests before any separately authorized use.
