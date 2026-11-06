# Part 1 v8c: organizer CI in the fork (2026-11-05/06)

Head `44b972435aeff6ea88cd01e64ccea3727a98294e` (branch `submission/ch8-smallsort-part1-v8c`): one commit on upstream
`233f96f66ab3785881cead133817ed5db4c76b09` (Kani `cd355b0b`, nightly-2026-10-22); library tree = VEIGHTMAX
`d3982a6240`. Workflow files and `scripts/run-kani.sh` are upstream's, unchanged; all ten were started by
`workflow_dispatch` in the fork.

| Workflow | Run | Result |
|---|---|---|
| Kani | [42076933030](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/42076933030) | success, attempt 3. In attempts 1 and 2 some macOS jobs were cancelled before start ("not acquired by Runner ..."); only those jobs were re-run |
| Rust Tests | [42076946034](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/42076946034) | success, attempt 4; attempts 1–3 had the same macOS runner cancellation |
| Flux, RAPx, KMIR, VeriFast, VeriFast (negative), GOTO Transcoder, Build Book, Testable SIMD | 42076958431, 42076971590, 42076984436, 42076996717, 42077009448, 42077022181, 42077034275, 42077046192 | success, attempt 1 |

Autoharness jobs used for the table: ubuntu job 127419531422 (attempt 1, 1 h 53 min), macOS job 127574772560
(attempt 3, 2 h 18 min).

`v8c-autoharness-smallsort.tsv`: the 233 `smallsort::verify` harnesses in the two autoharness job logs (status,
Verification Time, satisfied covers), with the v7 times from run 41836353526 (same pin) where the harness exists in
v7, and whether the harness stubs `panic_on_ord_violation`. Extracted with `parse_log.py` from the `Thread N:` lines;
the workflow itself does not check covers.

| OS | SUCCESSFUL | failed checks | covers satisfied | sum VT | SmallSort share of all autoharness VT | max VT | > 300 s | > 200 s |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| ubuntu | 233/233 | 0 | 966/966 | 9103 s | 66.4% (of 13712 s) | 316.8 s `merge::general_direct_u64_n9` | 1 | 5 |
| macOS | 233/233 | 0 | 966/966 | 11651 s | 69.7% (of 16718 s) | 323.0 s `merge::general_direct_u64_n9` | 3 | 9 |

198 harnesses are common with v7 (v7 had 202; four were split into eleven parts). On the common harnesses the sum VT
changed from 7754 s to 7962 s on ubuntu (+2.7%) and from 8579 s to 10020 s on macOS (+16.8%). Some unchanged
harnesses slowed down on macOS only, e.g. `network::network_safety_unstable_u64_n0_to17` 88.6 → 263 s and
`network::dispatch_safety_unstable_u8_n18_31_32` 170 → 313 s; the cause (runner variance or the new contracts on the
real helpers that these routes call) was not investigated.

`panic-stubbed-ordinary.txt`: the 71 ordinary harnesses that replace `panic_on_ord_violation` with a stub, so their
result covers normal return only. Produced by `panicstub.py` (static, name-based: it finds the fn or macro invocation
that defines each harness and checks its attribute block, following macros). The same script gives 57 on v7.

No warning in the job logs points at `smallsort/verify`.
