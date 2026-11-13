# E1 bounded patch review

Candidate dc24745c68951effb702a4302e84481ca74bc51a;
tree 4e17cba9a9ae0bbc625f5fc6c147ff1cca17dc04;
parent 94c00a8859bc9e4f0f1b7db73a95dbee88f6213a.
SOURCE-REPORTED / NOT_RUN for all compiler/type/MIR/runtime claims below.

Exact production write paths:

- kani-compiler/src/kani_middle/transform/check_uninit/mod.rs
- kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs
- kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs

All other source changes are new tests/expected/uninit/part1-edges/** (17 Rust/golden pairs,
README). No existing fixture/golden, runtime, codegen admission, points-to/contracts,
DFCC/driver/JSON/schema/compiletest or W15-owned file changed. No CI overlay in the source tree.

## Transfer and masks

Every constant StoreArgument now obtains constant_init_mask, checks full Sized allocation
length, materializes a local, sets its byte mask and only then takes its address. The later
operand_ty/mk_ref sees Copy(place), not Constant. Missing masks and mismatched layouts inject
specific Unsupported diagnostics; RuntimeChecks cannot have a shadow-carrying union type.
Constant ordinary union local assignments also use SetStorage rather than mk_ref(Constant).
Ordinary union SetStorage uses complete storage layout (via for_deinit) so build_set does not
require an active field or synthesize an all-true initialized mask. Actual initialized bits
remain allocation Option::is_some bits, including false. Existing MU typed-data mask behavior
is unchanged. The existing set model writes `layout[relative] && value` across its exact range;
this replaces false bytes instead of preserving a previous initialized witness.

Caller union transfer_mask remains whole-storage true as before: it selects bytes to copy,
not bytes to bless. Callee initialization still comes from the stored witness. Constant fixture
Byte is an ordinary one-byte union with either a real u8 payload or a unit field, not MU.
The initialized constant contains Some(0), which must remain true independently of value zero.

## Raw stores and projection checks

The destination walk detects raw Deref anywhere in the projection path. Earlier raw dereferences
that load pointer values still get Check; the last pointee is not read before its store. SetRef
addresses the complete destination place after the store and uses that field's typed layout.
Union writes retain their own existing create/copy/field masks. Existing address-taking exclusions
for raw dereferences and MU are unchanged; no initialized reference to Pair is formed.
Pair is repr(C): head u8 offset0, padding1..4, value u32 offset4..8, tail u8 offset8,
tail padding9..12 on the requested target. Rust assertions pin size12/offset4/offset8. Written
value is explicitly u32; read_volatile(addr_of!(...value)) is *const u32. The padding control's
cast::<u8>().add(1) reads exactly byte1; tail read is u8 byte8. Both remain outside the setter.

## DST

Caller checks all shadow argument/return layouts before adding ANY Begin/Store/Load/deinit
operations. Callee entry checks all such arguments and return before adding loads. Unsized
normal return cannot enqueue a StoreArgument. The defensive build_argument_operation guard
uses argument_size, not maybe_size (the latter reports slice ELEMENT size); it executes before
locals/addresses/model resolution in that builder. argument_size allows sized objects and
ordinary union complete storage, rejects Slice/TraitObject, and does not alter slice pointer
checks/setters/chunk operations. A compiler-side unit test covers these classifications,
including zero-sized storage and nonzero slice element size. Unit execution: NOT_RUN.

Pinned source tests/kani/UnsizedFnParams/unsized_by_value_args.rs establishes the inherited
trait self:[T] / (*Box<[T]>).method source pattern. New source substitutes MU<u8> and reads
slot1. Box coercion is [MU<u8>;2] to [MU<u8>]; method receiver self is the unsized slice value,
not Box or reference. Actual compilation and Move/Slice operand binding remain NOT_RUN and
are mandatory CI admission. Box is only a reachability vehicle; no heap/realloc support change.
By-reference source passes &mut [MU<u8>] (Sized fat pointer), while existing flat sized-slot
transfer controls remain the other companions. No compile error is runtime-model evidence.

## Immutable origins and casts

No admission or seed code changes. SUBRANGE is a const reference to a valid aligned two-byte
subarray at offset1 of three-byte anonymous storage; pointer add is one MU<u8> element,
cast is *const [MU<u8>;2], alignment1 and remaining extent2. Only SUBRANGE appears at runtime;
CI must check that an unintended whole origin did not also qualify the same allocation.
M1 requires offset Some(0), exact whole extent, supported Freeze origin and no referent
relocations. Some(0) remains distinct from missing offset and None mask bits.

Relocation fixture slots contain MU<&u8>, so the hole never constructs an invalid initialized
reference. Slot0 holds &0u8 in both inputs, ensuring the referent has relocations even in the
hole case. Target pointer width controls slot sizes (8 bytes / slot on x86_64); no manual
pointer-width integer cast occurs. raw_eq's inferred T is [MU<&u8>;2], both arguments valid
shared references to storage. Its result is ignored because distinct pointed-to allocation
identities need not compare equal. Slot1 is the only semantic hole; right bytes must all pass.

Named SOURCE is [MU<u8>;3], Sync/Freeze and valid with a slot hole. raw_eq uses &SOURCE, not
an anonymous M1 origin or a forged initialized byte reference. Determine whether a prior
static initialization path applies in CI. The existing raw-pointer-static setter has a narrower
operand condition; it is not evidence that every named-static shared-reference path passes.
Do not change these legal expectations to FAILURE or label unqualified initialized-byte failures
as ordinary UB. Unserved legal paths are limitations and a release decision for the coordinator.

## Independent review and local validation

Independent Luna HIGH reviewer /root/e1_review, separate context, read-only, no nested delegation,
reviewed the exact committed diff above and returned no concrete findings. It checked masks,
projected setter/intermediate dereferences, guard placement/classification and authored controls.
It did not compile or establish actual MIR/type/generated-property binding. This is static review,
not independent proof credit or CI qualification.

Approved scratchpad rustfmt --check PASS (rustfmt 1.11.0-nightly c1070d6938 2026-09-28),
git diff --check PASS, Python scope/fixture/hash audit PASS, unchanged strong-oracle Python
adversarial checker 21/21 PASS. No cargo/rustc/Kani/CBMC/Miri/build/push/CI ran.
