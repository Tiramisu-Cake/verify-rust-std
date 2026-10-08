# usize::is_multiple_of primitive admission — design before implementation

## Source obligation and trust decision

Pinned repository source is `library/core/src/num/uint_macros.rs` at blob
`558763a41c013bcda43c4a64ec3c01e6a9f54229`. The unsigned integer macro
defines `pub const fn is_multiple_of(self, rhs: Self) -> bool` at line 3919
with body:

```rust
match rhs {
    0 => self == 0,
    _ => self % rhs == 0,
}
```

The exact braced source-body SHA-256 (including its source whitespace) is
`67d3897787b9eb698ef9485939e36a378c56a63034c3d833f05f4b3d1837b56b`;
the full source file SHA-256 is
`18f5398756410bddf13b918dbb8e821a3207817497ceb89874660a7bbc80b885`;
the normalized branch-body digest is
`5d70817e98d8e37df4968b9e833bee6d0a3888af7d0412f94ac89222479d2271`.
The checked source adapter below is an alpha-renamed copy of this exact
branch body: `Self -> usize`, `self -> value`; its match arms and operators
are otherwise identical. A hosted source-admission check must bind the actual
callee to the pinned blob/body digest and verify this mapping. This does not
prove the actual std callee's implementation body: the std method receives a
new trusted primitive contract, and the adapter separately proves the same
equation from its ordinary body.

Stock VeriFast 26.10 does not declare this `usize` method in
`bin/rust/std/lib.rsspec`. The new declaration is a trusted primitive
summary, with `req true`, a branch-form postcondition
`ens if rhs == 0 { result == (self == 0) } else { result == (self % rhs == 0) }`,
and `on_unwind_ens false`. The assertion-level branch keeps modulo out of the
zero-divisor branch; the zero case matches the exact source body. The
contract adds no heap permission, allocation premise, machine-overflow
model, or postcondition about any other integer operation. This is an
explicit trust extension and needs its own profile hash and regression gate.
Apply `usize-multiple.patch` after the existing W1, M2a, copy, and strict
cleanup patches; it changes only the isolated VeriFast Rust standard-library
specification. The pinned stock spec SHA-256 is
`2da7acfb6596f8abec90c103ef7f294152c18f974b88124669882fc051272999`. The
four-patch input SHA-256 is
`f550600564f5bfd3c618dcc4724452249c754a74e8895cbc11b60fafba994cf5`, taken
from hosted run 37716179905's `build/std_lib.patched.rsspec`; applying this
patch's unique `usize`-impl insertion with the branch-form post yields
predicted SHA-256
`9e5ca27b68806f29f41a986add42be5046d3d9e1ba3917a0c5b026d4104caa33`.
This digest was computed by changing the annotation in hosted run
37750163906's staged spec; the next hosted profile must verify patch
application and recompute/record the actual staged spec hash. The updated
patch SHA-256 is recorded below.

## Diagnostic fixtures and expected evidence

`usize-multiple-cases.rs` puts the checked alpha-renamed adapter in the shared
prefix so it remains visible in every extracted CASE. Each isolated proof
therefore checks its adapter body; the first positive wrapper checks the full
conditional formula through a direct adapter call. The cases are:

| Case | Evidence sought |
|---|---|
| Adapter formula wrapper | Calls the shared checked adapter; its postcondition is the full zero-safe conditional formula and it does not unwind. |
| Arbitrary builtin/adapter comparison with a framed mutable `u32` points-to chunk | The branch-form post states the exact zero/nonzero result equation without calling a runtime method from ghost logic; the body still compares adapter and builtin results with an assertion, and returns the unrelated chunk unchanged. |
| Zero/zero, positive/zero, even/2, and odd/2 cases | Establish the four source boundary examples without introducing another helper summary. |
| Two deliberately false result assertions: positive dividend with zero divisor, and odd dividend with divisor two | Execute each builtin call into a local first, then assert that result is true with a `TARGET` marker. Do not guess an oracle; each is a useful negative only after hosted output reaches its exact assertion. |

Every positive case must have its own expected body, execution, return, and leak
accounting. Require exporter, decoder, VeriFast, refinement, unchanged-source,
and existing checked regression/admission gates to pass. The actual extracted
SmallSort call must resolve to this exact `usize` method; setup or an unrelated
`Option`/tuple helper failure is inconclusive. A green adapter or primitive
microcase establishes neither the whole merge proof nor proof of the trusted
standard-library implementation.

Run37748834934 at2960c082 failed before compilation: the insertion patch
had no trailing context; git apply rejected the internal-file hunk. Regenerated
normal unified diff includes following closing-impl context. Recomputed exact
post-spec hash from recovered f5506005 base plus literal insertion replaces the
earlier predicted d5807998 hash; the previous prediction was not confirmed.
Only whitespace/insertion-context preparation changed; exact contract stays.
All55jobseconds charged; no proof or primitive-admission result obtained.
The regenerated diff also removes spaces from the adjacent empty spec line,
so the new patch itself passes strict whitespace checks. No declaration changes.
Final static repair retains original surrounding spec whitespace. The diff
uses the existing primitive declaration as leading context and the final
on_unwind clause as trailing context, moving identical saturating clauses
without changing their resulting association. No dirty blank line occurs in
the patch text. Previous whitespace-cleanup draft was not dispatched.

Run37749632949/c54b9ee3 applied the repaired patch and checked staged
9933b6aa bytes, then built the unchanged3a08722c console. It stopped at cache
self-test because console-cache.py retained the older profile ID/key set.
This is setup rejection, not a proof result. Cache profile schema is now
explicitly updated for the zero-safe usize profile and required usize_patch
input; exact whole-profile/manifest/payload and all9 controls remain mandatory.
No console digest is broadened; previous cache/profile evidence remains historic.

Run 37750163906 built the current four-patch-plus-primitive profile. The
adapter-formula wrapper passed, but the arbitrary frame, boundary, and
zero-divisor negative cases were inconclusive: VeriFast terminated with
`Division_by_zero` while evaluating the pure conditional-expression contract.
The odd-divisor negative reached its assertion under the prior profile, but it
must be recalibrated after the contract repair. The case file now uses the
stock assertion-level `ens if` split in the primitive declaration, checked
adapter, and wrappers, keeping `% rhs` solely in the nonzero branch; the
unrelated frame is a mutable raw pointer so its points-to chunk is writable.
The zero-divisor negative from this run is not counted as proof evidence.

The updated patch is SHA-256
`b4990d0708b343bce838811f33e43e5a5f4dd442201b7b4efe2c5800116288ca`; the
predicted staged spec SHA-256 is
`9e5ca27b68806f29f41a986add42be5046d3d9e1ba3917a0c5b026d4104caa33`.
Both require confirmation in the next hosted build before proof outcomes are
interpreted.

Final declaration prints the same assertion-branch post on a single `//@ ens`
line, preserving the5-line insertion count and downstream std-spec coordinates.
Current patch SHA-256 `ecdd1fd6fcc8d811f02fa308ddc533386e0031193d527ea6950a099f8ccccaa1`; exact staged spec SHA-256 `d92e5044bbb2692e7b006fc649df361fe80bf878b69b5a2bb80635a27330f227`.
The preceding multiline candidate was not dispatched.
