# `sort4_stable`: generic proof architecture decision

## Current disposition after no-patch review

[No-patch phase](SORT4-NO-PATCH-PHASE.md) completed2026-10-06;
[assessment](SORT4-NO-PATCH-ASSESSMENT.md) is the current feasibility conclusion.
Official26.10 retains the relevant tuple/HRTB/direct-unwind/scratch-copy blockers;
normal-only annotations and the integrated Kani route did not provide a new
full-resource c1 hypothesis. No new run or generic sort4 proof. This is not a
proof of universal no-patch impossibility. Current recommended next task is the
bounded contract/admissibility review, pending owner decision. Verifier development
is not selected. The proposal below is preserved as **history, NOT AUTHORIZED**;
the no-patch approval did not authorize its dependencies or exceptional routing.

## Historical architecture decision

Decision 2026-10-06: recommend only a separately reviewed one-callback
normal/direct-unwind recovery gate using explicit proof continuations.
Existing patches are insufficient for full generic sort4; copying to raw scratch,
selection semantics and five-call composition remain dependencies.
See the selected route and exact owner decision below.

Follow-up approval: [SORT4-CONTRACT-PHASE.md](SORT4-CONTRACT-PHASE.md) permits
refining the contract and selecting one concrete architecture proposal from
existing evidence. No new VeriFast run, patch build/application or semantic
implementation is authorized. This assessment's existing proof boundaries
remain unchanged; use [STATUS](STATUS.md) for the current checkpoint.

## Retained frozen-profile assessment

**No established source-exact route under the frozen VeriFast profile was
identified; no generic diagnostic was dispatched.** This is a feasibility
assessment, not a theorem that every unchanged-tool route is impossible, and
not an executed `sort4_stable` proof. The approved Kani functional harnesses
were completed independently in [the hosted functional result](SORT4-RESULTS.md).
The only established unrestricted
generic target result remains the isolated `has_efficient_in_place_swap`
size helper; none of it proves comparator calls, pointer copying, or
`sort4_stable` ownership.

## Obligations versus existing evidence

The exact target is
[`library/core/src/slice/sort/shared/smallsort.rs`](../../library/core/src/slice/sort/shared/smallsort.rs),
blob `e555fce440872898e47fd5114f32eb15401d07df`. Its five actual
`FnMut(&T, &T) -> bool` calls need tuple-2 argument ownership and the
higher-ranked `FnOnce::Output = bool` projection. Each call creates two
shared-reference obligations and needs a normal continuation that accounts
for the live borrow and callback resources. Safety alone does not require
ending each shared borrow before the next comparison; shared borrows may
coexist where the Rust lifetimes permit it. By normal return, the proof must
recover the resources required by its postcondition. Each callback can unwind
directly; on that edge, the proof must account for the source/frame resources,
the current callback resource/state, and one current logical ownership
sequence while preserving permitted callback effects. The actual
body then needs four initialized and valid source reads, four valid writes,
the per-copy non-overlap condition, a sufficient cross-range separation
argument, and an ownership protocol for generic values after copying. The
caller’s `Freeze` bound is not on `sort4_stable` and does not imply `Copy`.
Safety cannot add comparator purity/order assumptions.

The first frozen-verifier blocker is evidenced by an actual `insert_tail`
comparator. Repeating the same callback setup under a `sort4_stable` label
would test a new body, but the evidence makes the same callback-boundary
failure likely; this is an inference from the shared compiler `FnMut` shape,
not an executed sort4 VeriFast result. It was judged unlikely to change the
phase decision:

- In [run 37400422055](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37400422055),
  unchanged VeriFast 26.09 reached the real generic `FnMut::call_mut` setup
  and failed to construct the tuple-2 `Args.own` resource. Related ghost
  closure and prelude-overlay attempts are documented as parser/definition
  failures in [the tuple ownership note](verifast-tuple-parser.md); they did
  not prove a comparator call.
