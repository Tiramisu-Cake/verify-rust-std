# Standalone kani5196 diagnostic handoff

`status=READY` for coordinator re-review of the statically validated follow-up. `go=NOT_GRANTED`. `proof_credit=NONE`. The planner's NO-GO reviewed the original candidate `f58dc11f4e6b20de31bb59ec372a8e91dd7ac2cd`. [Planner review at g0 commit 14b0ad03f7](DIAG-REVIEW.md)

## Control identity

| Item | Frozen value |
| --- | --- |
| Worktree | `/root/kani-ch8-kani5196-diag-control-20261123` |
| Local branch | `ch8-kani5196-diag-control` |
| Local fix commit | `8ca646c22ee7d6fb5d2d51b7eebd90bf142b38f2` |
| Local fix direct parent | `f58dc11f4e6b20de31bb59ec372a8e91dd7ac2cd` |
| Exact trigger tree, shared with the local fix | `a98c4fe00f9f15f5f50fb1b5a16ffe89f4ecec96` |
| Exact trigger direct parent, pinned as `control_parent` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Author | `Tiramisu-Cake <igkharin@gmail.com>` |
| Request SHA-256 | `9aab99b1ccd650d6fe1f489ddbb3c4964a409293d79ad835160c6419a3433e41` |
| Workflow SHA-256 | `8362ebadbe1e0802366c13be8ee83254011a2c12bb040473f72095292dc17aa5` |

The local fix uses `[skip ci]`. For authorized dispatch, the coordinator must construct a separate trigger commit with the exact trigger tree and sole parent above. The gate compares checkout HEAD to `GITHUB_SHA` and checks the full payload diff against that parent. It requires attempt `1` and a push to `refs/heads/uninit-ci/ch8-q-pilot-v1` in `Tiramisu-Cake/kani`. The workflow uses the serial `ch8-s2-fork` concurrency group with cancellation disabled. The control branch remains local. The coordinator owns review, the fork slot and dispatch. [Workflow](/root/kani-ch8-kani5196-diag-control-20261123/.github/workflows/ch8-q-pilot.yml) · [Frozen request](/root/kani-ch8-kani5196-diag-control-20261123/ch8-kani5196-diag-control/CI-REQUEST.json)

## Review findings and fixes

| Review finding | Fix | Regression or check |
| --- | --- | --- |
| The three Rust 2015 standalone fixtures could not resolve `core`. | Declare `extern crate core;` in ITER, SELECT and SLICE. Refresh source digests, operation anchors, and observer coordinates. The standalone canary inputs remain verbatim. | Frozen fixture and named anchor checks passed. Live compilation is pending. |
| SLICE-CHECK treated the stock mangled name as the declared `writer` path. | Match the declared `writer` in stock metadata and bind its exact emitted assigns symbol through the pinned DFCC command for the same prepared GOTO. Require the rooted fixture call, generated helper and wrapped writer path to the typed write. | The mangled helper binds. A different exported helper, an unrelated helper named by both stock and DFCC, and a different GOTO path each fail. |
| Both `caller_location` guards missed their attested source. A separate rooted call could stand in for the guard's own origin. | Match the attested `kani-compiler/src/intrinsics.rs` key. Bind each false assertion to its own source and descriptor with the pinned memory-initialization hook or intrinsic codegen lowering. Pointer guards require the corresponding containing helper and a pinned source coordinate. | Both native descriptors bind at the erased operation. An unrelated rooted call, wrong intrinsic source line, live guard, and non-false instruction are rejected. |
| A measured SUCCESS could have unexercised observers. | Require satisfied required covers and successful required assertions for measured SUCCESS. A measured FAILURE preserves entry and return statuses for review of the target alarm. | Unreachable or unsatisfiable return covers and an unreachable assertion block comparison on SUCCESS. A FAILURE with a target alarm preserves the satisfied entry and unreachable return. |
| Aggregate-cap behavior lacked a finalization regression. | Exercise finalization with a reduced aggregate budget that includes the index and all pair receipts. | Optional projections drop first. When a required projection drops, the index and pair agree on the gap and the pair becomes incomplete. Pair hashes and total published bytes are checked. |

