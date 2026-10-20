# R10 BeforeLive source review — 2026-10-21

Read-only review of `R9-BEFORELIVE-NOTE-20261020.md`, the R5 addressability
controls, and the native StorageLive implementation in tool HEAD
`48ace768cf974a2db400ca14e5f82253b7a77fa0`. No project/tool changes,
builds, preparation, compilers, proofs, or raw evidence were used.

## Reachable calibration, not the BeforeLive obligation

A source-preserving diagnostic calibration can place a physical resource
assertion before a later local declaration while avoiding that future local:

```rust
pub unsafe fn before_storage_live(anchor: *mut u64)
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    //@ assert *anchor |-> ?observed; // TARGET: missing physical owner before later local
    let local = 31u64;
    assert!(local == 31);
}
```

`anchor` is a bound parameter, while `req true` supplies no points-to chunk;
the exact target can therefore reach the native missing-heap diagnostic rather
than an unbound-local error. The existing R5 negative classifier already
requires unchanged source/stage receipts, a single error at the target line,
and the mapped diagnostic. This variant would only calibrate that physical
error path at a source point before a later declaration. It asks about the
parameter address, not `local`'s future stack slot, and so does **not** close,
replace, or earn credit for physical BeforeLive. It also duplicates the
resource shape of `missing_physical_owner`; its only extra value is the source
ordering calibration, which is not currently a MIR-order receipt.

## Exact blocker for the future local

The R5 case instead asserts through `&local` before its declaration. In
`vf_mir_translator.ml:4249–4255`, MIR `StorageLive` becomes a separate
`RustStorageLiveStmt` carrying its source/MIR locations, raw MIR local ID, and
translated local name. In `verifast.ml:1214–1222`, a deferred local's type is
registered in `tenv`, but its address/value is not inserted into native `env`.
A local used by ghost address-taking is deferred. Runtime local-variable
evaluation uses the live `env` (`verifast1.ml:8567`); type visibility in
`tenv` is not a runtime address binding. Thus the annotation can type-resolve
`local` but cannot evaluate its address, and the observed lexical/unbound-local
refusal is not a physical heap refusal.

The bare-MIR escape hatch does not bridge this interval. The opt-in
`mir_stack_addr(n)` admission and rewrite are in `vf_mir_translator.ml:5737–5759`
and `7247–7316`: it accepts a unique hidden raw MIR local ID (not a
source/debug-named local), restricted to a materialized stock struct, and
rewrites to `AddressOf(Var vf_name)`. It emits a source/MIR identity diagnostic;
it does not create a verifier `env` binding or heap object. The ordinary
variable evaluator still needs that binding.

The first native address term is created while processing
`RustStorageLiveStmt` (`verifast.ml:1032–1145`). That handler requires the local
to be dead and deferred, obtains the unique `x_addr` symbol, performs the
existing interval exclusions, then calls `produce_cxx_object`. Only after
production succeeds does it add both `x` and `$rust_storage_live$x` to `env`.
No existing source-level interface supplies the actual future slot address
strictly before this handler while keeping the local absent from the liveness
environment. `LocalAddrTaken` is emitted separately for Rocq; its eager local
allocation consumer (`bin/rust/rocq/SymbolicExecution.v:318–348`) does not
consume native StorageLive/Dead receipts and cannot establish native ownership
or liveness.

Therefore no source-only rewrite of the current BeforeLive mutant can target
the future local's physical address under the existing model. A source/MIR-bound
pre-live address receipt plus a checked resource interface would be new
semantics; a symbol name, raw local ID, numeric address, eager Rocq slot, or
unrelated `anchor` refusal is not a substitute. Keep the existing BeforeLive
case INCONCLUSIVE and separate any anchor-based calibration from that
qualification obligation. No Rocq/storage-model expansion or proof credit is
proposed.
