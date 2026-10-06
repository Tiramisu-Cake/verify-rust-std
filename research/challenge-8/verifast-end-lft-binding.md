# Experimental ghost lifetime binding cut

This source patch applies after the tuple parser and FnMut HRTB patches to
VeriFast 26.09 source `809de4596839b739dd999f9e462242c835e3af46`.
It changes only `vf_mir_translator.ml` and `verifast.ml`. The preceding HRTB
patch is `d90fb7a814b098a6008c4e64c567d2a3798e8f18999d12905425ef17224dbe1f`;
the translator input file after it is SHA-256
`ef88c9c08388ef85bc661675f19212041e37b341d5ab61132ff80e5b9080b8d4`.
The original `verifast.ml` input is SHA-256
`5968a05e264042782e8373c452b241ccdd1f4ba3323d596888a9bdf6b18c3310`.
The patch is [verifast-end-lft-binding.patch](verifast-end-lft-binding.patch),
SHA-256 `76c3f6dbc54183997a40d91c8a178a3b751a6771c8a42e79bb9cacbbe04c89e8`.

## Scope and semantics

The opt-in source spelling is a regular ghost statement,
`//@ end_lft_binding::<'cmp>();`, strictly inside the Rust block whose first
ghost declaration is exactly one `let_lft 'cmp = cmp_k`. The marker must precede
the original closing brace and must be unique for that block. It does not
change any Rust token or runtime operation. The translator pairs that block's
existing synthetic ghost start with a new synthetic end at the marker. It
consumes the original closing-brace dummy call as a no-op, preventing a second
release of the reserved half of `lifetime_token(cmp_k)`.

The existing `find_blocks` reconstruction makes a nested `Ast.BlockStmt`
containing the MIR prefix. The existing `BlockStmt` continuation returns the
reserved half on normal exit, return, unwinding return, and outgoing goto. A
successor may not jump into that prefix from outside. The type name `'cmp`
goes out of scope at the marker. The proof must still recover its other token
half by closing fractional accesses, then call ordinary `end_lifetime(cmp_k)`
with the full token. To recover `points_to<T>` after the lifetime ends it must
use the genuine `borrow_end` tokens and `open_full_borrow_content<T>`; this
patch neither creates ownership nor changes those contracts.

Rust MIR unwind actions use explicit returns or cleanup-block gotos, both of
which run the scope exit check. A separate AST exception continuation is
unsupported for this strict block and fails closed if invoked.

The new internal first statement of the synthetic block opts into a strict
kernel exit check. At **every** block exit, the verifier rejects a heap chunk
whose type arguments mention the ending local ghost type instead of silently
filtering it. It also rejects a surviving outer variable whose type mentions
that type. Local projection equalities containing the ending type are removed
while the verifier explores code outside the block and restored for sibling
paths still inside it. All type-parameter bound facts newly registered in the
shortened prefix have lexical scope and are forgotten after that block, even
when they do not mention `'cmp`. Existing block behavior outside this opt-in
remains as before. The internal statement is consumed by `BlockStmt`; no AST constructor,
parser grammar, verifier assumption, or lifetime axiom is added.

The current probe has no additional generic `F` or `T` restriction. The exact
Rust `insert_tail` body and signature remain the target. This experimental
feature does not prove that function or Challenge 8 by itself.

## Hosted acceptance and negative regressions

All executable checks, compilation, and verification belong on GitHub-hosted
Actions. The local static checks are patch applicability and whitespace only.

1. Apply tuple parser, HRTB, then this patch to the pinned source. Record
   exact source hashes, build/refinement results, and the generated verifier
   binary hash. Verify that this patch changes only its two named source files;
   the combined tuple-parser, HRTB, and lifetime-cut sequence changes three
   source files.
2. On the exact-source `insert_tail` probe, close both comparator access
   fractions before the marker. Immediately after it, prove the **full**
   `lifetime_token(cmp_k)`, then run ordinary `end_lifetime`, both `borrow_end`
   calls, and both `open_full_borrow_content<T>` calls before the actual
   `tail.read()`. Inspect normal, early-return, and comparator-unwind paths.
   Reaching the next body obligation is a milestone, not a full proof.
3. Reject malformed, duplicate, wrong-lifetime, unknown, outside-block, and
   post-brace markers. A marker in a nested active ghost declaration block or
   a block with other declarations is unsupported and must fail closed.
4. Reject a live ghost chunk parameterized by `'cmp` at the cut; a weak `ens`
   must not make its removal silently succeed. An unclosed fractional access
   must fail the full-token assertion or `end_lifetime`. Ghost use of `'cmp`
   after the cut must fail type checking; an incoming goto to the prefix must
   fail. A second `end_lifetime` or full-token assertion after the original
   brace must fail, showing that no token is returned twice.

The structural pairing and CFG ingress check still require hosted validation
against the actual exported MIR. If they reject its shape, stop and inspect
the resulting AST/trace before broadening the feature. Do not weaken the
source fidelity, unwind checks, resource checks, or generic domain to obtain
a green run.
