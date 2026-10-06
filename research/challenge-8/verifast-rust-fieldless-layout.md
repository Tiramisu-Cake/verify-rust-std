# Experimental Rust fieldless layout profile

This patch is a separate experiment derived from VeriFast 26.09 source commit
`809de4596839b739dd999f9e462242c835e3af46`. Its compiler-private exporter is
intended for Rust `nightly-2026-02-05`, rustc commit
`db3e99bbab28c6ca778b13222becdea54533d908`. The patch SHA-256 is
`fd37c158aecd1d383d32e1a7656fc9a1bc4f9d73504baf2f15a9f5714d79ee7a`.

The exporter emits explicit `rustLayoutInfo.absent` for ADTs outside the exact
layout domain or when rustc's layout query fails. It emits `exact` only for a
local struct with no fields in the compiler's original variant field list, no
HIR generic parameters, successful layout query, and no `packed`, `transparent`,
SIMD, scalable, or linear representation. Default `repr(Rust)` and `repr(C)`
are admitted, including `repr(align(N))`. The facts are byte size and ABI
alignment from rustc's `TyAndLayout`; alignment is ABI alignment, not preferred
alignment.

The exact payload repeats the raw ADT definition name, complete definition
span (including source file identity), target triple, and pointer width. The
translator checks each repeated value against the enclosing ADT and MIR root,
and validates the eligible shape and scalar domain before making an AST
attribute. It checks a sane pointer width, requires the size to be zero (the
Rust empty-struct rule, independent of `repr(align)`), requires a positive
power-of-two ABI alignment, checks target-width bounds, and checks size
divisibility by alignment. Metadata failures use these diagnostic prefixes:

- `RustLayoutMetadata: malformed:` for unsupported shape or invalid size or
  alignment.
- `RustLayoutMetadata: binding mismatch:` for a different ADT name, source
  definition span, target triple, or pointer width.

An absent record creates no exact AST fact. A proof that needs an exact size or
alignment therefore remains unproved. At the engine, exact facts are accepted
only for Rust structs with no generic parameters and no translated fields. The
Rust size lower bound is `0`; the existing positive lower bound remains for
C/C++. Existing field offset, ownership, and aliasing rules are untouched.

The exact rule applies to the `type_info` used for that same translated struct:
its `sizeof` equals the recorded byte size and its `alignof` equals the recorded
ABI alignment. This permits reasoning about true ZSTs such as an empty
`#[repr(align(8))]` struct and their `.add` step. It does not establish exact
layout for structs with fields, generic ADTs, packed or transparent layouts,
enums, unions, or DSTs. It adds no rule for pointer provenance, ownership,
offsets, or aliasing, and does not automatically check Copy-related UB or prove
`sort4`.

The compiler output binds metadata to its ADT, source span, and target. The
workflow must additionally pin and record the source SHA and compiler/tool
profile for each run. These bindings detect stale or misassociated metadata;
they are not cryptographic authentication against a coordinated rewrite of the
metadata and its binding fields.

`vf_mir_exporter/build.rs` regenerates Rust Cap'n Proto bindings from the
modified schema. `src/rust_frontend/Makefile` builds the exporter, and the
VeriFast build generates the OCaml bindings. Both exporter and console must be
rebuilt from the patched source on a GitHub-hosted runner; the stock profile
remains the unchanged release binaries. No build, verifier, test, or runner was
executed locally for this patch. Static `git diff --check` passed on the
editable source copy; the patch still requires hosted compilation and the
recorded positive/negative matrix.
