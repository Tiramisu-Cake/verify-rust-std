# Source-linked C1+C2 bound prefix — proposed experimental profile, NOT_RUN

Session 2026-10-10 00:34:15–02:34:15 UTC (03:04:15 finish/checkpoint only).
WORK-POLICY revision `c7ca8c467aecf10a4b53039372ee97714f854ee3`,
adopted in this branch at `6726a08d30b37d6d0f4ae65c3d8c2861615d249a`.
This card precedes any C2 semantic implementation. It does not accept a tool
profile, certify a callback, or upgrade the unbound C2 discovery scaffold.

Independent GPT-6 Sol targeted design review at approximately 00:55 UTC:
**conditional GO** for this one exact profile. It requires consuming the sole
source-196 parsed declaration into one sibling after C1 normal recovery,
keeping C1 unwind outside C2, relocating `_63`–`_72` exactly once with their
allocation/init/address/live/dead effects, and leaving bool `c2` outside.
Both Output=bool substitutions must be checked against the exact compiler
HRTB clause. It also requires complete input/runtime inventory, full raw
CURRENT posts and causal controls; default-off C1 and mandatory unbound
scaffold refusal must remain unchanged. This approves the bounded design for
implementation, not the eventual patch or a proof verdict.

## Actual obligation and boundary

The actual body is `library/core/src/slice/sort/shared/smallsort.rs`'s
`sort4_stable`, called from `small_sort_general_with_scratch` at source line
254. The bounded theorem must execute its first two exact comparisons:
`is_less(&*v_base.add(1), &*v_base)` then
`is_less(&*v_base.add(3), &*v_base.add(2))`. Preserve both returned `bool`s and
all normal/direct-Continue unwind outcomes. The first callback's direct
unwind must return before beginning C2. The second's direct unwind must occur
after full C1 normal recovery. After C2 normal close, strict scope exit,
pair recovery and four-cell rejoin, project only the remaining normal suffix
before c3. This bounded prefix is not a whole-sort4 callable summary.

Use the existing raw non-ZST contract unchanged: source four `T` cells and
owners, current `F` cell/`F.own`, thread and T/F type resources, positive T
size and optional destination allocation. Keep original complete normal and
unwind CURRENT source/F/optional-destination posts, return and leak checks.
Do not assert entry-value preservation of source or destination: these posts
are existential resource conservation. No Copy/Freeze/purity/no-panic
restriction, source signature/runtime edit, ownership bridge or changed
memory/kernel/refinement semantics. The original full target remains open,
including ZST and actual caller guard/interface composition.

## Evidence pins and falsifiable hypothesis

A5DE Build `a5de0e51-3663-4c7d-9844-ff6b122436ee` captured annotated
source SHA256 `ecd83f8c0840a07f138bc8afa2a36c661f296d748693afa2a0a61667cb3372e4`,
ghost-stripped runtime `3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72`,
complete normal MIR `e270457999f9371bc94664917ebd96699eecec0b91148899aa48c511f398c82b`
(82 blocks/164 locals), readonly MIR
`3598b01b91af60d4ad5f96cabc8225aad30bb9a2bd73eb7fc7add15473fb1a29`
(28/110), and unbound diagnostic AST
`4fa7d49e420dc80681328bacdf08bb1d674dc2413001b99501da1c09b11dbb0a`.
The source-linked scaffold always refused before proof. Its source-196
`'cmp2` declaration is inside a closed placeholder block, so it does not bind
the source-223 call. The pinned original AST is a diagnostic input, not a
successful proof artifact.

Hypothesis: a new exact opt-in translator profile can consume the *one parsed*
source-196 `TypeWithTypeidDecl('cmp2, typeid_of_lft(cmp2_k))` into a real
second local scope, sibling to C1's `'cmp` scope, while retaining all
pre-boundary MIR local allocation, callback and cleanup effects. C1's current owners, F and
thread enter C2 only after its normal join; C2 borrows cells `(3,2)` and
restores the same complete CURRENT resources on both C2 outcomes.

## Proposed narrow AST transformation for independent review

1. A separate `SORT4_ACTUAL_C2_BOUND_PREFIX_TEST=1` gate checks exact source,
   full typed MIR modes, pre-transform AST and local/control inventory before
   transformation. Default-off C1 behavior and
   `SORT4_ACTUAL_C2_DISCOVERY_TEST=1` mandatory unbound refusal stay intact.
   Admit exactly one `sort4_stable` and reject mixed opt-ins. The existing
   source parser still parses source-196 declaration; this profile consumes it
   once, without making the placeholder itself a proof path.
2. Rebuild C1's existing strict scope and first direct-unwind epilogue from
   the A5DE full AST. C1's normal source-191 debt close, source-192 strict exit,
   source-193 pair recovery and source-194 four-cell join precede the new C2
   scope. Preserve C1 receiver/tuple/reference locals `_27`–`_34`, their
   source-190 initialization sequence, c1 assignment and both outcome arms.
3. Begin a **sibling** C2 `BlockStmt` at the source-196 declaration, not a
   nested child of an unended C1 block. Include exact source-197–216 ghost
   preparation, source-217–222 direct-unwind marker, all source-223
   receiver/reference/tuple pointer creation and call-switch statements,
   source-224 normal debt close. Move the *original* C2 receiver/tuple/ref/raw
   pointer declarations `_63`–`_72` into this scope exactly once, in original
   order, before their initializer statements; keep `c2` bool outside because
   its result is used by the remaining original suffix. Preserve source-223
   first tuple operand `v_base+3`, second `v_base+2`, receiver `is_less` and
   `FnMut::call_mut<F, (&'cmp2 T,&'cmp2 T), 'cmp2>` with returning c2 assignment
   and unwinding edge. The compiler HRTB `F/T Output=bool` premise must be
   registered for this exact second substitution and checked independently
   of the already accepted C1 registration. No generic Output assumption.
