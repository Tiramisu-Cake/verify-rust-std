# #752 native binding control handoff

`READY` · `go=NOT_GRANTED` · `proof_credit=NONE`

The revised control is local in `/root/kani-ch8-pr752-binding-control-w13` on `experiment/ch8-pr752-binding-control-w13-fix`. It addresses the two findings from planner review `0f9d38fcdb`. The earlier control remains on `experiment/ch8-pr752-binding-control-w13`. The new commit shares the frozen v22 parent so the coordinator's same-tree, same-parent trigger procedure applies. [Planner review](BINDING-CHECK-REVIEW.md) · [Worker task](BINDING-CHECK-IMPL-TASK.md) · [Binding plan](BINDING-CHECK-PLAN.md)

| Object | Commit | Tree | Parent |
| --- | --- | --- | --- |
| Revised local control | `341a719bbdab85a7d0846cad061300dd4fe0de69` | `0938a64902c4bc095cbbf5b525066d73a78637ee` | `6518a69cbe3cd70c03cea07ae64305aeba5104fb` |
| Reviewed local control | `e147f9c57809eebcf727ae9d4d17a8647a06bdaa` | `0f25052cf1ff2a1ce6fb5af16c429e66726a2641` | `6518a69cbe3cd70c03cea07ae64305aeba5104fb` |
| Control v22 | `6518a69cbe3cd70c03cea07ae64305aeba5104fb` | `54c750649f32e839c8222c46e05c30039746f9b5` | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` |
| Std | `152f11556ab19c6dcfa21b5a0f1096603530ce67` | `08c6c08235035dbca44715c4b4822f5c34c041f6` | `5402b33188d51d4c30e1302af710a27c7a60d831` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |

The request SHA-256 is `91528026e497fbb3dceafff7baf2c6b6dfc98bec76c69391047314bfd57e7f11`. The workflow SHA-256 is `3f0f9f8673a46d3026621c3acd19d10865ee44e529be1425548fa53dbb5e263c`. Four of the 19 control payload hashes were refreshed. The nine std and eight stock-tool hashes were verified against the exact pins. The stock setup produces one attestation of the resolved Rust compiler, Kani launcher, driver and compiler, CBMC 6.11.0 and `goto-instrument` executables, with their paths and SHA-256 values. [Frozen request](/root/kani-ch8-pr752-binding-control-w13/ch8-pr752-binding-control/CI-REQUEST.json)

## Coordinator trigger

The trigger is a `push` to `Tiramisu-Cake/kani` at `refs/heads/uninit-ci/ch8-q-pilot-v1`, workflow `.github/workflows/ch8-q-pilot.yml`, attempt `1`, with one `ubuntu-24.04` job. The concurrency group is `ch8-s2-fork` with `cancel-in-progress: false`. After review and GO, the coordinator owns the same-tree, same-parent trigger commit and records its exact SHA in GO. The local control includes `[skip ci]`. The workflow checks the event, attempt, checked-out trigger SHA, parent, changed paths and payload hashes, then checks the independent std and tool identities. No trigger commit was created and no CI or GCB work was submitted. [Control workflow](/root/kani-ch8-pr752-binding-control-w13/.github/workflows/ch8-q-pilot.yml)

The exact selectors run serially as `D-S, D-U, D-F, F2, F3, U2, U3, C3, K1, K2, K3, K4, W1`. The first eight have `RUSTFLAGS` unset. The last five use `RUSTFLAGS='--cfg kani_smallsort_controls'`. `CARGO_ENCODED_RUSTFLAGS` is unset for all. Each root has a fresh target, export and temp path. The request freezes regular output, exact selection, one harness job, the 240 s harness timeout and object bits 12. Stock CaDiCaL and unwind 32 are expected, with uninit/value-validity off. The stock configuration and rendered CBMC argv record the effective settings for offline comparison. [Exact invocation](BINDING-CHECK-PLAN.md#frozen-invocation)

## Limits

| Scope | Limit |
| --- | --- |
| Job | 105 min with up to 30 min setup, 65 min verification, 9 min finalization and 1 min margin |
| Stock build | At most 900 s within the setup window, then one attestation within the remaining setup time |
| Root clocks | 240 s stock harness timeout and 300 s for the whole root. The worker stops at the whole-root deadline less an 8 s reap reserve |
| Launch cutoff | Refuse new roots inside the last 330 s of the 65 min verification window |
| Sampled RSS | Child PGID 8,388,608 KiB, outer owned tree 12,582,912 KiB, available-memory reserve 2,097,152 KiB. The receipt records the effective caps and observed peaks |
| Private capture per root | 16 MiB regular stdout, 1 MiB stderr, 8 MiB stock export and 64 MiB combined inspector output with a 63/1 MiB stdout/stderr split |
| Structured artifact | Up to 4 MiB of projections per root and 64 MiB aggregate including the index. Each setup receipt is read with a 1 MiB cap |

The v22 runner provides child timeout, bounded output, RSS sampling and process cleanup. The outer supervisor reaps the worker and descendants before the next root. Root receipts preserve actual exits, expected exits, cutoff phase and cleanup. Setup failures and cutoffs use the finalizer to materialize the index with explicit gaps. The workflow has no automatic retry. [Collection runner](/root/kani-ch8-pr752-binding-control-w13/ch8-pr752-binding-control/binding.py)

## Scoped evidence access

The requested GO must confirm reviewer access to the fork Actions artifact `ch8-pr752-binding-<run_id>-<attempt>`, retained for seven days. The workflow packages only the structured members below. Artifact access and capture quality on real runner output remain untested. If a member is inaccessible or a binding is ambiguous, record the corresponding evidence gap and keep the role `UNKNOWN`. [Offline acceptance](BINDING-CHECK-PLAN.md#offline-acceptance)

| Member | Planned observations |
| --- | --- |
| `binding-index.json` | Run/attempt, trigger, checkout and request identities, setup attestation, limits, exact argv and cfg, resource/exit/reap receipts, per-root paths, hashes, and explicit gaps |
| `<root>/regular.json` | Native ordinal, display ID and stock-format ID, class, status, full description and exact Location where present, terminal summary and source offsets |
| `<root>/stock-export.json` | Selected harness and exact-selection metadata, effective settings, outcome, contract kind/target/stubs, property totals and relevant buckets at JSON Pointers |
| `<root>/native.json` | Actual Kani-rendered commands and their coordinates. The 11 binding roots also request rooted call paths, declaration and symbol anchors, symbol types and ordered instruction spans from the prepared GOTO file. K1 and K2 are property-only controls |

The 11 inspection roots are D-S, D-U, D-F, F2, F3, U2, U3, C3, K3, K4 and W1. Both read-only `goto-instrument` views, `--show-goto-functions` and `--list-symbols`, receive the unique prepared GOTO file identified by the pinned CBMC argv and confined to the root temp directory. They share the original inspector capture allowance and whole-root deadline. The runner checks the file SHA-256 around the pair and records a separate command, digest, capture limit and supervision receipt for each view. Full stdout/stderr, the stock export file and native dumps stay in private temporary storage. [Pinned CBMC function headers](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-programs/show_goto_functions.cpp#L40-L62) · [Pinned CBMC type listing](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-programs/show_symbol_table.cpp#L47-L68)

The projection keeps stock `target_fn` and `verified_stubs` declarations alongside the mangled native IDs. The join uses the concrete SmallSort instance name, the pinned implementation's source span, the native function type and a direct path from the selected root. A Check additionally requires a path from the method to the exact exported DFCC wrapper tied to that invocation. A plain Replace projects the rooted Freeze instance and its scoped generated instructions without requiring `--enforce-contract`. Competing instances, unresolved calls and missing anchors remain explicit. The instruction byte span and line range preserve the full multiline assertion or assumption and its order relative to the surrounding instructions. Per-property acceptance and Check/Replace role verdicts remain offline. [Native projector](/root/kani-ch8-pr752-binding-control-w13/ch8-pr752-binding-control/native.py) · [Pinned CBMC instruction format](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-programs/goto_program.cpp#L209-L225)

## Local validation

- `git diff --check` passed on both control comparisons, against the reviewed commit and against v22. `binding.py validate` passed on the committed revision with synthetic event metadata. `binding.py check-source` passed on clean checkouts of the two exact pins.
- Static comparison verified all 13 plan selectors in order, eight cfg-off and five cfg-on source attributes and all 13 `unwind(32)` attributes. The request diff contains only four payload digest updates, which preserves the pins, options, workflow trigger, roster and full resource envelope.
- `python3 -m unittest discover -s ch8-pr752-binding-control -v` reported `Ran 29 tests in 2.626s` and `OK`. Source-shaped regressions cover the default Check with an exact DFCC wrapper, the plain Freeze Replace without an enforce symbol, competing comparator and instance candidates, missing types, the multiline postcondition with a following instruction and exact UTF-8 spans, and shared capture limits and reap across both read-only inspectors.
- `python3 -m unittest discover -s ch8-q-pilot-control -p test_run.py -v` reported `Ran 14 tests in 21.898s` and `OK`.

Synthetic stand-ins exercised the harness and inspector execution paths. Actual runtime, native channel coverage and proof observations await the coordinator's run.
