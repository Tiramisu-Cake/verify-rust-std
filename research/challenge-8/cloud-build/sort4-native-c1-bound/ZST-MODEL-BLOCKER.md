# Native C1 ZST blocker — exact frozen model limitation

READY for VeriFast-agent review; diagnosis complete, model repair NOT_AUTHORIZED
in this session. No peer profile imported or message/publication sent. Full
native C1 remains INCOMPLETE; connected C4 NOT_RUN. No admissible source-specific
repair preserves all required obligations on the frozen model.

Fresh009 exact physical203 / postlist138 / Goto63 afterLabel3 / originalroot131
is the sole unvisited dead228,2 node. Fresh9ae observes the precise size-bound
triggers during native entry array_inv, before first statement or len/size_of
calls. [Physical-node review](FRESH-009AD1C2-REVIEW.md),
[Entry-bound review](FRESH-9AE319B8-REVIEW.md).

## Pinned static chain

Tool HEAD f76012fb518703b1d98e243ac4f487f16877cfcb; effective kernel37ed2550,
translator381e80eb (full pins in NATIVE-C1-BOUND-TOOL-MANIFEST.json). Frozen
`src/verifast1.ml:6500–6519` creates an axiom for **every declared struct**:
`0 < sizeof(struct_typeid(args)) <= max_uintptr`; args are quantified.
`sizeof_core` represents both generic parameter T and StructType through
`sizeof(typeid)`; generic sizedness alone supplies no positive-size condition.

Stock `bin/rust/std/lib.rsspec:429` declares `struct MaybeUninit<T>`.
At523–525 in the effective spec (478–480 in upstream pinned base), automatic
`size_of_MaybeUninit` equates its size to `size_of<T>`.
The frozen translator's `translate_adt_ty` StructKind/UnionKind mapping at791–817
also represents actual Rust union MaybeUninit as StructTypeExpr; actual std
`library/core/src/mem/maybe_uninit.rs:355–358` is a union, admitting ZST layouts.
This combines to positive T size when the MU size term is introduced.

Native scratch contract is `array<MaybeUninit<T>>(strip_metadata(scratch),
ptr_len(scratch), values)` with foreach owners. In raw3521 target entry, the
source141 scratch array invokes stock array_inv before source145 size guard;
array_inv post includes `count * size_of<MaybeUninit<T>> <= isize::MAX`.
Stock size_of contract itself only returns size_of<T>; it has no nonzero req.
Source FreezeMarker, FnMut lifetime/type binding and CFG correction impose none.

Old3521 verbose2 and native009/9ae verbose4 do not print named axiom events.
Fresh9ae callback-free verbosity6 logs size_of_MaybeUninit at2414 then
MaybeUninit_size_limits at2415, while producing native scratch array_inv post
before firstbody2558 and len2568/size_of2600. First-body positive-size query
passes withMU and fails withoutMU. This directly identifies entry-triggered
model positivity, not a source-specific binding or reachability accounting bug.
The native target has the same model/native array_inv term; its zero route is
retained in source/MIR/AST, correctly unvisited under these existing constraints.

## Required preservation and scope

Fresh009 identifies physical203 as postlist138 / ordinal256 Goto63 afterLabel3,
mapped to originalroot131; noEXEC203. Equalprinted202/204 execute. Never remove ZST return, add assume(size>0), merge its
location with a visited node, or suppress dead-code checking to obtain green.
Native source/F/thread/type resources must remain derived from safe entry;
scratch MU opaque. No MU/reference inverse or optional-T adapter needed.

Any repair of the unconditional struct lower bound, union/layout representation,
MaybeUninit model, triggers or kernel is a general semantics/model change.
Current owner assignment allows diagnosis only there. A maintainer proposal
needs its own rationale/admission/regression gate including generic ZST, unit,
MU<()> and ordinary nonZST/normal/unwind controls, before this target is rerun.
No connected C4 extension until full native C1 exit0 with retained paths/checks.

Effective std spec independently reconstructed by Git-object read plus applying
only the saved `refreshed-applied.patch` bin/rust/std/lib.rsspec hunk, without
proof/extraction execution: SHA256d33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf
exactly matches frozen snapshot. verifast1.ml Git object SHA256
b1b0ae618bbce1a0bce9714ce10a47dbeb855e919b980b7ce6a70108ff9b91d7.
This avoids relying on the separately evolving `/root/verifast` worktree bytes.

