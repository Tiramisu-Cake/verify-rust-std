# R18 registration basis

Task `select-s5-unselected-borrow-autonomous-2026-10-22-r18`, phase `SORT4-ACTUAL-C2-2026-10-22-R18`, owner `select-sort4`, lane `o26-sort4-c1-current-recovery`. T0 `2026-10-22T12:12:06Z` (fixed at actual work start, including preparation); main deadline `2026-10-22T14:12:06Z`; absolute `2026-10-22T14:42:06Z`; 3600 Cloud seconds; per-Build timeout 270..1200 s with 240 s report reserve; unlimited sequential Builds; no R17 carry.

## Routing decision (owner-approved 2026-10-22)

R18 is a **new account and window over the pinned R17 profile bytes**, not a new tool/profile chain. The Cloud adapters (`a1-entry-r17.py`, `a1-runner-r17.py`, `a1-actual-body-r17.py`, `a1-tool-r17.py`), lane route and final translator phase overlay (`r17-c1-phase-binding.patch`) accept only the R17 authorization literal, and the task pins profile `A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json` SHA-256 `87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091`.

- **R18 Builds pass `SORT4_A1_AUTHORIZATION_PHASE_ID=SORT4-ACTUAL-C2-2026-10-21-R17` to Cloud as the tool routing key.** That value identifies the effective R16/R17 tool chain only; it is not an R17 account, window or authorization.
- **R18 Builds are accounted only in `BUDGET-A1-ACTUAL-C2-2026-10-22-R18.json`** with coordinator/ledger phase `SORT4-ACTUAL-C2-2026-10-22-R18`. The closed R17 ledger is not touched.
- The profile's historical fields (`account`, `phase`, start/deadlines, `previous_build_id`) remain the R17 values and are not used for R18 admission; the Cloud side checks only the profile SHA and the shared `--deadline-epoch` from the R18 config.

## Client registration (control.py)

- `authorized_phase`: R18 requires the exact ledger phase/owner/lane/start/main/absolute deadlines, 3600 ceiling, `maximum_builds` null, 1200 max timeout and 240 reserve; absolute deadline must equal the R18 cutoff.
- `envs`: for R18, reads the R17 profile path from the proof SHA, refuses unless its SHA-256 equals the pin and its authorization/protocol/mode/body fields are the R17 values; emits the R17 routing key, protocol, checked-trait flag and profile SHA.
- `config`/`source_restore_transport`/`run_command`: R18 uses the R17 timeout budget (270..1200, 240 reserve), compressed source restore, and R18 main-deadline checks at both pre-submit and post-preflight points.
- R16/R17 and earlier registrations unchanged.

## Synthetic checks

`test_a1_r18_registration.py` (9 tests, no Cloud/proof): exact committed ledger; refusals for owner, each deadline (±1 s and the old R17 window), ceiling ±1, max timeout, build-count, lane, reserve, closed status, wrong phase, non-Select owner; timeout 269/1201 refused; environment emits the R17 routing key over exact profile bytes; any byte change or authorization/mode/body/protocol change to the profile refused; source restore enabled; R17 constants unchanged; lane route keyed by R17 literal and has no R18 literal. Historical R16/R17 `test_exact_account_required` now fail only with "Phase deadline has passed" (their windows expired), as expected.

Preparation: `smallsort-session prepare` bundle `PREPARED_NOT_REGISTERED` (see `preparation-spec.json`, `preparation-bundle.json`); its draft R18 profile/recipe were intentionally not adopted, per the routing decision above.
