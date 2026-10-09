# Actual sort4 post-mark print TEST — isolated verifier-core instrumentation

This is a separate Cloud-only, unaccepted TEST profile. The pinned O26
production tool and its kernel remain untouched. A disposable copy receives
only `verifast-actual-sort4-postmark-print-TEST.patch`, which adds opt-in
printing immediately after `stmts_mark_addr_taken` returns in
`src/verifast.ml` and before `verify_block`. No statement, ref, heap chunk,
model, contract, rule, operation order, or runtime source is rewritten.
Editing a verifier-core file creates a new trust surface even though this
patch only reads the post-mark AST and writes diagnostic artifacts. It is
never accepted as an ordinary production or proof profile.

The exact input remains O24's actual `sort4_stable` source pair: verified
SHA-256 `fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9`,
original `3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72`.
The complete NORMAL and readonly function MIR hashes remain
`667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d`
and `925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5`.
Both modes retain 55 blocks, 137 local declarations, five FnMut calls,
eight select calls, four copy calls, direct first-call `Continue`, and no
Cleanup/Drop; refinement must pass. The production translator hash is
`0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a`.
The unmodified verifier-core source at stock commit
`f76012fb518703b1d98e243ac4f487f16877cfcb` has SHA-256
`adbf2c3de02cba7fbdb0b8e203a864e34c1b2ab16de4f6b153477106dbba04d0`.

The hook selects only a body containing exactly one serialized reserved
`__vf_sort4_first_unwind` marker in the exact verified file. It writes
`Marshal.No_sharing` bytes immediately after mark and again after printing;
the two files must compare byte-for-byte. Its trace includes every reached
local's source location, name, address-taken bit, lossless type/initializer
Marshal hex, and `blockPtr` owner as a unique physical `BlockStmt` path or
explicit `UNOBSERVED`. It prints ordered `locals_to_free` names and const
bits. These lists are **lazy**: `stmt_mark_addr_taken` binds block pointers,
while `DeclStmt` verification may append cleanup entries later. This
post-mark trace cannot show that later cleanup or prove safe storage freeing.
Any unmapped/ambiguous owner, missing selected tuple, changed AST bytes, or
failed output gate makes the result inconclusive. No AST scope splice runs.

The hypothesis is that c1 tuple local `$_28` and the later tuple locals
`$_41`, `$_72`, `$_79`, `$_108` have observable post-mark types and owner
paths, while their actual cleanup fate remains open. The reviewed source,
MIR and refinement baseline runs first. The rebuilt isolated console runs
the same fixture twice: opt-in off must emit no output and reproduce the
stock first error at `verified/lib.rs(185,13-36)`, then opt-in on must emit
one trace and the **same** first error. Both runs must keep leak/dead-code
checks active as part of ordinary full verification; neither may be called
a negative if setup, output, source, profile, MIR, or error gates differ.

The falsifier is any changed source or full MIR graph, a changed first error,
nonempty off output, missing on dump, differing post-mark before/after bytes,
or a patch touching code outside the single print hook. Output is
diagnostic only (`accepted=false`, `verification_accepted=false`). It gives
no storage-safety, alias, liveness, lifetime-cut, generic/ZST, full
normal/unwind-post, or actual select proof credit. The blocked AST-scope TEST
remains blocked and disabled.
