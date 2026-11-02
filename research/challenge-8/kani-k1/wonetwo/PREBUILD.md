# WONETWO PRE-BUILD REVIEW

WAITING FOR COORDINATOR GO. No Build submitted; own UUIDs none, spent/reserved $0/$0.
The published packet commit is the review SHA. Task: `../TASK-WONETWO.md`.
Branch `experiment/kani-k1-wonetwo-20261102`; task base `305cce3cf11dd9181ca773175bca5804c982f0eb`,
WONEDIAG result base `b7a8db4a98`. Library-only commit
`4231462d124b8c69bfaa55dd0eb956717308f1be`; library tree `c407b96a8cde34a9f28b8a967bf897f74bd06992`.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12 unchanged.

## Complete change and preserved domain

`library.patch` is the full library diff: 49 appended lines in `verify/wrap/wone.rs` only.
All original bytes, including every N0..3/N3 harness and negative control, are an unchanged prefix.
All other library files, including ordinary N2 wrappers, are byte-identical to task base.
No changes to private Rust T/F/CMP/probe models, targets, requires/ensures/modifies or runtime bodies.
New PFCs reuse the original targets inside existing opt-in `wrap::wone`, after their definitions.
No visibility changes, copied types/targets, stubs, summaries, assumptions or length dispatch.

Each new PFC explicitly constructs initialized backing4, active offset1, literal len2;
A/B/probe/left/right remain independent unrestricted u8 values. All use original unwind16.
The contracts still require len<=3 and nonnull/aligned/readable initialized writable regions.
Ensures retain sorted keys x>>1 and scalar-old full-byte count at the independent probe.
All generated checks and write-set enforcement remain enabled; input_frame runs after return.

| New PFC in wrap::wone | Existing target / T / canonical F | Scratch |
|---|---|---|
| unstable_byte_n2 | unstable_byte_len / u8 / byte_less | unchanged real network route |
| freeze_noncopy_n2 | freeze_noncopy_len / private NonCopyU8 / noncopy_less | real general internal scratch48 |
| stable_byte_n2 | stable_byte_len / u8 / byte_less | separate uninitialized scratch48, entire mutable slice |

Stable u8 retains whole-slice scratch modifies and all 48 borrowed slots. No prefix borrow or init.
Its len>=2 requirement remains scratch.len()>=len+16 (18 at N2); this fixture supplies 48.
Uncontracted `input_covers_n2` runs after real return and input_frame, seven reachable goals per row:
return, reversed keys, increasing keys, tied-distinct values, duplicate values, probe hit/miss.
Source witnesses: reversed A/B=2/0, increasing=0/2, tied=0/1, duplicate=0/0;
hit probe=A, miss A/B/probe=0/0/1. These are satisfiability witnesses, not proof results.
No N0/N1/N3 cover is imported; SUCCESS requires intended checks plus all seven covers per row.
Stable Cell, old N3 rows, ordinary N2 wrappers and negative controls are not selected.

## Static checks, exact request and budget

`check_static.py` / `static-check.json`: PASS, ordinary exact200 unchanged, cfg-on exact394
= prior391 plus exactly the three new names; inherited opt-in and target order checked separately.
`pfc-order.txt`: ordinary pfc sites26/bad0. That script includes gated child PFCs;
its label is not the ordinary200 count. Rustfmt and whitespace PASS; Rust/comments<=100 columns.
`tooling-static.txt`: lanes/workflows/toolchain/pin unchanged vs
`30f77e859903df14b442ff9294d4fbbd44827f20`. No local cargo/rustc/Kani/CBMC run.
Native compilation, all N2 checks and covers remain NOT_RUN.

`g1.request.json` equals active `RUN-REQUEST.json`; request ID `wonetwo-g1-20261102`.
Request SHA256 `86fe88261638589df056b4276f5eda6484d6870f9afd3bf77efd4225c96d2008`.
Measurement / controls:true / kani_jobs:1 / uninit_checks:false / timeout10 / standard4.
Exactly three SUCCESS rows, with full exact names:

- `slice::sort::shared::smallsort::verify::wrap::wone::unstable_byte_n2`
- `slice::sort::shared::smallsort::verify::wrap::wone::freeze_noncopy_n2`
- `slice::sort::shared::smallsort::verify::wrap::wone::stable_byte_n2`

Validator PASS with max-total-minutes60; `request-args.txt` includes `--exact`.
Controls cfg enables availability; only the three new rows execute. No expected FAILED rows.
One Build only, no retry/G2: full proposed reserve (3*10+30)*$0.0135=$0.8100.
`budget-prebuild.txt`: global used $77.2035/reserved $0; projected $78.0135 <= cap $88.96.
Own builds0/1, spent/reserved $0/$0. Refresh global budget after exact-packet coordinator GO.
Library commit is separate from research/request; both use [skip ci], push without force.

## After coordinator GO only

Dispatch the published branch with tools/k1g.sh; record UUID/request/source/library identities.
Then `k1g.sh watch UUID` with CODEX_THREAD_ID and end the turn; no model polling.
At terminal use bounded K-1 status/summary/peaks and needed log-grep/log-lines; check-tooling
against `30f77e859903df14b442ff9294d4fbbd44827f20`. K-1 is outside Evidence Brief/Select-Merge.
VT=UNKNOWN unless printed; TIMEOUT/OOM are resource outcomes, not proof acceptance.
RESULT-WONETWO.md <=30 lines: rows/status/VT/RSS/covers/failed checks and four-wrapper table
(Cell N0..3; three other wrappers N2/N3). Prior evidence: RESULT-WONE.md / RESULT-WONEDIAG.md.
Proof scope only these fixtures with key x>>1, backing and scratch48; not N16 or generic T/FnMut.
New N2 PFCs do not replace ordinary N2 wrappers without a separate correspondence review.
Publish result with REVIEW REQUEST <sha> / WONETWO ЗАВЕРШЁН; stop after this single stage.
