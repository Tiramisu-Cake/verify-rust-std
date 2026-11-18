# W13 — compose S2 r2 source + W11 diagnostic runner

ISSUED by coordinator after owner request13:47. Correctness verification, not
security work. Fresh/current model+Fast, no subagents. STOP only real blocker,
not volume/context. No compiler, cargo/rustc/Kani/CBMC/full runner or CI.
Paths from `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Frozen inputs: source9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6,
package0a4cef493f858d0e91d3ebccfbbab0b8d32d0119/reviewe40ac8e8dd,
stock0aac16ef62da9e9d5645782d458593e5d78143ba, r1 control2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8.
Run44284869572 failed compile27.6s/0roots after cfg gate; missing rustc error,
preview omitted16235bytes; actual cause UNKNOWN. Your static report7de045996987af5454052c33c448eaf31e910a32
did not establish a concrete defect. R2 reduces risk, not a proven causal fix.

W11 runner package **ac956bdf4db98a95e2da988ccd2c527582d3d32f**, directory
`kani3300/ch8-s2/runner-diagnostics-r2/`; control
**b678fb6cdd5edf69a4e952167422f36a45a3d6cb**, tree
**beb2346615ffbb7027b2f1ea8ea33a149952aa0b**, parent
**9e14e033f9ee31522b571c127609dcdff76d230b**. Isolated worktree
`/root/kani-ch8-s2-diagnostics-w11` read-only; 29 targeted tests PASS, production
retention NOT_RUN. Its error-block collector/receipt/pack/fallback code stays owned
by11. Preserve bytes; localized runner findings return11, don't silently repair.

Source change: remove sort8_registration_only (all13 registration lines). Replace
sort8_stable verified stubs with one simple ordinary diagnostic model, no sort8 PFC
registration needed. Owner named general32_weak; coordinator found the same
stub_verified at sorting_s2_batch.rs:54 in **general32_assumed**, under the same cfg.
Both must use ordinary stubs, or removing registration recreates r0's missing-PFC
error. Check every effective root/cfg, including unselected compiled items.

The model must preserve the exact applicable u8/KeyLess domain, call signature,
input/output/init/frame/allocation and full-value sortedness/multiplicity relation
of the replaced summary. No empty/no-op/weak replacement for the assumed positive;
don't add Copy/trait restrictions to production signatures or mutate runtime std.
Prefer the smallest explicit implementation using existing model machinery, without
new PFC/old()/modifies machinery for sort8. Document exact concrete topology and
model domain. Both general32 probes remain DIAGNOSTIC_ASSUMED; no new proof credit.
The weak control still isolates weak_merge and keeps its sole S2_NEG_GENERAL32_WEAK
failure. Keep constructive/nonvacuity witness and all original assertions/covers;
new model/source semantic checks are offline diagnostics, not qualification.

Create isolated source/control worktrees, preserve all old candidates. Compose
new source + exact W11 runner into **one** immutable `kani3300/ch8-s2/batch-r2/`
package. Control must retain required parent9e14; no trigger/CI branch/publication.
Update source/request/fixture/hash/patch/CFG-PFC map bindings consistently. Gate
all11 effective roots: every remaining stub_verified target has active PFC; ordinary
stubs point to exact active replacements. Do not weaken unsupported/missing/wrongcfg/
foreign-name controls or hardcoded counts to hide unresolved uses. Recheck valid
remaining PFCs for insert_tail/merge/swap; sort8 removed registration grants nothing.

Same selection11roots,20covers,6exact negatives; same stock tool,600s/root,
compile900/group7500/internal8100/phase-step7560/job180min,1serialgroup,RSS12GiB+
2GiB headroom,checkout7/5/2 and all error/decoder/shutdown/fallback controls.
Preserve W11 diagnostics through request hash/packing changes. Run targeted Python/
static package/cfg/stub/model and relevant runner error-path tests once, including
long-middle diagnostics and truthful cap/partial completeness. No native compile.
Record semantic/model change in cost interpretation; don't compare missing r1
roots as measured speedup. No solver sweep or new budgets.

Package: exact full g0/source/control/tree/parent/request/workflow/tool pins,
SOURCE/CONTROL full+delta patches, ROW/CFG/STUB/model maps, runner byte-invariance
against ac956/b678 and any later reviewed immutable correction, manifests/validation,
CI request and HANDOFF. Narrowly justify every file delta. Runtime compile/model/
actual retention NOT_RUN. Old reviews do not approve the new combined source.

Reviewer14 receives exact committed combined package on READY; GO-request only
after APPROVE and resolved findings. Repeat/publication/accounting owner-only;
item1 28/28,item2 provisional10/14,total38/42, no assumed next charge number.
No CI/rerun/cancel/push/PR/ledger/reservation/budget. Exact ownpaths commit --only,
`[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>. Final
`READY <full g0 SHA> <source SHA/tree> <control SHA/tree/parent>`.