- Compiler MIR evidence records the actual `for<'a, 'b> FnMut<(&'a T, &'b T)>`
  bound and `for<'a, 'b> FnOnce::Output = bool`. The compiler MIR evidence is
  recorded in [run 37408278446](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37408278446).
  The unchanged release translator omits that bound-region projection at a
  call; the tuple-parser-only diagnostic, before the HRTB translator patch,
  in [run 37407173581](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37407173581)
  reaches the Output-versus-bool mismatch. The targeted HRTB diagnostic,
  using the tuple-parser profile, in [run 37409198258](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37409198258)
  advanced past that return-type mismatch, then stopped at the actual
  `tail.read()` ownership obligation. This required a verifier semantic patch
  that this phase forbids; it is evidence of the missing capability, not
  authorization to import it. The guard regressions and borrow-access result
  in [run 37410979109](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37410979109)
  still did not establish complete recovery of the comparison resources.
- The separate unchanged-release normal recovery control in
  [run 37437514808](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37437514808)
  proves a useful but narrower fact: a generic `T` caller can recover two
  current cells and `T.own` after ordinary shared references in a natural
  block. It includes no `FnMut` callback, five sequential comparisons,
  source-exact lifetime boundary, or callback unwind. The later actual
  `insert_tail` diagnostics retain direct-unwind, scope, and storage blockers;
  see [the prepared-phase report](PREPARED-PHASE-2026-10-06.md).

Together these results show a missing tuple/HRTB/resource-recovery proof
route, not a `sort4_stable` failure. The shorter body removes insertion's gap,
loop, guard and `ManuallyDrop` obligations, but still makes five callback
calls and copies generic values. A new hosted unchanged-release probe was
judged likely to reach the same front-end/callback boundary and not change
this decision, so it was not justified.

## Remaining safety and UB obligations

No generic `sort4_stable` property is checked yet. A future proof must still
establish:

- provenance, alignment, bounds and initialization for all four source
  elements and four destination slots, including ZST pointer semantics;
- non-overlap for each executed `copy_nonoverlapping`, plus a clear
  cross-copy argument preventing earlier writes from changing later sources;
- no lost prior destination resources and exactly one current logical
  ownership sequence for non-`Copy`, destructor-bearing values, without
  assuming a second independently droppable copy;
- all five callback calls at their actual generic types, accounting for the
  live shared-borrow resources at each continuation and recovering the full
  resources required by the normal and direct-unwind posts;
- the updated `F` and frame state, including valid interior/callback effects
  on both normal and panic paths; sortedness/stability require separate
  functional assumptions;
- explicit evidence for dangling/misaligned access, uninitialized reads,
  immutable-byte mutation and invalid values.

The Kani evidence ledger records two material instrumentation boundaries:
`copy_nonoverlapping` validity checks are unsupported in the pinned run
37396688760, and the immutable-byte mutation detector gap was reproduced in
37397720683. A default-check functional success cannot close either category.
The other UB categories also need results applicable to this target; previous
isolated detector controls are not a proof of this generic function.

## Selected route — explicit recovery continuations, one comparison epoch

Decision dated2026-10-06: recommend a **separately approved bounded prerequisite
experiment** for a source-defined exceptional recovery continuation, using the
narrow tuple/HRTB interpretations as reviewed dependencies. NO-GO for claiming
the existing patch chain already proves generic sort4. This proposal is
NOT AUTHORIZED for implementation/build/dispatch in the current phase.

A single comparison lifetime can cover the real unsafe-block prefix containing
c1..c5. The proof would share the four source cells once, track genuine reference
initialization accesses at each call, and retain their borrow-end obligations.
Shared borrows may coexist; ending/recreating a lifetime at each comparison is
not a safety requirement. After successful c5, close every remaining access,
leave the annotated epoch BEFORE the four copies, obtain the full lifetime
token, invoke a checked ordinary recovery helper and recover four current owned
source cells. Index/permutation reasoning then supplies the selected read cells
for the four copies. The proof must derive real pointer permissions, not only
numeric equality of addresses.

At panic c_k the same kind of helper must run after leaving the epoch, using
the resources actually outstanding at that point (including earlier calls),
before the original direct-unwind return. A source-written ordinary helper,
not an auto-lemma/axiom, must consume genuine access/borrow-end tokens and return
full current T.own/storage, F and frame. Earlier callbacks' and the panicking
callback's legal effects survive. Each of the five paths needs its own checked
resource state, not a post returning comparison debt.

