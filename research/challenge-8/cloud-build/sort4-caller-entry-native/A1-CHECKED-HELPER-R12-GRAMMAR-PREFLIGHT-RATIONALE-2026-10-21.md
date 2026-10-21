# R12 isolated ghost grammar preflight

R11 separated two unresolved failure classes: the fully qualified Option
constructor did not resolve as a constructor, and a `use` embedded in the
helper declaration block failed parsing. These failures prevented the helper
proof stage from reaching the body. The R12 parser audit found that module
imports and ghost declarations occupy distinct parser alternatives. A small
Cloud-only preflight therefore checks the complete helper grammar shape before
the canonical caller fixtures are assembled.

The preflight uses the exact `OPTION_CLEANUP_IMPORT` and pure
`OPTION_CLEANUP_LEMMA` bytes supplied by the fixture module. A generic exported
Rust `Option<&'a T>` anchor keeps Option ADT export in the source unit while the
verifier focuses only the helper lemma. It writes a fresh `verified/lib.rs` and
`original/lib.rs` pair for each of three controls and binds both hashes before
each same-Build console stage. The positive pair is accepted only when the
console exits zero, emits an AST, and the pinned helper selector selects one
manual `a1_cleanup_option_ref` lemma at its exact source interval. Negative
pairs are accepted only when a nonzero stage has the one expected diagnostic
at the exact source line: the R11 S4 constructor-resolution message or the R11
S5 parse error at the following lemma declaration. The S5 control places a
bare `use ...;` declaration inside the ghost block; it does not nest a Rust
`//@` line annotation inside the block.

R12 profile pin `a1_checked_cleanup_import_sha256` binds the standalone import
bytes separately; the loaded fixture module and generated full source pair
retain their own existing source pins and hashes.

The stage runs with the reconstructed pinned console and compiler toolchain,
but `c4.clean_env` strips A1 macro and stage controls. It checks the active
Cloud provider, authorization phase, historical protocol phase, Build,
coordinator profile SHA, tool receipt, tool source hashes, source locations,
and tool identity before and after every stage. Each variant keeps its own
stage/log/AST metadata. Exceptions, partial or not-run stages, missing or
malformed fields, changed hashes, wrong diagnostics, and unexpected exits
remain blocked or inconclusive; they do not turn into a successful control.

This is a grammar/context gate only. The runtime anchor is not focused, the
helper's ownership proof is not inferred from successful parsing, and neither
this result nor its AST record carries proof credit or a caller receipt. R12
must still run the nonpublishing helper body proof in the same Build and exact
caller source pair before any caller consumes the helper summary. P0a/P0b
body-and-conformance receipts remain independently mandatory on their exact
positive caller pair.

Synthetic tests exercise the stage service contract, including exact
diagnostics and source coordinates, plus exception, partial, malformed exit,
missing metadata, log mismatch, bad AST selection, tool/profile guard, and
unexpected-negative outcomes. They do not run the parser, compiler, or
verifier.
