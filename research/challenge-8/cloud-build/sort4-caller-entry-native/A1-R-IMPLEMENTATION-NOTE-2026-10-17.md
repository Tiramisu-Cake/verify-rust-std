# A1 R draft: required-item representation (UNRUN)

This draft is the R transport component only. It is based on VeriFast source
`f76012fb518703b1d98e243ac4f487f16877cfcb` and the final selected-branch
translator reconstruction with SHA-256
`e484d9f95202c876957a5d5ab349c6a40bc04dbcf813db4b373819402d807e64`.
Apply `required-item-representation.patch` after the existing selected-branch
translator patch. No local compiler, source extractor, proof runner, or verifier
was executed. The candidate has no proof credit.

`RequiredFn` now carries the compiler item path/index, method HIR and compiler
generics, every method clause, all parent-trait clauses in a separate
compiler-owner list, and a required-item-only scoped region binding table,
and a required-item-only type parameter binding table. `GenericParamDef` carries
compiler parameter index and definition index. Its type parameter binding table
keeps wire aliases separate from source names (`Self` and `F`) and compiler
numeric identities. `Body`, `TraitImpl`, and
`TraitImplItem` carry distinct
compiler definition indices. The pinned exporter previously collected only
struct-headed trait impls; under the A1 opt-in it also collects the two generic
`StableSmallSortTypeImpl for T` impls. OFF retains the original impl collection
and original required-item encoding.
The certified root trait inventory is restricted to exactly two required
methods. Its threshold must be safe `() -> usize` with no signature lifetimes;
`small_sort` must be safe, have the three checked input borrows, and return
unit. Unknown or provided associated items fail closed under the opt-in.

The opt-in required-item encoder is local to the certified trait. It encodes
region identities using the local item index, signature or clause binder owner,
de Bruijn depth, bound variable index and compiler region kind. The binding
table records these semantic coordinates separately from wire aliases. A
bijection of aliases is accepted when declarations, types and clauses are
renamed consistently; a duplicate, free region or input-position swap is
refused. Every clause gets its own binder owner. FnMut and FnOnce::Output are matched only by a narrow
structural alpha correspondence over their separately scoped variables; the
clauses remain distinct. Unknown types, region scopes, constants, clause kinds,
and binder kinds fail closed. The ordinary global `encode_region`, `encode_ty`
and `encode_clause` are untouched.
The reader requires compiler-exported `Self: Sized` and
`Self: StableSmallSortTypeImpl` parent-trait clauses before marking the AST
`Self` parameter sized. It retains the self predicate separately from Sized
and rejects unknown parent clauses. Parent clause regions use the parent trait
definition index; method clauses and signature regions use the method index.
Type parameter aliases are looked up from the single method binding table in
all three scopes; parent-clause region ownership never changes the `Self` alias.
The [rustc `clauses_of` source documentation](https://doc.rust-lang.org/nightly/nightly-rustc/src/rustc_hir_analysis/collect/clauses_of.rs.html)
motivates checking both the `Self: Trait` clause and trait-header bounds. That
online source is not the pinned 2026-09-25 compiler source; the exact clause
inventory remains an explicit UNRUN Cloud gate.

The internal canonical region spelling preserves the old native contract's
elided borrow classification. It starts with `'__vf_req` only when the pinned
global encoder would have produced a name starting `'_`; explicit-role regions
start `'vf_req`. The reader can accept an arbitrary bijective wire alias rename
because it normalizes through the scoped binding table before `gen_contract`.
This matters because `gen_contract` classifies mutable in/out borrows by that
prefix. The reader checks three distinct elided mutable input borrows in the
actual `small_sort` signature. Type parameter uses similarly encode compiler
`ParamTy.index` in the wire alias; the reader checks alias membership, the
Self/F binding table and numeric declarations, then restores their declared
AST names. A consistent bijective rename of these wire aliases is accepted.
A later review must compare the
native pre, returning post, and unwind post ASTs with the OFF generation and
reject any loss of resources or changed outcome branch.

The translator keeps a read-only `A1RequiredInterface` record with method
compiler identity, method parameter identities, signature regions, scoped
binding tables, decoded input/output types, and the full decoded clause list.
It adds F to the AST
parameters in compiler call order `Self, F, late signature regions`, records
that order explicitly, and preserves Sized, outlives, Send, and Sync through the existing
native generation categories. It validates the HRTB FnMut/Output pair without
turning it into an assumed ghost fact. No small_sort summary or conformance
claim follows from this record.

Integration with C: insert the threshold-only pure returning-post conjunction
after `gen_contract adt_defs loc ... required_outlives required_send required_sync
params result` in `translate_trait_required_fn`. Keep the native contract and
both outcome arms. C/G must use the new numeric Body/TraitImpl/TraitImplItem
identities for the generic impl inventory and must not merge their printed
`<T as StableSmallSortTypeImpl>::method` names. The R source certificate is
still supplied by the enclosing A1 driver; the opt-in flag and exact root name are only
transport gates.

Static checks completed: the patch applies to an isolated exact base with
`git apply --check --whitespace=error`; the translator baseline hash matches
the recorded final reconstruction. This is not a compile check. First Cloud
validation must establish the pinned rustc/Cap'n Proto API shape, actual method
clause inventory, region binder roles, full native AST equality, and all required
positive/negative gates in the A1 matrix. If any of those fail, this draft is
NO-GO until reviewed in-scope repair; no evidence is inferred from the patch.
