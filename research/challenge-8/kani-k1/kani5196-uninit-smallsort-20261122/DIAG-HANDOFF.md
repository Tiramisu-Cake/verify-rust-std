# Standalone kani5196 diagnostic handoff

`status=READY` for coordinator review of the statically validated control candidate. `go=NOT_GRANTED`. `proof_credit=NONE`.

## Control identity

| Item | Frozen value |
| --- | --- |
| Worktree | `/root/kani-ch8-kani5196-diag-control-20261123` |
| Local branch | `ch8-kani5196-diag-control` |
| Commit | `f58dc11f4e6b20de31bb59ec372a8e91dd7ac2cd` |
| Tree | `b3d9ffb77c631555d493fcd27ebe1011ec4cf941` |
| Direct parent | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |
| Author | `Tiramisu-Cake <igkharin@gmail.com>` |
| Request SHA-256 | `9f353b02df6a096c64fa408a929c42ae4b63ed0b47390f34448d5344d702fde4` |
| Workflow SHA-256 | `8362ebadbe1e0802366c13be8ee83254011a2c12bb040473f72095292dc17aa5` |

The local commit uses `[skip ci]`. The reviewed trigger must use the exact tree and direct parent above. The event gate compares checkout HEAD to `GITHUB_SHA` and requires attempt `1`, a push to `refs/heads/uninit-ci/ch8-q-pilot-v1` in `Tiramisu-Cake/kani`, and the existing serial `ch8-s2-fork` concurrency group with cancellation disabled. The control branch remains local. The coordinator owns review, the fork slot and dispatch. [Workflow](/root/kani-ch8-kani5196-diag-control-20261123/.github/workflows/ch8-q-pilot.yml) · [Frozen request](/root/kani-ch8-kani5196-diag-control-20261123/ch8-kani5196-diag-control/CI-REQUEST.json)

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
| `iter.rs` | `be08bba3f7b9c6f286c278cea81feaa9f8515a01e0fab1b147b7f6076cb2f8fd` |
| `select.rs` | `ecccbf211a05bad83ff49b5292462071c0609c297b16073a6f373b3f461e7e14` |
| `slice.rs` | `2703ef9f125a76536bd22586ef5f32132e0b59995222a1b4ddb6a0855c9d1fd3` |

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

- 20 diagnostic Python tests passed. They cover the exact roster and pair mode delta, compiler and backend argv identity, separate callee/fixture coordinates, wrong or ambiguous target, extra and missing failures, guard acceptance and rejection, successful and deliberate negative exits under supervision, watchdog and RSS cleanup, inspector cutoff, admission reserves, and projection caps.
- The 22 accepted campaign tests and 14 inherited v22 supervisor tests passed.
- Workflow YAML and shell syntax, Python AST, exact pinned tool commit/tree/source hashes, fixture digests, and `git diff --check` passed. A depth-three local clone passed the synthetic trigger gate and rejected a mismatched trigger SHA and a retry attempt.
- Local work used Git, static checks and synthetic Python only. CI dispatch remains pending.

## Changed paths

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
