# #752 native binding control handoff

`READY` · `go=NOT_GRANTED` · `proof_credit=NONE`

The local control candidate is in `/root/kani-ch8-pr752-binding-control-w13` on `experiment/ch8-pr752-binding-control-w13`. This handoff uses g0 task head `68ff4ba14e430ce28c5c4acfb7157e02210cf283`. The std candidate and its organizer workflow were preserved byte for byte. [Worker task](BINDING-CHECK-IMPL-TASK.md) · [Binding plan](BINDING-CHECK-PLAN.md)

| Object | Commit | Tree | Parent |
| --- | --- | --- | --- |
| Local control | `e147f9c57809eebcf727ae9d4d17a8647a06bdaa` | `0f25052cf1ff2a1ce6fb5af16c429e66726a2641` | `6518a69cbe3cd70c03cea07ae64305aeba5104fb` |
| Control v22 | `6518a69cbe3cd70c03cea07ae64305aeba5104fb` | `54c750649f32e839c8222c46e05c30039746f9b5` | `ba32286ee4f370593a2c9f0d8834a12d473c82d7` |
| Std | `152f11556ab19c6dcfa21b5a0f1096603530ce67` | `08c6c08235035dbca44715c4b4822f5c34c041f6` | `5402b33188d51d4c30e1302af710a27c7a60d831` |
| Stock Kani | `9834c96ce90ff57d8495416530b080dc3d52ce25` | `938e9932cb2127239afb4f093f6302652c053398` | `70d7da0ae18991f9604d299784b974a43636945a` |

The request SHA-256 is `698fbb2c776319d1ef48b24146449cf7181e5871f8b6dde6ac662558921cf34e`. The workflow SHA-256 is `3f0f9f8673a46d3026621c3acd19d10865ee44e529be1425548fa53dbb5e263c`. The request inventories 19 control payload hashes, nine std file hashes, and eight stock-tool file hashes. The stock setup produces one attestation of the resolved Rust compiler, Kani launcher, driver and compiler, CBMC 6.11.0 and `goto-instrument` executables, with their paths and SHA-256 values. [Frozen request](/root/kani-ch8-pr752-binding-control-w13/ch8-pr752-binding-control/CI-REQUEST.json)

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
| `<root>/native.json` | Relevant actual Kani-rendered commands and their coordinates. The 11 binding roots also request the read-only prepared GOTO projection. K1 and K2 are property-only controls |

The 11 inspection roots are D-S, D-U, D-F, F2, F3, U2, U3, C3, K3, K4 and W1. The inspector receives the unique prepared GOTO file identified by the pinned CBMC argv shape and confined to the root temp directory. The runner checks its SHA-256 before and after inspection and uses the pinned `goto-instrument --show-goto-functions` without an output-file argument. The projection preserves ordered instructions and coordinates for direct call paths, symbols, source/type anchors and literal values. It labels lexical scope and unresolved direct or indirect mappings. All per-property acceptance and Check/Replace binding decisions remain with offline review. Full stdout/stderr, the stock export file and GOTO dumps stay in private temporary storage. [Pinned CBMC function headers](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-programs/show_goto_functions.cpp#L40-L62) · [Pinned CBMC instruction format](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-programs/goto_program.cpp#L36-L215)

## Local validation

- `git diff --check` passed on the control delta. Frozen `binding.py validate` passed on the committed clean control with synthetic event metadata. `binding.py check-source` passed on clean checkouts of both exact source pins. The request hashes and all payload and pin files were checked.
- Static comparison against g0 verified 13 exact selectors in table order, the literal argv template, eight cfg-off and five cfg-on source attributes, all 13 `unwind(32)` attributes, and the fork workflow's trigger, serialization and resource envelope.
- `python3 -m unittest discover -s ch8-pr752-binding-control -v` reported `Ran 28 tests in 3.374s` and `OK`. The tests cover both cfgs and root clocks, the 8 GiB cap and lower effective cap, exit 1 followed by exit 0, duplicate IDs and multiline locations, missing or ambiguous GOTO, read-only inspection hashes, partial terminal and malformed export, publication cutoffs, reap and setup-failure finalization.
- `python3 -m unittest discover -s ch8-q-pilot-control -p test_run.py -v` reported `Ran 14 tests in 22.653s` and `OK`.

Synthetic stand-ins exercised the harness and inspector execution paths. Actual runtime, native channel coverage and proof observations await the coordinator's run.
