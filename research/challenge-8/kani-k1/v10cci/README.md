# SmallSort submission head: organizer CI in the fork (2026-11-07)

Head `872d5a43380752786415bc00d2a12ce0e930cb37` (branch `submission/ch8-smallsort`): one commit on upstream
`233f96f66ab3785881cead133817ed5db4c76b09` (Kani `cd355b0b`); library tree `b2482f4508` (INSERTPFC, which also ran
the 13 negative controls and the cfg-on inventory on this tree). Workflow files and `scripts/run-kani.sh` are
upstream's, unchanged; all ten were started by `workflow_dispatch` in the fork.

| Workflow | Run | Result |
|---|---|---|
| Kani | [42363378063](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/42363378063) | success, attempt 1 (16/16 jobs) |
| Rust Tests, Flux, RAPx, KMIR, VeriFast, VeriFast (negative), GOTO Transcoder, Build Book, Testable SIMD | 42363383857, 42363389143, 42363394305, 42363399372, 42363404755, 42363410264, 42363415347, 42363420522, 42363425836 | success, attempt 1 |

Autoharness jobs used for the table: ubuntu job 128376214089 (1 h 41 min), macOS job 128376214006 (2 h 03 min).

`v10-autoharness-smallsort.tsv`: the 235 `smallsort::verify` harnesses in the two autoharness job logs (status,
Verification Time, satisfied covers), the times of the same harness in the previous head `22082ba685`
(`../v9cci/`), and whether the harness stubs `panic_on_ord_violation`. Extracted with `parse_log.py` from the
`Thread N:` lines; the workflow itself does not check covers.

| OS | SUCCESSFUL | failed checks | covers satisfied | sum VT | SmallSort share of all autoharness VT | max VT | > 300 s | > 200 s |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| ubuntu | 235/235 | 0 | 978/978 | 7802 s | 65.9% (of 11833 s) | 246.1 s `merge::stable_direct_u64_n9` | 0 | 2 |
| macOS | 235/235 | 0 | 978/978 | 10534 s | 70.3% (of 14978 s) | 340.5 s `merge::general_direct_u64_n9` | 1 | 5 |

Against `22082ba685`, the head differs only by two `proof_for_contract` harnesses for `insertion_sort_shift_left`
(`helper_contracts::insertion_safety_u64_len{2,3}`: ubuntu 40.4 / 45.9 s, macOS 47.9 / 55.2 s). The 233 common
harnesses sum to 8916 → 7716 s on ubuntu and 9999 → 10431 s on macOS. Single-run timings on hosted runners vary; no
cause is claimed for the differences.

`panic-stubbed-ordinary.txt`: the 71 ordinary harnesses that replace `panic_on_ord_violation` with a stub, so their
result covers normal return only; identical to the v9 list (the two new harnesses do not stub it). Produced by
`panicstub.py` (static, name-based); the two `merge::sort4_arbitrary_comparator_{u64,bytes16}_n4` harnesses come from
a two-function macro the script does not follow and were checked by hand: no stub.

No warning in the job logs points at the SmallSort files.