The missing frontend capability is an explicit, fail-closed annotation associating
those source-written recovery statements with the actual `UnwindAction::Continue`
edge. Conceptually: Continue→leave borrow epoch→ordinary checked recovery→the
original unwinding ReturnStmt. In the complete one-epoch plan the normal edge goes through ordinary recovery
after c5, before the unchanged first copy. The c1-only prerequisite fixture
instead recovers immediately after its sole call, before its return. This is a **new trusted translation**, even
if implemented using existing AST blocks/gotos. Existing strict lifetime-cut
also changes `verifast.ml`; this proposal is not “kernel-free” by relabeling it.
No annotation syntax or new patch is implemented here.

### Dependency table and reviewed evidence

All referenced patches are read-only evidence. Hashes below are of the current
checked-in patches; source is VeriFast26.09
`809de4596839b739dd999f9e462242c835e3af46`.

| Needed capability / exact material | Observed result | Unproved gap / disposition |
| --- | --- | --- |
| Transparent tuple-2 field ownership, [tuple patch](verifast-tuple-own.patch), SHA256 `ff2576f727d13d9dfcd9616a030b72ad0b0a27ce87cc96014af2d2ba42249660`; parser input `f7f2c2bf573be09d8ce5dcd640ddca0e1437a8f18464facc9621ac287a5082e8` | 37406214235 reaches actual insert_tail callback preconditions; 37407173581 consumes explicit unwind debt and passes leak check, then fails Output vs bool | Candidate reuse only after trust/tuple-share compatibility regression. Cannot synthesize field owners from nothing. |
| Compiler-exported two-region FnOnce::Output=bool instance, [HRTB patch](verifast-fnmut-hrtb.patch), SHA256 `d90fb7a814b098a6008c4e64c567d2a3798e8f18999d12905425ef17224dbe1f`; translator input `7319d2638c3fc49a1663b50925d565ca2e10d95754933ed58e37f27239936803` | 37409198258 passes result type; 37410979109 passes8 real-MIR matcher cases | Candidate reuse; matches actual F, both T, regions, bool projection and unique bound. Match tests intentionally lack resources and fail; they are not eight callback proofs. Sort4's actual exported shape still needs auditing. |
| Strict shortened epoch, [lifetime-cut patch](verifast-end-lft-binding.patch), SHA256 `bd95733ec743be3ff343f653a2d8c49339315d3085c9faf1da4d096748fdf77c`; translator after HRTB `ef88c9c08388ef85bc661675f19212041e37b341d5ab61132ff80e5b9080b8d4`, kernel input `5968a05e264042782e8373c452b241ccdd1f4ba3323d596888a9bdf6b18c3310` | 37414755368 passes8 HRTB+12 scope cases; actual insertion normal cut/end/recovery/read passes; next failure is address of &*tmp | Candidate reuse with extra ingress/bound-metadata gates. It changes translator AND kernel continuation checks. Its successful unwind uses a partial debt post, not recovered full cells. |
| Ordinary recovery helper, [release fixture](verifast-borrow-recovery-cases.rs), recover_pair and [design audit](BORROW-RECOVERY-DESIGN.md) | 37437514808 and37448682524: unrestricted generic two-cell natural-block normal recovery,3 intended negatives, source/refinement checks pass | Reuse proof technique, not an unverified four-cell summary. Must prove four-cell helper at exact future fixture/profile; repeated sharing and all direct-unwind invocations remain unproved. |
| Source-defined recovery at direct Continue | Translator `vf_mir_translator.ml:2475–2483` emits immediate unwinding ReturnStmt; kernel BlockStmt.return_cont skips trailing ghost helper | **Needs design/implementation and separate trust approval.** Strict cut alone does not execute recovery on unwind; automatic recovery is ruled out by nonghost_callers_only APIs. Preserve Cleanup/Abort/Terminate and all normal successors. |
| Raw uninitialized destination copy | Pinned `bin/rust/std/lib.rsspec:545–548` copy summary requires `src[..count] |-> vs` AND `dst[..count] |-> _`; prelude_core points_to/array require some(T), not none | **Missing contract capability for actual MaybeUninit scratch.** Existing generic Drop gate37419989766 uses initialized dst. No permission to assume initialized scratch. Must separately justify optional-initialization/byte-copy spec with padding/validity/non-overlap/provenance and independent negative gate; not implemented here. |
| Exact `hint::select_unpredictable` pointer result/permissions | Actual hint.rs:836 body uses MaybeUninit, intrinsic selection and DropOnPanic; pinned translator/spec search finds no named select support | **Unverified callee/intrinsic dependency.** Need actual pointer-instantiated helper at matching source or explicitly reviewed faithful intrinsic model before summary use. An assumed `if` rewrite is forbidden. This selection dependency starts after c2 and need not enter the first one-call recovery gate. |
| ONE ownership plus scratch representation relation | Actual Drop gate37419989766 checks exact generic copy effect and one ownership list; source still initialized. Caller gate37435525052 checks cleanup only for its local fixtures | Reuse separation of physical bytes/owners. No general clone/share/transport bridge for source and scratch. First full sort4 post retains source owners plus nondropped scratch Shadow; later scratch access/caller transport requires another proof, especially non-Freeze/ZST. |
| MD/address-taken/local Drop/declaration-order/projection-name patches | Historical insertion/cleanup results and MD half-storage/RawPtr failures preserved in prepared-phase report | Unnecessary for sort4's own body; exclude from first callback profile. The hint helper may create further requirements; do not import insertion patch chain speculatively. |

