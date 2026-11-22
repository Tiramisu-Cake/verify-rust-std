# Kani #5196 SmallSort uninit control handoff

`READY` · `go=NOT_GRANTED` · `proof_credit=NONE`

The control is committed locally on `experiment/ch8-kani5196-uninit-control-20261122` in `/root/kani-ch8-kani5196-uninit-control-20261122`. The coordinator owns review, confirmation of evidence access, and any dispatch after the #752 binding run releases the shared lane. [Worker task](IMPL-TASK.md) · [Approved plan](PLAN.md) · [Frozen request](/root/kani-ch8-kani5196-uninit-control-20261122/ch8-kani5196-control/CI-REQUEST.json)

| Input | Commit | Tree |
| --- | --- | --- |
| Local control | `3c9b9e7590c80989c3f230fa766e9c9410a01f09` | `db76c06c9ab6947d4abbf99ad7304f08d8b1e21b` |
| Control parent and v22 supervisor | `6518a69cbe3cd70c03cea07ae64305aeba5104fb` | `54c750649f32e839c8222c46e05c30039746f9b5` |
| Tool from `feliperodri/kani` | `bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a` | `15816aaf3b6dfa4855452e34825073db8ca6760f` |
| Candidate std | `152f11556ab19c6dcfa21b5a0f1096603530ce67` | `08c6c08235035dbca44715c4b4822f5c34c041f6` |
| Older #752 std head | `872d5a43380752786415bc00d2a12ce0e930cb37` | `384023c2f80a04d0618aa7ce971b1419494b062b` |

| Member | SHA-256 |
| --- | --- |
| `ch8-kani5196-control/CI-REQUEST.json` | `2fdb7889471f8c2ede6583b8e3c8ab3f74e0e6e5e0bafb5d431a6d0321a639f7` |
| `.github/workflows/ch8-q-pilot.yml` | `620d382bb6057114db07464e85912ea6bb25c5460e42715cf147c623a12f6c18` |
| Pinned canary `tests/expected/uninit/nested-unions/main.rs` | `3e71829b6ee39601ad29546aefb71ae861505bd9b4b555c36ea9d595468d63bb` |
| Pinned canary `tests/expected/uninit/nested-unions/expected` | `7c4b4bd80f002d4dc0c8c0180f8c01dbfcee18da9dc1a6ac967cac24282d5bcd` |

The request contains the source and control payload file hashes. The job checks the exact trigger checkout and parent, both std trees, the tool tree, source attributes, and the copied canary fixture. The stock setup builds Kani once under runner temp and records the resolved Rust compiler and Kani launcher, driver and compiler, plus CBMC 6.11.0, `goto-instrument` and Kissat 4.0.1. It records executable paths and SHA-256 values. The driver selects its build toolchain, `nightly-2026-11-19`, for both std trees. The older checkout declares `nightly-2026-10-22` and is tested verbatim. The campaign verifies the setup before execution and verifies the inputs and setup again at close. [Runner](/root/kani-ch8-kani5196-uninit-control-20261122/ch8-kani5196-control/campaign.py) · [Attestation](/root/kani-ch8-kani5196-uninit-control-20261122/ch8-kani5196-control/tool_attestation.py)

## Trigger and roster

The trigger is a `push` to `Tiramisu-Cake/kani` at `refs/heads/uninit-ci/ch8-q-pilot-v1`, using workflow `.github/workflows/ch8-q-pilot.yml`, attempt `1`, and one `ubuntu-24.04` job. The concurrency group is `ch8-s2-fork` with `cancel-in-progress: false`. The coordinator's eventual trigger commit uses the reviewed tree and parent. The local commit uses `[skip ci]`. [Workflow](/root/kani-ch8-kani5196-uninit-control-20261122/.github/workflows/ch8-q-pilot.yml)

