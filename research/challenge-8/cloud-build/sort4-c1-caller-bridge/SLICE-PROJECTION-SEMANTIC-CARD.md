# Exact slice as_mut_ptr value projection candidate

Fresh Build e97528f0-80a2-4e23-9b43-80601e06f3bb, source/infra
15056f9e820633fbe047f6a064eb2374076ce9ae, passes typed MIR/fragment refinement
and executes scratch-success filter + original check without executing abort.
First failure BEFORE callsite: `No such function: std::slice::<impl [T]>::as_mut_ptr`.
Raw logs/stages remain preserved. Source mapping collector also has an audit-only
hash mismatch: certificate hashes caller payload without the saved file's added
newline. Repair compares exact payload and records saved file hash independently;
no original gate or evidence overwritten. Both representations contain retained
abort call and selected check spans. No premise credit from this first build.

Authorized narrow patch: add ONLY exact name `std::slice::<impl [T]>::as_mut_ptr`
to existing `as_ptr` arm in pinned O26 translator. Preserve existing one-receiver,
GenArgType+late-lifetime substitution shape and typed element-pointer CastExpr.
Runtime source method core/slice/mod.rs778 is exactly
`self as *mut [T] as *mut T`. Source path/blob/hash/body becomes lane input evidence.
Pinned upstream f76012fb and ordered O26 patches retained; candidate is applied
ONLY in caller-entry lane after frozen translator check, before source compilation.
Candidate full applied-diff and tool snapshots replace no historical profile.

Rationale: this cast strips metadata while retaining pointer address/provenance.
Existing verifast1 reference-to-sized-pointer cast implements strip_pointer_metadata.
FnCallResult emits result assignment/goto only. No pointee permission, T.own,
lifetime, type_interp, storage, frame or recovery resource is created; all caller
rights must still originate from native FBC arrays/current owner foreach. Pure
method cannot panic; pointer projection does not execute comparator/copy. Existing
normal/unwind/refiner and complete native-return/leak checks remain enabled.
No other as_mut_ptr, including MaybeUninit::<T>::as_mut_ptr, matches new arm.
No global memory/alias/kernel/spec change. Production profile remains UNACCEPTED.

Independent pre-implementation review: GPT-6 Sol resource_review read exact source,
frozen lowering/FnCallResult and metadata cast, confirming value-only conservation.
Concerns/gates: generic T and MU pointer-value positives with native full frame
return/leak; unrelated raw-pointer authority and wrong-pointer-value negatives
must fail AFTER projection at exact assertion. Retain source/refinement/MIR gates
for actual selected prefix and full AST dump via stock optional diagnostic emitter.
No intended-negative credit for setup/frontend/unrelated first failures.

This patch does NOT solve generic MaybeUninit open/close identity or opaque
ownership transfer. type_interp is not native generated heap evidence; stock
produce_type_interp real-function rule is separately classified and currently
unused. Positive-size c1 remains conditional and ZST stays legal selected input.
Unchanged select/c1 results preserved at old exact pins; no profile transfer.

Scope incident during delegated preparation: worker briefly copied modified
run-o26-refresh.sh and new slice-projection-controls.py into foreign clean
/root/verify-rust-std-verifast-infra, branch infra/verifast-mdnew-cfg,
HEAD da19a64ce9212b384c78bc040b4105eeeeeee714. Main stopped this immediately.
Worker removed only its new module and restored tracked runner from exact HEAD
blob; reported final git status clean. No index/ref/build/ledger/coordinator
mutation there. This violated worktree scope temporarily; no lasting foreign diff.
All published candidate paths belong to select-night only.
