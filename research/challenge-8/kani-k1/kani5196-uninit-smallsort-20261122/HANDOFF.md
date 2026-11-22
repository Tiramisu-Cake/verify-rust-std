# Kani #5196 SmallSort uninit control handoff

`READY` · `go=NOT_GRANTED` · `proof_credit=NONE`

The revised control is committed locally on `experiment/ch8-kani5196-uninit-control-20261122` in `/root/kani-ch8-kani5196-uninit-control-20261122`. It addresses the clock finding in g0 `0068f3a826` and awaits re-review. The coordinator owns review, confirmation of evidence access, and any dispatch after the #752 binding run releases the shared lane. [Review](REVIEW.md) · [Worker task](IMPL-TASK.md) · [Approved plan](PLAN.md) · [Frozen request](/root/kani-ch8-kani5196-uninit-control-20261122/ch8-kani5196-control/CI-REQUEST.json)

| Input | Commit | Tree |
| --- | --- | --- |
| Revised local control | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` | `cf85db18831eea84e66723b16de37da08ef5fdd3` |
| Direct control parent reviewed in `REVIEW.md` | `3c9b9e7590c80989c3f230fa766e9c9410a01f09` | `db76c06c9ab6947d4abbf99ad7304f08d8b1e21b` |
| v22 supervisor and changed-path baseline | `6518a69cbe3cd70c03cea07ae64305aeba5104fb` | `54c750649f32e839c8222c46e05c30039746f9b5` |
| Tool from `feliperodri/kani` | `bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a` | `15816aaf3b6dfa4855452e34825073db8ca6760f` |
| Candidate std | `152f11556ab19c6dcfa21b5a0f1096603530ce67` | `08c6c08235035dbca44715c4b4822f5c34c041f6` |
| Older #752 std head | `872d5a43380752786415bc00d2a12ce0e930cb37` | `384023c2f80a04d0618aa7ce971b1419494b062b` |

| Member | SHA-256 |
| --- | --- |
| `ch8-kani5196-control/CI-REQUEST.json` | `61727590165551e10ea7615e045d5893b8a47022779224b1ccbded0322d5e0bb` |
| `.github/workflows/ch8-q-pilot.yml` | `5f3e84230c80c70f54129277aee41d1334247e4f7b8532ad4a13a4a8ebd9b7e3` |
| Pinned canary `tests/expected/uninit/nested-unions/main.rs` | `3e71829b6ee39601ad29546aefb71ae861505bd9b4b555c36ea9d595468d63bb` |
| Pinned canary `tests/expected/uninit/nested-unions/expected` | `7c4b4bd80f002d4dc0c8c0180f8c01dbfcee18da9dc1a6ac967cac24282d5bcd` |

The request contains the source and refreshed control payload file hashes. The job checks the exact trigger checkout and direct parent. A depth-three checkout makes the v22 baseline available for the full changed-path check. The job also checks both std trees, the tool tree, source attributes, and the copied canary fixture. The stock setup builds Kani once under runner temp and records the resolved Rust compiler and Kani launcher, driver and compiler, plus CBMC 6.11.0, `goto-instrument` and Kissat 4.0.1. It records executable paths and SHA-256 values. The driver selects its build toolchain, `nightly-2026-11-19`, for both std trees. The older checkout declares `nightly-2026-10-22` and is tested verbatim. The campaign verifies the setup before execution and verifies the inputs and setup again at close. [Runner](/root/kani-ch8-kani5196-uninit-control-20261122/ch8-kani5196-control/campaign.py) · [Attestation](/root/kani-ch8-kani5196-uninit-control-20261122/ch8-kani5196-control/tool_attestation.py)

## Trigger and roster

The trigger is a `push` to `Tiramisu-Cake/kani` at `refs/heads/uninit-ci/ch8-q-pilot-v1`, using workflow `.github/workflows/ch8-q-pilot.yml`, attempt `1`, and one `ubuntu-24.04` job. The concurrency group is `ch8-s2-fork` with `cancel-in-progress: false`. The coordinator's eventual trigger commit uses the reviewed tree and parent. The local commit uses `[skip ci]`. [Workflow](/root/kani-ch8-kani5196-uninit-control-20261122/.github/workflows/ch8-q-pilot.yml)

The two standalone canaries run ON first, positive then negative, with default unwind 8. The negative expects exactly the two named uninitialized-read failures at the pinned read site on line 52. The pinned expected file gives the two description strings. Calibration binds the emitted IDs across regular output and export and requires the corresponding source locations. An unsupported property, an extra failure, or absent evidence leaves calibration incomplete. The std order is candidate `S2, UF2, N18, M8-C, M8-R, S2-C, F2-C`, then older PR head `S2, UF2, N18, M8-C, M8-R`. Each pair runs OFF then ON with `-Z uninit-checks` as the sole flag change. Source inspection confirmed unwind 34 for S2, UF2 and M8, 65 for N18, and 32 for the two trait checks. All roots use exact selection, one job, regular output, stock JSON export, CaDiCaL, and object bits 12. Each root has a new private working directory, build, temp and export paths. [Exact argv and limits](PLAN.md#invocation-and-budget)

A deliberate nonzero exit is recorded as an observation. A confirmed pre-harness compiler or link fault in one std tree yields scoped `NOT_RUN` rows. A confirmed shared launch or flag fault applies across the remaining roster. An isolated cutoff permits the next case after verified reap. The compile classification requires an applicable native diagnostic and corroboration from the pinned std build. An ambiguous compiler diagnostic remains available for offline review. [Diagnostic selection and coordinates](/root/kani-ch8-kani5196-uninit-control-20261122/ch8-kani5196-control/observations.py)

## Limits

| Scope | Frozen limit |
| --- | --- |
| Job | 180 minutes, with 30 minutes for setup, 132 minutes of child watchdog time and 9 minutes for closing checks, finalization and upload. The remaining 540 s cover 364 s for per-root cleanup and reap, 78 s for per-root startup, 30 s of launch headroom, and 68 s for campaign validation, parent preparation and other overhead |
| Setup build | One build capped at 900 seconds inside the 30-minute setup window |
| Root clocks | Standalone 90 s harness / 120 s whole-child watchdog, N18 360 / 420, other std 240 / 300 |
| Launch and cleanup | Launch requires the full watchdog plus 3 s for journaling and worker startup, 6 s for child cleanup, 8 s for outer containment and reap, and 30 s of job headroom. The supervisor checks admission again after parent preparation. If startup leaves too little time for the full watchdog, the worker records `NOT_RUN` |
| Sampled RSS | 8 GiB child PGID, 12 GiB outer owned tree, 2 GiB runner-memory reserve. Receipts retain nominal and effective limits, sample scopes, peaks and reap state |
| Private capture | Up to 16 MiB stdout, 1 MiB stderr and 8 MiB export per root, with bounded head and tail on pipe cutoffs |
| Structured publication | 4 MiB per root and 128 MiB aggregate, with the roster index retained on cutoff |

## Scoped evidence and availability

The fork Actions artifact `ch8-kani5196-<run_id>-<attempt>` is retained for seven days. After the authorized job uploads it, the coordinator downloads the named artifact from `Tiramisu-Cake/kani` with `gh run download` and shares the local directory path with reviewers. The coordinator records access confirmation before GO. The upload is limited to the structured artifact directory. Raw captures, traces and original export files stay in private runner temp. [Evidence rules](PLAN.md#offline-results-and-item-1)

| Published member | Content |
| --- | --- |
| `index.json` | Trigger and source identities, request and setup digests, argv, phases, capture digests and gaps, resource and exit receipts, canary results, and exact root and pair member paths |
| `<root>/regular.json` | Native ordinals, property IDs, classes, statuses, descriptions and locations, plus terminal counts and source coordinates |
| `<root>/stock-export.json` | Scoped harness, exact selection, effective compiler and settings, contract declarations, outcome, property buckets and counts with JSON Pointers |
| `<root>/observations.json` | Regular/export/exit reconciliation and required cover observations. Typed compiler, command and phase excerpts include native source coordinates and explicit missing states for symex, SSA conversion and first CNF counters |
| `pairs/<pin>-<id>.json` | OFF and ON receipts and evidence references, with timing and RSS comparisons for completed and reconciled pairs. Missing measurements and cutoffs stay explicit |

Proof credit and interpretation of the uninitialized-read instrumentation remain offline. The structured file records declaration and property evidence for Check/Replace. It does not establish that a generated check covers each relevant read.

## Local validation

- Frozen control validation passed with synthetic fork event metadata in a depth-three clone. It verified all 24 payload digests and rejected a mismatched trigger SHA. Exact-source checks passed for the two std checkouts and Kani checkout, including file digests and harness attributes. Python AST, workflow YAML, shell syntax and `git diff --check` passed.
- All 22 control tests and 14 inherited v22 tests passed. The new synthetic test runs the production supervisor and worker launch path and checks the 120, 300 and 420 s stock watchdogs, the 90, 240 and 360 s harness timeouts, and refusal before launch or after budget overruns during preparation or worker startup. The same test detects all three shortened watchdogs on the reviewed control.
- Local validation used Git, Python and synthetic processes. The revised control stayed local and no CI was dispatched. Runtime calibration and native proof observations await the authorized run.
