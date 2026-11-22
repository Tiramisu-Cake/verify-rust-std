# #752 native binding replay handoff

`READY` · `go=NOT_GRANTED` · `proof_credit=NONE`

The replay control is local in `/root/kani-ch8-pr752-binding-control-w13` on `experiment/ch8-pr752-binding-control-w13-fix`. It covers the nine roles left open by run `45068646559/1`. The coordinator owns any future trigger and GO for one fork job. [Minimal replay](BINDING-ACCEPTANCE.md#minimal-replay) · [Binding plan](BINDING-CHECK-PLAN.md) · [Prior control handoff](BINDING-CHECK-HANDOFF.md)

| Object | Commit | Tree | Parent |
| --- | --- | --- | --- |
| Replay control | `0ca368a85ff322a60eb2ea3a79bca233117cdc5f` | `8815092b812af5e822ca9fa07c3d2f3eedb55aa5` | `341a719bbdab85a7d0846cad061300dd4fe0de69` |
| Std | `152f11556ab19c6dcfa21b5a0f1096603530ce67` | `08c6c08235035dbca44715c4b4822f5c34c041f6` | `5402b33188d51d4c30e1302af710a27c7a60d831` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |

| Control digest | SHA-256 |
| --- | --- |
| Frozen request | `0596043cd2fc8bcdec02480dcedf7dfa51fba380127dc8cf7e04e4f436e17cf3` |
| Workflow | `586669604c717ac68ed3823cf9e0ecad56854a9a1c17b8651fdba85f5f493167` |

The request pins 20 control payloads. A future same-tree trigger uses the replay's immediate parent `341a719bbdab85a7d0846cad061300dd4fe0de69`. Validation checks the parent, changed paths and payload hashes. The event is a push on `refs/heads/uninit-ci/ch8-q-pilot-v1` in `Tiramisu-Cake/kani`, attempt 1. [Frozen request](/root/kani-ch8-pr752-binding-control-w13/ch8-pr752-binding-control/CI-REQUEST.json) · [Workflow](/root/kani-ch8-pr752-binding-control-w13/.github/workflows/ch8-q-pilot.yml)

## Replay scope

The serial order is **D-F, F2, F3, U2, U3, C3, K3, K4, W1**. K3, K4 and W1 receive `RUSTFLAGS=--cfg kani_smallsort_controls`. Both Rust flag variables are unset on the first six roots, and `CARGO_ENCODED_RUSTFLAGS` is unset on every root. The exact selectors, flags, 300 s whole-root and 240 s solver clocks, 8 GiB child cap, 105 min job ceiling and private capture budgets match the prior request. Each root takes both native views from its own prepared GOTO and publishes its own regular and stock projections. [Exact selectors and expected outcomes](BINDING-CHECK-PLAN.md#exact-roots-and-expected-outcomes)

## Publication and review

The three members per root share **6 MiB**. The native projector's ceiling is also **6 MiB** and its allowance is the space left after the regular and stock members and native provenance. All nine roots reserve up to **54 MiB**, with a **64 MiB** aggregate ceiling including `binding-index.json`. The planned scoped artifact is `ch8-pr752-binding-<run_id>-<attempt>`.

The native projection tags required rows with `mandatory_kinds` and packs them before optional context. It carries original type and instruction coordinates, declaration and DFCC joins, prepared-input and inspector identities, and same-root regular ASSERT candidates matched by clause location and description. Check candidates cover dispatch, pre-state, the wrapped body, active-slice assigns and the generated ASSERT. Replace candidates cover forwarding and dispatch, pre-state, active-slice havoc and the clause ASSUME. The pinned pairings are U2→F2 and U3/C3→F3. Confirm them using the retained type, comparator, active-slice domain and clause. Confirm the guard-off routes for K3/K4 and W1 during the same review. [Native projector](/root/kani-ch8-pr752-binding-control-w13/ch8-pr752-binding-control/native.py)

The `publication` receipt reports required and retained JSON record bytes, observed and retained counts, and missing record kinds. The byte totals measure the encoded records themselves. The index repeats the receipt so member-level cap failures remain visible. Generic constants and duplicate per-instruction source anchors are omitted. Confirm mode selection, instruction order, clause and property joins, expected terminals, and any gaps during offline acceptance. [Publisher](/root/kani-ch8-pr752-binding-control-w13/ch8-pr752-binding-control/publication.py) · [Offline acceptance](BINDING-CHECK-PLAN.md#offline-acceptance)

## Local validation

- The committed control passed `binding.py validate` with synthetic event metadata. `binding.py check-source` passed on the exact std and Kani checkouts. Request comparison verified the full records for the nine retained roots and the previous resource limits with the requested publication cap increase.
- All 30 binding-control tests and 14 shared-runner tests passed. The overflow test forced optional records past 6 MiB and checked retention of the Check ASSERT and its regular-property match, concrete assigns, and ordered Replace capture, havoc and ASSUME. A second case exceeded the mandatory budget and checked bounded publication, missing-kind reporting and byte accounting.
- The control commit carries `[skip ci]` and remains local. Real native output coverage and the nine open verdicts await offline review of an authorized replay.
