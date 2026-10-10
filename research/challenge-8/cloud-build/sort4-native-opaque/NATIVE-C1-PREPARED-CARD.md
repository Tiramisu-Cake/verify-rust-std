# Native resources prepared for C1: isolated diagnostic, DRAFT / NOT_RUN

This card precedes implementation of [native-c1-prepared.rs](native-c1-prepared.rs).
The proposed component stops immediately before an actual `FnMut` call. It is
not a callback theorem or an actual caller-to-sort4 edge. No compiler,
verifier, proof runner, extractor, Cloud Build, or patched tool is run here.

Build 081 reached the verifier frontend; its parser rejected
`open <&'cmp T>.own(t, ref)` before entry proof. The revised diagnostic attempts
to open the same reference-own type predicate through `open own::<&'cmp T>(t)(ref)`,
the stock `own::<T>(t)(value)` syntax already used by the checked cell-split
helper. This changes only syntax at the two reference openings in each prepared
case; it neither substitutes `shared_ref_own` without a demonstrated type-predicate
identity nor assumes a reverse lemma. The pinned `f76012fb` Rust-Belt spec has
`close_ref_own` and `shared_ref_own` but no `open_ref_own`. Whether the
reference-own definition is transparent to this open remains a verifier
obligation, so the revised cases remain DRAFT / NOT_RUN.

## Source and contract

Use the safe signature of `small_sort_general_with_scratch` at pinned
`library/core/src/slice/sort/shared/smallsort.rs:220` (SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`).
Keep its automatic native `&mut [T]`, `&mut [MaybeUninit<T>]`, and `&mut F`
contract, with complete normal/unwind posts, return ownership, local-free and
leak checks. The runtime boundary is the internal `size_of::<T>() == 0` early
return followed by `len >= 8`, as in the C1 candidate. Non-ZST is a condition
of this *internal* path, not derived from the real caller's selected sort4
branch; ZST and the caller's real guard/abort behavior remain outside it.

Use the exact source expression of `slice::as_mut_ptr` at
`library/core/src/slice/mod.rs:778`, `self as *mut [T] as *mut T`, with receiver
renamed `v` (SHA-256
`e3a45814fc07497d6e85d182d6b30782711e4b77752fa817988ec6da12e2cb6f`).
This is only source-anchored expression correspondence, not external method
binding or complete actual native source/MIR/AST correspondence. There is no
runtime comparator, no new raw-source precondition, and no scratch-to-T cast.

From the automatic native pre, explicitly expose current thread, source
`[..len]` and its `foreach` T owners, comparator cell/F owner, and the opaque
scratch `MaybeUninit<T>` array/owners. Produce the stock T/F type
interpretations explicitly. Split exactly the first four source cells and
owners, preserving the tail. Run the existing checked lifetime and borrow
preparation for operands 1 then 0: full-borrow close, borrow, share, reference
creation/share initialization, reference-own packaging, tuple-own packaging,
fractional `ref_initialized` access and comparison-debt ingredients. Assert
these inputs at the pre-call boundary while they actually exist. Then undo the
tuple/reference packaging using only transparent stock predicates, close the
debt, end the lifetime binding, call the checked `recover_pair` and
`join_four_owned_cells`, rejoin the untouched tail, and restore full CURRENT
native source/F/thread/MU resources. The positive post is the *automatic*
normal native post. With no fallible runtime operation on this path, generated
unwind post still remains enabled and checked; there is no manufactured C1
unwind event. An inability to undo reference packaging or satisfy a debt token
is an intended localized first proof blocker, not permission to discard it.

Checked helper definitions are copied, with bodies and contracts unchanged,
from `overnight-sort4/capture.py` (`interior_pointer_limits`,
`split_four_owned_cells`), `overnight-callback/callback-cases.rs`
(`comparison_debt`, `recover_pair`), and
`overnight-callback/join-four-owned-cells.rs` (`join_four_owned_cells`). They
must verify before the native body. No additional axiom, assumed inverse,
ownership bridge, positive-size pre, `Copy`, purity, or F restriction is added.

## Frozen environment, expected observations and next decision

Target the frozen C4 profile: HEAD
`f76012fb518703b1d98e243ac4f487f16877cfcb`, translator SHA-256
`1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313`,
kernel SHA-256
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`,
and effective pins in `../sort4-native-c4/FROZEN-C4-SNAPSHOT.json`. Keep
C1–C4 target/capture flags off for this independent component. The third batch
uses the separately pinned capture-only translator with its new opt-in0,
kernel37ed and all other frozen inputs unchanged; this exercises default-off.
No native
alias overlay, compose strict-compat draft, new marker or trusted semantics.

Expected positive: paired source/MIR/refinement succeeds; all four local lemma bodies and the debt predicate verify first; the native body reaches the explicit prepared-resource
assertions, reverses only its own ghost packaging, and closes the full generated
normal/unwind/return/free/leak obligations. A localized negative, if included,
may assert `false` immediately after preparation or delete exactly one owner
ingredient and must fail at that intended location after preparation. An
unsupported `size_of`, cast, lifetime declaration, reference-own opening,
tuple-own opening, or unrelated helper failure is reported at its true first
stage, leaving later checks NOT_RUN. A false post before body reach is not an
intended negative.

Even a positive prepared component leaves the actual comparator's compiler
HRTB/Output binding, direct unwind and CURRENT callback recovery unproved. The
frozen C4 C1 marker admits only `sort4_stable`, and the external
`v.as_mut_ptr()` binding, real checked-add guard/abort, branch selection,
`scratch.as_mut_ptr()` and actual `sort4_stable` call edge are absent. No
whole-sort4 summary or proof-status upgrade follows from this component.