The two standalone canaries run ON first, positive then negative, with default unwind 8. The negative expects exactly the two named uninitialized-read failures at the pinned read site on line 52. The pinned expected file gives the two description strings. Calibration binds the emitted IDs across regular output and export and requires the corresponding source locations. An unsupported property, an extra failure, or absent evidence leaves calibration incomplete. The std order is candidate `S2, UF2, N18, M8-C, M8-R, S2-C, F2-C`, then older PR head `S2, UF2, N18, M8-C, M8-R`. Each pair runs OFF then ON with `-Z uninit-checks` as the sole flag change. Source inspection confirmed unwind 34 for S2, UF2 and M8, 65 for N18, and 32 for the two trait checks. All roots use exact selection, one job, regular output, stock JSON export, CaDiCaL, and object bits 12. Each root has a new private working directory, build, temp and export paths. [Exact argv and limits](PLAN.md#invocation-and-budget)

A deliberate nonzero exit is recorded as an observation. A confirmed pre-harness compiler or link fault in one std tree yields scoped `NOT_RUN` rows. A confirmed shared launch or flag fault applies across the remaining roster. An isolated cutoff permits the next case after verified reap. The compile classification requires an applicable native diagnostic and corroboration from the pinned std build. An ambiguous compiler diagnostic remains available for offline review. [Diagnostic selection and coordinates](/root/kani-ch8-kani5196-uninit-control-20261122/ch8-kani5196-control/observations.py)

## Limits

| Scope | Frozen limit |
| --- | --- |
| Job | 180 minutes, with 30 minutes for setup, 132 minutes of planned child slots, 9 minutes for finalization and 9 minutes of spare |
| Setup build | One build capped at 900 seconds inside the 30-minute setup window |
| Root clocks | Standalone 90 s harness / 120 s slot, N18 360 / 420, other std 240 / 300 |
| Launch and cleanup | A new root needs its whole slot plus 30 s before verification cutoff. Its outer cutoff reserves 8 s for v22 containment and reap. The child watchdog ends 6 s before that outer cutoff so the child can record termination and begin cleanup |
| Sampled RSS | 8 GiB child PGID, 12 GiB outer owned tree, 2 GiB runner-memory reserve. Receipts retain nominal and effective limits, sample scopes, peaks and reap state |
| Private capture | Up to 16 MiB stdout, 1 MiB stderr and 8 MiB export per root, with bounded head and tail on pipe cutoffs |
| Structured publication | 4 MiB per root and 128 MiB aggregate, with the roster index retained on cutoff |

## Scoped evidence and availability

The shared fork Actions artifact channel is configured as `ch8-kani5196-<run_id>-<attempt>`, available to reviewers with fork Actions access and retained for seven days. Reviewer access confirmation is pending and must be recorded before GO. Live artifact delivery and the native evidence produced by this tool build await the authorized job. The upload is limited to the structured artifact directory. Raw captures, traces and original export files stay in private runner temp. [Evidence rules](PLAN.md#offline-results-and-item-1)

| Published member | Content |
| --- | --- |
| `index.json` | Trigger and source identities, request and setup digests, argv, phases, capture digests and gaps, resource and exit receipts, canary results, and exact root and pair member paths |
| `<root>/regular.json` | Native ordinals, property IDs, classes, statuses, descriptions and locations, plus terminal counts and source coordinates |
| `<root>/stock-export.json` | Scoped harness, exact selection, effective compiler and settings, contract declarations, outcome, property buckets and counts with JSON Pointers |
| `<root>/observations.json` | Regular/export/exit reconciliation and required cover observations. Typed compiler, command and phase excerpts include native source coordinates and explicit missing states for symex, SSA conversion and first CNF counters |
| `pairs/<pin>-<id>.json` | OFF and ON receipts and evidence references, with timing and RSS comparisons for completed and reconciled pairs. Missing measurements and cutoffs stay explicit |

Proof credit and interpretation of the uninitialized-read instrumentation remain offline. The structured file records declaration and property evidence for Check/Replace. It does not establish that a generated check covers each relevant read.

## Local validation

- Frozen control validation passed with synthetic fork event metadata. Exact-source checks passed for the two std checkouts and Kani checkout, including the file digests and literal or macro harness attributes. Python AST, workflow YAML and shell syntax checks passed. `git diff --check` passed.
- All 21 control tests and 14 inherited v22 tests passed. The tests covered manifest order and argv, nonzero then successful execution, a scoped older-tree compile blocker, child and outer RSS cutoffs, timeouts and reaping, split capture coordinates, incomplete export, and artifact finalization.
- The implementation used the task files from g0 `c144da41fd6b8f954ff29f6434a9a9d71fead3fa`. Those files were unchanged when the handoff was added over the coordinator's newer g0 commits. Local validation used Git, Python and synthetic processes. Cargo, rustc, Kani and CBMC were not invoked locally. The control stayed local and no CI was dispatched.
