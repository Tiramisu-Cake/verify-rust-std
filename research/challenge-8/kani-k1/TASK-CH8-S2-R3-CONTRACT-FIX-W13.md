# W13 — S2 r3 contract macro repair and active-stack audit

ISSUED by coordinator on owner15:27 request. Fresh /new13, preserve current model/
tier, Fast OFF, no subagents. Correctness verification, not security work.
STOP only real blocker, not volume/context. No cargo/rustc/Kani/CBMC/compiler/
macro-expansion executable/full runner or CI. Python/static checks allowed.
Paths from `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Known r2 outcome, coordinator/ledger7560bc06534233b11cb0c01959b2a82e6f994def:
run44302170220/attempt1 compileFAILED23.4s/0roots, diagnostics complete, exactly
one error: `Failed to find contract closure __kani_recursion_check_swap_if_less
in function core::slice::sort::shared::smallsort::swap_if_less`.
R2 is uncharged under confirmed pre-root compile failure rule; r0/r1 also0.
R1 actual diagnostic remains UNKNOWN; similarity is a hypothesis, not new evidence.
One compact artifact ch8-s2-batch3probes-44302170220-1 may be read only if needed
to pin the retained diagnostic. No full/raw logs/archives/Cloud bypass or new run.

Frozen sourceefb1aba7fc6445cba6cd75154713b598c9e2579d/tree4563e06722871ae5eafdf6d288afa21a406b6ba8,
worktree `/root/verify-rust-std-ch8-s2-r2-final-w13`; final package
5a9e715ad9e303fbd10600ee379313301c87e9b3/reviewa2d6428b35930282b03f91eeadba72eaf3cbef9b,
control2ce62b5bb31abd44824dc8e358f77e63d539ed98/treedadbd710770720cd360529188c81c6d19a8de61c,
required parent9e14e033f9ee31522b571c127609dcdff76d230b. Stock tool
0aac16ef62da9e9d5645782d458593e5d78143ba unchanged. Trigger59ff/r2 history immutable.

Repair swap_if_less contract annotations under s2_assumed. Trace exact stock macro
source: safety::requires wrapper expansion, direct crate::kani::* paths, attribute
ordering/group recognition and creation/lookup of __kani_recursion_check closures.
Compare pure direct requires/modifies/ensures stack on sort8_stable. Prefer smallest
consistent macro-family/ordering fix; no compiler/toolchain patch or replacement
with a weaker assumed stub. Preserve **all actual predicates**: current source has
five safety::requires clauses (two offsets, same allocation, two access clauses),
write-set/frame, semantic ensures with old(), comparator/domain restrictions and
function signature/body. Do not implement the owner's approximate clause count
as deletion. Preserve non-s2/S1/runtime safety annotations and effective semantics;
any conditional normalization must retain their original predicates outside S2.

Audit every active function contract stack in the S2 consumed source/module slice
for all11 effective cfg contexts, including unselected compiled items. At least
swap_if_less, insert_tail, sort8_stable, bidirectional_merge and active callers/
providers/model helpers must be enumerated. Record full path, source/hash/line,
effective attrs in expansion order, wrapper/direct macro family, cfg availability,
expected generated closure group and exact unchanged premise/frame/post semantics.
Fix the same concrete pattern where needed, not merely the first reported site.
An offline source check must distinguish the known old mixed/ordering pattern from
the repaired stacks and reject missing/wrong-cfg/inconsistent variants. If adding
a reusable preflight, integrate into existing check-source before tool build, with
targeted tests; no claim that static classification proves Rust compilation.

Keep the reviewed r2 ordinary diagnostic_sort8 in BOTH general32 probes, removed
sort8_registration_only,11roots/20covers/6negative oracles, model/witness/frame/
domain and DIAGNOSTIC_ASSUMED boundaries. Production algorithm CFG/bodies/generic
signatures unchanged; no added Copy bounds, weakened checks or new proof credit.
Source old-field/runtime invariance and prior model/runner conclusions should be
inherited by exact unchanged bytes rather than a repeated broad audit.

Create isolated source/control candidates; preserve all old branches/objects. New
immutable g0 package `kani3300/ch8-s2/batch-r3/` contains exact source/control/tree/
parent/request/workflow/tool pins, full/delta patches, source/contract-stack/CFG-PFC/
stub/row maps, manifests, targeted validation and HANDOFF. Control parent stays9e14;
source topology must preserve base99e within checkout5 without rewriting old commits.
Review derivation delta fromefb even if new parent is condensed97ac. Update only
necessary source/payload/fixture/request/hash bindings and the targeted source gate.
Retain repaired runner diagnostics B01/B02 code byte-identically except required
identity literals/gate integration; no unrelated runner repair. Production error
retention now observed by coordinator; do not claim complete producer universality.

Same stock/caps/selection:600s/root,compile900,root-sum6600,group7500,internal8100,
step7560,setup1800,job180min,serial1,RSS12GiB+2GiB headroom,checkout7/5/2.
Run relevant Python/static contract/CFG/model and changed service/error-path checks
once; no broad unchanged suite or native compiler. New compile/runtime/model
qualification remains NOT_RUN; r3 is a source-supported repair pending CI.

READY -> independent14 delta review -> root exact GO-request r3. Retry/publication/
accounting require separate owner/coordinator GO; no CI/rerun/cancel/push/PR/ledger/
reservation/budget actions. Currentitem1 29/29,item2 **9/14**,total38/43 reference.
Old intake474 is superseded, not issued. Exact ownpaths commit --only, `[skip ci]`,
Tiramisu-Cake <igkharin@gmail.com>. Final `READY <full g0> <source/tree> <control/tree/parent>`.
