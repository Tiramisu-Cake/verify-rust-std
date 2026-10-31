# WRAP-N2 PRE-BUILD REVIEW — WAITING FOR COORDINATOR GO

Prepared 2026-10-31T19:50:13+00:00. Worktree `/root/verify-rust-std-kani-wraptwo`,
branch `experiment/kani-k1-wraptwo-20261031`; no build dispatched.
Base `6f3a2629615cc7184b840d3c21aaea54b129267e` (task-only commit c6b2d61129 followed it).
Source/library commit `471db13c99bde77722a8f717e8efeef3397eb683`; library tree `20c91cb296489182f14384a1b78b31f04eb16932`.
Kani pin `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12 unchanged.

## Concrete contracts and source dispatch

All three PFCs target free, concrete forwarding functions; each passes the supplied typed
fn pointer to the real qualified trait entry with no leaf, panic, adapter or verified stubs.

| Wrapper / PFC | Concrete entry and implementation | Real N2 work |
|---|---|---|
| stable_cell / stable_cell_n2 | `<Cell<u8> as StableSmallSortTypeImpl>`; !Freeze blanket default | insertion from index 1; scratch ignored |
| unstable_byte / unstable_byte_n2 | `<u8 as UnstableSmallSortTypeImpl>` → Freeze/Copy specialization; efficient swap | network route, insertion only, no sort9/sort13/merge |
| freeze_noncopy / freeze_noncopy_n2 | `<NonCopyU8 as UnstableSmallSortFreezeTypeImpl>`; Freeze + !Copy default, size1×48≤4096 | general: two singleton copies, merge directly into input, forget panic copy-back guard |

Dispatch source: smallsort.rs Stable impl lines30–46; Unstable Freeze forwarding90–105;
Freeze default113–133 and Copy impl142–170; general205–293; network311–376.
NonCopyU8 is local repr(transparent), has no Copy/Drop and exports no existing private type.

Each requires N=2 and readable/initialized, writable typed input region, then canonical fn
address equality (the same cast comparison as StageA). Each modifies only `v`, ensures pure
`sorted(v)` by key `model >> 1`, and `old(count(v, probe)) == count(v, probe)`.
Models: complete u8 / Cell.get() / NonCopyU8.0; count compares full bytes, including low bit.
Probe is a separate unconstrained u8 argument, unchanged and shared across scalar pre/post
counts; no static state, byte oracle, representation/padding read or F call in specifications.
Typed init predicates declare the premise; stock uninit-off is not an init/UB detector.
Ordinary generic helper contracts remain StageA baseline; this patch migrates no consumer.

Positive domains: initialized backing[4], input subregion[1..3], symbolic outside sentinels.
Stable scratch: separate MaybeUninit<Cell<u8>>[2], initialized symbolic slot0 and unread uninit
slot1, exposed len0..2; check slot0 unchanged. Other scratch is local to runtime bodies.
No typed slice/reference is created over the uninitialized general/network scratch tails.
Unwind16 on all five harnesses; model/count are componentwise and never compare arrays.
No unwinding assertions disabled. Covers expected9/7/7: reversed, increasing, tied distinct
values, duplicate values, probe hit/miss and each entry return; Stable adds empty/uninit tail.
Frame assertions check backing prefix/suffix for each PFC and initialized Stable scratch.

## Exact G1 request and controls

`g1.request.json` is byte-identical to `../RUN-REQUEST.json`;
SHA-256 `315459c5e6060019967b01bd7fe244c6a68db36edfb85ba44435578a8ef1d8ba`. Namespace prefix below:
`slice::sort::shared::smallsort::verify::wrap::`.

| Exact suffix | Expect | Required check / expected covers |
|---|---|---|
| stable_cell_n2 | SUCCESS | sorted + full-value count + input/scratch frame; 9 covers |
| unstable_byte_n2 | SUCCESS | sorted + full-value count + input frame; 7 covers |
| freeze_noncopy_n2 | SUCCESS | sorted + full-value count + input frame; 7 covers |
| rejects_always_true | FAILED | `wrap canonical comparator required`; 3 covers |
| rejects_payload_corruption | FAILED | `wrap full-value checker rejects payload corruption`; 1 cover |

First control: plain proof, symbolic case0..2 reaches each wrapper with its typed always-true
pointer. Literal kani::assert at wrap.rs:61; rejected guard returns before trait call.
Requires and guard use identical canonical predicates; PFC assumes the valid canonical case.
The lane's unchanged `--no-assert-contracts` is why the explicit body guard is used by this
plain control. No PFC assumptions or stub summary can hide the invalid-pointer call.
Second: plain real Unstable u8 trait entry with canonical F, no wrapper mutation. The same
sorted/count helpers must pass before flipping v[0]^=1; sorted keys must still pass, then only
literal kani::assert at wrap.rs:227 is expected to fail. Probe remains independent.
Unrelated failure, unwind, timeout, compile/unsupported error is not control acceptance.

G1 settings: measurement, gcb-e2-standard-4 / k1-standard4 (4CPU/16GiB), controls=true,
kani_jobs=1, uninit_checks=false, 10min/harness. Native compile and all proofs NOT_RUN.

## Budget and conditional G2

Own builds0, spent$0, reserved$0; task cap$2, ≤2 builds including failed/retries.
Project prebuild budget: used$69.9135, reserved$0, cap$88.96; see budget-prebuild.txt.
G1 envelope5×10+30=80min×$0.0135=$1.08 (project upper bound$70.9935).
G2 retry only after a semantic/compile fix, fresh delta review/GO and budget check: exact same
five rows on the new tree, reserve$1.08; G1 actual must be≤$0.92 or report PARTIAL.
Optional ordinary inventory template: controls=false, work20+overhead30=50min/$0.675,
only a semantically unchanged tree and within the 2-build cap. It cannot see wrap.
After successful G1, inventory may be skipped honestly as NOT_RUN: ordinary library projection
is byte-identical. Inventory is not evidence for wrapper proofs or a substitute for G2 retry.
Fresh global and own cost checks are mandatory before any authorized dispatch; cap unchanged.

## Static validation and review boundary

`check_wraptwo.py`:30 checks PASS (scope, cfg-off projection, pin/lane unchanged, exact rows,
clauses/oracle/frames/entries, literal locations, request validation). These are lexical/source
checks, not compile/proof evidence. Rustfmt --check on both changed Rust files and diff --check
PASS. Separate Luna High read-only review found no correctness/dispatch issue, including final
scratch len0..2 update; see SOURCE-REVIEW.md. No local cargo/rustc/Kani/CBMC was run.
Library changes are only new verify/wrap.rs and cfg registration at end of verify.rs;
runtime bodies/signatures, other verify modules, toolchain/tools/workflows are unchanged.

STOP: coordinator reviews the published package, then explicitly sends GO before G1 dispatch.
After GO: fresh budget → k1g.sh dispatch experiment/kani-k1-wraptwo-20261031 →
k1g.sh watch UUID → end turn. No status polling. Read bounded K-1 summary/peaks/log slices,
check-tooling UUID 30f77e859903df14b442ff9294d4fbbd44827f20 and identities after completion.
No Evidence Brief / Select-Merge phase applies to this K-1 task; no raw/full logs or archives.

This is an N2 forwarding-contract interface/PFC/control pilot; all proof outcomes are NOT_RUN.
No integrated PASS, literal trait contract, threshold-complete, stable-order, arbitrary-F,
padding, uninit detector, panic/unwind theorem or proof credit is claimed. Extension to N7/N8
needs fresh real-body proofs, covers, matched probe/frame domains and resources; general gains
nontrivial half insertion/merge, network grows insertion work. Three names cover three selected
paths, not all six trait implementations; no new target beyond N2 is prepared here.
