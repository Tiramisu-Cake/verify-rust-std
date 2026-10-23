The shared closure inventory proves committed file identities and bytes, but cannot establish that the final encoded payload/configuration fits transport caps. The existing committed-source client preflight must check those final caps.

# Registration plan — SORT4-ACTUAL-SELECT-2026-10-23-R23

This bundle is **PREPARED_NOT_REGISTERED**. It does not authorize or dispatch a Cloud Build.

- Owner/task: `select-sort4` / `select-callee-acceptance-autonomous-2026-10-23-r23`
- Branch and selected HEAD: `research/night-select-sort4-cloud-2026-10-09` / see `bundle.json`
- Baseline checkpoint: `cb364c5be02b759e436f1d2af056215636bcc172`
- Window: T0 `2026-10-23T07:37:19Z`, main deadline `2026-10-23T09:37:19Z`, absolute deadline `2026-10-23T10:07:19Z`
- Budget: `3600` Cloud seconds, max timeout `1200`, report reserve `240`
- Lane: `o26-select-callee-r20`
- Profile: new draft `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-SELECT-R23-PROFILE-2026-10-23.json` from `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json`

## Required branch-client registration

The selected client remains authoritative at `research/challenge-8/cloud-build/control.py`. The phase ID `SORT4-ACTUAL-SELECT-2026-10-23-R23` is absent from the selected client source. Existing client hooks found by static source inspection: `authorized_phase()` line 736, `envs()` line 270, `config()` line 495, `run_command()` line 850. Review/add exact phase-specific checks in `authorized_phase` (account/owner/lane/window/deadline and timeout), profile/environment binding in `envs`, source/recipe checks in `config` or source preparation, and final authorization before reservation in `run_command`. The branch lane entrypoint must consume the prepared ledger, the prepared profile and recipe. Add matching synthetic registration and service error-path tests.

The generated ledger's draft status intentionally fails current submission gates. The session preparer does not create permissive client hooks, alter the live coordinator, or decide trusted proof/profile semantics. Commit the reviewed generated files and client registration on the assigned branch, then run the branch's static preflight and synthetic service tests before any separately authorized use.
