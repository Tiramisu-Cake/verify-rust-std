# R23 translator compile-layer repair

P6 built the exporter and decoder at exit0, but the translator reported a
duplicate `RawPtrTyRd` module. The candidate removes only the new duplicate
and keeps the original binding. A static scan finds94 unique module names.
The previous static claim that such duplicates were legal was incorrect;
the historical record is retained and the P6 receipt records the correction.

A subsequent type-layer audit found additional compile defects before a new
Build: `D.decode_ty` maps a Reader value into a `D.ty` record, while local
`decode_ty` maps that record to the semantic variant used by the gates. Array
elements in `D.ty_kind_array_ty` are already records. The candidate applies
only the required layer transitions for the existing exact u64/array3 and
Ref/Unsize checks; generic `Type ty` values receive local semantic decoding.
The matching existing code at translator1424/1678/1947/12328 supplies the
interfaces. The new operand matcher intentionally keeps its intermediate
record because its pattern matches that representation.

No type, resource, call, lifetime, scope, signature, body, metadata, or control
gate is broadened; unknown types retain refusal. Compiler, translator and
proof acceptance remain Cloud-UNVERIFIED. Profile6 and phase8 checks pass;
no actual compiler, decoder, exporter, refiner or verifier ran locally.
