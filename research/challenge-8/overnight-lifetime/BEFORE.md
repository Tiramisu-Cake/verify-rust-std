# 26.10 strict lifetime-cut component: decision before implementation

This component is newly authorized for the overnight research branch. It is
separate from accepted S6/CFG and all experimental H2, callback, helper and
sort4 components. The old project-authored 26.09
`verifast-end-lft-binding.patch` is design evidence, not an applicable or
trusted 26.10 certificate. The target base is VeriFast f76012fb plus the
current separately identified overnight patch chain (through the O17
callback and H2b drafts); no 26.09 HRTB patch is imported.

## Actual obligation, hypothesis, and domain

O16 reached the first unchanged actual `sort4_stable` comparator under the
positive-size, non-ZST diagnostic contract and failed the full current-source
unwind post with the first two cells borrowed. The sole exporter
`ghostDeclBlocks` binds `let_lft 'cmp = cmp_k` to the entire real unsafe
block, whose second comparison immediately follows the first. A ghost-only
source block is not an exporter block. The falsifiable hypothesis is that an
explicit unique source-written `end_lft_binding::<'cmp>()` marker between
comparisons can shorten the lifetime binding in the reconstructed verifier
AST, returning the reserved half token exactly once on normal and direct
unwind exits, so checked source-written recovery can run before the second
comparison or the original unwinding return. This component proves only
scope mechanics; it adds no borrow, owner, array or callback resources and
does not itself prove sort4 safety or order.

The scope feature is opt-in: exactly one named lifetime in exactly one
exported real Rust ghost declaration block whose sole declaration is its
`let_lft`; one regular ghost marker strictly inside the block and before its
real closing brace; complete source/MIR binding, including marker position,
block start/end, exact body path, and CFG ingress/egress. No generic
`end_lft_binding` behavior is admitted for malformed, nested, multiple,
unmatched, or non-Continue/unsupported exits. Other functions retain stock
semantics. The selected sort4 diagnostic retains its current four initialized
source cells with exactly four `T.own`, optional destination, current
comparator `F.own`, thread/type resources and unrestricted permitted
comparator behavior; `size_of::<T>()>0` is explicit and ZST/general generic
coverage remains open. The complete intended normal post still requires an
initialized destination; the diagnostic normal post is partial. The full
current-source/owners/optional-destination/comparator unwind post remains
unchanged and is expected to fail until the separate checked unwind recovery
protocol is integrated.

## Proposed semantics and trust boundary

The translator relocates the **existing** synthetic ghost block end from the
real brace to the unique source marker, retains the original brace as a
verified no-op, and constructs a nested `Ast.BlockStmt` over the existing MIR
prefix. The normal successor after the cut remains the next original Rust
statement. Return/outgoing-goto/direct-unwinding-return paths leave the
shortened block through stock continuations; a jump into its prefix from
outside is rejected. The marker does not create a lifetime or return a token
by itself. The existing `BlockStmt` consumes/reserves the lifetime-token
fraction and returns that same fraction at exit.

This requires **new trusted changes in both** `vf_mir_translator.ml` and
`verifast.ml`. The kernel-side change is essential: stock block exit silently
filters heap chunks whose type arguments mention the ending local lifetime.
The strict opt-in exit instead rejects any such live chunk, surviving outer
variable type, or escaping bound/inference metadata; it must not discard a
chunk or silently alter permission/heap terms. Bounds learned inside the
scope on an outer type parameter such as `F` are rebased to an immutable
entry snapshot at all exits, with direct scoped references rejected; saved
bounds and outer variable types are checked before leaving. Normal, return,
unwinding return, and outgoing-goto paths receive the same strict check and
restore the half token once. AST exception exits not supported by the
certified Rust lowering fail closed. There is no change to separation logic,
SMT, prelude axioms, memory model, permission rules, refinement, leak,
validity, or dead-code enforcement. An implementation that drops resources,
weakens target posts or bypasses real cleanup is rejected.

The parser/translator extension is disabled by default. A source marker is
rejected unless the hosted invocation sets `SORT4_STRICT_LFT_CUT=1`; without
such a marker the patch follows the stock route. This opt-in merely enables
the generic strict-scope operation. It is **not** a certificate that a
particular std body or comparator call matches the operation: each fixture
and any later actual-sort4 integration must separately pin full source,
function DefPath, declaration-block coordinates and complete typed MIR/CFG.

## Hosted regression gate and outcome decisions

The separate 26.10 patch must statically apply after the pinned current
chain, change only the named translator/kernel files, and pass hosted build,
NORMAL and readonly MIR export/decode, refinement and full verifier checks.
The old 26.09 control bodies are to be ported as **fresh source/MIR
fixtures**, preserving exact intended failure classification: positive
simple cut and direct-unwind/early-return paths; malformed, duplicate,
wrong lifetime, unknown/outside/nested/post-brace markers; incoming goto,
double half-token use, second end_lifetime, `'cmp` type use after cut,
unclosed fractional access, live `'cmp`-typed heap chunk, outer-variable
escape, stale F-bound/inferred metadata, and callback or shared cleanup
that does not fit the selected shape. A negative counts only if its positive
setup reaches the intended strict obligation; source parse, export, missing
callee, or unrelated helper failure is inconclusive. Keep full normal and
unwind posts, return/leak/dead-code and memory/refinement checks enabled.

For actual sort4, admission is separate: exact unchanged Rust body/signature
and pinned std hash; complete five-call NORMAL/readonly graph; unique first
FnMut operand trace to `v_base+1`/`v_base`; exact scope marker and all
normal/unwind/cleanup edges; generated AST prefix/outer continuation; checked
normal and unwind debt close/recovery/join-four source steps. A cut-only PASS
does not close that target. If the strict check detects a surviving chunk or
bounds, revisit the resource protocol; do not remove the check. If 26.10 AST
or bounds shapes differ from the old patch, resolve the discrepancy with
explicit review before broadening the implementation.
