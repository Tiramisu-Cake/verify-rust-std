# RESULT INTEGWRAP — PASS (WRAP-N2 wrappers in the ordinary Part 1 set)

Task `TASK-INTEGWRAP.md` (`55ef62880a`). Base `f000cb484e` (P1-CLEAN, library tree `73e902bec8`,
native 197/377); cap 88.96 inherited. Pin Kani `9461e07af7`, nightly-2026-10-12; tools/workflows/
flags untouched; no local cargo/rustc/Kani. Packet `integwrap/PREBUILD.md`, GO for `46417470bd`.
Library commit `4ef0f7984b`, library tree **`426fb74a829db04569a6e8eabed99cb78232962b`**
(identical in G1 head `46417470bd` and G2 head `c92a0889ab`).

## Patch

`verify/wrap.rs` (new) = WRAP-N2 `811c78777d` code (comment-stripped equality). Only deltas:
`cfg(kani_smallsort_controls)` on `always_true`, `rejects_always_true`, `rejects_payload_corruption`,
and 4 comments without research labels. `verify.rs`: `mod wrap;` appended (order unchanged), one
doc line. `smallsort.rs` and other verify modules byte-identical to base (runtime bodies/signatures
unchanged). Static gate 23/23 (`integwrap/static-check-prebuild.json`), rustfmt `--check` clean.

## Sets (names next to this file)

- ordinary exact **200** = P1-CLEAN 197 + `wrap::{stable_cell_n2, unstable_byte_n2,
  freeze_noncopy_n2}` — `integwrap/ordinary-expected.txt`; native G2 equal as a set.
- cfg-on **382** = P1-CLEAN 377 + those 3 + `wrap::{rejects_always_true, rejects_payload_corruption}`
  — `integwrap/cfg-on-expected.txt`; source-derived, no native cfg-on inventory in this task
  (G1 compiled the whole cfg-on tree and ran all 5 wrap names).

## Builds (k1-standard4; own 2 builds, $0.7155 ≤ $1.8, reserved 0)

| Build | UUID / request | Result | Cost |
|---|---|---|---|
| G1 | `26f3b7d8-df01-4ef8-9d80-7315316b39fc` / `integwrap-g1-20261101` | COMPLETE, gate/expectation true, 5/5 as expected | $0.1755 |
| G2 | `0e3bda37-d158-4a8e-942a-68f9b1579a5c` / `integwrap-g2-inventory-ordinary-20261101` | exact 200 | $0.5400 |

Head/pin/request sha256 (`e23558b8…`, `60304112…`) match; check-tooling vs `30f77e8599` ok ×2.
Project after: used $72.6945 / $88.96, reserved $0 (`integwrap/budget-final.txt`).

## G1 rows (controls on, jobs 1, uninit off; Kani exit 1 from the 2 controls only)

| Harness (wrap::) | Status | VT s | cbmc RSS KiB | Fail/total | Covers | Failure location |
|---|---|---|---|---|---|---|
| stable_cell_n2 | SUCCESS | 34.27 | 234444 | 0/300 | 9/9 | — |
| unstable_byte_n2 | SUCCESS | 27.06 | 237544 | 0/481 | 7/7 | — |
| freeze_noncopy_n2 | SUCCESS | 168.09 | 836468 | 0/461 | 7/7 | — |
| rejects_always_true | FAILED = exp. | 0.43 | 37412 | 1/544 | 3/3 | `wrap canonical comparator required` wrap.rs:61 |
| rejects_payload_corruption | FAILED = exp. | 0.65 | UNKNOWN (not sampled) | 1/325 | 1/1 | `wrap full-value checker rejects payload corruption` wrap.rs:269 |

RSS = sampled cbmc VmHWM (2 s, direct metadata binding, `integwrap/g1.peaks.txt`); whole run
time-v max 2124060 KiB (compiler), wall 5:59.61. All 27 covers reached; unreachable checks
10/18/8/37/18 are not covers. No unwind/OOM. Check totals differ from WRAP-N2 (300/481/461 vs
304/497/473): callees carry no generic contracts on this tree; this run is the evidence here.

## G2

Native ordinary inventory 200 names, names SHA-256 `a4f73537…71c` (kani-list order); sorted set
equal to `ordinary-expected.txt`, 0 missing / 0 extra (`integwrap/g2.inventory.txt`).

## OPEN / NOT_RUN

The other 197 ordinary proofs are NOT_RUN on tree `426fb74a82` (coordinator full CI, both OS). No
claim of a general FnMut, stable tie order, padding, init detection, unwind or full-threshold result.

P1 V3 CANDIDATE library tree 426fb74a829db04569a6e8eabed99cb78232962b
