# Select R12 checked-helper ghost grammar design

## Pinned parser and source evidence

The R11 profile `A1-CHECKED-CALLER-R11-PROFILE-2026-10-21.json` (SHA-256
`46047334a985ccc0f5b6833ca0ab4a67347e9b7782c7a489ffe6bb0e4aa8ce13`) pins
tool HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`. At that Git commit,
`src/rust_frontend/vf_mir_translator/rust_parser.ml` is blob
`e27eee316f6ba809ca6fe2111e42f217745e45bf`, raw SHA-256
`b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622`.
The active R11 source patches target the translator, exporter, and schema;
none changes `rust_parser.ml`, so this is the effective parser grammar under
that profile.

The relevant productions distinguish module imports from helper declarations:

- `parse_ghost_use_decl_or_decl_batch` accepts one standalone `use` or a batch
  of ghost declarations within one `/*@ ... @*/` annotation
  (`rust_parser.ml:1197–1207`). The two alternatives are mutually exclusive.
- `parse_ghost_decl_block` calls only `parse_ghost_decls`
  (`:950–953`); the declaration alternatives include `lem` but no `use`
  (`:803–872`). A `use` embedded at the start of this block leaves the
  following lemma outside the grammar, matching the R12-accounted S5 parse
  failure.
- Top-level `parse_decl` routes a ghost declaration block through that pure
  declaration parser (`:1161`); module declarations recurse through
  `parse_decl` (`:1089–1092`).
- The import tree grammar accepts nested brace imports and paths
  (`:1180–1192`). The parser's Rust annotation bridge routes ghost-use batches
  through `parse_ghost_use_decl_or_decl_batch`
  (`vf_mir_translator.ml:512–514`, `vf_mir_annot_parser.ml:76–81`).

The pinned working example
`tests/rust/safe_abstraction/linked_list/verified/linked_list.rs`, blob
`a4ab600d68ba1053741f4f982098b55b133d7b758a1194be088f8d25df7c2314`, places
`//@ use std::option::{Option, Option::None, Option::Some};` at module level
(line 27), then starts separate `/*@` declarations (line 29 onward). Its
`match v` uses `Option::None` and `Option::Some(v0)` (lines 615–635), and its
ghost code uses `std::option::Option_own::<&'a T>` (line 2680). This is the
source-shape precedent for the candidate; it is not an execution of the
candidate helper.

## Candidate source and boundaries

Emit one standalone module-level annotation immediately before the helper
block:

```rust
//@ use std::option::{Option, Option::None, Option::Some};
/*@
lem a1_cleanup_option_ref<'a, T>(value: std::option::Option<&'a T>)
    req thread_token(?t) &*& std::option::Option_own::<&'a T>(t, value);
    ens thread_token(t);
{
    open std::option::Option_own::<&'a T>(t, value);
    match value {
        Option::None => {}
        Option::Some(r) => {}
    }
}
@*/
```

The helper block remains the exact unit covered by `checked_cleanup_helper`
metadata and its source hash. The separate import is part of the complete
generated-source SHA and is validated as one unique, standalone line directly
before that block. The constructor spelling changes to the imported names;
the helper name, explicit internal lifetime and type parameter, arbitrary
`Option<&'a T>` parameter, required pre/post, predicate open, observer calls,
and exact caller pairing remain unchanged. No runtime import, runtime body,
Rust signature, assumption, leak, forget, or predicate contract is added.

The parser requires an explicit lifetime after `&` (`:100–108`) and accepts
named lifetime and type parameters in lemma headers (`:730–748`). Generic
type arguments are parsed by `parse_type_args` (`:156–157`). The statement
match production uses repeated statement arms (`:626–629, 677–678`); this
candidate intentionally uses the fixture's no-comma arm spelling. A match
arm can be a zero-argument path or a path applied to a variable pattern; the
working Option example confirms both constructor shapes.

## Distinct controls and proof boundary

The source-shape controls are separate:

1. The S4-style fully qualified variant paths isolate the constructor
   name-resolution failure; S4 recorded `Not a constructor of type
   std::option::Option` at `verified/lib.rs:84`.
2. Placing the import inside the helper `/*@ ... @*/` block is a grammar
   negative: the pure ghost-declaration production has no `use` case, and the
   mixed import/declaration batch production accepts only one branch.
3. The standalone module-level import followed immediately by a pure helper
   block is the positive grammar candidate, supported by the pinned example.
   Actual parser/verifier execution remains Cloud-only.

The `Some` body obligation remains independent from these syntax controls.
Pinned parser-generated enum ownership opens to ownership of each variant's
fields (`rust_parser.ml:995–1015`); `Option::Some(r)` therefore retains
`<&'a T>.own`. The pinned `shared_ref_own` constructor is defined as a
persistent pointee share (`bin/rust/rust_belt/general.rsspec:68`). Whether the
helper body discharges that residual while preserving exactly
`thread_token(t)` is not established by grammar or source precedent. Keep the
same-build nonpublishing checked-helper proof mandatory before any caller
consumes its summary. Do not infer a body PASS or P0a/P0c/P1 acceptance from
this candidate or from synthetic tests.

Static controls will bind exact helper bytes and computed body lines, require
the import to be a distinct adjacent module-level annotation, reject import
duplication/placement inside the helper block, and retain both variant arms
and all existing no-assumption/no-leak/no-forget checks. No local Rust parser,
compiler, preparer, verifier, or Cloud build is used for this grammar task.