Additional static input audit during this phase used a clean existing checkout
at the exact pinned VeriFast source (no apply/build): `std/lib.rsspec` SHA256
`24c86cd57364d1962e13232bde46117f16b71dc4b8ba6264a4577903cfc53ecb`,
prelude SHA256 `d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5`.
The scratch-init gap is established by reading the actual typed copy precondition
and points_to_=option definition, not an executed sort4 failure. The source
never needs initialized dst for Rust runtime copy; it is the current verifier
summary that lacks this case.

### Why the historical green prefixes are insufficient

Inspection of run37414755368's saved source/log confirms its on_unwind_ens
contains half lifetime token, borrow_end tokens, initialization fractions and
close tokens, not restored full source cells. Its first unwind leak check passes
that deliberately partial post. Normal helper calls occur after the cut and
then the real tail read passes. Direct panic never executes those trailing
statements. Therefore reusing only three historical patches and expecting full
unwind restoration would repeat an already understood gap.

The strict-cut profile's recorded output files are parser SHA256
`734495d9aead953ff799cb3d03fd55215209b493206616ecfb962c756c974073`,
translator `15a9db2fbafa0f04e74e75e5bee0dd7d941a7428906e42432e9d9687843bbcce`,
kernel `eb9052b5f58c6f62d0a57ecb723d04c1725438607cebac6d1d07b37b6298a287`.
These identify historical evidence, not a new allowed profile.

### First bounded experiment — NOT AUTHORIZED

Scope: **one actual-shape c1 callback**, four generic initialized source cells,
separate four-slot uninitialized scratch as a frame, unrestricted T/F. Prove
an isolated mechanism fixture whose runtime statement and direct Continue shape
match `let c1 = is_less(&*v_base.add(1), &*v_base)`; it ends after recovery.
Compare annotated/stripped versions of that fixture exactly. This is explicitly
a fixture, not extraction/proof of the complete sort4 function. Audit full
sort4 MIR separately to map c1 and its direct Continue, without rewriting its
body. First establish a source-written continuation's correctness before any
all-five integration or copying/model extension.

Falsifiable hypothesis: the narrowly annotated normal and direct-Continue paths
can both leave the comparison epoch and call the SAME proved recovery helper,
returning all four current owned source cells and unchanged scratch initialization,
while preserving legal effects and the original unwind outcome. A passed debt
post or fresh owned-cell assumption falsifies acceptance, not fulfills it.

Prospective fixed profile for owner review: VeriFast26.09 exact source above,
Rust nightly-2026-02-05; tuple patch→HRTB patch→strict-cut patch at the three
listed hashes→one separately reviewed exceptional-routing patch. That last patch
**does not exist yet and has no hash**. Freeze its allowed files/CFG rules before
implementation, and record its actual diff/hash before any dispatch. Keep all
prelude/memory/alias/refinement files unchanged in this first gate; kernel diff
is limited to the explicitly reviewed existing strict-cut behavior. No raw-copy
summary change, MD, Drop specializer or new solver/tool is part of this gate.
Default90min hosted budget, serial isolated cases, no automatic broader phase.