Exact saved normal MIR: bb1 calls size_of<T> into_8→bb2; bb2 assigns
_7=(_8==0), then bool SwitchInt values=[0], targets=[4,3]. Thus false/nonzero
routesbb4; true/zero routesbb3. Pre-AST root79 has If(_7, Goto3, Goto4);
post-AST retains it and the Label3→Goto63 tail. There is no successor inversion
or dropped ZST block in this binding; default bool “otherwise” means true.
The root131 candidate refers to original pre-AST, not a post-rewrite list index.

Fresh009ad1c2/f8115f33 observes unused native MU[] suffices fordeadzero; noMU
genericguardVF0. Both pairedfullMIR/refinement pass and noASTbranch lost. Native
positive verifierexit1 despite complete reached normal/directunwind/len<8 posts;
C1INCOMPLETE, connectedC4NOT_RUN. See FRESH-009AD1C2-REVIEW.md. General axiom
repair is outside this assignment; diagnostic infrastructure fixes do not repair
this model. No workaround weakening the entry/posts/dead-code gate is proposed.

## Minimal maintainer reproducer

On the exact frozen tool (not the bound source-specific overlay), the paired
callback-free body (formatted excerpt; exact file/hash is in fresh evidence) is:

```rust
use std::mem::size_of;
fn small_sort_general_with_scratch<T>(v: &mut [T]) {
    let len = v.len();
    if size_of::<T>() == 0 { return; }
    if len >= 8 {
        //@ assert len >= 8;
    }
}
```

Change only the signature to add unused
`scratch: &mut [std::mem::MaybeUninit<T>]`. No body accesses scratch, no callback,
no explicit contract/assume, no pointer rewrite or binding admission opt-in.
Default safe-reference native entry and full automatic normal/unwind posts
apply. In009, both paired export/decode/refinement pass: original body VF0;
with MU parameter VF1/deadcode12,2. Saved evidence holds full bodies, MIR, AST
and verifier commands. Completed targeted follow-up9ae319b8 /b81f1c3c adds a ghost
positive-size assertion as the first statement (before len), keeping the guard.
Only diagnostic verbosity changes to6; no general code/axiom/model edits.

The maintainer question is: how should the existing generic struct/union size
bound and MaybeUninit size equality admit MU<ZST> while preserving permissions,
array footprint limits and nonZST behavior? Any proposed change requires its
own reviewed semantic rationale, explicit scope/pins and regression gate before
implementation. Relevant acceptance examples: generic same-guard bodies with
and without MU, zero-sized concrete layouts including unit and MU<()>, array
zero-size/empty behavior, ordinary nonzero layouts, native resources/full posts,
normal/direct-unwind/len early returns, strict cuts, address false-post controls,
all existing dead-code/refinement/leak/validity/uninitialized checks. These are
review requirements, not an authorized general layout experiment matrix here.
The fix must permit the genuine sizezero branch, not manufacture EXEC records
or make a duplicate printed position hide it. No source-specific binding change
can undo the instantiated contradiction without changing the frozen model or
weakening/removing required source/resource/check obligations.

Native source/header and tool pin cards:
NATIVE-C1-BOUND-TOOL-MANIFEST.json, NATIVE-DEAD-CODE-IDENTITY-DIAGNOSTIC-MANIFEST.json,
../sort4-native-c4/FROZEN-C4-SNAPSHOT.json. User excludes external pointer caller,
guards/overflow, selector/C5/copy, MU inverse and optional-T destination adapter.
No message or publication sent to a maintainer; this committed handoff is ready
for an independently authorized VeriFast-agent task.

Fresh9ae terminal diagnostic SUCCESS/354sec, archivef23156ad5744bace48a0dd1c36b4eae7a2e05c672787331539644298fdc70466 verified. WithMU firstentryquery succeeds
thenVF1dead13,2; withoutMU firstquery fails5,41–42. No source-specific target fix
was applied: only diagnostic instrumentation, dependency/phase setup repairs
and saved-evidence reading. Model repair must be reviewed separately.
