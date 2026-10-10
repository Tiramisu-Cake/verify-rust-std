# C2 scope inventory — A5DE scaffold, read-only findings

Status: source/MIR/AST inspection only. This note does not bind either ghost
lifetime, prove a callback, admit a summary, or change the C2 `NOT_RUN` status.
WORK-POLICY revision 2026-10-10 was read. No compiler, extractor, verifier, or
proof command was run for this inspection.

## Pinned evidence and correct record identity

The fresh capture is Build `a5de0e51-3663-4c7d-9844-ff6b122436ee`, proof/infra
SHA `f925546602be4c606c0e60416f1f12047412c6a`, archive
`f87c9703fce601db67cb5e702e8c7481313d2ebea9c40e15f158b3882e833a99`.
The A5DE evidence note is
[`C2-FRESH-A5DE-EVIDENCE.md`](../sort4-native-entry-c1/C2-FRESH-A5DE-EVIDENCE.md);
source pin is [`C2-SOURCE-PIN.json`](../sort4-native-entry-c1/C2-SOURCE-PIN.json).
The full records were read from the archive extraction path
`/tmp/c2-a5de-read/allprooflogs/cases/sort4-c1-current-recovery/`:

| Record | SHA-256 | Shape / status |
| --- | --- | --- |
| `c2-normal-sort4-full-mir.txt` | `e270457999f9371bc94664917ebd96699eecec0b91148899aa48c511f398c82b` | 82 blocks, 164 locals |
| `c2-readonly-sort4-full-mir.txt` | `3598b01b91af60d4ad5f96cabc8225aad30bb9a2bd73eb7fc7add15473fb1a29` | 28 blocks, 110 locals |
| `actual-c2-unbound-scaffold-ast.ml` | `4fa7d49e420dc80681328bacdf08bb1d674dc2413001b99501da1c09b11dbb0a` | diagnostic-only AST; C2 deliberately unbound |

These are not the old C1 discovery records: `c2-discovery-fixture/normal-sort4-
full-mir.txt` is `667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d`
and readonly is `925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5`.
Those belong to the 55-block/137-local C1 fixture; do not cite them as A5DE C2.
The A5DE AST is the sole captured scaffold artifact, not the source-correct
bound AST. Its diagnostic says `UNBOUND_C2_LIFETIME_NOT_PROOF`; proof was not run.

The exact annotated source pin is `ecd83f8c0840a07f138bc8afa2a36c661f296d748693afa2a0a61667cb3372e4`,
ghost-stripped runtime is `3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72`.
Pinned source locations: C1 marker/call/cut at 185/190/192; second lifetime
begin and `let_lft 'cmp2` at 195/196; second unwind marker at 218; actual second
callback at 223; C2 cut at 225. The captured scaffold preserves 5 FnMut, 8
selector, and 4 copy occurrences. Complete source/MIR export, decode, and
refinement passed; the service graph inventories remain
`UNREVIEWED_COMPLETE_GRAPH_CAPTURE`, not proofs.

## Callback-local inventory from fresh normal MIR

The local declaration index below is the order in `localDecls` (and happens to
match the numeric `_N` MIR local). Types are the captured erased-region MIR
types. `addressTaken` is not a field in these complete MIR records; no boolean
fact for that property can be read from this schema. AST lowering does show the
explicit address-of / reference construction noted below. This is the allocation
inventory to preserve if a second local scope is later formed; `StorageLive` and
`StorageDead` are MIR operations, not claims that VeriFast's `locals_to_free`
should be emptied.

| Callback/source | Decl index / local | Type / role | Storage events (normal MIR) |
| --- | --- | --- | --- |
| C1 / 190 | 26 `_26` | `bool`, destination for `c1` | live BB22; initialized by returning outcome |
| C1 / 190 | 27 `_27` | `&mut F`, FnMut receiver | live BB22; dead BB24 |
| C1 / 190 | 28 `_28` | tuple `(&T, &T)`, call args in order `(1,0)` | live BB22; dead BB24 |
| C1 / 190 | 29 `_29` | `&T`, reborrow/reference for first argument | live BB22; dead BB24 |
| C1 / 190 | 30 `_30` | `&T`, `create_ref` temporary for `v_base+1` | live BB22; dead BB24 |
| C1 / 190 | 31 `_31` | `*const T`, raw pointer at `v_base+1` | live BB22; dead BB24 |
| C1 / 190 | 32 `_32` | mutable local of type `*const T`, pointer construction temporary | live BB22; dead BB23 |
| C1 / 190 | 33 `_33` | `&T`, reborrow/reference for second argument | live BB23; dead BB24 |
| C1 / 190 | 34 `_34` | `&T`, `create_ref` temporary for `v_base` | live BB23; dead BB24 |
| C2 / 223 | 62 `_62` | `bool`, destination for `c2` | live BB51; initialized by returning outcome |
| C2 / 223 | 63 `_63` | `&mut F`, FnMut receiver | live BB51; dead BB54 |
| C2 / 223 | 64 `_64` | tuple `(&T, &T)`, call args in order `(3,2)` | live BB51; dead BB54 |
| C2 / 223 | 65 `_65` | `&T`, reborrow/reference for first argument | live BB51; dead BB54 |
| C2 / 223 | 66 `_66` | `&T`, `create_ref` temporary for `v_base+3` | live BB51; dead BB54 |
| C2 / 223 | 67 `_67` | `*const T`, raw pointer at `v_base+3` | live BB51; dead BB54 |
| C2 / 223 | 68 `_68` | mutable local of type `*const T`, pointer construction temporary | live BB51; dead BB52 |
| C2 / 223 | 69 `_69` | `&T`, reborrow/reference for second argument | live BB52; dead BB54 |
| C2 / 223 | 70 `_70` | `&T`, `create_ref` temporary for `v_base+2` | live BB52; dead BB54 |
| C2 / 223 | 71 `_71` | `*const T`, raw pointer at `v_base+2` | live BB52; dead BB54 |
| C2 / 223 | 72 `_72` | mutable local of type `*const T`, pointer construction temporary | live BB52; dead BB53 |

