# W1 bounded pointer wrapping profile — draft, not yet accepted

Profile ID: `experimental-merge-wrapping-01-v1`. The unchanged base artifacts,
nightly and tool-spec manifest remain those of `../stock-26.10/PROFILE.md`.

Patch: `wrapping.patch`, SHA-256
`c7c776ff5aef2b8668aa2ed3d59b47109fce1d67a9dc2f2043fc2744dc0ed31e`.
It applies with `git apply` to the clean official VeriFast 26.10 source commit
`f76012fb518703b1d98e243ac4f487f16877cfcb`. Base file SHA-256 pins:

| File | SHA-256 |
| --- | --- |
| `bin/rust/prelude_core.rsspec` | `435146cd4632541241563ae45b146704c14f6f7cdd3b5d404837617f08bc91b8` |
| `bin/rust/std/lib.rsspec` | `2da7acfb6596f8abec90c103ef7f294152c18f974b88124669882fc051272999` |
| `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` | `c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445` |

The source applicability pin is upstream Rust
`cd371e035c7e573760c43bf934d53e8118ee3e7d` with unchanged local blob IDs:

| Source | Git blob | SHA-256 |
| --- | --- | --- |
| `library/core/src/ptr/const_ptr.rs` | `1c4d25f551667a453e9e3fb5ecad0fc55ca1224e` | `0c2faf5702586f429585e07b3ef6773aa4034b48804f66a1439370c602793e4d` |
| `library/core/src/ptr/mut_ptr.rs` | `c9d3c8d737b4aa980595f68f62e11ca1d7e21f2b` | `f10ffcdeed5a97d1f219ddbfa2e1fd11e7b4ca3825189801985b96629cda16f7` |
| `library/core/src/intrinsics/mod.rs` | `062a626fae4b46417a97e6e5eae122e1888ba8af` | `de4a6d2afbd1d9f725222c1f4d95a107b8202586b952ce2a619a054c6f2f1865` |

## Contract and source mapping

`wrapping_pointer_offset(p, d)` is the single new ghost arithmetic definition.
It constructs `pointer_ctor(p.provenance, wrapped_address, p.metadata)`, where
`wrapped_address` is `p.address + d` corrected once by `usize::MAX + 1` if it
crosses either numeric end. Every admitted byte delta satisfies
`-usize::MAX <= d <= usize::MAX`, so one correction is exact modulo
`usize::MAX + 1`. It supplies no `points_to`, allocation, liveness or aliasing
facts. Ordinary `ptr_add_` and Rust `add/sub/offset` retain their existing
nonmodular lowering and contracts.

The const and mut `wrapping_add/sub/offset` MIR call names each lower through
the existing `FnCallOutcome` path to typed synthetic functions in
`std::intrinsics`. The unsigned functions require `count == 0 || count == 1`
at the primitive call, with explicit numeric address and layout bounds
`0<=address<=usize::MAX` and `0<=size_of(T)<=usize::MAX`; their signed byte deltas are respectively
`count * size_of::<T>()` and `-count * size_of::<T>()`. The signed functions
require `-1 <= count <= 1`; their byte delta is `count * size_of::<T>()`.
The actual `std::intrinsics::arith_offset<T>` has the same signed bounded
contract. All normal posts equate the complete result pointer with the ghost
constructor, and all unwind posts are false. No function obtains memory rights.

Pinned `wrapping_add` calls `wrapping_offset(count as isize)` and
`wrapping_sub` calls `wrapping_offset((count as isize).wrapping_neg())` in both
pointer modules. For 0 and 1, the cast is exact and wrapping negation yields
0 and -1. Counts above 1, including high-bit `usize` values, are rejected
before this cast at the synthetic primitive request; the source's general
high-bit behavior is outside W1. Pinned const `wrapping_offset` calls
`intrinsics::arith_offset(self, count)`; mut casts that result to `*mut T`.
The intrinsic source declares two's-complement wrapping and says its result
need not be valid for memory access. The source docs explicitly retain the
original allocation identity through escape and reentry. The synthetic mut
contracts encode the unchanged pointer metadata and provenance across that
cast. Their typed signatures are separate, but all seven contracts use the
same ghost arithmetic definition.

## Trust and pending acceptance

The translator's method dispatch and the intrinsic contracts are new trusted
semantics, justified by the pinned wrapper and intrinsic source, not proved
Rust bodies. The source-level wrapper summaries bypass calls inside those
bodies; each wrapper requires independent source-linked acceptance tests.
The patch changes neither pointer constructors nor the kernel, exporter,
decoder, alias model, refiner, ordinary arithmetic, or runtime std source.
It is limited to `T: Sized`; zero-size `T` yields byte delta zero, but any
functional ZST guard bridge remains open. Resource provenance is preserved as
a pointer field; a foreign same-address chunk cannot be used through this
result without a separate valid read permission.

Static review: the patch applies cleanly to the pinned source. No local build,
compilation, test, verifier, extractor or runner was executed. Acceptance needs
the W1 hosted positive/negative matrix, exact expected precondition failures,
source/export/refinement integrity, full normal/unwind/body/leak/dead-code
gates and regressions described in `../OVERNIGHT-26.10-PHASE.md`.

Root self-review: numeric/layout bounds are explicit primitive reqs and fixture
premises, not inferred from the mathematical constructor field types. They are
valid raw-address/layout domain restrictions, not allocation/access rights.
Negative cases without observed exact diagnostics use TARGET calibration markers
and remain INCONCLUSIVE; predicates/coordinates will be pinned after evidence.
