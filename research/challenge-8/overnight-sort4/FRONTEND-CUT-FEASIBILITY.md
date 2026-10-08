# Frontend-only first-comparator scope cut: feasibility review

This is a read-only architecture review. It proposes no active patch and
changes no proof status. The target is the unchanged first comparator in
actual 26.10 `sort4_stable` under the positive-size, non-ZST diagnostic
contract in [FIRST-CALL-RECOVERY-DESIGN.md](FIRST-CALL-RECOVERY-DESIGN.md).

## Possible splice point

The translator receives `BodyRd.ghost_decl_blocks_get_list` in
`translate_body`, converts the sole `let_lft` declaration at
`vf_mir_translator.ml:4913–4941` into synthetic
`#ghost_decl_block_start`/`#ghost_decl_block_end` statements, and
`find_blocks` reconstructs an `Ast.BlockStmt` using the matching real Rust
brace. `translate_basic_blocks_to_stmts` then emits the body AST (around
line 5219). An exact source marker between `c1` and `c2` could, in
principle, cause the translator to move the sole
`TypeWithTypeidDecl('cmp,...)` and the first-call prefix into an inner
`Ast.BlockStmt`, place its close at the marker, and leave the rest of the
original unsafe block outside that lifetime declaration. The original
closing-brace dummy command must be consumed exactly once as a no-op; it
must not release another lifetime-token half. No runtime MIR operation may
be removed, duplicated, or reordered. This is an AST scope-correspondence
change, not a ghost-only syntax trick or a source-level Rust block.

The stock `BlockStmt` path in `verifast.ml:2519–2699` consumes a lifetime
token for `TypeWithTypeidDecl`, reserves a half, and returns that half on
normal, return, and outgoing-goto continuations. Thus an inner AST block
could mechanically release the half after the first normal call and on a
certified direct-unwind goto. The required source sequence would close the
two reference-init fractions into concrete debt inside the inner block,
then run checked lifetime/borrow recovery and four-cell reassembly outside
the block. The first call's actual MIR has `Continue` unwind and no cleanup
block; its pre-call locals are raw pointers, references, tuple of references,
bool, and a reborrow of `F`, with no observed destructor call in that prefix.
These facts make a narrow control-flow splice plausible, but they do not
prove it sound for all source/model states.

## Why a translator-only patch is not yet admissible

The stock `BlockStmt` continuation silently filters heap chunks with type
arguments that mention the ending local type before returning the reserved
token half (`verifast.ml:2651–2673`). Its test sees a direct
`GhostTypeParam`, not all inferred/bounded metadata. A translator-inserted
block would inherit this behavior. For example, a still-live
`live::<'cmp,T>()` chunk could disappear at the cut instead of failing a
leak or proving its discharge. A name/CFG/source-shape gate cannot inspect
the verifier's dynamic heap across generic callback execution. The earlier
26.09 end-lifetime patch added a **kernel** strict-exit check precisely to
reject such chunks and to handle outer type-parameter bounds learned inside
the scope. It also rejected outer variables whose types mention the local
lifetime and rebased bound metadata on every exit. Omitting that part is a
semantic relaxation, even if the selected sort4 trace currently has no
known surviving `'cmp` chunk.

The generic `F: FnMut(&T,&T)` HRTB matching can refine type-parameter bound
metadata while the first call is checked. A bounded/inferred `F` or owner
chunk may therefore retain scope-dependent metadata even when its printed
type argument is only `F`. A static frontend check over the source and
decoded MIR cannot in general establish the absence of this proof-state
condition. A source-inserted assertion of one token or one named debt also
does not inventory all heap chunks. The stock `BlockStmt` does not wrap its
`econt` with the same lifetime cleanup; actual Rust unwind is represented
by `ReturnStmt(unwinding())`, so a narrow admission must prove the selected
path uses that continuation and not an unsupported AST exception edge.

Consequently a frontend-only split could be a **diagnostic** to test CFG
and resource ordering, but a green result cannot be accepted as actual
sort4 ownership proof without either (a) a fresh strict-exit kernel check
equivalent to the old one, or (b) a separately justified and mechanically
enforced proof-state invariant strong enough to exclude silent filtering,
stale bounds and unsupported exits. The latter has no identified stock API
or source-only certificate today. Porting the old strict checker is the
better evidenced route if the normal/unwind path shape is confirmed.

## Exact gates for any diagnostic splice

Admission must bind the exact std function/source bytes, the only
`ghostDeclBlocks` entry, unique `let_lft` and cut marker coordinates, the
first of exactly five `FnMut::call_mut` calls, its `(_5,_6)` arguments and
`v_base+1`/`v_base` tuple operands, normal successor, direct Continue,
all incoming/outgoing edges and all cleanup/Drop inventory. It must reject
an entry into the inner prefix from outside, a path from the first call
to `c2` that bypasses the cut, a second exit releasing the same token,
an early return, another callback, a different first-call operand, and a
changed unwind action. The generated AST must show every original Rust
statement once, the normal path reaching `c2` only after recovery, and
the unwind path reaching original unwinding return only after checked
recovery, with no runtime statement on the wrong branch. Paired NORMAL and
readonly full typed-MIR, refinement, complete verifier trace,
return/leak/dead-code checks, and controls for a live `'cmp`-typed chunk,
mutated bound metadata, wrong/missing debt, and shared cleanup are required.

Even if these checks pass, the frontend-only variant remains experimental
until the silent-filter and metadata issue has a mechanically enforced
solution. The 26.09 strict-cut patch and its hosted insertion fixture are
useful design evidence, not a 26.10 trust certificate.