Full mechanism posts:
normal returns c1's actual Boolean plus `SrcOwn(s,V_after) * RawDst(d,I_after) *
Cb(F,Q_after) * Frame(H_after)`; unwind returns the same resource predicate and
the original panic outcome, without a Boolean result. Scratch enters with none^4 initialization. I_after includes permitted callback
effects and their resource disposition in Q_after/H_after; it equals none^4
only if scratch is inaccessible to F. s2/s3 and scratch remain
untouched by the fixture except legal callback effects; V_after/F/frame use
current permitted effects, not pre-call rollback. No live local lifetime or
borrow debt; no ownership duplication/leak; no Copy/Freeze/purity restriction.
These fixture posts test the missing prerequisite. Full sort4 target posts
remain exactly those in [the contract](SORT4-CONTRACT.md), including all five
panic sites and initialized nondropped destination on normal return.

| Isolated regression | Required observation / intended rejection |
| --- | --- |
| Positive normal callback, arbitrary Boolean/current valid state | Actual FnMut body/spec call and helper check succeed; full four-cell/scratch/frame post and leak check, including both bool results |
| Positive direct panic at c1, effects retained | Actual Continue edge reaches checked helper once then original unwinding return; full resources/post/leak check, no runtime cleanup fabricated |
| Unchanged generic normal recovery controls | Existing2 positives and3 intended negatives remain at their expected obligations; no optional helper pollution |
| Tuple generic fields/non-Copy; tuple1/3/4/unrelated struct | Tuple2 field-own closes/opens from genuine resources; missing one field owner fails tuple/call precondition; unrelated behavior unchanged |
| HRTB8-case guard suite | Exact existing counts/locations including absent/different Output, mismatched F/T/regions, unannotated call and other body; no equality leakage. Add explicit ambiguous duplicate predicate rejection before registration. |
| Strict-scope12-case suite + previously untested incoming CFG edge | Live scoped chunk/unclosed fraction/post-cut use/double-end/malformed marker fail at scope/token/type gate; external ingress to epoch must reject structurally |
| Exceptional marker negative matrix | Missing/duplicate/wrong-call/misplaced marker, nested unsupported epoch, non-Continue edge or incoming jump rejected by structural frontend gate; no unrelated parse failure accepted |
| Missing token/debt or forged source owner | Actual checked helper precondition fails; neither callback normal nor panic can mint the missing resource |
| False recovered-value post / two independently droppable ownership lists | Actual fixture postcondition/resource failure; no weakening to comparison debt |
| Cleanup/Abort/Terminate/no-annotation controls | Original MIR/AST successors remain identical; no recovery routing on those edges and no erased drop/abort/termination |

Acceptance: all positives and intended negatives, exact exports/decoded CFG and
annotated→stripped byte/refinement checks, helper body verification at same
source/profile, all normal/unwind/leak/dead-code checks. The transformed AST must
show only added proof statements, identical runtime call/result/successor/panic
behavior, no incoming bypass and helper exactly once on each selected edge.
Admissibility review must explicitly accept source-written exceptional proof
continuations and strict kernel exit behavior; green fixtures alone cannot
establish soundness or challenge acceptance.

NO-GO if full unwind recovery is unexpressible, markers match ambiguous edges,
a stateful/non-Freeze comparator forces invented readonly assumptions, fractions
or provenance are assumed, refinement/source correspondence fails, or a negative
fails at setup/unrelated helper. Stop and reassess; no automatic additional patch.
GO establishes only the one-callback capability. Before a later full-body gate,
review sharing all four cells across five calls (including repeated same-cell
accesses), panic c1..c5, select helper, raw scratch copy summary and ZST/padding/
ownership resources. These dependencies cannot be waived by the first gate.

## Historical proposed owner decision — not current authorization

Decide whether to authorize this narrow exceptional-continuation design/trust
review and one-callback full-normal/full-direct-unwind implementation experiment,
with the explicit historical tuple/HRTB/strict-cut dependencies and regression
matrix. Whole generic sort4 remains NO-GO until scratch-copy/selection and
five-call recovery gates are resolved. Accept/clarify the separated-range and
single-owner scratch research contract before treating it as the public target.
No new VeriFast run, patch application/edit, later sorting target or external
publication occurred in this phase; this document ends at the owner decision.
