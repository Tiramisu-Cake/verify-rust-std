# Native safe entry → first C1 callback: bounded candidate, NOT_RUN

This is a reviewable **internal diagnostic**, not a theorem about the actual
`small_sort_general_with_scratch` caller or the complete `sort4_stable`. The
source template is [native-c1-candidate.rs](native-c1-candidate.rs). Its isolated
case unit received fresh paired capture/refinement in d77612a5/86e38e3a after
ghost syntax repair, but refuses at strict entry172:1–30 before callback. The
case sourceSHA7ebcf7cd and ghost-stripSHA7c35a7e0 pin that experiment; the
template itself is not a callable proved summary. See FRESH-D776-REVIEW.md. WORK-POLICY revision
read: `6726a08d30b37d6d0f4ae65c3d8c2861615d249a` (the adopted policy from
`c7ca8c467aecf10a4b53039372ee97714f854ee3`).

## Source anchors and exact boundary

This fixture copies selected source expressions; it does not establish full
actual native source/MIR/AST correspondence. The native signature and
`let len = v.len()` correspond to
`library/core/src/slice/sort/shared/smallsort.rs:220–225` (SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`).
The first comparison is the exact runtime expression at line 620:
`let c1 = is_less(&*v_base.add(1), &*v_base);`. The candidate's only executable
operation under `len >= 8` is this expression. Its pointer expression is the
exact body of `slice::as_mut_ptr`, `self as *mut [T] as *mut T`, with receiver
renamed `v` (`library/core/src/slice/mod.rs:778`, SHA-256
`e3a45814fc07497d6e85d182d6b30782711e4b77752fa817988ec6da12e2cb6f`).
This checks the implementation expression, **not** the external `v.as_mut_ptr()`
method binding or its provenance/lifetime contract.

The internal `if size_of::<T>() == 0 { return; }` is a deliberate runtime
boundary. It does not follow from the actual `len >= 8` sort4 branch: lengths
8–15 permit ZST. Its false branch explicitly supplies `size_of::<T>() > 0`
for the C1 pointer geometry. The candidate keeps generic
`T: FreezeMarker, F: FnMut(&T, &T) -> bool`, every legal native slice length,
and `&mut [MaybeUninit<T>]` scratch; no `Copy`, purity, or scratch conversion is
assumed. Its C1 claim is restricted to non-ZST T and `len >= 8`. The real caller
still needs proof of its own ZST route and selection guards.

The actual caller's `len < 2` return, checked `scratch.len() < len + 16`
arithmetic/abort, `v.as_mut_ptr()`, `scratch.as_mut_ptr()`, inline-const sort8
selection, and first `sort4_stable(...)` call are absent. In particular, the
known checked-add overflow panic route is not silently turned into a bound.
The existing exact-one-body/source-SHA C4 admission gates cannot credit this
native body as a connected caller. No C2–C5, selector, copy, destination writes,
ordering, or full sort4 return are in this diagnostic.

## Resource and callback contract

The function has **no manually supplied `req`/`ens`**: its safe `&mut` signature
must produce the automatic native contract and consume its full generated
normal and unwind posts, return ownership, locals-to-free and leak checks. From
that native pre, the ghost code reads the current thread and full source array
with `foreach` T owners, the F cell and owner, and the full scratch
`MaybeUninit<T>` array with opaque MU owners. It splits the first four T cells
and retains the tail. No numeric pointer equality is used to create rights.
`produce_type_interp::<T/F>()` is stock explicit logical production, with both
chunks disposed of on normal and C1 direct unwind. The candidate must recover
CURRENT first-four T values and owners, rejoin them with the untouched tail,
recover CURRENT F cell/owner, and retain the unchanged MU frame and thread on
both outcomes. Entry snapshots are not demanded after `FnMut`.

The borrow/debt/recovery sequence is copied from the checked first-call
fixtures: `interior_pointer_limits` and `split_four_owned_cells` from
`overnight-sort4/capture.py` SHA-256
`0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060`;
`comparison_debt` and `recover_pair` from
`overnight-callback/callback-cases.rs` SHA-256
`2701eaf2609bea993fa6a464bd7d2467bf1df7d155fbf240229f5db660b9b1a3`;
`join_four_owned_cells` from `overnight-callback/join-four-owned-cells.rs`
SHA-256 `b35dd247226a3dd88ab8f22a50141896b5556d3a96bec1e982077060d0731e66`.
These definitions are included before the native body and retain their checked
contracts. They provide no scratch-to-optional-T adapter and no inferred
`MaybeUninit` inverse or ownership bridge.

## Frozen environment and expected first refusal

Use only the frozen C4 profile: tool HEAD
`f76012fb518703b1d98e243ac4f487f16877cfcb`, translator SHA-256
`1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313`,
kernel SHA-256
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`,
and all remaining effective pins in
`../sort4-native-c4/FROZEN-C4-SNAPSHOT.json` (SHA-256
`004dab0f90e2abf75a422c83302015f593ec9273a78fc72d0e09ef71c1a2432b`).
Do not use the native slice alias overlay, old compose strict-compat draft,
strict-cut draft, selector profile, or an unreviewed tool extension.

The candidate writes the **existing** `__vf_sort4_first_unwind` marker so the
source retains its intended C1 direct-unwind recovery. The frozen C4 translator
and bound gate constrain this marker/Output binding to the exact
`sort4_stable` target, while this body is `small_sort_general_with_scratch`.
Thus the expected first *rule* dependency is source-specific admission of the
native body's comparator unwind/strict lifetime/Output binding. A fresh paired
source/MIR/refinement/pre-AST capture may instead refuse earlier on the new
size guard, slice cast, or ghost shape; report the actual first stage and
location. If it reaches the comparator, generic `FnMut` Output equality must
come from the compiler's exact quantified clause and the existing HRTB opt-in
for the exact target. No bool equality, debt discharge, or native unwind post
may be assumed. A capture with an unbound lifetime or unresolved marker is a
diagnostic artifact and must be refused before proof/summary export, never
classified as a positive verifier run.

If a future, separately reviewed binding makes the target admissible, the
positive acceptance gate is a fresh exact-source Cloud proof of this one body,
with the automatic native normal and direct-unwind posts, unit return, leak and
dead-code checks intact. An intended normal false-post control must fail only
at that post after C1; an intended C1-unwind false assertion must fail only
after the actual comparator's unwind edge. Missing-debt/owner controls count
only at their named recovery obligation. Frontend/setup or unrelated-helper
failures leave these targets NOT_RUN. A positive internal result would establish
only this bounded helper, not the missing external method, actual guard/call
edge, ZST case, or complete sort4.
