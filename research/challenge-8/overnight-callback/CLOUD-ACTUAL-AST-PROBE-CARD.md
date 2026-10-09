# Actual sort4 AST scope probe — before instrumentation

## R2 print-only extension after Cloud build 293435cf

The fresh O24 print probe reached the exact stock 185:13–36 reserved-marker
refusal. Its complete `Ast.Func` `Marshal.No_sharing` snapshot SHA-256 is
`dc7e8487ae46470ebcb9f964cb158c44d9bf75042cffa79d465f4d7e67001d39`.
The scope trace shows one `'cmp` declaration block at `root[138]`, its first
`FnMut::call_mut` switch at `root[138]/block[32]`, a normal-arm statement,
then a line-191 `OtherStmt`, `end_lft_binding`, `recover_pair` and
`join_four_owned_cells`; blocks 37 onward start the next call. The
line-191 statement and 134 earlier root declarations are **UNOBSERVED** at
their node-detail level. The text trace also omits the block's
`locals_to_free`, `Close` predicate arguments, call operands/type arguments,
and local assignment targets/values. No resource or lifetime conclusion is
inferred from these omissions.

R2 changes only text rendering in the same isolated, opt-in translator copy.
For each full AST node encountered it prints a `Marshal.No_sharing` SHA-256
and location. It exposes `DeclStmt` names, types, address-taken flags and
initializer descriptors; `TypeWithTypeidDecl`; every `Close` predicate,
type/index/argument descriptors; call type/index/argument descriptors,
including `FnMut` and `recover_pair`; local assignment targets/values; and
`BlockStmt.locals_to_free` metadata. Unknown expression/pattern/type shapes
are explicitly `UNOBSERVED` with their node hash, never guessed. The
original complete `Ast.Func` snapshot must retain the exact SHA above, the
off run must emit no dump, and all pre-existing source/MIR, profile,
refinement and 185:13–36 refusal gates remain. R2 is diagnostic only, not an
AST rewrite, a resource-model change or an accepted frontend component.

This is a Cloud-only, print-only diagnostic for the unchanged `sort4_stable`
body in `smallsort.rs`. O24's whole-body source and paired typed MIR reached
the reserved `__vf_sort4_first_unwind` marker, but do not show whether the
translator places the first `FnMut::call_mut` under the exact ghost-declaration
block introduced by `let_lft 'cmp = cmp_k`. That containment determines whether
an eventual outgoing unwind `goto` would use the stock `BlockStmt` lifetime
exit. The hypothesis is falsifiable: the first-call switch and both arms must
be inside one unique `TypeWithTypeidDecl("'cmp", typeid_of_lft(cmp_k))` block;
the probe must also report if this is false or ambiguous.

The diagnostic domain is the positive-size (`size_of::<T>() > 0`) four-cell
actual source fixture with current `T.own`, comparator `F.own`, thread and
optional destination resources. Its active normal post is partial. The full
normal target additionally initializes all four destination representations;
each callback unwind target returns the four *current* source owners, optional
destination before any copy, current `F.own`, thread and no borrow debt. Neither
target is established by an AST capture. Generic/ZST coverage is open.

The probe is disabled by default and touches only the disposable translator
copy built from the frozen O26 source profile (translator SHA-256
`0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a`).
It is not an accepted profile component. It writes a lossless OCaml Marshal
snapshot of the generated `sort4_stable` declaration with `No_sharing`, plus
a location/ancestor/block-order text trace. It changes no AST node, MIR edge,
proof resource, contract, kernel, std source, or verifier verdict. It runs
before stock verification of that body, so the expected full-verifier first
error remains `verified/lib.rs(185,13-36): No such function:
__vf_sort4_first_unwind`. A changed first error makes the probe inconclusive.

Admission before interpreting the trace requires the exact O24 verified and
ghost-stripped original unit SHA-256 values `fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9`
and `3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72`,
the complete NORMAL and readonly `sort4_stable` record SHA-256 values
`667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d`
and `925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5`,
and the existing first-call typed operand/CFG candidate audit. That audit
must still report only `CALIBRATION_REVIEW_REQUIRED`. Both complete graphs
must retain five FnMut, eight select and four copy calls; the first FnMut
must have ordered cells `v_base+1, v_base`, a normal target and direct
`Continue`, with no shared Cleanup or Drop. The translator additionally
checks the exact verified source bytes and local/block counts before dumping.
The probe artifact must bind source, both full graphs, the compiler/schema,
production translator and the rebuilt probe binary to one Cloud run.

Controls: after rebuilding the isolated probe console, run full VeriFast twice
on the *same captured fixture*: first with `SORT4_AST_SCOPE_PROBE=0`, then with
`SORT4_AST_SCOPE_PROBE=1`. The off run must produce the exact baseline
reserved-marker first refusal, no probe log marker and an empty AST output
directory. The on run must produce the identical first refusal and one dump.
A changed original/verified source, moved or duplicated marker,
wrong first operand/target/unwind action, graph count, Cleanup/Drop, or wrong
translator profile must reject at its corresponding source/MIR/profile gate.
A failed gate is not an intended proof negative. If the AST shows absent,
duplicate, or incorrectly nested lifetime blocks or first-call switches,
record the exact negative observation; never repair it by rewriting the AST
inside this probe.

The Marshal file is an OCaml compiler-internal snapshot, not a portable proof
certificate. Its human-readable trace preserves statement order, ancestor
blocks, source locations, first-call switch and `returning`/`unwinding` arm
order; unknown nodes remain in the lossless snapshot. The first normal
`FnCallOutcome` arm is verified before unwind. Since the current normal c1
path lacks a lawful early lifetime recovery under the frozen kernel, a future
handler can fail normally before direct unwind is checked. AST containment
alone is never an unwind proof, an accepted semantic patch, or a license to
assume an actual select summary.

Cloud Build347068de failed while building the isolated print-only console:
`Args.body_name` is unavailable in the enclosing Make functor at the probe
insertion point. The existing local TrBody exposes `State.body_name` and
`State.body_imp_loc`, while `local_decl_types` is already a lexical binding.
The new PROBE revision fixes those three metadata references only. No AST
node or verification rule changes; all same-source/on-off/refusal gates remain.
This was a setup failure before the probe ran, never a proof negative.
