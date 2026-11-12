# R7 design — source candidate, NOT_COMPILED / NOT_RUN

Prepared before the B1 Rust edits. Exact accepted base: 4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c,
tree af28e22ec446b254cfa3a28b2882eafa58d5a458. B0 adds only the R6b exact initializer identity
to the shared skip list, retaining BeginArgumentTransfer and the entire current source chain.
B1 is a representation candidate; neither cost reduction nor semantic success is established.

## State mapping and invariants

MEM_INIT_STATE retains its one original KaniMemoryInitializationState marker and exactly
tracked_object_id:usize, tracked_offset:usize, value:bool. All twelve argument_buffer_* fields
move one-to-one to ARGUMENT_BUFFER:ArgumentBuffer, dropping only the argument_buffer_ prefix.
The new mutable named static has the distinct KaniMemoryInitializationArgumentBuffer marker.
It is not an anonymous immutable allocation and is never an immutable seed.
The constructors retain false for the three bool fields and zero for the nine usize fields.
MODEL-MAP records each field and every runtime read/write site.

Begin, store, load and reset change only field ownership/access. Signature/count/written/remaining,
strict index order, usize::MAX, mandatory return zero, demonic argument selection including none,
and matched layout validation remain unchanged. Store reads the live source before Move/reset.
Load uses the saved has_witness/value/relative_offset and the live destination: a selected false
witness remains false through value && layout[relative_offset]. No source pointer is saved or reread.
No witness and false witness remain distinct. All old assertions and continuation/abort edges remain.
Reset still chooses two nondet usize values, sets main value=false, then clears only buffer active,
selected_argument and has_witness. Inactive payload/sequence fields are not reset wholesale.

## DFCC identities and write footprint

Keep kani/core fallback and resolve two exact markers through StaticDef -> Instance::mangled_name
-> actual emitted symbol. Reject duplicate markers, identical object names, partial emitted sets,
and missing symbols with uninit enabled. Without uninit and with neither symbol emitted, permit
an empty private target set. A PFC harness with uninit injects the reset; reset references both
statics, so they must be reachable and emitted before handle_check_contract (compiler_interface).

Keep the original whole-main Lambda::as_contract_for target. For the buffer generate exactly
the twelve scalar member expressions, checked against bool/size_t types, each with its own lambda.
Do not generate a whole-buffer lambda, wildcard, user referent, or padding target. The existing
public modifies tuple routing and frame/clause logic stay unchanged. Exact field coverage is
checked independently of total lambda count; emitted binding is a coordinator gate.

The only whole-record construction is ArgumentBuffer::new in the static initializer. No runtime
Begin/store/load/reset statement writes the whole record, bytes, or padding. Runtime writes are
scalar field assignments/compound assignments. If emitted scopes show an aggregate/padding write,
this candidate stops for design clarification; no blanket aggregate exemption is authorized.

## Closure and qualification

The private zero-input initializer has only six scalar assignments. Its two any() calls infer
usize and dispatch through the built-in Arbitrary implementation/AnyRaw hook; no user memory,
user callback or generic user implementation enters its skipped body. Both uninit providers use
the shared skip guard. The call, original reset and immutable finalizer still execute.
The unchanged finalizer sees exactly one main marker and the same three typed fields; it inserts
seeds after all reset statements and before normal return. No refs/calls reseed state.

Only static source/hash/diff/pinned rustfmt checks run locally. Compilation and every G1/G2
outcome remain NOT_RUN until coordinator CI. B0 and B1 must receive identical reviewed test-only
delta and flags. If B0 closes all gates, select B0. G1 then full G2 (including both heavy fixtures)
precedes any M3. No local source push, build, CI/Cloud dispatch, workflow or runner edit.
