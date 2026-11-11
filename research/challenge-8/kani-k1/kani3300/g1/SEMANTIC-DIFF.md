# KANI3300 G1 — semantic candidate (static only)

- Defect: arbitrary direct raw-pointer union pointees previously rejected reads/updates,
  and union shadow extent used max(field size), losing rustc alignment tail.
- Base: 657c2b24516b967f67ce71994299d0ef328aede9, without CMP2.
  Production is byte-identical to c39cc1121cdb287d9d77c38b87cff6c84c2c8046.
- Storage extent and arm offsets come from rustc, with checked field ranges.
  Storage extent is rustc size(U). Untyped copy/copy_nonoverlapping and write_bytes
  affect their complete extent, including padding/tail and false source bytes.
- Typed union transfers use a separate preserve mask: OR of supported arm data masks.
  Copy and argument/return load intersect destination state with that mask; false
  source data stays false. Allocation constants are intersected too.
- MIR Copy and Move stay distinct. Move clears source-only bytes after transferring
  the witness; destination wins on overlap. Argument Move is cleared on the matching
  callee-entry load. The flat buffer gains one Move flag, and never reads dead sources.
  Immediate constructor/field Move operands clear after source checks, before assign;
  destination masks install afterward. Repeat copies every slot before one source clear.
- Whole construction replaces the full extent with the chosen typed field mask;
  projected field/subfield stores replace only their own extent (padding false).
  A ZST field write changes no payload; whole ZST construction resets the union.
- Structural validation precedes zero-size/scalar ABI shortcuts. By-value union
  containers, nested unions, unsupported enum layouts and fn-pointer fields reject.
- Direct union field reads check the actual selected projection; taking an address
  does not read/initialize payload. Pointer bytes never initialize their pointee.
- Bodyful arguments and returns use the same paired shadow protocol, forced return
  index zero, consumed match and size check. Addresses are captured before overwrite;
  return transfers use saved IDs, never dereference expired stack pointers.
- Existing MaybeUninit storage/flat-array recognition and lang-item transmute rules
  remain separate. Existing MU typed storage transfers retain their P1 mask policy.
- Unmodeled typed_swap/select_unpredictable/volatile/foreign effects reject explicitly.
  No init predicates, user validity/provenance/bounds/frame checks or aliases weakened.
- No new points-to model, backend, runner, trusted premise or CI/tooling changes.
- Mask rule is an explicit layout-derived inference for shared union data storage,
  not observed backend preservation. Pinned maybe_uninit.rs:273-315 permits loss at
  typed padding; pinned ptr/mod.rs:463-469,587-598 distinguishes untyped copies.
- Discriminating controls: wide/narrow/whole/field/ZST reset; C/Rust layouts; typed
  padding loss versus untyped tail copy; argument/return overwrite; overlap raw backing;
  pointer alias and delayed typed read; moved-from aliases; all-ZST; rejected G2/intrinsic/bodyless paths.
- Compilation/native/full regression/core replay are NOT_RUN. Proof credit NONE.
  This packet does not close general #3300 or authorize dispatch/Cloud spending.
- Inherited P1 limitation: MU<T> transmute Move-source alias invalidation is not
  repaired here; MU-specific conversion whitelist is unchanged, MU<U> is G2-rejected.
