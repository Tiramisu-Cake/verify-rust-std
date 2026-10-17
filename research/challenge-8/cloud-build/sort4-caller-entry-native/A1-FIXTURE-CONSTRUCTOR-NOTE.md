# A1 fixture constructor — Cloud-only, diagnostic, UNRUN

`a1-fixtures.py` constructs source-certified diagnostic inputs for the first
A1 matrix. Importing the module is inert. Its `main` and `construct` paths
require the exact `SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17` phase,
Cloud Build identity, and `/workspace` source/output paths. Do not invoke it on
the VPS. This constructor writes source and certificate files only; it does
not launch a compiler, translator, proof runner, or verifier.

Before writing, it hashes each source file against the A1 pins: `smallsort.rs`
`85c75bc9…a175e1`, stable `quicksort.rs` `4a41df6b…9d8f4c`, and
`shared/mod.rs` `fa9eec29…4dcdfcc8` from the A1 review/manifest. The pinned
checkpoint is `a22282dac3765c7d9948e6edfb0ae74102a4280b`. The A1 manifest has no
separate `marker.rs` digest, so the constructor records and checks the exact
`marker.rs` SHA from that source commit (`f7e098f8…05f80755`) as well as the
Freeze declaration span. A mismatch stops construction.

The certificate records file hashes and exact source spans/bytes for the full
`StableSmallSortTypeImpl` trait, both full original impl blocks, source-defined
16/32/scratch constants, the original `FreezeMarker` block, the standard
`Freeze` declaration provenance, the unrestricted quicksort signature and
guard/call, the original helper prefix span 220–254, and the complete helper
body span used to form a diagnostic cut source. It records the relevant call
graph and cut boundaries. The fixture
imports `std::marker::Freeze`; the builtin Freeze declaration is certificate
provenance only and is not redefined in the fixture.

The constructor emits one byte-identical positive Rust unit for P0a, P0b, P0c,
P-dispatch, and P1. It contains both original threshold impls, a separately
named `a1_guard_observer` made by changing only the original quicksort item
name, and the original quicksort function with its unrestricted signature,
guard, and actual generic `small_sort` call. Per-case target/focus identities
remain distinct; P1 receives interface/export/decode/refinement inspection
only. It also emits N-false31 and separate N-default-contract/N-freeze-contract
variants. Both contract negatives
carry mutation certificates pairing original and mutated impl bytes and hashes;
each changes only its named threshold return to 33. Their intended check is the
`result<=32` impl-body/conformance post, so original-source refusal is not a
valid negative result.

P0c retains the actual unrestricted generic signature and threshold call, has
no supplied length/Freeze premise, computes `let requirement = len + 16`, and
asserts `len<=32` and `requirement<=48`. It cuts before the generic
`small_sort` call and before non-base continuation. P1 preserves the actual
generic `T::small_sort(v, scratch, is_less)` call and cuts only the non-base
continuation. It is an interface/export/decode/refinement inspection unit;
the caller and `small_sort` bodies receive no proof credit.

The actual default and Freeze `small_sort` methods call insertion/helper
dependencies. The generated units include a source-derived helper prefix that
retains `len < 2`, the `len + 16` abort guard, pointer formation, and the const/
length decision. Labeled cuts return before the sort8 calls, the first sort4
call, and the pointer-copy fallback. The insertion dependency remains a marked
panic-body cut. Neither helper nor insertion is a verified target or eligible
summary, and neither may be consumed by a verified target. The exact helper
prefix is also retained in the certificate and `helper-prefix.fragment`. If the pinned
focus/conformance mode cannot verify the requested threshold body while
preserving the complete source inventory and refusing these unproved cuts,
that gate is NO-GO/INCONCLUSIVE; do not broaden proof targets or treat these
cuts as verified dependencies. This package is not executable proof readiness.

The constructor emits only the selected Rust source and certificate. The Cloud
runner must form the verified/original pair with the existing inert
`sort4-native-c1-bound/ghost-strip.py` and bind both resulting hashes into its
receipt. `source_pair_id` here is the shared generated-source identity across
target/focus cases; it does not replace the runner's paired verified/original
source hash.

No fixture was generated locally. Only source inspection and static Python
syntax checking were performed. The next integration step must bind the
certificate and case identities into the reviewed Cloud runner, preserve
normal/unwind/native posts, and confirm the focused threshold body plus
conformance checks before any Build submission. The constructor itself proves
nothing about translator behavior, proof acceptance, or A1 completion.

The emitted source does not invent VeriFast syntax for the common safe trait
contract; that contract/conformance work remains a reviewed translator/runner
integration obligation. The constructor records source-level impl identities,
but leaves compiler impl/item IDs `null` until the Cloud compiler query binds
them. Consequently `executable_proof_ready` is always false, and the source
certificate alone cannot open either a common summary or a first-matrix gate.
