# Cloud-only compiler binding query: design before implementation

Phase `SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11`. Policy revision
`c7ca8c467aecf10a4b53039372ee97714f854ee3` read. Pinned exporter source:
VeriFast `f76012fb518703b1d98e243ac4f487f16877cfcb`,
`src/rust_frontend/vf_mir_exporter/src/lib.rs`; pinned compiler:
nightly 1.100.0 `f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f`.
This candidate is uncompiled and unexecuted until the authorized Cloud lane.

## Actual question and domain

The actual stable quicksort base case calls both
`T::small_sort_threshold()` and `T::small_sort(v, scratch, is_less)`.
`quicksort.rs` has an unconstrained `T` and a real
`F: FnMut(&T, &T) -> bool` clause. `smallsort.rs` has the original blanket
default and `T: FreezeMarker` specialized implementations of both methods.
The prior translator's source/clauses rule can prove local diagnostic bodies,
but its inferred selected name is not a compiler-selected implementation ID.

The new fixture copies those trait/impl method definitions and both threshold
constants exactly. Three callers execute the same guard and both trait calls:
generic `T: FreezeMarker`, concrete `Cell<u8>` fallback, and unconstrained
generic `T`. Each retains a real mutable `FnMut` callback and the same three
operands. The non-base continuation and transitive sorting helper bodies are
explicit diagnostic cuts; they cannot prove whole quicksort or sorting.
The source certificate records SHA-256 of actual quicksort, SmallSort and
FreezeMarker files, exact copied blocks, the allowed cuts and fixture SHA.

## Query and trust boundary

The exporter probe runs only when all three Cloud/phase/evidence environment
gates equal the new phase ID. At `encode_fn_call_data`, it uses the original
`FnDef` DefId and generic arguments from the actual call operand and the
caller's `body.typing_env(tcx)`. It calls pinned
`ty::Instance::try_resolve` without inventing or strengthening a ParamEnv.
Records contain caller DefPath/DefId and source span, `TypingEnv` and caller
clauses, original callee DefPath/DefId/generic args, resolved instance kind,
resolved generic args, resolved method/impl DefId and source span where
available, original operand/arguments and call span. Resolution `None` or
error is recorded distinctly. A machine parser requires exactly two records
for each of the three callers and preserves the raw exporter log and hashes.

This is read-only evidence. It changes no Cap'n Proto/MIR serialization,
translator, specialization model, runtime std, verifier or proof contracts.
Compiler API or call-site ambiguity fails closed. An `Item` resolved to a
trait/default method, a `None`, or an error cannot silently become selected
binding. The runner reports `observed_selected`, `observed_fallback`, or
`unresolved` separately from verification status; no Boolean success is proof
of a binding. Generic quicksort's unconstrained `T` cannot borrow the
Freeze-qualified result. Source/refinement and normal/unwind proof obligations
remain independent and open.

## Admission and expected outcomes

Before compiler execution, the runner pins the source/proof manifest and
fixture bytes; the isolated production copy must match its original exporter
source hash. The patch touches only that exporter file. Cloud builds it with
the existing `make -C src/rust_frontend build-vf-rust-mir-exporter` target and
checks the patched source and built binary identities. The query runs the
exporter on a fresh fixture under the pinned compiler sysroot, capturing stderr
and MIR output. Normal and readonly invocations, if both used, must agree.

If both selected calls resolve to source IDs in the original specialized impl,
the fallback pair to the blanket impl, and the unconstrained pair is reported
without unjustified specialization, record narrow compiler binding evidence.
Any missing pair, duplicate, mismatched callee, unknown `InstanceKind`,
unexpected impl/source span, or API/build failure is `INCONCLUSIVE`/setup,
with no proof credit. A resolved selected diagnostic is still not transfer to
unrestricted quicksort or acceptance of the experimental translator rule.
