The shared closure inventory proves committed file identities and bytes, but cannot establish that the final encoded payload/configuration fits transport caps. The existing committed-source client preflight must check those final caps.

# Registration plan — SORT4-ACTUAL-LIFETIME-2026-10-21-R16

This bundle is **PREPARED_NOT_REGISTERED**. It does not authorize or dispatch a Cloud Build.

- Owner/task: `select-sort4` / `select-actual-lifetime-autonomous-2026-10-21-r16`
- Branch and selected HEAD: `research/night-select-sort4-cloud-2026-10-09` / see `bundle.json`
- Baseline checkpoint: `55ce3dcb2a70cb9300d472cac3282daf7c7cdc52`
- Window: T0 `2026-10-21T17:50:34Z`, main deadline `2026-10-21T19:50:34Z`, absolute deadline `2026-10-21T20:20:34Z`
- Budget: `3600` Cloud seconds, max timeout `1200`, report reserve `240`
- Lane: `o26-sort4-c1-current-recovery`

## Required branch-client registration

The selected client remains authoritative at `research/challenge-8/cloud-build/control.py`. The phase ID `SORT4-ACTUAL-LIFETIME-2026-10-21-R16` is absent from the selected client source. Existing client hooks found by static source inspection: `authorized_phase()` line 630, `envs()` line 211, `config()` line 389, `run_command()` line 737. Review/add exact phase-specific checks in `authorized_phase` (account/owner/lane/window/deadline and timeout), profile/environment binding in `envs`, source/recipe checks in `config` or source preparation, and final authorization before reservation in `run_command`. The branch lane entrypoint must consume the prepared profile and recipe. Add matching synthetic registration and service error-path tests.

The generated ledger's draft status intentionally fails current submission gates. The session preparer does not create permissive client hooks, alter the live coordinator, or decide trusted proof/profile semantics. Commit the reviewed generated files and client registration on the assigned branch, then run the branch's static preflight and synthetic service tests before any separately authorized use.