4. C2 unwind arm closes source-219 debt, then reaches its own strict scope
   exit, source-220 recover `(3,2)`, source-221 four-cell join and **original**
   direct unwind return. C2 normal path closes source-224 debt, exits strict
   scope once at source-225, recovers `(3,2)` at 226 and rejoins at 227.
   C1 unwind never enters C2 scope/cleanup. Preserve all original c1/c2 bool
   assignments, declarations, allocation and drop effects. Retain exact
   return/leak and full normal/unwind post checks.
5. Only after C2 normal join, replace the following *normal* suffix by the
   bounded return to the unchanged original post. Walk every retained
   `BlockStmt`/`PureStmt`/`IfStmt`/`SwitchStmt` label and goto recursively,
   refusing unknown control containers, unresolved targets and any ingress
   into the removed suffix. Do not remove failing nodes or disable strict
   dead-code checks. The full source/MIR/AST certificate still counts all
   runtime 5 FnMut, 8 select and 4 copy occurrences; the bounded proof path
   executes two FnMut only.

The exact implementation must pin source span, local declaration order/count,
StorageLive/Dead and initialization, address-of operations, cleanup/Drop facts,
both marker shapes, two switch shapes and both unwind epilogues. A5DE normal
MIR has C1 call BB23 and C2 call BB53 with `unwindAction=continue`; C2
`_63`–`_68` live at BB51, `_69`–`_72` at BB52, actual call BB53, receiver,
tuple and refs dead at BB54. Readonly MIR has different block IDs, so its
inventory requires its own check. The MIR schema has no `addressTaken` field;
the exact AST address-of construction and local declaration `taken` refs are
the available checks. No claim of a missing boolean field.

### Declaration placement / path footprint audit

The original translator AST eagerly places all 161 translated local
declarations at function entry, including future `_98`–`_103`, `_105`–`_110`
and `_134`–`_139` receiver/tuple/ref locals. The exact full pre-AST retains
all 161. The bounded AST retains 143: 125 outer, 8 in C1 and 10 in C2. It
projects away the 18 declarations associated solely with later callback
calls, along with that later suffix. They execute on none of the bounded
normal or direct-unwind paths. This is an actual AST allocation-placement
change; the full pre-AST count alone does not justify it. In `src/verifast.ml`,
an uninitialized `DeclStmt` with `address_taken=false` can still call
`produce_object`, particularly for a struct/tuple. That can create an
abstract local resource, so keeping those declarations on the artificial
bounded normal return would add an allocation/free footprint not present at
the source-227 boundary.

The source/MIR reason for omitting those future declarations from the bounded
AST is that each corresponding normal MIR `StorageLive` occurs only at its
later source call (lines 241, 242 or 249), after the C2 boundary. A mechanical
audit of the saved complete normal MIR checks that each of the 18 locals'
first basic-block occurrence is its own `StorageLive`, after the second
FnMut call. The readonly MIR uses different local numbering; a separate audit
checks its later `_98`–`_109` first occurrences are likewise `StorageLive`
after the second FnMut call (at readonly lines 254–256), with `_110` and
`_134`–`_139` absent. The saved-input audit also checks the complete normal
82-block and readonly 28-block edge graphs: all blocks are noncleanup, each
nonfinal block has exactly its successor as normal target and
`unwindAction=continue`; the second calls are BB53 and BB4, while the first
later local lives are BB62 and BB21. Thus neither direct callback unwind can
enter a later block, and every normal path to a later local crosses the
second callback's normal successor. The C2 callback
locals `_63`–`_72` have their own `StorageLive` only at the source-223 call
preparation, and every one is retained inside C2 before that preparation;
bool `c2` is kept outside. This bounds the proof before the later callback
storage lifetimes begin. Independent review must still assess whether removing
those eager translated `DeclStmt` allocation/free effects is admissible for
this prefix. It must independently review the recorded edge audit and inspect
actual post-AST heap/free behavior.
Source/MIR timing and declaration counts alone do not prove equivalence. If
that audit fails, the bound projection is not admitted even if VF0 appears.
The current translator explicitly lowers `StorageLive` and `StorageDead` to
empty statement lists (it records them only in the optional Rocq trace;
`vf_mir_translator.ml` near its `StorageLive`/`StorageDead` cases). Thus the
MIR storage events are source correspondence constraints; they are **not**
claims that the emitted VeriFast AST preserves literal storage operations.
The concrete AST declaration production/free semantics and per-path heap
changes must be reviewed separately.

## Cloud gates and decisions

Fresh Cloud positive: exact full source/MIR/refinement capture, emitted
post-transform AST and full VF0 including same-unit checked recovery/join
helpers, normal/current source/F/optional destination, both direct unwind
posts, return/leak and strict dead-code checks. Negatives must reach intended
obligations: distinct C1/C2 missing-debt controls fail the corresponding
recovery precondition; the normal false-post control fails the actual normal
post; C1/C2 unwind branch-local false assertions check reachability of each
unwind epilogue, while the positive checks both original unwind posts;
omitted join controls fail current source ownership.
Source operand, MIR call/unwind and pre-AST mutants must refuse admission.
Default-off C1 matrix and unbound C2 diagnostic must retain their previous
behavior. Setup/frontend/unrelated helper failures are inconclusive.

PASS permits the next already agreed actual blocker within remaining session
time; a resource failure localizes a C2 pair/F/owner debt for routine repair.
If correct binding requires an unreviewed parser/kernel/model change, a new
ownership axiom, hiding an outcome, or weakened post, stop and return that
decision. No local compile, extraction, proof or Cloud dispatch from this
independent worktree; main owner controls the Cloud lane and account.
