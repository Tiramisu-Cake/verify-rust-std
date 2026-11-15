# F7 bounded compile-seam audit

Source 8e299aa6243bc5f06a29c51e98aafa9564478220, parent3f5242bb15, reference F.
Both reusable checks PASS: parent→F7 inventories5 Rust files; B1→F7 inventories192.
54 bound API contracts include the48 inherited contracts and explicit journal
begin/replace/restore, both delayed writers and both backend scopes. Generic K/V
and lifetime arguments, imports, declarations and impl headers match exact F.
Independent worker14's distinct55-contract audit also passes; see its review JSON.
Ten checker synthetic tests pass. Reports pin checker and contract hashes.

`mod delayed_cache` resolves to the new exact F file; DelayedCache is imported and
initialized in both production and scope-unit constructors. BodyTransformation's
scope API returns DelayedTransformationScope<'_>; Deref/DerefMut target the same
transformer, and Drop restores its actual cache. Both ordinary and failed-root
writers call replace_delayed_body; the temporary TransformationResult import and
direct writer snippets are gone. No fake API/no-op/stub remains.

Both backend guards begin before reachability/global-pass consumers and last
through contract/model materialization. Cprover export workers own materialized
symbols; LLBC's owned transformer covers the PubFns path too. Immutable prepare/
finalize, regular/stub transformations and loop metadata remain exact F.

This is bounded source-token/identity inspection, not Rust symbol/trait/borrow
resolution, macro expansion or compilation. Native fmt/build/clippy/default and
LLBC compilation remain NOT_RUN; they are explicit coordinator CI stages.