AST support is consistent with this mapping: C1 receiver/tuple are `$_27`/`$_28`
at AST line 288; C2 are `$_63`/`$_64` at line 424. It constructs C1 refs from
`v_base+1` then `v_base`, and C2 refs from `v_base+3` then `v_base+2`, using
`fn_outcome_result(create_ref(&*ptr))` followed by `reborrow_ref(&*ref)` before
assigning tuple fields `0` and `1`.

For C2, MIR BB51 opens storage for `_63`–`_68`; BB52 ends `_68` and opens `_69`–
`_72`; BB53 ends `_72` and contains the actual `FnMut::call_mut`; BB54 ends the
remaining receiver, tuple, refs and pointer temporaries and opens `_73` for the
post-call ghost step. This is the concrete pre-call allocation/initialization
sequence a projection must retain. In particular it is not enough to preserve
an empty `locals_to_free` list while moving only the call node. Readonly MIR has
different numbering/CFG (c2 receiver/tuple `_63`/`_64` are live BB12, end BB13),
so do not transplant its local IDs or block numbers into the normal proof.

Requested block-32 context: normal-MIR BB32 is a source-199 ghost-temporary
block, not the second callback block. It ends local `_42` (source-line-198 empty
ghost declaration) and opens `_43` (source-line-199 empty ghost declaration),
then continues to BB33. C2 callback storage starts at BB51; the callback is BB53.
BB32 therefore gives no evidence that `cmp2` is bound to a real lexical scope.

## Lifetime shape, callback edges, and narrow scope design

The source/draft order is sibling intent: C1 has `cmp_k = begin_lifetime()` at
161 and `let_lft 'cmp = cmp_k` at 163; its callback and its normal post close
`comparison_debt`, end `'cmp`, recover pair `(1,0)`, and rejoin four cells at
190–194. Only after that normal prefix does C2 begin `cmp2_k` at 195 and declare
`'cmp2` at 196, prepare current owners `(3,2)` at 197–216, introduce the second
unwind cleanup at 217–222, then call at 223. Its normal path closes C2 debt at
224, ends `'cmp2`, recovers `(3,2)` and rejoins at 226–227. The draft's intended
sequential sibling scopes are not what A5DE implemented: the one captured
`'cmp2` declaration is in a **closed placeholder block at source 196**, with no
later lexical binding. Do not describe the scaffold as two bound scopes.

The AST has one explicit `SwitchStmt` per comparator call. C1 at AST line 288
uses `FnMut::call_mut<F, (&'cmp T, &'cmp T), 'cmp>` with receiver/tuple `$_27`,
`$_28`; `returning(__result)` initializes `c1`, while `unwinding()` returns
`unwinding()`. C2 at AST line 424 uses
`FnMut::call_mut<F, (&'cmp2 T, &'cmp2 T), 'cmp2>` with `$_63`, `$_64`;
`returning(__result)` initializes `c2`, while `unwinding()` returns
`unwinding()`. MIR call sites are normal BB23 for source190 and BB53 for
source223; both terminators have `unwindAction = continue`. AST source-level
outcome arms must not be collapsed into normal-only calls. The function declares
`c1`/`c2` as bool and the Rust callback is `FnMut(&T,&T)->bool`; the captured
AST carries `F`, tuple, and lifetime substitutions on `call_mut`, but no
separate emitted `Output = bool` clause. Do not claim an independent output
equality proof from this scaffold (the discovery profile has OutputEq off).

The C2 unwind marker is a source annotation immediately before the runtime
second call in the AST: it closes `comparison_debt(t, cmp2_k, v_base+3,
v_base+2, left2_ref, right2_ref, fractions)`, recovers `(3,2)`, and joins the
four current cells. C1's marker/epilogue is earlier. Therefore first-call
direct unwind returns before the normal continuation that starts C2; it must
not enter C2 cleanup or acquire a `cmp2` scope. Second-call unwind occurs only
after the first callback returned and C1's normal cleanup/rejoin completed.
Both paths retain the original unwind return and target return/leak/strict
checks.

Narrow design to review before any implementation: make the actual C1 and C2
boundaries two distinct sibling lexical scopes (distinct begin/binding/end
identities and distinct unwind epilogues), with C2 scope entered only on C1's
normal edge. Put C2's actual declaration/preparation, its source-217 cleanup
block, the unchanged call switch and its normal close/recover/join under that
real second scope. Keep all source/MIR declaration order and callback operand
construction, including the `_63`–`_72` live/init/dead effects; route only the
two verified cleanup edges to their own existing recovery sequence. Preserve
all callback outcome arms and keep both bool assignments. Then audit all CFG
ingress/egress and normal/direct-unwind posts against the full original AST,
not just a cut-marker count. The source-196 placeholder must be consumed into
the second real scope, not left as a closed block or copied as a second
declaration. Exact source/MIR/AST hashes and local/drop/addressability facts
must be re-pinned and independently reviewed before a proof run.

This remains bounded C1+C2 composition only. The actual caller selects
`sort4_stable` at `len >= 8` after its guard; this includes 8–15 (including
zero-sized `T`) and, for the other branch, lengths `>=16` when `size_of::<T>()
> 16`. Thus 8–15 is a sufficient unconditional caller slice, not the entire
actual sort4 call domain. The A5DE scaffold supplies neither that caller
precondition nor a C2 ownership theorem; actual `C2` remains `NOT_RUN`.
