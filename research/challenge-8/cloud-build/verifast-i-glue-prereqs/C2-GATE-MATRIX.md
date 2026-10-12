# C2 admission and proof gate matrix

All source digests are SHA-256 over the exact complete source bytes. An
`allow-control` source is admitted only as a named test fixture; it is not a
profile-wide source authorization. Compiler/layout metadata mutations must
retain the positive pair's source digest and reach the actual translator/kernel
gate. Storage-lineage controls are distinct, fully pinned source pairs and
must reach the actual translated marker and origin kernel path after body
entry. A runner-side generic digest rejection is not credit for either kind of
control.

| Case | Expected result | Evidence required |
|---|---|---|
| positive pair | C2 prefix and diagnostic suffix prove | constructor, `ENTRY`, exact `TARGET`, method implementation checking, full normal/unwind posts, lifetime and leak gates |
| overlap | reject at own/separation close | function body entered; target not reached; report the aliased local incarnation and failed separation predicate. The Rust cast uses `&*tmp as *const u64 as *mut u64` to avoid casting a shared reference directly to a mutable raw pointer. |
| missing source right | fail at full source-permission assertion at C2 target | body entered and exact assertion reached |
| readonly destination | fail in checked Drop `safety_proof` while establishing the copy safety bridge | quarter-only destination permission cannot establish the full uninitialized destination array needed by the `safety_proof`; this is a permission-refusal control, not a C2 target or body-copy write negative |
| source marker call | reject source annotation call | exact admitted source digest; parser/name-resolution diagnostic; no internal marker AST node emitted |
| changed source digest | reject source admission | exact negative pair and source-hash gate before layout claims |
| layout/compiler/target/type mutants | reject translator/kernel metadata admission | positive source digest preserved; malformed/foreign metadata delivered to intended real gate |
| strict survivor | pass | its admitted source pair; `let_lft` strict block contains an address-taken local before its marker, while incoming tail remains unchanged; show body entry and checked old-to-new heap mapping at strict exit |
| reconstructed origin | reject | its own admitted pair; actual `tail.read`/`tail.write` reconstruction, then later read and constructor separation gate |
| consumed origin | reject | its own admitted pair; incoming tail is consumed before `tmp`, then constructor separation gate after body entry |
| fresh local incarnation after cleanup | pass | its own admitted pair; two nested scratch StorageLive/StorageDead scopes retire before `tmp`, with each fresh incarnation traced |
| retired-storage separation | fail | its own admitted pair; first local's raw address survives `StorageDead`, then exact span-apart assertion against second address-taken local fails because numeric address reuse is allowed |
| wrong MIR/local marker binding | reject | positive source digest preserved; real translated marker carries body MIR id and declaration inventory, then kernel reports the mismatched bound identity |

The C2 target is immediately after the constructor/resource assertions and
before the diagnostic copy suffix. That suffix uses checked ordinary copy
resource recovery and ManuallyDrop to avoid invoking the compiler-generated
Drop edge; it does not claim C3. The actual `Drop::drop` implementation and its
`safety_proof` remain part of the checked input and cannot be omitted or trusted.
