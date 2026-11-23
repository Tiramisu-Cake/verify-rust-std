# Kani 5196 base comparison and SLICE fixture handoff

Two frozen local candidates use `.github/workflows/ch8-q-pilot.yml`, the same fork push ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, and attempt `1` in `Tiramisu-Cake/kani`. Each candidate targets a separate serial job in `ch8-s2-fork`. Both requests carry `status=READY`, `go=NOT_GRANTED`, and `proof_credit=NONE`. Dispatch and native calibration are pending. [Task](DIAG-NEXT-TASK.md) · [Prior run analysis](DIAG-RUN-45163409005-ANALYSIS.md)

## Frozen Git identities

The refs are in `/root/kani-ch8-kani5196-diag-control-20261123`. Both local control commits descend directly from `5b5aa3cb619d65378d691cf5ad05a48cce341a9c`. Each trigger is a `git commit-tree` commit with its candidate's exact control tree and sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`.

| Item | A · Base comparison | B · SLICE fixture |
| --- | --- | --- |
| Control branch | `ch8-kani5196-diag-base-control` | `ch8-kani5196-diag-slice2-control` |
| Control head | `ecb469340193d95858cecd82120760a67807df13` | `decdd792c62a7fb814486c8b09f2d2edd1218e9e` |
| Shared control and trigger tree | `db99548f694e0dc85fde0b91819b30e6be9abc1e` | `873c75105516e2c8e1f0fabab878fe44175033bf` |
| Trigger branch | `ch8-kani5196-diag-base` | `ch8-kani5196-diag-slice2` |
| Trigger SHA | `07741eafd5901509590cf0fe1b2fb7b5953b65c4` | `6e2922538d721509e9788d00298e07a2ad99d6b7` |
| Tool SHA | `5d80a641d333c929e00ed1e1255c637265f15749` | `bcdc1a0f8dc566654da1f18b4e502f0f4e7ad40a` |
| Tool tree | `d835856aea4b85e75a6eb3fe100d5c5479b6c2f9` | `15816aaf3b6dfa4855452e34825073db8ca6760f` |
| Request SHA-256 | `9738a694ac53e1e9e5c4b30a2015170335b5a5830997750c27f762a525f063c6` | `a1c343cb04e87554a578ca59ae35ff6f3a2ba284b2f6361dd3803eeacef9bd36` |
| Workflow SHA-256 | `86a31d2608a59d821f0e71bb713635884ff4d4e54168a9c961d385913d50d645` | `7641ab8022b8df635d70707c53a58750816aaab5bc9997843ec1d1720186712c` |

## Diffs and rosters

**A · Base comparison.** The ten complete root requests and all five fixture digests match run `45163409005`. Read-only Git inspection confirmed that `5d80a641d` is the merged `main` parent (`da0406b78^2`). Its nightly `2026-11-19`, Cargo lock and manifests, dependency declarations, setup scripts, and submodule pins match the PR head. The base source defines `UninitChecks` as a `-Z` feature and adds ghost state and `--ub-check=uninit` in the standalone driver. The base predates `tests/expected/uninit/nested-unions`. The request records the PR-head provenance of the byte-identical `main.rs` and `nested-unions.expected` and verifies them in the frozen control checkout. Build, launch and close attest the actual base tool SHA and tree. A retains the previous ITER-INIT and SELECT binder limitations documented in the prior run analysis.

**B · SLICE fixture.** At entry and return, the Rust observer checks length and the eight indexed `u64` values individually. The fixture diff is confined to those two observers. The request records all 18 assertion coordinates and both cover coordinates. Check binds the actual write through its rooted DFCC wrapper. Replace and Init require the rooted harness call and the typed generated model call at the `modifies` line. The eight retained invocation arrays match the prior run. The binder also recognizes the direct typed public `select_unpredictable` call at its fixture anchor and the mangled `MaybeUninit<usize>::assume_init_read` receiver. Those two matchers are covered by synthetic regressions in B.

Both jobs start with `CAL-POS` (`buffer_written_then_read_ok`) and `CAL-NEG` (`buffer_partly_written_ub`), both ON. Each following row runs OFF then ON. ON adds `-Z uninit-checks` to the corresponding OFF invocation.

| Candidate | Ordered pairs and exact selectors | Roots |
| --- | --- | ---: |
| A | `ITER` (`iter_by_value`), `ITER-INIT` (`iter_initialized`), `SELECT` (`select_pointer`), `SELECT-INIT` (`select_initialized`) | 10 |
| B | `SLICE-CHECK` (`slice_check`), `SLICE-REPLACE` (`slice_replace`), `SLICE-INIT` (`slice_initialized`) | 8 |

Each `ubuntu-24.04` job has a 4,500 s ceiling, 1,800 s setup and build envelope with a 900 s build watchdog, 540 s finalization and upload, and 30 s launch headroom. Each canary gets 90 s Kani time, a 120 s child watchdog, and unwind 8. Each diagnostic root gets 60 s Kani time, a 90 s child watchdog, and unwind 16. Every root adds 3 s startup, 6 s child cleanup, 15 s inspection, and 8 s outer reap. Both use CaDiCaL and 12 object bits.

| Candidate | Roster envelope | Job margin |
| --- | ---: | ---: |
| A | `2 × 152 + 8 × 122 = 1,280 s` | 850 s |
| B | `2 × 152 + 6 × 122 = 1,036 s` | 1,094 s |

## Validation

From the parent of each clean, depth-three `control` checkout, these are the workflow's frozen control and synthetic test commands. `GITHUB_SHA` is the exact trigger SHA for that checkout.

```bash
export PYTHONDONTWRITEBYTECODE=1
export GITHUB_REPOSITORY=Tiramisu-Cake/kani GITHUB_EVENT_NAME=push
export GITHUB_REF=refs/heads/uninit-ci/ch8-q-pilot-v1 GITHUB_RUN_ATTEMPT=1
export GITHUB_SHA="$(git -C control rev-parse HEAD)"
python3 control/ch8-kani5196-diag-control/diagnostic.py validate
python3 -m unittest discover -s control/ch8-kani5196-diag-control
python3 control/ch8-kani5196-diag-control/diagnostic.py check-source --tool tool
```

| Check | A · Base comparison | B · SLICE fixture |
| --- | --- | --- |
| Frozen control and source | Passed 35 payload hashes, 5 fixture hashes, source coordinates, exact trigger event and parent, and 41 base tool hashes. Both canary hashes matched the original Git blobs. | Passed 35 payload hashes, 5 fixture hashes, source coordinates, exact trigger event and parent, and 41 PR-head tool hashes. |
| Diagnostic synthetic suite | 27 passed | 28 passed |
| Shared control and supervisor suites | 28 shared and 14 supervisor tests passed | 27 shared and 14 supervisor tests passed |

The shared suites ran from the candidate control checkouts with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ch8-kani5196-control` and `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ch8-q-pilot-control`. Both candidates passed workflow YAML parsing, `bash -n` for workflow shell steps, Python AST parsing, and `git diff --check` against the control and trigger parents. The event gates rejected a wrong ref, wrong trigger SHA, attempt `2`, and the control commit's direct parent. Both source gates rejected the other candidate's tool. Live compilation, generated GOTO, and calibration remain pending.
