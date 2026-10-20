# R9 BeforeLive investigation — 2026-10-20

Read-only source investigation while Build2 runs. No profile, tool, or source
implementation changed. The current lexical `mir_stack_addr`/unbound-local
refusal cannot establish a physical heap refusal before MIR `StorageLive`.

## Verified ordering and representations

- In `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`, every MIR local
  gets a VF `DeclStmt` in the function prologue (`translate_to_vf_local_decl`,
  near 2116; declaration list assembled near 7385 and prepended to the blocks
  near 7752). MIR `StorageLive` and `StorageDead` remain separate translated
  statements (near 4248–4261). The name mapping is the translated MIR local ID;
  the allocation symbol name is that local name plus `_addr`.
- `src/verifast.ml:3601–3626` gathers the Rust incoming heap, every local with a
  StorageLive event, and constness into `rust_storage_context`. The deferred
  branch in `DeclStmt` (`:1210–1223`) registers the local's type and deferred
  status without inserting an address value into native `env`. Its local
  address-taken flag is separately emitted as `LocalAddrTaken`.
- At `RustStorageLiveStmt` (`src/verifast.ml:1032–1145`), the checker first
  requires a deferred, currently-dead local, obtains
  `get_unique_var_symb_non_ghost (x ^ "_addr") (PtrType t)`, applies the
  existing exclusion assumptions against incoming/live allocations, and only
  then calls `produce_cxx_object`. The native `env` gains both `x` and its
  `$rust_storage_live$x` receipt only after object production succeeds. Thus
  source ghost code before this statement cannot name an `env`-bound address.
- `get_unique_var_symb_non_ghost` (`src/verifast1.ml:6784–6797`) constructs a
  stable uninterpreted symbol and applies type bounds / Rust pointer-shape
  assertions. “Unique” here is symbol-table uniqueness; the helper does not
  allocate storage, add points-to ownership, or establish separation from the
  input heap. Reusing that term early would therefore bind a candidate symbol,
  not establish that it denotes the physical address of the impending stack
  slot.
- The generated Rocq `LocalAddrTaken` protocol (`bin/rust/rocq/SymbolicExecution.v`
  around 318–348 and function-local allocation around 672–677) allocates a
  local slot at function entry when its flag is true. That consumer does not
  follow the native Rust StorageLive/Dead receipts. Its earlier slot cannot be
  used as proof that native source `env` contains a live owner, nor as
  independent Rocq/storage-liveness credit.
- `mir_stack_addr` rewriting (`vf_mir_translator.ml:7200–7282`) resolves an
  exact raw MIR local ID to `AddressOf (Var ...)`; it does not create a native
  `env` entry. It is restricted to a materialized struct local with hidden
  name and supported declaration index. Even where admitted, it does not
  override the pre-live native local-binding boundary.

## Safe control boundary

An internal diagnostic immediately before `produce_cxx_object` could report
the current `StorageLive` local ID/span, type, symbolic `addr`, and bounded
incoming/live heap terms. It could be source/MIR-bound to the actual StorageLive
statement, but it would run *while processing* that statement and would only
observe the impending symbol. Because the symbol has no prior allocation
receipt and no established relation to an existing points-to chunk, this is
not a source-before-StorageLive physical heap refusal. A failed assertion on
the symbol, or a fabricated equality to an input element, would not repair
that gap.

To prove a physical refusal at a source point strictly before StorageLive, the
native checker would need a checked mapping from that source point to the
specific MIR local's actual stack address while leaving the local absent from
the liveness environment and without producing its object. No current
source-level or translator interface supplies that mapping. Adding a separate
pre-live address receipt would be a new semantic interface; storing it under
the local's ordinary environment key would incorrectly make the local appear
live to the existing `StorageLive` guard. `LocalAddrTaken`, a symbol-name
convention, numeric-address equality, and Rocq's eager local slot are not
substitutes.

Therefore the existing model can support only a bounded observation before
object production at the StorageLive handler. It cannot soundly classify a
strictly pre-StorageLive case as EXPECTED_PHYSICAL_HEAP_REFUSAL without a
reviewed, source/MIR-bound pre-live address representation and a checked
resource rule. Keep the existing BeforeLive case INCONCLUSIVE until that
interface exists; keep default-on addressability controls separate from the
default-off R8 allocation premise, and award no storage/liveness or Rocq
credit.
