# PANICPROBE result (E1): should_panic calibration holds; guard attribution UNKNOWN by description
Build `aff12270-00bd-49e5-a680-5bab36e988eb` (k1-standard4, 18:27:31–18:41:42Z), head `e147981c0a`, library commit `4bd0da5ac0`
(tree b2d54f08), request `panicprobe-e1-diag-6roots-20261103` sha256 d1dccfe4…dbe6b, Kani 9461e07a; check-tooling vs
e8e238db9d rc 0. Run COMPLETE, Kani exit 1, Cloud Build FAILURE, lane gate False (expectation_met False: rows 4/6, below).
| # | Root | Status (verdict line) | VT s | Checks | Failed descriptions (terse) | Covers | CBMC RSS |
|---|---|---|---:|---|---|---|---:|
| 1 | panic_control_plain | SUCCESS (panics as expected) | 0.04 | 1/2 | placeholder | 1/1 | UNKNOWN |
| 2 | panic_control_ub | FAILED (failures other than panics) | 0.07 | 2/8 | placeholder; `dereference failure: pointer outside object bounds` | 1/1 | UNKNOWN |
| 3 | panic_network_u8_n18_should_panic | SUCCESS (panics as expected) | 37.0 | 1/279, 11 unr. | placeholder | 1/1 | 0.48 GiB |
| 4 | panic_network_u8_n18_plain | FAILED | 36.0 | 1/279, 11 unr. | placeholder | 1/1 | 0.48 GiB |
| 5 | panic_general_u8_n16_should_panic | SUCCESS (panics as expected) | 26.0 | 1/255, 4 unr. | placeholder | 1/1 | 0.41 GiB |
| 6 | panic_general_u8_n16_plain | FAILED | 21.2 | 1/255, 4 unr. | placeholder | 1/1 | 0.40 GiB |
## Gates and classification
"placeholder" = `This is a placeholder message; Kani doesn't support message formatted at runtime`. Lane gate per row: rows
1/3/5 met; row 2 met (located pointer check); rows 4/6 not met: the guard description is the placeholder, not
`does not correctly implement a total order`. Expectations were not changed. CBMC RSS: per-row peaks (`peaks.txt`);
rows 1/2 finished between 2 s samples. Whole run max RSS 1.66 GiB (time -v), kani-compiler 1.62 GiB; no OOM.
- Calibration correct: row 1 SUCCESS, row 2 FAILED with panic + pointer check. Rows 3 and 5 SUCCESS.
- Rows 4/6: exactly one failed check each, no pointer/arithmetic/other-class check failed (row 3/5 verdict lines confirm
  all failures are class assertion). But the one description is the placeholder, which core `panic!` literals share
  (rows 1/2 show it too). By the criterion and the coordinator's GO ("attribution by Failed Checks descriptions"):
  **guard attribution UNKNOWN**; the conclusion "stub cuts only paths that reached the guard" is not claimed.
- Fact, not counted: contrary to the GO note, this terse log does print `File:` lines (log-grep, `log-grep-harness-file.txt`).
  Each failed check of rows 3–6 is at `smallsort.rs` line 854, `in slice::sort::shared::smallsort::panic_on_ord_violation`
  (the `panic!` of the guard). Whether this location may serve as attribution is the coordinator's decision.
- No compile warning in smallsort sources (`[-]> .*smallsort`: no match). No unexpected failed check to escalate.
## Limits and cost
Domain u8 only, N16 (stable general) and N18 (unstable network), comparator any-bool, no read, no mutation. Not checked:
uninit/validity, unwind cleanup (Kani panics do not unwind; `CopyOnDrop` not run), the original volatile comparator.
Own spent $0.1890 (cap $1.30); project after: used $90.1365, reserved $0.9450 (other owner), cap $93.96. One Build, no retry.
## Addendum (coordinator decision after review of e288f8bf08)
Location `smallsort.rs:854 in panic_on_ord_violation` accepted as unambiguous attribution (controls point at their own
panicprobe.rs lines 37/48/54). Diagnostic classification counted: on u8 N16 general and N18 network without stub the only
failed check is the guard panic; no other default-check failures. Conclusion: the stub cuts paths that reached the guard;
no other default-check failures found on these two domains. Lane gate of rows 4/6 unchanged: frozen gate not accepted.