## Roster and invocation

Run the first two rows ON in order. Run the remaining rows in order, OFF then ON for each pair. OFF and ON share the exact source, selector, and settings except the ON insertion shown below.

| Root or pair | Fixture | Exact selector | Contract mode |
| --- | --- | --- | --- |
| CAL-POS | `main.rs` | `buffer_written_then_read_ok` | Ordinary |
| CAL-NEG | `main.rs` | `buffer_partly_written_ub` | Ordinary |
| ITER | `iter.rs` | `iter_by_value` | Ordinary |
| ITER-INIT | `iter.rs` | `iter_initialized` | Ordinary |
| SELECT | `select.rs` | `select_pointer` | Ordinary |
| SELECT-INIT | `select.rs` | `select_initialized` | Ordinary |
| SLICE-CHECK | `slice.rs` | `slice_check` | Check on `writer` |
| SLICE-REPLACE | `slice.rs` | `slice_replace` | Replace using verified `writer` |
| SLICE-INIT | `slice.rs` | `slice_initialized` | Replace using verified `writer` |

| Fixture | SHA-256 |
| --- | --- |
| `main.rs`, verbatim pinned canary | `3e71829b6ee39601ad29546aefb71ae861505bd9b4b555c36ea9d595468d63bb` |
| `nested-unions.expected`, verbatim pinned expectations | `7c4b4bd80f002d4dc0c8c0180f8c01dbfcee18da9dc1a6ac967cac24282d5bcd` |
| `iter.rs` | `6a36f2a4cc988ff3e09e3f5d67a9bbe91b112f9246ca314eba2f3a205050a61d` |
| `select.rs` | `75b3bdb7dd1287891db2ae8c78e559b41ab397d216a6151484829dc6b0c73d1b` |
| `slice.rs` | `973d57a7c28952bb6a833e2cdea77f62641e37722837d033c1077433b143b226` |

The request contains the full normalized argv array per root, named fixture coordinates, assertion lines and coverage labels. The runner substitutes the attested launcher and the private fixture and export paths.

```text
{launcher} {fixture} -Z unstable-options -Z export-json --export-json {export}
  --harness {selector} --exact --jobs=1 --output-format=regular --verbose --keep-temps
  --default-unwind {unwind} --harness-timeout {seconds}s
  [slice: -Z function-contracts -Z stubbing -Z mem-predicates --no-assert-contracts]
  [ON: -Z uninit-checks]
  --cbmc-args --object-bits 12
```

CaDiCaL is the pinned driver's default. The runner checks the emitted compiler input, selector, mode and sysroot, the checker argv and effective stock settings, and the selected contract mode. It verifies fixture and prepared GOTO identities in their private root directories. [Fixture directory](/root/kani-ch8-kani5196-diag-control-20261123/ch8-kani5196-diag-control/fixtures) · [Runner](/root/kani-ch8-kani5196-diag-control-20261123/ch8-kani5196-diag-control/diagnostic.py)

## Dependencies and clocks

The job checks out `feliperodri/kani` at `bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a`, tree `15816aaf3b6dfa4855452e34825073db8ca6760f`. It builds the tool once with `nightly-2026-11-19`, CBMC 6.11.0 and Kissat 4.0.1 installed. Launch and close checks cover the persisted Kani launcher, driver, compiler, actual Rust compiler identity, `cbmc`, `goto-cc`, `goto-instrument`, and Kissat. The job hashes the actual Kani verification sysroot libraries, relevant installed Rust sources, and pinned tool files. The recorded compiler sysroot is compared with `--sysroot` in the emitted compiler command. Source and executable digests that depend on the installed or built files will be available in the run attestation. One `ubuntu-24.04` Actions job, with zero Cloud Build use.

