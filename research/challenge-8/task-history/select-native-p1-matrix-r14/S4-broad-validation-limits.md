# S4 broad-test accounting and limits

## Recorded broad run

Command: `python -m unittest discover -p 'test_a1_*.py'` from `research/challenge-8/cloud-build/sort4-caller-entry-native`.

The returned unittest summary was **480 tests, 19 failures, 2 errors**. The tool response truncated the detailed output (it reported 35,632 original tokens), and no raw output file was retained. Per instruction, the broad suite was not rerun. Consequently the exact full list of 19 failures is not recoverable from the retained terminal output; the IDs below are the exact failures/errors visible in the response and subsequent narrow accounting, rather than a guessed completion of the missing tail.

## Exact visible failures/errors

- `test_a1_auto_profile_gate.ProfileGateTests.test_historical_r7_profile_pins_remain_recorded` — assertion that `A1-PACKAGING-R7-PROFILE-2026-10-20.json` remains in active `recipe["proof_paths"]`; the active R14 closure omits the expired historical profile.
- `test_a1_auto_profile_gate.ProfileGateTests.test_published_r11_profile_remains_historical_after_r12_closure_advance` — assertion that the historical R11 profile remains in active `proof_paths`.
- `test_a1_auto_profile_gate.ProfileGateTests.test_published_r8_profile_is_connected_to_current_transport_and_files` — assertion that the historical R8 profile is in active `proof_paths`.
- `test_a1_auto_profile_gate.ProfileGateTests.test_published_r9_profile_is_connected_to_current_transport_and_files` — assertion that the historical R9 profile is in active `proof_paths`.
- `test_a1_auto_profile_gate.ProfileGateTests.test_published_r12_profile_binds_the_current_registration_closure` — assertion that R12 profile is in active `proof_paths`.
- The same five test IDs fail through `test_a1_union_profile_gate.ProfileGateTests`; these are the compatibility entrypoint's duplicate profile-binding checks.
- `test_a1_r11_registration.R11Registration.test_recipe_and_lane_select_the_r11_adapter_without_replacing_history` — historical R11 profile is not in the active R14 recipe's `proof_paths`.
- `test_a1_r12_registration.R12Registration.test_coordinator_recipe_lane_and_core_route_select_only_r12_profile` — historical R12 profile is not in the active R14 recipe's `proof_paths`.
- `test_a1_r12_registration.R12Registration.test_fresh_account_profile_and_existing_history_are_separate` — source-runner SHA assertion differs from current `a1-runner.py`; this is a stale registration pin after the S4 runner edit, not a runtime-logic assertion.
- `test_a1_r13_registration.R13Registration.test_adapter_pins_match_profile_snapshot` — source-runner SHA assertion differs from current `a1-runner.py`; stale historical pin.
- `test_a1_r13_registration.R13Registration.test_fresh_phase_account_and_non_admitting_profile` — expected `AUTHORIZED`, observed `CLOSED`; R13 is historical/closed under current R14 selection.
- `test_a1_r13_registration.R13Registration.test_route_and_recipe_bind_r13_without_rewriting_history` — assertion that closed R13 profile remains in active R14 recipe `proof_paths`.
- `test_a1_r14_registration.R14Registration.test_fresh_phase_account_and_nonadmitting_profile` — expected unused build seconds `0`, observed `1441`; ledger reflects accounted S3/S4 usage.

The two exact errors were:

- `test_a1_r12_registration.R12Registration.test_core_profile_registry_and_coordinator_environment` — `SystemExit: Phase account is closed or has no explicit authorization`, raised by `control.py:612` in `authorized_phase`.
- `test_a1_r13_registration.R13Registration.test_coordinator_accepts_only_exact_r13_account_shape` — same `SystemExit` from `control.py:612` for the closed R13 account.

A subsequent **narrow** profile/registration selection showed additional current-state details and duplicate compatibility tests, but it is not substituted for the missing broad-suite tail. The only touched-runner-related assertion found in that narrow pass was an outdated SHA pin; no failed assertion implicated the S4 redirect input-binding behavior. The focused S4/runner/matrix suite passed 32/32.

## Local execution boundary

This discovery run did **not** run the actual compiler, preparer, VeriFast exporter, MIR decoder, refinement checker, or verifier. Static test-source inspection found only these subprocess categories: `git show`/`git rev-parse` for source/account snapshots; `patch` on temporary source copies; shell snippets with fake stage functions; and generated source-input transport round-trips in temporary directories. Those transport tests do execute their synthetic base64/gzip/lzma restoration decoder; they do not invoke the proof pipeline's MIR decoder or any compiler/verifier stage. No Cloud Build or full runner was launched.
