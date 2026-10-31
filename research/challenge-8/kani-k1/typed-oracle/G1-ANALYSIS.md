# G1 terminal analysis — PARTIAL, recommendation STOP

Build `c8365803-0352-4695-a86d-8ecee29b59fe`; request `typed-oracle-g1-20261031-r1`.
Source `cb7445b2b4d4b6714c3ac7cf7a1757314d463e8f`; library
`702a552ae226f885fe03ef5e8af0a386848587ac`; request SHA-256
`66c2af602d22e45d3756349143aa42258fdde2dbc244ae06111bb0c9a5596895`.
Source/request/Kani identities agree across bounded summary, rows, Cloud status and process records.
`check-tooling` passed against cap `6b12002d79b6ccb4ded6c4790b1c592c65d6c591`:
actual pool k1-standard4 and all six bound-file hashes agree; lane unchanged.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`; repository toolchain nightly-2026-10-12
remains unchanged. Summary binds this Kani pin; runtime rustc version string is not exposed here.
Actual controls cfg ON, Linux jobs1, swap OFF, uninit checks OFF. Not Mac/jobs3 evidence.

## Status and control limitation

Cloud status FAILURE; tool compilation/build success; summary status COMPLETE; Kani exit1.
Eight positive harnesses SUCCESS, one control FAILED; no TIMEOUT, OOM or missing rows.
All nine completion covers reached (1/1 per wrapper). Exact cover property IDs are not emitted;
each wrapper has a single source completion cover, including bridge completion and control pre-assert.
Control failed1/613, unreachable67, covers1/1, 5.6921606 verification seconds.
Bounded log lines2749–2761 identify the failure in
`assert_u64_properties::<lt_u64 function item, 2>` at `typed_oracle.rs:68`, with message
`This is a placeholder message; Kani doesn't support message formatted at runtime`.
This does not match request expect_check `typed full-value counts are preserved`.
Both sortedness and count asserts are emitted from that macro invocation at line68.
The supported terse evidence supplies no distinct check/property ID or class to disambiguate them.
Source reasoning says the low-bit flip preserves the comparator key and should break native counts,
but that reasoning is not independently established count-only failure identity in this output.
Therefore control acceptance is PARTIAL/UNKNOWN; aggregate gate/expectation/measurement remain false.
No source or matcher was changed, and no automatic retry was submitted.
Eight individually successful positive rows remain recorded; no proof credit transfers to ordinary,
P2, migration or another caller geometry from this incomplete pilot acceptance.

## Matched observations

Verification seconds and per-process CBMC VmHWM are separate metrics. These ratios compare accepted
positive rows in one run; they are not an accepted aggregate gate or statistical performance proof.
Native checker has extra checks; these counts are reported rather than hidden in a combined speedup.

| Pair | old→new verification s | time change | old→new CBMC KiB | RSS change | checks old→new |
| --- | --- | --- | --- | --- | --- |
| G8 projection | 190.83966→274.23306 | +43.70% | 1584636→1597668 | +0.82% | 407→434 |
| G8 native total | 190.83966→245.28836 | +28.53% | 1584636→1543356 | -2.61% | 407→611 |
| G8 projected→native | 274.23306→245.28836 | -10.55% | 1597668→1543356 | -3.40% | 434→611 |
| S8 native total | 130.50938→127.12238 | -2.60% | 770328→726920 | -5.64% | 405→609 |
| A13 projection | 434.62630→467.07452 | +7.47% | 2231068→2235640 | +0.20% | 442→469 |

G8 projected→native is a preliminary count-only improvement conditional on projection; the full G8
native variant remains slower than the original oracle. S8's small single-run difference is not a
consistent gain across required pairs. A13 still checks the original generic callee ensures.
Bridge is separate: SUCCESS, 1.3681898s, 0/190 checks,70 unreachable,1/1 cover, CBMC PID9517/43416KiB.
Control is separate: FAILED,5.6921606s, CBMC PID9361/193352KiB; unresolved assertion identity above.
Decision STOP for migration/X6: no consistent useful time/memory benefit in required u64/A pairs.

## Timing and attribution limits

Sampler pages0/8 and8/1 contain9/9 direct CBMC records, each with unique metadata match, full
source/Kani/build identities and PID. `process-attribution.json` preserves those bounded records.
Sample interval2s; first_s/last_s are sampled process observations, not harness wall time.
All per-harness wall times and per-harness/PID driver peaks remain UNKNOWN: the existing interface
records no such fields. Driver whole-command peak1226980KiB is not assigned to individual harnesses;
CBMC PPID8825 is recorded but is not independent identification of a driver process/PID peak.
Whole verification invocation wall1998.06s includes library compilation; maxRSS2322532KiB.
Verify begins330s after validation; Cloud execution12:53:42.927707637→13:33:22.779046 UTC
also includes setup/summary/upload and must not be used as a harness runtime.

## Closure

Own UUID-only budget: build1, spentUSD0.5400, reservedUSD0; one unused slot remains.
Optional G2 NOT_RUN: prepared request remains available; current GO authorized G1 only.
The arithmetic would permit G2 (0.540+0.810=1.350<=2), but budget is not dispatch authorization.
No measured u8 savings. Static A-u8 consumer audit COMPLETE/source-only; no new A retirement/credit.
No semantic changes after GO, no new request dispatch, no raw/archive evidence or local proof tools.
