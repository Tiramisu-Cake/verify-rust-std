# S4 controls

Execution NOT_RUN. Exact selectors, argv construction, expected per-invocation
exits and source hashes are in CONTROL-MANIFEST.json. Reuse mixed.rs without
editing its reads, roots, modes, line numbers, or serialized inventories.

Seven isolated fresh processes and four mixed fresh processes per tool give
18 isolated-to-mixed root comparisons. Shared ordinary roots are immutable_legal,
immutable_hole_negative, ordinary_ensures_legal and unrelated_legal_after_cycle;
shared callee to establish in the actual model is std::ptr::read::<u8>. The
cycle and legal/negative PFC roots remain separate mode controls. Actual unit
membership and selected Instance identities must be checked; a common source
file alone does not establish a common unit.

New native controls (NOT_RUN): six delayed_cache tests cover first snapshot over
two replacements, exact non-Clone value and false/true modified flags, warmed/
untouched/new regular preservation, previously absent failed-root removal,
repeated scopes, empty scope, and invalid lifecycle rejection. Two actual
BodyTransformation guard tests use empty safe compiler-independent state for
normal/early return and catch_unwind/reuse. No synthetic unsafe tcx/Instance.
The production guard's populated restoration uses the same generic journal;
real compiler-backed isolation is the 18 comparisons, not these unit stand-ins.

Preserve S2 immutable19/unit9, S3 two single intended failures/reinit SUCCESS,
all existing local Uninit/validity, mode/contract/loop controls, and accepted
Quick selectors with each fixture's own flags and default solver/checks.
No old golden inventory is updated. No T1b acceptance remains.
