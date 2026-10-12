# Independent preimplementation review — bounded I storage/layout prerequisites

Verdict: **conditional GO for the C0–C2 candidate only**. This is a design
decision, not a proof result, profile adoption, or permission to run C3. Reviewed
the proposed `DESIGN.md`, compatibility and future gates, I tool `b6cb276a`,
reference glue `a158398e`, and the pinned rustc
`f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f` source copies. No verifier,
compiler, extractor, or proof runner was executed.

## Why the bounded rule is admissible

The pinned MIR `syntax.rs:365–382` defines `StorageLive` as fresh uninitialized
storage and `StorageDead` as deallocation. `step.rs:103–110` dispatches these
events; `stack.rs:500–613` tracks `Dead`/`Live` and deallocates indirect
storage; `memory.rs:251–295` reserves a fresh allocation ID for an allocated
object. Two simultaneously live, positive-size allocations, including a new
callee local and a still-live legal incoming u64 cell, cannot occupy the same
numeric bytes. The rule can therefore supply bounded span separation for the
exact admitted translated MIR events. It does **not** supply memory permission,
initialized contents, pointer provenance, or any fact about an unrelated raw
pointer. Existing I `points_to`, validity, and `free_locals` checks remain
authoritative. Refusing a second `StorageLive` while a local is live is a
conservative restriction: rustc specifies free-then-fresh for that event.

The model must only emit numeric separation once each span is known positive,
currently allocated, and representable without address-plus-size wrap in the
pointer/`usize` model used by the target assertion. Check or derive those range
facts from the existing legality and bounds rules; do not silently treat an
unbounded mathematical sum as an equivalent wrapping `usize` expression. A
receipt must name an allocation *incarnation*, not a local name or a previously
retired symbolic address. Retire it at `StorageDead`, `free_locals`, and each
relevant normal/loop cleanup edge. A fresh incarnation may reuse a dead address.

## Resource identity across I strict scopes

I `src/verifast.ml:2535–2589,2824–2844` freezes and rebases types and rebuilds
heap `Chunk` objects on strict exit; the reference glue's physical `entry ==
chunk` test cannot survive this unchanged. The proposed explicit old-to-new
mapping is acceptable only while the **old object is actually present in the
current path heap** immediately before that checked freeze, and the replacement
preserves predicate, coefficient, terms, and size, changing type arguments only
by I's existing freeze/rebase. Record the mapping at that operation, with no
fallback to structural equality, matching address/type, or a global origin
table. Keep it continuation-local and restore it on normal return, branch,
label, and backtracking paths. A consumed, split, merged, opened, closed, or
reproduced chunk loses the incoming identity unless an independently justified
rule is reviewed. `src/assertions.ml:747–785,1120–1150` constructs new chunks
for fractional splitting, so treating equal-looking residual pieces as the
original would be unsound. Negative controls must reach the intended receipt
gate after strict survival, consume/reproduce, split/merge, and nested paths.

## Compiler layout and source admission

The pinned `rustc_span::SourceFileHash::new_in_memory(Sha256, full_bytes)` path
exists in `span.rs:1767–1785`. The layout rule is acceptable for only the exact
nongeneric `CopyOnDrop { src: *const u64, dst: *mut u64, len: usize }` fixture on
the pinned compiler and x86_64 Linux target, using PostAnalysis `layout_of` and
the **actual** field offsets. Validate size, alignment, every field size/offset,
nominal identity, mutability, exact source bytes, compiler identity, and target
at the exporter/decoder/translator/model boundary. Commit an explicit allowlist
of full source hash(es) for the original/verified pair and compare them against
independent input receipts; a hash merely declared inside metadata is not source
admission. The saved positive pair currently hashes to
`1f602539155e245b09b8af960559dd99d338bf352c024fa15faed1fed0c3963a`
(original) and
`ff2351600be322e79057af6bee3c001c79ee7eed56086208b5c7cc6691ec5c6f`
(verified). If the candidate's pair changes, review and pin the new bytes before
execution. DefPathHash corroborates the identity but is not a content pin.
Reject duplicate, partial, foreign, and annotation-forged attributes. Preserve
I's empty Rust struct/ZST semantics and positive-size C rules.

## C2 dependency and decision boundary

The saved `natural_onecell` source retains an actual `impl Drop for CopyOnDrop`
with a strong method precondition, canonical `safety_proof`, and resource
restoration. If that intact source needs the existing checked
selected-effect/`gen_drop_contract` branch to build and verify, import the
*minimal exact qualified branch* from `a158398e` as an explicit C2 dependency;
verify its method body and canonical bridge in the same C2 lane. Do not replace
the method with an assumption, suppress its verification, remove the Drop impl,
or weaken the caller posts to make a geometry prefix green. This addition does
not admit generated glue, observation/Instance metadata, selected-method
redirection, or refiner changes; those remain C3. Any required new semantic
rule beyond this existing exact branch returns for architectural review.

C0 settings closure and C1 changed-component build precede the C2 positive and
intended negatives. C2 can establish a compiler/source-qualified constructor
and resource prefix only. It does not establish the full Drop theorem, actual
generic `CopyOnDrop<T>` layout for arbitrary `T`, actual `insert_tail` panic
cleanup, or the C3 generated glue call/refinement. C4–C7 remain affected
regression obligations on the eventual combined pin.