| Limit | Value |
| --- | --- |
| Job, setup, build | 75 min, 1,800 s, 900 s |
| Canary unwind, Kani harness timeout, child watchdog | 8, 90 s, 120 s |
| Diagnostic unwind, Kani harness timeout, child watchdog | 16, 60 s, 90 s |
| Per-root reserves | 3 s startup, 6 s child cleanup, 15 s read-only GOTO inspection including cleanup, 8 s outer reap |
| Job admission | 2,012 s roster, 540 s finalization/upload, 30 s launch headroom, 118 s spare |
| RSS | 8 GiB child and 12 GiB outer nominal caps, 2 GiB runner reserve. The index records effective sampled limits and verified reap. |
| Private capture per root | 16 MiB stdout, 1 MiB stderr, 8 MiB export. Inspection separately allows 16 MiB stdout and 1 MiB stderr across its two views. |
| Structured publication | 4 MiB per root and 72 MiB total including the index. The upload retains one artifact for seven days. |

## Evidence and access

The only upload is `ch8-kani5196-diag-<run_id>-<attempt>`. It contains the 16-root index, the seven pair comparisons, and bounded regular, stock, typed-binding, check and diagnostic projections. A native failure is retained with its exit code. A runner or checker cutoff and any evidence or publication gap are recorded in the relevant root. Common setup and launch faults produce scoped `NOT_RUN` receipts. Backend traces, raw logs, prepared binaries and original exports stay in runner temp.

Read access to the fork and the prior named structured artifact's metadata was confirmed using the authenticated `Tiramisu-Cake` account. The diagnostic upload is pending dispatch. The coordinator owns retrieval and reviewer access confirmation for the exact artifact. [Fork Actions](https://github.com/Tiramisu-Cake/kani/actions)

The calibration policy requires the exact two `std::ptr::read::<u32>` IDs at their bound callee operations and fixture read sites. Each unsupported guard must be `SUCCESS` with pinned provenance. The binding requires exact rooted call edges and an attested callee or model coordinate. A compiled path with only inline sites and insufficient caller coordinates remains `INCOMPLETE`, as do ambiguous calls, missing observers and unsupported guards without proved provenance. Successful static binding does not assign a dynamic object, shadow-byte mask or transfer history. The stock export can report trace availability without carrying trace steps. Live fixture compilation, observed sysroot path and calibration remain for the authorized run. The downstream verdict and any upstream report remain with offline review. [Plan](DIAG-PLAN.md)

## Local validation

- All 24 diagnostic Python tests passed, including the Check-symbol, guard-origin, measured-observer, and finalization cases above.
- The 22 accepted campaign tests and 14 inherited v22 supervisor tests passed.
- Workflow YAML and run-step shell syntax, Python AST, exact pinned tool commit and tree, all 41 pinned tool file hashes, payload and fixture digests, frozen fixture anchors, and `git diff --check` passed.
- All four prior CAL-POS structured guard descriptors matched the pinned tool lowering with local comparison source anchors and synthetic instruction coordinates. Live prepared GOTO and sysroot attestation remain pending.
- A depth-three local checkout of a synthetic trigger with the exact tree and parent passed the event gate. The gate rejected the local fix commit's direct parent, a mismatched event SHA, a mismatched ref, and attempt `2`.
- Validation used Git, static checks and synthetic Python. The fork dispatch and native calibration remain pending.

## Trigger payload paths relative to the trigger parent

- `.github/workflows/ch8-q-pilot.yml`
- `ch8-kani5196-diag-control/CI-REQUEST.json`
- `ch8-kani5196-diag-control/diag_evidence.py`
- `ch8-kani5196-diag-control/diag_request.py`
- `ch8-kani5196-diag-control/diagnostic.py`
- `ch8-kani5196-diag-control/fixtures/iter.rs`
- `ch8-kani5196-diag-control/fixtures/main.rs`
- `ch8-kani5196-diag-control/fixtures/nested-unions.expected`
- `ch8-kani5196-diag-control/fixtures/select.rs`
- `ch8-kani5196-diag-control/fixtures/slice.rs`
- `ch8-kani5196-diag-control/native_binding.py`
- `ch8-kani5196-diag-control/test_diagnostic.py`
- `ch8-kani5196-diag-control/test_native_binding.py`
